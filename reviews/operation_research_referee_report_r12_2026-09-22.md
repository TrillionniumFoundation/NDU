# Referee Report on R12 Scientific Revision

**Journal:** Operations Research  
**Manuscript:** *Neural Differential Utility: Accepted Adaptive Service Control and Certified Value-Gradient Learning*  
**Reviewed branch:** revision/ndu-operations-research-r12-20260922  
**Review branch:** review/operation-research-r12-harsh-20260922  
**Review date:** 2026-09-22  
**Round:** R12 external harsh review  
**Immediate prior full review:** reviews/operation_research_referee_report_r10_2026-09-21.md on review/operation-research-r10-harsh-20260921

## Recommendation

**Reject in the present form, while encouraging a theory-centered resubmission after substantial restructuring.**

R12 is a materially stronger paper than R10. It is not an incremental packaging revision. The authors have directly answered several of the most important mathematical criticisms in the prior report: the flagship structural result now permits arbitrary feasible comparison protocols, boundary tiers, vector decisions, multiple inequality and equality commitments, signed coefficients, and full-tree absolute switching. The scalar-tree specialization yields cumulative subtree cuts and an exact critical-friction program. The revision also adds a quantitative price-capacity margin, an acceptance-face loss decomposition, a finite-sample pipeline-selection statement, and a matched-certified-accuracy computational study. Reproducibility remains unusually strong.

I therefore regard many of the concrete R10 blockers as **closed**.

My recommendation nevertheless remains rejection because the central editorial problem has changed rather than disappeared. The new mathematics is broader, but its core engine is still a polyhedral KKT/subgradient decomposition followed by elimination of incidence-matrix tensions. The most operationally distinctive new nonsmooth theorem is not actually exercised in the new learning experiment, which sets the absolute-switching term to zero. The positive learning theorem is conditional on projection onto an optimal exposed face defined by optimal multipliers; in the implemented problem that face is not known without already having essentially solved the constrained optimization problem. The finite-sample selection theorem is a clean Hoeffding/union-bound wrapper but is not instantiated by the reported stress test. Most importantly, the empirical neural proposals remain extremely poor before classical refinement, and the complete learned pipeline is consistently slower than cold SLSQP at the same certified tolerance.

The revision has therefore succeeded in making the **accepted-control theory** substantially more defensible while making the continued title-level emphasis on **neural value-gradient learning** harder to justify.

I did not find an obvious fatal algebraic error in the main new theorem chain under the stated assumptions. My rejection is principally about novelty, scientific identity, operational content, and the evidentiary burden created by the integrated title.

---

# 1. What R12 genuinely fixes

## 1.1 The full-tree structural scope is now materially broader

Theorem 4.1 no longer relies on a scalar, interior, constant static comparator with strictly positive tariff coefficients. The general formulation allows a compact polyhedron with inequalities, equalities, boundaries, vector tiers, smooth graph coupling, signed coefficients, and arbitrary feasible comparison protocol. Absolute switching enters through saturated or capacity-constrained edge tensions.

This is a real answer to R10 Sections 3 and 24.2--24.6.

## 1.2 Full-tree nonsmooth switching is solved rather than merely requested

The scalar-tree elimination is useful. The cumulative subtree residuals \(H_n\) expose exactly how continuation prices and switching capacities interact, and the critical-friction program is a more meaningful object than the previous two-review threshold.

The nonconstant-comparator example is also valuable because it prevents the incorrect extrapolation that increasing switching friction always makes a fixed outside protocol easier to support.

## 1.3 Comparative statics have improved

R12 now states monotonicity of accepted gain for a zero-switching comparator, monotonicity of optimal switching with friction, effects of tighter commitments, and the distinction between a lower-ray threshold for a constant zero-switching comparator and a bounded interval for an already-changing protocol.

This is closer to the type of structural interpretation I asked for in R10.

## 1.4 The price-capacity margin is a useful quantitative refinement

The margin \(\Delta_\lambda\) improves on a binary normal-cone membership test. The two-sided strong-convexity/smoothness bounds make the residual economically interpretable, and the quadratic subclass gives an exact gain formula when the feasible/sign-clearance conditions are generous enough.

This is one of the strongest genuinely new R12 additions.

## 1.5 The learning discussion is much more honest

The paper explicitly states that the optimal face is not known to the implemented actor, that the residual certificate is method-independent, that the finite-sample validation theorem does not certify arbitrary distribution shift, and that the current data do not establish superiority of derivative weighting.

These qualifications are scientifically appropriate.

## 1.6 Matched accuracy is finally used

The computational comparison now fixes certified error tolerances rather than comparing unlike stopping conditions. The learned pipeline includes generation, projection, exact repair, certification, gating, and the classical refinement that actually occurs. This directly addresses the earlier timing objection.

## 1.7 Reproducibility is not a rejection reason

The package reports 2,682 verified certificates, 35,742 exact subtree checks, 535,658 tier checks, 48 verified static comparators, 432 new deployments, and independent replay that imports neither the optimizer nor numerical linear-algebra libraries. The manuscript and companion are built from ordinary committed source inputs, and the historical supplement is explicitly demoted to an archive.

I would not reject R12 for reproducibility, source integrity, or failure to expose unfavorable outcomes.

---

# 2. The main theoretical theorem is broader, but the mathematical engine remains close to standard convex duality

Theorem 4.1 is correct-looking and useful. It is also, at its mathematical core,

\[
\nabla r(z) \in N_P(z)+\partial(\lambda T)(z),
\]

with the polyhedral normal written in inequality/equality/boundary multipliers and the absolute-value subgradient represented as bounded edge tensions.

The authors themselves correctly credit the subgradient principle and generalized-lasso-style absolute-value duality as standard. The scalar-tree cut result then follows by eliminating edge tensions through the rooted incidence matrix.

That specialization has operational interpretation. But for a flagship Operations Research paper, the question is whether this constitutes a sufficiently deep new structural phenomenon rather than a particularly careful application of known convex-analysis machinery.

I am not yet convinced.

The strongest claim is not that a new optimality principle has been discovered; it is that a familiar optimality system has an interpretable continuation-price/switching-flow representation for this model. That can support a strong paper if it yields nontrivial new algorithms, sharp economic consequences, or a compelling application. R12 has not yet pushed far enough on those consequences.

In particular:

1. the general balance theorem is a KKT/subgradient characterization;
2. the scalar-tree cut form is incidence-matrix elimination;
3. the friction interval is a projection of a linear feasibility system in \((\lambda,s,\mu,\nu,\xi)\);
4. the zero-switching critical friction is a min-max capacity program;
5. the price-capacity margin is a metric projection of the marginal reward onto the same normal-plus-subgradient set.

These are coherent and elegant. I do not think elegance alone establishes the level of conceptual novelty implied by the paper's current breadth and title.

---

# 3. The new nonsmooth theory is not integrated with the new computational study

This is a major R12 problem.

The strongest new structural addition is the full-tree absolute-switching theory. Yet the main noncentered implementation study states explicitly that the computational experiment sets the absolute-switching term to zero.

As a result, the headline new theory and the headline new learning experiment are again only partially connected.

The manuscript does perform structural LP cross-checks for the nonsmooth theorem, including random boundary/signed-coefficient cases and tree threshold tests. Those are useful correctness diagnostics. They are not a computational or operational demonstration of the nonsmooth service-control problem.

At minimum, a serious structural study should show how the critical-friction/cut characterization changes actual accepted decisions on nontrivial service instances. Better would be to compare:

- direct nonlinear optimization with absolute switching;
- the balance/cut certificate;
- continuation-price interpretations;
- how the accepted policy changes as friction crosses critical values;
- which edges saturate and which continuation constraints bind;
- runtime or complexity benefits from exploiting the tree structure.

At present the manuscript adds a strong nonsmooth theorem and then evaluates a smooth \(\lambda=0\) learned-control problem.

That weakens the claim that the theory and computation form a single integrated contribution.

---

# 4. The acceptance-face theorem is mathematically correct-looking but operationally circular

Theorem 6.2 is the main positive bridge from value gradients to decisions. It says that, on the exposed face determined by optimal continuation multipliers, box normals, and switching tensions, metric projection of a predicted actor gives a quadratic regret bound.

This is a useful decomposition. It explains why generic feasibility repair can incur first-order loss.

But the theorem's operational content is much weaker than its placement in the paper suggests.

The face \(\mathcal F_*\) is defined using \(\mu^*,\nu^*,\xi^*,s^*\) at the unknown optimizer \(x^*\). If those optimal prices and tensions have already been verified, then one has already solved or essentially certified the difficult constrained problem whose solution the learned actor was supposed to accelerate.

The paper acknowledges this and does not pretend the actor knows the face. That honesty is important. It also means the theorem does **not** currently provide an implementable reason why value-gradient learning should outperform a generic learned proposal plus classical optimization.

The theorem is best understood as an **ex post structural explanation of when actor error becomes quadratic rather than first-order**, not as a practical learning guarantee.

To make it a true learning result, the authors would need something like:

- a method for identifying the correct face from approximate information without first solving the full problem;
- a stability theorem showing when an estimated face is correct;
- probabilistic active-set identification guarantees;
- an approximate-face regret theorem with explicit misclassification penalties;
- or a certificate-aware training method that provably reduces the relevant continuation-price/switching-face error.

Without one of these, the strongest learning theorem remains conditional on the unavailable object it needs.

---

# 5. The finite-sample pipeline-selection theorem is standard and not instantiated by the experiment

Proposition 6.3 is a correct and clean application of bounded-variable Hoeffding plus a union bound over \(M\) frozen pipelines.

I do not regard it as a major learning-theory contribution.

More importantly, the current experiment is explicitly not an instantiation of the theorem. The stress test reuses four fixed training seeds and four selected graph families; it is not an independent validation study from a declared deployment distribution with an established uniform certificate range \(B\).

The paper says this clearly.

That creates a scientific gap between theorem and evidence. The theorem says what could be certified under independent validation. The experiment does not demonstrate that procedure, report a concrete \(B\), give \(M,n,\delta\), or show that the resulting bound is operationally useful at the scale of the available economic gain.

If pipeline selection is intended to be a title-level positive learning contribution, the paper should actually execute it.

---

# 6. The raw neural actors still fail badly

The new experiment is more extensive and better designed than R10, but it does not rescue the neural candidate generator.

The projection table is stark.

Mean projection gains per discounted service-review are approximately:

- cycle: \(-0.8182\) value, \(-0.7620\) value-gradient;
- random-edge: \(-0.8189\) value, \(-0.7622\) value-gradient;
- geometric: \(-1.4765\) value, \(-1.4383\) value-gradient;
- weighted-block: \(-2.0903\) value, \(-2.0668\) value-gradient.

By contrast, the final classical gains are approximately \(0.0019\)--\(0.0051\).

Thus the average raw/projection actor error is not on the scale of the available operational improvement. It is orders of magnitude larger.

The manuscript also reports that 162 of 384 new learned proposals remain worse than static after weighted projection.

This is not a small transfer degradation. It is evidence that the inherited learned representation is often a poor proposal for the shifted problem class.

The tree-flow diagnostic is more encouraging on the first three families, but it remains negative on weighted block and is not the deployed algorithmic centerpiece.

The paper deserves credit for reporting these failures. The failures nevertheless count against the current claim that value-gradient learning is a major positive contribution.

---

# 7. The final learned pipeline succeeds because classical optimization rescues it

At matched tolerance, the learned and classical pipelines end at essentially the same reward because SLSQP refinement drives them to the same solution quality.

That is exactly what a good fallback should do.

But it means the scientific question is whether the learned warm start reduces the cost of obtaining the certified solution.

It does not.

At \(10^{-7}\) tolerance, median times are:

- cycle: cold SLSQP 13.69 ms; value 19.60 ms; value-gradient 19.41 ms;
- random-edge: 35.78 ms; 49.53 ms; 49.91 ms;
- geometric: 67.84 ms; 88.62 ms; 86.91 ms;
- weighted-block: 113.03 ms; 140.69 ms; 139.06 ms.

The same ordering holds at \(10^{-5}\).

Therefore the complete learned pipeline is consistently slower than cold SLSQP on every reported family while achieving essentially the same final gain.

This is the most important empirical fact in R12.

A learned candidate generator can still be scientifically valuable if it provides robustness, amortization across repeated related solves, better large-scale asymptotics, hardware acceleration, or solution quality unavailable to a classical baseline. R12 currently demonstrates none of those advantages.

The paper instead demonstrates a safe procedure for rejecting or refining poor learned proposals. That is useful engineering, but it is not yet a compelling neural-optimization result.

---

# 8. The current title overstates the role of neural learning

The title remains:

*Neural Differential Utility: Accepted Adaptive Service Control and Certified Value-Gradient Learning.*

After R12, the accepted-control half is stronger. The neural half is weaker as a title claim.

The architecture is inherited, fixed, and deliberately modest. The paper does not claim architectural novelty. Derivative weighting has no statistically resolved advantage. The strongest shifted actors are often badly wrong. Matched-certified-accuracy latency favors cold SLSQP. The residual certificate is method-independent. The face theorem is conditional on an unknown optimal face. The validation theorem is standard concentration and is not executed in the reported experiment.

Under these facts, "Neural Differential Utility" reads more like project branding than the scientific center of the current paper.

I strongly recommend a theory-centered title and a substantial demotion of the neural material unless a future revision produces a genuinely positive learning result.

---

# 9. The paper still has a two-paper identity problem

R12 creates a deeper shared vocabulary than R10: continuation prices, switching tensions, and boundary normals now appear in structural optimality, residual certification, and the acceptance-face decomposition.

That is real progress.

But the two halves still do not depend on one another strongly enough.

The accepted-control theory can stand without neural learning.

The learned-control pipeline can be certified by the residual bound without the new economic interpretation of the continuation prices.

The current computation does not use absolute switching, so the most distinctive new structural theorem is not needed by the learning study.

The finite-sample selection theorem could be attached to almost any bounded a posteriori certificate.

The result remains a strong candidate **accepted adaptive service control** paper plus a separate, honest but empirically unsuccessful **learn-certify-refine** study.

The scientific center should be chosen explicitly.

---

# 10. Scenario-tree scale and algorithmic exploitation remain underdeveloped

The paper has several thousand-node historical examples and a 992-coordinate predecessor stress test, but the new noncentered study uses 21, 60, 90, and 120 contingent tier coordinates.

For the general theorem, the manuscript says the critical-friction program has a linear number of node variables and local balance constraints when subtree sums are represented recursively, but explicitly does not claim a linear-time solution.

That is appropriately cautious. It also leaves an important opportunity unused.

If the tree/cut structure is the main OR contribution, I would expect stronger algorithmic development:

- complexity of computing the critical friction;
- decomposition across services or branches;
- dynamic-programming or flow formulations;
- warm-start behavior as \(\lambda\) varies;
- parametric breakpoints;
- scaling with tree depth and branching;
- comparison against generic LP/QP solvers;
- or exploitable sparsity guarantees.

Without such results, the full-tree theorem is structurally interpretable but computationally underdeveloped.

---

# 11. The price-capacity margin is useful but "sharp" should be interpreted narrowly

Theorem 4.4 is one of the best additions in R12, but its strongest language should stay close to its assumptions.

The upper bound is global under strong convexity. The lower bound depends on feasible step length and preservation of nonzero switching signs. Near a boundary or a switching kink, \(a_{\max}\) can be small, and the lower bound can become much weaker than the unconstrained metric distance suggests.

Exact equality requires the stated quadratic Hessian subclass plus enough clearance to take the full step.

The manuscript does acknowledge these qualifications.

I would nevertheless avoid allowing "sharp price-capacity margin" to be read as a generally exact value-of-adaptation formula. It is an exact threshold residual and a two-sided value bound, becoming exact under a special quadratic/clearance configuration.

That is still useful.

---

# 12. The economic model remains stylized enough that the theory must carry the paper

The institutional assumptions are now clear:

- observable and contractible regime, stock, tier, demand, and fulfillment;
- exogenous regime process;
- externally fixed tariffs;
- no hidden action;
- no private type;
- known feasible polyhedron;
- synthetic demand/service experiments.

These assumptions are legitimate for a structural model.

They also remove many of the economically difficult issues in dynamic service contracts.

The paper therefore needs either exceptional structural theory or compelling operational calibration to clear a flagship bar.

The canonical exact information hierarchy is elegant, but it is synthetic. The new noncentered study is also synthetic. The resource offset and dimensionless forcing make it difficult to assess whether a gain of \(0.002\)--\(0.005\) per discounted service-review is operationally meaningful.

A field calibration is not logically required for a theory paper. In its absence, however, the theoretical contribution has to be correspondingly stronger and more unmistakably new.

---

# 13. The continuation-price formulation is still fundamentally an offline convex program on a scenario tree

The paper uses dynamic language appropriately, and the remaining-budget state is a legitimate recursive representation.

But after fixing the finite exogenous tree, the accepted full-contingent problem is a concave program over a polyhedron with known coefficients.

This matters for positioning.

The novelty is not that a dynamic constrained control problem can be flattened into a scenario-tree convex program, nor that resource/promise states can restore recursion. Those are classical ideas, and the manuscript now says so.

The novelty must therefore lie in the particular service-control structure extracted from the dual system.

R12 has improved that case, but the manuscript should continue to resist language that makes the general constrained dynamic-programming machinery sound newly invented.

---

# 14. The statistical evidence remains descriptive rather than confirmatory

The new crossed bootstrap is much better than the earlier seed-only interval. The manuscript correctly treats graph families as fixed strata and distinguishes training-seed variation from instance variation.

The derivative-weighted minus value-only projection-gain interval still includes zero widely: approximately \([-0.4044,0.4507]\).

Four training seeds are also too few to make strong statements about training variability.

The paper says this.

Therefore no title, abstract, or conclusion should imply that value-gradient supervision has been empirically validated as superior.

The theoretical face result is not a substitute for that empirical finding because it is conditional on a face that the implementation does not know.

---

# 15. Specific technical and presentation comments

## 15.1 Instantiate the pipeline-selection theorem

Give at least one concrete numerical example with declared \(M,n,\delta,B\), report the resulting bound, and compare it with the economic improvement scale. Otherwise Proposition 6.3 remains detached from the empirical paper.

## 15.2 Add a nonzero-absolute-switching computational study

This is the single most obvious missing experiment after R12. Use the full-tree theorem on the model it was created for.

## 15.3 Report face-identification diagnostics if learning remains central

For each learned proposal, report whether its active continuation constraints, box faces, and switching signs agree with the certified optimum. This would directly test the mechanism behind Theorem 6.2.

## 15.4 Separate candidate quality from refinement quality

The current final table makes all learned pipelines look equally successful after refinement. Add a table with:

- fraction certified immediately;
- fraction selecting static;
- fraction requiring refinement;
- iterations/time saved or added relative to cold solve;
- final gap;
- warm-start distance to optimum;
- active-set/face accuracy.

## 15.5 Explain why the first four frozen R10 seeds are scientifically representative

The manuscript says they were not selected for favorable performance. That is good. Still explain why four seeds are enough for this transfer study and retain the limitation prominently.

## 15.6 Develop the critical-friction algorithmically

Even if no linear-time theorem is available, give computational complexity for the LP formulation, exploit the tree structure, and benchmark it against a generic formulation.

## 15.7 Tighten literature positioning around graph total variation and parametric convex optimization

The generalized-lasso citation is useful, but the manuscript should also make clear which aspects of the tree-capacity/friction path are inherited from known total-variation/fused-lasso/network-flow duality and which are genuinely new because of continuation participation.

## 15.8 Keep "certified" attached to the correct object

The deterministic certificate certifies a **policy**, not the learning process. The validation proposition can certify expected regret of a **frozen complete pipeline** under its sampling assumptions. These are different claims and should remain linguistically separated throughout.

## 15.9 Clarify operational units

The synthetic experiments should explain the scale of gains and costs. A dimensionless gain of \(0.003\) can be economically trivial or important depending on normalization.

## 15.10 Keep the historical supplement out of the scientific burden

R12 improves this substantially. The final submission should continue moving toward one self-contained current paper plus a focused EC.

---

# 16. What I would require for a credible theory-centered resubmission

This is now the more promising route.

1. **Rename and recenter the paper around accepted adaptive service control.**
2. **Treat the full-tree balance/cut/friction theory as the main contribution.**
3. **Exercise that theory computationally with nonzero absolute switching.**
4. **Develop at least one algorithmic consequence beyond generic LP/QP solution.**
5. **Use the price-capacity margin to derive interpretable comparative statics or decision rules.**
6. **Keep the exact canonical information hierarchy as an illustration.**
7. **Move most neural architecture details and negative transfer diagnostics to the EC unless they are needed to demonstrate a certification workflow.**
8. **Preferably add a calibrated service example or a richer synthetic design with economically interpretable scales.**

A paper following this route could be much more coherent.

---

# 17. What I would require if the authors insist on a learning-centered identity

The bar is higher because the current experiments are negative.

At least one of the following is needed:

1. a theorem making the optimal acceptance face identifiable or approximately usable without first solving the full problem;
2. a certificate-aware learning method that reduces continuation-price/face error;
3. a statistically resolved quality advantage for derivative supervision;
4. a matched-certified-accuracy speed advantage;
5. a clear amortization advantage over many repeated solves;
6. a scale regime where the classical fallback is no longer practical but the learned method remains useful;
7. an actually executed independent-validation selection experiment with a nonvacuous bound.

Without such a result, the neural component should not remain coequal with the accepted-control theory.

---

# 18. Reproducibility assessment

This remains a strength.

I found no reason to doubt that the reported package is internally traceable. The manuscript exposes negative outcomes, records environment and timing details, separates historical material from the active EC, uses ordinary committed TeX inputs, and supplies independent rational/fraction-based checking of the declared policy certificates.

The package discipline is substantially above average.

That should be preserved.

It should not be used as a substitute for scientific novelty.

---

# 19. Overall assessment

R12 is the strongest version I have reviewed in this sequence.

The authors have successfully removed the narrowest mathematical limitation that drove the R10 report. The full-tree continuation/switching balance, scalar cut characterization, nonconstant-comparator friction interval, and price-capacity margin are serious additions. The manuscript is also admirably transparent about what the learning experiments do not show.

That transparency leads directly to the remaining conclusion.

The current paper contains a potentially strong accepted adaptive service-control theory paper. It does **not** yet contain a comparably strong neural-learning result.

The positive learning theorem is conditional on an optimal exposed face that the implemented actor does not know. The statistical pipeline theorem is standard and not instantiated. The new learned actors are often catastrophically poor before refinement. The full learned pipeline is slower than cold SLSQP at matched certified accuracy. The most distinctive new nonsmooth theory is not used in the main computational study. No field application offsets these weaknesses.

For Operations Research, I therefore still do not find the integrated manuscript sufficiently coherent or sufficiently strong under its current title and contribution claims.

**Recommendation: Reject in the present form. Encourage a substantially restructured, theory-centered resubmission focused on accepted adaptive service control, with neural learning demoted unless a future revision establishes an independent positive learning contribution.**
