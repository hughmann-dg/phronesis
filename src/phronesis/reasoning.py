"""A transparent baseline reasoner for exercising Phronesis locally.

It deliberately uses inspectable heuristics. Production deployments can replace
this object at the Council boundary with a model-backed reasoner while retaining
the same doctrine and output contracts.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .contracts import CounselResponse, PhilosophicalBasis
from .doctrines import Doctrine
from .models import DecisionPacket, claim_texts

if TYPE_CHECKING:
    from .sources import SourceCorpus


_ADAPTIVE = {"incremental", "phase", "phased", "pilot", "trial", "stage", "staged", "partial", "prototype", "test"}
_DELAY = {"delay", "wait", "defer", "later", "postpone"}
_IMMEDIATE = {"now", "immediate", "today", "q4", "launch"}
_DEADLINE = {"expires", "deadline", "freeze", "must", "due", "urgent"}


@dataclass(frozen=True)
class _SchoolPolicy:
    adaptive_weight: float
    adaptive_condition: str
    delay_under_uncertainty: float
    reason_template: str
    risk: str


_SCHOOL_POLICIES = {
    "aristotelian-counsel": _SchoolPolicy(
        0.26,
        "always",
        0,
        "{recommendation} is the most prudent fit to the particulars, especially {constraint}, while keeping the effect on {stakeholder} in view.",
        "The option may optimize process while neglecting long-term trust or flourishing",
    ),
    "stoic-counsel": _SchoolPolicy(
        0.28,
        "always",
        0,
        "{recommendation} concentrates attention on controllable commitments and reduces dependence on a single favorable outcome.",
        "Calling a dependency uncontrollable may excuse inadequate preparation",
    ),
    "machiavellian-realism": _SchoolPolicy(
        0.31,
        "stakeholders",
        0,
        "{recommendation} creates more opportunities to secure cooperation from {stakeholder} before resistance becomes decisive.",
        "A stakeholder may gain more by blocking than cooperating",
    ),
    "clausewitzian-strategy": _SchoolPolicy(
        0.42,
        "context",
        0,
        "{recommendation} is more robust to friction from {constraint} and preserves adaptation during execution.",
        "Friction and dispersed effort may prevent execution from matching the plan",
    ),
    "sun-tzu-positioning": _SchoolPolicy(
        0.38,
        "always",
        0,
        "{recommendation} improves information and position before an irreversible commitment.",
        "Waiting to improve position may allow the current problem to compound",
    ),
    "humean-skepticism": _SchoolPolicy(
        0.36,
        "uncertainty",
        0.12,
        "{recommendation} can generate evidence about {unknown} before confidence outruns observation.",
        "The causal case may rest on inference rather than repeated observation",
    ),
    "bayesian-analysis": _SchoolPolicy(
        0.34,
        "uncertainty",
        0.12,
        "{recommendation} has information value: it can update confidence about {unknown} while limiting exposure.",
        "Numerical confidence may imply precision unsupported by the inputs",
    ),
    "consequentialist-analysis": _SchoolPolicy(
        0.22,
        "stakeholders",
        0,
        "{recommendation} limits concentrated downside while advancing benefits for the named stakeholders.",
        "Aggregate benefit may conceal a severe burden on one stakeholder",
    ),
}


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def _first(values: tuple[str, ...], default: str) -> str:
    return values[0] if values else default


class HeuristicReasoner:
    """Source-citing deterministic baseline; no opaque persona simulation."""

    def __init__(self, corpus: "SourceCorpus | None" = None) -> None:
        self.corpus = corpus

    def counsel(self, packet: DecisionPacket, doctrine: Doctrine) -> CounselResponse:
        if doctrine.id == "socratic-examination":
            return self._examine(packet, doctrine)

        scores = self._score_options(packet, doctrine)
        ranked = sorted(packet.options, key=lambda option: (-scores[option], packet.options.index(option)))
        recommendation = ranked[0]
        runner_up = ranked[1]
        margin = scores[recommendation] - scores[runner_up]

        assumption = _first(
            claim_texts(packet.assumptions),
            f"The stated objective—{packet.objective}—is the objective that should govern the choice.",
        )
        unknown = _first(
            claim_texts(packet.unknowns),
            "The most consequential execution uncertainty has been identified.",
        )
        constraint = _first(packet.constraints, "Available capacity is sufficient for the chosen option.")
        stakeholder = _first(packet.stakeholders, "the people affected by the decision")

        reasons = self._school_reasons(doctrine.id, packet, recommendation, constraint, stakeholder, unknown)
        risks = self._school_risks(doctrine.id, packet, recommendation)
        evidence_factor = min(0.08, len(packet.facts) * 0.02)
        uncertainty_penalty = min(0.09, (len(packet.assumptions) + len(packet.unknowns)) * 0.015)
        confidence = round(max(0.42, min(0.84, 0.58 + min(margin, 0.18) + evidence_factor - uncertainty_penalty)), 2)

        return CounselResponse(
            school_id=doctrine.id,
            school_name=doctrine.name,
            recommendation=recommendation,
            strongest_reason=reasons[0],
            reasoning=tuple(reasons),
            assumptions=(assumption, f"{constraint} remains a real constraint rather than a negotiable preference."),
            major_risks=tuple(risks),
            confidence=confidence,
            what_would_change=(
                f"Prefer {runner_up!r} if evidence shows it advances the objective with less exposure to {risks[0].lower()}.",
                f"Reassess if this unknown is resolved differently: {unknown}",
            ),
            disconfirming_evidence=(
                f"Evidence that {recommendation!r} cannot satisfy the stated objective.",
                f"A successful comparable case for {runner_up!r} under the same constraints.",
            ),
            philosophical_basis=(self._basis(doctrine, reasons[0]),),
        )

    def _score_options(self, packet: DecisionPacket, doctrine: Doctrine) -> dict[str, float]:
        objective_tokens = _tokens(packet.objective) - {"the", "and", "with", "without", "to", "a"}
        context_tokens = _tokens(" ".join(packet.constraints + tuple(claim_texts(packet.all_claims))))
        deadline_present = bool(context_tokens & _DEADLINE)
        uncertainty = len(packet.assumptions) + len(packet.unknowns)
        policy = _SCHOOL_POLICIES.get(doctrine.id)
        scores: dict[str, float] = {}

        for option in packet.options:
            words = _tokens(option)
            score = min(0.12, len(words & objective_tokens) * 0.04)
            if deadline_present and words & _IMMEDIATE:
                score += 0.12
            if deadline_present and words & _DELAY:
                score -= 0.18

            adaptive = bool(words & _ADAPTIVE)
            if adaptive and policy and _policy_applies(policy, packet, uncertainty):
                score += policy.adaptive_weight
            if policy and policy.delay_under_uncertainty and words & _DELAY and uncertainty:
                score += policy.delay_under_uncertainty
            scores[option] = score
        return scores

    def _school_reasons(
        self,
        school_id: str,
        packet: DecisionPacket,
        recommendation: str,
        constraint: str,
        stakeholder: str,
        unknown: str,
    ) -> list[str]:
        common = f"{recommendation!r} best connects the available means to the stated objective: {packet.objective}"
        policy = _SCHOOL_POLICIES.get(school_id)
        school_reason = (
            policy.reason_template.format(
                recommendation=repr(recommendation),
                constraint=constraint.lower(),
                stakeholder=stakeholder,
                unknown=unknown.lower(),
            )
            if policy
            else common
        )
        return [school_reason, common]

    def _school_risks(self, school_id: str, packet: DecisionPacket, recommendation: str) -> list[str]:
        policy = _SCHOOL_POLICIES.get(school_id)
        risk = policy.risk if policy else "The recommendation may fail under an untested assumption"
        second = (
            f"{recommendation!r} may become harder to reverse than the packet's {packet.reversibility.value} rating suggests"
        )
        return [risk, second]

    def _examine(self, packet: DecisionPacket, doctrine: Doctrine) -> CounselResponse:
        questions = [
            f"What observable outcome would show that {packet.objective.lower()} was achieved?",
            f"What evidence makes {packet.current_preference!r} preferable?" if packet.current_preference else "Which option do you currently prefer, and why?",
            f"What would prove this assumption wrong: {_first(claim_texts(packet.assumptions), 'the current framing is correct')}?",
            "What happens if no option is chosen now?",
        ]
        return CounselResponse(
            school_id=doctrine.id,
            school_name=doctrine.name,
            recommendation=None,
            strongest_reason="The framing should be tested before advice is offered.",
            reasoning=tuple(questions),
            assumptions=tuple(claim_texts(packet.assumptions)),
            major_risks=("A premature recommendation could harden an invalid framing.",),
            confidence=0.72,
            what_would_change=("Answer the examination questions with observable evidence.",),
            disconfirming_evidence=("Evidence that the objective and option set are already complete and mutually understood.",),
            philosophical_basis=(
                self._basis(doctrine, "Questions test the packet's premises before prescribing action."),
            ),
        )

    def _basis(self, doctrine: Doctrine, application: str) -> PhilosophicalBasis:
        source = doctrine.sources[0]
        if self.corpus is not None:
            passages = self.corpus.search(
                f"{doctrine.principles[0]} {doctrine.primary_question}",
                top_k=1,
                source_ids=(source.id,),
            )
            if passages:
                passage = passages[0]
                return PhilosophicalBasis(
                    principle=doctrine.principles[0],
                    source_id=passage.source_id,
                    citation=passage.citation,
                    application=application,
                    grounding="retrieved-primary-source",
                    source_excerpt=passage.text,
                    source_url=passage.source_url,
                )
        return PhilosophicalBasis(
            principle=doctrine.principles[0],
            source_id=source.id,
            citation=source.citation,
            application=application,
        )


def recommendation_counts(counsels: tuple[CounselResponse, ...]) -> Counter[str]:
    return Counter(counsel.recommendation for counsel in counsels if counsel.recommendation is not None)


def _policy_applies(policy: _SchoolPolicy, packet: DecisionPacket, uncertainty: int) -> bool:
    return {
        "always": True,
        "stakeholders": len(packet.stakeholders) >= 2,
        "uncertainty": uncertainty > 0,
        "context": bool(packet.constraints or uncertainty),
    }[policy.adaptive_condition]
