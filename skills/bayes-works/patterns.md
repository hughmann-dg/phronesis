# Patterns — Bayes Works

These are modern reconstructions grounded in the paper's inverse-probability structure, not procedures stated verbatim by Bayes.

## Model-Before-Update

**When to use**: Evidence is being inserted into a formula before hypotheses are clear.

**How**: Define competing hypotheses or parameter, observed event, sampling process, independence assumptions, and selection mechanism.

**Trade-offs**: Prevents meaningless precision but exposes model disagreement that arithmetic cannot resolve. (Problem; Section I)

## Prior Provenance Record

**When to use**: An update depends materially on a prior.

**How**: State whether the prior comes from base rates, prior studies, expert judgment, or a modeling convention; show alternatives.

**Trade-offs**: Makes assumptions auditable but cannot manufacture evidence. (Section II postulate, interpreted)

## Interval-First Update

**When to use**: Data are sparse or model inputs uncertain.

**How**: Report a credible range or several sensitivity cases; identify which inputs move the conclusion.

**Trade-offs**: More honest than a point estimate but less rhetorically simple. (Proposition 9 and scholium, adapted)

## Diagnostic-Evidence Test

**When to use**: New evidence is dramatic but may be equally likely under several hypotheses.

**How**: Compare probability of the evidence under each hypothesis; update only to the degree the evidence discriminates.

**Trade-offs**: Reduces narrative overreaction, but likelihood estimates may themselves be uncertain. (Modern extension)

## Decision Separation

**When to use**: A probability update is treated as an automatic action recommendation.

**How**: Separate belief update from outcome values, rights, risk tolerance, reversibility, and value of more information.

**Trade-offs**: Prevents category errors; requires another decision model beyond Bayes's paper. (Modern extension)
