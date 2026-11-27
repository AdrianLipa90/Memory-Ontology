"""Source Kuramoto conformance and immutable native observation composition."""
import math
from copy import deepcopy

import pytest

from engines.rdss_relational_dynamics_v32 import (
    AdaptiveEdge, phase_step, phase_readout36, order_parameter
)
from test_pip_native_e2e import pncs, execute

PROGRAM = "PIP_THOUGHT_PHASE_OBSERVATION_V0_5.pnv"
SCOPE = ["pip", "thought", "two-cluster", 36]
N = 36

def initial(shift=0):
    return tuple([shift-math.pi/4]*18 + [shift+math.pi/4]*18)

def source_snapshots():
    base = AdaptiveEdge("left", "right", .5, 1.)
    learned = base.update("verified", "fixture", True, 0, 1, 1)
    failed = base.update("failed", "fixture", False, 0, 1, 1)
    return base, learned, failed

def simulate(edge, gain, steps, shift=0):
    k = gain*edge.phase_weight()
    matrix = tuple(tuple(k/18 if (i<18)!=(j<18) else 0.
                         for j in range(N)) for i in range(N))
    theta = initial(shift)
    for _ in range(steps):
        theta = phase_step(theta, (0.,)*N, matrix, (0.,)*N, 2/steps)
    return theta

def delta(theta):
    return theta[18]-theta[0]

def fs(theta):
    r = phase_readout36([0.]*N, theta)["relation"]
    return math.acos(math.sqrt(min(1., max(0., r))))

def oracle(k):
    return 2*math.atan(math.exp(-4*k))

@pytest.mark.parametrize("index", [0,1,2])
def test_closed_form_and_refinement(index):
    edge = source_snapshots()[index]
    k = edge.phase_weight()
    coarse = simulate(edge, 1, 100)
    fine = simulate(edge, 1, 400)
    err_c = abs(delta(coarse)-oracle(k))
    err_f = abs(delta(fine)-oracle(k))
    assert err_f < err_c/3
    assert err_f < .004
    assert sum(fine)/N == pytest.approx(0, abs=1e-13)
    assert fine[:18] == pytest.approx([fine[0]]*18)
    assert fine[18:] == pytest.approx([fine[18]]*18)
    assert fs(fine) == pytest.approx(delta(fine)/2, abs=1e-12)
    assert abs(order_parameter(fine))**2 == pytest.approx(
        math.cos(delta(fine)/2)**2)

def test_memory_intervention_failed_control_and_ablation():
    a,b,c = source_snapshots()
    assert a.accessibility == b.accessibility == c.accessibility == .5
    assert (a.conductance,b.conductance,c.conductance) == (1,2,1)
    assert a.history == () and b.history[0][0] == "verified"
    assert c.history[0][2] is False
    x,y,z = [simulate(e,1,400) for e in (a,b,c)]
    assert z == x
    assert fs(y) < fs(x)
    assert fs(x) == pytest.approx(math.atan(math.exp(-2)), abs=.002)
    assert fs(y) == pytest.approx(math.atan(math.exp(-4)), abs=.002)
    assert simulate(a,0,100) == simulate(b,0,100) == initial()
    shifted = simulate(b,1,400,shift=2.)
    assert shifted == pytest.approx([v+2 for v in y], abs=1e-12)
    assert fs(shifted) == pytest.approx(fs(y), abs=1e-12)

def observe(pncs, cp, after, ref, **override):
    keys = ("scope","memory_ref","phase","duration","count","ref")
    data = {"prior."+k:v for k,v in zip(keys,cp)}
    data.update({"observation.scope":cp[0], "observation.memory_ref":cp[1],
                 "observation.before":cp[2], "observation.after":after,
                 "observation.duration":.5, "observation.previous_ref":cp[5],
                 "observation.step_ref":ref})
    data.update(override)
    original = deepcopy(data)
    result = execute(pncs, PROGRAM, data).emitted
    assert data == original
    return result

def test_native_phase_lineage(pncs):
    edge = source_snapshots()[0]
    k = edge.phase_weight()
    matrix = tuple(tuple(k/18 if (i<18)!=(j<18) else 0.
                         for j in range(N)) for i in range(N))
    origin = list(initial())
    cp = [SCOPE,"M0",origin,0,2**63,"origin"]
    previous = origin
    entries = []
    for j in range(4):
        after = list(phase_step(previous,(0.,)*N,matrix,(0.,)*N,.5))
        r = observe(pncs,cp,after,"step-"+str(j))
        assert r["WITNESS"] == [True]*4
        entry = r["ENTRY"]
        assert entry[0] == cp[5]
        assert entry[4] == previous and entry[5] == after
        entries.append(entry)
        cp = r["CHECKPOINT"]
        previous = after
    assert cp[3:5] == [2,2**63+4]
    assert type(cp[4]) is int
    assert entries[0][4] == origin
    assert entries[-1][5] == cp[2]
    assert fs(cp[2]) < fs(origin)

@pytest.mark.parametrize("field,value,slot", [
    ("scope",["other"],0), ("memory_ref","wrong",1),
    ("before",[0.]*N,2), ("previous_ref","wrong",3)])
def test_native_observation_mismatch(pncs, field, value, slot):
    cp = [SCOPE,"M0",list(initial()),0,0,"origin"]
    r = observe(pncs,cp,list(initial()),"step",**{"observation."+field:value})
    assert r["WITNESS"] == [i!=slot for i in range(4)]
