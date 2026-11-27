"""Cross-contract identity seam only; original upstream fixtures and operators."""
from dataclasses import replace
import importlib.util
import math
import os
from pathlib import Path
import sys

import numpy as np
import pytest
from phasenav_natural_code.native_pnv_exec_v01 import execute_pnv
from phasenav_natural_code.orch_orbital_time_v27 import SubjectiveTimeKernel
from phasenav_natural_code.pnlf_orbital_memory_v01 import (
    advance_liminal_segment, admit_liminal_segment, validate_checkpoint_against_header,
    validate_segment_against_header,
)
from phasenav_natural_code.qhtri_pnlf_trajectory_binding_v01 import (
    build_qhtri_pnlf_trajectory_binding, require_segment_trajectory_commitment,
)

ROOT=Path(__file__).resolve().parents[1]

def upstream_fixture():
    root=os.environ.get("PNCS_ROOT")
    if not root:
        pytest.skip("Pinned PNCS source fixture required")
    path=Path(root)/"tests/test_qhtri_pnlf_trajectory_binding_v01.py"
    spec=importlib.util.spec_from_file_location("pip_upstream_pnlf_fixture",path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module

def run(name, sources):
    return execute_pnv((ROOT/"native"/name).read_text(),sources=sources).emitted

def hotel_nodes():
    r=run("PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv",{"now.object":"same"})
    nodes=[r["NOW"]]
    for _ in range(2):
        r=run("PIP_HOTEL_SERIAL_STEP_V0_2.pnv",{
            "now.node":r["INDEX"],"now.winding":r["WINDING"],
            "now.spinor_i_sign":r["SIGN"],"next.object":"same"})
        nodes.append(r["NOW"])
    return nodes

def test_existing_pnlf_paux_hotel_identity_seam():
    if not os.environ.get("PNV_STATE_MEMORY_ROOT"):
        pytest.skip("Pinned State Memory source required")
    from pnv_state_memory import (
        HilbertStateSpace, EventDrivenAUXTether, PAUXExactError,
        bind_phase_checkpoint, reconstruct_phase_checkpoint,
    )
    f=upstream_fixture()
    kernel=SubjectiveTimeKernel()
    left,opened,segment=f.candidate_segment(kernel)
    header=f.header(kernel)
    binding=build_qhtri_pnlf_trajectory_binding(
        header,segment,f.htri_receipts(),f.bindings(kernel))
    rebound=advance_liminal_segment(
        opened,tau_cursor=2.042,trajectory_commitment=f.d("5"),
        t36_trajectory_commitment=binding.commitment)
    right=f.checkpoint(2.042,kernel,predecessor=left.checkpoint_object_id,content="8")
    admitted=admit_liminal_segment(
        rebound,right_checkpoint=right,resolution_witness_sha256=f.d("9"))
    require_segment_trajectory_commitment(binding,admitted)
    validate_segment_against_header(header,admitted)
    assert sum(s["proper_dt"] for s in binding.payload["steps"])==pytest.approx(.042)
    # Same frozen INPUT sample, explicitly not a trajectory endpoint.
    phi=np.asarray(f.snapshot().phi,dtype="<f8")
    raw=phi.tobytes()
    assert len(raw)==288
    h=HilbertStateSpace(36)
    state=h.state(np.exp(1j*phi)/math.sqrt(36),label="phase36")
    tether=EventDrivenAUXTether()
    nodes=hotel_nodes()
    assert [n[2] for n in nodes]==[0,1,2]
    assert nodes[2][0]==1
    selected=[]
    parent=None
    for epoch,(node,pnlf) in enumerate(zip((nodes[0],nodes[2]),(left,right))):
        validate_checkpoint_against_header(header,pnlf)
        meta={"pip_causal_node":node,"pnlf_checkpoint":pnlf.checkpoint_object_id,
              "pnlf_segment":admitted.segment_id,
              "trajectory_commitment":binding.commitment,
              "source":"IMMUTABLE_TEST_INPUT"}
        cp=h.checkpoint(state,parent_id=parent,relation="IDENTITY",metadata=meta)
        b=tether.commit(cp)
        receipt=tether._receipts[b.receipt_hash]
        desc=bind_phase_checkpoint(raw,cp,b.as_dict(),receipt,state_label="phase36")
        restored=reconstruct_phase_checkpoint(raw,desc)
        assert restored==cp and restored["metadata"]==meta
        assert type(restored["metadata"]["pip_causal_node"][2]) is int
        assert b.epoch==epoch
        assert tether.verify_freshness(restored)
        selected.append((cp,b,desc))
        parent=cp["object_id"]
        corrupted=replace(desc,metadata={**meta,"pnlf_checkpoint":"wrong"})
        with pytest.raises(PAUXExactError,match="reconstructed object_id mismatch"):
            reconstruct_phase_checkpoint(raw,corrupted)
    assert selected[0][0]["state_id"]==selected[1][0]["state_id"]
    assert selected[0][0]["object_id"]!=selected[1][0]["object_id"]
    assert selected[1][1].epoch==1 and nodes[2][2]==2 and right.tau==2.042
    fresh=EventDrivenAUXTether()
    for cp,b,desc in selected:
        restored=reconstruct_phase_checkpoint(raw,desc)
        assert fresh.commit(restored)==b
        assert fresh.verify_freshness(restored)
    assert fresh.restore_current()==selected[-1][0]
    assert fresh.continuity(selected[0][0]["object_id"],selected[1][0]["object_id"])
