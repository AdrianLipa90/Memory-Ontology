import importlib.util
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engines" / "reconstruction" / "orbital_reconstruction.py"
SCHEMA = ROOT / "schemas" / "holographic-memory-profile.schema.json"
EXAMPLE = ROOT / "examples" / "orbital-holographic-memory.json"

spec = importlib.util.spec_from_file_location("orbital_reconstruction", ENGINE)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class OrbitalHolographicStackTest(unittest.TestCase):
    def test_phase_wrap_preserves_address(self):
        kwargs = dict(
            orbit_class="A",
            scale="meso",
            boundary="ctx",
            relation_signature="rel",
            provenance_commitment="prov",
        )
        a = module.OrbitalAddress(phase_rad=0.25, **kwargs)
        b = module.OrbitalAddress(phase_rad=0.25 + math.tau, **kwargs)
        self.assertEqual(a.address_id(), b.address_id())

    def test_two_of_three_reconstruction(self):
        projections = [
            {"projection_id":"p1","invariant":"I","status":"COMMITTED","weight":1.0,"provenance_commitment":"a"},
            {"projection_id":"p2","invariant":"I","status":"OBSERVED","weight":1.0,"provenance_commitment":"b"},
            {"projection_id":"p3","invariant":"J","status":"CANDIDATE","weight":100.0,"provenance_commitment":"c"},
        ]
        result = module.reconstruct(projections, min_support=2)
        self.assertEqual(result["status"], "RECONSTRUCTED")
        self.assertEqual(result["invariant"], "I")
        self.assertEqual(result["support"], 2)

    def test_insufficient_support_fails_loud(self):
        result = module.reconstruct([
            {"projection_id":"p1","invariant":"I","status":"COMMITTED","weight":1.0,"provenance_commitment":"a"}
        ], min_support=2)
        self.assertEqual(result["status"], "INSUFFICIENT_EVIDENCE")

    def test_recalled_requires_provenance(self):
        with self.assertRaises(ValueError):
            module.authorize_output("RECALLED", provenance_verified=False)
        self.assertEqual(
            module.authorize_output("RECALLED", provenance_verified=True),
            "RECALLED",
        )

    def test_schema_and_example_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(example["schema_version"], schema["properties"]["schema_version"]["const"])
        for key in schema["required"]:
            self.assertIn(key, example)
        self.assertGreaterEqual(
            len(example["projections"]),
            example["reconstruction"]["min_support"],
        )


if __name__ == "__main__":
    unittest.main()
