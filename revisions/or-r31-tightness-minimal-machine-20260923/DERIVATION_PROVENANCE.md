# R31 derivation provenance and preservation map

## Review baseline

R31 is created directly from `review/operation-research-r30-independent-harsh-20260923`. The answered report is `reviews/operation_research_referee_report_r30_independent_2026-09-23.md`, which reviewed scientific revision `revision/ndu-operations-research-r30-quotient-memory-20260923` at commit `fdc1ed47d46dc9d3344b8bce47c1670f11dcd475`.

The earlier same-day report `operation_research_referee_report_r30_quotient_memory_2026-09-23.md` performed a stale version audit and is not the scientific baseline for R31. It remains in repository history.

## Historical mathematics used rather than rederived from scratch

| Historical source | R31 use |
|---|---|
| R30 `quotient_theory.tex` | occurrence-to-vertex quotient, reflection recursion, global upper bounds, coefficient-event bit proof, compact certificate |
| R29 `price_main.tex` | predecessor finite-price construction and exact scalar-response logic |
| R30 `memory_theory.tex` | reached price sets, behavioral equivalence, heterogeneous renewal frontier, radial comparative static |
| R29 `memory_main.tex` | original (k)-branch necessary-memory family; now elevated to an explicit linear tightness corollary |
| R30/R29 shared-table files | graph-sized public comparator and fixed-release supporting-cut oracle |
| R30 computational package | exact laminar, QP, public-promise-grid, scale, coefficient, and audit evidence |
| retained R26--R29 theory volumes | switching, continuous states, sensitivity, deployment and governance results; preserved but not used to enlarge the R31 exact-closure domain |

## New R31 derivations

### Tight response-size theorem

For a deterministic (n)-vertex chain with (a_i=q_i=1), ([l_i,h_i]=[0,1]), (r_i=2i), unit transition/discount and redundant cap (B_i=n-i+1), direct backward substitution gives
[
R_i(eta)=sum_{j=i}^{n}[2j-eta]_{[0,1]}.
]
The local breakpoints (2j-1) and (2j) are pairwise distinct. Every breakpoint changes the slope of each ancestor response containing that local term, so no cancellation is possible. The family therefore has exactly (2n) global knots and (n^2+2n) stored affine segments. This closes the matching-order lower-bound gap without empirical assumptions.

### Minimal reached transducer

The R30 behavior recursion is factored into:
1. the reached deterministic output transducer ((v,eta));
2. classical output/successor behavioral minimization;
3. contract-specific consequences: finite reachability, price-order contiguity, alphabet reuse across observed public vertices, and the renewal lower bound.

The accounting is split into (K_*=max_v c_v), (C_*=sum_v c_v), and read-only response/precision storage.

### Exact query reuse

The compiled root response has at most (3N) indexed knots. Binary search plus one affine inversion gives the post-compilation root-query corollary. Policy emission and auditing remain separately charged.

## Preservation rule

R31 is an additive revision layer. It does not rewrite or delete the R30 theorem/evidence directory. Shared-comparator, tables, and electronic-companion modules copied into the R31 directory are intended to remain byte-identical to their R30 sources unless a subsequent R31-specific editorial cross-reference requires a documented change.

Root reader entry points (`main.tex`, `electronic_companion.tex`, `README.md`, submission checklist and generated PDFs/label files when rebuilt) may change to select the R31 package. The preceding R30 root sources remain reconstructible from branch history and from the preserved R30 directory.
