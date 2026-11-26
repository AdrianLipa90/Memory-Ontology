"""Internal QHTRI surface address space, not a Linux mount or a new oscillator."""
import math
import json
from pathlib import Path
from copy import deepcopy
from vendor.phaseholomotion.aux_ternary_bridge import binary_lanes
from noema_publication import Publications, NAMESPACES, ALIASES
ROOT_ADDRESS = "DYNAMIC_STATE_SPACE/"
AUX_ADDRESS = ROOT_ADDRESS + "AUX"
FIELD_NAMES = ("phi", "phase36_lift", "omega", "g", "winding36", "tick", "tau", "generation", "qhtri", "trits12", "AUX")
MAHAL_KEY = "NOEMA_MAHAL"
MAHAL_ADDRESS = ROOT_ADDRESS + MAHAL_KEY
EXPERIENCE_ADDRESS = MAHAL_ADDRESS + "/EXPERIENCE"
DB_ADDRESS = ROOT_ADDRESS + "DB"
MMAP_ADDRESS = ROOT_ADDRESS + "MMAP"
def identity():
    return {"address": ROOT_ADDRESS, "owner": "PLUGIN_QHTRI", "kind": "INTERNAL_VIRTUAL_SURFACE", "mount_required": False, "separate_crystal": False}

class QHTRISurface:
    def __init__(self):
        self._fields = None
        self.pip_causal = None
        self.publications = Publications()
        self._source = None
        self._mahal = json.loads(Path(__file__).with_name("NOEMA_MAHAL_SCENE_V1.json").read_text(encoding="utf-8"))
    def bind(self, result, omega, g):
        # The existing Coupler is the sole producer. Keep references to its
        # actual output fields; phi is the wrapped view of the same lift.
        self._fields = {"phi": [x % (2*math.pi) for x in result["phase36_lift"]],
            "phase36_lift": result["phase36_lift"], "omega": omega, "g": g,
            "winding36": result["winding36"], "tick": result["sequence"],
            "tau": result["tau"], "generation": result["generation"],
            "qhtri": result["qhtri"], "trits12": result["trits12"]}
        self._source = result["source"]
        self.publications.bind(result)
    def attach_publications(self, scene, terminal, unpack_paths):
        self.publications.attach(scene, terminal, unpack_paths)
    def dispatch_terminal(self, packet):
        return self.publications.dispatch_terminal(packet)
    def aux_status(self):
        if self._fields is None: return "AWAITING_FRAME"
        return "UNKNOWN_TRITS" if self._fields["trits12"] is None else "EXPLICIT_TRITS"
    def read_aux(self):
        # Derive a read-only view from exactly the bound frame, not another
        # producer, a persisted snapshot, or the hashed AUX3 wire witness.
        f = self._fields
        trits = None if f is None else f["trits12"]
        return {"schema": "PNAML_NOEMA_TERNARY_AUX_V1", "address": AUX_ADDRESS,
            "status": self.aux_status(), "source": self._source,
            "generation": None if f is None else f["generation"],
            "sequence": None if f is None else f["tick"],
            "tau": None if f is None else f["tau"],
            "phase36_lift": None if f is None else list(f["phase36_lift"]),
            "winding36": None if f is None else list(f["winding36"]),
            "trits12": None if trits is None else list(trits),
            "binary_downstream": None if trits is None else binary_lanes(trits),
            "hold_count": None if trits is None else trits.count(0),
            "native_host_verified": False, "dynamic_hashing": False}
    def describe(self):
        f=self._fields
        return {**identity(), "status": "BOUND" if f is not None else "OPEN_AWAITING_QHTRI_FRAME",
            "source": self._source, "generation": None if f is None else f["generation"],
            "sequence": None if f is None else f["tick"], "tau": None if f is None else f["tau"],
            "fields": list(FIELD_NAMES) + ["PIP_CAUSAL"], "native_host_verified": False,
            "aux_address": AUX_ADDRESS, "aux_status": self.aux_status(),
            "published_namespaces": [ROOT_ADDRESS+n for n in NAMESPACES],
            "scene_namespaces": [MAHAL_ADDRESS], "experience_address": EXPERIENCE_ADDRESS,
            "storage_namespaces": [DB_ADDRESS, MMAP_ADDRESS]}
    def open(self, address=ROOT_ADDRESS):
        if address in (ROOT_ADDRESS,ROOT_ADDRESS.rstrip("/")): return self
        if not isinstance(address,str) or not address.startswith(ROOT_ADDRESS): raise KeyError(address)
        key=address[len(ROOT_ADDRESS):]
        if key == 'PIP_CAUSAL' or key.startswith('PIP_CAUSAL/'):
            if self.pip_causal is None: return {'status': 'AWAITING_PIP_BINDING'}
            return self.pip_causal.read(key[len('PIP_CAUSAL'):])
        if key.split("/",1)[0] in (*NAMESPACES, *ALIASES):
            return self.publications.read(key)
        if address.rstrip("/") == AUX_ADDRESS: return self.read_aux()
        if address.rstrip("/") in (DB_ADDRESS, MMAP_ADDRESS):
            from storage_inventory import inventory
            return inventory(address.rstrip("/"))
        if address in (EXPERIENCE_ADDRESS, EXPERIENCE_ADDRESS+"/"):
            from operation_memory import read_experience
            try:
                return read_experience()
            except Exception as exc:
                return {"address": EXPERIENCE_ADDRESS, "status": "UNVERIFIED",
                        "error_type": type(exc).__name__}
        if key in (MAHAL_KEY, MAHAL_KEY+"/"):
            return deepcopy(self._mahal)
        if key.startswith(MAHAL_KEY+"/"):
            room_id=key[len(MAHAL_KEY)+1:]
            for room in self._mahal["rooms"]:
                if room["id"]==room_id: return deepcopy(room)
            raise KeyError(address)
        if key not in FIELD_NAMES: raise KeyError(address)
        if self._fields is None: raise LookupError("QHTRI has not produced a frame")
        return self._fields[key]
    def read(self, address):
        value=self.open(address)
        return self.describe() if value is self else value
