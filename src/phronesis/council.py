"""The Counsel → Contest → Decide workflow after packet examination."""

from __future__ import annotations

from collections import defaultdict
from typing import Protocol, Sequence

from .contracts import (
    CounselResponse,
    CouncilResult,
    CrossExamination,
    RedTeamReport,
    StageRecord,
    Synthesis,
    validate_counsel_response,
)
from .doctrines import DEFAULT_COUNCIL, Doctrine, get_doctrine
from .models import DecisionPacket, claim_texts
from .reasoning import HeuristicReasoner, recommendation_counts


class Reasoner(Protocol):
    def counsel(self, packet: DecisionPacket, doctrine: Doctrine) -> CounselResponse: ...


class Council:
    """Orchestrates independent counsel, challenge, red team, and synthesis."""

    def __init__(self, reasoner: Reasoner | None = None) -> None:
        self.reasoner = reasoner or HeuristicReasoner()
        corpus = getattr(self.reasoner, "corpus", None)
        self.passage_verifier = getattr(corpus, "verifies_passage", None)

    def ask(self, school_id: str, packet: DecisionPacket) -> CounselResponse:
        doctrine = get_doctrine(school_id)
        response = self.reasoner.counsel(packet, doctrine)
        validate_counsel_response(
            response,
            options=packet.options,
            expected_school_id=doctrine.id,
            expected_school_name=doctrine.name,
            allowed_sources=tuple((source.id, source.citation) for source in doctrine.sources),
            allow_null_recommendation=doctrine.id == "socratic-examination",
            passage_verifier=self.passage_verifier,
        )
        return response

    def examine(self, packet: DecisionPacket) -> CounselResponse:
        return self.ask("socratic-examination", packet)

    def convene(
        self,
        packet: DecisionPacket,
        school_ids: Sequence[str] | None = None,
    ) -> CouncilResult:
        selected = tuple(school_ids or DEFAULT_COUNCIL)
        if len(selected) < 2:
            raise ValueError("a Council requires at least two schools")
        if len(set(selected)) != len(selected):
            raise ValueError("Council schools must be unique")

        # Each call receives only the packet and its doctrine, preserving independence.
        counsels = tuple(self.ask(school_id, packet) for school_id in selected)
        if any(counsel.recommendation is None for counsel in counsels):
            raise ValueError("Socratic Examination is an intake mode and cannot cast a Council vote")
        cross_examinations = self._cross_examine(counsels, packet)
        preliminary = self._synthesize(counsels, packet, cross_examinations, red_team=None)
        red_team = self._red_team(preliminary.recommendation, counsels, packet)
        synthesis = self._synthesize(counsels, packet, cross_examinations, red_team=red_team)

        return CouncilResult(
            packet=packet.to_dict(),
            counsels=counsels,
            cross_examinations=cross_examinations,
            red_team=red_team,
            synthesis=synthesis,
            stages=(
                StageRecord("counsel", f"{len(counsels)} schools advised independently."),
                StageRecord("cross_examination", f"{len(cross_examinations)} challenges preserved disagreements."),
                StageRecord("red_team", f"The leading option {red_team.target_recommendation!r} was attacked without a vote."),
                StageRecord("arbiter", f"The arbiter selected {synthesis.recommendation!r} rather than averaging positions."),
            ),
        )

    def _cross_examine(
        self, counsels: tuple[CounselResponse, ...], packet: DecisionPacket
    ) -> tuple[CrossExamination, ...]:
        by_id = {counsel.school_id: counsel for counsel in counsels}
        challenges: list[CrossExamination] = []
        specs = (
            ("machiavellian-realism", "aristotelian-counsel", "What incentive makes the affected stakeholders cooperate?"),
            ("humean-skepticism", "machiavellian-realism", "What observed evidence supports the claimed incentive structure?"),
            ("clausewitzian-strategy", "humean-skepticism", "What is the cost of gathering more evidence while execution windows close?"),
            ("stoic-counsel", "clausewitzian-strategy", "Which execution concerns are outside our control, and which merely lack preparation?"),
            ("consequentialist-analysis", "stoic-counsel", "Who bears harm even if the decision-maker acts with discipline?"),
        )
        for critic, target, challenge in specs:
            if critic in by_id and target in by_id:
                target_counsel = by_id[target]
                contested = (
                    target_counsel.assumptions[0]
                    if target_counsel.assumptions
                    else "The target counsel's recommendation survives its stated risks."
                )
                challenges.append(
                    CrossExamination(
                        critic,
                        target,
                        f"{target_counsel.school_name} recommends {target_counsel.recommendation!r}: "
                        f"{target_counsel.strongest_reason} {challenge}",
                        contested,
                    )
                )
        if not challenges:
            for critic, target in zip(counsels, counsels[1:]):
                challenges.append(
                    CrossExamination(
                        critic.school_id,
                        target.school_id,
                        f"What evidence would make {target.recommendation!r} fail under this doctrine?",
                        target.assumptions[0] if target.assumptions else "The recommendation survives its stated risks.",
                    )
                )
        return tuple(challenges)

    def _red_team(
        self,
        recommendation: str,
        counsels: tuple[CounselResponse, ...],
        packet: DecisionPacket,
    ) -> RedTeamReport:
        stated_assumptions = set(claim_texts(packet.assumptions))
        assumptions = tuple(
            dict.fromkeys(
                assumption
                for counsel in counsels
                for assumption in counsel.assumptions
                if assumption not in stated_assumptions
            )
        ) or ("The leading option can be executed without an unstated dependency.",)
        unknown = claim_texts(packet.unknowns)
        stakeholder = packet.stakeholders[-1] if packet.stakeholders else "an unrepresented stakeholder"
        constraint = packet.constraints[0] if packet.constraints else "a hidden critical dependency"
        rollback_failure = (
            f"A non-reversible failure occurs while pursuing {recommendation!r} and rollback is unavailable."
            if packet.reversibility.value == "low"
            else f"The downside of {recommendation!r} exceeds the packet's {packet.reversibility.value} reversibility rating."
        )
        biases = ["planning fallacy", "sunk-cost reasoning"]
        if packet.current_preference is not None:
            biases.insert(0, "confirmation bias around the current preference")
        else:
            biases.insert(0, "premature consensus from a shared framing")
        return RedTeamReport(
            target_recommendation=recommendation,
            hidden_assumptions=assumptions,
            catastrophic_edge_cases=(
                rollback_failure,
                f"Two risks treated as independent fail together: {constraint} and {unknown[0] if unknown else 'an unmeasured operational risk'}.",
            ),
            incentive_failures=(f"{stakeholder} can block execution and gains no credible benefit from cooperating.",),
            fragile_dependencies=tuple(packet.constraints[:2]) or ("No critical dependency owner is named.",),
            biases=tuple(biases),
            mitigation_tests=(
                "Name an owner, observable pass condition, and rollback trigger for every critical assumption.",
                "Run a bounded pilot or tabletop failure exercise before the irreversible step.",
            ),
        )

    def _synthesize(
        self,
        counsels: tuple[CounselResponse, ...],
        packet: DecisionPacket,
        cross_examinations: tuple[CrossExamination, ...],
        red_team: RedTeamReport | None,
    ) -> Synthesis:
        counts = recommendation_counts(counsels)
        argument_score_by_option: dict[str, float] = defaultdict(float)
        challenges_by_school: dict[str, int] = defaultdict(int)
        for challenge in cross_examinations:
            challenges_by_school[challenge.target_school_id] += 1
        for counsel in counsels:
            if counsel.recommendation is not None:
                source_bonus = min(0.06, len(counsel.philosophical_basis) * 0.03)
                challenge_penalty = min(0.12, challenges_by_school[counsel.school_id] * 0.04)
                fragility_penalty = min(0.08, (len(counsel.assumptions) + len(counsel.major_risks)) * 0.01)
                argument_score_by_option[counsel.recommendation] += (
                    counsel.confidence + source_bonus - challenge_penalty - fragility_penalty
                )
        recommendation = min(
            packet.options,
            key=lambda option: (-argument_score_by_option[option], option.casefold(), option),
        )
        supporters = tuple(c.school_id for c in counsels if c.recommendation == recommendation)
        lead = max(
            (c for c in counsels if c.recommendation == recommendation),
            key=lambda counsel: counsel.confidence,
        )
        opponents = [c for c in counsels if c.recommendation != recommendation]
        if opponents:
            strongest_opponent = max(opponents, key=lambda counsel: counsel.confidence)
            opposing = f"{strongest_opponent.school_name} favors {strongest_opponent.recommendation!r}: {strongest_opponent.strongest_reason}"
        else:
            alternatives = [option for option in packet.options if option != recommendation]
            opposing = f"The strongest unresolved alternative is {alternatives[0]!r}; unanimous framework agreement may reflect shared dependence on the same packet assumptions."

        vote_share = counts[recommendation] / len(counsels)
        average_support = sum(c.confidence for c in counsels if c.recommendation == recommendation) / counts[recommendation]
        confidence = 0.47 + vote_share * 0.22 + (average_support - 0.5) * 0.28
        if red_team is not None:
            confidence -= min(0.07, len(red_team.hidden_assumptions) * 0.015)
        confidence = round(max(0.51, min(0.89, confidence)), 2)
        critical = (
            red_team.hidden_assumptions[0]
            if red_team and red_team.hidden_assumptions
            else _first_assumption(packet)
        )
        disagreements = tuple(
            f"{c.school_name} recommends {c.recommendation!r} rather than {recommendation!r}."
            for c in opponents
        ) or ("The schools agree on the option but emphasize different failure modes.",)
        return Synthesis(
            recommendation=recommendation,
            primary_rationale=f"After weighing source basis, cross-examination, and red-team exposure: {lead.strongest_reason}",
            supporting_schools=supporters,
            strongest_opposing_argument=opposing,
            critical_assumption=critical,
            confidence=confidence,
            what_would_change=lead.what_would_change[0],
            disagreements=disagreements,
        )


def _first_assumption(packet: DecisionPacket) -> str:
    return (
        packet.assumptions[0].text
        if packet.assumptions
        else "The selected option can be executed within the stated constraints."
    )
