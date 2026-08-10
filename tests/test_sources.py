import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from phronesis.models import ValidationError
from phronesis.council import Council
from phronesis.reasoning import HeuristicReasoner
from phronesis.sources import SourceCorpus


class SourceCorpusTests(unittest.TestCase):
    def test_verified_primary_text_can_be_retrieved_with_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)
            record = corpus.ingest_text(
                "Practical wisdom concerns action and particulars.\n\nScientific knowledge concerns what cannot be otherwise.",
                {
                    "id": "example-ethics",
                    "title": "Example Ethics",
                    "author": "Example Author",
                    "translator": "Public Domain Translator",
                    "edition": "Test edition",
                    "publication_year": 1900,
                    "source_url": "https://example.test/ethics",
                    "rights_status": "public-domain-verified",
                    "rights_evidence": "Published in 1900; test fixture.",
                    "retrieved_date": "2026-08-09",
                    "ingestion_status": "verified"
                },
            )

            results = corpus.search("wisdom particulars", top_k=1)

            self.assertEqual(results[0].source_id, "example-ethics")
            self.assertEqual(results[0].locator, "paragraph 1")
            self.assertIn("Example Author", results[0].citation)
            self.assertIn("Practical wisdom", results[0].text)
            stored = Path(directory, "texts", "example-ethics.txt").read_bytes()
            self.assertEqual(hashlib.sha256(stored).hexdigest(), record.sha256)

    def test_unverified_translation_cannot_be_ingested(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)

            with self.assertRaisesRegex(ValidationError, "rights"):
                corpus.ingest_text(
                    "Some text",
                    {
                        "id": "unverified",
                        "title": "Modern Translation",
                        "author": "Ancient Author",
                        "edition": "Unknown",
                        "source_url": "https://example.test/source",
                        "rights_status": "verification-required",
                        "retrieved_date": None,
                        "ingestion_status": "candidate"
                    },
                )

    def test_source_retrieval_date_must_match_the_public_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)

            with self.assertRaisesRegex(ValidationError, "retrieved_date"):
                corpus.ingest_text(
                    "Some text",
                    {
                        "id": "bad-date",
                        "title": "Old Work",
                        "author": "Old Author",
                        "edition": "Verified edition",
                        "source_url": "https://example.test/source",
                        "rights_status": "public-domain-verified",
                        "rights_evidence": "Edition-specific rights statement",
                        "retrieved_date": 42,
                        "ingestion_status": "verified",
                    },
                )

    def test_ingestion_requires_verified_status_and_a_retrieval_date(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)
            metadata = {
                "id": "missing-gate",
                "title": "Old Work",
                "author": "Old Author",
                "translator": None,
                "edition": "Verified edition",
                "publication_year": 1900,
                "source_url": "https://example.test/source",
                "rights_status": "public-domain-verified",
                "rights_evidence": "Edition-specific rights statement",
                "retrieved_date": None,
            }

            with self.assertRaisesRegex(ValidationError, "ingestion_status"):
                corpus.ingest_text("Some text", metadata)

            metadata["ingestion_status"] = "verified"
            with self.assertRaisesRegex(ValidationError, "retrieved_date"):
                corpus.ingest_text("Some text", metadata)

    def test_counsel_uses_matching_corpus_passage_for_philosophical_basis(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)
            corpus.ingest_text(
                "Practical wisdom is concerned with action in particular situations.",
                {
                    "id": "aristotle-nicomachean-ethics",
                    "title": "Nicomachean Ethics",
                    "author": "Aristotle",
                    "translator": "Verified Translator",
                    "edition": "Verified test edition",
                    "publication_year": 1900,
                    "source_url": "https://example.test/ethics",
                    "rights_status": "public-domain-verified",
                    "rights_evidence": "Published in 1900; test fixture.",
                    "retrieved_date": "2026-08-09",
                    "ingestion_status": "verified",
                },
            )
            from phronesis.models import DecisionPacket

            packet = DecisionPacket.from_dict(
                {"decision": "Choose", "objective": "Act with practical wisdom", "options": ["A", "B"]}
            )

            counsel = Council(reasoner=HeuristicReasoner(corpus=corpus)).ask("aristotelian-counsel", packet)

            basis = counsel.philosophical_basis[0]
            self.assertEqual(basis.grounding, "retrieved-primary-source")
            self.assertIn("particular situations", basis.source_excerpt)
            self.assertEqual(basis.source_url, "https://example.test/ethics")

    def test_stoic_counsel_retrieves_the_verified_epictetus_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)
            corpus.ingest_text(
                "Our own present judgments, impulses, and acts are the proper location of agency; outcomes controlled by others are not guaranteed.",
                {
                    "id": "epictetus-discourses-enchiridion",
                    "title": "A Selection from the Discourses with the Encheiridion",
                    "author": "Epictetus",
                    "translator": "George Long",
                    "edition": "Verified test edition",
                    "publication_year": 1900,
                    "source_url": "https://example.test/epictetus",
                    "rights_status": "public-domain-verified",
                    "rights_evidence": "Published in 1900; test fixture.",
                    "retrieved_date": "2026-08-09",
                    "ingestion_status": "verified",
                },
            )
            from phronesis.models import DecisionPacket

            packet = DecisionPacket.from_dict(
                {
                    "decision": "Choose",
                    "objective": "Act well despite uncertain outcomes",
                    "options": ["commit now", "run a trial"],
                }
            )

            counsel = Council(reasoner=HeuristicReasoner(corpus=corpus)).ask("stoic-counsel", packet)

            basis = counsel.philosophical_basis[0]
            self.assertEqual(basis.grounding, "retrieved-primary-source")
            self.assertEqual(basis.source_id, "epictetus-discourses-enchiridion")
            self.assertIn("proper location of agency", basis.source_excerpt)
            self.assertEqual(basis.source_url, "https://example.test/epictetus")

    def test_search_rejects_a_persisted_record_whose_rights_are_no_longer_ingestible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)
            corpus.ingest_text(
                "Verified wisdom passage.",
                {
                    "id": "rights-change",
                    "title": "Verified Work",
                    "author": "Author",
                    "translator": None,
                    "edition": "Edition",
                    "publication_year": 1900,
                    "source_url": "https://example.test/work",
                    "rights_status": "public-domain-verified",
                    "rights_evidence": "Edition-specific statement",
                    "retrieved_date": "2026-08-09",
                    "ingestion_status": "verified",
                },
            )
            record_path = Path(directory, "records", "rights-change.json")
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record["rights_status"] = "restricted"
            record_path.write_text(json.dumps(record), encoding="utf-8")

            with self.assertRaisesRegex(ValidationError, "rights"):
                corpus.search("wisdom")

    def test_search_rejects_text_that_no_longer_matches_its_recorded_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)
            corpus.ingest_text(
                "Original wisdom passage.",
                {
                    "id": "hash-change",
                    "title": "Verified Work",
                    "author": "Author",
                    "translator": None,
                    "edition": "Edition",
                    "publication_year": 1900,
                    "source_url": "https://example.test/work",
                    "rights_status": "public-domain-verified",
                    "rights_evidence": "Edition-specific statement",
                    "retrieved_date": "2026-08-09",
                    "ingestion_status": "verified",
                },
            )
            Path(directory, "texts", "hash-change.txt").write_text(
                "Modified wisdom passage.",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValidationError, "checksum"):
                corpus.search("wisdom")

    def test_persisted_source_records_are_revalidated_before_use(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)
            corpus.ingest_text(
                "Verified passage.",
                {
                    "id": "invalid-record",
                    "title": "Verified Work",
                    "author": "Author",
                    "translator": None,
                    "edition": "Edition",
                    "publication_year": 1900,
                    "source_url": "https://example.test/work",
                    "rights_status": "public-domain-verified",
                    "rights_evidence": "Edition-specific statement",
                    "retrieved_date": "2026-08-09",
                    "ingestion_status": "verified",
                },
            )
            record_path = Path(directory, "records", "invalid-record.json")
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record["retrieved_date"] = None
            record["unexpected"] = "not in the public schema"
            record_path.write_text(json.dumps(record), encoding="utf-8")

            with self.assertRaisesRegex(ValidationError, "unexpected|retrieved_date"):
                corpus.list_records()

    def test_ingestion_does_not_coerce_metadata_outside_the_source_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)

            with self.assertRaisesRegex(ValidationError, "notes"):
                corpus.ingest_text(
                    "Verified passage.",
                    {
                        "id": "bad-notes",
                        "title": "Verified Work",
                        "author": "Author",
                        "translator": None,
                        "edition": "Edition",
                        "publication_year": 1900,
                        "source_url": "https://example.test/work",
                        "rights_status": "public-domain-verified",
                        "rights_evidence": "Edition-specific statement",
                        "retrieved_date": "2026-08-09",
                        "ingestion_status": "verified",
                        "notes": 42,
                    },
                )

    def test_malformed_persisted_json_is_reported_as_validation_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)
            Path(directory, "records", "broken.json").write_text("{", encoding="utf-8")

            with self.assertRaisesRegex(ValidationError, "broken.json"):
                corpus.list_records()

    def test_search_rejects_an_ingested_record_with_missing_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)
            corpus.ingest_text(
                "Verified wisdom passage.",
                {
                    "id": "missing-text",
                    "title": "Verified Work",
                    "author": "Author",
                    "translator": None,
                    "edition": "Edition",
                    "publication_year": 1900,
                    "source_url": "https://example.test/work",
                    "rights_status": "public-domain-verified",
                    "rights_evidence": "Edition-specific statement",
                    "retrieved_date": "2026-08-09",
                    "ingestion_status": "verified",
                },
            )
            Path(directory, "texts", "missing-text.txt").unlink()

            with self.assertRaisesRegex(ValidationError, "missing its text"):
                corpus.search("wisdom")

    def test_ingestion_refuses_to_overwrite_an_existing_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)
            metadata = {
                "id": "immutable-source",
                "title": "Verified Work",
                "author": "Author",
                "translator": None,
                "edition": "Edition",
                "publication_year": 1900,
                "source_url": "https://example.test/work",
                "rights_status": "public-domain-verified",
                "rights_evidence": "Edition-specific statement",
                "retrieved_date": "2026-08-09",
                "ingestion_status": "verified",
            }
            corpus.ingest_text("Original text.", metadata)

            with self.assertRaisesRegex(ValidationError, "already exists"):
                corpus.ingest_text("Replacement text.", metadata)


if __name__ == "__main__":
    unittest.main()
