from pathlib import Path
import unittest

from phronesis.benchmark import BenchmarkSuite


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


if __name__ == "__main__":
    unittest.main()
