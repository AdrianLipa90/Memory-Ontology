# Prospective memory: determination and time-dependent commitment v0.2

2026-11-26. Candidate extension of [author postulates v0.1](prospective-memory-intention-will-sacrifice-v0.1.md). The user relations W=I*tau and P=W*D remain unchanged as proposed cumulative observables. This note distinguishes predictive readouts from the definition. No universal human volition law, moral value, physical energy, native NOEMA execution or general cognition claim.

## Independent observation of determination

For a declared set of comparable prior opportunities, with recorded admissibility, cost/context and accepted/rejected allocation decisions, a candidate Bernoulli propensity estimate is Dhat=(alpha+n_positive)/(alpha+beta+n_positive+n_negative). This is a beta posterior mean under conditional iid Bernoulli sampling, not a general definition of determination. Distinct costs, changing context, lack of resources and missing observations are confounders; exclude unavailable opportunities and preserve provenance. Fixture alpha=beta=1, 12 synthetic past decisions. No human calibration. A cost mapping kP must have units cost per unit of P; behavior identifies the combined scale unless independently calibrated.

## Cumulative record vs bounded operational readout

W_history=int I d tau is not required to saturate; for constant I it equals I*tau. The source bounded evidence-dependent w from V32 p.196 remains separate. A possible effective control filter is dW_eff/dtau=I-W_eff/T, W_eff(0)=0. For constant I, W_eff=I*T*(1-exp(-tau/T)), hence W_eff≈I*tau for tau<<T. This is a new candidate, not replacement of the author equation. It is an exponential memory kernel and a leaky integrator; historical W and a decaying active readout can coexist. A declared gain absorbs T in the normalized benchmark. Filter T is not inferred from the source. The benchmark bounded model uses the generating timescale T=1.8, making it an oracle-form comparator. No claim of a discovered time constant.

## Executed benchmark

Actual directed positive-cost graph shortest-path computation; two detours, a direct route, a comparison destination. Unknown block and verified cancellation are separate, all policies respect budget 4. Two synthetic generators of willingness labels: stationary latent tolerance 4*latent*I plus bounded noise, and age-sensitive tolerance multiplied by 1-exp(-tau/1.8). Latent propensity sampled independently of observed 12 prior binary allocations conditional on that propensity; I and tau sampled independently. The latter generator is not the linear author postulate. Each generator 1200 calibration cases (seed 421) and 2400 held-out cases (seed 917), 1511 feasible detours scored per generator. The same random seeds make the regimes paired rather than independent. Additional stationary shift set (seed 1217), 1485 feasible detours scored with age-trained gains frozen. One scalar gain selected per comparator by training accuracy on grid 0..8 step .05. Shuffled D as negative control.

| Policy score | Stationary accuracy | Age accuracy | Age-trained to stationary shift |
|---|---:|---:|---:|
| I*.5 | .772336 | .819987 | .770370 |
| I*Dhat | .896095 | .892124 | .808081 |
| W*.5 | .744540 | .831238 | .722559 |
| W*Dhat | .818001 | .887492 | .815488 |
| W*shuffled_D | .702846 | .796161 | .676768 |
| I*(1-exp(-tau/1.8))*Dhat | .858372 | .915288 | .838384 |

The time-independent history estimator beats linear W*D on both same-regime test sets; saturation wins on the age regime under known generating form. These are synthetic preference classification scores, not actual goal completion or welfare. Only feasible detours are scored; open/cancelled/unknown cases are not part of accuracy. Exact matched-state history intervention: I=1, tau=2, gain=1, path x-a-g cost 2, reference cost 1; Dhat=3/14 rejects premium 1, Dhat=11/14 accepts. Constructed causal effect of stored history on policy, not endogenous emergence. Stronger evidence requires independently measured costs and opportunity-conditioned decisions, real held-out route discovery and source-bound dynamics. No arbitrary parity-to-truth mapping.

[Executable reference](../native/PROSPECTIVE_MEMORY_DETERMINATION_V0_2.pnv), [receipt](../benchmarks/prospective_memory_determination_receipt.json). Functions executed in JavaScript tool runtime; serialized module and receipt read back. Full repository tests not run. Main unchanged.

**Native migration:** the linked PNV candidate replaces the active prototype source; historical benchmark execution was not PNV. See [migration contract](pncs-pnv-native-migration-v0.1.md) for original source lineage and open native bindings.
