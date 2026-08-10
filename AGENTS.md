# Phronesis contributor guidance

- Preserve the distinction between primary source, interpreted doctrine, and executable behavior.
- Never implement a school as historical personality role-play.
- Keep public output compatible with the JSON schemas in `schemas/`.
- Keep independent counsel independent: a school must not see another school's conclusion before its own response exists.
- The red team attacks but does not vote.
- Cite a source work and locator for every important doctrinal claim. Do not invent quotations.
- Do not ingest a source until its specific edition or translation has verified rights evidence.
- Runtime code should remain standard-library-only unless a dependency is justified in an architecture decision.
- Every new school must add a doctrine, an explicit baseline strategy, a matching skill, manifest source IDs with locators, and public-seam tests. School-specific output belongs under `extensions`.
- When a counsel skill has a reference knowledge skill, declare it on the doctrine and explicitly route through it before quoting.
- Run `python -m phronesis audit --root .`, `python -m unittest discover -s tests -v`, and the benchmark before committing.
