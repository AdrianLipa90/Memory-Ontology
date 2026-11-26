# PNCS memory grammar / PNLF state-space integration v0.2

Author direction: PNCS/PNV only for target program semantics. 2026-11-26. Candidate integration; no Python/JavaScript implementation added. No native execution, canonical promotion, or NOEMA mutation in this pass.

## Source authority (exact pinned revision)

PNCS repository revision 958d41402c3af4107856fccee849027aedfaad8d:
- [Hybrid Memory Grammar v0.3](https://github.com/AdrianLipa90/PhaseNav-Natural-Coding-System/blob/958d41402c3af4107856fccee849027aedfaad8d/spec/PNCS_HYBRID_MEMORY_GRAMMAR_V0_3.md)
- [Hybrid Grammar v0.2](https://github.com/AdrianLipa90/PhaseNav-Natural-Coding-System/blob/958d41402c3af4107856fccee849027aedfaad8d/spec/PNCS_HYBRID_GRAMMAR_V0_2.md)
- [PNLF Orbital Memory v0.1](https://github.com/AdrianLipa90/PhaseNav-Natural-Coding-System/blob/958d41402c3af4107856fccee849027aedfaad8d/spec/PNLF_ORBITAL_MEMORY_V0_1.md)
- [Existing procedural planner receipt](https://github.com/AdrianLipa90/PhaseNav-Natural-Coding-System/blob/958d41402c3af4107856fccee849027aedfaad8d/provenance/receipts/PNCS_MEMORY_GUIDED_PLANNER_PACKAGE_GATE_V0_3.json): 13 targeted tests passed; 10000 updates, same current-condition digest, a -> b, counterfactual -> a without factual mutation. This is upstream evidence only, not a new execution or proof of native acceleration.
- The v0.3 parser and v0.1 native PNV executor were inspected. Syntax and execution vocabularies are distinct. The experimental PNV semantic memory graph contains TRACE/BIND/ROUTING, which are not admitted opcodes of the narrow native executor. Do not copy them into executable PNV/1.

## Semantic bindings (source terms, NOT new KAKU IDs)

PNAML Mobile CLX2 TERM_INDEX.tsv and original shards 01,02,05,08 at source dictionary revision 5fe9daa5e2b4841e598628aa5a1a7beadb0e70b1. The CD address is not a PNCS operator or a KAKU content ID.

| Source ID | Term | CD address | Role here |
|---|---|---:|---|
| CLX2-TIME-005 | Memory Trace | 179 | History-bearing residue |
| CLX2-AGENCY-001 | Intention | 229 | Preferred future constraint |
| CLX2-AGENCY-002 | Will | 230 | Dynamic stability of intention |
| CLX2-TEMP-008 | Temporal Persistence | 366 | Duration of efficacy |
| CLX2-TEMP-014 | Episodic Memory | 372 | Contextual occurrence |
| CLX2-TEMP-017 | Prospective Memory | 375 | Intended future action/cue |
| CLX2-TEMP-018 | Procedural Memory | 376 | Acquired route/skill |
| CLX2-AGX-016 | Persistence | 491 | Maintaining goal/policy |
| CLX2-AGX-021 | Policy Revision | 496 | Evidence-bound revision |

No exact Determination or Sacrifice canonical match was located by the term-name search. Keep author postulates as candidates, not dictionary additions. Exact PNCS content realization and mass/36D binding remain unresolved; do not infer them from proximity, CD address or source name.

## State Memory and Liminal Memory

PNLF already defines S_i -- Lambda_i(tau) --> S_(i+1), immutable admitted checkpoints, append-only liminal revisions, TAU_FRAME=(PILOT_L,Lambda(tau),PILOT_R,T36), and independent functional M-layer and orbital O-band. Proposed mapping: a registered goal and cue may be retained as a present commitment; the history of goal pursuit, revised paths and verified allocation observations is represented by liminal revisions, not completed future events. PILOT_R remains unresolved until admitted; it need not equal the desired goal. Only reduction and consolidation witnesses create a new admitted checkpoint. A recall opens a new liminal trajectory instead of changing the archived checkpoint. Preserve object ID, segment ID, commitments, model identities, generation, and source/occurrence lineage. Store W_history and w_current in distinct typed relations; no claim that either is mass, binding energy or orbital band.

## Candidate programs

- [PNCS state-space declarations](../native/MEMORY_STATE_SPACE_V0_2.pncs): historical trace separate from learned geometry; implicit GUIDE, consolidation request; no PERSIST, no durable write. ROUTE is declared topology, not proof of traversal. No unconditional REINFORCE of a hypothetical route; a verified transition event is the input. The graph computations require actual admitted operator bindings.
- [PNCS prospective memory](../native/PROSPECTIVE_MEMORY_V0_3.pncs): explicit recall, latent cue-conditioned GUIDE, independent allocation occurrence and evidence-bound revision request. Commitment and its historical trace are separate. A cue is not proof of successful action. Runtime must check verified-source requirements before TRACE; syntax alone does not enforce causal timing. The current candidate takes observed allocation as input, not an outcome of the proposed route.
- [PNV observation gate](../native/MEMORY_CAUSAL_OBSERVATION_GATE_V0_1.pnv): uses only SOURCE, IDENTITY, COMPOSITION, ASSERT and EMIT; no invented transform or comparator binding. Checks matched context/state, distinct histories/memory/route, equality after no-trace interval and non-mutation of factual memory. Requires trusted, independently admitted observations with positive declared delay and a controlled memory-only intervention, and an observation contract appropriate to the memory. Equality after delay is a stronger special-case persistence witness, not a general definition. It cannot validate these experimental conditions or source truth solely from the submitted values; no claim of cryptographic or canonical admission.

All three are new authored source candidates. Manual source-grammar inspection, no native parser execution or interpreter receipt. Four v0.1 PNV transition candidates remain unbound; the new PNV gate reduces the binding surface for evidence checks but does not replace dynamics. No new runtime or callback implementation.

## Legacy diagnostic migration ledger

Previous branch Python files are historical test/diagnostic evidence. Do not use them as semantic authority and do not introduce additional Python. Native replacement still required before retiring each active file:
- fold_collatz_witness: exact arithmetic and inverse lineage; bind Collatz radical.
- pnaml_classical_isomorphism: source HTRI/QHTRI tangent and operator identities; bind existing QHTRI evidence.
- pnaml_closed_loop_memory_fixture: verified event/replay/causal effects; use memory grammar and PNLF receipts.
- pnaml_conditional_contraction, pnaml_joint_state_stability, pnaml_memory_metastability: source phase/weight evolution, stability and matched controls; require native Coupler observation receipts.
- pnaml_mori_zwanzig, pnaml_observability_cognitive_diagnostics: projection, kernel and observability contracts; require native operator and observation bindings.
- rdss_memory_mechanics_v32, rdss_relational_dynamics_v32 and two associated tests: TIR frame transport, relation structure and RDSS invariants; exact KAKU/RADICAL authoring and native conformance tests pending.

The existing diagnostic source/receipts remain available. No behavioral parity, exact 36D realization, registered native transform or native execution asserted. Next gate: actual PNCS admission and NOEMA producer observations, then run PNV observation gate and inverse lineage. Report access limitations before any change of technology.
