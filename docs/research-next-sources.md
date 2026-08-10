# Research: next edition-verified sources

Research date: 2026-08-09
Rights jurisdiction: United States

Acquisition update: all five recommended records were subsequently acquired and ingested on 2026-08-09. The manifest and ignored local corpus contain the retrieval date and SHA-256 of the exact ingested text. Follow-on research for Sun Tzu, Mill, Bayes, and Musashi is recorded in [research-follow-on-sources.md](research-follow-on-sources.md); the Musashi candidate was promoted from gated to an ingested Japanese source on 2026-08-10.

## Recommendation

Use a two-tier next set:

1. **Runtime-priority core:** `machiavelli-prince`, `machiavelli-discourses`, `clausewitz-on-war`, and `hume-enquiry`. These are the four un-ingested records used by the three default-council schools that still lack verified primary texts: Machiavellian Realism, Clausewitzian Strategy, and Humean Skepticism.
2. **Manifest-order companion:** `plato-dialogues`. It is the first remaining candidate in manifest order, is directly cited by the Socratic doctrine, and now has an unusually strong single-volume provider match containing both cited dialogues.

Acquire all five in the same pass if capacity permits. If “next set” must be limited, the four-record runtime-priority core has the greatest immediate effect because it completes primary-source coverage for every school in `DEFAULT_COUNCIL`. This selection follows the [manifest](../sources/manifest.yaml), current [doctrine definitions](../src/phronesis/doctrines.py), the [source policy](source-policy.md), and the [roadmap](roadmap.md).

This document began as a source-acquisition recommendation. The later acquisition pass changed the manifest and local ignored corpus; the manifest now records the actual retrieval date and SHA-256 for each acquired source.

## 1. `plato-dialogues`

Recommended edition:

- **Title:** *The Dialogues of Plato in Five Volumes, Vol. 2 (of 5): Translated into English with Analyses and Introductions*
- **Author:** Plato
- **Translator:** Benjamin Jowett
- **Edition:** Third edition, revised and corrected throughout, with marginal analyses and an index of subjects and proper names
- **Publication:** Oxford University Press, American Branch, New York; 1892
- **Editor:** No separate editor is credited by the provider. Jowett is credited as translator and as responsible for the analyses and introductions.
- **Stable source page:** [Project Gutenberg eBook #76464](https://www.gutenberg.org/ebooks/76464)
- **Plain-text acquisition URL:** [UTF-8 plain text](https://www.gutenberg.org/ebooks/76464.txt.utf-8)
- **Rights evidence:** the edition-specific Gutenberg catalog says, “Copyright: Public domain in the USA.”

Why this edition: the catalog identifies the third edition, the 1892 original publication, Jowett, and contents that include both *Apology* and *Gorgias*.[^plato-catalog] The plain-text title matter independently identifies the title, translator, original publication, and third edition.[^plato-text] It also preserves the volume's marginal page numbers, including the relevant 454–461 sequence in *Gorgias*, so it is a materially better match for the doctrine's Stephanus-style locators than the older separate Gutenberg transcriptions.[^plato-locators]

Suggested manifest values:

- `title`: `The Dialogues of Plato in Five Volumes, Vol. 2 (of 5): Translated into English with Analyses and Introductions`
- `translator`: `Benjamin Jowett`
- `edition`: `Oxford University Press, American Branch, third edition, revised and corrected throughout; Project Gutenberg eBook #76464`
- `publication_year`: `1892`
- `source_url`: `https://www.gutenberg.org/ebooks/76464`
- `rights_status`: `public-domain-verified`
- `rights_evidence`: `Project Gutenberg's edition-specific catalog record states: Copyright: Public domain in the USA.`
- `notes`: `Volume II contains Meno, Euthyphro, Apology, Crito, Phaedo, Gorgias, and appendices. The plain-text transcription preserves marginal page-number guides relevant to the doctrine's Apology 21d-23b and Gorgias 454c-461b locators. Rights verification is scoped to the United States.`

Uncertainty: the transcription preserves page numbers but not always the letter subdivisions (`a`–`e`) in a machine-readable form. Passage-level interpretation should therefore verify the relevant spans against the rendered edition or page images before quoting.

## 2. `machiavelli-prince`

Recommended edition:

- **Title:** *The Prince*
- **Author:** Niccolò Machiavelli
- **Translator:** W. K. (William Kenaz) Marriott
- **Editor:** Not credited by the provider
- **Publication year:** `null`
- **Stable source page:** [Project Gutenberg eBook #1232](https://www.gutenberg.org/ebooks/1232)
- **Plain-text acquisition URL:** [UTF-8 plain text](https://www.gutenberg.org/ebooks/1232.txt.utf-8)
- **Rights evidence:** the edition-specific Gutenberg catalog says, “Copyright: Public domain in the USA.”

The catalog establishes the title, author, translator, contents, eBook number, and US public-domain status.[^prince-catalog] The plain-text title matter confirms Marriott but does not identify a print publisher, edition statement, or publication year.[^prince-text] Per the repository policy, `publication_year` should remain explicit `null`; do not substitute the work's original 1532 publication date or the Gutenberg release date for this translation's edition year.

Suggested manifest values:

- `title`: `The Prince`
- `translator`: `W. K. Marriott`
- `edition`: `Project Gutenberg eBook #1232; English translation by W. K. Marriott`
- `publication_year`: `null`
- `source_url`: `https://www.gutenberg.org/ebooks/1232`
- `rights_status`: `public-domain-verified`
- `rights_evidence`: `Project Gutenberg's edition-specific catalog record states: Copyright: Public domain in the USA.`
- `notes`: `The provider does not establish a print publication year for this translation. The Gutenberg text also includes Description of the Methods Adopted by the Duke Valentino and The Life of Castruccio Castracani of Lucca after The Prince. Rights verification is scoped to the United States.`

## 3. `machiavelli-discourses`

Recommended edition:

- **Title:** *Discourses on the First Decade of Titus Livius*
- **Author:** Niccolò Machiavelli
- **Translator:** Ninian Hill Thomson
- **Editor:** Not credited by the provider
- **Publication:** Kegan Paul, Trench & Co., London; 1883
- **Stable source page:** [Project Gutenberg eBook #10827](https://www.gutenberg.org/ebooks/10827)
- **Plain-text acquisition URL:** [UTF-8 plain text](https://www.gutenberg.org/ebooks/10827.txt.utf-8)
- **Rights evidence:** the edition-specific Gutenberg catalog says, “Copyright: Public domain in the USA.”

The catalog establishes the exact title, author, translator, and US public-domain status.[^discourses-catalog] The transcribed title page identifies the London publisher and 1883 publication year.[^discourses-text]

Suggested manifest values:

- `title`: `Discourses on the First Decade of Titus Livius`
- `translator`: `Ninian Hill Thomson`
- `edition`: `Kegan Paul, Trench & Co., London, 1883; Project Gutenberg eBook #10827`
- `publication_year`: `1883`
- `source_url`: `https://www.gutenberg.org/ebooks/10827`
- `rights_status`: `public-domain-verified`
- `rights_evidence`: `Project Gutenberg's edition-specific catalog record states: Copyright: Public domain in the USA.`
- `notes`: `The provider title differs from the manifest's generic Discourses on Livy and should be preserved exactly. Rights verification is scoped to the United States.`

## 4. `clausewitz-on-war`

Recommended edition:

- **Title:** *On War*
- **Author:** Carl von Clausewitz
- **Translator:** Colonel J. J. (James John) Graham
- **Editor/annotator:** Colonel F. N. Maude, C.B.
- **Edition:** New and revised edition with introduction and notes; London reprinting; eighth impression in three volumes
- **Publication year:** `null`
- **Stable source page:** [Project Gutenberg eBook #1946](https://www.gutenberg.org/ebooks/1946)
- **Plain-text acquisition URL:** [UTF-8 plain text](https://www.gutenberg.org/ebooks/1946.txt.utf-8)
- **Rights evidence:** the edition-specific Gutenberg catalog says, “Copyright: Public domain in the USA.”

The catalog establishes the title, author, Graham translation, and US public-domain status.[^clausewitz-catalog] The transcribed edition matter says that Graham's translation first appeared in 1874 and that 1909 was a London reprinting; it separately identifies this text as a new and revised edition with Maude's introduction and notes and as the eighth impression in three volumes.[^clausewitz-text] It does not unambiguously say that the eighth impression itself was published in 1909, so the policy requires `publication_year: null` rather than an inference.

Suggested manifest values:

- `title`: `On War`
- `translator`: `J. J. Graham`
- `edition`: `New and revised edition of J. J. Graham's translation with introduction and notes by F. N. Maude; eighth impression in three volumes; edition matter notes the 1874 first translation and a 1909 London reprinting; Project Gutenberg eBook #1946`
- `publication_year`: `null`
- `source_url`: `https://www.gutenberg.org/ebooks/1946`
- `rights_status`: `public-domain-verified`
- `rights_evidence`: `Project Gutenberg's edition-specific catalog record states: Copyright: Public domain in the USA.`
- `notes`: `The transcription says the Graham translation first appeared in 1874 and that 1909 was a London reprinting, but it does not unambiguously date the identified eighth impression. The acquired text is a new and revised edition with F. N. Maude's introduction and notes. Rights verification is scoped to the United States.`

## 5. `hume-enquiry`

Recommended edition:

- **Title:** *An Enquiry Concerning Human Understanding*
- **Author:** David Hume
- **Translator:** `null` (the work is in English)
- **Editor:** Sir L. A. (Lewis Amherst) Selby-Bigge
- **Edition:** Extracted from *Enquiries Concerning the Human Understanding, and Concerning the Principles of Morals*; reprinted from the posthumous edition of 1777; second edition
- **Publication year:** 1902
- **Stable source page:** [Project Gutenberg eBook #9662](https://www.gutenberg.org/ebooks/9662)
- **Plain-text acquisition URL:** [UTF-8 plain text](https://www.gutenberg.org/ebooks/9662.txt.utf-8)
- **Rights evidence:** the edition-specific Gutenberg catalog says, “Copyright: Public domain in the USA.”

The catalog identifies the title, author, Selby-Bigge as editor, and US public-domain status.[^hume-catalog] The plain text specifies that this is the second edition of 1902, reprinted from the posthumous 1777 edition, and describes Selby-Bigge's editorial apparatus.[^hume-text]

Suggested manifest values:

- `title`: `An Enquiry Concerning Human Understanding`
- `translator`: `null`
- `edition`: `Second edition, 1902; reprinted from the posthumous edition of 1777 and edited with introduction, comparative tables of contents, and analytical index by L. A. Selby-Bigge; Project Gutenberg eBook #9662`
- `publication_year`: `1902`
- `source_url`: `https://www.gutenberg.org/ebooks/9662`
- `rights_status`: `public-domain-verified`
- `rights_evidence`: `Project Gutenberg's edition-specific catalog record states: Copyright: Public domain in the USA.`
- `notes`: `This Gutenberg text is an extract from the larger Enquiries volume. No translator applies because Hume wrote in English. Rights verification is scoped to the United States.`

## Deferred manifest candidates

- `seneca-moral-letters`: defer. It appears before Machiavelli in manifest order, but no current doctrine cites it. More importantly, Project Gutenberg's Seneca catalog does not presently list *Moral Letters*, while Standard Ebooks labels its Gummere edition as still in production and says it is not yet in the catalog.[^seneca-gutenberg][^seneca-standard] This record remains `verification-required` until a complete, downloadable, edition-specific provider record exists.
- `marcus-aurelius-meditations`: defer. It also is not cited by a current doctrine, and Stoic Counsel already routes through three ingested Epictetus sources. If this record is promoted later, Gutenberg eBook #55317 is a clean candidate: George W. Chrystal's 1902 *The Meditations of the Emperor Marcus Aurelius Antoninus*, based on the Foulis translation of 1742, with explicit US public-domain status.[^marcus-catalog][^marcus-text]
- `sun-tzu-art-of-war`, `mill-utilitarianism`, and `bayes-essay`: subsequently acquired in the follow-on batch documented in [research-follow-on-sources.md](research-follow-on-sources.md).

Strict manifest order would place Sun Tzu before Clausewitz and Hume. The recommendation intentionally prioritizes completing the default council after resolving the first uncited-book detour (Seneca and Marcus). If catalog order is treated as inviolable rather than advisory, stop the batch after the two Machiavelli records and make Sun Tzu the first record in the following batch.

## Acquisition cautions

- Keep the catalog page as `source_url`; use the plain-text URL only as the acquisition endpoint. The catalog page is the durable edition and rights record.
- Do not treat a Gutenberg release/update date as the edition's `publication_year`.
- Preserve exact provider titles even where they differ from the manifest's generic title.
- Record `null` rather than guessing a translator, editor, or publication year.
- Verify that the downloaded text still displays the same title matter and rights header before hashing it.
- Gutenberg warns that a catalog rights field can occasionally be wrong and instructs users to inspect the license inside the ebook.[^gutenberg-license] The five recommended plain texts were checked for the unrestricted-US opening notice and none displays the special copyright-holder-permission notice at its beginning; repeat that check on the exact downloaded bytes.
- Rights evidence here is expressly US-scoped. Check local law before use elsewhere.

## Primary-provider references

[^plato-catalog]: Project Gutenberg, [eBook #76464 catalog record](https://www.gutenberg.org/ebooks/76464), metadata and copyright fields.
[^plato-text]: Project Gutenberg, [eBook #76464 UTF-8 text](https://www.gutenberg.org/ebooks/76464.txt.utf-8), title matter and transcriber's note.
[^plato-locators]: Project Gutenberg, [eBook #76464 UTF-8 text](https://www.gutenberg.org/ebooks/76464.txt.utf-8), *Gorgias* marginal analysis and page guides 454–461.
[^prince-catalog]: Project Gutenberg, [eBook #1232 catalog record](https://www.gutenberg.org/ebooks/1232), metadata, contents, and copyright fields.
[^prince-text]: Project Gutenberg, [eBook #1232 UTF-8 text](https://www.gutenberg.org/ebooks/1232.txt.utf-8), title matter.
[^discourses-catalog]: Project Gutenberg, [eBook #10827 catalog record](https://www.gutenberg.org/ebooks/10827), metadata and copyright fields.
[^discourses-text]: Project Gutenberg, [eBook #10827 UTF-8 text](https://www.gutenberg.org/ebooks/10827.txt.utf-8), title page.
[^clausewitz-catalog]: Project Gutenberg, [eBook #1946 catalog record](https://www.gutenberg.org/ebooks/1946), metadata and copyright fields.
[^clausewitz-text]: Project Gutenberg, [eBook #1946 UTF-8 text](https://www.gutenberg.org/ebooks/1946.txt.utf-8), edition matter.
[^hume-catalog]: Project Gutenberg, [eBook #9662 catalog record](https://www.gutenberg.org/ebooks/9662), metadata and copyright fields.
[^hume-text]: Project Gutenberg, [eBook #9662 UTF-8 text](https://www.gutenberg.org/ebooks/9662.txt.utf-8), edition matter.
[^seneca-gutenberg]: Project Gutenberg, [Seneca author catalog](https://www.gutenberg.org/ebooks/author/1308).
[^seneca-standard]: Standard Ebooks, [*Moral Letters to Lucilius* production page](https://standardebooks.org/ebooks/seneca/moral-letters-to-lucilius/richard-m-gummere).
[^marcus-catalog]: Project Gutenberg, [eBook #55317 catalog record](https://www.gutenberg.org/ebooks/55317), metadata and copyright fields.
[^marcus-text]: Project Gutenberg, [eBook #55317 UTF-8 text](https://www.gutenberg.org/ebooks/55317.txt.utf-8), title page.
[^gutenberg-license]: Project Gutenberg, [license explanation](https://www.gutenberg.org/policy/license.html), “Books Not Protected Under U.S. Copyright Law” and catalog-warning sections.
