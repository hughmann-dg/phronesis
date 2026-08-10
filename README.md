# Phronesis

Phronesis is a source-grounded decision-advisory engine. It applies explicit reasoning traditions to a normalized decision, preserves disagreement, attacks the leading option, makes a concrete recommendation, and records forecasts for later review.

It does **not** simulate famous people. A response is produced by a documented doctrine derived from cited works.

## What works

- Decision Packets distinguish facts, assumptions, estimates, opinions, and unknowns.
- Ten explicit doctrines are available: Socratic Examination handles non-voting intake, and the default Council convenes the other nine voting lenses.
- The Council runs independent counsel, cross-examination, a non-voting red team, and arbiter synthesis.
- Every counsel response includes a philosophical basis and source locator.
- A rights-aware local corpus can ingest and retrieve verified primary texts.
- The decision journal records choices, confidence, predictions, outcomes, and lessons.
- A five-domain benchmark checks validated contracts, declared citations, and verified-primary-source coverage separately.
- The package uses only the Python standard library at runtime.

The included reasoner is a transparent deterministic baseline with explicit school-specific signals and stable, order-independent tie breaking. It is useful for exercising the system, but it is not a substitute for full doctrinal deliberation. The `Reasoner` protocol in `phronesis.council` is the seam for a model-backed implementation; every response is validated before it enters cross-examination or synthesis.

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

## Install the Codex plugin

The repository root is a skills-only Codex plugin through `.codex-plugin/plugin.json`. A Python install makes the CLI available but does not register Codex skills. From this checkout, give Codex this exact request:

```text
$plugin-creator Add the existing plugin at C:\Users\mikes\Documents\Codex\phronesis to my personal marketplace, preserving this checkout as the plugin source.
```

Refresh Codex, open the CLI with `codex`, enter `/plugins`, install **Phronesis** from the Personal marketplace, and start a new task. Confirm that `aristotelian-counsel` and `aristotle-works` both appear among its bundled skills. After installation, invoking `aristotelian-counsel` explicitly routes through the bundled `aristotle-works` reference skill before quoting.

See the official [plugin packaging guide](https://developers.openai.com/plugins/build/plugins) for marketplace and distribution options.

## Core commands

```text
phronesis validate PACKET.json
phronesis examine PACKET.json
phronesis ask stoic-counsel PACKET.json
phronesis council PACKET.json
phronesis doctrines [SCHOOL]
phronesis benchmark benchmarks/cases.json
phronesis audit --root .
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

Metadata must conform to `schemas/source-record.schema.json`, be marked `verified` or `ingested`, and include a retrieval date. Ingestion refuses `verification-required` and `restricted` records. Retrieval revalidates the persisted rights status and SHA-256 before returning a passage.
Counsel commands search `sources/corpus` by default; pass `--corpus-dir` to use another verified corpus.

School-specific structured analysis belongs inside the counsel contract's `extensions` object; top-level fields remain stable across schools.

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
python -m phronesis benchmark benchmarks/cases.json --corpus-dir sources/corpus
python -m phronesis audit --root .
```

Licensed under Apache-2.0. External source texts are **not** covered by that license; see `docs/source-policy.md` and `sources/manifest.yaml`.
