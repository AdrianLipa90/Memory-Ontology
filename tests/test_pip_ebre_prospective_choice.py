"""Finite prospective policy using original PNV, no new runtime."""
from itertools import product
import pytest
from test_pip_native_e2e import pncs, execute, step
from test_pip_ebre_unified import proof

PROGRAM="PIP_EBRE_PROSPECTIVE_CHOICE_V1_2.pnv"

def choose(pncs,a,status,proved,ref="choice"):
    return execute(pncs,PROGRAM,{
        "goal.ref":"recheck","occurrence.ref":ref,
        "allocation.accepted":a,"allocation.rejected":4-a,
        "allocation.history_ref":"history-"+str(a),"route.status":status,
        "inference.proved":proved,"context.ref":"fixed"}).emitted

@pytest.mark.parametrize("a,status",list(product(range(5),range(4))))
def test_exact_prospective_policy(pncs,a,status):
    good=proof(pncs,(True,)*4)["PROVED"]
    bad=proof(pncs,(True,False,True,True))["PROVED"]
    x,y=choose(pncs,a,status,good),choose(pncs,a,status,bad)
    go=status==0 or (status==1 and a>=2)
    assert x["PROPOSAL"]==y["PROPOSAL"]==[go,not go and status!=3,status==3]
    assert x["D"]==[a+1,6] and x["WILL"]==2
    assert x["SACRIFICE"]==[2*(a+1),6]
    assert x["RECORD"][-1] is True and y["RECORD"][-1] is False
    assert x["WITNESS"][0] is True

def test_history_intervention_and_character(pncs):
    def arm(votes):
        hotel=execute(pncs,"PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv",
                      {"now.object":"origin"}).emitted
        counts=[0,0,0]
        prev=None
        for j,vote in enumerate(votes):
            ref="allocation-"+str(j)
            hotel=step(pncs,hotel,ref)
            out=execute(pncs,"PIP_CHARACTER_DEPOSIT_STEP_V0_1.pnv",{
                "deposit.owner":"Pip","deposit.query_domain":"comparable-allocation",
                "deposit.candidate_labels":["GO","HOLD"],"deposit.label_a":"GO","deposit.label_b":"HOLD",
                "deposit.count_a":counts[0],"deposit.count_b":counts[1],"deposit.count":counts[2],
                "deposit.previous_observation_ref":prev,"observation.ref":ref,
                "observation.owner":"Pip","observation.query_domain":"comparable-allocation",
                "observation.candidate_labels":["GO","HOLD"],"observation.choice":"GO" if vote else "HOLD",
                "observation.vote_a":int(vote),"observation.vote_b":int(not vote),
                "observation.hotel_occurrence":hotel["INDEX"]}).emitted
            assert all(out["WITNESS"])
            counts=out["CHECKPOINT"][3:6]
            prev=ref
        assert counts==[sum(votes),4-sum(votes),4]
        assert out["CHARACTER"]==[[counts[0],4],[counts[1],4]]
        data=choose(pncs,counts[0],1,True)
        selected=step(pncs,hotel,"policy-proposal")
        assert selected["HOTEL"]==hotel["NOW"]
        return data,selected
    low,h1=arm([True,False,False,False])
    high,h2=arm([True,True,True,False])
    assert low["PROPOSAL"]==[False,True,False]
    assert high["PROPOSAL"]==[True,False,False]
    assert h1["INDEX"]==h2["INDEX"]==5
    assert h1["NOW"][5]==h2["NOW"][5]=="policy-proposal"
