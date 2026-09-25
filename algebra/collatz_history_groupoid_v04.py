from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .prime_hilbert_collatz_association import (
    AssociationAlgebraError,
    accelerated_odd_collatz,
    accelerated_odd_collatz_inverse,
    decode_word,
    dissociate_code,
    encode_word,
)

SCHEMA = "COLLATZ_RETAINED_HISTORY_PATH_GROUPOID_V0_4"


class CollatzGroupoidError(ValueError):
    pass


def _odd_positive(n: int, field: str) -> int:
    if isinstance(n, bool) or not isinstance(n, int) or n < 1 or n % 2 == 0:
        raise CollatzGroupoidError(f"{field} must be a positive odd integer")
    return n


def _branch(a: int) -> int:
    if isinstance(a, bool) or not isinstance(a, int) or a < 1:
        raise CollatzGroupoidError("branch valuation must be a positive integer")
    return a


@dataclass(frozen=True)
class SignedBranch:
    valuation: int
    direction: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "valuation", _branch(self.valuation))
        if self.direction not in (-1, 1):
            raise CollatzGroupoidError("direction must be +1 or -1")

    @property
    def token(self) -> int:
        return 2 * self.valuation - 1 if self.direction == 1 else 2 * self.valuation

    @classmethod
    def from_token(cls, token: int) -> "SignedBranch":
        if isinstance(token, bool) or not isinstance(token, int) or token < 1:
            raise CollatzGroupoidError("signed branch token must be positive")
        if token % 2:
            return cls((token + 1) // 2, 1)
        return cls(token // 2, -1)

    def inverse(self) -> "SignedBranch":
        return SignedBranch(self.valuation, -self.direction)


def encode_signed_history(history: Iterable[SignedBranch]) -> int:
    return encode_word(tuple(step.token for step in history))


def decode_signed_history(code: int) -> tuple[SignedBranch, ...]:
    return tuple(SignedBranch.from_token(t) for t in decode_word(code))


def apply_signed_branch(value: int, step: SignedBranch) -> int:
    n = _odd_positive(value, "value")
    if step.direction == 1:
        u, actual = accelerated_odd_collatz(n)
        if actual != step.valuation:
            raise CollatzGroupoidError(
                f"forward branch mismatch: expected a={step.valuation}, got a={actual}"
            )
        return u
    try:
        return accelerated_odd_collatz_inverse(n, step.valuation)
    except AssociationAlgebraError as exc:
        raise CollatzGroupoidError(str(exc)) from exc


def reduce_history(start: int, history: Iterable[SignedBranch]) -> tuple[SignedBranch, ...]:
    current = _odd_positive(start, "start")
    stack: list[tuple[int, SignedBranch, int]] = []
    for step in tuple(history):
        if not isinstance(step, SignedBranch):
            raise CollatzGroupoidError("history must contain SignedBranch")
        target = apply_signed_branch(current, step)
        if stack:
            prev_source, prev_step, prev_target = stack[-1]
            if (
                prev_target == current
                and prev_source == target
                and prev_step.valuation == step.valuation
                and prev_step.direction == -step.direction
            ):
                stack.pop()
                current = target
                continue
        stack.append((current, step, target))
        current = target
    return tuple(item[1] for item in stack)


@dataclass(frozen=True)
class CollatzPath:
    start: int
    history: tuple[SignedBranch, ...] = ()

    def __post_init__(self) -> None:
        _odd_positive(self.start, "start")
        h = tuple(self.history)
        current = self.start
        for step in h:
            if not isinstance(step, SignedBranch):
                raise CollatzGroupoidError("history must contain SignedBranch")
            current = apply_signed_branch(current, step)
        object.__setattr__(self, "history", h)

    @property
    def end(self) -> int:
        current = self.start
        for step in self.history:
            current = apply_signed_branch(current, step)
        return current

    @property
    def prime_history_code(self) -> int:
        return encode_signed_history(self.history)

    @property
    def is_identity(self) -> bool:
        return not self.history and self.end == self.start

    def inverse(self) -> "CollatzPath":
        return CollatzPath(
            self.end,
            tuple(step.inverse() for step in reversed(self.history)),
        )

    def reduced(self) -> "CollatzPath":
        return CollatzPath(self.start, reduce_history(self.start, self.history))

    def to_dict(self) -> dict:
        return {
            "schema": SCHEMA,
            "start": self.start,
            "end": self.end,
            "signed_history": [
                {"valuation": x.valuation, "direction": x.direction, "token": x.token}
                for x in self.history
            ],
            "prime_history_code": self.prime_history_code,
            "history_length": len(self.history),
            "physical_quantum_claim": False,
            "collatz_convergence_claim": False,
        }


def identity_path(obj: int) -> CollatzPath:
    return CollatzPath(_odd_positive(obj, "object"), ())


def forward_path(seed: int, steps: int) -> CollatzPath:
    start = _odd_positive(seed, "seed")
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise CollatzGroupoidError("steps must be a non-negative integer")
    current = start
    history: list[SignedBranch] = []
    for _ in range(steps):
        target, a = accelerated_odd_collatz(current)
        history.append(SignedBranch(a, 1))
        current = target
    return CollatzPath(start, tuple(history))


def compose_paths(first: CollatzPath, second: CollatzPath) -> CollatzPath:
    if first.end != second.start:
        raise CollatzGroupoidError("path endpoints do not compose")
    raw = first.history + second.history
    return CollatzPath(first.start, reduce_history(first.start, raw))


def dissociate_path(path: CollatzPath, cut: int) -> tuple[CollatzPath, CollatzPath]:
    if isinstance(cut, bool) or not isinstance(cut, int) or not 0 <= cut <= len(path.history):
        raise CollatzGroupoidError("cut must lie in [0, history_length]")
    left_code, right_code = dissociate_code(path.prime_history_code, cut)
    left_history = decode_signed_history(left_code)
    right_history = decode_signed_history(right_code)
    left = CollatzPath(path.start, left_history)
    right = CollatzPath(left.end, right_history)
    if compose_paths(left, right) != path.reduced():
        raise AssertionError("prime dissociation does not reconstruct path")
    return left, right


def inverse_laws_hold(path: CollatzPath) -> bool:
    p = path.reduced()
    inv = p.inverse()
    return (
        compose_paths(p, inv) == identity_path(p.start)
        and compose_paths(inv, p) == identity_path(p.end)
    )


def associativity_holds(a: CollatzPath, b: CollatzPath, c: CollatzPath) -> bool:
    if a.end != b.start or b.end != c.start:
        raise CollatzGroupoidError("paths are not a composable triple")
    left = compose_paths(compose_paths(a, b), c)
    right = compose_paths(a, compose_paths(b, c))
    return left == right


def structure_classification() -> dict:
    return {
        "global_representation_category": "PARTIAL_TYPED_CATEGORY",
        "retained_history_collatz_sector": "PATH_GROUPOID_ON_VALID_FINITE_SIGNED_COLLATZ_PATHS",
        "action_groupoid": False,
        "reason_not_action_groupoid": (
            "no single globally defined group action is established; inverses are "
            "branch/state dependent partial path inverses"
        ),
        "maximal_core_claim": False,
        "relation_to_core": (
            "certified subgroupoid candidate inside the invertible core after "
            "objects/sectors are restricted to valid path domains/images"
        ),
        "lossy_projections_included": False,
    }
