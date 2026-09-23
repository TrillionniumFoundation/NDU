# Response to the R23 Operations Research referee report

**Manuscript:** *Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains*  
**Revision:** R24, September 23, 2026.  
**Report addressed:** `reviews/operation_research_referee_report_r23_2026-09-23.md`, review commit `685fdc4d4f1823c6930bd6ccdfbc66822043bf9e`.  
**Reviewed scientific base:** complete R23 paper `b4165155612fea340a8832bbe7a8b13fe2b9259b`.  
**New branch:** `revision/ndu-operations-research-r24-20260923`.

We thank the referee for distinguishing the paper's accepted-control results from the empirical standing of its neural implementation. We have reorganized the manuscript around accepted expansion relative to an optimized restricted contract, strengthened that connection with a benchmark-relative transfer theorem, and executed the requested comparator-tightness and computational-accounting diagnostics. We have not removed neural methods, prior theorems, unfavorable comparisons, or historical derivations. The formal main/companion pair retains all 72 predecessor mathematical statement and proof blocks; the robust result is explicitly relabeled as a certification lemma. A separate computational record preserves relocated experiments as part of the code-and-data package, not as a second formal journal companion.

The main structural addition is not another generic robustness or learning theorem. For positive scalar continuation payments, we now prove an exact bijection around **any feasible restricted contract**, including a nonconstant or boundary contract with unused participation slack. Relative flows have lower bounds determined by that slack, rather than being forced nonnegative. Theorem `thm:r24-transfers` gives the exact quadratic expansion formula against an optimized restricted contract and charges comparator error when the restricted optimization is approximate. A fully worked three-node time-only example has restricted value `5/24`, accepted value `21/64`, and expansion `23/192`. Its optimal relative flow has a negative coordinate and would be excluded by applying the older cap-matching coordinates outside their assumptions. This connects the paper's strongest structural material directly to its economic comparator.

## 1. Completed object, provenance, and reproducibility

We use the completed R23 manuscript, not the earlier R20 plan-only tip. The new branch begins at the latest review commit and retains that report. Exact reviewed root files are copied to `predecessor/`, with hashes in `PREDECESSOR_SHA256.json`. Every older revision directory and report remains unchanged. The final package includes ordinary standalone TeX, compiled PDFs, a result ledger, source and result hashes, executable scripts, and independent rational replay. These establish what was executed and preserved; they are not presented as evidence of scientific novelty or journal acceptance.

## 2. Deficiencies already resolved in R22/R23

We retain the stronger lifted primal--dual continuation baseline, optimized time-only amendments, full-polyhedron scaling through 1,023 nodes, deterministic frozen-ensemble validation, solver-state isolation, and joint coefficient uncertainty. The original observations, seeds, failure records, and statistical targets remain distinct. No historical small-sample or randomized-fleet statement is pooled into the new fixed-fit timing study or into deterministic-policy validation.

## 3. Scientific identity and the role of Neural Differential Utility

The title, abstract, opening contribution statement, order of results, and conclusion now center on accepted-service expansion, continuation prices, transfer coordinates, and implemented gain certification. The principal structural conclusion can be stated without invoking a predictor: accepted revisions admit exact benchmark-relative continuation coordinates, with price/capacity conditions and constructive witnesses for economic gain. Neural Differential Utility remains an implementation route, with its full value-gradient and inexact-response analysis preserved. Direct-price and classical methods remain comparators, not supporting characters selected to make a neural method appear superior.

We distinguish four questions throughout the numerical discussion: the value created by enlarging the accepted class; the portion recovered by an implemented proposal; the reliable online cost of recovering it; and the total cost after labels, fitting, and setup. Expansion value belongs to the policy class. A learned approximation can recover that value or reduce its computational cost; it does not create the class-expansion value by itself.

## 4. Scale and interpretation of the robust result

The affine-uncertainty implication is now **Lemma `thm:r23-robust`**, explicitly a certification lemma. Its statement and proof remain intact. We identify vertex robust counterparts and weak duality as classical, and retain the interior-comparator counterexample because it prevents a wrong economic comparison when acceptance changes with the model. We do not use this short lemma to carry the novelty burden. The main structural development is the continuation/transfer analysis, including the new benchmark-relative result.

## 5. Designed uncertainty versus calibration

The manuscript now distinguishes truth-in-set certification, sensitivity to a declared perturbation family, statistical coverage calibration, and field robustness. The first two are established here; the latter two are not claimed. The radius grid and the construction of participation/capacity perturbations remain fully disclosed. The nominal failure frequency is a property of that designed family, not an estimated operational failure probability. No field data, calibrated coverage, or out-of-set protection has been invented to answer this objection.

## 6. Classical robust maximin and learning's contribution

The stronger classical robust-maximin comparison and all adverse neural/direct-price results remain. Its objective maximizes the common certified maximin criterion; the learned candidates solve different, price-mediated response problems and can obtain lower certificate values. Accordingly, the robust gain experiment establishes a value of accepted optimization and certification, not a neural theorem or a matched-quality neural speed advantage. The additional fresh-host timing record reports those differing achieved certificates alongside complete costs.

## 7. Amortization against lifted continuation

We executed a new 1,728-pipeline study: three full accepted polyhedra; one independently fitted 64-label model pair per configuration; 32 held-out contexts; three repetitions; three methods; and two final rational certificate targets. The configurations are 63 nodes with six resources/four capacities, 127 nodes with twelve resources/eight capacities, and 255 nodes with six resources/four capacities. We report individual label and fit costs, setup differences, prediction, initial solve, audit, polishing, and every fallback component. The teacher labels are numerically computed optimizer statistics audited to the declared tolerance; exactness refers to the independent certificate arithmetic, not an assertion of infinite-precision training labels.

The comparison is against lifted continuation, not a retired cold or dense baseline. `timing_analysis.json` records the cost difference at query volumes from one through one million and computes an observed crossing only when measured online savings are positive. It retains paired resampling intervals and a moving-block sensitivity check. A nonpositive saving or an interval spanning zero does not justify an amortization claim. The actual outcome is recorded rather than imposed by the manuscript. The raw and aggregated records retain all attempts and failures.

## 8. Expansion value is not predictor value

The new transfer theorem connects the optimized restricted contract itself to the expanded class. The implementation theorem then subtracts a proposal's certified loss; the benchmark gate charges the restricted comparator's numerical error. The introduction and Sections `sec:r22-early`, `sec:r24-transfers`, `sec:r22-benchmark`, and `sec:r24-diagnostics` explicitly separate these objects. The original positive conditional expansion-gain results and the near-optimal direct-price results are unchanged. They do not imply that a neural method is responsible for the underlying expansion opportunity.

## 9. Online comparator costs

We now state three protocols unambiguously. Accepted implementation audits the candidate and its own objective gap. Pointwise economic certification additionally requires a restricted-comparator upper bound; the robust version requires all eight outer-comparator bounds unless valid reusable bounds are already available. Population validation computes these comparators offline for an independently sampled frozen-policy evaluation.

The nominal matched timing tables measure the first protocol. The archived R23 robust analysis now charges the whole eight-comparator batch to each independently certified method, while explicitly noting that its old timers omitted ensemble prediction. To avoid combining timings from different hosts, we additionally executed a fresh 16-context, two-radius study with all three methods. All 96 complete pointwise certifications include individual ensemble prediction, fresh workspaces, rational repair, vertex evaluation, and the eight-comparator batch. One-time model loading and geometry construction are separately disclosed. The batch is actually reused among methods in the experiment but charged once when evaluating each method as an independent deployment. Because candidates need not achieve the same robust gain, this is complete cost accounting, not a matched-quality speed claim.

## 10. Quantified robust outer-bound tightness

For each of the 96 R23 contexts and each of its four radii, we evaluate two strictly interior rational coefficient vectors, giving 768 models and 1,536 new comparator solves. At each model we separately optimize the true model-specific accepted time-only comparator and the common outer time-only comparator under the same interior objective. Each value is enclosed between an independently checked rational feasible lower value and a Fenchel upper certificate.

The reported slack is the original vertex-mixture certificate minus the true restricted optimum. We separate outer-set relaxation from interpolation and numerical upper-bound error. Both are reported as certified intervals, with means, medians, quartiles, ninety-fifth percentiles, and maxima by radius. At radius one quarter, the mean total upper slack is approximately `0.096102`, comprising approximately `0.075207` from the outer class and `0.020896` from interpolation. Machine-readable intervals, not rounded numerical optima, determine these summaries. This diagnostic quantifies conservatism without replacing the uniform proof with a sampled argument.

## 11. Novelty boundary and the central result

The first result-level comparison row now highlights the benchmark-relative transfer characterization rather than treating all standard convex ingredients as independent innovations. General KKT, total-variation support functions, conjugate sensitivity, envelope differentiation, and generic projected-gradient rates remain explicitly attributed to established tools. The accepted-service consequences are cumulative continuation prices, exact transfer geometry, cap/slack comparative statics, constructive tension repair and gain, and economic certificates tied to the optimized restriction.

The new theorem strengthens, rather than merely renames, that connection. It translates continuation slack correctly around a nonconstant optimized comparator, includes boundary points, represents restricted equalities exactly, and gives a comparator-error-charged expansion formula. The older nonnegative-flow theorem remains unchanged under its cap-matching assumptions. Exact rational identity tests over 64 tree instances and a fully checked KKT example accompany, but do not replace, the proof.

## 12. Breadth, organization, and preservation

The main paper now begins with the accepted expansion problem and develops the continuation/transfer results before approximation. The detailed canonical inventory institution and information hierarchy move intact to the formal electronic companion. The full value-gradient, face, scalar, and validation theorems remain available; none has been discarded. Old numerical tables and execution details are moved to a clearly dated computational record within the reproducibility archive. Every essential mathematical statement and proof remains in the main/companion pair.

The package checker verifies the formal pair against the lengthy-paper page limits and verifies all 72 predecessor mathematical blocks, allowing only the documented robust theorem-to-lemma environment change. The computational record is retained for audit and historical completeness, not represented as an additional formal companion that silently relaxes the journal's page policy. The submission checklist distinguishes those destinations. Final page counts and reference checks are generated from the compiled PDFs rather than guessed from source length.

## 13. Synthetic exact-model study and information budget

The paper remains a theory/methods study with synthetic service primitives. It does not recast optimizer-generated labels as newly discovered field information. Training values and resource statistics are paid outputs of an optimization-and-audit stage. There is no claim of a new learning generalization theorem, unknown-demand identification, or universal neural efficiency. The accepted-control theorems stand independently of those empirical claims; the implementation studies measure which methods recover their value and at what recorded cost.

## 14. Specific comments

**14.1 Title.** Revised to accepted service adaptation, continuation prices, transfer coordinates, and certified gains. Neural Differential Utility remains in the implementation discussion and all associated results.

**14.2 Robust theorem label.** Relabeled as a certification lemma, with its mathematical statement and proof preserved.

**14.3 Outer tightness.** Added 768 interior models, separate true/outer comparator brackets, and a relaxation/interpolation decomposition.

**14.4 Scaling variability.** Added the larger repeated matched study and a complete retrospective median, quartile, paired-difference, and resampling-interval analysis of all 800 original scaling rows. The old eight-context limitation remains explicit.

**14.5 Warm-start versus predictor value.** Every new timing row separates the proposal and fallback phases. The implemented fallback starts from a fresh zero state, so it cannot be credited with predictor-induced iteration savings. Fallback avoidance, conditional fallback cost, and conditional fallback iterations are reported separately.

**14.6 Exact-label budget.** Label generation, teacher setup, exact audits, and individual fit costs are charged. Numerical optimizer labels are not called free information or exact mathematical optima.

**14.7 Comparator deployment role.** The three protocols and the fresh robust end-to-end study make the online/offline distinction explicit.

**14.8 Frozen models.** Conditionality remains prominent. Timing resampling is also conditional and descriptive; it does not supply an algorithm-level guarantee over fitting or tuning. A moving-block sensitivity calculation discloses the serial-dependence issue introduced by continuation.

**14.9 Global assumptions.** The abstract, introduction, theorem, and conclusion explicitly retain strong convexity and smooth resource coupling for the global gradient bridge. The transfer bijection and robust certification implication have their own, different assumptions.

**14.10 Reproducibility versus scientific priority.** The response distinguishes executed checks from proof, novelty, operational necessity, and the editor's decision. No checker output is labeled as journal acceptance.

## 15. Conditions for reconsideration

The main paper follows the theory-centered route: an optimized restricted comparator, continuation balance, transfer geometry, critical friction, constructive gain, and implemented economic certification. The newly proved benchmark-relative coordinates make that route mathematically explicit. A compact exact example and a strengthened repeated-query study support it. All neural and earlier theoretical material is preserved with clear placement rather than deleted or used to assert an advantage unsupported by measurements.

We also performed the requested learning-side accounting even though the paper no longer relies on a neural-centered identity: lifted-continuation break-even analysis, larger paired timing samples, phase-resolved fallback, online comparator charges, explicit optimizer-label costs, and measured robust outer-bound conservatism. We have not substituted an uncalibrated synthetic cube for field validation.

## 16. Editorial recommendation

We address the report through a substantially reorganized and strengthened manuscript, not a promise to revise later. The reviewed paper, the full response, preserved derivations, new theorem, completed numerical records, compiled manuscripts, and independent final-commit checks are supplied for renewed assessment. We do not presume the editor's or referee's eventual recommendation.
