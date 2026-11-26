# HTRI coupled phase–weight stability — v0.1

Status: LOCAL MODEL DIAGNOSTIC / EXACT CONDITIONAL TANGENT IDENTITIES / ASYMPTOTIC BASINS OPEN.
Part of the [joint memory and state-space ontology](memory-state-space-ontology-v0.1.md).
The installed PNAML Mobile 1.5.9 source was reviewed: coupled_stream.py, noema_surface.py, vendor/ciel_geometry/noema_surface_mmap.py. QHTRISurface is an internal virtual address space owned by the Coupler; /dev/shm/noema_surface/ is not a mandatory OS mount. The current private plugin release is pluginrel_6b07c6b6a1248191a76c1ad63ec878c4. Archive download into the local container was denied by its URL-access mechanism. No callable pnaml_coupled_run was available. No native host or H200 required for the local Model experiment; no full plugin Coupler execution claimed. The executed isolated CPU model uses the previously extracted v1.5.8 Model AST and local source-kernel transcription, not a byte-identical imported v1.5.9 release.

## 1. Source discrete tangent

For each of 32 batches of d=36, hold frequencies fixed and perturb phase p and symmetric zero-diagonal g. The 12 core oscillators are not perturbed. With the actual source sign, D_ij=p_i-p_j,
p_i'=p_i+dt (omega_i^mod + sum_j g_ij sin D_ij/d), modulo 2pi.
g_ij'=clip(q g_ij+B_ij(p'),0,1), q=1-kappa^2, diagonal zero.
B_ij=kappa sum_h a_h^2 m_hij cos[h(p_i'-p_j')].
Using lifted infinitesimal phase differences (away from coordinate wraps), the exact smooth-sector derivative is
\[
\delta p_i'=\delta p_i+\frac{dt}{d}\sum_j[
g_{ij}\cos D_{ij}(\delta p_i-\delta p_j)+\sin D_{ij}\,\delta g_{ij}].
\]
\[
s_{ij}=-\kappa\sum_h a_h^2h m_{hij}\sin[h(p_i'-p_j')],
\qquad v_{ij}=q\delta g_{ij}+s_{ij}(\delta p_i'-\delta p_j').
\]
Let r_ij=q g_ij+B_ij(p'). The directional derivative of clipping is v for 0<r<1, 0 outside [0,1], max(v,0) at r=0 and min(v,0) at r=1; diagonal zero. At kinks it is directional and not a single linear Jacobian. Finite perturbations crossing a clipping boundary need not match the infinitesimal derivative.

Symmetric weights ensure cancellation of pairwise sine terms and hence preservation of each batch's mean-phase perturbation with fixed frequencies. We work in the batch-centered tangent sector. The measured norm is sqrt(mean(dp^2)+mean(dg^2)), an explicitly chosen dimensionless diagnostic weighting, not physical energy or a canonical TIR metric.

## 2. Executed test

256 warmup steps, dt=.01, 512 followup steps, seeds 42,43,44; normalized random centered phase perturbation and symmetric interior-weight perturbation treated separately; comparison uses weight perturbation with its feedback into phase disabled. The directional derivative was checked against combined one-step nonlinear perturbation of 1e-8. A first check at 1e-6 for seed 42 exceeded the chosen derivative tolerance; near clipping transitions finite differences are step-dependent. Smaller check agrees to about 2.3e-8 relative error. This is a diagnostic of two sampled directions per seed, not an exhaustive tangent spectrum or Lyapunov exponent.

Final joint norm gains:
| seed | phase initial | weight initial | weight no-feedback | relative one-step derivative error |
|---|---:|---:|---:|---:|
|42|1.1958835362366607|.6029514183634733|.5782262278933659|2.213879866234105e-8|
|43|1.1733682547140716|.6008164369087645|.5774671738920427|2.2948788284947036e-8|
|44|1.2114283777963788|.6005929904971556|.578901732449964|2.1649604208342373e-8|

Weight-only initial perturbation creates phase differences in the coupled system (final phase RMS .15287924, .14801833, .14366094 for a unit initial weight RMS tangent). The final joint gains with feedback exceed control; the weight components alone also exceed the control in these samples. No-feedback conditional q^n bound passed at recorded horizons. Mean-phase perturbation and weight symmetry preserved to numerical precision. These are finite-time directions, not a proof of attractor stability or global multistability.

## 3. Exact sign-sensitive coherent-state test

The source uses +g_ij sin(p_i-p_j), not the conventional attractive +g_ij sin(p_j-p_i). At equal phases, equal modulated frequencies within each batch, and a fixed admissible symmetric g, the rotating coherent state has phase tangent
\[
\delta p'=(I+dt L_g/d)\delta p .
\]
Weight-to-phase derivative and phase-to-weight derivative vanish at exact equal phases. For any nonzero positive Laplacian eigenvalue the discrete phase multiplier is >1. This is a conditional linear instability of the coherent solution, not a claim about all nonlinear states with source heterogeneous frequencies.

Synthetic fixture uses equal frequencies and g*=clip(B(0)/kappa²,0,1), diagonal zero, same for all batches; its coherent rotating trajectory has constant g*. From the source masks the computed maximum eigenvalue is 36.000000000000085, 35 positive modes. Predicted gain 1.01; measured single-step phase RMS gain for 1e-7 perturbation along the top eigenvector 1.0100000001724583; fixed weight error 0. No source sign changed. The coherent fixture does not represent native initialization.

## 4. Ontological consequences

- Memory weight contraction under a fixed imposed phase history does not imply contraction of the full state space.
- Phase and geometry transport perturbations across layers; they can decay at different rates and the response can retain history after its initial carrier attenuates.
- Uniform phase coherence is not a generic attracting memory pattern for this implemented sign.
- Neither finite amplification nor a coherent-state instability proves multiple stable memories. Next: nonlinear return/recovery and recurrence tests at matched frequencies, long-horizon trajectories, multiple initial perturbations and verified source bindings. No arbitrary double-well added.
- Preserve the original TIR reference/transport contracts and avoid interpreting a norm increase as semantic significance, physical energy or consciousness.

Reference diagnostic and compact receipt are stored alongside this formalism. The repository adapter is a port of the executed local algorithm; its import and full repo suite were not run in this pass.
