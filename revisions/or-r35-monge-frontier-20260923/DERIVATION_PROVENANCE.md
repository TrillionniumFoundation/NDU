# R35 derivation and version provenance

## Immutable inputs

- Repository: TrillionniumFoundation/NDU.
- Independent report: `a017f474619e86be533547acac87a3c8354f64cf`, file `reviews/operation_research_referee_report_r30_independent_2026-09-23.md`, blob `2ea2deaa03f063e23665c7f6a9b1a12dd13573e7`.
- Report's reviewed scientific commit: `fdc1ed47d46dc9d3344b8bce47c1670f11dcd475` (R30).
- Latest validated scientific baseline used: `fbfdf24b370201c810425f633f5fc06048282b5c` (R34), tree `c4453b7695bbcbd5ff70d5d7b90edd57905a6ac5`.
- Baseline workflow: 35871676942; artifact 10754943107, `ndu-or-r34-reader-build`. Its reader/source package was the local build input. The remote revision inherits the entire baseline Git tree, not only this artifact.
- Destination branch: `revision/ndu-operations-research-r35-monge-frontier-20260923`.

The latest located independent review evaluates R30, not R34. Subsequent revisions are not represented as independently accepted or already reviewed. The source commit actually used to compile this revision is recorded by the build; it is not inferred from a branch name.

## Mathematical dependencies

The R31 modules supply the laminar equivalence, quotient, quadratic tightness, rational coefficient construction, deterministic output-transducer interpretation, separate memory accounting, heterogeneous deterministic frontier, radial comparative static, and shared-table supporting cut. The R32 companion adds the flow/supply-price and accounting/encoding concordance. R33 adds piecewise-quadratic closure including marginal jumps, the shared-circuit alternative, whole-path KKT reference, and fixed-codebook lotteries. R34 proves cap anchoring, one remaining continuous highest level, a global randomized dynamic program, the off-cap example, and all-budget pathwise equivalence.

R35 takes the proved R34 continuous codebook reduction as its starting point. It proves Monge inequalities for interpolation edges and deterministic cells, then proves monotone differences between terminal-anchor objectives. Ordered intervals turn that difference into a Monge inequality after minimization. The triangular-domain exchange and leftmost-tie rule justify divide-and-conquer search. Prefix moments retain constant-work exact cost evaluation. Winning-only backtracking gives the stated output-inclusive work/storage bound. Thus the new algorithm changes how the same global problem is evaluated, not which controller class is feasible.

## Classical algorithmic attribution

- F. Frances Yao (1980), Efficient dynamic programming using quadrangle inequalities. Proceedings of the Twelfth Annual ACM Symposium on Theory of Computing, 429–435. DOI: 10.1145/800141.804691.
- A. Aggarwal, M. M. Klawe, S. Moran, P. Shor, and R. Wilber (1987), Geometric applications of a matrix-searching algorithm. Algorithmica 2:195–208. DOI: 10.1007/BF01840359.

Primary publisher records checked September 23, 2026: https://dl.acm.org/doi/10.1145/800141.804691 and https://link.springer.com/article/10.1007/BF01840359 . Generic Monge/matrix-search principles are not claimed as new. The theorem supplies the cost-specific hypotheses and a self-contained divide-and-conquer proof; no unimplemented SMAWK bound is claimed.

## Evidence dependencies and limits

`monge_frontier.py` reuses R34's exact primitive interface and moment evaluator. This is intentional same-input equivalence, not independent economic modeling. The new verifier uses direct branchwise sums and three-point quadratic recovery for independent terminal-cell checks, and invokes the unchanged R34 exhaustive enumerator. That enumerator shares the proved anchor reduction, but not the production dynamic program or moment evaluator. Neither exhaustive anchored comparison nor a finite nonanchor grid replaces the continuum proof.

`benchmark.py` counts and times the unmodified R34 randomized solver on the same first five scale inputs. Its counting wrapper changes counters only. The 512- and 1,024-branch baseline statuses are NOT_RUN. Timings are run-specific; the exact work counts and value equalities are the reproducible structural comparison. The accelerated deterministic solver is timed separately and compared with its original solver in the 98-case suite. No empirical service calibration or external specialized-solver run is asserted.

`reproduce_inherited.py` executes unchanged R33 and R34 tests in separate temporary directories. `PRESERVATION_MANIFEST.json` records the inherited file hashes and archived root wrappers. The workflow separately checks that no base file is deleted or changed outside the authorized root reader/build paths and the new revision namespace.

## Presentation source

Operations Research submission guidelines, checked September 23, 2026: https://pubsonline.informs.org/page/opre/submission-guidelines . The manuscript uses the lengthy-paper category and preserves 11-point type, 1.5 spacing, one-inch margins, anonymous title page, text-only abstract of at most 200 words, equation-free introduction, author–year references, and collected tables. Final page and layout counts are generated, not promised. No author-only submission declarations are supplied.
