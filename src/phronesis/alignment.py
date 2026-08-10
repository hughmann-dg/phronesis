"""Repository-wide alignment checks for doctrine, skills, sources, and packaging."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .doctrines import list_doctrines
from .models import ValidationError
from .reasoning import supported_school_ids
from .sources import SourceRecord


def audit_repository(root: str | Path) -> dict[str, Any]:
    """Return machine-readable errors when repository layers drift apart."""

    root = Path(root)
    errors: list[str] = []
    manifest_path = root / "sources" / "manifest.yaml"
    try:
        manifest_records = _load_flat_manifest(manifest_path)
    except (OSError, ValueError) as exc:
        manifest_records = []
        errors.append(f"cannot read source manifest: {exc}")
    manifest = {str(record.get("id")): record for record in manifest_records if record.get("id")}

    schema_path = root / "schemas" / "source-record.schema.json"
    try:
        source_schema = json.loads(schema_path.read_text(encoding="utf-8"))
        required_source_fields = set(source_schema["required"])
        allowed_source_fields = set(source_schema["properties"])
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        required_source_fields = set()
        allowed_source_fields = set()
        errors.append(f"cannot read source schema: {exc}")

    manifest_ids: list[str] = []
    for record in manifest_records:
        source_id = str(record.get("id", "<missing-id>"))
        manifest_ids.append(source_id)
        missing = sorted(required_source_fields - set(record))
        if missing:
            errors.append(f"manifest source {source_id} is missing: {', '.join(missing)}")
        unknown = sorted(set(record) - allowed_source_fields)
        if unknown:
            errors.append(f"manifest source {source_id} has unexpected fields: {', '.join(unknown)}")
        errors.extend(_manifest_record_errors(record, source_id))
        if record.get("ingestion_status") == "ingested":
            if record.get("rights_status") not in {"public-domain-verified", "permission-granted"}:
                errors.append(f"ingested source {source_id} does not have ingestible rights")
            for key in ("rights_evidence", "retrieved_date", "sha256"):
                if not record.get(key):
                    errors.append(f"ingested source {source_id} is missing {key}")
    duplicate_ids = sorted(source_id for source_id in set(manifest_ids) if manifest_ids.count(source_id) > 1)
    if duplicate_ids:
        errors.append(f"source manifest has duplicate ids: {', '.join(duplicate_ids)}")

    doctrines = list_doctrines()
    doctrine_ids = {doctrine.id for doctrine in doctrines}
    voting_ids = doctrine_ids - {"socratic-examination"}
    supported_ids = set(supported_school_ids())
    if voting_ids != supported_ids:
        errors.append(
            "heuristic strategy coverage differs from voting doctrines: "
            f"missing={sorted(voting_ids - supported_ids)}, extra={sorted(supported_ids - voting_ids)}"
        )

    for doctrine in doctrines:
        skill_path = root / "skills" / doctrine.id / "SKILL.md"
        if not skill_path.is_file():
            errors.append(f"doctrine {doctrine.id} has no matching skill")
            skill_text = ""
        else:
            skill_text = skill_path.read_text(encoding="utf-8")
        agent_path = root / "skills" / doctrine.id / "agents" / "openai.yaml"
        if not agent_path.is_file():
            errors.append(f"doctrine {doctrine.id} has no agent descriptor")
        for source in doctrine.sources:
            manifest_source = manifest.get(source.id)
            if manifest_source is None:
                errors.append(f"doctrine {doctrine.id} cites source absent from manifest: {source.id}")
            else:
                if manifest_source.get("author") != source.author:
                    errors.append(f"doctrine {doctrine.id} source metadata differs from manifest: {source.id}")
                if not isinstance(source.title, str) or not source.title.strip():
                    errors.append(f"doctrine {doctrine.id} source has no work title: {source.id}")
                if not isinstance(source.locator, str) or not source.locator.strip():
                    errors.append(f"doctrine {doctrine.id} source has no locator: {source.id}")
        if doctrine.reference_skill:
            reference_path = root / "skills" / doctrine.reference_skill / "SKILL.md"
            if not reference_path.is_file():
                errors.append(f"doctrine {doctrine.id} reference skill is missing: {doctrine.reference_skill}")
            required_link = f"../{doctrine.reference_skill}/SKILL.md"
            if required_link not in skill_text:
                errors.append(f"skill {doctrine.id} does not route through {doctrine.reference_skill}")

    forbidden_contract_phrases = (
        "Return the standard counsel contract plus",
        "Return the standard counsel contract and include",
    )
    for skill_path in (root / "skills").glob("*/SKILL.md"):
        text = skill_path.read_text(encoding="utf-8")
        if any(phrase in text for phrase in forbidden_contract_phrases):
            errors.append(f"skill {skill_path.parent.name} adds fields outside the extension container")

    missing_links = _missing_markdown_links(root)
    errors.extend(f"missing local Markdown link: {path} -> {target}" for path, target in missing_links)

    verified_local_sources = 0
    records_dir = root / "sources" / "corpus" / "records"
    texts_dir = root / "sources" / "corpus" / "texts"
    if records_dir.is_dir():
        for record_path in sorted(records_dir.glob("*.json")):
            try:
                raw_record = json.loads(record_path.read_text(encoding="utf-8"))
                record = SourceRecord.from_dict(raw_record)
                source_id = record.id
                manifest_record = manifest.get(source_id)
                if manifest_record is None:
                    errors.append(f"local source is absent from manifest: {source_id}")
                    continue
                comparable = {
                    "title": record.title,
                    "author": record.author,
                    "translator": record.translator,
                    "edition": record.edition,
                    "publication_year": record.publication_year,
                    "source_url": record.source_url,
                    "rights_status": record.rights_status.value,
                    "rights_evidence": record.rights_evidence,
                    "retrieved_date": record.retrieved_date,
                    "ingestion_status": record.ingestion_status.value,
                    "sha256": record.sha256,
                    "notes": record.notes,
                }
                if any(manifest_record.get(key) != value for key, value in comparable.items()):
                    errors.append(f"local source provenance differs from manifest: {source_id}")
                    continue
                text_path = texts_dir / f"{source_id}.txt"
                payload = text_path.read_bytes()
                digest = hashlib.sha256(payload).hexdigest()
                if digest != record.sha256 or digest != manifest_record.get("sha256"):
                    errors.append(f"local source checksum mismatch: {source_id}")
                    continue
                if record.rights_status.value not in {"public-domain-verified", "permission-granted"}:
                    errors.append(f"local source rights are not ingestible: {source_id}")
                    continue
                verified_local_sources += 1
            except (OSError, KeyError, json.JSONDecodeError, ValidationError) as exc:
                errors.append(f"cannot validate local source record {record_path.name}: {exc}")

    plugin_manifest_path = root / ".codex-plugin" / "plugin.json"
    for required_path in (
        root / "MANIFEST.in",
        root / "setup.py",
        plugin_manifest_path,
        root / "tests" / "test_doctrine_contracts.py",
    ):
        if not required_path.is_file():
            errors.append(f"packaging guard is missing: {required_path.name}")
    if plugin_manifest_path.is_file():
        try:
            plugin_manifest = json.loads(plugin_manifest_path.read_text(encoding="utf-8"))
            if plugin_manifest.get("name") != "phronesis" or plugin_manifest.get("skills") != "./skills/":
                errors.append("plugin manifest does not expose the Phronesis skill tree")
        except (OSError, json.JSONDecodeError, AttributeError) as exc:
            errors.append(f"cannot validate plugin manifest: {exc}")

    return {
        "errors": sorted(errors),
        "doctrine_count": len(doctrines),
        "manifest_source_count": len(manifest_records),
        "verified_local_source_count": verified_local_sources,
    }


def _manifest_record_errors(record: dict[str, Any], source_id: str) -> list[str]:
    errors: list[str] = []
    if not re.fullmatch(r"[a-z0-9-]+", source_id):
        errors.append(f"manifest source {source_id} has an invalid id")
    for key in ("title", "author", "edition"):
        value = record.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"manifest source {source_id} has invalid {key}")
    source_url = record.get("source_url")
    parsed = urlparse(source_url) if isinstance(source_url, str) else None
    if parsed is None or parsed.scheme not in {"http", "https"} or not parsed.netloc:
        errors.append(f"manifest source {source_id} has invalid source_url")
    if record.get("rights_status") not in {
        "public-domain-verified",
        "permission-granted",
        "restricted",
        "verification-required",
    }:
        errors.append(f"manifest source {source_id} has invalid rights_status")
    if record.get("ingestion_status") not in {"candidate", "verified", "ingested", "excluded"}:
        errors.append(f"manifest source {source_id} has invalid ingestion_status")
    retrieved_date = record.get("retrieved_date")
    if retrieved_date is not None:
        try:
            if not isinstance(retrieved_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", retrieved_date):
                raise ValueError
            date.fromisoformat(retrieved_date)
        except ValueError:
            errors.append(f"manifest source {source_id} has invalid retrieved_date")
    sha256 = record.get("sha256")
    if sha256 is not None and (not isinstance(sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", sha256)):
        errors.append(f"manifest source {source_id} has invalid sha256")
    for key in ("translator", "rights_evidence", "notes"):
        value = record.get(key)
        if value is not None and not isinstance(value, str):
            errors.append(f"manifest source {source_id} has invalid {key}")
    publication_year = record.get("publication_year")
    if publication_year is not None and (isinstance(publication_year, bool) or not isinstance(publication_year, int)):
        errors.append(f"manifest source {source_id} has invalid publication_year")
    return errors


def _load_flat_manifest(path: Path) -> list[dict[str, Any]]:
    """Parse this repository's deliberately flat YAML source catalog."""

    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line == "sources:":
            continue
        if raw_line.startswith("  - "):
            if current is not None:
                records.append(current)
            current = {}
            line = raw_line[4:]
        elif raw_line.startswith("    "):
            if current is None:
                raise ValueError(f"field before first source at line {number}")
            line = raw_line[4:]
        else:
            raise ValueError(f"unsupported manifest structure at line {number}")
        if ":" not in line:
            raise ValueError(f"invalid manifest field at line {number}")
        key, raw_value = line.split(":", 1)
        normalized_key = key.strip()
        if normalized_key in current:
            raise ValueError(f"duplicate manifest field {normalized_key!r} at line {number}")
        current[normalized_key] = _yaml_scalar(raw_value.strip())
    if current is not None:
        records.append(current)
    return records


def _yaml_scalar(value: str) -> Any:
    if value in {"null", "~"}:
        return None
    if value in {"true", "false"}:
        return value == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith('"'):
        return json.loads(value)
    return value


def _missing_markdown_links(root: Path) -> list[tuple[str, str]]:
    missing: list[tuple[str, str]] = []
    for path in root.rglob("*.md"):
        if any(part in {".git", "build"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            destination = (path.parent / target.split("#", 1)[0]).resolve()
            if not destination.exists():
                missing.append((str(path.relative_to(root)), target))
    return missing
