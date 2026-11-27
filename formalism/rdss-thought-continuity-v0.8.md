# Thought dynamics: selected occurrence continuity — v0.8

Author research direction: Adrian Lipa, Pip Project.
Status: OFFLINE PNAML CONTINUITY CONFORMANCE CANDIDATE.
Base b4c76d2. Extends [v0.7](rdss-thought-return-feedback-v0.7.md).
Reuse the existing Mobile and Semantic Adapter snapshots, CausalHotel,
original PNV/1, and vendor/pnaml_continuity MemoryStore. No new runtime,
database, persistent index, transport or admission policy.

## Selected event and identity

A source-owned v0.7 return observation can be selected as an explicit
occurrence object reference. In the test fixture only, the source owner
selects both return observations (including a failed evidence result).
Use a stable event identifier, not a phase sample or arbitrary tick.
The Coupler consumes an explicit pip_half_time at a separately supplied
software frame. The frame sequence, Collatz index, event reference and
Hotel index remain distinct. Only the unchanged native Hotel successor
assigns the causal index. Unselected frames create no new rooms.

## Continuity fixture

Use existing MemoryStore.remember/get_event/verify, including existing
shards, transaction and duplicate semantics. Record selected events,
their explicit object reference, source frame, evidence and Collatz tag.
The journal retains immutable event records; no raw AUX phase vector,
dynamic AUX hash or continuous sampling. For this synthetic two-cluster
model only, persist selected scalar model checkpoint components (two
cluster phases, orbital coordinates and time) as typed relation targets
using exact float.hex text at the journal storage boundary. This is a
test-only storage representation, not a PNAML wire codec or a general
36D checkpoint. The existing journal's JSON storage is not native
internal transport. No operational AUX files are opened.

Close the SQLite connection, discard the Coupler and create a fresh one.
Use the existing verified journal head and previous-CID chain to select
the fixture events in chronological order. Replay their explicit
occurrences through CausalHotel.advance, reconstructing the original
native nodes with exact integer index/sign/parent. Unrelated journal
events do not generate rooms. Replaying the same immutable event to
MemoryStore is idempotent; do not call Hotel.advance twice for a duplicate.
Rebuild the model AdaptiveEdge and Collatz state using the original
operators and selected verified inputs; reconstruct the final selected
synthetic orbit and two-cluster phase checkpoint. Compare one further
source phase/orbit step against the uninterrupted model from that
checkpoint. No claim of complete asynchronous scheduler resumption:
return angle accumulator, pending events and producer cursors are not
restored here. This is a closed/reopened database and new Coupler in one
test process, not a machine reboot or live cross-session attestation.

## Scope

Tests in both existing plugin variant CI jobs. No plugin release change.
This establishes a bounded offline replay contract if CI succeeds.
Operational atomicity across journal and live producer, a source-owned
native PNLF/PAUX checkpoint and existing Ternary Socket TX/RX are still
open. Follow [transport policy](../projects/pip-project/PNAML_TRANSPORT_POLICY.md).
Do not promote the test harness to a runtime adapter or replace PNCS/PNV.
Manuscript unchanged.
