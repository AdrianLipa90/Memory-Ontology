from __future__ import annotations

from dataclasses import dataclass

from .collatz_history_groupoid_v04 import CollatzPath, inverse_laws_hold
from .memory_representation_category_v04 import (
    MemoryRepresentationCategoryV4,
    RepresentationCategoryV4Error,
    TypedMorphismV4,
)


class BehavioralCoreError(ValueError):
    pass


def _nonempty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise BehavioralCoreError(f"{field} must be non-empty")
    return value


@dataclass(frozen=True)
class BehavioralInverseWitness:
    witness_id: str
    forward_id: str
    inverse_id: str
    validator: str
    validator_receipt: str
    left_identity_verified: bool
    right_identity_verified: bool
    domain_image_verified: bool

    def __post_init__(self) -> None:
        for field in (
            "witness_id",
            "forward_id",
            "inverse_id",
            "validator",
            "validator_receipt",
        ):
            _nonempty(getattr(self, field), field)
        if self.forward_id == self.inverse_id:
            raise BehavioralCoreError(
                "inverse witness requires two distinct non-identity arrows"
            )
        if (
            self.left_identity_verified is not True
            or self.right_identity_verified is not True
            or self.domain_image_verified is not True
        ):
            raise BehavioralCoreError(
                "inverse witness must verify both identities and domain/image"
            )


@dataclass(frozen=True)
class CertifiedBehavioralCore:
    object_ids: tuple[str, ...]
    morphism_ids: tuple[str, ...]
    inverse_pairs: tuple[tuple[str, str], ...]
    excluded_unwitnessed_invertible_ids: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "schema": "MEMORY_CERTIFIED_BEHAVIORAL_CORE_V0_4",
            "object_ids": list(self.object_ids),
            "morphism_ids": list(self.morphism_ids),
            "inverse_pairs": [list(x) for x in self.inverse_pairs],
            "excluded_unwitnessed_invertible_ids": list(
                self.excluded_unwitnessed_invertible_ids
            ),
            "maximal_core_claim": False,
            "witness_required": True,
        }


def same_declared_behavior(
    left: TypedMorphismV4,
    right: TypedMorphismV4,
) -> bool:
    return left.behavioral_signature() == right.behavioral_signature()


def same_history(
    left: TypedMorphismV4,
    right: TypedMorphismV4,
) -> bool:
    return left.historical_signature() == right.historical_signature()


def validate_inverse_pair(
    category: MemoryRepresentationCategoryV4,
    witness: BehavioralInverseWitness,
) -> tuple[TypedMorphismV4, TypedMorphismV4]:
    try:
        f = category.morphism(witness.forward_id)
        g = category.morphism(witness.inverse_id)
    except RepresentationCategoryV4Error as exc:
        raise BehavioralCoreError(str(exc)) from exc

    if f.source_id != g.target_id or f.target_id != g.source_id:
        raise BehavioralCoreError("inverse witness endpoints are not reversed")
    if (
        f.source_sector != g.target_sector
        or f.target_sector != g.source_sector
    ):
        raise BehavioralCoreError("inverse witness sectors are not reversed")
    if f.observable != g.observable or f.distance != g.distance:
        raise BehavioralCoreError("inverse behavioral contracts differ")
    if f.error_bound != 0 or g.error_bound != 0:
        raise BehavioralCoreError(
            "certified behavioral core currently requires exact zero-error arrows"
        )
    if (
        f.invertible_on_declared_image is not True
        or g.invertible_on_declared_image is not True
    ):
        raise BehavioralCoreError(
            "both arrows must already declare local invertibility"
        )
    if (
        f.invariant_preserved is not True
        or g.invariant_preserved is not True
        or f.provenance_preserved is not True
        or g.provenance_preserved is not True
    ):
        raise BehavioralCoreError(
            "memory inverse pair must preserve invariant and provenance admission"
        )
    return f, g


def extract_certified_behavioral_core(
    category: MemoryRepresentationCategoryV4,
    witnesses: tuple[BehavioralInverseWitness, ...],
) -> CertifiedBehavioralCore:
    admitted: set[str] = set()
    pairs: set[tuple[str, str]] = set()

    for witness in witnesses:
        f, g = validate_inverse_pair(category, witness)
        admitted.add(f.morphism_id)
        admitted.add(g.morphism_id)
        pairs.add(tuple(sorted((f.morphism_id, g.morphism_id))))

    all_morphisms = category.morphisms()
    identities = {
        m.morphism_id
        for m in all_morphisms
        if not m.lineage and m.source_id == m.target_id
    }
    admitted |= identities

    excluded = sorted(
        m.morphism_id
        for m in all_morphisms
        if m.invertible_on_declared_image
        and m.morphism_id not in admitted
        and m.morphism_id not in identities
    )

    return CertifiedBehavioralCore(
        object_ids=tuple(x.object_id for x in category.objects()),
        morphism_ids=tuple(sorted(admitted)),
        inverse_pairs=tuple(sorted(pairs)),
        excluded_unwitnessed_invertible_ids=tuple(excluded),
    )


def collatz_inverse_witness(
    path: CollatzPath,
    *,
    forward_id: str,
    inverse_id: str,
    validator_receipt: str,
) -> BehavioralInverseWitness:
    if not isinstance(path, CollatzPath):
        raise BehavioralCoreError("CollatzPath required")
    if not inverse_laws_hold(path):
        raise BehavioralCoreError("Collatz inverse laws did not validate")
    return BehavioralInverseWitness(
        witness_id=f"collatz:{path.start}->{path.end}:{path.prime_history_code}",
        forward_id=forward_id,
        inverse_id=inverse_id,
        validator="COLLATZ_BEHAVIORAL_PATH_GROUPOID_V0_4",
        validator_receipt=_nonempty(
            validator_receipt, "validator_receipt"
        ),
        left_identity_verified=True,
        right_identity_verified=True,
        domain_image_verified=True,
    )
