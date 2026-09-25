import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "memory-object.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "procedural-memory.json"


class RepositoryContractTest(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_required_fields_exist(self):
        for key in self.schema["required"]:
            self.assertIn(key, self.example)

    def test_schema_version(self):
        self.assertEqual(
            self.example["schema_version"],
            self.schema["properties"]["schema_version"]["const"],
        )

    def test_enum_memberships(self):
        props = self.schema["properties"]

        for value in self.example["retained_objects"]:
            self.assertIn(value, props["retained_objects"]["items"]["enum"])

        self.assertIn(self.example["persistence"], props["persistence"]["enum"])

        for field in ("access", "plasticity", "effects"):
            allowed = props[field]["items"]["enum"]
            for value in self.example[field]:
                self.assertIn(value, allowed)

        self.assertIn(
            self.example["epistemic_status"],
            props["epistemic_status"]["enum"],
        )

    def test_procedural_core(self):
        retained = set(self.example["retained_objects"])
        self.assertTrue({"path", "topology"}.issubset(retained))
        self.assertIn("implicit", self.example["access"])
        self.assertTrue({"routing", "attractor"}.issubset(set(self.example["effects"])))


if __name__ == "__main__":
    unittest.main()
