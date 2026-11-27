# RDSS thought action — v0.2

Author research direction: Adrian Lipa, Pip Project, The Reality of the Imaginary.
Status: CANDIDATE DISCRETE ACTION / SOURCE-BOUND FINITE CONFORMANCE.
Extends [thought-path interference v0.1](thought-path-interference-v0.1.md), not the underlying RDSS metric or PNCS interpreter.

## 1. Existing source geometry

Memory-Ontology base 6a895069aa6dab1fe0c132541876393b60389e2a:
[RDSS V32 crosswalk](rdss-book-v32-mechanics-crosswalk.md) pp.132–133 specifies
\[
L_{\rm rel}(q,\dot q;M)=\tfrac12 g_M(\dot q,\dot q)-V_M(q).
\]
pp.126–132 give Poincare routing geometry; pp.140–141 give IDT directed traffic
eta=W_++W_- and intrinsic duration d tau=eta d lambda.
[Existing kernels](../engines/rdss_relational_dynamics_v32.py) provide
disk_distance, activity, duration. The exact source of mass, accessibility
and learned weights is [memory mechanics](../engines/rdss_memory_mechanics_v32.py).
Do not multiply the source kinetic term by a semantic mass without a metric
binding: CIEL mass, PNCS realization mass and accessibility are distinct.

Use a fixed declared metric sector, a path of ordered segments and positive
elapsed intrinsic times Delta tau_e. For the Poincare disk sector,
\[
\ell_e=d_{\mathbb D}(q_e,q_{e+1}),\quad
\Delta\tau_e=(W_{+,e}+W_{-,e})\Delta\lambda_e.
\]
For the piecewise constant-potential, constant-speed geodesic profile,
\[
K_e=\frac{\ell_e^2}{2\Delta\tau_e},\quad
U_e=V_e\Delta\tau_e,\quad
\boxed{S_H[\gamma;M]=\sum_e (K_e-U_e)}.
\]
These are integrated quantities in normalized model units, with
lambda_H in the same action unit. This is exact for that piecewise profile;
for varying metric or potential it is a discretization requiring convergence
checks. Metric lengths, time, cost and action are not interchangeable.
Do not claim a metric field equation or a 36D lift from this sector.

## 2. Memory coupling candidate

V32 pp.105–108 uses learned positive route weight w and routing cost 1/w.
The existing immutable Memory.encounter records verified history and
changes learned_weight by quality*rho (failed encounters do not reinforce).
The following is a new explicit potential *profile*, not a source law:
\[
V_e(M)=\beta / w_e(M),\qquad \beta\ge0 .
\]
Beta supplies potential units and is externally declared. No physical
force or mass interpretation. An equivalent zero-point shift of V affects
common-time phases uniformly; it need not be uniform across unequal times.
Keep accessibility, exact realization mass, semantic mass and learned_weight
separate; this profile consumes only learned_weight. No arbitrary imputation.
At fixed geometry, duration, candidate family and source input, changing M
alone can change action and coherent intensity; beta=0 is the ablation.
The sign is L=T-V: reducing route cost raises S at fixed kinetic term,
but coherence is oscillatory, so this does not entail monotone preference.

## 3. Native seams

[PIP_THOUGHT_ACTION_STEP_V0_2.pnv](../projects/pip-project/native/PIP_THOUGHT_ACTION_STEP_V0_2.pnv)
folds K-U, cumulative action and duration, emitting ordered segment lineage
and scope/continuity witnesses. The path owner provides already validated
positive times and scale, real finite quadrature and exact edge provenance.
The program does not select, persist, mutate the Hotel clock or introduce
new admission machinery; witnesses are diagnostic, not execution authority.
The existing PNV/1 interpreter has no intrinsic multiply, division, metric
or transcendental opcode. Existing RDSS kernels plus the explicit test
quadrature supply the numeric inputs. The conformance adapter is test-only,
not a new runtime engine or callback. A full native source-bound quadrature
operator remains an open PNCS task.

After folding, pass dimensionless per-edge Delta S/lambda_H to the existing
PNCS semantic_u1_coupling; feed the returned components to the existing
[PIP_THOUGHT_PATH_SUM_STEP_V0_1](../projects/pip-project/native/PIP_THOUGHT_PATH_SUM_STEP_V0_1.pnv).
For each coherent family, bind the family scope to the same immutable memory
snapshot and context. Compare counterfactual snapshots in separate sums.
Reverse oriented connection transport is conjugated; reversing a kinetic
trajectory in time is not by itself the inverse oriented connection. Do
not infer action antisymmetry. All lineage remains separate from intensity.

## 4. Stationarity and intervention

At V=0, fixed endpoints on a common disk geodesic, fixed total duration T,
the kinetic term is stationary and minimal at equal speed; Cauchy–Schwarz
gives sum ell_e^2/(2 dt_e) >= (sum ell_e)^2/(2T).
Geodesic refinement at equal speed preserves action exactly in the model.
This is a finite metric-sector result, not a continuum optical limit.

Test a symmetric two-corridor graph with equal lengths/durations and weights.
A verified event reinforces one edge in the second path from w=1 to w=2.
At beta=1, dt=1, lambda_H=1, the action difference is +0.5;
J changes from 4 to 2+2 cos(0.5). Failed encounter control stays at 4;
beta=0 stays at 4 for both snapshots. Compare against incoherent sum 2.
The history-bearing variable here is the existing learned_weight, not
the fresh observation or active coordinates. The test demonstrates causal
efficacy in the constructed policy model, not calibrated cognition or live
NOEMA dynamics. A family can remain open (HOLD) despite a large intensity.
No new conclusion is admitted by this arithmetic.

## 5. Validation and open frontier

Conformance tests exercise the original pinned PNCS reference interpreter
and U(1) transport, original RDSS distance/duration/memory update, equal-speed
refinement, finite stationarity, time parametrization, matched-state
intervention, failed encounter and ablation, scope mismatch, signed action
and exact integer accumulation. No dynamic AUX hash; inputs are immutable
synthetic fixtures. Further work: source-defined memory-to-metric/potential
binding, continuous stationary action and measures, actual candidate
enumeration with owner references, native numeric operators, live producer
experiment and independent prediction. No repository code is attributed to
hardware execution.
