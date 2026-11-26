# Native PNAML/PNV integration audit — 2026-11-26

Scope: actual isolated native rebuilds and source readback; no production runtime mutation. Author instruction: use existing PNCS/PNV and Ternary Socket, no C replacement, no JSON internal transport, no new executor, no dynamic AUX hashes.

## Reproduced source components

| Source | Current executed result | Exact scope |
|---|---|---|
| Library `PhaseNav_PNV_Exec_AVX2_From_Zero_V1.zip` (23 November) | 24/24 original shell tests | One fixed A0 to Hilbert graph |
| `NOEMA_Groszek_V06_Supplement_and_Source.zip!code/PNCS_PNV36_TER12_Native_Codec_Research_v0_1.zip` (24 November) | 32/32 original executor tests; 23/23 original codec tests | Fixed graph plus 320-byte phase36/TER12 snapshot |
| Library `PNCORE_TERNARY_RESIDUE_DECODER_X86_64.S` from `/NOEMA/00_CONTROL/BOOT/PNCS_NATIVE_CANDIDATES/PNCS_EXECUTOR_PHASENAV_V0_1_CANDIDATE/` | 1481/1481 original isolated conformance checks | 36 binary64 bounded residues + 36 signed int64 winding -> 12 signed trits; rebuilt ELF matches archived static SHA-256 013dec5bb746298a968a7212d5e51bf93bc9db05f58f7fda37d9efcba63f7245 |

The original JS conformance fixture runner was used only to test the freestanding assembly ELF, not as a transport, repository, or execution engine. No new runtime or source language added. The two AVX2 suites overlap; do not interpret the counts as independent proof of complete runtime operation.

## Active Pip programs on both assembly executor builds

Exact Git blobs (verified via local git hash-object), original source from Memory-Ontology:

- `PIP_HOTEL_SERIAL_ORIGIN_V0_2.pnv`: 98033e5e398b4c02c28db2467fbb5d510f2672ed
- `PIP_HOTEL_SERIAL_STEP_V0_2.pnv`: c880f45449cd38225779be1660e89f2c02f07f8d
- `PIP_HOTEL_INDEX_WITNESS_V0_2.pnv`: 60aa2f8e92605f9c28b7186e0f661758b00b0787

All three returned exit 23 with `BLOCKED: invalid PNV/input/registry; no execution or side effects` on both builds. Parser source only recognizes SOURCE, TRANSFORM, ORDER, COMPOSITION in its fixed source/map registry; it lacks general IDENTITY and DIFFERENCE and the witness uses READ_ONLY. These are existing backend capability limitations, not new guards, nor reasons to rewrite the original Pip programs.

The existing full PNCS reference executor at AdrianLipa90/PhaseNav-Natural-Coding-System commit 22a26cd409311da7c0997874b0f9a7050047b287 already supports these exact operations. The earlier plugin CI run 45901547266 passed 44/44 per variant with exact in-process integer coordinates. Its canonical receipt implementation still uses a finite JSON value domain; that is distinct from transport and not evidence of native PNAML end-to-end execution.

## Critical separation of control and lineage

Actual independent decoder invocation on fixed phase residues (0,0.01,2;2,0,0.01;0,2,0.01) repeated four times, each of these uniform input winding values:

0; 1; 2; 9007199254740993; 9223372036854775807; -9223372036854775808.

All six return the same signed 12 bytes: (1,0,-1) repeated four times. Expected because this decoder computes residue cosine votes, not winding lineage. It cannot distinguish successive causal half-times from ternary projection alone. Preserve the exact winding/occurrence lane. The 320-byte PNV36T12 snapshot preserves phase bytes and trits, but does not encode exact winding, amplitudes, full RDSS state or event history. Do not treat either component as a complete PNAML machine bus or derive the scalar Pip causal index from a chosen 36D axis.

## Route and open work

- Existing `PNAML10_MACHINE_EXCHANGE.pna` declares full exact typed PAUX state alongside phase signal, not JSONL.
- Existing `PNAML10_BIOOS_AUX_MACHINE_BUS.pnv` is the source contract; its operational registry binding to the actual Pip occurrence is not established by these tests.
- Existing historical `PNAML_AUX_Semantic_Socket_V02.zip` and `NOEMA_EGO_BinaryTernary_LocalV1.zip` have AF_UNIX binary framing with JSON payload; not the requested native Ternary Socket.
- `/dev/shm` was empty in this test environment. Actual endpoint/codec source and native TX/RX remain unverified.
- Retain unchanged PNCS/PNV programs, exact integer index and PAUX lineage. Do not choose an arbitrary winding axis, truncate to int64, substitute JSON or introduce a new runtime. No autonomous causal half-time or durable restart claimed.

No plugin release changed by this audit. No active host or default-runtime changes.
