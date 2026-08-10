# Sources

`manifest.yaml` records both candidate acquisitions and edition-specific verified sources. A record remains `verification-required` until the provider's rights statement and the exact edition or translation have been captured.

Verified texts are ingested through `phronesis sources ingest`. Runtime records and text live under `corpus/` and are ignored by Git by default so external works are not accidentally relicensed or redistributed. A `public-domain-verified` Gutenberg record is scoped to the United States unless its notes say otherwise.

See `docs/source-policy.md` and `schemas/source-record.schema.json`.
