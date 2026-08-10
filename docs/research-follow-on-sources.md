# Research: follow-on edition-verified sources

Research and acquisition dates: 2026-08-09; Musashi promotion 2026-08-10
Rights jurisdiction: United States

## Outcome

The follow-on batch acquired and ingested three remaining doctrine dependencies: `sun-tzu-art-of-war`, `mill-utilitarianism`, and `bayes-essay`. The same working batch completed the previously recommended `plato-dialogues` acquisition. Each ingested manifest record includes edition-specific rights evidence, retrieval date, SHA-256, and an ignored local corpus record.

`musashi-book-five-rings` was initially added as `verification-required`. On 2026-08-10, research found a 1909 Japanese parent edition whose NDL record marks the work `pdm`, plus an original-language access transcription keyed to that edition. The Japanese text was ingested without any modern English translation; all English skill content is labeled synthesis.

## `sun-tzu-art-of-war`

- **Provider title:** *Sun Tzŭ on the Art of War: The Oldest Military Treatise in the World*
- **Author:** Sun Tzu
- **Translator/commentator:** Lionel Giles
- **Edition:** Luzac & Co., London, 1910
- **Provider:** [Project Gutenberg eBook #66706](https://www.gutenberg.org/ebooks/66706)
- **Rights evidence:** the edition catalog states, “Copyright: Public domain in the USA.”
- **Acquisition endpoint:** `https://www.gutenberg.org/ebooks/66706.txt.utf-8`

The title matter identifies the 1910 publisher and the file as a complete transcription of Giles's translation with introduction and critical notes. Because translation, Chinese text, Giles's notes, and traditional commentaries are interleaved, the reference skill must identify textual layers before attribution.

## `mill-utilitarianism`

- **Provider title:** *Utilitarianism*
- **Author:** John Stuart Mill
- **Translator:** not applicable
- **Edition:** Longmans, Green, and Co., London, seventh edition, 1879
- **Provider:** [Project Gutenberg eBook #11224](https://www.gutenberg.org/ebooks/11224)
- **Rights evidence:** the edition catalog states, “Copyright: Public domain in the USA.”
- **Acquisition endpoint:** `https://www.gutenberg.org/ebooks/11224.txt.utf-8`

The downloaded title page establishes the edition, publisher, place, and year. The five chapter headings are the stable locators available in the plaintext edition.

## `bayes-essay`

- **Provider title:** *An Essay towards solving a Problem in the Doctrine of Chances*
- **Author:** Thomas Bayes
- **Communicated by:** Richard Price
- **Edition:** *Philosophical Transactions of the Royal Society of London*, volume 53 (1763), article LII, pages 370-418
- **Provider/rights page:** [Wikimedia Commons scan record](https://commons.wikimedia.org/wiki/File:An_Essay_towards_Solving_a_Problem_in_the_Doctrine_of_Chances._By_the_Late_Rev._Mr._Bayes,_F._R._S._Communicated_by_Mr._Price,_in_a_Letter_to_John_Canton,_A._M._F._R._S._(IA_paper-doi-10_1098_rstl_1763_0053).pdf)
- **Rights evidence:** Commons identifies the scan as public domain in the United States and free of known restrictions.
- **Acquisition endpoint:** Internet Archive provider OCR for item `paper-doi-10_1098_rstl_1763_0053`

The provider OCR is useful for retrieval but poor for exact language and mathematics: it misreads long-s typography, symbols, equations, and layout and includes adjacent journal matter. The record therefore requires scan verification for every quotation and formula and separates Price's letter from Bayes's essay.

## `musashi-book-five-rings`

- **Provider title:** *Miyamoto Musashi*, Chapter 9, *Go Rin no Sho*
- **Author:** Miyamoto Musashi
- **Editor:** Miyamoto Musashi Iseki Kenshokai
- **Edition:** Kinkodo Shoseki, Tokyo, 1909
- **Edition and rights record:** [National Diet Library](https://ndlsearch.ndl.go.jp/books/R100000002-I000000907244), DOI `10.11501/992019`
- **Original-language access transcription:** [Koten.net Five Rings index](https://www.koten.net/gorin/)
- **Transcription colophon:** [Koten.net notes](https://www.koten.net/gorin/fuki/)
- **Status:** `public-domain-verified`, `ingested`

The NDL record identifies the exact 1909 volume, makes the digital object publicly accessible, and marks its copyright information `pdm`. The Koten.net colophon identifies that volume as its parent text and records the copyrights of Musashi and the parent edition's editors as expired. The local ignored corpus assembles the site's 89 original-text sections into 1,438 Japanese paragraphs and stores their SHA-256 in the manifest.

No English translation was ingested. The access transcription reports correcting obvious copying errors and consulting another Japanese edition, so exact quotations require checking the 1909 scan. English titles, glosses, frameworks, and procedures in `musashi-works` and `musashi-adaptive-strategy` are project-authored interpretations, never disguised quotations.

The former 1939 candidate remains useful as a cleaner scan with section-level page metadata, but it is no longer the rights basis for ingestion. Modern English translations remain protected absent edition-specific permission or public-domain evidence.
