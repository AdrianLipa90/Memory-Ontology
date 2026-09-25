# GREMLIN v0.4 — retained-history Collatz subgroupoid audit

Status: **LIVE_INTERNAL_AUDIT / CANDIDATE_ONLY**

Input branch:

`feat/prime-hilbert-collatz-association-v0.4-20260925`

## Live receipts

- task: `gremlin:whisper:sha256:f753497102309273b08ab7eb6c927e34699f8d34397c1e2c62776328cfc55df1`
- ingest: `gremlin:whisper:sha256:c9292819ce42a4101d7a07397fe38fb47c58060bec5357cbb1eb6867ea913404`
- PhaseNav36D state: `gremlin:whisper:sha256:e3d31a83e72632b231f399802288983f655a4484eef534ab7e7df2c7590eaba5`
- fused: `gremlin:whisper:sha256:5205624b7b6d30acfc951f16b5f9ffa2b08b8306c3e6d62a5008b6b95df21eb9`
- internal audit: `gremlin:whisper:sha256:4334c5a436549b72bcad88e378abfa96a209501df0ec281356ecc1df626dcc37`

GREMLIN route species:

```text
OWL
RAVEN
```

Phase-attention terms:

```text
equal-valuation
false-cancel
composable
noninverse
```

This targets the critical HOUND/RAVEN boundary: two Collatz edges may share the
same valuation (a=v_2(3n+1)), so equality of branch labels is insufficient
for inverse cancellation.

The runtime implementation therefore cancels only after all of the following
are true:

1. orientations are opposite;
2. valuations match;
3. the second traversal starts at the exact target of the first;
4. the second traversal returns to the exact source of the first;
5. inverse branches are revalidated through the forward Collatz branch.

The randomized gate includes 100 explicit equal-valuation/noninverse
witnesses with zero false cancellations.

## Classification

Current bounded classification:

[
oxed{
	ext{valid finite retained-history Collatz paths}
;leadsto;
	ext{path groupoid}
}
]

This is a subgroupoid candidate inside the invertible core of the broader
partial representation category after restricting objects/sectors to the
valid domains and images of the path maps.

It is **not** currently classified as an action groupoid because no single
global group action on all odd states has been established.

It is **not** claimed to be the maximal/core subgroupoid of the whole
representation category, because other exact invertible representation arrows
may exist independently.

Lossy holographic projections remain outside this reversible fragment.
