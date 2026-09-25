import itertools
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from algebra.orbital_ternary_memory_algebra import (
    IntegerPath,
    OrbitalTernaryAddress,
    OrbitalTernaryAlgebraError,
    TernaryPath,
    boundary,
    exact_sector_projection,
    holonomy,
    is_cycle,
    normalize_phase,
    phase_pairing,
    phasenav_outer_shell_to_stella,
    stella_shell,
    stella_shell_counts,
)


def test_stella_shell_decomposition_is_exact():
    assert stella_shell_counts() == {
        "CENTER": 1,
        "AXIS": 6,
        "EDGE": 12,
        "CORNER": 8,
    }


def test_phasenav_outer_sign_shell_is_exact_stella_corner_shell():
    seen = set()
    for signs in itertools.product((-1, 1), repeat=3):
        stella = phasenav_outer_shell_to_stella(signs)
        assert stella == signs
        assert stella_shell(stella) == "CORNER"
        seen.add(stella)
    assert len(seen) == 8


def test_ternary_composition_stays_in_sector_when_closed():
    a = TernaryPath((1, 0, -1))
    b = TernaryPath((-1, 1, 0))
    c = a.compose(b)
    assert isinstance(c, TernaryPath)
    assert c.coeffs == (0, 1, -1)


def test_ternary_overflow_lifts_to_integer_chain_exactly():
    a = TernaryPath((1, 0, -1))
    b = TernaryPath((1, 1, 0))
    c = a.compose(b)
    assert isinstance(c, IntegerPath)
    assert c.coeffs == (2, 1, -1)


def test_no_mod3_or_saturation_is_silently_applied():
    c = TernaryPath((1,)).compose(TernaryPath((1,)))
    assert isinstance(c, IntegerPath)
    assert c.coeffs == (2,)
    assert c.coeffs != (-1,)
    assert c.coeffs != (1,)


def test_triangle_cycle_satisfies_boundary_zero():
    # Directed edges e01, e12, e20.
    B = (
        (-1, 0, 1),
        (1, -1, 0),
        (0, 1, -1),
    )
    t = TernaryPath((1, 1, 1))
    assert boundary(B, t) == (0, 0, 0)
    assert is_cycle(B, t)


def test_open_path_has_nonzero_boundary():
    B = (
        (-1, 0, 1),
        (1, -1, 0),
        (0, 1, -1),
    )
    t = TernaryPath((1, 1, 0))
    assert boundary(B, t) == (-1, 0, 1)
    assert not is_cycle(B, t)


def test_holonomy_character_respects_composable_ternary_sum():
    theta = (0.2, -0.4, 0.9)
    a = TernaryPath((1, 0, 0))
    b = TernaryPath((0, -1, 1))
    c = a.compose(b)
    assert isinstance(c, TernaryPath)
    assert abs(
        holonomy(c, theta)
        - holonomy(a, theta) * holonomy(b, theta)
    ) < 1e-12


def test_integer_overflow_lift_preserves_holonomy_product():
    theta = (0.31,)
    a = TernaryPath((1,))
    b = TernaryPath((1,))
    c = a.compose(b)
    assert isinstance(c, IntegerPath)
    assert abs(
        holonomy(c, theta)
        - holonomy(a, theta) * holonomy(b, theta)
    ) < 1e-12


def test_reverse_path_conjugates_holonomy():
    theta = (0.2, 0.5, -0.7)
    a = TernaryPath((1, -1, 1))
    assert abs(
        holonomy(a.negate(), theta)
        - holonomy(a, theta).conjugate()
    ) < 1e-12


def test_phase_is_canonical_mod_two_pi():
    a = TernaryPath((1,))
    assert normalize_phase(2 * math.pi) == 0.0
    assert abs(
        phase_pairing(a, (2 * math.pi + 0.3,)) - 0.3
    ) < 1e-12


def test_orbital_address_is_refined_by_signed_path_and_holonomy():
    addr = OrbitalTernaryAddress(
        retained_classes=("path", "relation"),
        path=TernaryPath((1, -1, 0)),
        orbit_class="o:test",
        edge_phases=(0.8, 0.3, 1.7),
        scale="local",
        boundary_context="ctx",
        provenance_commitment="sha256:abc",
    )
    assert addr.sector == "TERNARY_SIMPLE_PATH"
    assert abs(addr.phase_rad - 0.5) < 1e-12
    p = exact_sector_projection(addr)
    assert p["path_coeffs"] == [1, -1, 0]
    assert abs(p["phase_rad"] - 0.5) < 1e-12
    assert p["physical_substrate_claim"] is False


def test_address_hash_is_phase_wrap_invariant():
    a = OrbitalTernaryAddress(
        ("path",),
        TernaryPath((1,)),
        "o",
        (0.4,),
        "s",
        "b",
        "p",
    )
    b = OrbitalTernaryAddress(
        ("path",),
        TernaryPath((1,)),
        "o",
        (0.4 + 2 * math.pi,),
        "s",
        "b",
        "p",
    )
    assert a.address_id() == b.address_id()


def test_exact_projection_rejects_integer_overflow_sector():
    addr = OrbitalTernaryAddress(
        ("path",),
        IntegerPath((2,)),
        "o",
        (0.1,),
        "s",
        "b",
        "p",
    )
    try:
        exact_sector_projection(addr)
        assert False
    except OrbitalTernaryAlgebraError:
        pass
