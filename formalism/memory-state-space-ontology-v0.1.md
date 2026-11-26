# Joint Ontology of Memory and State Spaces — v0.1

Author of the underlying Memory Ontology and TIR–RDSS programme: Adrian Lipa.
Research extension, 2026-11-26. Status: CANDIDATE FORMALISM / FINITE REFERENCE MODEL. This supplements, rather than replaces, the substrate-neutral core and its taxonomy. Scope is memory and state spaces; attention, volition and phenomenal consciousness are outside the present research objective.

## 1. State, carrier and history

Retain the core law
\[
Z_t=(X_t,M_t),\qquad X_{t+1}=F(X_t,u_t;M_t),\quad M_{t+1}=U(M_t,X_t,u_t).
\]
An active state is not the state space, an occurrence is not its coordinate representation, and memory is not the totality of past states.

Represent a history-conditioned state space by
\[
\mathfrak X_t=(\Sigma_t,G_t,\nabla_t,V_t,M_t)
\]
with admissible transitions \(\mathcal A_t(x,u)\) and an observation map \(P_t:\Sigma_t\to Y_t\). Here \(\Sigma_t\) is the carrier, \(G_t\) a metric where defined, \(\nabla_t\) a transport/connection, \(V_t\) an evaluation potential, and \(M_t\) history-bearing structure. None of these geometric objects is assumed to exist on every substrate. In a graph realization use weighted edges and typed transports; in a smooth realization use a manifold, tensors and a declared connection. A changing carrier is a family of spaces with explicit comparison maps, not automatically a fixed manifold or a globally trivial fiber bundle.

A proposed geometry update is
\[
(\Sigma_{t+1},G_{t+1},\nabla_{t+1},V_{t+1},\mathcal A_{t+1})
=\mathcal B(\Sigma_t,G_t,\nabla_t,V_t,\mathcal A_t;M_t,M_{t+1},e_t).
\]
The event \(e_t\) has occurrence identity, typed relations, context, source and outcome. The constitutive map \(\mathcal B\) is open in general; it need not change every component. Changes of coordinates must be distinguished from changes of the modeled structure. Compare a metric difference on the same identified carrier or through a declared pullback; do not subtract tensors or vertices in unrelated spaces.

## 2. Causal memory criterion

For matched active state, input, boundary, observation contract and intervention horizon, a memory variable qualifies when:
1. distinct histories leave distinct values of that variable;
2. the difference persists beyond the inducing event;
3. intervening on it changes a subsequent reachable trajectory, transition cost, distribution or other explicitly declared observable.

Let \(\mathcal R_H(x,m;u)\) denote the admissible reachable states within horizon \(H\) and input protocol \(u\). Compare both reachable sets and the induced path laws or costs. A change of positive edge weights can change path preference without changing graph topology or unbudgeted reachability. A topology change modifies admissible edges; a budget-dependent reachable set can change even with topology fixed. These are distinct memory mechanisms.

A proposed causal witness on a common observable space is
\[
D_H(m_1,m_2)=d(\mathcal L(P X_{t:t+H}\mid do(M=m_1),x,u),
\mathcal L(P X_{t:t+H}\mid do(M=m_2),x,u)).
\]
Choose and declare \(d\), tolerance, horizon and observation. \(D_H=0\) for a particular contract does not prove no memory exists in any other contract. Correlation or mutual information alone is not a causal witness.

## 3. Reference-conditioned scalar layer (TIR / PNCS)

For typed reference \(V\) and comparison \(Q\) on the existing 36-phase carrier,
\[
z(V,Q)=\frac1{36}\sum_j e^{i(Q_j-V_j)},\quad R=|z|^2,\quad
S_{\rm rel}=-\frac{\ln2}{24\pi}\ln(R+\epsilon).
\]
Retain the full phase lift, occurrence and provenance. A joint reference transformation is distinct from changing the reference while holding the observation fixed. On the equal-amplitude projective tangent sector the Fubini–Study metric is \((I-\mathbf1\mathbf1^T/36)/36\); its rank is 35, so the common phase is lost by projective reduction. It does not identify the entire space with a rank-three TIR sector.

Retain semantic mass, density, viscosity, exploration temperature, accessibility, coherence, relative phase, defect, potential and evidence as distinct quantities. A scalar is not the complete state, and a metric is not a truth value. In particular the CIEL score, PNCS exact realization mass and recall accessibility have different contracts. No new scalar weighting or physical calibration is asserted here.

## 4. Transport, geometry and memory of paths

In the admitted TIR binary-frame sector, a relation generator \(\mathcal E_{xy}\in\operatorname{Herm}_0(2)\) determines \(\ell_{xy}^2=\operatorname{Tr}(\mathcal E_{xy}^2)/2\).
Transport \(W_{xy}\) maps y-frame components to x-frame. The endpoint closure defect is
\[
\mathcal C_{xyz}=\mathcal E_{xz}-(\mathcal E_{xy}+W_{xy}\mathcal E_{yz}W_{xy}^{\dagger}).
\]
Its norm is invariant under consistent local frame changes. Compatible endpoints select zero defect in the source sector; context-extended relations need not close. This is distinct from rotational loop holonomy. A nonzero closure defect is not automatically an error or a memory trace: history, persistence and causal efficacy remain necessary.

For paths, retain ordered transport \(W_\gamma\) with a specified structure group and representation, and occurrence-level lineage. Two paths with the same endpoints can have distinct holonomies. Conversely, a common holonomy does not imply identical histories. The existing signed integer winding chains and the raw-history/behavioral-quotient distinction remain valid; an inverse pair can be behaviorally neutral without erasing its recorded provenance. No general groupoid, smooth continuum or full PhaseNav-to-TIR identification follows.

## 5. Memory and state-space crosswalk

| State-space structure | Possible retained memory object (not automatic equivalence) |
|---|---|
| State / configuration | S: state memory |
| Typed relation / tensor | R: relational memory |
| Ordered trajectory / transport | Γ: path and procedural memory |
| Metric, weights, potential | R, Γ, O: learned preferences and transition constraints |
| Admissible topology / barriers | T: connectivity memory |
| Transition/update map | O: operator memory |
| Boundary, context, reference | B: boundary memory |
| Hidden coordinates and projected dynamics | Access axis: implicit or inaccessible memory, if causal criteria hold |
| Invariant | Identity-preserving constraint, not necessarily a trace of history |
| Attractor / basin | Candidate persistent pattern, not necessarily learned |
| Bifurcation | Possible structural reorganization, not proof of consolidation |

The original six retained-object primitives S,R,Γ,T,O,B remain the taxonomy backbone. Episodic, semantic and procedural describe organization; explicit/implicit describe access. Geometric, structural and dynamic memory are mechanism profiles that may overlap these axes.

## 6. Hidden state and reduced memory

For a frozen linear block model \(z'=Az+Bh,\ h'=Cz+Dh\), eliminating hidden variables yields
\[
z_{n+1}=Az_n+\sum_{j=0}^{n-1}BD^jCz_{n-1-j}+BD^nh_0.
\]
This is exact for that model; a nonlinear evolving geometry needs its own reduction. Non-Markovianity of an observation is neither necessary nor sufficient for memory under the core law. An enlarged full state may be Markovian. Observability, accessibility, persistence and causal efficacy are separate tests. In particular a hidden symmetry direction that cannot affect any admitted observable does not establish operational memory under that contract.

## 7. Finite operational realization and test programme

Use a finite graph with fixed occurrence identities, positive symmetric lengths for its metric sector, and distinct nonnegative costs for routing. Keep observed event identity and validation separate from learned weight. A verified traversal may decrease its route cost; a failed or replayed event does not reinforce it in the declared fixture. A later accessibility decay need not revert that cost. No claim that this is a universal constitutive law.

Reference priorities:
- history intervention at matched active state and input, and a no-update control;
- topology versus cost-conditioned reachability; invariance under relabeling;
- persistence after decay of accessibility, distinguish event record from learned geometry;
- partial reconstruction and provenance, read-only recall versus reconsolidation;
- spontaneous consolidation in the existing adaptive dynamics without inserting a double-well potential;
- generalization to held-out histories, alternative state-space representations and substrate-neutral behavioral equivalence;
- derive the source-compatible transport/metric update and nonlinear reduced memory; benchmark uncertainty and loss.

## 8. Source and evidence ledger

- [Core law](memory-law-v0.1.md) and [ontology](../ontology/memory-ontology-v0.1.md): original active-state/memory distinction, history/persistence/causality, EVENT → TRACE → PATH → STRUCTURE → LAW.
- [RDSS V32 equation crosswalk](rdss-book-v32-mechanics-crosswalk.md): source equations, not a blanket derivation of geometry evolution.
- [TIR contextual geometry](tir-contextual-relational-geometry-v0.1.md): pinned source TIR spatial core, discrete solder form, W transport and endpoint closure; CLX2 phase scalar.
- [Interdisciplinary index](rdss-interdisciplinary-isomorphism-index-v0.1.md): exact identities, structural analogies and candidates kept separate.
- [CPU feedback](../benchmarks/pnaml_closed_loop_memory_fixture_receipt.json), [classical correspondence](../benchmarks/pnaml_classical_isomorphism_receipt.json), [metastability](../benchmarks/pnaml_memory_metastability_receipt.json), [reduction](../benchmarks/pnaml_mori_zwanzig_receipt.json), [observability](../benchmarks/pnaml_observability_cognitive_receipt.json): prior recorded model experiments, not rerun by this integration. Constructed bistability is not spontaneous HTRI consolidation. Source model diagnostics are not physical or semantic validation.

The integration is a candidate extension of Memory Ontology, not a change to the TIR/RDSS canon, native PNAML runtime or physical interpretation. No physical mass/energy equivalence or consciousness claim. A state-space description must be substrate-neutral at the ontology layer; concrete metric and constitutive laws are representation- and domain-dependent.
