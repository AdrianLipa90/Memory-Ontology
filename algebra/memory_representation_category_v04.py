from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Iterable

from .prime_hilbert_collatz_association import (
    associate_codes,
    decode_word,
    dissociate_code,
    encode_word,
)

SCHEMA = "MEMORY_REPRESENTATION_CATEGORY_V0_4"

ROLE_CODE = {
    "COMPILER": 1,
    "EMBEDDING": 2,
    "PROJECTION": 3,
    "RECONSTRUCTION": 4,
    "OBSERVABLE": 5,
    "DYNAMIC": 6,
}


class RepresentationCategoryV4Error(ValueError):
    pass


def _error_fraction(value) -> Fraction:
    if isinstance(value, bool):
        raise RepresentationCategoryV4Error("error bound cannot be boolean")
    if isinstance(value, Fraction):
        q = value
    elif isinstance(value, int):
        q = Fraction(value, 1)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise RepresentationCategoryV4Error("error_bound must be finite")
        q = Fraction(str(value))
    elif isinstance(value, str):
        try:
            q = Fraction(value)
        except Exception as exc:
            raise RepresentationCategoryV4Error("invalid rational error bound") from exc
    else:
        raise RepresentationCategoryV4Error("unsupported error bound type")
    if q < 0:
        raise RepresentationCategoryV4Error("error_bound must be non-negative")
    return q


def _nonempty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RepresentationCategoryV4Error(f"{field} must be non-empty")
    return value


@dataclass(frozen=True)
class MetricCompositionWitness:
    witness_id: str
    distance: str
    triangle_bound_verified: bool

    def __post_init__(self) -> None:
        _nonempty(self.witness_id, "metric witness_id")
        _nonempty(self.distance, "metric distance")
        if self.triangle_bound_verified is not True:
            raise RepresentationCategoryV4Error(
                "metric witness must explicitly verify a triangle/composition bound"
            )


@dataclass(frozen=True)
class SectorCompatibilityWitness:
    witness_id: str
    output_sector: str
    input_sector: str
    relation: str
    admitted: bool

    def __post_init__(self) -> None:
        _nonempty(self.witness_id, "sector witness_id")
        _nonempty(self.output_sector, "output_sector")
        _nonempty(self.input_sector, "input_sector")
        _nonempty(self.relation, "sector relation")
        if self.admitted is not True:
            raise RepresentationCategoryV4Error(
                "sector witness must explicitly admit compatibility"
            )


@dataclass(frozen=True)
class RepresentationObjectV4:
    object_id: str
    memory_id: str
    family: str
    invariant_commitment: str
    provenance_commitment: str
    sector: str = "GENERAL"

    def __post_init__(self) -> None:
        for field in (
            "object_id",
            "memory_id",
            "family",
            "invariant_commitment",
            "provenance_commitment",
            "sector",
        ):
            _nonempty(getattr(self, field), field)


@dataclass(frozen=True)
class TypedMorphismV4:
    morphism_id: str
    source_id: str
    target_id: str
    observable: str
    distance: str
    error_bound: float
    horizon: int
    source_sector: str
    target_sector: str
    lineage: tuple[int, ...] = ()
    invariant_preserved: bool = True
    provenance_preserved: bool = True
    invertible_on_declared_image: bool = False
    total_on_declared_domain: bool = True
    metric_witness_ids: tuple[str, ...] = ()
    sector_witness_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field in (
            "morphism_id",
            "source_id",
            "target_id",
            "observable",
            "distance",
            "source_sector",
            "target_sector",
        ):
            _nonempty(getattr(self, field), field)
        object.__setattr__(self, "error_bound", _error_fraction(self.error_bound))
        if isinstance(self.horizon, bool) or not isinstance(self.horizon, int) or self.horizon < 1:
            raise RepresentationCategoryV4Error("horizon must be positive")
        line = tuple(self.lineage)
        if any(isinstance(x, bool) or not isinstance(x, int) or x < 1 for x in line):
            raise RepresentationCategoryV4Error("lineage codes must be positive integers")
        object.__setattr__(self, "lineage", line)

    @classmethod
    def generator(
        cls,
        *,
        morphism_id: str,
        source_id: str,
        target_id: str,
        role: str,
        observable: str,
        distance: str,
        error_bound: float,
        horizon: int,
        source_sector: str,
        target_sector: str,
        invariant_preserved: bool = True,
        provenance_preserved: bool = True,
        invertible_on_declared_image: bool = False,
        total_on_declared_domain: bool = True,
    ) -> "TypedMorphismV4":
        role_u = str(role).upper()
        if role_u == "IDENTITY":
            lineage = ()
        else:
            if role_u not in ROLE_CODE:
                raise RepresentationCategoryV4Error(f"unsupported role {role_u}")
            lineage = (ROLE_CODE[role_u],)
        return cls(
            morphism_id=morphism_id,
            source_id=source_id,
            target_id=target_id,
            observable=observable,
            distance=distance,
            error_bound=error_bound,
            horizon=horizon,
            source_sector=source_sector,
            target_sector=target_sector,
            lineage=lineage,
            invariant_preserved=invariant_preserved,
            provenance_preserved=provenance_preserved,
            invertible_on_declared_image=invertible_on_declared_image,
            total_on_declared_domain=total_on_declared_domain,
        )

    @property
    def history_code(self) -> int:
        return encode_word(self.lineage)

    def admitted_error(self, epsilon) -> bool:
        try:
            e = _error_fraction(epsilon)
        except RepresentationCategoryV4Error:
            return False
        return self.error_bound <= e

    def canonical_signature(self) -> dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "observable": self.observable,
            "distance": self.distance,
            "error_bound": {
                "numerator": self.error_bound.numerator,
                "denominator": self.error_bound.denominator,
            },
            "horizon": self.horizon,
            "source_sector": self.source_sector,
            "target_sector": self.target_sector,
            "lineage": list(self.lineage),
            "history_code": self.history_code,
            "invariant_preserved": self.invariant_preserved,
            "provenance_preserved": self.provenance_preserved,
            "invertible_on_declared_image": self.invertible_on_declared_image,
            "total_on_declared_domain": self.total_on_declared_domain,
            "metric_witness_ids": list(self.metric_witness_ids),
            "sector_witness_ids": list(self.sector_witness_ids),
        }


def identity_for(obj: RepresentationObjectV4) -> TypedMorphismV4:
    return TypedMorphismV4.generator(
        morphism_id=f"id:{obj.object_id}",
        source_id=obj.object_id,
        target_id=obj.object_id,
        role="IDENTITY",
        observable="IDENTITY",
        distance="EXACT",
        error_bound=0.0,
        horizon=2**31 - 1,
        source_sector=obj.sector,
        target_sector=obj.sector,
        invertible_on_declared_image=True,
    )


def _copy_with_id(m: TypedMorphismV4, morphism_id: str) -> TypedMorphismV4:
    return TypedMorphismV4(
        morphism_id=morphism_id,
        source_id=m.source_id,
        target_id=m.target_id,
        observable=m.observable,
        distance=m.distance,
        error_bound=m.error_bound,
        horizon=m.horizon,
        source_sector=m.source_sector,
        target_sector=m.target_sector,
        lineage=m.lineage,
        invariant_preserved=m.invariant_preserved,
        provenance_preserved=m.provenance_preserved,
        invertible_on_declared_image=m.invertible_on_declared_image,
        total_on_declared_domain=m.total_on_declared_domain,
        metric_witness_ids=m.metric_witness_ids,
        sector_witness_ids=m.sector_witness_ids,
    )


def compose_v4(
    first: TypedMorphismV4,
    second: TypedMorphismV4,
    *,
    composed_id: str,
    metric_witness: MetricCompositionWitness | None = None,
    sector_witness: SectorCompatibilityWitness | None = None,
) -> TypedMorphismV4:
    """Return second o first with explicit metric and sector authority."""
    if first.target_id != second.source_id:
        raise RepresentationCategoryV4Error("morphism endpoints do not compose")

    if not first.lineage and first.source_id == first.target_id:
        if first.target_sector != second.source_sector:
            raise RepresentationCategoryV4Error("identity sector does not match next source sector")
        return _copy_with_id(second, composed_id)
    if not second.lineage and second.source_id == second.target_id:
        if first.target_sector != second.source_sector:
            raise RepresentationCategoryV4Error("previous target sector does not match identity sector")
        return _copy_with_id(first, composed_id)

    if first.observable != second.observable or first.distance != second.distance:
        raise RepresentationCategoryV4Error("behavioral contracts do not compose")

    metric_ids = first.metric_witness_ids + second.metric_witness_ids
    if metric_witness is None:
        raise RepresentationCategoryV4Error(
            "non-identity error composition requires explicit metric witness"
        )
    if metric_witness.distance != first.distance:
        raise RepresentationCategoryV4Error("metric witness distance mismatch")
    metric_ids = metric_ids + (metric_witness.witness_id,)

    sector_ids = first.sector_witness_ids + second.sector_witness_ids
    if first.target_sector != second.source_sector:
        if sector_witness is None:
            raise RepresentationCategoryV4Error(
                "partial morphism sectors do not compose without explicit witness"
            )
        if (
            sector_witness.output_sector != first.target_sector
            or sector_witness.input_sector != second.source_sector
        ):
            raise RepresentationCategoryV4Error("sector witness endpoints mismatch")
        sector_ids = sector_ids + (sector_witness.witness_id,)
    elif sector_witness is not None:
        if (
            sector_witness.output_sector != first.target_sector
            or sector_witness.input_sector != second.source_sector
        ):
            raise RepresentationCategoryV4Error("sector witness endpoints mismatch")
        sector_ids = sector_ids + (sector_witness.witness_id,)

    left_code = first.history_code
    right_code = second.history_code
    combined_code = associate_codes(left_code, right_code)
    lineage = first.lineage + second.lineage
    if encode_word(lineage) != combined_code:
        raise AssertionError("prime/Hilbert lineage association failed")

    return TypedMorphismV4(
        morphism_id=composed_id,
        source_id=first.source_id,
        target_id=second.target_id,
        observable=first.observable,
        distance=first.distance,
        error_bound=first.error_bound + second.error_bound,
        horizon=min(first.horizon, second.horizon),
        source_sector=first.source_sector,
        target_sector=second.target_sector,
        lineage=lineage,
        invariant_preserved=first.invariant_preserved and second.invariant_preserved,
        provenance_preserved=first.provenance_preserved and second.provenance_preserved,
        invertible_on_declared_image=(
            first.invertible_on_declared_image and second.invertible_on_declared_image
        ),
        total_on_declared_domain=(
            first.total_on_declared_domain and second.total_on_declared_domain
        ),
        metric_witness_ids=metric_ids,
        sector_witness_ids=sector_ids,
    )


def dissociate_lineage(morphism: TypedMorphismV4, cut: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    left_code, right_code = dissociate_code(morphism.history_code, cut)
    return decode_word(left_code), decode_word(right_code)


class MemoryRepresentationCategoryV4:
    def __init__(self, objects: Iterable[RepresentationObjectV4] = ()) -> None:
        self._objects: dict[str, RepresentationObjectV4] = {}
        self._morphisms: dict[str, TypedMorphismV4] = {}
        for obj in objects:
            self.add_object(obj)

    def add_object(self, obj: RepresentationObjectV4) -> None:
        if obj.object_id in self._objects:
            raise RepresentationCategoryV4Error(f"duplicate object {obj.object_id}")
        self._objects[obj.object_id] = obj
        ident = identity_for(obj)
        self._morphisms[ident.morphism_id] = ident

    def object(self, object_id: str) -> RepresentationObjectV4:
        try:
            return self._objects[object_id]
        except KeyError as exc:
            raise RepresentationCategoryV4Error(f"unknown object {object_id}") from exc

    def add_morphism(self, morphism: TypedMorphismV4) -> None:
        if morphism.morphism_id in self._morphisms:
            raise RepresentationCategoryV4Error(f"duplicate morphism {morphism.morphism_id}")
        src = self.object(morphism.source_id)
        dst = self.object(morphism.target_id)
        if src.memory_id != dst.memory_id:
            raise RepresentationCategoryV4Error("morphism cannot silently change memory identity")
        self._morphisms[morphism.morphism_id] = morphism

    def morphism(self, morphism_id: str) -> TypedMorphismV4:
        try:
            return self._morphisms[morphism_id]
        except KeyError as exc:
            raise RepresentationCategoryV4Error(f"unknown morphism {morphism_id}") from exc
