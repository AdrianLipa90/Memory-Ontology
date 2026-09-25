import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from algebra.memory_representation_category import (
    BehaviorContract,
    MemoryRepresentationCategory,
    MemoryRepresentationCategoryError,
    PartialMorphism,
    RepresentationObject,
    classify_global_structure,
)


def obj(oid, family, sector="GENERAL"):
    return RepresentationObject(
        oid,
        "memory:m",
        family,
        invariant_commitment="inv:1",
        provenance_commitment="prov:1",
        sector=sector,
    )


def test_representation_fiber_keeps_same_underlying_memory():
    c = MemoryRepresentationCategory(
        [
            obj("q", "QUANTUM_NATIVE"),
            obj("b", "BINARY"),
            obj("t", "TERNARY_STELLA"),
        ]
    )
    assert [x.object_id for x in c.fiber("memory:m")] == ["b", "q", "t"]


def test_identity_arrows_exist_for_every_representation():
    c = MemoryRepresentationCategory([obj("a", "BINARY")])
    i = c.morphism("id:a")
    assert i.source_id == i.target_id == "a"
    assert i.invertible is True


def test_compiler_cannot_silently_change_memory_identity():
    a = obj("a", "BINARY")
    b = RepresentationObject(
        "b", "memory:other", "TERNARY_STELLA", "inv:1", "prov:1"
    )
    c = MemoryRepresentationCategory([a, b])
    with pytest.raises(MemoryRepresentationCategoryError):
        c.add_morphism(
            PartialMorphism(
                "bad",
                "a",
                "b",
                "COMPILER",
                "route_choice",
                "D",
                0,
                10,
            )
        )


def test_approximate_compilers_compose_by_triangle_bound():
    c = MemoryRepresentationCategory(
        [obj("q", "Q"), obj("t", "T"), obj("b", "B")]
    )
    c.add_morphism(
        PartialMorphism(
            "qt", "q", "t", "COMPILER", "route_choice", "D", 0.02, 100
        )
    )
    c.add_morphism(
        PartialMorphism(
            "tb", "t", "b", "COMPILER", "route_choice", "D", 0.03, 80
        )
    )
    qb = c.compose("qt", "tb", composed_id="qb")
    assert qb.source_id == "q" and qb.target_id == "b"
    assert qb.error_bound == pytest.approx(0.05)
    assert qb.horizon == 80
    assert qb.role == "COMPILER"


def test_composed_compiler_admission_uses_requested_contract():
    c = MemoryRepresentationCategory(
        [obj("q", "Q"), obj("t", "T"), obj("b", "B")]
    )
    c.add_morphism(
        PartialMorphism(
            "qt", "q", "t", "COMPILER", "route_choice", "D", 0.02, 100
        )
    )
    c.add_morphism(
        PartialMorphism(
            "tb", "t", "b", "COMPILER", "route_choice", "D", 0.03, 80
        )
    )
    qb = c.compose("qt", "tb", composed_id="qb")
    assert qb.admitted_by(
        BehaviorContract(0.05, 80, "route_choice", "D")
    )
    assert not qb.admitted_by(
        BehaviorContract(0.049, 80, "route_choice", "D")
    )


def test_mismatched_observables_do_not_compose():
    c = MemoryRepresentationCategory(
        [obj("a", "A"), obj("b", "B"), obj("c", "C")]
    )
    c.add_morphism(
        PartialMorphism(
            "ab", "a", "b", "COMPILER", "route_choice", "D", 0, 10
        )
    )
    c.add_morphism(
        PartialMorphism(
            "bc", "b", "c", "COMPILER", "phase", "D", 0, 10
        )
    )
    with pytest.raises(MemoryRepresentationCategoryError):
        c.compose("ab", "bc", composed_id="ac")


def test_lossy_projection_prevents_global_groupoid_claim():
    c = MemoryRepresentationCategory(
        [obj("full", "INTEGER_CHAIN"), obj("view", "TERNARY")]
    )
    c.add_morphism(
        PartialMorphism(
            "project",
            "full",
            "view",
            "PROJECTION",
            "signed_support",
            "D",
            0,
            100,
            domain_sector="EDGE_MULTIPLICITY_LE_1",
            invertible=False,
            total_on_declared_domain=False,
        )
    )
    assert c.is_groupoid_on(["project"]) is False


def test_exact_sector_can_form_local_groupoid_fragment():
    c = MemoryRepresentationCategory(
        [
            obj("phase", "PHASENAV_OUTER"),
            obj("stella", "STELLA_CORNER"),
        ]
    )
    c.add_morphism(
        PartialMorphism(
            "ps",
            "phase",
            "stella",
            "COMPILER",
            "sign_tuple",
            "EXACT",
            0,
            100,
            domain_sector="OUTER_SIGN_SHELL",
            invertible=True,
        )
    )
    c.add_morphism(
        PartialMorphism(
            "sp",
            "stella",
            "phase",
            "COMPILER",
            "sign_tuple",
            "EXACT",
            0,
            100,
            domain_sector="CORNER_SHELL",
            invertible=True,
        )
    )
    assert c.is_groupoid_on(["ps", "sp"]) is True


def test_partial_reconstruction_selects_category_not_groupoid():
    assert (
        classify_global_structure(
            has_lossy_projection=False,
            has_partial_reconstruction=True,
            ternary_closed_under_composition=False,
        )
        == "CATEGORY_OF_PARTIAL_TYPED_MORPHISMS"
    )


def test_nonclosed_ternary_algebra_is_not_promoted_to_group():
    assert (
        classify_global_structure(
            has_lossy_projection=False,
            has_partial_reconstruction=False,
            ternary_closed_under_composition=False,
        )
        == "CATEGORY_WITH_PARTIAL_TERNARY_ALGEBRA"
    )


def test_provenance_failure_blocks_behavioral_admission():
    m = PartialMorphism(
        "x",
        "a",
        "b",
        "COMPILER",
        "route_choice",
        "D",
        0,
        10,
        provenance_preserved=False,
    )
    assert not m.admitted_by(
        BehaviorContract(0, 10, "route_choice", "D")
    )


def test_invariant_failure_blocks_behavioral_admission():
    m = PartialMorphism(
        "x",
        "a",
        "b",
        "COMPILER",
        "route_choice",
        "D",
        0,
        10,
        invariant_preserved=False,
    )
    assert not m.admitted_by(
        BehaviorContract(0, 10, "route_choice", "D")
    )
