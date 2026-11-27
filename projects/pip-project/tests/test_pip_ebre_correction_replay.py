"""Selected correction replay in existing Mobile/Semantic journal, test only."""
import os
from pathlib import Path
import pytest
from phasenav_natural_code.native_pnv_exec_v01 import execute_pnv

ROOT=Path(__file__).resolve().parents[1]
KEYS=("s","sq","qv","r","rv","vw")

def run(name,sources):
    return execute_pnv((ROOT/"native"/name).read_text(),sources=sources)

def proof(mask,ref,flags):
    result=run("PIP_EBRE_FINITE_CASES_V1_0.pnv",{
        "theory.ref":ref,"occurrence.ref":ref+"-proof",
        **{"theory.c"+str(i):v for i,v in enumerate(mask)}})
    return {"ref":ref,"premises":list(mask),"primary":result.emitted["PROVED"],
            "proof_ref":result.receipt["receipt_sha256"],**dict(zip(KEYS,flags))}

def repair(a,b):
    return run("PIP_EBRE_DEPENDENCY_REPAIR_V1_1.pnv",{
        "revision.ref":"correction",**{"before."+k:v for k,v in a.items()},
        **{"after."+k:v for k,v in b.items()}}).emitted

def event(ref,mask,flags):
    values={**{"c"+str(i):v for i,v in enumerate(mask)},**dict(zip(KEYS,flags))}
    return {"event_id":ref,"kind":"test_result","title":"Selected EBRE premise snapshot",
            "summary":"Synthetic immutable premises, not AUX",
            "source_ref":"fixture:"+ref,
            "context":{"session_id":"ebre-v11","object_id":ref},
            "relations":[{"source":ref,"type":k,"target":"1" if v else "0","status":"fixture"}
                         for k,v in values.items()]}

@pytest.mark.parametrize("alternative",[True,False])
def test_selected_correction_journal_and_native_replay(monkeypatch,tmp_path,alternative):
    variant=os.environ.get("PNAML_VARIANT")
    if not variant:
        pytest.skip("Existing PNAML variant CI required")
    refs=ROOT/"integrations/pnaml"/variant/"skills/pnaml-coupled-phase-stream/references"
    monkeypatch.syspath_prepend(str(refs))
    monkeypatch.syspath_prepend(str(refs/"vendor"))
    from vendor.pnaml_continuity.core import MemoryStore
    from pip_hotel_native import CausalHotel
    masks=((True,)*4,(True,False,True,True))
    flags=(alternative,alternative,True,False,False,True)
    h=CausalHotel()
    db=tmp_path/"journal.sqlite"
    ids=("original","correction")
    with MemoryStore(db) as store:
        for k,(ref,mask) in enumerate(zip(ids,masks)):
            payload=event(ref,mask,flags)
            assert store.remember(payload)["status"]=="COMMITTED"
            assert store.remember(payload)["status"]=="DUPLICATE"
            h.advance(ref,"fixture",k+10)
        expected=repair(proof(masks[0],ids[0],flags),proof(masks[1],ids[1],flags))
        original=[h.lookup(i) for i in range(2)]
    del h
    restored=CausalHotel()
    with MemoryStore(db) as store:
        receipt=store.verify()
        assert receipt["status"]=="PASS" and receipt["events_checked"]==2
        b=store.get_event(receipt["event_head"])
        a=store.get_event(b["prev_cid"])
        assert a["prev_cid"] is None
        states=[]
        for k,row in enumerate((a,b)):
            assert row["event_id"]==ids[k]
            values={s["payload"]["type"]:s["payload"]["target"]=="1"
                    for s in row["shards"] if s["kind"]=="typed_relation"}
            mask=tuple(values["c"+str(i)] for i in range(4))
            fs=tuple(values[x] for x in KEYS)
            states.append(proof(mask,row["event_id"],fs))
            # Generation/sequence here are fixed fixture replay coordinates.
            restored.advance(row["event_id"],"fixture",k+10)
        actual=repair(*states)
        assert actual==expected
        assert actual["A_STATUS"]==[alternative]*3
        assert [restored.lookup(i) for i in range(2)]==original
