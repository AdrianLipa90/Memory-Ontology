# Geometry of truth and dependency-preserving consolidation — v0.1

Author source: Adrian Lipa, The Reality of the Imaginary V32, printed pp.274–284 (Chapter 31). Candidate research extension of [archive sieve](archive-sieve-transformational-memory-v0.1.md) and [checkpoint restore](archive-checkpoint-restore-v0.2.md). No changes to main, canonical PNCS or NOEMA.

## 1. Typed separation

Source pp.275–277, 282–283 distinguish semantic content, complex contextual scalar, familiarity, accessibility, confidence, evidence and provenance. A claim record must retain content, time and measurement scope, status relative to an evidence set, sources, dependency relations and consuming transformations. Proposed record H=(claim_id, scope, evidence_set, dependency_graph, epistemic_status, learned_relation_refs, lineage). A transmission is an occurrence, not necessarily a new observation. Source IDs help identify exact copies; different IDs do not guarantee independent evidence. A correction is a new occurrence linked to the superseded assertion, not a rewrite of its historical record.

## 2. Exact copying model

Source pp.277–278: prior odds O=1, report likelihood ratio 4, three transmissions. For independent reports under both H and not-H, O=4^3=64; in the ideal copying model O=4. The independent contrary observation has LR=1/16. Corrected odds are respectively 4 and 1/4, corresponding to probabilities 4/5 and 1/5. Counts of transmissions are separate from counts of distinct evidence origins. No new information is obtained from exact copies conditional on their known source under the ideal model. General correlated reports require joint likelihoods; neither equality of a label nor a distinct label calibrates a likelihood.

General chain rule: O_post = O_prior times the product of conditional likelihood ratios P(E_j|H,E_<j)/P(E_j|not-H,E_<j) where these terms are defined. A deterministic copy conditional on its original has ratio 1 on the observed support. Source group identity is sufficient only in the declared copying model, not in arbitrary dependence graphs.

## 3. Corrected evidence versus learned dispositions

Source pp.279–280: w'=w+eta(v-w), w0=4/5, v=1/5, eta=1/4. Then w_k=v+(w0-v)(1-eta)^k. Exact w1=13/20, w2=43/80, w3=145/320. The evidence-status revision is separate from this relaxation. The source's target v is a declared value, not generally a posterior probability. The numerical equality with the corrected probability in this example does not define a universal binding. An invalidated claim must not be used as an established premise merely because the old disposition remains strong. Preserve historical scope: a report about the earlier clock and a claim about the present clock are not interchangeable.

Source pp.281–283: conflicting reports coexist as attributed records. Distinguish supported, contradicted, unresolved conflict, and insufficient evidence relative to scope and evidence. HOLD may retain unresolved alternatives (-i,+i) in an admitted decision policy; do not redefine the canonical ternary operator as a universal truth table.

## 4. Projection and repair

For exact copies, retain origin and transmission aggregate separately, including scope and source lineage. A proposed evidence-aware sieve projection must preserve the evaluation of the declared query family and enough dependency information for later corrections. It need not preserve all historical detail; unknown origin stays unknown. A sufficient commuting criterion is pi F_e = Fbar_e pi for admitted future evidence/correction events, plus observation factorization. This is conditional, not universal. A summary storing only total count 3 cannot distinguish three copies from three independent reports, and therefore cannot preserve both posterior readouts in this example.

A proposed repair uses the affected claims and consuming transformations reachable along typed dependency edges, re-evaluating them under current evidence; graph reachability identifies candidates for re-evaluation, not automatic invalidity. Cyclic dependencies and alternate support require explicit operator semantics; no general inverse or monotone propagation law is assumed. Replay may require original inputs and a checkpoint; if lost, the exact historical counterfactual is unavailable. No real archive deletion or correction propagation performed here.

## 5. Executed PNV witness

[TRUTH_SOURCE_CORRECTION_V0_1.pnv](../native/TRUTH_SOURCE_CORRECTION_V0_1.pnv) executed with the unmodified original PNCS interpreter, Git blob c9041234cc66d5670e7b74f0c101434647067341. 77 ops, 13 assertions, 8 perturbed input controls rejected, repeated receipt identical. Small integer DIFFERENCE operations compute numerator/denominator pairs for the source odds and corrective recurrence. No external transform callbacks. Input source labels, expected values, scope and statuses are static fixture data; no general deduplication, independence inference, calibrated evidence admission or status classification is implemented. Equality checks on historical record/scope are fixture checks, not persistence mutation tests. Interpreter hashes static synthetic values; do not supply live AUX. [Compact receipt](../benchmarks/truth_source_correction_pnv_v0.1.json).

Next: test a typed evidence graph with multiple supports, source-copy consolidation and dependent conclusion re-evaluation, with admitted PNCS/PNV operators. Separate automatic evidence evaluation from arithmetic witness. No new Python/JavaScript engine.
