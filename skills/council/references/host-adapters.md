# Host adapters

The Council depends on semantic capabilities, not vendor-specific tool names. Preserve these invariants on every host:

- one fresh context per voting school;
- no inherited Council conversation or other advisor conclusion;
- only the Decision Packet, assigned counsel skill, linked source-work skill, and counsel response contract enter the initial task;
- all initial responses are collected before comparison;
- the Red Team runs separately after preliminary synthesis and never votes.

## Codex and ChatGPT Work

Codex is a full-Council surface when its subagent tools are enabled. Use fresh, non-forked subagents and pass only the allowed materials.

ChatGPT Work loads the Council through the same OpenAI plugin package. Run the full Council only when the active Work environment exposes a fresh-context delegated-task primitive. Start every advisor without inherited turns and pass only the allowed materials. Run advisors concurrently when capacity permits; otherwise use fresh tasks in waves. If no such primitive is available, use the capability fallback instead of simulating independent counsel.

## Claude Code and Cowork

Claude Code and Cowork are full-Council surfaces when Agent/subagent delegation is enabled. Use a fresh context for each school. Do not use a fork that inherits the Council conversation. The Claude plugin manifest exposes the same canonical skill tree to both products.

## GitHub Copilot

GitHub Copilot CLI is a verified full-Council surface through its separate-context subagents. Copilot IDE agent mode is also suitable when subagents are enabled. Assign exactly one school to each initial general-purpose or custom subagent. Other Copilot surfaces may discover the skill without exposing delegation; use the capability fallback there. The repository-level `.agents/skills` adapters route to the canonical `skills/` tree.

## Capability fallback

If the active surface has no fresh-context delegation primitive, stop before producing simulated votes. Offer one of these transparent fallbacks:

1. run a single named school as counsel;
2. run `phronesis council PACKET.json` and label the output as the deterministic in-process baseline;
3. move the decision to a supported surface and reconvene the full Council.
