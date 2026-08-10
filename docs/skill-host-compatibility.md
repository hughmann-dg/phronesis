# Skill host compatibility

Phronesis uses the open Agent Skills structure: one directory per skill, a `SKILL.md` entry point, and only portable `name` and `description` frontmatter. The canonical tree is `skills/`; relative links keep counsel skills attached to their source-work skills. Generated `.agents/skills` adapters provide repository discovery without duplicating doctrine or sources.

| Host | Discovery or package seam | Full Council execution |
| --- | --- | --- |
| Codex | `.agents/skills` or `.codex-plugin/plugin.json` | Yes, with fresh non-forked subagents |
| ChatGPT Work | OpenAI plugin manifest | When the active Work environment exposes fresh-context delegation; otherwise safe fallback |
| Claude Code | `.claude-plugin/plugin.json` | Yes, with Agent/subagent delegation enabled |
| Claude Cowork | Uploaded or marketplace-installed Claude plugin | Yes, with Cowork subagent coordination enabled |
| GitHub Copilot | `.agents/skills` | Yes in Copilot CLI; also in IDE agent mode when subagents are enabled; other surfaces use safe fallback |

The repository audit enforces portable skill names and descriptions, matching directory names, both plugin manifests, exact discovery adapters, local links, and the Council's isolation protocol.

Compatibility has two levels. Discovery means the host can load the skill. Full Council execution additionally requires fresh-context delegation. A host that only satisfies discovery must never manufacture multiple advisor voices in one context.

## Verification

Run the portable repository checks on every change:

```text
python -m phronesis audit --root .
python -m unittest discover -s tests -v
python -m phronesis benchmark benchmarks/cases.json
python scripts/sync_skill_adapters.py --check
```

When the vendor tools are installed, also run their native smoke checks:

```text
gh skill publish skills --dry-run
claude --plugin-dir .
```

The GitHub command validates the canonical tree against the Agent Skills specification. In Claude Code, confirm `/phronesis:council` is listed. In Codex, confirm `$council` and a linked source-work skill are listed. ChatGPT Work and Cowork require an install-and-invoke smoke test in their plugin UI.

Host syntax is allowed only in packaging and the Council's host-adapter reference. School doctrine and source-work content remain host-neutral.

## Platform references

- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills)
- [Anthropic: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Anthropic: Claude Code plugins](https://code.claude.com/docs/en/plugins)
- [GitHub: Adding agent skills for Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
