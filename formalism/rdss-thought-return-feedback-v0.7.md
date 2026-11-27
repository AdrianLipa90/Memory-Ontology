# Thought dynamics: return-driven memory feedback — v0.7

Author research direction: Adrian Lipa, Pip Project.
Status: FINITE HYBRID MODEL / SOURCE-KERNEL CONFORMANCE CANDIDATE.
Base 718d6db. Extends [v0.6](rdss-thought-orbital-memory-v0.6.md),
[v0.5](rdss-thought-synchronization-v0.5.md) and [v0.2](rdss-thought-action-v0.2.md).
The Hotel is history, not a guest book. The Collatz index is not its causal index.

## 1. Continuous flow and return seam

Reuse the v0.5 symmetric 18+18 phase sector and v0.6 CP1 imprint, the
source AdaptiveEdge, phase_step, displacement, kick, kepler_segment,
orbit_invariants and collatz_step/inverse. No replacement engine.
Between events the edge snapshot is frozen. In normalized model units
the orbit follows z''=-mu z/|z|^3; the phase follows delta'=-2K sin(delta),
K=g*a*c. The two continuous subsystems interact through discrete events,
not an assumed continuous cross-force.

For the declared prograde bound-orbit fixture, accumulate oriented
angle increments arg(conj(z_old)*z_new) without wrapping the total.
A positive crossing of 2pi*k marks a return candidate. The discrete
reference uses the first sample after each crossing (no interpolation);
the event time is approximate and must refine with timestep. This
detector is valid only with resolved increments and monotone positive
angular momentum in this fixture. It is not a universal return detector.

An independent evidence input decides whether a candidate is verified.
For verified events, compute the pre-update FS imprint from the current
phase state, apply the source kick, then update AdaptiveEdge and perform
one tagged Collatz step. The fixture uses quality=1/2, rho=1, eta=0,
gain=0.2, mu=1, and a=1/2, c=1 initially. The kick is expressed in the
local radial/tangential frame and rotated into the orbital plane.
This frame binding and the return event policy are new declared choices.
Failed candidates are recorded but do not kick, reinforce or consolidate.
The arithmetic does not independently verify evidence. Source references,
before/after states, parity and event count remain independent of phase
amplitude. No assertion of universal Collatz termination.

## 2. Closed feedback experiment

From the same circular initial orbit and initial phase difference pi/2,
compare two histories with the same evidence flags (verified twice).
In the feedback arm the subsequent phase coupling uses the updated
edge; in the ablation it uses the initial edge throughout. Both arms
still record the verified updates and Collatz tags. The first event
must match exactly. The different conductances only enter phase flow
after that event; the second kick and later trajectory can then differ.
A zero-gain control makes both arms identical. A failed first event is
a separate evidence control: its memory and index remain unchanged.
Test the third orbit segment, not only a changed stored parameter.
Independent source snapshots and immutable event records are retained.
The experiment is not a native live NOEMA producer.

## 3. Action and dissipation

The normalized Kepler sector has L_orb=|z'|^2/2+mu/|z|.
Its Euler-Lagrange equation yields the source acceleration.
For the symmetric phase reduction at fixed K, let
    U_K(alpha,beta)=K*(1-cos(beta-alpha)).
Then alpha'=-partial_alpha U_K, beta'=-partial_beta U_K.
This is a gradient flow, not a conservative Euler-Lagrange equation.
The Rayleigh functional R=(alpha'^2+beta'^2)/2 together with
L_phase=-U_K gives the Lagrange-Rayleigh equations
    partial_theta U_K + partial_theta' R = 0.
Between events dU_K/dt=-2 K^2 sin(delta)^2. The orbital energy
E=|v|^2/2-mu/|z| is conserved in the continuous reference.
At a discrete event account separately for orbital work
Delta E=Re(conj(v_minus)*Delta v)+|Delta v|^2/2
and the potential jump Delta U=(K_plus-K_minus)*(1-cos(delta)).
Do not identify either quantity with physical energy or assume their
sum is conserved without the dissipation and event-work ledger.
The additive L_orb-U_K and Rayleigh functional describe this fixed-memory
piecewise sector; the discrete event law remains a separately declared
map. The v0.2 geodesic action is a distinct observable, not this action.
No source-derived continuous memory Lagrangian has been established.

## 4. Native observation

PIP_THOUGHT_RETURN_FEEDBACK_V0_7 composes immutable source-owned
candidate/verified event observations, before/after edge refs, orbit,
phase, Collatz index and tag, event work, and prior ref. It emits
diagnostic identities for scope, previous ref, memory and index.
No arithmetic inference of evidence, integration, runtime gate or
persistence in the PNV program; original PNCS interpreter in tests.
No dynamic AUX hash, Hotel successor invocation or manuscript edit.
