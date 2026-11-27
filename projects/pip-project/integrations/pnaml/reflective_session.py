"""One executable offline PNAML/Pip integration profile.

Host orchestration only: original PNV, GUIDE, Coupler, Hotel and MemoryStore
own their respective operations. No new dispatcher, agent, database or wire.
This deterministic software model profile is not a live producer binding.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path
from copy import deepcopy

PIP = Path(__file__).resolve().parents[2]
REPO = PIP.parents[1]
PROGRAM = PIP/"native/PIP_EBRE_UNIFIED_TRANSITION_V1_3.pnv"
PREFIX = "PIP:REFLECTIVE:OFFLINE:"
KEYS = ("s","sq","qv","r","rv","vw")
ROUTES = {"direct":(0,), "detour":(1,2)}
START = [True,False,False]

def source_path(variant):
    if variant not in ("mobile","semantic"):
        raise ValueError("existing plugin variant required")
    return PIP/"integrations/pnaml"/variant/"skills/pnaml-coupled-phase-stream/references"

def activate_sources(variant):
    refs=source_path(variant)
    for p in (REPO,refs/"vendor",refs):
        if str(p) not in sys.path:
            sys.path.insert(0,str(p))
    return refs

class ReflectiveSession:
    """Selected-event orchestration over one existing software owner.

    A fresh owner is used on a deterministic model restart; original source
    generation is retained on old Hotel occurrences. No live AUX is replayed.
    The journal is the only persistent authority for this profile. On failure
    reopen from its verified committed events instead of retrying a partial
    in-memory mutation. One writer per explicitly selected session.
    """
    def __init__(self, journal, tcd_root, variant="mobile", *, seed=42, dt=.01):
        refs=activate_sources(variant)
        from coupled_stream import Coupler, Model
        from phasenav_natural_code.native_pnv_exec_v01 import execute_pnv
        from phasenav_natural_code.procedural_memory_runtime_v03 import ProceduralMemoryRuntime, RouteState
        from consciousness_dictionary.registry import Lexicon
        from engines.rdss_relational_dynamics_v32 import AdaptiveEdge
        self.execute=execute_pnv
        self.lex=Lexicon.load(Path(tcd_root)/"ontology/registry/v0_2",
            Path(tcd_root)/"ontology/relations/extra_relations.jsonl")
        self.model=Model(seed,dt)
        self.owner=Coupler(refs/"assets/poster_encoded.rdssg",48,72,0,
                           pip={"address":"5","memory":{"store_path":str(journal)}})
        self.store=self.owner.pip.memory.store
        self.hotel=self.owner.pip.causal
        self.profile={"seed":seed,"dt":dt,"variant":variant,"profile":"EBRE_OFFLINE_V1"}
        self.procedure=ProceduralMemoryRuntime("pip-reflective-offline",[
            RouteState("direct",("S","G"),.2),
            RouteState("detour",("S","M","G"),.1)],learning_rate=.2)
        self.edge=AdaptiveEdge("left","right",.5,1.)
        self.collatz=3
        self.orbit=(1+0j,1j)
        self.window=[True,True,True,False] # declared synthetic prior, not user history
        self.character=[0,0,0]
        self.character_ref=None
        self.theory={"ref":"initial","mask":[True]*4,"flags":[False,False,True,False,False,True]}
        self.last=None
        self.episodes=0
        self.failed=False
        try:
            self._restore()
        except Exception:
            self.close()
            raise

    def close(self):
        self.owner.pip.memory.close()

    def __enter__(self): return self
    def __exit__(self,*_): self.close()

    def pnv(self,name,data):
        return self.execute((PIP/"native"/name).read_text(),sources=data).emitted

    def _rows(self):
        receipt=self.store.verify()
        if receipt["status"]!="PASS":
            raise RuntimeError("PNAML journal verification failed")
        cid=receipt["event_head"]
        rows=[]
        while cid is not None:
            row=self.store.get_event(cid)
            if row is None:
                raise RuntimeError("journal lineage unavailable")
            if row["event_id"].startswith(PREFIX):
                rows.append(row)
            else:
                raise ValueError("offline profile requires an isolated selected journal; not a live or mixed journal")
            cid=row["prev_cid"]
        return list(reversed(rows))

    def _record(self,ref,body):
        payload={"event_id":ref,"kind":"test_result","title":"Pip reflective offline occurrence",
                 "summary":json.dumps(body,sort_keys=True,allow_nan=False),
                 "importance":1.0,"source_ref":"offline-model:"+ref,
                 "context":{"session_id":"pip-reflective-offline","object_id":ref},
                 "relations":[{"source":ref,"type":"profile","target":"EBRE_OFFLINE_V1","status":"fixture"}]}
        return self.store.remember(payload)

    def _tick(self,ref):
        # Explicit test constitutive profile, from existing RDSS phase_step.
        # Feed only the relative coupling increment to the ORIGINAL Model.
        # No invented production transform binding. No phase arrays persisted.
        from engines.rdss_relational_dynamics_v32 import phase_step
        target=None
        if self.last is not None:
            theta=tuple(self.last["phase36_lift"])
            K=.2*self.edge.phase_weight()
            A=tuple(tuple(K/18 if (i<18)!=(j<18) else 0. for j in range(36)) for i in range(36))
            p=phase_step(theta,(0.,)*36,A,(0.,)*36,self.profile["dt"])
            target={"phase_increment36":[x-y for x,y in zip(p,theta)],"source_ref":ref}
        self.last=self.owner.consume(self.model.next(target))
        return self.last

    def _restore(self):
        rows=self._rows()
        if not rows:
            ref=PREFIX+"origin"
            frame=self._tick(ref)
            body={"profile":self.profile,"generation":frame["generation"],"sequence":frame["sequence"]}
            receipt=self._record(ref,body)
            if receipt["status"]!="COMMITTED":
                raise RuntimeError("origin not committed")
            self.hotel.advance(ref,body["generation"],body["sequence"])
            return
        first=rows[0]
        body=json.loads(first["summary"])
        if first["event_id"]!=PREFIX+"origin" or body["profile"]!=self.profile:
            raise ValueError("offline profile/seed/dt mismatch")
        self._tick(first["event_id"])
        self.hotel.advance(first["event_id"],body["generation"],body["sequence"])
        for row in rows[1:]:
            saved=json.loads(row["summary"])
            if saved["command"]["ref"]!=row["event_id"]:
                raise RuntimeError("event identity mismatch")
            actual=self._episode(saved["command"],replay=saved)
            if actual["semantic"]!=saved["semantic"]:
                raise RuntimeError("selected event replay diverged")

    def _character_update(self,choice,ref,index):
        labels=["GO","HOLD"]
        a,b,n=self.character
        out=self.pnv("PIP_CHARACTER_DEPOSIT_STEP_V0_1.pnv",{
            "deposit.owner":"Pip","deposit.query_domain":"offline-comparable-allocation",
            "deposit.candidate_labels":labels,"deposit.label_a":"GO","deposit.label_b":"HOLD",
            "deposit.count_a":a,"deposit.count_b":b,"deposit.count":n,
            "deposit.previous_observation_ref":self.character_ref,
            "observation.ref":ref,"observation.owner":"Pip",
            "observation.query_domain":"offline-comparable-allocation",
            "observation.candidate_labels":labels,"observation.choice":labels[int(not choice)],
            "observation.vote_a":int(choice),"observation.vote_b":int(not choice),
            "observation.hotel_occurrence":index})
        if not all(out["WITNESS"]):
            raise RuntimeError("original character witness failed")
        self.character=out["CHECKPOINT"][3:6]
        self.character_ref=ref
        self.window=(self.window+[choice])[-4:]

    def _episode(self,cmd,replay=None):
        from consciousness_dictionary.query import external_phase_projection
        from engines.rdss_memory_mechanics_v32 import collatz_step,collatz_inverse,kepler_segment,kick,displacement
        from phasenav_natural_code.pnlf_orbit_governor_v01 import classify_phase9
        ref=cmd["ref"]
        frame=self._tick(ref)
        prior=self.hotel.nodes[self.hotel.now]["node"]
        data={"goal.ref":"G","occurrence.ref":ref,
              "revision.ref":ref,"allocation.accepted":sum(self.window),
              "allocation.rejected":4-sum(self.window),"allocation.history_ref":prior[5],
              "route.status":cmd["status"],"context.ref":cmd["theory"]["ref"],
              "now.node":self.hotel.now,"now.winding":prior[2],"now.spinor_i_sign":prior[3],
              "environment.ref":cmd["environment"],"environment.direct":cmd["edges"][0],
              "environment.first":cmd["edges"][1],"environment.second":cmd["edges"][2]}
        for side,t in (("before",self.theory),("after",cmd["theory"])):
            data.update({side+".ref":t["ref"],side+".proof_occurrence":t["ref"]+":proof"})
            data.update({side+".c"+str(i):v for i,v in enumerate(t["mask"])})
            data.update({side+"."+k:v for k,v in zip(KEYS,t["flags"])})
        # Existing GUIDE, not a replacement route selector. Policy is computed
        # inside the linked graph and suppresses movement when it says HOLD.
        candidates=("detour",) if cmd["status"]==1 else ("direct","detour")
        candidate=self.procedure.guide(candidates)
        pos=START[:]
        observations=[]
        for i,action in enumerate(ROUTES[candidate]):
            inp={**data,"action.code":action,"action.ref":ref+":"+str(i),
                 **dict(zip(("state.start","state.middle","state.goal"),pos))}
            out=self.execute(PROGRAM.read_text(),sources=inp).emitted
            observations.append(out["E.RECORD"])
            pos=out["E.NEXT"]
            if not out["E.ATTEMPT"] or out["E.BLOCKED"] or out["E.NG"]:
                break
        go=out["C.PROPOSAL"][0]
        arrived=bool(go and pos[2])
        # Route learning is an isolated synthetic procedural snapshot only,
        # never a digest of the owner AUX. Replay re-executes these exact traces.
        if go:
            self.procedure.apply_trace(candidate,outcome="POSITIVE" if arrived else "NEGATIVE",event_id=ref.replace(":","_"))
            self.edge=self.edge.update(ref,ref,arrived,0,1,1)
        tag=None
        if arrived:
            n,tag=collatz_step(self.collatz)
            if collatz_inverse(n,tag)!=self.collatz:
                raise RuntimeError("Collatz inverse mismatch")
            self.collatz=n
        # Existing FS displacement and Kepler reference, model units only.
        phases=frame["phase36_lift"]
        delta=math.atan2(math.sin(phases[18]-phases[0]),math.cos(phases[18]-phases[0]))
        z,v=self.orbit
        if arrived:
            dm=displacement((0.,0.,1.),(0.,-math.sin(delta),math.cos(delta)),(1.,0.,0.))
            v=kick(v,.05,dm)
        self.orbit=kepler_segment(z,v,1.,self.profile["dt"],1)
        # TCD projection uses actual owner frame; scores remain volatile.
        rows=external_phase_projection(self.lex,phases,limit=len(self.lex.terms))
        band=classify_phase9(phases[0],phases[18]).payload["orbital_band"]
        idx=out["H.INDEX"]
        if cmd["status"] in (0,1):
            self._character_update(go,ref,idx)
        semantic={"conclusions":out["R.A_STATUS"],"recheck":out["R.RECHECK"],
                  "proof":out["P1.CERTIFICATE"],"proposal":out["C.PROPOSAL"],
                  "route":candidate if go else None,"arrived":arrived,
                  "observations":observations,"hotel_index":idx,
                  "collatz":self.collatz,"tag":tag,"character":self.character[:],
                  "tcd_top":rows[0]["term_id"],"pnlf_band":band}
        if replay is not None:
            # Check semantic results before committing the reconstructed view.
            if semantic!=replay["semantic"]:
                raise RuntimeError("deterministic semantic replay mismatch")
            generation,sequence=replay["generation"],replay["sequence"]
            if sequence!=frame["sequence"]:
                raise RuntimeError("model replay sequence mismatch")
        else:
            generation,sequence=frame["generation"],frame["sequence"]
            body={"command":cmd,"semantic":semantic,"generation":generation,"sequence":sequence}
            receipt=self._record(ref,body)
            if receipt["status"]!="COMMITTED":
                raise RuntimeError("selected occurrence did not commit")
        self.hotel.advance(ref,generation,sequence)
        if self.hotel.nodes[idx]["node"]!=out["H.NOW"]:
            raise RuntimeError("Hotel linked transition differs from original successor")
        self.theory=deepcopy(cmd["theory"])
        self.episodes+=1
        return {"semantic":semantic,"source_frame":{"generation":generation,"sequence":sequence}}

    def advance(self,command):
        if self.failed:
            raise RuntimeError("reopen from verified journal after interrupted operation")
        cmd=deepcopy(command)
        ref=cmd.get("ref")
        if not isinstance(ref,str) or not ref.startswith(PREFIX) or ref==PREFIX+"origin":
            raise ValueError("explicit offline occurrence reference required")
        if set(cmd)!={"ref","status","theory","environment","edges"}:
            raise ValueError("explicit typed offline command required")
        if type(cmd["status"]) is not int or cmd["status"] not in range(4):
            raise ValueError("route status 0..3 required")
        t=cmd["theory"]
        if set(t)!={"ref","mask","flags"} or not isinstance(t["ref"],str):
            raise ValueError("theory reference and fixed family required")
        for x,n in ((t["mask"],4),(t["flags"],6),(cmd["edges"],3)):
            if not isinstance(x,list) or len(x)!=n or any(type(v) is not bool for v in x):
                raise ValueError("typed Boolean inputs required")
        if not isinstance(cmd["environment"],str):
            raise ValueError("environment reference required")
        old=self.store.get_event(ref)
        if old is not None:
            saved=json.loads(old["summary"])
            if saved["command"]!=cmd:
                raise ValueError("event identity collision")
            return {"status":"DUPLICATE","semantic":saved["semantic"]}
        try:
            return {"status":"COMMITTED",**self._episode(cmd)}
        except Exception:
            self.failed=True
            raise

    def snapshot(self):
        # Volatile diagnostic readout, never stored/hashes of live AUX.
        return {"episodes":self.episodes,"hotel":self.hotel.describe(),
                "procedure":self.procedure.snapshot(),"edge_weight":self.edge.phase_weight(),
                "collatz":self.collatz,"character":self.character[:],
                "phase36":self.last["phase36_lift"][:],
                "orbit":[[z.real,z.imag] for z in self.orbit],
                "theory":deepcopy(self.theory),"next_guide":self.procedure.guide(),
                "journal":self.store.verify(),"native_host_verified":False}

def demo_command(i):
    return {"ref":PREFIX+"episode-"+str(i),"status":0,
            "theory":{"ref":"T-"+str(i),"mask":[True,i==0,True,True],
                      "flags":[i>0,i>0,True,False,False,True]},
            "environment":"fixed-blocked-direct","edges":[False,True,True]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--journal",required=True)
    p.add_argument("--tcd-root",required=True)
    p.add_argument("--variant",choices=("mobile","semantic"),default="mobile")
    p.add_argument("--episodes",type=int,default=6)
    a=p.parse_args()
    with ReflectiveSession(a.journal,a.tcd_root,a.variant) as s:
        for i in range(s.episodes,s.episodes+a.episodes):
            print(json.dumps(s.advance(demo_command(i)),allow_nan=False),flush=True)
        state=s.snapshot()
        # No raw evolving phase output in default CLI receipt.
        del state["phase36"]
        print(json.dumps(state,allow_nan=False))

if __name__=="__main__":
    main()
