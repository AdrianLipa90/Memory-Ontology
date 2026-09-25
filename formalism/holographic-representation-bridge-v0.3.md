# Holographic Representation Bridge — v0.3

Status: **EXECUTABLE_CANDIDATE / CROSS_BRANCH_RUNTIME_SEAM / NO_MAIN_MERGE**

This adapter makes the v0.3 representation category consume the existing
v0.2 holographic reconstruction kernel and the signed-ternary orbital
projection format.

## Flow

\[
\text{orbital/ternary exact-sector payload}
\to
\text{holographic projection}
\to
\text{existing reconstruction kernel}
\to
\text{typed partial RECONSTRUCTION morphism}.
\]

A signed-ternary orbital projection is admitted only when:

- its representation is explicitly `SIGNED_TERNARY_ORBITAL`;
- path coefficients lie in \(\{-1,0,+1\}\);
- provenance is non-empty;
- it does not self-assert physical substrate authority.

The existing reconstruction kernel remains the authority for support and
conflict classification.

A successful reconstruction creates a projection-bundle object and a partial

\[
\rho_S:P_S\rightharpoonup R(m)
\]

morphism. `INSUFFICIENT_EVIDENCE` and `CONFLICT` create no reconstruction
arrow.

## Fresh local integration gate

```text
23 passed, 0 failed
```

This gate contains:

- 12 representation-category tests;
- 11 holographic bridge tests.

It verifies reconstruction after partial projection loss, fail-loud conflict,
candidate-support exclusion, order-invariant provenance commitment and
authority boundaries.
