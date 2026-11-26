import os
import sys
from pathlib import Path
import math
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from affective_hair import project_hair, PALETTE, FIELD_IDS
from consciousness_dictionary.rifc import AffectiveField
from consciousness_dictionary.affect_detection import affect_phase36
from consciousness_dictionary.registry import Lexicon

@pytest.fixture(scope="module")
def lexicon():
    return Lexicon.load(Path(os.environ["TCD_ROOT"]) / "ontology/registry/v0_2")

def field():
    return AffectiveField(.6,.2,.1,.1,.4,.7)

def test_imports_and_source_palette(lexicon):
    assert [lexicon.get(p[3]).canonical_name for p in PALETTE] == [
        "Affect","Fear","Anger","Joy","Calm","Sadness"]
    assert len(FIELD_IDS)==10
    for label,color,_,tid,relation in PALETTE:
        r=project_hair("Pip",field(),{label:1},lexicon,source_ref="explicit fixture")
        assert r["strands"][0]["colour"]==color
        assert r["strands"][0]["share"]==1
        assert r["strands"][0]["relation"]==relation
        assert r["field"]==field()
        assert r["phase36"]==affect_phase36(field())
        assert len(r["phase36"])==36

def test_mix_and_independent_identities(lexicon):
    a=project_hair("Pip",field(),{"curiosity":1,"fear":1},lexicon,source_ref="Pip report")
    b=project_hair("Ciel",field(),{"happiness":2,"calm":1},lexicon,source_ref="Ciel report")
    assert a["identity"]!=b["identity"]
    assert [x["share"] for x in a["strands"]]==[.5,.5]
    assert [x["colour"] for x in b["strands"]]==["gold","green"]
    assert math.isclose(sum(x["share"] for x in b["strands"]),1)
    assert a["phase36"]==b["phase36"] # field alone cannot identify discrete affect

@pytest.mark.parametrize("weights",[{},{"calm":0}])
def test_missing_not_neutral(lexicon,weights):
    r=project_hair("Pip",field(),weights,lexicon,source_ref="fixture")
    assert r["status"]=="UNSPECIFIED" and r["strands"]==()

@pytest.mark.parametrize("weights",[{"fear":-1},{"fear":float("nan")},{"fear":True},{"surprise":1}])
def test_bad_weight(lexicon,weights):
    with pytest.raises(ValueError):
        project_hair("Pip",field(),weights,lexicon,source_ref="fixture")

def test_field_domain_and_provenance(lexicon):
    with pytest.raises(ValueError):
        project_hair("Pip",AffectiveField(2,0,0,0,0,0),{},lexicon,source_ref="fixture")
    with pytest.raises(ValueError):
        project_hair("Pip",field(),{},lexicon,source_ref="")

def test_large_finite_intensities(lexicon):
    r=project_hair("Pip",field(),{"fear":1e308,"calm":1e308},lexicon,source_ref="fixture")
    assert [x["share"] for x in r["strands"]]==[.5,.5]
