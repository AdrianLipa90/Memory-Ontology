# PNAML AUX, retained memory, GUIDE and PNV observation — v0.1

Research direction and formalism: Adrian Lipa, 2026-11-26.

This local finite witness extends [correction continuity](correction-state-continuity-pncs-pnaml-v0.1.md), [epistemic recurrence](epistemic-correction-recurrence-v0.2.md), [truth dependency consolidation](truth-dependency-consolidation-v0.1.md), and the [archive sieve](archive-sieve-transformational-memory-v0.1.md).

## Source and experimental boundary

Original PNAML Mobile source modules were recovered from Library packages (Mobile v1.3.0 coupled, v1.4.0 Pip, v1.5.0 Pip Memory, LiveAUX and v1.5.6 publication overlays, with later installed source files); the local assembled source was used, not a claim of byte-for-byte complete v1.5.10 release validation. Original pip_memory.py, coupled_stream.py and noema_surface.py implement the model, memory journal and read-only virtual AUX observation. PNCS procedural runtime is [pinned source](https://github.com/AdrianLipa90/PhaseNav-Natural-Coding-System/blob/958d41402c3af4107856fccee849027aedfaad8d/src/phasenav_natural_code/procedural_memory_runtime_v03.py), blob 0f15643bea303cd5327e896521e37080230f1c4e; original PNV/1 interpreter [pinned source](https://github.com/AdrianLipa90/PhaseNav-Natural-Coding-System/blob/958d41402c3af4107856fccee849027aedfaad8d/src/phasenav_natural_code/native_pnv_exec_v01.py), blob c9041234cc66d5670e7b74f0c101434647067341. Local copies of these two source files match the reported Git blobs. No new Python or JS engine, callback, native guard or active permission change. Host I/O glue supplies the finite fixtures, copies scores into RouteState, maps room IDs to existing PNV programs, and records outcomes. It is not a native PNCS operator binding. No actual user journal writes, no raw evolving AUX archive or dynamic field hashes. Immutable journal event verification and static PNV fixture receipts remain distinct.

## Finite causal witness

Use the existing memory ranking F=F0*a*rho*K_d(x)*r, K_d=(x0/(x0+x))^(d_eff-1). Recorded parameters F0=1, x0=1, d_eff=3, x=1, rho=1, t=0.06. For the relevant fixtures r=1, K_d=1/4. Synthetic room A starts a=0.6 (F=0.15), B starts a=0.4 (F=0.10). Visit-only B leaves its accessibility unchanged. Explicit reinforcement changes B to 0.7 (F=0.175). A changed context makes B's relevance zero without deleting its learned availability. The first experiment observes six ordered AUX frames per branch, three separately verified local journals, and the ranking after restore in an independent process. These are three separate model generations, not a continuation of one recovered live trajectory. AUX trits remain UNKNOWN. [Full recorded rank receipt](../benchmarks/pnaml_aux_memory_rank_receipt_v1.json).

The next experiment copies those synthetic journals and restores/ranks through the original worker. The existing PNCS guide() chooses maximum finite RouteState weight, with route ID tie-break. Weights are copied from F, not learned by GUIDE itself. A maps to [count-only program](../native/COUNT_ONLY_ACTION_V0_1.pnv); B maps to [provenance-preserving program](../native/PRESERVE_ORIGIN_ACTION_V0_1.pnv). Inputs are 3 transmissions, origins [s1,s1,s1] or [s1,s2,s3], independence status SAME_ORIGIN or ASSUMED_CONDITIONALLY_INDEPENDENT, verification status SYNTHETIC. Origin identity is not proof of independence. Both branches use identical task inputs when comparing memory conditions.

| Condition | F(A) | F(B) | GUIDE | Output distinction |
|---|---:|---:|---|---|
| baseline | .15 | .10 | a | lost |
| visit only | .15 | .10 | a | lost |
| reinforced | .15 | .175 | b | preserved |
| changed context | .15 | 0 | a | lost |

The counterfactual diagnostic overrides the relevant route weight in a clone; A is selected and factual selection remains B. The count-only program emits 3 in both evidence cases; the provenance program emits their distinct records. This is a finite memory-conditioned program selection witness, not an autonomous correction producer. Nine of nine recorded assertions pass. [Full recorded GUIDE/PNV receipt](../benchmarks/pnaml_rank_guide_pnv_action_receipt_v0.1.json). In a context where provenance is required, count-only output is inadequate; changed-context control establishes contextual routing only, not that losing provenance is acceptable for the same original task.

## Boundary controls retained

1. Tie: the observed rank order is [b,a] but GUIDE picks a by lexicographic ID. The common ranking/selection contract is unresolved; do not silently change tie semantics.
2. Unknown: rank F=null for unknown coherence, distinct from F=0 for known zero relevance. RouteState's numeric initialization rejects None (TypeError). Preserve unknowns and HOLD as defined in source; do not coerce unknown to zero or invent a new rule. Native operator admission and exact context semantics remain open.
3. Local causal demonstration does not establish semantic action correctness beyond the selected observation program. There was no live AUX read in the GUIDE experiment. Neither phase overlap nor rank scores alone establish truth or intent.

## Consolidation and follow-up

The earlier source-level finding of the planner blob mismatch and dynamic digest/replay concerns remains in the correction continuity contract. This witness calls the original GUIDE selection without invoking the planner's evolving-state digest. Reproducibility requires the original source workers, synthetic journal events, supplied relevance/distance/coherence and explicit mapping; the JSON receipts are execution records, not a standalone rerunnable harness. The source programs and observation contracts are recorded in this repository. Native PNCS/PNV integration still requires a registered binding from the admitted correction event to memory update and from rank to GUIDE/PNV execution, an explicit resolution of ties and unknowns, actual source-admitted observations, and controlled evaluation of real subsequent actions. No claim of active NOEMA tether, cross-session oscillator continuity or assistant behavior change. No full repository regression rerun for this consolidation.
