---
name: council
description: "Run the Phronesis Council workflow for a substantive decision: normalize intake, gather independent school counsel, cross-examine disagreements, red-team the leader, synthesize a concrete decision, preserve dissent, and optionally record it for review."
---

# The Council

Use the sequence **Examine → Counsel → Contest → Decide → Review**. The executable `Council.convene` assumes a normalized packet is ready for deliberation; call the separate examination seam first whenever framing is incomplete.

1. Normalize a Decision Packet and separate facts, assumptions, estimates, opinions, and unknowns.
2. Use Socratic examination if the framing is incomplete.
3. Select differentiated, relevant schools. Use all nine voting schools by default; narrow the set only when the user requests it or a doctrine explicitly defers. Give each only the packet and its doctrine; collect counsel independently before sharing conclusions.
4. Cross-examine load-bearing assumptions across schools.
5. Run the red team against the leading option without giving it a vote.
6. Act as arbiter. Choose an option instead of averaging positions into vague consensus.
7. Preserve the strongest opposing argument, critical assumption, calibrated confidence, and decision-changing evidence.
8. Offer to record predictions and a review date in the decision journal.

Required synthesis fields: `recommendation`, `primary_rationale`, `supporting_schools`, `strongest_opposing_argument`, `critical_assumption`, `confidence`, `what_would_change`, and `disagreements`.

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
