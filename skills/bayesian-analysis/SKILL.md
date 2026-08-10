---
name: bayesian-analysis
description: Represent uncertainty with priors, likelihoods, updates, expected outcomes, sensitivity ranges, and value of information. Use for forecasts or decisions where new evidence can materially change confidence.
---

# Bayesian Analysis

## Source-first deliberation

<!-- phronesis:source-first-protocol
reference_skill: bayes-works
source_order: before-option-evaluation
recommendation_order: after-feedback
-->

Before analyzing the options or choosing a recommendation, load [bayes-works](../bayes-works/SKILL.md), then read [Proposition 9 and its scholium](../bayes-works/chapters/ch05-proposition-nine-scholium.md) together with the reference skill's executable limits. Derive the hypotheses, uncertainty ranges, update logic, and information value before proposing an answer. Do not choose an option first and manufacture probabilities that support it.

1. Define competing hypotheses and a defensible prior or range.
2. Separate data from subjective inputs.
3. Estimate how likely the evidence is under each hypothesis.
4. Update confidence and show sensitivity to uncertain inputs.
5. Compare expected outcomes and the value and cost of further information.

Never launder guesses through precise numbers. Use ranges when inputs do not justify point estimates. Route source-grounded questions through [bayes-works](../bayes-works/SKILL.md) before quoting. Ground the conceptual basis in Bayes's *Essay*, Proposition 9 and its scholium. Retrieve the primary scan/OCR record by source ID, cite proposition and original-page locators, verify formulas against the scan, and do not invent quotations.

Return the standard counsel contract. Put `priors`, `updates`, `sensitivity`, and `information_value` inside the contract's `extensions` object. Explain calculations plainly.
