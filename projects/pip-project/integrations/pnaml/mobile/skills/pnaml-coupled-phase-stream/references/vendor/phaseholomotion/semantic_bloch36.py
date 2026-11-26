"""36-mode PhaseNav semantic geometry and an explicitly lossy Bloch-ball projection.

Research formalism: Adrian Lipa (RDSS/PNAML/PhaseNav/PhaseHoloMotion).
Reference implementation. A 36D complex state remains primary; the Bloch view
is a measurement/projection, NOT a faithful representation of the full state.
"""
from __future__ import annotations
from dataclasses import dataclass
import json, math, cmath, hashlib
from pathlib import Path
from typing import Sequence

DIM = 36
PAIRS = 18
TAU = 2 * math.pi
KAPPA = math.log(2) / (24 * math.pi)
ZETA0 = abs(1j)**2 / 2
SIGMA = abs(1j)**2 / math.log(2)
HOLD_BRANCHES = ('-i', '+i')
M61 = 2**61 - 1

def check_phase36(x: Sequence[float]) -> tuple[float, ...]:
    if len(x) != DIM:
        raise ValueError('Expected exactly 36 phases')
    v = tuple(float(t) for t in x)
    if not all(math.isfinite(t) for t in v):
        raise ValueError('Non-finite phase')
    return v

def collatz_hash(token: str) -> int:
    h = int.from_bytes(token.encode('utf-8'), 'big') % M61
    for _ in range(13):
        h = h // 2 if h % 2 == 0 else 3*h + 1
        h %= M61
    return h

def sentence_phase(text: str) -> tuple[float, ...]:
    """Port of Consciousness Dictionary phasenav_native.sentence_phase.
    Preserve text.lower().split() and Collatz hashing; not a language model embedding.
    """
    words = str(text).lower().split()
    if not words:
        words = ['relation']
    ss = [0.0] * DIM
    cc = [0.0] * DIM
    for word in words:
        h = collatz_hash(word)
        for i in range(DIM):
            phi = (h * KAPPA * TAU * (i + 1)) % TAU
            ss[i] += math.sin(phi)
            cc[i] += math.cos(phi)
    n = len(words)
    return tuple(math.atan2(ss[i] / n, cc[i] / n) % TAU for i in range(DIM))

def semantic_text(node: dict) -> str:
    """A clearly declared scene adapter, not canonical term payload."""
    return ' | '.join([str(node.get('label','')), str(node.get('definition','')),
                       ' '.join(sorted(map(str, node.get('members',[]))))])

def phases(node: dict) -> tuple[float, ...]:
    if node.get('phase36') is not None:
        return check_phase36(node['phase36'])
    return sentence_phase(semantic_text(node))

def ket36(v: Sequence[float]) -> tuple[complex, ...]:
    return tuple(cmath.exp(1j*p) / math.sqrt(DIM) for p in check_phase36(v))

def overlap(a: Sequence[float], b: Sequence[float]) -> complex:
    aa = ket36(a)
    bb = ket36(b)
    return sum(x.conjugate() * y for x, y in zip(aa, bb))

def circular_delta(a: float, b: float) -> float:
    return (b - a + math.pi) % TAU - math.pi

def relation(a: Sequence[float], b: Sequence[float]) -> dict:
    a = check_phase36(a)
    b = check_phase36(b)
    z = overlap(a, b)
    R = min(1., max(0., abs(z)**2))
    d = math.sqrt(sum(circular_delta(u,v)**2 for u,v in zip(a,b)) / DIM)
    return {'complex_overlap': [z.real,z.imag], 'coherence':R,
            'relative_phase':cmath.phase(z), 'angular_distance36':d,
            'information_action':-KAPPA * math.log(R + 1e-12)}

def _rot(v: tuple[float,float,float], k: int) -> tuple[float,float,float]:
    """Fixed, published pair-basis rotation: Rz(2πk/18) Ry(θ_k)."""
    theta = .65*math.sin(TAU*k/18) + .25*math.cos(TAU*k/9)
    gamma = TAU*k/18
    x,y,z = v
    a = math.cos(theta)*x + math.sin(theta)*z
    return (math.cos(gamma)*a - math.sin(gamma)*y,
            math.sin(gamma)*a + math.cos(gamma)*y,
            -math.sin(theta)*x + math.cos(theta)*z)

def bloch36_projection(v: Sequence[float]) -> dict:
    """Trace out 18 pair indices after fixed per-pair measurement frames.
    Every one of 36 complex modes contributes. Projected point is inside a
    Bloch BALL in general (mixed reduced state); shell is reference only.
    """
    psi = ket36(v)
    XYZ = [0.,0.,0.]
    components = []
    for k in range(PAIRS):
        a,b = psi[2*k], psi[2*k+1]
        wt = abs(a)**2 + abs(b)**2
        # convention: rho_01 = a * conjugate(b), y = -2 Im(rho_01)
        local = (2*(a*b.conjugate()).real/wt,
                 -2*(a*b.conjugate()).imag/wt,
                 (abs(a)**2-abs(b)**2)/wt)
        p = _rot(local,k)
        for j in range(3): XYZ[j] += wt*p[j]
        components.append({'pair':k, 'modes':[2*k,2*k+1],
                           'weight':wt, 'bloch':[round(q,12) for q in p]})
    purity = min(1.,math.sqrt(sum(x*x for x in XYZ)))
    return {'xyz': [round(x,12) for x in XYZ],
            'radius':purity, 'mixed_state':purity < 1-1e-9,
            'mode_count':DIM, 'pair_count':PAIRS,
            'projection':'fixed_pair_frame_partial_trace_v1',
            'pairs':components}

def spinor(phase: float) -> complex:
    return cmath.exp(.5j*phase)

def evolve_unwrapped(v: Sequence[float], delta: Sequence[float]) -> tuple[float, ...]:
    return tuple(a+b for a,b in zip(check_phase36(v),check_phase36(delta)))

def geometric_path_phase(states: Sequence[Sequence[float]]) -> float:
    """Bargmann/Pancharatnam loop; cyclic closure is explicit."""
    if len(states) < 3: return 0.0
    prod = 1+0j
    for i in range(len(states)):
        z = overlap(states[i], states[(i+1) % len(states)])
        if abs(z) < 1e-12: raise ValueError('Undefined loop phase: orthogonal neighbors')
        prod *= z / abs(z)
    return cmath.phase(prod)

def validate_scene(scene: dict) -> dict:
    if scene.get('schema') != 'PHASEHOLOMOTION_BLOCH36_V1':
        raise ValueError('Scene schema mismatch')
    nodes = scene.get('nodes',[])
    if not 1 <= len(nodes) <= 128:
        raise ValueError('1..128 nodes required')
    ids = [n.get('id') for n in nodes]
    if any(not isinstance(t,str) or not t for t in ids) or len(set(ids)) != len(ids):
        raise ValueError('Unique nonempty string node ids required')
    for node in nodes: phases(node)
    kinds = {'DEPENDS_ON','NOT_EQUIVALENT_TO','RELATED_TO','MEMBER_OF',
             'COACTIVATES_WITH','TRANSPORTS_TO','COUNTERFACTUAL_TO','EVOKES','INHIBITS'}
    for edge in scene.get('edges',[]):
        if edge.get('source') not in ids or edge.get('target') not in ids:
            raise ValueError('Dangling typed semantic relation')
        if edge.get('type') not in kinds:
            raise ValueError('Undeclared relation type')
    return scene

def compile_scene(scene:dict) ->dict:
    validate_scene(scene)
    out = dict(scene)
    out['nodes'] = [{**n, 'phase36':list(phases(n)),
                     'bloch':bloch36_projection(phases(n))} for n in scene['nodes']]
    lookup = {n['id']:n for n in out['nodes']}
    out['edges'] = [{**e, 'geometry36':relation(lookup[e['source']]['phase36'],
                                            lookup[e['target']]['phase36'])} for e in scene.get('edges',[])]
    out['constants'] = {'kappa':KAPPA,'zeta0':ZETA0,'sigma':SIGMA,
                        'singularity':'s=|i|²/2+iτ','designated_poles':['-i','+i'],
                        'hold_potential':['-i','+i'], 'aux_measured':False}
    out['status'] = 'COMPUTED_SCENE; NOT_LIVE_PNAML'
    return out

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('scene')
    p.add_argument('-o','--output')
    a=p.parse_args()
    scene=json.loads(Path(a.scene).read_text(encoding='utf-8'))
    out=json.dumps(compile_scene(scene), ensure_ascii=False,indent=2)
    if a.output: Path(a.output).write_text(out+'\n',encoding='utf-8')
    else: print(out)

if __name__ == '__main__': main()
