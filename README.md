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

The repository deliberately separates ontology, taxonomy, domain mappings, formalism, representation, and machine-readable schemas/examples.

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

Representation is deliberately **not** folded into this tuple. The same abstract memory object may have several representations.

## Representation duality

The current project representation may be quantum-native while the memory law remains substrate-neutral.

For a quantum-native representation \(R_Q\), a binary realization \(R_B\) is accepted as an equivalent binaryization only when it preserves a declared task-relevant behavioral contract:

\[
d_H(R_Q,R_B)\le\varepsilon.
\]

The central open quantity is the minimal binaryization resource frontier

\[
\mathbf C_{\mathrm{bin}}^{*}(\varepsilon,H;R_Q).
\]

This prevents two opposite errors: assuming quantum-native notation proves a physical quantum substrate, or assuming the naive \(2^n\) explicit-amplitude expansion is the optimal classical realization. Structured state families may admit sparse, factored, symbolic or otherwise compressed binary representations. Quantum-native advantage is therefore treated as a benchmarkable claim.

## Repository layout

- formalism/memory-law-v0.1.md — candidate domain-general memory law and operational criteria.
- formalism/representation-duality-v0.1.md — Q-native↔binary equivalence and binaryization-cost formalism.
- ontology/memory-ontology-v0.1.md — ontological primitives and hierarchy.
- taxonomy/memory-taxonomy-v0.1.md — multi-axis classification.
- cross_domain/classical-memory-map-v0.1.md — mapping of conventional memory terms.
- cross_domain/ternary-stella-cross-domain-audit-v0.2.md — exact/quotient/analogy audit across GREMLIN, chemistry and spectroscopy.
- benchmarks/binaryization-benchmark-spec-v0.1.md — fail-loud comparison protocol.
- schemas/memory-object.schema.json — machine-readable memory-object schema.
- schemas/representation-profile.schema.json — representation/evidence contract.
- examples/procedural-memory.json — procedural-memory instance.
- examples/representation-duality.json — current quantum-native representation profile.
- tests/test_repository_contract.py — memory-object structural validation.
- tests/test_representation_contract.py — representation-contract validation.
- tests/test_ternary_cross_domain_contract.py — dependency-free ternary/Stella exact-sector checks.
- provenance/TERNARY_CROSS_DOMAIN_AUDIT_V0_2.json — source-bound cross-domain audit receipt.
- todo/ternary-stella-intuition-v0.1.md — partially resolved ternary/Stella research queue and open promotion gates.
- CHANGELOG.md — append-only change record.

## Epistemic status

Version 0.1 is a formal research proposal. The substrate-neutral definition is intended to be testable across physical, biological and computational realizations.

Current position:

\[
\boxed{\text{substrate-neutral law}+\text{quantum-native current representation}+\text{binaryizability open}}
\]

Physical quantum necessity is not assumed. It is a separate empirical claim. Likewise, representation advantage is not inferred from superposition alone: it must survive strong binary baselines under matched accuracy, horizon, observable contract, and readout/sampling costs.

## Author

Adrian Lipa
