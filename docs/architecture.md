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

`Council` depends on the small `Reasoner` protocol: `counsel(packet, doctrine) -> CounselResponse`. A model adapter receives only those two inputs, requests structured output, and attaches retrieved source passages. The Council validates school identity, option membership, confidence, required fields, declared source IDs and locators, grounding mode, and the extension container before cross-examination. School-specific fields remain nested under `extensions`.

`Council.convene` assumes packet intake is complete. The total-agent workflow calls the separate `examine` seam first when objectives, terms, options, or evidence remain incomplete; a programmatic caller that has already completed intake may convene directly.
