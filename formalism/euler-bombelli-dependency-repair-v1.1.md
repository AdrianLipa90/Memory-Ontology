# EBRE dependency repair — v1.1 candidate

Author research direction: Adrian Lipa. Base 8be69ad.
Extends [v1.0](euler-bombelli-reflective-extension-v1.0.md), [truth dependency](truth-dependency-consolidation-v0.1.md) and [epistemic repair](epistemic-debt-dependency-repair-v0.1.md).
The Hotel is history. Correction appends a new event and never removes the previous occurrence.

## Finite support graph

The original EBRE theorem is Q, with primary support A produced by
the original finite proof program. A separate declared support is
B=S AND (S implies Q). These Boolean inputs indicate retained active
premises, not asserted ground truth of the world.
Q is derivable iff A OR B. V is derivable iff (Q AND (Q implies V))
OR (R AND (R implies V)). W is derivable iff V AND (V implies W).
The original v1.0 proof checks one restricted propositional family;
the new source graph combines its result with independent alternative
proof routes in this fixed monotone fragment. Distinct routes do not
imply statistical independence of evidence origins. False derivability
means NOT_DERIVED, not a proof of negation.

The native PNV graph computes the before/after supports and three
conclusion statuses, reflexive downstream recheck flags, and actual
status changes. A premise change marks all downstream candidates for
re-evaluation; alternative support can keep Q, V or W derivable.
A theory identity change outside this fixed formula family is outside
the test scope. The original v1.0 proof reference is carried, not
cryptographically authenticated by the repair graph. No new opcodes,
interpreter, runtime gate, live AUX or transport.

## Memory intervention

A correction appends a selected occurrence through the existing Hotel
successor. In a test-only policy, rebuild a derived active relation
weight using currently supported routes and original AdaptiveEdge
updates. The historical weight and proof attempts remain separate.
This is a reversible recomputation of a derived view, not a new
unlearning law, not an overwrite of historical observations. The
original additive AdaptiveEdge law does not implement negative
reinforcement. Compare phase trajectories from matched active state,
with gain=0 as causal ablation. The old Collatz tag is retained rather
than inverted by a correction. No conversion of a proof status into
a real observation, no semantic mass change.

## Validation

Exhaustive 128 states in the two selected primary masks and six
alternative-support flags, with 7 revisions each (896 transitions).
A separate oracle uses direct Boolean expressions. Three controls:
alternative Q support survives, alternative V support survives,
and complete loss of all three conclusions. Compare actual original
PNV outputs, Hotel lineage, original AdaptiveEdge and phase kernels.

The PNAML replay of selected corrections is tested separately using
the existing journal, not a new persistent engine. PNLF/PAUX cross-repo
v0.9 remains unmerged pending Actions access. No live NOEMA validation.
