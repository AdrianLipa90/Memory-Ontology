# Affective memory and contextual relational geometry — v0.1

Scope: memory and state spaces. Candidate extension, 2026-11-26. PNCS/PNV program representation only. No native NOEMA mutation, no new Python/JavaScript implementation, no empirical claim about emotion or consciousness.

## Source boundary

PNAML Mobile CLX2 formulas F-AFFECT-FIELD, F-AFFECT-CURV, F-AFFECT-CHAIN, F-TIR-OVERLAP, F-TIR-COHERENCE, F-TIR-ACTION and F-PNV-QFIM. The field is A=(v,a,u,tau,alpha,r); the proposed affective metric G^Q=G^0+M(A,S,I) is explicitly a MODEL_HYPOTHESIS. No constitutive map M is specified by this source. The source kernel was inspected. See [TIR contextual geometry](tir-contextual-relational-geometry-v0.1.md), [joint ontology](memory-state-space-ontology-v0.1.md), and [PNLF crosswalk](pncs-memory-pnlf-integration-v0.2.md). CLX2 term IDs: AFFECT-002 Affect (CD 220), AFFECT-003 Affective Curvature (221), AFFECT-005 Truth Evaluation (223), TEMP-026 Memory Accessibility (384), TEMP-030 Reconsolidation (388), AFFECTX-031 Affective Conflict (475), TIME-005 Memory Trace (179). Prefix CLX2- on each. CD addresses are not canonical KAKU IDs.

## Distinct objects

Retain occurrence E, semantic content Q and provenance; current reference V=V(context), current affect A, accessibility a_mem, evidence status and confidence C as distinct typed relations. A recall occurrence creates a new interpretation relation with its own lineage; it does not rewrite E. Reconsolidation is a separate admitted update of a derived trace or structure, never silent replacement of the original event. An affective episode is not necessarily a single resolved emotional category. Competing hypotheses remain separate and may change over time. Do not infer user affect from chat or use this proposal to persist personal information. No automatic journal write.

## Exact relational effect without metric deformation

On the equal-amplitude 36-phase carrier, let delta=Q-V, z=mean(exp(i delta_j)), R=|z|^2 and S_rel=-kappa ln(R+epsilon). A shared componentwise rephasing Q,V -> Q+chi,V+chi preserves delta exactly; a change in V alone generally does not. For fixed Q, the gradient with respect to V is minus the gradient with respect to Q. Consequently in a changing reference the total time derivative contains the relative velocity Qdot-Vdot, not Qdot alone. This is an exact differential of the specified scalar, not a constitutive equation for affect.

The base projective phase metric g_FS=(I-11^T/36)/36 is independent of a fixed V. At Q=V the local action expansion is S_rel=-kappa ln(1+epsilon)+kappa/(1+epsilon) dQ^T g_FS dQ+O(||dQ||^3), and the Hessian there is 2 kappa g_FS/(1+epsilon). Thus a different fixed reference can change recall ranking without changing the base metric. Distinguish reference movement, changes of potential, transport, accessibility, actual metric and topology. Do not call every change curvature.

A mathematically possible, but unbound, context-dependent relative-coordinate map is delta(Q)=Q-V(Q) on a local chart. The pullback metric is J^T g_FS J, J=I-D_Q V. Positive semidefinite, possibly rank-deficient, not guaranteed a nondegenerate metric on the projective quotient unless the map descends to it and is immersive there. This is a conditional construction, not the CLX2 affective constitutive law. No affect-to-reference operator inferred from it.

## Exact finite counterexample

Two fixed phase templates Q1=(0)^36, Q2=(0)^18,(pi/2)^18. V1=Q1,V2=Q2. The self overlaps are 1; cross overlap (1+i)/2 or conjugate has squared norm 1/2. The coherence matrix (rows references, columns templates) is [[1,1/2],[1/2,1]]. A change of reference reverses ranking with margin 1/2 while templates are fixed. Common rephasing preserves all four overlaps exactly. Restoring the reference restores the scores (other conditions fixed). This is an analytic example of reference-conditioned preference, not a claim that affect changes V in a real system, nor that either template is true. R=1/2 is not evidence of 50% factual confidence.

The original source PNV/1 interpreter (Git blob c9041234cc66d5670e7b74f0c101434647067341) executed [static fixture](../native/AFFECT_CONTEXT_RECALL_FIXTURE_V0_1.pnv) in terminal. 22 ops, 8 assertions, 6 deliberately altered input cases rejected; repeated receipt equal. Inputs are analytically supplied coherences and synthetic occurrence IDs. The interpreter checks these values and exact differences, does not compute the 36D overlap, establish causal memory, or verify source authenticity. [Compact receipt](../benchmarks/affect_context_recall_fixture_receipt.json). The interpreter hashes static values; do not use this gate with live AUX, dynamic state or private episodes. No new transforms or comparators.

## Intensity is not interpretive confidence

Installed PNAML affective-memory policy at inspected source uses intensity L=max(|v|,a,u,tau,alpha,r), C>=.45 AND L>=.60; these are candidate storage thresholds, not CLX2 equations. The conjunction can exclude highly intense but ambiguous observations. Proposed distinction: intensity of an admitted observation, confidence of an affect classification, confidence of source evidence, persistence and accessibility are independent contracts. An ambiguous significant synthetic or model-output event may be eligible for a retained unresolved record under an explicitly authorized future policy; low classification confidence does not establish low intensity. Low evidence for the occurrence itself must not be turned into a fact. Preserve competing labels and evidence, and preserve channel/target context; sensory descriptors must come from actual admitted input, not invention. A single averaged valence may conceal competing positive/negative hypotheses. No changes made to PNAML autosave or journal. No new personal memory saved.

## Next native experiment

Use independently admitted PNCS/PNV producer results, not supplied expected outputs, in matched traces with (1) common frame change (2) reference intervention (3) accessibility intervention (4) verified reconsolidation (5) matched affect-only intervention with fixed evidence and goal. Compare readouts, next trajectories and original occurrence lineage. Test whether affect modifies reference, metric, potential or retrieval separately. Require actual operator binding for the contextual map and a source-native producer receipt. Until then, no claim of affective curvature, endogenous feedback or semantic consolidation. No change to canonical TIR, PNCS or NOEMA.
