from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

SCHEMA = "MEMORY_PRIME_HILBERT_COLLATZ_ASSOCIATION_V0_4"


class AssociationAlgebraError(ValueError):
    pass


def _positive_int(value: int, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise AssociationAlgebraError(f"{field} must be a positive integer")
    return value


def primes_first(count: int) -> tuple[int, ...]:
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise AssociationAlgebraError("count must be a non-negative integer")
    if count == 0:
        return ()
    out: list[int] = []
    n = 2
    while len(out) < count:
        prime = True
        limit = math.isqrt(n)
        for p in out:
            if p > limit:
                break
            if n % p == 0:
                prime = False
                break
        if prime:
            out.append(n)
        n += 1 if n == 2 else 2
    return tuple(out)


def encode_word(exponents: Iterable[int]) -> int:
    word = tuple(exponents)
    for e in word:
        _positive_int(e, "word exponent")
    code = 1
    for p, e in zip(primes_first(len(word)), word):
        code *= p**e
    return code


def decode_word(code: int) -> tuple[int, ...]:
    _positive_int(code, "prime word code")
    if code == 1:
        return ()
    remainder = code
    exponents: list[int] = []
    prime_index = 0
    while remainder > 1:
        p = primes_first(prime_index + 1)[-1]
        if remainder % p != 0:
            raise AssociationAlgebraError(
                "invalid prime word: non-consecutive prime support"
            )
        e = 0
        while remainder % p == 0:
            remainder //= p
            e += 1
        exponents.append(e)
        prime_index += 1
    return tuple(exponents)


def prime_position_shift(code: int, offset: int) -> int:
    _positive_int(code, "prime word code")
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise AssociationAlgebraError("offset must be a non-negative integer")
    word = decode_word(code)
    if not word:
        return 1
    primes = primes_first(offset + len(word))
    out = 1
    for j, e in enumerate(word):
        out *= primes[offset + j] ** e
    return out


def associate_codes(left_code: int, right_code: int) -> int:
    left = decode_word(left_code)
    right = decode_word(right_code)
    direct = encode_word(left + right)
    shifted_product = left_code * prime_position_shift(right_code, len(left))
    if direct != shifted_product:
        raise AssertionError("prime/Hilbert concatenation identity failed")
    return direct


def dissociate_code(code: int, cut: int) -> tuple[int, int]:
    word = decode_word(code)
    if isinstance(cut, bool) or not isinstance(cut, int) or not 0 <= cut <= len(word):
        raise AssociationAlgebraError("cut must lie in [0, word_length]")
    return encode_word(word[:cut]), encode_word(word[cut:])


def all_dissociations(code: int) -> tuple[tuple[int, int], ...]:
    word = decode_word(code)
    return tuple(dissociate_code(code, k) for k in range(len(word) + 1))


def hilbert_shift_index(index: int, offset: int) -> int:
    if isinstance(index, bool) or not isinstance(index, int) or index < 0:
        raise AssociationAlgebraError("index must be a non-negative integer")
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise AssociationAlgebraError("offset must be a non-negative integer")
    return index + offset


def hilbert_unshift_index(index: int, offset: int) -> int:
    if isinstance(index, bool) or not isinstance(index, int) or index < 0:
        raise AssociationAlgebraError("index must be a non-negative integer")
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise AssociationAlgebraError("offset must be a non-negative integer")
    if index < offset:
        raise AssociationAlgebraError("index is outside the shifted image")
    return index - offset


def hilbert_pack_channel(channel: int, index: int, arity: int) -> int:
    if isinstance(arity, bool) or not isinstance(arity, int) or arity < 1:
        raise AssociationAlgebraError("arity must be positive")
    if isinstance(channel, bool) or not isinstance(channel, int) or not 0 <= channel < arity:
        raise AssociationAlgebraError("channel outside [0, arity)")
    if isinstance(index, bool) or not isinstance(index, int) or index < 0:
        raise AssociationAlgebraError("index must be non-negative")
    return arity * index + channel


def hilbert_unpack_channel(address: int, arity: int) -> tuple[int, int]:
    if isinstance(arity, bool) or not isinstance(arity, int) or arity < 1:
        raise AssociationAlgebraError("arity must be positive")
    if isinstance(address, bool) or not isinstance(address, int) or address < 0:
        raise AssociationAlgebraError("address must be non-negative")
    index, channel = divmod(address, arity)
    return channel, index


def v2(n: int) -> int:
    _positive_int(n, "n")
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def accelerated_odd_collatz(n: int) -> tuple[int, int]:
    _positive_int(n, "n")
    if n % 2 == 0:
        raise AssociationAlgebraError("accelerated odd Collatz requires odd n")
    m = 3 * n + 1
    a = v2(m)
    return m // (2**a), a


def accelerated_odd_collatz_inverse(u: int, a: int) -> int:
    _positive_int(u, "u")
    _positive_int(a, "a")
    if u % 2 == 0:
        raise AssociationAlgebraError("accelerated odd Collatz target must be odd")
    numerator = (2**a) * u - 1
    if numerator % 3 != 0:
        raise AssociationAlgebraError("requested Collatz inverse branch is inadmissible")
    n = numerator // 3
    if n <= 0 or n % 2 == 0:
        raise AssociationAlgebraError("inverse branch does not yield a positive odd source")
    if accelerated_odd_collatz(n) != (u, a):
        raise AssociationAlgebraError("inverse branch fails exact forward validation")
    return n


@dataclass(frozen=True)
class CollatzLiftedState:
    value: int
    history: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        _positive_int(self.value, "value")
        if self.value % 2 == 0:
            raise AssociationAlgebraError("lifted Collatz state value must be odd")
        word = tuple(self.history)
        for a in word:
            _positive_int(a, "Collatz branch valuation")
        object.__setattr__(self, "history", word)

    @property
    def history_code(self) -> int:
        return encode_word(self.history)

    def to_dict(self) -> dict:
        return {
            "schema": SCHEMA,
            "value": self.value,
            "history_code": self.history_code,
            "history": list(self.history),
            "history_length": len(self.history),
            "history_representation": "POSITIONAL_PRIME_WORD",
            "runtime_history_representation": "RELATIONAL_WORD",
            "countable_allocation": "HILBERT_SHIFT",
            "physical_quantum_claim": False,
        }


def collatz_associate_step(state: CollatzLiftedState) -> CollatzLiftedState:
    u, a = accelerated_odd_collatz(state.value)
    return CollatzLiftedState(u, state.history + (a,))


def collatz_dissociate_step(state: CollatzLiftedState) -> CollatzLiftedState:
    if not state.history:
        raise AssociationAlgebraError("cannot dissociate empty Collatz history")
    a = state.history[-1]
    previous = accelerated_odd_collatz_inverse(state.value, a)
    return CollatzLiftedState(previous, state.history[:-1])


def collatz_associate(seed: int, steps: int) -> CollatzLiftedState:
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise AssociationAlgebraError("steps must be a non-negative integer")
    state = CollatzLiftedState(seed)
    for _ in range(steps):
        state = collatz_associate_step(state)
    return state


def collatz_dissociate(state: CollatzLiftedState, steps: int) -> CollatzLiftedState:
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise AssociationAlgebraError("steps must be a non-negative integer")
    out = state
    for _ in range(steps):
        out = collatz_dissociate_step(out)
    return out


def deconcatenation_is_coassociative(code: int) -> bool:
    """Finite witness for every ordered triple cut of one encoded word."""
    word = decode_word(code)
    n = len(word)
    for i in range(n + 1):
        for j in range(i, n + 1):
            a = encode_word(word[:i])
            b = encode_word(word[i:j])
            c = encode_word(word[j:])
            left = associate_codes(associate_codes(a, b), c)
            right = associate_codes(a, associate_codes(b, c))
            if left != code or right != code or left != right:
                return False
    return True


__all__ = [
    "SCHEMA",
    "AssociationAlgebraError",
    "primes_first",
    "encode_word",
    "decode_word",
    "prime_position_shift",
    "associate_codes",
    "dissociate_code",
    "all_dissociations",
    "hilbert_shift_index",
    "hilbert_unshift_index",
    "hilbert_pack_channel",
    "hilbert_unpack_channel",
    "v2",
    "accelerated_odd_collatz",
    "accelerated_odd_collatz_inverse",
    "CollatzLiftedState",
    "collatz_associate_step",
    "collatz_dissociate_step",
    "collatz_associate",
    "collatz_dissociate",
    "deconcatenation_is_coassociative",
]
