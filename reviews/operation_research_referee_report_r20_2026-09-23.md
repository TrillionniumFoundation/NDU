# Confidential Referee Report for Operations Research

**Manuscript:** *Neural Differential Utility: Accepted Multistage Service Control and Certified Value-Gradient Decisions*  
**Review date:** September 23, 2026  
**Repository:** TrillionniumFoundation/NDU  
**Reviewed branch tip:** review source branch **revision/ndu-operations-research-r20-20260923**, SHA **45553b28f40c92a14895b8b82d8739e608f6d4b1**  
**Latest complete manuscript on that tip:** R19, source/publication commit **cb4f8644652ebe92f0aac5294baaff898d97f5cf**  
**Prior complete referee report considered:** **reviews/operation_research_referee_report_r14_2026-09-22.md**

**Recommendation:** **Reject in the present form. I would encourage a substantially refocused new submission, not another incremental revision of the current integrated manuscript.**

## Executive assessment

This is a materially stronger paper than the R14 manuscript. The authors have taken the previous report seriously. In particular, the new resource-price theorem is no longer confined to a two-date scalar star; the current main theorem allows a general compact accepted polyhedron, vector decisions, several resource coordinates, nonconstant outside protocols, hard inequalities and equalities, and endogenous nonsmooth switching signs. The paper also adds an explicit inexact-response bound for the actually implemented feasible decision. Empirically, the revision now includes the missing direct-price and non-neural comparators, eight independent training/deployment pairs, deliberate boundary and capacity checks, exact rational replay, and a matched-accuracy timing experiment that charges prediction, response, repair, audit, and actual fallback. These are real improvements, not cosmetic edits.

I also do **not** currently see an obvious fatal algebraic error in the two new R19 core results, Theorem “Global resource-price and value-gradient bridge” and Theorem “Auditable inexact-response bound,” under their stated strong-convexity and smoothness assumptions. The Bregman identity, the response Lipschitz estimate, the quadratic price-error bound, and the convex-combination argument used to charge an inexact response are internally coherent. The reproducibility package remains unusually transparent, including adverse results.

The central editorial problem has nevertheless become sharper rather than disappearing. The paper now contains evidence that its best implementation is **not neural**. The radial-basis direct-price method has the smallest reported unrefined regret upper bound and the highest immediate certificate pass rate. It is also the only surrogate in the matched-cost table that is faster than the lower-mean classical baseline at the coarse (10^{-3}) target. At (10^{-5}), every surrogate falls back on every timed case, while the classical baselines are faster. The neural value-gradient pipeline therefore does not provide the computational advantage that could justify making “Neural Differential Utility” the organizing scientific claim.

At the same time, the new general value-gradient theorem is, in my reading, a clean and useful synthesis of familiar convex-analytic ingredients—envelope/Danskin sensitivity, strong-convexity stability of argmin maps, Fenchel/Bregman decomposition, and residual certification—specialized to this accepted-control architecture. The manuscript itself acknowledges that these ingredients are standard. For Operations Research, the revision still does not establish a sufficiently sharp methodological separation from parametric convex optimization, differentiable optimization, predict-then-optimize, or learning of optimizer statistics/dual variables. This is especially problematic because several directly relevant learning-and-optimization literatures are absent from the current discussion.

My recommendation is therefore based primarily on **scientific positioning, novelty, and necessity**, not on a detected mathematical contradiction. I would not ask the authors to add yet another layer of experiments to the present 35-page main paper plus a 35-page companion. I think the work needs a decisive choice of paper.

# 1. Review-object and provenance issue: “R20” is not yet a completed manuscript revision

The branch named **revision/ndu-operations-research-r20-20260923** does not currently contain a completed R20 manuscript. Its tip adds only **revisions/or-r20-20260923/REVISION_PLAN.json** on top of the complete R19 publication commit. Root **main.tex**, **main.pdf**, **electronic_companion.tex**, **electronic_companion.pdf**, **README.md**, and the submission checklist remain the R19 artifacts. The title page explicitly says “Revision R19,” and the README describes the R19 package.

The R20 plan proposes a certificate-price-polishing algorithm, a new replay, and a new 4,608-record original-versus-polished timing study. None of those planned R20 results is present at the reviewed branch tip. They therefore cannot be counted as evidence in this report.

For completeness, the complete R19 publication commit does have a successful status context **ndu-or-r19/final-sha**. The R20 plan-only tip has no analogous final-manuscript status, which is appropriate because there is not yet a completed R20 manuscript to validate.

This is not itself a reason to reject the science. It is important because the editor should not interpret the branch name as evidence that the certificate-polishing proposal has already solved the runtime or dual-slack concerns discussed below.

# 2. What R19 genuinely fixes from the previous report

Several changes deserve explicit credit.

First, the positive theorem is no longer restricted to the centered scalar star. The new formulation keeps the full accepted polyhedron in the response problem and allows vector tiers, multiple capacities, equality restrictions, signed coefficients, nonconstant outside protocols, and endogenous absolute-value switching signs. This directly addresses one of the most serious R14 scope objections.

Second, the paper now distinguishes four objects that were previously too easy to conflate: response-subproblem error, analytical regret, the independent full-objective certificate, and a statistical expected-gain statement. The inexact-response theorem charges the actual feasible repaired output rather than an idealized floating-point proposal.

Third, the missing baseline problem is partly corrected. The current experiment includes direct-price tanh regression, direct-price quadratic regression, and cubic RBF direct-price interpolation, in addition to value-only and derivative-supervised critics. This is exactly the sort of comparison that was required.

Fourth, the authors do not hide the outcome. Direct-price and non-neural methods are stronger. The manuscript says so explicitly.

Fifth, the current multistage experiment is materially harder than the old star experiment. It has 63 tree nodes, two service coordinates per node, six coupled resource coordinates, four additional cross-service capacities, a heterogeneous outside protocol, continuation constraints, root equalities, and endogenous switching signs. The deliberate geometry suite also forces actual capacity binding, tier boundaries, and switching kinks instead of labeling generic samples as stress cases.

Sixth, the matched-cost experiment corrects the earlier unfair fixed (10^{-9}) initial-solve comparison. Classical and surrogate response solvers now start at the same (10^{-5}) numerical tolerance and must meet the same independent final certificate.

These changes are substantial. My negative recommendation is not a claim that R19 failed to respond to R14.

# 3. The new evidence undermines the neural-centered scientific framing

The most important R19 table is, in my view, Table “Unrefined multistage decisions and conditional frozen-fleet gains.”

The reported mean regret upper bounds are approximately:

- Tanh value: **0.034374**
- Tanh value + gradient: **0.003685**
- Tanh direct price: **0.001581**
- Quadratic value: **0.003079**
- Quadratic value + gradient: **0.002794**
- Quadratic direct price: **0.000271**
- RBF direct price: **0.000158**

The (10^{-3}) immediate certificate pass rates move in the same direction: **0.00%**, **0.54%**, **3.66%**, **4.59%**, **9.47%**, **65.48%**, and **86.43%**, respectively.

This is an informative result, but it does not support a neural-critic-centered paper. The strongest method is a simple non-neural direct-statistic interpolator. Even the direct-price tanh method outperforms the value-gradient tanh critic. Thus the evidence says that the operational statistic is useful, but learning a scalar neural value and differentiating it is not the preferred implementation.

The matched-cost table makes the issue more severe. At the (10^{-3}) target, the lower-mean classical baseline is about **13.453 ms**, while the methods are approximately:

- Tanh value: **43.712 ms**
- Tanh value + gradient: **42.169 ms**
- Tanh direct price: **41.519 ms**
- Quadratic value: **40.264 ms**
- Quadratic value + gradient: **39.654 ms**
- Quadratic direct price: **19.790 ms**
- RBF direct price: **9.563 ms**

Only RBF direct price is faster than the best observed classical mean. The neural methods are not close. Their fallback rates are between **98.44% and 100%**.

At the stricter (10^{-5}) target, **every surrogate method falls back in 100% of the timed cases**. The lower classical mean is about **26.180 ms**, versus roughly **37.808–43.532 ms** for the surrogates.

This is not a minor benchmarking detail. It changes what the paper is about. The current evidence supports something like:

> Learn or approximate a low-dimensional resource statistic when a coarse certificate is operationally sufficient; simple direct non-neural approximation can be effective.

It does **not** support the stronger scientific identity implied by “Neural Differential Utility,” nor does it show that a neural value-gradient method is required for the accepted-control problem.

If the authors retain the current empirical truth, which they should, the title, abstract, introduction, and contribution hierarchy need to stop making the neural critic the conceptual center.

# 4. The derivative-supervision result is valid but scientifically weaker than the presentation suggests

The paper reports a paired eight-training/deployment comparison in which derivative supervision improves the tanh critic, with an approximate Student interval for the mean difference of about ([-0.04158,-0.01980]). This is useful evidence that, for the chosen random-feature model and distribution, adding derivative labels improves decisions.

But the result has three limitations.

First, the derivative labels come from the same exact optimization pipeline that produces the training labels. This is not a setting in which derivative information arrives cheaply from nature while function values are expensive. The experiment gives the learner extra exact optimizer information, and the stronger result should therefore be interpreted as a supervised representation comparison, not as evidence that “differential utility” creates information unavailable to a direct learner.

Second, direct-price learning is stronger. Once the paper trains the six-dimensional target statistic directly, the value-gradient detour is not the best way to obtain the operational quantity.

Third, the neural model is a fixed-random-feature tanh basis with a ridge readout, not a fully trained deep architecture. That is perfectly legitimate computationally, but it further weakens the case for a neural contribution at a top OR journal.

I would keep the paired result in a revised paper, but I would not make it a headline contribution.

# 5. The R19 bridge appears to be a specialization/synthesis of standard convex sensitivity machinery; the novelty boundary is still not sharp enough

Theorem “Global resource-price and value-gradient bridge” is elegant. It is also close in structure to what one obtains by combining standard results:

1. strong convexity gives uniqueness and Lipschitz stability of the optimizer/response;
2. Danskin/envelope sensitivity gives grad_h J = Ux*;
3. the smooth coupling price is eta* = grad Psi(Ux*);
4. the response at (eta^*) recovers (x^*);
5. Bregman/Fenchel algebra decomposes suboptimality;
6. Lipschitz gradients convert the decomposition to a quadratic residual bound.

The application-specific value is that the accepted polyhedron and nonsmooth switching remain inside the response and therefore do not require an optimal-face oracle. That is useful. But the paper needs to explain why this is a new OR theorem rather than a well-executed application of standard parametric convex optimization and conjugate sensitivity.

The current related-literature section does not do enough work on this point. It cites classical convex analysis, approximate dynamic programming, generalized lasso/TV, and multiparametric QP, but it does not engage the literatures closest to the *learning-to-optimize* claim.

A top-journal paper cannot rely on “the ingredients are standard but their integration is new” without showing precisely which existing result fails to deliver the claimed bridge, and which new consequence is unlocked by the accepted-control structure.

I would ask for a theorem-by-theorem comparison table in any resubmission:

- existing result / reference;
- assumptions in the existing result;
- what it already implies for this model;
- what the present theorem adds;
- whether that addition is mathematical, algorithmic, statistical, or application-specific.

Without that separation, the novelty case is too diffuse.

# 6. The related literature omits directly relevant learning-and-optimization work

I consider this a major issue, not a cosmetic citation request.

The present main manuscript does not appear to discuss **Smart “Predict, then Optimize”** by Elmachtoub and Grigas (Management Science 68(1):9–26), which explicitly studies prediction models through downstream optimization loss. Nor does it discuss **From Predictive to Prescriptive Analytics** by Bertsimas and Kallus (Management Science 66(3):1025–1044), which is foundational OR work on learning decisions from data.

For differentiable optimization, the paper should confront at least **Amos and Kolter (2017), “OptNet: Differentiable Optimization as a Layer in Neural Networks,” ICML/PMLR 70:136–145**, which explicitly combines constrained quadratic optimization, sensitivity analysis, and learning.

Most directly, **Kraul, Seizinger, and Brunner (2023), “Machine Learning–Supported Prediction of Dual Variables for the Cutting Stock Problem with an Application in Stabilized Column Generation,” INFORMS Journal on Computing 35(3):692–709**, predicts optimal dual variables and uses them to improve an optimization algorithm. That paper is extremely relevant to the present claim that a learned low-dimensional price/dual-like statistic can accelerate repeated optimization.

These papers do not automatically invalidate the present contribution. They do mean that the current novelty discussion is incomplete. In particular, once R19 shows that direct-price prediction is the strongest approach, prior work on learning duals or optimizer-relevant statistics becomes central, not peripheral.

A resubmission should also compare with modern learning-augmented warm-start and parametric-optimization methods, not only with generic “machine learning for control” references.

# 7. The “value gradient” is created by a deliberately chosen reward perturbation; this must be positioned carefully

The theorem defines a context perturbation (h) through the linear term U^T h, and then obtains
**grad_h J = Ux*.**
This is correct and useful, but the identity is an envelope result for a deliberately chosen coordinate system. The reader should not be left with the impression that an arbitrary scalar value function naturally reveals every operational resource price.

The statistical problem is therefore not “discover a hidden gradient of value” in the abstract. It is closer to:

> choose a reward coordinate whose derivative equals a desired resource statistic, then learn the scalar value well enough in derivative to recover that statistic.

That can still be a worthwhile construction. But the scientific burden is then to show when learning the scalar value is preferable to learning the statistic directly. R19's own results currently answer that question in the negative.

This point is especially important because the direct-price methods receive the same exact-solver-generated training population and are much stronger.

# 8. The classical baseline remains too weak for an algorithmic acceleration claim

The matched-cost experiment is much fairer than before, but it still does not establish an algorithmic advantage against the strongest relevant classical alternatives.

The current baselines are essentially cold and previous-context versions of the paper's classical solver stack, with common numerical tolerances and cached problem structure. That is useful, but the model is a repeated, highly structured convex optimization problem with:

- fixed constraint matrices over many contexts,
- only a low-dimensional changing resource-reward vector plus friction,
- strong convexity,
- warm-start opportunities,
- dual/price continuity,
- and, in special cases, explicit transfer coordinates.

This is precisely where one should expect specialized parametric QP, active-set continuation, sensitivity-based warm starts, cached factorization, or learned/classical dual warm-start methods to perform well.

The paper itself derives continuation-flow coordinates and price structure but does not convincingly benchmark the strongest structure-aware solver implied by its own theory against the surrogates. The R20 plan to “polish” resource and equality prices is effectively an admission that substantial certificate-side classical improvement may remain.

Before claiming computational value from learning, the authors should benchmark against a carefully engineered price/dual continuation method that uses the same low-dimensional structure but does not learn a statistical surrogate.

# 9. The fixed 63-node study is not enough to establish scalable computational relevance

The new multistage experiment is more structurally realistic than the old star, but it is still one fixed synthetic problem size: 63 nodes and 126 tier variables, with six resource factors.

The exact classical method solves a coarse certified query in roughly 13–14 ms and a strict query in roughly 26 ms on the reported host. That is already very cheap.

An Operations Research reader needs to know how the tradeoff changes with:

- tree depth and node count;
- number of service coordinates;
- number of continuation constraints;
- number of coupled resources;
- number of extra capacities;
- condition number / curvature;
- fraction of active box and capacity constraints;
- proximity to switching and active-set transitions.

The old star scaling experiment cannot substitute for scaling of the new general polyhedral response, because the central R19 contribution was precisely to leave the easy star.

Without a scaling study on the *new* general class, the current timing result is a benchmark anecdote rather than an algorithmic contribution.

# 10. The heterogeneous experiment's outside protocol is not an economically compelling comparator

The manuscript correctly discloses that the heterogeneous multistage study uses a specified feasible, node-dependent outside protocol and **does not prove that this protocol is the reoptimized best static or otherwise optimal restricted comparator**.

That disclosure is good. It also limits the meaning of the positive gain numbers.

The conditional frozen-fleet lower bounds are all around (0.54)–(0.58), while mean gains are around (1.4). But a positive gain relative to an arbitrary feasible outside protocol may say more about the weakness of the outside protocol than about the quality of the learned policy.

For algorithmic evaluation, regret relative to the exact optimum is the more informative quantity, and on that measure direct-price/non-neural methods dominate the neural critics.

For economic evaluation, the comparator should be a meaningful restricted policy class—e.g., a reoptimized static contract, a reoptimized time-only policy, or another institutionally defensible benchmark. The earlier canonical sections do exactly this. The current multistage learning experiment does not.

I would not use the current frozen-fleet gain theorem as headline evidence for operational value until the comparator has a stronger economic interpretation.

# 11. The frozen-fleet guarantee is mathematically legitimate but operationally artificial

The paper is commendably explicit that simultaneous confidence bounds for each of the 56 individual frozen policies are all zero. It then constructs a different deployable object: on each new context, independently draw one of the eight frozen policies uniformly and execute it.

Conditional on the frozen policies and the stated sampling assumptions, the Hoeffding/union-bound calculation is straightforward. My concern is not the algebra. It is the target.

Most practitioners would deploy one validated model, a deterministic ensemble, or a selected model with a separate holdout—not randomly choose one of eight independently trained models for every query merely to make the finite-sample target equal to the pooled mean.

The positive fleet bound therefore feels like a statistical workaround for the inability to certify any single training run, rather than evidence that the training procedure is reliable.

A stronger learning paper would do one of the following:

1. reserve a genuinely independent final validation set and certify a predeclared selected/ensembled policy;
2. give a hierarchical or algorithm-level generalization statement that includes training randomness;
3. demonstrate stability across substantially more independent training runs;
4. make the randomized fleet itself operationally motivated rather than statistically convenient.

The present theorem should be retained as a precise conditional statement if desired, but it should not carry much editorial weight.

# 12. The experiment remains an exact-model surrogate study, not a data-driven operations study

All operational primitives are synthetic. The feasible set, objective, transition structure, and acceptance constraints are known. Training labels come from the exact optimization model. Train and deployment contexts come from the same declared synthetic generator. The paper does not study model misspecification, distribution shift, unknown demand law, noisy resource coefficients, or field calibration.

The manuscript is transparent about these limitations. Transparency is necessary, but it does not make the missing operational validation irrelevant.

This matters because the strongest justification for learning would normally arise when some component of the environment must itself be estimated or when repeated exact optimization is genuinely expensive. Here the exact model is known and exact optimization is measured in tens of milliseconds.

Consequently, the learning component currently looks like surrogate regression for a known parametric convex program. That can be useful, but it raises the bar for methodological novelty and scale.

# 13. “General accepted polyhedra” should not be conflated with general accepted objectives

The R19 bridge is geometrically broad, but its quantitative guarantee depends on a strongly convex (phi) and a smooth (Psi) with a Lipschitz gradient. The paper acknowledges this near the conclusion.

That qualification should be more prominent. Strong convexity is not a harmless technicality if the broader accepted-control theory permits linear or merely convex resource terms. Adding regularization to obtain curvature can change the policy and economic objective.

Thus the theorem is general with respect to accepted **feasible geometry**, but not with respect to the entire class of accepted objectives developed earlier in the manuscript.

I would sharpen the abstract and introduction to avoid letting “general accepted polyhedra” read as “general accepted-control problem.”

# 14. The paper still contains at least two scientific papers

Even after moving substantial historical material to the companion, the main manuscript contains:

1. a canonical inventory/service-contract model;
2. exact accepted-information comparisons;
3. a customer-neutral adaptive-direction theorem;
4. continuation participation on a large tree;
5. general normal-cone/KKT balance;
6. critical-friction/subtree-cut theory;
7. constructive transfer coordinates and repair;
8. a general resource-price/value-gradient theorem;
9. an inexact-response certificate;
10. a synthetic learning benchmark;
11. a frozen-fleet finite-sample result;
12. matched-accuracy computational timing.

The logical connections are real, but the manuscript reads as a program rather than a single top-journal paper. The consequence is that every contribution is discussed too briefly relative to the literature it must defeat.

The current 35-page main text plus 35-page companion is not merely long; it is scientifically overdetermined.

I continue to recommend choosing one of two routes.

## Route A: accepted-control theory

Make the paper about the accepted-control geometry:

- optimized static and information-class comparators;
- continuation participation;
- continuation prices and switching capacities;
- critical friction;
- exact transfer coordinates;
- constructive gain/certificate results.

Move the entire neural/value-gradient implementation to a separate paper or a short computational illustration. The current theory is much more distinctive than the neural benchmark.

## Route B: learning-augmented repeated optimization

Make the paper about learning optimizer-relevant resource statistics for repeated accepted convex programs:

- state one general accepted-polyhedron model early;
- derive the resource-statistic/value-gradient relation and inexact certificate;
- engage predict-then-optimize, differentiable optimization, dual prediction, warm starts, and parametric optimization directly;
- benchmark direct-statistic methods, value-gradient methods, and strong structure-aware classical solvers;
- scale to instances where exact optimization is materially costly;
- include misspecification or distribution shift;
- use a meaningful final deployment policy and independent validation.

The canonical inventory hierarchy and most of the earlier friction theory would then become motivation or companion material.

The present manuscript tries to execute both routes simultaneously.

# 15. Specific technical and presentation comments

### 15.1 Clarify the precise novelty of the two-Bregman identity

The exact identity
**J - F(x_eta) = B_H(eta*, eta) + B_Psi(u_eta, u*).**
is attractive. The paper should state whether this identity is a new lemma for this composite conjugate pair or a direct instance of a known Fenchel/Bregman duality identity. A direct reference would improve the paper even if the novelty is in its accepted-control use.

### 15.2 Explain why learning (J) is preferable to learning (eta^*)

R19's answer appears to be “it is not, empirically, on this problem.” That is acceptable, but then the theoretical role of the value critic should be recast as one admissible construction rather than the central implementation.

### 15.3 Report solver details in the main paper

The main paper should state enough about the classical solver and cached work to interpret a 10–40 ms comparison without forcing the reader into the companion. In particular: solver family, matrix factorization reuse, warm-start state, and whether symbolic/numeric factorizations are shared across contexts.

### 15.4 Separate theorem stress tests from algorithmic evidence

The 64 deliberate geometry cases and 64 quartic checks are useful theorem validation. They are not evidence that the learning method is robust at those boundaries unless the trained models themselves are evaluated under a declared distribution shift.

### 15.5 The capacity-activation star rows do not compare predictors

The companion correctly states that all methods are repaired to the same decision in the all-binding capacity stratum. The main narrative should make equally clear that these rows validate the response/repair layer, not the learned approximation.

### 15.6 Clarify the fleet theorem's sampling statement

The theorem says identical context distributions across policies are unnecessary, while the operational interpretation is a uniform random choice of a frozen policy for a new context. If deployment uses one common context distribution, state that directly. If policy-specific context distributions are allowed, define the target mixture carefully so the theorem's estimand matches the deployment mechanism.

### 15.7 Do not overinterpret the break-even number

The 2,546-query RBF break-even is host- and protocol-specific, based on observed mean differences and a conservatively charged offline cost. It is useful descriptive accounting, not a universal economic threshold. The manuscript mostly says this already; keep that caution.

### 15.8 The R20 price-polishing plan should be treated as future work until executed

The planned fixed-primal dual-price polishing may improve the certificate and reduce fallback. It may also make a purely classical warm-start/certificate pipeline stronger, further weakening the case for neural learning. Either outcome is scientifically informative. It should be reviewed only after the complete R20 manuscript and raw results exist.

# 16. What would change my recommendation

I would reconsider a substantially refocused new submission if it did the following.

For a **theory-centered paper**, I would want a much cleaner novelty map against convex analysis, total-variation duality, resource allocation, dynamic contracting, and parametric programming, followed by one compelling accepted-control theorem chain and a small number of exact examples.

For a **learning-centered paper**, I would want:

- direct engagement with predict-then-optimize, differentiable optimization, dual-variable prediction, and learning-augmented optimization;
- strong parametric/active-set/dual-warm-start classical baselines;
- a scaling study on the full general polyhedral model, not the old star;
- problem sizes where exact certified optimization is materially costly;
- a justified deployment target rather than an arbitrary outside protocol;
- an independent final validation design for a deployable model/ensemble;
- at least one meaningful misspecification or distribution-shift study;
- and a title/contribution structure that follows the actual winning method rather than privileging neural critics.

If RBF/direct-price methods remain strongest, that is not a failure. It simply means the paper should be about **certified learned resource statistics for accepted optimization**, not “Neural Differential Utility.”

# 17. Recommendation to the editor

R19 is a serious revision and it resolves several concrete deficiencies identified in the prior report. I find the new general bridge mathematically plausible under its assumptions, the experimental reporting unusually candid, and the reproducibility package strong.

However, the revision also generates evidence that weakens the manuscript's central scientific identity. The best surrogate is non-neural and directly predicts the operational statistic. Neural pipelines are substantially slower than classical optimization at the coarse target and remain slower at the strict target; at the strict target every surrogate falls back. The exact model is known and cheap enough that the practical need for a learned value critic remains unestablished. The new theorem is an elegant integration of standard convex-sensitivity ingredients, but the manuscript does not yet separate its novelty adequately from the directly relevant predict-then-optimize, differentiable-optimization, dual-prediction, and parametric-optimization literatures. The fixed synthetic benchmark and arbitrary outside comparator do not supply the missing operational significance.

I therefore do **not** recommend another major-revision cycle on the present integrated manuscript.

**Decision recommendation: Reject in the present form; encourage a substantially refocused new submission if the authors choose either the accepted-control theory route or the learning-augmented optimization route and rebuild the paper around that single contribution.**
