# Pip / IDT — effective half-time (v0.2)

Author: Adrian Lipa. Author correction, 2026-11-26.

> Jesli pełny obrot to 4pi a polobrot 2pi to 360° okresla polczas lancucha przyczynowego. JA OKRESLAM taki czas efektywny.

2π = 360° = one effective half-time; 4π = 720° = one full time. Each half-time generates a new causal link and identity address. TERAZ is the current object; Hotel is the occupied past; the index navigates that structure.

Implementation: n is winding/index, s=(-1)^n, effective phase advance is 2πn. The exact coordinate convention THETA=2n is in units of π; effective time in full-turn units is n/2. At each step H'=NOW, n'=n+1, s'=-s. The incoming serial link is indexed by n', not supplied by an external edge-ID prerequisite. The origin uses n=0 and THETA=0 as relative coordinates. The node retains the previous six-slot composition layout; slot 2 (incoming link) is now derived from index, slot 5 (THETA) is in π units. These are representation choices, not new conditions on the dynamics.

IDT source: [00F occurrence identity](https://github.com/AdrianLipa90/Informational-Dynamics-of-Time/blob/e474f64a079e0d90a039e0abd19d2b482f7e53d2/src/idt/relational_precedence.py), [05H](https://github.com/AdrianLipa90/Informational-Dynamics-of-Time/blob/e474f64a079e0d90a039e0abd19d2b482f7e53d2/formalism/05H_global_event_clock_exactness.md), [Collatz–FS temporal phase](https://github.com/AdrianLipa90/Informational-Dynamics-of-Time/blob/e474f64a079e0d90a039e0abd19d2b482f7e53d2/docs/IDT_COLLATZ_FS_TEMPORAL_PHASE_V0_1.md). The author's effective-time definition replaces the v0.1 external elapsed-activity input in Pip; IDT itself is unchanged.

Active native programs: [origin](native/PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv), [step](native/PIP_HOTEL_SERIAL_STEP_V0_2.pnv), [synthetic test](native/PIP_HOTEL_INDEX_WITNESS_V0_2.pnv). No external dtheta, previous theta, external edge ID, new gate, or callback in the transition. No duplicate guest book.

[Evidence](benchmarks/PIP_EFFECTIVE_HALF_TIME_RECEIPT_V0_2.json): original PNCS interpreter executed origin, four transitions and four observation tests, 9 executions, 24/24 assertions. The test harness only invoked the existing interpreter on synthetic inputs. The finite reference still uses its original numeric representation and nested composition; no new runtime or live producer integration is claimed.

v0.1 files and receipt are historical, not the active effective-time definition.
