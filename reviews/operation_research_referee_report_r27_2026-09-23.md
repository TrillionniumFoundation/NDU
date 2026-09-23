# Confidential Referee Report for Operations Research

**Manuscript:** *Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains*  
**Revision reviewed:** R27, September 23, 2026  
**Reviewed branch:** revision/ndu-operations-research-r27-20260923  
**Reviewed scientific tip:** 85fe1a799a192758a93a423bbb6d213ab9f04cce  
**Review type:** Independent harsh review of the current revision tip  
**Area claimed by the manuscript:** Stochastic Models  
**Recommendation:** **Major Revision. I do not recommend acceptance in the present form.**

## Executive assessment

R27 is a materially stronger paper than the R24 version I can reconstruct from the preserved review history. The authors have not merely patched notation. They have added a genuine optimized-restriction release theorem, comparator-adjusted continuation-rent comparative statics, a friction-path result with a reoptimized comparator, an exact promised-payment state formulation, continuous promise-preserving lower/upper certificates, and a new cached-dual construction for jointly changing continuation coefficients, commitments, rewards, and switching friction. They have also corrected the amortization sign, moved the exit-at-review institution to the foreground, retained adverse learning evidence, reduced the journal-facing manuscript to a regular-length package, and made the new R27 calculations independently replayable.

I did not find a fatal algebraic contradiction in the principal R27 cached-price theorem or in the restriction-release formulas I checked. The current package is unusually careful about distinguishing optimizer proposals from rational certificates, pointwise evidence from continuous-set guarantees, exact anchors from approximate anchors, and online query arithmetic from offline solves. The final branch tip carries a successful final-SHA status, the package check passes, the standard-library replay reports 232 independently audited optimization records, 240 cached-price evaluations, exact gap decompositions, and rejection of 14 negative controls. Reproducibility is not the reason for my negative recommendation.

The remaining problem is more fundamental and more appropriate to the current Operations Research bar: **I am not yet convinced that the manuscript isolates a sufficiently novel, unified stochastic-operations contribution, rather than a very careful synthesis of standard parametric quadratic programming, envelope arguments, Bellman state compression, concave interpolation, stochastic-dual-cut ideas, and weak-duality certificates.** The paper now contains many correct-looking results, but the mathematical engines remain only partially connected to each other and the economic information restrictions remain largely exogenous.

The current Operations Research editorial statement emphasizes innovative and impactful OR research, methodological rigor, and broad decision-making relevance. For Stochastic Models, rigor alone is not sufficient; the contribution should carry a message of broad interest that transcends the functional context. R27 is much closer to that standard than its predecessors, but it does not yet clear it in my view.

My recommendation is therefore **Major Revision, with a high bar**. A next version should not add another theorem family, another cache layer, or another replay count. It should consolidate the paper around one central contribution and prove a bridge result that the present manuscript still lacks.

---

# 1. Review object, package integrity, and what R27 clearly fixes

I reviewed the R27 tip, not an earlier predecessor. The scientific predecessor is R26 at 38f99a5b46d8cfe4f1197fc869735d5f798c499a; R27 is five commits ahead and introduces the correlated-price theorem and evidence package. The main PDF is reported as 26 pages including title/references/tables, and the formal electronic companion is 20 pages. The abstract is 181 words. This is compatible with the current regular-manuscript format and is no longer a length-driven objection.

The final-SHA status ndu-or-r27/final-sha is successful. The R27 package check reports resolved references, no horizontal overflow, 72 new optimizer proposals independently audited, 24 new off-ray queries, 240 cached-price evaluations, and successful replay of inherited R24/R25/R26 artifacts. The independent replay uses only the standard library and explicitly separates solver proposals from rational verification.

These checks establish package integrity and arithmetic reproducibility. They do not establish novelty or editorial suitability, but they remove a large class of lower-level concerns.

R27 also resolves several substantive objections visible in the preserved R24 referee history:

1. The paper is no longer centered on the transfer-coordinate identity alone. Theorem 4.1 studies the **optimized value frontier** under controlled restriction release and gives an exact regular-cell segment, its reduced curvature, marginal restriction rent, and the first active-set/bottleneck event.
2. The comparator is explicitly reoptimized. Theorem 5.1 compares full-class and restricted-class continuation rents, and Proposition 5.2 treats the friction path with both policies moving.
3. The continuation institution is now primary. Ex ante participation is correctly described as a special case that retains only the root row.
4. The horizon issue is no longer hidden. Section 6 states plainly that a history tree can grow exponentially in horizon and introduces an augmented state (t,z,q,b).
5. The continuous-promise construction does not rely on unverified interpolation. It combines feasible deterministic mixtures with affine upper planes and an explicit a posteriori gap certificate.
6. The robust-comparator objection is addressed in a mathematically cleaner way. The new R27 theorem reuses normalized dual prices while evaluating the **actual query coefficients**, rather than only comparing against a common relaxed outer set.
7. The manuscript no longer advertises the historical learned routes as a positive computational contribution. Their unfavorable outcomes are retained and delimited.

These are meaningful improvements. My remaining objections therefore concern the scientific identity of the resulting paper, not whether the authors responded.

---

# 2. The top-journal novelty burden is still not isolated theorem by theorem

This is the main issue.

The current manuscript is admirably explicit that several ingredients are established: strong convexity, normal cones, multiparametric quadratic programming, promise states, concave interpolation, stochastic dual cuts, and robust set containment. However, after reading the paper in that spirit, I still struggle to identify which theorem contains a mathematical idea that is both (i) genuinely new beyond those ingredients and (ii) central enough to carry an Operations Research paper.

The difficulty is easiest to see result by result.

### Theorem 4.1: restriction-release frontier

The global statements—piecewise-affine optimizer, piecewise-quadratic value, active-set changes, multiplier envelope formula—are standard consequences of strongly concave multiparametric quadratic programming with polyhedral constraints. The regular-cell formula
x(t)=z+tPv and V(t)-V(0)=t sum_j omega_j |xi_j| - (t^2/2) v^T S v
is a clean sensitivity calculation. The continuation-specific “first bottleneck” formula is operationally interpretable, but mathematically it is the first inactive linear constraint hit by the parametric direction. The three-node example is good pedagogy, yet it does not by itself convert the sensitivity calculation into a new stochastic-model theorem.

### Theorem 5.1: comparator-adjusted continuation rents

The derivative Delta'(t)=d^T(mu_X-mu_Y) is the envelope theorem applied to two reoptimized value functions. The U-shaped example usefully prevents a wrong economic intuition, but the general theorem is close to a direct subtraction of standard value derivatives.

### Proposition 5.2: friction path

The identity Delta'(lambda)=T(z_lambda)-T(x_lambda) again follows from the envelope theorem under uniqueness. The zero-set construction via a piecewise-affine restricted path and linear KKT feasibility is correct-looking and useful, but it remains a parametric-programming consequence.

### Theorem 6.1: promised-payment state

The exact state (t,z,q,b) is the right state, and the converse implementation argument is important for the application. But the mathematical pattern is a Bellman sufficiency result for an additive commitment state, closely related to standard promised-utility/resource-state dynamic programming.

### Theorem 6.2 / R26 continuous envelopes

The lower construction is concave interpolation over feasible deterministic mixtures; the upper construction is a weak-duality/stochastic-dual-cut style affine majorant. The participation interpretation is useful, but the mechanism is recognizable.

### Proposition 7.1: reward-only cached envelope

This is a smoothness/strong-convexity Taylor upper bound with approximate-anchor error.

### Theorem 7.3: correlated comparator reuse

This is the strongest new R27 result. The exact four-term decomposition is clean and potentially useful. Nevertheless, the global upper bound is a separable weak-duality certificate obtained by linearizing the coupled quadratic with alpha, pricing inequalities/equalities, normalizing the absolute-value tension, and maximizing scalar conjugates. The local quadratic reuse loss then follows under retained-face assumptions from the squared resource residual and a quadratic coordinate-response residual.

I regard Theorem 7.3 as a real improvement over the historical outer-comparator construction, but the manuscript still needs to explain much more sharply why this theorem is not simply a specialized dual upper bound plus local sensitivity.

**Required revision.** I strongly recommend a theorem-by-theorem novelty table in the response and, more importantly, a corresponding change in the paper itself. For each principal result, state:

- the closest established theorem class;
- exactly which conclusion is not available from that class without the continuation-contract structure;
- whether the novelty is mathematical, operational, or computational;
- which assumption is essential for that added conclusion.

If the honest answer is that the novelty is mainly the synthesis and interpretation, then the paper needs a much stronger operational decision problem to justify that synthesis. If the intended novelty is mathematical, the authors need at least one theorem whose proof genuinely exploits nested continuation constraints, promise states, or restriction geometry in a way that is not merely a relabeling of generic parametric convex optimization.

At present, I cannot locate that theorem with sufficient confidence.

---

# 3. The Stochastic Models positioning remains vulnerable

The manuscript chooses Stochastic Models and now has a much better argument for that choice than R24. Section 6 contains a genuine stochastic recursion, the public regime is Markov, and the continuous-state construction has stochastic child allocations.

But most of the paper's central theorems do not use stochastic structure in an essential way.

Theorem 4.1 is a generic finite-dimensional polyhedral parametric QP theorem. Theorem 5.1 is a generic RHS-sensitivity result. Proposition 5.2 is a generic friction-parameter result. Proposition 7.1 and Theorem 7.3 are generic certificate constructions for strongly concave quadratic programs with separable box conjugates. In all of these, the finite history tree has already been compressed into matrices A,E,M,D and coefficient vectors. The stochastic origin of those rows is not used by the mathematics, except when one particular row is interpreted as a continuation constraint.

The truly stochastic portion is Section 6, but that section is also the most recognizably standard dynamic-programming component. This creates a fit problem: the generic optimization results are the paper's most prominent structural claims, while the stochastic result is the bridge needed to motivate the area.

A Stochastic Models paper should, in my view, make the stochastic system central enough that the principal insight would be lost if the tree probabilities and continuation nesting were replaced by arbitrary linear constraints. R27 is not yet there.

**Required revision.** The authors should do one of two things:

1. **Strengthen the stochastic core.** Prove a result about the release frontier, comparator rents, or reusable prices that materially exploits subtree nesting, Markov recombination, or promise-state structure. For example, a representation or complexity result showing that continuation-specific prices/restriction rents can be computed in the augmented state without forming the history tree would directly connect the stochastic and optimization halves.

2. **Reconsider the area and the paper's claim.** If the intended contribution is primarily parametric optimization/certification, the Optimization area may be a more natural scientific home. The service-contract interpretation can remain, but the paper should not lean on Stochastic Models merely because a finite scenario tree generated the linear constraints.

I do not insist on a particular area assignment, but the current justification is still more asserted than demonstrated.

---

# 4. The paper still has two mathematical engines that are not actually connected

This is, to me, the most important constructive opportunity for a revision.

The paper now has:

- a **full-vector engine** for restriction release, continuation rents, friction paths, and cached comparator prices; and
- an **augmented-state engine** for exact promised-payment recursion and continuous-state lower/upper envelopes.

These are both useful. But there is no theorem showing that the first engine can be represented or certified through the second.

This matters because the introduction and abstract encourage the reader to see a single story: continuation commitments create an augmented state; contractual restrictions create value; reusable continuation prices certify that value without excessive recomputation. Yet the concrete R27 cache experiment is still a 63-node full-tree vector problem. The cache dimension n is the decision-vector dimension, and the query arithmetic is O(n(d+1)) per anchor after preprocessing. If n is the history-tree size, this remains exponential in horizon in a nonrecombining tree.

Section 6 correctly says that the promise-state recursion can avoid materializing histories when the state is sufficient. But Sections 4, 5, and 7 do not inherit that compression automatically.

This is not a cosmetic disconnect. It means the paper has not yet established the strongest operational claim suggested by its architecture: **that one can value and certify restriction release in a continuation-contract model using the sufficient stochastic state rather than the full history tree.**

**Required revision.** I would regard a bridge theorem here as potentially paper-defining. Examples of acceptable directions include:

- a state-space version of the restricted comparator and its dual prices;
- a recursive decomposition of the release multiplier/rent;
- a cached-price certificate defined on Bellman states or post-decision promises;
- conditions under which a pooling restriction on histories can be represented as a finite-dimensional state restriction;
- a complexity comparison between history-vector certification and augmented-state certification.

Without such a bridge, Sections 4–5, Section 6, and Section 7 read as three adjacent papers rather than one theorem chain.

---

# 5. The information-restriction hierarchy is still exogenous, so “which information creates value” is only conditional accounting

R27 is careful to say that the hierarchy increments are ordering-dependent and are not Shapley values or unique causal attributions. That is correct and important.

However, the manuscript still assigns substantial economic meaning to the classes fixed, time-only, current-regime, limited-memory, and full-history without modeling why a provider can implement one class and not another, or what it costs to move between them.

The release parameter t is a bound on deviations from linear pooling equalities. It is mathematically precise, but operationally it is not yet an information-acquisition or organizational decision variable. Likewise, the hierarchy's increments identify the value of enlarging an exogenously declared feasible set. They do not determine whether the provider should pay to install sensors, retain state, redesign software, change a review protocol, or maintain a larger policy table.

This is particularly visible in the legacy experiment, where “current regime” is only an annotation/pooling key on a heterogeneous tree and is explicitly not a fully Markov primitive description. The public-Markov family is cleaner, but it is synthetic.

**Required revision.** Either:

- introduce a simple but explicit implementation-cost model for policy memory/information resolution and optimize net value over the hierarchy; or
- substantially temper the language “which contractual information creates value” to “how much optimized value is associated with a specified exogenous relaxation of the implementable class.”

A top OR paper should distinguish value accounting from an endogenous design decision.

---

# 6. The R27 cached-price theorem is useful, but its practically favorable regime is narrower than the narrative suggests

Theorem 7.3 fixes the common box, H, R, D, h, and kappa. It allows A_theta,b_theta,F_theta,f_theta,p_theta,c_theta, and the scalar friction lambda_theta to change.

This is already a meaningful correlated family. But it does **not** cover changes in quadratic curvature, the resource-loading matrix, the switching operator, the installed-tier offset, or switching weights. In many service-adaptation problems, operating shocks can change precisely those objects.

More importantly, the attractive **quadratic reuse-loss** statement is local and conditional. It requires:

- an exact primal-dual anchor;
- equality of the anchor certificate at the anchor;
- the query optimizer to stay on the priced face;
- the cached positive continuation prices to remain complementary;
- the same box-normal direction v0 to remain valid;
- all switching-gap terms to vanish;
- a locally Lipschitz optimizer.

The manuscript commendably includes a degenerate two-cap example showing linear loss when the face changes. That example should be treated as a central warning, not a side qualification.

The global certificate remains valid when the face changes, but its quality can deteriorate sharply. The operational question is therefore not merely “can prices be reused?” but “when should the cache be trusted, when should it be refreshed, and can that decision itself be certified cheaply?”

**Required revision.** Please add an explicit, computable cache-governance result. At minimum, I would like one of:

- a sufficient test, based only on query coefficients and cached data, that certifies retention of the priced face and hence the quadratic loss regime;
- a certified upper bound on the decomposition terms that triggers refresh before the economic certificate becomes useless;
- a piecewise cache partition with guaranteed local quality;
- a theorem quantifying how cache density must scale with a desired certificate tolerance over a specified parameter polytope.

Without such a result, Theorem 7.3 is a valid upper-bound mechanism but the practical significance of the local quadratic statement remains fragile.

---

# 7. The uniform correlated-uncertainty corollary certifies a fixed policy, not an adaptive policy map

Corollary 7.4 is mathematically clean. It lower-bounds the worst-case implemented gain on a parameter polytope using one fixed cached price per cell, provided the fixed implemented policy is feasible at all vertices and hence throughout the affine cell.

This does provide a genuine continuous-set guarantee. I agree with the authors that the order of the anchor and vertex extrema matters, and the exact counterexample is useful.

However, the theorem's implemented policy is **fixed over the whole uncertainty set**. The main operational motivation is adaptation to changing conditions. In the pointwise 24-query experiment, the implemented full-class proposals are query-specific. Thus the continuous uniform theorem and the adaptive pointwise experiment certify different deployment objects.

The manuscript does not currently provide a uniform guarantee for a parameter-dependent implemented policy xhat(theta), even a piecewise-affine or cached-policy map.

That distinction should be more prominent. Otherwise readers may infer that the continuous uncertainty theorem certifies the same adaptive policy mechanism used in the query study.

**Required revision.** Either:

- extend the corollary to a declared piecewise-affine/piecewise-constant policy map with vertex-checkable feasibility and a cellwise gain bound; or
- explicitly state in the abstract, introduction, and evidence section that the continuous-set theorem concerns a fixed implemented policy, whereas the off-ray study concerns query-specific policies and is only pointwise.

This is a substantive deployment distinction, not a wording preference.

---

# 8. The computational evidence validates certificates, but it still does not establish broad operational significance or scaling

The new R27 evidence is much better designed than the historical learned-vs-classical race. I appreciate the following:

- inherited ray holdouts are separated from 24 new off-ray queries;
- the cache is frozen and does not receive query optimizer labels;
- all 72 new optimization proposals are treated as offline evaluation;
- the replay recomputes the model and certificates independently;
- all 24 cached bounds are tighter than their matched historical outer bounds;
- all 24 implemented policies have positive cached gain certificates;
- no unmatched end-to-end speedup is claimed.

These are all strengths.

But the numerical study is still a designed sensitivity experiment on a 63-node, two-service family derived from the authors' own synthetic primitives. It demonstrates that the theorem works on the constructed family and that a three-price cache can be much tighter than the old outer bound. It does not yet show that the cache remains useful under:

- larger history/state dimensions;
- more services;
- larger parameter dimension d;
- more complicated active-face changes;
- denser continuation matrices;
- longer horizons under state recombination;
- cache miss/refresh policies;
- different restriction hierarchies;
- non-designed parameter paths.

The main text correctly refuses to claim a measured speed advantage. But then the empirical contribution is mostly a verification of certificate tightness on one engineered family.

For a theory paper this can be acceptable, but in that case the mathematical novelty must carry the paper. If the authors want the computational layer to support broad operational impact, more is needed.

**Required revision.** Add a compact scaling study or reduce the evidentiary claims. I would prefer a study varying at least n, number of services, parameter dimension, cache size, and frequency of active-face changes, reporting:

- certificate slack;
- cache-evaluation cost;
- candidate-policy feasibility audit cost;
- refresh frequency/cost under a declared trigger;
- total memory;
- comparison with a fresh restricted solve at matched certificate quality.

No neural model is needed. In fact, I recommend not adding one.

---

# 9. “No history enumeration” trades one curse for another; the paper should quantify that trade more sharply

Section 6 now correctly avoids the old mistake of equating linear-in-tree-size work with polynomial-in-horizon work. The manuscript explicitly notes that the promise state is continuous, that a grid with G^k points can blow up in the number of commitment coordinates, and that child-allocation work can grow with the number of successors.

This candor is welcome.

Still, the abstract and introduction place significant weight on “global value bounds without enumerating public histories.” That statement is true for the R26 continuous-state construction under its assumptions, but it is only half the computational story. The method replaces explicit history growth by a continuous-state approximation problem whose anchor/plane count has no proved rate as a function of target error.

The theorem gives an **a posteriori** uniform certificate, not an **a priori** complexity theorem.

That distinction should be impossible to miss.

**Required revision.** Please add a concise theorem/proposition or formal discussion that separates:

1. state sufficiency;
2. existence of finite certified approximations;
3. approximation error;
4. storage/evaluation cost;
5. dependence on commitment dimension and branching;
6. any conditions under which a polynomial accuracy rate is available.

It is fine if no general rate exists. The important point is to identify exactly what computational problem has been solved and what remains exponential/high-dimensional.

---

# 10. The literature positioning is improved but still needs a closest-results comparison, not only boundary-setting prose

The current literature section does a good job distinguishing this paper from hidden-action/private-information dynamic contracting. It also credits convex optimization, generalized lasso, explicit parametric QP, robust containment, and stochastic dual cuts.

What is still missing is a **closest-result comparison**.

For example, the paper should directly compare Theorem 4.1 with the closest multiparametric-QP sensitivity/explicit-solution results: what is mathematically new beyond a one-parameter RHS/bound perturbation?

Similarly, Theorem 7.3 should be compared with reusable Lagrangian/dual bounds, Benders cuts, SDDP cuts, and parametric dual sensitivity: what is new in the normalized switching-price reuse and four-term gap decomposition?

The continuous-state envelope should be compared with standard concave interpolation plus dual cuts in approximate dynamic programming: what does continuation participation add that is not already implied by those methods?

At present the manuscript often says, correctly, “we do not claim the general principle as new.” But once all the general principles are removed, the reader still needs a crisp statement of the residue.

This is especially important because the paper is now mathematically mature enough that novelty—not correctness—is the main editorial question.

---

# 11. The paper remains too multi-centered

The main manuscript is shorter, but it still contains at least three substantial scientific narratives:

1. optimized restriction-release sensitivity and comparator rents;
2. promised-payment stochastic recursion and continuous-state certificates;
3. reusable dual comparator certification under correlated parameter changes.

The historical learning/timing evidence is now demoted, which helps. But the remaining three narratives still compete for the identity of the paper.

A top-journal paper can certainly contain several results, but they should form an unavoidable theorem chain. Here the current logical relationship is weaker:

- Section 4 does not require Section 6.
- Section 6 does not require Section 4.
- Section 7 does not require the promised-payment recursion.
- The R27 cache experiment is conducted on the full-tree legacy geometry rather than on the continuous-state recursion.

This is why the bridge theorem in Section 4 of this report is so important. It would turn three neighboring contributions into one story.

If the authors cannot supply that bridge, I recommend choosing one scientific identity and moving the other material to a separate paper.

---

# 12. Specific technical comments

## 12.1 Theorem 4.1 is globally descriptive but only locally constructive

The theorem correctly separates the global piecewise-quadratic/piecewise-affine statement from the regular-cell explicit formula. However, the surrounding prose says that “successive segments describe the complete release frontier.”

That is only operationally constructive if the authors specify what happens at degeneracies, simultaneous events, dependent active rows, and restriction-multiplier zeros. The paper says to solve an “appropriate small release quadratic program or a degenerate active-set refinement,” but that is not yet an algorithm.

If “complete frontier” is intended as an existence/structure statement, say so. If it is intended as a computational procedure, provide the procedure and its termination/correctness statement.

## 12.2 Theorem 5.1 handles multiplier nonuniqueness correctly in prose; numerical use should do the same

The manuscript appropriately states that at a degenerate point the directional derivative is the minimum of d^T mu over the optimal multiplier set, and that one cannot subtract arbitrary selected multipliers.

Please ensure that every empirical “continuation price” comparison obeys this rule. A solver-returned multiplier is not automatically the economically relevant directional price at degeneracy.

## 12.3 Proposition 5.2 should not be read as a cheap zero-set algorithm

The proposition avoids a full-class optimization at every friction value, but it may still require:

- enumerating the restricted parametric cells;
- refining them by switching signs and active accepted rows;
- solving a full-dimensional KKT feasibility problem on each cell.

The paper already says there is no polynomial bound on the number of cells. I would add one sentence in the main proposition discussion explicitly saying that this is a structural reduction, not a general computational-complexity improvement.

## 12.4 The exact promised-payment state is institution-dependent

The recursion is exact because the continuation obligation is additive and summarized by a remaining scalar payment b, while other required state is explicitly carried. This should remain tightly tied to the service institution.

The general polyhedral model elsewhere allows signed coefficients and arbitrary additional accepted constraints. Those do not automatically admit the scalar promise state. The current text mostly respects this boundary; please make it explicit whenever results from Sections 4–5 are interpreted through Section 6.

## 12.5 Theorem 7.3 avoids query restricted optimization, not query optimization in general

The cache computes an upper bound on the restricted comparator without a fresh restricted solve. The deployed adaptive policy still has to come from somewhere, and its feasibility/value must be audited.

The R27 study uses query-specific full-class proposals offline. Therefore “no query optimization” would be false if interpreted for the whole deployment system. The manuscript usually says “no restricted optimization,” which is correct. Keep that wording everywhere.

## 12.6 Query arithmetic is not complete certificate cost

The O(n(d+1)) per-anchor count is for the cached upper-bound evaluation after preprocessing. A complete economic certificate also needs the implemented-policy value and feasibility checks against the actual query constraints, which can cost O(nnz(A_theta)) or more depending on representation.

The paper acknowledges this qualitatively. I recommend displaying the complete per-query accounting in one compact table so that the attractive cache arithmetic is not mistaken for total deployment cost.

## 12.7 The uniform fixed-policy corollary should state nonemptiness/feasibility assumptions prominently

The theorem assumes every restricted class is nonempty and the fixed implemented policy is feasible for the full accepted class throughout the parameter set. These are strong but reasonable assumptions. They should be repeated in the statement/discussion of the positive uniform example, not left implicit through the general model declaration.

## 12.8 The cache family fixes more geometry than the phrase “jointly changing costs” may suggest

Only the scalar friction coefficient changes in the switching penalty; D,h,kappa,H,R stay fixed. I recommend wording such as “jointly changing rewards, commitments, continuation coefficients, and switching-friction scale” rather than a broader phrase that may suggest arbitrary cost-function perturbations.

## 12.9 The negative learning results should remain, but no further learning experiments are needed

The historical evidence is now scientifically useful precisely because it prevents an unsupported computational-advantage narrative. The strict-target 100% fallbacks and absence of observed finite amortization should remain visible, but I would not spend additional revision effort on neural architectures.

## 12.10 The data/code section is strong

The distinction between current journal-facing argument, preserved predecessors, and computational archive is much clearer than in earlier revisions. I have no major objection here.

---

# 13. What I would require before acceptance could be considered

I would not ask for another broad expansion. I would ask for a **consolidating revision** with the following minimum deliverables.

### 13.1 One central novelty claim

Identify one theorem chain that is the paper's primary contribution and rewrite the abstract/introduction around it. Every other result should support that chain.

### 13.2 A bridge between stochastic state compression and restriction/comparator certification

This is the single most valuable possible revision. Show how the release value, restriction rent, or cached comparator can be represented/certified in the sufficient augmented state without reconstructing the full history vector, at least under a meaningful subclass.

### 13.3 A closest-results comparison

Add explicit comparisons to multiparametric QP sensitivity, Bellman promise/resource states, stochastic dual cuts/Benders-style upper bounds, and reusable dual certificates. State exactly what is new beyond each.

### 13.4 A clearer economic status for the restriction hierarchy

Either model the cost/choice of information resolution or consistently describe the hierarchy as exogenous feasible-set accounting.

### 13.5 A cache-governance result

Provide a certified face-retention/quality test or refresh rule. The current local quadratic statement is too conditional to carry a practical reuse claim by itself.

### 13.6 Align the continuous uniform theorem with adaptive deployment

Either extend the uniform certificate to a declared parameter-dependent policy map or clearly separate fixed-policy uniform guarantees from query-specific pointwise policies.

### 13.7 One compact scaling experiment

No new machine learning is needed. Vary problem size, parameter dimension, cache size, and active-face instability; report total certificate cost and quality.

---

# 14. Recommendation to the editor

R27 is a substantial and serious revision. The authors have addressed many of the concrete scientific objections visible in the predecessor review history. The optimized comparator is now genuinely analyzed rather than merely named; the continuation institution is coherent; the horizon caveat is explicit; the robust outer-comparator weakness has a mathematically better alternative; the learning evidence is honestly negative; and the reproducibility package is strong.

For those reasons I would **not** repeat the R24-style objection that the paper is only a transfer-coordinate reparametrization. It is no longer that paper.

However, I am still not ready to recommend publication in Operations Research. The principal results remain too readily decomposable into standard parametric-QP sensitivity, envelope identities, Bellman sufficiency, concave interpolation, and weak-duality certification. The stochastic recursion and the full-vector restriction/certification machinery are not yet joined by a theorem. The implementable information hierarchy is exogenous. The attractive cache-quality result is local to a retained priced face, and the continuous uniform guarantee is for a fixed policy rather than the adaptive policy mechanism that motivates the paper.

These are not copy-editing issues, but neither do they require another sprawling research program. A focused revision could resolve them if it produces a genuine bridge theorem and sharply isolates novelty.

**Decision recommendation: Major Revision.**

**Acceptance should require consolidation and a new unifying result, not additional layers of experiments or certificates. If the next revision cannot show a mathematically or operationally nontrivial link between continuation-state structure and restriction/comparator certification, I would then recommend rejection on novelty and scientific-identity grounds.**
