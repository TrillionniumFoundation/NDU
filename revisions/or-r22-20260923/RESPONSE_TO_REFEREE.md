# Response to the September 23, 2026 Operations Research report (R20 review object)

**Current revision:** R22. **Branch:** `revision/ndu-operations-research-r22-20260923`.

**Paper:** *Accepted Service Adaptation with Neural Differential Utility: Continuation Prices and Certified Gains*.

**Report addressed:** `reviews/operation_research_referee_report_r20_2026-09-23.md`, review commit `18381729edf8d15a536ebef16abf6660ee0db48f`. The reviewed R20 tip was `45553b28f40c92a14895b8b82d8739e608f6d4b1`; its complete manuscript was R19, publication commit `cb4f8644652ebe92f0aac5294baaff898d97f5cf`.

We thank the referee for distinguishing the mathematical improvements from the remaining scientific and empirical questions. This revision gives the manuscript one operational object: the certified gain from expanding an already optimized accepted service-policy class. Continuation geometry identifies the expansion margin, the resource statistic produces an accepted response, and an exact certificate and benchmark gate connect that response to realized gain. Neural differential utility remains a developed implementation of this chain; it is neither removed nor made synonymous with universal computational superiority. Every earlier theorem, proof and adverse experimental result is retained in the complete current main/companion package or the immutable predecessor documents as specified below.

The principal additions are (i) a componentwise exact certificate with an irreducible price-repair floor, (ii) a convex resource/equality-price repair with a rational monotonicity safeguard, (iii) a benchmark-gate theorem and explicit regularization-bias accounting, (iv) a structure-aware lifted primal--dual continuation baseline, (v) independent final validation of two deterministic ensembles against reoptimized time-only amendments, and (vi) scaling on ten full accepted-polyhedron configurations. The ordinary root sources and PDFs, not a plan or encoded transport, are the current review objects. `results/package_check.json`, `results/replay.json`, and `MANIFEST.json` identify the actual executed evidence. Timing numbers are generated from the publication host, not transcribed from a developmental run.

## Additional R22 result: complete repair closes the fixed-block certificate limitation

Beyond executing the inherited R21 design, R22 proves **complete dual-price repair and exact certificate attainment** (`thm:r22-complete`). For the stated quadratic accepted model, the full constrained dual minimum is attained and equals the primal optimum even if the accepted polyhedron has no strictly feasible point or has dependent equality rows. Therefore the best certificate for a fixed feasible decision equals its actual regret. Allowing all prices to vary can remove the extra switching/participation floor created by fixed-block repair; it cannot change that regret. The gradient and a global Lipschitz constant are explicit, and exact projected-gradient iterates have a proved nonincreasing upper bound and a reciprocal-iteration error rate. Numerical best-bound retention alone is not assigned that exact-iterate rate.

The accompanying context-transport corollary gives a nonlearned classical warm start with a fresh auditable certificate when reward and friction change but the accepted geometry remains fixed. It requires neither an optimal-face oracle nor a new primal solve if the fresh certificate already passes. This is not relabeled as the measured twelve-step block algorithm or claimed to have a measured speed advantage. Independent standard-library rational checks cover 225 exact primal/dual optima (45 without strict feasibility), 3,600 projected-gradient steps, and 450 new-context certificate transports. The proof, tests, and test counts are all ordinary repository files.

This separates the genuinely accepted-control consequence from its established tools: polyhedral normal cones and projected-gradient convergence are classical; exact attainable certificate floors and the resulting decision-versus-certificate intervention distinguish the operational questions here. Full earlier statements, proofs and adverse results are retained.

## 1. Incomplete R20 review object and provenance

We agree with the version diagnosis. R20's plan-only tip is not called a completed manuscript. R22 branches from the pinned R21 ordinary-source checkpoint `c2d25791bd1f4c2b1801a446376a86c50eb381fe`, which had not published executed results or new root manuscripts, and preserves the exact R19 root files under `predecessor/`, with pinned SHA-256 values in `PREDECESSOR_SHA256.json`. It replaces both root manuscripts and their metadata with actual R22 artifacts. The complete source, derivations, raw records, generated tables and response accompany them. Publication and independent verification are separate workflow jobs; commit-status context `ndu-or-r22/final-sha` is attached to the final published SHA, not merely the input source SHA.

Locations: root `main.tex`, `main.pdf`, `electronic_companion.tex`, `electronic_companion.pdf`; `PROVENANCE.json`; `MANIFEST.json`; `results/package_check.json`; `.github/workflows/ndu-or-r22-publication.yml`.

## 2. Improvements already credited in R19

The full accepted polyhedron, vector tiers, several resources, heterogeneous outside protocol, equalities, hard capacities, endogenous switching signs, and the inexact-response theorem all remain. We do not replace the general bridge with a scalar or known-face special case. All seven original predictors and eight training/deployment pairs are retained. The complete R19 main experimental block is reproduced verbatim in a dated companion section, including its unfavorable accuracy and runtime evidence. The older scalar, verified-cell, friction, continuous and nonlinear developments remain available without destructive edits.

The build verifies verbatim preservation of every pre-existing theorem, proposition, lemma, corollary, definition, assumption and proof block across the current main and companion. `PRESERVATION_MAP.md` and `results/package_check.json` record the check.

## 3. Neural framing and the strongest direct-price comparator

The title and opening now identify accepted expansion and certified gains as the organizing decision problem while retaining Neural Differential Utility. The paper does not claim that an RBF interpolator is neural, that a scalar critic is necessary, or that neural methods beat the strongest observed classical implementation. The original RBF/direct-price findings remain, and the new comparisons are reported for all methods. The direct-price route and the value-gradient route are two ways to obtain the resource statistic; the common contribution is the accepted decision and auditable gain they support.

The new matched-cost experiment compares original and repaired certificates without changing the underlying proposal. It includes 5,120 complete pipelines with identical independent final tolerances, actual fallback, and a strong classical alternative. Its tables and discussion are generated from every recorded row. A better pass rate is not relabeled a better decision, and a speedup against a weaker baseline is not called superiority over the lifted classical solver.

Locations: abstract and introduction; main Sections `sec:r22-certification`, `sec:r22-benchmark` and the current computational study; `tables/matched.tex`; `matched_cost.py`; `results/matched_rows.json`.

## 4. Derivative supervision and model description

The paired R19 result remains a representation comparison on the same optimizer-generated training population. The main text states that the tanh models use fixed random features with a ridge readout, not a fully trained deep network. Value and derivative labels are generated by the same known optimization model; we make no claim that derivative labels provide information unavailable to a direct learner or arrive at zero cost. New scaling records separately charge label generation and fitting. No original unfavorable comparator is removed to elevate the neural result.

Locations: current computational methods paragraph; dated R19 empirical section in the companion; `results/scaling_summary.json` setup records; `tables/setup.tex`.

## 5. Novelty of the global bridge

We now identify established ingredients explicitly: strong-convexity sensitivity, an envelope identity in specified reward coordinates, and Fenchel/Bregman algebra. We do not claim these as new general results. The model-specific consequence is an accepted response that keeps continuation, equality, capacity and switching constraints inside the optimization problem across face changes. The main theorem-comparison table states what each prior result already delivers, what is added here, and whether the addition is analytic, algorithmic, statistical or application-specific.

The new certificate contribution is also stated precisely. At an actually feasible decision, its upper-bound gap equals box Fenchel error, resource mismatch, switching slack and participation slack, plus known outward rounding. Holding switching and inequality prices fixed makes the latter two terms an irreducible floor for resource/equality-price polishing. This yields a stopping/diagnostic rule rather than another claim that classical duality itself is novel. The small-dimensional repair is convex and its rational acceptance test is monotone; twelve numerical steps are not advertised as exact finite convergence.

Locations: `sections/literature.tex`, `sections/certification.tex`, `sections/complete_dual.tex`, `complete_dual_checks.py`; main labels `thm:r22-decomposition`, `prop:r22-polishing`; `LITERATURE_MAP.md`.

## 6. Missing learning-and-optimization literature

The revision engages all four requested literatures directly and adds a modern warm-start comparison: Elmachtoub and Grigas (2022), Bertsimas and Kallus (2020), Amos and Kolter (2017), Kraul, Seizinger and Brunner (2023), and Sambharya et al. (2024). Stellato et al. (2020) is cited for the OSQP solver implementation. Author names, issue years, page ranges and primary-source identifiers are recorded in `LITERATURE_MAP.md` and the bibliography.

The comparison does not infer that these papers have no certificates or no applicable results merely because their models differ. Predict-then-optimize already motivates downstream decision loss; dual-variable prediction already motivates learned optimizer statistics; differentiable layers already relate constrained optimization and learning; learned fixed-point warm starts already study acceleration with appropriate guarantees. Our distinction is the specified accepted-service expansion problem, its exact decision/benchmark certificates and the empirical implementation on that geometry.

## 7. Deliberately chosen value-gradient coordinates

The introduction, theorem discussion and comparator section now state that the perturbation is the prescribed linear resource-reward coordinate. The derivative equals the resource vector because of this construction, not because every arbitrary value function reveals every price. The scalar critic is optional. One structural difference is integrability of a differentiable scalar gradient; our tanh critic is not constrained to be convex, so neither cyclic monotonicity nor a performance advantage is inferred from this observation. We retain direct-price learning as a central comparator and report when it is stronger.

Location: main `sec:r19-bridge` and `sec:r22-benchmark`; literature comparison table.

## 8. Stronger structure-aware classical baseline

We implement a lifted full-objective QP with the resource coordinate introduced explicitly and constrained to equal the tier resource load. This replaces the dense resource quadratic by a sparse diagonal quadratic plus resource equalities. It reuses the numerical workspace and carries the entire previous primal/dual state, including resource prices, between contexts. It is a classical structure-aware continuation method with no statistical learner. Its original and lifted formulations have the same objective and acceptance constraints, and all final decisions are checked by the same independent full-objective rational audit.

The main paper describes solver family, fixed matrices, cached workspace/factorization, linear-term updates, adaptive-penalty refactorization, warm-start contents, and what the cold reset does and does not reset. We do not claim to have exhausted all active-set, commercial or parametric solvers. The strengthened baseline is actually executed on the same contexts and tolerances, not left as a proposed comparison.

Locations: `core.py:Lifted`, `matched_cost.py`, `scaling.py`; main solver paragraph and current timing table.

## 9. Scaling the full general class

The new study contains ten configurations: the base service/resource/capacity class grows from 31 to 1,023 tree nodes (up to 2,046 tier variables), and additional configurations change service count, resource count, extra capacities and diagonal curvature. Each configuration has its own fixed independent training population and two fitted predictor types, plus eight held-out contexts and both final tolerance targets. The study contains 640 audited training labels and 800 deployment attempts. It compares dense cold, dense previous-context, lifted continuation, tanh-gradient and RBF-direct pipelines. Setup, label generation, fitting and matrix nonzeros are retained separately; all deployment failures remain in summaries rather than disappearing from timing means.

This is descriptive structural scaling, not a high-confidence universal complexity comparison. The uniform 64-label budget was finalized after an explicitly disclosed dense-label engineering run revealed substantial offline cost, before the reported final scaling run. Both architectures and all specified geometries remain; no held-out model selection was performed. `audit_notes/LABEL_BACKEND.md` distinguishes the engineering plan from final evidence.

Locations: `DESIGN.json`, `scaling.py`, `results/scaling_rows.json`, `results/scaling_fits.json`, compressed exact primitives/records; main strict-target and companion coarse-target tables.

## 10. Economically meaningful outside comparator

The announced heterogeneous feasible protocol is retained as the participation reference, not promoted to an optimized economic benchmark. The new comparison reoptimizes time-only amendments under the identical continuation, root, box and capacity constraints. These amendments have a common adjustment at a given date/service while preserving the outside protocol's heterogeneity; we expressly do not call them best-static total tiers.

A separate lifted restricted solve, exact class-preserving repair, and additional equality checks provide both a feasible restricted value and an upper bound on the true restricted optimum. The benchmark-gate theorem gives a one-sided computable gain against that optimum, not just against a numerically selected weak incumbent. The full costs of this gate are separate from acceleration claims. New validation uses it; the old outside-relative results remain as historical evidence.

Locations: `time_comparator.py`, `certificate.py` additional equality verification; `sections/benchmark.tex`; companion exact time-only repair construction.

## 11. Deterministic deployment and independent validation

The new deployable rules are deterministic means of all eight frozen tanh-gradient price predictions or all eight frozen RBF-direct predictions, followed by a fully specified response, repair and benchmark gate. No model is selected using final validation results. New final populations contain 2,048 IID contexts and 512 shifted contexts. Four simultaneous conditional expected-gain lower bounds cover both policies on both populations. Their target is gain over the true reoptimized time-only optimum.

We use a safe range width of twice the corner-certified bound: a feasible approximate restricted solve cannot be assumed to dominate the true restricted optimum on every future query. A one-sided sample statistic subtracts the restricted upper bound. No uniform future numerical-tolerance assertion is inferred from the observed comparator errors. The theorem conditions on the frozen rule; it does not guarantee every future training run.

A code inspection identified adaptive solver-state leakage in an initial pilot. We isolated every numerical workspace per method/context and reran the final experiment using fresh, previously unexamined seeds 23011/23012, without changing fitted models, ensemble weights or selecting a preferred policy. The pilot is excluded from the manuscript and confidence calculations, and its provenance/correction is retained in `audit_notes/STATE_ISOLATION_CORRECTION.json`. The older randomized-fleet theorem is preserved for its different target and does not substitute for this final evidence.

Locations: `validation.py`; main `prop:r22-validation`; `results/validation_summary.json`; independent reconstruction in `replay.py`.

## 12. Shift, known-model scope and operational interpretation

The frozen trained models are now evaluated on a deliberately wider resource-reward/friction distribution without retraining. This is a learned-policy covariate-shift study, not merely a theorem geometry check. We report its actual regret, certificate pass rate and restricted-contract gains. The accepted model itself remains known and synthetic. Unknown demand laws, incorrectly specified resource coefficients, changing acceptance constraints and field calibration are not claimed to be solved by the pointwise certificates. A valid certificate for an incorrectly specified operational model is not evidence of field validity.

Locations: current empirical shift subsection; `validation.py`; `results/validation_geometry.json`; companion distinction from historical boundary/quartic checks.

## 13. Geometry versus objective generality

The abstract and theorem discussion prominently state strong convexity and smooth resource coupling for the global quadratic price-error bound. The new certificate section separately proves that weak Fenchel certification extends to proper closed convex box costs and coupling whenever the conjugates are finite; it does not carry the quadratic sensitivity rate to that larger objective class. If curvature is added by regularization, an explicit original-objective regret bound charges its bias. The experiments use their stated economic curvature, not an unreported regularizer.

Location: main `eq:r22-regularization`; `theory_checks.py` exact noncurved/nonsmooth examples; no regularity assumption is hidden in the generalized statement.

## 14. Coherent paper and preservation of scientific content

We reorganize the paper around one question, the accepted-expansion gain relative to an optimized restricted class. The early general formulation states that target; continuation geometry establishes it; the price-response theorem and certificate implement it; the benchmark gate and final validation evaluate the same target. The complete R19 empirical section moves verbatim to a dated companion section; all older mathematical results and proofs remain. This avoids presenting a succession of revision-specific experiments as independent headline contributions without deleting the history or abandoning the neural development.

Both current documents use the journal's anonymous, 11-point, one-and-a-half-spaced, one-inch-margin format, author-year references and tables after references. Tables may share pages instead of forcing one page per table; text is not shrunk to conceal length. Actual page counts and all-reference checks are recorded in the package checklist. The paper is prepared for the journal's Lengthy category, not represented as a standard 30-page submission.

## 15. Specific comments

### 15.1 Two-Bregman identity

We identify the R19 identity as Fenchel/Bregman algebra applied to the stated conjugate pair and cite the underlying convex-analytic framework. Its use in an accepted, implementable response is the point, not a new universal identity. The new four-component identity makes the same novelty boundary explicit.

### 15.2 Value learning versus direct-price learning

A scalar value critic is an admissible construction with a specified gradient coordinate and integrability structure. No general preference is asserted. Both original and new tables retain the stronger direct-price comparisons.

### 15.3 Solver details

The current main includes OSQP's operator-splitting family, lifted resource representation, fixed matrix workspace, linear-cost updates, full warm-start state and adaptive-penalty refactorization caveat. Statistical validation, unlike the timing study, deliberately uses fresh workspaces to define a memoryless frozen policy.

### 15.4 Theorem stress versus learned robustness

The preserved 64 geometry cases and 64 quartic checks remain labeled as theorem checks. New shift records evaluate the actual frozen learned ensembles on the declared shifted population; no field robustness is inferred. Geometry activity counts are separately reported and are not forced to be positive or called stress when they are zero.

### 15.5 All-binding star rows

The companion's historical capacity rows continue to state that a common repaired decision tests response/repair, not predictor differentiation. The current main explicitly preserves that interpretation.

### 15.6 Fleet sampling

For the old uniform-fleet operational description we distinguish a common independent context distribution from a different mixture that jointly samples a model index and an index-specific context law. These are not interchangeable targets. The current expected-gain conclusion uses the new deterministic, state-isolated policy under a separately stated common distribution for each validation domain.

### 15.7 Break-even interpretation

The historical 2,546-query figure remains host/protocol-specific descriptive accounting, not a universal economic threshold. New timing and offline costs are reported separately. An empirical advantage against one baseline is not extrapolated to all hardware, stronger solvers or stricter tolerances.

### 15.8 Execute price polishing before claiming it

R22 implements and executes price polishing. For every matched record, original and repaired decisions/tensions/inequality prices must be identical, the rational upper bound cannot increase, and the final target must pass after any actual fallback. The independent replay checks those facts. This distinguishes an executed algorithmic addition from R20's unexecuted plan.

## 16. Conditions for reconsideration

The revised package supplies a precise literature/novelty map, a single accepted-expansion theorem chain, a stronger low-dimensional classical formulation, scaling on the full class, a meaningful optimized comparator, independent final deterministic validation, and a declared frozen-policy shift study. It retains neural theory and implementations while following the actual evidence rather than concealing stronger non-neural methods. These changes address the requested scientific tests directly; they do not presume that every editor must agree on novelty or that additional field studies are unnecessary.

## 17. Closing response

We have not treated the recommendation as a reason to stop the research or replace the paper with a plan. R22 is a completed, testable revision with proofs, executable methods, raw results, current manuscripts and final-commit verification. It establishes concrete accepted-control and certified-gain claims under their stated assumptions. It does not claim neural computational superiority where the executed experiments do not support it, nor does it equate successful reproduction with journal acceptance.

## R22 structure-aware scaling refinement amendment

During execution, the inherited large-tree code exposed a structurally weaker dense full-objective fallback at numerical tolerance 1e-9. The scale study now gives **all five methods at both targets** a fresh lifted full-objective fallback at the same numerical tolerance, charging its setup, solve and independent rational audit. There is no cross-method fallback state. Training labels, frozen rules, geometry, seeds, sample counts and certificate targets are unchanged. No time from the interrupted developmental dense-fallback run is used as publication evidence. The original source remains in R21 and the initial R22 source commit. The complete 63-node matched experiment keeps its documented protocol; the scale and matched timing results are not pooled. `audit_notes/SCALING_REFINEMENT_AMENDMENT.md` and `DESIGN.json` record this amendment.
