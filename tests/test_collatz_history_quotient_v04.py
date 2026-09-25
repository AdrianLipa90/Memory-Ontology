import random

from algebra.collatz_history_groupoid_v04 import (
    SignedBranch,
    forward_path,
    identity_path,
)
from algebra.collatz_history_quotient_v04 import (
    HistoricalCollatzPath,
    behavioral_quotient,
    compose_historical,
    historical_identity,
    quotient_functor_law,
    same_behavior_different_history,
    structure_classification,
)
from algebra.prime_hilbert_collatz_association import decode_word


def hist_from_forward(seed, steps):
    p = forward_path(seed, steps)
    return HistoricalCollatzPath(p.start, p.history)


def test_raw_forward_then_reverse_retains_history():
    p = hist_from_forward(27, 20)
    loop = compose_historical(p, p.reverse_traversal())
    assert loop.start == loop.end == 27
    assert len(loop.history) == 40
    assert loop.prime_history_code != 1
    assert loop.is_raw_identity is False


def test_behavioral_quotient_of_roundtrip_is_identity():
    p = hist_from_forward(27, 20)
    loop = compose_historical(p, p.reverse_traversal())
    assert behavioral_quotient(loop) == identity_path(27)


def test_history_identity_and_behavior_identity_are_distinct():
    raw_id = historical_identity(27)
    p = hist_from_forward(27, 10)
    loop = compose_historical(p, p.reverse_traversal())
    assert loop != raw_id
    assert same_behavior_different_history(loop, raw_id)


def test_historical_composition_is_associative_without_erasure():
    p = hist_from_forward(27, 5)
    q = hist_from_forward(p.end, 7)
    r = hist_from_forward(q.end, 9)
    left = compose_historical(compose_historical(p, q), r)
    right = compose_historical(p, compose_historical(q, r))
    assert left == right
    assert len(left.history) == 21


def test_behavioral_quotient_respects_composition():
    p = hist_from_forward(27, 8)
    q = hist_from_forward(p.end, 8)
    assert quotient_functor_law(p, q)
    assert quotient_functor_law(p, p.reverse_traversal())


def test_prime_history_roundtrip_stays_raw():
    p = hist_from_forward(871, 25)
    restored = HistoricalCollatzPath(
        p.start,
        tuple(
            SignedBranch.from_token(t)
            for t in decode_word(p.prime_history_code)
        ),
    )
    assert restored == p


def test_random_quotient_functor_law():
    rng = random.Random(20260925)
    for _ in range(1000):
        seed = 2 * rng.randrange(1, 100000) + 1
        p = hist_from_forward(seed, rng.randrange(0, 20))
        q = hist_from_forward(p.end, rng.randrange(0, 20))
        assert quotient_functor_law(p, q)


def test_classification_keeps_provenance_separate():
    c = structure_classification()
    assert c["historical_layer"].startswith("CATEGORY")
    assert c["behavioral_layer"] == "REDUCED_PATH_GROUPOID"
    assert c["provenance_erased_by_quotient"] is True
    assert c["global_action_groupoid_claim"] is False
