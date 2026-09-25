import pytest

from algebra.memory_representation_category_v04 import (
    MemoryRepresentationCategoryV4,
    MetricCompositionWitness,
    RepresentationCategoryV4Error,
    RepresentationObjectV4,
    SectorCompatibilityWitness,
    TypedMorphismV4,
    compose_v4,
    dissociate_lineage,
    identity_for,
)


def obj(oid, sector="GENERAL"):
    return RepresentationObjectV4(oid, "memory:m", "F", "inv", "prov", sector)


def gen(mid, src, dst, role, *, err=0.01, horizon=100, ssec="A", tsec="B", distance="D", invertible=False):
    return TypedMorphismV4.generator(
        morphism_id=mid,
        source_id=src,
        target_id=dst,
        role=role,
        observable="route_choice",
        distance=distance,
        error_bound=err,
        horizon=horizon,
        source_sector=ssec,
        target_sector=tsec,
        invertible_on_declared_image=invertible,
    )


def metric():
    return MetricCompositionWitness("metric:D:triangle", "D", True)


def test_identity_left_and_right_preserve_signature():
    a=obj("a","A"); b=obj("b","B")
    f=gen("f","a","b","COMPILER",ssec="A",tsec="B")
    left=compose_v4(identity_for(a),f,composed_id="left")
    right=compose_v4(f,identity_for(b),composed_id="right")
    assert left.canonical_signature()==f.canonical_signature()
    assert right.canonical_signature()==f.canonical_signature()


def test_nonidentity_composition_requires_metric_triangle_witness():
    f=gen("f","a","b","COMPILER",ssec="A",tsec="B")
    g=gen("g","b","c","PROJECTION",ssec="B",tsec="C")
    with pytest.raises(RepresentationCategoryV4Error):
        compose_v4(f,g,composed_id="fg")


def test_metric_witness_distance_must_match():
    f=gen("f","a","b","COMPILER",ssec="A",tsec="B")
    g=gen("g","b","c","PROJECTION",ssec="B",tsec="C")
    bad=MetricCompositionWitness("bad","OTHER",True)
    with pytest.raises(RepresentationCategoryV4Error):
        compose_v4(f,g,composed_id="fg",metric_witness=bad)


def test_sector_mismatch_fails_without_explicit_witness():
    f=gen("f","a","b","COMPILER",ssec="A",tsec="B1")
    g=gen("g","b","c","PROJECTION",ssec="B2",tsec="C")
    with pytest.raises(RepresentationCategoryV4Error):
        compose_v4(f,g,composed_id="fg",metric_witness=metric())


def test_sector_witness_admits_declared_partial_interface():
    f=gen("f","a","b","COMPILER",ssec="A",tsec="B1")
    g=gen("g","b","c","PROJECTION",ssec="B2",tsec="C")
    sw=SectorCompatibilityWitness("sector:B1->B2","B1","B2","RESTRICTION",True)
    h=compose_v4(f,g,composed_id="fg",metric_witness=metric(),sector_witness=sw)
    assert h.source_sector=="A" and h.target_sector=="C"
    assert h.sector_witness_ids[-1]=="sector:B1->B2"


def test_sector_witness_endpoints_must_match():
    f=gen("f","a","b","COMPILER",ssec="A",tsec="B1")
    g=gen("g","b","c","PROJECTION",ssec="B2",tsec="C")
    bad=SectorCompatibilityWitness("bad","X","Y","RESTRICTION",True)
    with pytest.raises(RepresentationCategoryV4Error):
        compose_v4(f,g,composed_id="fg",metric_witness=metric(),sector_witness=bad)


def test_associativity_with_exact_sector_interfaces():
    f=gen("f","a","b","COMPILER",err=0.01,horizon=100,ssec="A",tsec="B")
    g=gen("g","b","c","EMBEDDING",err=0.02,horizon=90,ssec="B",tsec="C")
    h=gen("h","c","d","OBSERVABLE",err=0.03,horizon=80,ssec="C",tsec="D")
    fg=compose_v4(f,g,composed_id="fg",metric_witness=metric())
    left=compose_v4(fg,h,composed_id="left",metric_witness=metric())
    gh=compose_v4(g,h,composed_id="gh",metric_witness=metric())
    right=compose_v4(f,gh,composed_id="right",metric_witness=metric())
    assert left.canonical_signature()==right.canonical_signature()
    assert left.error_bound==pytest.approx(0.06)
    assert left.horizon==80


def test_prime_lineage_association_preserves_order():
    f=gen("f","a","b","COMPILER",ssec="A",tsec="B")
    g=gen("g","b","c","PROJECTION",ssec="B",tsec="C")
    fg=compose_v4(f,g,composed_id="fg",metric_witness=metric())
    gf_lineage=(g.lineage+f.lineage)
    assert fg.lineage==f.lineage+g.lineage
    assert fg.lineage!=gf_lineage


def test_lineage_dissociation_recovers_component_role_words():
    f=gen("f","a","b","COMPILER",ssec="A",tsec="B")
    g=gen("g","b","c","PROJECTION",ssec="B",tsec="C")
    fg=compose_v4(f,g,composed_id="fg",metric_witness=metric())
    left,right=dissociate_lineage(fg,len(f.lineage))
    assert left==f.lineage
    assert right==g.lineage


def test_error_and_horizon_composition_are_parenthesization_independent():
    f=gen("f","a","b","COMPILER",err=0.1,horizon=100,ssec="A",tsec="B")
    g=gen("g","b","c","EMBEDDING",err=0.2,horizon=70,ssec="B",tsec="C")
    h=gen("h","c","d","OBSERVABLE",err=0.3,horizon=90,ssec="C",tsec="D")
    left=compose_v4(compose_v4(f,g,composed_id="fg",metric_witness=metric()),h,composed_id="left",metric_witness=metric())
    right=compose_v4(f,compose_v4(g,h,composed_id="gh",metric_witness=metric()),composed_id="right",metric_witness=metric())
    assert left.error_bound==pytest.approx(right.error_bound)
    assert left.horizon==right.horizon==70


def test_invertibility_is_not_created_by_composition():
    f=gen("f","a","b","DYNAMIC",ssec="A",tsec="B",invertible=True)
    g=gen("g","b","c","PROJECTION",ssec="B",tsec="C",invertible=False)
    fg=compose_v4(f,g,composed_id="fg",metric_witness=metric())
    assert fg.invertible_on_declared_image is False


def test_history_preserving_local_fragment_can_remain_invertible():
    f=gen("f","a","b","DYNAMIC",ssec="A",tsec="B",invertible=True)
    g=gen("g","b","c","DYNAMIC",ssec="B",tsec="C",invertible=True)
    fg=compose_v4(f,g,composed_id="fg",metric_witness=metric())
    assert fg.invertible_on_declared_image is True


def test_category_registry_refuses_cross_memory_arrow():
    a=obj("a")
    b=RepresentationObjectV4("b","memory:other","F","inv","prov")
    c=MemoryRepresentationCategoryV4([a,b])
    f=gen("f","a","b","COMPILER",ssec="A",tsec="B")
    with pytest.raises(RepresentationCategoryV4Error):
        c.add_morphism(f)


def test_invalid_metric_witness_cannot_be_constructed():
    with pytest.raises(RepresentationCategoryV4Error):
        MetricCompositionWitness("w","D",False)


def test_invalid_sector_witness_cannot_be_constructed():
    with pytest.raises(RepresentationCategoryV4Error):
        SectorCompatibilityWitness("w","A","B","UNKNOWN",False)
