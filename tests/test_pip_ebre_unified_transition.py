"""One linked PNV transition: no host transfer of intermediate proof/policy values."""
from itertools import product
import pytest
from test_pip_native_e2e import pncs, execute, step

PROGRAM="PIP_EBRE_UNIFIED_TRANSITION_V1_3.pnv"
KEYS=("s","sq","qv","r","rv","vw")

@pytest.mark.parametrize("alternate",[False,True])
@pytest.mark.parametrize("accepted,status",[(0,0),(1,1),(3,1),(3,2),(3,3)])
@pytest.mark.parametrize("edges",[(False,True,True),(True,False,True),(True,True,False)])
def test_linked_transition(pncs,alternate,accepted,status,edges):
    origin=execute(pncs,"PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv",
                   {"now.object":"origin"}).emitted
    flags=(alternate,alternate,True,False,False,True)
    data={"before.ref":"old","after.ref":"new","before.proof_occurrence":"p0",
          "after.proof_occurrence":"p1","revision.ref":"rev","goal.ref":"G",
          "occurrence.ref":"event-1","allocation.accepted":accepted,
          "allocation.rejected":4-accepted,"allocation.history_ref":"fixture",
          "route.status":status,"context.ref":"fixture","state.start":True,
          "state.middle":False,"state.goal":False,"action.code":1,
          "action.ref":"action-1","environment.ref":"env",
          "environment.direct":edges[0],"environment.first":edges[1],
          "environment.second":edges[2],"now.node":origin["NOW"],
          "now.winding":origin["WINDING"],"now.spinor_i_sign":origin["SIGN"]}
    for side,mask in (("before",(True,)*4),("after",(True,False,True,True))):
        data.update({side+".c"+str(i):v for i,v in enumerate(mask)})
        data.update({side+"."+k:v for k,v in zip(KEYS,flags)})
    result=execute(pncs,PROGRAM,data)
    out=result.emitted
    assert out["P0.CERTIFICATE"][-1] is True
    assert out["P1.CERTIFICATE"][-1] is False
    assert out["R.RECHECK"]==[True]*3
    assert out["R.CHANGED"]==[not alternate]*3
    assert out["R.A_STATUS"]==[alternate]*3
    assert out["C.RECORD"][-1] is alternate
    go=status==0 or (status==1 and accepted>=2)
    assert out["C.PROPOSAL"]==[go,not go and status!=3,status==3]
    assert out["E.ATTEMPT"] is go
    assert out["E.BLOCKED"] is (go and not edges[1])
    middle=go and edges[1]
    assert out["E.NEXT"]==[not middle,middle,False]
    assert out["H.NOW"]==step(pncs,origin,"event-1")["NOW"]
    assert out["SELECTED_EVENT"][0]=="event-1"
    # A second selected occurrence consumes the actual first output.
    next_data={**data,"now.node":out["H.NOW"],"now.winding":out["H.INDEX"],
               "now.spinor_i_sign":out["H.SIGN"],"occurrence.ref":"event-2",
               "action.ref":"action-2","action.code":2,
               **dict(zip(("state.start","state.middle","state.goal"),out["E.NEXT"]))}
    next_out=execute(pncs,PROGRAM,next_data).emitted
    assert next_out["E.NG"] is (middle and edges[2])
    assert next_out["H.HOTEL"]==out["H.NOW"] and next_out["H.INDEX"]==2
