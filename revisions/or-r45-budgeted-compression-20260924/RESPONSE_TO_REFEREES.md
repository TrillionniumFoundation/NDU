# Response to the R44 Operations Research Referee Report

Manuscript: **Limited-Memory Renewal Contracts: Budgeted Compression and Certified Joint Design**.

Reviewed manuscript: R44, commit `fe066aac2862fc89fc8eb2e19fd98b4b96e6d5a3`. Latest independent report: `reviews/operation_research_referee_report_r44_independent_harsh_2026-09-24.md`, on review commit `91583abe77208ec4ed25b5fbc5a15f89d54fcd6f`. This response addresses that report, not the earlier R42 report used by R44.

Revision branch: `revision/ndu-operations-research-r45-budgeted-compression-20260924`.

## Central change

The revision supplies a constructive guarantee for the original symbol budget rather than making union expansion the main answer. Theorem 3.1 gives exact conditional alphabet design at every cardinality with actual opening charges. Corollary 3.2 makes this a polynomial global catalog algorithm at saturation, with variable branch count and symbol budget. Theorem 4.2 supplies an additive approximation scheme for joint catalog design at the original budget when the branch count is fixed. It enumerates a feasible weighted target net, not alphabet subsets. The approximation exponent and the numerical dependence on accuracy are explicit. Theorems 5.1 and 7.1 add local distortion certificates and charge-aware inexact support recovery. These results complement, rather than retract, the exact continuous, saturated Monge, and union-augmentation theory.

The current article and companion retain all 34 inherited theorem/proposition/lemma label identifiers audited in the complete R44 readers. Seven new labeled results are added. Every historical source file and numerical artifact remains untouched. The new content map records relocated material and identifies the full predecessor readers. Earlier tables are not passed off as newly executed experiments.

## 1. Version audit and substantive continuity

We have used the report's pinned R44 tip as the scientific predecessor and the report-bearing review commit as the new branch base. In particular, the corrected active-face inequality count remains s + 1 + 4k. The exact positive price-gap example, fixed union construction, and original-budget versus enlarged-budget distinction remain. The revision does not attempt to erase a valid objection by reverting to an older manuscript or changing the reported problem.

The new root readers, response, source, executed evidence, and validation record belong only to the new revision branch. The review branch and every preceding revision branch are unchanged.

## 2. Audit of the two-price argument

Section 7 now writes the two optimizer inequalities explicitly and adds them to obtain the monotonicity of exact supported totals. This proof covers arbitrary tie-breaking among exact optimizers. It is not applied to approximate optimizers.

We define U explicitly as the minimum of two certified endpoint upper bounds, not necessarily the minimized dual value. The theorem's recovered target is the mixture of the endpoint target vectors; it preserves that mixed vector and its aggregate promise, not both endpoint vectors simultaneously. The pre-draw tier and every positive-probability realized ceiling are reconstructed and checked.

The strict-gap example retains values 45/64 and 453/640. We now state that the gap 3/640 is 1/150 of the original optimum. It is labeled a relaxation-gap example, not a factor-two lower bound.

## 3. The original memory budget

The reviewer correctly distinguishes bicriteria augmentation from original-budget approximation. The new principal results address the latter directly. Given targets, every candidate path in Theorem 3.1 uses at most the requested budget. At saturation the targets are forced, so this theorem solves the full catalog problem with nonuniform charges and heterogeneous realization ceilings.

At an interior promise, Theorem 4.2 enumerates a weighted target net for each possible lowest installed level. It preserves that lower level as a feasibility anchor, rounds only k - 1 weighted target coordinates, fills the remaining coordinate, and repairs any residual within target caps. A profile within the stated weighted distance of the globally optimal targets retains the same optimal book as a feasible comparison. Lipschitz sensitivity then gives the requested additive loss without changing the installed budget or its charge.

For fixed k the scheme is polynomial in the displayed numerical accuracy parameter and catalog/input size. Its exponent is k - 1. It is not described as an FPTAS with a variable number of branches, and an interrupted net does not receive a completed-coverage certificate. This explicit complexity distinction is part of the theorem, not a later disclaimer.

## 4. Contribution beyond generic Lagrangian convexification

We select two of the constructive routes requested by the report: optimal budgeted compression and a same-budget approximation scheme. The target-crossing decomposition is not the old price-admissible recurrence with a renamed multiplier. All ordered arcs are allowed; each arc owns branches according to their fixed targets, and an ineligible upper endpoint contributes fixed intermediate service rather than an illegal lottery. Opening charges are optimized inside the path objective. This yields every exact and at-most cardinality in one computation.

The recurrence itself and interval dynamic programming are classical, as the revised positioning makes explicit and cites. The model-specific contribution is the exact contractual edge reduction and its use as an efficient oracle in a feasible global target net. The paper does not claim a new general theorem about one-dimensional convexification, Caratheodory mixtures, or generic grid enumeration.

We do not claim that twice the memory is universally necessary. The original-budget results and the conditional frontier answer the resource issue by the alternative routes expressly requested in the report. A tight universal expansion lower bound is not asserted as proved.

## 5. Nonvacuous charged guarantees and the returned policy

Charges are included at three distinct levels. First, conditional book selection minimizes actual distortion plus actual selected-level fees. Second, the same-budget target-net theorem permits arbitrary nonnegative catalog fees and provides the requested additive accuracy without an uncontrolled union fee. Its proof keeps the globally optimal book fixed in the target comparison, so its fee does not change. Third, support compression minimizes the net distortion--charge term for the requested budget instead of automatically paying for the entire union.

The local Jensen certificate subtracts the minimum feasible anchor fee from its upper bound and reports the selected distortion-and-charge deficit exactly. It can still be loose, and no uniform relative approximation is claimed when net values can be near zero or negative.

The operational recommendation keeps the better of the core target portfolio and a feasible greedy policy at the same budget, in addition to retaining the old incumbent among the core profiles. We preserve an important charged counterexample: the core method is 101/3600 below the optimum 1373/3600, while the greedy fallback attains it. The raw core, safeguard, union, prune-down and exact values are all retained. The manuscript reports core success on 35 of 36 cases and safeguard success on 36 of 36, not a fictitious universal success of conditional optimization.

## 6. Continuous design, adaptive candidates and local certificates

The original uniform mesh theorem and its sharpness proof remain in Appendix D. The new local analysis distinguishes eligible chord interpolation, where curvature produces a target-specific quadratic deficit, from ineligible upper levels, where the shortfall expression is first order. It does not apply a curvature bound across an eligibility discontinuity.

Theorem 5.1 computes a posteriori distortion-and-charge certificates at ideal capped targets. Proposition 5.2 gives explicit original-budget comparison-book rates, including the grid-availability, zero-charge and realization-headroom assumptions. These compare installed policies at the same memory budget and do not rely on a small price tolerance removing mesh loss.

The study adds 22 direct comparisons against exact continuous references in four stated solvable regimes. In the interior two-branch case, a four-candidate pool containing the ideal targets reaches the exact two-symbol continuous optimum, while the 65-point uniform catalog still loses 0.0029909375. The saturated off-cap-top case is recovered with six adaptive candidates. Two seven-branch saturated comparisons also retain exact continuous references. Adaptive midpoint selection is identified as a candidate-generation heuristic, not given an unproved universal complexity guarantee. Exact-reference loss and Jensen certificates are separately reported.

## 7. Comparative computation and resource quality

The new comparison sample uses six seeds and three distinct cap families, with heterogeneous weights and curvatures, several promise/risk settings, and eighteen free plus eighteen nonuniform-charge cases. Exact joint catalog optima are computed at every budget through twice the original budget. Baselines include raw two-price recovery, greedy addition with exact reallocation, greedy union pruning with reallocation, and exact enlarged-budget design.

The evidence includes gain over the old original-budget incumbent, comparison with greedy addition, overlap, nestedness, actual union size, percentage expansion, gain per added symbol when defined, and optimality loss at the union's actual size. The last of these is not replaced by a difference from an original-budget price bound. All component policies and raw results remain available.

The core method beats greedy addition in ten cases and loses in one. Two original-budget incumbents are strictly improved. Endpoint books are nested in 23 of 36 cases, and the largest union has four levels. These observations are not a factor-two necessity study. Instead, the exact conditional frontier and exact small joint frontiers make the value of each available resource budget observable.

The additional scaling study has twelve random heterogeneous instances through 256 branches, 65 candidates and eight installed symbols, each timed three times. It tests conditional optimization and reports valid posterior gaps, not unknown global joint errors. Repeated timings on one instance are not statistical population replications.

## 8. Mathematical independence of validation

The prior checker is now described according to its actual scope: rational policy replay and a separate implementation of a common price decomposition. We add a genuinely different formulation rather than rename that checker.

The new mixed-integer model retains original branch probabilities, pre-draw intermediate service, level activation binaries, support binaries, the root equality, participation caps and the implication y + level <= realization ceiling for every used support. It neither eliminates probabilities through the canonical formula nor imports any price or target-crossing recurrence. Tangent and secant envelopes bracket quadratic costs with an analytic error bound. Twelve selected input instances at two budgets give 24 independent comparisons and 48 envelope solves.

All exact catalog values lie within the numerical brackets under the declared comparison tolerance, all solver runs report optimal termination, and direct residuals are below 1e-6. The manuscript expressly calls these numerical MIP brackets, not exact rational global certificates. Separate support/subset enumeration supplies 288 exact conditional comparisons. These two validation paths address different failure modes.

## 9. Inexact oracles, promise repair and numerical risk

The new support theorem permits feasible suboptimal endpoint policies and certified approximate price bounds. Each oracle defect is the certified upper bound minus the endpoint's actual priced payoff. The final guarantee separately displays the weighted oracle defects, price-bracket error and optimally compressed distortion--charge penalty.

Approximate optimizers are not assumed to have monotone supported totals. The theorem requires and checks a feasible bracket. It does not invent a call-complexity bound for an unspecified approximate solver.

The target-repair lemma clips to a selected book's feasible target intervals and performs bounded rational transfers to meet the root equality. The companion distinguishes mixed-target perturbation from root residual: their sum, multiplied by the branch response Lipschitz constant, bounds the extra loss. Checking only the root residual would miss cancellation of branchwise errors. Lotteries are reconstructed after repair, and realized totals are checked directly. Ten deliberately suboptimal support pairs and 144 repair tests supplement the exact-support evidence.

Parameter-estimation uncertainty is not conflated with arithmetic error. In particular, an estimated realization threshold must be replaced by a defensible safe bound before optimization; the theorem does not claim continuity of the selected book across eligibility changes.

## 10. Operational interpretation

The revised manuscript keeps the renewal mechanism and its full information restrictions. It explains that an execution symbol is one enabled terminal command, not one bit, and that additional enabled levels can require certification or maintenance expenditure. A supplied opening-charge function is not an empirical estimate made by the paper. The zero-fee regime is a declared comparison case rather than a claim that actual memory is free.

The new main theorem no longer requires a provider to accept doubled memory. The original-budget global saturation result and fixed-branch approximation scheme give a pure optimization contribution within the original institution. A service-gateway interpretation is identified as an interpretation of the abstract class, not independent calibration or evidence of a second deployed model. No operational data or willingness to expand an interface has been invented.

## 11. Length, structure and preservation

The article now presents the original-budget results before pricing and computation. Continuous quadratic design and saturated Monge theory are regular appendices. The companion retains institutional theory, robustness, deterministic/randomized comparisons, catalog and union results, and mathematical proofs. Older study protocols and full historical tables remain in the complete predecessor readers, with their original scientific sources untouched.

The locally rendered R45 main paper has 34 total pages, including two reference pages; the companion has 33 pages. This is 32 nonreference main pages, compared with R44's reported 39. The publication manifest records the final runner page counts. The abstract is under 200 words. The build checks journal layout, page limits, cross-references, duplicate labels and overfull boxes. All 34 inherited mathematical label identifiers remain in the current main/companion; the reorganization is not a deletion of the prior theorems.

## 12. Scope of each claim

The manuscript now distinguishes: exact conditional catalog optimization; exact global saturated catalog design; the fixed-branch same-budget additive scheme; a finite target portfolio without a universal global guarantee; exponential unrestricted continuous quadratic reference optimization; and at-most-double-memory union recovery. The abstract introduces the original-budget results and their branch-count restriction before secondary results.

The charged local bound is reported as a measured distortion-and-charge certificate, while the arbitrary-accuracy same-budget guarantee comes from completed target-net coverage. The independent MIP experiment is explicitly numerical. The broader interface language is a mathematical abstraction with a service-gateway interpretation, not a claimed second empirical validation.

## 13. Requested routes for a credible revision

The revision implements the report's original-budget route, optimal-compression route, controlled charged-design route, independent-formulation route, inexact-oracle route, and comparative-computation route. It does not replace them with a lowered contribution statement. Tight factor-two necessity and empirical calibration are not claimed; the paper's stronger original-budget theory does not depend on either claim. The conditional all-budget frontier supplies the requested m-plus-extra-symbol tradeoff, and the separate target-net theorem supplies a global original-budget guarantee under a precise fixed-branch condition.

## 14. Minor comments

The exact-optimizer tie inequality, endpoint-bound interpretation, relative strict-gap size, mixed-target meaning, catalog-versus-installed-size distinction, and original-budget versus augmented-value distinction are explicit in the current main text. The main and companion tables add resource overlap and quality at the actual union size. The operational recommendation includes the same-budget safeguard while retaining raw union and portfolio values.

Stored-entry bit lengths are not presented as bounds on every arithmetic temporary. Resident-memory counters are identified as cumulative process quantities, not incremental algorithm storage. The abstract is text-only and the introduction contains no equations or mathematical notation. References are author-year and alphabetical. Tables are placed after the references; the analytic figure remains near its relevant appendix discussion. No new footnotes or author-identifying title information are introduced.

## 15. Closing assessment

We appreciate the report's distinction between mathematical credibility and significance. The new submission is anchored by original-budget optimization, exact conditional compression and a proved fixed-branch additive scheme. It retains the prior theory, supplies independently formulated comparisons, and keeps the charged portfolio failure visible. The source, complete proof chain, executed evidence, and branch-specific readers are available for another independent review. Publication suitability remains for the journal and referees to assess; the response makes no claim that numerical checks alone establish that decision.
