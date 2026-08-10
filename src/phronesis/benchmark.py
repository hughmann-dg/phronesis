"""Behavioral benchmark harness across distinct decision domains."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from .council import Council
from .contracts import (
    CouncilResult,
    CounselResponse,
    CrossExamination,
    PhilosophicalBasis,
    RedTeamReport,
    StageRecord,
    Synthesis,
    validate_counsel_response,
)
from .doctrines import get_doctrine
from .models import DecisionPacket, ValidationError
from .sources import SourceCorpus


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    category: str
    packet: DecisionPacket


class BenchmarkSuite:
    def __init__(
        self,
        cases: tuple[BenchmarkCase, ...],
        council: Council | None = None,
        corpus: SourceCorpus | None = None,
    ) -> None:
        if not cases:
            raise ValidationError("benchmark suite must contain at least one case")
        self.cases = cases
        self.council = council or Council()
        reasoner = getattr(self.council, "reasoner", None)
        self.corpus = corpus or getattr(reasoner, "corpus", None)

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        council: Council | None = None,
        corpus: SourceCorpus | None = None,
    ) -> "BenchmarkSuite":
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError(f"cannot load benchmark suite: {exc}") from exc
        if not isinstance(raw, list):
            raise ValidationError("benchmark suite must be a JSON array")
        cases: list[BenchmarkCase] = []
        seen: set[str] = set()
        for item in raw:
            if not isinstance(item, Mapping):
                raise ValidationError("each benchmark case must be an object")
            case_id = str(item.get("id", "")).strip()
            category = str(item.get("category", "")).strip()
            if not case_id or case_id in seen:
                raise ValidationError("benchmark ids must be non-empty and unique")
            if not category:
                raise ValidationError(f"benchmark {case_id} is missing category")
            seen.add(case_id)
            cases.append(BenchmarkCase(case_id, category, DecisionPacket.from_dict(item.get("packet", {}))))
        return cls(tuple(cases), council, corpus)

    def run(self) -> dict[str, Any]:
        outputs: list[dict[str, Any]] = []
        contract_passes = 0
        citation_passes = 0
        recommendations: Counter[str] = Counter()
        confidences: list[float] = []
        verified_bases = 0
        total_bases = 0
        for case in self.cases:
            result = self.council.convene(case.packet)
            synthesis = result.synthesis
            contract_ok = _council_contract_is_valid(result, case.packet, self.corpus)
            citations_ok = all(_counsel_citations_resolve(counsel, self.corpus) for counsel in result.counsels)
            case_bases = [basis for counsel in result.counsels for basis in counsel.philosophical_basis]
            case_verified_bases = sum(_is_verified_primary_basis(basis, self.corpus) for basis in case_bases)
            verified_bases += case_verified_bases
            total_bases += len(case_bases)
            contract_passes += int(contract_ok)
            citation_passes += int(citations_ok)
            recommendations[synthesis.recommendation] += 1
            confidences.append(synthesis.confidence)
            outputs.append(
                {
                    "id": case.id,
                    "category": case.category,
                    "recommendation": synthesis.recommendation,
                    "confidence": synthesis.confidence,
                    "contract_ok": contract_ok,
                    "citations_ok": citations_ok,
                    "verified_primary_source_basis_rate": round(case_verified_bases / len(case_bases), 3)
                    if case_bases
                    else 0.0,
                }
            )
        total = len(self.cases)
        return {
            "total_cases": total,
            "categories": sorted({case.category for case in self.cases}),
            "contract_pass_rate": round(contract_passes / total, 3),
            "citation_pass_rate": round(citation_passes / total, 3),
            "verified_primary_source_basis_rate": round(verified_bases / total_bases, 3)
            if total_bases
            else 0.0,
            "average_confidence": round(sum(confidences) / total, 3),
            "recommendation_distribution": dict(recommendations),
            "cases": outputs,
        }


def _counsel_citations_resolve(counsel: CounselResponse, corpus: SourceCorpus | None) -> bool:
    try:
        doctrine = get_doctrine(counsel.school_id)
    except KeyError:
        return False
    known_ids = {source.id for source in doctrine.sources}
    known_citations = {
        (source.id, source.citation)
        for source in doctrine.sources
    }
    if not counsel.philosophical_basis:
        return False
    for basis in counsel.philosophical_basis:
        if basis.source_id not in known_ids or not basis.citation or not basis.application:
            return False
        if basis.grounding == "doctrine-citation" and (basis.source_id, basis.citation) not in known_citations:
            return False
        if basis.grounding == "retrieved-primary-source" and not _is_verified_primary_basis(basis, corpus):
            return False
        if basis.grounding not in {"doctrine-citation", "retrieved-primary-source"}:
            return False
    return True


def _is_verified_primary_basis(basis: PhilosophicalBasis, corpus: SourceCorpus | None) -> bool:
    if (
        corpus is None
        or basis.grounding != "retrieved-primary-source"
        or not basis.source_excerpt
        or not basis.source_url
    ):
        return False
    try:
        return corpus.verifies_passage(
            basis.source_id,
            basis.source_excerpt,
            basis.source_url,
            basis.citation,
        )
    except ValidationError:
        return False


def _council_contract_is_valid(
    result: CouncilResult,
    packet: DecisionPacket,
    corpus: SourceCorpus | None,
) -> bool:
    try:
        if not isinstance(result, CouncilResult) or not result.counsels:
            return False
        for counsel in result.counsels:
            doctrine = get_doctrine(counsel.school_id)
            validate_counsel_response(
                counsel,
                options=packet.options,
                expected_school_id=doctrine.id,
                expected_school_name=doctrine.name,
                allowed_sources=tuple((source.id, source.citation) for source in doctrine.sources),
                allow_null_recommendation=False,
                passage_verifier=corpus.verifies_passage if corpus else None,
            )
    except (AttributeError, KeyError, TypeError, ValidationError):
        return False
    synthesis = result.synthesis
    if (
        not isinstance(synthesis, Synthesis)
        or not isinstance(result.cross_examinations, tuple)
        or not isinstance(result.stages, tuple)
    ):
        return False
    text_fields = (
        synthesis.primary_rationale,
        synthesis.strongest_opposing_argument,
        synthesis.critical_assumption,
        synthesis.what_would_change,
    )
    school_ids = {counsel.school_id for counsel in result.counsels}
    counsel_ids = tuple(counsel.school_id for counsel in result.counsels)
    expected_supporters = tuple(
        counsel.school_id for counsel in result.counsels if counsel.recommendation == synthesis.recommendation
    )
    cross_examinations_ok = bool(result.cross_examinations) and all(
        isinstance(challenge, CrossExamination)
        and challenge.critic_school_id in school_ids
        and challenge.target_school_id in school_ids
        and challenge.critic_school_id != challenge.target_school_id
        and _nonempty_text(challenge.challenge)
        and _nonempty_text(challenge.contested_assumption)
        for challenge in result.cross_examinations
    )
    red_team = result.red_team
    red_team_ok = isinstance(red_team, RedTeamReport) and all(
        _nonempty_string_tuple(values)
        for values in (
            red_team.hidden_assumptions,
            red_team.catastrophic_edge_cases,
            red_team.incentive_failures,
            red_team.fragile_dependencies,
            red_team.biases,
            red_team.mitigation_tests,
        )
    )
    expected_stages = ("counsel", "cross_examination", "red_team", "arbiter")
    stages_ok = tuple(stage.name for stage in result.stages if isinstance(stage, StageRecord)) == expected_stages and all(
        isinstance(stage, StageRecord) and _nonempty_text(stage.summary) for stage in result.stages
    )
    return bool(
        result.packet == packet.to_dict()
        and len(school_ids) == len(counsel_ids)
        and synthesis.recommendation in packet.options
        and all(isinstance(value, str) and value.strip() for value in text_fields)
        and not isinstance(synthesis.confidence, bool)
        and isinstance(synthesis.confidence, (int, float))
        and 0 <= synthesis.confidence <= 1
        and synthesis.supporting_schools == expected_supporters
        and synthesis.disagreements
        and all(isinstance(value, str) and value.strip() for value in synthesis.disagreements)
        and cross_examinations_ok
        and red_team_ok
        and red_team.target_recommendation == synthesis.recommendation
        and stages_ok
    )


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_string_tuple(values: Any) -> bool:
    return isinstance(values, tuple) and bool(values) and all(_nonempty_text(value) for value in values)
