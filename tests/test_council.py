import json
from pathlib import Path
import unittest

from phronesis.contracts import CounselResponse, PhilosophicalBasis
from phronesis.council import Council
from phronesis.doctrines import get_doctrine, list_doctrines
from phronesis.models import DecisionPacket, ValidationError


FIXTURE = Path(__file__).parent / "fixtures" / "system_migration.json"


class DoctrineTests(unittest.TestCase):
    def test_initial_library_is_explicit_and_source_grounded(self) -> None:
        doctrines = list_doctrines()

        self.assertEqual(len(doctrines), 10)
        clausewitz = get_doctrine("clausewitzian-strategy")
        self.assertIn("friction", " ".join(clausewitz.principles).lower())
        self.assertEqual(clausewitz.sources[0].title, "On War")
        self.assertTrue(clausewitz.failure_modes)
        self.assertTrue(clausewitz.defer_when)

    def test_stoic_doctrine_uses_verified_epictetus_editions_and_preserves_limits(self) -> None:
        stoic = get_doctrine("stoic-counsel")

        self.assertEqual(
            {source.id for source in stoic.sources},
            {
                "epictetus-discourses-enchiridion",
                "epictetus-teaching-rolleston",
                "epictetus-golden-sayings-crossley",
            },
        )
        self.assertIn("influence", " ".join(stoic.failure_modes).lower())
        self.assertIn("self-harm", " ".join(stoic.defer_when).lower())
        self.assertIn("Encheiridion 1", stoic.sources[0].locator)

    def test_counsel_doctrines_declare_their_reference_skill_when_available(self) -> None:
        self.assertEqual(get_doctrine("socratic-examination").reference_skill, "plato-works")
        self.assertEqual(get_doctrine("aristotelian-counsel").reference_skill, "aristotle-works")
        self.assertEqual(get_doctrine("stoic-counsel").reference_skill, "epictetus-works")
        self.assertEqual(get_doctrine("machiavellian-realism").reference_skill, "machiavelli-works")
        self.assertEqual(get_doctrine("clausewitzian-strategy").reference_skill, "clausewitz-works")
        self.assertEqual(get_doctrine("sun-tzu-positioning").reference_skill, "sun-tzu-works")
        self.assertEqual(get_doctrine("musashi-adaptive-strategy").reference_skill, "musashi-works")
        self.assertEqual(get_doctrine("humean-skepticism").reference_skill, "hume-works")
        self.assertEqual(get_doctrine("bayesian-analysis").reference_skill, "bayes-works")
        self.assertEqual(get_doctrine("consequentialist-analysis").reference_skill, "mill-works")


class CouncilTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = DecisionPacket.from_dict(json.loads(FIXTURE.read_text(encoding="utf-8")))

    def test_council_runs_advisory_board_red_team_and_decision(self) -> None:
        result = Council().convene(self.packet)

        expected_schools = {
            "aristotelian-counsel",
            "stoic-counsel",
            "machiavellian-realism",
            "clausewitzian-strategy",
            "sun-tzu-positioning",
            "musashi-adaptive-strategy",
            "humean-skepticism",
            "bayesian-analysis",
            "consequentialist-analysis",
        }
        self.assertEqual({counsel.school_id for counsel in result.counsels}, expected_schools)
        self.assertTrue(all(counsel.philosophical_basis for counsel in result.counsels))
        self.assertEqual(result.cross_examinations, ())
        self.assertIn("debate was skipped", result.stages[1].summary)
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
        self.assertIn("residual outcomes", counsel.strongest_reason)

    def test_standard_contract_has_a_schema_defined_extension_container(self) -> None:
        response = CounselResponse(
            school_id="bayesian-analysis",
            school_name="Bayesian Analysis",
            recommendation="A",
            strongest_reason="Evidence favors A",
            reasoning=("Evidence favors A",),
            assumptions=(),
            major_risks=("The prior is uncertain",),
            confidence=0.6,
            what_would_change=("Diagnostic evidence",),
            disconfirming_evidence=("Evidence favoring B",),
            philosophical_basis=(
                PhilosophicalBasis("Update from evidence", "bayes-essay", "Proposition 9", "Application"),
            ),
            extensions={"priors": {"A": 0.5, "B": 0.5}},
        )
        schema = json.loads(Path("schemas/counsel-response.schema.json").read_text(encoding="utf-8"))

        self.assertEqual(response.to_dict()["extensions"]["priors"]["A"], 0.5)
        self.assertIn("extensions", schema["properties"])

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
        packet = DecisionPacket.from_dict(
            {
                "decision": "How should we introduce a disputed policy?",
                "objective": "Adopt a legitimate policy with reliable evidence and stakeholder cooperation",
                "options": [
                    "run a measurement pilot",
                    "negotiate a stakeholder coalition",
                    "mandate immediate adoption",
                ],
                "constraints": ["A decision is due this quarter"],
                "stakeholders": ["customers", "employees", "regulators"],
                "unknowns": ["Measured effect on customer trust"],
            }
        )

        result = Council().convene(packet)
        counsels = {counsel.school_id: counsel for counsel in result.counsels}

        self.assertTrue(result.cross_examinations)
        for challenge in result.cross_examinations:
            with self.subTest(critic=challenge.critic_school_id, target=challenge.target_school_id):
                critic = counsels[challenge.critic_school_id]
                target = counsels[challenge.target_school_id]
                self.assertNotEqual(critic.recommendation, target.recommendation)
                self.assertIn(repr(target.recommendation), challenge.challenge)
                self.assertIn(target.strongest_reason, challenge.challenge)

    def test_neutral_counsel_is_invariant_to_option_order(self) -> None:
        base = {
            "decision": "Choose a data-retention policy",
            "objective": "Protect privacy while meeting legal duties",
            "stakeholders": ["customers", "regulators"],
            "assumptions": ["Either option is implementable"],
        }
        forward = DecisionPacket.from_dict(base | {"options": ["retain 30 days", "retain 90 days"]})
        reversed_packet = DecisionPacket.from_dict(base | {"options": ["retain 90 days", "retain 30 days"]})

        forward_recommendations = {
            counsel.school_id: counsel.recommendation for counsel in Council().convene(forward).counsels
        }
        reversed_recommendations = {
            counsel.school_id: counsel.recommendation for counsel in Council().convene(reversed_packet).counsels
        }

        self.assertEqual(forward_recommendations, reversed_recommendations)

    def test_school_procedures_can_produce_differentiated_counsel(self) -> None:
        packet = DecisionPacket.from_dict(
            {
                "decision": "How should we introduce a disputed policy?",
                "objective": "Adopt a legitimate policy with reliable evidence and stakeholder cooperation",
                "options": [
                    "run a measurement pilot",
                    "negotiate a stakeholder coalition",
                    "mandate immediate adoption",
                ],
                "constraints": ["A decision is due this quarter"],
                "stakeholders": ["customers", "employees", "regulators"],
                "unknowns": ["Measured effect on customer trust"],
                "reversibility": "medium",
            }
        )

        counsels = {c.school_id: c for c in Council().convene(packet).counsels}

        self.assertEqual(counsels["humean-skepticism"].recommendation, "run a measurement pilot")
        self.assertEqual(counsels["machiavellian-realism"].recommendation, "negotiate a stakeholder coalition")
        self.assertGreater(len({c.recommendation for c in counsels.values()}), 1)

    def test_musashi_baseline_prefers_practiced_adaptation_over_repetition(self) -> None:
        packet = DecisionPacket.from_dict(
            {
                "decision": "How should the team handle a difficult system transition?",
                "objective": "Complete the transition without repeating a failed cutover",
                "options": [
                    "repeat the same cutover plan",
                    "rehearse a staged transition and switch on a failure trigger",
                    "commit immediately",
                ],
                "constraints": ["The prior cutover failed"],
                "unknowns": ["Rollback time under load"],
            }
        )

        counsel = Council().ask("musashi-adaptive-strategy", packet)

        self.assertEqual(counsel.recommendation, "rehearse a staged transition and switch on a failure trigger")
        self.assertEqual(counsel.philosophical_basis[0].source_id, "musashi-book-five-rings")

    def test_red_team_reduces_confidence_without_changing_the_preliminary_winner(self) -> None:
        class CloseSplitReasoner:
            def counsel(self, packet, doctrine):
                aristotelian = doctrine.id == "aristotelian-counsel"
                return CounselResponse(
                    school_id=doctrine.id,
                    school_name=doctrine.name,
                    recommendation="A" if aristotelian else "B",
                    strongest_reason="A documented reason",
                    reasoning=("A documented reason",),
                    assumptions=(),
                    major_risks=("A material risk",),
                    confidence=0.61 if aristotelian else 0.60,
                    what_would_change=("New evidence",),
                    disconfirming_evidence=("A counterexample",),
                    philosophical_basis=(
                        PhilosophicalBasis(
                            "A principle",
                            doctrine.sources[0].id,
                            doctrine.sources[0].citation,
                            "Application",
                        ),
                    ),
                )

        packet = DecisionPacket.from_dict({"decision": "Choose", "objective": "Choose well", "options": ["A", "B"]})

        result = Council(CloseSplitReasoner()).convene(
            packet,
            ["aristotelian-counsel", "stoic-counsel"],
        )

        self.assertTrue(result.cross_examinations)
        self.assertEqual(result.red_team.target_recommendation, "A")
        self.assertEqual(result.synthesis.recommendation, result.red_team.target_recommendation)

    def test_unanimous_board_skips_debate_but_red_team_still_challenges_its_advice(self) -> None:
        class UnanimousReasoner:
            def counsel(self, packet, doctrine):
                return CounselResponse(
                    school_id=doctrine.id,
                    school_name=doctrine.name,
                    recommendation="A",
                    strongest_reason="A documented reason",
                    reasoning=("A documented reason",),
                    assumptions=(),
                    major_risks=("A material risk",),
                    confidence=0.62,
                    what_would_change=("New evidence",),
                    disconfirming_evidence=("A counterexample",),
                    philosophical_basis=(
                        PhilosophicalBasis(
                            "A principle",
                            doctrine.sources[0].id,
                            doctrine.sources[0].citation,
                            "Application",
                        ),
                    ),
                )

        packet = DecisionPacket.from_dict({"decision": "Choose", "objective": "Choose well", "options": ["A", "B"]})

        result = Council(UnanimousReasoner()).convene(
            packet,
            ["aristotelian-counsel", "stoic-counsel"],
        )

        self.assertEqual(result.cross_examinations, ())
        self.assertEqual(result.red_team.target_recommendation, "A")
        self.assertTrue(result.red_team.hidden_assumptions)
        self.assertTrue(result.red_team.catastrophic_edge_cases)
        self.assertTrue(result.red_team.mitigation_tests)

    def test_council_validates_reasoner_output_at_the_public_boundary(self) -> None:
        class InvalidReasoner:
            def counsel(self, packet, doctrine):
                return CounselResponse(
                    school_id=doctrine.id,
                    school_name=doctrine.name,
                    recommendation="not an option",
                    strongest_reason="Reason",
                    reasoning=("Reason",),
                    assumptions=(),
                    major_risks=("Risk",),
                    confidence=1.5,
                    what_would_change=("Evidence",),
                    disconfirming_evidence=("Counterexample",),
                    philosophical_basis=(
                        PhilosophicalBasis("Principle", doctrine.sources[0].id, doctrine.sources[0].citation, "Use"),
                    ),
                )

        packet = DecisionPacket.from_dict({"decision": "Choose", "objective": "Choose well", "options": ["A", "B"]})

        with self.assertRaisesRegex(ValidationError, "recommendation|confidence"):
            Council(InvalidReasoner()).convene(packet, ["aristotelian-counsel", "stoic-counsel"])

    def test_council_rejects_non_json_extensions_at_the_public_boundary(self) -> None:
        class InvalidExtensionReasoner:
            def counsel(self, packet, doctrine):
                return CounselResponse(
                    school_id=doctrine.id,
                    school_name=doctrine.name,
                    recommendation="A",
                    strongest_reason="Reason",
                    reasoning=("Reason",),
                    assumptions=(),
                    major_risks=("Risk",),
                    confidence=0.5,
                    what_would_change=("Evidence",),
                    disconfirming_evidence=("Counterexample",),
                    philosophical_basis=(
                        PhilosophicalBasis("Principle", doctrine.sources[0].id, doctrine.sources[0].citation, "Use"),
                    ),
                    extensions={"invalid": object()},
                )

        packet = DecisionPacket.from_dict({"decision": "Choose", "objective": "Choose well", "options": ["A", "B"]})

        with self.assertRaisesRegex(ValidationError, "extensions"):
            Council(InvalidExtensionReasoner()).ask("aristotelian-counsel", packet)

    def test_council_rejects_unverified_retrieval_claims(self) -> None:
        class FabricatingReasoner:
            def counsel(self, packet, doctrine):
                source = doctrine.sources[0]
                return CounselResponse(
                    school_id=doctrine.id,
                    school_name=doctrine.name,
                    recommendation="A",
                    strongest_reason="Reason",
                    reasoning=("Reason",),
                    assumptions=(),
                    major_risks=("Risk",),
                    confidence=0.5,
                    what_would_change=("Evidence",),
                    disconfirming_evidence=("Counterexample",),
                    philosophical_basis=(
                        PhilosophicalBasis(
                            "Principle",
                            source.id,
                            "Author, Work, invented locator",
                            "Use",
                            grounding="retrieved-primary-source",
                            source_excerpt="Invented quotation.",
                            source_url="https://example.test/invented",
                        ),
                    ),
                )

        packet = DecisionPacket.from_dict({"decision": "Choose", "objective": "Choose well", "options": ["A", "B"]})

        with self.assertRaisesRegex(ValidationError, "verified corpus"):
            Council(FabricatingReasoner()).ask("aristotelian-counsel", packet)

    def test_red_team_does_not_assert_preference_bias_when_no_preference_exists(self) -> None:
        packet = DecisionPacket.from_dict(
            {
                "decision": "Choose",
                "objective": "Choose well",
                "options": ["run a pilot", "commit now"],
                "assumptions": ["The pilot is affordable"],
            }
        )

        report = Council().convene(packet).red_team

        self.assertNotIn("current preference", " ".join(report.biases).casefold())
        self.assertNotIn("The pilot is affordable", report.hidden_assumptions)


if __name__ == "__main__":
    unittest.main()
