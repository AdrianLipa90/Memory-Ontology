# Memory Representation Category — v0.4

Status: CANDIDATE / ASSOCIATIVITY-GATED / PRIME-HISTORY / NO_MAIN_MERGE

v0.4 closes three explicit gaps left by the v0.3 HOUND audit.

## Ordered lineage

Each non-identity generator receives a positive role code. The ordered lineage

\[
\ell(f)=(c_1,\dots,c_k)
\]

is encoded through the v0.4 Prime-Hilbert word address

\[
G(\ell)=\prod_j p_j^{c_j}.
\]

Composition concatenates lineage rather than collapsing it to a single lossy
role label. Identity arrows use the empty word.

## Exact error algebra

The first adversarial run found a real implementation failure:

\[
(0.01+0.02)+0.03=0.06,
\]

while the other floating-point parenthesization produced
0.060000000000000005.

v0.4 therefore stores error bounds as exact non-negative rational values
using Python Fraction.

## Metric composition authority

For two non-identity arrows, error bounds are not added unless the caller
provides an explicit MetricCompositionWitness for the declared distance.

Only then is the triangle-style bound

\[
\varepsilon_{g\circ f}
\le
\varepsilon_f+\varepsilon_g
\]

admitted.

## Partial-sector compatibility

Every arrow declares source and target sectors.

Automatic composition requires

\[
S_{\rm target}(f)=S_{\rm source}(g).
\]

A mismatch requires an explicit SectorCompatibilityWitness; no implicit
GENERAL wildcard is inserted.

## Associativity gate

For composable arrows with compatible typed contracts and explicit witnesses,
the two parenthesizations

\[
h\circ(g\circ f)
\quad\text{and}\quad
(h\circ g)\circ f
\]

produce the same full canonical signature, including:

- exact rational error bound;
- horizon;
- source/target sector;
- ordered lineage and prime history code;
- invariant/provenance flags;
- invertibility/totality flags;
- witness lineage.

## Dissociation

The prime history code admits exact declared-cut dissociation of the composite
lineage. This recovers provenance components; it is not by itself an inverse
map on represented data.

Actual inverse dynamics require an inverse witness. The companion
Prime-Hilbert-Collatz module supplies one exact finite-history example.

## Invertibility firewall

Composition never creates invertibility. A lossy projection remains
noninvertible even if another component is locally reversible.

History-preserving dynamic sectors may remain locally invertible on their
declared image.

## Test result

First adversarial category run:

30 passed, 1 failed

Failure: floating-point parenthesization mismatch.

After exact rational correction:

31 passed, 0 failed

Combined suite consists of 16 association/dissociation tests and 15 v0.4
category tests.

## Claim boundary

Supported:

The implemented finite typed representation-morphism class has explicit
identities and associative canonical composition when its declared metric and
sector witnesses exist.

Not established:

- arbitrary mathematical category theorem;
- global groupoid;
- automatic triangle inequalities;
- automatic sector embeddings;
- invertibility of lossy projections;
- infinite-history completion;
- Collatz convergence.
