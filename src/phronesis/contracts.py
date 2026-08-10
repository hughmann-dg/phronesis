"""Serializable output contracts for counsel and Council deliberation."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Callable, Mapping
from urllib.parse import urlparse

from .models import ValidationError
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
    extensions: Mapping[str, Any] = field(default_factory=dict)

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


def validate_counsel_response(
    response: CounselResponse,
    *,
    options: tuple[str, ...],
    expected_school_id: str,
    expected_school_name: str,
    allowed_sources: tuple[tuple[str, str], ...],
    allow_null_recommendation: bool = False,
    passage_verifier: Callable[[str, str, str, str], bool] | None = None,
) -> None:
    """Validate a reasoner's response at the Council's public boundary."""

    if not isinstance(response, CounselResponse):
        raise ValidationError("reasoner must return a CounselResponse")
    if response.school_id != expected_school_id or response.school_name != expected_school_name:
        raise ValidationError("reasoner response school identity does not match the requested doctrine")
    if response.recommendation is None:
        if not allow_null_recommendation:
            raise ValidationError("counsel recommendation must match one of the packet options")
    elif response.recommendation not in options:
        raise ValidationError("counsel recommendation must match one of the packet options")
    _nonempty_text(response.strongest_reason, "strongest_reason")
    _string_sequence(response.reasoning, "reasoning", require_nonempty=True)
    _string_sequence(response.assumptions, "assumptions")
    _string_sequence(response.major_risks, "major_risks", require_nonempty=True)
    _string_sequence(response.what_would_change, "what_would_change", require_nonempty=True)
    _string_sequence(response.disconfirming_evidence, "disconfirming_evidence", require_nonempty=True)
    if isinstance(response.confidence, bool) or not isinstance(response.confidence, (int, float)):
        raise ValidationError("counsel confidence must be a number between 0 and 1")
    if not 0 <= response.confidence <= 1:
        raise ValidationError("counsel confidence must be between 0 and 1")
    if not isinstance(response.extensions, Mapping):
        raise ValidationError("counsel extensions must be an object")
    _json_value(response.extensions, "extensions")
    if not response.philosophical_basis:
        raise ValidationError("counsel philosophical_basis must not be empty")
    known_ids = {source_id for source_id, _ in allowed_sources}
    known_citations = set(allowed_sources)
    for basis in response.philosophical_basis:
        if not isinstance(basis, PhilosophicalBasis):
            raise ValidationError("philosophical_basis entries must be PhilosophicalBasis values")
        for field_name in ("principle", "source_id", "citation", "application"):
            _nonempty_text(getattr(basis, field_name), f"philosophical_basis.{field_name}")
        if basis.source_id not in known_ids:
            raise ValidationError("philosophical_basis source_id is not declared by the doctrine")
        if basis.source_excerpt is not None and not isinstance(basis.source_excerpt, str):
            raise ValidationError("counsel philosophical_basis.source_excerpt must be a string or null")
        if basis.source_url is not None:
            if not isinstance(basis.source_url, str):
                raise ValidationError("counsel philosophical_basis.source_url must be a string or null")
            parsed = urlparse(basis.source_url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValidationError("counsel philosophical_basis.source_url must be an absolute HTTP(S) URL")
        if basis.grounding == "doctrine-citation":
            if (basis.source_id, basis.citation) not in known_citations:
                raise ValidationError("doctrine citation does not match a declared source locator")
        elif basis.grounding == "retrieved-primary-source":
            _nonempty_text(basis.source_excerpt, "philosophical_basis.source_excerpt")
            _nonempty_text(basis.source_url, "philosophical_basis.source_url")
            if passage_verifier is None or not passage_verifier(
                basis.source_id,
                basis.source_excerpt or "",
                basis.source_url or "",
                basis.citation,
            ):
                raise ValidationError("retrieved philosophical basis is not present in a verified corpus")
        else:
            raise ValidationError("philosophical_basis grounding is not recognized")


def _nonempty_text(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"counsel {field_name} must be a non-empty string")


def _string_sequence(values: Any, field_name: str, *, require_nonempty: bool = False) -> None:
    if not isinstance(values, tuple) or (require_nonempty and not values):
        raise ValidationError(f"counsel {field_name} must be a tuple of strings")
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValidationError(f"counsel {field_name} must contain non-empty strings")


def _json_value(value: Any, field_name: str) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValidationError(f"counsel {field_name} must contain finite JSON numbers")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValidationError(f"counsel {field_name} keys must be strings")
            _json_value(item, f"{field_name}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _json_value(item, f"{field_name}[{index}]")
        return
    raise ValidationError(f"counsel {field_name} must contain only JSON-compatible values")
