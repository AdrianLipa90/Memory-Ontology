"""AUX ternary ↔ downstream binary bridge, preserving continuous 36D PNAML carrier.

Source formalism: Adrian Lipa. Local, non-actuating reference adapter.
Contract: PNAML_RDSS_PNCS_WAVE_CONTRACT_V0_5.pna.

The continuous phase36 carrier, unwrapped winding, and 12 control trits are
separate lanes. HOLD (0) preserves the potential pair (-i,+i); it is NOT an
ordinary binary zero, a missing measurement, or a paused phase oscillator.

QHNI v1 reserved zero bytes are NOT measurements, so they must not be decoded
as AUX HOLD. This module neither authenticates a native AUX source nor actuates.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Sequence

from .semantic_bloch36 import DIM, TAU, check_phase36, bloch36_projection

TRITS = 12
VALID = frozenset((-1, 0, 1))
# 472-byte payload + 32-byte SHA-256; little-endian reference witness only.
_PAYLOAD = struct.Struct('<4sHHQd12b4x36d36i')
FRAME_BYTES = _PAYLOAD.size + hashlib.sha256().digest_size
MAGIC = b'AUX3'
VERSION = 1


def validate_trits(trits: Sequence[int]) -> tuple[int, ...]:
    if len(trits) != TRITS or any(type(t) is not int or t not in VALID for t in trits):
        raise ValueError('12 exactly signed integer trits from {-1,0,+1} required')
    return tuple(trits)


def binary_lanes(trits: Sequence[int]) -> dict:
    """Lossless binary downstream adapter: (value_bits, valid_mask).

    +1 => value 1, valid 1; -1 => value 0, valid 1.
    HOLD=> valid 0, value 0 (placeholder only), retaining [-i,+i] potential.
    The pair is essential: data bits alone are not invertible.
    """
    trits = validate_trits(trits)
    values = sum((1 << i) for i, t in enumerate(trits) if t == 1)
    mask = sum((1 << i) for i, t in enumerate(trits) if t != 0)
    holds = ((1 << TRITS) - 1) ^ mask
    return {'value_bits': values, 'valid_mask': mask, 'hold_mask': holds,
            'bit_order': 'lsb=trit[0]', 'width': TRITS, 'hold_potential': ['-i', '+i']}


def decode_binary_lanes(values: int, valid_mask: int) -> tuple[int, ...]:
    if type(values) is not int or type(valid_mask) is not int or not 0 <= values < 1 << TRITS or not 0 <= valid_mask < 1 << TRITS:
        raise ValueError('invalid 12-bit binary lane')
    if values & ~valid_mask:
        raise ValueError('noncanonical HOLD: value must not be asserted when mask=0')
    return tuple(0 if not (valid_mask >> i) & 1 else (1 if (values >> i) & 1 else -1)
                 for i in range(TRITS))


def _windings(phi: Sequence[float]) -> tuple[int, ...]:
    vals = tuple(math.floor(t / TAU) for t in phi)
    if any(w < -(2**31) or w >= 2**31 for w in vals):
        raise ValueError('winding does not fit int32')
    return vals


@dataclass(frozen=True)
class AuxFrame:
    sequence: int
    tau: float
    trits12: tuple[int, ...]
    phase36: tuple[float, ...]
    winding36: tuple[int, ...]

    @classmethod
    def from_values(cls, sequence: int, tau: float, trits12: Sequence[int], phase36: Sequence[float]) -> 'AuxFrame':
        if type(sequence) is not int or not 0 <= sequence < (1 << 64):
            raise ValueError('sequence outside uint64')
        if not math.isfinite(tau):
            raise ValueError('tau must be a finite internal lifted unit')
        ph = check_phase36(phase36)
        return cls(sequence, float(tau), validate_trits(trits12), ph, _windings(ph))

    def to_bytes(self) -> bytes:
        frame = AuxFrame.from_values(self.sequence, self.tau, self.trits12, self.phase36)
        if tuple(self.winding36) != frame.winding36:
            raise ValueError('inconsistent unwrapped winding')
        data = _PAYLOAD.pack(MAGIC, VERSION, FRAME_BYTES, self.sequence, self.tau,
                             *self.trits12, *self.phase36, *self.winding36)
        return data + hashlib.sha256(data).digest()

    @classmethod
    def from_bytes(cls, blob: bytes) -> 'AuxFrame':
        if len(blob) != FRAME_BYTES:
            raise ValueError('incorrect AUX frame size')
        data, sha = blob[:-32], blob[-32:]
        if hashlib.sha256(data).digest() != sha:
            raise ValueError('AUX frame sha256 mismatch')
        if any(data[36:40]):
            raise ValueError('AUX frame reserved bytes must be zero')
        fields = _PAYLOAD.unpack(data)
        magic, version, size, sequence, tau = fields[:5]
        if (magic, version, size) != (MAGIC, VERSION, FRAME_BYTES):
            raise ValueError('invalid AUX frame header')
        trits = fields[5:17]
        phase = fields[17:53]
        winding = fields[53:89]
        frame = cls.from_values(sequence, tau, trits, phase)
        if tuple(winding) != frame.winding36:
            raise ValueError('AUX winding integrity failure')
        return frame

    def inspect(self) -> dict:
        lanes = binary_lanes(self.trits12)
        return {
            'schema': 'PHASEHOLOMOTION_AUX_TERNARY_BRIDGE_V02',
            'sequence': self.sequence,
            'tau_internal': self.tau,
            'trits12': list(self.trits12),
            'binary_downstream': lanes,
            'hold_count': self.trits12.count(0),
            'phase36': list(self.phase36),
            'winding36': list(self.winding36),
            'bloch_projection': bloch36_projection(self.phase36),
            'spinor4pi_phase0': [math.cos(self.phase36[0] / 2), math.sin(self.phase36[0] / 2)],
            'source_status': 'LOCAL_REFERENCE_WITNESS_UNVERIFIED',
            'native_aux_ack': 'UNKNOWN',
            'downstream_device_authority': False,
        }


def from_qhni_v1(blob: bytes, *, explicit_trits: Sequence[int] | None = None) -> AuxFrame:
    """Read QHNI v1 source phases; AUX is never inferred from reserved zero bytes.

    An explicit trit argument is a local simulation/test input only; not evidence
    that NIC measured AUX. Sequence/tau are model-unit metadata of the adapter.
    """
    if len(blob) != 640 or blob[:4] != b'QHNI' or struct.unpack_from('<HH', blob, 4) != (1, 640):
        raise ValueError('Expected one QHNI v1 (640 bytes)')
    if explicit_trits is None:
        raise ValueError('QHNI v1 does not measure AUX; reserved zeros are not HOLD')
    if any(blob[624:640]):
        raise ValueError('QHNI reserved bytes are not zero: invalid v1 record')
    phi = struct.unpack_from('<36d', blob, 48)
    seq = struct.unpack_from('<Q', blob, 8)[0]
    tick = struct.unpack_from('<Q', blob, 24)[0]
    return AuxFrame.from_values(seq, float(tick), explicit_trits, phi)


def from_scene(scene: dict, node_id: str, trits12: Sequence[int], sequence: int = 1, tau: float = 0) -> AuxFrame:
    if scene.get('schema') != 'PHASEHOLOMOTION_BLOCH36_V1':
        raise ValueError('invalid phase scene schema')
    found = [n for n in scene.get('nodes', []) if n.get('id') == node_id]
    if len(found) != 1 or not isinstance(found[0].get('phase36'), list):
        raise ValueError('node missing or lacks explicit 36D carrier')
    return AuxFrame.from_values(sequence, tau, trits12, found[0]['phase36'])



def overlay_scene(scene: dict, frame: AuxFrame, node_id: str) -> dict:
    """Place a decoded binary bridge witness onto an existing semantic set.

    Does not invent ontology edges or semantic meaning. Other scene nodes and
    their relations are unchanged. This is local display input, not actuation.
    """
    if scene.get('schema') != 'PHASEHOLOMOTION_BLOCH36_V1':
        raise ValueError('not a PhaseHoloMotion scene')
    found = [n for n in scene.get('nodes', []) if n.get('id') == node_id]
    if len(found) != 1:
        raise ValueError('target node must exist exactly once')
    result = json.loads(json.dumps(scene))
    for node in result['nodes']:
        if node['id'] == node_id:
            node['phase36'] = list(frame.phase36)
            node['winding'] = list(frame.winding36)
            node['aux_ternary12'] = list(frame.trits12)
            node['aux_binary_downstream'] = binary_lanes(frame.trits12)
            node['source_record_type'] = 'AUX3_LOCAL_REFERENCE_BINARY_WITNESS'
            node['source_provenance'] = 'IMPORTED_UNVERIFIED'
            node['aux_measured'] = False
            break
    result['source'] = 'AUX3_BINARY_REFERENCE_UNVERIFIED'
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Local reference bridge, not native AUX execution')
    sub = parser.add_subparsers(dest='command', required=True)
    make = sub.add_parser('pack', help='pack scene node with explicitly supplied 12 trits')
    make.add_argument('scene'); make.add_argument('node'); make.add_argument('trits', help='12 comma-separated signed trits')
    make.add_argument('output'); make.add_argument('--sequence', type=int, default=1)
    make.add_argument('--tau', type=float, default=0)
    inspect = sub.add_parser('inspect', help='verify and inspect a 504-byte AUX3 frame')
    inspect.add_argument('frame'); inspect.add_argument('--output')
    inject = sub.add_parser('overlay', help='overlay verified local AUX3 carrier onto an existing scene node')
    inject.add_argument('frame'); inject.add_argument('scene'); inject.add_argument('node'); inject.add_argument('output')
    args = parser.parse_args()
    if args.command == 'pack':
        scene = json.loads(Path(args.scene).read_text(encoding='utf-8'))
        trits = [int(t) for t in args.trits.split(',')]
        frame = from_scene(scene, args.node, trits, args.sequence, args.tau)
        Path(args.output).write_bytes(frame.to_bytes())
        print(json.dumps({'status': 'LOCAL_WITNESS_PACKED', 'frame_bytes': FRAME_BYTES,
                          'sha256': hashlib.sha256(Path(args.output).read_bytes()).hexdigest(),
                          'binary_downstream': binary_lanes(frame.trits12)}, ensure_ascii=False))
    elif args.command == 'overlay':
        frame = AuxFrame.from_bytes(Path(args.frame).read_bytes())
        scene = json.loads(Path(args.scene).read_text(encoding='utf-8'))
        result = overlay_scene(scene, frame, args.node)
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({'status':'LOCAL_SCENE_OVERLAY_CREATED', 'source':'AUX3_BINARY_REFERENCE_UNVERIFIED', 'node':args.node, 'output':args.output}))
    else:
        frame = AuxFrame.from_bytes(Path(args.frame).read_bytes())
        s = json.dumps(frame.inspect(), ensure_ascii=False, indent=2)
        if args.output: Path(args.output).write_text(s+'\n', encoding='utf-8')
        else: print(s)

if __name__ == '__main__': main()
