from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

MORPHISM_ROLES = {
    "IDENTITY",
    "COMPILER",
    "EMBEDDING",
    "PROJECTION",
    "RECONSTRUCTION",
    "OBSERVABLE",
}


class MemoryRepresentationCategoryError(ValueError):
    pass


def _nonempty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise MemoryRepresentationCategoryError(f"{field} must be non-empty")
    return value


@dataclass(frozen=True)
class BehaviorContract:
    epsilon: float
    horizon: int
    observable: str
    distance: str = "declared_output_distance"

    def __post_init__(self) -> None:
        e = float(self.epsilon)
        if not math.isfinite(e) or e < 0:
            raise MemoryRepresentationCategoryError(
                "epsilon must be finite and non-negative"
            )
        object.__setattr__(self, "epsilon", e)
        if (
            isinstance(self.horizon, bool)
            or not isinstance(self.horizon, int)
            or self.horizon < 1
        ):
            raise MemoryRepresentationCategoryError(
                "horizon must be a positive integer"
            )
        _nonempty(self.observable, "observable")
        _nonempty(self.distance, "distance")


@dataclass(frozen=True)
class RepresentationObject:
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
class PartialMorphism:
    morphism_id: str
    source_id: str
    target_id: str
    role: str
    observable: str
    distance: str
    error_bound: float
    horizon: int
    domain_sector: str = "GENERAL"
    invariant_preserved: bool = True
    provenance_preserved: bool = True
    invertible: bool = False
    total_on_declared_domain: bool = True

    def __post_init__(self) -> None:
        for field in (
            "morphism_id",
            "source_id",
            "target_id",
            "observable",
            "distance",
            "domain_sector",
        ):
            _nonempty(getattr(self, field), field)
        role = str(self.role).upper()
        if role not in MORPHISM_ROLES:
            raise MemoryRepresentationCategoryError(
                f"unsupported morphism role {role}"
            )
        object.__setattr__(self, "role", role)
        err = float(self.error_bound)
        if not math.isfinite(err) or err < 0:
            raise MemoryRepresentationCategoryError(
                "error_bound must be finite and non-negative"
            )
        object.__setattr__(self, "error_bound", err)
        if (
            isinstance(self.horizon, bool)
            or not isinstance(self.horizon, int)
            or self.horizon < 1
        ):
            raise MemoryRepresentationCategoryError(
                "horizon must be a positive integer"
            )

    def admitted_by(self, contract: BehaviorContract) -> bool:
        return (
            self.observable == contract.observable
            and self.distance == contract.distance
            and self.horizon >= contract.horizon
            and self.error_bound <= contract.epsilon
            and self.invariant_preserved
            and self.provenance_preserved
        )


class MemoryRepresentationCategory:
    """Finite typed category-like registry for partial representation maps.

    Partiality is explicit in domain-sector metadata. This object does not claim
    that every arrow is invertible or that every pair of representations is
    connected.
    """

    def __init__(
        self, objects: Iterable[RepresentationObject] = ()
    ) -> None:
        self._objects: dict[str, RepresentationObject] = {}
        self._morphisms: dict[str, PartialMorphism] = {}
        for obj in objects:
            self.add_object(obj)

    def add_object(self, obj: RepresentationObject) -> None:
        if not isinstance(obj, RepresentationObject):
            raise MemoryRepresentationCategoryError(
                "RepresentationObject required"
            )
        if obj.object_id in self._objects:
            raise MemoryRepresentationCategoryError(
                f"duplicate object {obj.object_id}"
            )
        self._objects[obj.object_id] = obj
        ident = PartialMorphism(
            morphism_id=f"id:{obj.object_id}",
            source_id=obj.object_id,
            target_id=obj.object_id,
            role="IDENTITY",
            observable="IDENTITY",
            distance="EXACT",
            error_bound=0.0,
            horizon=2**31 - 1,
            domain_sector=obj.sector,
            invertible=True,
            total_on_declared_domain=True,
        )
        self._morphisms[ident.morphism_id] = ident

    def object(self, object_id: str) -> RepresentationObject:
        try:
            return self._objects[object_id]
        except KeyError as exc:
            raise MemoryRepresentationCategoryError(
                f"unknown object {object_id}"
            ) from exc

    def fiber(
        self, memory_id: str
    ) -> tuple[RepresentationObject, ...]:
        return tuple(
            sorted(
                (
                    x
                    for x in self._objects.values()
                    if x.memory_id == memory_id
                ),
                key=lambda x: x.object_id,
            )
        )

    def add_morphism(self, morphism: PartialMorphism) -> None:
        if not isinstance(morphism, PartialMorphism):
            raise MemoryRepresentationCategoryError(
                "PartialMorphism required"
            )
        if morphism.morphism_id in self._morphisms:
            raise MemoryRepresentationCategoryError(
                f"duplicate morphism {morphism.morphism_id}"
            )
        src = self.object(morphism.source_id)
        dst = self.object(morphism.target_id)
        if (
            morphism.role
            in {"COMPILER", "EMBEDDING", "RECONSTRUCTION"}
            and src.memory_id != dst.memory_id
        ):
            raise MemoryRepresentationCategoryError(
                f"{morphism.role} cannot silently change "
                "underlying memory identity"
            )
        self._morphisms[morphism.morphism_id] = morphism

    def morphism(self, morphism_id: str) -> PartialMorphism:
        try:
            return self._morphisms[morphism_id]
        except KeyError as exc:
            raise MemoryRepresentationCategoryError(
                f"unknown morphism {morphism_id}"
            ) from exc

    def compose(
        self,
        first_id: str,
        second_id: str,
        *,
        composed_id: str,
    ) -> PartialMorphism:
        """Return second ∘ first.

        For non-identity arrows, observable and distance contracts must agree.
        Error bounds add by the triangle bound and supported horizon becomes
        the minimum of the two arrows.
        """
        f = self.morphism(first_id)
        g = self.morphism(second_id)
        if f.target_id != g.source_id:
            raise MemoryRepresentationCategoryError(
                "morphism endpoints do not compose"
            )
        if f.role == "IDENTITY":
            return PartialMorphism(
                composed_id,
                g.source_id,
                g.target_id,
                g.role,
                g.observable,
                g.distance,
                g.error_bound,
                g.horizon,
                g.domain_sector,
                g.invariant_preserved,
                g.provenance_preserved,
                g.invertible,
                g.total_on_declared_domain,
            )
        if g.role == "IDENTITY":
            return PartialMorphism(
                composed_id,
                f.source_id,
                f.target_id,
                f.role,
                f.observable,
                f.distance,
                f.error_bound,
                f.horizon,
                f.domain_sector,
                f.invariant_preserved,
                f.provenance_preserved,
                f.invertible,
                f.total_on_declared_domain,
            )
        if (
            f.observable != g.observable
            or f.distance != g.distance
        ):
            raise MemoryRepresentationCategoryError(
                "behavioral contracts do not compose"
            )
        role = (
            "COMPILER"
            if f.role == g.role == "COMPILER"
            else "PROJECTION"
        )
        return PartialMorphism(
            morphism_id=composed_id,
            source_id=f.source_id,
            target_id=g.target_id,
            role=role,
            observable=f.observable,
            distance=f.distance,
            error_bound=f.error_bound + g.error_bound,
            horizon=min(f.horizon, g.horizon),
            domain_sector=f.domain_sector,
            invariant_preserved=(
                f.invariant_preserved and g.invariant_preserved
            ),
            provenance_preserved=(
                f.provenance_preserved and g.provenance_preserved
            ),
            invertible=f.invertible and g.invertible,
            total_on_declared_domain=(
                f.total_on_declared_domain
                and g.total_on_declared_domain
            ),
        )

    def is_groupoid_on(
        self, morphism_ids: Iterable[str]
    ) -> bool:
        """Necessary finite witness: all selected arrows must be invertible."""
        return all(
            self.morphism(mid).invertible for mid in morphism_ids
        )


def classify_global_structure(
    *,
    has_lossy_projection: bool,
    has_partial_reconstruction: bool,
    ternary_closed_under_composition: bool,
) -> str:
    """Fail-loud classifier for the current Memory-Ontology stack."""
    if has_lossy_projection or has_partial_reconstruction:
        return "CATEGORY_OF_PARTIAL_TYPED_MORPHISMS"
    if not ternary_closed_under_composition:
        return "CATEGORY_WITH_PARTIAL_TERNARY_ALGEBRA"
    return "GROUPOID_CANDIDATE_REQUIRES_INVERSE_WITNESSES"
