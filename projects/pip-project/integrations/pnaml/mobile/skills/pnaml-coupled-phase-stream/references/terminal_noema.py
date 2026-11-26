"""Scoped read-only adapter over the existing Terminal36D dispatcher."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent/"vendor"))
from phasenav36d.terminal36d import Terminal36D
from phasenav36d.concept_gates import concept_gate
from noema_surface import QHTRISurface, ROOT_ADDRESS, DB_ADDRESS, MMAP_ADDRESS, MAHAL_ADDRESS, EXPERIENCE_ADDRESS, FIELD_NAMES
from noema_publication import NAMESPACES, ALIASES

READ_OPS={"PHASENAV_LIST_DIR","PHASENAV_INSPECT_PATH"}
class NoemaTerminal(Terminal36D):
    def __init__(self,surface):
        super().__init__()
        self.surface=surface
        self.capabilities["PHASENAV_LIST_DIR"]=(self.list_virtual,False,"READ")
        self.capabilities["PHASENAV_INSPECT_PATH"]=(self.inspect_virtual,False,"READ")
    @staticmethod
    def _sha(_):return None
    def list_virtual(self,p):
        path=p["path"].rstrip("/")
        if path==ROOT_ADDRESS.rstrip("/"):
            return {"address":ROOT_ADDRESS,"entries":[*FIELD_NAMES,*NAMESPACES,"DB","MMAP","NOEMA_MAHAL"],
                    "surface":self.surface.describe()}
        if path in (DB_ADDRESS,MMAP_ADDRESS,MAHAL_ADDRESS):
            return self.surface.read(path)
        if path.startswith(ROOT_ADDRESS) and path[len(ROOT_ADDRESS):] in (*NAMESPACES,*ALIASES):
            return self.inspect_virtual(p)
        raise KeyError("not a NOEMA directory")
    def inspect_virtual(self,p):
        path=p["path"].rstrip("/")
        if path in (DB_ADDRESS,MMAP_ADDRESS,MAHAL_ADDRESS,ROOT_ADDRESS.rstrip("/")):
            return self.surface.read(path)
        # Inventory only: do not return raw AUX fields or unrelated paths.
        if path.startswith(MAHAL_ADDRESS+"/") and path!=EXPERIENCE_ADDRESS:
            return self.surface.read(path)
        if path in (ROOT_ADDRESS+x for x in FIELD_NAMES):
            return {"address":path,"status":"BOUND" if self.surface.describe()["status"]=="BOUND" else "AWAITING_FRAME"}
        if path==EXPERIENCE_ADDRESS:return self.surface.read(path)
        if path.startswith(ROOT_ADDRESS):
            head=path[len(ROOT_ADDRESS):].split('/',1)[0]
            head=ALIASES.get(head,head)
            if head in NAMESPACES and "/" not in path[len(ROOT_ADDRESS):]:
                return {"address":path,"namespace":head,"status":"PUBLISHED_NAMESPACE", "surface_status":self.surface.describe()["status"],"read_route":"existing_surface.read(address)","raw_dynamic_state_returned":False}
        raise KeyError("not an address in this read-only NOEMA namespace")
    def execute(self,p):
        if p.get("schema")!="PHASENAV_ACTION_PACKET_V1":raise ValueError("invalid action packet")
        op=p.get("operation")
        if op not in READ_OPS:raise ValueError("operation not implemented by the NOEMA inventory adapter")
        # Semantic classification is informational. A typed operation already identifies the action.
        advisory=concept_gate("READ",p.get("intent",op)).__dict__
        receipt=super().execute({**p,"intent":"inspect read NOEMA inventory"})
        receipt["intent_classification"]=advisory
        receipt["intent_classification_authority"]="ADVISORY_ONLY_FOR_TYPED_NOEMA_READ"
        receipt["scope"]="CURRENT_EXECUTOR; NOT_AUTHENTICATED_REMOTE_HOST"
        receipt["dynamic_hashing"]=False
        return receipt

def main(p):
    # Standalone diagnostics create only an unbound virtual view, not a producer or new DB/MMAP.
    return NoemaTerminal(QHTRISurface()).execute(p)
if __name__=="__main__":
    print(json.dumps(main(json.load(sys.stdin)),ensure_ascii=False,allow_nan=False))
