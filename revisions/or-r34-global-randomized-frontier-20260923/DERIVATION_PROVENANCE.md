# R34 derivation and version provenance

## Immutable inputs

- Scientific base: `38b3f264e371758054d94a9f94088ae17a816241`, branch `revision/ndu-operations-research-r33-piecewise-randomized-20260923`.
- Latest independent referee report: `a017f474619e86be533547acac87a3c8354f64cf`; reviewed scientific R30 commit `fdc1ed47d46dc9d3344b8bce47c1670f11dcd475`.
- Report path: `reviews/operation_research_referee_report_r30_independent_2026-09-23.md`, blob `2ea2deaa03f063e23665c7f6a9b1a12dd13573e7`.
- Earlier same-day nominal R30 review: `7fc9b09c87723c060173dc22ab795a8a40e73ed3`. The independent report expressly corrects its stale-state interpretation; it is not treated as the latest substantive analysis.
- R33 successful source/reader workflow: run `35860094458`, artifact `10749816784`. The reader artifact supplied the local source snapshot; its files were checked against the inherited tree and preservation hashes.

## Dependency map: inherited versus new

The classical laminar mapping, normalized occurrence quotient, quadratic event bounds, coefficient-event rational complexity, and shared-table comparator are inherited. R31 provides the explicit-table tightness family and transducer-based accounting. R32 sharpens priority/complexity exposition. R33 provides piecewise-quadratic closure, the shared persistent circuit, nonsmooth conjugate certificates, the fixed-codebook adjacent-lottery theorem, and the uniform three-branch separation.

The new chain is:

1. R33 Theorem `thm:r33-lotteries` reduces a fixed codebook to an adjacent chord and deterministic intermediate mean.
2. Quadratic interpolation identity `eq:r34-chord` makes each nonhighest codeword's objective affine within a cap-order cell.
3. New Lemma `lem:r34-anchor` moves those levels to caps or deletes collisions, leaving at most one continuous highest level.
4. New Theorem `thm:r34-global` combines a standard ordered-prefix recurrence with an exact contractual tail minimization. It includes global optimality, constructive backtracking, arithmetic/storage accounting, and rational bit complexity.
5. New Proposition `prop:r34-offcap` exhibits a strict failure of cap-only codebook search: `5/8` is optimal between caps `1/2` and `3/4`.
6. New Theorem `thm:r34-pathwise` uses root saturation and increasing branch payoff to identify the entire pathwise randomized frontier with the deterministic frontier. It is not obtained by transferring an expected-feasibility certificate.

The new global result assumes quadratic terminal reward and quadratic intermediate costs as stated. The inherited piecewise-quadratic response theorem remains broader in a different direction. The companion's general-convex-intermediate-cost observation is an oracle reduction only, with no unsupported rational complexity assertion.

## Validation and limits

`verify.py` uses exact fractions and separate branchwise/exhaustive logic. It compares all reduced candidates, additional nonanchor grids, and controller replay; it does not replace the structural proof. `reproduce_inherited.py` executes unchanged R33 scripts in a temporary directory and saves the rerun separately. `PRESERVATION_MANIFEST.json` binds 35 inherited reader modules, scripts, and evidence files, and four archived wrappers. No parent branch is updated.

`BUILD_VALIDATION.json` records the scientific source commit, content hashes, generated reader hashes, page counts, log checks, and actual exact-test summaries. The publication commit can be a child of that scientific commit. A local record marked `local-uncommitted` is not a remote source assertion.

## External source checks

Checked September 23, 2026:

- INFORMS Operations Research submission guidelines: `https://pubsonline.informs.org/page/opre/submission-guidelines`. The Lengthy Manuscript category generally permits 40 pages excluding references; the build conservatively checks at most 40 total pages. General source format is 11-point, 1.5-spaced, one-inch margins.
- Klimm and Warode, DOI `10.1287/moor.2021.1151`; parametric piecewise-quadratic flow is an inherited comparator, not software run by this revision.
- Zhang, DOI `10.1287/opre.1120.1056`; finite policy graphs for dynamic contracts are retained as prior work, not treated as a new concept.

These checks support source attribution and formatting. They do not establish exhaustive novelty, practical dominance over specialized solvers, service calibration, or editorial acceptance.
