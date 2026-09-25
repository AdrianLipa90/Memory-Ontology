import random
import pytest

from algebra.prime_hilbert_collatz_association import (
    AssociationAlgebraError,
    CollatzLiftedState,
    accelerated_odd_collatz,
    accelerated_odd_collatz_inverse,
    all_dissociations,
    associate_codes,
    collatz_associate,
    collatz_associate_step,
    collatz_dissociate,
    collatz_dissociate_step,
    decode_word,
    deconcatenation_is_coassociative,
    dissociate_code,
    encode_word,
    hilbert_pack_channel,
    hilbert_shift_index,
    hilbert_unshift_index,
    hilbert_unpack_channel,
    prime_position_shift,
    primes_first,
)


def test_prime_word_roundtrip_and_order():
    w = (2, 1, 4, 3)
    code = encode_word(w)
    assert decode_word(code) == w
    assert encode_word((1, 2)) != encode_word((2, 1))


def test_prime_hilbert_concat_identity():
    u = (2, 3, 1)
    v = (4, 1)
    gu, gv = encode_word(u), encode_word(v)
    assert associate_codes(gu, gv) == encode_word(u + v)
    assert gu * prime_position_shift(gv, len(u)) == encode_word(u + v)


def test_association_is_exactly_associative():
    a = encode_word((2, 1))
    b = encode_word((4,))
    c = encode_word((3, 2, 2))
    assert associate_codes(associate_codes(a, b), c) == associate_codes(
        a, associate_codes(b, c)
    )


def test_dissociation_is_exact_inverse_of_association():
    u = encode_word((2, 1, 3))
    v = encode_word((4, 2))
    joined = associate_codes(u, v)
    left, right = dissociate_code(joined, 3)
    assert left == u
    assert right == v


def test_all_dissociations_cover_all_word_cuts():
    code = encode_word((1, 2, 3))
    cuts = all_dissociations(code)
    assert len(cuts) == 4
    assert [decode_word(a) for a, _ in cuts] == [(), (1,), (1, 2), (1, 2, 3)]
    assert [decode_word(b) for _, b in cuts] == [(1, 2, 3), (2, 3), (3,), ()]


def test_deconcatenation_coassociativity_witness():
    for word in [(1,), (2, 1), (1, 3, 2), (4, 1, 2, 3, 1)]:
        assert deconcatenation_is_coassociative(encode_word(word))


def test_hilbert_shift_has_exact_partial_inverse_on_image():
    for n in range(100):
        for k in range(10):
            shifted = hilbert_shift_index(n, k)
            assert hilbert_unshift_index(shifted, k) == n
    with pytest.raises(AssociationAlgebraError):
        hilbert_unshift_index(2, 3)


def test_hilbert_channel_pack_is_bijection_for_finite_branch_set():
    for arity in (2, 3, 7):
        seen = set()
        for channel in range(arity):
            for index in range(100):
                address = hilbert_pack_channel(channel, index, arity)
                assert hilbert_unpack_channel(address, arity) == (channel, index)
                seen.add(address)
        assert seen == set(range(arity * 100))


def test_accelerated_collatz_inverse_is_exact_on_generated_branch():
    for n in range(1, 500, 2):
        u, a = accelerated_odd_collatz(n)
        assert accelerated_odd_collatz_inverse(u, a) == n


def test_invalid_collatz_inverse_branch_fails_closed():
    with pytest.raises(AssociationAlgebraError):
        accelerated_odd_collatz_inverse(1, 1)


def test_lifted_collatz_step_is_reversible():
    for n in (1, 3, 5, 7, 9, 15, 27, 31, 97, 255):
        s = CollatzLiftedState(n)
        t = collatz_associate_step(s)
        assert collatz_dissociate_step(t) == s


def test_multistep_collatz_history_roundtrip():
    for seed in (1, 3, 5, 7, 9, 15, 27, 31, 97, 255, 871):
        forward = collatz_associate(seed, 25)
        back = collatz_dissociate(forward, 25)
        assert back == CollatzLiftedState(seed)
        assert len(forward.history) == 25


def test_collatz_history_code_is_exact_branch_word():
    s = CollatzLiftedState(27)
    expected = []
    for _ in range(12):
        _, a = accelerated_odd_collatz(s.value)
        expected.append(a)
        s = collatz_associate_step(s)
    assert s.history == tuple(expected)
    assert decode_word(s.history_code) == tuple(expected)


def test_random_finite_collatz_histories_roundtrip():
    rng = random.Random(20260925)
    for _ in range(300):
        seed = 2 * rng.randrange(1, 50000) + 1
        steps = rng.randrange(0, 30)
        forward = collatz_associate(seed, steps)
        back = collatz_dissociate(forward, steps)
        assert back == CollatzLiftedState(seed)


def test_prime_support_must_be_consecutive():
    with pytest.raises(AssociationAlgebraError):
        decode_word(10)


def test_first_primes_reference():
    assert primes_first(10) == (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
