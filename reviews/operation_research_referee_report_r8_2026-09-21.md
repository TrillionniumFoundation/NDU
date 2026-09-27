# Referee Report on R7 Scientific Revision

**Journal:** Operations Research  
**Manuscript:** *Neural Differential Utility: Accepted Dynamic Service Contracts and Certified Value-Gradient Learning*  
**Reviewed branch:** revision/ndu-operations-research-r7-20260921  
**Reviewed head:** 26be0b3e3f0eb74134627099ac7d6901ace5d85e  
**Review branch:** review/operation-research-r8-harsh-20260921  
**Review date:** 2026-09-21  
**Round:** R8 external harsh review of the scientific R7 revision

## Recommendation

**Reject in its present form. I would not recommend another incremental revision of the same manuscript architecture. A substantially reconceived paper could be worth a fresh evaluation, but the authors need to choose what the paper actually is.**

R7 is materially stronger than R6. Several objections from the prior report are now genuinely closed rather than cosmetically answered. In particular, I find the new accepted continuous information hierarchy to be a real scientific advance over the previous grid-only comparison; the customer-exit extension addresses a serious institutional objection; the portfolio certificate is now decision-scale rather than vacuous; and the value-only/value-gradient comparison finally uses the same raw oracle observations.

Those repairs matter. My recommendation is nevertheless negative for a different reason than in the previous round.

The current paper still attempts to carry three claims at once:

1. a theory of accepted adaptive service contracts;
2. a structural paper on one-dimensional persistent adjustment and exact certification; and
3. a neural/value-gradient computational contribution.

The first component has become credible. The second contains several useful, if mostly specialized, mathematical results. The third is still not convincing as an Operations Research contribution, and it remains prominent enough in the title, abstract, and contribution structure that it cannot be treated as a minor appendix.

More importantly, after reading the implementation rather than only the tables, I believe the computational comparison is not yet designed fairly enough to support the claimed repeated-solve advantage. The learned actor is a fitted degree-12 polynomial approximation to a known matrix inverse. The analytic degree-12 Chebyshev method uses essentially the same computational representation without training. Conjugate gradients are only modestly slower and are orders of magnitude more accurate. Direct methods are timed with a fresh factorization inside each call, even though the experiment is explicitly framed as repeated decisions on a fixed service-dependency graph, where factorization reuse is the natural comparator.

Thus the paper has moved from "the neural certificate is too loose" to a more fundamental issue: **the new certificate is tight enough, but the experiment does not establish that learning is needed, algorithmically novel, statistically beneficial, or operationally preferable.**

That distinction is important.

---

# 1. What R7 genuinely fixes

I begin with the positive changes because the report should not recycle objections that are no longer valid.

## 1.1 The accepted information hierarchy is now the right comparison

The paper now solves static, time-only, time-regime, and full inherited-state classes under the same customer-utility, filled-demand, and physical-cost commitments. The reported rewards are

- static: -5.870110973;
- time only: -5.869294096;
- time-regime: -5.252736080;
- full inherited state: -5.233445701.

The increments are therefore approximately

- time: 0.000816877;
- current regime: 0.616558016;
- inherited tier: 0.019290379.

This closes the previous objection that the paper was borrowing an inherited-state increment from the unconstrained provider relaxation and then narrating it as part of the accepted Pareto gain.

The new result is also intellectually useful because it shows that inherited-tier information accounts for only about three percent of the total accepted improvement. Most of the gain is ordinary current-regime reallocation under a fixed payment budget. The manuscript now says this explicitly.

## 1.2 The continuous deterministic result is stronger than the old coarse randomized result

R7 no longer depends on the one-state lottery from the 0.1 tier menu for its headline economic effect. The continuous accepted optimum is deterministic and improves provider reward by about 0.636665272 relative to the optimized continuous static contract while preserving customer utility, service, and physical cost.

This is substantially cleaner than the earlier finite-menu statement.

## 1.3 Continuation participation is now treated seriously

The customer-exit extension is a meaningful response to the commitment objection. The paper imposes 3,280 history-specific continuation constraints on the eight-review regime tree and reports a deterministic feasible protocol with gain about 0.453078763 and an exact weighted-residual upper gap below 6.95e-7.

The finite-tree formulation is standard convex quadratic optimization, but it is the correct constraint system for the stated outside option. I do not see an obvious algebraic defect in the weighted residual bound from the committed source.

## 1.4 The learning certificate is now economically scaled

The old finite-chain residual certificate could be formally true while being too large to support a decision. R7's portfolio certificate is different. It gives per-service loss bounds below 1e-6 while the gain over the optimized uniform tier is about 1.6e-2 per service.

That is the right order-of-magnitude comparison.

## 1.5 Equal raw oracle access is now correctly implemented

The new value-only and value-gradient fits receive the same three scalar teacher values per training graph. The directional derivative term is constructed from those same values. This closes the previous unequal-information objection.

However, closing the information-fairness objection exposes a new result: the gradient weighting itself does not produce a statistically established benefit. I return to that below.

---

# 2. The principal blocker: the "neural value-gradient" problem is a fitted polynomial inverse of a known quadratic system

The learning experiment is mathematically transparent enough that its limitation is now easy to state.

At deployment, the accepted portfolio update is the strictly concave quadratic program

a^T theta - theta^T K theta + linear terms,

with

K = (m + lambda) I + zeta L,

where L is a known graph Laplacian. The unconstrained Lagrangian solution is proportional to K^{-1} applied to two right-hand sides. The learned critic replaces K^{-1} with a degree-12 polynomial p_c(K), whose thirteen coefficients are fitted by least squares.

This is not a generic neural approximation problem. It is a data-fitted polynomial approximation to a known scalar inverse function over a known spectral interval.

The source code makes this explicit:

- the feature map is a Chebyshev recurrence;
- the readout has exactly thirteen coefficients;
- the teacher value is generated with a sparse LU factorization of K;
- the analytic comparison is the degree-12 Chebyshev inverse on the same spectral interval;
- the actor is one-half p_c(K)b.

The model therefore already knows the operator family, the spectral interval, the exact functional form that must be approximated, and the fact that a polynomial functional calculus is appropriate.

I do not object to this as an engineering approximation. I object to presenting it as a central learning contribution without showing why data fitting adds something scientifically unavailable from numerical linear algebra.

The manuscript itself acknowledges that polynomial filtering is established. Once that is conceded, the burden is to show one of the following:

1. the learned polynomial is materially better than a deterministic polynomial chosen from the known spectrum;
2. the learned representation transfers to operator families where the inverse is not analytically specified;
3. the learned critic solves a genuinely dynamic nonlinear control problem where the value function is unknown;
4. the gradient supervision has a robust statistical or computational benefit; or
5. the learned policy provides an operational advantage after fair amortization and certification costs.

R7 does not establish any of these.

---

# 3. The reported benchmark does not show a meaningful advantage for learning

The 1,024-coordinate table is especially revealing.

The reported rows are approximately:

| Method | Mean loss/service | Max bound/service | Time |
|---|---:|---:|---:|
| learned value-gradient | 1.52e-8 | 8.04e-7 | 1.214 ms |
| learned value-only | 1.68e-8 | 9.01e-7 | 1.222 ms |
| analytic Chebyshev | 2.69e-8 | 3.67e-7 | 1.220 ms |
| conjugate gradient | 6.11e-10 | 3.46e-9 | 1.524 ms |
| sparse direct | approximately 0 | 7.80e-12 | 7.619 ms |
| dense Cholesky | approximately 0 | 7.80e-12 | 18.010 ms |

This table does not support the prominence of the learned method.

## 3.1 Analytic Chebyshev is essentially equally fast and needs no training

The analytic degree-12 Chebyshev inverse takes about 1.220 ms, essentially identical to the learned value-gradient actor at 1.214 ms.

It also has a **smaller maximum certified bound** than the learned actor: approximately 3.67e-7 versus 8.04e-7 per service.

The learned method has a somewhat lower mean realized loss on these four test graphs, but there is no broad statistical experiment showing that this advantage survives over graph draws, tariff distributions, spectral ranges, or topology families.

The obvious question for an Operations Research reader is therefore:

**Why train thirteen coefficients at all when a deterministic degree-12 approximation is equally fast, simpler, reproducible without data, and better in the worst certified bound reported by the paper?**

The manuscript does not answer this.

## 3.2 Conjugate gradients are only modestly slower and dramatically more accurate

The learned actor is about 0.31 ms faster than the reported CG implementation at d=1024. In exchange, CG's mean loss is roughly twenty-five times smaller, and its maximum certified bound is more than two orders of magnitude smaller.

A 1.21 ms versus 1.52 ms comparison on one CPU environment, using the median of only three calls, is not enough to establish an operationally meaningful speed advantage.

The difference is especially weak because the experiment does not report:

- timing distributions;
- warm-up effects;
- cache effects;
- repeated online horizons;
- batched decisions;
- preconditioning;
- warm starts;
- tolerance-performance curves;
- hardware variation;
- or an application-level latency requirement for which 0.3 ms matters.

## 3.3 The direct-solver benchmark is not fair for a repeated-solve claim

This is a serious implementation issue.

In the committed portfolio code, the sparse direct baseline is implemented with a solve call that factorizes K inside each invocation. The dense Cholesky baseline likewise constructs the factorization inside the solve function.

By contrast, the learned and analytic polynomial methods have no comparable per-call factorization setup.

For a fixed service-dependency graph, K is fixed. The paper explicitly motivates the actor as useful for repeated decisions. In exactly that setting, a direct factorization should be cached once and reused for new right-hand sides and new payment calibration steps.

The training code itself already uses a reusable sparse LU factorization when producing teacher values, so the implementation is aware that this is possible.

The correct benchmark should separate:

- one-time setup/factorization cost;
- amortized per-decision triangular solves;
- repeated right-hand-side cost;
- changing-graph versus fixed-graph regimes.

Without this decomposition, the 7.62 ms sparse-direct number materially overstates the repeated online cost of the natural direct baseline.

The same concern applies to dense Cholesky.

This problem is not a minor timing-detail issue. The paper's computational narrative is specifically that a compact learned representation offers a repeated-solve tradeoff. That tradeoff cannot be evaluated with a baseline that is forced to refactorize every time.

## 3.4 The certificate cost is excluded from the timing

The learned method's scientific claim is not merely "fast approximate action"; it is "certified accepted action."

The timing excludes the independent rational audit.

That exclusion is disclosed, which is good, but the paper then needs two explicit latency metrics:

1. action-generation latency;
2. end-to-end certified-deployment latency.

Otherwise the reader cannot assess whether the certification machinery is operationally affordable.

---

# 4. The value-gradient result is statistically null in the experiment actually reported

The equal-information redesign is correct, but its result is weak.

For d = 64, 256, and 1,024, the paired 95% intervals for value-only loss minus value-gradient loss all include zero. The value-gradient fit improves six of ten training seeds, not all seeds.

The reported mean improvements are on the order of 1e-9 per service.

That is several orders of magnitude smaller than the accepted economic gain and is tiny even relative to the already tiny approximation losses.

The authors now state this honestly, but the title still says "Certified Value-Gradient Learning," and the abstract still gives the learning component substantial prominence.

If the value-gradient weighting has no statistically established improvement over the equal-information value-only fit, then one of two things should happen:

1. remove value-gradient learning from the title and central contribution claim; or
2. design an experiment where gradients solve a demonstrably harder learning problem and produce a robust benefit.

At present, the experiment shows that both fits are excellent because the underlying inverse approximation is easy and highly structured. It does not show that value-gradient supervision is a scientifically important ingredient.

---

# 5. The "transfer" evidence is largely architectural, not learned generalization

The manuscript says that the same thirteen coefficients transfer from graph sizes 32 or 64 to 256 and 1,024 without retraining.

That is true, but the strength of this statement should be reduced.

The training and test matrices all come from the same tightly controlled family:

- a cycle plus one random perfect matching;
- maximum degree at most three;
- coupling strength in a small fixed set;
- a known common spectral interval;
- the same quadratic objective;
- the same inverse operator K^{-1};
- the same tariff-generation rule.

A polynomial in K is dimension agnostic by construction. The analytic Chebyshev polynomial transfers in exactly the same sense.

Thus "transfer to larger graphs" here is mostly a property of the chosen functional calculus, not evidence that a learned model has discovered a representation that generalizes across operational environments.

The empirical generalization study is also extremely small:

- four fixed test graphs per size;
- one graph seed for the test suite;
- no different topology family;
- no spectral shift outside the design interval;
- no degree shift;
- no weighted or directed dependency graph;
- no disconnected or highly clustered structures;
- no nonquadratic coupling;
- no changing acceptance geometry.

This is inadequate if transfer is to remain a central claim.

At minimum, the authors should evaluate several genuinely different graph families and report performance across independent graph draws rather than four fixed test instances.

---

# 6. The learned experiment is only a single accepted quadratic update, not the multistage control problem

The main economic model is dynamic:

- regime evolves;
- inherited tier is persistent;
- adjustment costs couple periods;
- customer acceptance matters;
- continuation participation can depend on the entire regime history.

The 1,024-dimensional learning experiment does not solve that problem.

It solves one accepted review/terminal Bellman update with a known quadratic structure.

The manuscript now admits this, which is preferable to overclaiming. But the admission creates a mismatch with the title and contribution structure.

There is no high-dimensional experiment showing:

- a learned continuation value across multiple reviews;
- error propagation across Bellman steps;
- endogenous inherited-state distributions under the learned policy;
- repeated acceptance constraints along a trajectory;
- continuation participation under the learned policy;
- stock decisions coupled to the learned tier decisions;
- nonlinear or nonquadratic continuation values;
- or a certificate for cumulative multistage policy loss.

The current learned actor therefore does not demonstrate that the paper's computational method addresses the dynamic service-contract problem that motivates the paper.

It demonstrates that a polynomial graph filter can approximately solve a structured quadratic linear system at one review.

That is a much narrower result.

---

# 7. The accepted contract theory is much improved, but the general methodological contribution remains too specialized for the current length and breadth

If the learning material were removed, I would take the accepted contract/control component seriously. But even then, the paper would need sharper positioning.

The exact continuous hierarchy relies on a particularly strong physical-policy identification condition: the service floor and physical-cost cap jointly pin stock to the static comparator's stock at every reachable state. This is elegant in the canonical instance, but it is also what collapses the accepted problem to a scalar payment-budget control problem.

Once that collapse occurs, the main exact hierarchy becomes a collection of concave quadratic programs and a Riccati recursion.

The continuation-participation extension is a finite-tree strictly concave quadratic program with linear subtree constraints.

The portfolio certificate is a standard strong-concavity/Lagrangian residual bound specialized to the quadratic accepted update.

The local customer-neutral theorem is a useful perturbation argument, but it establishes a local feasible improving direction under strict inequalities, not a broad characterization of when accepted adaptivity is valuable.

The structural envelope and Topkis arguments are valid tools, but the manuscript properly concedes that they are established machinery.

The question for Operations Research is therefore not whether these results are correct. It is whether the collection produces a sufficiently original and general contribution relative to the manuscript's scope.

The current official Operations Research editorial statement emphasizes significance, methodological rigor, clarity, and broad OR utility. The Optimization statement explicitly says a paper should excel in at least one of modeling, theory, algorithms, computation, or applications and should be clear and concise. The Stochastic Models statement emphasizes importance of the modeled system, originality, quality, exposition, and utility to the OR/MS community.

See:
https://pubsonline.informs.org/page/opre/editorial-statement/area-editors-statements

R7 has many correct pieces, but the ratio of genuinely new general insight to total manuscript breadth remains too low.

---

# 8. "Value of information" needs conceptual qualification because the inherited tier is an endogenous state

The accepted hierarchy is useful, but the terminology is slightly too close to an exogenous-information interpretation.

The full class conditions on q, the inherited tier. But q is not an exogenous signal. It is yesterday's contract decision, and therefore an endogenous state variable that can encode earlier regimes through the policy.

The increment

W(t,z,q) - W(t,z)

is therefore the value of allowing the policy to condition on a persistent endogenous contractual state, not simply the value of observing an additional external piece of information.

This distinction matters because "information value" can otherwise suggest that the model is measuring the value of a signal about demand.

I recommend replacing broad phrases such as "inherited-tier information" with a more explicit label such as:

- value of inherited contractual state;
- value of persistent-state feedback;
- incremental value of conditioning on the installed tier.

The mathematics does not change, but the economic interpretation becomes cleaner.

---

# 9. The contracting institution is coherent now, but it is still constrained control under a fixed tariff, not general dynamic contract design

R7 is much more careful on this point than earlier versions.

The model assumes:

- observable regimes;
- observable stock;
- observable fulfillment;
- observable tier;
- contractible actions;
- enforceable contingent protocols;
- a fixed premium/indemnity menu;
- no private type;
- no hidden effort.

The continuation-participation extension relaxes customer commitment but does not introduce information rents, renegotiation bargaining, hidden action, or endogenous tariff design.

There is nothing wrong with studying this institution. It can be a legitimate service-operations model.

But the manuscript should resist any wording that suggests a contribution to general dynamic contracting.

The operational question is better described as:

**How should a provider adapt an externally priced, persistent service tier under customer participation and service commitments?**

That is narrower and more defensible.

If the authors want stronger "contract design" language, they need a model in which at least one economically meaningful contract dimension is actually designed rather than fixed exogenously.

---

# 10. The robustness study is improved but remains a synthetic one-factor sensitivity exercise

The 31-case accepted sensitivity analysis is a genuine improvement over the previous provider-only robustness discussion.

It is also still centered on one synthetic canonical instance.

Most cases are one-at-a-time perturbations around that same instance. There is no empirical calibration, field data, or independent operational environment.

The official Operations Research data/software/computation standards emphasize both reproducibility and meaningful empirical testing. The current area statements also note that engineering solutions should be demonstrated in real rather than purely artificial environments when the claimed contribution is practical.

The paper can still succeed as a theory paper without real data. But if it chooses that route, the theoretical contribution must carry a much higher burden.

At present the manuscript tries to get practical relevance from the 1,024-service computational study, but that study is itself synthetic and algorithmically tailored to a known quadratic inverse.

The paper therefore sits uncomfortably between theory and application:

- not general enough to be a broad stochastic-control theory contribution;
- not empirically grounded enough to be a strong service-operations application;
- not algorithmically novel enough to be a compelling learning/optimization paper.

This is the central editorial problem.

---

# 11. The repository evidence package is not self-contained

This is a concrete reproducibility concern.

The branch contains:

- source code;
- compact recorded metrics;
- verification.json;
- hashes of a larger local run.

However, several files used by the verifier and referenced by RESULT_HASHES.json are **not actually committed on the reviewed branch**, including:

- results/accepted_continuous_exact.json;
- results/interim_participation.json;
- results/portfolio_deployments.json;
- the full portfolio test graph records;
- the full training output records;
- main.pdf;
- electronic_companion.pdf.

The source-first design can reproduce these files, but a hash of an absent artifact is not independently reviewable evidence of the original run.

This matters especially because verify.py replays the generated rational policies only after those files exist. A reviewer examining the repository cannot inspect the original 3,280-node policy or the original 288 deployed portfolio vectors from the committed branch.

The README says the complete generated records and PDFs are included in a "delivered reproducibility bundle." That may be true outside GitHub, but the repository itself does not establish it.

For a computational paper making exact-certificate claims, I recommend one of the following:

1. commit the compact machine-checkable certificate records;
2. attach them to a versioned GitHub release with stable hashes;
3. archive the complete reproducibility bundle in a permanent repository and link its immutable identifier.

At minimum, the exact policies and multipliers needed for certificate replay should be available without relying on an unversioned external bundle.

---

# 12. The manuscript is still overfull and historically layered

The main manuscript is reported as 31 pages and the electronic companion as another 31 pages.

The companion intentionally preserves:

- prior continuous-time derivations;
- diffusion material;
- historical manufactured examples;
- older chain learning studies;
- earlier unfavorable comparisons;
- retained mathematical history.

Preserving scientific history in the repository is commendable.

Preserving all of it in the active journal companion is not necessarily good manuscript design.

A referee should not have to distinguish four generations of evidence to understand what the current paper actually claims.

The current paper would be stronger if the active submission contained only material needed for the current theorem chain and computational claims, while historical derivations remained archived in the repository.

Operations Research's current area statements explicitly emphasize contribution-to-length ratio and clarity.

The paper is still paying a substantial exposition cost for results that are not part of the new accepted-contract argument.

---

# 13. Mathematical audit of the new core results

I did not find an obvious fatal algebraic error in the new scalar accepted hierarchy from the committed source.

That is worth stating explicitly.

## 13.1 Physical-policy identification

The supporting-price argument is logically sound under its stated strict inequality. Summing

C(S)-C(s) - xi [f(S)-f(s)] >= 0

and combining it with the service floor and physical-cost cap indeed forces equality state by state at positive-probability reviews.

The limitation is not correctness but strength of assumption and specialization.

## 13.2 Derandomization

For static, time-only, and time-regime classes, replacing a public-randomized rule with its conditional mean preserves the linear payment term and weakly reduces convex maintenance and adjustment costs. The caveat for full histories is correctly handled separately.

## 13.3 Exact full-state quadratic recursion

The Riccati construction is appropriate for the reduced quadratic accepted problem, provided the reported endpoint checks truly establish interiority over q in [0,1]. The branch records compact verification claims but, as noted above, does not commit the full generated exact hierarchy JSON used by the replay script.

## 13.4 Customer-neutral perturbation theorem

The theorem correctly exploits a first-order maintenance reduction under a payment-neutral regime reallocation, with adjustment costs entering at second order around a constant tier.

It is a local existence theorem. It should not be used rhetorically as if it characterized the global accepted gain or robustly explained all 31 sensitivity cases.

## 13.5 Continuation residual certificate

The weighted residual inequality follows from

H >= m diag(w)

and scalar completion of squares. It is a valid a posteriori upper bound for the finite quadratic tree program.

Again, the novelty question is separate: this is a specialized residual certificate for a strongly concave quadratic program, not a new general theory of dynamic contracting.

## 13.6 Portfolio certificate

The portfolio bound is also algebraically standard:

- weak Lagrangian duality;
- strong concavity K >= mu I;
- residual completion of squares.

It is useful because the resulting numbers are small, but the theorem itself does not make the learned approximation novel.

---

# 14. The computational design needs a substantially stronger revision if learning remains in the paper

If the authors insist on keeping learning in the title and main contribution list, I would require all of the following.

## 14.1 Fair linear-algebra baselines

Report at least two deployment regimes:

**Changing K / one-shot solve**
- include factorization setup;
- include graph preprocessing;
- compare learned, analytic polynomial, CG, preconditioned CG, sparse direct, and dense methods where appropriate.

**Fixed K / repeated solves**
- factor K once;
- reuse sparse LU or Cholesky;
- reuse any preconditioner;
- report amortized solve time across many right-hand sides and many review decisions.

The current benchmark is not adequate for the second regime.

## 14.2 More timing repetitions and uncertainty

Three calls are not enough for millisecond-scale claims.

Use enough repetitions to report:

- median;
- interquartile range;
- p90/p95;
- warm/cold cache differences;
- multiple hardware environments if speed is an important claim.

## 14.3 Stronger graph distribution shift

At minimum include independent draws from several families, for example:

- random geometric;
- Erdos-Renyi with controlled degree;
- small-world;
- block/community graphs;
- weighted graphs;
- degree distributions outside training;
- spectral intervals shifted from the training enclosure.

If the method fails outside the fixed spectral window, say so.

## 14.4 A nonlinear or genuinely dynamic task

The learned method should be tested on a problem where the exact target is not simply K^{-1} for a known SPD matrix.

Examples could include:

- multistage portfolio control with learned continuation values;
- nonlinear maintenance;
- state-dependent coupling;
- stochastic graph changes;
- joint stock and tier control;
- continuation participation propagated through a learned policy.

Otherwise the learning section remains an elaborate approximation of a textbook linear solve.

## 14.5 End-to-end certification cost

Report separately:

- action generation;
- acceptance correction;
- rational certificate construction;
- certificate verification.

If certification is a selling point, its cost cannot remain outside every operational comparison.

## 14.6 Statistical comparison against analytic polynomial methods

The paper currently gives seed uncertainty for value-gradient versus value-only, but not a meaningful distributional comparison against the analytic Chebyshev method.

The analytic baseline is the scientifically most important comparator because it has the same message-passing structure without training.

---

# 15. If the authors instead choose the contract/control paper, the manuscript could become much stronger

I believe this is the more promising path.

A focused paper could center on:

1. accepted adaptive service contracts under a fixed tariff;
2. the physical-policy identification lemma;
3. exact continuous information/state-conditioning decomposition;
4. deterministic continuous optimum;
5. continuation participation and the value of commitment;
6. the local customer-neutral improvement mechanism;
7. exact and a posteriori certification.

The neural material could be removed from the title and either:

- reduced to a short implementation example; or
- moved to a separate paper.

That would immediately improve coherence.

The remaining theory should then be generalized where possible:

- characterize when the physical-policy pinning condition holds beyond the canonical discrete demand family;
- give sharper sufficient conditions for positive accepted adaptivity relative to the **reoptimized** static comparator;
- clarify how the inherited-state increment relates to adjustment cost and endogenous memory;
- separate results that require quadratic maintenance from results that survive broader convex costs;
- position the contribution directly against service contracts, dynamic adjustment, inventory contracts, and constrained MDPs.

A real service-system calibration would also materially strengthen the paper, but a sufficiently strong theory paper need not depend on one.

---

# 16. Specific comments on exposition and terminology

1. The title still overstates the learning component. If the learning section remains as currently designed, "Certified Value-Gradient Learning" should not be half of the title.

2. "Neural Differential Utility" remains a branding term rather than a mathematically distinct control object. The manuscript itself correctly says the expanded model is an ordinary MDP. Consider a descriptive title centered on adaptive service contracts.

3. The abstract gives the 1,024-coordinate learned result too much weight relative to the fact that it is one structured quadratic update.

4. The phrase "transfer to new graph structures" should be weakened. The test graphs remain in the same cycle-plus-random-matching family.

5. "Value of inherited-tier information" should be clarified as value of conditioning on an endogenous persistent contractual state.

6. The fine-menu deterministic incumbents are appropriately labeled as incumbents. Keep that caution.

7. The robustness table appropriately retains infeasible and zero-gain cases. Keep that practice.

8. The manuscript should distinguish the exact rational core from floating-point sensitivity results in every table caption, not only in surrounding prose.

9. The operational implication section currently tries to unify exact scalar theory, finite-tree participation, and graph learning. This unification is asserted more than demonstrated.

10. Historical continuous-time and diffusion material should be archived outside the active companion unless it is directly used by a current theorem.

11. The paper should state more prominently that the learned deployment uses a known coercivity constant and a known spectral enclosure. These are central to why the certificate and polynomial transfer are easy.

12. The timing table should specify whether each method includes setup/factorization. At present that information is essential and not visible in the table.

13. If a fixed graph is the intended repeated-decision setting, cached sparse factorization should be the default direct baseline.

14. If graphs change every review, then graph construction and setup must be included in **all** methods' timing.

15. The paper should not infer practical importance from the 1,024 dimension alone. A 1,024-dimensional sparse SPD system is not inherently a difficult OR computation.

16. The use of only four fixed test graphs per size should be stated in the main table, not left mainly to the companion.

17. The derivative step-size sensitivity uses one seed. That is too weak to support any robustness claim about the value-gradient weighting.

18. The learned coefficients should be compared directly with the analytic Chebyshev coefficients and with the best polynomial approximation for the empirical eigenvalue distribution. This would reveal what, if anything, the training has learned beyond the known inverse.

19. A degree sweep is needed. Degree 12 appears fixed a priori, but the runtime-accuracy frontier across degrees is more informative than a single selected point.

20. If the main operational value is memory footprint, report actual working-memory and factorization-memory measurements rather than comparing only coefficient bytes with a dense matrix.

---

# 17. Minimum requirements before I would support another review

I would not support an R8-style patch that adds another table while preserving the current architecture.

Before reconsideration, I would require a deliberate choice between two manuscript identities.

## Path A: accepted adaptive service-contract theory

Required changes:

- remove learning from the title and central contribution unless it is genuinely necessary;
- sharply reduce historical companion material;
- generalize the economic theory where possible;
- clarify endogenous-state versus exogenous-information language;
- deepen positioning against contract and constrained-control literature;
- make the exact certificate package self-contained;
- optionally add a real or calibrated service application.

## Path B: certified learning for high-dimensional stochastic control

Required changes:

- move beyond a known quadratic inverse;
- demonstrate a truly multistage high-dimensional control problem;
- use fair amortized numerical-linear-algebra baselines;
- include preconditioned and cached methods;
- evaluate real distribution shift and multiple graph families;
- report statistically meaningful timing and accuracy experiments;
- include cumulative policy/certification guarantees;
- show that value-gradient supervision materially helps.

Trying to do both at the current level leaves the paper below the Operations Research threshold in each dimension.

---

# 18. Final assessment

R7 deserves credit for serious scientific revision. The accepted continuous comparison, the continuation-participation extension, and the tighter certificates are not cosmetic.

I also do not see evidence, from the source I reviewed, of a fatal algebraic collapse of the new exact scalar result.

Nevertheless, **correctness is no longer the main issue**.

The manuscript's remaining problem is significance and integration.

The strongest economic result is specialized but credible. The strongest computational result is a certified approximation of a known quadratic inverse. The learned method is nearly indistinguishable in runtime from an analytic polynomial, statistically indistinguishable from the value-only fit in the gradient comparison, and compared against direct methods using a timing protocol that unnecessarily refactorizes the fixed matrix. The 1,024-dimensional result is a single structured update rather than the dynamic contract problem.

For a flagship journal, that is not enough.

**Recommendation: Reject. A substantially reconceived, narrower submission could merit fresh review, but I would not recommend continuing the present manuscript through another incremental revision cycle.**
