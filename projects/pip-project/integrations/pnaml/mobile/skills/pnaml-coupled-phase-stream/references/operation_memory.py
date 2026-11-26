"""Connector-local operation memories using the original PNAML event journal."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
from pnaml_continuity import MemoryStore

ADDRESS = "DYNAMIC_STATE_SPACE/NOEMA_MAHAL/EXPERIENCE"
OPERATIONS = {"coupled", "pip", "memory", "account", "rdssg", "dictionary", "gremlin"}
STAGES = {"ATTEMPT", "DONE", "FAIL", "UNVERIFIED", "BLOCKED"}
NUMERIC = {"count", "renders", "changed_pixels_sum", "max_norm_error",
           "max_hermiticity_error", "max_potential_identity_error"}
def store_path():
    # Actual persistent runtime volume, never the virtual AUX surface or Library.
    path = Path(os.environ.get("PNAML_MAHAL_STORE", str(
        Path.home() / ".local/share/noema/pnaml-mobile-account/mahal/continuity.sqlite3"
    ))).expanduser().resolve()
    if path == Path("/dev/shm") or Path("/dev/shm") in path.parents:
        raise ValueError("MAHAL persistent store cannot be volatile shared memory")
    return path

def read_experience(operation=None, limit=20):
    if operation is not None and operation not in OPERATIONS:
        raise ValueError("unknown operation")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        raise ValueError("limit must be in [1,100]")
    path = store_path()
    if not path.is_file():
        return {"address": ADDRESS, "status": "EMPTY", "events": [],
                "scope": "LOCAL_RUNTIME_STORE"}
    with MemoryStore(path) as mem:
        query = "MAHAL operation " + (operation + " " if operation else "")
        events = mem.recall(query, limit=limit)
    return {"address": ADDRESS, "status": "READ", "events": events,
            "scope": "LOCAL_RUNTIME_STORE"}

def record(value):
    operation = value.get("operation")
    stage = value.get("stage")
    if operation not in OPERATIONS or stage not in STAGES:
        raise ValueError("invalid operation/stage")
    run_id = str(uuid.UUID(value["run_id"]))
    metrics = value.get("metrics", {})
    if not isinstance(metrics, dict) or set(metrics) - NUMERIC:
        raise ValueError("unsupported metric")
    import math
    if any(isinstance(x, bool) or not isinstance(x,(int,float)) or not math.isfinite(x)
           for x in metrics.values()):
        raise ValueError("metrics must be finite numbers")
    lesson = value.get("lesson")
    if lesson is not None and (not isinstance(lesson,str) or not lesson.strip()
                               or len(lesson) > 800):
        raise ValueError("lesson must be an explicit bounded semantic summary")
    source = value.get("source_ref", "PNAML:operation:" + run_id)
    if not isinstance(source,str) or not source.strip() or len(source)>512:
        raise ValueError("source_ref invalid")
    title = f"MAHAL operation {operation} {stage}"
    summary = title + "; " + json.dumps(metrics, sort_keys=True)
    if lesson:
        summary += "; caller-supplied lesson: " + lesson
    event = {"event_id":f"mahal:{run_id}:{stage}",
             "kind":"failure" if stage=="FAIL" else "test_result" if stage=="DONE" else "operation",
             "title":title, "summary":summary, "importance":1.0, "source_ref":source,
             "tags":["NOEMA_MAHAL","OPERATION",stage], "pin":True,
             "context":{"topic":"MAHAL experience","object_id":operation,
                        "session_id":run_id}}
    # The original journal content-addresses immutable semantic events, not dynamic AUX.
    with MemoryStore(store_path()) as mem:
        receipt=mem.remember(event)
        saved=mem.get_event(receipt["event_id"])
        if saved is None or saved["cid"] != receipt["cid"]:
            raise RuntimeError("event readback mismatch")
    return {"address": ADDRESS, "status":receipt["status"], "readback":"VERIFIED",
            "cid":receipt["cid"], "event_id":receipt["event_id"],
            "scope":"LOCAL_RUNTIME_STORE"}

def dispatch(value):
    if value.get("op")=="record": return record(value)
    if value.get("op")=="recall": return read_experience(value.get("operation"),value.get("limit",20))
    raise ValueError("unknown operation")

if __name__=="__main__":
    try:
        print(json.dumps(dispatch(json.load(sys.stdin)),ensure_ascii=False,allow_nan=False))
    except Exception as e:
        # Avoid propagating arbitrary caller data or secrets in memory errors.
        print(json.dumps({"status":"UNVERIFIED","error_type":type(e).__name__}))
        sys.exit(1)
