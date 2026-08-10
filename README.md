# Phronesis

Phronesis is a source-grounded decision-advisory engine. It applies explicit reasoning traditions to a normalized decision, preserves disagreement, attacks the leading option, makes a concrete recommendation, and records forecasts for later review.

It does **not** simulate famous people. A response is produced by a documented doctrine derived from cited works.

## What works

- Decision Packets distinguish facts, assumptions, estimates, opinions, and unknowns.
- Ten explicit doctrines are available: Socratic Examination handles non-voting intake, and the default Council convenes the other nine voting lenses.
- The interactive Council skill dispatches source-first counsel to isolated advisor agents, collects their recommendations before comparison, debates only when recommendations differ, and always red-teams its preliminary advice before final synthesis.
- Every counsel response includes a philosophical basis and source locator.
- A rights-aware local corpus can ingest and retrieve verified primary texts.
- The decision journal records choices, confidence, predictions, outcomes, and lessons.
- A five-domain benchmark checks validated contracts, declared citations, and verified-primary-source coverage separately.
- The package uses only the Python standard library at runtime.

The included in-process reasoner is a transparent deterministic baseline with explicit school-specific signals and stable, order-independent tie breaking. It does not create model agents, and its optional source retrieval grounds citations rather than supplying full doctrinal deliberation. The interactive Council skill implements the isolated source-first agent workflow. For programmatic model integration, the `Reasoner` protocol in `phronesis.council` is the seam: the adapter is responsible for giving each school a fresh source-first context, and every response is validated before it enters conditional debate or synthesis.

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

## Install the skills

Phronesis keeps one canonical Agent Skills tree in `skills/`. The OpenAI and Claude plugin manifests expose it to ChatGPT Work, Codex, Claude Code, and Claude Cowork. Codex repository mode and GitHub Copilot discover generated adapters in `.agents/skills`; each adapter routes to the canonical skill, so doctrine and source books are never copied between hosts.

### Codex and ChatGPT Work

The repository root is a skills-only OpenAI plugin through `.codex-plugin/plugin.json`. A Python install makes the CLI available but does not register the plugin. From this checkout, give Codex this exact request:

```text
$plugin-creator Add the existing plugin at C:\Users\mikes\Documents\Codex\phronesis to my personal marketplace, preserving this checkout as the plugin source.
```

Refresh Codex, open `/plugins`, install **Phronesis** from the Personal marketplace, and start a new task. The same plugin can be distributed to ChatGPT Work through the shared plugin directory. Confirm that `aristotelian-counsel` and `aristotle-works` both appear among its bundled skills.

See the official [plugin packaging guide](https://developers.openai.com/plugins/build/plugins) for marketplace and distribution options.

### Claude Code and Cowork

The repository root is also a Claude plugin through `.claude-plugin/plugin.json`. Test it directly in Claude Code:

```text
claude --plugin-dir .
```

Invoke `/phronesis:council`, or let Claude select it from its description. In Claude Desktop or Cowork, upload the repository as a custom plugin or distribute it through a Claude plugin marketplace. Claude Code and Cowork can run the full Council when Agent/subagent delegation is enabled.

### GitHub Copilot

Open the repository in a supported Copilot agent surface. Copilot discovers the adapters under `.agents/skills`; invoke `council` explicitly or ask for a Phronesis Council decision review. Copilot CLI is the verified full-Council surface; IDE agent mode also works when subagents are enabled. The adapters contain no Copilot-only doctrine or source content.

The Council requires fresh-context delegation. On hosts with subagent/custom-agent orchestration it assigns one school per isolated agent. ChatGPT Work can discover and invoke the plugin, but it runs the full Council only when the active Work environment exposes fresh-context delegation. On any surface without that capability, the skill refuses to simulate nine independent votes in one context and offers a single-school or deterministic CLI fallback.

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
skills/         canonical school, source-work, and Council procedures
.agents/skills/ generated repository-discovery adapters
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
