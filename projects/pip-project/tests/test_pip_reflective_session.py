"""Full source-linked offline entry point, including interrupted commit recovery."""
import importlib.util
import json
import os
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("pip_reflective_session",ROOT/"integrations/pnaml/reflective_session.py")
session=importlib.util.module_from_spec(spec)
spec.loader.exec_module(session)

@pytest.fixture
def profile(tmp_path):
    variant=os.environ.get("PNAML_VARIANT")
    if not variant:
        pytest.skip("Pinned Mobile/Semantic CI required")
    return (tmp_path/"unified.sqlite",os.environ["TCD_ROOT"],variant)

def test_single_entrypoint_restarts_and_continues(profile):
    journal,tcd,variant=profile
    with session.ReflectiveSession(*profile) as a:
        original=[]
        for i in range(4):
            original.append(a.advance(session.demo_command(i)))
        assert [x["semantic"]["arrived"] for x in original]==[False,True,True,True]
        assert [x["semantic"]["route"] for x in original]==["direct"]+["detour"]*3
        assert a.hotel.now==4 and a.episodes==4
        assert a.collatz==4 # 3 -> 5 -> 8 -> 4
        assert a.character==[4,0,4]
        assert original[0]["semantic"]["conclusions"]==[True]*3
        assert original[1]["semantic"]["conclusions"]==[True]*3
        assert original[1]["semantic"]["proof"][-1] is False
        assert a.last["producer_feedback"]["phase_error"]<1e-10
        saved=a.snapshot()
        assert saved["journal"]["events_checked"]==5
        assert a.advance(session.demo_command(3))["status"]=="DUPLICATE"
        assert a.snapshot()==saved
        for row in a._rows():
            body=json.loads(row["summary"])
            assert not any(k in row["summary"] for k in ("phase36_lift","omega36","coupling36","fingerprint_sha256"))
            assert "generation" in body
        # Independent uninterrupted reference after the saved checkpoint.
        expected=a.advance(session.demo_command(4))["semantic"]
        final=a.snapshot()
    with session.ReflectiveSession(*profile) as b:
        assert b.episodes==5
        assert b.snapshot()==final
        assert b.model.gen!=original[0]["source_frame"]["generation"]
        assert b.hotel.lookup(1)["source_frame"]==original[0]["source_frame"]
        assert b.advance(session.demo_command(4))["semantic"]==expected
        assert b.advance(session.demo_command(5))["semantic"]["arrived"]
        assert b.hotel.now==6
        assert b.store.verify()["events_checked"]==7

def test_resume_after_commit_before_hotel_update(profile,monkeypatch):
    with session.ReflectiveSession(*profile) as a:
        original=a._record
        def interrupted(ref,body):
            receipt=original(ref,body)
            raise RuntimeError("simulated process interruption after journal commit")
        monkeypatch.setattr(a,"_record",interrupted)
        with pytest.raises(RuntimeError,match="simulated process interruption"):
            a.advance(session.demo_command(0))
        assert a.failed
        assert a.hotel.now==0
    with session.ReflectiveSession(*profile) as b:
        assert b.episodes==1 and b.hotel.now==1
        assert b.advance(session.demo_command(0))["status"]=="DUPLICATE"
        assert b.advance(session.demo_command(1))["semantic"]["arrived"] is True
        assert b.store.verify()["events_checked"]==3

def test_hold_withdrawal_and_replay(profile):
    with session.ReflectiveSession(*profile) as a:
        initial=a.snapshot()
        for i,status in enumerate((2,3)):
            cmd={**session.demo_command(i),"status":status}
            result=a.advance(cmd)["semantic"]
            assert result["route"] is None and result["arrived"] is False
            assert result["proposal"]==([False,True,False] if status==2 else [False,False,True])
        saved=a.snapshot()
        assert saved["procedure"]==initial["procedure"]
        assert saved["character"]==initial["character"]
        assert saved["collatz"]==initial["collatz"]
        assert saved["hotel"]["index"]==2
    with session.ReflectiveSession(*profile) as b:
        assert b.snapshot()==saved


def test_actual_separate_process_restart(profile,tmp_path):
    import subprocess,sys
    journal,tcd,variant=profile
    def run(db,count):
        command=[sys.executable,str(ROOT/"integrations/pnaml/reflective_session.py"),
                 "--journal",str(db),"--tcd-root",tcd,"--variant",variant,
                 "--episodes",str(count)]
        result=subprocess.run(command,check=True,capture_output=True,text=True,
                              env=os.environ.copy(),timeout=120)
        lines=[json.loads(line) for line in result.stdout.splitlines()]
        return lines[:-1],lines[-1]
    a,one=run(journal,3)
    b,two=run(journal,3)
    all_at_once,whole=run(tmp_path/"reference.sqlite",6)
    assert [x["semantic"] for x in a+b]==[x["semantic"] for x in all_at_once]
    for k in ("episodes","procedure","edge_weight","collatz","character","orbit","theory","next_guide"):
        assert two[k]==whole[k]
    assert two["journal"]["events_checked"]==whole["journal"]["events_checked"]==7
    assert two["hotel"]["index"]==whole["hotel"]["index"]==6
    assert a[0]["source_frame"]["generation"]!=b[0]["source_frame"]["generation"]
    assert "phase36" not in two


def test_fiat_lux_orbit_feedback_dark_ablation_and_restart(profile,tmp_path):
    import numpy as np
    journal,tcd,variant=profile
    with session.ReflectiveSession(journal,tcd,variant,optical_mode="coupled") as a, \
         session.ReflectiveSession(tmp_path/"ablation.sqlite",tcd,variant,optical_mode="ablated") as b:
        ref=session.PREFIX+"light"
        pulse=session.demo_pulse(ref,a.owner.scene["materials"][0]["id"])
        first=a.advance_optical(ref,pulse)
        other=b.advance_optical(ref,pulse)
        assert first["semantic"]==other["semantic"]
        assert first["semantic"]["verified_model_imprint"]
        assert first["semantic"]["fs_distance"]>0
        assert first["semantic"]["energy_shift"]!=0
        assert first["semantic"]["collatz"]==5 and first["semantic"]["tag"]==1
        assert first["semantic"]["source_coupling_increment"]==0
        assert np.array_equal(a.owner.psi,b.owner.psi)
        assert a.advance_optical(ref,pulse)["status"]=="DUPLICATE"
        assert a.optical_steps==1
        for i in range(4):
            dark=session.PREFIX+"dark-"+str(i)
            x=a.advance_optical(dark)["semantic"]
            y=b.advance_optical(dark)["semantic"]
            assert x["response"] is None and not x["verified_model_imprint"]
            assert y["response"] is None and x["collatz"]==y["collatz"]==5
            assert x["source_coupling_increment"]>0
            assert y["source_coupling_increment"]==0
        # Read the original owner's actual published coupling and QHTRI
        # amplitudes, not the requested increment or a surrogate engine.
        ga=np.asarray(a.owner.noema_surface.read("DYNAMIC_STATE_SPACE/g"))
        gb=np.asarray(b.owner.noema_surface.read("DYNAMIC_STATE_SPACE/g"))
        g_gap=float(np.linalg.norm(ga-gb))
        phase_gap=float(np.linalg.norm(np.asarray(a.last["phase36_lift"])-np.asarray(b.last["phase36_lift"])))
        qhtri_gap=float(np.linalg.norm(a.owner.psi-b.owner.psi))
        assert g_gap>1e-10 and phase_gap>1e-10 and qhtri_gap>1e-10
        assert np.max(abs(ga-ga.T))<1e-10
        assert abs(a.last["qhtri"]["norm"]-1)<1e-10
        assert a.last["trits12"] is None
        assert a.last["dynamic_hashing"]=="NONE_IN_THIS_ROUTE"
        saved=a.snapshot()
        psi=a.owner.psi.copy()
        print("FIAT_LUX_DARK_ABLATION",json.dumps({"fs_distance":first["semantic"]["fs_distance"],
              "energy_shift":first["semantic"]["energy_shift"],"coupling_gap":g_gap,
              "phase_gap":phase_gap,"qhtri_gap":qhtri_gap}))
        for row in a._rows():
            assert not any(k in row["summary"] for k in ("phase36_lift","omega36","coupling36",
                    "realized_phase_increment36","requested_phase_increment36","amplitude_real"))
        next_ref=session.PREFIX+"after-restart"
        expected=a.advance_optical(next_ref)["semantic"]
        next_psi=a.owner.psi.copy()
    with session.ReflectiveSession(journal,tcd,variant,optical_mode="coupled") as a:
        assert a.optical_steps==6
        assert a.hotel.now==6 and a.store.verify()["events_checked"]==7
        assert a.advance_optical(next_ref)["semantic"]==expected
        assert np.allclose(a.owner.psi,next_psi,rtol=0,atol=1e-12)
    with session.ReflectiveSession(tmp_path/"dark-only.sqlite",tcd,variant,optical_mode="coupled") as a:
        for i in range(3):
            r=a.advance_optical(session.PREFIX+"unlit-"+str(i))["semantic"]
            assert r["source_coupling_increment"]==r["energy_shift"]==0
            assert r["collatz"]==3
        ref=session.PREFIX+"subthreshold"
        pulse=session.demo_pulse(ref,a.owner.scene["materials"][0]["id"])
        pulse["work_function_ev"]=10.
        r=a.advance_optical(ref,pulse)["semantic"]
        assert r["response"]=="NO_PHOTOELECTRIC_RESPONSE"
        assert r["fs_distance"]==r["energy_shift"]==0
        assert r["tag"] is None and r["collatz"]==3

def test_optical_process_restart_and_route_interleave(profile,tmp_path):
    import subprocess,sys
    journal,tcd,variant=profile
    def run(db,steps):
        args=[sys.executable,str(ROOT/"integrations/pnaml/reflective_session.py"),
              "--journal",str(db),"--tcd-root",tcd,"--variant",variant,
              "--episodes","0","--optical-mode","coupled","--optical-steps",str(steps)]
        p=subprocess.run(args,check=True,capture_output=True,text=True,timeout=120,env=os.environ.copy())
        rows=[json.loads(line) for line in p.stdout.splitlines()]
        return rows[:-1],rows[-1]
    first,x=run(journal,2)
    second,y=run(journal,3)
    whole,z=run(tmp_path/"continuous.sqlite",5)
    assert [r["semantic"] for r in first+second]==[r["semantic"] for r in whole]
    for k in ("orbit","collatz","orbital_energy_shift","source_coupling_increment","optical_steps"):
        assert y[k]==z[k]
    assert first[0]["source_frame"]["generation"]!=second[0]["source_frame"]["generation"]
    assert y["hotel"]["index"]==z["hotel"]["index"]==5
    with session.ReflectiveSession(journal,tcd,variant,optical_mode="coupled") as a:
        assert a.advance(session.demo_command(0))["status"]=="COMMITTED"
        assert a.hotel.now==6 and a.episodes==1 and a.optical_steps==5
        saved=a.snapshot()
    with session.ReflectiveSession(journal,tcd,variant,optical_mode="coupled") as b:
        assert b.snapshot()==saved
