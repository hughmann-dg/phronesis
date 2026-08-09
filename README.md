# Phronesis

Phronesis is a source-grounded decision-advisory engine. It applies explicit reasoning traditions to a normalized decision, preserves disagreement, attacks the leading option, makes a concrete recommendation, and records forecasts for later review.

It does **not** simulate famous people. A response is produced by a documented doctrine derived from cited works.

## What works

- Decision Packets distinguish facts, assumptions, estimates, opinions, and unknowns.
- Nine explicit doctrines are available; the default Council uses Aristotle, Stoic, Machiavellian, Clausewitzian, and Humean lenses.
- The Council runs independent counsel, cross-examination, a non-voting red team, and arbiter synthesis.
- Every counsel response includes a philosophical basis and source locator.
- A rights-aware local corpus can ingest and retrieve verified primary texts.
- The decision journal records choices, confidence, predictions, outcomes, and lessons.
- A five-domain benchmark checks contracts and citation coverage.
- The package uses only the Python standard library at runtime.

The included reasoner is a transparent deterministic baseline. The `Reasoner` protocol in `phronesis.council` is the seam for a model-backed implementation; doctrine, independence, validation, citations, and journaling remain unchanged.

## Install

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e .
```

Or run directly from the repository:

```powershell
$env:PYTHONPATH = "src"
python -m phronesis council tests/fixtures/system_migration.json
```

## Core commands

```text
phronesis validate PACKET.json
phronesis examine PACKET.json
phronesis ask stoic-counsel PACKET.json
phronesis council PACKET.json
phronesis doctrines [SCHOOL]
phronesis benchmark benchmarks/cases.json
```

Record a decision:

```powershell
phronesis council decision.json --record `
  --user-decision "incremental migration" `
  --user-confidence 0.75 `
  --review-date 2027-03-31 `
  --predicted-outcome "No major outage"
```

Review it later:

```text
phronesis journal list
phronesis journal review ENTRY_ID --actual-outcome "..." --lesson "..."
phronesis journal insights
```

Ingest and search a rights-verified primary text:

```text
phronesis sources ingest text.txt metadata.json
phronesis sources search "practical wisdom particulars"
phronesis ask aristotelian-counsel decision.json
```

Metadata must conform to `schemas/source-record.schema.json`. Ingestion refuses `verification-required` and `restricted` records.
Counsel commands search `sources/corpus` by default; pass `--corpus-dir` to use another verified corpus.

## Python API

```python
import json
from phronesis.council import Council
from phronesis.models import DecisionPacket

packet = DecisionPacket.from_dict(json.load(open("decision.json", encoding="utf-8")))
result = Council().convene(packet)
print(result.synthesis.recommendation)
```

## Repository map

```text
src/phronesis/  executable models, doctrines, Council, corpus, journal, CLI
skills/         reusable school and Council procedures
schemas/        JSON contracts
sources/        provenance manifest and rights-controlled corpus location
benchmarks/     five-domain evaluation suite
docs/           architecture, protocols, policy, and roadmap
tests/          behavior tests at public seams
```

## Verify

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m phronesis benchmark benchmarks/cases.json
```

Licensed under Apache-2.0. External source texts are **not** covered by that license; see `docs/source-policy.md` and `sources/manifest.yaml`.
