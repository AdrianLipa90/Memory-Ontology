# Behavioral/Historical Signature Split and Certified Core — v0.4

Status: **FINAL V0.4 CANDIDATE / WITNESS-GATED CORE / READY FOR MAIN**

This closes the remaining semantic gap between provenance identity and
behavioral invertibility.

## Two signatures

Every typed morphism now exposes two projections.

Behavioral signature:

```text
source/target
observable + distance
exact rational error bound
horizon
source/target sectors
invariant preservation
declared local invertibility
domain totality
```

Historical signature adds:

```text
ordered prime lineage
prime history code
provenance preservation
metric witness lineage
sector witness lineage
```

The existing `canonical_signature()` remains an alias for the historical
signature for backward compatibility.

Therefore two arrows may satisfy

[
B(f)=B(g)
]

while

[
H(f)
e H(g).
]

This is intentional: declared behavior can agree while provenance differs.

## Certified behavioral core

The implementation does not infer invertibility from the boolean
`invertible_on_declared_image` alone.

A non-identity arrow enters the certified behavioral core only through an
explicit inverse-pair witness that verifies:

1. reversed source/target objects;
2. reversed declared sectors;
3. matching behavioral observable and distance;
4. exact zero error in the present v0.4 core;
5. invariant/provenance admission;
6. both left and right identity laws;
7. domain/image compatibility.

Object identities are always included.

An arrow marked invertible but lacking an inverse witness is reported as
`excluded_unwitnessed_invertible`.

The resulting object is a **certified under-approximation** of the maximal
categorical core; no maximal-core claim is made.

## Collatz validator

The Collatz behavioral path-groupoid provides one concrete inverse validator.

A witness is issued only after the tested laws

[
p^{-1}circ p=1,
qquad
pcirc p^{-1}=1
]

hold on the actual validated finite path.

The raw prime lineage remains in the historical layer. The behavioral quotient
may reduce exact backtracking to identity without deleting historical
provenance from the source layer.

## Compatibility correction

The corrected groupoid classifier retains the historical API key

`retained_history_collatz_sector`

as a compatibility alias, while the precise key is

`behavioral_reduced_collatz_sector`.

The alias is explicitly documented as referring to the reduced behavioral
groupoid; raw provenance remains in `collatz_history_quotient_v04`.

## Final targeted gate

Local targeted v0.4 gate:

```text
63 passed, 0 failed
elapsed: 0.71 s
```

Coverage in this gate:

- Prime–Hilbert association/dissociation;
- accelerated Collatz finite-history reversal;
- exact-rational representation-category associativity;
- metric/sector witnesses;
- reduced behavioral Collatz path groupoid;
- raw-history -> behavioral quotient;
- behavioral/historical signature separation;
- witness-gated certified behavioral core.

This local gate reconstructs the branch logic from the current GitHub source
and is not represented as a GitHub Actions receipt.

## Claim boundary

Supported:

- explicit separation of behavioral and historical signatures;
- witness-gated certified invertible subcategory;
- Collatz finite-path inverse witness;
- preservation of provenance outside the behavioral quotient;
- backward-compatible classifier key.

Not claimed:

- maximal invertible core of every possible representation arrow;
- global action groupoid;
- Collatz convergence;
- infinite-history completion;
- physical quantum or ternary substrate.
