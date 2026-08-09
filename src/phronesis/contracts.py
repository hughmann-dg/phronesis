"""Serializable output contracts for counsel and Council deliberation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .serialization import jsonable


@dataclass(frozen=True)
class PhilosophicalBasis:
    principle: str
    source_id: str
    citation: str
    application: str
    grounding: str = "doctrine-citation"
    source_excerpt: str | None = None
    source_url: str | None = None


@dataclass(frozen=True)
class CounselResponse:
    school_id: str
    school_name: str
    recommendation: str | None
    strongest_reason: str
    reasoning: tuple[str, ...]
    assumptions: tuple[str, ...]
    major_risks: tuple[str, ...]
    confidence: float
    what_would_change: tuple[str, ...]
    disconfirming_evidence: tuple[str, ...]
    philosophical_basis: tuple[PhilosophicalBasis, ...]

    def to_dict(self) -> dict[str, Any]:
        return jsonable(self)


@dataclass(frozen=True)
class CrossExamination:
    critic_school_id: str
    target_school_id: str
    challenge: str
    contested_assumption: str


@dataclass(frozen=True)
class RedTeamReport:
    target_recommendation: str
    hidden_assumptions: tuple[str, ...]
    catastrophic_edge_cases: tuple[str, ...]
    incentive_failures: tuple[str, ...]
    fragile_dependencies: tuple[str, ...]
    biases: tuple[str, ...]
    mitigation_tests: tuple[str, ...]


@dataclass(frozen=True)
class Synthesis:
    recommendation: str
    primary_rationale: str
    supporting_schools: tuple[str, ...]
    strongest_opposing_argument: str
    critical_assumption: str
    confidence: float
    what_would_change: str
    disagreements: tuple[str, ...]


@dataclass(frozen=True)
class StageRecord:
    name: str
    summary: str


@dataclass(frozen=True)
class CouncilResult:
    packet: dict[str, Any]
    counsels: tuple[CounselResponse, ...]
    cross_examinations: tuple[CrossExamination, ...]
    red_team: RedTeamReport
    synthesis: Synthesis
    stages: tuple[StageRecord, ...]

    def to_dict(self) -> dict[str, Any]:
        return jsonable(self)
