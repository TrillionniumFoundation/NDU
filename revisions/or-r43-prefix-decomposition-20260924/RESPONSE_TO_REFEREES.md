# Response to the R42 Operations Research Referee Report

Manuscript: Limited-Memory Renewal Contracts: Exact Quadratic Design and Prefix Decomposition.

Revision: R43, September 24, 2026.

Review baseline: `a0d1f4e3dfc3f7639f806cab01f1faae877d5361` on `review/operation-research-r42-independent-harsh-20260924`.

Report: `reviews/operation_research_referee_report_r42_independent_harsh_2026-09-24.md`.

New branch: `revision/ndu-operations-research-r43-prefix-decomposition-20260924`.

## Principal changes

This revision adds a structural decomposition rather than treating exhaustive continuous enumeration as the only algorithmic contribution. A single promise price converts the shared alphabet problem into an ordered path problem. Its eligibility-aware edge rewards incorporate nonsaturated branch targets, heterogeneous shortfall costs, and actual selected-level charges. The price oracle is polynomial with variable branch count and variable alphabet budget. It gives exact completion bounds for prefix search, a finite exact catalog algorithm, and independently checkable global intervals at interruption. No strong outer duality is assumed.

The new theorem is stated for an abstract ordered-interface allocation class with branch-specific eligibility thresholds. The renewal model is a specialization. A fixed-input lower bound proves that the uniform mesh rate is sharp, and a monotone-charge theorem identifies the boundary of the retained one-branch randomization example. We correct the face-count error, expand the computational study, provide a separately formulated original-policy nonlinear cross-check, and distinguish mathematical globality, numerical corroboration, and provenance.

All previous revision directories remain unchanged. The immediately preceding article, companion, README, and checklist are snapshotted byte for byte. The R42 joint-design parameter study and all its tables are retained in the electronic companion, with cross-references from the current main article. No old experiment is represented as a newly executed timing.

## 1. The incorrect face-enumeration bound

The referee is correct that a general lottery branch may require four inequalities, not three: the two chord bounds, the target cap, and the eligibility ceiling. A positive tolerance does not make either of the last two redundant. The current theorem now uses `M_s = s + 1 + 4k`, and the crude linear-system bound is `sum_s (2s-1)^k 2^(s+1+4k)`.

We also state the sharper rank-limited count, summing binomial coefficients through dimension `s+k-1`, instead of all subsets. The instrumented implementation records its actual number of inequalities and checks the corrected bound. The current article does not repeat the old exponent. Historical R42 sources and responses retain their original bytes, as they should in an audit trail; the new revision explicitly supersedes the erroneous count rather than rewriting the history of the report.

Location: Theorem “Exact joint continuous design” in the corrected R43 `joint_design.tex`; code `frontier.py`; raw `continuous_frontier.json`.

## 2. A genuine decomposition beyond generic face enumeration

Theorems “Polynomial price decomposition” and “Finite search and an anytime global interval” are new. For a fixed price, concavity permits removal of all levels after the first maximum of price-adjusted reward. The remaining ordered book has nondecreasing price-adjusted values. Branches can then be partitioned by the consecutive levels that cross their target caps. An eligible upper endpoint implements the cap by its adjacent lottery; otherwise the lower endpoint and a scalar shortfall conjugate give the branch value. These are exact edge contributions, not heuristic local scores.

The resulting acyclic dynamic program takes `O((k+m)N^2)` arithmetic work and `O(N^2+mN)` storage on an N-level catalog. Both k and m vary. Rational quadratic data give exact rational arithmetic with polynomial bit complexity; general convex shortfall costs use a stated scalar oracle. This removes branch-mode enumeration and catalog-subset enumeration from every price subproblem. The predecessor saturated Monge algorithm remains a sharper special case with different assumptions; its complexity is not transferred to the general problem.

A mandatory book prefix has an exact priced completion bound using the same suffix tables. If the prefix already crosses the price-adjusted maximum, later levels cannot improve its priced allocation; mandatory charges are retained. Thus the bounds explicitly use the ordered alphabet and eligibility structure. Search partitions each prefix into its own book and its one-index extensions. It terminates finitely, and it preserves an upper bound on every unresolved subtree at interruption.

We do not claim that the unrelaxed global search is polynomial, fixed-parameter tractable, or an FPTAS. The new result is the nontrivial decomposition and its exact prefix bounds, one of the substantive algorithmic directions requested by the referee. A polynomial price subproblem is not presented as a proof of zero outer duality gap.

Location: Section “Eligibility-Prefix Decomposition”; `decomposition.py` and independent `checker.py`.

## 3. Why the mesh certificate matters, and why its order cannot improve uniformly

The new fixed-input lower-bound proposition uses one branch, one symbol, no opening charge, cap and promise both 1/2, terminal reward `c-c^2/2`, and intermediate cost `y^2/2`. On every odd-denominator uniform grid, the best feasible level is half a mesh below the promise. Direct substitution gives loss `h/4+h^2/4`. The input is fixed as the grid is refined, so this proves order-sharpness along an infinite sequence without using growing input magnitudes or a specially chosen charge.

This lower bound concerns the stated uniform catalogs. It is not asserted for adaptive catalogs: including the cap removes this particular error. We retain the existing exact-feasible transport proof in full.

The computational use is stronger than exhaustive fixed-budget catalog enumeration. An interrupted prefix search already gives a valid catalog interval `[L,U]`; transport gives `[L,U+K_m h]` for continuous design. The report now separates optimization gap from discretization error, includes the full dependence on the charge Lipschitz constant and heterogeneous shortfall costs, and does not require the catalog solver to finish before providing a useful bound.

Location: Proposition “A fixed-input lower bound”; Theorem “Finite search and an anytime global interval”; exact sharpness checks in `verification.json` and interval records in `scaling.json`.

## 4. Independent global witnesses rather than only conditional inner certificates

The referee's distinction is important. The fixed-book multiplier certifies conditional allocation only. The old source hashes certify provenance only. Neither establishes that every other book has been excluded.

The new global witness includes a feasible winning policy, the exact tree partition, the complete child list at each split, an upper-bound price at each pruned or unresolved node, and an inner supporting price for every explicitly evaluated node book. A separate checker rebuilds priced tables from explicit lottery support maximization, not from the solver's edge-construction code, verifies every partition, and checks the policy's exact promise and realization constraints. It imports neither the prefix solver nor the continuous cell generator.

Every feasible book is either represented by a verified node book or covered by a verified pruned or unresolved subtree. This supplies the missing finite global object. Tampered upper-bound records are rejected. Numerical third-party comparisons remain a different source of evidence and are labeled as such.

Location: `checker.py`, the certificate ledgers in `results/certificates/`, and the companion's “Independent Global Verification and Experimental Protocol.”

## 5. Independent original-policy nonlinear formulation

We provide a second global formulation using the original branch lottery probabilities, continuous terminal levels, intermediate services, and binary support indicators. It retains the bilinear promise constraints and cubic expected-reward terms. It does not import the closed-cell objective, cell generator, KKT systems, or price dynamic program. A bounded support indicator enforces each realization ceiling, and a hypograph variable handles the nonlinear objective through SCIP's documented interface.

The study crosses three risk regimes on independently seeded one- and two-branch, two-symbol instances. Each book size is solved separately and the union bounds are reported. The output records numerical lower and upper bounds, solver status, nodes, elapsed time, gap, and package version. A time limit is reported rather than silently dropped. Feasibility tolerance is 1e-8; the target relative gap is 1e-7; cross-method comparisons allow absolute tolerance 2e-5.

These are numerical global bounds within tolerances, not exact-rational proofs. The separately completed rational face computations provide the exact comparison values. The build requires all six comparisons to be present and consistent before publication. The machine-readable study summary is the authoritative execution record; the local draft is not mistaken for a completed third-party run.

Location: `scip_check.py`, `continuous_frontier.json`, and the independent-cross-check table in the companion.

## 6. Expanded computation, explicit stopping, and arithmetic growth

The continuous reference study now crosses branch counts 1 through 4, budgets 1 and 2, and risk tolerances 0, 1/8, and 1, with a further five-branch case. It records all 25 runs. The predeclared budget is 5,000 stationary systems per instance. We report cells started and completed, the fraction of completed cells that are infeasible, all systems attempted, nonsingular systems, feasible candidates, wall time, traced memory, and process resident-set high-water mark.

The maximum bit length of every stored fraction-free elimination integer and every computed rational candidate is observed explicitly. An incomplete face run has no asserted global upper bound. Its reported frontier is a reproducible enumeration-budget frontier, not a claim that larger instances cannot be solved by other methods.

The new prefix method is separately studied up to 256 distinct-cap branches, 65 catalog levels, and budget 8. Its globally checked intervals are computed at the actual promise and tolerance, with heterogeneous costs and actual affine selected-level charges. Separate rows vary shortfall-cost scale and the charge slope. The raw data retain evaluated-book counts, expanded prefixes, all-subset counts for comparison, price-table sizes, rational bit lengths, and separate checker times. All timings are single instrumented measurements and are not presented as uninstrumented performance averages.

Location: Tables “New prefix search and continuous enclosures,” “Scaling parameters and work,” and the two complete continuous-enumeration tables; `study.py` and raw JSON records.

## 7. A broader mathematical contribution without unsupported calibration

We take the referee's second suggested route: broaden the reusable mathematical class. The price theorem needs an ordered shared interface, a common increasing concave output reward, separable convex shortfall costs, target caps, and branch-specific eligibility thresholds at least as large as the target caps. A common overrun parameter, a three-date renewal narrative, and actuarial acceptance language are not required for the theorem.

The renewal contract remains the motivation and a fully specified specialization, including the acceptance timing and execution boundary. The security-interface analogy is not elevated into empirical validation of those choices. We add no fabricated customer data, calibrated parameter magnitudes, or deployment claims. The methodological contribution is now stated independently of that operational interpretation.

Location: “A reusable ordered-interface allocation class,” with the original operational-foundation material preserved.

## 8. The nonmonotone-charge randomization example

The example with charge `3c(1-c)` and its proof remain intact. Its interpretation is now explicitly limited to a mathematical possibility produced by that nonmonotone charge; it is not called a generic certification-cost advantage.

We add a positive structural boundary result: with continuously chosen levels, one branch, concave reward, convex intermediate cost, and any nonnegative nondecreasing selected-level charge, a deterministic one-level policy dominates every randomized policy at the same feasible promise and realization tolerance. Replace the lottery by its terminal mean and intermediate service by its mean. Jensen improves operating payoff, and the old maximum used level has charge at least that of the mean, while all additional charges are nonnegative.

This covers zero charge, nondecreasing affine and convex charges, and a fixed opening fee plus a monotone surcharge. It explains why the retained one-branch example needs a charge outside that class. It does not assert deterministic collapse for arbitrary heterogeneous multi-branch instances or for a fixed catalog that does not contain the mean.

Location: Proposition “One branch with a monotone charge” and its proof.

## 9. Scope, novelty, and presentation

The title now reads “Exact Quadratic Design and Prefix Decomposition.” The introduction and conclusion explicitly distinguish general concave fixed-book structure, the scalar-oracle decomposition, and feasible discretization from exact unrestricted continuous optimization for rational quadratic data. This clarifies assumptions without removing the continuous exact-design theorem or weakening its conclusion.

The new comparison with Handler and Zang identifies Lagrangian path methods as classical. Jourdain and Pages remain the close predecessor for optimized one-dimensional dual grids. The paper continues to credit the classical quadratic witness, matrix-search, stochastic-rounding, and opening-cost principles. The novelty table retains its previous rows and now explicitly distinguishes structural reductions from generic optimization mechanisms. A polynomial-size quadratic witness is not described as an efficient exhaustive search algorithm.

The abstract is a single 183-word text-only paragraph. The introduction contains no equations or mathematical notation. The anonymous readers use 11-point type, one-inch margins, and one-and-a-half spacing, with author-year references. The article uses the journal's Lengthy-manuscript category; compilation checks the nonreference page limit and companion length, undefined references, and overfull boxes. Detailed historical studies and the new implementation protocol are in the companion, not deleted.

## 10. Preservation and reproducibility

The new branch descends from the immutable R42 review commit. Publication changes only the current reader wrappers and outputs, the current README and checklist, and newly introduced R43 files. Every other file tracked at the review baseline is compared against that baseline before publication. All prior revision branches and the review branch remain untouched. The manuscript snapshot in `predecessor/` is checked against the exact baseline bytes.

Tests of R42 and its predecessors execute in disposable directory copies. Source hashes and a clean committed source identity are recorded separately from test results. The final build-validation record names the precise scientific source commit, PDF hashes, page counts, and evidence files. This provides the next referee with the new paper, complete proofs, specific responses, independently checkable global witnesses, and the intact derivation history.
