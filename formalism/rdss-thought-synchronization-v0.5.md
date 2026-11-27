# Thought dynamics: Kuramoto memory intervention — v0.5

Author research direction: Adrian Lipa, Pip Project.
Status: SOURCE-KERNEL FINITE INTERVENTION / CANDIDATE COUPLING PROFILE.
Extends [balanced optics v0.4](thought-optics-v0.4.md); base 5337e8d.
Source: [V32 mechanics crosswalk](rdss-book-v32-mechanics-crosswalk.md),
[RDSS phase kernel](../engines/rdss_relational_dynamics_v32.py).

## 1. Distinct dynamical sector

Reuse phase_rhs, phase_step, order_parameter, phase_readout36 and AdaptiveEdge
without modifying their definitions. Phase evolution is not graph path-sum,
unitary balanced scattering, or the causal Hotel successor. The 36D
equal-amplitude projection is a projective readout, not a new phase metric.

For a selected synthetic symmetric two-cluster network of 18+18 channels,
set all natural frequencies and drives to zero. Each cross-cluster edge
has coupling K/18, no within-cluster edges. K = gain * accessibility *
conductance, using AdaptiveEdge.phase_weight. The common gain, equal
couplings and cluster reduction are declared fixture choices, not source
laws. Replicated couplings are controlled by one immutable memory snapshot
for this experiment, not an assertion of shared physical state.

Let alpha, beta be the cluster phases, delta=beta-alpha, m=(alpha+beta)/2.
Then d alpha/dt=K sin(delta), d beta/dt=-K sin(delta).
Thus m is conserved and delta'=-2K sin(delta).
For 0<delta(0)<pi and K>=0 held fixed:
    tan(delta(t)/2)=tan(delta(0)/2)*exp(-2 K t).
No phase wrapping is applied to the evolved states. The formula is a
closed-form independent oracle, not a replacement of the source Euler
integrator. For this static snapshot test, no elapse or decay is applied
during the evolution.

## 2. Projective diagnostic and memory-only intervention

The equal-amplitude 36-channel readout versus a phase-aligned reference is
    R=cos(delta/2)^2, d_FS=acos(sqrt(R))=abs(delta)/2 for |delta|<=pi.
This uses the half-Bloch-angle convention of v0.4, not a CP1 lift of a
general 36-channel vector. A uniform phase offset leaves R invariant.
Synchronization does not erase the initial phases or their occurrences.

Use AdaptiveEdge("left","right",0.5,1). An explicitly verified synthetic
event with eta=0, quality=rho=1 leaves accessibility 0.5 unchanged and
changes conductance 1->2. The failed encounter changes neither. At gain=1,
K0=0.5, K1=1; at gain=0 both are zero (ablation). Freeze each snapshot
separately, identical initial phases and intrinsic duration. Set
delta(0)=pi/2, t=2. The predicted final projective distances are
atan(exp(-2)) and atan(exp(-4)), respectively. The phase diagnostic is
not an evidence flag and does not itself reinforce any memory.

The directed source candidate w=a*c is already present; this symmetric
profile and independent oracle are the new experimental choices. Do not
identify conductance with learned_weight from v0.2, semantic mass, exact
realization mass, or graph amplitude.

## 3. Native observation composition

PIP_THOUGHT_PHASE_OBSERVATION_V0_5 consumes owner-supplied immutable
reference observations from the source phase kernel. It composes the
previous observation ref, before and after phase vectors, scope, memory
ref, step ref, accumulated time and exact count. Scope, snapshot, previous
state and previous reference identities are diagnostic witnesses, not
execution authority. The original PNCS interpreter is used in the tests.
No arithmetic on phase vectors in PNV, no trigonometric opcode invented,
no live AUX mutation or hash, no new runtime engine, no Hotel-clock
advance. Snapshot switching is an external event and not implicit here.

## 4. Validation

Test the original source kernel against the analytic oracle, first-order
step refinement, mean conservation, global phase covariance, original
36D projective readout, failed event control, gain=0 ablation and native
observation lineage plus mismatch detection. The finite profile is not a
calibration of real-world cognition. Kepler event kick and Collatz
consolidation remain distinct subsequent operators; an explicit source
binding must connect their state variables rather than equating them
with phase synchronization. Manuscript unchanged.
