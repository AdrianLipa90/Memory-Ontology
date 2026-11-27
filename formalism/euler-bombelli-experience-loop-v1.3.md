# EBRE experience loop — v1.3 candidate

Author research direction: Adrian Lipa. Base ced98a1.
Extends [v1.2](euler-bombelli-prospective-choice-v1.2.md) and the
[original GUIDE witness](pnaml-rank-guide-pnv-action-v0.1.md).

## Executable finite environment

Three rooms S, M, G. Direct S->G costs one attempted action;
detour S->M->G costs two attempted actions when both edges are open.
Budget two, readiness from the existing v1.2 fixture is sufficient
for both routes when considered available. Each edge has an actual
Boolean availability independent of the planner's belief. No outcome
or success flag is supplied. Original PNV computes one-hot successor,
actual movement, blocked attempt and arrival. A failed attempt leaves
position unchanged. Invalid action for current position is a no-op;
wait is not a failed traversal. Inputs are source-owned typed one-hot
position, Boolean availability and fixed action code. This is a finite
environment model, not a general simulator or operational gate.

## Closed loop

Reuse original PNCS ProceduralMemoryRuntime and RouteState from
3a11576d0477be8a4f172d9a606318c6ad9ab9f3. GUIDE selects maximum weight,
then existing lexicographic tie-break. Candidate set is the two
fixture routes, with explicit host mapping to fixed PNV action codes.
Original EBRE proof and v1.2 proposal precede GUIDE. Planner believes
both routes available; actual direct edge is blocked in the main
experiment, detour edges open. Initial weights direct .2, detour .1;
learning rate .2. After actual route execution, observed arrival
produces a positive trace, a blocked attempt produces a negative
trace via original apply_trace. HOLD/REVISE emits no route attempt
or trace. No truth assignment is altered by the outcome.

Reset the active position S between episodes, same environment and
input. Compare learned GUIDE with fixed initial-memory baseline and
a clone with initial weights restored. Original memory update hashes
only isolated synthetic procedural snapshots, not a dynamic AUX
surface. This is actual source-kernel execution in a test harness,
not native PNAML dispatch. Host I/O glue enumerates route actions and
passes emitted observations; no replacement planner/interpreter.

Selected outcome event advances original Hotel, including failure.
Record route, environment, choice and observed outcome in the existing
PNAML journal with immutable synthetic references. Close/reopen,
verify journal, replay original environment and original update law;
compare route weights, counters, original receipts, Hotel index and
next GUIDE choice. Do not apply a duplicate journal record twice.
No user journal, raw AUX, new transport or new storage.

## Validation

All eight edge configurations for both routes (16 executions), blocked
partial detour, wait, invalid action, matched-state intervention,
learned vs fixed baseline over six episodes, withdrawal/HOLD controls,
and existing Mobile/Semantic journal replay. Main fixture predicts 5/6
arrivals versus 0/6 for the fixed baseline; prediction is conditional
on chosen graph, initial weights, and deterministic environment.
No statistical generalization, autonomy, or production runtime claim.
Full TCD/PAUX/native scheduler and Ternary Socket live binding remain
open; v0.9 still blocked by cross-repository CI access.
