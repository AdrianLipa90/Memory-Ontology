"""Original PNV finite proof-by-cases and source-kernel memory intervention."""
from itertools import product
from copy import deepcopy
import math
import pytest
from test_pip_native_e2e import pncs, execute, step
from test_pip_thought_orbital_memory import imprint
from engines.rdss_memory_mechanics_v32 import (
    Memory, branch_address, collatz_step, collatz_inverse, kick, kepler_segment)
from engines.rdss_relational_dynamics_v32 import AdaptiveEdge, phase_step
from engines.reconstruction.orbital_reconstruction import reconstruct, authorize_output

PROGRAM="PIP_EBRE_FINITE_CASES_V1_0.pnv"

def proof(pncs,mask,ref="attempt"):
    s={"theory.ref":["fixture",*mask],"occurrence.ref":ref,
       **{"theory.c"+str(i):b for i,b in enumerate(mask)}}
    before=deepcopy(s)
    out=execute(pncs,PROGRAM,s).emitted
    assert s==before
    return out

@pytest.mark.parametrize("mask",list(product((False,True),repeat=4)))
def test_exhaustive_against_classical_truth_table(pncs,mask):
    r=proof(pncs,mask)
    expected=[[],[]]
    for h,p,a,q in product((False,True),repeat=4):
        clauses=(h or p,(not h) or a,(not p) or q,(not a) or q)
        model=all(not use or ok for use,ok in zip(mask,clauses))
        if not q:
            expected[int(h)].append(model)
        elif p and a:
            assert model  # both hypothesis branches satisfiable
    assert r["NEG_COUNTEREXAMPLES"]==expected[0]
    assert r["POS_COUNTEREXAMPLES"]==expected[1]
    assert r["BRANCHES"]==[not any(v) for v in expected]
    assert r["PROVED"]==all(not any(v) for v in expected)
    assert r["CERTIFICATE"][-1]==r["PROVED"]

def test_proof_memory_orbit_and_single_hotel(pncs):
    good=proof(pncs,(True,True,True,True),"proof")
    bad=proof(pncs,(True,False,True,True),"ablation")
    assert good["BRANCHES"]==[True,True] and good["PROVED"]
    assert bad["BRANCHES"]==[True,False] and not bad["PROVED"]
    # Bombelli–Euler address branches are orthogonal labels, not evidence.
    plus,minus=branch_address((1,)),branch_address((-1,))
    assert plus[0]-minus[0]==-1 and plus[1]!=minus[1]
    scope=["family","hypothesis","memory","graph","basis"]
    seam=execute(pncs,"PIP_THOUGHT_BALANCED_SEAM_V0_4.pnv",{
        "left.real":1,"left.imag":0,"right.real":-1,"right.imag":0,
        "left.depth":0,"right.depth":0,"left.scope":scope,"right.scope":scope,
        "left.ref":list(plus[1]),"right.ref":list(minus[1]),"seam.ref":"EBRE",
        "seam.phase_ref":"fixture"}).emitted
    assert seam["WITNESS"]==[True,True] and seam["OUTPUT"]==[[0,0],[2,0],1]
    # No authority to treat imagined content as a historical observation.
    assert authorize_output("INFERRED",provenance_verified=False)=="INFERRED"
    with pytest.raises(ValueError):
        authorize_output("RECALLED",provenance_verified=False)
    assert reconstruct([{"status":"IMAGINED","invariant":"Q",
        "projection_id":"branch","provenance_commitment":"fixture"}],
        min_support=1)["status"]=="INSUFFICIENT_EVIDENCE"
    origin=execute(pncs,"PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv",
                   {"now.object":"origin"}).emitted
    base=AdaptiveEdge("left","right",.5,1.)
    memory=Memory("relation",.5,(.5,)*5,"fixture-mass")
    def arm(result,gain):
        cert=result["CERTIFICATE"]
        event=cert[1]
        verified=result["PROVED"]
        # Actual occurrence = proof attempt, not truth of H or a recalled event.
        hotel=step(pncs,origin,event)
        edge=base.update(event,"fixture:certificate",verified,0,1,1)
        m=memory.encounter(event,"fixture:certificate",verified,1,1,0)
        n,tag=collatz_step(3) if verified else (3,None)
        if verified:
            assert collatz_inverse(n,tag)==3
        theta=tuple([-math.pi/4]*18+[math.pi/4]*18)
        K=gain*edge.phase_weight()
        A=tuple(tuple(K/18 if (i<18)!=(j<18) else 0. for j in range(36))
                for i in range(36))
        for _ in range(100):
            theta=phase_step(theta,(0.,)*36,A,(0.,)*36,.02)
        v=kick(1j,.5,imprint(theta))
        orbit=kepler_segment(1+0j,v,1,.01,100)
        return hotel,edge,m,n,theta,orbit
    x,y=arm(good,1),arm(bad,1)
    assert x[0]["INDEX"]==y[0]["INDEX"]==1
    assert x[0]["HOTEL"]==y[0]["HOTEL"]==origin["NOW"]
    assert x[0]["NOW"]!=y[0]["NOW"]
    assert x[1].conductance==2 and y[1].conductance==1
    assert x[2].learned_weight==2 and y[2].learned_weight==1
    assert x[2].identity==y[2].identity and x[2].mass==y[2].mass
    assert x[3]==5 and y[3]==3
    assert abs(x[4][18]-x[4][0]) < abs(y[4][18]-y[4][0])
    assert abs(x[5][0]-y[5][0]) > .01
    assert arm(good,0)[4:]==arm(bad,0)[4:]


def test_native_reuse_and_dependency_revision(pncs):
    mask=(True,True,True,True)
    source={"theory.ref":"T","occurrence.ref":"original-proof",
            **{"theory.c"+str(i):b for i,b in enumerate(mask)}}
    first=execute(pncs,PROGRAM,source)
    cert=first.emitted["CERTIFICATE"]
    data={"cached.theory":cert[0],"cached.premises":cert[2],
          "cached.proved":cert[-1],"cached.occurrence":cert[1],
          "cached.receipt_ref":first.receipt["receipt_sha256"],
          "query.theory":"T","query.premises":list(mask),
          "query.occurrence":"later-query"}
    def reuse(**updates):
        return execute(pncs,"PIP_EBRE_REUSE_V1_0.pnv",{**data,**updates}).emitted
    assert reuse()["REUSABLE"] is True
    assert reuse()["INFERENCE"][-1][0]=="original-proof"
    assert reuse(**{"query.theory":"T-next"})["W"]==[False,True,True]
    revised=[True,False,True,True]
    assert reuse(**{"query.premises":revised})["REUSABLE"] is False
    assert not proof(pncs,tuple(revised))["PROVED"]
    assert reuse(**{"cached.proved":False})["REUSABLE"] is False
