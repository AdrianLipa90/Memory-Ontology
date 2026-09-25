# Memory Representation Category — v0.3

Status: **GREMLIN_SYNTHESIS_CANDIDATE / PARTIAL_TYPED_MORPHISMS / NO_MAIN_MERGE**

## 1. Why the branch synthesis is not a group

The independent Memory-Ontology lines contain operations that are not globally
closed or invertible.

The signed ternary path sector obeys

\[
1+1=2\notin T_3.
\]

Holographic projection may intentionally discard information not required by a
declared observable. Reconstruction is defined only for admissible projection
sets satisfying support and provenance gates.

Therefore the combined system is not a single group.

## 2. Why it is not a global groupoid

A groupoid requires every morphism to be invertible.

The stack contains:

- lossy projections;
- partial reconstruction;
- coarse-graining;
- compiler mappings admitted only under \((\varepsilon,H)\) contracts.

These are not generally invertible. Hence a global groupoid claim is false.

Exact sector isomorphisms may still form local groupoid fragments. The current
example is

\[
\{\pm1\}^3_{\rm PhaseNav}
\cong
\{\pm1\}^3_{\rm Stella\ corner}.
\]

## 3. Minimal organizing structure

Let \(\mathsf{Mem}\) denote underlying Memory-Ontology memory identities and
let \(\mathsf{Rep}\) contain typed manifestations of those memories.

There is a projection

\[
p:\mathsf{Rep}\to\mathsf{Mem}
\]

sending each representation object to the underlying memory identity.

For one memory \(m\), the set

\[
p^{-1}(m)
\]

is its representation fiber: binary, ternary, orbital, quantum-native, or
other admissible manifestations.

We do not yet claim the stronger categorical conditions required for a formal
Grothendieck fibration. The current claim is only a **category over Memory
Ontology with explicit representation fibers**.

## 4. Typed partial morphisms

A morphism

\[
f:R_a(m)\rightharpoonup R_b(m)
\]

contains:

- source and target representation types;
- morphism role;
- declared domain sector;
- task observable and distance;
- error bound;
- horizon;
- invariant-preservation flag;
- provenance-preservation flag;
- invertibility witness when available.

Roles currently include:

\[
\text{IDENTITY, COMPILER, EMBEDDING, PROJECTION, RECONSTRUCTION, OBSERVABLE}.
\]

Partiality is explicit rather than repaired silently.

## 5. Behavioral composition

For two compatible representation compilers

\[
R_1\xrightarrow{f}R_2\xrightarrow{g}R_3,
\]

under a metric/divergence satisfying the triangle bound,

\[
\varepsilon_{g\circ f}
\le
\varepsilon_f+\varepsilon_g.
\]

The supported horizon is bounded by

\[
H_{g\circ f}=\min(H_f,H_g).
\]

Composition fails closed when the declared observables or distance contracts
do not match.

This connects directly to the existing representation-duality criterion

\[
d_H(R_a,R_b)\le\varepsilon.
\]

## 6. Algebraic path fiber

Inside the path representation fiber, the previously derived exact algebra is

\[
T_3^E
\hookrightarrow
C_1(G;\mathbb Z)
\xrightarrow{\partial=B}
C_0(G;\mathbb Z).
\]

The ternary object is a partial exact sector, not a subgroup under unrestricted
addition.

Overflow is lifted exactly:

\[
t\boxplus u=
\begin{cases}
t+u\in T_3^E,&\|t+u\|_\infty\le1,\\
\operatorname{Lift}_{\mathbb Z}(t+u),&\text{otherwise}.
\end{cases}
\]

## 7. Orbital phase as character

For edge phases \(\theta\),

\[
\chi_\theta(n)=e^{i n^T\theta}
\]

is a group character of the integer chain group into \(U(1)\).

Thus the orbital phase coordinate on the exact path sector is

\[
\phi(n)=n^T\theta\pmod{2\pi}.
\]

The U(1) character is an observable morphism. It is not generally invertible
back to the full chain.

## 8. Holographic projection and reconstruction

A projection

\[
\pi_j:R(m)\to P_j(m)
\]

may preserve only a declared invariant.

For an admissible set \(S\), reconstruction is a partial morphism

\[
\rho_S:
\prod_{j\in S}P_j(m)
\rightharpoonup
R(m)
\]

defined only when support, compatibility and provenance requirements pass.

Therefore holographic reconstruction is naturally represented by partial typed
morphisms rather than by global inverse arrows.

## 9. Provenance as an admission condition

Behavioral equivalence alone is insufficient for historical identity.

A representation morphism is admitted only when the relevant invariant and
provenance commitments are preserved.

This keeps:

\[
\text{RECALLED}
\neq
\text{RECONSTRUCTED}
\neq
\text{INFERRED}
\neq
\text{IMAGINED}.
\]

## 10. Falsification result

The new structure survives the following negative checks:

- global group: **REJECTED** by ternary non-closure;
- global groupoid: **REJECTED** by lossy/partial arrows;
- untyped adapter graph: **REJECTED** because observable and provenance
  contracts affect admissible composition;
- exact local isomorphism fragments: **ADMITTED** where inverse witnesses exist;
- category of typed partial morphisms: **CURRENT MINIMAL FIT**.

Reference implementation:

`algebra/memory_representation_category.py`

Targeted test gate:

```text
12 passed, 0 failed
```
