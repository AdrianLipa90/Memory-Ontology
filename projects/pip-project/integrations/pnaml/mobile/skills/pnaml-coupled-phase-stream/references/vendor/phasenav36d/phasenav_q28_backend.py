from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

MAX_QUBITS = 28
MODE_QUBITS = 6
WORKSPACE_QUBITS = 22
CHUNK_AMPLITUDES = 1 << 18


@dataclass(frozen=True)
class Q28Layout:
    """Candidate PhaseNav register allocation; not yet canonical."""
    mode: tuple[int, ...] = tuple(range(0, 6))
    workspace: tuple[int, ...] = tuple(range(6, 28))

    @property
    def total_qubits(self) -> int:
        return len(self.mode) + len(self.workspace)


@dataclass
class QState:
    amplitudes: np.ndarray
    n_qubits: int

    def __post_init__(self) -> None:
        self.amplitudes = np.asarray(self.amplitudes, dtype=np.complex128).reshape(-1)
        if self.n_qubits < 0 or self.n_qubits > MAX_QUBITS:
            raise ValueError("n_qubits outside 0..28")
        if self.amplitudes.size != (1 << self.n_qubits):
            raise ValueError("state length does not match qubit count")
        if not np.isfinite(self.amplitudes.real).all() or not np.isfinite(self.amplitudes.imag).all():
            raise ValueError("non-finite amplitudes")


class Q28PhaseNavBackend:
    """Dynamic dense state-vector backend, expanding only when a qubit is touched.

    Logical capacity is capped at 28 qubits.  A state begins with the smallest
    register needed by the PhaseNav encoding and adds higher ancillas in |0>.
    No physical-QPU claim is made by this numerical backend.
    """

    def __init__(self, max_qubits: int = MAX_QUBITS):
        if not (MODE_QUBITS <= int(max_qubits) <= MAX_QUBITS):
            raise ValueError("max_qubits must be in 6..28")
        self.max_qubits = int(max_qubits)
        self.layout = Q28Layout()

    def capacity_receipt(self) -> dict:
        dense_bytes = 16 * (1 << self.max_qubits)
        return {
            "schema": "PHASENAV_Q28_CAPACITY_V1",
            "backend": "dynamic_dense_complex128",
            "max_qubits": self.max_qubits,
            "mode_address_qubits": MODE_QUBITS,
            "workspace_qubits": self.max_qubits - MODE_QUBITS,
            "dense_complex128_bytes": dense_bytes,
            "dense_complex128_gib": dense_bytes / float(1 << 30),
            "dynamic_expansion": True,
            "physical_qpu_claim": False,
        }

    def basis_state(self, n_qubits: int, index: int = 0) -> QState:
        n = int(n_qubits)
        if n < 1 or n > self.max_qubits:
            raise ValueError("invalid qubit count")
        size = 1 << n
        idx = int(index)
        if idx < 0 or idx >= size:
            raise ValueError("basis index out of range")
        a = np.zeros(size, dtype=np.complex128)
        a[idx] = 1.0 + 0.0j
        return QState(a, n)

    def encode_phase36(self, phase36) -> QState:
        phi = np.asarray(phase36, dtype=np.float64).reshape(-1)
        if phi.size != 36 or not np.isfinite(phi).all():
            raise ValueError("PhaseNav encoding requires exactly 36 finite phases")
        a = np.zeros(1 << MODE_QUBITS, dtype=np.complex128)
        a[:36] = np.exp(1j * np.mod(phi, 2.0 * math.pi)) / math.sqrt(36.0)
        return QState(a, MODE_QUBITS)

    def _ensure(self, state: QState, qubit: int) -> QState:
        q = int(qubit)
        if q < 0 or q >= self.max_qubits:
            raise ValueError(f"qubit {q} outside backend capacity 0..{self.max_qubits-1}")
        if q < state.n_qubits:
            return state
        target_n = q + 1
        new = np.zeros(1 << target_n, dtype=np.complex128)
        new[: state.amplitudes.size] = state.amplitudes
        return QState(new, target_n)

    @staticmethod
    def _validate_u2(U) -> np.ndarray:
        u = np.asarray(U, dtype=np.complex128)
        if u.shape != (2, 2):
            raise ValueError("single-qubit gate must be 2x2")
        if not np.allclose(u.conj().T @ u, np.eye(2), atol=1e-12):
            raise ValueError("single-qubit gate must be unitary")
        return u

    def single_qubit(self, state: QState, qubit: int, U) -> QState:
        state = self._ensure(state, qubit)
        q = int(qubit)
        u = self._validate_u2(U)
        arr = state.amplitudes
        stride = 1 << q
        pair_block = stride << 1
        N = arr.size

        if pair_block <= CHUNK_AMPLITUDES:
            blocks_per_chunk = max(1, CHUNK_AMPLITUDES // pair_block)
            chunk_span = blocks_per_chunk * pair_block
            for base in range(0, N, chunk_span):
                end = min(N, base + chunk_span)
                sub = arr[base:end].reshape(-1, 2, stride)
                a = sub[:, 0, :].copy()
                b = sub[:, 1, :].copy()
                sub[:, 0, :] = u[0, 0] * a + u[0, 1] * b
                sub[:, 1, :] = u[1, 0] * a + u[1, 1] * b
        else:
            for base in range(0, N, pair_block):
                for off in range(0, stride, CHUNK_AMPLITUDES):
                    width = min(CHUNK_AMPLITUDES, stride - off)
                    lo = slice(base + off, base + off + width)
                    hi = slice(base + stride + off, base + stride + off + width)
                    a = arr[lo].copy()
                    b = arr[hi].copy()
                    arr[lo] = u[0, 0] * a + u[0, 1] * b
                    arr[hi] = u[1, 0] * a + u[1, 1] * b
        return state

    def hadamard(self, state: QState, qubit: int) -> QState:
        s = 1.0 / math.sqrt(2.0)
        return self.single_qubit(state, qubit, np.array([[s, s], [s, -s]], dtype=np.complex128))

    def rz(self, state: QState, qubit: int, theta: float) -> QState:
        th = float(theta)
        U = np.array([[np.exp(-0.5j * th), 0.0], [0.0, np.exp(0.5j * th)]], dtype=np.complex128)
        return self.single_qubit(state, qubit, U)

    def phase(self, state: QState, qubit: int, theta: float) -> QState:
        th = float(theta)
        U = np.array([[1.0, 0.0], [0.0, np.exp(1j * th)]], dtype=np.complex128)
        return self.single_qubit(state, qubit, U)

    def x(self, state: QState, qubit: int) -> QState:
        return self.single_qubit(state, qubit, np.array([[0, 1], [1, 0]], dtype=np.complex128))

    def cnot(self, state: QState, control: int, target: int) -> QState:
        c, t = int(control), int(target)
        if c == t:
            raise ValueError("control and target must differ")
        state = self._ensure(state, max(c, t))
        arr = state.amplitudes
        N = arr.size
        stride_t = 1 << t
        pair_block = stride_t << 1

        if c > t:
            for base in range(0, N, pair_block):
                if base & (1 << c):
                    for off in range(0, stride_t, CHUNK_AMPLITUDES):
                        width = min(CHUNK_AMPLITUDES, stride_t - off)
                        lo = slice(base + off, base + off + width)
                        hi = slice(base + stride_t + off, base + stride_t + off + width)
                        tmp = arr[lo].copy()
                        arr[lo] = arr[hi]
                        arr[hi] = tmp
        else:
            stride_c = 1 << c
            small = stride_c << 1
            for base in range(0, N, pair_block):
                for off in range(0, stride_t, small):
                    lo0 = base + off + stride_c
                    hi0 = base + stride_t + off + stride_c
                    lo = slice(lo0, lo0 + stride_c)
                    hi = slice(hi0, hi0 + stride_c)
                    tmp = arr[lo].copy()
                    arr[lo] = arr[hi]
                    arr[hi] = tmp
        return state

    @staticmethod
    def norm(state: QState) -> float:
        return float(np.vdot(state.amplitudes, state.amplitudes).real)

@dataclass
class SparseQState:
    indices: np.ndarray
    amplitudes: np.ndarray
    n_qubits: int

    def __post_init__(self) -> None:
        self.indices = np.asarray(self.indices, dtype=np.uint64).reshape(-1)
        self.amplitudes = np.asarray(self.amplitudes, dtype=np.complex128).reshape(-1)
        if self.indices.size != self.amplitudes.size:
            raise ValueError("sparse index/amplitude size mismatch")
        if self.n_qubits < 1 or self.n_qubits > MAX_QUBITS:
            raise ValueError("n_qubits outside 1..28")
        if self.indices.size and int(self.indices.max()) >= (1 << self.n_qubits):
            raise ValueError("sparse basis index outside register")
        if not np.isfinite(self.amplitudes.real).all() or not np.isfinite(self.amplitudes.imag).all():
            raise ValueError("non-finite sparse amplitudes")
        if self.indices.size > 1 and np.any(self.indices[1:] <= self.indices[:-1]):
            raise ValueError("sparse indices must be strictly increasing")


def _sparse_from_terms(terms: dict[int, complex], n_qubits: int) -> SparseQState:
    keys = sorted(k for k, v in terms.items() if v != 0.0j)
    idx = np.asarray(keys, dtype=np.uint64)
    amp = np.asarray([terms[k] for k in keys], dtype=np.complex128)
    return SparseQState(idx, amp, n_qubits)


def _state_sha256_sparse(state: SparseQState) -> str:
    import hashlib
    h = hashlib.sha256()
    h.update(int(state.n_qubits).to_bytes(2, "little", signed=False))
    h.update(np.asarray(state.indices, dtype="<u8").tobytes(order="C"))
    h.update(np.asarray(state.amplitudes, dtype="<c16").tobytes(order="C"))
    return h.hexdigest()


def _ensure_sparse(state: SparseQState, qubit: int, max_qubits: int) -> SparseQState:
    q = int(qubit)
    if q < 0 or q >= max_qubits:
        raise ValueError(f"qubit {q} outside backend capacity 0..{max_qubits-1}")
    if q < state.n_qubits:
        return state
    return SparseQState(state.indices.copy(), state.amplitudes.copy(), q + 1)


def _sparse_single(state: SparseQState, qubit: int, U, max_qubits: int) -> SparseQState:
    state = _ensure_sparse(state, qubit, max_qubits)
    q = int(qubit)
    u = Q28PhaseNavBackend._validate_u2(U)
    mask = 1 << q
    terms: dict[int, complex] = {}
    for idx_raw, amp in zip(state.indices, state.amplitudes):
        idx = int(idx_raw)
        bit = 1 if (idx & mask) else 0
        lo = idx & ~mask
        hi = lo | mask
        a0 = u[0, bit] * amp
        a1 = u[1, bit] * amp
        if a0 != 0.0j:
            terms[lo] = terms.get(lo, 0.0j) + a0
        if a1 != 0.0j:
            terms[hi] = terms.get(hi, 0.0j) + a1
    return _sparse_from_terms(terms, state.n_qubits)


def _sparse_cnot(state: SparseQState, control: int, target: int, max_qubits: int) -> SparseQState:
    c, t = int(control), int(target)
    if c == t:
        raise ValueError("control and target must differ")
    state = _ensure_sparse(state, max(c, t), max_qubits)
    cmask, tmask = 1 << c, 1 << t
    terms: dict[int, complex] = {}
    for idx_raw, amp in zip(state.indices, state.amplitudes):
        idx = int(idx_raw)
        out = idx ^ tmask if (idx & cmask) else idx
        terms[out] = terms.get(out, 0.0j) + amp
    return _sparse_from_terms(terms, state.n_qubits)


def _sparse_norm(state: SparseQState) -> float:
    return float(np.vdot(state.amplitudes, state.amplitudes).real)


def _encode_phase36_sparse(self, phase36) -> SparseQState:
    phi = np.asarray(phase36, dtype=np.float64).reshape(-1)
    if phi.size != 36 or not np.isfinite(phi).all():
        raise ValueError("PhaseNav encoding requires exactly 36 finite phases")
    idx = np.arange(36, dtype=np.uint64)
    amp = np.exp(1j * np.mod(phi, 2.0 * math.pi)) / math.sqrt(36.0)
    return SparseQState(idx, amp, MODE_QUBITS)


def _run_sparse_circuit(self, phase36, gates) -> SparseQState:
    state = self.encode_phase36_sparse(phase36)
    if not isinstance(gates, (list, tuple)):
        raise ValueError("gates must be a list")
    if len(gates) > 4096:
        raise ValueError("Q28 circuit exceeds 4096-gate limit")
    s2 = 1.0 / math.sqrt(2.0)
    H = np.array([[s2, s2], [s2, -s2]], dtype=np.complex128)
    X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    for spec in gates:
        if not isinstance(spec, dict):
            raise ValueError("gate specification must be an object")
        gate = str(spec.get("gate", "")).upper()
        if gate == "H":
            state = _sparse_single(state, int(spec["qubit"]), H, self.max_qubits)
        elif gate == "X":
            state = _sparse_single(state, int(spec["qubit"]), X, self.max_qubits)
        elif gate == "RZ":
            th = float(spec["theta"])
            U = np.array([[np.exp(-0.5j*th), 0.0], [0.0, np.exp(0.5j*th)]], dtype=np.complex128)
            state = _sparse_single(state, int(spec["qubit"]), U, self.max_qubits)
        elif gate == "PHASE":
            th = float(spec["theta"])
            U = np.array([[1.0, 0.0], [0.0, np.exp(1j*th)]], dtype=np.complex128)
            state = _sparse_single(state, int(spec["qubit"]), U, self.max_qubits)
        elif gate == "CNOT":
            state = _sparse_cnot(state, int(spec["control"]), int(spec["target"]), self.max_qubits)
        else:
            raise ValueError(f"unsupported Q28 gate: {gate or '<missing>'}")
    return state


# Candidate methods are bound explicitly to keep the pre-existing dense API intact.
Q28PhaseNavBackend.encode_phase36_sparse = _encode_phase36_sparse
Q28PhaseNavBackend.run_sparse_circuit = _run_sparse_circuit
Q28PhaseNavBackend.sparse_norm = staticmethod(_sparse_norm)
Q28PhaseNavBackend.sparse_state_sha256 = staticmethod(_state_sha256_sparse)
