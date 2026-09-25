from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Iterable

TAU = math.tau
ADMISSIBLE_PROJECTION_STATUS = {"OBSERVED", "COMMITTED"}
OUTPUT_STATES = {
    "RECALLED",
    "RECONSTRUCTED",
    "INFERRED",
    "IMAGINED",
    "INSUFFICIENT_EVIDENCE",
    "CONFLICT",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def normalize_phase(phi: float) -> float:
    value = float(phi) % TAU
    if math.isclose(value, TAU, rel_tol=0.0, abs_tol=1e-12):
        return 0.0
    if math.isclose(value, 0.0, rel_tol=0.0, abs_tol=1e-12):
        return 0.0
    return value


@dataclass(frozen=True)
class OrbitalAddress:
    orbit_class: str
    phase_rad: float
    scale: str
    boundary: str
    relation_signature: str
    provenance_commitment: str

    def canonical(self) -> dict[str, Any]:
        return {
            "orbit_class": self.orbit_class,
            "phase_rad": round(normalize_phase(self.phase_rad), 12),
            "scale": self.scale,
            "boundary": self.boundary,
            "relation_signature": self.relation_signature,
            "provenance_commitment": self.provenance_commitment,
        }

    def address_id(self) -> str:
        return "sha256:" + _sha256(self.canonical())


def reconstruct(
    projections: Iterable[dict[str, Any]],
    *,
    min_support: int = 2,
) -> dict[str, Any]:
    if min_support < 1:
        raise ValueError("min_support must be >= 1")

    groups: dict[str, dict[str, Any]] = {}
    used = 0

    for raw in projections:
        if raw.get("status") not in ADMISSIBLE_PROJECTION_STATUS:
            continue
        invariant = raw.get("invariant")
        projection_id = raw.get("projection_id")
        provenance = raw.get("provenance_commitment")
        weight = raw.get("weight", 1.0)

        if not isinstance(invariant, str) or not invariant:
            continue
        if not isinstance(projection_id, str) or not projection_id:
            continue
        if not isinstance(provenance, str) or not provenance:
            continue
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            continue
        weight = float(weight)
        if not math.isfinite(weight) or weight <= 0:
            continue

        used += 1
        group = groups.setdefault(
            invariant,
            {"invariant": invariant, "support": 0, "weight": 0.0, "projection_ids": []},
        )
        group["support"] += 1
        group["weight"] += weight
        group["projection_ids"].append(projection_id)

    if not groups:
        return {
            "status": "INSUFFICIENT_EVIDENCE",
            "support": 0,
            "used_projections": used,
        }

    ranked = sorted(
        groups.values(),
        key=lambda g: (g["support"], g["weight"], g["invariant"]),
        reverse=True,
    )
    best = ranked[0]

    if best["support"] < min_support:
        return {
            "status": "INSUFFICIENT_EVIDENCE",
            "support": best["support"],
            "used_projections": used,
            "candidate_invariant": best["invariant"],
        }

    if len(ranked) > 1:
        second = ranked[1]
        if (
            second["support"] == best["support"]
            and math.isclose(second["weight"], best["weight"], rel_tol=0.0, abs_tol=1e-12)
        ):
            return {
                "status": "CONFLICT",
                "support": best["support"],
                "used_projections": used,
                "candidate_invariants": sorted([best["invariant"], second["invariant"]]),
            }

    return {
        "status": "RECONSTRUCTED",
        "invariant": best["invariant"],
        "support": best["support"],
        "weight": best["weight"],
        "projection_ids": sorted(best["projection_ids"]),
        "used_projections": used,
    }


def authorize_output(requested_state: str, *, provenance_verified: bool) -> str:
    if requested_state not in OUTPUT_STATES:
        raise ValueError("unknown output state")
    if requested_state == "RECALLED" and not provenance_verified:
        raise ValueError("RECALLED requires verified historical provenance")
    return requested_state
