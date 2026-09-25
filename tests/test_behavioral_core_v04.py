import pytest

from algebra.behavioral_core_v04 import (
    BehavioralCoreError,
    BehavioralInverseWitness,
    collatz_inverse_witness,
    extract_certified_behavioral_core,
    same_declared_behavior,
    same_history,
    validate_inverse_pair,
)
from algebra.collatz_history_groupoid_v04 import forward_path
from algebra.memory_representation_category_v04 import (
    MemoryRepresentationCategoryV4,
    RepresentationObjectV4,
    TypedMorphismV4,
)


def obj(oid, sector="S"):
    return RepresentationObjectV4(
        oid, "memory:m", "F", "inv", "prov", sector
    )


def morph(
    mid, src, dst, *,
    role="DYNAMIC",
    ssec="S",
    tsec="S",
    err=0,
    invertible=True,
    lineage=None,
):
    if lineage is None:
        return TypedMorphismV4.generator(
            morphism_id=mid,
            source_id=src,
            target_id=dst,
            role=role,
            observable="state",
            distance="EXACT",
            error_bound=err,
            horizon=100,
            source_sector=ssec,
            target_sector=tsec,
            invertible_on_declared_image=invertible,
        )
    return TypedMorphismV4(
        morphism_id=mid,
        source_id=src,
        target_id=dst,
        observable="state",
        distance="EXACT",
        error_bound=err,
        horizon=100,
        source_sector=ssec,
        target_sector=tsec,
        lineage=tuple(lineage),
        invariant_preserved=True,
        provenance_preserved=True,
        invertible_on_declared_image=invertible,
    )


def exact_witness(fid="f", gid="g"):
    return BehavioralInverseWitness(
        "w", fid, gid, "UNIT", "receipt:1", True, True, True
    )


def test_same_declared_behavior_can_have_different_history():
    a=morph("a","x","y",lineage=(1,))
    b=morph("b","x","y",lineage=(2,3))
    assert same_declared_behavior(a,b) is True
    assert same_history(a,b) is False
    assert a.behavioral_signature()==b.behavioral_signature()
    assert a.historical_signature()!=b.historical_signature()


def test_canonical_signature_remains_historical_for_compatibility():
    a=morph("a","x","y",lineage=(1,2))
    assert a.canonical_signature()==a.historical_signature()
    assert a.canonical_signature()!=a.behavioral_signature()


def test_invertible_flag_without_witness_is_excluded_from_certified_core():
    c=MemoryRepresentationCategoryV4([obj("x"),obj("y")])
    c.add_morphism(morph("f","x","y"))
    core=extract_certified_behavioral_core(c,())
    assert "f" not in core.morphism_ids
    assert core.excluded_unwitnessed_invertible_ids==("f",)


def test_exact_inverse_pair_enters_certified_core_with_identities():
    c=MemoryRepresentationCategoryV4([obj("x"),obj("y")])
    c.add_morphism(morph("f","x","y"))
    c.add_morphism(morph("g","y","x"))
    core=extract_certified_behavioral_core(c,(exact_witness(),))
    assert set(core.morphism_ids)=={"id:x","id:y","f","g"}
    assert core.inverse_pairs==(("f","g"),)
    assert core.excluded_unwitnessed_invertible_ids==()


def test_lossy_projection_cannot_enter_core_by_external_witness():
    c=MemoryRepresentationCategoryV4([obj("x"),obj("y")])
    c.add_morphism(morph("f","x","y",role="PROJECTION",invertible=False))
    c.add_morphism(morph("g","y","x"))
    with pytest.raises(BehavioralCoreError):
        extract_certified_behavioral_core(c,(exact_witness(),))


def test_nonzero_error_pair_is_not_exact_core():
    c=MemoryRepresentationCategoryV4([obj("x"),obj("y")])
    c.add_morphism(morph("f","x","y",err="1/100"))
    c.add_morphism(morph("g","y","x",err=0))
    with pytest.raises(BehavioralCoreError):
        validate_inverse_pair(c,exact_witness())


def test_sector_reverse_must_match():
    c=MemoryRepresentationCategoryV4([obj("x","A"),obj("y","B")])
    c.add_morphism(morph("f","x","y",ssec="A",tsec="B"))
    c.add_morphism(morph("g","y","x",ssec="C",tsec="A"))
    with pytest.raises(BehavioralCoreError):
        validate_inverse_pair(c,exact_witness())


def test_collatz_domain_validator_generates_inverse_witness():
    p=forward_path(27,12)
    c=MemoryRepresentationCategoryV4([
        obj(f"odd:{p.start}"),
        obj(f"odd:{p.end}"),
    ])
    f=morph(
        "collatz:f",
        f"odd:{p.start}",
        f"odd:{p.end}",
        ssec="ODD_STATE",
        tsec="ODD_STATE",
    )
    g=morph(
        "collatz:inv",
        f"odd:{p.end}",
        f"odd:{p.start}",
        ssec="ODD_STATE",
        tsec="ODD_STATE",
    )
    c.add_morphism(f); c.add_morphism(g)
    w=collatz_inverse_witness(
        p,
        forward_id="collatz:f",
        inverse_id="collatz:inv",
        validator_receipt="receipt:collatz:v04",
    )
    core=extract_certified_behavioral_core(c,(w,))
    assert {"collatz:f","collatz:inv"}.issubset(core.morphism_ids)


def test_core_keeps_all_object_identities_even_without_nonidentity_arrows():
    c=MemoryRepresentationCategoryV4([obj("a"),obj("b"),obj("c")])
    core=extract_certified_behavioral_core(c,())
    assert core.object_ids==("a","b","c")
    assert set(core.morphism_ids)=={"id:a","id:b","id:c"}


def test_invalid_inverse_witness_boolean_cannot_be_constructed():
    with pytest.raises(BehavioralCoreError):
        BehavioralInverseWitness(
            "w","f","g","V","r",True,False,True
        )
