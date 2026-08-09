"""Behavioral benchmark harness across distinct decision domains."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from .council import Council
from .models import DecisionPacket, ValidationError


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    category: str
    packet: DecisionPacket


class BenchmarkSuite:
    def __init__(self, cases: tuple[BenchmarkCase, ...], council: Council | None = None) -> None:
        if not cases:
            raise ValidationError("benchmark suite must contain at least one case")
        self.cases = cases
        self.council = council or Council()

    @classmethod
    def from_file(cls, path: str | Path, council: Council | None = None) -> "BenchmarkSuite":
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
        return cls(tuple(cases), council)

    def run(self) -> dict[str, Any]:
        outputs: list[dict[str, Any]] = []
        contract_passes = 0
        citation_passes = 0
        recommendations: Counter[str] = Counter()
        confidences: list[float] = []
        for case in self.cases:
            result = self.council.convene(case.packet)
            synthesis = result.synthesis
            contract_ok = bool(
                synthesis.recommendation in case.packet.options
                and synthesis.primary_rationale
                and synthesis.strongest_opposing_argument
                and synthesis.critical_assumption
                and synthesis.what_would_change
                and synthesis.disagreements
            )
            citations_ok = all(
                counsel.philosophical_basis
                and all(basis.source_id and basis.citation and basis.application for basis in counsel.philosophical_basis)
                for counsel in result.counsels
            )
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
                }
            )
        total = len(self.cases)
        return {
            "total_cases": total,
            "categories": sorted({case.category for case in self.cases}),
            "contract_pass_rate": round(contract_passes / total, 3),
            "citation_pass_rate": round(citation_passes / total, 3),
            "average_confidence": round(sum(confidences) / total, 3),
            "recommendation_distribution": dict(recommendations),
            "cases": outputs,
        }
