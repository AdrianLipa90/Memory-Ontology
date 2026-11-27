# Thought graph propagation — v0.3

Author research direction: Adrian Lipa, Pip Project / The Reality of the Imaginary.
Status: EXACT FINITE GRAPH RECURRENCE / NATIVE PNV VERTEX FOLD / C4 EXACT SECTOR.
Extends [thought path interference](thought-path-interference-v0.1.md) and [RDSS thought action](rdss-thought-action-v0.2.md). Base 30289415fed271239a47bb4ce8cab405e7786066.

## 1. The potential field

Fix one declared finite directed multigraph with immutable edge identities,
context, memory snapshot M, and action scale lambda_H. Different edges can
share endpoints. The source owns the graph and the action inputs. At each
layer, one step means one edge traversal, not necessarily equal intrinsic
duration or Hotel causal time. For a fixed-time experiment require equal
step durations, or extend vertices by the time state and compare only
compatible endpoints. The carrier must include all history-dependent
coordinates necessary to make edge transport Markovian; otherwise merging
prefix amplitudes at a vertex is invalid.

For edge e:u->v let t_e=w_e exp(i s_e/lambda_H), with w_e nonnegative
dimensionless amplitude weight (not learned route weight by default).
The action s_e is the integrated K_e-U_e from v0.2. Use the existing PNCS
semantic U(1) transport for arbitrary phases.

\[
\psi_0(v)=\mathbf1[v=a],\qquad
\psi_{k+1}(v)=\sum_{e:u\to v}t_e\,\psi_k(u).
\]
In matrix form T_{vu}=sum_{e:u->v}t_e, psi_k=T^k psi_0 for a frozen
graph. Ordered products apply for time-dependent layers. Distributivity
gives by induction exactly the sum of products over all length-k directed
walks from a to v. Cycles and parallel edges are included, no carry-forward
or implicit absorbing target. A different terminal-path or stopping
contract requires an explicit extended graph. This is a fixed finite
horizon, not an infinite sum. Path-dependent weights/actions require
an augmented state or the original explicit path sum.

This is a finite optical amplitude algebra correspondence, not an
identification of thought with photons. T is not necessarily unitary:
for branching without normalization, total squared amplitude can grow.
Neither squared magnitude nor walk count is a truth value, probability,
choice or a new observation.

## 2. Preserve alternative histories without enumerating them

Alongside amplitude retain the independent integer walk count
\[
N_0(v)=\mathbf1[v=a],\qquad N_{k+1}(v)=\sum_{e:u\to v}N_k(u).
\]
Even zero amplitude can carry a nonzero count and provenance. This counts
all declared graph walks, including zero-weight edges, not realized trips.
Each (family, context, M, graph, scale, layer, vertex) is a reference to
one retained checkpoint. Each incoming entry records the predecessor
reference, edge and action reference, transported contribution and count.
References, not recursive copies of predecessor checkpoints, form a
layered provenance DAG. With immutable graph/action bindings and retained
checkpoints the full ordered walk family can be unfolded if needed.
Different paths are not collapsed as historical identities; the potential
readout is compressed. No new Hotel occurrence is created for an imagined
walk. The count can be exact even when amplitudes are approximate.

The mathematical recurrence takes O(H|E|) scalar operations and
O(|V|) current numeric states (including isolated vertex initialization
O(H|V|)); retained lineage has O(H(|V|+|E|)) entries. Exact integer bit
complexity grows with counts. These are recurrence operation counts, not
measured runtime speedups. The PNV fold's serialization and repeated
local list copies can incur extra overhead. No claim of constant-size
unbounded history or live parallel hardware.

## 3. Native operators and explicit orchestration seam

[PIP_THOUGHT_C4_TRANSPORT_V0_3](../projects/pip-project/native/PIP_THOUGHT_C4_TRANSPORT_V0_3.pnv)
computes the four exact unit rotations (x,y),(-y,x),(-x,-y),(y,-x).
Integer components remain exact, including values beyond binary64.
This is the C4 subgroup of U(1); no rounding a general phase to a C4 code.
The existing source owner selects the declared orientation. For arbitrary
phase/weight the existing pinned PNCS semantic_u1_coupling computes the
incoming contribution; its reference floating precision applies.

[PIP_THOUGHT_GRAPH_VERTEX_STEP_V0_3](../projects/pip-project/native/PIP_THOUGHT_GRAPH_VERTEX_STEP_V0_3.pnv)
folds a single incoming contribution and count into a target layer.
Uses only SOURCE, IDENTITY, DIFFERENCE, COMPOSITION. Four witnesses report
predecessor scope/layer/source, target, graph and scale consistency.
They are not new authorization rules. Counts, source amplitude, edge
uniqueness, action binding, completeness and references are supplied by
the existing owner; the operator cannot infer their validity or deduplicate
a repeated edge delivery. Keep distinct parallel edge IDs. The old
path-sum step and action fold remain unchanged. No mutation of live AUX,
no new clock, no dynamic AUX hash. Standard PNV receipts concern static
test fixtures.

The test harness schedules immutable finite layers and feeds existing
PNCS transport or exact C4 outputs into the native vertex fold. It is
not an added runtime engine, an actual PNCS graph scheduler, or a live
producer binding. Full native arbitrary complex multiplication and
source-bound orchestration remain open. No new callback is registered.

## 4. Invariants and validation

- Exact C4 zero-amplitude cancellation preserves count and edge lineage;
  later transport cannot resurrect an already cancelled scalar without
  changing the declared state/coherence sector.
- Explicit walk enumeration and graph recurrence agree for finite cyclic
  multigraphs with weighted complex transport.
- Gauge shift t'_e=exp(i(chi_v-chi_u))t_e gives
  psi'_k(v)=exp(i(chi_v-chi_a))psi_k(v); intensities and counts invariant.
- Two parallel unit edges per layer yield 2^H walks. H=80 verifies exact
  integer count and amplitude with 160 incoming fold operations, not
  enumerating 2^80 histories; no measured speedup asserted.
- RDSS v0.2 action and verified memory-weight update feed the recurrence.
  Beta=0 and failed encounter are controls. Retained provenance and
  amplitudes remain distinct.
- Wrong predecessor layer/snapshot/context or target remains visible.

## 5. Book seam

Pip need not visit every possible corridor separately. A finite potential
field propagates across the declared relational graph, merging coherent
contributions at common typed states. A dark room may still have many
possible incoming journeys. Spider keeps the dependency DAG, while
Owl checks evidence only after candidate evaluation. This is not an
automatic conclusion admission. The next book revision follows code
validation.
