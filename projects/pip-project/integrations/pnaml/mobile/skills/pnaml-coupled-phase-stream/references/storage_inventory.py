"""Read-only inventory of existing connector-configured storage. No creation."""
from pathlib import Path
import os
import sqlite3
from contextlib import closing

ROOT = "DYNAMIC_STATE_SPACE/"
def db_path():
    # Match the existing operation_memory.store_path default without importing the writer.
    return Path(os.environ.get("PNAML_MAHAL_STORE", str(
        Path.home() / ".local/share/noema/pnaml-mobile-account/mahal/continuity.sqlite3"
    ))).expanduser().resolve()

def db_inventory():
    p = db_path()
    result = {"address": ROOT+"DB", "path":str(p), "scope":"CURRENT_EXECUTOR_FILESYSTEM",
              "status":"NOT_FOUND", "tables":[], "created":False}
    try:
        if not p.is_file():
            return result
        result["size_bytes"]=p.stat().st_size
        # SQLite mode=ro: cannot create the database or write its contents.
        with closing(sqlite3.connect(p.as_uri()+"?mode=ro", uri=True, timeout=1)) as db:
            db.execute("PRAGMA query_only=ON")
            result["tables"]=[row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        result["status"]="FOUND_READ_ONLY"
    except (OSError,sqlite3.Error) as e:
        result.update(status="UNVERIFIED",error_type=type(e).__name__)
    return result

def mmap_inventory():
    # Use the original vendor schema, no ensure_surface/open r+ and no hashing.
    from ciel_geometry import noema_surface_mmap as htri
    root=htri.DEFAULT_SURFACE_ROOT
    description=htri.describe_surface(root)
    entries=[]
    for name,spec in description["files"].items():
        p=Path(spec["path"])
        entry={"name":name,"path":str(p),"shape":list(spec["shape"]),
               "dtype":spec["dtype"],"expected_bytes":spec["nbytes"],"status":"NOT_FOUND"}
        try:
            if p.is_file():
                size=p.stat().st_size
                entry.update(actual_bytes=size,status="FOUND_SIZE_MATCH" if size==spec["nbytes"] else "SIZE_MISMATCH")
        except OSError as e:
            entry.update(status="UNVERIFIED",error_type=type(e).__name__)
        entries.append(entry)
    return {"address":ROOT+"MMAP","root":str(root),"scope":"CURRENT_EXECUTOR_FILESYSTEM",
            "status":"FOUND" if any(x["status"]=="FOUND_SIZE_MATCH" for x in entries) else
                     "PARTIAL_OR_UNVERIFIED" if any(x["status"]!="NOT_FOUND" for x in entries) else "NOT_FOUND",
            "entries":entries,"created":False,"dynamic_hashing":False}
def inventory(address):
    if address==ROOT+"DB":return db_inventory()
    if address==ROOT+"MMAP":return mmap_inventory()
    raise KeyError(address)
