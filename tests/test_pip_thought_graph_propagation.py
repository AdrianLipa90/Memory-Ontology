"""Native graph-fold conformance. Layer scheduling below is test-only."""
from copy import deepcopy
from itertools import product
import math

import pytest
from engines.rdss_memory_mechanics_v32 import Memory
from test_pip_native_e2e import pncs, execute
from test_pip_thought_path_interference import holonomy
from test_pip_rdss_thought_action import quadrature, seed, step

VERTEX = "PIP_THOUGHT_GRAPH_VERTEX_STEP_V0_3.pnv"
ROTATE = "PIP_THOUGHT_C4_TRANSPORT_V0_3.pnv"
SCOPE = ["family","context","M0","graph",1]
KEYS = ("family","context","memory","graph","scale","layer","node",
        "real","imag","count","lineage")


def vertex(scope,k,node,z=(0,0),n=0):
    return list(scope)+[k,node,*z,n,[]]


def fold_vertex(pncs,cp,previous,edge,contribution,**overrides):
    # edge = (immutable edge id, source, target, phase, amplitude weight).
    eid,u,v,phase,w=edge
    s={"vertex."+k:x for k,x in zip(KEYS,cp)}
    s.update({"incoming.predecessor_ref":previous[:7],
              "incoming.edge_ref":eid,"incoming.graph":previous[3],
              "incoming.scale":previous[4],"incoming.source":u,
              "incoming.target":v,"incoming.action_ref":[eid,phase,w],
              "incoming.real":contribution[0],"incoming.imag":contribution[1],
              "incoming.count":previous[9]})
    s.update(overrides)
    original=deepcopy(s)
    r=execute(pncs,VERTEX,s).emitted
    assert s==original
    return r


def layers(pncs,holonomy,nodes,edges,h,*,exact=False,scope=SCOPE):
    # Static test scheduler; never enumerates paths or dispatches live AUX.
    current={v:vertex(scope,0,v,(int(v=="a"),0),int(v=="a")) for v in nodes}
    archive={(0,v):x for v,x in current.items()}
    for k in range(1,h+1):
        nxt={v:vertex(scope,k,v) for v in nodes}
        for edge in edges:
            eid,u,v,phase,w=edge
            prev=current[u]
            x,y=prev[7:9]
            if exact:
                assert type(phase) is int and 0<=phase<4 and w==1
                rot=execute(pncs,ROTATE,{"amplitude.real":x,"amplitude.imag":y})
                pair=rot.emitted["ROTATIONS"][phase]
            else:
                z=holonomy.semantic_u1_coupling(complex(x,y)*w,[phase])
                pair=(z.real,z.imag)
            r=fold_vertex(pncs,nxt[v],prev,edge,pair)
            assert r["WITNESS"]==[True]*4
            assert r["VERTEX_REF"]==r["CHECKPOINT"][:7]
            nxt[v]=r["CHECKPOINT"]
        current=nxt
        archive.update({(k,v):x for v,x in current.items()})
    return current,archive


def explicit(edges,h,holonomy):
    # Independent small-horizon oracle enumerates each ordered edge sequence.
    paths=[("a",1+0j)]
    for _ in range(h):
        paths=[(v,z*w*holonomy.semantic_u1_transport([p]))
               for node,z in paths for _,u,v,p,w in edges if u==node]
    return paths


def entries(lineage):
    out=[]
    while lineage:
        lineage,last=lineage
        out.append(last)
    return list(reversed(out))


@pytest.mark.parametrize("h",[0,1,2,3,5])
def test_cyclic_weighted_graph_against_enumeration(pncs,holonomy,h):
    nodes=["a","b","c","isolated"]
    edges=[("ab1","a","b",.2,.7),("ab2","a","b",1.1,.5),
           ("bc","b","c",-.3,1.2),("ca","c","a",.8,1),
           ("bb","b","b",.4,.8),("ac","a","c",-.9,.6)]
    current,archive=layers(pncs,holonomy,nodes,edges,h)
    oracle=explicit(edges,h,holonomy)
    for v,cp in current.items():
        values=[z for node,z in oracle if node==v]
        assert complex(*cp[7:9])==pytest.approx(sum(values),abs=1e-12)
        assert cp[9]==len(values)
        if h:
            for p,e,a,x,y,n in entries(cp[10]):
                assert archive[(p[5],p[6])][:7]==p
                assert archive[(p[5],p[6])][9]==n
                assert p[5]==h-1
    assert current["isolated"][9]==0


def test_exact_cancel_retains_distinct_paths(pncs,holonomy):
    edges=[("plus","a","b",0,1),("minus","a","b",2,1),
           ("next","b","c",1,1)]
    current,archive=layers(pncs,holonomy,["a","b","c"],edges,2,exact=True)
    b=archive[(1,"b")]
    assert b[7:10]==[0,0,2]
    assert [e[1] for e in entries(b[10])]==["plus","minus"]
    assert current["c"][7:10]==[0,0,2]
    assert entries(current["c"][10])[0][0]==b[:7]


def test_exponential_walk_count_without_enumeration(pncs,holonomy):
    edges=[("first","a","a",0,1),("second","a","a",0,1)]
    current,archive=layers(pncs,holonomy,["a"],edges,80,exact=True)
    assert current["a"][7:10]==[2**80,0,2**80]
    assert all(type(v) is int for v in current["a"][7:10])
    assert len(archive)==81
    assert sum(len(entries(x[10])) for x in archive.values())==160
    assert all(len(e[0])==7 for x in archive.values() for e in entries(x[10]))


def test_c4_exact_rotations(pncs):
    n=10**100
    r=execute(pncs,ROTATE,{"amplitude.real":n,"amplitude.imag":-n-1})
    assert r.emitted["ROTATIONS"]==[[n,-n-1],[n+1,n],[-n,n+1],[-n-1,-n]]


def test_gauge_and_edge_order(pncs,holonomy):
    nodes=["a","b","c"]
    edges=[("ab","a","b",.2,1),("ac","a","c",.7,1),
           ("bc","b","c",.1,.8),("ca","c","a",-.4,.6),
           ("cc","c","c",.3,1)]
    chi={"a":.2,"b":-.3,"c":1.1}
    shifted=[(e,u,v,p+chi[v]-chi[u],w) for e,u,v,p,w in edges]
    x,_=layers(pncs,holonomy,nodes,edges,5)
    y,_=layers(pncs,holonomy,nodes,shifted,5)
    r,_=layers(pncs,holonomy,nodes,list(reversed(edges)),5)
    for v in nodes:
        z=complex(*x[v][7:9]); zz=complex(*y[v][7:9])
        assert zz==pytest.approx(z*holonomy.semantic_u1_transport([chi[v]-chi["a"]]))
        assert abs(zz)**2==pytest.approx(abs(z)**2)
        assert complex(*r[v][7:9])==pytest.approx(z)
        assert x[v][9]==y[v][9]==r[v][9]


@pytest.mark.parametrize("beta",[0,1,2*math.pi])
def test_rdss_action_memory_controls(pncs,holonomy,beta):
    before=Memory("right",.2,(1,1,1,1,1),"mass-ref")
    after=before.encounter("event","fixture",True,1,1,0)
    fail=before.encounter("failed","fixture",False,1,1,0)
    coords={"a":0,"l":.3j,"r":-.3j,"b":.5}
    def evaluate(m,tag):
        scope=SCOPE.copy();scope[2]=tag
        edges=[]
        for eid,u,v in [("al","a","l"),("ar","a","r"),
                        ("lb","l","b"),("rb","r","b")]:
            w=m.learned_weight if eid=="ar" else 1
            k,p,dt=quadrature(coords[u],coords[v],(.5,.5),1,w,beta)
            action=step(pncs,seed(eid,tag,u),eid,u,v,k,p,dt)
            assert action["WITNESS"]==[True]*5
            edges.append((eid,u,v,action["DELTA_S"],1))
        state,_=layers(pncs,holonomy,list(coords),edges,2,scope=scope)
        assert state["b"][9]==2
        return abs(complex(*state["b"][7:9]))**2
    assert evaluate(before,"M0")==pytest.approx(4)
    assert evaluate(fail,"MF")==pytest.approx(4)
    assert evaluate(after,"M1")==pytest.approx(2+2*math.cos(beta/2),abs=1e-12)


@pytest.mark.parametrize("field,value,slot",[
    ("predecessor_ref",["wrong"],0),("target","wrong",1),
    ("graph","wrong",2),("scale",2,3)])
def test_scope_witness(pncs,field,value,slot):
    prev=vertex(SCOPE,0,"a",(1,0),1)
    cp=vertex(SCOPE,1,"b")
    r=fold_vertex(pncs,cp,prev,("edge","a","b",0,1),(1,0),
                  **{"incoming."+field:value})
    assert r["WITNESS"]==[i!=slot for i in range(4)]
