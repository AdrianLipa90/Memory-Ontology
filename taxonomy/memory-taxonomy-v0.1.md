# Memory Taxonomy — v0.1

Memory is classified on independent axes rather than by one flat tree.

## Canonical tuple

\[
M=(Q,\tau,A,P,E,C)
\]

where \(Q\) is the retained-object set and the remaining coordinates describe persistence, access, plasticity, dynamical effect and coupling.

**Representation is not an intrinsic coordinate of this tuple.** A single abstract memory instance may be realized by quantum-native, binary, hybrid, biological, material or other representations. Representation is tracked by a separate profile so ontology is not confused with implementation.

## Axis 1 — Retained object \(Q\)

Non-exclusive values:

- state
- relation
- path
- topology
- operator
- boundary

A procedural skill, for example, will usually include path and topology, and may also include operator.

## Axis 2 — Persistence \(\tau\)

Suggested bins over a continuous timescale:

- ephemeral
- transient
- persistent
- structural
- effectively_invariant

These are operational categories, not different substances.

## Axis 3 — Access mode \(A\)

- direct — retained structure is directly addressable/readable within the modeled interface.
- reconstructive — access is obtained through reconstruction from distributed traces.
- implicit — memory changes behavior without direct retrieval of a represented record.
- latent — the trace exists but is not expressed under current conditions.

"Implicit" belongs here, not beside "procedural" as a peer memory type.

## Axis 4 — Plasticity/update mode \(P\)

- volatile
- adaptive
- consolidating
- append_only
- self_modifying

Multiple modes may apply over different timescales.

## Axis 5 — Effect on future dynamics \(E\)

- bias — changes preference/probability/cost.
- constraint — removes or restricts reachable transitions.
- attractor — draws dynamics toward a region or trajectory.
- routing — selects among possible transition paths.
- generative — contributes to construction of new states/structures.

## Axis 6 — Inter-layer coupling \(C\)

Memory layers form a coupled system rather than isolated stores.

For layers \(M_i\),

\[
\dot M_i=A_i+\sum_{j\neq i}C_{ij}B_{ij}.
\]

The graph of \(C_{ij}\) can represent fast-to-slow consolidation, slow-to-active reactivation, mutual reinforcement, inhibition, overwriting, gating and context-dependent routing.

## Representation profile — orthogonal to taxonomy

For implementation studies define a separate profile

\[
R=(\mathcal F,\varepsilon,H,\mathcal O,\mathbf C,\mathcal E),
\]

where:

- \(\mathcal F\) — representation family: quantum-native, binary, hybrid or substrate-neutral;
- \(\varepsilon\) — tolerated behavioral error;
- \(H\) — comparison horizon;
- \(\mathcal O\) — observable/query contract;
- \(\mathbf C\) — resource-cost vector;
- \(\mathcal E\) — evidence status.

This separation is required because "quantum-native" answers a different question from "procedural", "implicit" or "persistent".

## Derived classifications

Conventional labels should be represented as regions in this product space rather than single primitive nodes.

Examples:

- procedural memory: path/topology + usually persistent/structural + often implicit + routing/attractor;
- working memory: mostly state/relation + transient + direct/reconstructive;
- priming: usually relation/path + transient + implicit + bias.

## Open axes for later versions

Candidate future axes include provenance fidelity, reversibility, error-correction strength, redundancy, spatial distribution, energetic/action cost, confidence/evidence class and substrate binding. Compression is tracked primarily as a representation-cost property rather than an ontological primitive.
