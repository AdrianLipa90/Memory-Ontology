# Ternary Stella Cross-Domain Audit — v0.2

Status: **CROSS_DOMAIN_FORMAL_AUDIT / PARTIAL_TODO_RESOLUTION / EXACT_SUBSTRUCTURES / GLOBAL_TERNARY_BINDING_OPEN**

This document cross-checks the ternary/Stella intuition against existing GREMLIN, Resonant Chemistry, Orbital Eclipse Spectroscopy, and PhaseNav Telescope structures.

It distinguishes four evidence classes:

- **ANALOGY** — similar shape or vocabulary only;
- **EXACT_QUOTIENT** — a many-to-one projection is exact for the declared observable;
- **EXACT_REPRESENTATION_ON_SECTOR** — the ternary object exactly represents a constrained sector;
- **ISOMORPHISM** — a bijection preserves the declared structure in both directions.

No physical quantum-necessity claim follows from any result below.

## 1. Source snapshot

Cross-check snapshot:

- GREMLIN main: 279aa3b9d7c9667f0ae58796a2b3d86544b26401
  - spec/GREMLIN_HERMITIAN_ORIENTED_EXCHANGE_V1_4.md
  - file blob: 9676a77eca8a0e51c354f0a0efc1ae40a2f5af2e
  - spec/GREMLIN_RELATIONAL_MEASUREMENT_CHANNEL_CATALOG_V0_1.md
  - file blob: f09600aa6aecbd976c547a1004cac2b94e43c16c
- Resonant Chemistry main: c60305b993e083233484ac00a7643cd3ee3611f4
  - reschem/relational_holonomy_spectroscopy.py
  - file blob: 7a6777c1f208a36e5c2ac84086f3251e8dbd9824
  - tests/test_relational_holonomy_spectroscopy.py
  - file blob: 407d514f7c83380d3ce8bfdfc02dc9a19b301d78
- Orbital Eclipse Spectroscopy main: 20957d9eafce27497e948c69cfc87dc9ef705e91
- PhaseNav Telescope main: d71bb0091136a241f579955b6ed87e9d8b74e647

The conclusions below are scoped to those source states.

## 2. Ternary carrier

Define the signed ternary set

\[
T_3=\{-1,0,+1\}.
\]

For three channels define the Stella state space

\[
\mathcal S_3=T_3^3.
\]

Therefore

\[
|\mathcal S_3|=3^3=27.
\]

Classify a state by the number \(k\) of non-zero coordinates. Then

\[
N_k={3\choose k}2^k,
\]

so

\[
\boxed{27=1+6+12+8.}
\]

The shells are:

- \(N_0=1\): center;
- \(N_1=6\): one active signed coordinate;
- \(N_2=12\): two active signed coordinates;
- \(N_3=8\): three active signed coordinates.

The outer shell is exactly

\[
\boxed{\{\pm1\}^3},
\]

which is in bijection with the eight vertices of a cube.

Status: **ISOMORPHISM** for the outer sign shell \(\{\pm1\}^3\leftrightarrow\) cube vertices; **EXACT COMBINATORICS** for the full \(27=1+6+12+8\) decomposition.

## 3. Exact ternary representation of oriented path support

Let \(G=(V,E)\) be an oriented graph.

For a simple path or simple cycle that traverses each edge at most once, define

\[
t_e=
\begin{cases}
+1,& \text{edge used in declared orientation},\\
0,& \text{edge absent from the path},\\
-1,& \text{edge used opposite to declared orientation}.
\end{cases}
\]

Then

\[
\mathbf t\in T_3^{|E|}.
\]

This is the standard signed edge-incidence coefficient restricted to multiplicities \(-1,0,+1\).

For a closed cycle and oriented incidence matrix \(B\),

\[
\boxed{B\mathbf t=0.}
\]

For edge phases \(\theta_e\), the loop phase is exactly

\[
\boxed{
\Phi_C
=
\sum_e t_e\theta_e
=
\mathbf t^T\boldsymbol\theta
\pmod{2\pi}.
}
\]

Writing

\[
U_e=e^{i\theta_e},
\]

the Wilson-loop factorization becomes

\[
\boxed{
W_C
=
e^{i\mathbf t^T\boldsymbol\theta}
=
\prod_e U_e^{t_e}.
}
\]

Thus the ternary coordinate has an exact operational meaning:

\[
+1\mapsto U_e,\qquad
0\mapsto 1,\qquad
-1\mapsto U_e^{-1}.
\]

Status: **EXACT_REPRESENTATION_ON_SECTOR**.

### Boundary

The full integer path/winding chain has coefficients

\[
n_e\in\mathbb Z.
\]

If an edge is traversed twice, \(n_e=2\), which is outside \(T_3\). Therefore the ternary carrier is not the full path algebra and is not closed under unrestricted path addition.

The exact scope is:

\[
\boxed{T_3^{|E|}\subset\mathbb Z^{|E|}}
\]

for signed support with edge multiplicity at most one.

A later coarse-graining from \(\mathbb Z\) to \(T_3\) must explicitly choose between sign, clipping, modulo-3, or another quotient. These choices are not equivalent.

## 4. Resonant Chemistry spectral trit witness

The Resonant Chemistry holonomy control includes a three-node ring with unit hoppings and loop flux

\[
\Phi=\frac{\pi}{2}.
\]

The tested spectrum is

\[
\boxed{\{-\sqrt3,\;0,\;+\sqrt3\}.}
\]

Define

\[
q_{\rm spec}(\lambda)=\frac{\lambda}{\sqrt3}.
\]

On this declared control spectrum,

\[
\boxed{
q_{\rm spec}:
\{-\sqrt3,0,+\sqrt3\}
\longleftrightarrow
\{-1,0,+1\}
}
\]

is a bijection.

Status: **EXACT_REPRESENTATION_ON_SECTOR** for this control Hamiltonian.

This does not imply that a generic molecular Hamiltonian has a ternary spectrum.

## 5. GREMLIN oriented-exchange spectral quotient

GREMLIN Hermitian Oriented Exchange v1.4 has spectrum

\[
\{-|E_R|,\;0,\;0,\;+|E_R|\}.
\]

For \(E_R\neq0\), define

\[
q_{\rm ex}(\lambda)=\frac{\lambda}{|E_R|}.
\]

Then the set of distinct eigenvalues maps exactly to

\[
\boxed{\{-1,0,+1\}.}
\]

However, the zero eigenvalue has multiplicity two.

Therefore \(q_{\rm ex}\) is exact as a spectral quotient but is not a bijection from the full state/eigenspace structure onto one trit.

Status: **EXACT_QUOTIENT**.

## 6. Spectroscopic response-sign quotient

For a declared observable \(\mathcal O\) and phase coordinate \(\Phi_a\), define a sign projection

\[
Q_\delta(x)=
\begin{cases}
-1,&x<-\delta,\\
0,&|x|\le\delta,\\
+1,&x>\delta.
\end{cases}
\]

Applied to a spectral response,

\[
t_{\alpha a}
=
Q_\delta
\left(
\frac{\partial\mathcal O_\alpha}{\partial\Phi_a}
\right),
\]

this gives a ternary response signature.

For exact symbolic mathematics, \(\delta=0\) yields the exact sign partition. For numerical or experimental data, \(\delta>0\) must be frozen from precision/noise before classification.

A chemically common-mode perturbation supplies an exact null example:

\[
\Delta E_m=\Delta E_n
\quad\Longrightarrow\quad
\Delta\omega_{mn}=0.
\]

Thus the three classes can be interpreted operationally as:

- \(-1\): negative differential response;
- \(0\): null/unresolved/common-mode response;
- \(+1\): positive differential response.

Status: **EXACT_QUOTIENT** of the declared continuous observable; magnitude information is intentionally discarded.

## 7. Three-channel Stella from spectroscopy

For three independently declared response coordinates,

\[
\mathbf t=(t_1,t_2,t_3)\in T_3^3,
\]

the response-class space is exactly the \(27\)-state Stella.

The shell count has a direct measurement interpretation:

- \(1\): all three channels null;
- \(6\): exactly one channel resolved, with either sign;
- \(12\): exactly two channels resolved, each with either sign;
- \(8\): all three channels resolved, with all sign combinations.

The eight fully active sign states are exactly

\[
(\pm1,\pm1,\pm1).
\]

Status: **EXACT COMBINATORIAL REPRESENTATION** after the three response coordinates and quantizer are declared.

The remaining scientific question is whether a particular three-channel choice is useful, sufficient, and stable under noise.

## 8. PhaseNav pair algebra cross-check

PhaseNav Telescope Vector Schema V2 contains symmetric and antisymmetric eigenspaces of an involution with eigenvalues

\[
+1,\qquad -1.
\]

This supplies a native signed two-sector decomposition.

A third value \(0\) can arise only after an additional null/inactive/projection rule is declared. The involution alone is not a three-eigenvalue operator.

Therefore the direct identification

\[
\text{PhaseNav pair algebra}\cong T_3
\]

is not currently justified.

Status: **ANALOGY / CONDITIONAL QUANTIZER**, not an isomorphism.

## 9. Memory-ontology interpretation

The strongest current use of the ternary carrier is as a discrete path/topology skeleton.

For a memory edge define, provisionally,

\[
m_e=(t_e,a_e,\theta_e),
\]

where:

- \(t_e\in T_3\): support/orientation class;
- \(a_e\): continuous or quantized strength/reinforcement;
- \(\theta_e\): phase/relational coordinate when the richer representation requires it.

This factorization prevents the ternary layer from pretending to preserve information that actually resides in amplitude or phase.

For simple procedural routes, \(t_e\) can represent path support and orientation exactly, while \(a_e,\theta_e\) retain richer dynamical information.

Status: **CANDIDATE MEMORY REPRESENTATION**, grounded by exact cross-domain substructures but not yet benchmarked as a full memory backend.

## 10. Balanced ternary versus \(\mathbb F_3\)

Signed routing semantics and finite-field arithmetic must remain distinct.

Balanced labels use

\[
-1,0,+1
\]

with ordinary signed interpretation.

In

\[
\mathbb F_3,
\]

one has

\[
1+1=-1.
\]

For path composition, traversing an edge twice should not automatically mean traversing it once in reverse. Therefore \(\mathbb F_3\) is not automatically the correct path algebra.

Current default:

\[
\boxed{\text{signed ternary for routing/sign support}}
\]

while

\[
\boxed{\mathbb F_3}
\]

remains a separate algebraic backend candidate to test only where modulo-3 closure is semantically correct.

## 11. Resolved TODO items

The following v0.1 questions are partially resolved.

### RESOLVED — combinatorics

\[
3^3=27=1+6+12+8
\]

is exact.

### RESOLVED — eight outer configurations

The eight fully active states are exactly

\[
\{\pm1\}^3.
\]

### RESOLVED ON DECLARED SECTOR — graph routing

Simple oriented path/cycle support has an exact ternary representation.

### RESOLVED WITNESS — chemistry spectrum

A declared Resonant Chemistry three-ring control has an exact normalized ternary spectrum.

### RESOLVED QUOTIENT — GREMLIN exchange

The GREMLIN oriented-exchange spectrum has an exact normalized three-value quotient.

## 12. Remaining TODO gates

The following remain open and must be tested before any promotion of a ternary memory backend.

1. **Composition law**
   - decide how repeated traversal and winding leave \(T_3\);
   - compare integer-count, sign, saturating, and modulo-3 semantics.

2. **Information-loss audit**
   - quantify information lost by
     \[
     R_Q\rightarrow R_{T_3}.
     \]

3. **Behavioral equivalence**
   - evaluate
     \[
     d_H(R_Q,R_{T_3})\le\varepsilon
     \]
     for declared memory tasks.

4. **Resource benchmark**
   - compare
     \[
     R_Q\rightarrow R_{T_3}\rightarrow R_B
     \]
     against direct
     \[
     R_Q\rightarrow R_B.
     \]

5. **Procedural-memory benchmark**
   - route completion;
   - consolidation;
   - interference;
   - transfer;
   - forgetting;
   - recovery after partial deletion.

6. **Stella-shell utility**
   - test whether the \(1/6/12/8\) shell decomposition improves routing, indexing, or anomaly detection over simpler sign vectors.

7. **Noise stability**
   - freeze \(\delta\) before evaluation;
   - measure class flips under noise and nuisance perturbations.

8. **Cross-domain adapter**
   - specify when a chemical/spectral trit is the same typed object as a memory-routing trit rather than merely sharing the same alphabet.

9. **Composite Stella trit**
   - keep OPEN;
   - only define it if an explicit microstate-to-logical-state map yields measurable benefit.

## 13. Current verdict

The original ternary intuition is no longer wholly untested.

The current defensible statement is

\[
\boxed{
\text{exact ternary substructures exist across graph routing and selected spectral quotients}
}
\]

while

\[
\boxed{
\text{a universal ternary memory representation remains OPEN}.
}
\]

The ternary layer should therefore be treated as a candidate discrete skeleton between a richer quantum-native representation and binary storage, with exactness asserted only on the declared sectors above.
