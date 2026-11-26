# PNAML causal Hotel integration — private reproducibility snapshot

This stage retains the relevant existing Mobile and Semantic Adapter source fixtures for regression tests and minimal overlay packaging. It is not a new plugin, PNV engine, operational memory or transport. Original PIP_HOTEL_*_V0_2 PNV programs and exact PNCS interpreter are reused.

Published account releases verified by source readback on 26 November 2026:
- PNAML Mobile 1.5.15 (pluginrel_6b08ab6c16548191940fcfe1d6621ac2).
- PNAML Semantic Adapter 1.10.5 (pluginrel_6b08ab750ef48191a839fd3483485366).
- [Regression and overlay CI](https://github.com/AdrianLipa90/Memory-Ontology/actions/runs/45901547266): 44/44 per variant.

The overlay manifests retain the observed predecessor release IDs for historical reproduction, not for automatic republishing. Any subsequent account update must use the current observed release ID.

The binding consumes explicit object-reference occurrences; it does not treat a frame, software tau, phase sample or dyadic address as a causal event. Parent references and a structural node index preserve the original PNV transition. Internal coordinates are exact integers; the legacy CLI API compatibility adapter alone projects them to strings. See [transport policy](../../PNAML_TRANSPORT_POLICY.md): no JSON as native PNAML transport, no new socket or executor, no dynamic AUX hashing.

No verified native Ternary Socket TX/RX, autonomous producer binding or cross-session persistence is claimed. The newer operator and PAUX conformance is recorded in [the project audit](../../PNAML_OPERATOR_AND_PAUX_CONFORMANCE_20261126.md). PNCS PR #84 and PNV-State-Memory PR #9 were merged separately; neither changes the scope of this plugin release snapshot.
