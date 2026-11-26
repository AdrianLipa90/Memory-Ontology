# Pip / IDT — Hotel as occurrence structure (v0.1)

Research author: Adrian Lipa. Implementation witness: 2026-11-26. Source correction: [HOTEL_INDEX.md](HOTEL_INDEX.md).

## Source authority

IDT pinned at e474f64a079e0d90a039e0abd19d2b482f7e53d2:

- [00F relational precedence implementation](https://github.com/AdrianLipa90/Informational-Dynamics-of-Time/blob/e474f64a079e0d90a039e0abd19d2b482f7e53d2/src/idt/relational_precedence.py), blob 42d029820d6991b83552443e74ae1886457db2a0: occurrence = prefix, state, theta, terminal edge and weight; recurrent state is not recurrent occurrence; NOW is the maximal supported occurrence/frontier.
- [05H graph-clock exactness](https://github.com/AdrianLipa90/Informational-Dynamics-of-Time/blob/e474f64a079e0d90a039e0abd19d2b482f7e53d2/formalism/05H_global_event_clock_exactness.md), blob a785a218a78cc3d93c5e03266952f32232d09fcd: positive elapsed increments sum along a unique prefix; a merger requires path-independent elapsed integrals for a scalar clock.
- [Collatz–FS temporal phase](https://github.com/AdrianLipa90/Informational-Dynamics-of-Time/blob/e474f64a079e0d90a039e0abd19d2b482f7e53d2/docs/IDT_COLLATZ_FS_TEMPORAL_PHASE_V0_1.md), blob 7cae714e86787b56cd64443553d397cb75d4e737: 2pi projective / 4pi spinor closure, elapsed activity distinct from phase, Collatz phase doubling distinct from the Euler occurrence count.
- [02JO NOW crosswalk](https://github.com/AdrianLipa90/Informational-Dynamics-of-Time/blob/e474f64a079e0d90a039e0abd19d2b482f7e53d2/formalism/02JO_temporal_density_material_front_now_crosswalk.md), blob 07ba0529876e7e7ecf95f3c424cf12232238c252: the logical realized frontier is not selected by continuum density alone.

## Serial specialization

Use one node N=(parent,incoming_edge,n,s,Theta,x). The parent chain is the Hotel (occupied past); no separately appended guest book. The current object x is TERAZ at its current occurrence address, not its phase representative. H_n=parent(N_n); H_(n+1)=N_n. The new N is a composition of H_(n+1), the realized incoming edge identity, n+1, -s, Theta+dTheta and the next object. Its serial index is n+1, derived from the node's coordinate, not a second store. A reference to a prior node is the relation to its occupied room. Origin has empty parent, no incoming edge, n=0, s=1, Theta=0. This zero is a relative elapsed-activity origin, not the primitive singularity zeta_0=|i|^-2/2.

At the selected Euler returns, exp(i(pi+2pi*n))=-1 and exp(i(pi+2pi*n)/2)=s*i, s=(-1)^n. The program steps between these selected returns; it does not claim that every IDT transition is a 2pi return. The correspondence between general IDT events and selected Euler returns must come from the original producer. Elapsed activity comes from the supplied realized IDT edge, not n*2pi. No duration calibration is fabricated.

[Origin](native/PIP_HOTEL_SERIAL_ORIGIN_V0_1.pnv), [step](native/PIP_HOTEL_SERIAL_STEP_V0_1.pnv), [independent observation witness](native/PIP_HOTEL_INDEX_WITNESS_V0_1.pnv). Original A0_TO_HILBERT_NATIVE.pnv remains byte-identical as the historical V15 source. The new step is not a call to the old RDSS_HILBERT_GUEST_REGISTER operator.

The reference PNV executor has no field projection, persistent pointer store, unbounded exact integer arithmetic or native IDT producer binding in the admitted vocabulary used here. Caller supplies coherent projections of the same current node and realized edge. COMPOSITION represents a nested finite value; production persistent structure sharing, index lookup, branching/frontier and atomic native binding are still OPEN. In a branched IDT graph use occurrence prefix/edge identities (not depth alone); concurrent NOW need not be unique. Preserve separate elapsed activities and merger defects. No arbitrary guard or new runtime is added. Witness assertions belong only to the synthetic test program, not the transition.

## Evidence

[Recorded execution summary](benchmarks/PIP_HOTEL_IDT_RECEIPT_V0_1.json): original PNCS interpreter, blob c9041234cc66d5670e7b74f0c101434647067341. One origin + four serial steps + four independent PNV witness calls, 16/16 witness assertions; four deliberately inconsistent observation controls rejected by the test witness. Fixture object sequence A,B,A,C,A; input elapsed increments 1,2,4,1. No callback or native host access. The original interpreter's numeric DIFFERENCE uses finite floating-point arithmetic; results here are exact small integers, not evidence of unbounded exact arithmetic. Receipts hash only synthetic static fixture values. Full local receipt is 50903 bytes (SHA-256 3380ee594c9afc5149d0d21ed4516ebb39b889a20bdd7ba3e01dc0295f7ced54), not uploaded as a full repo object in this change.

No proof of physical time, no derivation of U(1) from the singularity, no live AUX or user journal write. The existing IDT and NOEMA source repositories are unmodified.
