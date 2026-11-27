"""Finite multiple-support revalidation through original EBRE/PNV."""
from itertools import product
from copy import deepcopy
import pytest
from test_pip_native_e2e import pncs, execute, step
from engines.rdss_relational_dynamics_v32 import AdaptiveEdge, phase_step
from engines.rdss_memory_mechanics_v32 import collatz_step,collatz_inverse
import math

PROGRAM="PIP_EBRE_DEPENDENCY_REPAIR_V1_1.pnv"
PROOF="PIP_EBRE_FINITE_CASES_V1_0.pnv"
KEYS=("s","sq","qv","r","rv","vw")
FULL=(True,)*4
REVISED=(True,False,True,True)

def state(pncs,mask,flags,ref):
    p=execute(pncs,PROOF,{"theory.ref":ref,"occurrence.ref":ref+"-proof",
         **{"theory.c"+str(i):v for i,v in enumerate(mask)}})
    return {"ref":ref,"premises":list(mask),"primary":p.emitted["PROVED"],
            "proof_ref":p.receipt["receipt_sha256"],**dict(zip(KEYS,flags))}

def repair(pncs,a,b,ref="correction"):
    s={"revision.ref":ref,**{"before."+k:v for k,v in a.items()},
       **{"after."+k:v for k,v in b.items()}}
    original=deepcopy(s)
    out=execute(pncs,PROGRAM,s).emitted
    assert s==original
    return out

def oracle(a):
    alt=a["s"] and a["sq"]
    q=a["primary"] or alt
    qv=q and a["qv"]
    rv=a["r"] and a["rv"]
    v=qv or rv
    w=v and a["vw"]
    return [q,v,w],[a["primary"],alt,qv,rv,w]

def affected(a,b):
    q=any(a[k]!=b[k] for k in ("premises","s","sq"))
    v=q or any(a[k]!=b[k] for k in ("qv","r","rv"))
    w=v or a["vw"]!=b["vw"]
    return [q,v,w]

def test_exhaustive_support_and_single_source_revisions(pncs):
    # All 128 effective premise combinations and each single-edge flip.
    for mask in (FULL,REVISED):
        for flags in product((False,True),repeat=6):
            a=state(pncs,mask,flags,"old")
            b=state(pncs,REVISED if mask==FULL else FULL,flags,"new")
            for target in [b,*[{**a,"ref":"new",k:not a[k]} for k in KEYS]]:
                r=repair(pncs,a,target)
                before,bs=oracle(a)
                after,ats=oracle(target)
                assert r["B_STATUS"]==before and r["A_STATUS"]==after
                assert r["B_SUPPORTS"]==bs and r["A_SUPPORTS"]==ats
                assert r["RECHECK"]==affected(a,target)
                assert r["CHANGED"]==[x!=y for x,y in zip(before,after)]

@pytest.mark.parametrize("flags,expected,changed",[
    ((True,True,True,False,False,True),[True,True,True],[False,False,False]),
    ((False,False,True,True,True,True),[False,True,True],[True,False,False]),
    ((False,False,True,False,False,True),[False,False,False],[True,True,True]),
])
def test_correction_preserves_independent_support_and_history(pncs,flags,expected,changed):
    a=state(pncs,FULL,flags,"old")
    b=state(pncs,REVISED,flags,"new")
    out=repair(pncs,a,b)
    assert out["B_STATUS"]==[True]*3 and out["A_STATUS"]==expected
    assert out["RECHECK"]==[True]*3 and out["CHANGED"]==changed
    origin=execute(pncs,"PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv",
                   {"now.object":"origin"}).emitted
    old=step(pncs,origin,a["proof_ref"])
    corrected=step(pncs,old,"correction")
    assert corrected["HOTEL"]==old["NOW"] and corrected["INDEX"]==2
    assert out["RECORD"][3:5]==[a["proof_ref"],b["proof_ref"]]
    # Rebuild derived active route from currently supported proofs; old
    # adaptive edge remains immutable. Chosen test policy, not source law.
    base=AdaptiveEdge("left","right",.5,1.)
    def active(supports):
        m=base
        for j,ok in enumerate(supports[:2]):
            m=m.update("support-"+str(j),"fixture:proof",ok,0,1,1)
        return m
    prior=active(out["B_SUPPORTS"])
    current=active(out["A_SUPPORTS"])
    assert prior.conductance==current.conductance+1
    assert prior.history[0][2] is True and current.history[0][2] is False
    def evolve(edge,gain):
        phase=tuple([-math.pi/4]*18+[math.pi/4]*18)
        K=gain*edge.phase_weight()
        A=tuple(tuple(K/18 if (i<18)!=(j<18) else 0. for j in range(36)) for i in range(36))
        for _ in range(100):
            phase=phase_step(phase,(0.,)*36,A,(0.,)*36,.02)
        return phase
    assert evolve(prior,1)!=evolve(current,1)
    assert evolve(prior,0)==evolve(current,0)
    # Tagged Collatz genealogy belongs to previous successful ingest.
    n,tag=collatz_step(3)
    assert n==5 and collatz_inverse(n,tag)==3
    # A correction is not an inverse Hotel event, nor an inverse Collatz step.
    assert corrected["INDEX"]!=n
