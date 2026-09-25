import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "representation-profile.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "representation-duality.json"


class RepresentationContractTest(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
        self.props = self.schema["properties"]

    def test_required_fields_exist(self):
        for key in self.schema["required"]:
            self.assertIn(key, self.example)

    def test_version_and_family(self):
        self.assertEqual(
            self.example["schema_version"],
            self.props["schema_version"]["const"],
        )
        self.assertIn(
            self.example["representation_family"],
            self.props["representation_family"]["enum"],
        )

    def test_epistemic_boundary(self):
        self.assertFalse(self.example["physical_substrate_claim"])
        self.assertEqual(self.example["evidence_status"], "formal_only")

    def test_equivalence_contract(self):
        eq = self.example["equivalence_contract"]
        self.assertGreaterEqual(eq["epsilon"], 0)
        self.assertTrue(eq["observable_contract"])
        self.assertIn("horizon", eq)

    def test_cost_metrics(self):
        allowed = set(self.props["cost_metrics"]["items"]["enum"])
        self.assertTrue(set(self.example["cost_metrics"]).issubset(allowed))
        self.assertIn("storage", self.example["cost_metrics"])
        self.assertIn("update_time", self.example["cost_metrics"])
        self.assertIn("query_time", self.example["cost_metrics"])


if __name__ == "__main__":
    unittest.main()
