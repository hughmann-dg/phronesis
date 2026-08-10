---
name: bayes-works
description: "Reference knowledge base from the rights-verified 1763 Royal Society publication of Thomas Bayes's Essay. Use for inverse probability, chance, expectation, binomial observations, Proposition 9, the scholium, approximation rules, priors, likelihoods, historical Bayes, or exact proposition and page locators."
---

# Thomas Bayes — Essay on the Doctrine of Chances

**Author**: Thomas Bayes | **Communicated by**: Richard Price | **Publication**: *Philosophical Transactions*, vol. 53 (1763), pp. 370-418 | **Provider OCR words**: ~15,069 | **Reference units**: 6 | **Generated**: 2026-08-09

## How to Use This Skill

- Use proposition and original-page locators, not OCR line numbers.
- Retrieve `bayes-essay` before source-grounded claims. For quotation or formulas, verify the Royal Society scan because the provider OCR misreads long-s typography, symbols, and layout.
- Distinguish Richard Price's covering letter and editorial explanation from Bayes's essay.
- Distinguish Bayes's specific inverse-probability problem from the broader modern Bayesian workflow.
- Do not turn historical mathematical assumptions into default priors for high-stakes decisions.

## Core Frameworks and Mental Models

### Reverse the direction of a chance problem

Bayes asks how observed successes and failures bear on the unknown chance governing future trials. This inverse question differs from calculating outcomes when the chance is already known. (Price letter and Bayes's Problem, pp. 370-376)

### Define the event model before calculating

Section I builds definitions and propositions about chance, expectation, contrary events, and repeated independent trials. Modern use should state hypotheses, event structure, independence assumptions, and what is being conditioned on before applying a formula. (Section I, pp. 376-389)

### Make the prior-generating construction visible

Section II introduces a geometrical experiment that makes the unknown chance itself arise from a uniform placement. This is a specific modeling postulate, not proof that ignorance always implies a uniform prior. (Section II postulate and experiment, pp. 389-393)

### Condition observations on possible chances

The central propositions relate an observed count of one event and its contrary to intervals of possible underlying chance. Proposition 9 provides the inverse result underlying later interpretations associated with Bayes's theorem. (Section II, Proposition 9, pp. 395-399)

### Express uncertainty as intervals and odds

The scholium translates the result into rules for finding the probability that an unknown chance lies between bounds, then develops approximations. Preserve uncertainty and sensitivity rather than reporting an unsupported point estimate. (Scholium and Rules 1-3, pp. 399-418)

### Keep history narrower than modern doctrine

Bayes's paper does not itself supply today's full vocabulary of priors, likelihood ratios, posterior predictive checks, decision utility, causal inference, or value of information. Those are later extensions and should be labeled accordingly.

## Chapter Index

| # | Reference unit | Main topics |
|---|---|---|
| [ch01](chapters/ch01-edition-boundaries.md) | Edition boundaries | scan, OCR, Price, pages, attribution |
| [ch02](chapters/ch02-letter-and-problem.md) | Price letter and problem | inverse probability, purpose, observed trials |
| [ch03](chapters/ch03-section-one.md) | Section I | chance, expectation, contrary events, repeated trials |
| [ch04](chapters/ch04-section-two.md) | Section II | postulate, geometrical experiment, conditioning |
| [ch05](chapters/ch05-proposition-nine-scholium.md) | Proposition 9 and scholium | inverse result, intervals, approximations |
| [ch06](chapters/ch06-executable-limits.md) | Executable limits | OCR, priors, dependence, precision, modern extensions |

## Topic Index

- **Approximation rules** -> ch05
- **Chance and probability** -> ch03
- **Conditioning and inverse probability** -> ch02, ch04-ch05
- **Expectation** -> ch03
- **Independence and repeated trials** -> ch03, ch06
- **Intervals and uncertainty** -> ch05
- **Prior construction and uniformity** -> ch04, ch06
- **Price versus Bayes attribution** -> ch01-ch02
- **Proposition 9** -> ch05
- **Scan and OCR verification** -> ch01, ch06

## Supporting Files

- [glossary.md](glossary.md) — historical and modern terms with attribution
- [patterns.md](patterns.md) — reconstructed Bayesian decision patterns
- [cheatsheet.md](cheatsheet.md) — routing, calculations, and hard stops

## Sources and Limits

Primary edition: Thomas Bayes, “An Essay towards solving a Problem in the Doctrine of Chances,” communicated by Richard Price, *Philosophical Transactions of the Royal Society of London* 53 (1763), article LII, pp. 370-418 (`bayes-essay`). The ingested artifact is provider OCR associated with the public-domain scan; rights verification is scoped to the United States.

The OCR is poor for exact language and mathematics. Verify every quotation, symbol, bound, and equation against the scan. Modern Bayesian analysis is a later interpretive and mathematical development. High-stakes probabilities require domain evidence, dependence checks, calibration, sensitivity analysis, and independent ethical constraints.
