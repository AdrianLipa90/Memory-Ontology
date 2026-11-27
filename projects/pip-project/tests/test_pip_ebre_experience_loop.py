"""Finite environment and source GUIDE, not a replacement runtime."""
from itertools import product
from pathlib import Path
import os
import pytest
from phasenav_natural_code.native_pnv_exec_v01 import execute_pnv
from phasenav_natural_code.procedural_memory_runtime_v03 import (
    ProceduralMemoryRuntime, RouteState,
)

ROOT=Path(__file__).resolve().parents[1]
ENV="PIP_EBRE_ENVIRONMENT_STEP_V1_3.pnv"
START=[True,False,False]
ROUTES={"direct":(0,),"detour":(1,2)}

def run(name,data):
    return execute_pnv((ROOT/"native"/name).read_text(),sources=data).emitted

def transition(position,action,edges,ref):
    return run(ENV,{"state.start":position[0],"state.middle":position[1],
        "state.goal":position[2],"action.code":action,"action.ref":ref,
        "environment.ref":"fixture","environment.direct":edges[0],
        "environment.first":edges[1],"environment.second":edges[2]})

def traverse(route,edges,ref):
    pos=START[:]
    observations=[]
    for i,action in enumerate(ROUTES[route]):
        out=transition(pos,action,edges,ref+"-"+str(i))
        assert sum(out["NEXT"])==1
        assert out["ATTEMPT"] is True
        observations.append(out)
        pos=out["NEXT"]
        if out["BLOCKED"]:
            break
    assert len(observations)<=2
    return pos[2],observations

def runtime():
    return ProceduralMemoryRuntime("pip-experience",[
        RouteState("direct",("S","G"),.2),
        RouteState("detour",("S","M","G"),.1)],learning_rate=.2)

def proposal(status=0):
    proof=run("PIP_EBRE_FINITE_CASES_V1_0.pnv",{
        "theory.ref":"fixture","occurrence.ref":"proof",
        **{"theory.c"+str(i):True for i in range(4)}})
    assert proof["PROVED"] is True
    return run("PIP_EBRE_PROSPECTIVE_CHOICE_V1_2.pnv",{
        "goal.ref":"G","occurrence.ref":"proposal","allocation.accepted":3,
        "allocation.rejected":1,"allocation.history_ref":"fixture",
        "route.status":status,"inference.proved":proof["PROVED"],
        "context.ref":"fixture"})

def episode(mem,edges,ref,status=0,learn=True):
    policy=proposal(status)
    if not policy["PROPOSAL"][0]:
        return None,None,[]
    route=mem.guide(("direct","detour") if status==0 else ("detour",))
    success,obs=traverse(route,edges,ref)
    if learn:
        mem.apply_trace(route,outcome="POSITIVE" if success else "NEGATIVE",event_id=ref)
    return route,success,obs

@pytest.mark.parametrize("edges",list(product((False,True),repeat=3)))
@pytest.mark.parametrize("route",["direct","detour"])
def test_all_actual_edge_states(route,edges):
    success,obs=traverse(route,edges,"trial")
    assert success==(edges[0] if route=="direct" else edges[1] and edges[2])
    assert obs[-1]["NG"] is success
    assert obs[-1]["BLOCKED"] is (not success)
    if route=="detour" and edges[1] and not edges[2]:
        assert obs[-1]["NEXT"]==[False,True,False]

def test_wait_and_invalid_action_no_trace():
    for action in (2,3):
        out=transition(START,action,(True,True,True),"wait")
        assert out["NEXT"]==START and not out["ATTEMPT"] and not out["BLOCKED"]
    mem=runtime()
    for status in (2,3):
        assert episode(mem,(True,True,True),"not-run",status)==(None,None,[])
    assert not mem.receipts

def test_closed_learning_loop_and_intervention():
    edges=(False,True,True)
    learned,fixed=runtime(),runtime()
    a,b=[],[]
    for i in range(6):
        a.append(episode(learned,edges,"trial-"+str(i))[:2])
        b.append(episode(fixed,edges,"fixed-"+str(i),learn=False)[:2])
    assert a==[("direct",False)]+[("detour",True)]*5
    assert b==[("direct",False)]*6
    assert learned.route("direct").negative_traces==1
    assert learned.route("detour").positive_traces==5
    assert learned.route("direct").weight==pytest.approx(0)
    assert learned.route("detour").weight==pytest.approx(1.1)
    clone=learned.counterfactual({"direct":.2,"detour":.1})
    assert episode(clone,edges,"probe",learn=False)[:2]==("direct",False)
    assert episode(learned,edges,"probe",learn=False)[:2]==("detour",True)

def test_existing_journal_replay(monkeypatch,tmp_path):
    variant=os.environ.get("PNAML_VARIANT")
    if not variant:
        pytest.skip("Existing variant CI required")
    refs=ROOT/"integrations/pnaml"/variant/"skills/pnaml-coupled-phase-stream/references"
    monkeypatch.syspath_prepend(str(refs))
    monkeypatch.syspath_prepend(str(refs/"vendor"))
    from vendor.pnaml_continuity.core import MemoryStore
    from pip_hotel_native import CausalHotel
    mem,h=runtime(),CausalHotel()
    db=tmp_path/"experience.sqlite"
    edges=(False,True,True)
    with MemoryStore(db) as store:
        for i in range(6):
            ref="trial-"+str(i)
            route,success,obs=episode(mem,edges,ref)
            values={"route":route,"arrived":str(int(success)),
                    "direct":"0","first":"1","second":"1",
                    "sequence":str(i),"generation":"fixture"}
            payload={"event_id":ref,"kind":"test_result",
                "title":"Selected route execution","summary":"Immutable synthetic result",
                "source_ref":"fixture:"+ref,
                "context":{"session_id":"pip-v13","object_id":ref},
                "relations":[{"source":ref,"type":k,"target":v,"status":"fixture"}
                             for k,v in values.items()]}
            assert store.remember(payload)["status"]=="COMMITTED"
            h.advance(ref,"fixture",i)
            assert store.remember(payload)["status"]=="DUPLICATE"
        original=[h.lookup(i) for i in range(6)]
        snapshot=mem.snapshot()
        receipts=mem.receipts
    del mem,h
    restored,hotel=runtime(),CausalHotel()
    with MemoryStore(db) as store:
        verified=store.verify()
        assert verified["status"]=="PASS" and verified["events_checked"]==6
        entries=[]
        cid=verified["event_head"]
        while cid is not None:
            row=store.get_event(cid)
            entries.append(row)
            cid=row["prev_cid"]
        for row in reversed(entries):
            values={s["payload"]["type"]:s["payload"]["target"]
                for s in row["shards"] if s["kind"]=="typed_relation"}
            e=tuple(values[k]=="1" for k in ("direct","first","second"))
            ref=row["event_id"]
            route,success,_=episode(restored,e,ref)
            assert route==values["route"] and success==(values["arrived"]=="1")
            hotel.advance(ref,values["generation"],int(values["sequence"]))
        assert restored.snapshot()==snapshot and restored.receipts==receipts
        assert restored.guide()=="detour"
        assert [hotel.lookup(i) for i in range(6)]==original
