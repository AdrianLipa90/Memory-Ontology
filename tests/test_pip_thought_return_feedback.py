"""Hybrid source-kernel return experiment; scheduling is a test fixture."""
import math
import cmath
from copy import deepcopy
import pytest
from engines.rdss_relational_dynamics_v32 import AdaptiveEdge, phase_step
from engines.rdss_memory_mechanics_v32 import (
    kick, kepler_segment, orbit_invariants, collatz_step, collatz_inverse)
from test_pip_thought_orbital_memory import imprint
from test_pip_thought_synchronization import initial, delta
from test_pip_native_e2e import pncs, execute

PROGRAM = "PIP_THOUGHT_RETURN_FEEDBACK_V0_7.pnv"
N = 36
SCOPE = ["pip","return","two-cluster"]
Q = .5

def experiment(feedback=True, gain=.2, flags=(True,True), dt=.02):
    base = AdaptiveEdge("left","right",.5,1.)
    edge = base
    theta = initial()
    z,v = 1+0j,1j
    angle = 0.
    n=3
    events=[]
    k=0
    # Two returns and one unit of subsequent free evolution.
    tail=math.ceil(1/dt)
    for j in range(math.ceil(40/dt)):
        active=edge if feedback else base
        K=gain*active.phase_weight()
        A=tuple(tuple(K/18 if (i<18)!=(l<18) else 0.
                      for l in range(N)) for i in range(N))
        theta=phase_step(theta,(0.,)*N,A,(0.,)*N,dt)
        new_z,new_v=kepler_segment(z,v,1,dt,1)
        step_angle=cmath.phase(z.conjugate()*new_z)
        assert 0 < step_angle < math.pi/2
        angle+=step_angle
        z,v=new_z,new_v
        if k < len(flags) and angle >= 2*math.pi*(k+1):
            verified=flags[k]
            before=edge
            old_v=v
            old_n=n
            ref="return-"+str(k)
            if verified:
                v=kick(v,Q,imprint(theta)*z/abs(z))
                n,tag=collatz_step(n)
            else:
                tag=None
            edge=edge.update(ref,["fixture",j+1],verified,0,Q,1)
            work=orbit_invariants(z,v,1)[0]-orbit_invariants(z,old_v,1)[0]
            assert work==pytest.approx(
                (old_v.conjugate()*(v-old_v)).real+abs(v-old_v)**2/2,
                abs=1e-12)
            events.append(dict(ref=ref,verified=verified,phase=theta,
                time=(j+1)*dt,z=z,old_v=old_v,v=v,before=before,after=edge,
                old_n=old_n,n=n,tag=tag,work=work))
            k+=1
        elif k==len(flags):
            tail-=1
            if tail==0:
                return events,(z,v),theta
    pytest.fail("fixture did not finish two returns and tail")

def test_feedback_intervention_and_zero_gain():
    a,xa,_=experiment(True)
    b,xb,_=experiment(False)
    assert a[0]==b[0]
    assert a[0]["after"].conductance==1.5
    assert a[1]["after"].conductance==b[1]["after"].conductance==2
    assert delta(a[1]["phase"]) < delta(b[1]["phase"])
    assert abs(a[1]["v"]-b[1]["v"]) > 1e-3
    assert abs(xa[0]-xb[0]) > 1e-3
    assert experiment(True,0)==experiment(False,0)

def test_failed_first_return_control():
    a,xa,_=experiment(True,flags=(False,True))
    b,xb,_=experiment(False,flags=(False,True))
    assert a==b
    assert a[0]["old_v"]==a[0]["v"]
    assert a[0]["before"].conductance==a[0]["after"].conductance
    assert a[0]["old_n"]==a[0]["n"]==3
    assert a[0]["tag"] is None
    assert a[0]["after"].history[0][2] is False
    # Feedback can only affect the tail after the second (verified) event.
    assert xa==xb

def test_return_refinement():
    coarse,_,_=experiment(dt=.04)
    fine,_,_=experiment(dt=.02)
    ref,_,_=experiment(dt=.005)
    for a,b,c in zip(coarse,fine,ref):
        assert abs(b["time"]-c["time"]) < .1
        assert abs(a["time"]-c["time"]) < .2
        assert abs(b["v"]-c["v"]) < .03
        assert b["n"]==c["n"] and b["tag"]==c["tag"]

@pytest.mark.parametrize("K",[0.,.1,.2,.4])
def test_lagrange_rayleigh_gradient_and_work(K):
    d=.8
    eps=1e-6
    U=lambda alpha,beta:K*(1-math.cos(beta-alpha))
    a,b=-d/2,d/2
    da=-(U(a+eps,b)-U(a-eps,b))/(2*eps)
    db=-(U(a,b+eps)-U(a,b-eps))/(2*eps)
    assert da==pytest.approx(K*math.sin(d),abs=1e-10)
    assert db==pytest.approx(-da,abs=1e-10)
    assert K*math.sin(d)*(db-da)==pytest.approx(-2*K*K*math.sin(d)**2)
    assert (K+.1)*(1-math.cos(d))-U(a,b)==pytest.approx(.1*(1-math.cos(d)))

def pack(event):
    cv=lambda x:[x.real,x.imag]
    return {"event.ref":event["ref"],"event.verified":event["verified"],
        "event.phase":list(event["phase"]),"event.time":event["time"],
        "event.orbit_before":[cv(event["z"]),cv(event["old_v"])],
        "event.orbit_after":[cv(event["z"]),cv(event["v"])],
        "event.index_before":event["old_n"],"event.index_after":event["n"],
        "event.parity":event["tag"],"event.work":event["work"]}

def native(pncs,cp,event,**overrides):
    data={"prior."+k:v for k,v in zip(
        ("scope","ref","memory_ref","index","count"),cp)}
    data.update(pack(event))
    data.update({"event.scope":cp[0],"event.previous_ref":cp[1],
        "event.memory_before":cp[2],"event.memory_after":event["ref"]+"-M"})
    data.update(overrides)
    original=deepcopy(data)
    r=execute(pncs,PROGRAM,data).emitted
    assert data==original
    return r

def test_native_feedback_genealogy(pncs):
    events,_,_=experiment()
    cp=[SCOPE,"origin","M0",3,2**63]
    entries=[]
    for event in events:
        r=native(pncs,cp,event)
        assert r["WITNESS"]==[True]*4
        entry=r["ENTRY"]
        assert entry[0]==cp[1] and entry[3]==cp[2]
        assert collatz_inverse(entry[11],entry[12])==entry[10]
        entries.append(entry)
        cp=r["CHECKPOINT"]
    assert cp[4]==2**63+2 and type(cp[4]) is int
    assert cp[3]==8
    assert entries[0][4]==entries[1][3]
    for field,value,slot in [("scope",["other"],0),
        ("previous_ref","wrong",1),("memory_before","wrong",2),
        ("index_before",99,3)]:
        r=native(pncs,[SCOPE,"origin","M0",3,0],events[0],
                 **{"event."+field:value})
        assert r["WITNESS"]==[i!=slot for i in range(4)]
