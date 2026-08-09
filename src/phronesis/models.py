"""Public domain models used at every Phronesis boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping


class ValidationError(ValueError):
    """Raised when user-supplied decision data violates the public contract."""


class ClaimKind(str, Enum):
    FACT = "fact"
    ASSUMPTION = "assumption"
    ESTIMATE = "estimate"
    OPINION = "opinion"
    UNKNOWN = "unknown"


class Reversibility(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def _strings(values: Any, field_name: str) -> tuple[str, ...]:
    if values is None:
        return ()
    if not isinstance(values, (list, tuple)):
        raise ValidationError(f"{field_name} must be a list of strings")
    return tuple(_text(value, field_name) for value in values)


def _confidence(value: Any, field_name: str, *, optional: bool = True) -> float | None:
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{field_name} must be a number between 0 and 1")
    result = float(value)
    if not 0 <= result <= 1:
        raise ValidationError(f"{field_name} must be between 0 and 1")
    return result


@dataclass(frozen=True)
class Claim:
    text: str
    kind: ClaimKind
    confidence: float | None = None
    source: str | None = None

    @classmethod
    def from_value(cls, value: Any, kind: ClaimKind) -> "Claim":
        if isinstance(value, str):
            return cls(text=_text(value, kind.value), kind=kind)
        if not isinstance(value, Mapping):
            raise ValidationError(f"{kind.value} entries must be strings or objects")
        source = value.get("source")
        if source is not None:
            source = _text(source, f"{kind.value}.source")
        return cls(
            text=_text(value.get("text"), f"{kind.value}.text"),
            kind=kind,
            confidence=_confidence(value.get("confidence"), f"{kind.value}.confidence"),
            source=source,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"text": self.text, "kind": self.kind.value}
        if self.confidence is not None:
            result["confidence"] = self.confidence
        if self.source is not None:
            result["source"] = self.source
        return result


def _claims(values: Any, kind: ClaimKind) -> tuple[Claim, ...]:
    if values is None:
        return ()
    if not isinstance(values, (list, tuple)):
        raise ValidationError(f"{kind.value}s must be a list")
    return tuple(Claim.from_value(value, kind) for value in values)


@dataclass(frozen=True)
class DecisionPacket:
    decision: str
    objective: str
    options: tuple[str, ...]
    constraints: tuple[str, ...] = ()
    stakeholders: tuple[str, ...] = ()
    facts: tuple[Claim, ...] = ()
    assumptions: tuple[Claim, ...] = ()
    estimates: tuple[Claim, ...] = ()
    opinions: tuple[Claim, ...] = ()
    unknowns: tuple[Claim, ...] = ()
    time_horizon: str | None = None
    reversibility: Reversibility = Reversibility.UNKNOWN
    current_preference: str | None = None
    current_confidence: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DecisionPacket":
        if not isinstance(data, Mapping):
            raise ValidationError("decision packet must be an object")
        decision = _text(data.get("decision"), "decision")
        objective = _text(data.get("objective"), "objective")
        options = _strings(data.get("options"), "options")
        if len(options) < 2:
            raise ValidationError("options must contain at least two choices")
        if len(set(option.casefold() for option in options)) != len(options):
            raise ValidationError("options must be unique")

        preference = data.get("current_preference")
        if preference is not None:
            preference = _text(preference, "current_preference")
            if preference not in options:
                raise ValidationError("current_preference must exactly match one of the options")

        raw_reversibility = data.get("reversibility", "unknown")
        try:
            reversibility = Reversibility(str(raw_reversibility).lower())
        except ValueError as exc:
            raise ValidationError("reversibility must be low, medium, high, or unknown") from exc

        time_horizon = data.get("time_horizon")
        if time_horizon is not None:
            time_horizon = _text(time_horizon, "time_horizon")

        metadata = data.get("metadata", {})
        if not isinstance(metadata, Mapping):
            raise ValidationError("metadata must be an object")

        return cls(
            decision=decision,
            objective=objective,
            options=options,
            constraints=_strings(data.get("constraints"), "constraints"),
            stakeholders=_strings(data.get("stakeholders"), "stakeholders"),
            facts=_claims(data.get("known_facts", data.get("facts")), ClaimKind.FACT),
            assumptions=_claims(data.get("assumptions"), ClaimKind.ASSUMPTION),
            estimates=_claims(data.get("estimates"), ClaimKind.ESTIMATE),
            opinions=_claims(data.get("opinions"), ClaimKind.OPINION),
            unknowns=_claims(data.get("unknowns"), ClaimKind.UNKNOWN),
            time_horizon=time_horizon,
            reversibility=reversibility,
            current_preference=preference,
            current_confidence=_confidence(data.get("current_confidence"), "current_confidence"),
            metadata=dict(metadata),
        )

    @property
    def all_claims(self) -> tuple[Claim, ...]:
        return self.facts + self.assumptions + self.estimates + self.opinions + self.unknowns

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "decision": self.decision,
            "objective": self.objective,
            "options": list(self.options),
            "constraints": list(self.constraints),
            "stakeholders": list(self.stakeholders),
            "known_facts": [claim.to_dict() for claim in self.facts],
            "assumptions": [claim.to_dict() for claim in self.assumptions],
            "estimates": [claim.to_dict() for claim in self.estimates],
            "opinions": [claim.to_dict() for claim in self.opinions],
            "unknowns": [claim.to_dict() for claim in self.unknowns],
            "time_horizon": self.time_horizon,
            "reversibility": self.reversibility.value,
            "current_preference": self.current_preference,
            "current_confidence": self.current_confidence,
            "metadata": dict(self.metadata),
        }
        return result


def claim_texts(claims: Iterable[Claim]) -> list[str]:
    """Return claim text for display and serialization adapters."""

    return [claim.text for claim in claims]
