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
