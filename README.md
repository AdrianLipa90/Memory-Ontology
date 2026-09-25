# Memory Ontology

A substrate-neutral formal ontology and taxonomy of memory.

## Core proposal

Memory is modeled as a persistent, history-dependent modification of the structure that governs future transitions.

For a system with active state \(X_t\), memory state \(M_t\), and input \(u_t\),

\[
X_{t+1}=F(X_t,u_t;M_t), \qquad
M_{t+1}=U(M_t,X_t,u_t).
\]

A memory trace is present when past interaction changes \(M_t\), that change persists over a non-zero timescale, and intervening on \(M_t\) changes future reachable trajectories.

Equivalent geometric form:

\[
\mathcal G_{t+\Delta}= \mathcal U(\mathcal G_t,\Gamma_t),
\]

where \(\Gamma_t\) is the traversed history and \(\mathcal G_t\) is the current relational/transition structure.

## Ontological hierarchy

\[
\text{EVENT} \rightarrow \text{TRACE} \rightarrow \text{PATH} \rightarrow \text{STRUCTURE} \rightarrow \text{LAW}.
\]

The repository deliberately separates ontology, taxonomy, domain mappings, formalism, and machine-readable schemas/examples.

## Important distinction

Terms such as **procedural**, **semantic** and **episodic** primarily classify the object/organization of memory. Terms such as **implicit** and **explicit** classify access mode. They therefore do not belong on one flat taxonomic tree.

## v0.1 axes

A memory instance is represented approximately as

\[
M=(Q,\tau,A,P,E,C),
\]

where:

- \(Q\) — retained object: state, relation, path, topology, operator or boundary/context;
- \(\tau\) — persistence timescale/class;
- \(A\) — access mode;
- \(P\) — plasticity/update mode;
- \(E\) — effect on future dynamics;
- \(C\) — coupling to other memory layers.

## Repository layout

- formalism/memory-law-v0.1.md — candidate domain-general memory law and operational criteria.
- ontology/memory-ontology-v0.1.md — ontological primitives and hierarchy.
- taxonomy/memory-taxonomy-v0.1.md — multi-axis classification.
- cross_domain/classical-memory-map-v0.1.md — mapping of conventional memory terms.
- schemas/memory-object.schema.json — machine-readable v0.1 schema.
- examples/procedural-memory.json — procedural-memory instance.
- tests/test_repository_contract.py — dependency-free structural validation.
- CHANGELOG.md — append-only change record.

## Epistemic status

Version 0.1 is a formal research proposal. The substrate-neutral definition is intended to be testable across physical, biological and computational realizations. A quantum-native representation may be used in implementations, but physical quantum memory is **not** assumed by the core ontology and requires independent evidence.

## Author

Adrian Lipa
