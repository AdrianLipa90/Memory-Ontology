import random
import pytest

from algebra.collatz_history_groupoid_v04 import (
    CollatzGroupoidError,
    CollatzPath,
    SignedBranch,
    associativity_holds,
    compose_paths,
    decode_signed_history,
    dissociate_path,
    encode_signed_history,
    forward_path,
    identity_path,
    inverse_laws_hold,
    reduce_history,
    structure_classification,
)


def test_signed_branch_token_roundtrip():
    for a in range(1, 30):
        for d in (-1, 1):
            s=SignedBranch(a,d)
            assert SignedBranch.from_token(s.token)==s


def test_prime_signed_history_roundtrip_preserves_order_and_orientation():
    h=(SignedBranch(2,1),SignedBranch(1,-1),SignedBranch(4,1),SignedBranch(3,-1))
    assert decode_signed_history(encode_signed_history(h))==h


def test_forward_path_inverse_laws():
    for seed in (1,3,5,7,9,15,27,31,97,255,871):
        p=forward_path(seed,25)
        assert inverse_laws_hold(p)


def test_forward_then_inverse_reduces_to_identity():
    p=forward_path(27,40)
    assert compose_paths(p,p.inverse())==identity_path(27)


def test_inverse_then_forward_reduces_to_identity_at_target():
    p=forward_path(27,40)
    assert compose_paths(p.inverse(),p)==identity_path(p.end)


def test_dissociation_recovers_segments_and_recomposes():
    p=forward_path(27,20)
    for cut in range(21):
        a,b=dissociate_path(p,cut)
        assert compose_paths(a,b)==p
        assert a.start==p.start
        assert b.end==p.end


def test_associativity_on_three_forward_segments():
    p=forward_path(27,30)
    a,b=dissociate_path(p,10)
    b1,c=dissociate_path(b,10)
    assert associativity_holds(a,b1,c)


def test_associativity_survives_inverse_cancellation():
    p=forward_path(27,10)
    q=forward_path(p.end,10)
    r=q.inverse()
    assert associativity_holds(p,q,r)
    assert compose_paths(compose_paths(p,q),r)==p


def test_random_finite_path_groupoid_laws():
    rng=random.Random(20260925)
    for _ in range(500):
        seed=2*rng.randrange(1,50000)+1
        n1=rng.randrange(0,20)
        n2=rng.randrange(0,20)
        n3=rng.randrange(0,20)
        a=forward_path(seed,n1)
        b=forward_path(a.end,n2)
        c=forward_path(b.end,n3)
        assert associativity_holds(a,b,c)
        assert inverse_laws_hold(a)
        assert inverse_laws_hold(b)
        assert inverse_laws_hold(c)


def test_wrong_forward_branch_is_rejected():
    p=forward_path(27,1)
    actual=p.history[0].valuation
    with pytest.raises(CollatzGroupoidError):
        CollatzPath(27,(SignedBranch(actual+1,1),))


def test_inverse_branch_is_state_dependent_not_valuation_only():
    p=forward_path(27,1)
    inv=p.inverse()
    other=1 if p.end!=1 else 3
    with pytest.raises(CollatzGroupoidError):
        CollatzPath(other,inv.history)


def test_noncomposable_paths_fail_closed():
    a=forward_path(27,2)
    b=forward_path(31,2)
    if a.end==b.start:
        b=forward_path(33,2)
    with pytest.raises(CollatzGroupoidError):
        compose_paths(a,b)


def test_reduction_does_not_cancel_same_valuation_without_inverse_direction():
    p=forward_path(1,2)
    assert len(p.history)==2
    assert reduce_history(p.start,p.history)==p.history


def test_structure_classification_is_bounded():
    c=structure_classification()
    assert c["retained_history_collatz_sector"].startswith("PATH_GROUPOID")
    assert c["action_groupoid"] is False
    assert c["maximal_core_claim"] is False
    assert c["lossy_projections_included"] is False
