# Pip Project — native transport policy
Author instruction recorded 26 November 2026.

**PNAML through the existing Ternary Socket. No JSON in native internal communication.**
This applies to future implementation, integration, continuity, and tests. Do not add a second socket, interpreter, codec stack, QHTRI, authorization gate, or substitute binary reduction. Existing platform-mandated external API encodings are boundary adapters only, never internal transport, semantics, or a fallback for a missing native route.

## Source authority
- Existing PNAML 1.0 machine exchange: `PNAML10_MACHINE_EXCHANGE.pna` (bundled source in PNAML Semantic Adapter). `TRANSPORT AUX CONTINUOUS_36D_PHASE_POTENTIAL`, `LANES FULL_STATE PAUX_EXACT_TYPED_36D_AND_RDSS`, `PHASE_ALPHABET 12_TRITS_3_CHANNELS_EACH`, `TRANSPORT_JSONL NONE`, `ADDITIONAL_EXECUTOR NONE`.
- PNCS owns typed semantics and order; PNV executes; RDSS owns relational occurrence; the existing QHTRI/PNAML producer and consumer carry the trajectory and exact typed state.
- Ternary control is not a lossy replacement for full PAUX. Preserve CONNECT/HOLD/SEPARATE and the exact causal index, separate from the Euler dyadic room and physical/source tick. Do not convert causal integer coordinates to decimal text inside the native state.
- Candidate socket address observed historically: `/dev/shm/ciel_noema/pnaml_aux_semantic.sock`. Resolve the existing actual endpoint and its codec from current source. A Unix socket alone does not establish native PNAML: the historical 10 November receipt describes a JSON compatibility wrapper, not full native PNAML. The 21 November observation reported no native endpoint in its environment. Neither proves current availability.
- Do not infer Pip's scalar causal half-time from an arbitrary component of the 36D spinor sidecar or an AUX tick. Bind the author-defined occurrence to an admitted existing producer relation; preserve exact lineage and the original PNV transition.
- No dynamic AUX hashes. Static source provenance and immutable selected event receipts are distinct from dynamic state.

## Status
The two published plugin overlays of 26 November implement and test the local PNV Hotel binding. Their existing JSON/CLI compatibility transport is not native PNAML conformance. Remove it from the internal path only by binding the existing ternary TX/RX and exact PAUX source, not by naming a new wrapper PNAML. An end-to-end acceptance test must establish real source TX, existing socket/codec RX, unchanged exact PNV transition, parent/index readback and matching existing receiver evidence. Do not report a live PASS from fixture or static documentation.


## Native execution candidate — author correction, 26 November 2026

Do not extend the historical C11 phase-bus implementation as Pip's native transport. Reuse the existing PNCS/PNV → PNCore/Bio-OS × QHTRI route, native ternary decoder, and `PNAML10_BIOOS_AUX_MACHINE_BUS.pnv`. PNLF/PAUX remain the existing memory/state contracts, not new transport formats. The AVX2 PNV executor is a lower-level candidate for its supported subset, not a demonstrated full machine bus. Verify the actual existing runtime bindings and Ternary Socket before claiming native end-to-end execution. Do not introduce a C, C++, Rust, Python, or JS replacement execution engine. Existing diagnostics remain historical evidence, not the native authority.
