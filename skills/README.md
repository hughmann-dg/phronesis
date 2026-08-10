# Skill contribution contract

Every school is a procedure, not a historical personality.

When adding or changing a school:

1. Add or update the executable `Doctrine`, including source IDs and precise work locators.
2. Give every voting doctrine an explicit deterministic baseline strategy; do not rely on option order for ties.
3. Add the matching `skills/<school-id>/SKILL.md` and agent descriptor.
4. If a rights-verified reference skill exists, declare `reference_skill` on the doctrine and route the counsel skill through it. Every voting skill must include a `Source-first deliberation` protocol that reads relevant source-book units before evaluating options. Retrieve the primary text before quoting.
5. Return the shared counsel contract. Put school-specific structured analysis only inside `extensions`.
6. Preserve independent counsel: dispatch each school in a fresh subagent context, do not let the coordinator preselect an answer, and do not let a school see another conclusion until its own validated response exists.
7. Keep the red team non-voting.
8. Add manifest records before citing source IDs. Candidate records use explicit nulls; ingested records require edition-specific rights evidence, retrieval date, and SHA-256.
9. Add public-seam tests and run `phronesis audit --root .`, the full unit suite, and the benchmark.
