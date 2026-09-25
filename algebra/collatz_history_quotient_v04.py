from __future__ import annotations

from dataclasses import dataclass

from .collatz_history_groupoid_v04 import (
    CollatzGroupoidError,
    CollatzPath,
    SignedBranch,
    apply_signed_branch,
    compose_paths,
    encode_signed_history,
    reduce_history,
)

SCHEMA = "COLLATZ_HISTORY_TO_BEHAVIOR_QUOTIENT_V0_4"


class CollatzHistoryCategoryError(ValueError):
    pass


@dataclass(frozen=True)
class HistoricalCollatzPath:
    """Raw validated path. No inverse-pair cancellation is performed."""

    start: int
    history: tuple[SignedBranch, ...] = ()

    def __post_init__(self) -> None:
        h = tuple(self.history)
        current = self.start
        try:
            for step in h:
                current = apply_signed_branch(current, step)
        except CollatzGroupoidError as exc:
            raise CollatzHistoryCategoryError(str(exc)) from exc
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
    def is_raw_identity(self) -> bool:
        return not self.history

    def reverse_traversal(self) -> "HistoricalCollatzPath":
        return HistoricalCollatzPath(
            self.end,
            tuple(step.inverse() for step in reversed(self.history)),
        )


def historical_identity(obj: int) -> HistoricalCollatzPath:
    return HistoricalCollatzPath(obj, ())


def compose_historical(
    first: HistoricalCollatzPath,
    second: HistoricalCollatzPath,
) -> HistoricalCollatzPath:
    if first.end != second.start:
        raise CollatzHistoryCategoryError(
            "historical path endpoints do not compose"
        )
    return HistoricalCollatzPath(
        first.start,
        first.history + second.history,
    )


def behavioral_quotient(path: HistoricalCollatzPath) -> CollatzPath:
    return CollatzPath(
        path.start,
        reduce_history(path.start, path.history),
    )


def quotient_functor_law(
    first: HistoricalCollatzPath,
    second: HistoricalCollatzPath,
) -> bool:
    if first.end != second.start:
        raise CollatzHistoryCategoryError(
            "historical path endpoints do not compose"
        )
    lhs = behavioral_quotient(
        compose_historical(first, second)
    )
    rhs = compose_paths(
        behavioral_quotient(first),
        behavioral_quotient(second),
    )
    return lhs == rhs


def same_behavior_different_history(
    a: HistoricalCollatzPath,
    b: HistoricalCollatzPath,
) -> bool:
    return (
        behavioral_quotient(a) == behavioral_quotient(b)
        and a.history != b.history
    )


def structure_classification() -> dict:
    return {
        "historical_layer":
            "CATEGORY_OF_RAW_VALIDATED_SIGNED_COLLATZ_PATHS",
        "behavioral_layer":
            "REDUCED_PATH_GROUPOID",
        "map":
            "QUOTIENT_FUNCTOR_BY_EXACT_ADJACENT_BACKTRACKING",
        "provenance_erased_by_quotient": True,
        "representation_category_interpretation": (
            "prime lineage belongs to historical layer; semantic "
            "invertibility belongs to behavioral quotient"
        ),
        "global_action_groupoid_claim": False,
        "collatz_convergence_claim": False,
    }
