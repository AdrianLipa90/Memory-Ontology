"""Exact native seam and existing RDSS/PNCS conformance; no runtime engine."""
from copy import deepcopy
import math
import random

import pytest
from engines.rdss_memory_mechanics_v32 import Memory, fs_log, norm
from engines.rdss_relational_dynamics_v32 import seam, seam_inverse, phase_readout36
from test_pip_native_e2e import pncs, execute
from test_pip_thought_path_interference import holonomy
from test_pip_rdss_thought_action import quadrature, seed, step

PROGRAM = "PIP_THOUGHT_BALANCED_SEAM_V0_4.pnv"
ROTATE = "PIP_THOUGHT_C4_TRANSPORT_V0_3.pnv"
SCOPE = ["family","context","memory","graph","basis"]

def apply(pncs,a,b,d,**overrides):
    s={"left.real":a[0],"left.imag":a[1],"right.real":b[0],"right.imag":b[1],
       "left.depth":d,"right.depth":d,"left.scope":SCOPE,"right.scope":SCOPE,
       "left.ref":["left",d],"right.ref":["right",d],
       "seam.ref":["seam",d],"seam.phase_ref":["phase",d]}
    s.update(overrides)
    original=deepcopy(s)
    r=execute(pncs,PROGRAM,s).emitted
    assert s==original
    return r

def energy_numerator(a,b):
    return sum(x*x for x in [*a,*b])

def rotate(pncs,a,k):
    return execute(pncs,ROTATE,{"amplitude.real":a[0],
        "amplitude.imag":a[1]}).emitted["ROTATIONS"][k]

@pytest.mark.parametrize("k",range(4))
def test_exact_c4_seam_matches_source(pncs,k):
    a,b=[3,-5],[-7,2]
    x,y=rotate(pncs,a,k),rotate(pncs,b,(-k)%4)
    r=apply(pncs,x,y,0)
    assert r["WITNESS"]==[True,True]
    bright,dark,d=r["OUTPUT"]
    assert d==1
    assert energy_numerator(bright,dark)==2*energy_numerator(a,b)
    source=seam(complex(*a),complex(*b),k*math.pi)
    assert [complex(*bright)/2,complex(*dark)/2]==pytest.approx(source)
    assert seam_inverse(*source,k*math.pi)==pytest.approx((complex(*a),complex(*b)))

def test_large_integer_exact_and_lineage(pncs):
    n=10**100
    a,b=[n,-n+1],[2*n,-3*n]
    first=apply(pncs,a,b,2**63)
    x,y,d=first["OUTPUT"]
    second=apply(pncs,x,y,d)
    assert second["OUTPUT"]==[[2*z for z in a],[2*z for z in b],2**63+2]
    assert energy_numerator(*second["OUTPUT"][:2])==4*energy_numerator(a,b)
    assert all(type(z) is int for z in [*x,*y,d])
    assert first["LINEAGE"]!=second["LINEAGE"]

@pytest.mark.parametrize("field,value,expected",[
    ("right.depth",1,[False,True]),("right.scope",["other"],[True,False])])
def test_scope_witness(pncs,field,value,expected):
    assert apply(pncs,[1,0],[0,0],0,**{field:value})["WITNESS"]==expected

def unitary(a,b,phi):
    return tuple(math.sqrt(2)*z for z in seam(a,b,phi))

def norm2(v):
    return math.fsum(abs(x)**2 for x in v)

def fs(a,b):
    r=abs(sum(x.conjugate()*y for x,y in zip(a,b)))/math.sqrt(norm2(a)*norm2(b))
    return math.acos(min(1,max(0,r)))

def bloch(a,b):
    n=abs(a)**2+abs(b)**2
    z=a.conjugate()*b
    return (2*z.real/n,2*z.imag/n,(abs(a)**2-abs(b)**2)/n)

def test_unitary_preserves_overlap_and_fs_source():
    rng=random.Random(42)
    for _ in range(64):
        a,b,c,d=[complex(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(4)]
        phi=rng.uniform(-math.pi,math.pi)
        x,y=unitary(a,b,phi),unitary(c,d,phi)
        assert norm2(x)==pytest.approx(norm2((a,b)))
        assert sum(p.conjugate()*q for p,q in zip(x,y))==pytest.approx(a.conjugate()*c+b.conjugate()*d)
        assert fs(x,y)==pytest.approx(fs((a,b),(c,d)),abs=1e-12)
        assert norm(fs_log(bloch(a,b),bloch(c,d)))==pytest.approx(fs((a,b),(c,d)),abs=1e-12)

def test_36d_equal_amplitude_profile():
    v=[.4*math.sin(.31*j) for j in range(36)]
    q=[x+.8*math.sin(.63*j) for j,x in enumerate(v)]
    a=[complex(math.cos(x),math.sin(x))/6 for x in v]
    b=[complex(math.cos(x),math.sin(x))/6 for x in q]
    r=phase_readout36(v,q)["relation"]
    assert fs(a,b)==pytest.approx(math.acos(math.sqrt(r)),abs=1e-12)
    shift=[.3*math.cos(j) for j in range(36)]
    assert phase_readout36([x+s for x,s in zip(v,shift)],[x+s for x,s in zip(q,shift)])["relation"]==pytest.approx(r)
    assert fs(a,[1j*x for x in a])==pytest.approx(0,abs=3e-8)

@pytest.mark.parametrize("beta",[0,1,math.pi,2*math.pi,4*math.pi])
def test_balanced_rdss_memory_intervention(pncs,holonomy,beta):
    base=Memory("right",.2,(1,1,1,1,1),"mass-ref")
    learned=base.encounter("verified","fixture",True,1,1,0)
    failed=base.encounter("failed","fixture",False,1,1,0)
    assert learned.accessibility==base.accessibility and learned.mass==base.mass
    def evaluate(memory,tag):
        phases=[]
        for name,mid,w in [("l",.3j,1),("r",-.3j,memory.learned_weight)]:
            cp=seed(name,tag,"a")
            ds=[]
            for j,(u,v,x,y,weight) in enumerate([("a",name,0,mid,w),(name,"b",mid,.5,1)]):
                k,p,t=quadrature(x,y,(.5,.5),1,weight,beta)
                r=step(pncs,cp,name+str(j),u,v,k,p,t)
                assert r["WITNESS"]==[True]*5
                ds.append(r["DELTA_S"])
                cp=r["CHECKPOINT"]
            phases.append(ds)
        split=apply(pncs,[1,0],[0,0],0)["OUTPUT"]
        z=[holonomy.semantic_u1_coupling(complex(*pair)/math.sqrt(2),phase)
           for pair,phase in zip(split[:2],phases)]
        # Exact numerator seam also supports finite float components, d=0.
        r=apply(pncs,[z[0].real,z[0].imag],[z[1].real,z[1].imag],0)
        assert r["WITNESS"]==[True,True]
        output=tuple(complex(*p)/math.sqrt(2) for p in r["OUTPUT"][:2])
        assert output==pytest.approx(unitary(*z,0))
        assert norm2(output)==pytest.approx(1)
        return output
    a,b,c=evaluate(base,"M0"),evaluate(learned,"M1"),evaluate(failed,"MF")
    assert abs(a[0])**2==pytest.approx(1)
    assert abs(a[1])**2==pytest.approx(0,abs=1e-12)
    assert c==pytest.approx(a)
    assert abs(b[0])**2==pytest.approx(math.cos(beta/4)**2,abs=1e-12)
    assert abs(b[1])**2==pytest.approx(math.sin(beta/4)**2,abs=1e-12)
    assert fs(a,b)==pytest.approx(math.acos(abs(math.cos(beta/4))),abs=3e-8)
