# Decision model

A Decision Packet is the boundary between user framing and deliberation. It requires a decision, an objective, and at least two distinct options.

Claims are intentionally separated:

| Class | Meaning | Typical treatment |
|---|---|---|
| Fact | Observation with a traceable basis | Verify provenance |
| Assumption | Belief the plan depends on | Seek falsification |
| Estimate | Quantified or bounded judgment | Carry confidence |
| Opinion | Preference or interpretation | Do not present as evidence |
| Unknown | Material unresolved question | Estimate information value |

The packet also captures constraints, stakeholders, time horizon, reversibility, current preference, and confidence. A current preference must exactly match an option so downstream comparisons remain unambiguous.

The executable validator is `DecisionPacket.from_dict`; the portable contract is `schemas/decision-packet.schema.json`.
