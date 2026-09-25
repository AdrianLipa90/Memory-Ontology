CORRECTION NOTE: this document describes the reduced behavioral path groupoid. Raw retained provenance is modeled separately in formalism/collatz-history-behavior-quotient-v0.4.md and is not erased by inverse cancellation.\n\n# Collatz Retained-History Path Groupoid — v0.4

Status: **EXACT FINITE PATH GROUPOID CANDIDATE / NO GLOBAL ACTION CLAIM / NO MAIN MERGE**

This module refines the Prime–Hilbert–Collatz association/dissociation algebra.

The key correction is that a Collatz branch valuation alone is not an inverse
identifier: different Collatz edges can share the same valuation
\(a=v_2(3n+1)\). Cancellation is therefore admitted only after exact
state-transition validation.

## Signed history alphabet

For branch valuation \(a\ge1\), encode forward and inverse traversal as

\[
\tau(a,+)=2a-1,
\qquad
\tau(a,-)=2a.
\]

A finite signed history is an ordered positive-integer word and therefore has
the positional prime address

\[
G(h)=\prod_j p_j^{\tau_j}.
\]

This preserves order and orientation.

## Objects and arrows

Objects are positive odd integers.

A forward generator is the exact accelerated odd-Collatz edge

\[
n\xrightarrow{a}u,
\qquad
u=\frac{3n+1}{2^a},
\quad
a=v_2(3n+1).
\]

Its formal inverse is admitted only on that edge image:

\[
u\xrightarrow{a^{-1}}n,
\qquad
n=\frac{2^a u-1}{3},
\]

with forward revalidation.

A path is a finite composable signed sequence of such validated traversals.

## Composition and reduction

Composition concatenates paths and then removes only adjacent exact
edge/inverse-edge pairs.

Two equal valuation labels do not cancel merely because their \(a\) values
match. Source/target reversal and opposite orientation are also required.

The tested laws are:

\[
(h\circ g)\circ f
=
h\circ(g\circ f),
\]

\[
p^{-1}\circ p=1_{s(p)},
\qquad
p\circ p^{-1}=1_{t(p)}.
\]

Declared-cut dissociation is checked against the positional-prime history
code and recomposes exactly.

## Classification

The retained-history Collatz sector is best classified as a **path groupoid on
valid finite signed Collatz paths**.

It is not promoted to an action groupoid because no single globally defined
group action has been established; inverse admissibility is state/branch
dependent.

It is also not claimed to be the maximal core of the full Memory
Representation Category. It is a certified subgroupoid candidate inside that
core after objects/sectors are restricted to valid path domains/images.

Lossy holographic projections remain outside this reversible fragment.

## Validation

Targeted unit/property gate:

```text
14 passed, 0 failed
```

Additional randomized adversarial gate:

```text
5000 composable random triples: PASS
5000 inverse-law checks per segment family: PASS
100 witnesses with repeated equal valuation but non-inverse direction:
no false cancellation
elapsed ~13.77 s
```

## Firewalls

- no Collatz convergence claim;
- no global groupoid claim for all representation morphisms;
- no action-groupoid claim;
- no maximal-core claim;
- no physical quantum claim.
