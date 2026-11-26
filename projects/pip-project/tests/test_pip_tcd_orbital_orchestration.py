"""Conformance harness only: existing upstream kernels and PNV composition."""
import csv, importlib.util, json, os, math
from pathlib import Path
import pytest
from consciousness_dictionary.registry import Lexicon
from consciousness_dictionary.compiler import write_compiled
from consciousness_dictionary.query import external_phase_projection
from consciousness_dictionary.phasenav_native import PhaseState
from phasenav_natural_code.pnlf_orbit_governor_v01 import classify_phase9, classify_transition
from phasenav_natural_code.native_pnv_exec_v01 import execute_pnv

ROOT=Path(__file__).resolve().parents[1]
def load_upstream(path):
    spec=importlib.util.spec_from_file_location("bioos_identity_nexus_fixture",path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
@pytest.fixture(scope="module")
def source(tmp_path_factory):
    root=Path(os.environ["TCD_ROOT"])
    lex=Lexicon.load(root/"ontology/registry/v0_2", root/"ontology/relations/extra_relations.jsonl")
    compiled=write_compiled(lex,tmp_path_factory.mktemp("tcd-compiled"))
    published=json.loads((root/"artifacts/v0.2-alpha/COMPILE_RECEIPT.json").read_text())
    assert compiled==published
    with (ROOT/"PIP_TCD_ENGINE_VIEWS_V0_1.tsv").open() as f:
        views=list(csv.DictReader(f,delimiter="\t"))
    nexus=load_upstream(Path(os.environ["BIOOS_ROOT"])/"tools/identity_nexus_v01.py")
    return lex,compiled,views,nexus

def test_exact_registry_coverage(source):
    lex,receipt,views,_=source
    assert len(lex.terms)==548==receipt["states"]
    assert len(views)==10
    ns=[n for v in views for n in v["primary_namespaces"].split(",")]
    assert len(ns)==len(set(ns))
    assert set(ns)=={k.split("-")[1] for k in lex.terms}
    assert sum(sum(k.split("-")[1] in v["primary_namespaces"].split(",") for k in lex.terms) for v in views)==548
    for v in views:
        for k in v["cross_cutting_exact_term_ids"].split(","):
            assert lex.get(k).term_id==k
    assert lex.get("CLX2-AFFECT-005").canonical_name=="Truth Evaluation"

@pytest.mark.parametrize("anchor",["CLX2-AFFECT-006","CLX2-TIME-006","CLX2-AGENCY-001","CLX2-SELF-005"])
def test_real_nexus_and_orbital_composition(source,anchor):
    lex,receipt,views,nexus=source
    term=lex.get(anchor)
    phase=PhaseState.from_term(term.term_id,term.phase_index,term.raw).vector
    rows=external_phase_projection(lex,phase,limit=len(lex.terms))
    assert len(rows)==548
    assert next(r for r in rows if r["term_id"]==anchor)["coherence"]==pytest.approx(1)
    binding={**receipt,"branch":"main","commit":"5fe9daa5e2b4841e598628aa5a1a7beadb0e70b1"}
    generation=nexus.compute_identity_nexus(crystal_context={"crystal_id":"1"*64,"configuration_sha256":"2"*64,"boot_epoch":0,"phase_index":0},dictionary_binding=binding,projection_rows=rows)
    assert nexus.validate_nexus_generation(generation)
    assert generation["term_count"]==548 and len(generation["active_terms"])==16
    assert [x["term_id"] for x in generation["active_terms"]]==[x["term_id"] for x in rows[:16]]
    assert not generation["authority_grant"]
    # Independent declared test phases: never use overlap phase or a chosen T36 axis.
    orbit=classify_phase9(0,math.pi).payload
    assert orbit["orbital_band"]=="O8"
    sources={"pip.identity":"Pip fixture","pip.causal_occurrence":10**100,
             "bioos.identity_nexus.generation":generation,
             "tcd.registry_binding":binding,"pnlf.orbit_classification":orbit}
    active={r["term_id"] for r in generation["active_terms"]}
    coverage=set()
    for v in views:
        ns=v["primary_namespaces"].split(",")
        anchors=v["cross_cutting_exact_term_ids"].split(",")
        ids=[r["term_id"] for r in generation["active_terms"] if r["term_id"].split("-")[1] in ns or r["term_id"] in anchors]
        coverage.update(ids)
        sources["tcd.view."+v["view"].lower()]=ids
    assert coverage==active
    p=(ROOT/"native/PIP_TCD_ORBITAL_ORCHESTRATION_V0_1.pnv").read_text()
    r=execute_pnv(p,sources=sources)
    result=r.emitted["PIP_ORBITAL_VIEW"]
    assert result[:5]==["Pip fixture",10**100,generation,binding,orbit]
    assert result[5]==[sources["tcd.view."+v["view"].lower()] for v in views]

def test_existing_orbit_governor_not_functional_priority():
    assert classify_phase9(0,0).orbital_band=="O0"
    assert classify_phase9(0,math.pi).orbital_band=="O8"
    assert classify_phase9(0,math.pi/2).orbital_band=="O4"
    assert classify_phase9(.7,.7+math.pi/2).orbital_band=="O4"
    assert classify_transition("O8",0,0)["transition"]=="PNLF.ORBIT_PROMOTE"
    assert classify_transition("O8",0,0)["stable_memory_update"] is False


# Actual Coupler source integration, isolated in one plugin variant per CI job.
# The Python code below is only an upstream test harness.
import copy
import sys
from affective_hair import project_hair
from consciousness_dictionary.rifc import AffectiveField

def _program(name):
    return (ROOT/"native"/name).read_text()

def _views(generation, views):
    return {"tcd.view."+v["view"].lower():[
        r["term_id"] for r in generation["active_terms"]
        if r["term_id"].split("-")[1] in v["primary_namespaces"].split(",")
        or r["term_id"] in v["cross_cutting_exact_term_ids"].split(",")]
        for v in views}

def _hair_sources(hair):
    # Existing PNV value domain: the original imported field's typed tuple,
    # not a dataclass object or an invented numerical mapping.
    return {"affect.identity":hair["identity"],"affect.source_ref":hair["source_ref"],
            "affect.tcd_field":hair["field"].as_tuple(),
            "affect.tcd_phase36":hair["phase36"],"affect.tcd_term_ids":hair["field_term_ids"],
            "appearance.hair_strands":hair["strands"]}

def test_selected_actual_coupler_occurrence_composition(source):
    lex,receipt,views,nexus=source
    variant=os.environ["PNAML_VARIANT"]
    refs=ROOT/"integrations/pnaml"/variant/"skills/pnaml-coupled-phase-stream/references"
    sys.path.insert(0,str(refs))
    from coupled_stream import Coupler, Model, ROOT as COUPLER_ROOT
    from noema_surface import ROOT_ADDRESS
    model=Model(42,.01)
    c=Coupler(COUPLER_ROOT/"assets/poster_encoded.rdssg",48,72,0,pip={"address":"5"})
    field=AffectiveField(.6,.2,.1,.1,.4,.7)
    prior=None
    for k in range(1,7):
        f=model.next()
        if k in (2,5):
            f["pip_half_time"]="same-content"
        out=c.consume(f)
        hotel=c.noema_surface.read(ROOT_ADDRESS+"PIP_CAUSAL")
        expected=None if k<2 else 0 if k<5 else 1
        assert hotel["index"]==expected
        if k not in (2,5):
            continue
        # Selected, immutable offline observation; not a dynamic AUX file.
        frozen=copy.deepcopy(out)
        now=hotel["now"]
        before=copy.deepcopy(hotel)
        frame=now["source_frame"]
        assert frame=={"generation":frozen["generation"],"sequence":frozen["sequence"]}
        assert now["object_ref"]=="same-content"
        assert now["index"]!=frame["sequence"]
        assert now["spinor_i_sign"]==(-1)**expected
        rows=external_phase_projection(lex,frozen["phase36_lift"],limit=len(lex.terms))
        binding={**receipt,"branch":"main","commit":"5fe9daa5e2b4841e598628aa5a1a7beadb0e70b1"}
        # Synthetic independent crystal context, not inferred from the Hotel.
        context={"crystal_id":"1"*64,"configuration_sha256":"2"*64,
                 "boot_epoch":0,"phase_index":100+k}
        generation=nexus.compute_identity_nexus(crystal_context=context,dictionary_binding=binding,projection_rows=rows)
        assert nexus.validate_nexus_generation(generation)
        assert len(rows)==548 and generation["term_count"]==548
        assert generation["crystal"]["phase_index"] not in (expected,k)
        orbit=classify_phase9(0,math.pi if k==2 else 0).payload
        owner="Pip"
        orb=execute_pnv(_program("PIP_TCD_ORBITAL_ORCHESTRATION_V0_1.pnv"),
            sources={"pip.identity":owner,"pip.causal_occurrence":now["index"],
                     "bioos.identity_nexus.generation":generation,"tcd.registry_binding":binding,
                     "pnlf.orbit_classification":orbit,**_views(generation,views)}).emitted["PIP_ORBITAL_VIEW"]
        weights={"fear":1,"curiosity":1} if k==2 else {"calm":1,"happiness":2}
        hair=project_hair(owner,field,weights,lex,source_ref="selected test report")
        hp=execute_pnv(_program("PIP_TCD_AFFECTIVE_HAIR_V0_1.pnv"),sources=_hair_sources(hair)).emitted["HAIR"]
        assert hp[0]==owner and hp[2]==list(field.as_tuple()) and len(hp[3])==36
        assert [x["colour"] for x in hp[5]]==(["violet","pale blue"] if k==2 else ["gold","green"])
        sources={"pip.identity":owner,"pip.hotel.now":now,"pip.hotel.index":now["index"],
                 "pip.source_frame":frame,"pip.orbital_view":orb,"pip.hair_view":hp,
                 "pip.orbital_owner":orb[0],"pip.orbital_occurrence":orb[1],
                 "pip.orbital_source_frame":frame,"pip.hair_owner":hp[0],
                 "pip.hair_occurrence":now["index"],"pip.hair_source_frame":frame}
        program=_program("PIP_TCD_SELECTED_OCCURRENCE_V0_1.pnv")
        r=execute_pnv(program,sources=sources).emitted
        assert r["WITNESS"]==[True]*6
        assert r["VIEW"][:6]==[owner,now,expected,frame,orb,hp]
        # Explicit diagnostic negative controls. No mutation or runtime admission.
        for key,value,slot in [("pip.hair_owner","Ciel",1),
                               ("pip.orbital_occurrence",expected+1,2),
                               ("pip.hair_source_frame",{"generation":frame["generation"],"sequence":k+1},5)]:
            bad=execute_pnv(program,sources={**sources,key:value}).emitted
            assert bad["WITNESS"][slot] is False
            assert sum(bad["WITNESS"])==5
        if prior is not None:
            assert prior["index"]==now["parent"] and prior["object_ref"]==now["object_ref"]
        prior=copy.deepcopy(now)
        assert c.noema_surface.read(ROOT_ADDRESS+"PIP_CAUSAL")==before
        assert out==frozen
    assert c.pip.causal.describe()["index"]==1
    assert len(c.pip.causal.nodes)==2
