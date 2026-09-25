from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .memory_representation_category import (
    MemoryRepresentationCategory,
    MemoryRepresentationCategoryError,
    PartialMorphism,
    RepresentationObject,
)


class HolographicRepresentationBridgeError(ValueError):
    pass


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def make_ternary_holographic_projection(
    *,
    projection_id: str,
    invariant: str,
    exact_sector_payload: Mapping[str, object],
    provenance_commitment: str,
    status: str = "COMMITTED",
    weight: float = 1.0,
) -> dict:
    if (
        exact_sector_payload.get("representation")
        != "SIGNED_TERNARY_ORBITAL"
    ):
        raise HolographicRepresentationBridgeError(
            "expected SIGNED_TERNARY_ORBITAL payload"
        )
    if exact_sector_payload.get("physical_substrate_claim") is not False:
        raise HolographicRepresentationBridgeError(
            "projection cannot acquire physical-substrate authority"
        )
    coeffs = exact_sector_payload.get("path_coeffs")
    if (
        not isinstance(coeffs, list)
        or not coeffs
        or any(x not in (-1, 0, 1) for x in coeffs)
    ):
        raise HolographicRepresentationBridgeError(
            "invalid exact ternary path coefficients"
        )
    phase = exact_sector_payload.get("phase_rad")
    if (
        isinstance(phase, bool)
        or not isinstance(phase, (int, float))
    ):
        raise HolographicRepresentationBridgeError(
            "phase_rad must be numeric"
        )
    if status not in {"OBSERVED", "COMMITTED", "CANDIDATE"}:
        raise HolographicRepresentationBridgeError(
            "invalid projection status"
        )
    if (
        not isinstance(weight, (int, float))
        or isinstance(weight, bool)
        or weight <= 0
    ):
        raise HolographicRepresentationBridgeError(
            "weight must be positive"
        )
    return {
        "projection_id": projection_id,
        "invariant": invariant,
        "status": status,
        "weight": float(weight),
        "provenance_commitment": provenance_commitment,
        "representation": "SIGNED_TERNARY_ORBITAL",
        "path_coeffs": list(coeffs),
        "phase_rad": float(phase),
        "orbit_class": exact_sector_payload.get("orbit_class"),
        "scale": exact_sector_payload.get("scale"),
        "boundary_context": exact_sector_payload.get(
            "boundary_context"
        ),
        "physical_substrate_claim": False,
    }


class HolographicRepresentationBridge:
    def __init__(
        self,
        category: MemoryRepresentationCategory,
        source_object_id: str,
    ) -> None:
        self.category = category
        self.source = category.object(source_object_id)
        self._projection_objects: dict[str, str] = {}

    def register_projection(
        self, projection: Mapping[str, object]
    ) -> str:
        pid = projection.get("projection_id")
        invariant = projection.get("invariant")
        provenance = projection.get("provenance_commitment")
        if not isinstance(pid, str) or not pid:
            raise HolographicRepresentationBridgeError(
                "projection_id required"
            )
        if not isinstance(invariant, str) or not invariant:
            raise HolographicRepresentationBridgeError(
                "projection invariant required"
            )
        if not isinstance(provenance, str) or not provenance:
            raise HolographicRepresentationBridgeError(
                "projection provenance required"
            )
        if projection.get("physical_substrate_claim") is True:
            raise HolographicRepresentationBridgeError(
                "projection cannot self-promote physical substrate"
            )
        family = str(
            projection.get("representation")
            or "HOLOGRAPHIC_PROJECTION"
        )
        oid = f"projection:{pid}"
        try:
            self.category.add_object(
                RepresentationObject(
                    object_id=oid,
                    memory_id=self.source.memory_id,
                    family=family,
                    invariant_commitment=invariant,
                    provenance_commitment=provenance,
                    sector="PROJECTION_VIEW",
                )
            )
            self.category.add_morphism(
                PartialMorphism(
                    morphism_id=f"project:{pid}",
                    source_id=self.source.object_id,
                    target_id=oid,
                    role="PROJECTION",
                    observable="memory_invariant",
                    distance="EXACT",
                    error_bound=0.0,
                    horizon=2**31 - 1,
                    domain_sector="DECLARED_PROJECTION_DOMAIN",
                    invariant_preserved=(
                        invariant
                        == self.source.invariant_commitment
                    ),
                    provenance_preserved=True,
                    invertible=False,
                    total_on_declared_domain=True,
                )
            )
        except MemoryRepresentationCategoryError as exc:
            raise HolographicRepresentationBridgeError(
                str(exc)
            ) from exc
        self._projection_objects[pid] = oid
        return oid

    def admit_reconstruction(
        self, result: Mapping[str, object]
    ) -> str | None:
        status = result.get("status")
        if status in {
            "INSUFFICIENT_EVIDENCE",
            "CONFLICT",
        }:
            return None
        if status != "RECONSTRUCTED":
            raise HolographicRepresentationBridgeError(
                f"unsupported reconstruction status {status}"
            )
        invariant = result.get("invariant")
        if invariant != self.source.invariant_commitment:
            raise HolographicRepresentationBridgeError(
                "reconstructed invariant does not match source memory"
            )
        pids = result.get("projection_ids")
        if not isinstance(pids, list) or not pids:
            raise HolographicRepresentationBridgeError(
                "reconstruction must list contributing projections"
            )
        missing = [
            pid
            for pid in pids
            if pid not in self._projection_objects
        ]
        if missing:
            raise HolographicRepresentationBridgeError(
                f"unregistered projection(s): {missing}"
            )
        records = [
            self.category.object(
                self._projection_objects[pid]
            )
            for pid in sorted(pids)
        ]
        bundle_commitment = "sha256:" + _sha256(
            {
                "memory_id": self.source.memory_id,
                "invariant": invariant,
                "projection_ids": sorted(pids),
                "provenance": [
                    x.provenance_commitment
                    for x in records
                ],
            }
        )
        bundle_id = "bundle:" + "+".join(sorted(pids))
        try:
            self.category.add_object(
                RepresentationObject(
                    object_id=bundle_id,
                    memory_id=self.source.memory_id,
                    family="HOLOGRAPHIC_PROJECTION_BUNDLE",
                    invariant_commitment=str(invariant),
                    provenance_commitment=bundle_commitment,
                    sector=(
                        "ADMISSIBLE_RECONSTRUCTION_SUPPORT"
                    ),
                )
            )
            self.category.add_morphism(
                PartialMorphism(
                    morphism_id=(
                        f"reconstruct:{bundle_id}"
                    ),
                    source_id=bundle_id,
                    target_id=self.source.object_id,
                    role="RECONSTRUCTION",
                    observable="memory_invariant",
                    distance="EXACT",
                    error_bound=0.0,
                    horizon=2**31 - 1,
                    domain_sector=(
                        "ADMISSIBLE_RECONSTRUCTION_SUPPORT"
                    ),
                    invariant_preserved=True,
                    provenance_preserved=True,
                    invertible=False,
                    total_on_declared_domain=False,
                )
            )
        except MemoryRepresentationCategoryError as exc:
            raise HolographicRepresentationBridgeError(
                str(exc)
            ) from exc
        return bundle_id
