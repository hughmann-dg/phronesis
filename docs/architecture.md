# Architecture

Phronesis separates evidence, interpretation, and behavior so a plausible answer cannot masquerade as a sourced one.

```mermaid
flowchart LR
    A["Edition-specific primary text"] --> B["Rights and provenance record"]
    B --> C["Local passage retrieval"]
    A --> D["Extracted doctrine"]
    D --> E["School reasoning procedure"]
    C --> E
    P["Decision Packet"] --> E
    E --> F["Independent counsel responses"]
    F --> G["Cross-examination"]
    G --> H["Non-voting red team"]
    H --> I["Arbiter synthesis"]
    I --> J["Decision journal and review"]
```

## Modules

- `models.py` validates Decision Packets and claim classifications.
- `doctrines.py` contains explicit school doctrine and source locators.
- `reasoning.py` is the transparent local baseline.
- `council.py` enforces independent counsel and the contest/arbiter protocol.
- `sources.py` enforces source rights, hashes text, and retrieves passages.
- `journal.py` stores atomic, portable decision records and review analytics.
- `benchmark.py` evaluates contracts and citation presence across domains.
- `cli.py` exposes the complete workflow as JSON commands.

## Model-backed extension

`Council` depends on the small `Reasoner` protocol: `counsel(packet, doctrine) -> CounselResponse`. A model adapter should receive only those two inputs, request structured output, validate it against `counsel-response.schema.json`, and attach retrieved source passages. Cross-examination and synthesis should continue to operate on validated contracts rather than free-form chat.
