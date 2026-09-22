# Response to the Operations Research referee — R19

## Reviewed source and revision identity

This response addresses the complete report `reviews/operation_research_referee_report_r14_2026-09-22.md`, which reviews R14 at `f34badb1acecd7eaebbb483b32688c77568f88a1`. At the start of this revision, the branch named `review/operation-research-r16-harsh-20260922` pointed to the R16 research-results commit `a3ddde9d80ef5c390dbb019d13bb719ddc22e1ef`, not to a new R16 report. The latest R18 branch, `d23de668070fc29a7073a9e4ef647c8159b0d580`, added an analysis plan but still had the R14 root manuscript. R17 contained only a partial transport object. We do not invent intervening reports or present those source-staging commits as completed manuscript revisions.

R19 takes the integrated route requested in the report. It extends the nonoracular learning theorem to the accepted multistage polyhedron, retains all earlier scientific documents and adverse observations, incorporates the full R16 repeated study, executes the missing accuracy-targeted comparison, and publishes ordinary complete TeX and compiled main/companion PDFs. The current paper is **Neural Differential Utility: Accepted Multistage Service Control and Certified Value-Gradient Decisions**. “Value-gradient” names the decision statistic and its guarantee, not a claim that gradient labels or neural parameterization always dominate.

## 1. Improvements already achieved in R14

We preserve the scalar theorem, positive switching costs, held-out validation, and adverse results. Its complete theorem, proof, experiment, timings, and scaling study now appear in the current companion. Exact predecessor PDFs and sources remain available separately. The new theorem does not invalidate the scalar result or silently replace its observations.

## 2. The positive subclass was exceptionally easy

The new **Global resource-price and value-gradient bridge** applies to a compact accepted polyhedron with vector decisions, several capacities, arbitrary equality restrictions, signed tariff coefficients, nonconstant comparators, and endogenous absolute switching signs. A strongly convex base resource function includes the unchanged switching term; a separate smooth convex resource coupling need not be rank one or quadratic. A specified linear resource-reward perturbation identifies the relevant partial gradient of a scalar value. The proof gives an exact two-Bregman-remainder identity and a global quadratic price-error bound, with no optimal face supplied at deployment.

The response still solves a constrained, potentially expensive base problem. The manuscript explicitly charges that computation rather than replacing one oracle with another. Low resource rank is optional for the theorem, and its usefulness for cost is empirical, not assumed.

## 3. Classical algorithms dominated the original complete pipeline

The old cost evidence remains. We also found that the R16 timing protocol retained numerical tolerance 1e-9 even for the coarse deployment target. We therefore execute the already recorded `MATCHED_COST_PLAN.json`: both classical and surrogate responses first use 1e-5 numerical tolerance, then the same independent full-objective audit decides whether a 1e-9 refinement is required. Cold and previous-context classical baselines and all seven frozen surrogate methods are included. Separate previous-context workspaces prevent a second target tolerance from receiving a within-context warm start. Every prediction, response, repair, audit, and actual refinement is charged.

The new complete timing table is generated from all 4,608 follow-up pipelines. It replaces neither the original measurements nor the quality study. The results distinguish a coarse-target direct-price interpolation advantage from strict-target classical advantages; they do not claim a neural speed advantage.

## 4. Missing non-neural and direct-statistic comparators

The current primary table includes value-only tanh, derivative-supervised tanh, direct-price tanh, value-only quadratic, derivative-supervised quadratic, direct-price quadratic, and cubic radial-basis direct-price interpolation. They receive the same training contexts, exact-solver label source, response map, and audit. The additional star study includes a cubic value baseline as well. All fitted coefficients and all deployment rows are retained.

The direct-price and non-neural methods are stronger than the neural critics on the current primitive. This finding is reported explicitly rather than omitted to protect the title.

## 5. The value-gradient claim was unresolved

The old R14 paired interval remains unresolved and is not overwritten. In the separate R16 multistage experiment, the mean regret upper bound is 0.034374346 for value-only tanh and 0.003684621 for derivative-supervised tanh. The eight-pair mean difference has the approximate Student interval [-0.041582698, -0.019796753]. The unit is an independent training/deployment pair. This supports improvement of that specified neural fitting procedure on that distribution, not universal gradient-supervision superiority. Direct-price tanh, quadratic direct-price, and RBF direct-price are better still.

## 6. Frozen-policy gain does not establish learning necessity

We agree with the inferential distinction and make the deployed object explicit. The original simultaneous bounds for each of 56 policies remain zero. A new proposition instead certifies a policy that independently chooses uniformly among eight frozen models for each new context. Conditional on those models, the 2,048 independent context observations target exactly that uniform fleet's expected gain. A simultaneous bound over seven methods uses the unchanged analytical range 25. It is not a guarantee for each model, a selected best model, or a population of new training runs. The paper does not use this gain statement as evidence that a neural network is necessary.

## 7. Difficult geometry was insufficiently represented

The primary distribution's limitations are stated. We explicitly report that the original R16 structural suite had no binding extra capacities. The new 64-instance suite has four declared strata: heterogeneous controls, binding root cross-service capacities, tier boundaries, and switching kinks. Each targeted stratum must exhibit its specified event in every case. Four primitive seeds and four contexts per stratum cover 15- and 31-node trees with two services and two/four resources. Every reference and implemented response is rationally replayed. The general inexact-response inequality is checked against independent reference brackets, and SLSQP independently checks one binding-capacity optimum from the outside initialization.

The retained star data are stratified by critical-friction distance, capacity binding, active and saturated leaves, nearest breakpoint, and optimal gain. The all-binding capacity stratum is correctly attributed to the response solver: every method is adjusted and attains the same value to numerical precision.

## 8. The nonoracular theorem did not reach the general theory

The new theorem directly retains the accepted polyhedron of the general balance theory. It neither divides by tariffs nor fixes the switching signs. The separate **Auditable inexact-response bound** applies to the actual feasible repaired decision with an independently bounded base-subproblem error. The bound also permits nonquadratic smooth convex coupling through lower curvature and an observable resource-price residual. Sixty-four exact rational quartic examples verify the decomposition and inexact bound, including box and switching boundaries. The general written proof—not these finite checks—establishes its scope.

The quadratic error estimate requires stated strong convexity; the earlier balance theory does not. We state that distinction instead of implying a condition-free quadratic bound.

## 9. Separation from classical literature

The introduction and proofs credit convex subdifferentials, conjugate duality, envelope sensitivity, generalized-lasso/total-variation methods, resource allocation, and parametric quadratic programming. We do not claim to invent those ingredients, scalar water filling, or gradient descent. The specific integration is: full continuation feasibility and switching remain in the response; a specified reward perturbation identifies its resource statistic as a scalar value gradient; an exact decomposition controls nonoracular decision regret; and a separately certified inexact-response error accounts for implemented rounding and repair. The continuation-transfer cone and two-pass tension repair remain the service-specific algorithmic structure.

## 10. Operational significance of engineered primitives

The new multistage primitive has heterogeneous nonconstant outside tiers, six resources, four extra capacity rows, and unknown switching signs. It is not the centered diagonal star. We also distinguish its **announced feasible outside protocol** from the reoptimized static benchmarks in the canonical and centered studies. The canonical accepted information hierarchy, customer-preserving improvement, stock identification, and continuation-exit calculations remain in the main paper in full.

No empirical service-provider calibration is claimed. Synthetic heterogeneity and a mathematically general theorem cannot establish field performance; this limitation is stated rather than disguised by a currency conversion.

## 11. Training uncertainty and context uncertainty

The primary comparison uses all eight independently trained models and their independently generated deployment cohorts. The paired interval uses eight—not 2,048—replications. The finite-sample fleet theorem conditions on all fitted models and uses the explicitly randomized finite fleet as its target. The original individual-policy bounds and their vacuity remain visible. We do not infer an unconditional finite-sample guarantee for the training procedure from the conditional fleet result.

## 12. “Prospective” provenance

The current manuscript describes R14 validation as held-out internal validation and the R16 protocol as a frozen, internally recorded, amended execution. The iteration-ceiling amendment followed an R15 solver failure; the complete unchanged-seed study was then rerun. The R19 fleet calculation is retrospective. New geometry checks are developmental theorem tests, and the accuracy-targeted timing is a follow-up execution of an existing plan. None is relabeled as external preregistration or untouched prospective model selection. Historical source wording is retained as history, not adopted as a new provenance claim.

## 13. Complete certification and offline costs

The paper distinguishes unrefined quality, immediate full-gap pass rate, and total certified deployment. All methods use the same exact-gap targets. The follow-up supplies component times, mean/median/p95, actual fallback rates, eight-cohort descriptive intervals, and same-host offline label and fitting costs. A finite break-even count appears only with a positive observed total online saving. An approximate prediction alone is not counted as a completed certified decision.

## 14. Breadth was not multistage depth

The primary coupled study now has six review levels, 63 nodes, two service coordinates, and six resource factors. The structural checks retain 15/31/63/127-node predecessors and add deliberate 15/31-node boundary tests. The star breadth scaling remains explicitly a two-review resource-allocation experiment, not evidence for deep-tree learning.

## 15. Manuscript coherence and preservation

The current narrative follows acceptance, structural comparative statics, a learnable resource statistic, implemented-decision certification, and complete deployment evidence. The canonical information hierarchy and general tree results remain in the main manuscript. Complete scalar and verified-cell components are in the current companion. Earlier continuous-time/diffusion and nonlinear investigations remain in exact predecessor documents and the unchanged historical supplement. `PRESERVATION_MAP.md` records the locations. No old revision directory, report, policy row, or unfavorable result is deleted or overwritten.

## 16. Status attached to the actual reviewed commit

The publication workflow produces complete source and compiled PDFs, commits the finished package to the new branch only, checks out that exact final SHA, verifies its committed manifest and package, and posts the validation status against that SHA. The result is not inferred from a successful check on an earlier staging commit. No claim of an external GitHub check is made before the actual final-SHA result exists.

## 17. Specific technical requests

**17.1 Price interpretation.** The learned price is the marginal smooth resource cost. Participation and hard-capacity multipliers remain inside the constrained response. The scalar coupling marginal is not the capacity-inclusive leaf price.

**17.2 Three certificate objects.** Response-subproblem error, analytical regret, and the independent full-objective gap are separately defined; expected gain is a fourth, statistical object. The inexact-response error uses raw implemented gain before the outside gate.

**17.3 Stratification.** Every requested geometric dimension is included in `results/reanalysis.json`, with exhaustive descriptive bins and all underlying rows preserved.

**17.4 Direct price.** Tanh, quadratic, and radial-basis direct-price methods are included with common training inputs and audit requirements.

**17.5 Non-neural alternatives.** Quadratic value/value-gradient/price and RBF price methods appear in the primary table, not only in an omitted auxiliary exercise.

**17.6 Gate scope.** The gate certifies gain relative to a known feasible comparator under the specified model. It is not robustness to misspecification, demand shift, tariff error, or implementation outside the audited polyhedron.

## 18–19. Integrated route and editorial assessment

R19 takes the integrated route by materially extending the decision theorem and executing stronger multistage comparisons, rather than deleting the general theory or asserting that incremental staging resolves the report. It preserves the original claim of accepted adaptive service control and expands the mathematical bridge beyond the star. The manuscript nevertheless distinguishes what its evidence establishes: derivative supervision improves one paired neural comparison, non-neural direct-price methods can be stronger, computational benefit depends on the certificate target, and field calibration is not supplied. Whether this integrated contribution meets the journal's novelty and significance threshold remains an editorial assessment, not a conclusion that a repository check can certify.
