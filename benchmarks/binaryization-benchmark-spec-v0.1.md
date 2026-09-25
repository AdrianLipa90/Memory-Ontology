# Binaryization Benchmark Specification — v0.1

## Purpose

Measure the cost of reproducing quantum-native memory dynamics with binary backends without assuming in advance that the binary representation is cheap or exponentially expensive.

## Test object

Use a family of memory systems

\[
\{\mathfrak M_n\}_{n\in N}
\]

with increasing problem size \(n\).

For procedural memory, each instance should contain a graph/state space, candidate trajectories, an update/consolidation rule, task-relevant queries, and controlled perturbations/interventions.

## Required backends

At minimum benchmark:

1. **Q-native reference** — the project's canonical quantum-native representation.
2. **Binary explicit** — explicit enumeration/state-vector/path-state baseline where feasible.
3. **Binary sparse** — sparse graph/state representation.
4. **Binary compressed** — strongest structurally appropriate compressed backend available.
5. **Binary task-specific** — an algorithm optimized for the declared observable/query contract.

The benchmark must not compare Q-native only against an intentionally weak binary baseline.

## Equivalence contract

Choose before timing:

\[
(\varepsilon,H,D,\mathcal A,Y).
\]

Report:

- error tolerance \(\varepsilon\);
- horizon \(H\);
- distance/divergence \(D\);
- intervention set \(\mathcal A\);
- observable set \(Y\).

A binary backend passes semantic equivalence only if

\[
d_H(R_Q,R_B)\le\varepsilon.
\]

A backend that fails equivalence cannot be counted as a successful binaryization regardless of performance.

## Metrics

Record separately:

\[
S=\text{peak storage},
\]

\[
T_c=\text{compile/initialization time},
\]

\[
T_u=\text{update time},
\]

\[
T_q=\text{query/readout time},
\]

\[
N_s=\text{samples/runs required},
\]

\[
D_s=\text{sequential dependency depth}.
\]

Optional platform metrics include energy, device cost, wall-clock latency, throughput, numerical precision, and accelerator utilization.

## Scaling protocol

For each size \(n\):

1. generate the same logical instance for every backend;
2. compile each backend;
3. verify \((\varepsilon,H)\)-equivalence;
4. run identical update/query workloads;
5. repeat over multiple seeds/instances;
6. report median and dispersion;
7. fit candidate scaling laws only over the measured range;
8. separate measured scaling from asymptotic claims.

## Explicit-amplitude control

When the Q-native state corresponds to \(n\) two-level degrees of freedom, include explicit state-vector binaryization where feasible as a control:

\[
S_{\mathrm{SV}}\propto 2^n.
\]

Do not treat this control as the optimal binary backend. Its purpose is to quantify the cost of literal amplitude expansion.

## Structure-ablation ladder

To determine where classical compression succeeds, progressively reduce exploitable structure:

1. product/separable paths;
2. sparse path superpositions;
3. symmetric/repeated motifs;
4. low-rank or low-entanglement families;
5. irregular but compressible graphs;
6. high-complexity state families.

The key observable is how the best binary cost frontier changes as structure is removed.

## Procedural-memory tasks

Recommended first tasks:

- trajectory completion;
- next-step prediction;
- skill execution after consolidation;
- transfer under graph perturbation;
- interference between partially overlapping skills;
- forgetting/decay under controlled update rules;
- recovery after partial state deletion;
- multi-skill routing.

## Evidence labels

Use only:

- **PARITY**
- **CLASSICAL_COMPRESSION**
- **CANDIDATE_Q_NATIVE_ADVANTAGE**
- **EMPIRICAL_Q_NATIVE_ADVANTAGE**
- **THEORETICAL_SEPARATION**
- **PHYSICAL_QUANTUM_NECESSITY**

Benchmark performance alone cannot establish physical quantum necessity.

## Fail-loud conditions

Return FAIL rather than an advantage claim if:

- semantic equivalence is not demonstrated;
- the binary baseline is structurally mismatched;
- precision differs materially without correction;
- sampling/readout cost is omitted;
- only one problem size is measured;
- synthetic data are presented as physical validation;
- an explicit \(2^n\) state-vector baseline is mislabeled as a universal classical lower bound.
