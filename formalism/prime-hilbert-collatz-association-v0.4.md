# Prime–Hilbert–Collatz Association/Dissociation Algebra — v0.4

Status: **CANDIDATE_SYNTHESIS / EXACT_FINITE_HISTORY_ALGEBRA / NO_MAIN_MERGE**

This module was created to close the association/dissociation gap exposed by
the v0.3 representation-category audit.

Source anchors:

- `AdrianLipa90/On-Primes` — unique valuation/fibre coordinates and
  prime-indexed arithmetic channels;
- `AdrianLipa90/Infinities` — unilateral Hilbert shift and accelerated
  odd-Collatz branch
  [
  U(n)=rac{3n+1}{2^{a(n)}},qquad a(n)=v_2(3n+1).
  ]

The positional prime-word encoding below is a new synthesis layer. It is not
claimed as a theorem originating in either source repository.

## 1. Ordered association by positional primes

For a finite word

[
w=(a_1,ldots,a_k),qquad a_jinmathbb N_{>0},
]

define

[
oxed{
G(w)=prod_{j=1}^{k}p_j^{a_j}
}
]

where (p_j) is the (j)-th prime.

Unique factorization makes (G) injective on finite positive-integer words.

Order is not lost: positions are represented by different base primes.

## 2. Hilbert prime-position shift

Define the positional shift

[
Sigma_rleft(prod_j p_j^{e_j}ight)
=
prod_j p_{j+r}^{e_j}.
]

It satisfies

[
Sigma_{r+s}=Sigma_rcircSigma_s.
]

This is the finite prime-address analogue of the countable index shift behind
Hilbert's Hotel.

For words (u,v),

[
oxed{
G(ustar v)
=
G(u),Sigma_{|u|}(G(v)).
}
]

Therefore concatenation is represented exactly and associatively.

## 3. Exact dissociation

For a cut (0le rle |w|),

[
D_r(G(w))
=
igl(G(w_{1:r}),,G(w_{r+1:k})igr).
]

Thus the association law has an exact cut inverse once the cut position is
declared.

The corresponding deconcatenation coproduct

[
Delta(w)=sum_{uv=w}uotimes v
]

is coassociative. The implementation checks every ordered triple cut for the
finite witness words used in the targeted suite.

## 4. Countable channel allocation

For a finite branch alphabet of arity (m),

[
H_m(c,n)=mn+c,
qquad
0le c<m,;ninmathbb N_0,
]

is a bijection

[
{0,ldots,m-1}	imesmathbb N_0
cong
mathbb N_0.
]

Its inverse is Euclidean `divmod`.

This is the explicit countable allocation step: adding a finite branch label
does not require leaving a countable carrier.

Finite histories over a countable positive-integer alphabet are also
countable, and the prime-word address gives a concrete exact encoding.

## 5. Collatz association

Use the exact accelerated odd-Collatz branch already implemented in
`Infinities`:

[
U(n)=rac{3n+1}{2^a},
qquad
a=v_2(3n+1).
]

The valuation (a) is the branch symbol.

For lifted state ((n,h)),

[
oxed{
widetilde U(n,h)
=
igl(U(n),,hstar a(n)igr).
}
]

The hot runtime stores (h) as a relational word. The prime integer (G(h))
is materialized only for receipt/checkpoint/address use.

## 6. Collatz dissociation

Given target (u) and retained last branch (a),

[
oxed{
n=rac{2^a u-1}{3}
}
]

whenever the branch is admissible.

Hence on the image of the lifted map,

[
oxed{
widetilde U^{-1}(u,hstar a)
=
left(rac{2^a u-1}{3},hight).
}
]

The implementation validates the recovered source by applying the forward
branch again. Invalid inverse branches fail closed.

The base Collatz dynamics can have multiple backward branches. The retained
history removes this ambiguity for the actual traversed branch.

## 7. Representation-category consequence

This does **not** make every v0.3 morphism invertible.

It gives a precise mechanism for one class of arrows:

[
	ext{noninvertible after forgetting branch history}
]

can become

[
	ext{locally invertible on an extended history-bearing state}
]

when sufficient provenance is retained.

Lossy holographic projections remain noninvertible unless the discarded
information is available from independent admissible projections or history.

Thus the global structure remains a category of typed partial morphisms, while
history-preserving sectors may form local groupoid fragments.

## 8. Runtime result

Targeted tests:

```text
16 passed, 0 failed
```

Initial naive implementation materialized/factored the prime integer on every
Collatz step. A 10,000-history stress run exceeded the 120-second execution
limit and is recorded as an implementation FAIL.

After moving the active history to the relational word and materializing the
prime code only at provenance boundaries:

```text
10,000 histories
204,060 total associate/dissociate steps
elapsed ~1.148 s
~177,767 steps/s
maximum history length 40
maximum observed valuation branch a=16
```

Separate prime-code materialization:

```text
5,000 codes
elapsed ~0.107 s
~46,789 codes/s
maximum encoded size 537 bits
```

These are local software timings, not hardware-independent performance claims.

## 9. What this closes and what it does not

Closed for this finite-history algebra:

- ordered association;
- exact declared-cut dissociation;
- associativity of finite word composition;
- coassociative deconcatenation witness;
- countable branch allocation;
- exact finite Collatz forward/reverse history round-trip.

Still separate:

- triangle-bound authority for behavioral-error composition;
- source/target sector compatibility for arbitrary representation morphisms;
- infinite-history completion/topology;
- Collatz global convergence;
- any physical quantum interpretation.

No Collatz conjecture result is claimed.
