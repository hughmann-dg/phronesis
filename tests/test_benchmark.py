from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from phronesis.benchmark import BenchmarkCase, BenchmarkSuite
from phronesis.council import Council
from phronesis.models import DecisionPacket
from phronesis.reasoning import HeuristicReasoner
from phronesis.sources import SourceCorpus


class BenchmarkTests(unittest.TestCase):
    def test_initial_suite_covers_five_decision_domains(self) -> None:
        suite = BenchmarkSuite.from_file(Path("benchmarks/cases.json"))

        report = suite.run()

        self.assertEqual(report["total_cases"], 5)
        self.assertEqual(
            set(report["categories"]),
            {"historical", "business", "personal", "technical", "strategic"},
        )
        self.assertEqual(report["contract_pass_rate"], 1.0)
        self.assertEqual(report["citation_pass_rate"], 1.0)
        self.assertEqual(report["verified_primary_source_basis_rate"], 0.0)

    def test_contract_rate_rejects_invalid_synthesis_confidence(self) -> None:
        packet = DecisionPacket.from_dict(
            {"decision": "Choose", "objective": "Choose well", "options": ["run a pilot", "commit now"]}
        )

        class InvalidCouncil:
            def convene(self, decision_packet):
                result = Council().convene(decision_packet)
                return replace(result, synthesis=replace(result.synthesis, confidence=1.5))

        report = BenchmarkSuite((BenchmarkCase("invalid", "test", packet),), council=InvalidCouncil()).run()

        self.assertEqual(report["contract_pass_rate"], 0.0)

    def test_contract_rate_rejects_an_empty_red_team_attack(self) -> None:
        packet = DecisionPacket.from_dict(
            {"decision": "Choose", "objective": "Choose well", "options": ["run a pilot", "commit now"]}
        )

        class InvalidCouncil:
            def convene(self, decision_packet):
                result = Council().convene(decision_packet)
                return replace(result, red_team=replace(result.red_team, mitigation_tests=()))

        report = BenchmarkSuite((BenchmarkCase("invalid-red-team", "test", packet),), council=InvalidCouncil()).run()

        self.assertEqual(report["contract_pass_rate"], 0.0)

    def test_contract_rate_rejects_a_result_for_a_different_packet(self) -> None:
        packet = DecisionPacket.from_dict(
            {"decision": "Choose", "objective": "Choose well", "options": ["run a pilot", "commit now"]}
        )

        class InvalidCouncil:
            def convene(self, decision_packet):
                result = Council().convene(decision_packet)
                return replace(result, packet={"decision": "A different decision"})

        report = BenchmarkSuite((BenchmarkCase("wrong-packet", "test", packet),), council=InvalidCouncil()).run()

        self.assertEqual(report["contract_pass_rate"], 0.0)

    def test_verified_primary_metric_checks_the_corpus_instead_of_trusting_a_label(self) -> None:
        packet = DecisionPacket.from_dict(
            {"decision": "Choose", "objective": "Act with practical wisdom", "options": ["A", "B"]}
        )
        with tempfile.TemporaryDirectory() as directory:
            corpus = SourceCorpus(directory)
            corpus.ingest_text(
                "Practical wisdom concerns action and particulars.",
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

            class FabricatingCouncil:
                def __init__(self) -> None:
                    self.real = Council(reasoner=HeuristicReasoner(corpus))

                def convene(self, decision_packet):
                    result = self.real.convene(decision_packet, ("aristotelian-counsel", "stoic-counsel"))
                    counsel = result.counsels[0]
                    fabricated_basis = replace(
                        counsel.philosophical_basis[0],
                        source_excerpt="Practical wisdom",
                        citation="Aristotle, Nicomachean Ethics, invented locator",
                    )
                    fabricated_counsel = replace(counsel, philosophical_basis=(fabricated_basis,))
                    return replace(result, counsels=(fabricated_counsel, *result.counsels[1:]))

            report = BenchmarkSuite(
                (BenchmarkCase("fabricated", "test", packet),),
                council=FabricatingCouncil(),
                corpus=corpus,
            ).run()

        self.assertEqual(report["verified_primary_source_basis_rate"], 0.0)
        self.assertEqual(report["citation_pass_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
