from __future__ import annotations

from dataclasses import dataclass
import cmath
import hashlib
import json
import math
from typing import Sequence

TAU = math.tau
TRITS = (-1, 0, 1)


class OrbitalTernaryAlgebraError(ValueError):
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


def normalize_phase(phi: float) -> float:
    value = float(phi) % TAU
    if (
        math.isclose(value, TAU, rel_tol=0.0, abs_tol=1e-12)
        or math.isclose(value, 0.0, rel_tol=0.0, abs_tol=1e-12)
    ):
        return 0.0
    return value


def stella_shell(v: Sequence[int]) -> str:
    if len(v) != 3 or any(x not in TRITS for x in v):
        raise OrbitalTernaryAlgebraError(
            "Stella cell must be three signed trits"
        )
    k = sum(x != 0 for x in v)
    return {0: "CENTER", 1: "AXIS", 2: "EDGE", 3: "CORNER"}[k]


def stella_shell_counts() -> dict[str, int]:
    out = {"CENTER": 0, "AXIS": 0, "EDGE": 0, "CORNER": 0}
    for a in TRITS:
        for b in TRITS:
            for c in TRITS:
                out[stella_shell((a, b, c))] += 1
    return out


def phasenav_outer_shell_to_stella(
    signs: Sequence[int],
) -> tuple[int, int, int]:
    if len(signs) != 3 or any(x not in (-1, 1) for x in signs):
        raise OrbitalTernaryAlgebraError(
            "PhaseNav outer-shell sign code must be in {+-1}^3"
        )
    return tuple(int(x) for x in signs)


@dataclass(frozen=True)
class IntegerPath:
    coeffs: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.coeffs:
            raise OrbitalTernaryAlgebraError("path cannot be empty")
        if any(
            isinstance(x, bool) or not isinstance(x, int)
            for x in self.coeffs
        ):
            raise OrbitalTernaryAlgebraError(
                "integer path coefficients must be integers"
            )

    def negate(self) -> "IntegerPath":
        return IntegerPath(tuple(-x for x in self.coeffs))

    def add(self, other: "IntegerPath") -> "IntegerPath":
        if len(self.coeffs) != len(other.coeffs):
            raise OrbitalTernaryAlgebraError("path dimensions differ")
        return IntegerPath(
            tuple(a + b for a, b in zip(self.coeffs, other.coeffs))
        )


@dataclass(frozen=True)
class TernaryPath:
    coeffs: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.coeffs:
            raise OrbitalTernaryAlgebraError("path cannot be empty")
        if any(x not in TRITS for x in self.coeffs):
            raise OrbitalTernaryAlgebraError(
                "ternary path coefficients must be in {-1,0,+1}"
            )

    def negate(self) -> "TernaryPath":
        return TernaryPath(tuple(-x for x in self.coeffs))

    def lift(self) -> IntegerPath:
        return IntegerPath(self.coeffs)

    def compose(
        self,
        other: "TernaryPath",
    ) -> "TernaryPath | IntegerPath":
        """Exact typed composition.

        If component-wise addition remains in T3, stay in the ternary
        sector. Otherwise lift exactly to the integer chain space instead
        of silently clipping, saturating, or reducing modulo 3.
        """
        if len(self.coeffs) != len(other.coeffs):
            raise OrbitalTernaryAlgebraError("path dimensions differ")
        summed = tuple(
            a + b for a, b in zip(self.coeffs, other.coeffs)
        )
        if all(x in TRITS for x in summed):
            return TernaryPath(summed)
        return IntegerPath(summed)


def boundary(
    incidence: Sequence[Sequence[int]],
    path: TernaryPath | IntegerPath,
) -> tuple[int, ...]:
    if not incidence:
        raise OrbitalTernaryAlgebraError(
            "incidence matrix cannot be empty"
        )
    width = len(path.coeffs)
    out = []
    for row in incidence:
        if len(row) != width:
            raise OrbitalTernaryAlgebraError(
                "incidence/path dimension mismatch"
            )
        out.append(
            sum(
                int(b) * int(t)
                for b, t in zip(row, path.coeffs)
            )
        )
    return tuple(out)


def is_cycle(
    incidence: Sequence[Sequence[int]],
    path: TernaryPath | IntegerPath,
) -> bool:
    return all(x == 0 for x in boundary(incidence, path))


def phase_pairing(
    path: TernaryPath | IntegerPath,
    edge_phases: Sequence[float],
) -> float:
    if len(path.coeffs) != len(edge_phases):
        raise OrbitalTernaryAlgebraError(
            "phase/path dimension mismatch"
        )
    return normalize_phase(
        sum(
            t * float(theta)
            for t, theta in zip(path.coeffs, edge_phases)
        )
    )


def holonomy(
    path: TernaryPath | IntegerPath,
    edge_phases: Sequence[float],
) -> complex:
    return cmath.exp(1j * phase_pairing(path, edge_phases))


@dataclass(frozen=True)
class OrbitalTernaryAddress:
    retained_classes: tuple[str, ...]
    path: TernaryPath | IntegerPath
    orbit_class: str
    edge_phases: tuple[float, ...]
    scale: str
    boundary_context: str
    provenance_commitment: str

    @property
    def phase_rad(self) -> float:
        return phase_pairing(self.path, self.edge_phases)

    @property
    def sector(self) -> str:
        if isinstance(self.path, TernaryPath):
            return "TERNARY_SIMPLE_PATH"
        return "INTEGER_WINDING_LIFT"

    def canonical(self) -> dict:
        return {
            "retained_classes": list(self.retained_classes),
            "path_coeffs": list(self.path.coeffs),
            "path_sector": self.sector,
            "orbit_class": self.orbit_class,
            "phase_rad": round(self.phase_rad, 12),
            "scale": self.scale,
            "boundary_context": self.boundary_context,
            "provenance_commitment": self.provenance_commitment,
        }

    def address_id(self) -> str:
        return "sha256:" + _sha256(self.canonical())


def exact_sector_projection(
    address: OrbitalTernaryAddress,
) -> dict:
    """Project an orbital address into the exact signed-support sector.

    This is representation-level. It neither modifies Memory Ontology nor
    asserts a physical ternary or quantum substrate.
    """
    if not isinstance(address.path, TernaryPath):
        raise OrbitalTernaryAlgebraError(
            "exact ternary projection requires TernaryPath sector"
        )
    return {
        "path_coeffs": list(address.path.coeffs),
        "phase_rad": round(address.phase_rad, 12),
        "orbit_class": address.orbit_class,
        "scale": address.scale,
        "boundary_context": address.boundary_context,
        "provenance_commitment": address.provenance_commitment,
        "representation": "SIGNED_TERNARY_ORBITAL",
        "physical_substrate_claim": False,
    }
