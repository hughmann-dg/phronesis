# Source and rights policy

Source age is not translation age. Phronesis therefore evaluates rights at the edition or translation level.

## Three layers

1. **Primary source:** immutable edition-specific text with URL, retrieval date, checksum, and rights evidence.
2. **Interpretation:** extracted principles linked to exact work locators. Interpretation must be labeled as such.
3. **Behavior:** a school procedure that applies those principles and returns a validated decision contract.

Do not replace layer 1 with a summary. Do not present layer 2 as a quotation. Do not let layer 3 invent a source.

## Ingestion gate

`SourceCorpus` accepts only `public-domain-verified` and `permission-granted`. A record also needs textual rights evidence. `verification-required` candidates remain in the manifest but cannot enter the retrieval corpus.

For every ingested text:

- identify author, title, translator, edition, publication year, and source URL; when the provider does not establish a translator or publication year, record explicit `null` and explain the uncertainty in `notes` rather than guessing;
- preserve the provider's rights statement as evidence;
- record retrieval date and SHA-256;
- retain original paragraph boundaries for locators;
- exclude restricted material from repository history and distributions.

Retrieval is also a gate: persisted records are revalidated, non-ingestible rights status is rejected, and the stored text must still match its recorded SHA-256.

The project's Apache-2.0 license applies to project-authored code, skills, prompts, and documentation. It does not relicense external texts.
