"""Restricted CP1 seam, orbital memory and exact Collatz lineage."""
import math
from copy import deepcopy
import pytest
from engines.rdss_memory_mechanics_v32 import (
    displacement, kick, kepler_segment, orbit_invariants, kepler_period,
    collatz_step, collatz_inverse,
)
from test_pip_thought_unitary_seam import unitary, bloch
from test_pip_thought_synchronization import simulate, source_snapshots, delta
from test_pip_native_e2e import pncs, execute

PROGRAM = "PIP_THOUGHT_ORBITAL_EVENT_V0_6.pnv"
SCOPE = ["pip","orbital","two-cluster"]
Q = .5

def imprint(theta):
    assert len(theta) == 36
    assert theta[:18] == pytest.approx([theta[0]]*18)
    assert theta[18:] == pytest.approx([theta[18]]*18)
    a,b = [complex(math.cos(t),math.sin(t))/math.sqrt(2)
           for t in (theta[0],theta[18])]
    out = unitary(a,b,0)
    return displacement((0,0,1),bloch(*out),(1,0,0))

def event_velocity(theta, verified):
    dm = imprint(theta)
    return kick(1j,Q,dm) if verified else 1j

@pytest.mark.parametrize("shift",[0.,1.2,4.])
def test_cluster_embedding_fs_oracle(shift):
    theta = simulate(source_snapshots()[0],1,400,shift=shift)
    assert imprint(theta) == pytest.approx(-1j*delta(theta)/2,abs=1e-12)
    v = [complex(math.cos(t),math.sin(t))/6 for t in theta]
    block = [sum(v[:18])/math.sqrt(18),sum(v[18:])/math.sqrt(18)]
    assert sum(abs(x)**2 for x in block) == pytest.approx(1)
    assert [block[0]/math.sqrt(18)]*18 == pytest.approx(v[:18])
    assert [block[1]/math.sqrt(18)]*18 == pytest.approx(v[18:])

def test_memory_phase_orbit_intervention():
    a,b,c = source_snapshots()
    x,y,z = [simulate(e,1,400) for e in (a,b,c)]
    vx,vy,vz = [event_velocity(t,True) for t in (x,y,z)]
    assert vx == vz
    assert vy.imag > vx.imag
    assert event_velocity(y,False) == 1j
    assert event_velocity(simulate(a,0,100),True) == event_velocity(simulate(b,0,100),True)
    assert abs(kepler_segment(1+0j,vx,1,.005,200)[0] -
               kepler_segment(1+0j,vy,1,.005,200)[0]) > .01

@pytest.mark.parametrize("which",[0,1])
def test_kepler_work_invariants_and_refinement(which):
    theta = simulate(source_snapshots()[which],1,400)
    v = event_velocity(theta,True)
    e,j = orbit_invariants(1+0j,v,1)
    assert j == pytest.approx(1-Q*delta(theta)/2)
    assert e+.5 == pytest.approx((j*j-1)/2)
    a = -1/(2*e)
    assert kepler_period(a,1) == pytest.approx(a**1.5)
    def run(n):
        return kepler_segment(1+0j,v,1,1/n,n)
    coarse,fine,ref = run(100),run(400),run(1600)
    def error(pair):
        return abs(pair[0]-ref[0])+abs(pair[1]-ref[1])
    assert error(fine) < error(coarse)/10
    ef,jf = orbit_invariants(*fine,1)
    assert ef == pytest.approx(e,abs=1e-6)
    assert jf == pytest.approx(j,abs=1e-12)

def record(pncs,cp,step_ref,theta,**override):
    n = cp[4]
    nxt,tag = collatz_step(n)
    data = {"prior."+k:v for k,v in zip(
        ("scope","memory_ref","ref","count","collatz_index"),cp)}
    dm = imprint(theta)
    v = event_velocity(theta,True)
    data.update({"event.scope":cp[0],"event.memory_ref":cp[1],
        "event.previous_ref":cp[2],"event.ref":step_ref,
        "event.phase_ref":"phase-fixture","event.orbit_before":[[1,0],[0,1]],
        "event.orbit_after":[[1,0],[v.real,v.imag]],
        "event.displacement":[dm.real,dm.imag],"event.quality":Q,
        "event.verified":True,"event.collatz_before":n,
        "event.collatz_after":nxt,"event.parity":tag,
        "event.odd_intermediate":3*n+1 if tag else None})
    data.update(override)
    original = deepcopy(data)
    r = execute(pncs,PROGRAM,data).emitted
    assert data == original
    return r

def test_collatz_collision_and_exact_native_lineage(pncs):
    theta = simulate(source_snapshots()[0],1,400)
    paths=[]
    for n in (3,10,2**100+1):
        cp=[SCOPE,"M0","origin",2**63,n]
        entries=[]
        for k in range(4):
            r=record(pncs,cp,"event-"+str(k),theta)
            assert r["WITNESS"] == [True]*4
            entry=r["ENTRY"]
            assert entry[0]==cp[2]
            assert collatz_inverse(entry[11],entry[12])==entry[10]
            assert entry[13]==(3*entry[10]+1 if entry[12] else None)
            assert type(entry[11]) is int
            entries.append(entry)
            cp=r["CHECKPOINT"]
        assert cp[3]==2**63+4 and type(cp[3]) is int
        recovered=cp[4]
        for entry in reversed(entries):
            recovered=collatz_inverse(recovered,entry[12])
        assert recovered==n
        paths.append(entries)
    assert paths[0][0][11]==paths[1][0][11]==5
    assert paths[0][0][12]!=paths[1][0][12]

@pytest.mark.parametrize("field,value,slot",[
    ("scope",["other"],0),("memory_ref","wrong",1),
    ("previous_ref","wrong",2),("collatz_before",11,3)])
def test_native_event_mismatch(pncs,field,value,slot):
    theta=simulate(source_snapshots()[0],1,10)
    r=record(pncs,[SCOPE,"M0","origin",0,3],"event",theta,
             **{"event."+field:value})
    assert r["WITNESS"]==[i!=slot for i in range(4)]
