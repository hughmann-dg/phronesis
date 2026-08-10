# Reference Unit 1: Edition, OCR, and Attribution Boundaries

## Core Idea

The ingested artifact is provider OCR derived from a scan of the 1763 *Philosophical Transactions* paper. It is useful for retrieval but unreliable for exact words, symbols, equations, and page layout.

## Frameworks Introduced

- **Scan-First Formula Rule**: Verify every equation, bound, superscript, integral, and numerical rule against the PDF scan.
  - When to use: Mathematical content affects analysis.
  - How: Route by OCR and page marker, then inspect the scan.
- **Price-Bayes Attribution Split**: Separate Richard Price's covering letter and editorial framing from Bayes's essay.
  - When to use: Stating the paper's purpose or historical significance.
  - How: Identify whether the passage precedes Bayes's stated Problem and Section I.
- **Adjacent-Matter Filter**: Exclude preceding and following journal articles and digitization boilerplate captured by OCR.

## Key Concepts

- **Article LII**: Paper designation in volume 53.
- **Original pages 370-418**: Stable locator range.
- **Provider OCR**: Machine text retaining long-s errors and layout corruption.
- **Scan**: Authoritative visual artifact for quotation and formulas.

## Anti-patterns

- **OCR quotation**: Reproducing “propofition” or damaged text as original spelling.
- **Formula reconstruction by guess**: Repairing symbols from context without scan verification.
- **Editor collapse**: Attributing Price's claims to Bayes.

## Worked Example

An analyst finds an OCR line around Proposition 9 that appears to place a denominator incorrectly. The analyst cites pp. 395-399, opens the scan, verifies the expression, and records the OCR defect rather than silently correcting the source corpus.

## Key Takeaways

1. OCR routes; scan verifies.
2. Cite original page and proposition.
3. Separate Price from Bayes.
4. Exclude adjacent journal matter.

## Connects To

- **ch02**: Price's letter and Bayes's Problem.
- **ch05**: Highest formula-verification risk.
