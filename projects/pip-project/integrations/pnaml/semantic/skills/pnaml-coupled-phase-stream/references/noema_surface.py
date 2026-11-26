"""Internal QHTRI surface address space, not a Linux mount or a new oscillator."""
import math
ROOT_ADDRESS = "DYNAMIC_STATE_SPACE/"
FIELD_NAMES = ("phi", "phase36_lift", "omega", "g", "winding36", "tick", "tau", "generation", "qhtri", "trits12")

def identity():
    return {"address": ROOT_ADDRESS, "owner": "PLUGIN_QHTRI", "kind": "INTERNAL_VIRTUAL_SURFACE", "mount_required": False, "separate_crystal": False}

class QHTRISurface:
    def __init__(self):
        self._fields = None
        self.pip_causal = None
        self._source = None
    def bind(self, result, omega, g):
        # The existing Coupler is the sole producer. Keep references to its
        # actual output fields; phi is the wrapped view of the same lift.
        self._fields = {"phi": [x % (2*math.pi) for x in result["phase36_lift"]],
            "phase36_lift": result["phase36_lift"], "omega": omega, "g": g,
            "winding36": result["winding36"], "tick": result["sequence"],
            "tau": result["tau"], "generation": result["generation"],
            "qhtri": result["qhtri"], "trits12": result["trits12"]}
        self._source = result["source"]
    def describe(self):
        f=self._fields
        return {**identity(), "status": "BOUND" if f is not None else "OPEN_AWAITING_QHTRI_FRAME",
            "source": self._source, "generation": None if f is None else f["generation"],
            "sequence": None if f is None else f["tick"], "tau": None if f is None else f["tau"],
            "fields": list(FIELD_NAMES) + ["PIP_CAUSAL"], "native_host_verified": False}
    def open(self, address=ROOT_ADDRESS):
        if address in (ROOT_ADDRESS,ROOT_ADDRESS.rstrip("/")): return self
        if not isinstance(address,str) or not address.startswith(ROOT_ADDRESS): raise KeyError(address)
        key=address[len(ROOT_ADDRESS):]
        if key == 'PIP_CAUSAL' or key.startswith('PIP_CAUSAL/'):
            if self.pip_causal is None: return {'status': 'AWAITING_PIP_BINDING'}
            return self.pip_causal.read(key[len('PIP_CAUSAL'):])
        if key not in FIELD_NAMES: raise KeyError(address)
        if self._fields is None: raise LookupError("QHTRI has not produced a frame")
        return self._fields[key]
    def read(self, address):
        value=self.open(address)
        return self.describe() if value is self else value
