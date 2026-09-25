# TODO / Research Queue — Ternary Stella Representation v0.2

Status: **PARTIALLY_RESOLVED / EXACT_SUBSTRUCTURES_IDENTIFIED / FULL_BACKEND_OPEN**

This file supersedes the original "untested intuition" status. The cross-domain audit found exact ternary structures in constrained graph and spectral sectors, but not a universal ternary replacement for the richer memory representation.

Formal audit:

- cross_domain/ternary-stella-cross-domain-audit-v0.2.md
- provenance/TERNARY_CROSS_DOMAIN_AUDIT_V0_2.json
- tests/test_ternary_cross_domain_contract.py

## Current representation hypothesis

Retain the candidate stack

\[
R_Q \rightarrow R_{T_3} \rightarrow R_B,
\]

where

\[
T_3=\{-1,0,+1\}.
\]

The ternary layer is currently interpreted as a candidate discrete skeleton for routing, support, orientation, and sign-class observables.

It is **not** assumed to preserve arbitrary amplitudes, phases, winding multiplicities, or full quantum-state information.

## What is now exact

### Stella combinatorics

For

\[
\mathbf t=(t_x,t_y,t_z),\qquad t_i\in T_3,
\]

the full state count is

\[
3^3=27.
\]

By number of active coordinates:

\[
\boxed{27=1+6+12+8.}
\]

The eight fully active states are

\[
\boxed{\{\pm1\}^3},
\]

which map bijectively to cube vertices.

### Oriented path support

For a simple path/cycle with each edge traversed at most once,

\[
t_e=
-1,0,+1
\]

exactly records reverse / absent / forward edge use.

For a closed cycle,

\[
B\mathbf t=0.
\]

For edge phases,

\[
\Phi_C=\mathbf t^T\boldsymbol\theta,
\qquad
W_C=\prod_e e^{it_e\theta_e}.
\]

This is an exact representation on the declared path sector.

### Chemistry spectral witness

A declared Resonant Chemistry three-site holonomy control has spectrum

\[
\{-\sqrt3,0,+\sqrt3\},
\]

which normalizes exactly to

\[
\{-1,0,+1\}.
\]

This is an exact witness for that control Hamiltonian, not a universal molecular spectrum.

### GREMLIN exchange quotient

The GREMLIN oriented-exchange spectrum

\[
\{-|E_R|,0,0,+|E_R|\}
\]

has the exact distinct-value quotient

\[
\{-1,0,+1\}.
\]

The zero multiplicity means this is a quotient, not a full-state isomorphism.

### Spectroscopic sign quotient

A frozen sign/null projection

\[
Q_\delta(x)\in\{-1,0,+1\}
\]

gives an exact ternary quotient of a declared response observable. The quotient intentionally loses magnitude.

## What remains open

### TODO-1 — path composition law

The ternary path sector is not closed under unrestricted addition:

\[
1+1=2\notin T_3.
\]

Compare at least:

- integer winding counts;
- sign-only projection;
- saturating ternary;
- modulo-3 / \(\mathbb F_3\);
- typed overflow into a richer path state.

Do not silently identify these choices.

### TODO-2 — Q-native to ternary information loss

Define and measure

\[
L_{Q\rightarrow T_3}
\]

for the observables required by each memory task.

Separate:

- lost amplitude information;
- lost phase information;
- lost multiplicity/winding information;
- lost interference information;
- preserved support/orientation information.

### TODO-3 — behavioral equivalence

For each task family evaluate

\[
d_H(R_Q,R_{T_3})\le\varepsilon.
\]

The ternary backend is admissible only where the declared \((\varepsilon,H)\) contract passes.

### TODO-4 — resource comparison

Benchmark

\[
R_Q\rightarrow R_{T_3}\rightarrow R_B
\]

against direct

\[
R_Q\rightarrow R_B.
\]

Measure at minimum:

- storage;
- update cost;
- query cost;
- compile/projection cost;
- sequential depth;
- accuracy/equivalence failure rate.

### TODO-5 — procedural-memory tasks

Run controlled tests for:

- path completion;
- skill consolidation;
- transfer;
- interference;
- forgetting;
- recovery after partial deletion;
- multi-skill routing.

### TODO-6 — Stella shell utility

Test whether

\[
1/6/12/8
\]

support shells provide useful structure for:

- routing;
- anomaly detection;
- confidence gating;
- sparse indexing;
- conflict classification.

Do not promote the shell decomposition merely because the combinatorics are exact.

### TODO-7 — noise threshold

For numerical/experimental sign classification, freeze

\[
\delta>0
\]

before evaluation.

Measure ternary class-flip rate under:

- numerical precision changes;
- detector/noise models;
- nuisance perturbations;
- repeated observations.

### TODO-8 — typed cross-domain adapter

A memory-routing trit, chemical path trit, and spectral-response trit may share the same alphabet without being the same typed object.

Define an adapter only if it preserves the relevant operation and semantics.

Required distinction:

\[
\text{same values}
\neq
\text{same object}.
\]

### TODO-9 — PhaseNav pair-sector binding

PhaseNav currently supplies native \(+1/-1\) involution sectors.

A zero state requires an explicit null/inactive/projection rule.

Test whether such a rule yields a useful and stable ternary subspace without corrupting the completed pair algebra.

### TODO-10 — composite Stella trit

Keep the project-specific composite "Stella trit" OPEN.

Only define one if an explicit map

\[
\pi:\Omega_{\rm micro}\rightarrow T_3
\]

or decoder relation has a measurable advantage over simply retaining three ordinary trits.

## Current default semantics

For path/routing use, prefer signed ternary semantics:

\[
-1=\text{reverse/opposed},
\qquad
0=\text{absent/null},
\qquad
+1=\text{forward/aligned}.
\]

Do not default to \(\mathbb F_3\), because

\[
1+1=-1\pmod3
\]

does not generally match repeated path traversal.

## Promotion rule

The ternary layer may be promoted from TODO to a formal representation backend only after:

1. the task-specific equivalence contract passes;
2. information loss is characterized;
3. path-composition semantics are fixed;
4. resource results beat or justify the added layer;
5. source and target types are explicit;
6. failure/noise behavior is fail-loud.

Until then the correct project status is

\[
\boxed{
\text{PARTIALLY_RESOLVED TERNARY REPRESENTATION CANDIDATE}
}
\]

with exactness restricted to the sectors documented in the v0.2 cross-domain audit.
