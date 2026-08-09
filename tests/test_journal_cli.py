import io
import json
from pathlib import Path
import tempfile
import unittest

from phronesis.cli import main
from phronesis.council import Council
from phronesis.journal import DecisionJournal
from phronesis.models import DecisionPacket


FIXTURE = Path(__file__).parent / "fixtures" / "system_migration.json"


class JournalTests(unittest.TestCase):
    def test_record_review_and_insights_use_the_journal_interface(self) -> None:
        packet = DecisionPacket.from_dict(json.loads(FIXTURE.read_text(encoding="utf-8")))
        result = Council().convene(packet)
        with tempfile.TemporaryDirectory() as directory:
            journal = DecisionJournal(directory)
            entry = journal.record(
                packet,
                result,
                user_decision="incremental migration",
                user_confidence=0.75,
                predicted_outcomes=["No major outage", "Migration completes before support expiry"],
                review_date="2027-03-31",
            )

            reviewed = journal.review(
                entry.id,
                actual_outcome="Completed in March with one minor incident.",
                lessons=["The phased cutover contained the incident."],
                prediction_results=[True, True],
            )

            self.assertEqual(journal.get(entry.id).actual_outcome, reviewed.actual_outcome)
            self.assertIsInstance(reviewed.to_dict()["lessons"], list)
            self.assertEqual(len(journal.list_entries()), 1)
            insights = journal.insights()
            self.assertEqual(insights["reviewed_decisions"], 1)
            self.assertEqual(insights["prediction_accuracy"], 1.0)
            self.assertEqual(insights["average_user_confidence"], 0.75)


class CliTests(unittest.TestCase):
    def test_council_command_emits_machine_readable_result(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = main(["council", str(FIXTURE)], stdout=stdout, stderr=stderr)

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["synthesis"]["recommendation"], "incremental migration")
        self.assertEqual(stderr.getvalue(), "")

    def test_validate_command_reports_bad_packets_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text('{"decision": "Only a title"}', encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()

            exit_code = main(["validate", str(path)], stdout=stdout, stderr=stderr)

            self.assertEqual(exit_code, 2)
            self.assertIn("objective", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_benchmark_command_runs_the_cross_domain_suite(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = main(["benchmark", "benchmarks/cases.json"], stdout=stdout, stderr=stderr)

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["total_cases"], 5)
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
