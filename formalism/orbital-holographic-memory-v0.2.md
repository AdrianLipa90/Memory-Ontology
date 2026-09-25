# Orbital-Holographic Memory Formalism — v0.2

## 1. Scope

This document extends Memory Ontology v0.1 with a computational representation and reconstruction stack. It does not modify the substrate-neutral definition of memory.

The stack is:

\[
\text{ontology}\to\text{relational graph}\to\text{orbital address}\to\text{projections}\to\text{reconstruction}\to\text{candidate generation}\to\text{verification}.
\]

## 2. Relational graph

Let a memory-bearing structure be represented by a typed multigraph

\[
G=(V,E,\mathcal R,\mathcal O,\mathcal B),
\]

where \(V\) are entities/states, \(E\) are typed relations, \(\mathcal R\) contains relation classes, \(\mathcal O\) transformation/operators, and \(\mathcal B\) boundary/context constraints.

A memory object need not be identical to any single node.

## 3. Orbital address

For a memory object \(m\), define

\[
\boxed{\mathcal A(m)=(Q,\Gamma,\mathcal O,\phi,s,B,\Pi)}
\]

with:

- \(Q\): retained-object classes from Memory Ontology;
- \(\Gamma\): path/trajectory signature;
- \(\mathcal O\): orbital or equivalence class;
- \(\phi\in U(1)\): optional cyclic phase coordinate;
- \(s\): scale or hierarchy level;
- \(B\): boundary/context;
- \(\Pi\): provenance commitment.

The address is relational. Storage location is not part of identity unless a domain profile explicitly requires it.

For cyclic phase,

\[
\phi\sim\phi+2\pi k,\qquad k\in\mathbb Z.
\]

Equivalent addresses must canonicalize phase before hashing.

## 4. Holographic projection family

Let \(\pi_j(m)\) be projection \(j\) of memory \(m\). The projections may be stored in different graph neighborhoods, scales, encodings or representations.

A shared invariant is

\[
\mathcal I(m)=I(\pi_1(m),\ldots,\pi_n(m)).
\]

"Holographic" here means that the memory can be reconstructed from a sufficient compatible subset of distributed relational projections. It does not assert physical holography.

For an admissible surviving subset \(S\),

\[
\hat m=\operatorname{Reconstruct}(\{\pi_j(m):j\in S\})
\]

must preserve the declared invariant within tolerance \(\varepsilon\).

## 5. Reconstruction criterion

A deterministic baseline uses support over invariant commitments:

\[
\hat I=\arg\max_I\sum_{j\in S}w_j\mathbf 1[I_j=I].
\]

Reconstruction passes only when:

1. support count is at least \(k_{\min}\);
2. provenance commitments are structurally valid;
3. no conflicting invariant has equal or greater admissible support;
4. the output is labelled RECONSTRUCTED, not RECALLED.

Weighted or probabilistic variants may replace this baseline but must retain fail-loud ambiguity handling.

## 6. Four output classes

\[
\boxed{\text{RECALLED}\neq\text{RECONSTRUCTED}\neq\text{INFERRED}\neq\text{IMAGINED}}
\]

- RECALLED: backed by a verified historical receipt or equivalent domain evidence.
- RECONSTRUCTED: recovered from compatible persistent projections.
- INFERRED: derived from retained structure but not itself historically stored.
- IMAGINED: generated completion/candidate satisfying selected constraints.

An IMAGINED or INFERRED object MUST NOT be promoted to RECALLED without an independently verified provenance transition.

## 7. Fault tolerance

For projection set \(P_m\) and required support \(k_{\min}\), the simplest erasure tolerance is

\[
f_{\max}=|P_m|-k_{\min}.
\]

This is a representation-level property, not a universal bound. Correlated failures, shared dependencies and adversarial corruption require stronger coding and provenance models.

## 8. Fractal / multiscale representation

A memory may have projections at multiple graph scales

\[
G^{(0)},G^{(1)},\ldots,G^{(L)}.
\]

A scale map \(S_{a\to b}\) is admissible when the declared memory invariant is preserved:

\[
d\left(\mathcal I(G^{(a)}),\mathcal I(S_{a\to b}(G^{(a)}))\right)\le\varepsilon.
\]

Self-similarity is optional. The term orbital-fractal is reserved for profiles that explicitly define repeated scale maps.

## 9. Epistemic boundary

This formalism supports quantum-native representations, cyclic phase and interference-aware addressing. It does not by itself establish a physical quantum substrate, neutrino memory lattice, Aharonov-Bohm vacuum structure, FTL signalling, or physical holographic universe. Such bindings are separate hypotheses.
