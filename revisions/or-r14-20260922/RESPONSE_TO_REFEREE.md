# Response to the Operations Research R12 referee report

**Manuscript:** Neural Differential Utility: Accepted Adaptive Service Control and Certified Value-Gradient Learning  
**Revision:** R14, September 22, 2026  
**New branch:** `revision/ndu-operations-research-r14-20260922`  
**Latest review:** `reviews/operation_research_referee_report_r12_2026-09-22.md`, review commit `5b1a62679f890006d8f6a234160fa9a02dcdbc5a`  
**Scientific predecessor:** completed R13 revision, `808b8f0353051581134d3b8b5a7424422d4e48a8`.

There is no intervening R13 referee report in the repository at the time this revision was prepared. We therefore distinguish repairs already present in R13 from the additional R14 results. The new manuscript retains the integrated title, the general vector/boundary/nonconstant-comparator theory, the canonical inventory results, and all adverse experiments. It responds to the report's learning-centered route by deriving and implementing a nonoracular learning guarantee rather than changing the title to avoid that burden.

The principal new material is **Section 7, Proposition 7.1 and Theorem 7.2**, with its executed study in **Section 9**. The two-review accepted-control geometry identifies a scalar coupling price. A derivative of a scalar neural value critic supplies that price, and a feasible price response has a global quadratic regret bound even across changes in binding constraints. This alternative needs no enumerated face library or optimal query-time multipliers. A separate observable residual and a rational Fenchel certificate make the guarantee usable numerically. Essential proofs are in the main manuscript, not delegated to an archival supplement.

## 1. Preserve the substantive repairs recognized in the report

We agree that broadening the full-tree theorem was a substantive repair. The R12 general balance and network statements remain in main Sections 3 and 4: arbitrary feasible comparators, signed coefficients, vector tiers, boundaries, equality and inequality commitments, smooth coupling, and absolute switching. The two-pass constructive transfer and tension-repair results from R13 remain in Section 4.5 onward. Their hypotheses and qualifications have not been weakened or silently replaced by the simpler star specialization.

The earlier scalar edge theorem is reproduced intact in EC Section EC.12, because the full-tree characterization now subsumes its role in the main exposition. This is a relocation, not deletion; its original source is unchanged and cross-document references resolve. All R13 root documents have exact predecessor snapshots.

## 2. Consequences beyond a reformulated KKT condition

The report correctly identifies normal cones, subgradients, and incidence elimination as classical. We continue to credit those tools. R13 supplied a constructive two-pass dual repair and sparse factorization. R14 adds a different, explicit algorithmic consequence in Proposition 7.1.

For a root and mutually exclusive continuation leaves, acceptance permits only nonnegative leaf-to-root payment transfers. It fixes the sign of every installation and continuation switch, converting the absolute friction into a known linear transfer charge. The critical friction is the largest positive marginal reward-to-switching-charge ratio. It can be computed in one scan, and a coordinate attaining a positive reduced reward supplies an explicit profitable accepted deviation below the threshold. The full optimal decision is recovered from one monotone scalar balance equation; sorting its breakpoints costs O(m log m) arithmetic operations and O(m) storage.

These are not generic complexity claims for all scenario trees. The sorting procedure belongs to the classical single-resource literature, which we now cite explicitly through Patriksson and Strömberg (2015). What is specific to the paper is the accepted-service reduction, installation-inclusive friction coefficient, and identification of the scalar value derivative needed for decisions. The direct threshold was cross-checked against 160 general tension LPs, rather than only against its own implementation.

## 3. Nonzero switching integrated with decisions and learning

R13 already supplied nonzero-switching binary-tree experiments, actual fused-edge and continuation diagnostics, friction paths, and verified-cell learning. These remain unchanged in Section 8 and its data.

Every R14 learned deployment also uses strictly positive absolute friction, uniformly drawn from 0.01 through 0.20. The absolute penalty is not dropped: Proposition 7.1 derives its transfer coefficient from root installation and all continuation edges. The fact that acceptance determines its signs is a structural property of this subclass. This does not replace the genuinely fused-edge, multistage experiment. Both remain visible, with their different scopes stated explicitly.

The structural tests include a friction path below, at, and above the critical value; accepted gain disappears at the threshold and is strictly positive below it. The zero-friction control appears only in the structural path, not in the learning or confirmation distribution.

## 4. An implementable alternative to the unknown optimal face

This is the central additional response. R13's approximate-price leakage certificate and region-verified cells already removed the need to assume an unverified face. R14 goes further: the new policy does not even predict a face.

For a predicted coupling price, the algorithm clips leaf responses and, only when the root capacity would be exceeded, performs a single-resource capacity adjustment. This response is feasible for every prediction. Theorem 7.2 proves two bounds: a squared observable price-consistency residual and a squared error relative to the true coupling price. The true price is the root quadratic curvature times the root transfer; it deliberately excludes the capacity multiplier, which remains in the feasible-set normal cone.

For a specified forcing direction, the envelope derivative of the scalar value is exactly that root transfer. Consequently an arbitrary differentiable scalar critic generates a feasible policy whose regret is bounded by an explicit constant times its squared partial-derivative error. The proof uses an exact convex-remainder identity and holds through binding-capacity transitions. It does not require the correct active set, strict complementarity, or a positive distance from a switching boundary.

The observable residual does not require the unknown optimal value or policy. In finite precision, the separate Fenchel bound certifies the actual rounded policy and includes capacity-repair errors. We do not pass an approximately stationary numerical response off as an exact instance of the analytical theorem.

## 5. Independent finite-sample validation actually executed

The R13 confirmation with 4,096 independent contexts, three frozen policies, a model-derived range, and a positive gain lower bound remains in Section 8.4. R14 executes an additional, independent confirmation for direct scalar-critic policies without full-objective refinement.

The first prespecified training seed supplies two frozen critics. A different recorded seed generates 2,048 new contexts; neither model is refit. Monotonicity in the common forcing and friction, together with convexity in the remaining context coordinate, reduces the uniform optimal-gain range calculation to two corners. Those corners are bounded by exact rational conjugates. The precise range, model hash, sample size, confidence parameter, corner policies, and every deployment are committed in `results/validation.json` and `results/validation_policies.jsonl`.

A one-sided Hoeffding bound with a union bound over the two policies gives a simultaneous positive expected-gain lower bound. The selected critic has empirical normalized gain about 0.119594 and a lower bound above 0.1081 at confidence 0.95. No full-objective classical rescue is used in this confirmation. The small difference between the two critics is not claimed significant. Their empirical average certificate is reported as an empirical average, not mislabeled an expected-regret confidence bound. The concentration argument is standard; the contribution is its concrete, economically nonvacuous execution for the proposed accepted policy.

## 6. Raw neural candidates, rather than only refined outcomes

The prior negative raw actors are retained verbatim. R14 adds a distribution on which the specified value statistic can be learned directly and usefully.

Across eight paired training seeds and 128 shared independent test contexts, all 2,048 feasible proposals pass the exact nonnegative-gain gate before any full-objective refinement. Mean normalized optimum gain is about 0.122047. Mean unrefined regret is approximately 5.96e-6 for value-only fitting and 2.21e-6 for value-gradient fitting. The mean exact certificate and both analytical bounds are reported alongside those losses. The raw policy, capacity projection, price, value error, gradient error, exact gain, and exact upper bound remain available for each case.

These results demonstrate accurate unrefined proposals in the specified two-review family. They do not rehabilitate the poorly shifted R12 actors by averaging them together with an easier family. The paper expressly distinguishes these populations.

## 7. Complete timing and the role of refinement

We agree that matching final accuracy and charging all executed operations are essential. The R14 matched-accuracy test uses a normalized exact gap of 1e-7. It includes prediction, capacity-only repair, the first rational audit, an actual scalar solve when necessary, and a second audit after that solve. It compares with three structure-aware classical methods: cold safeguarded Newton, Brent, and breakpoint scanning. Small SLSQP comparisons check correctness rather than serve as the sole timing baseline.

The complete learned pipeline is slower than the structure-aware classical baseline in the recorded run. It often uses fewer full-solver iterations, but two rational audits dominate this particular implementation. This unfavorable result is reported in the main text and in EC Table 11. We do not infer a speed or amortization advantage. The independent confirmation and raw-quality table deliberately exclude the full-objective refinement, so their positive policy results cannot be attributed to classical rescue. Offline label-generation and fitting costs are also reported separately.

## 8–9. Integrated scientific identity and the title

We retain the title and address the report's substantive alternative. The accepted-control geometry is now needed to identify the sufficient learning statistic: acceptance transforms leaf decisions into transfers, determines switching signs, creates the rank-one resource interaction, and identifies the value derivative whose prediction controls regret. The same statistic drives the implemented policy and its observable certificate. That is a direct dependence between the structural and learning components, not simply a generic certification wrapper attached to an unrelated actor.

We do not claim that a neural architecture is novel or that a network must beat an exact scalar solver on a small synthetic family. The contribution is a constructive theorem connecting a scalar neural critic to feasible accepted decisions, and positive direct deployment in an independently evaluated distribution. Whether the complete combination meets the journal's novelty threshold remains an editorial judgment; we do not label that judgment mathematically closed.

## 10. Algorithmic development and scenario scale

The R13 factored LP, two-pass repair, and first-order brackets remain. R14 adds the closed-form critical friction and the finite breakpoint algorithm for the star subclass. It records measurements through 32,767 continuation leaves and compares multiple scalar solvers. The table distinguishes structural solve time from complete audit-inclusive deployment time.

The increase is in branching at a fixed two-date horizon. We make neither a deep-tree scaling claim nor a general linear-time convex-optimization claim. Arithmetic and storage complexity are distinguished from bit complexity. All raw timings and iteration counts are committed, including cases where Brent or Newton beats the sorting implementation.

## 11. Scope of sharp margin statements

The existing strong-convexity upper bound, local feasible-step lower bound, and exact quadratic formula keep their original hypotheses. They are not promoted to universal boundary equalities. The new residual bound is proved with the exact diagonal-plus-rank-one Hessian in the stated subclass; the global derivative bound is an inequality, not a claim of exact regret equality. Capacity-binding cases are explicitly included in the proof and in 106 of the arbitrary-price tests.

## 12–13. Institution, units, and standard stochastic control

The paper continues to describe an observable, externally priced, synthetic service institution. It does not claim private-information incentive compatibility, field calibration, online partial-information control, or an escape from the Markov/scenario-tree framework.

The revised opening model now explicitly distinguishes the canonical ex ante master agreement from the later continuation-exit institution. The scalar-critic companion reconstructs the full node reward gradients and verifies that their sum is zero, so the common outside tier is reoptimized. It explains how convex resource increments and a harmless common level shift recover nonnegative gross costs. The star study is the identified-stock quadratic-resource specialization, not an assertion that every inventory model is quadratic. Profit is normalized by the exact discounted review mass 1.9, and derivative errors use the specified unnormalized value and forcing units.

## 14. Statistical evidence and training variability

R14 adds eight independent training seeds with paired examples and features. A plan file fixes the training size, architecture, loss weight, ridge coefficient, test size, seeds, tolerance, and timing comparators before fitting. This is not presented as external preregistration. The primary inferential unit is the training seed, not each correlated context reused across fits.

The paired regret difference has a 95% Student interval that includes zero. The manuscript says so. The derivative-weighted numerical mean is lower, but neither this small-seed approximation nor secondary endpoints are used to claim a universally superior training loss. The separate bounded-variable confirmation is a different result with different assumptions and an explicit finite-sample confidence statement. It does not rely on a Gaussian approximation.

## 15. Specific requests

| Report item | Location and action |
|---|---|
| 15.1 Instantiate selection | Main Sections 8.4 and 9.2; exact range, M, n, delta, model hash, raw confirmation policies. |
| 15.2 Nonzero switching | Preserved multistage paths and new strictly positive-friction critic distribution; Section 7 derives, rather than suppresses, the switching charge. |
| 15.3 Face diagnostics | All R13 masks, switching signs, acceptance leakage, membership failures, and refinement records remain. The new method needs no face prediction; it instead reports price error, residual, root-capacity projection, and policy certificates. |
| 15.4 Separate candidate/refinement | Main Table 6 is unrefined; EC Table 11 includes all actual refinement and audits. Independent confirmation uses no full-objective rescue. |
| 15.5 Four inherited seeds | No claim that the old four seeds are representative. They remain a historical transfer diagnostic; the new eight paired seeds are analyzed separately. |
| 15.6 Friction algorithm | Proposition 7.1, general-LP cross-checks, explicit improving witness, breakpoint solver, and scaling through 32,767 leaves. |
| 15.7 Literature positioning | Graph total variation, parametric QP, safe screening, and now classical single-resource algorithms are explicitly credited. |
| 15.8 Correct certification object | Distinguish analytical regret inequalities, exact rational policy gaps, empirical statistics, and finite-sample expected-gain bounds. Wall-clock timings and optimizer success flags are not certificates. |
| 15.9 Operational units | Main Sections 8.1 and 9.1 and EC.13 give the currency-free normalization and primitive mapping. |
| 15.10 Historical burden | New essential proofs are in main Section 7. The historical supplement is archival, with exact predecessor PDFs and a relocation map. |

## 16–17. The proposed routes to resubmission

We follow the report's integrated-learning route rather than remove the learning material. Theorem 7.2 is a nonoracular global value-gradient-to-decision result, and the independent confirmation shows useful positive gain from direct neural proposals without full-objective refinement. The new theorem does not require an optimal exposed face. The full theory, approximate-price certificate, verified-cell approach, old experiments, and new direct-price approach are retained with explicit assumptions.

We do not claim all possible suggested advantages simultaneously. In particular, complete latency remains unfavorable, and the derivative-supervision difference is unresolved. These are visible findings, not missing rows to be hidden. The revision's affirmative case rests on the new constructive theorem and accepted direct deployment, not on an unsupported universal advantage.

## 18–19. Reproducibility and overall assessment

The independent standard-library verifier replays 6,626 rational certificates and 2,577,514 exact algebraic checks. Structural tests include 480 solver agreements, 128 SLSQP comparisons, 160 general tension LP comparisons, and 800 arbitrary-price bound checks. Ordinary TeX and Python sources, data, frozen coefficients, logs, generated tables, requirements, source hashes, and the reviewer response are included. The workflow rebuilds the actual PDFs and publishes only to the new R14 branch.

Preservation checks confirm 763 predecessor files remain byte-identical and seven replaced root documents have exact snapshots. The main PDF has 43 total pages, including three reference pages, placing it at 40 pages excluding references in the lengthy-manuscript category. The current companion has 38 pages. The manuscript uses 11-point text, 1.5 spacing, one-inch margins, an anonymous title page, a 184-word text-only abstract, an equation-free introduction, and deferred main-paper tables. The optional earlier scalar proof is relocated intact; no adverse numerical evidence is removed.

We submit this revision for renewed assessment of its mathematical, computational, and operational contributions. The response documents what has been established, what has been executed, and what remains a comparative or editorial question; it does not substitute reproducibility for scientific novelty or imply acceptance in advance.
