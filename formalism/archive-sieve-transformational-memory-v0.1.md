# Archive sieving and transformational memory — V32 source contract v0.1

Author source: Adrian Lipa, The Reality of the Imaginary, V32, printed pp.260–270. Research branch from consolidated main 347e1e839f5fb1c7170158f417c4f9fe9ab8127a. No native NOEMA mutation.

## Distinct archive and learned state

V32 p.261 writes (X,M) -> (X,P(M)) for pure archive sieving, with X including learned geometry and M the detailed archive. Memory Ontology uses M more broadly as history-bearing causal structure. Explicit crosswalk: Z=(x,L,A), where x is active state, L is learned structure and A is the detailed archive. The pure sieve is (x,L,A)->(x,L,P(A)), with identity, lineage and dependencies preserved at the instant of projection. This notation is a proposed clarification, not replacement of either source definition.

For an admitted query family Q, horizon H, input protocol u and observable O, preservation requires equal (or explicitly tolerance-bounded) future O trajectories for the full and reduced representations. The retained summary must preserve any archive dependencies used by the update/observation laws. A sufficient stronger condition is a projection pi such that pi F_e = Fbar_e pi for every admitted future event e, and O = Obar pi. This is a conditional commuting-diagram criterion, not a universal compression claim. Counterexamples include identity queries whose source record was dropped, unresolved promises, provenance-dependent correction and changing query families.

## Exact source example and native PNV execution

V32 p.263: w0=1/5, w'=w+(1-w)/4. Residual r=1-w gives r'=3r/4. Represent r=N/D, with N0=4,D0=5. Each step N'=3N,D'=4D. The exact values are w3=212/320=0.6625 and w4=956/1280=0.746875. Reset and one further event give 8/20=0.4. These are source choices, not new fitted weights.

The program [ARCHIVE_SIEVE_V0_1.pnv](../native/ARCHIVE_SIEVE_V0_1.pnv) uses existing SOURCE, DIFFERENCE, COMPOSITION, IDENTITY and RETURN to calculate the recurrence with exactly representable small integer operands, not external transform callbacks. It emits a full representation and its checkpoint projection, then two continuation arithmetic branches consuming the same retained operands. A second interpreter execution with an empty synthetic archive gives the same continuation. This deliberately demonstrates absence of archive dependency for the declared scalar rule. It does not deserialize a checkpoint or run separate persistent replicas; no actual archive mutation or native NOEMA state evolution. 76 ops, 12 assertions passed, two deliberately incorrect initial residual inputs rejected, repeat equal. See [compact recorded receipt](../benchmarks/archive_sieve_pnv_receipt.json). The pinned interpreter performs numeric DIFFERENCE in binary64; these finite small integer computations are exact, not a claim of arbitrary precision.

## Order, entropy and recoverability

V32 p.265 supplies A(w)=w+1, B(w)=2w. Starting from zero, B(A(0))=2, A(B(0))=1, A(A(0))=2. PNV computes these values: the retained effect distinguishes some orders but cannot identify its unique history. A numerical endpoint is not necessarily holonomy in a specified connection. V32 p.262: counts (12,20) -> (13,21) after one positive observation; PNV calculates both updates. Those counts are sufficient for that proportion only, not guest identity. V32 pp.268–269: four equiprobable guest alternatives give two bits of uncertainty when their identity is not retained, while the count can remain known. The entropy example is analytic, not evaluated by the PNV program.

## PNAML/PNLF consolidation

V32 pp.269–270: live AUX read-only to clients; immediate selected significant episode shards with occurrence/context/source; daily journals, aggregate statistics and periodic checkpoints. A pure archive projection does not overwrite or hash live AUX. Preserve actual source and transformed lineage, commitments, corrections, and applicable erasure handling. Retained learned state can still change under future experience. The candidate projection is not a new persistence policy and does not authorize real deletion. PNLF state and liminal segments must retain the fields required by the chosen observation/update contracts.

Next native test: compare full/reduced independent checkpoint restores, matched input/goal, typed actual route outcomes and an intentionally reset structure; vary queries and verify unavailable details are not reconstructed as observations. Use an actual existing admitted PNCS/PNV runtime and producer, not a new Python or JS engine. No merge into main or canonical promotion in this pass.
