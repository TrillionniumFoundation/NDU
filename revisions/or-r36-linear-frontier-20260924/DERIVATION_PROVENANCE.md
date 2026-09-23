# R36 derivation and evidence provenance

## Immutable identities

Repository: `TrillionniumFoundation/NDU`.

Independent review branch: `review/operation-research-r30-independent-harsh-20260923` at `a017f474619e86be533547acac87a3c8354f64cf`.

Review path: `reviews/operation_research_referee_report_r30_independent_2026-09-23.md`; blob `2ea2deaa03f063e23665c7f6a9b1a12dd13573e7`. The report reviewed R30 commit `fdc1ed47d46dc9d3344b8bce47c1670f11dcd475`, not R31–R36.

Baseline branch: `revision/ndu-operations-research-r35-monge-frontier-20260923` at reader commit `7e49851cd04f0f7e015c2561b43a4e7591574e67`; tree `d276ecc4810f94c0d2e9dcaa52394977e830bce8`. Its scientific source commit is `59ea34389e6329c56fd4d9a75e640cfebeecfa59`.

Baseline reader artifact: Actions run `35878626631`, artifact `10758823672` (`ndu-or-r35-reader-build`). The complete remote base tree, not only the downloaded reader subset, is inherited by the new branch.

New branch: `revision/ndu-operations-research-r36-linear-frontier-20260924`. The exact scientific source commit is recorded only after the source/evidence commit exists, in `BUILD_VALIDATION.json`. A local non-Git build reports content hashes and does not invent a commit identity.

## Proof dependencies

R31: classical laminar reduction; exact occurrence-to-vertex quotient; compact quadratic event bound and explicit-table lower-bound family; fixed-query finite transducer, classical behavioral minimization, price-order consequences; deterministic renewal frontier, radial comparative static, and shared-table support.

R32: explicit convex-cost flow representation and parameter distinction; reduced rational and aggregate-height accounting; expanded residual-priority audit.

R33: continuous piecewise-quadratic extension with marginal jumps; shared representation/query tradeoff; exact restricted-codebook lotteries and a strict randomization benefit; whole-parametric-path active-set comparator.

R34: cap anchoring except for a continuous highest randomized level; exact terminal interval and six moments; all-budget global randomized design; pathwise frontier equivalence; quadratic exact algorithm and independent reduced-candidate enumeration.

R35: Monge interpolation and deterministic-cell costs; Monge terminal costs after continuous minimization; feasible triangular monotone search; O(mk log(k+1)) implementation and exact same-input comparison.

R36: one-sided ordinal staircase completion that preserves total monotonicity in arbitrary submatrices; application and implementation of classical SMAWK; O(mk) exact work and O(mk+k) storage, including reconstruction; conservative O(mkS³) bit bound with inherited coefficient height. No assertion that SMAWK, generic Monge search, state minimization, or memoization is new.

## Primary-source and format check

The classical matrix-search reference is Aggarwal, Klawe, Moran, Shor, and Wilber (1987), *Geometric applications of a matrix-searching algorithm*, Algorithmica 2:195–208, DOI `10.1007/BF01840359`. The publisher's abstract distinguishes monotone matrices from matrices whose every submatrix is monotone; the complete reduction/interpolation invariants needed here are written in the companion. The bibliography retains this and all predecessor entries.

Operations Research submission guidelines were checked on September 24, 2026: `https://pubsonline.informs.org/page/opre/submission-guidelines`. The lengthy-manuscript layout is used. The source and validation records state actual page counts, not a claimed journal waiver. No journal upload, authorship declaration, conflict-of-interest attestation, or editorial decision was made.

## Evidence independence and limits

`linear_frontier.py` deliberately reuses the inherited exact economic interface and moment oracle. R34/R35 same-input equality therefore validates a changed search procedure, not three independent economic derivations. Separate direct-branch enumeration and three-point interval minimization avoid those production moments and DP. All-submatrix enumeration tests the ordinal interface itself. Nonanchor grids are falsification only. Analytical proofs, not finite tests, justify the continuum and asymptotic claims.

The scale study is synthetic and single-run. It records unfavorable small-instance constants and the deterministic count's lack of crossover through 2,048 branches. It is not a published-specialist benchmark. Both institutions use exactly the prior feasible set, root saturation, and observation convention.

## Preservation and exact source identity

`PRESERVATION_MANIFEST.json` covers inherited reader sources/evidence and byte-identical copies of the four original root wrappers. The workflow additionally checks every path in the entire immutable R35 base tree. Only those wrappers, the two current reader PDFs, new R36 labels, the new revision directory, and its isolated transport/workflow may change. Historical theorem modules, reports, evidence, and broader volumes are neither removed nor silently rewritten. Earlier review/revision branches and main are untouched.

`SOURCE_PAYLOAD_MANIFEST.json` records transported source hashes; `BUILD_VALIDATION.json` records the actual committed scientific source, reader hashes, reference/layout checks, new tests, inherited regression results, and whole-tree preservation. The workflow does not force-push.
