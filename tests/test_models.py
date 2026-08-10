import json
from pathlib import Path
import unittest

from phronesis.models import DecisionPacket, ValidationError


class DecisionPacketTests(unittest.TestCase):
    def test_packet_normalizes_distinct_claim_types(self) -> None:
        packet = DecisionPacket.from_dict(
            {
                "decision": "Should we migrate System X during Q4?",
                "objective": "Reduce operational risk and technical debt.",
                "options": ["migrate now", "delay six months", "incremental migration"],
                "constraints": ["December production freeze"],
                "stakeholders": ["Operations", "Engineering"],
                "known_facts": ["Vendor support expires in March"],
                "assumptions": ["Operations can support a Q4 cutover"],
                "estimates": [{"text": "Migration takes eight weeks", "confidence": 0.6}],
                "opinions": ["The old system is frustrating"],
                "unknowns": ["Holiday incident volume"],
                "time_horizon": "12-24 months",
                "reversibility": "medium",
                "current_preference": "migrate now",
                "current_confidence": 0.7,
            }
        )

        self.assertEqual(packet.facts[0].text, "Vendor support expires in March")
        self.assertEqual(packet.assumptions[0].kind.value, "assumption")
        self.assertEqual(packet.estimates[0].confidence, 0.6)
        self.assertEqual(packet.unknowns[0].kind.value, "unknown")
        self.assertEqual(packet.to_dict()["current_confidence"], 0.7)

    def test_packet_rejects_preference_outside_options(self) -> None:
        with self.assertRaisesRegex(ValidationError, "current_preference"):
            DecisionPacket.from_dict(
                {
                    "decision": "Choose a path",
                    "objective": "Make progress",
                    "options": ["A", "B"],
                    "current_preference": "C",
                }
            )

    def test_normalized_claims_match_the_public_schema_properties(self) -> None:
        packet = DecisionPacket.from_dict(
            {
                "decision": "Choose",
                "objective": "Choose carefully",
                "options": ["A", "B"],
                "known_facts": [{"text": "Observed", "source": "Record 1"}],
            }
        )
        schema = json.loads(Path("schemas/decision-packet.schema.json").read_text(encoding="utf-8"))
        allowed = set(schema["$defs"]["claims"]["items"]["oneOf"][1]["properties"])

        self.assertLessEqual(set(packet.to_dict()["known_facts"][0]), allowed)

    def test_packet_rejects_properties_outside_the_public_schema(self) -> None:
        with self.assertRaisesRegex(ValidationError, "unexpected"):
            DecisionPacket.from_dict(
                {
                    "decision": "Choose",
                    "objective": "Choose carefully",
                    "options": ["A", "B"],
                    "unexpected": "silently accepting this would diverge from the schema",
                }
            )

    def test_claim_kind_cannot_contradict_its_packet_collection(self) -> None:
        with self.assertRaisesRegex(ValidationError, "kind"):
            DecisionPacket.from_dict(
                {
                    "decision": "Choose",
                    "objective": "Choose carefully",
                    "options": ["A", "B"],
                    "assumptions": [{"text": "Observed directly", "kind": "fact"}],
                }
            )

    def test_packet_rejects_both_fact_aliases_in_one_payload(self) -> None:
        with self.assertRaisesRegex(ValidationError, "known_facts|facts"):
            DecisionPacket.from_dict(
                {
                    "decision": "Choose",
                    "objective": "Choose carefully",
                    "options": ["A", "B"],
                    "known_facts": ["Observed one"],
                    "facts": ["Observed two"],
                }
            )


if __name__ == "__main__":
    unittest.main()
