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
            corpus.ingest_text(
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


if __name__ == "__main__":
    unittest.main()
