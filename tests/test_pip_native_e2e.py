"""Execute the existing Pip PNV/1 source through the original PNCS interpreter.
Host-side assertions are test observations only; they are not new runtime semantics.
"""
import importlib.util
import os
from pathlib import Path
import sys

import pytest

NATIVE = Path(__file__).resolve().parents[1] / "projects" / "pip-project" / "native"


@pytest.fixture(scope="module")
def pncs():
    path = os.environ.get("PNCS_NATIVE_EXEC_PATH")
    if not path:
        if os.environ.get("CI"):
            pytest.fail("PNCS_NATIVE_EXEC_PATH required for CI")
        pytest.skip("Set PNCS_NATIVE_EXEC_PATH to the original PNCS interpreter")
    spec = importlib.util.spec_from_file_location("pip_pncs_reference", path)
    if spec is None or spec.loader is None:
        pytest.fail("Cannot load the PNCS interpreter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def execute(pncs, name, sources):
    return pncs.execute_pnv((NATIVE / name).read_text(encoding="utf-8"), sources=sources)


def step(pncs, before, obj):
    return execute(pncs, "PIP_HOTEL_SERIAL_STEP_V0_2.pnv", {
        "now.node": before["NOW"],
        "now.winding": before["WINDING"],
        "now.spinor_i_sign": before["SIGN"],
        "next.object": obj,
    }).emitted


def observation(before, after):
    return {
        "observation.hotel": after["HOTEL"],
        "observation.previous_now": before["NOW"],
        "observation.index": after["INDEX"],
        "observation.winding": after["WINDING"],
        "observation.previous_index": before["INDEX"],
        "observation.sign": after["SIGN"],
        "observation.previous_sign": before["SIGN"],
        "observation.theta": after["THETA"],
        "observation.previous_theta": before["THETA"],
    }


def assert_step(pncs, before, after, n, obj):
    assert after["HOTEL"] == before["NOW"]
    assert after["INDEX"] == after["WINDING"] == n
    assert after["SIGN"] == (-1)**(n % 2)
    assert after["THETA"] == 2*n
    assert all(type(after[key]) is int for key in ("INDEX", "WINDING", "SIGN", "THETA"))
    assert after["NOW"] == [before["NOW"], n, n, (-1)**(n % 2), 2*n, obj]
    witness = execute(pncs, "PIP_HOTEL_INDEX_WITNESS_V0_2.pnv", observation(before, after))
    assert len(witness.emitted) == 6
    assert all(value is True for value in witness.emitted.values())


@pytest.mark.parametrize("length", [64, 256])
def test_origin_serial_history_and_reverse_navigation(pncs, length):
    current = execute(pncs, "PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv",
                      {"now.object": "origin"}).emitted
    assert current == {"HOTEL": None, "NOW": [None, None, 0, 1, 0, "origin"],
                       "INDEX": 0, "WINDING": 0, "SIGN": 1, "THETA": 0}
    for n in range(1, length + 1):
        # Repeated objects must still receive distinct occurrence addresses.
        obj = "A" if n % 2 else "B"
        previous, current = current, step(pncs, current, obj)
        assert_step(pncs, previous, current, n, obj)
    # Verify the occupied past through its existing parent chain, without
    # constructing a second guest book or a new operational index.
    node = current["HOTEL"]
    for n in range(length - 1, -1, -1):
        assert node[2] == n
        assert node[3] == (-1)**(n % 2)
        assert node[4] == 2*n
        assert node[5] == ("origin" if n == 0 else ("A" if n % 2 else "B"))
        node = node[0]
    assert node is None


@pytest.mark.parametrize("n", [2**53-2, 2**53-1, 2**53, 2**53+1, 2**63, 10**100, 10**400])
def test_exact_winding_in_actual_native_programs(pncs, n):
    # A synthetic boundary fixture, not a claim that n prior rooms exist.
    current = {"NOW": [None, n, n, (-1)**(n % 2), 2*n, "seed"],
               "HOTEL": None, "INDEX": n, "WINDING": n,
               "SIGN": (-1)**(n % 2), "THETA": 2*n}
    addresses = []
    for offset in range(1, 4):
        previous, current = current, step(pncs, current, "repeat")
        assert_step(pncs, previous, current, n+offset, "repeat")
        addresses.append(current["INDEX"])
    assert len(set(addresses)) == 3


@pytest.mark.parametrize("field", ["hotel", "index", "winding", "sign", "theta"])
def test_native_witness_detects_corrupted_observation(pncs, field):
    before = execute(pncs, "PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv", {"now.object": "A"}).emitted
    after = step(pncs, before, "B")
    data = observation(before, after)
    key = "observation." + field
    data[key] = None if field == "hotel" else data[key] + 1
    with pytest.raises(pncs.NativePNVAssertionError):
        execute(pncs, "PIP_HOTEL_INDEX_WITNESS_V0_2.pnv", data)
