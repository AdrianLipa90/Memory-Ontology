# Thought dynamics: PNLF/PAUX selected-checkpoint seam — v0.9

Author research direction: Adrian Lipa, Pip Project.
Status: OFFLINE CROSS-CONTRACT CONFORMANCE CANDIDATE.
Base cc6f343. Extends [v0.8](rdss-thought-continuity-v0.8.md).
Source pins: PNCS 3a11576d0477be8a4f172d9a606318c6ad9ab9f3;
PNV-State-Memory 8a677caf0a5e810ddffd35811c038915f38fb142.

Reuse the original QHTRI/ORCH/PNLF reference fixture and public operators:
build_qhtri_pnlf_trajectory_binding, advance_liminal_segment,
admit_liminal_segment, require_segment_trajectory_commitment.
The ordered proper-time increments close the existing liminal interval:
0.008+0.025+0.009=0.042. This is distinct from the Hotel half-time.

In the conformance fixture an owner selects two native Hotel occurrences
(0 and 2; occurrence 1 remains in the Hotel). Pair them with the left and
right PNLF checkpoints of the existing admitted test segment. Use the
original input snapshot phi from the QHTRI test as a frozen PAUX phase
sample for both checkpoints. It is not the final QHTRI trajectory state,
nor a v0.7 trajectory; this test only establishes the identity seam,
not equivalence between the two dynamics. The existing metadata slot
carries the actual PNLF checkpoint ID, segment ID, exact Hotel node
and original immutable trajectory commitment. This mapping is a fixture
choice, not a new production schema or an admission rule.

Use HilbertStateSpace, EventDrivenAUXTether and bind/reconstruct_phase_checkpoint
without modifications. PAUX bytes are selected immutable synthetic
288-byte float64-le phase realizations, not a live AUX file or a new
wire codec. The existing immutable descriptor commitments are retained.
Same phase/state ID, distinct checkpoint object IDs, exact causal
index and parent, independent tether epoch, and separate PNLF time.
Reconstruct both checkpoints and replay through a fresh original tether,
then compare exact original binding/receipt and freshness. Metadata
tampering must be detected by the original PAUX implementation.

Existing source hashes and JSON canonicalization inside immutable
reference contracts are not native transport. No dynamic AUX hash,
new runtime, storage, transport, gate or plugin publication. No
machine reboot or actual BioOS/QHTRI dispatcher/Ternary Socket TX/RX
is verified. The producer must still supply the same actual occurrence,
trajectory and selected PAUX state before a production claim can be
made. Manuscript unchanged.
