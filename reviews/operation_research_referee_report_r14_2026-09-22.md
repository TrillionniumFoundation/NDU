# Confidential Referee Report for Operations Research

**Manuscript:** *Neural Differential Utility: Accepted Adaptive Service Control and Certified Value-Gradient Learning*  
**Revision reviewed:** R14, September 22, 2026  
**Repository branch reviewed:** revision/ndu-operations-research-r14-20260922  
**Reviewed HEAD:** f34badb1acecd7eaebbb483b32688c77568f88a1  
**Prior referee report used for comparison:** reviews/operation_research_referee_report_r12_2026-09-22.md  
**Scientific predecessor identified by the authors:** 808b8f0353051581134d3b8b5a7424422d4e48a8  
**Recommendation:** **Reject in the present form. A substantially reconceptualized manuscript could merit a new submission.**

## Executive assessment

R14 is a serious revision. It directly addresses two of the strongest objections in my R12 report. First, the new two-review star construction removes the specific circularity of the earlier optimal-face theorem: the learned object is now a scalar value derivative, the policy is recovered from a feasible price response, and the regret bound no longer assumes access to the unknown optimal active face. Second, the authors actually execute a finite-sample expected-gain calculation for frozen policies under a declared synthetic distribution and retain positive absolute switching friction. These are genuine improvements.

I also find the R14 reproducibility package unusually transparent. The manuscript retains adverse experiments, reports that derivative supervision is not statistically resolved, reports that the complete learned pipeline is slower than structure-aware classical optimization, commits raw policies and timings, and includes an independent standard-library rational replay. I did not identify an obvious fatal algebraic error in Proposition 7.1 or Theorem 7.2 under their stated assumptions. The residual bound follows from the quadratic expansion and normal-cone inequality; the prior-price bound is consistent with the Lipschitz sensitivity of the single-resource response; and the envelope identity correctly identifies the specified derivative with the root transfer in this specialization.

The problem is now less correctness than **scientific necessity and scope**. The positive learning result is obtained only after the general accepted-control problem is collapsed to a two-date, scalar-transfer, diagonal-quadratic, single-resource star in which acceptance fixes every switching sign and the exact decision is already recoverable from one scalar equation. On precisely this positive-learning subclass, the exact classical solver is extremely cheap and faster than the complete learned pipeline. The learned critic is a fixed-random-feature tanh model with a ridge readout trained on exact solver labels, yet it is not compared with simple non-neural interpolation or low-dimensional regression. The statistically unresolved value-versus-value-gradient comparison remains unresolved. The broader multistage/vector/boundary theory still does not inherit the new nonoracular learning theorem.

Thus R14 makes the manuscript mathematically cleaner while sharpening the central editorial problem: **why is neural learning needed for the problem on which the positive theorem and experiment are proved, and why should the star result support the paper's broad integrated title?** At the Operations Research level, I do not think the current manuscript answers those questions.

---

# 1. What R14 genuinely fixes

## 1.1 The optimal-face circularity is genuinely removed in the new star theorem

Theorem 7.2 is materially different from the R12 acceptance-face result. The deployed response does not require the query-time optimal multipliers, a pre-enumerated active face, strict complementarity, or distance from a switching boundary. The policy uses a predicted scalar coupling price and remains feasible after the stated capacity adjustment.

This is the strongest positive change in R14.

## 1.2 Positive switching friction is present in the new learning distribution

The new contexts draw the switching-friction parameter from 0.01 to 0.20. The absolute penalty is not silently dropped. In the star subclass, acceptance fixes the sign of installation and continuation moves, so the nonsmooth penalty becomes a linear transfer charge. That is a legitimate structural reduction.

## 1.3 The finite-sample calculation is now executed rather than merely stated

The validation code freezes two policies, evaluates 2,048 new contexts, derives a uniform bounded range, applies a simultaneous Hoeffding lower bound, and reports a positive lower confidence bound for expected gain over the static gate. This directly repairs a major weakness of R12.

## 1.4 The authors preserve unfavorable evidence

The older poor shifted actors remain. The new paper says explicitly that the complete learned pipeline is slower than cold structure-aware methods, that the derivative-training difference is unresolved, and that the new star experiment does not imply arbitrary-tree transfer.

This transparency materially improves the credibility of the paper.

---

# 2. The R14 positive-learning result is obtained by making the optimization problem exceptionally easy

The crucial R14 specialization has all of the following simultaneously:

1. two review dates only;
2. a root with mutually exclusive continuation leaves;
3. a constant interior outside tier;
4. one scalar accepted-transfer coordinate per leaf;
5. diagonal quadratic leaf resources;
6. one rank-one root quadratic coupling;
7. one scalar root capacity;
8. fixed feasible boxes;
9. switching signs determined globally by acceptance;
10. a three-coordinate synthetic context ((h,alpha,lambda));
11. fixed primitive coefficients across the entire training and validation population.

Under these restrictions the accepted optimization becomes a continuous separable quadratic resource-allocation problem with a single coupling constraint. The exact optimizer is obtained from one monotone scalar equation. The authors themselves correctly cite the classical single-resource literature and do not claim a new generic water-filling algorithm.

This is exactly why the new theorem is implementable. It is also exactly why the learning problem is no longer compelling.

The paper should not argue that learning becomes necessary because the general accepted-control problem is complicated, then establish its affirmative learning result only on a subclass where the complication has disappeared.

---

# 3. On the positive R14 subclass, the exact classical algorithm dominates the learned pipeline

The paper's own timing table is decisive.

For 127 leaves at a normalized exact-gap tolerance of (10^{-7}):

- cold scalar Newton: median total 5.353 ms;
- Brent: 5.363 ms;
- sorted breakpoints: 5.513 ms;
- value-only learned pipeline: 10.635 ms;
- value-gradient learned pipeline: 10.600 ms.

The audit itself costs about 5.22 ms. The learned methods require refinement on 81.25% and 78.12% of timed contexts, respectively, so they usually pay for a first audit, a scalar solve, and a second audit.

More importantly, the underlying exact solve is almost free. The reported median scalar-Newton solve time at 127 leaves is roughly 0.09--0.13 ms depending on the table and execution path. At 32,767 leaves, Brent is still about 1.14 ms and safeguarded Newton about 1.87 ms. The explicit critical-friction calculation is about 0.067 ms.

These measurements undermine, rather than support, a neural-optimization motivation. The exact structural algorithm is already extremely fast at a scale far larger than the learned experiment.

If certification is operationally required, the classical method wins outright. If certification is not required, then the paper must compare uncertified or lightly certified learned deployment against equally lightweight exact or approximate classical alternatives. It currently moves between those two objectives.

---

# 4. The paper still has not established that a neural model is needed

The R14 critic is a 192-unit tanh random-feature model with frozen random hidden weights and a fitted ridge readout. The context is only three-dimensional. The target statistic is a scalar value and one scalar derivative.

I see no comparison against:

- linear or quadratic response surfaces;
- cubic splines;
- tensor-product interpolation;
- radial-basis interpolation;
- low-order polynomial chaos;
- nearest-cell or multilinear lookup;
- monotone regression;
- direct regression of the scalar coupling price;
- a small parametric formula exploiting the known piecewise-quadratic structure.

This omission is now a central scientific problem. Once the accepted problem has been reduced to a one-price response with a three-dimensional context, the burden is on the authors to show that a neural critic contributes something beyond generic function approximation.

The current experiment shows that one particular random-feature regressor can approximate the exact solution map. It does not show that "neural" structure matters.

---

# 5. The value-gradient claim remains empirically unresolved

The primary paired difference in mean regret, value-gradient minus value-only, has the reported 95% interval

[
[-9.568	imes 10^{-6},;2.059	imes 10^{-6}],
]

which includes zero.

The same is true for the reported paired differences in gradient MSE and certificate gap. In the independent validation cohort the empirical expected-gain difference between the two frozen policies is on the order of only (3.4	imes 10^{-7}) per discounted review, while both simultaneous lower bounds are essentially the same at about 0.1081.

I agree with the manuscript that no superiority claim should be made. But this creates a title-level problem. Both "value-only" and "value-gradient" policies are actually deployed through a derivative of the fitted scalar critic; the distinction is whether derivative labels enter the fitting loss. R14 does not establish that derivative supervision improves decisions.

The theorem establishes that **derivative error controls policy regret** in the star model. That is a structural sensitivity statement. It is not empirical evidence that value-gradient training is better than value fitting.

The title and abstract should distinguish those claims much more sharply.

---

# 6. The expected-gain confidence bound certifies a frozen policy, not the necessity of learning

The R14 Hoeffding result is valid for its stated bounded synthetic distribution if the range calculation and frozen-policy protocol are accepted. But the object certified is simply positive expected gain over static for two already-fitted policies.

The exact optimizer is available for every context from the known model and scalar solver. Therefore a deterministic classical policy can achieve the pointwise optimum without a learned approximation. The confidence exercise does not establish that learning enables a decision that the model cannot already compute cheaply.

The result is best interpreted as:

> a particular frozen approximate policy retains positive average benefit over the static baseline under a specified synthetic context distribution.

That is useful as a safety statement. It is not, by itself, a learning contribution of Operations Research significance.

A stronger paper would relate the finite-sample statement to a setting where exact online optimization is genuinely expensive, unavailable, noisy, partially observed, or constrained by a real latency/throughput budget.

---

# 7. The new learning distribution appears deliberately easy relative to the advertised difficult geometry

Several reported facts point in the same direction:

- all 2,048 unrefined proposals in the shared test cohort have nonnegative gain;
- the static gate fires 0% of the time;
- root-capacity projection occurs on only 1.56% of proposals;
- the average optimal gain is about 0.122, while average unrefined regret is only (10^{-6})-scale;
- the validation distribution uses the same fixed primitive star and the same low-dimensional context family.

The theorem is advertised as global through binding-capacity transitions and active-set changes. Yet the learned distribution rarely activates the root-capacity repair. The hard cases are instead exercised mainly by synthetic arbitrary-price structural tests, not by the learned policy distribution.

A serious evaluation should deliberately concentrate mass near:

- the critical-friction threshold;
- leaf activation and saturation breakpoints;
- root-capacity activation;
- small-gain regions where the static gate is genuinely nontrivial;
- switching-boundary transitions;
- primitive perturbations that move those boundaries.

Otherwise the positive deployment result risks being a demonstration on a region selected to be comfortably inside the successful regime.

---

# 8. The R14 bridge does not extend to the paper's general accepted-control theory

The earlier sections allow far more than the star theorem:

- multistage trees;
- vector tiers;
- arbitrary feasible comparators;
- signed tariff coefficients;
- equality and inequality commitments;
- boundary solutions;
- nonconstant outside protocols;
- smooth graph coupling;
- nonsmooth switching with endogenous saturated tensions.

The R14 scalar-critic theorem discards almost all of that structure. It does not cover a general tree, vector decisions, unknown switching signs, multiple coupled resources, or the nonconstant-comparator geometry that is emphasized as a contribution earlier in the paper.

R14 therefore does not fully solve the manuscript's identity problem. It creates a mathematically clean **special case in which learning works**, while the paper's general theory remains a different object.

The authors must either:

1. extend the nonoracular derivative-to-policy theorem materially beyond the star subclass; or
2. narrow the paper so that the star model, rather than the general multistage program, is the central scientific object.

At present the title and introduction imply a level of integration that the theorem dependency graph does not support.

---

# 9. The novelty of Proposition 7.1 and Theorem 7.2 needs a much harder literature separation

Proposition 7.1 reduces to classical continuous separable resource allocation with one coupling constraint. The cited Patriksson--Strömberg literature explicitly surveys breakpoint, relaxation, and multiplier algorithms for very large single-resource problems. The R14 scaling table itself confirms that classical scalar methods are excellent here.

The potentially novel object is therefore not the scalar solve. It must be the **accepted-service transformation plus the particular value-derivative interpretation and certificate**.

That distinction is not yet developed deeply enough.

For Theorem 7.2, the mathematical ingredients are also close to standard tools:

- envelope/Danskin sensitivity of a unique optimum;
- Lipschitz response of strongly convex/separable resource allocation;
- a quadratic Bregman remainder;
- rank-one inverse algebra;
- normal-cone optimality;
- Fenchel dual upper bounds.

The theorem is clean and useful. But a flagship OR paper needs a precise answer to: what part of the theorem is not already a straightforward specialization of parametric convex resource allocation and value-function sensitivity?

The current discussion credits classical tools but mostly asserts that the accepted-service interpretation is the contribution. That may be enough for a specialized paper; I am not convinced it is enough for the breadth of the present manuscript.

---

# 10. The synthetic primitive construction is too engineered to establish operational significance

The positive experiment fixes one primitive seed and generates:

- 127 equally likely leaves;
- tariff integers drawn from 8 through 12;
- random offset integers;
- balanced forcing so the common outside tier 1/2 is reoptimized in every context;
- quadratic curvatures tied directly to review weights;
- a three-dimensional context box;
- friction drawn from a narrow positive interval.

This is excellent for testing identities. It is weak evidence for an operational service-control claim.

The balance construction is particularly important: the model is deliberately generated so that the desired static comparator remains exactly centered. That makes the algebra clean, but it also means the experiment is a theorem harness more than a calibrated operations problem.

A top OR paper can be fully theoretical. If it chooses that route, novelty must be correspondingly deep. If it wants operational claims, the paper needs a realistic primitive family, calibration, or at least a substantially more heterogeneous stress population not generated to preserve the key reduction.

---

# 11. Statistical evidence is split across two different inferential questions

The paired eight-seed experiment uses training seed as the replication unit and correctly states that the Student interval is conditional on a shared test cohort. This measures training variability conditional on those 128 contexts.

The 2,048-context validation instead freezes the first training seed and obtains a bounded-variable confidence statement over new contexts. That measures deployment-context uncertainty conditional on one fitted pair of models.

Neither result alone establishes reliability of the full **training-and-deployment procedure** over both sources of randomness.

This is not a mathematical error. It is a scope issue. The manuscript should not let the independent-context confidence statement substitute for evidence that training is stable.

If the training procedure is part of the scientific contribution, a hierarchical or repeated-freeze design is needed: independently train several models, freeze them under a prespecified selection rule, then evaluate selected models on genuinely untouched deployment cohorts.

---

# 12. The "prospective" validation provenance is weaker than the wording suggests

The committed EXPERIMENT_PLAN.json does pre-specify the eight training seeds, the shared test seed, architecture, training size, loss weight, tolerance, and timing comparators.

However, the plan file does **not** contain the later validation seed 14999, (n=2048), (M=2), (delta=0.05), or the validation selection rule. Those settings appear in validation.py and the resulting validation artifact.

The source comment says those values were fixed before that program's first execution. That may be true, but it is not the same evidentiary object as a plan committed before training and before inspection of the earlier R14 results.

I do not require external preregistration for a computational OR paper. I do require precise language. The paper should call this a held-out internal validation unless commit history establishes that the full validation protocol was immutable before model selection and earlier result inspection.

---

# 13. The complete certification architecture still makes the learned method operationally unattractive

Only 17.48% of value-only and 19.04% of value-gradient proposals immediately meet the (10^{-7}) exact-gap tolerance. Thus roughly four-fifths of proposals require exact refinement in the matched-accuracy pipeline.

This is a more informative statistic than the very small average unrefined regret.

For certified deployment, the learned model mostly serves as an expensive warm start to a scalar problem that is already solved in a handful of Newton iterations.

The paper should quantify a realistic regime in which the learned proposal actually reduces total resource consumption: batch size, hardware, audit frequency, tolerance, number of repeated contexts, and amortization horizon. At present there is no such regime in the reported data.

---

# 14. The scaling experiment is not evidence of difficult stochastic-control scale

The 32,767-leaf experiment varies breadth at a fixed two-date horizon. The manuscript appropriately admits this.

But then the scaling evidence should not be used to create an impression that the learned approach addresses large multistage trees. The experiment is a large vector in a one-price separable resource-allocation problem.

Indeed, the classical scalar methods remain so fast at 32,767 leaves that the scaling experiment again strengthens the case for direct optimization.

If large scenario trees are a motivation, the paper needs depth, state coupling, multiple resource constraints, or another feature that prevents the scalar collapse.

---

# 15. The manuscript still contains two different papers

The main manuscript now combines:

1. general accepted multistage service-control geometry;
2. cumulative subtree cuts and critical friction;
3. constructive transfer and tension repair;
4. price-capacity margin theory;
5. verified cells;
6. older shifted neural actors and their failures;
7. the new two-review scalar-critic theorem;
8. a new direct-learning experiment;
9. prior information-value and continuous material retained through companions.

The main manuscript is reported as 40 pages excluding references, with a 38-page electronic companion and a 37-page historical archive.

Preservation is good repository practice. It is not a reason for the journal article to retain every scientific direction in its narrative.

The paper would be substantially stronger if it selected one center:

- **theory-centered:** accepted adaptive service control on trees, with structural algorithms and operational comparative statics; or
- **learning-centered:** a nonoracular value-derivative decision method for a genuinely difficult repeated optimization class, with strong baselines and a clear computational or informational advantage.

R14 tries to keep both at full strength. I still think that choice weakens the submission.

---

# 16. The exact final repository HEAD does not have a reported GitHub status

The reviewed HEAD is f34badb1acecd7eaebbb483b32688c77568f88a1. Its commit message ends with "[skip ci]". The repository connection reports no combined status entries for that exact commit.

The commit contains build logs, PASS summaries, compiled manuscripts, 6,626 replayed certificates, and the standard-library verification output. Those are useful artifacts. But they are not the same thing as a CI check attached to the exact published HEAD.

This is not a scientific rejection reason. It is a provenance issue. The response should not imply that the exact final HEAD itself passed an external GitHub status check unless such a status exists. A simple final validation workflow on the exact reviewable SHA would remove this ambiguity.

---

# 17. Specific technical and presentation points

## 17.1 Clarify the status of the capacity multiplier

Theorem 7.2 deliberately defines (eta^*=chi_0 v^*) and leaves the root-capacity multiplier in the feasible-set normal cone. This is mathematically defensible, but readers accustomed to a single resource price can easily interpret (eta^*) as the full KKT multiplier. The text should emphasize more strongly that the deployed surrogate may internally raise the leaf price by a capacity multiplier while the learned statistic is only the quadratic root marginal term.

## 17.2 Separate exact dual-gap certificates from analytical regret bounds

The tables already distinguish them. The prose should be equally disciplined. The residual inequality applies to the exact feasible response for a predicted price; the rational Fenchel certificate includes finite-precision repair; the validation lower bound concerns expected gain, not expected regret.

## 17.3 Report hard-regime stratification

At minimum, stratify unrefined regret and certification rate by:

- distance to critical friction;
- whether root capacity binds;
- number of active/saturated leaves;
- distance to nearest breakpoint;
- optimum gain magnitude.

A global average hides exactly the geometry the theorem is designed to handle.

## 17.4 Add direct-price learning baselines

If the true operational statistic is a scalar price, train models directly on (eta^*) or (v^*). Compare value-critic differentiation against direct supervised price regression. Otherwise the paper cannot show that learning a scalar value and differentiating it is preferable to learning the scalar decision statistic itself.

## 17.5 Add non-neural surrogate baselines

This is mandatory if "neural" remains in the title.

## 17.6 Do not treat a static-gain gate as a general safety result

The gate works because static is feasible and the model is completely known. It certifies improvement relative to one comparator, not robustness to misspecification, demand shift, tariff error, or implementation error outside the modeled polytope.

---

# 18. What would change my recommendation

I see two viable routes.

## Route A: accepted-control theory paper

1. Remove neural branding from the title.
2. Make the general multistage balance/cut/critical-friction theory the center.
3. Prove stronger algorithmic consequences for nontrivial trees or coupled resources.
4. Add operational comparative statics that are not merely KKT restatements.
5. Use the star theorem only as an illustrative corollary.
6. Reduce the historical and learning material sharply.

This could become a coherent OR theory paper.

## Route B: integrated learning paper

1. Extend the nonoracular derivative-to-policy guarantee beyond the two-date one-resource star.
2. Evaluate regimes where direct exact optimization is actually nontrivial.
3. Compare against direct price regression and simple non-neural surrogates.
4. Stress critical-friction, capacity-binding, and breakpoint neighborhoods.
5. Demonstrate either a real latency/throughput advantage, a genuine information advantage, or a robustness advantage after charging certification.
6. Use a fully prespecified repeated-train/held-out-deployment protocol.
7. Keep the adverse R12 evidence and explain precisely why the new method succeeds where the old actors fail.
8. Narrow title claims to what is actually established if derivative supervision remains statistically unresolved.

Without one of these routes, another cycle of adding theorems and experiments is unlikely to solve the manuscript's core identity problem.

---

# 19. Recommendation to the editor

R14 is substantially stronger than R12. I no longer regard unknown optimal faces, zero-switching computation, or unexecuted finite-sample validation as the principal objections. The authors have made real progress.

Nevertheless, I recommend **rejection in the present form**.

My reason is not an identified algebraic failure. It is that the manuscript's affirmative integrated-learning case now rests on a deliberately simplified resource-allocation subclass for which:

- the exact classical solution is explicit and extremely fast;
- the complete learned pipeline is slower;
- most learned proposals still require exact refinement for the stated tolerance;
- derivative supervision has no statistically resolved advantage;
- simple non-neural surrogates are not evaluated;
- the validation distribution is synthetic and fixed to one primitive star;
- and the nonoracular theorem does not extend to the broader multistage/vector theory that gives the paper its apparent scope.

The work contains publishable ideas. In my view, it does not yet constitute a single Operations Research paper at the level implied by its current title, breadth, and claims.

**Decision recommendation: Reject; encourage a new submission only after major scientific refocusing rather than another incremental revision.**
