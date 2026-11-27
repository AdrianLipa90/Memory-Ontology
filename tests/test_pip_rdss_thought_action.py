"""Finite source crosswalk; host quadrature is a test fixture, not an engine."""
import math
from copy import deepcopy

import pytest
from engines.rdss_memory_mechanics_v32 import Memory
from engines.rdss_relational_dynamics_v32 import disk_distance, duration
from test_pip_native_e2e import pncs, execute
from test_pip_thought_path_interference import holonomy, fold

PROGRAM = "PIP_THOUGHT_ACTION_STEP_V0_2"
KEYS = ("path","context","memory_ref","start","current","scale",
        "total","duration","count","lineage")


def seed(path="p", snapshot="M0", start="a"):
    return [path,"ctx",snapshot,start,start,1,0,0,0,[]]


def step(pncs, cp, edge, start, end, kinetic, potential, dt, **overrides):
    s = {"action."+k:v for k,v in zip(KEYS,cp)}
    s.update({"segment.path":cp[0],"segment.context":cp[1],
              "segment.memory_ref":cp[2],"segment.start":start,
              "segment.end":end,"segment.scale":cp[5],
              "segment.kinetic_integral":kinetic,"segment.potential_integral":potential,
              "segment.duration":dt,"segment.source_ref":["fixture",cp[2],edge],
              "segment.edge":edge})
    s.update(overrides)
    original=deepcopy(s)
    r=execute(pncs,PROGRAM+".pnv",s).emitted
    assert s==original
    return r


def quadrature(q0,q1,traffic,dl,weight,beta):
    # Source geometry + declared constant-speed geodesic action profile.
    dt=duration([(*traffic,dl)])
    assert dt>0 and weight>0
    length=disk_distance(q0,q1)
    return length**2/(2*dt), beta/weight*dt, dt


def path(pncs, coords, ids, weights, beta=0, snapshot="M0", name="p", times=None):
    times=times or [((.5,.5),1)]*(len(coords)-1)
    cp=seed(name,snapshot,ids[0])
    ds=[]
    for n,(x,y) in enumerate(zip(coords,coords[1:])):
        traffic,dl=times[n]
        k,u,dt=quadrature(x,y,traffic,dl,weights[n],beta)
        r=step(pncs,cp,name+str(n),ids[n],ids[n+1],k,u,dt)
        assert r["WITNESS"]==[True]*5
        ds.append(r["DELTA_S"])
        cp=r["CHECKPOINT"]
    assert cp[4]==ids[-1]
    assert cp[6]==pytest.approx(math.fsum(ds))
    return cp,ds


def test_refinement_and_stationarity(pncs):
    # Real diameter: d(0,tanh(s/2))=s. Fixed total duration 2.
    end=math.tanh(1)
    mid=math.tanh(.5)
    direct,_=path(pncs,[0,end],["a","b"],[1],times=[((.5,.5),2)])
    refined,_=path(pncs,[0,mid,end],["a","m","b"],[1,1])
    assert direct[6:8]==pytest.approx([1,2])
    assert refined[6:8]==pytest.approx(direct[6:8])
    for shift in (-.2,-.01,.01,.2):
        other,_=path(pncs,[0,math.tanh((1+shift)/2),end],
                     ["a","m","b"],[1,1])
        assert other[6]==pytest.approx(1+shift**2)
        assert other[6]>refined[6]


def test_idt_and_signed_action(pncs):
    # Equal integrated IDT duration despite changed parameterization.
    a,_=path(pncs,[0,.3],["a","b"],[1],beta=2,
             times=[((.5,.5),1)])
    b,_=path(pncs,[0,.3],["a","b"],[1],beta=2,
             times=[((1,1),.5)])
    assert a[6:8]==pytest.approx(b[6:8])
    assert a[6]<0


def coherent(pncs,holonomy,weight,beta,snapshot):
    scope=["family",["ctx",snapshot],"a","b",1]
    sum_cp=scope+[0,0,0,[]]
    actions=[]
    # Mirror corridors have exactly equal geometric action at equal weights.
    for name,mid,weights in [("left",.3j,[1,1]),("right",-.3j,[weight,1])]:
        cp,ds=path(pncs,[0,mid,.5],["a",name,"b"],weights,beta,snapshot,name)
        actions.append(cp[6])
        z=holonomy.semantic_u1_coupling(1+0j,[s/cp[5] for s in ds])
        # Preserve complete action lineage in the existing sum entry reference.
        r=fold(pncs,sum_cp,[name,cp], [name+"0",name+"1"],
               (z.real,z.imag),scope=scope)
        assert r["WITNESS"]==[True]*5
        sum_cp=r["CHECKPOINT"]
    return abs(complex(*sum_cp[5:7]))**2,actions,sum_cp


@pytest.mark.parametrize("beta",[0,.5,1,2,math.pi,2*math.pi])
def test_memory_only_intervention(pncs,holonomy,beta):
    before=Memory("right-edge",.2,(1,1,1,1,1),"mass-ref")
    after=before.encounter("verified","fixture",True,1,1,0)
    failed=before.encounter("failed","fixture",False,1,1,0)
    assert before.accessibility==after.accessibility==failed.accessibility
    assert before.mass==after.mass and before.exact_realization_mass==after.exact_realization_mass
    assert (before.learned_weight,after.learned_weight,failed.learned_weight)==(1,2,1)
    a,aa,acp=coherent(pncs,holonomy,before.learned_weight,beta,"M0")
    b,ba,bcp=coherent(pncs,holonomy,after.learned_weight,beta,"M1")
    f,_,_=coherent(pncs,holonomy,failed.learned_weight,beta,"Mfail")
    assert a==pytest.approx(4) and f==pytest.approx(a)
    assert ba[1]-ba[0]==pytest.approx(beta/2)
    assert aa[1]-aa[0]==pytest.approx(0)
    assert b==pytest.approx(2+2*math.cos(beta/2),abs=1e-12)
    assert acp[8]!=bcp[8]
    assert before.history==() and after.history[0][0]=="verified"


@pytest.mark.parametrize("field,value,slot",[
    ("path","wrong",0),("context","wrong",1),("memory_ref","wrong",2),
    ("scale",2,3),("start","wrong",4)])
def test_scope_visible(pncs,field,value,slot):
    r=step(pncs,seed(),"e","a","b",2,1,1,**{"segment."+field:value})
    assert r["WITNESS"]==[i!=slot for i in range(5)]


def test_exact_integrated_components(pncs):
    n=10**100
    a=step(pncs,seed(),"e","a","m",n,1,2)
    b=step(pncs,a["CHECKPOINT"],"f","m","b",1,n,3)
    assert a["TOTAL"]==n-1 and b["TOTAL"]==0 and b["DURATION"]==5
    assert type(b["TOTAL"]) is int
    assert b["CHECKPOINT"][8]==2
    assert b["CHECKPOINT"][9][1][0]=="f"
