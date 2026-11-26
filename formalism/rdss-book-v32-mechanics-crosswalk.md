# RDSS Book I V32 — memory mechanics integration

Source: Adrian Lipa, *The Reality of the Imaginary*, V32 Relational Atlas Edition. Printed page numbers below (PDF page = printed page + 1). This is an implementation crosswalk, not a replacement for the book or a claim that every chapter has been implemented.

## Equation and mechanism inventory

| Printed pages | Source equation / mechanism | Executable reference |
|---|---|---|
| 60–61 | J(p)=1-p; H=-p ln p-(1-p)ln(1-p); D_H=ln2-H; sum w_e (norm_g(F_e)^2 + lambda_e D_H(p_e)) | entropy, defect, action_defect (caller supplies metric norms) |
| 62–63 | symmetric probability [1+2 sqrt(p(1-p)) cos(Delta theta/2)]/2; complementary antisymmetric probability; Omega(s)=s/(1-s) on Re(s)=1/2 | half_interface, zero_axis |
| 64–75 | Euler-root genealogy; kappa=ln2/(24pi); scale=2^-d, inverse-square=4^d; identity/occurrence/path/provenance distinct | branch_address, KAPPA, contraction, Memory |
| 86–91, 98–101, 267–269 | exponential decay; successful recall a'=a+eta quality rho(1-a); F=F0 a rho K_d(x) typed_match; auxiliary accelerated Collatz and unreduced parity phase q_C | decay, recall, attraction, collatz_step/inverse, parity_phase |
| 105–108 | register -> weights -> routing -> evidenced update; p_i=w_i/sum w, cost=1/w | Memory.encounter, routing_probabilities |
| 119–120 | conformal candidate g=2^(2D(x)) eta; physical length and field calibration separate | documented only; metric field equation not implemented |
| 132–133 | L_rel=.5 g(qdot,qdot)-V(q); grad force; action defect distinct from stationary action | scalar FOLD witness; general metric dynamics open |
| 142–144 | m=.25e+.25z+.20d+.15P+.15b; delta tau=(delta t/.353)(1-r²) C sqrt(m A)/(1+Delta); T²=a³/m | semantic_mass, ciel_clock, kepler_period |
| 265–266 | CP1 Fubini–Study tangent log, oriented dyad eP=n cross eQ; delta m=xi.eQ+i xi.eP; event kick q delta m; Kepler segments | fs_log, frame, displacement, transport, kick, kepler_segment, orbit_invariants |
| 267–270 | distinguish accessibility, learned geometry, episode detail and query-specific entropy; provenance retained | Memory state separates accessibility, learned weight, exact mass reference, history; archive policy open |

Reference kernel: [rdss_memory_mechanics_v32.py](../engines/rdss_memory_mechanics_v32.py). Test command from repository root: python -m unittest discover -s tests -p test_rdss_memory_mechanics_v32.py.

## Integration boundary

The CIEL five-component scores must be supplied by their source operators; no invented weights for missing values. The original PNCS regularized candidate kernel K_d=(x0/(x0+x))^(d_eff-1) uses effective dimension independent of room depth. Phase itinerary uses the unreduced map, while odd accelerated moves consume two itinerary steps. The root address convention stores exact rational multiples of pi with the branch genealogy. The CP1 reference uses half the Bloch angle and parallel transport on the unit sphere; antipodal ambiguity fails closed. The orbit integrator is velocity Verlet in the declared normalized Kepler reference.

A verified event is explicit caller input, not automatic verification by the arithmetic. The model retains an immutable occurrence identity and exact realization mass reference; accessibility updates do not overwrite them. A failed encounter is recorded without reinforcing access. The illustrative learned-weight increment is a candidate implementation of the source routing example; it is not a new canonical law.

The FOLD bridge is a separate candidate in [fold-collatz-memory-dynamics-candidate-v0.4.md](fold-collatz-memory-dynamics-candidate-v0.4.md). Preserve the exact distinction between semantic mass and erasure-cost equivalent. Neither conformal scaling nor the Landauer analogy proves physical mass, spacetime curvature, or free energy. Full QHTRI coupling, relational metric field evolution, 36D transport, source CIEL score implementations, episodic consolidation, and the remainder of Book I need independent integration and verification.


## Second integration pass — transport and network dynamics

| Printed pages | Mechanism | Reference implementation |
|---|---|---|
| 119–120 | prescribed conformal factor exp(2D ln 2), relational Lambda scalar B omega N phi/(A R)+kappa | conformal_factor, relational_scalar; no physical source equation |
| 126–132, 151, 192 | Poincare routing distance and additive goal-conditioned path cost | disk_distance, goal_cost; not a stationary-action solver |
| 140–141 | IDT eta=W+ + W-, j=W+ - W-, chi=j/eta; intrinsic duration and relational lapse | activity, duration, lapse |
| 184–186 | symmetric graph diffusion; positive explicit step bound; transverse circulation not reducible to scalar gradient | diffusion_step; full transverse fluid mechanics open |
| 214–215 | local-frame transport; bright/dark half-frame channels, exact inverse and norm retention | gauge_transform, seam, seam_inverse, chain_seams |
| 216–218 | ordered SU(2) Wilson products; conjugation-invariant trace | wilson_loop, su2; continuum curvature solver open |
| 223–227 | coupled phase dynamics, order parameter and higher harmonic, unwrapped phases | phase_rhs, phase_step, order_parameter |
| 231–234 | 36D relative phase, PNCS squared overlap, DNCrypt novelty, coordinate-wise address gate, relative phase composition | phase_readout36, phase_address_match, relative_phase |

Reference implementation: [rdss_relational_dynamics_v32.py](../engines/rdss_relational_dynamics_v32.py); tests: [test_rdss_relational_dynamics_v32.py](../tests/test_rdss_relational_dynamics_v32.py).

The directed AdaptiveEdge coupling w=a*c is a candidate bridge, not an equation attributed to the source. Verified encounters reinforce accessibility and conductance, while accessibility decays independently. In the independent JS reference witness, identical initial 36-phase vectors and frequencies are evolved with the two memory states on a directed ring. The active coupling gives an unwrapped RMS difference of 0.9810776583 rad; disabling coupling yields zero. See [receipt](../benchmarks/rdss_v32_ring_intervention_receipt.json). This is a finite numerical demonstration, not a full native NOEMA stream or proof of physical nonlocality.

### Additional CIEL source

The pinned [CIEL orbital foundation specification](https://github.com/AdrianLipa90/CIEL-The-Living-Core/blob/df431ff5ac551d8ac31f95f3122722d7662474c2/na_brudno/przed/src/CIEL_Orbital_Foundation_Packk/06_SUBJECTIVE_TIME_WINDING_AND_SEMANTIC_MASS.md) confirms the five mass components, and defines weighted winding sum Delta phi * Delta t / Delta tau / (2 pi). This is distinct from bare unwrapped turns. It does not specify a complete executable operator for each mass score. Do not impute missing definitions. Its attractor-weight period formula uses A_eff, while V32 p.142 specifies m in its normalized orbital example; these are separate readouts unless a binding is established.

### Validation scope

Source-mapped functions and unit-test files committed; independent JS ring witness executed. Python suite, existing repository-wide tests, and GPU/native QHTRI not run in this pass. Remaining work includes typed irreversible/ reversible learning events, source score derivation, full metric dynamics, vectorized transport and later chapter mechanics.
