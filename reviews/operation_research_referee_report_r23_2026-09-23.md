# Confidential Referee Report for Operations Research

**Manuscript:** *Accepted Service Adaptation with Neural Differential Utility: Continuation Prices and Robust Certified Gains*  
**Review date:** September 23, 2026  
**Repository:** TrillionniumFoundation/NDU  
**Reviewed branch:** revision/ndu-operations-research-r23-20260923  
**Reviewed SHA:** b4165155612fea340a8832bbe7a8b13fe2b9259b  
**Prior report considered:** reviews/operation_research_referee_report_r20_2026-09-23.md  
**Current recommendation:** **Reject in the present form. I would not recommend another incremental revision cycle under the current integrated manuscript architecture. I would encourage a substantially refocused new submission centered on the accepted-control theory and certification contribution.**

## Executive assessment

R23 is a serious and technically competent revision. It directly addresses many concrete deficiencies identified in the previous report. The paper now has a completed review object rather than a plan-only branch; the strongest classical baseline is structure-aware; the full accepted-polyhedron scaling experiment reaches 1,023 nodes; the economic comparator is a reoptimized time-only amendment rather than an arbitrary outside protocol; the final statistical validation uses deterministic frozen ensembles and independent samples; and the new R23 section studies simultaneous objective and acceptance-coefficient misspecification rather than relabeling covariate shift as robustness. The authors also preserve adverse evidence instead of suppressing it.

I did not find an obvious fatal algebraic contradiction in the principal new mathematical blocks I checked. In particular, the global resource-price bridge, the complete dual-repair result, and the R23 robust-comparator theorem appear internally coherent under their stated assumptions. The R23 vertex argument is valid: vertex feasibility protects all affine interior models, and a common outer class with vertex upper bounds yields a lower gain certificate against the true model-specific restricted optimum. The exact replay and provenance machinery are unusually strong.

The remaining problem is therefore not that the revision is incomplete or careless. It is that the paper still does not establish a sufficiently sharp, necessary, and unified scientific contribution for Operations Research.

The revision has now made the central tension impossible to ignore. The most distinctive part of the manuscript is the accepted-control geometry and certification theory. The neural/value-gradient component is neither necessary for that theory nor empirically preferred. The strongest nominal surrogate is still non-neural direct-price approximation, the strongest strict-target computational baseline is classical lifted continuation, and the strongest R23 robust decision rule is classical robust maximin. The paper repeatedly and correctly says that it does not claim neural superiority. That candor is commendable, but it also removes the main reason to retain “Neural Differential Utility” as an organizing scientific identity.

R23 additionally adds a robust-optimization layer. The new theorem is correct and useful as a certification device, but its mathematical content is an elementary combination of affine uncertainty, vertex feasibility, a union-containing outer comparator class, and weak duality. The counterexample is instructive, but this is not by itself a major robust-optimization contribution. Empirically, the uncertainty set is designed rather than estimated, and the classical robust-maximin rule is stronger than both protected learned rules at every positive radius.

My view is therefore sharper than in the previous report: the revision has successfully removed many technical objections, but in doing so it has shown that the paper should be rebuilt around accepted-service expansion, continuation prices, transfer coordinates, and auditable certification. The current integrated manuscript still reads like several substantial papers forced into one package.

# 1. Review object, provenance, and reproducibility are no longer concerns

This R23 branch is a complete manuscript revision. The reviewed head is SHA b4165155612fea340a8832bbe7a8b13fe2b9259b. The root main and electronic-companion sources are R23 artifacts. The package check reports:

- 40 main-text pages excluding references;
- 40 companion pages;
- 179 abstract words;
- 70 preserved mathematical blocks;
- all references resolved;
- no overfull text lines;
- 1,152 robust policy replays;
- 3,072 vertex comparator certificates;
- 768 nominal diagnostics;
- six negative controls rejected;
- no recorded failed robust solves.

The final-sha status is successful. I therefore do not base any criticism below on an incomplete branch, missing execution, or unverifiable manuscript object.

This is a meaningful improvement over the R20 plan-only branch reviewed previously.

# 2. R23 genuinely resolves several prior objections

The previous report asked for stronger classical baselines, scaling on the actual general polyhedral class, a meaningful optimized comparator, a deployable deterministic validation target, and a misspecification study. R22/R23 now provide all of these in some form.

First, the classical baseline is materially stronger. The lifted formulation keeps the resource equality explicitly, retains primal and dual continuation state, uses cached matrices, and includes all prediction, solve, repair, audit, polishing, and fallback work in the reported pipeline.

Second, the paper no longer relies on the old scalar star to claim scalability. The full-polyhedron study varies node count, service dimension, resource rank, capacity count, and curvature, reaching 1,023 nodes.

Third, the nominal economic validation now compares against a reoptimized accepted time-only amendment. This addresses the earlier concern that gain over a weak outside protocol could be economically uninformative.

Fourth, the positive finite-sample claim now concerns two deterministic eight-model ensembles fixed before final validation, rather than a randomized frozen fleet constructed largely for statistical convenience.

Fifth, R23 does study genuine model-coefficient misspecification. Reward, friction, participation coefficients, and capacity budgets change together. This is substantively different from the earlier context-distribution shift.

These are real corrections. They should be credited.

# 3. The paper's central scientific identity is still misaligned with its own evidence

The title still places “Neural Differential Utility” at the center. The paper now repeatedly states that a neural critic is only one possible proposal mechanism and is not necessary for the guarantee. That is scientifically responsible, but it leaves the title and contribution hierarchy difficult to defend.

At the 63-node matched-cost benchmark, the strongest observed coarse classical mean is the lifted continuation method at 7.539 ms. RBF direct price is 8.542 ms. Tanh value-gradient is 38.503 ms. At the strict target, lifted continuation is 18.941 ms, while RBF direct is 36.492 ms and tanh value-gradient is 39.541 ms.

More importantly, after the fixed-primal price repair but before full fallback, every surrogate method has a 0.00% strict-target pass rate. The learned methods therefore still require full refinement in every timed strict case. The classical lifted method remains substantially cheaper in the matched study.

The new robust experiment strengthens the same conclusion. At 25% uncertainty radius, the mean certified gain lower bounds are approximately:

- protected tanh-gradient: 0.808414;
- protected RBF-direct: 0.815943;
- classical robust maximin: 0.848251.

The minimum lower bounds show the same ordering: approximately 0.225658, 0.278173, and 0.378572.

Thus the current empirical hierarchy is:

1. accepted-control structure and certification are useful;
2. direct-price approximation is more effective than the neural value-gradient route;
3. strong classical optimization remains at least as important and often stronger.

That is a coherent scientific story. It is not a neural-centered story.

If the authors insist on retaining the neural material, I would treat it as one implementation route in an accepted-control/certification paper. I would not continue to organize the paper around a named neural paradigm that the experiments do not support as necessary or preferred.

# 4. The R23 robust theorem is valid but too elementary to carry the revision's novelty burden

The new theorem is useful. It also has a short proof because the essential ingredients are elementary.

The argument is:

1. affine vertex feasibility implies feasibility for every convex combination of uncertainty vertices;
2. a common outer set contains every model-specific restricted comparator class;
3. vertex upper bounds on that common outer set upper-bound the interior model-specific restricted optimum after convex combination;
4. subtracting those bounds gives a worst-vertex lower certificate.

I believe this argument is correct. I also believe it is much closer to a careful certification lemma than to a major robust-optimization theorem.

The interior-comparator counterexample is helpful because it exposes a real mistake one could make: separately optimizing vertex-specific restricted comparators need not protect an interior comparator when the feasible set itself changes. But the remedy is exactly to upper-bound all comparators over one containing class. That is an important implementation detail, not a deep new robust-optimization principle.

The manuscript says this explicitly, which is good. The editorial consequence is that R23 cannot use the robust layer to solve the more fundamental novelty problem of the integrated paper.

# 5. The R23 robustness experiment is a designed stress test, not evidence about operational misspecification

The new experiment is much better labeled than earlier robustness language. Nevertheless, its evidentiary scope is narrow.

The uncertainty cube is designed by the authors. The four radii are 0, 6.25%, 12.5%, and 25%. The perturbation directions are deterministic algebraic patterns in reward, friction, participation coefficients, and capacities. There is no empirical estimation of this uncertainty set, no coverage analysis, no observed misspecification distribution, and no external validation that these coefficient errors resemble a real service system.

The most striking descriptive result is that both unprotected nominal learned rules are infeasible in 100% of recorded contexts at every positive radius. This demonstrates that nominal feasibility is not robust to the declared perturbations. It does not demonstrate that nominal policies would fail with that frequency in a real deployment. The uncertainty design is sufficiently adversarial that universal violation is partly a property of the test construction.

This is completely acceptable as a theorem stress test. It is not enough to establish operational robustness in the empirical sense.

The paper acknowledges this limitation, but the new robust section is now large enough that the reader needs a clearer distinction between:

- mathematical truth-in-set robustness;
- sensitivity to a deliberately constructed perturbation family;
- statistically calibrated uncertainty;
- field robustness under model misspecification.

Only the first two are established.

# 6. The robust extension demonstrates the strength of the optimization/certification layer more than the strength of learning

The protected tanh and RBF rules use frozen predicted nominal prices, but the actual guarantee comes from solving over the robust accepted set, exact repair, vertex evaluation, and certified comparator upper bounds.

That is valuable. It also means the robust result is primarily a result about the accepted-response and certification machinery.

The same R23 experiment includes a classical robust-maximin QP that is stronger in the reported gain metric. The learned predictor is therefore not doing the essential scientific work in the robust result. It is supplying one proposal price to a robust optimization layer that already has to enforce all uncertain constraints and audit the final decision.

A top-journal paper should be explicit about what learning adds after this robust layer is present. At present I do not see a demonstrated advantage in robustness, accuracy, runtime, or statistical reliability.

# 7. The scaling experiment is useful but still does not establish an amortized learning advantage

The new full-class scaling table is a substantial improvement. It does not, however, support a strong learned-optimization claim.

At 1,023 nodes and two services, strict-target mean costs are approximately:

- dense cold: 23,474.91 ms;
- dense previous: 17,741.59 ms;
- lifted continuation: 3,758.21 ms;
- tanh: 4,018.75 ms;
- RBF: 3,987.11 ms.

The learning methods are close to the lifted classical baseline, but they do not beat it there.

There are individual configurations where a learned method has a smaller reported mean than lifted continuation. For example, in the 127-node, two-service, 12-resource, eight-capacity case, tanh is 139.52 ms versus 152.99 ms for lifted continuation. But each table entry uses only eight held-out attempts. No uncertainty interval or repeated independent training study supports an algorithmic superiority claim from such differences.

The more important point is that these pipelines include fallback. If a learned proposal cannot avoid the expensive refinement reliably, then its computational role is a warm-start or proposal heuristic. It should be compared and analyzed as such.

I would like to see an amortization analysis against the strongest lifted classical baseline across query volume and scale, including:

- exact label-generation cost;
- model-fit cost;
- setup cost;
- memory;
- repeated-query online cost;
- failure/fallback probability;
- and confidence intervals for timing differences.

The old RBF break-even number is correctly retired. A new break-even analysis against the strongest current baseline is the relevant quantity if computational acceleration is to remain part of the paper.

# 8. The positive economic-gain validation does not identify the value of learning

The deterministic validation is statistically cleaner and economically more meaningful than before. The positive lower bounds against the optimized time-only comparator are useful evidence that the expanded accepted policy class creates value.

But this is primarily evidence for the value of **adaptivity and policy-class expansion**, not for the value of a neural or learned implementation.

The IID mean gain lower bounds are about 1.334651 and 1.337039 for the tanh-gradient and RBF ensembles, while their regret upper bounds are 0.002501 and 0.000113. The learned methods are very close to the full accepted optimum in this synthetic model, so both inherit almost all of the expansion value.

That is a good computational approximation result. It does not show that learning creates the expansion value. The expansion value is generated by the accepted-control model and exists even with exact classical optimization.

The paper should separate these questions more aggressively:

1. How much value comes from expanding the accepted policy class?
2. How much of that value can a cheap approximate decision recover?
3. What is the cheapest reliable way to recover it?
4. Does learning outperform structure-aware classical continuation after offline cost is charged?

At present the first question has the strongest answer, while the fourth remains unfavorable or unresolved.

# 9. The cost and operational status of robust comparator certification need sharper treatment

Each R23 robust gain certificate uses eight outer-class comparator solves per context and radius. The paper says these are charged separately and not hidden as free labels. Good.

But the operational interpretation is still unclear.

If these comparator upper bounds are required online before a decision can be declared to have certified gain against the true restricted optimum, then the certificate itself requires a nontrivial batch of optimization work. In that case, the learned proposal cannot plausibly be advertised as a low-cost online substitute without showing total end-to-end robust certification time.

If, instead, those comparator solves are an evaluation device used offline to assess a frozen policy class, then the paper should say clearly that the pointwise economic guarantee is not necessarily the online deployment protocol.

This distinction matters because the manuscript uses “implemented,” “auditable,” and “certified” in an operational sense. A certificate whose comparator side is more expensive than solving the candidate policy may still be scientifically useful, but its role is different.

R23 explicitly declines to make a matched-runtime claim. I agree with that choice. I would go further and remove any residual implication that the robust learned rule is computationally attractive until total robust certification cost is reported against the classical maximin alternative.

# 10. The conservatism of the common outer comparator is not quantified

The common outer class is the correct way to obtain a uniform certificate against model-specific restricted optima under changing acceptance sets. However, positive radius enlarges that outer class and can make the restricted upper bound conservative.

The manuscript acknowledges this qualitatively. It does not quantify how conservative the bound is.

This matters because the reported robust gain lower bound is not the actual worst-case gain; it is a lower bound formed by subtracting an outer-class upper bound. The strength of the scientific conclusion depends on whether that upper bound is reasonably tight.

I would ask for a diagnostic on sampled interior coefficient realizations:

- solve the true model-specific restricted comparator directly;
- compare its value with the outer-class certified upper bound;
- report the distribution of the resulting certificate slack as the radius grows.

This would not change theorem validity. It would tell the reader whether the robust economic certificate is informative or merely safe.

# 11. The novelty boundary of the accepted-control theory remains too diffuse

The accepted-control material is, in my view, the strongest part of the paper. It also still needs a sharper novelty claim.

The manuscript now does a much better job of acknowledging standard ingredients:

- convex KKT and normal-cone conditions;
- total-variation duality;
- envelope/Danskin sensitivity;
- strong-convexity stability;
- Fenchel/Bregman identities;
- projected-gradient convergence;
- robust vertex arguments;
- Hoeffding concentration.

The theorem-level comparison table is helpful. But many rows still describe the “present addition” as a model-specific packaging or accepted-control consequence. That may be publishable if the consequence itself is structurally new and important. The paper needs to identify exactly which one or two consequences meet that standard.

The most promising candidates are not the neural bridge or the R23 robust lemma. They are:

- the continuation-price / switching-capacity characterization specialized to accepted service adaptation;
- the exact continuation-transfer coordinates;
- the constructive tension repair and gain witness;
- the connection between accepted expansion value and auditable implemented decisions.

If those are the contribution, the paper should be rewritten so that a reader can state the main theorem in one sentence without mentioning neural networks, robust maximin, frozen ensembles, historical stars, and several generations of certificate repair.

The current manuscript instead presents a long chain in which several links are standard and several others are application-specific. The reader has to infer which link is supposed to be the top-journal contribution.

# 12. The paper still contains multiple substantial papers

The authors argue that everything serves one target: accepted expansion relative to an optimized restricted contract. That is a coherent umbrella. It does not make the manuscript scientifically unitary.

The main paper currently contains, among other things:

1. a canonical inventory/service-contract model;
2. exact accepted information values;
3. a customer-neutral adaptive-direction theorem;
4. continuation participation on a large history tree;
5. general polyhedral KKT/switching balance;
6. subtree cuts and critical friction;
7. exact continuation-flow coordinates;
8. constructive two-pass tension repair;
9. a general resource-price/value-gradient bridge;
10. an inexact-response theorem;
11. a Fenchel certificate decomposition;
12. fixed-block and complete dual repair;
13. deterministic validation theory;
14. full-polyhedron scaling;
15. joint model-coefficient robustness;
16. a robust outer-comparator theorem;
17. multiple large computational studies.

The main manuscript is at the 40-page nonreference limit, and the companion is another 40 pages.

This is not merely a formatting problem. The breadth prevents each contribution from receiving the literature comparison and interpretation it would need to stand independently at Operations Research.

I continue to believe that a theory-centered paper would be substantially stronger.

# 13. The synthetic exact-model setting still raises the burden on methodological novelty

The paper is transparent that all data are synthetic. The operational model is known. Training labels are produced by exact optimization. The acceptance constraints, objective family, and perturbation set are designed by the authors.

R22 adds covariate shift. R23 adds coefficient misspecification. These are meaningful stress tests, but neither changes the fundamental fact that the study is a surrogate-learning experiment on a known parametric optimization model.

That is not disqualifying for a theory/methods paper. It does mean the learning contribution must earn its place through one of the following:

- a new learning theorem;
- a decisive computational advantage;
- a new robustness advantage;
- or a practically compelling repeated-optimization regime.

The current paper does not establish any of these for the neural route.

The accepted-control theory does not need field data to be interesting. The neural framing does.

# 14. Specific technical and presentation comments

### 14.1 The title should follow the scientific contribution

“Accepted Service Adaptation with Neural Differential Utility” still overstates the role of the neural construction. The paper's own tables and conclusions say that neural approximation is neither necessary nor computationally superior.

A title centered on accepted service adaptation, continuation prices, or certified accepted expansion would be more faithful to the manuscript.

### 14.2 The R23 theorem should be labeled as a certification lemma rather than allowed to appear as a major robust-optimization result

The theorem is correct, but its proof is essentially one paragraph of affine interpolation and weak duality. Its importance is in preventing an incorrect comparator construction. The paper should present it at that scale.

### 14.3 Quantify robust outer-bound tightness

As noted above, report the gap between the common-outer-class upper certificate and directly optimized model-specific restricted comparators on sampled interior models.

### 14.4 Report variability in the scaling table

Eight held-out contexts per structural configuration are too few for small timing differences to be scientifically persuasive. Report medians, dispersion, and paired differences, or increase the repeated sample size.

### 14.5 Separate warm-start value from predictor value

When a learned proposal falls back to the same full optimization, the relevant question is how much work the proposal saves conditional on fallback and how often it avoids fallback. Report these components explicitly across scale.

### 14.6 The exact-label information budget remains asymmetric

Derivative and direct-price methods are trained on optimizer-generated statistics. This is legitimate, but the paper should emphasize that these labels are not free information. A value-gradient construction does not discover a resource statistic that the system otherwise lacks; the exact optimizer supplies it during training.

### 14.7 Clarify the deployment role of comparator solves

State unambiguously whether the time-only and robust outer-comparator optimization is part of each online certified decision or only part of offline evaluation.

### 14.8 The deterministic validation result is conditional on the frozen models

The manuscript now says this correctly. Keep that language prominent. The result is not an algorithm-level guarantee over retraining, hyperparameter variation, or model selection.

### 14.9 Avoid using “global” without immediately restating the objective assumptions

The global bridge is global over the accepted polyhedron and across face/switching changes under strong convexity and smooth coupling. It is not a general guarantee for every accepted objective developed earlier in the paper. The current text is mostly careful; the abstract-level wording should remain equally precise.

### 14.10 Reproducibility strength should not substitute for scientific priority

The exact replay, preservation map, mutation controls, hashes, and CI are excellent. They establish that the reported calculations are auditable. They do not by themselves establish novelty, operational necessity, or journal fit.

# 15. What would change my recommendation

I would reconsider a new submission built around a much narrower accepted-control contribution.

A strong theory-centered version could contain:

- the optimized restricted comparator and accepted expansion problem;
- continuation participation and the general balance theorem;
- subtree/transfer structure and critical friction;
- exact continuation-flow coordinates;
- one constructive repair/gain theorem;
- one general certification theorem connecting an implemented feasible decision to the optimized restricted comparator;
- a compact synthetic example and one scaling experiment.

The neural/value-gradient material could then become a short illustration or a separate learning-augmented optimization paper.

If the authors instead want a learning-centered paper, the burden is higher. I would want:

- a title that does not privilege neural critics unless they win on a meaningful criterion;
- a new break-even analysis against lifted primal-dual continuation;
- substantially more timing repetitions and paired uncertainty intervals;
- a setting where exact certified optimization is materially expensive relative to amortized learning;
- a clear online role for certificates and comparator solves;
- calibrated or data-derived uncertainty, or a new learning theorem that justifies the surrogate beyond synthetic exact-model regression;
- and a contribution statement framed around learned resource statistics rather than “Neural Differential Utility.”

The current manuscript has enough strong material for a good paper. I do not think the correct next step is to add more layers to the current 40+40-page integrated version.

# 16. Recommendation to the editor

R23 is substantially better than the R19 manuscript reviewed through the prior R20 branch. It resolves most of the concrete experimental and validation deficiencies that I identified previously. The current mathematical statements I checked appear internally coherent, the reproducibility record is unusually strong, the optimized comparator is now economically meaningful, the classical baseline is much stronger, and the new misspecification section is honestly labeled.

Those improvements also clarify the editorial problem. The evidence does not support a neural-centered paper. Direct-price approximation remains stronger than the neural value-gradient route, lifted classical continuation remains the strongest strict-target computational baseline in the main matched study, and classical robust maximin is strongest in the R23 robustness experiment. The new robust theorem is valid but elementary. The manuscript's most distinctive contribution is the accepted-control geometry and certification structure, yet that contribution is diluted by an extensive learning, validation, robustness, and historical apparatus.

I therefore recommend **rejection in the present form, without another incremental major-revision cycle on the same integrated manuscript**.

I would encourage the authors to submit a substantially refocused paper centered on accepted service adaptation, continuation prices, transfer coordinates, critical friction, and auditable economic-gain certification. That version could be significantly stronger scientifically even if it were shorter and contained less machine learning.

**Decision recommendation: Reject; encourage a new, sharply refocused submission rather than R24 of the current architecture.**
