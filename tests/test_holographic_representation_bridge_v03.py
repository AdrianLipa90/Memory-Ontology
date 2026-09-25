import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engines.reconstruction.orbital_reconstruction import reconstruct
from algebra.memory_representation_category import (
    MemoryRepresentationCategory,
    RepresentationObject,
)
from algebra.holographic_representation_bridge import (
    HolographicRepresentationBridge,
    HolographicRepresentationBridgeError,
    make_ternary_holographic_projection,
)


def payload(coeffs, phase=0.0):
    return {
        "representation": "SIGNED_TERNARY_ORBITAL",
        "path_coeffs": list(coeffs),
        "phase_rad": phase,
        "orbit_class": "o:A",
        "scale": "meso",
        "boundary_context": "ctx",
        "physical_substrate_claim": False,
    }


def setup_bridge():
    source = RepresentationObject(
        "memory:full",
        "memory:m",
        "ORBITAL_MEMORY",
        "I",
        "prov:root",
        "GENERAL",
    )
    c = MemoryRepresentationCategory([source])
    return c, HolographicRepresentationBridge(
        c, "memory:full"
    )


def p(
    pid,
    invariant="I",
    status="COMMITTED",
    coeffs=(1, 0, -1),
    weight=1.0,
):
    return make_ternary_holographic_projection(
        projection_id=pid,
        invariant=invariant,
        exact_sector_payload=payload(coeffs),
        provenance_commitment=f"prov:{pid}",
        status=status,
        weight=weight,
    )


def test_ternary_projection_is_consumed_by_existing_reconstruction():
    projections = [
        p("p1"),
        p("p2"),
        p("p3", status="CANDIDATE"),
    ]
    result = reconstruct(projections, min_support=2)
    assert result["status"] == "RECONSTRUCTED"
    assert result["invariant"] == "I"
    assert result["projection_ids"] == ["p1", "p2"]


def test_reconstruction_becomes_typed_partial_morphism():
    c, b = setup_bridge()
    projections = [p("p1"), p("p2")]
    for x in projections:
        b.register_projection(x)
    result = reconstruct(projections, min_support=2)
    bundle = b.admit_reconstruction(result)
    assert bundle == "bundle:p1+p2"
    m = c.morphism("reconstruct:bundle:p1+p2")
    assert m.role == "RECONSTRUCTION"
    assert m.invertible is False
    assert m.total_on_declared_domain is False


def test_partial_loss_can_still_reconstruct():
    c, b = setup_bridge()
    projections = [p("p1"), p("p2"), p("p3")]
    for x in projections:
        b.register_projection(x)
    surviving = projections[:2]
    result = reconstruct(surviving, min_support=2)
    assert result["status"] == "RECONSTRUCTED"
    assert result["support"] == 2
    assert (
        b.admit_reconstruction(result)
        == "bundle:p1+p2"
    )


def test_insufficient_support_creates_no_reconstruction_arrow():
    c, b = setup_bridge()
    projections = [p("p1")]
    b.register_projection(projections[0])
    result = reconstruct(projections, min_support=2)
    assert result["status"] == "INSUFFICIENT_EVIDENCE"
    assert b.admit_reconstruction(result) is None


def test_equal_support_conflict_creates_no_reconstruction_arrow():
    c, b = setup_bridge()
    projections = [
        p("p1", "I"),
        p("p2", "I"),
        p("q1", "J"),
        p("q2", "J"),
    ]
    for x in projections:
        b.register_projection(x)
    result = reconstruct(projections, min_support=2)
    assert result["status"] == "CONFLICT"
    assert b.admit_reconstruction(result) is None


def test_candidate_projection_is_not_historical_support():
    projections = [
        p("p1"),
        p("p2", status="CANDIDATE"),
    ]
    result = reconstruct(projections, min_support=2)
    assert result["status"] == "INSUFFICIENT_EVIDENCE"
    assert result["support"] == 1


def test_physical_substrate_self_promotion_fails_closed():
    bad = payload((1, 0, -1))
    bad["physical_substrate_claim"] = True
    with pytest.raises(
        HolographicRepresentationBridgeError
    ):
        make_ternary_holographic_projection(
            projection_id="p",
            invariant="I",
            exact_sector_payload=bad,
            provenance_commitment="prov:p",
        )


def test_nonternary_coefficients_fail_closed():
    with pytest.raises(
        HolographicRepresentationBridgeError
    ):
        make_ternary_holographic_projection(
            projection_id="p",
            invariant="I",
            exact_sector_payload=payload(
                (2, 0, -1)
            ),
            provenance_commitment="prov:p",
        )


def test_projection_objects_remain_in_same_memory_fiber():
    c, b = setup_bridge()
    b.register_projection(p("p1"))
    b.register_projection(p("p2"))
    ids = [
        x.object_id
        for x in c.fiber("memory:m")
    ]
    assert ids == [
        "memory:full",
        "projection:p1",
        "projection:p2",
    ]


def test_reconstruction_bundle_provenance_is_order_invariant():
    c1, b1 = setup_bridge()
    xs = [p("p1"), p("p2")]
    for x in xs:
        b1.register_projection(x)
    r1 = reconstruct(xs, min_support=2)
    bid1 = b1.admit_reconstruction(r1)
    prov1 = c1.object(bid1).provenance_commitment

    c2, b2 = setup_bridge()
    ys = [p("p2"), p("p1")]
    for x in ys:
        b2.register_projection(x)
    r2 = reconstruct(ys, min_support=2)
    bid2 = b2.admit_reconstruction(r2)
    prov2 = c2.object(bid2).provenance_commitment
    assert prov1 == prov2


def test_mismatched_reconstructed_invariant_is_rejected():
    c, b = setup_bridge()
    b.register_projection(p("p1"))
    with pytest.raises(
        HolographicRepresentationBridgeError
    ):
        b.admit_reconstruction(
            {
                "status": "RECONSTRUCTED",
                "invariant": "J",
                "projection_ids": ["p1"],
            }
        )
