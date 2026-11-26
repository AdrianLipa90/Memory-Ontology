# HTRI conditional contraction and structural memory — v0.1

Scope: source-derived software rule, not physical H200 validation. This is a restriction on spontaneous consolidation within the joint memory/state-space ontology. Source local PNAML Mobile 1.5.8 Model and transcribed HTRI kernel. Preserve the implemented sign of phase coupling and the actual per-step (not per-unit-time) plasticity.

## Conditional theorem

Write the source off-diagonal update as
\[
g_{n+1}=\Pi_{[0,1]}(qg_n+B(\phi_{n+1})),\quad q=1-\kappa^2,\quad \kappa=\ln2/(24\pi),
\]
with diagonal set to zero and \(B_{bij}(\phi)=\kappa\sum_h a_h^2 m_{hij}\cos[h(\phi_{bi}-\phi_{bj})]\), source harmonics \(h=(1,3,6,9)\), \(a=(1,.5,.33,.25)\), binary mask \(m\). For identical phase histories, nonexpansiveness of clipping in Frobenius norm gives
\[
\|\Delta g_n\|_F\le q^n\|\Delta g_0\|_F .
\]
The diagonal projection does not increase this norm. At fixed phase there is a unique fixed point for each edge, \(\operatorname{clip}(B/\kappa^2,0,1)\). With common time-dependent forcing two different initial weights forget their difference asymptotically. \(q=0.9999154859929605\), upper-envelope half-life about 8201.22 updates, not an empirical fitted half-life. Changing dt alone does not rescale the source plasticity rule.

For distinct phase histories the general inequality is
\[
\|\Delta g_{n+1}\|_F\le q\|\Delta g_n\|_F+\|\Delta B_{n+1}\|_F .
\]
Iteration gives
\[
\|\Delta g_n\|_F\le q^n\|\Delta g_0\|_F+
\sum_{k=1}^n q^{n-k}\|\Delta B_k\|_F .
\]
This upper bound is not an equality or lower bound. For matched batch/lane identities, cosine Lipschitz continuity and the centered pair-difference identity imply the conservative bound
\[
\|\Delta B_k\|_F\le
\kappa\sqrt{2d}\left(\sum_h a_h^2h\right)\|\Delta\phi_{k,\mathrm{centered}}\|_F .
\]
Center phase differences separately per batch. This concerns lifted coordinates, not arbitrary unmatched phase gauges. It does not prove stability or multistability of the full feedback system. Permanent distinct weight trajectories cannot persist under an identical imposed phase history; different phase histories, structural/topological degrees of freedom or independent retained state may carry memory. A long transient is not proof of multiple basins.

## Controlled witness

Seed 42, 64 common warmup updates, then 192 updates with opposed common lane phase increments ±.04 sin(2πj/36), then matched active phase state and frequency from A with B's trained coupling tensor transplanted into B. Both evolve without extra inputs for 1024 updates, dt=.01. In the replay control update B's trained weights with A's actual subsequent phases. Identical-history control matches A exactly for 16 steps. The source update was independently reconstructed on A's phases (maximum error 1.11e-16). No extra memory potential, new Hebbian law or permanent memory journal.

Full coupling gap 57.7703774 initially, 23.0840699 at 1024 (39.9583%); replay gap 22.2742626 (38.5565%); aggregate projected gap 1.28778692 to .607885238; projected phase RMS 0 to .0200209931. No positive violation of the conditional contraction bound. This establishes finite history-dependent structural efficacy for the chosen intervention, not spontaneous bistability. The planned three-seed run timed out after completing seed 42. No claim about seeds 43/44, long-run convergence of free trajectories, semantic recall or hardware. See receipt and portable diagnostic.

## Implication for state-space ontology

Distinguish contraction of a conditional geometry update from the stability of the combined \((\phi,g)\) state. The latter includes the backreaction of geometry on phase dynamics and cannot be inferred from the former. Future tests: multiple seeds and horizons; recurrence and return after perturbation in autonomous dynamics; compare frozen and feedback-conditioned phases; examine whether separate topology or operator memory is required. Do not insert a double well merely to obtain a positive result.
