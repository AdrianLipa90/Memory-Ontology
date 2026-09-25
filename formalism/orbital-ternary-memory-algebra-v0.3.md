# Orbital–Ternary Memory Algebra — v0.3

Status: **GREMLIN_SYNTHESIS_CANDIDATE / EXACT_SECTOR_BRIDGE / NO_MAIN_MERGE**

This document combines two previously independent Memory-Ontology branches:

- `feat/orbital-holographic-memory-stack-v0.2-20260925`
- `feat/ternary-cross-domain-audit-v0.2-20260925`

The synthesis was routed through the GREMLIN specialist contract:
SPIDER for structural overlap, RAVEN for cross-formalism bridges, MOLE for
algebraic reduction, HOUND for mismatch boundaries and MANTIS for
falsification.

## 1. Exact shared object

Let the typed memory graph be

\[
G=(V,E,\mathcal R,\mathcal O,\mathcal B).
\]

The orbital branch leaves the path coordinate \(\Gamma\) abstract. The
ternary branch supplies an exact signed-support representation for simple
oriented paths and cycles:

\[
T_E
=
\{t\in\mathbb Z^{|E|}:t_e\in\{-1,0,+1\}\}.
\]

The inclusion

\[
\iota:T_E\hookrightarrow C_1(G;\mathbb Z)\cong\mathbb Z^{|E|}
\]

is exact.

Therefore an orbital path signature may be represented exactly by \(t\in T_E\)
whenever each oriented edge has multiplicity at most one.

## 2. Boundary algebra

Let \(B\) be the oriented vertex-edge incidence matrix.

The boundary operator is

\[
\partial t=Bt.
\]

The exact ternary cycle sector is

\[
Z_T(G)=T_E\cap\ker B.
\]

Thus

\[
Bt=0
\]

is the algebraic closure condition for a signed simple cycle.

This connects Memory Ontology path/topology memory directly to the ternary
audit without introducing a new physical assumption.

## 3. The crucial non-closure and typed overflow

The ternary sector is not closed under unrestricted path addition:

\[
1+1=2\notin T_3.
\]

GREMLIN/HOUND therefore rejects modulo-3, clipping and saturation as silent
default composition rules.

Define typed partial composition

\[
t\boxplus u=
\begin{cases}
t+u\in T_E,&\|t+u\|_\infty\le1,\\
\operatorname{Lift}_{\mathbb Z}(t+u)
\in C_1(G;\mathbb Z),&\text{otherwise}.
\end{cases}
\]

The result either remains in the exact ternary sector or is promoted to the
full integer winding chain. No information is silently discarded.

This is the central algebraic bridge between the two branches.

## 4. U(1) holonomy character

Assign edge phases

\[
\theta=(\theta_e)_{e\in E}.
\]

On the full integer chain define

\[
\chi_\theta(n)
=
\exp\!\left(i n^T\theta\right)
\in U(1).
\]

This is a group character:

\[
\chi_\theta(n+m)
=
\chi_\theta(n)\chi_\theta(m).
\]

Restricted to composable ternary paths it remains exact.

The orbital phase coordinate is therefore not an independent placeholder on
this sector. It can be derived as

\[
\boxed{
\phi(t)=
\arg\chi_\theta(t)
=
t^T\theta\pmod{2\pi}.
}
\]

This identifies the ternary audit's Wilson-loop formula with the orbital
branch's cyclic phase coordinate.

## 5. Refined orbital address

On the exact sector define

\[
\boxed{
\mathcal A_T(m)
=
(Q,t,\mathcal O,\phi(t),s,B,\Pi)
}
\]

with

\[
t\in T_E,
\qquad
\phi(t)=t^T\theta\pmod{2\pi}.
\]

When composition overflows the ternary sector, the same address lifts to an
integer-winding path:

\[
\mathcal A_{\mathbb Z}(m)
=
(Q,n,\mathcal O,\phi(n),s,B,\Pi),
\qquad n\in\mathbb Z^{|E|}.
\]

Thus ternary is a typed exact sector of the orbital address, not a replacement
for the full path algebra.

## 6. Stella ↔ PhaseNav exact seam

The orbital PhaseNav profile already contains the outer sign shell

\[
\Sigma=\{\pm1\}^3.
\]

The ternary branch defines

\[
\mathcal S_3=T_3^3
\]

with shell decomposition

\[
27=1+6+12+8.
\]

The eight-point outer shell is exactly

\[
N_3=\{\pm1\}^3.
\]

Therefore

\[
\boxed{\Sigma\cong N_3}
\]

by the identity map on the three signs.

This is an exact isomorphism of the outer sign code only. It does not prove
that the full PhaseNav algebra is ternary. The center/axis/edge Stella states
add explicit zero/inactive coordinates that require typed semantics.

## 7. Holographic projection and reconstruction

The orbital-holographic branch reconstructs a memory from compatible
projections preserving a declared invariant.

A ternary projection may therefore be admitted as one member of a projection
family only when its typed map preserves the requested invariant:

\[
d\left(
\mathcal I(m),
\mathcal I(\pi_T(m))
\right)
\le\varepsilon.
\]

For the exact simple-path sector the signed support/orientation and induced
holonomy are preserved exactly.

Magnitude, repeated winding and other information outside that sector require
the integer lift or a separate approximation contract.

The epistemic states remain unchanged:

\[
\text{RECALLED}
\neq
\text{RECONSTRUCTED}
\neq
\text{INFERRED}
\neq
\text{IMAGINED}.
\]

## 8. GREMLIN cross-branch relation result

Observed exact links:

1. PhaseNav outer sign shell \(\Sigma\) ↔ Stella corner shell: **ISOMORPHISM**.
2. Signed ternary path sector \(T_E\) → integer chain space: **EXACT INCLUSION**.
3. \(Bt=0\): **EXACT CYCLE CONSTRAINT**.
4. \(\chi_\theta(t)=e^{it^T\theta}\): **EXACT U(1) HOLONOMY ON SECTOR**.
5. \(\Gamma\leftrightarrow t\) for edge multiplicity ≤1:
   **EXACT REPRESENTATION ON SECTOR**.
6. Orbital \(\phi\) = ternary path-phase pairing on that sector:
   **EXACT REPRESENTATION ON SECTOR**.

Candidate synthesis:

\[
\mathcal A(m)
\longrightarrow
\mathcal A_T(m)
\longrightarrow
\mathcal A_{\mathbb Z}(m)
\]

with fail-loud typed overflow.

## 9. Firewalls

The synthesis does **not** assert:

- closure of \(T_3^E\) under unrestricted path addition;
- a default \(\mathbb F_3\) path algebra;
- a physical ternary substrate;
- a physical quantum substrate;
- that the Stella zero coordinate is already part of canonical PhaseNav;
- that outer-shell isomorphism proves full-algebra isomorphism;
- that a ternary projection preserves observables not included in its contract.

## 10. Current implementation gate

Reference implementation:

`algebra/orbital_ternary_memory_algebra.py`

Targeted local validation:

```text
14 passed, 0 failed
```

The tests cover shell combinatorics, outer-shell mapping, typed overflow,
boundary/cycle behavior, U(1) character composition, phase reversal,
phase-wrap canonicalization and exact-sector orbital projection.
