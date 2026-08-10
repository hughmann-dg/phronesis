---
name: council
description: "Convene the Phronesis Council as a board of advisors for a substantive decision: gather independent source-grounded advice, debate only when recommendations differ, always red-team the board's advice, deliver a concrete recommendation, preserve dissent, and optionally record it for review."
---

# The Council

Use the sequence **Examine → Advise → Debate if needed → Challenge → Decide → Review**. Treat the Council as a board of independent advisors, not a debating society. The executable `Council.convene` assumes a normalized packet is ready; call the separate examination seam first whenever framing is incomplete.

1. Normalize a Decision Packet and separate facts, assumptions, estimates, opinions, and unknowns.
2. Use Socratic examination if the framing is incomplete.
3. Select differentiated, relevant advisors. Use all nine voting schools by default; narrow the board only when the user requests it or a doctrine explicitly defers.
4. Give each advisor only the packet and its doctrine. Collect every response before revealing another advisor's conclusion.
5. Compare recommendations. If all advisors recommend the same option, skip debate. If recommendations differ, debate only the disputed recommendations and their load-bearing assumptions.
6. Synthesize the preliminary board advice without averaging positions into vague consensus.
7. Always run the Red Team against that advice. Require holes, failure cases, fragile assumptions, and mitigation tests; the Red Team challenges but never votes.
8. Deliver final advice that either survives the challenge or changes in response. Preserve the strongest opposing argument, critical assumption, calibrated confidence, decision-changing evidence, and any dissent.
9. Offer to record predictions and a review date in the decision journal.

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
