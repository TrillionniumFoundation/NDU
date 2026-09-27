# Referee Report on R10 Scientific Revision

**Journal:** Operations Research  
**Manuscript:** *Neural Differential Utility: Accepted Adaptive Service Control and Certified Value-Gradient Learning*  
**Reviewed branch:** revision/ndu-operations-research-r10-20260921  
**Reviewed head:** 3f5bc42f0fa053453ca82f8ab3d66b5b46d88372  
**Scientific source commit before publication replay:** bdadc86eaf00c98e89ef73aa05bcdd8763516c65  
**Immediate scientific predecessor:** 584296b1a22de455a482c6809f00eda1387b6dab  
**Prior harsh report:** reviews/operation_research_referee_report_r9_2026-09-21.md on review/operation-research-r9-harsh-20260921  
**Review branch:** review/operation-research-r10-harsh-20260921  
**Review date:** 2026-09-21  
**Round:** R10 external harsh review

## Recommendation

**Reject in the present form.**

R10 is a serious reconstruction, not another cosmetic patch. It closes many of the concrete objections in the prior report: the new theory is now in the active manuscript; the graph coupling is written consistently; continuation participation is treated explicitly; the scalar tree result is substantially sharper than the earlier generic normal-cone statement; a genuinely nonlinear multistage computational problem has been added; cached and preconditioned classical baselines are present; strong graph/operator shift is tested; unfavorable learned outcomes are retained; end-to-end audit time is reported; and the validation workflow now actually rebuilds and rechecks the scientific package.

I therefore do **not** repeat the R9 diagnosis that the revision is unintegrated or that the computational section is unchanged. Those objections are closed.

My recommendation nevertheless remains rejection because the revision has now exposed the deeper editorial problem. The paper combines a narrow but interesting structural control theorem with a learning component whose strongest empirical conclusions are negative or inconclusive. The resulting manuscript is auditable, but auditability is not the same as a flagship-level contribution.

The main structural theorem is mathematically clean, but its completeness is confined to a scalar, interior, constant-static, positive-payment, exact-payment-neutral tree class. Within that class the proof is essentially a tree summation-by-parts representation of the first-order cone condition for a concave program. The two-review absolute-friction threshold is exact but even narrower. The remaining-payment Bellman state is useful, but resource/promise-state augmentation is a classical device and is not positioned against the constrained-MDP and promised-utility literatures. The stock-identification result is a well-executed supporting-price/newsvendor argument, not by itself a major new OR theory.

The learning evidence is more damaging to the current paper identity. The value-gradient advantage is statistically unresolved: the paired ten-seed mean difference is approximately 0.000577 per discounted service-review with a 95% interval of [-0.003923, 0.005076]. On the hardest weighted-block shift, the value-only and value-gradient proposals have mean raw gains of -0.097068 and -0.098095, while the classical solution gains +0.001953. The static gate returns the static policy for **every one of the 40 learned weighted-block deployments**. Across all learned deployments, 43 of 160 raw learned decisions are negative. The corresponding maximum learned certificate bounds on the weighted-block family are 4.8 and 3.69, enormously larger than the 0.001953 economic gain available from the classical optimum. These are not small degradations. They show that the certificate can protect the system from a failed learned proposal, but they do not show that the learned representation transfers successfully.

The cached re-audit also removes the earlier computational motivation for the quadratic learned critic. At 1,024 services, cached sparse solution takes 5.33 ms with a maximum bound of about 7.8e-12 per service, whereas the learned gradient readout takes 5.47 ms with a bound of about 3.42e-7. At 64 and 256 services the cached sparse method is also faster in the reported end-to-end numbers. The authors correctly no longer claim a speedup, but once that claim is removed, it becomes difficult to justify “Certified Value-Gradient Learning” as half of the paper title.

I did not find an obvious fatal algebraic error in the central R10 theorem chain under its stated assumptions. The present rejection is therefore primarily about **novelty, generality, paper identity, and the evidentiary burden created by the title**, not about a theorem collapsing on inspection.

---

# 1. What R10 genuinely fixes

The revision deserves credit for resolving a large number of prior blockers.

## 1.1 The manuscript is now actually revised

The root manuscript identifies itself as Revision R10 and directly inputs the new general theory, tree structure, and nonlinear multistage sections. The README, response, build scripts, tables, manuscript, companion, and historical supplement are synchronized. This closes the most basic R9 objection.

## 1.2 The graph-coupling formulation is repaired

The general formulation now uses vector node tiers and a joint convex coupling function. The displayed graph-edge term is genuinely nonseparable. The previous scalar/univariate notation no longer pretends to contain a Laplacian interaction it could not represent.

## 1.3 The generic KKT result is no longer sold as the flagship theorem

The manuscript now labels the tangent/normal-cone result and the Bregman decomposition as standard convex analysis. That is the correct positioning. The new structural claim is the scalar tree-edge criterion, which is materially more informative than “there exists a feasible improving direction.”

## 1.4 Continuation participation is treated structurally

The new tree criterion accounts for every continuation row. The edge perturbation is designed so that only one descendant subtree sum changes, with the correct sign. The manuscript also separates the ex-ante zero-friction memory statement from the case with history-specific promises and provides a counterexample with a 1/32 gap.

## 1.5 The computational experiment is no longer a known quadratic inverse

The new task is graph-coupled, quartic, multistage, and constrained at every history. The largest case has 992 contingent tier coordinates. This is a real response to the prior objection that the computational headline was being supported mainly by a fitted inverse of a known SPD operator.

## 1.6 Strong distribution shift is finally tested honestly

The test set changes graph family, weighted degree, horizon, dimension, quartic curvature, coupling, and operator spectrum. The weighted-block family moves the normalized Hessian maximum from roughly 11.7 in the training template to roughly 113–128. The learned failure under that shift is retained rather than hidden.

## 1.7 Classical baselines are materially better

The revision adds cached sparse/dense factorizations, preconditioned iteration, cached baseline-Hessian preconditioning in the nonlinear task, separate setup cost, and repeated timing observations. The manuscript explicitly says the methods are not compared at matched accuracy and refrains from a speedup claim.

## 1.8 Reproducibility is now a strength rather than a blocker

The R10 workflow reruns the predecessor science, runs the nonlinear study, cached re-audit, independent verifier, structural checks, table generation, operator diagnostics, all three PDF builds, and package validation. The final recorded run contains rational policies, multipliers, continuation checks, oracle records, raw timing arrays, and independent reconstruction of the nonlinear residual. This is substantially stronger than the workflow criticized in R9.

These are important improvements. They also mean that the remaining issues are not likely to be fixed by another layer of packaging.

---

# 2. The core editorial problem is now contribution, not correctness

The paper currently tries to make three contributions simultaneously:

1. a structural theory of accepted adaptive service control;
2. an exact synthetic information-value decomposition for the canonical service model;
3. a learned proposal mechanism with ex-post policy certificates for nonlinear high-dimensional control.

Each piece contains useful material. I do not think their combination currently clears the Operations Research bar.

The structural theory is not yet broad enough to carry the entire paper as a theory paper. The canonical model remains heavily engineered and example-specific. The learning results do not establish either a statistical advantage of gradient supervision or a computational advantage at matched certified accuracy. The synthetic experiments do not supply the application importance that could compensate for limited theoretical or algorithmic generality.

The result is a manuscript whose scientific honesty has improved faster than its central claim. R10 openly reports that the hard shift breaks the learned policy, that the gradient-supervision interval includes zero, and that no matched-accuracy speedup has been demonstrated. I view that transparency positively. But a flagship journal still needs a positive contribution whose importance survives those caveats.

At present I see a promising service-control paper plus an interesting audit framework, not a coherent flagship contribution under the current title.

---

# 3. The complete tree-edge criterion is the strongest new result, but its scope is too narrow

Theorem 4.1 is the most important new theoretical result in R10. It deserves to be evaluated carefully.

The theorem considers scalar tiers on a finite tree, an interior constant comparator, strictly positive discounted payment coefficients c_n, exact equality of root expected payment, continuation inequalities on every nonroot subtree, and a differentiable convex resource function. It defines the marginal provider reward per payment unit at the static comparator,

k_n = [w_n a_n - partial_n R(bar theta 1)] / [w_n a_n],

and proves that the static protocol is globally optimal exactly when k_n is nondecreasing from parent to child.

The proof uses subtree payment deviations S_n and the identity

gradient W(bar theta 1) dot (x - bar theta 1)
= sum over nonroot n of (k_n - k_parent(n)) S_n,

with S_n <= 0. Under concavity, the sign condition yields global optimality. A violated edge generates the two-coordinate transfer.

I believe this argument is correct in the stated class.

The difficulty is the level of novelty and generality.

## 3.1 The theorem is a specialized polar-cone characterization

The mathematical engine is simple: the feasible cone induced by nested subtree budgets has an explicit cumulative-sum representation, and the polar-cone condition becomes monotonicity of a local marginal ratio along edges. That is useful, but it is closely tied to first-order optimality of a concave program over a very particular tree cone.

The authors should not mistake “closed form” for “deep structure.” A top OR theorem should ideally reveal a structural phenomenon that survives meaningful extensions or produces new comparative statics that are not obvious from cone duality.

## 3.2 “Complete” is true only for a restricted class

The abstract says that a “complete tree-edge criterion” characterizes improvement under continuation participation. That wording is too broad without the nearby qualifiers.

The theorem requires, among other things:

- scalar tiers;
- a constant static comparator;
- interiority of that comparator;
- positive payment coefficients;
- exact root payment neutrality;
- continuation caps generated by the same static outside protocol;
- a finite tree;
- differentiable convex resources.

The paper has a vector graph model elsewhere, but the complete theorem does not cover it. It has box constraints elsewhere, but the theorem avoids boundary comparators. It discusses weak root acceptance only in a short extension after the theorem.

A reader could reasonably infer from the abstract and introduction that the criterion solves the general accepted-control model. It does not.

## 3.3 The most economically interesting extensions remain open

A much stronger theoretical contribution would characterize at least some of the following:

- nonconstant static outside protocols;
- boundary static optima;
- vector tiers with graph coupling;
- multiple payment/service commitments;
- zero or sign-changing net payment coefficients;
- more general continuation outside options;
- full-tree nonsmooth switching costs rather than only a two-review chain;
- endogenous or partially optimized tariffs;
- comparative statics of the optimal accepted value, not just existence of a local improving edge.

I do not require all of these. I do require enough generalization that the flagship theorem is recognizably about a class of service-control systems rather than one convenient cone.

## 3.4 A full-tree nonsmooth result would be much more compelling

The two-review absolute-friction threshold is exact and clean, but it is a one-dimensional result. The natural next question is what happens on the full tree under total-variation/absolute switching costs. Does the no-improvement region admit a cut, flow, isotonic, or dual characterization? Can one compute a global critical friction or a set of edgewise thresholds without solving the nonlinear program?

A full-tree nonsmooth theorem would be a meaningful structural advance. The current two-review corollary is useful but too small to carry the paper.

---

# 4. Stock identification is carefully repaired but remains standard in mathematical content

The R10 stock proposition is better than the earlier version. It correctly handles one-sided derivatives, atoms, boundary minimizers, exogenous occupation weights, approximate growth, and an explicit additive vector extension.

I see no obvious error in the scalar critical-fractile calculation.

But the underlying mechanism is standard:

1. form a supported physical objective C - xi f;
2. identify its unique constrained minimizer;
3. sum the nonnegative supporting gaps;
4. use the accepted fill/cost inequalities to force the sum to zero.

The result is valuable because it eliminates physical stock from the accepted comparison. It should remain. It should not be treated as independent evidence of flagship-level theoretical novelty.

The key limitation is also substantive: regime occupation probabilities must be exogenous and policy invariant. If service tiers affect demand, churn, transition probabilities, customer retention, or future operating state, the supporting-gap sum no longer compares the same occupation weights without further argument. This assumption is stated, which is good, but it sharply limits the economic generality.

---

# 5. The remaining-payment state is useful, but the manuscript underpositions a classical idea

The R10 continuation formulation introduces a remaining-payment budget as a Bellman state and allocates child budgets jointly with the current tier. This is the right way to preserve history-specific continuation feasibility.

It is also conceptually close to standard constrained dynamic programming and promised-value/resource-state constructions.

The current bibliography is too thin here. At minimum, the paper should confront:

- Altman, *Constrained Markov Decision Processes* (1999), for constrained-state/resource augmentation and occupation-measure foundations;
- the promised-utility state tradition in dynamic contracting, including Spear and Srivastava (1987), Thomas and Worrall (1988), and related recursive formulations.

The paper is not a private-information contracting paper, so these references are not direct substitutes for the model. But the state-augmentation principle is not new. The contribution, if any, must be the specific service-control structure obtained after introducing the budget state.

At present the manuscript says the remaining-payment state “reconciles continuation participation with dynamic programming.” That is correct as a model construction, but it is too close to established recursive methods to be counted as a major standalone innovation without sharper positioning.

---

# 6. The zero-friction memory discussion is improved, but it weakens the original “memory” narrative

R10 correctly distinguishes two facts:

1. with only ex-ante linear commitments, convex stage costs, and no other history-dependent feasibility, full-history information has no value at zero switching friction beyond time and current regime;
2. with history-specific continuation promises, history can matter even when physical switching friction is zero, because history indexes contractual obligations.

This is a good correction.

It also changes the interpretation of inherited-tier value. The persistent tier is not generally revealing additional demand information. It can act as a record of prior obligations or decisions. The manuscript now says this explicitly.

That precision should be carried consistently through the entire paper. Any older language that suggests “the inherited tier contains information” should specify whether the information is about exogenous demand, endogenous contractual state, or merely a sufficient statistic for prior decisions.

The canonical accepted hierarchy reports an inherited-tier increment of only about 0.01929 after time and current regime are already available, versus a total static-to-full gain of about 0.63667. The manuscript acknowledges that this is roughly three percent of the total. This further argues against framing persistent “memory” as the dominant economic mechanism.

---

# 7. The nonlinear learning experiment is a real improvement, but its strongest result is failure under shift

The new nonlinear experiment is a legitimate response to the previous review. It is no longer a fitted inverse of a known quadratic operator.

However, the reported evidence does not support learning as a title-level positive contribution.

## 7.1 The weighted-block shift is a complete learned-policy failure before gating

On the weighted-block family:

- Newton-direct raw gain: +0.001953;
- Newton-PCG raw gain: +0.001953;
- value-only learned raw gain: -0.097068;
- value-gradient learned raw gain: -0.098095.

The static gate returns the static policy in 20/20 value-only cases and 20/20 value-gradient cases.

This is not “degraded transfer.” It is a failure of the learned proposal mechanism on the strongest shift.

The gate makes deployment safe. That is useful. But the scientific conclusion is then: a simple certified fallback can reject bad learned proposals. It is not: the learned critic transfers successfully.

## 7.2 The certificates become operationally uninformative on the hardest shift

The maximum certificate bounds on the weighted-block family are 4.8 and 3.69, while the classical incremental gain is only 0.001953.

A valid upper bound can be mathematically correct and still be useless for decision quality at the scale of the economic effect.

The paper should report, for every family, ratios such as:

certificate bound / classical achievable gain,

and perhaps

certificate bound / proposed improvement.

That would immediately show where the certificate is decision-informative and where it is merely formally valid.

## 7.3 The gate proves “no harm,” not “learning works”

The static gate is almost tautologically safe because it compares exact rewards of the repaired proposal and the static comparator and chooses the larger.

I support including it. But it is not a substitute for a robust learned policy.

The paper should distinguish three claims:

- **feasibility certification:** the submitted policy obeys constraints;
- **optimality-gap certification:** the submitted policy is within an explicit bound of the unknown optimum;
- **fallback safety:** a known comparator is selected when the learned proposal is worse.

R10 has all three mechanisms in some form, but on the hardest shift only the third provides a useful operational decision.

---

# 8. “Certified Value-Gradient Learning” is still too strong a title phrase

The strongest certificates in R10 are **policy certificates**. Their validity does not depend on the candidate being produced by a neural critic. A classical candidate receives the same kind of residual audit.

This is a virtue mathematically. It is a problem rhetorically.

The title phrase “Certified Value-Gradient Learning” suggests that the learning procedure itself has a certified generalization, convergence, or performance property. The paper does not prove such a result.

What it proves is closer to:

> a learned candidate can be independently checked by a deterministic a posteriori certificate.

Those are different claims.

A more accurate title would foreground accepted adaptive service control and describe learning as a candidate-generation implementation, unless the authors develop a genuine learning theorem.

---

# 9. The value-gradient supervision claim is empirically unresolved

The paper is commendably explicit here.

Across the ten training seeds, the paired mean difference between value-gradient and value-only fitting is approximately 0.000577 per discounted service-review, with a 95% Student interval of approximately

[-0.003923, 0.005076].

This interval includes zero comfortably.

Therefore the manuscript cannot claim a reproducible advantage of gradient weighting. It currently avoids making that claim, which is correct.

But this creates a larger question: if “value-gradient” is in the title, what positive fact about value-gradient learning has actually been established?

The answer cannot be simply that value gradients are used. A title-level methodological phrase needs a demonstrated advantage, a theorem, or a distinctive capability.

The current experiment establishes neither a statistically resolved benefit nor a matched-quality computational benefit.

---

# 10. The statistical design quantifies training-seed variation, not problem-distribution uncertainty

The paired interval is constructed from ten training seeds, each evaluated on the same eight test problems.

That is a reasonable way to quantify variation from the training sample.

It is not a confidence interval for generalization across graph/problem instances or across graph families.

There are only two independently generated test instances per family. In particular, there are only two weighted-block instances supporting the strongest distribution-shift conclusion.

A stronger computational study should separate at least:

- training-data variation;
- test-instance variation within a graph family;
- family-level shift;
- timing variation.

A hierarchical or two-way design with substantially more independently generated test problems would be more persuasive. The current ten-seed t-interval should be described narrowly as training-seed uncertainty conditional on the fixed test set.

---

# 11. The static comparator is engineered to be exactly one half

The nonlinear test instances are constructed by weighted-centering the forcing so that the unique reoptimized static tier is exactly 1/2.

This is legitimate for a controlled synthetic experiment. It is also unusually convenient.

It simplifies:

- the outside continuation caps;
- the static gate;
- the feasibility geometry;
- the interpretation of centered features;
- the static optimality check.

The theory itself also relies on an interior constant comparator in its strongest complete criterion.

This alignment raises the concern that both the theorem and the experiment are optimized around the same convenient geometry.

A more convincing study should include instances where the optimized static comparator is:

- not exactly 1/2;
- problem-dependent;
- near a boundary;
- nonconstant across services if the institution permits that;
- generated without weighted centering designed to make the comparator analytic.

Otherwise it is difficult to assess how much of the success comes from the algorithm and how much comes from building the test family around an analytically convenient baseline.

---

# 12. The feasibility repair is too crude to leave uninterpreted

The learned actor is clipped, rounded down, and then multiplied by a common nonnegative scaling factor chosen to satisfy every subtree cap.

This repair is easy to certify, but it is not a projection onto the feasible region and is not designed to minimize economic distortion.

That matters because the reported learned reward is the reward **after repair**.

The current results do not cleanly separate:

1. representation error of the learned actor;
2. violation of continuation constraints before repair;
3. distortion caused by the common scaling repair;
4. remaining suboptimality after repair.

On the weighted-block family, where the final learned reward collapses, this decomposition is essential. If the raw actor is nearly useful but global scaling destroys it, then the problem is the repair. If the actor is already poor, then the problem is transfer. Those lead to different scientific conclusions.

At minimum, the paper should report:

- fraction of proposals feasible before repair;
- distribution of repair scale factors;
- objective loss caused by repair;
- constraint violation before repair;
- comparison against an optimal Euclidean or objective-aware projection;
- comparison against a feasibility-aware actor parameterization.

Without this, the hard-shift result cannot be diagnosed.

---

# 13. The classical computational comparison is still not decisive

R10 improves the baseline design substantially. The new timing table is much more credible than the previous one.

But the paper still does not establish a learning advantage at matched certified accuracy.

The nonlinear solvers achieve maximum normalized gaps below roughly 5.7e-10. The learned methods have bounds orders of magnitude larger and, on one family, economically bad raw policies.

Comparing 215 ms for a learned proposal against 270 ms for a high-accuracy PCG/Newton solve on the weighted-block case is not evidence of a useful speedup if the former returns a policy that must be rejected by the gate and the latter produces the actual +0.001953 gain.

The right experiment is:

> For a fixed economically meaningful certificate tolerance, what is the end-to-end cost of each method to return a feasible policy meeting that same tolerance?

The manuscript explicitly says this matched-accuracy hybrid experiment has not been performed. That honesty is appropriate, but it means the algorithmic question remains unanswered.

The paper also lacks a comparison to mature general-purpose or specialized convex optimization software. A custom Python Newton/dual implementation is useful for controlled study, but it should not be treated as the practical frontier without additional benchmarking.

---

# 14. The quadratic re-audit now argues against the old learning story

The cached quadratic table is especially informative.

At 1,024 services:

- cached sparse: 5.33 ms, bound about 7.8e-12;
- learned gradient: 5.47 ms, bound about 3.42e-7.

At 256 services:

- cached sparse: 1.90 ms;
- learned gradient: 2.02 ms.

At 64 services:

- cached sparse: 0.96 ms;
- learned gradient: 1.11 ms.

The learned method is not faster in this corrected comparison, while the sparse method is dramatically more accurate.

This does not invalidate the learned critic as an illustration. It does remove the most natural reason to keep the old quadratic portfolio study in the main paper.

I recommend moving that study entirely to the companion or historical supplement. Retaining both the old quadratic learned critic and the new nonlinear learned critic in the active main manuscript makes the paper longer while the old experiment no longer supports a positive central claim.

---

# 15. The architecture itself is modest and should be described accordingly

The nonlinear “neural potential” is a fixed 63-feature softplus representation formed from identity, one-step smoothing, and two-step smoothing transforms. Only the linear readout coefficients are fit by regularized least squares.

This is a perfectly reasonable approximation architecture.

It is not a substantial neural-learning innovation.

The paper already says the architecture is not claimed as new. That is good. But then the contribution must come from either:

- provably better approximation;
- reliable transfer;
- a clear computational advantage;
- an operational application;
- or a new theoretical connection between value gradients and accepted control.

R10 does not yet establish any of those strongly enough.

A fixed nonlinear feature map plus linear regression is especially hard to justify as a title-level learning contribution when derivative weighting is statistically inconclusive.

---

# 16. The finite-difference target guarantee does not solve the learning problem

The central-difference target is no longer incorrectly called exact. The paper gives an explicit error bound, and all scalar oracle records are certified.

That is a real improvement.

But the largest normalized directional target error bound is about 0.004167, while the observed mean value-gradient improvement over value-only fitting is only about 0.000577.

These are not directly the same random quantity, so one should not mechanically compare them as confidence bounds. Still, the scale difference is a warning: the deterministic target approximation error can be materially larger than the empirical effect the paper is trying to detect.

The paper should include sensitivity to h and to oracle accuracy in the nonlinear experiment, not only in the historical quadratic discussion.

---

# 17. The “value-only” baseline uses derivative-design information in preprocessing

In the training code, the common feature scaling is computed using both the value-feature matrix X and the directional derivative feature matrix DX:

scale = sqrt(mean(X^2) + mean(DX^2) + ...).

The value-only regression does not use derivative target values DY, but it does use a scaling derived partly from derivative-feature geometry.

This is not a serious unfairness against the value-only method; if anything, it gives that baseline additional structural preprocessing.

However, the terminology should be exact. “Value-only” means no derivative **targets**, not that the entire fitting pipeline is independent of derivative-design information.

Because the claimed derivative advantage is already statistically unresolved, all such details should be explicit.

---

# 18. The paper remains entirely synthetic

The revised manuscript states this clearly, which is preferable to overclaiming.

The problem is editorial rather than ethical.

Accepted service control, inventory commitments, review periods, and service-level agreements are mature OR topics. In such a setting, a flagship paper normally needs either:

- a substantial new theory with clear generality;
- a substantial algorithmic advance;
- or a compelling empirical/calibrated application.

R10 is not yet strong enough on any one of these axes.

The canonical service example is synthetic. The robustness study is local and synthetic. The nonlinear graph study is synthetic. The graph shifts are useful stress tests, but they do not establish that the modeled tariff/continuation structure corresponds to a real operational setting.

A serious calibration would strengthen the paper greatly, especially if it demonstrated that the primitive edge criterion, friction threshold, or static gate changes a real service decision.

---

# 19. The literature positioning is still too thin for the paper’s ambition

The current active bibliography is remarkably short given that the manuscript spans:

- inventory/service contracts;
- constrained stochastic control;
- continuation participation;
- dynamic programming with promise/resource states;
- hysteresis;
- graph-coupled optimization;
- neural approximation;
- Sobolev/value-gradient fitting;
- a posteriori optimality certificates.

The paper has improved its service-contract citations and now credits standard convex tools. But important neighboring literatures remain missing.

At minimum, the authors should locate the paper against:

- constrained Markov decision processes and resource-constrained dynamic programming;
- recursive promise-state methods;
- approximate dynamic programming and residual-based performance bounds;
- safe/constrained learning where feasibility is certified separately from proposal quality;
- modern numerical methods for large sparse convex programs with tree and graph structure.

The main issue is not citation count. It is that without this map, several constructions that are standard in adjacent communities risk being presented as more conceptually distinctive than they are.

---

# 20. The paper identity remains unresolved

R10 tries to keep the integrated identity rather than choose between the two paths described in the prior report.

I do not think that choice has worked.

The structural service-control theory and the learned proposal mechanism do not currently reinforce each other enough.

The tree theorem is scalar and local in primitive marginal ratios. The nonlinear learning experiment is vector-valued and graph-coupled. The strongest theorem does not explain the learned architecture. The learning architecture does not enable the theorem. The residual certificate is generic strong convexity and works equally for classical solutions. The static gate is method-agnostic.

In other words, the two halves share an application vocabulary but not a deep scientific dependency.

The result is still two papers in one:

### Paper A: accepted adaptive service control

This paper would contain:

- supporting-price stock identification;
- the exact accepted information hierarchy;
- the continuation-compatible tree theorem;
- a stronger full-tree nonsmooth friction result;
- promise-budget dynamic programming;
- structural comparative statics;
- possibly a calibrated service application.

### Paper B: certified candidate generation for nonlinear constrained control

This paper would contain:

- the quartic graph/tree model;
- learning and classical solvers;
- a posteriori rational certificates;
- feasibility-aware approximation;
- matched-tolerance comparisons;
- broad distribution-shift statistics.

At present Paper A is more mature.

---

# 21. Required changes for a credible theory-focused resubmission

If the authors pursue the service-control paper, I would recommend all of the following before resubmission.

## 21.1 Remove learning from the title

Unless a new theorem or decisive computational result makes learning essential, the title should describe the structural accepted-control contribution.

## 21.2 Generalize the tree theorem materially

At least one major extension should be solved, not merely discussed. Candidates include:

- nonconstant static policies;
- boundary optima;
- vector tiers with structured coupling;
- multiple continuation budgets;
- full-tree absolute switching;
- a broader class of outside options.

## 21.3 Derive comparative statics

The paper needs results that say how accepted adaptivity changes with economically interpretable primitives, not only whether a local edge can improve.

Examples:

- monotonicity of adaptive value in switching friction;
- bounds in terms of dispersion of payment rates;
- sensitivity to continuation tightness;
- conditions under which inherited-tier value vanishes or is bounded;
- comparative statics for the critical friction on a full tree.

## 21.4 Position the promise-budget state correctly

Add the constrained-MDP and recursive promise-state literature and state exactly what is new in the service-control specialization.

## 21.5 Keep the exact canonical hierarchy as an illustration, not the general theorem

The exact rational decomposition is useful and impressive as verification. It should illustrate the structural theory rather than serve as the main evidence of generality.

## 21.6 Move most learning material out of the main paper

A short computational illustration can remain if it demonstrates how an accepted policy is certified. The old quadratic study should not remain a coequal main contribution.

## 21.7 Preferably add a calibrated application

A real service setting would make the structural conditions and thresholds more meaningful and could justify the service-control framing even if the theorem remains somewhat specialized.

---

# 22. Required changes for a credible learning-focused resubmission

If the authors instead insist on retaining “Certified Value-Gradient Learning” as a central identity, substantially more is required.

## 22.1 Establish a positive learning result

At least one of the following must be demonstrated:

- a statistically resolved quality advantage from gradient supervision;
- a matched-certified-accuracy computational advantage;
- a theorem giving an approximation/generalization advantage;
- a capability that classical methods cannot practically deliver.

R10 establishes none of these.

## 22.2 Fix the hard-shift failure

A method that falls back to static in every weighted-block case has not solved the proposed transfer problem.

Possible directions include:

- train on a broader operator family;
- use spectrum/degree-aware normalization;
- enforce feasibility structurally;
- adapt features to graph family;
- use online refinement;
- train with certificate-aware loss;
- include an explicit out-of-distribution detector.

## 22.3 Benchmark the full fallback pipeline

If the proposed deployed system is “learn, certify, and refine classically when needed,” then measure that actual pipeline.

For each tolerance, report:

- fraction accepted immediately;
- fraction gated to static;
- fraction requiring refinement;
- total latency;
- final certified gap;
- final improvement over static.

## 22.4 Match quality across methods

The main timing comparison should fix a certificate tolerance or economic regret threshold. Comparing a 1e-10-gap solver with a loose learned proposal is not a scientifically clean speed comparison.

## 22.5 Increase test-instance replication

Two instances per family are insufficient for broad transfer claims. Use many independent graph/problem instances and separate training-seed uncertainty from problem-distribution uncertainty.

## 22.6 Diagnose repair distortion

Report pre-repair feasibility, scale factors, reward lost in repair, and comparisons with better projections or feasibility-aware parameterizations.

---

# 23. Reproducibility assessment

This is one area where R10 is unusually strong.

I verified the structure of the committed package and the recorded validation outputs. The package reports:

- 176 nonlinear deployment records;
- 72 cached-quadratic records;
- 2,640 exact continuation checks;
- 52,624 exact tier checks;
- 720 oracle records;
- independent fraction-based reconstruction of objectives and residuals;
- 120 structural edge tests;
- 12 absolute-friction tests;
- the exact 1/32 promise-state counterexample;
- three compiled documents;
- a manifest of source hashes.

The workflow now runs scientific reproduction and compilation rather than only archiving source.

I would not reject R10 for reproducibility.

One small presentation issue remains: the build invokes a predecessor source-preparation script to materialize some active R7-derived sections. This is reproducible, but a final submission package would be easier to inspect if all active manuscript inputs existed as ordinary committed source files without requiring a generation step. This is a usability suggestion, not a scientific blocker.

---

# 24. Detailed technical comments

## 24.1 Scope of the edge theorem in the abstract

Add “scalar,” “interior constant static comparator,” and “payment-neutral” near the first abstract-level description of the complete criterion.

## 24.2 Weak versus exact root acceptance

The main theorem uses exact root equality. The short extension for weak root acceptance adds k_o >= 0. This distinction should appear earlier because the broader accepted-control model uses inequalities.

## 24.3 Positive tariffs

The complete criterion assumes a_n > 0. Explain whether zero or negative net payment rates can arise in the intended service setting. If they can, the ratio k_n is singular or changes economic meaning.

## 24.4 Boundary comparators

The strongest theorem avoids bar theta equal to 0 or 1. Boundary static solutions are common in constrained service problems. A normal-cone version is easy, but the elegant edge-ratio statement may change. This should be investigated, not left implicit.

## 24.5 Vector accepted control

The general model is vector-valued, but the structural theorem is scalar. The paper should not let the graph experiment create the impression that the theorem covers graph-coupled vector tiers.

## 24.6 Full-tree absolute switching

The two-review threshold is exact but limited. A full-tree characterization would substantially improve the theory.

## 24.7 Promise-state recursion

State whether b denotes a conditional or unconditional discounted payment budget at each node and keep normalization consistent throughout the main text. The current equation is understandable but should be tied explicitly to the earlier unconditional subtree rows.

## 24.8 Static gate certificate

When the gate selects static, report the resulting certified optimality gap of the selected decision directly, not only the proposed learned bound. This makes clear whether the gate merely prevents negative gain or also yields a useful near-optimality statement.

## 24.9 Certificate-scale diagnostics

Add tables of normalized certificate-bound / achievable-gain ratios. The weighted-block numbers reveal a huge difference between formal validity and operational usefulness.

## 24.10 Finite-difference sensitivity

Repeat the nonlinear experiment for several h values or justify why h = 1/40 is near-optimal under the stated oracle-gap tradeoff.

## 24.11 Value-only preprocessing

Clarify that value-only fitting uses no derivative targets but shares feature scaling that includes DX geometry.

## 24.12 Timing environment

The reported environment is one CI/Azure machine. Avoid drawing hardware-independent conclusions from millisecond differences.

## 24.13 Classical solver breadth

Add at least one mature convex/nonlinear solver baseline or explain why the custom Newton-dual implementation is representative.

## 24.14 Static-comparator construction

Add non-centered test families where the optimized static tier is not analytically fixed at 1/2.

## 24.15 Test-set independence

The paper should state explicitly that the Student interval is conditional on eight fixed test problems and captures only training-seed variation.

## 24.16 Historical supplement

The historical supplement is useful for preservation, but it should not be part of the scientific burden on a normal external reader. The active paper should be understandable without reading it.

## 24.17 Main-paper length

The active main manuscript still carries both the retained quadratic learned-control section and the new nonlinear section. The old quadratic section should be moved out of the main chain.

## 24.18 Terminology

“Certified learning” should be replaced by “certificate-checked learned proposals” unless the learning rule itself receives a theorem.

---

# 25. Minimum bar before I would recommend another full referee round

I would not recommend another incremental R11 that simply adds more tables around the present architecture.

Before another full round, I would want to see a structural choice.

For a **theory/control submission**:

1. learning removed from the title;
2. one materially stronger structural theorem beyond the current scalar constant-comparator edge condition;
3. full positioning against constrained-MDP/promise-state literature;
4. clearer comparative statics;
5. reduced computational material in the main paper;
6. preferably a calibrated application or a much broader structural model.

For a **learning/algorithm submission**:

1. a positive, statistically resolved or theoretical reason for value-gradient learning;
2. hard-shift performance that does more than gate to static;
3. matched-certificate-tolerance timing;
4. many more independent test instances;
5. decomposition of actor error versus feasibility-repair error;
6. an actually benchmarked learn-certify-refine pipeline.

Either route could produce a strong paper. The current hybrid does not yet do so.

---

# 26. Final assessment

R10 is the first revision in this sequence that I regard as a **complete, reviewable scientific manuscript rather than an incremental patch**. That is a substantial achievement.

The key theorems appear internally coherent under their stated assumptions. The continuation-compatible edge construction is a genuine improvement over the earlier generic convex-optimality discussion. The nonlinear study is appropriately difficult, and the authors deserve credit for retaining the severe distribution-shift failures. The reproducibility package is unusually careful.

But the revision also makes the central weakness impossible to ignore.

The paper’s strongest new structural theorem is complete only in a narrow scalar tree class and is mathematically close to a specialized first-order cone characterization. The most general convex pieces are standard. The promise-budget recursion is underpositioned relative to classical constrained dynamic programming. The canonical exact decomposition remains synthetic. The learning architecture is modest, gradient supervision has no statistically resolved advantage, the corrected quadratic baseline no longer favors learning, and the hardest nonlinear transfer setting causes all learned proposals to fall back to the static policy. There is no matched-certified-accuracy speed advantage and no real application.

In a lower-bar venue I would view R10 as a strong, transparent, and technically careful contribution. For *Operations Research*, the manuscript still needs a clearer identity and a substantially stronger positive result.

**Recommendation: Reject in the present form. I would encourage a genuinely restructured resubmission centered on accepted adaptive service control, with the learning component demoted unless new evidence changes its scientific role.**
