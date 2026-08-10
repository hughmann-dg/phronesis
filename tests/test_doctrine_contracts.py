import unittest

from phronesis.council import Council
from phronesis.doctrines import list_doctrines
from phronesis.models import DecisionPacket


class DoctrinePublicContractTests(unittest.TestCase):
    def test_every_doctrine_executes_through_the_validated_public_seam(self) -> None:
        packet = DecisionPacket.from_dict(
            {
                "decision": "Choose a prudent next step",
                "objective": "Learn while limiting avoidable harm",
                "options": ["run a measured pilot", "commit now"],
                "stakeholders": ["customers", "employees"],
                "unknowns": ["Long-term effect"],
            }
        )

        for doctrine in list_doctrines():
            with self.subTest(doctrine=doctrine.id):
                response = Council().ask(doctrine.id, packet)
                self.assertEqual(response.school_id, doctrine.id)
                if doctrine.id == "socratic-examination":
                    self.assertIsNone(response.recommendation)
                else:
                    self.assertIn(response.recommendation, packet.options)


if __name__ == "__main__":
    unittest.main()
