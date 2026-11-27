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
