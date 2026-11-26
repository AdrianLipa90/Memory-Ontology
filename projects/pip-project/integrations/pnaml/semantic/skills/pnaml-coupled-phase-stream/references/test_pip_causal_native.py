import unittest
from pathlib import Path
from coupled_stream import Model, Coupler, ROOT, legacy_cli_view
from pip_hotel_native import CausalHotel, _pnv, _ORIGIN, _STEP
from noema_surface import ROOT_ADDRESS


class TestNativeCausalBinding(unittest.TestCase):
    def test_structural_equivalence_to_nested_native_pnv(self):
        h = CausalHotel()
        reference = None
        for n in range(64):
            obj = "same" if n % 2 else "other"
            h.advance(obj, "fixture", n)
            if reference is None:
                reference = _pnv.execute_pnv(_ORIGIN, sources={"now.object": obj}).emitted
            else:
                reference = _pnv.execute_pnv(_STEP, sources={
                    "now.node": reference["NOW"], "now.winding": reference["WINDING"],
                    "now.spinor_i_sign": reference["SIGN"], "next.object": obj,
                }).emitted
            # Dereferencing the one stored structural chain reproduces the
            # original nested PNV representation, not a second archive.
            reconstructed = None
            for k in range(n + 1):
                node = h.nodes[k]["node"]
                reconstructed = [reconstructed, *node[1:]]
            self.assertEqual(reconstructed, reference["NOW"])
            self.assertEqual(h.now, n)
        self.assertEqual(len(h.nodes), 64)
        self.assertEqual(h.describe()["occupied_past_count"], 63)

    def test_4096_occurrences_and_exact_navigation(self):
        h = CausalHotel()
        for n in range(4096):
            h.advance("repeat", "fixture", n)
        self.assertEqual(len(h.nodes), 4096)
        self.assertEqual(h.describe()["index"], 4095)
        self.assertEqual(h.describe()["hotel_head"], 4094)
        for n in (0, 1, 1024, 4094, 4095):
            row = h.lookup(n)
            self.assertEqual(row["index"], n)
            self.assertEqual(row["theta_pi_units"], 2*n)
            self.assertEqual(row["parent"], None if n == 0 else n-1)
            self.assertEqual(row["spinor_i_sign"], (-1)**(n % 2))
            self.assertEqual(row["role"], "TERAZ" if n == 4095 else "HOTEL")
        self.assertEqual(h.lookup("4096")["status"], "NOT_FOUND")

    def test_exact_native_integers_at_large_synthetic_seed(self):
        h = CausalHotel()
        for n in (2**53-1, 2**63, 10**100):
            # Explicit synthetic seed, not reconstruction of absent history.
            h.nodes = {n: {"node": [None, n, n, (-1)**(n % 2), 2*n, "seed"],
                           "source_frame": {"generation": "fixture", "sequence": 0}}}
            h.now = n
            h.advance("next", "fixture", 1)
            self.assertEqual(h.describe()["index"], n+1)
            self.assertEqual(h.lookup("NOW")["theta_pi_units"], 2*(n+1))
            self.assertEqual(h.lookup("NOW")["tau_effective"]["numerator"], n+1)

    def test_same_coupler_surface_explicit_events_only(self):
        c = Coupler(ROOT/"assets/poster_encoded.rdssg", 48, 72, 0, pip={
            "address": "5", "causal_events": [{"sequence": 2, "object_ref": "A"}]})
        s = c.noema_surface
        self.assertIs(s.pip_causal, c.pip.causal)
        self.assertEqual(s.read(ROOT_ADDRESS+"PIP_CAUSAL")["status"],
                         "AWAITING_EXPLICIT_OCCURRENCE")
        m = Model(42, .01)
        for k in range(1, 9):
            f = m.next()
            if k in (4, 7):
                f["pip_half_time"] = "A"
            out = c.consume(f)
            self.assertEqual(out["pip"]["causal"], s.read(ROOT_ADDRESS+"PIP_CAUSAL"))
            self.assertEqual(out["pip"]["Sigma"]["room"]["address"], "5")
            self.assertEqual(out["pip"]["phase"]["phase36_lift"], out["phase36_lift"])
            self.assertIs(s.open(ROOT_ADDRESS+"qhtri"), out["qhtri"])
            expected = None if k < 2 else (0 if k < 4 else 1 if k < 7 else 2)
            self.assertEqual(out["pip"]["causal"]["index"], expected)
        self.assertEqual(s.read(ROOT_ADDRESS+"PIP_CAUSAL/INDEX/0")["role"], "HOTEL")
        self.assertEqual(s.read(ROOT_ADDRESS+"PIP_CAUSAL/NOW")["role"], "TERAZ")
        self.assertEqual(s.read(ROOT_ADDRESS+"PIP_CAUSAL/HOTEL")["index"], 1)
        self.assertEqual(s.read(ROOT_ADDRESS+"PIP_CAUSAL/2")["object_ref"], "A")
        self.assertEqual(len(c.pip.causal.nodes), 3)


    def test_exact_native_vs_legacy_api_boundary(self):
        h = CausalHotel()
        n = 10**100
        h.nodes = {n: {"node": [None, n, n, 1, 2*n, "seed"],
                       "source_frame": {"generation": "fixture", "sequence": n}}}
        h.now = n
        h.advance("next", "fixture", n+1)
        native = h.describe()
        path = ROOT_ADDRESS+"PIP_CAUSAL/INDEX/"+str(n+1)
        item = h.lookup(n+1)
        frame = {"pip": {"causal": native}, "surface_reads": {path: item}}
        projected = legacy_cli_view(frame)
        self.assertEqual(h.lookup(n+1), h.lookup(str(n+1)))
        self.assertIs(type(native["index"]), int)
        self.assertIs(type(item["parent"]), int)
        self.assertIs(type(item["incoming_link"]), int)
        self.assertIs(type(item["source_frame"]["sequence"]), int)
        self.assertIs(type(item["tau_effective"]["denominator"]), int)
        self.assertEqual(native["index"], n+1)
        self.assertEqual(projected["pip"]["causal"]["index"], str(n+1))
        self.assertEqual(projected["surface_reads"][path]["parent"], str(n))
        self.assertEqual(projected["surface_reads"][path]["source_frame"]["sequence"], str(n+1))
        self.assertEqual(projected["surface_reads"][path]["tau_effective"]["denominator"], "2")
        self.assertEqual(frame["pip"]["causal"]["index"], n+1)
        self.assertEqual(h.lookup(n+1)["parent"], n)
        self.assertEqual(h.lookup(True)["status"], "NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
