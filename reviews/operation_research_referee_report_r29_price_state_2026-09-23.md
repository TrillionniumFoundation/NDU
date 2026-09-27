# Confidential Referee Report for Operations Research

**Manuscript:** *Accepted Service Adaptation: Finite Continuation Prices and the Value of Memory*  
**Revision reviewed:** `revision/ndu-operations-research-r29-price-state-20260923`  
**Review branch:** `review/operation-research-r29-price-state-harsh-20260923`  
**Recommendation:** **Reject; a substantially reworked paper could be resubmitted as a new manuscript**

---

## Executive assessment

This is a genuine scientific revision, unlike the nominal R29 branch reviewed previously. The manuscript now has a new theorem-level center: a finite continuation-price construction for a positive-payment, separable quadratic, no-switching subclass; a linear-order memory lower bound and an exact memory-value frontier for a renewal family; a graph-sized zero-release shared-table formulation; and a fixed-table exact supporting-cut oracle. The new branch is materially different from the earlier manuscript and directly responds to the previous report's request for a constructive, graph-input result.

The main theorem is interesting. Its key idea is that, under one scalar additive commitment and separable strictly concave local rewards, every continuation cap acts as a one-sided reflection of a monotone payment response. A public vertex contributes at most one cap threshold, local actions contribute at most two clipping thresholds, and the union of breakpoints can therefore be bounded on the compact recombining graph rather than on its exponentially larger history unfolding. The resulting running-maximum price state is operationally interpretable and the lower-bound example shows that a nonconstant amount of memory can genuinely be necessary.

I nevertheless do not recommend publication in *Operations Research* in the present form. The reason is no longer lack of scientific delta. The problem is that the revision still has not established the priority and significance of its central algorithmic theorem against the closest classical Operations Research literature, and its computational study does not test the theorem against the relevant algorithmic baselines.

Most importantly, the manuscript compares the new construction to nested resource allocation on chains and to SDDP/policy-graph decomposition, but it omits the substantially closer literature on **separable convex resource allocation with tree/laminar constraints**. The full-history version of the manuscript's principal no-switching model is exactly a separable concave allocation problem with subtree-sum constraints, i.e. a laminar/tree-constrained resource-allocation structure. At a minimum, the paper must confront:

- K. M. Mjelde (1983), “Resource Allocation with Tree Constraints,” *Operations Research* 31(5):881–890, DOI 10.1287/opre.31.5.881.
- C. S. Tang (1990), “Reducing Separable Convex Programs with Tree Constraints,” *Management Science* 36(11):1407–1412, DOI 10.1287/mnsc.36.11.1407.

The latter explicitly gives a reduction procedure for separable convex programs with tree constraints; the former is in this journal and studies concave resource allocation under nested subset constraints arranged as a tree. These are not peripheral citations. They are structurally closer to the manuscript's expanded primal problem than the chain-nested allocation references currently emphasized.

The potentially publishable residual claim is therefore not “tree-constrained separable allocation admits scalar prices” or “caps create thresholds.” Those ideas are old. The residual claim would have to be stated much more sharply: **repeated subtree structure in a compact recombining public DAG can be quotient-compressed into a finite family of response functions whose total breakpoint universe is linear in the compact graph, yielding an exact policy with a finite endogenous price-memory state without unfolding the laminar scenario tree.** I can believe that this quotient theorem is new, but the manuscript has not yet demonstrated that it is not an immediate memoized/recombined form of the classical tree-constraint reductions. Until that comparison is done carefully, the priority case is incomplete.

The computational evidence is also not yet sufficient for an algorithmic contribution at the *Operations Research* level. The reported exact checks are valuable for correctness, but the timing section is essentially an internal verification study of the authors' own rational-arithmetic implementation. There is no comparison to tree-constrained resource-allocation algorithms, no comparison to a full-tree convex solver over the range where unfolding remains possible, no comparison to a promise-state dynamic program, and no serious comparison to policy-graph decomposition or generic convex optimization on appropriate formulations. The 190-vertex / 64-date example is useful as a proof-of-concept, but “the unfolded tree would contain (3^{64}) histories” is not itself a meaningful computational benchmark because modern policy-graph methods also avoid naive scenario-tree enumeration.

For these reasons, I view the current paper as a promising new methodological manuscript whose central result has not yet been placed securely enough in the OR literature to clear the journal's novelty bar.

---

# 1. Version audit and scientific delta

The current branch is substantively new. Relative to the previously reviewed nominal R29 manuscript, it introduces:

1. a new finite-price construction on a recombining public DAG;
2. an explicit arithmetic/storage bound for complete payment-response functions;
3. a finite endogenous price-label implementation;
4. a matching linear-order necessary-memory family;
5. an exact memory-value frontier via ordered segmentation;
6. a graph-sized zero-release shared-table QP;
7. a fixed-table positive-release exact oracle and supporting cuts;
8. a new exact computational suite aimed at the central coupled stochastic graph.

This is the kind of change the previous report requested. I therefore do **not** repeat the prior criticism that the revision contains no new manuscript content.

The current paper should be evaluated on the merits of these new results.

---

# 2. What I believe the central theorem actually proves

Theorem 4.1 is best understood as a compact-input quotient result for a special separable laminar allocation problem.

For a public DAG vertex (v), define the optimal conditional payment response (R_v(eta)) to an incoming scalar payment price (eta). Because the local reward is strictly concave quadratic, the local action response is clipped affine. Because successor payment responses are continuous, nonincreasing, and piecewise affine, their weighted sum is again continuous, nonincreasing, and piecewise affine. Imposing the current continuation cap truncates that response from above, which adds at most one new threshold (alpha_v). Hence every graph vertex adds at most three globally new knots: two local clipping knots and one cap threshold.

The operational policy then propagates
[
s_v=max{eta,alpha_v},
]
so the only dynamically changing information is the largest threshold seen along the realized path, plus the root price.

This is a clean result. The proof is short because the important closure property is scalar order plus additive payment separability.

I find the theorem mathematically plausible and, on the assumptions stated, I did not identify a counterexample in the manuscript or implementation. The independent verifier checks the same response identities over many exact rational instances, and the code does not appear to rely on an extensive-form solution to generate the response curves.

The publication question is therefore not “does the theorem obviously fail?” It is “is this theorem genuinely new relative to the correct classical algorithmic literature, and is the compact-DAG quotient sufficiently important to justify an *Operations Research* paper?” The current revision has not yet answered that question.

---

# 3. The closest literature comparison is still incomplete

This is my principal concern.

The manuscript now cites Vidal–Jaillet–Maculan, Schoot Uiterkamp–Hurink–Gerards, and Wu–Nip–He on nested resource allocation. That is an improvement. But those papers emphasize nested/ascending constraints, often on a chain. The present full-history constraints are not merely a chain: they are subtree constraints on a scenario tree, hence a **laminar family**.

That structure has a long OR literature. In particular:

- Mjelde (1983, *Operations Research*) explicitly studies concave resource allocation with constraints on totals over subsets, subsets of subsets, and so on — exactly the tree/laminar pattern.
- Tang (1990, *Management Science*) studies separable convex programs with tree constraints and gives a reduction procedure solving the problem through a linear number of one-variable convex subproblems.

The manuscript's finite-price proof uses exactly the kind of scalar marginal-price and subtree reduction structure one would expect in this literature.

The authors need to answer, theorem by theorem:

1. If the public DAG is unfolded to a history tree, is the resulting optimization problem a direct special case of Mjelde/Tang tree-constrained resource allocation after sign changes and probability weighting?
2. If yes, what part of Theorem 4.1 is not already implicit in their reduction?
3. Does memoizing identical subtree response functions in the classical reduction immediately produce the manuscript's compact-DAG recursion?
4. If not, what feature of the recombining stochastic graph prevents that equivalence?
5. Is the (|mathcal B|le 3N) global knot-union bound new, or can it be extracted from the classical reduction?
6. Is the (N+1) realized price-label bound new, or is it an immediate corollary of the classical multiplier propagation?
7. What is the strongest previously known complexity bound for the exact quadratic tree-constrained problem, and what is the precise input model used there?
8. What is the complexity of applying that method to the unfolded tree versus applying the new quotient method directly to the compact DAG?

The novelty matrix currently skips this entire comparison. In my view, this is not acceptable for an algorithmic paper at *Operations Research*, especially when one of the omitted papers is from *Operations Research* itself.

---

# 4. The compact-DAG contribution needs a formal quotient theorem

The proof of Theorem 4.1 starts from a finite unfolding to invoke convexity and uniqueness, then switches to a graph-level induction. I believe the argument can be made rigorous, but the manuscript should state the quotient property explicitly rather than leave it implicit.

A formal statement should distinguish:

- a **public vertex** (v) in the compact DAG;
- an **occurrence** (h) of that vertex in the unfolded history tree;
- the incoming accumulated price (eta_h);
- the fact that all primitives below occurrences of the same public vertex are identical except for the scalar incoming price.

The authors should prove explicitly that every occurrence (h) of public vertex (v) with incoming price (eta) has the same optimal conditional response (R_v(eta)), regardless of the ancestor path that produced (eta). That is the exact quotient property that allows repeated subtrees to be represented once.

This matters because the manuscript's claimed complexity advantage lives entirely in the difference between the compact graph and the unfolded laminar tree. The proof should isolate that step as a theorem, not just treat the graph recursion as self-evident.

I would also like to see a precise complexity comparison of the form:

- compact input size: (N) public vertices, (M) public edges, rational primitive encoding length (L);
- unfolded tree size: (H), potentially exponential in horizon;
- new arithmetic work/storage as a function of (N,M);
- classical tree algorithm work/storage as a function of (H);
- statement of what is and is not claimed about bit complexity in (L).

Without this, the reader cannot tell whether the main result is a genuinely new quotient algorithm or simply a different presentation of an old tree reduction.

---

# 5. Arithmetic complexity is not bit complexity, and the distinction matters here

The manuscript is careful to say that
[
O((N+M)Nlog(N+1))
]
is an arithmetic-operation bound rather than a rational bit-complexity bound. That qualification is correct, but it is more consequential than the current presentation suggests.

The exact implementation repeatedly:

- forms weighted sums of rational slopes/intercepts;
- computes new breakpoint locations by solving rational affine equations;
- merges curves across many stages.

Even with only (O(N)) distinct knots globally, numerator and denominator sizes can grow substantially with horizon and transition denominators. The exact Python timings reported in the paper are therefore not explained by the arithmetic count alone.

For a theory paper, the authors have two defensible options:

1. provide a polynomial bit-growth / bit-complexity bound under a stated rational encoding model; or
2. keep the result explicitly in the real-RAM/arithmetic model and remove any language that could be read as a conventional polynomial-time algorithmic claim.

At minimum, the experiments should report coefficient bit lengths as a function of graph size and explain whether those lengths grow linearly, quadratically, or worse in the tested families. The current package records some bit-length information, but the paper does not use it to characterize the cost of exact arithmetic.

---

# 6. The memory theorem is interesting but narrower than the narrative sometimes suggests

Theorem 5.1 is a useful addition. It does two things:

1. proves a worst-case (Theta(N)) lower bound on the number of distinct dynamic labels required for exact implementation in a deliberately recombining family;
2. computes the exact value of a finite memory alphabet in that family via ordered segmentation.

I accept the logic of the construction. The strict concavity/monotonicity argument forces distinct optimal terminal tiers, so a deterministic controller at the common terminal public state must distinguish the predecessor branches somehow.

However, the operational interpretation needs sharper boundaries.

The theorem is not a general optimal-memory theorem for the service-contract model. It is a three-date family engineered so that the only relevant history signal is the branch-specific continuation cap. The segmentation dynamic program is standard once the cell loss is derived. The result therefore establishes a worst-case memory lower bound and an exact frontier for one family, not a general characterization of optimal retention depth.

The manuscript should avoid phrases that make the result sound like a general theory of information architecture. A stronger contribution would characterize broader conditions under which optimal memory cells are ordered by continuation price, or show that the running-maximum price state is minimal in an automata/state-equivalence sense for a nontrivial class.

There is also a conceptual accounting issue that should be made completely explicit. The paper counts writable label bits but excludes:

- the read-only threshold table;
- numerical precision of the thresholds;
- any storage for the public graph and primitives;
- the root-price recomputation when the root promise changes.

This is a legitimate architecture convention, but the economic interpretation of “memory cost” depends heavily on it.

---

# 7. The service-contract interpretation remains weaker than the optimization contribution

The principal theorem assumes:

- positive scalar additive payments;
- exogenous public Markov transitions;
- separable strictly concave quadratic local rewards;
- scalar tier decisions or separable coordinates under one scalar commitment;
- no intertemporal switching cost in the central finite-price result;
- no coupled vector commitments;
- no private information;
- continuation caps that are public-state sufficient.

Under these assumptions, the problem is very close to a structured resource-allocation problem. The “service contract” interpretation is possible, but it does not itself create the mathematics.

That is not fatal for a methodological paper. But then the optimization novelty must be especially clear.

If the authors want the operational application to carry part of the contribution, they need at least one substantive service-design result that is not simply a relabeling of a budget-allocation theorem. For example:

- conditions under which renewal rights generate strictly more memory than the physical Markov state;
- comparative statics linking cap heterogeneity to the number of active price labels;
- a theorem connecting contractual outside-option dispersion to memory value;
- a calibrated or realistically parameterized service example demonstrating a nonobvious design implication.

At present, the application remains synthetic and illustrative.

---

# 8. The zero-release shared-table formulation is correct but standard in spirit

Proposition 6.1 is useful because it prevents the common mistake of reselecting the table independently in each successor. The graph-sized conditional-payment recursion is the right way to compile one shared public table.

But the proposition is not, by itself, an algorithmic novelty. The paper acknowledges this.

The important role of this section should therefore be supporting, not coequal with the finite-price theorem. I recommend shortening it in the main paper and moving more of the general shared-table machinery to the companion.

Also, the notation is unnecessarily confusing: (K) is used both for the number of information cells and elsewhere for a restricted value. Please separate those symbols.

---

# 9. The positive-release oracle is useful, but the outer design problem remains unresolved

Proposition 6.2 is a legitimate improvement over the old extensive-form-dual representation: for a fixed table and release radius, the new finite-price engine supplies an exact value and a supporting cut without first solving the full history tree.

That is worthwhile.

However, the outer continuous shared-table problem still has a standard Benders-style master with no finite exact cut bound. Therefore the paper should not let this section blur the distinction between:

- an exact compact oracle for each fixed table query; and
- an exact polynomial algorithm for the globally optimized positive-release table problem.

The manuscript mostly makes this distinction correctly. It should continue to do so, and the abstract should not imply that the shared-table design problem as a whole has the same finite complexity guarantee as the price-response construction.

---

# 10. The computational evidence validates implementation, not comparative performance

The exact rational verification is a strength. In particular, the package contains:

- whole response-curve identity checks;
- exact state-flow checks;
- local KKT checks;
- exact primal-dual equality;
- small unfolded-tree cross-checks;
- exact memory-frontier enumeration for small (k);
- exact supporting-cut checks.

This is unusually auditable.

But these checks answer “did the code implement the theorem?” They do not answer “is the new algorithm computationally important relative to existing OR methods?”

The computational section should include at least the following baselines.

### 10.1 Classical tree-constrained allocation

Implement or obtain a faithful implementation of a directly relevant tree/laminar allocation algorithm, at least for the quadratic case. Compare on unfolded instances as far as memory permits.

The point is not that the tree method will win at 64 ternary dates — it obviously cannot even materialize that tree. The point is to identify empirically when the compact quotient becomes material and whether the new response construction has a meaningful constant-factor cost before that crossover.

### 10.2 Generic convex optimization on the unfolded model

For small-to-medium history trees, solve the exact quadratic program with a high-quality commercial or open-source solver and compare value, runtime, and memory.

### 10.3 Promise-state dynamic programming

Where a fine exact or near-exact promise grid is possible, compare against the natural state recursion. This would show what is gained by the finite dual-price state versus the primal promise state.

### 10.4 Policy-graph / decomposition baseline

Because the paper cites policy-graph decomposition and SDDP as the modern comparison, it should include at least one computational comparison or a carefully justified explanation of why such a comparison is not meaningful for exact single-query evaluation.

### 10.5 Scaling beyond 190 public vertices

An (O(N^2))-storage exact-response method should be tested at much larger compact graph sizes. Hundreds of vertices are too small to reveal the practical cost of the quadratic response-table growth or rational coefficient inflation.

The paper should report:

- response-construction time;
- root-query inversion time;
- certificate-generation time;
- audit time;
- peak memory;
- total stored segments;
- maximum segments at one vertex;
- coefficient bit lengths;
- repeated-query amortization if multiple root promises are a target use case.

Single-run timings are acceptable as supplementary diagnostics, but not as the main computational case for an algorithmic OR contribution.

---

# 11. The “exponential scenario tree” comparison is rhetorically too easy

The statement that a 64-date three-regime instance would have roughly ((3^{64}-1)/2) unfolded histories is mathematically true, but it is not a strong computational comparison.

No competent multistage stochastic-programming implementation would explicitly enumerate that tree when the public process is Markov and recombining. Policy graphs, state aggregation, dynamic programming, and approximate decomposition exist precisely to exploit such structure.

The new theorem's real contribution is stronger and more specific: it claims an **exact** finite response closure and an **exact** bounded endogenous memory state for a special continuous-control problem.

The computational narrative should focus on that distinction instead of using naive tree size as the principal scale contrast.

---

# 12. The paper remains too broad for its new theorem-level center

The main manuscript still preserves:

- release-frontier sensitivity;
- comparator-adjusted continuation rents;
- switching-friction paths;
- promise-state recursion;
- continuous-state envelopes;
- the old shared-table bridge;
- reward-only cache bounds;
- correlated cache bounds;
- outer-set loss bounds;
- cache governance;
- adaptive Bernstein certificates.

Many of these results are individually correct and useful. But they do not all belong in the same *Operations Research* paper once the new finite-price theorem becomes the center.

The repository may preserve every historical derivation. The journal manuscript does not need to.

The current preservation-driven architecture makes the paper read like a research program archive rather than a focused article. It also makes novelty adjudication much harder because inherited, standard, and new claims are interleaved.

I strongly recommend a publication version organized around:

1. the compact-DAG finite-price theorem;
2. the precise relation to tree/laminar resource allocation;
3. the minimal-memory theorem;
4. the shared-table comparator needed for the economic benchmark;
5. computational evidence targeted at those results.

The older sensitivity/cache/certificate machinery can remain in the repository or a separate companion unless it is essential to a theorem used in the main argument.

---

# 13. Technical comments on Theorem 4.1

I did not find a decisive mathematical error, but several points need tightening.

### 13.1 Define capped and uncapped response functions separately

The notation (H_v(eta)) is introduced as the value subject to all caps, while (d_v(eta)) is the payment before imposing the current cap. The proof then refers to an “uncapped” problem.

Introduce explicit notation such as (H_v^{mathrm{pre}}) or (widetilde H_v) for the problem with successor caps imposed but the current cap removed. This will make the reflection proof much easier to audit.

### 13.2 Root equality versus root cap

State explicitly whether the root also has a cap (B_0), and require
[
b_0in[L_0,U_0]subseteq(-infty,B_0].
]
The implementation assumes both the root response curve and the exact root promise.

### 13.3 Plateau convention

The “leftmost finite solution” convention for (d_v(alpha_v)=B_v) is reasonable. Please prove explicitly that using (max(eta,alpha_v)) is valid on an equality plateau and that the induced policy remains unique even if the dual price is not unique.

### 13.4 Occurrence-to-vertex invariance

As noted above, this should be stated as a separate lemma. It is the formal reason recombination is safe.

### 13.5 Global knot count versus stored segments

The global distinct knot universe is (O(N)), but storing a separate piecewise-affine response at every vertex is (O(N^2)) in the worst case. The paper states this, but some prose reads as though the response representation itself were linear size. Keep the distinction visible.

### 13.6 Multi-coordinate corollary

Corollary 4.2 states that the breakpoint universe grows with total local action dimension (D), while the dynamic price-label count remains at most (N+1). This is plausible because only cap barriers become dynamic labels. Please explain this distinction in words; otherwise readers may wonder why local action knots do not increase the number of realized incoming prices.

---

# 14. Technical comments on the memory frontier

### 14.1 Clarify the controller model

Define exactly what counts as a memory symbol. Does the controller have access to:

- current public regime;
- date;
- inherited physical tier;
- current remaining promise;
- root price;
- read-only threshold table?

The example suppresses several of these by construction. The theorem should state the observation model explicitly so that “at least (k) symbols” cannot be evaded by carrying the branch identity in another state variable.

### 14.2 Randomization

The theorem is stated for deterministic implementation. Because the objective is strictly concave, I suspect the lower bound extends naturally to randomized controllers if the same expected feasibility requirements are used. Either prove that or explain why deterministic policies are the intended contract class.

### 14.3 Broader structural result

If possible, strengthen the theorem beyond the crafted family. A characterization of when memory cells must be contiguous in continuation-price order for a broader class would substantially improve the paper.

---

# 15. Technical comments on the shared-table oracle

The supergradient formula has the correct qualitative sign structure: upper corridor multipliers contribute positively to the table center and lower multipliers negatively; both contribute positively to release width.

However, the treatment of ties between physical bounds and corridor bounds should be formalized carefully. The code tests a clean interior-center case in which the corridor, not the physical box, is active. The theorem claims validity under ties and zero-width intersections. The companion should give a complete normal-cone decomposition proving that the chosen split always exists and preserves the global supporting inequality.

Also distinguish “supergradient of the fixed-table value in the design parameters” from “Benders cut sufficient to solve the global design problem in finitely many iterations.” Only the former is established.

---

# 16. Literature and positioning changes required

At minimum, the revision should add and discuss:

1. Mjelde (1983), *Operations Research*, “Resource Allocation with Tree Constraints.”
2. Tang (1990), *Management Science*, “Reducing Separable Convex Programs with Tree Constraints.”
3. The broader laminar/submodular resource-allocation literature if relevant to the exact feasible-set geometry.
4. The existing nested resource-allocation papers already cited.
5. Policy-graph decomposition and SDDP, but only after the classical deterministic/laminar connection is addressed.

The paper should include a proposition or table mapping its expanded no-switching problem to the notation of the classical tree-constrained allocation literature.

The burden is then to identify the exact extra result supplied by **recombination and quotienting**, not to re-establish scalar marginal allocation from scratch.

---

# 17. What would make a new submission compelling

I would take a substantially revised new submission seriously if it did all of the following.

## A. Establish priority against tree/laminar allocation

Prove explicitly what is new relative to Mjelde/Tang and later laminar allocation algorithms.

A strong form would be:

- full history problem belongs to a known tree-constrained class;
- known methods scale with unfolded tree size (H);
- repeated stochastic subtrees admit a quotient representation on a public DAG of size (N);
- the quotient has a globally bounded response-knot universe;
- exact optimal execution requires only a finite endogenous price automaton;
- this quotient theorem is not obtained by a previously published reduction.

## B. Strengthen complexity reporting

Give either a rational bit-complexity result or a disciplined arithmetic-model theorem plus empirical coefficient-growth results.

## C. Add serious algorithmic baselines

Benchmark against the closest exact tree/laminar methods, generic QP on unfoldable instances, and at least one state/decomposition alternative.

## D. Sharpen the memory result

Either generalize the ordered-memory frontier or characterize minimal price-state memory for a broader class.

## E. Focus the paper

Remove most inherited cache/governance/sensitivity material from the journal manuscript unless it is directly used by the new theorem.

## F. Strengthen operational interpretation

Give a nontrivial service-contract implication that depends on continuation participation and recombination, not merely on generic resource scarcity.

---

# 18. Minor and presentation comments

1. The title is much better aligned with the new contribution than the previous title.
2. The abstract appropriately discloses the no-switching subclass and the adverse cache result.
3. The phrase “finite continuation prices” can be misread as saying the dual prices themselves take finitely many possible values for all promises. The theorem gives finitely many realized labels for a fixed root query plus barriers. Consider wording this more precisely.
4. The manuscript should define (d_v(-infty)) as the finite left-tail constant rather than use extended-real notation informally.
5. Use different symbols for the number of information cells and the restricted value (K).
6. The “Lengthy Manuscript” format may satisfy page guidance, but editorially the current breadth remains excessive.
7. The repository preservation machinery is impressive but should not occupy scientific narrative space.
8. The exact verifier is a strength; describe it as implementation verification, not independent mathematical proof.
9. The 83/84 cache-refresh result is correctly retained and should remain clearly separated from the new algorithm.
10. The literature-audit file should be expanded to include the tree/laminar allocation lineage before the authors make any residual priority claim.

---

# 19. Recommendation to the editor

This revision is scientifically much stronger than the manuscript I reviewed previously. It now contains a genuinely constructive theorem and a meaningful memory consequence. I would not reject it for lack of effort, lack of mathematical content, or lack of reproducibility.

I nevertheless recommend **Reject** in its present form.

The central reason is that the paper has not yet established that its main exact algorithmic result is new relative to the most directly relevant classical OR literature on separable convex/concave resource allocation with tree constraints. That omission is particularly important because the expanded scenario-tree model is visibly laminar, and classical papers in *Operations Research* and *Management Science* already solve closely related tree-constrained allocation problems using scalar marginal structure.

The compact recombining-DAG quotient may well be the genuinely new result. If so, the authors should rebuild the paper around that precise distinction, prove the quotient relationship formally, benchmark it against the correct baselines, and narrow the surrounding material.

I would be open to evaluating such a substantially reworked paper as a new submission.

**Decision recommendation: Reject; encourage a fundamentally revised resubmission centered on the compact-DAG quotient theorem and its minimal-memory consequences.**
