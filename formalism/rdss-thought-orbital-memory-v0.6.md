# Thought dynamics: Kepler–Collatz memory seam — v0.6

Author research direction: Adrian Lipa, Pip Project.
Status: FINITE SOURCE-KERNEL CONFORMANCE / DECLARED SECTOR BINDING.
Base af28c23. Extends [v0.5](rdss-thought-synchronization-v0.5.md)
and [v0.4](thought-unitary-seam-v0.4.md). Source: [V32 crosswalk](rdss-book-v32-mechanics-crosswalk.md),
especially pp. 86–91, 98–101, 142–144 and 265–270; existing
[RDSS memory operators](../engines/rdss_memory_mechanics_v32.py).
The Hotel is history, not a second guest book.

## 1. Exact two-cluster restriction

In the v0.5 equal-amplitude 18+18 sector, use orthonormal block vectors
L,R (each nonzero entry 1/sqrt(18)). The 36-vector is exactly
(e^(i alpha)L+e^(i beta)R)/sqrt(2). Its two coefficients are a CP1
representation in this fixed subspace, not a general 36D -> CP1 map.
Apply the existing normalized seam H to the coefficients.
For mean phase m and delta=beta-alpha, the output is
e^(i m)(cos(delta/2), -i sin(delta/2)).
For 0<=delta<pi the source Bloch tangent log at north, with eQ=(1,0,0)
and eP=(0,1,0), gives delta_m=-i delta/2.
The proof follows from the Bloch vector (0,-sin(delta),cos(delta)).
Its magnitude is d_FS=delta/2. Common phase leaves the displacement
unchanged, but does not identify the causal occurrences.

## 2. Event kick and Kepler return

Use the existing displacement, kick, kepler_segment and orbit_invariants.
A declared owner-supplied verified event has quality q>=0; in this
fixture q=1/2. The failed event has no kick (explicit experiment policy).
No coherence score authorizes a new event. Set initial z=1, v=i, mu=1
in normalized model units. The quality and fixed central parameter are
fixture inputs, not semantic-mass identifications. Then
v_after = i(1-q delta/2). With q=1/2 and delta in [0,pi/2],
the orbit is bound; the exact instantaneous angular momentum is
J=1-q delta/2 and energy E=J^2/2-1. Event work is E_after-E_before.
Between events the source velocity-Verlet integrator approximates the
Kepler orbit. The normalized period source function kepler_period(a,mu)
equals sqrt(a^3/mu); the full Newtonian revolution is 2pi times this
quantity in this selected model, with a=-mu/(2E). No clock identity.

Compare the two v0.5 memory snapshots at the same initial phases,
elapsed time, initial orbital coordinates, and event inputs. At gain=0,
the upstream phase dynamics are identical and so are the orbital
outcomes. A failed prior reinforcement is a separate control. A failed
current event preserves the orbit velocity. This is a finite causal
witness of memory -> phase -> FS displacement -> orbital trajectory.
It is not yet an endogenous return-triggered learning rule.

## 3. Collatz consolidation and provenance

The original accelerated source map C(n) returns the next integer and
the parity tag b. For odd n the route is dissociation 3n, ingest +1,
consolidation /2; for even n it is consolidation /2. Keep the odd
intermediate 3n+1 and parity as explicit ordered path information.
The exact inverse source operator recovers n from (C(n),b). In particular
3 and 10 both reach 5 but carry different histories. This illustrates
why equal consolidated content must not identify occurrences.
The selected positive integer is an owner-supplied index in this
fixture; it is not the Hotel causal index, physical mass, orbital radius,
or a newly generated address. A finite Collatz path does not require
a claim of universal termination.

## 4. Native composition

PIP_THOUGHT_ORBITAL_EVENT_V0_6 records owner-supplied source outputs
without replacing numerical operators: phase observation reference,
memory reference, event reference, orbit before/after, displacement,
quality and evidence status, Collatz before/after/parity and exact
odd intermediate (or None). Scope, memory, prior reference and index
continuity are diagnostic identity witnesses. Counter and ancestry
are independent of orbit and Collatz values. The native program does
not itself establish the Collatz arithmetic, verify evidence or write
AUX; the original source operators and conformance tests do the
arithmetic. No runtime admission policy or second Hotel index.

## 5. Validation and open boundary

Test the two-cluster embedding and FS tangent oracle, global phase,
memory-only intervention, both failed controls and gain=0, Kepler
energy/work and angular momentum with timestep refinement, exact
Collatz inverse/collision and native lineage/mismatch witnesses.
No manuscript edits, no new runtime engine, no dynamic AUX hashing.
The source V32 FOLD bridge remains a distinct candidate. Mapping
Collatz output to orbital radius, actual return-triggered reinforcement,
and a joint endogenous action remain open; do not silently identify
accessibility, conductance, learned weight, or semantic mass.
