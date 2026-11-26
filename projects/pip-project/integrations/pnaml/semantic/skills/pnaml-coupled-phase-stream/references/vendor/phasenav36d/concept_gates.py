from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .vector_kernel import batch_phase36,circular_distance_matrix
@dataclass(frozen=True)
class GateVerdict:
    status:str; score:float; threshold:float; gate:str; reason:str
SEMANTIC_CLASS={
 'READ':{'read','inspect','list','find','search','validate','hash','diagnose','status'},
 'WRITE':{'write','create','candidate','append','receipt','archive','unarchive','github','repo','repository'},
 'COPY':{'copy','materialize','stage'},
 'VECTORIZE':{'vectorize','phase','36d','batch','embedding'},
 'VCS':{'checkpoint','commit','branch','tag','bundle','diff'},
 'EXECUTE_TYPED':{'execute','run','dispatch','invoke','typed'},
}
THRESHOLD={'READ':2.7,'WRITE':2.7,'COPY':2.7,'VECTORIZE':2.7,'VCS':2.5,'EXECUTE_TYPED':2.6}
def concept_gate(gate,intent):
    g=gate.upper(); text=str(intent).lower(); tokens=set(text.replace('_',' ').split())
    lexical=len(tokens & SEMANTIC_CLASS.get(g,set()))>0
    v=batch_phase36([g,text]); dist=float(circular_distance_matrix(v[:1],v[1:])[0,0])
    t=THRESHOLD.get(g,2.5)
    passed=lexical or dist<=t
    return GateVerdict('PASS' if passed else 'BLOCKED_CONCEPT_GATE',dist,t,g,f'lexical={lexical};phase_distance={dist:.6f}')
