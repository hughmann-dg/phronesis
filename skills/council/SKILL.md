---
name: council
description: "Convene the Phronesis Council as a board of isolated, source-first advisor agents for a substantive decision: gather independent advice, debate only when recommendations differ, always red-team the board's advice, deliver a concrete recommendation, preserve dissent, and optionally record it for review."
---

# The Council

Use the sequence **Examine → Advise → Debate if needed → Challenge → Decide → Review**. Treat the Council as a board of independent advisors, not a debating society. The executable `Council.convene` assumes a normalized packet is ready; call the separate examination seam first whenever framing is incomplete.

1. Normalize a Decision Packet and separate facts, assumptions, estimates, opinions, and unknowns.
2. Use Socratic examination if the framing is incomplete.
3. Select differentiated, relevant advisors. Use all nine voting schools by default; narrow the board only when the user requests it or a doctrine explicitly defers.
4. Dispatch one isolated subagent per selected school under the protocol below. The coordinator does not choose an option or draft school answers.
5. Compare recommendations. If all advisors recommend the same option, skip debate. If recommendations differ, debate only the disputed recommendations and their load-bearing assumptions.
6. Synthesize the preliminary board advice without averaging positions into vague consensus.
7. Always run the Red Team as a separate non-voting subagent against that advice. Require holes, failure cases, fragile assumptions, and mitigation tests.
8. Deliver final advice that either survives the challenge or changes in response. Preserve the strongest opposing argument, critical assumption, calibrated confidence, decision-changing evidence, and any dissent.
9. Offer to record predictions and a review date in the decision journal.

Use the host's fresh-context delegation primitive; the names differ, but the isolation barrier does not. Read [Host adapters](references/host-adapters.md) when selecting the mechanism for Codex, ChatGPT Work, Claude Code/Cowork, or GitHub Copilot. If the active surface cannot create isolated advisor contexts, do not imitate a Council by writing multiple voices in the coordinator context. Explain the limitation and offer either one clearly identified school or the deterministic CLI baseline instead.

Required synthesis fields: `recommendation`, `primary_rationale`, `supporting_schools`, `strongest_opposing_argument`, `critical_assumption`, `confidence`, `what_would_change`, and `disagreements`.

## Independent agent protocol

<!-- phronesis:independent-agent-protocol
advisor_context: fresh-per-school
history: packet-skill-reference-contract-only
source_order: before-option-evaluation
collection_barrier: all-initial-before-comparison
coordinator_preselection: forbidden
coordinator_rewrite: forbidden
-->

The coordinator orchestrates; it must not make a private preliminary decision and then ask the schools to justify it.

1. Create a fresh delegated agent task for every selected voting school. Never ask one agent to produce more than one school's initial counsel.
2. Start each advisor without inherited Council conversation history. Give it only the normalized Decision Packet, its assigned counsel skill, the linked reference knowledge skill, and the standard counsel response contract. Do not include another school's output, the coordinator's preferred option, a preliminary synthesis, or a target vote.
3. Require the advisor to read its counsel skill, route through its reference knowledge skill, and read the topic-relevant source-book chapters before evaluating the options. Exact quotations require retrieval from the verified primary text; otherwise the advisor must cite the work and locator and clearly synthesize in its own words.
4. Require the advisor to derive its source-grounded feedback first and propose its own recommendation last. A citation added after an answer has already been selected does not satisfy this protocol.
5. Collect every initial response before revealing any conclusion to any other advisor. If concurrency is limited, dispatch in waves using fresh, history-free tasks so later advisors cannot see earlier answers.
6. Validate each response against the public counsel contract. Return an invalid response to the same advisor with only the validation errors and that advisor's own work; the coordinator must not silently rewrite it.
7. Only after all initial responses are valid may the coordinator compare recommendations, run targeted cross-examination, or synthesize preliminary board advice.

The Red Team receives the completed initial counsels and preliminary recommendation only after this independence barrier. It attacks but does not vote. Final synthesis must identify which recommendations came from which independent advisors and preserve material dissent.

## School Routing

- Route incomplete framing through [Socratic Examination](../socratic-examination/SKILL.md) before convening; it asks questions and never votes.
- Route particulars, character, and flourishing through [Aristotelian Counsel](../aristotelian-counsel/SKILL.md).
- Route agency, judgment, duty, and adversity through [Stoic Counsel](../stoic-counsel/SKILL.md).
- Route incentives, power, coalitions, and resistance through [Machiavellian Realism](../machiavellian-realism/SKILL.md).
- Route objectives, friction, concentration, and execution through [Clausewitzian Strategy](../clausewitzian-strategy/SKILL.md).
- Route position, information, timing, and optionality through [Sun Tzu Positioning](../sun-tzu-positioning/SKILL.md).
- Route practice, tool fit, transition points, and renewal through [Musashi Adaptive Strategy](../musashi-adaptive-strategy/SKILL.md).
- Route evidence, causal inference, and overconfidence through [Humean Skepticism](../humean-skepticism/SKILL.md).
- Route priors, updates, sensitivity, and information value through [Bayesian Analysis](../bayesian-analysis/SKILL.md).
- Route stakeholder benefits, harms, distribution, and second-order effects through [Consequentialist Analysis](../consequentialist-analysis/SKILL.md).

Every doctrinal claim must identify a source work and locator. Never simulate historical figures as personalities.
