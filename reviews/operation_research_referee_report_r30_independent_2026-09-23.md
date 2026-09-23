# Confidential Referee Report for Operations Research

**Manuscript:** *Accepted Service Adaptation: Compact Allocation Quotients and Minimal Price Memory*  
**Revision reviewed:** `revision/ndu-operations-research-r30-quotient-memory-20260923`  
**Reviewed commit:** `fdc1ed47d46dc9d3344b8bce47c1670f11dcd475`  
**Review branch:** `review/operation-research-r30-independent-harsh-20260923`  
**Recommendation:** **Reject; encourage a substantially reframed resubmission after the remaining priority and significance questions are closed**

---

## Executive assessment

R30 is a real and substantial scientific revision. This point matters because an earlier same-day review branch was created against an obsolete view of the remote state and concluded that R30 contained no scientific changes. That conclusion is not correct for the revision reviewed here. Relative to `revision/ndu-operations-research-r29-price-state-20260923`, the current R30 branch is three commits ahead and changes the main manuscript and electronic companion, adds a new theorem package, a response to referees, new comparison algorithms, new exact tests, and a new computational study.

The authors have addressed most of the concrete objections in the previous R29 report. In particular, R30 now (i) maps the unfolded problem explicitly into classical laminar/tree-constrained resource allocation; (ii) acknowledges that normalized memoization of a classical occurrence-indexed reduction gives the same compact-graph recursion; (iii) proves an occurrence-to-vertex quotient instead of leaving recombination implicit; (iv) gives a rational bit-complexity theorem rather than only an arithmetic-operation count; (v) replaces a worst-case memory example by a backward behavioral-equivalence theorem for the exact writable alphabet; (vi) extends the renewal frontier to heterogeneous probabilities and costs; (vii) adds an outside-option comparative static; (viii) supplies tree, generic convex, and public-graph promise-state comparisons; and (ix) separates the focused R30 article from the retained broader switching/cache/deployment theory.

This is a much stronger paper. I did not find a simple counterexample to the central reflection recursion, quotient identity, minimal-alphabet construction, renewal segmentation formula, or tied-bound supporting-cut argument. The exact verification package is unusually careful.

I nevertheless do not recommend publication in *Operations Research* at this stage. The reason has changed. The paper has correctly conceded that scalar marginal allocation, laminar reduction, and memoization are inherited. Once those claims are removed from the novelty case, the publication burden falls on three residual contributions:

1. a **complete parametric response representation** on the compact DAG, including breakpoint and rational bit bounds;
2. a **minimal additional writable-memory representation** obtained by behavioral quotienting; and
3. a **contractual interpretation** of that memory through renewal participation constraints.

Those are potentially publishable ideas, but the current literature audit is still centered on the literature identified by the previous referee. It does not yet confront the literatures that become closest *after R30's own reframing*: parametric quadratic optimization, state/model minimization and automata minimization, and finite policy-graph representations in dynamic contracts. Consequently, I cannot verify the claimed residual priority at the level expected for a top OR journal.

There is also a theorem-level significance issue. The paper proves useful upper bounds, but gives no matching worst-case lower bounds for the linear global-knot universe or quadratic total response storage. The experiments exhibit dense response tables, but a computational stress example is not a complexity lower bound. Because R30 now presents representation complexity as a principal theoretical contribution, tightness is no longer optional positioning detail.

My recommendation is therefore **Reject, with encouragement to resubmit after a sharper priority audit, matching lower-bound/tightness results or a meaningful generalization, and a more precise statement of what "minimal memory" means under the paper's observation architecture.** This recommendation is not based on a detected correctness failure or poor reproducibility.

---

# 1. Version audit: R30 is a substantive revision

The current R30 should not be evaluated as a nominal branch rename. A direct comparison with the R29 price-state revision shows, among other changes:

- `main.tex` is materially rewritten;
- `electronic_companion.tex` is materially rewritten;
- a complete `revisions/or-r30-quotient-memory-20260923/` theorem and implementation directory is added;
- the R29 manuscript is preserved under `predecessor/`;
- a point-by-point `RESPONSE_TO_REFEREES` is added;
- new files implement an independent unfolded laminar baseline, a public-graph promise-state baseline, exact behavioral minimization, corridor tests, and larger scale families;
- the new manuscript is 22 pages plus a 10-page electronic companion.

The scientific delta is therefore large and directly responsive to the prior report.

This matters for editorial history: future reviews should identify the exact commit being reviewed, because the repository is moving rapidly and branch names alone have already produced one stale audit.

---

# 2. What R30 now establishes credibly

Before discussing remaining objections, I want to record what I regard as genuine progress.

## 2.1 The laminar connection is finally stated correctly

Proposition 2.1 gives an invertible probability-weighted transformation from the occurrence-indexed accepted-service problem to separable concave allocation with laminar descendant constraints. Mjelde (1983) and Tang (1990) are now treated as structural predecessors rather than peripheral citations.

This is the right intellectual starting point.

## 2.2 The quotient theorem is no longer implicit

Theorem 3.1 now distinguishes a public vertex from its occurrences in the unfolded history tree and proves that two occurrences at the same public vertex and the same incoming scalar price have the same normalized continuation problem and optimizer. This is the exact quotient statement the previous report requested.

The recursion
[
x_v^0(eta)=[(r_v-a_v eta)/q_v]_{[l_v,h_v]}, qquad
d_v(eta)=a_vx_v^0(eta)+betasum_w p_{vw}R_w(eta), qquad
R_v(eta)=min{B_v,d_v(eta)}
]
and the reflected price (s_v=max{eta,alpha_v}) are now cleanly separated into pre-cap and capped objects.

## 2.3 The arithmetic/bit distinction is addressed

Theorem 3.3 explicitly introduces total rational input length (L), coefficient height (S), and a bit-operation bound. The manuscript does not claim strong polynomiality. This is a major improvement over an arithmetic-only complexity statement.

## 2.4 The memory theorem is materially stronger

Theorem 4.1 is not merely a crafted lower-bound instance. For a fixed root query and a specified observation architecture, it recursively identifies two reachable price states exactly when they induce the same complete future optimal behavior. The minimum common writable alphabet is the maximum number of behavioral classes at a public vertex.

The strict example in the companion showing that two numerical prices can collapse to one behavioral symbol is particularly useful: it demonstrates that the theorem is not just "count the barriers."

## 2.5 The computational section now has a meaningful public-graph control

The promise-grid baseline is more informative than a naive scenario-tree comparison because it already exploits the same public graph. The paper correctly states that the contribution is exact continuous closure, not merely avoiding explicit histories. This is the right comparison narrative.

These improvements are substantial. The remaining issues below arise precisely because R30 has clarified what its actual contribution is.

---

# 3. The closest remaining literature is now parametric optimization, and it is missing

R30 correctly states that memoizing normalized tree responses yields the same graph recursion. This is intellectually honest, but it moves the novelty question one level deeper:

> What is new about constructing the **entire parameterized response family**, bounding its breakpoints/output size, and doing so with exact rational bit complexity?

The current literature section does not answer that question.

A particularly relevant omitted paper is:

- Max Klimm and Philipp Warode (2021), “Parametric Computation of Minimum-Cost Flows with Piecewise Quadratic Costs,” *Mathematics of Operations Research* 47(1):812–846, DOI 10.1287/moor.2021.1151.

That paper develops parametric algorithms for separable, continuous, piecewise-quadratic strictly convex flow problems and explicitly relates algorithmic steps to breakpoints in the parametric output, obtaining output-polynomial algorithms. I am **not** asserting that their network-flow feasible set subsumes the present laminar quotient, or that their theorem implies the (3N) knot bound. It may not. The problem is that R30's residual novelty is now explicitly a parametric-response theorem, and the manuscript does not compare itself to a modern MOR paper whose central object is a piecewise-quadratic parametric optimum and its breakpoints.

The paper should also discuss the broader sensitivity/parametric lineage for separable optimization over polymatroids. For example:

- Tobias Harks, Max Klimm, and Britta Peis (2018), “Sensitivity Analysis for Convex Separable Optimization Over Integral Polymatroids,” *SIAM Journal on Optimization* 28(3):2222–2245, DOI 10.1137/16M1107450.

Again, the integral sensitivity theorem is not the same as the continuous quadratic result here. But after R30 explicitly identifies its feasible set as a truncated laminar polymatroid base, omitting the parametric/sensitivity literature leaves the priority audit incomplete.

### What I require

The authors should add a theorem-by-theorem comparison answering at least:

1. Is (R_v(eta)) a special case of a known parametric convex-program solution map after dualization or sign changes?
2. Which known parametric algorithms can compute the whole solution path for the unfolded laminar problem?
3. Does the compact-DAG quotient give a response-size bound that those results do not imply?
4. Is the global (3N) knot-union bound new as a structural statement, or merely a sharper bound for this subclass?
5. Is the stated binary rational bound stronger/different from existing output-polynomial parametric algorithms?
6. What is the exact novelty after normalized memoization is granted for free?

Until this comparison is done, the central algorithmic priority case remains unclosed.

---

# 4. The “minimal writable alphabet” theorem is very close to classical machine/model minimization

The second major novelty claim also needs a different literature audit than the one currently supplied.

The backward relation in Equation (4.1) says, in substance, that two states are equivalent if:

- they emit the same current action; and
- after every possible observed public transition, their successor states are equivalent.

That is exactly the structural pattern underlying minimization of deterministic output machines (Moore/Mealy-type machines), Myhill–Nerode-style behavioral equivalence, bisimulation/state aggregation, and minimal state models.

For example:

- Jacques Peyrière (2023), “Moore machines duality,” *Theoretical Computer Science* 951:113774, DOI 10.1016/j.tcs.2023.113774, explicitly studies a minimum-state equivalent Moore machine.
- Robert Givan, Thomas Dean, and Matthew Greig (2003), “Equivalence notions and model minimization in Markov decision processes,” *Artificial Intelligence* 147(1–2):163–223, DOI 10.1016/S0004-3702(02)00376-4, develops equivalence/bisimulation notions and minimal reduced MDPs preserving optimal policies.
- James C. Bean, John R. Birge, and Robert L. Smith (1987), “Aggregation in Dynamic Programming,” *Operations Research* 35(2):215–220, DOI 10.1287/opre.35.2.215, is an older OR reference on reducing dynamic-program state spaces through aggregation.

The R30 novelty matrix briefly calls the minimization principle “standard,” but the main paper does not cite or map to this literature. That is not enough, because Theorem 4.1 is advertised as one of the three main contributions.

I believe the genuinely model-specific content is potentially interesting:

- the quotient compiler produces a finite reached price machine from a continuous control problem;
- the behavioral classes are contiguous in price order;
- the exact optimal contract can need (Theta(N))-scale additional memory in an appropriate family;
- numerical price states can collapse strictly under behavioral equivalence.

Those are the aspects that should be claimed. By contrast, “backward signatures yield the minimum equivalent deterministic behavior machine” is a classical minimization principle.

### Required revision

Recast Theorem 4.1 explicitly as:

1. a reduction from the reached optimal price-state graph to a deterministic output transducer;
2. application of classical behavioral/state minimization to that transducer;
3. new structural consequences specific to the price-ordered contract problem (contiguity, size bounds, lower-bound family, and interaction with contractual caps).

That would make the novelty both stronger and more defensible.

---

# 5. “Minimal memory” is architecture-conditional, not an absolute controller-state complexity

The paper is aware of this issue, but the title and abstract still encourage a broader reading than the theorem supports.

The theorem gives the minimum **additional writable alphabet** under an architecture in which the decoder receives, without charge:

- the current public vertex, including date;
- a read-only graph/primitives table;
- the root price for the fixed query;
- thresholds and transition/output maps.

Any past branch identity, promise, previous tier, or retained random seed is charged only if it is carried outside that public observation.

Under that convention,
[
K_*=max_v c_v
]
is correct because symbol indices can be reused at different public vertices. But it is not the same object as:

- the total number of combined controller states ((v,	ext{symbol}));
- total read-only plus writable implementation memory;
- memory required when the current public state itself must be encoded;
- a query-uniform controller valid for all root promises.

This is not a flaw if the metric is stated narrowly. It becomes a flaw when “minimal memory” is used without the qualifier.

### I recommend reporting three quantities separately

1. **Additional writable alphabet:** (K_*=max_v c_v).
2. **Combined reached behavior states:** for example (sum_v c_v) (or the exact reachable combined-state count under the chosen representation).
3. **Read-only representation size:** graph, thresholds, response tables, and coefficient precision.

The title or abstract should say “minimal additional writable price memory” or otherwise make the free-public-observation convention impossible to miss.

The randomized extension also inherits this architecture dependence. The theorem assumes retained private randomness is charged as memory and feasibility is imposed in conditional expectation. If the service contract instead requires pathwise feasibility with respect to the controller's own randomization, that is a different admissible policy class. The paper should state which economic institution justifies the expectation convention.

---

# 6. A directly relevant Operations Research dynamic-contract policy-graph paper is missing

The service-contract positioning should include:

- Hao Zhang (2012), “Solving an Infinite Horizon Adverse Selection Model Through Finite Policy Graphs,” *Operations Research* 60(4):850–864, DOI 10.1287/opre.1120.1056.

Zhang studies a dynamic adverse-selection model with a Markov information process and uses finite policy graphs to represent continuation contracts and payoff frontiers. The model, information structure, and approximation algorithm are not the same as R30. But this is an *Operations Research* paper connecting dynamic contracts, Markov information, continuation values, and finite policy-graph representations. It is too close to the paper's conceptual framing to omit.

R30 currently cites dynamic contracting on one side and policy-graph decomposition on another side, but it does not connect them through the literature that already uses finite policy graphs for dynamic contracts.

The authors should explain clearly:

- why the present “public vertex + writable price symbol” machine is different from a contract policy graph;
- whether the exact finite-memory result can be interpreted as an exact policy-graph compression theorem for this public-information subclass;
- what is gained relative to approximate continuation-frontier policy graphs.

This comparison could materially strengthen the service interpretation.

---

# 7. The representation-size theorems need matching lower bounds or a stronger generalization

Theorem 3.1 proves:

- at most (3N) globally distinct response knots;
- (O(N^2+M)) scalar response storage.

The dense-knot experiment shows 197,369 stored segments at 511 vertices, which is useful evidence that quadratic storage can arise in practice. But an experiment is not a lower bound.

Once response-size complexity is a principal novelty, I expect the paper to answer whether these bounds are tight.

In fact, the likely constructions appear simple enough that this should be feasible:

- distinct local clipping thresholds can force (Omega(N)) distinct global knots;
- on a chain or appropriately nested DAG, ancestor response functions can inherit downstream knots, plausibly yielding (Omega(N^2)) total stored segments.

If those lower bounds are correct, they should be proved. If they are not, then the upper bound may be improvable, which is even more important.

The memory side already has the ingredients for a linear lower bound through the renewal family. The paper should make the tightness story explicit across all three representation quantities:

| Quantity | Current upper bound | Current lower-bound status |
|---|---:|---|
| Global knot universe | (O(N)) | no theorem stated matching it |
| Total response storage | (O(N^2+M)) | dense experiment, no matching theorem |
| Raw realized price labels | (O(N)) | lower-bound relationship not summarized |
| Minimal writable alphabet | (O(N)) | renewal family appears to give linear worst case |

A top-journal theory paper should not leave the core output-size bounds one-sided when matching examples seem within reach.

An alternative route would be to generalize the finite closure substantially beyond separable quadratics—for example to an explicitly representable class of piecewise-quadratic or piecewise-smooth local rewards with a complexity parameter. Either tightness or broader generality would improve the theorem-level significance.

---

# 8. The outside-option “dispersion” claim is broader in prose than in the theorem

Proposition 4.3 is mathematically clean, but its scope should be described more precisely.

The proposition fixes a centered, strictly ordered direction (d_j) and studies the one-parameter family
[
b_j(epsilon)=ar b+epsilon d_j.
]
It proves that the loss from an insufficient deterministic alphabet is strictly increasing in the scalar (epsilon) along this particular mean-preserving radial path.

That is **not** the same as proving monotonicity under arbitrary mean-preserving spreads, convex order, majorization, variance order, or every natural notion of “greater dispersion.”

Yet the abstract says that “greater outside-option dispersion at a fixed mean payment strictly increases the loss from insufficient memory,” which can easily be read as a general dispersion comparative static.

The authors should do one of two things:

1. weaken the prose everywhere to “along a fixed mean-preserving radial spread of continuation caps”; or
2. prove a genuine partial order result (for example, an appropriate majorization/convex-order monotonicity theorem).

The current one-parameter result is still useful, but it should not be advertised as a general theorem about dispersion.

---

# 9. The remaining exact theorem is narrow enough that top-journal significance is still uncertain

After the correct R30 concessions, the exact finite-price compiler requires:

- one scalar additive commitment;
- positive payment coefficients;
- separable strictly concave quadratic rewards;
- interval controls;
- exogenous acyclic public transitions;
- public-state-sufficient caps;
- no intertemporal switching cost;
- no coupled vector commitments.

This is a coherent and nontrivial subclass. But it is also a narrow one.

The previous versions could present the theorem as a broad new dynamic-contract solution method because the laminar connection was not yet explicit. R30 can no longer do that. The paper now correctly says the full-history optimization is classical laminar allocation and that normalized memoization gives the same recursion.

Therefore the top-journal case must come from sharper structural statements about the quotient representation, exact parametric output, and memory architecture.

At present I see a technically sound special-class theorem package, but not yet a decisive *Operations Research* contribution because:

- the residual novelty is not fully positioned against the relevant parametric/minimization literature;
- the output-size bounds lack matching lower bounds;
- the service-design comparative static is family-specific;
- the computational study is synthetic;
- the exact closure disappears with switching, coupled commitments, or more general local objectives.

This is why I recommend rejection rather than acceptance despite the strong revision.

---

# 10. The computational section is much better, but its baselines no longer target the most important novelty question

The new experiments are a major improvement.

Strengths include:

- exact agreement with an independently coded occurrence-indexed laminar reduction;
- a generic sparse convex solve on unfoldable instances;
- a public-graph primal promise-grid method;
- separate build/inversion/certificate/audit measurements;
- coefficient bit lengths;
- a 2,045-vertex long-horizon family;
- a separate dense-knot family that exposes response-table growth;
- explicit negative/censored evidence rather than only successful timings.

I do not object to these experiments as validation.

However, after R30 admits that a **normalized memoized tree reduction has the same recurrence**, the timing advantage over the deliberately nonmemoized occurrence-indexed baseline is not itself evidence of a new algorithmic principle. The paper says this honestly, but then the right benchmark question changes.

The most relevant computational comparison would now be against algorithms designed for:

- parametric piecewise-quadratic optimization;
- separable polymatroid/resource-allocation sensitivity;
- a compact representation of the same quotient where available.

I do not require original Mjelde/Tang software from decades ago. I do require the computational study to align with the theorem that is now claimed as new.

The SciPy `trust-constr` comparison is also a weak generic baseline. It is useful as a numerical cross-check, not as evidence of practical competitiveness against specialized convex/QP software. The manuscript mostly says this correctly; the editorial case should not lean heavily on those timing ratios.

The public promise-grid comparison is the most informative baseline in the current paper because it isolates the gain from exact continuous dual closure rather than from recombination alone.

---

# 11. Comments on the bit-complexity theorem

I regard Theorem 3.3 as a serious improvement and did not find an immediate contradiction in its path-denominator argument. Several aspects should nevertheless be strengthened for publication.

1. The proof should make explicit which intermediate quantities are reduced after rational arithmetic and which common denominators are conceptual only.
2. Sorting/comparison cost should be integrated explicitly into the Turing-model statement rather than hidden under the arithmetic count (A).
3. The distinction between response-coefficient height and aggregate certificate/value height, now discussed in the companion, should be cross-referenced directly from the theorem.
4. The theorem is specific to the coefficient-event construction. That specificity should remain in the statement; it is not a generic bit bound for all implementations of the quotient recursion.
5. If the authors retain a claim of polynomial preprocessing as a central contribution, they should compare this exact encoding result with the complexity guarantees in the omitted parametric-optimization literature discussed above.

These are requests for sharpening, not claims that the current proof is false.

---

# 12. Comments on the minimal-machine theorem

The theorem is plausible under the stipulated architecture, but its exposition should separate classical and new ingredients.

### Classical ingredient

Backward partition refinement by equality of current outputs and successor equivalence classes is a standard way to minimize a deterministic behavior machine.

### Model-specific ingredients

The new content appears to be:

- existence of a finite reached price machine despite continuous controls;
- at most (N+1) raw incoming-price labels for a fixed query;
- contiguity of behavioral classes in price order;
- exact coupling to the unique optimal contract;
- a linear worst-case contractual memory family;
- collapse of distinct prices when future behavior coincides.

These should be the theorem's foreground.

I would also like an explicit statement relating the class count (c_v) to a conventional minimal Moore/Mealy transducer after public vertices are treated as exogenous inputs. That would eliminate ambiguity over what exactly has been minimized.

---

# 13. Comments on the renewal frontier

The heterogeneous frontier is a useful extension.

The cell loss
[
C(i,j)=sum_{h=i}^j pi_h{f(b_h)-f(b_i)+h_h(b_h-b_i)}
]
and contiguous-cell dynamic program are convincing under the stated monotonicity assumptions.

Two caveats:

1. The segmentation recurrence is standard; the manuscript already acknowledges this. The contribution is the contract-specific cell cost and the proof that an optimal information partition can be ordered.
2. The frontier remains deterministic. The exact-optimum randomized lower bound in Theorem 4.1 does not imply that randomization is useless for every restricted alphabet size. The companion correctly says this. The main text and abstract should preserve that distinction carefully.

A stronger paper could ask whether randomized restricted-memory frontiers coincide with deterministic ones for this renewal family, or characterize when randomization strictly improves a finite alphabet. That is not required for correctness, but it would deepen the memory-design contribution.

---

# 14. Comments on the shared-table comparator

The R30 scope is now appropriately disciplined:

- zero release has a graph-sized convex formulation;
- a fixed positive-release query can be solved exactly by the compiler;
- the multipliers yield a supporting inequality;
- ties and singleton effective intervals are handled;
- no finite-cut guarantee for the continuous outer design problem is claimed.

I did not find a decisive flaw in the normal-cone splitting argument as written.

This material is supporting machinery rather than a main novelty, and the manuscript now treats it that way. I would keep it concise.

---

# 15. Presentation and claim calibration

The manuscript is much more focused than prior revisions, but several phrases should be tightened.

1. **Title:** “Minimal Price Memory” sounds absolute. The theorem is minimal *additional writable memory conditional on a free public vertex and read-only program*, for a fixed root query.
2. **Abstract dispersion claim:** qualify the one-parameter radial spread unless a stronger dispersion order is proved.
3. **“Polynomial rational bit complexity”:** specify that this is for the coefficient-event compiler on rational inputs.
4. **“Minimal alphabet”:** distinguish (K_*) from total combined public-state/memory states and from read-only storage.
5. **Computational superiority:** continue avoiding any claim that the un-memoized tree timing ratio establishes superiority over the equivalent normalized memoized reduction.
6. **Service interpretation:** the application should not be allowed to conceal how specialized the exact optimization subclass is.

The bibliography should add the parametric optimization, model/machine minimization, state aggregation, and dynamic-contract policy-graph references relevant to the new R30 framing.

---

# 16. What would make a resubmission substantially stronger

I would take a new submission seriously if it closes the following points.

## A. Complete the residual priority audit

Add, at minimum, a theorem-level comparison with:

- Klimm and Warode (2021), parametric piecewise-quadratic flow;
- Harks, Klimm, and Peis (2018), separable polymatroid sensitivity;
- classical/modern Moore or transducer minimization;
- Givan, Dean, and Greig (2003), model minimization/bisimulation;
- Bean, Birge, and Smith (1987), state aggregation in OR;
- Zhang (2012), finite policy graphs in dynamic contracts.

The paper need not claim these results subsume R30. It must explain precisely why they do not.

## B. Prove tightness, or generalize the exact closure

Give matching worst-case constructions for the (O(N)) knot universe and (O(N^2)) total response storage, if those bounds are tight. Make the linear memory lower bound explicit as part of the same theorem package.

Alternatively, extend the compiler beyond pure quadratics to a meaningful piecewise-quadratic/structured concave class with complexity stated in terms of local breakpoints.

## C. Recast the memory theorem in standard minimization language

Treat the reached price graph as a deterministic output machine with public-transition input. Cite the standard minimization principle, then isolate the genuinely new price-order and contractual results.

## D. Report memory in more than one accounting convention

At minimum report:

- extra writable symbols/bits;
- combined reached ((v,	ext{class})) states;
- read-only response representation and coefficient precision.

This will prevent readers from interpreting (K_*) as total controller complexity.

## E. Calibrate or strengthen the economic comparative static

Either prove a genuine dispersion-order result or state the current radial result narrowly. A deeper majorization/mean-preserving-spread theorem would materially improve the service-design contribution.

## F. Align computational baselines with the residual novelty

The main empirical question is no longer whether unfolding is expensive. It is whether the complete exact parametric representation is useful relative to other parametric/sensitivity approaches on the same structured class.

---

# 17. Recommendation to the editor

R30 is not a failed revision. It fixes a remarkable number of the previous report's substantive objections and contains a coherent theorem package. I found no obvious mathematical counterexample, and the reproducibility work is stronger than what is typical in this area.

My rejection recommendation rests on a narrower but important point: **the paper's own R30 corrections have changed what must be novel, and the literature/complexity case has not yet caught up with that change.**

After conceding the classical laminar reduction and normalized memoization equivalence, the paper must establish priority for its complete parametric response representation. After replacing numerical price counting by backward behavioral equivalence, it must distinguish its contract-specific result from standard deterministic machine/model minimization. And if output-size complexity is a central result, the natural worst-case tightness questions should be answered rather than left to experiments.

The current manuscript is therefore scientifically credible but not yet sufficiently positioned or sharpened for *Operations Research*.

**Decision recommendation: Reject; encourage a substantially reframed resubmission centered on (i) the exact residual novelty relative to parametric optimization and machine minimization, (ii) tight representation/memory complexity, and (iii) a precisely scoped contractual-memory implication.**
