"""Offline selected-event replay through existing PNAML components."""
import os
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]

@pytest.fixture
def sources(monkeypatch):
    variant = os.environ.get("PNAML_VARIANT")
    if not variant:
        pytest.skip("Run inside existing Mobile/Semantic variant CI")
    refs = ROOT/"integrations/pnaml"/variant/"skills/pnaml-coupled-phase-stream/references"
    monkeypatch.syspath_prepend(str(refs/"vendor"))
    monkeypatch.syspath_prepend(str(refs))
    monkeypatch.syspath_prepend(str(REPO/"tests"))
    from coupled_stream import Coupler, Model, ROOT as COUPLER_ROOT
    from vendor.pnaml_continuity.core import MemoryStore
    from test_pip_thought_return_feedback import experiment
    return Coupler, Model, COUPLER_ROOT, MemoryStore, experiment

def make_coupler(sources):
    Coupler, _, root, _, _ = sources
    return Coupler(root/"assets/poster_encoded.rdssg",48,72,0,pip={"address":"5"})

def selected_payload(e, frame, index):
    values = {
        "generation": str(frame["generation"]), "sequence": str(frame["sequence"]),
        "hotel_index": str(index), "verified": str(int(e["verified"])),
        "collatz_before": str(e["old_n"]), "collatz_after": str(e["n"]),
        "parity": "none" if e["tag"] is None else str(e["tag"]),
        "alpha": e["phase"][0].hex(), "beta": e["phase"][18].hex(),
        "z_real": e["z"].real.hex(), "z_imag": e["z"].imag.hex(),
        "v_real": e["v"].real.hex(), "v_imag": e["v"].imag.hex(),
        "model_time": e["time"].hex(),
    }
    event_id = "pip-v08-"+e["ref"]
    return {"event_id":event_id,"kind":"test_result",
            "title":"Pip v0.8 selected model return","summary":"Synthetic source observation",
            "source_ref":"fixture:v0.7:"+e["ref"],
            "context":{"session_id":"pip-v08-fixture","object_id":event_id},
            "relations":[{"source":event_id,"type":k,"target":v,"status":"fixture"}
                         for k,v in values.items()]}

def replay_records(store):
    receipt = store.verify()
    assert receipt["status"]=="PASS"
    cid=receipt["event_head"]
    chosen=[]
    while cid is not None:
        event=store.get_event(cid)
        assert event is not None
        context=next((s["payload"] for s in event["shards"]
                      if s["kind"]=="context"),{})
        if context.get("session_id")=="pip-v08-fixture":
            chosen.append(event)
        cid=event["prev_cid"]
    return list(reversed(chosen))

def relation_values(event):
    return {s["payload"]["type"]:s["payload"]["target"]
            for s in event["shards"] if s["kind"]=="typed_relation"}

@pytest.mark.parametrize("flags",[(True,True),(False,True)])
def test_selected_returns_restart_and_model_step(sources,tmp_path,flags):
    from engines.rdss_relational_dynamics_v32 import AdaptiveEdge, phase_step
    from engines.rdss_memory_mechanics_v32 import collatz_step,collatz_inverse,kepler_segment
    _, Model, _, Store, experiment = sources
    events,_,_=experiment(flags=flags)
    c=make_coupler(sources)
    model=Model(42,.01)
    db=tmp_path/"memory.sqlite"
    ids=[]
    with Store(db) as store:
        for k in range(1,8):
            frame=model.next()
            if k in (2,5):
                e=events[len(ids)]
                frame["pip_half_time"]="pip-v08-"+e["ref"]
            out=c.consume(frame)
            if k not in (2,5):
                continue
            now=c.pip.causal.lookup("NOW")
            assert now["object_ref"]==frame["pip_half_time"]
            assert now["index"]==len(ids) and now["index"]!=frame["sequence"]
            payload=selected_payload(e,now["source_frame"],now["index"])
            receipt=store.remember(payload)
            assert receipt["status"]=="COMMITTED"
            duplicate=store.remember(payload)
            assert duplicate["status"]=="DUPLICATE" and duplicate["cid"]==receipt["cid"]
            ids.append(payload["event_id"])
            if k==2:
                store.remember({"event_id":"unrelated","kind":"decision",
                    "title":"Unrelated journal event","summary":"Not a Hotel occurrence",
                    "source_ref":"fixture:unrelated"})
        assert store.verify()["events_checked"]==3
        original=[c.pip.causal.lookup(i) for i in range(2)]
        assert len(c.pip.causal.nodes)==2
    del c
    restarted=make_coupler(sources)
    assert restarted.pip.causal.now is None
    edge=AdaptiveEdge("left","right",.5,1.)
    index=3
    with Store(db) as reopened:
        records=replay_records(reopened)
        assert [r["event_id"] for r in records]==ids
        for r in records:
            values=relation_values(r)
            restarted.pip.causal.advance(r["event_id"],
                 values["generation"],int(values["sequence"]))
            assert restarted.pip.causal.now==int(values["hotel_index"])
            verified=values["verified"]=="1"
            assert index==int(values["collatz_before"])
            if verified:
                nxt,tag=collatz_step(index)
                assert tag==int(values["parity"])
                assert collatz_inverse(nxt,tag)==index
                index=nxt
            else:
                assert values["parity"]=="none"
            assert index==int(values["collatz_after"])
            # Journal source is the selected immutable event, not a mutable AUX sample.
            edge=edge.update(r["event_id"],r["source_ref"],verified,0,.5,1)
        last=relation_values(records[-1])
        assert index==events[-1]["n"]
        assert edge.conductance==events[-1]["after"].conductance
        assert edge.accessibility==events[-1]["after"].accessibility
        assert len(edge.history)==len(events)
        assert [restarted.pip.causal.lookup(i) for i in range(2)]==original
        assert restarted.pip.causal.describe()["occupied_past_count"]==1
        theta=tuple([float.fromhex(last["alpha"])]*18+[float.fromhex(last["beta"])]*18)
        z=complex(float.fromhex(last["z_real"]),float.fromhex(last["z_imag"]))
        v=complex(float.fromhex(last["v_real"]),float.fromhex(last["v_imag"]))
        assert theta==events[-1]["phase"] and z==events[-1]["z"] and v==events[-1]["v"]
        assert float.fromhex(last["model_time"])==events[-1]["time"]
        def next_step(t,z,v,m):
            K=.2*m.phase_weight()
            A=tuple(tuple(K/18 if (i<18)!=(j<18) else 0. for j in range(36))
                    for i in range(36))
            return phase_step(t,(0.,)*36,A,(0.,)*36,.02),kepler_segment(z,v,1,.02,1)
        e=events[-1]
        assert next_step(theta,z,v,edge)==next_step(e["phase"],e["z"],e["v"],e["after"])
