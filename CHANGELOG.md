# Changelog

This file is append-only.

## 2026-09-25 — v0.1

Initial formalization of Memory Ontology.

Added:

- candidate domain-general law of memory;
- EVENT → TRACE → PATH → STRUCTURE → LAW ontological chain;
- six retained-object primitives: state, relation, path, topology, operator, boundary;
- independent taxonomy axes for persistence, access, plasticity, dynamical effect and inter-layer coupling;
- explicit separation of procedural/semantic/episodic categories from implicit/explicit access modes;
- generic procedural-memory representation as a metastable path/topology structure;
- machine-readable JSON schema and example;
- dependency-free repository contract tests;
- explicit epistemic boundary between substrate-neutral formalism and physical quantum implementation claims.


### Representation-duality extension

Added:

- formal separation of memory law, representation and physical substrate;
- quantum-native and binary representation families;
- (epsilon, H)-behavioral equivalence criterion;
- Q→B binaryization compiler contract;
- Pareto resource frontier for minimal binaryization cost;
- explicit-amplitude Theta(2^n p) storage baseline with an explicit warning that it is not a universal classical lower bound;
- representation evidence regimes from PARITY through theoretical separation, with physical-substrate necessity kept separate;
- fail-loud binaryization benchmark specification;
- machine-readable representation profile and validation test;
- current project position: substrate-neutral law + quantum-native current representation + binaryizability open.


### Ternary/Stella intuition TODO

Recorded a non-canonical research TODO for later validation:

- classical balanced-ternary layer `{-1,0,+1}` as a possible coarse representation between Q-native and binary backends;
- clarification that one standard trit has 3 states, while three trits have 27 states;
- decomposition `27 = 1 + 6 + 12 + 8`, with the 8 outer sign configurations given by `(±1,±1,±1)`;
- explicit allowance for a future project-specific composite "Stella trit" only if its coarse-graining map is defined;
- benchmark questions for information loss, routing utility, compression, and cost versus direct binaryization.

Status: UNTESTED INTUITION / TODO; no quantum-advantage or physical-substrate claim.

## 2026-09-25 — v0.2 branch: orbital-holographic memory stack

Added:

- orbital relational address \(\mathcal A(m)=(Q,\Gamma,\mathcal O,\phi,s,B,\Pi)\);
- holographic projection/reconstruction contract based on shared invariants rather than single-node authority;
- explicit RECALLED / RECONSTRUCTED / INFERRED / IMAGINED separation;
- provenance gate forbidding imagined candidates from being silently promoted to historical recall;
- dependency-free reference reconstruction kernel;
- optional PhaseNav directed RGB± phase profile;
- explicit eight-octant sign-code interpretation \(\{\pm1\}^3\) as a representation cardinality, not a physical flavor claim;
- GREMLIN integration contract for ingest, graph correlation, reconstruction, candidate completion, verification and receipts;
- machine-readable holographic-memory profile and formal example;
- v0.2 invariant tests.

Epistemic boundary: orbital/holographic is a computational representation formalism here. Physical Aharonov-Bohm, neutrino, FTL/nonlocality or cosmological bindings remain separate hypotheses requiring independent evidence.


### Ternary/Stella cross-domain audit v0.2

Integrated the independent ternary audit line into the synthesis branch.

Added:

- exact 27-state Stella combinatorics with 1+6+12+8 shell decomposition;
- exact outer-shell bijection \(\{\pm1\}^3\leftrightarrow\) cube vertices;
- exact signed-ternary representation of simple oriented path/cycle support;
- exact Wilson-loop factorization on the edge-multiplicity-≤1 sector;
- fail-loud non-closure warning for unrestricted path addition;
- explicit distinction between signed ternary semantics and \(\mathbb F_3\);
- source-bound audit receipt and contract tests.

Status: EXACT_SUBSTRUCTURES_IDENTIFIED / FULL_TERNARY_MEMORY_BACKEND_OPEN.


## 2026-09-25 — v0.3 branch: GREMLIN orbital–ternary algebraic synthesis

Combined the previously independent orbital-holographic and ternary/Stella
branches on a new feature branch without mutating main.

GREMLIN/SPIDER/RAVEN/MOLE synthesis identified:

- exact inclusion \(T_3^E\subset\mathbb Z^E\) for signed path support;
- boundary operator \(Bt\) and exact ternary cycle sector;
- exact U(1) character \(\chi_\theta(n)=\exp(i n^T\theta)\);
- exact path-to-orbital phase bridge \(\phi=t^T\theta\pmod{2\pi}\);
- exact isomorphism between PhaseNav \(\{\pm1\}^3\) and the Stella corner shell;
- typed partial ternary composition with exact overflow lift into integer winding chains;
- explicit rejection of silent modulo-3, clipping and saturation defaults.

Reference algebra and 14 targeted tests added.

Status: CANDIDATE_SYNTHESIS / EXACT_SECTOR_BRIDGE / NO_MAIN_MERGE.


### v0.3 representation-category + holographic bridge

Added:

- category over Memory Ontology with explicit representation fibers;
- typed partial representation morphisms with observable, error, horizon,
  invariant and provenance contracts;
- fail-loud rejection of a global group/groupoid interpretation;
- exact local groupoid fragment for the PhaseNav outer-shell / Stella
  corner-shell isomorphism;
- executable adapter from signed-ternary orbital projections into the existing
  holographic reconstruction kernel;
- partial-reconstruction arrows only after support/provenance gates pass;
- 23/23 fresh local integration tests on a byte-identical copy of branch
  `orbital_reconstruction.py` (Git blob
  `e797576042d876a289c61c1815b5f0aedf64172f`).

Status: CANDIDATE_ONLY / NO_MAIN_MERGE.
