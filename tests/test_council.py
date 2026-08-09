import json
from pathlib import Path
import unittest

from phronesis.council import Council
from phronesis.doctrines import get_doctrine, list_doctrines
from phronesis.models import DecisionPacket


FIXTURE = Path(__file__).parent / "fixtures" / "system_migration.json"


class DoctrineTests(unittest.TestCase):
    def test_initial_library_is_explicit_and_source_grounded(self) -> None:
        doctrines = list_doctrines()

        self.assertEqual(len(doctrines), 9)
        clausewitz = get_doctrine("clausewitzian-strategy")
        self.assertIn("friction", " ".join(clausewitz.principles).lower())
        self.assertEqual(clausewitz.sources[0].title, "On War")
        self.assertTrue(clausewitz.failure_modes)
        self.assertTrue(clausewitz.defer_when)


class CouncilTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = DecisionPacket.from_dict(json.loads(FIXTURE.read_text(encoding="utf-8")))

    def test_council_runs_counsel_contest_red_team_and_decision(self) -> None:
        result = Council().convene(self.packet)

        self.assertEqual(len(result.counsels), 5)
        self.assertTrue(all(counsel.philosophical_basis for counsel in result.counsels))
        self.assertTrue(result.cross_examinations)
        self.assertNotIn("red-team", result.synthesis.supporting_schools)
        self.assertIn(result.synthesis.recommendation, self.packet.options)
        self.assertEqual(result.synthesis.recommendation, "incremental migration")
        self.assertTrue(result.synthesis.strongest_opposing_argument)
        self.assertGreater(result.synthesis.confidence, 0.5)
        self.assertLessEqual(result.synthesis.confidence, 0.9)
        self.assertEqual(
            [stage.name for stage in result.stages],
            ["counsel", "cross_examination", "red_team", "arbiter"],
        )

    def test_ask_school_returns_standard_contract(self) -> None:
        counsel = Council().ask("stoic-counsel", self.packet)

        self.assertEqual(counsel.school_id, "stoic-counsel")
        self.assertIn(counsel.recommendation, self.packet.options)
        self.assertTrue(counsel.reasoning)
        self.assertTrue(counsel.major_risks)
        self.assertTrue(counsel.what_would_change)
        self.assertGreaterEqual(counsel.confidence, 0)
        self.assertLessEqual(counsel.confidence, 1)
        self.assertIsInstance(counsel.to_dict()["reasoning"], list)
        self.assertIsInstance(counsel.to_dict()["philosophical_basis"], list)

    def test_current_preference_does_not_anchor_independent_counsel(self) -> None:
        base = {
            "decision": "Choose between equivalent paths",
            "objective": "Make a defensible choice",
            "options": ["Option A", "Option B"],
        }
        prefers_a = DecisionPacket.from_dict(base | {"current_preference": "Option A"})
        prefers_b = DecisionPacket.from_dict(base | {"current_preference": "Option B"})

        recommendations_a = tuple(c.recommendation for c in Council().convene(prefers_a).counsels)
        recommendations_b = tuple(c.recommendation for c in Council().convene(prefers_b).counsels)

        self.assertEqual(recommendations_a, recommendations_b)

    def test_cross_examination_targets_the_actual_counsel(self) -> None:
        result = Council().convene(self.packet)
        challenge = result.cross_examinations[0]
        target = next(counsel for counsel in result.counsels if counsel.school_id == challenge.target_school_id)

        self.assertIn(repr(target.recommendation), challenge.challenge)
        self.assertIn(target.strongest_reason, challenge.challenge)


if __name__ == "__main__":
    unittest.main()
