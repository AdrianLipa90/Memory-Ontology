# Prospective memory: intention, will and sacrifice — v0.1

Author postulates (Adrian Lipa, 2026-11-26): intention × time = will; will × determination = sacrifice.
Status: CANDIDATE CONSTITUTIVE RELATIONS / SYNTHETIC POLICY FIXTURE. Scope: prospective memory and state-space transitions, not general consciousness or moral measurement.

## Source constraints

The Reality of the Imaginary V32, printed pp.188–198: intention is a currently represented commitment to a preferred state, not an observed future event. Maintain the distinction among goal, route, policy, action occurrence and outcome. p.196 supplies an illustrative bounded commitment update w_next=(1-alpha)w+alpha e. pp.197–198 separate urgent evidence-based revision, cue-triggered prospective memory and Collatz exploration/replanning. pp.140–141 define activity-derived duration from directed traffic. See [joint ontology](memory-state-space-ontology-v0.1.md) and [TIR geometry](tir-contextual-relational-geometry-v0.1.md).

## Candidate relations

For an admitted commitment identity g and time measure tau:
\[
W_g(\tau)=\int_{\tau_0}^{\tau}I_g(s)d s,\qquad P_g(\tau)=D_g(\tau)W_g(\tau).
\]
For constant I these reproduce the author product exactly. W is cumulative intention exposure, not a bounded probability, present confidence or proof of persistence under disturbance. P is a readiness proxy, not actual cost, moral value or physical energy. For the scalar fixture I>=0 and D in [0,1] are dimensionless normalized inputs, tau measured in chosen duration units; W and P have the same units. A conversion scale is required before comparing P with costs; the illustrative fixture chooses unit conversion. No empirical calibration of D or claim that this is its unique definition. A normalized temporal integral cannot be multiplied by physical force without defining dimensions.

IDT: d tau = eta d lambda, eta=W_+ + W_->0 on an admitted active relation. Then W=integral I(lambda) eta(lambda) d lambda. Positive activity does not establish intention; I=0 gives zero incremental W even with a positive clock. Subdivision invariance holds for exact integration; a coordinate change must preserve the measure. IDT duration is not automatically physical proper time or autobiographical time.

If intention is a vector in a varying tangent frame:
\[
\mathbf W_g^a=\int_{\tau_0}^{\tau} \mathcal T_{\tau_0\leftarrow s}\mathbf I_g(s)d s,\quad \mathbf P_g^a=D_g\mathbf W_g^a.
\]
The specified history path determines parallel transport to a common anchor a. Under compatible local frame changes the result transforms at the anchor. Different paths may produce different results if holonomy is nontrivial. Do not sum unrelated goals or frames. For a scalar readiness proxy choose a declared projection/norm of the vector; cancellation and persistence duration are different observables. The impulse analogy is formal only, not a derived physical law.

## Current commitment versus accumulated history

Retain the source illustrative rule separately:
\[
w_{n+1}=(1-\alpha)w_n+\alpha e_n,\quad 0\leq w,e,\alpha\leq1.
\]
For constant evidence e, w_n=e+(1-alpha)^n(w_0-e). w can decay even when historical W has grown. With w0=.8, alpha=.2, one contrary assessment .2 yields .68; next restored assessment .8 yields .704. Sustained contrary evidence .2 yields w20=.2069175290276411; transient then restored evidence yields w20=.7982706177430898. No inference of universal volition. An admissibility change or reliable withdrawal of a goal must be able to override any accumulated readiness immediately. When revising the goal, close the old occurrence and start a new typed commitment, preserving lineage; do not silently rewrite W or count future outcomes as observations.

## Prospective-memory record and transition

M_pros=(owner,goal_id,context,cue,conditional_response,review_condition,occurrence,lineage,status,W,w,D). This is a proposed profile of existing state/relation/path/operator/boundary primitives, not a new taxonomy root. Record actual evidence, outcome and cost separately. A state-transition policy may select an admissible goal-preserving path with cost C_g rather than an admissible comparison path of cost C_ref only if C_g<=B_hard and max(0,C_g-C_ref)<=k_P P, with an explicitly declared common cost unit and k_P. P does not confer permission or require taking a harmful route. HOLD retains unresolved availability; verified cancellation closes/revises the commitment. When no goal path fits the budget, hold or explicitly revise according to context. Actual cost premium is recorded only for a completed chosen route relative to a declared comparison; it is not synonymous with all forms of sacrifice.

## Executed finite policy fixture

See [reference](../engines/prospective_memory_commitment.mjs) and [receipt](../benchmarks/prospective_memory_commitment_receipt.json). Deterministic factorial decision table: 4 availability conditions × 3 durations (1,2,4) × 3 D (.25,.5,1) × 4 detour premiums (.5,1,2,4) = 144 cases; repeated identical open/cancelled outcomes are not independent samples. Goal route cost 1+premium, hard budget 4, alternative cost 1. All policies handle verified cancellation explicitly. Local cheapest baseline favors alternative on ties; rigid original route holds when blocked; replan selects all feasible goal routes; W*D policy additionally applies its willingness threshold. No claim of optimized policy or empirical superiority.

| Policy | Goal arrivals | Alternative | HOLD | Revision | Sum paid premiums |
|---|---:|---:|---:|---:|---:|
| Local |0|108|0|36|0|
| Rigid |36|0|72|36|0|
| Replan |63|0|45|36|31.5|
| W*D |53|0|55|36|16|

Of 36 detour cases, W*D reaches 17 versus 27 for budget-only replan. With matched active state, intention I=1, D=.5, route premium 1 and identical constraints, duration 1 gives P=.5/HOLD; duration 4 gives P=2/arrival. This is a constructed causal memory witness through an explicitly chosen history-dependent policy, not a discovered law of HTRI. Costs and thresholds chosen, no fitting or random trials. No evidence that P alone improves success; tradeoff between retained goal pursuit and costs. Independently checked finite frame covariance (2D rotation fixture, error 0) and clock subdivision (W=3.5 both representations). Source bounded commitment update evaluated separately as above; not integrated into the policy fixture. No native PNAML/NOEMA or repo-wide test.

## Next validation

Bind exact cue/goal identity and verified history to the existing memory register. Define measurable determination from independently observed effort/resource allocation, and test held-out replan tasks with identical access budgets and nontrivial alternatives. Model commitment revision and costs separately from accumulation; compare against no-history control and fixed threshold. Imaginary Collatz opens alternatives, admits relevant verified relations, then consolidates a revised path while preserving the historical goal occurrence. No arithmetic parity implies successful fulfilment.

## Follow-up

[Determination and time-dependent commitment v0.2](prospective-memory-determination-v0.2.md) tests independently estimated history-based determination, time-independent versus linear-time versus bounded readouts, and a matched-state causal intervention. The original author postulates remain unchanged; the new filter is a candidate operational readout.
