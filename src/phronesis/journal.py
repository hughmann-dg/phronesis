"""Durable decision journal and lightweight calibration analytics."""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .contracts import CouncilResult
from .models import DecisionPacket, ValidationError
from .serialization import jsonable
from .storage import atomic_write_text


def _validate_date(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} must use YYYY-MM-DD") from exc
    return value


@dataclass(frozen=True)
class JournalEntry:
    id: str
    date: str
    decision_packet: dict[str, Any]
    council_recommendation: dict[str, Any]
    user_decision: str
    user_confidence: float
    council_confidence: float
    key_assumptions: tuple[str, ...]
    predicted_outcomes: tuple[str, ...]
    review_date: str | None
    actual_outcome: str | None = None
    lessons: tuple[str, ...] = ()
    prediction_results: tuple[bool, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return jsonable(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "JournalEntry":
        return cls(
            id=str(data["id"]),
            date=str(data["date"]),
            decision_packet=dict(data["decision_packet"]),
            council_recommendation=dict(data["council_recommendation"]),
            user_decision=str(data["user_decision"]),
            user_confidence=float(data["user_confidence"]),
            council_confidence=float(data["council_confidence"]),
            key_assumptions=tuple(data.get("key_assumptions", ())),
            predicted_outcomes=tuple(data.get("predicted_outcomes", ())),
            review_date=data.get("review_date"),
            actual_outcome=data.get("actual_outcome"),
            lessons=tuple(data.get("lessons", ())),
            prediction_results=tuple(bool(value) for value in data.get("prediction_results", ())),
        )


class DecisionJournal:
    """Stores one recoverable JSON document per decision."""

    def __init__(self, directory: str | os.PathLike[str]) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        packet: DecisionPacket,
        council_result: CouncilResult,
        *,
        user_decision: str,
        user_confidence: float,
        predicted_outcomes: Iterable[str] = (),
        review_date: str | None = None,
    ) -> JournalEntry:
        if user_decision not in packet.options:
            raise ValidationError("user_decision must exactly match one of the packet options")
        if isinstance(user_confidence, bool) or not isinstance(user_confidence, (int, float)) or not 0 <= user_confidence <= 1:
            raise ValidationError("user_confidence must be between 0 and 1")
        predictions = tuple(str(value).strip() for value in predicted_outcomes)
        if any(not prediction for prediction in predictions):
            raise ValidationError("predicted_outcomes cannot contain blank values")
        review_date = _validate_date(review_date, "review_date")
        now = datetime.now(timezone.utc)
        slug = re.sub(r"[^a-z0-9]+", "-", packet.decision.casefold()).strip("-")[:36] or "decision"
        entry_id = f"{now:%Y%m%d}-{slug}-{uuid.uuid4().hex[:8]}"
        entry = JournalEntry(
            id=entry_id,
            date=now.date().isoformat(),
            decision_packet=packet.to_dict(),
            council_recommendation=council_result.synthesis.__dict__,
            user_decision=user_decision,
            user_confidence=float(user_confidence),
            council_confidence=council_result.synthesis.confidence,
            key_assumptions=tuple(claim.text for claim in packet.assumptions),
            predicted_outcomes=predictions,
            review_date=review_date,
        )
        self._write(entry)
        return entry

    def get(self, entry_id: str) -> JournalEntry:
        if not re.fullmatch(r"[a-zA-Z0-9-]+", entry_id):
            raise ValidationError("invalid journal entry id")
        path = self.directory / f"{entry_id}.json"
        if not path.is_file():
            raise KeyError(f"journal entry not found: {entry_id}")
        return JournalEntry.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list_entries(self) -> tuple[JournalEntry, ...]:
        entries = [
            JournalEntry.from_dict(json.loads(path.read_text(encoding="utf-8")))
            for path in self.directory.glob("*.json")
            if path.is_file()
        ]
        return tuple(sorted(entries, key=lambda item: (item.date, item.id), reverse=True))

    def review(
        self,
        entry_id: str,
        *,
        actual_outcome: str,
        lessons: Iterable[str],
        prediction_results: Iterable[bool] = (),
    ) -> JournalEntry:
        entry = self.get(entry_id)
        outcome = actual_outcome.strip()
        if not outcome:
            raise ValidationError("actual_outcome must be a non-empty string")
        lesson_values = tuple(str(lesson).strip() for lesson in lessons)
        if not lesson_values or any(not lesson for lesson in lesson_values):
            raise ValidationError("lessons must include at least one non-empty value")
        results = tuple(prediction_results)
        if results and len(results) != len(entry.predicted_outcomes):
            raise ValidationError("prediction_results must match the number of predicted_outcomes")
        if any(not isinstance(value, bool) for value in results):
            raise ValidationError("prediction_results must contain only booleans")

        reviewed = JournalEntry(
            **{
                **entry.to_dict(),
                "key_assumptions": entry.key_assumptions,
                "predicted_outcomes": entry.predicted_outcomes,
                "actual_outcome": outcome,
                "lessons": lesson_values,
                "prediction_results": results,
            }
        )
        self._write(reviewed)
        return reviewed

    def insights(self) -> dict[str, Any]:
        entries = self.list_entries()
        reviewed = [entry for entry in entries if entry.actual_outcome is not None]
        prediction_results = [value for entry in reviewed for value in entry.prediction_results]
        return {
            "total_decisions": len(entries),
            "reviewed_decisions": len(reviewed),
            "pending_reviews": len(entries) - len(reviewed),
            "average_user_confidence": round(sum(e.user_confidence for e in entries) / len(entries), 3) if entries else None,
            "average_council_confidence": round(sum(e.council_confidence for e in entries) / len(entries), 3) if entries else None,
            "prediction_accuracy": round(sum(prediction_results) / len(prediction_results), 3) if prediction_results else None,
            "lesson_themes": _lesson_themes(reviewed),
        }

    def _write(self, entry: JournalEntry) -> None:
        target = self.directory / f"{entry.id}.json"
        atomic_write_text(target, json.dumps(entry.to_dict(), indent=2, ensure_ascii=False) + "\n")


def _lesson_themes(entries: list[JournalEntry]) -> list[dict[str, Any]]:
    themes = {
        "execution": ("execution", "delay", "capacity", "incident", "cutover", "friction"),
        "incentives": ("incentive", "stakeholder", "cooperation", "resistance", "support"),
        "evidence": ("evidence", "assumption", "estimate", "unknown", "forecast"),
        "positioning": ("timing", "option", "pilot", "phase", "position"),
    }
    combined = " ".join(lesson.casefold() for entry in entries for lesson in entry.lessons)
    counts = [
        {"theme": theme, "mentions": sum(combined.count(word) for word in words)}
        for theme, words in themes.items()
    ]
    return [item for item in sorted(counts, key=lambda item: (-item["mentions"], item["theme"])) if item["mentions"]]
