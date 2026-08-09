"""Rights-aware local retrieval for primary-source grounding."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse

from .models import ValidationError
from .storage import atomic_write_text


class RightsStatus(str, Enum):
    PUBLIC_DOMAIN_VERIFIED = "public-domain-verified"
    PERMISSION_GRANTED = "permission-granted"
    RESTRICTED = "restricted"
    VERIFICATION_REQUIRED = "verification-required"


class IngestionStatus(str, Enum):
    CANDIDATE = "candidate"
    VERIFIED = "verified"
    INGESTED = "ingested"
    EXCLUDED = "excluded"


_INGESTIBLE_RIGHTS = {RightsStatus.PUBLIC_DOMAIN_VERIFIED, RightsStatus.PERMISSION_GRANTED}


def _required_text(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"source {key} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class SourceRecord:
    id: str
    title: str
    author: str
    translator: str | None
    edition: str
    publication_year: int | None
    source_url: str
    rights_status: RightsStatus
    rights_evidence: str
    retrieved_date: str | None
    ingestion_status: IngestionStatus
    sha256: str
    notes: str | None = None

    @classmethod
    def for_ingestion(cls, data: Mapping[str, Any], text: str) -> "SourceRecord":
        source_id = _required_text(data, "id")
        if not re.fullmatch(r"[a-z0-9-]+", source_id):
            raise ValidationError("source id must contain lowercase letters, digits, and hyphens only")
        try:
            rights_status = RightsStatus(_required_text(data, "rights_status"))
        except ValueError as exc:
            raise ValidationError("source rights_status is not recognized") from exc
        if rights_status not in _INGESTIBLE_RIGHTS:
            raise ValidationError("source rights must be public-domain-verified or permission-granted before ingestion")
        rights_evidence = _required_text(data, "rights_evidence")
        source_url = _required_text(data, "source_url")
        parsed = urlparse(source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValidationError("source_url must be an absolute HTTP(S) URL")
        translator = data.get("translator")
        if translator is not None:
            translator = _required_text(data, "translator")
        year = data.get("publication_year")
        if year is not None and (isinstance(year, bool) or not isinstance(year, int)):
            raise ValidationError("publication_year must be an integer or null")
        notes = data.get("notes")
        if notes is not None:
            notes = str(notes)
        retrieved_date = data.get("retrieved_date")
        if retrieved_date is not None:
            if not isinstance(retrieved_date, str):
                raise ValidationError("source retrieved_date must be a YYYY-MM-DD string or null")
            try:
                date.fromisoformat(retrieved_date)
            except ValueError as exc:
                raise ValidationError("source retrieved_date must use YYYY-MM-DD") from exc
        return cls(
            id=source_id,
            title=_required_text(data, "title"),
            author=_required_text(data, "author"),
            translator=translator,
            edition=_required_text(data, "edition"),
            publication_year=year,
            source_url=source_url,
            rights_status=rights_status,
            rights_evidence=rights_evidence,
            retrieved_date=retrieved_date,
            ingestion_status=IngestionStatus.INGESTED,
            sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            notes=notes,
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SourceRecord":
        return cls(
            **{
                **data,
                "rights_status": RightsStatus(data["rights_status"]),
                "ingestion_status": IngestionStatus(data["ingestion_status"]),
            }
        )


@dataclass(frozen=True)
class SourcePassage:
    source_id: str
    title: str
    author: str
    locator: str
    text: str
    score: float
    source_url: str
    rights_status: str

    @property
    def citation(self) -> str:
        return f"{self.author}, {self.title}, {self.locator}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"citation": self.citation}


class SourceCorpus:
    """A small, transparent lexical corpus suitable for local RAG baselines."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root)
        self.records_dir = self.root / "records"
        self.texts_dir = self.root / "texts"
        self.records_dir.mkdir(parents=True, exist_ok=True)
        self.texts_dir.mkdir(parents=True, exist_ok=True)

    def ingest_file(self, text_path: str | os.PathLike[str], metadata: Mapping[str, Any]) -> SourceRecord:
        return self.ingest_text(Path(text_path).read_text(encoding="utf-8"), metadata)

    def ingest_text(self, text: str, metadata: Mapping[str, Any]) -> SourceRecord:
        if not isinstance(text, str) or not text.strip():
            raise ValidationError("source text must be non-empty UTF-8 text")
        record = SourceRecord.for_ingestion(metadata, text)
        atomic_write_text(self.texts_dir / f"{record.id}.txt", text)
        atomic_write_text(
            self.records_dir / f"{record.id}.json",
            json.dumps(asdict(record), indent=2, ensure_ascii=False) + "\n",
        )
        return record

    def list_records(self) -> tuple[SourceRecord, ...]:
        return tuple(
            SourceRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))
            for path in sorted(self.records_dir.glob("*.json"))
        )

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        source_ids: Iterable[str] | None = None,
    ) -> tuple[SourcePassage, ...]:
        query_tokens = _tokens(query)
        if not query_tokens:
            raise ValidationError("search query must contain words")
        if top_k < 1 or top_k > 50:
            raise ValidationError("top_k must be between 1 and 50")
        allowed = set(source_ids) if source_ids is not None else None
        candidates: list[SourcePassage] = []
        for record in self.list_records():
            if allowed is not None and record.id not in allowed:
                continue
            text_path = self.texts_dir / f"{record.id}.txt"
            if not text_path.is_file():
                continue
            paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text_path.read_text(encoding="utf-8")) if part.strip()]
            for index, paragraph in enumerate(paragraphs, start=1):
                paragraph_tokens = _tokens(paragraph)
                overlap = query_tokens & paragraph_tokens
                if not overlap:
                    continue
                coverage = len(overlap) / len(query_tokens)
                density = len(overlap) / max(1, len(paragraph_tokens))
                score = round(coverage * 0.85 + min(0.15, density), 4)
                candidates.append(
                    SourcePassage(
                        source_id=record.id,
                        title=record.title,
                        author=record.author,
                        locator=f"paragraph {index}",
                        text=paragraph,
                        score=score,
                        source_url=record.source_url,
                        rights_status=record.rights_status.value,
                    )
                )
        return tuple(sorted(candidates, key=lambda item: (-item.score, item.source_id, item.locator))[:top_k])

def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))
