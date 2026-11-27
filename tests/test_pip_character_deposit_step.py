"""Step 1 conformance: the original PNCS interpreter, no new engine."""
from copy import deepcopy
from fractions import Fraction

import pytest
from test_pip_native_e2e import pncs, execute, step

PROGRAM = "PIP_CHARACTER_DEPOSIT_STEP_V0_1.pnv"


def initial(owner="Pip", a=0, b=0, previous=None):
    # Declared immutable test checkpoint; not an additional storage engine.
    return [owner, "same-question", ["left", "right"], a, b, a+b, previous]


def sources(checkpoint, occurrence, choice):
    owner, domain, labels, a, b, total, previous = checkpoint
    return {
        "deposit.owner": owner, "deposit.query_domain": domain,
        "deposit.candidate_labels": labels, "deposit.label_a": labels[0],
        "deposit.label_b": labels[1], "deposit.count_a": a,
        "deposit.count_b": b, "deposit.count": total,
        "deposit.previous_observation_ref": previous,
        "observation.ref": [owner, occurrence["INDEX"]],
        "observation.owner": owner, "observation.query_domain": domain,
        "observation.candidate_labels": labels, "observation.choice": choice,
        "observation.vote_a": int(choice == labels[0]),
        "observation.vote_b": int(choice == labels[1]),
        "observation.hotel_occurrence": occurrence["NOW"],
    }


def observe(pncs, cp, occurrence, choice):
    s = sources(cp, occurrence, choice)
    original = deepcopy(s)
    result = execute(pncs, PROGRAM, s).emitted
    assert result["WITNESS"] == [True]*9
    assert s == original
    assert result["LINEAGE"] == [cp[-1], s["observation.ref"], occurrence["NOW"]]
    assert result["CHECKPOINT"][-1] == s["observation.ref"]
    return result


def run(pncs, choices):
    hotel = execute(pncs, "PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv",
                    {"now.object":"selected choice"}).emitted
    cp = initial()
    lineage = []
    for n, choice in enumerate(choices):
        if n:
            hotel = step(pncs, hotel, "selected choice")
        before = deepcopy(hotel)
        result = observe(pncs, cp, hotel, choice)
        cp = result["CHECKPOINT"]
        lineage.append((result["LINEAGE"], choice))
        assert hotel == before
        assert cp[3:6] == [choices[:n+1].count("left"),
                           choices[:n+1].count("right"), n+1]
        assert sum(Fraction(*x) for x in result["CHARACTER"]) == 1
    return result, lineage


def test_character_is_not_history(pncs):
    a, la = run(pncs, ["left","left","right","right"])
    b, lb = run(pncs, ["right","left","right","left"])
    c, lc = run(pncs, ["left","left","left","right"])
    assert a["CHARACTER"] == b["CHARACTER"] == [[2,4],[2,4]]
    assert la != lb  # equal distribution, different ordered choice observations
    assert c["CHARACTER"] == [[3,4],[1,4]]
    assert la != lc


@pytest.mark.parametrize("n",[2**53,2**63,10**100])
def test_exact_counts_and_occurrence(pncs,n):
    # Seeded count/index boundary, not a reconstruction of n observations.
    cp = initial(a=n,b=2,previous=["Pip",n+1])
    hotel = {"NOW":[None,n+2,n+2,(-1)**(n%2),2*(n+2),"seed"],
             "INDEX":n+2,"WINDING":n+2,"SIGN":(-1)**(n%2),"THETA":2*(n+2)}
    r=observe(pncs,cp,hotel,"left")
    assert r["CHARACTER"] == [[n+1,n+3],[2,n+3]]
    assert all(type(x) is int for pair in r["CHARACTER"] for x in pair)
    assert r["LINEAGE"][1][1] == n+2


@pytest.mark.parametrize("key,value,slot",[
    ("deposit.label_a","right",0),
    ("deposit.label_b","left",1),
    ("observation.owner","Ciel",2),
    ("observation.query_domain","another-question",3),
    ("observation.candidate_labels",["right","left"],4),
    ("deposit.previous_observation_ref",["Pip",0],5),
    ("observation.choice","right",6),
    ("observation.vote_b",1,6),
    ("deposit.count",9,7),
])
def test_mismatch_remains_visible(pncs,key,value,slot):
    hotel=execute(pncs,"PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv",
                  {"now.object":"selected choice"}).emitted
    cp=initial()
    s=sources(cp,hotel,"left")
    s[key]=value
    r=execute(pncs,PROGRAM,s).emitted
    assert r["WITNESS"][slot] is False
    assert "CHECKPOINT" in r
    assert r["LINEAGE"][-1]==hotel["NOW"]
