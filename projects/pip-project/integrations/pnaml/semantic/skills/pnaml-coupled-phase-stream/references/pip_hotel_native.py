"""PNAML binding of unchanged Pip PNV/1 transitions, not a replacement engine.

Hotel nodes are actual structural occurrences, indexed by their exact native
winding. Parent references avoid recursively copying the whole past.
Only explicit occurrence object references reach the PNV interpreter.
No AUX frame or evolving phase vector is hashed or persisted by this binding.
"""
from pathlib import Path
import importlib.util
import sys

_SKILLS = Path(__file__).resolve().parents[2]
_PROGRAMS = _SKILLS / "pnaml-pip-geometry" / "references"
_INTERPRETER = _SKILLS / "pnaml-pip-geometry" / "references" / "native_pnv_exec_v01.py"
_spec = importlib.util.spec_from_file_location("_pip_upstream_pnv", _INTERPRETER)
_pnv = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _pnv
_spec.loader.exec_module(_pnv)

_ORIGIN = (_PROGRAMS / "PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv").read_text(encoding="utf-8")
_STEP = (_PROGRAMS / "PIP_HOTEL_SERIAL_STEP_V0_2.pnv").read_text(encoding="utf-8")


class CausalHotel:
    """One serial structural Hotel in the existing Pip, local to this run."""
    def __init__(self, config=None):
        self.nodes = {}
        self.now = None
        self.schedule = {}
        self.last_receipt = None
        for event in (config or {}).get("causal_events", []):
            self.schedule.setdefault(event["sequence"], []).append(event["object_ref"])

    def advance(self, object_ref, generation, sequence):
        # Object references, not mutable AUX samples or an external edge ID.
        if not isinstance(object_ref, str) or not object_ref:
            raise ValueError("pip half-time requires an explicit nonempty object_ref")
        if self.now is None:
            result = _pnv.execute_pnv(_ORIGIN, sources={"now.object": object_ref})
        else:
            prev = self.nodes[self.now]["node"]
            result = _pnv.execute_pnv(_STEP, sources={
                "now.node": self.now,
                "now.winding": prev[2],
                "now.spinor_i_sign": prev[3],
                "next.object": object_ref,
            })
        n = result.emitted["INDEX"]
        self.nodes[n] = {
            "node": result.emitted["NOW"],
            "source_frame": {"generation": generation, "sequence": sequence},
        }
        self.now = n
        self.last_receipt = result.receipt["receipt_sha256"]

    def consume(self, result, frame):
        sequence, generation = result["sequence"], result["generation"]
        for object_ref in self.schedule.pop(sequence, []):
            self.advance(object_ref, generation, sequence)
        if "pip_half_time" in frame:
            self.advance(frame["pip_half_time"], generation, sequence)
        return self.describe()

    def lookup(self, key):
        if key == "NOW":
            n = self.now
        elif key == "HOTEL":
            n = None if self.now is None else self.nodes[self.now]["node"][0]
        else:
            if type(key) is int and key >= 0:
                n = key
            elif isinstance(key, str) and key.isascii() and key.isdecimal():
                n = int(key)
            else:
                return {"status": "NOT_FOUND", "requested": key}
        if n not in self.nodes:
            return {"status": "NOT_FOUND", "requested": key}
        record = self.nodes[n]
        parent, link, index, sign, theta, obj = record["node"]
        # Native surface: exact typed integers, with no serialization.
        return {"status": "FOUND", "role": "TERAZ" if n == self.now else "HOTEL",
                "index": index, "parent": parent,
                "incoming_link": link,
                "spinor_i_sign": sign, "theta_pi_units": theta,
                "tau_effective": {"numerator": index, "denominator": 2},
                "object_ref": obj, "source_frame": dict(record["source_frame"])}

    def describe(self):
        parent = None if self.now is None else self.nodes[self.now]["node"][0]
        return {"schema": "PIP_CAUSAL_HOTEL_PNV_V0_2_BINDING_V1",
                "status": "AWAITING_EXPLICIT_OCCURRENCE" if self.now is None else "BOUND",
                "noema_address": "NOEMA:PIP",
                "now": None if self.now is None else self.lookup("NOW"),
                "hotel_head": parent,
                "index": self.now,
                "occupied_past_count": len(self.nodes) - (self.now is not None),
                "scope": "CURRENT_COUPLER_RUN",
                "addressing": "CAUSAL_INDEX_DISTINCT_FROM_DYADIC_ROOM",
                "last_immutable_pnv_receipt": self.last_receipt,
                "native_host_verified": False, "dynamic_aux_hashing": False}

    def read(self, suffix):
        if suffix in ("", "/"):
            return self.describe()
        key = suffix.strip("/")
        if key.startswith("INDEX/"):
            key = key[len("INDEX/"):]
        return self.lookup(key)
