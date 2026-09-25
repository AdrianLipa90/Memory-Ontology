# Representation Duality and Binaryization Cost — v0.1

## 1. Status

This document formalizes a representation question without deciding the physical substrate question.

The Memory Ontology core remains substrate-neutral. The current research representation may be quantum-native. A binary realization is treated as a possible compiler/emulator target whose cost must be measured or bounded rather than assumed.

Therefore the claims are separated:

1. **Ontology claim** — what qualifies as memory.
2. **Representation claim** — how the same memory dynamics are encoded and evolved.
3. **Physical-substrate claim** — what physical medium realizes the representation.

No implication between these three levels is automatic.

## 2. Abstract memory dynamics

Let the abstract memory system be

\[
\mathfrak M=(X,M,U,F,Y),
\]

where:

- \(X_t\) is active state;
- \(M_t\) is history-bearing memory structure;
- \(U\) updates memory;
- \(F\) updates active state;
- \(Y\) defines observable outputs relevant to the task.

The abstract dynamics are

\[
M_{t+1}=U(M_t,X_t,u_t),
\]

\[
X_{t+1}=F(X_t,u_t;M_t),
\]

\[
y_t=Y(X_t,M_t).
\]

A representation is not the memory law itself. It is an implementation of \(\mathfrak M\).

## 3. Two representation families

### 3.1 Quantum-native representation

A quantum-native realization \(R_Q\) may encode memory structure using amplitudes, phases, interference, superposition, tensor-product structure, or related Hilbert-space objects.

We write

\[
R_Q(\mathfrak M)=
(\mathcal H,\rho_t,\mathcal U_Q,\mathcal O_Q),
\]

where \(\mathcal H\) is the representation space, \(\rho_t\) the represented state, \(\mathcal U_Q\) the update dynamics, and \(\mathcal O_Q\) the task-relevant observables.

"Quantum-native" here describes the formal representation. It does not by itself assert that a physical quantum processor is present.

### 3.2 Binary representation

A binary realization \(R_B\) encodes the same abstract memory dynamics into finite classical bit strings and classical update rules:

\[
R_B(\mathfrak M)=
(\{0,1\}^{L},b_t,\mathcal U_B,\mathcal Q_B).
\]

The length \(L\) may vary with problem size and requested precision.

Binary representation includes explicit state-vector emulation, sparse representations, tensor-network-like factorizations, symbolic graphs, decision diagrams, low-rank models, or any other implementation ultimately encoded in bits.

## 4. Representation equivalence

Exact equality of internal representations is unnecessary. What matters is preservation of task-relevant behavior.

For horizon \(H\), admissible intervention sequence \(a_{0:H-1}\), and output metric or statistical divergence \(D\), define

\[
d_H(R_1,R_2)
=
\sup_{a_{0:H-1}\in\mathcal A^H}
D\!\left(
P_{R_1}(Y_{0:H}\mid a_{0:H-1}),
P_{R_2}(Y_{0:H}\mid a_{0:H-1})
\right).
\]

Two representations are \((\varepsilon,H)\)-equivalent when

\[
d_H(R_1,R_2)\le\varepsilon.
\]

For deterministic systems, \(P\) may be replaced by output trajectories and \(D\) by an appropriate trajectory distance.

This definition prevents a misleading comparison in which one backend stores more internal detail than the task ever exposes.

## 5. Binaryization

A binaryization of a quantum-native representation is a compiler/emulator

\[
\mathcal C_{Q\rightarrow B}^{(\varepsilon,H)}
:
R_Q
\longrightarrow
R_B
\]

such that

\[
d_H(R_Q,R_B)\le\varepsilon.
\]

The inverse direction, when defined, is

\[
\mathcal C_{B\rightarrow Q}^{(\varepsilon,H)}.
\]

No requirement is made that either compiler preserve internal coordinates. It must preserve the chosen behavioral contract.

## 6. Cost vector

Binaryization cost is not a single universal scalar. Define a resource vector

\[
\mathbf C_B^{(\varepsilon,H)}
=
\left(
S_B,
T_B^{\mathrm{compile}},
T_B^{\mathrm{update}},
T_B^{\mathrm{query}},
N_B^{\mathrm{samples}},
D_B
\right),
\]

where:

- \(S_B\): storage footprint;
- \(T_B^{\mathrm{compile}}\): one-time translation/initialization cost;
- \(T_B^{\mathrm{update}}\): cost of one memory update;
- \(T_B^{\mathrm{query}}\): cost of a task-relevant query/readout;
- \(N_B^{\mathrm{samples}}\): samples/runs required to reach the requested statistical accuracy;
- \(D_B\): effective sequential depth / dependency depth.

An analogous vector \(\mathbf C_Q^{(\varepsilon,H)}\) is defined for the quantum-native realization.

For a use case with non-negative weights \(w\), an optional scalarized cost is

\[
C_B^{w}(\varepsilon,H)
=
w\cdot \mathbf C_B^{(\varepsilon,H)}.
\]

The weights must be declared before comparing implementations.

## 7. Minimal binaryization cost

Let \(\mathcal B_{\varepsilon,H}(R_Q)\) be the set of all binary realizations that satisfy the equivalence contract.

The minimal binaryization resource frontier is

\[
\boxed{
\mathbf C_{\mathrm{bin}}^{*}
(\varepsilon,H;R_Q)
=
\inf_{R_B\in\mathcal B_{\varepsilon,H}(R_Q)}
\mathbf C(R_B)
}
\]

interpreted component-wise as a Pareto frontier rather than as one privileged number.

A statement that binaryization is "expensive" is meaningful only relative to this frontier or a declared subset of binary backends.

## 8. Explicit-amplitude baseline

For a generic pure state on \(n\) two-level quantum degrees of freedom,

\[
|\psi\rangle=
\sum_{x\in\{0,1\}^n}\alpha_x|x\rangle.
\]

An explicit classical state-vector representation contains \(2^n\) complex amplitudes. At fixed finite numerical precision \(p\), its storage therefore scales as

\[
S_{\mathrm{SV}}(n,p)=\Theta(2^n p)
\]

up to representation constants.

This is a **baseline for explicit amplitude simulation**, not a universal lower bound for every classical simulation.

The state may admit a much smaller classical description when it possesses exploitable structure, including sparsity, low entanglement, symmetry, low rank, stabilizer structure, repeated motifs, restricted observables, or a compact generative rule.

Also, the existence of \(2^n\) amplitudes does not imply simultaneous classical access to \(2^n\) independent outputs from a quantum device. Readout and sampling costs remain part of \(\mathbf C_Q\).

## 9. Compression ratio

For any binary backend \(B\), define the representation expansion factor relative to the quantum-native implementation:

\[
\chi_S
=
\frac{S_B}{S_Q},
\]

and analogously

\[
\chi_U
=
\frac{T_B^{\mathrm{update}}}{T_Q^{\mathrm{update}}},
\qquad
\chi_Q
=
\frac{T_B^{\mathrm{query}}}{T_Q^{\mathrm{query}}}.
\]

The vector

\[
\boldsymbol\chi
=
(\chi_S,\chi_U,\chi_Q,\ldots)
\]

is more informative than a single "speedup."

## 10. Representation regimes

### R0 — Parity

A binary realization preserves the required behavior at comparable asymptotic and practical cost.

Interpretation: quantum-native notation is convenient but not resource-essential for the tested task family.

### R1 — Structured classical compression

Naive explicit binaryization is expensive, but a compact classical representation exists because the state family is structured.

Interpretation: the \(2^n\) explicit state-vector baseline overstates the true classical cost.

### R2 — Empirical representation advantage

Across a declared task family and accuracy target, the best tested binary baselines exhibit a growing resource gap:

\[
\|\mathbf C_B\| \gg \|\mathbf C_Q\|.
\]

Interpretation: there is measured representation advantage against the tested classical methods. This is not yet a proof of optimal classical lower bounds.

### R3 — Complexity separation

A lower bound or accepted complexity argument excludes all relevant binary realizations below a stated asymptotic resource class while a quantum-native realization stays below that class.

Interpretation: representation advantage has a theoretical separation for the stated problem family and assumptions.

### R4 — Physical-substrate necessity

The physical memory phenomenon itself cannot be reproduced by any admissible non-quantum physical model within the declared empirical tolerance.

This is a much stronger empirical claim than R2 or R3 and is **not** asserted by Memory Ontology v0.1.

## 11. Procedural-memory specialization

Let a procedural memory be represented as a graph of reinforced trajectories

\[
G_P(t)=(V,E,W_t).
\]

A quantum-native realization may permit coherent combinations of candidate paths before task-relevant readout.

A binary backend must reproduce the same \((\varepsilon,H)\)-behavior, but it is free to use:

- explicit path enumeration;
- weighted graphs;
- sparse path tables;
- dynamic programming;
- tensor/factorized state;
- symbolic compression;
- learned surrogate transition models.

The research question is therefore not:

> "Can procedural memory be binary?"

but:

\[
\boxed{
\text{What is the minimal binary cost of preserving the same procedural dynamics?}
}
\]

## 12. No-free-advantage rule

A representation advantage claim must not be inferred merely from the word "superposition."

For every claimed advantage, report:

1. task family;
2. input/problem size;
3. \(\varepsilon\);
4. horizon \(H\);
5. observable/query contract;
6. best binary baselines attempted;
7. quantum-native implementation used;
8. storage, update, query and sampling costs;
9. approximation/compression assumptions;
10. whether the result is empirical or asymptotic.

Without these fields the status remains **candidate representation advantage**.

## 13. Current project position

Memory Ontology v0.1 therefore adopts the following position:

\[
\boxed{
\text{substrate-neutral law}
+
\text{quantum-native current representation}
+
\text{binaryizability open}
}
\]

with the central measurable quantity

\[
\boxed{
\mathbf C_{\mathrm{bin}}^{*}
(\varepsilon,H;R_Q).
}
\]

Whether this frontier is comparable, polynomially larger, exponentially larger, or physically unattainable is an empirical/theoretical result to be established, not an axiom.
