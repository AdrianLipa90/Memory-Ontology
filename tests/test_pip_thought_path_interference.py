"""Conformance through the original PNCS interpreter and U(1) reference."""
import importlib.util
import math
from copy import deepcopy
from pathlib import Path

import pytest
from test_pip_native_e2e import pncs, execute

PROGRAM = "PIP_THOUGHT_PATH_SUM_STEP_V0_1.pnv"
SCOPE = ["family", "context", "a", "b", 1]


@pytest.fixture(scope="module")
def holonomy(pncs):
    path = Path(pncs.__file__).with_name("semantic_u1_holonomy_v01.py")
    spec = importlib.util.spec_from_file_location("pip_existing_u1", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fold(pncs, cp, ref, edges, amplitude, scope=SCOPE):
    keys = ["family", "domain", "start", "end", "scale"]
    s = {"sum."+k:v for k,v in zip(keys,cp[:5])}
    s.update({"path."+k:v for k,v in zip(keys,scope)})
    s.update({"sum.real":cp[5], "sum.imag":cp[6], "sum.count":cp[7],
              "sum.lineage":cp[8], "path.ref":ref, "path.edges":edges,
              "path.real":amplitude[0], "path.imag":amplitude[1]})
    original = deepcopy(s)
    result = execute(pncs,PROGRAM,s).emitted
    assert s == original
    return result


def initial():
    return SCOPE + [0,0,0,[]]


def run(pncs,holonomy,paths):
    cp=initial()
    for ref, edges, phases, weight in paths:
        # Existing PNCS reference receives declared dimensionless action.
        z=holonomy.semantic_u1_coupling(complex(weight),phases)
        result=fold(pncs,cp,ref,edges,(z.real,z.imag))
        assert result["WITNESS"]==[True]*5
        cp=result["CHECKPOINT"]
    return complex(*cp[5:7]),cp


def pair(delta, weights=(1,1)):
    return [("left",["a-l","l-b"],[0,0],weights[0]),
            ("right",["a-r","r-b"],[delta/2,delta/2],weights[1])]


@pytest.mark.parametrize("delta,expected",[(0,4),(math.pi/2,2),(math.pi,0)])
def test_interference(pncs,holonomy,delta,expected):
    z,cp=run(pncs,holonomy,pair(delta))
    assert abs(z)**2==pytest.approx(expected,abs=1e-12)
    assert cp[7]==2
    assert cp[8][1][0]=="right" and cp[8][0][1][0]=="left"
    assert min(sum(p[2]) for p in pair(delta))==0
    # Incoherent baseline is always 2, regardless of phase.


def test_weight_and_order(pncs,holonomy):
    paths=pair(math.pi,(2,1))
    z,cp=run(pncs,holonomy,paths)
    rz,rcp=run(pncs,holonomy,list(reversed(paths)))
    assert abs(z)**2==pytest.approx(1)
    assert rz==pytest.approx(z)
    assert cp[8]!=rcp[8]


def test_gauge_and_composition(pncs,holonomy):
    paths=pair(math.pi/3)
    z,_=run(pncs,holonomy,paths)
    shifted=[(r,e,holonomy.open_gauge_shift(p,[.2,k,.9]),w)
             for k,(r,e,p,w) in enumerate(paths)]
    zz,_=run(pncs,holonomy,shifted)
    assert zz==pytest.approx(z*holonomy.semantic_u1_transport([.7]))
    assert abs(zz)**2==pytest.approx(abs(z)**2)
    assert holonomy.semantic_u1_transport([.2,.4])==pytest.approx(
        holonomy.semantic_u1_transport([.2])*holonomy.semantic_u1_transport([.4]))


def test_higher_action_path_changes_result(pncs,holonomy):
    low=[("left",["a-l","l-b"],[0,0],1)]
    z,_=run(pncs,holonomy,low)
    cancel,_=run(pncs,holonomy,pair(math.pi))
    reinforce,_=run(pncs,holonomy,pair(2*math.pi))
    assert abs(z)**2==1
    assert abs(cancel)**2<1e-24
    assert abs(reinforce)**2==pytest.approx(4)


def test_empty_zero_and_exact_integer(pncs,holonomy):
    z,cp=run(pncs,holonomy,[])
    assert z==0 and cp[7:]==[0,[]]
    r=fold(pncs,initial(),"zero",["edge"],(0,0))
    assert r["AMPLITUDE"]==[0,0] and r["CHECKPOINT"][7]==1
    n=10**100
    r=fold(pncs,initial(),"huge",["edge"],(n,-n))
    r=fold(pncs,r["CHECKPOINT"],"second",["edge2"],(-n+1,n+1))
    assert r["AMPLITUDE"]==[1,1]
    assert all(type(x) is int for x in r["AMPLITUDE"])


@pytest.mark.parametrize("slot",range(5))
def test_scope_mismatch_visible(pncs,slot):
    scope=SCOPE.copy()
    scope[slot]="different" if slot<4 else 2
    r=fold(pncs,initial(),"bad",["edge"],(1,0),scope)
    assert r["WITNESS"]==[j!=slot for j in range(5)]
    # Candidate only; not an admitted checkpoint.
