# Collatz History Category -> Behavioral Groupoid Quotient — v0.4

Status: **CORRECTION / TWO-LAYER MEMORY SEMANTICS / NO_MAIN_MERGE**

The earlier path-groupoid result is correct only after an explicit behavioral
reduction. Memory provenance must not be silently identified with behavioral
state identity.

## Historical layer

Let H_hist have positive odd integers as objects and raw validated signed
Collatz paths as arrows. Composition is literal history concatenation.

No inverse-pair deletion occurs. Therefore a forward traversal followed by the
exact reverse traversal returns to the same numerical state but remains a
non-empty historical loop. Its positional-prime provenance code remains
nontrivial.

## Behavioral quotient

Define a reduction map

q: H_hist -> G_beh

that removes adjacent exact edge/inverse-edge backtracking after state
validation.

Then a round-trip becomes identity only at the behavioral layer:

q(p^-1 o p) = 1.

The tested functor law is

q(g o_hist f) = q(g) o_beh q(f).

Thus the reduced path groupoid is a behavioral quotient, not the raw
provenance object.

## Memory-Ontology consequence

Two executions may have identical current state while carrying different
history:

state identity != history identity.

This explains the v0.4 representation-category split:

- ordered prime lineage belongs to the historical/provenance layer;
- invertibility belongs to the behavioral quotient;
- deleting lineage merely to force inverse laws would destroy memory evidence.

## Validation

Quotient tests:

    8 passed, 0 failed

Combined with reduced behavioral-groupoid tests:

    22 passed, 0 failed

The randomized quotient test contains 1000 composable path pairs.

## Corrected classification

H_hist -> G_beh

where H_hist is the raw history-preserving path category, G_beh is the reduced
Collatz path groupoid, and q is the exact-backtracking behavioral quotient.

No action-groupoid, maximal-core, Collatz-convergence, or physical-quantum
claim is made.
