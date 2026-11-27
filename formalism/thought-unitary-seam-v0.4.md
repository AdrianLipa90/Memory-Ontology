# Thought optics: balanced seam and projective geometry — v0.4

Author research direction: Adrian Lipa, Pip Project.
Status: EXACT C4/GAUSSIAN INTEGER SEAM / FINITE CP1 CONFORMANCE.
Extends [graph propagation v0.3](thought-graph-propagation-v0.3.md).
Base: b1f590d5530903f56ec8fec5f0813c80fa8d0971.

## 1. Existing RDSS seam, a distinct unitary profile

The source [RDSS relational dynamics](../engines/rdss_relational_dynamics_v32.py)
implements seam(a,b,phi) = ((exp(i phi/2)a + exp(-i phi/2)b)/2,
(exp(i phi/2)a - exp(-i phi/2)b)/2) and seam_inverse.
Its pair norm squared is half the input norm squared; the original
chain_seams has a separate norm-retaining boundary contract.
Keep both original operators unchanged.

For a closed, two-channel, balanced scattering fixture, define the
explicit normalization U_phi = sqrt(2) * seam_phi:
\[
U_\phi=\frac1{\sqrt2}
\begin{pmatrix}1&1\\1&-1\end{pmatrix}
\begin{pmatrix}e^{i\phi/2}&0\\0&e^{-i\phi/2}\end{pmatrix}.
\]
Direct multiplication gives U_phi^dagger U_phi=I, and its inverse
is diag(e^{-i phi/2},e^{i phi/2}) H, where H=U_0=H^dagger.
A complete layer of disjoint pairs, each with unitary scattering,
is unitary, as is its composition with independent U(1) phase shifts
and a permutation. This does not make the unrestricted v0.3 graph
transfer unitary. No implicit normalization after arbitrary branching;
if channels are unmatched or coupled to other sectors, the closed
pair profile does not apply without a declared extension.

## 2. Exact sector without square-root arithmetic

With one common denominator (sqrt(2))^d, store Gaussian integer
numerators A,B and the integer exponent d. Transport A,B using
the existing [C4 PNV](../projects/pip-project/native/PIP_THOUGHT_C4_TRANSPORT_V0_3.pnv)
if the prescribed phase factors are in {1,i,-1,-i}. For the seam
the factors are opposite half phases; general edge phase delays
can also be composed before U_0. Do not round arbitrary phases.

\[
(A,B,d)\longmapsto(A+B,A-B,d+1).
\]
This is the exact numerator action of H on that sector; the squared
norm is (|A|^2+|B|^2)/2^d. The parallelogram identity proves its
preservation. Two zero-phase seams give (2A,2B,d+2), the same
normalized amplitudes, without deleting two historical steps.
Bright/dark are amplitude channels, not truth/falsehood or
epistemic acceptance. Exact norm is a model invariant, not physical
energy. A zero channel is not a deleted path or unknown evidence.

[PIP_THOUGHT_BALANCED_SEAM_V0_4](../projects/pip-project/native/PIP_THOUGHT_BALANCED_SEAM_V0_4.pnv)
uses only SOURCE, DIFFERENCE, IDENTITY and COMPOSITION. Two witnesses
expose common scope and denominator depth; the program does not
admit routes or register a new runtime guard. Inputs must be typed
by the source owner, with nonnegative integer depth, matched basis
and independent immutable lineage references. It receives the
already phase-transported inputs; the phase reference is retained,
not independently validated by this step. Full graph orchestration,
non-C4 multiplication and arbitrary precision phase inputs are open.
The new operator does not advance the Hotel clock.

## 3. Fubini–Study readout

On the nonzero normalized two-component amplitude sector, use the
standard projective Fubini–Study distance (half Bloch angle):
\[
d_{FS}([\psi],[\xi])=\arccos
\frac{|\langle\psi,\xi\rangle|}{\|\psi\|\|\xi\|}.
\]
The source [RDSS memory mechanics](../engines/rdss_memory_mechanics_v32.py)
fs_log uses this half-angle convention on CP1. The conformance harness
maps normalized pairs to Bloch vectors and compares the norm of fs_log
to the projective distance away from the antipodal cut locus; distance
itself remains defined there, the source tangent chart does not.
Under a common unitary transformation the overlap and distance
remain unchanged. Global phase is invisible to this projective
readout, not to occurrence-level provenance.

For 36 equal-magnitude channels with phase vectors V,Q, the existing
phase_readout36 returns R=|mean(exp(i(Q_j-V_j)))|^2. This is exactly
the squared normalized inner-product magnitude of the equal-amplitude
vectors; thus d_FS=acos(sqrt(R)) in this profile. The 36-channel
sector and CP1 are distinct; a general amplitude distribution must
not be collapsed to 36 phase coordinates or treated as a CP1 state.

## 4. RDSS/IDT memory intervention in balanced thought optics

Use two mirror geodesic corridors of equal duration and geometry,
with the action terms from [v0.2](rdss-thought-action-v0.2.md).
The split state H(1,0)=(1,1)/sqrt(2); each arm receives its
PNCS action phase; apply H again. For relative action phase
delta=(S_R-S_L)/lambda_H, the outputs are
\[
J_B=\cos^2(\delta/2),\quad J_D=\sin^2(\delta/2),\quad
J_B+J_D=1.
\]
The state moves through CP1; its distance to the unperturbed output
is acos(|cos(delta/2)|). Compare with the raw v0.3 unnormalized
path sum and its different scale.

Use the existing Memory.encounter with eta=0 to isolate a learned
weight change 1->2, keeping accessibility and semantic mass fixed.
For the candidate V=beta/w and unit duration/action scale the
relative phase is beta/2; beta=0 is the coupling ablation and a
failed encounter is the evidence control. Actual source disk_distance,
IDT duration, v0.2 PNV action fold and PNCS semantic_u1_coupling are
used in the test. General phase transport is floating reference
execution, not a new native numeric engine. This is a causal witness
within the declared finite model, not an endogenous learning law.

## 5. Integration boundaries

The existing 36D overlap and CP1 FS chart are exercised, not
replaced. The memory coupling beta/w remains a modeling choice from
v0.2; no derived geometry deformation, Kuramoto backreaction or
Kepler/Collatz feedback is asserted. Such a closed-loop extension
requires explicit state, a source-defined constitutive update and
verified events; coherence does not itself authorize reinforcement.
No live AUX, hardware or dynamic state hashing. The host harness
provides immutable test observations and calls the existing PNCS
interpreter; no new runtime or callback. The manuscript remains unchanged.
