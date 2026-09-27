# Referee Report on R6 Scientific Revision

**Journal:** Operations Research  
**Manuscript:** *Neural Differential Utility: Accepted Dynamic Service Contracts and Certified Value-Gradient Learning*  
**Reviewed branch:** revision/ndu-operations-research-r6-20260921  
**Reviewed head:** 1004079f29ce65e9a8e3157c63d654b28d42f1f6  
**Prior referee report:** reviews/operation_research_referee_report_r6_2026-09-21.md at review commit a16435cca2c973331e60908b4c45f505de71e698  
**Review date:** 2026-09-21  
**Round:** R7 external harsh review of the scientific R6 revision

## Recommendation

**Reject in its present form. A substantially more focused resubmission could be worth reconsidering, but I would not recommend another incremental revision of the current manuscript architecture.**

This recommendation is materially different from the previous round.

R6 is a genuine scientific revision. The authors have responded seriously to many of the central objections in the previous report. In particular, the new manuscript now has an explicit customer and ex-ante acceptance institution; it optimizes the continuous static contract rather than using the arbitrary 0.5 tier as the principal benchmark; it imposes service and customer-utility constraints; it supplies an exact rational feasible policy and an independent Lagrangian Bellman upper bound for the headline customer-preserving improvement; it develops switching thresholds and a dual-coordinate adjustment-cost extension; and it replaces the manufactured continuous example as the main learning experiment with an operationally connected nonmanufactured finite-chain teacher. These are substantial repairs.

I therefore do **not** reject R6 because it is a relabeled R4/R5 manuscript, and I do **not** find an obvious algebraic failure in the exact customer-preserving certificate after auditing the source implementation and the recorded rational output.

The remaining problem is more fundamental for *Operations Research*: the paper still has not decided what its principal scientific contribution is, and the strongest new exact result is not yet connected tightly enough to the “persistent contract / NDU / value-gradient learning” claims in the title. The manuscript currently contains at least three papers: an accepted dynamic service-contract model, a structural/algorithmic paper on one-dimensional persistent adjustment, and a neural value-gradient computational paper. The first of these has become credible. The second contains useful mathematics. The third remains far too weak computationally to justify its prominence. The combined paper is broader than the evidence can support.

The central publication blockers are now:

1. the exact accepted-contract gain is not decomposed by information class, so the paper does not identify how much of its flagship Pareto improvement is actually due to the inherited persistent tier;
2. robustness of the accepted Pareto gain is largely absent—the sensitivity study is primarily for the unconstrained provider problem, not for the accepted customer-preserving problem that now carries the paper;
3. the neural experiment is performed on a tiny problem for which exact dynamic programming is essentially instantaneous in the recorded implementation;
4. the advertised learning “certificate” is numerically far too loose to be decision-useful and is only a finite-chain certificate, not a continuum guarantee;
5. the value-gradient comparison is not an equal-information experiment because the derivative-supervised learner receives derivative labels constructed from neighboring exact teacher values;
6. the contracting institution is now coherent, but it assumes complete observability, contractibility, commitment, and public randomization, making the economic problem closer to constrained control under an accepted exogenous tariff than to general dynamic contract design;
7. the paper remains under-positioned against some directly adjacent contract-adjustment and inventory-contract literature;
8. the active GitHub “current referee package” links to PDFs that are not actually committed on the reviewed revision branch.

These are not cosmetic points. They affect the interpretation of the main result, the novelty claim, and the justification for the manuscript's title and scope.

---

# 1. R6 is a real revision, and several previous blockers are genuinely closed

Because the previous report centered in part on revision integrity, I want to state clearly what has changed.

The active manuscript is now R6 throughout its source. The response-to-referee document is new and detailed. The active model adds an explicit customer who accepts an ex-ante contingent protocol. Customer utility, discounted fill, and an optional physical-cost cap enter a finite occupation-measure program. The static comparator is optimized continuously. The computational code and exact certificate are new. The continuous-review learning model uses the same operating primitives rather than the old manufactured quadratic HJB as its primary experiment.

Most importantly, the principal static-vs-dynamic comparison has been repaired.

The recorded continuous static optimum is

[
	heta^*_{m stat}=0.582110391776ldots,
qquad
W^*_{m stat}=-5.870110973047ldots .
]

The accepted dynamic policy has

[
W_{m acc}=-5.244970661075ldots,
]

so the provider-reward gain is

[
0.625140311972ldots.
]

The exact certificate verifies the same discounted fill, customer utility, and physical cost as the continuous static comparator. The feasible policy is rational except for presentation as decimals, and the independently evaluated rational Lagrangian Bellman upper bound is approximately (8.20	imes10^{-16}) above the feasible value.

This is a meaningful result. It resolves the earlier objection that the main reported gain was purchased by lowering service, and it is materially stronger than simply showing that an enlarged action set beats an arbitrarily fixed tier.

I also credit the paper for keeping unfavorable historical comparisons visible rather than rewriting the record.

The recommendation remains negative because the stronger R6 result exposes a new question that the manuscript does not yet answer: **what part of that accepted Pareto gain is actually generated by the persistent inherited contract state, as opposed to ordinary regime-contingent reallocation of an exogenously priced tier?**

---

# 2. The flagship accepted Pareto result is not decomposed by information class

This is now the most important scientific omission.

The manuscript provides a useful nested comparison for the **unconstrained provider problem**:

- static contract;
- time-only rule;
- time-regime rule;
- full time-regime-inherited-tier rule.

For the canonical grid problem, the paper reports approximately

[
W_{m static,grid}=-5.873763514,
]

[
W_{t,z}=-5.052903964,
]

and

[
W_{t,z,q}=-5.002310555.
]

Thus inherited-tier information adds about

[
0.050593409
]

in the unconstrained relaxation.

That is informative, but it is not the problem that now carries the paper.

The flagship R6 result is the **accepted** problem with customer utility and service held to the optimized continuous static benchmark, and optionally with physical cost capped. Those constraints alter the feasible set, the relevant shadow prices, and potentially the value of each information source. An information decomposition from the unconstrained relaxation cannot simply be transferred to the constrained problem.

This distinction matters especially because the exact accepted policy actually uses the inherited tier in a substantive way. Inspection of the positive-occupancy policy shows multiple reachable inherited tiers from period 2 onward, with different chosen contracts at the same time and regime. Therefore the inherited state is not merely a formal variable in the accepted solution.

The paper should solve the accepted counterpart of its own information hierarchy:

[
mathcal P_{m stat}
subseteq
mathcal P_t
subseteq
mathcal P_{t,z}
subseteq
mathcal P_{t,z,q},
]

under the **same customer-utility, fill, and physical-cost requirements** used in the flagship comparison.

At minimum the paper should report:

- accepted best static value;
- accepted time-only value;
- accepted time-regime value;
- accepted full-state value;
- the incremental accepted value of regime information;
- the incremental accepted value of inherited-tier information;
- whether randomization is required in each restricted class;
- matching numerical or exact bounds tight enough to make those increments credible.

Without this, the headline result establishes that **some contingent accepted policy** beats the optimized static policy, but it does not identify how much of the gain is attributable to the specific persistent-state mechanism that motivates the paper.

For a paper centered on persistent contractual state, this decomposition is not optional.

---

# 3. The exact Pareto improvement is credible but too instance-specific to carry the current claims

The new exact certificate is one of the strongest parts of the manuscript. It is also unusually tailored.

In the certified accepted solution, every positive-occupancy stock choice is

[
S=z+2.
]

Consequently the accepted dynamic protocol can preserve the static comparator's discounted fill and physical cost exactly while varying the contract tier. Customer utility is then matched by a single public randomization at one state. The gain comes primarily from state-contingent reallocation of the tier, including a reduction in the convex maintenance term, while paying more adjustment cost.

This is mathematically legitimate. But for an *Operations Research* paper it raises the obvious robustness question:

**Is the exact Pareto improvement structurally robust, or is it a specially aligned feature of this small translated-demand instance, quadratic maintenance, linear premium/indemnity schedule, and chosen reservation point?**

The current sensitivity analysis does not answer that question. It mainly recomputes the unconstrained dynamic program as parameters vary. That is not a robustness analysis of the accepted customer-preserving result.

The paper needs a sensitivity or robustness study for the **accepted problem itself**. At a minimum, vary:

- adjustment cost (lambda);
- maintenance curvature and preferably maintenance functional form;
- indemnity coefficient (kappa);
- premium slope;
- customer service valuation (
u);
- service reservation level;
- customer reservation utility;
- regime persistence;
- demand dispersion, not only translated location;
- the tier grid;
- the stock grid.

For each perturbation, report whether a positive accepted gain remains, which constraints bind, whether randomization remains necessary, and how the information decomposition changes.

A stronger paper would identify primitive sufficient conditions under which a customer-preserving adaptive improvement exists, even if only locally around a static benchmark. The current exact result proves existence for one calibrated synthetic instance; it does not yet explain how generic the phenomenon is.

---

# 4. The paper still has an identity problem: accepted contracts, envelope algorithms, and neural learning are three different contributions

R6 is more coherent than R4, but it is still overextended.

The manuscript now contains:

1. a finite-horizon accepted service-contract model with customer participation and service constraints;
2. Topkis monotonicity and switching-threshold results;
3. a one-dimensional inherited-state upper-envelope algorithm;
4. an (O(n^{-2})) contract-grid bound;
5. a Bregman/dual-coordinate extension;
6. an exact occupation-measure and Bellman-dual certificate;
7. a continuous-rate reconfiguration model;
8. a finite-chain verification bound;
9. a trained value-gradient critic experiment.

Each item can be defensible in isolation. The problem is that the paper does not establish that all of them are necessary to answer one central OR question.

The accepted-contract result does not need a neural network.

The exact envelope result does not need the customer institution.

The continuous-rate learning model is explicitly not the asymptotic limit of the original eight-period jump-adjustment model without rescaling; it is a related model with different adjustment units and a speed limit.

The finite-chain learning experiment does not validate the exact accepted policy.

The result is a manuscript whose breadth makes every component look thinner than it would in a focused paper.

My preferred reconstruction would make the accepted service-contract problem the center of the article:

- institution;
- structural policy results;
- exact/efficient solution method;
- accepted information-value decomposition;
- robust computational study;
- exact certificate.

The neural continuous-review material should either be removed to a separate paper or elevated dramatically with evidence that approximate learning is needed on problems where exact dynamic programming is infeasible.

At present the word **“Neural”** is still disproportionately prominent relative to the scientific role of neural learning in the main accepted-contract result.

---

# 5. The neural experiment does not establish computational necessity or advantage

The R6 response correctly distinguishes the new trained critic from the old deterministic hinge compilation. That is a real improvement.

However, the new experiment remains too small to support a neural computational contribution.

The continuous-review state is one scalar tier coordinate plus three regimes and time. The “teacher” is an exact finite controlled Markov chain with 160 tier intervals and 803 time steps. The recorded exact dynamic-programming solve for that teacher takes approximately

[
0.033 	ext{seconds}
]

in the committed output.

The four neural training runs take approximately

[
3.36,quad 5.76,quad 3.36,quad 6.22 	ext{seconds}.
]

Thus, in the recorded environment, constructing the exact 160-grid teacher is roughly two orders of magnitude faster than training one of the neural critics. This is not a perfectly apples-to-apples comparison—the network may be viewed as a compressed function representation or a precursor to higher-dimensional use—but the manuscript provides no experiment in which that potential benefit is realized.

There is no:

- high-dimensional state space;
- large action space that defeats exact DP;
- out-of-sample parameter transfer;
- amortization across many initial states or parameter settings;
- memory-compression comparison;
- inference-throughput comparison;
- sample-efficiency benchmark against non-neural approximation;
- wall-clock comparison to interpolation or spline approximation;
- comparison to approximate dynamic programming baselines.

Therefore the learning experiment currently demonstrates only that a neural network can imitate a value function that exact dynamic programming already computes almost instantly.

That is not enough for an *Operations Research* computational contribution.

If the neural component remains in the title, the paper should include a problem size at which exact dynamic programming is genuinely burdensome and demonstrate a consequential tradeoff in solution time, memory, accuracy, or repeated-decision throughput.

---

# 6. The “certified value-gradient learning” claim is much stronger than the numerical certificate

The finite-chain policy-loss bound is mathematically sensible, and I appreciate the explicit statement that it is not a continuum certificate.

But the numerical budgets are extremely loose.

The recorded pairs are approximately:

- observed loss (0.0291), bound (5.337);
- observed loss (0.0148), bound (2.903);
- observed loss (0.0203), bound (4.247);
- observed loss (0.00695), bound (2.183).

The bounds are roughly 180 to more than 300 times the realized policy losses. They are also large relative to the absolute magnitude of the value itself.

A formally valid upper bound can still be practically vacuous. Here the certificate does not distinguish a useful learned policy from a severely degraded one at a resolution relevant to the reported improvements.

This matters because the title advertises **“Certified Value-Gradient Learning.”**

I would require one of two changes:

**Option A: strengthen the certificate.**  
Use a sharper residual-to-performance argument, local occupancy-weighted certificate, monotonicity/shape restrictions, verified interpolation bounds, interval arithmetic, or another mechanism that reduces the guaranteed loss to a scale comparable to the operational gains being discussed.

**Option B: narrow the claim.**  
Call the result exhaustive finite-chain residual evaluation or an a posteriori worst-case budget, and remove “certified” from the title unless a decision-useful guarantee is actually achieved.

The manuscript is commendably transparent about the distinction between observed loss and worst-case budget. But transparency about a weak certificate does not make the certificate strong enough to support the paper's branding.

---

# 7. The value-gradient experiment is not an equal-information comparison

The paper says the value-only and value-gradient runs use the same sampled input locations, initial weights, minibatch sequence, and optimization schedule. This is useful experimental control.

But the two training objectives do **not** receive the same information.

The derivative targets are generated from the exact teacher value array by a numerical gradient operation and interpolation. In effect, the value-gradient learner receives information about how teacher values vary across neighboring tier points, while the value-only learner receives only scalar values at the sampled inputs.

That is a legitimate form of additional supervision. The manuscript acknowledges this. It also means the experiment cannot establish that the value-gradient formulation is a better use of the **same oracle budget**.

The relevant baselines should include at least:

- value-only training with an equal amount of teacher information;
- value-only training with more sampled points chosen to match the cost of derivative-label construction;
- a spline or shape-preserving interpolant using the same teacher table;
- finite-difference regularization without explicit gradient labels;
- a monotone or convexity-informed critic, where the structural theory permits it;
- more than two seeds.

Two paired seeds, both favorable to derivative supervision, are suggestive but not sufficient for a methodological conclusion.

At minimum, the paper should change the interpretation from “gradient supervision improves learning” to the narrower statement that **supplying additional numerical derivative labels improved the deployed policy in two paired synthetic runs**.

That is true. It is also much less ambitious.

---

# 8. The contracting institution is now coherent, but it is an unusually complete-contract environment

The prior report criticized the absence of any counterparty. R6 fixes that problem.

The customer and provider sign an ex-ante master agreement. Regime, tier, stock, demand, and fulfillment are observable and contractible. The provider follows a contingent protocol. Public randomization is permitted. There is no hidden action, private type, interim participation, or renegotiation. Transfers are enforceable.

These assumptions define a coherent model.

They also remove most of what makes dynamic contracting difficult.

Under the stated assumptions, the economic object is best described as **constrained stochastic control under an accepted state-contingent tariff/protocol**. This is not a criticism of the mathematics; it is a request for proportional positioning.

The paper should not drift rhetorically toward a general solution to dynamic service contracting. It should explain where such complete contractibility is realistic:

- cloud-service capacity commitments?
- managed logistics contracts?
- publicly metered service tiers?
- capacity reservations with observable stocking or fulfillment?
- regulated service schedules?

Without an application context, the customer institution risks looking like a formal device added to repair the previous service-degradation objection.

A top OR paper needs either:

1. a convincing operational setting in which the assumed observability, commitment, and contingent tier control are natural; or
2. a theory extension showing what survives when one important friction is relaxed, such as interim participation, imperfect action contractibility, or limited menu commitment.

The paper does not need to become a full mechanism-design article. It does need to justify why the institutional assumptions correspond to an important operations problem rather than merely making the constrained MDP convenient.

---

# 9. The literature review is much better, but still misses close neighbors

The bibliography has expanded substantially and now includes relevant work on SLAs, inventory contracts, hysteretic policies, and incentive-efficient control.

That is a major improvement.

However, the paper still needs to position itself more directly against literature in which inventory decisions and contract terms are jointly designed or contract terms are adjusted after information arrives.

Two examples that appear particularly relevant are:

- Henig, Gerchak, Ernst, and Pyke (1997), “An Inventory Model Embedded in Designing a Supply Contract,” *Management Science* 43(2):184–189.
- Nasser and Turcic (2019), “Temporary Contract Adjustment to a Retailer with a Private Demand Forecast,” *Management Science* 65(1):209–229.

The first is directly about inventory embedded in contract design. The second is directly about contract adjustment after information arrival. They are not the same model as R6, but that is precisely why the manuscript should explain the distinction.

The paper should also be clearer about what is novel relative to the closest SLA and contract-adjustment literature at the level of individual results:

- Is the accepted occupation-measure formulation novel, or standard constrained-MDP machinery applied to this institution?
- Are the hysteresis thresholds novel beyond standard switching-cost logic?
- Is the dual-coordinate Bregman envelope novel beyond a Legendre-coordinate rewriting?
- Is the exact Pareto certificate novel as methodology or primarily as evidence for this instance?
- Is the principal contribution the economic comparison rather than any one mathematical technique?

A top-journal paper can make a valuable contribution by combining known methods in a new operational setting, but then the operational insight and empirical relevance must carry more weight.

---

# 10. The structural mathematics is useful, but the novelty needs sharper separation from standard machinery

Several R6 mathematical results are clean:

- monotonicity under premium-liability compatibility;
- inherited-state envelope representation;
- linear upper-hull construction for ordered scalar tier slopes;
- a second-order contract-grid loss bound without assuming global concavity;
- two-tier hysteresis inequalities;
- aggregate revealed-preference comparative statics;
- Bregman dual-coordinate envelope identity.

I view the (O(n^{-2})) grid result as one of the stronger analytic pieces, especially because the paper carefully avoids inferring the rate from numerical grid differences.

However, the manuscript sometimes presents a collection of standard ingredients as though the collection itself automatically forms a broad theory.

The following distinctions should be made explicit:

- Topkis monotone selection is standard machinery; novelty lies in the contract-specific primitive conditions and consequences.
- A max of affine functions with ordered slopes admits a standard convex-hull treatment; novelty lies in recognizing and exploiting that structure in this model.
- Two-tier hysteresis under switching costs is expected; novelty must come from the operational interpretation or multi-tier consequences.
- The Bregman expansion is an algebraic dual-coordinate identity; it does not by itself provide a multidimensional fast algorithm.
- Occupation-measure LPs and Lagrangian Bellman bounds are standard constrained-MDP tools; the novelty is the exact economic comparison they certify, not the generic duality machinery.

The paper already states several of these limitations, which is good. The next version should go further and organize the contribution section around **what is genuinely new**, not around everything that can be proved once the model is written down.

---

# 11. The continuous-review model is connected to the primitives, but it still feels like a second paper

R6 fixes the old problem that the continuous HJB example was manufactured and disconnected from the inventory primitives.

The new continuous-review model uses the same demand regimes, inventory reduction, premium, indemnity, and maintenance components. The tier evolves through a bounded velocity and incurs a quadratic rate cost.

This is a coherent related model.

But it is not the same economic model as the eight-period jump-adjustment problem. The paper correctly explains that the adjustment term must be rescaled as

[
lambda(	heta-q)^2/Delta
]

to obtain a finite flow cost, and it imposes a speed constraint. Therefore the continuous-review section should not be interpreted as a convergence validation of the original accepted model.

That leaves the reader with two distinct models:

- the finite accepted jump-contract model, for which the strongest exact economic result is proved;
- the continuous-rate provider-relaxation model, for which neural learning is studied.

The customer acceptance constraints are optional and dualized in the continuous model, but the reported learning experiment uses the provider relaxation, not the accepted contract problem.

This disconnect is smaller than in R4, but still significant.

If the learning component remains, I would prefer to see it solve an approximation of the **accepted** dynamic contract problem, or at least demonstrate that the learned policy respects economically meaningful service/customer constraints. Otherwise the neural section does not advance the paper's strongest economic result.

---

# 12. The computational study remains a toy study by OR standards

The finite canonical problem has:

- 8 periods;
- 3 regimes;
- 11 contract tiers;
- 13 stock choices;
- 264 nonterminal states;
- 37,752 full state-action combinations.

This is an excellent size for an exact certificate and a transparent pedagogical example.

It is not a convincing scale demonstration for a computational contribution.

Similarly, the continuous-review chain has only one continuous state dimension and three regimes. Exact solution is extremely fast.

A top OR paper making algorithmic and learning claims should contain at least one materially larger instance, for example:

- multiple products;
- multiple customer classes;
- several contractual service dimensions;
- inventory carryover;
- backlog;
- network or multi-location structure;
- higher-dimensional persistent contractual state.

I do not require all of these. I require at least one case that reveals why the proposed structure or learning method matters computationally.

The current hull scaling experiment to 2,048 tier intervals is useful for verifying one-dimensional algorithmic complexity, but it does not substitute for a realistic high-dimensional operational problem.

---

# 13. The exact customer-preserving certificate is strong evidence, but it should be interpreted narrowly

I audited the exact-certificate implementation because the R6 abstract relies heavily on it.

The implementation constructs:

1. two deterministic feedback policies differing at the one randomized state;
2. an exact rational mixture weight chosen to match the static customer utility;
3. exact forward propagation of reward, customer utility, fill, and physical cost;
4. rational nonnegative Lagrange multipliers;
5. a Bellman recursion over the complete finite stock/tier action set for the Lagrangian relaxation.

The recorded feasible value and upper bound differ by approximately

[
8.20	imes 10^{-16}.
]

This is a legitimate two-sided certificate for the stated finite-grid accepted problem. The multipliers are proposed from the floating LP but their validity is checked in exact rational arithmetic; the proof does not rely on the floating optimizer's “optimal” status alone.

That is good work.

But the abstract currently risks making this exactness sound broader than it is. The certificate does **not** establish:

- optimality with continuous contract actions in the dynamic accepted problem;
- robustness to perturbations of primitives;
- optimality in the continuous-review model;
- neural policy optimality;
- field validity of the customer model.

The paper should state prominently that the exact accepted optimum is for the specified **0.1 dynamic tier grid with the stated stock menu**, compared to an exactly optimized continuous static tier.

The comparison is still strong because the static comparator is finer. But the scope must remain precise.

---

# 14. The paper should distinguish constrained and unconstrained comparative statics more aggressively

The manuscript is aware that changing (kappa) can change the customer-participation feasible set and therefore invalidate a direct transfer of the unconstrained exposure comparative static.

That caveat is correct.

The same issue appears more broadly throughout R6.

Many structural results are for the unconstrained Bellman problem:

- monotone policy theorem;
- envelope recursion;
- exposure comparative statics;
- information-restricted values;
- continuous-review learning.

The headline economic result is for a constrained occupation-measure problem.

A reader can easily move from one part to another and infer more than has been proved.

I recommend a recurring notation distinction:

- (V^{m rel}) for provider relaxation;
- (V^{m acc}) for accepted constrained value;
- separate proposition statements whenever a property transfers to the accepted problem;
- explicit flags in every computational table showing which problem is being solved.

In particular, the paper should not use the unconstrained inherited-state information increment as qualitative evidence for the accepted program without solving or bounding the accepted restriction.

---

# 15. Public randomization is mathematically fine, but its operational interpretation deserves discussion

The exact accepted optimum uses a lottery at one state between tiers 0.7 and 0.8.

For a risk-neutral customer under an enforceable ex-ante protocol, this is mathematically legitimate. Occupation measures make randomization natural.

Operationally, however, a service-level contract may not allow a provider to draw a public random number after observing the regime and then choose one of two contractual tiers.

If the paper wants the exact randomized policy to be more than a mathematical certificate, it should explain:

- what physical or contractual mechanism implements the public lottery;
- whether randomized tier assignment is acceptable to the customer;
- whether the same gain can be approximated by a deterministic policy with a finer tier grid;
- how much value is lost under deterministic accepted policies;
- whether randomization is merely a convexification device caused by the coarse 0.1 tier grid.

This is particularly important because the static comparator is continuous while the accepted dynamic policy uses a coarse grid. A deterministic continuous-tier accepted policy might offer a more natural benchmark and could eliminate the need for the lottery.

I strongly recommend solving the continuous-tier or sufficiently fine-grid accepted problem numerically, even if the exact rational certificate remains on the coarse grid.

---

# 16. The current “neural” branding is still not earned

The manuscript has become much more careful in its statements, but the title remains

*Neural Differential Utility: Accepted Dynamic Service Contracts and Certified Value-Gradient Learning*.

I do not think the evidence supports this title.

The strongest result is an exact constrained stochastic-control result that does not use neural learning.

The structural results do not require neural learning.

The exact certificate does not use neural learning.

The neural experiment has two seeds, uses exact-DP-generated labels, runs on a one-dimensional state variable, and has very loose worst-case performance bounds.

This is not a minor stylistic complaint. Titles signal the principal contribution to editors and readers.

A title centered on dynamic accepted service contracts, persistent tier adjustment, and certified adaptivity would be much more faithful to the actual strength of R6.

If the authors insist on retaining “Neural,” then the learning section needs to become a first-class computational contribution with scale, baselines, uncertainty, and practically meaningful certification.

---

# 17. Reproducibility is improved, but the active referee package contains broken PDF links

The R6 README says:

- “Manuscript (main.pdf)”
- “Electronic companion (electronic_companion.pdf)”

on the current revision branch.

Those two root PDF files are not present at the reviewed R6 head. The archived pre-R6 PDFs exist, and the build script can generate new R6 PDFs locally, but the active README links to files that are absent from the branch.

This is a smaller issue than the R5 revision-integrity failure, but it should still be fixed.

A referee should not have to infer that a missing linked artifact is expected to be generated locally.

Either:

- commit the exact reviewed R6 PDFs;
- attach them as immutable release artifacts and link them correctly; or
- remove the broken links and make clear that source compilation is required.

The manuscript source is sufficient for this review, so this does not drive my recommendation. It is nevertheless a submission-quality defect.

---

# 18. Specific technical comments

## 18.1 Scope of the inherited-only equivalence

The proposition equating inherited-only and time-only policies from deterministic (q_0) is correct for deterministic feedback in the stated unconstrained setting because the tier path is deterministic.

The text should make even more explicit that this equality is **not automatically an equality of accepted constrained randomized classes**. Once public randomization and expectation constraints are central, the information-class comparison must be defined carefully at the level of admissible randomized protocols.

This is another reason to solve the accepted restricted classes directly.

## 18.2 Exact static optimization

The static enumeration argument is credible for the finite stock menu and continuous tier. It would be useful to state explicitly in the theorem whether every pairwise stock-line crossing must be enumerated even if the crossing is never on the upper envelope, or whether an upper-envelope preprocessing can reduce the candidate set. This is minor but would improve the algorithmic presentation.

## 18.3 (O(n^{-2})) grid theorem

The supporting-subgradient argument is substantially clearer than in the previous version.

The paper should preserve the current scope discipline: the theorem controls contract discretization for the unconstrained dynamic program. It does not automatically certify stock discretization, the accepted LP, or the continuous-review approximation.

## 18.4 Hysteresis

The two-tier hysteresis proposition is correct and useful as a local structural interpretation. For a multi-tier grid, I would like to see at least one theorem or computational diagnostic about the ordering and width of actual surviving inaction regions, not merely pairwise crossings of surviving hull lines.

## 18.5 Bregman extension

The dual-coordinate identity is valid and elegantly stated. The paper should resist presenting it as a broad multidimensional algorithmic result. In dimensions greater than one, the hard geometry has simply moved into an affine-envelope problem in the dual coordinate.

The current caveat already says this; keep it prominent.

## 18.6 Continuous-rate generator

The continuous-review proposition is a local-consistency construction with an Euler regime transition and rescaled adjustment cost. It is not a statement that the unit-time continuous-time Markov semigroup reproduces the original discrete transition matrix. The current wording mostly respects this distinction. I would keep the word “embedding” qualified as “locally consistent review-rate construction.”

## 18.7 Learning derivative labels

The gradient labels are centered numerical differences of the teacher table. They are therefore discretization-dependent and correlated with the exact teacher values. Report sensitivity to teacher grid resolution and differentiation rule if these labels remain central.

## 18.8 Statistical evidence

Two seeds are not enough to characterize a stochastic training procedure. At minimum use substantially more seeds and report distributions of policy loss, not only two favorable paired outcomes.

## 18.9 Certificate terminology

The finite-chain residual scan is exhaustive over the finite chain, which is good. But “complete scan” and “certificate” should not be used in adjacent prose in a way that readers could confuse it with interval-verified arithmetic or continuum verification.

---

# 19. What I would require for a credible resubmission

I would not recommend another revision that simply adds more appendices, checks, or secondary theorems. The paper needs **subtraction and concentration**.

A credible resubmission would do the following.

### 19.1 Choose the primary paper

My recommendation is to make the paper about **accepted dynamic service contracts with persistent tier adjustment**.

The neural continuous-review study should be removed or reduced to a brief extension unless it can be transformed into a genuinely necessary large-scale computational method.

### 19.2 Complete the accepted information-value decomposition

Solve the customer-constrained problem under:

- static;
- time-only;
- time-regime;
- full time-regime-inherited-tier information.

Use the same reservation constraints in every class. Report exact or tight numerical bounds.

This is the single most important missing experiment.

### 19.3 Establish robustness of the accepted gain

Repeat the accepted comparison over a meaningful design of primitives and reservation levels. Show when the Pareto gain exists, when it disappears, and which mechanism drives it.

### 19.4 Solve a finer or continuous-tier accepted problem

Keep the exact coarse-grid certificate, but demonstrate that the result is not a 0.1-grid/randomization artifact. Quantify deterministic-versus-randomized value.

### 19.5 Strengthen the operational institution

Either anchor the model in a concrete service-contract application or relax one complete-contract assumption and show which results survive.

### 19.6 Reposition against the closest literature

Add the missing contract-adjustment and inventory-contract work and provide a theorem-by-theorem novelty map.

### 19.7 If neural learning remains, make it earn its place

Use a problem where exact DP is costly, compare against serious approximation baselines, equalize information/computational budgets, use many seeds, and provide a practically meaningful performance certificate.

### 19.8 Simplify the manuscript

Move historical material and unrelated generic HJB machinery out of the main narrative. The paper should read as one argument, not as a repository of every valid result produced during the project.

---

# 20. Positive elements that should be preserved

Despite the recommendation, R6 contains several components I would strongly retain.

- The authors now use the optimized continuous static comparator.
- The customer institution is explicit rather than implicit.
- The service-degradation objection is addressed directly.
- The exact feasible-policy plus Bellman-dual certificate is rigorous and independently evaluable.
- The paper distinguishes provider reward, customer utility, fill, and physical cost.
- The inherited-state envelope is clean.
- The grid-error theorem is a real analytic contribution.
- The switching-threshold discussion is operationally interpretable.
- The Bregman extension is properly caveated.
- The paper openly states that expanded-action MDP equivalence holds.
- The continuous learning experiment no longer relies on a manufactured value function.
- The authors report weak worst-case neural bounds rather than hiding them.
- Historical unfavorable results and parameterization parity remain visible.

This is a much better scientific manuscript than the nominal R5 package.

That improvement should not be obscured by the negative recommendation.

---

# 21. Recommendation to the editor

**Reject in present form.**

The reason is no longer revision integrity or an obviously invalid benchmark. R6 has repaired those problems.

The reason is that the manuscript still does not meet the coherence, identification, and computational-evidence standard I would expect for *Operations Research*.

The strongest new result is an exact, customer-preserving adaptive-contract improvement in a small finite model. That result is credible and worth developing.

But the paper does not yet show how much of that accepted gain is due to the persistent inherited contract state; it does not establish robustness of the accepted gain; it does not justify the neural method on a problem that requires learning; and its finite-chain neural certificate is far too loose to support the prominence of “Certified Value-Gradient Learning” in the title.

I would encourage a **new, substantially focused submission** built around the accepted dynamic service-contract result, with constrained information decomposition, robustness, a realistic operational interpretation, and a cleaner literature position.

I would not recommend another incremental round that adds yet more mathematical and neural material to the current architecture.
