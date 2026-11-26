# PNCS/PNV native implementation policy and migration v0.1

Author direction, 2026-11-26: **PNCS/PNV, not JavaScript or Python.** PNCS is the semantic authority; PNV is the program representation. Do not introduce a replacement language or runtime without notifying the author before implementation. A host adapter or numerical validation environment is not semantic authority. No new Python or JavaScript implementation is introduced by this correction. Existing NOEMA, plugin and main branch are not modified.

## Source basis and status

Pinned PNCS source: [native PNV execution contract](https://github.com/AdrianLipa90/PhaseNav-Natural-Coding-System/blob/958d41402c3af4107856fccee849027aedfaad8d/spec/PNCS_NATIVE_PNV_EXEC_TOOL_V0_1.md), [authoring contract](https://github.com/AdrianLipa90/PhaseNav-Natural-Coding-System/blob/958d41402c3af4107856fccee849027aedfaad8d/spec/PNCS_GREMLIN_PNV_AUTHORING_V0_2.md), [executor source](https://github.com/AdrianLipa90/PhaseNav-Natural-Coding-System/blob/958d41402c3af4107856fccee849027aedfaad8d/src/phasenav_natural_code/native_pnv_exec_v01.py).

The admitted executor vocabulary is SOURCE, IDENTITY, DIFFERENCE, CONDITION, ORDER, TRANSFORM, COMPOSITION, RETURN with ASSERT and EMIT statements. TRANSFORM takes one resolved value and an admitted binding name, not arbitrary inline code. COMPOSITION constructs ordered input lists; it does not silently multiply, branch, or execute a formula. Exact KAKU realization, RADICAL content identities, operator lineage and canonical promotion must follow the original PNCS authoring contract; this migration assigns no invented canonical IDs or 36D vectors. No new opcode. The four programs below are authored PNV/1 candidates (CHYBA, READ_ONLY), checked against the source grammar and dependency ordering, not parsed or executed by the native interpreter in this session. All custom transform names below are **proposed unbound semantic contracts**, not claims of existing registered operators. No callback implementation in another language is authorized by this file. Native binding/admission and execution receipts are OPEN. Do not use arbitrary host callbacks to bypass PNCS.

## Replacement map

Historical prototype source is retained in Git history at the pre-migration commit [9591239b3991dec97a1d0c02ec1dc9c0634b0302](https://github.com/AdrianLipa90/Memory-Ontology/tree/9591239b3991dec97a1d0c02ec1dc9c0634b0302). Original receipts retain their real execution provenance; no historical JS result is relabeled PNV.

| Historical prototype (Git history) | Native PNV candidate | Evidence |
|---|---|---|
| memory_state_space_reference.mjs | [MEMORY_STATE_SPACE_V0_1](../native/MEMORY_STATE_SPACE_V0_1.pnv) | [receipt](../benchmarks/memory_state_space_reference_receipt.json) |
| imaginary_collatz_history_lift.mjs | [IMAGINARY_COLLATZ_HISTORY_V0_1](../native/IMAGINARY_COLLATZ_HISTORY_V0_1.pnv) | [receipt](../benchmarks/imaginary_collatz_history_lift_receipt.json) |
| prospective_memory_commitment.mjs | [PROSPECTIVE_MEMORY_COMMITMENT_V0_1](../native/PROSPECTIVE_MEMORY_COMMITMENT_V0_1.pnv) | [receipt](../benchmarks/prospective_memory_commitment_receipt.json) |
| prospective_memory_determination_benchmark.mjs | [PROSPECTIVE_MEMORY_DETERMINATION_V0_2](../native/PROSPECTIVE_MEMORY_DETERMINATION_V0_2.pnv) | [receipt](../benchmarks/prospective_memory_determination_receipt.json) |

The native candidate programs represent core transitions, not a line-for-line port of the historical benchmark loops. Those loops remain reproducible from the pinned historical sources; native benchmark orchestration and equivalence remain OPEN. Prior Python CPU model diagnostics already on this branch remain historical research evidence, not the target implementation; they are not converted to, expanded in, or admitted as the native architecture here. Do not remove prior diagnostics without retaining their evidence/lineage and preparing native replacements.

## Binding contracts (candidate)

### Memory state space

Sources: memory.state = typed nodes, positive symmetric edge weights, occurrence register, accessibility; memory.event = occurrence ID, endpoints, verified status, source; memory.query = start and nonnegative budget; memory.duration = nonnegative elapsed duration.

memory.verified_edge_update receives [state,event]. Validate existing edge, identity and provenance; duplicate identical occurrence is idempotent; conflicting occurrence rejects. Verified event updates cost c'=0.5+0.5(c-0.5), access a'=a+0.25(1-a); unverified event adds only its record. Return independent next state. These numerical factors are fixture choices. memory.shortest_paths receives [state,query], returns distances for reachable nodes and budgeted set; unreachable marked explicitly, no nonfinite JSON. memory.accessibility_decay receives [state,duration], returns state with a'=a exp(-duration) and weights unchanged. See original [formalism](memory-state-space-ontology-v0.1.md); the candidate is a single-transition graph and query contract, not general metric evolution.

### Imaginary Collatz history

collatz.state = (n,q,y,horizon,lineage), exact positive integer n, rational q and y in [0,1), horizon nonnegative. For exact arithmetic encode unbounded integers and reduced rational numerator/denominator as decimal strings in canonical JSON where necessary; do not use binary floating point. Preserve immutable occurrence/semantic lineage distinct from arithmetic history. collatz.parity returns n mod 2. collatz.three_n and collatz.add_unit return arithmetic intermediate 3n and 3n+1; these are pure values, not semantic acts or side effects. collatz.select_unaccelerated receives [state,bit,repaired_n] and returns n/2 for even or repaired_n for odd; validate parity. collatz.baker_lift receives [state,bit,next_n], returns (next_n,2q-bit,(y+bit)/2,horizon+1,lineage); verify q itinerary bit and arithmetic transition. collatz.inverse_lift recovers bit=floor(2y'), q=(q'+bit)/2, y=2y'-bit, horizon-1 and previous n by validated branch inversion; the lineage field is unchanged by the arithmetic witness. Inverse requires horizon>=1 and valid parity/integer preimage. Exact canonical state equality is asserted. The source itinerary is defined on admitted trajectories; no universal termination inference. Arithmetic alone does not create a semantic relation.

### Prospective memory

Sources: prospective.intention and duration nonnegative finite; determination and current_commitment, evidence, alpha in [0,1]; routes typed admitted alternatives with positive costs and context/provenance; budget nonnegative; status open/detour/blocked_unknown/unavailable_verified; cost_scale finite nonnegative and unit-bearing.

prospective.multiply receives two scalars and returns their product (W=I tau, P=W D). prospective.commitment_update receives [w,e,alpha] and returns (1-alpha)w+alpha e. prospective.admissible_route_proposal receives [routes,budget,status,P,cost_scale] and returns a non-actuating proposal with selected route or HOLD/revision, preserving evidence and goal identity. Verified withdrawal overrides readiness; unresolved route availability is not verified cancellation. Goal route must be admitted and within hard budget; premium relative to declared admissible comparison must not exceed cost_scale P. No actual resource consumption or successful outcome asserted. For graph discovery, metric and transport use the declared source contracts rather than a hidden implementation.

### Determination

determination.comparable_opportunities = independently observed admissible comparable allocation opportunities with accepted/rejected labels and provenance; determination.beta_prior = two positive parameters. determination.posterior_mean receives [opportunities,prior] and returns (alpha+n_positive)/(alpha+beta+n_positive+n_negative). Missing, unavailable, incomparable observations are not rejections. determination.constant_intention_filter receives [I,tau,T] with T>0, returns I T (1-exp(-tau/T)); historical W stays I tau. Other bindings share prospective memory contracts. The model's time scale and cost conversion are not source-derived calibrations. The actual held-out classifier, shuffled baseline, calibration and shift benchmark from historical evidence require separate native test paths; no claim that this program reproduces all prior results.

## Next work / verification boundary

Resolve source KAKU and RADICAL identities via exact PNCS/PNV authoring, bind only actual admitted operators, run native interpreter and inverse-lineage tests through existing NOEMA/PNAML path, compare emitted results to historical receipts. If a binding or runtime is unavailable, report the specific limitation before changing implementation language. Do not promote candidate status on the basis of structural inspection. The branch is a research proposal and must remain distinct from a validated native runtime.

## Follow-up v0.2

[PNCS Memory Grammar and PNLF integration](pncs-memory-pnlf-integration-v0.2.md) links the pre-existing native semantic grammar, exact CLX2 source terms, orbital/liminal memory and a callback-free PNV observation gate. Two new PNCS source candidates and one PNV gate; native admission/execution remains open. Includes the migration ledger for the 12 earlier Python diagnostic files.
