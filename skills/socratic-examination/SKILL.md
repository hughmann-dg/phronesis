---
name: socratic-examination
description: Challenge the framing, premises, definitions, option set, and confidence of a decision before advice. Use for poorly framed choices, assumption audits, or requests to question a preferred option without yet recommending one.
---

# Socratic Examination

Do not impersonate Socrates and do not recommend an option during the initial examination.

1. Restate the objective and ambiguous terms.
2. Separate observations from assumptions, estimates, opinions, and unknowns.
3. Ask what evidence supports each decisive premise and what would falsify it.
4. Test whether the constraints and option set are real and complete.
5. Ask what happens if the user does nothing.
6. End with the few questions whose answers have the greatest decision value.

Ground the method in Plato's *Apology* 21d-23b and *Gorgias* 454c-461b. Cite the relevant work and locator; do not invent quotations.

Return the standard counsel contract with `recommendation: null`; use `reasoning` for the prioritized questions. Put `clarified_decision`, `contested_terms`, `assumptions_treated_as_facts`, `missing_options`, and `evidence_needed` inside the contract's `extensions` object.
