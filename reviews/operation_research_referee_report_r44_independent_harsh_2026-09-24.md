# Confidential Referee Report for Operations Research

**Manuscript:** *Limited-Memory Renewal Contracts: Exact Quadratic Design and Resource Augmentation*  
**Revision reviewed:** `revision/ndu-operations-research-r44-resource-augmentation-20260924`  
**Revision tip reviewed:** `fe066aac2862fc89fc8eb2e19fd98b4b96e6d5a3`  
**Immediate predecessor:** `revision/ndu-operations-research-r43-prefix-decomposition-20260924`, tip `55313f79ad7d6b09c2edf1ceeafe254898a2bcbe`  
**Predecessor independent report:** `reviews/operation_research_referee_report_r42_independent_harsh_2026-09-24.md`  
**Review branch:** `review/operation-research-r44-independent-harsh-20260924`  
**Date:** September 24, 2026  
**Recommendation:** **Reject in the present form. R44 is a technically serious revision and the new two-price union construction appears sound under the stated assumptions, but the headline polynomial result is a bicriteria resource-augmentation theorem that permits up to twice the original memory rather than an algorithm for the original limited-memory problem. The charged version can be quantitatively vacuous, the factor-two tradeoff is neither characterized nor shown necessary, the continuous comparison is numerically very loose, and the computational study is predominantly internal certificate validation rather than evidence of algorithmic or operational impact at the standard of Operations Research.**

---

## Executive assessment

R44 is materially stronger than R42 and R43. The authors have corrected the active-face inequality count identified in the preceding report. They have also added a genuine new theorem rather than merely expanding the exposition: two priced catalog solutions whose aggregate targets bracket the promise are combined into one fixed union alphabet; branch targets are mixed; the canonical response on the union book is then used to preserve the root promise, the pre-draw intermediate-service rule, and every realization ceiling. For zero opening charges, the resulting alphabet has at most twice the original number of levels and is within a prescribed additive tolerance of the original-budget catalog optimum. The revision supplements this construction with a positive price-gap example, exact-rational certificates, mutation tests, and scaling runs reaching 256 branches and 65 catalog levels.

These are real advances. The new theorem directly addresses one of the principal requests in the R42 report: it converts the polynomial price oracle into a polynomial constructive guarantee with variable branch count and alphabet budget. The theorem also avoids an invalid strong-duality claim. The strict-gap example correctly demonstrates why arbitrarily accurate price minimization alone need not recover the original-budget optimum.

I performed a source-level audit of the theorem statement, proof, companion derivation, implementation, checker, archived tables, and the R43 price decomposition on which R44 relies. I do not see an immediate counterexample to the endpoint bracket, monotonicity of supported totals, target interpolation, union-book dominance, concavity step, exact feasibility reconstruction, price-error identity, or charge-excess identity. The central R44 result therefore appears mathematically credible. My recommendation is not based on a fabricated correctness objection.

The problem is significance and problem fidelity. The manuscript is motivated throughout by a hard limit of at most \(m\) execution symbols. Its scalable theorem solves a different problem with as many as \(2m\) symbols. That is a legitimate bicriteria result, but it does not resolve the original-budget optimization problem, whose exact methods remain exponential. Moreover, the strongest clean guarantee requires zero charges, precisely the regime in which extra symbols are treated as free. With charges, the theorem subtracts an uncontrolled instance-dependent term Ω that may dominate the entire objective scale. The reported charged experiments illustrate this weakness rather than overcoming it.

The paper consequently sits in an uncomfortable position. As an application paper, it has no calibrated operational setting establishing that doubling memory is acceptable or that symbol charges are negligible. As an optimization paper, its main new polynomial theorem is essentially one-dimensional Lagrangian convexification plus a model-specific union-feasibility lemma, with no tightness, hardness, lower bound, general memory-value frontier, or competitive computational comparison. I do not believe this combination clears the publication bar of *Operations Research* in its current 39-nonreference-page main-paper form.

---

# 1. Version audit and what R44 genuinely fixes

The audited revision is seven commits ahead of R43 and preserves the previous manuscript pipeline. The build record reports 41 main-paper pages, 39 nonreference pages, a 38-page electronic companion, a five-page response, no unresolved references, and no overfull boxes. The source package is unusually careful about preservation, exact arithmetic, and reader provenance.

R44 makes the following substantive changes.

1. **The R42 complexity-count error is fixed.** The exact continuous theorem now counts four potentially distinct inequalities for a lottery branch: two chord bounds, the target cap, and the realization-eligibility ceiling. The safe bound is \(s+1+4k\), and the manuscript no longer understates the active-set enumeration exponent.

2. **The price oracle is turned into a feasible recovery procedure.** R43 established a polynomial path dynamic program for each Lagrangian price. R44 uses two supported solutions to construct a fixed union book with exact aggregate promise and exact branchwise risk feasibility.

3. **The paper no longer relies on an implicit zero duality gap.** It explicitly provides an instance with original-budget optimum \(45/64\), minimum price bound \(453/640\), and gap \(3/640\).

4. **The memory and charge accounting is explicit.** The union contains at most \(2m\) levels, and the extra opening cost is reported as the exact quantity
   
   Ω = R(c^- \cup c^+) - θR(c^-) - (1-θ)R(c^+).

5. **The implementation evidence is stronger.** The revision stores exact endpoint policies, targets, lotteries, prices, upper bounds, a union policy, an original-budget policy, price error, and charge excess. A separate checker replays these quantities and rejects fourteen declared semantic corruptions.

These are not cosmetic edits. In particular, the resource-augmentation theorem is a meaningful response to the prior report's request for a result beyond raw stationary-face enumeration.

Nevertheless, the revision does not establish a scalable algorithm for the original \(m\)-symbol problem. It establishes a scalable algorithm for a relaxed problem in which the resource cap may double. Whether that is enough is the central editorial issue.

---

# 2. Technical audit of the two-price recovery theorem

## 2.1 Endpoint prices and monotonicity

The endpoint construction is plausible and, under the declared Lipschitz assumptions, correct. At the negative endpoint, the price-adjusted branch response is strictly increasing, so every branch selects its cap and the total target is ̅b. At the positive endpoint, the price-adjusted response is strictly decreasing, so every branch selects the first book level and the total is at most \(B\).

For completeness, the paper should state the standard monotonicity argument explicitly. If \(x_1\) and \(x_2\) are arbitrary optimizers at prices λ1 < λ2, optimality at the two prices implies

\((λ_2-λ_1)(S_1-S_2) \ge 0\),

so every selected supported total at the lower price is at least every selected supported total at the higher price. This is the clean reason that arbitrary tie-breaking does not break the bracket. The companion currently asserts that ties do not obstruct the rule, but the two-line inequality would make the proof self-contained.

## 2.2 Target mixing and union feasibility

The most model-specific part of R44 is sound-looking. Each endpoint book is a subset of the installed union. Therefore, at each endpoint target, the union response weakly dominates the old response. The fixed-book response is concave in the target, so the response at the mixed target dominates the mixture of endpoint responses. The canonical union rule then reconstructs a pre-draw intermediate tier and an adjacent eligible lottery.

This avoids three invalid shortcuts:

- randomizing the installed book;
- using a draw-dependent intermediate tier;
- or averaging terminal levels that need not belong to the catalog.

The exact promise is preserved because branch targets are mixed with a common scalar θ. The realization ceiling is preserved because the canonical response uses the highest eligible union level and puts any residual target into the fixed intermediate tier. I do not see a hidden feasibility relaxation here.

## 2.3 Price error and charge accounting

The identity

\(θD(λ_-) + (1-θ)D(λ_+) = θJ_- + (1-θ)J_+ + e\)

with

\(e=(λ_+-λ_-)(S_--B)(B-S_+)/(S_--S_+)\)

is correct. Since \(U\) is the smaller endpoint price bound, the mixed endpoint payoff is at least \(U-e\). The elementary \(xy/(x+y) \le (x+y)/4\) bound gives the stated stopping criterion.

The charge identity is also correct:

\(Ω=(1-θ)R(c^-\setminus c^+) + θR(c^+\setminus c^-)\).

This is useful accounting. It is important, however, not to confuse correct accounting with a useful approximation guarantee. That distinction becomes decisive in the charged case, discussed below.

## 2.4 Strict price-gap example

The example serves its logical purpose. The original two-symbol optimum is \(45/64\), the minimum price bound is \(453/640\), and the difference is \(3/640\). The three-level union book attains the price value. Thus the example refutes any claim that smaller price tolerance alone must close the original-budget gap.

The example does **not** show that a factor-two alphabet increase is necessary. It uses three rather than four levels, and the gain over the two-level optimum is only \(3/640\), which is exactly \(1/150\), or about 0.67%, of \(45/64\). The manuscript correctly disclaims a factor-two lower bound. That disclaimer also highlights how much theory remains missing before the resource tradeoff is well understood.

---

# 3. Principal blocker: the scalable theorem changes the optimization problem

The manuscript is framed as a theory of limited execution memory. The original feasible set permits at most \(m\) installed levels. The central polynomial theorem permits up to \(2m\) levels. It compares the value of this enlarged feasible set with the optimum of the original feasible set.

That is a **bicriteria approximation theorem**, not an approximation algorithm for the stated original problem.

Bicriteria results can be important. Here, however, the paper does not provide the theory needed to make the resource relaxation compelling.

- There is no lower bound showing that \(2m\), \(2m-1\), or even \(m+1\) symbols are ever necessary for the claimed accuracy.
- There is no family showing a price gap that requires an alphabet close to the union size.
- There is no guarantee for a continuum of budgets such as \(m+r\) or \((1+\alpha)m\).
- There is no union-compression theorem.
- There is no approximation guarantee after merging or deleting redundant union levels.
- There is no characterization of when the two supported books are nested, nearly nested, or disjoint.
- There is no memory-value frontier quantifying how much objective improvement is purchased by each additional level.

The factor two is inherited from taking the union of two \(m\)-level designs. With one scalar coupling constraint, two supported designs are the classical convexification object. Thus the factor-two bound is structurally natural, but also generic. The paper needs either a tightness theorem or a stronger model-specific improvement to establish that this is more than the direct union consequence of one-dimensional Lagrangian recovery.

The experiments make the theoretical gap more visible. In the twelve scaling runs, the reported union sizes are often \(m\) or \(m+1\), and never approach \(2m\). For example, the zero-charge runs with \(m=8\) use 9 or 11 levels, not 16. This is encouraging computationally, but it means the paper currently has neither a worst-case necessity result nor a structural explanation of the much smaller observed expansion.

Most importantly, the original-budget problem remains where it was in R43:

- exact unrestricted continuous optimization is an exponential stationary-face reference algorithm;
- exact catalog optimization is a finite but worst-case exponential prefix search;
- the polynomial path dynamic program solves only the priced relaxation.

R44 therefore sidesteps, rather than resolves, the main algorithmic difficulty at the original memory budget. The paper should be evaluated on the merits of a resource-augmentation result, not as though it now supplies a polynomial solution to limited-memory design itself.

---

# 4. Novelty relative to classical Lagrangian convexification remains too thin

The manuscript is commendably candid that Lagrangian convexification, supporting solutions, and two-point recovery are classical. The new ingredient is the claim that, for this ordered-interface class, the aggregate target mixture can be implemented by one fixed union alphabet while preserving contractual timing and risk constraints.

I agree that this implementation lemma is nontrivial and model-specific. I am not convinced that it is sufficient to anchor a flagship optimization paper of this length.

Abstractly, the R44 construction has the following form:

1. solve a one-parameter Lagrangian relaxation at two prices;
2. use the scalar coupling constraint to mix two resource usages;
3. take the union of the two designs;
4. invoke monotonicity and concavity to implement the mixed resource vector;
5. pay the union cost.

The first two steps are classical. The fourth step is the main theorem-specific insight. The third and fifth steps yield the factor-two resource and Ω penalties almost mechanically.

For *Operations Research*, I would expect the manuscript to push beyond this template in at least one direction:

- prove that the factor two is tight for the abstract class;
- exploit ordering to improve \(2m\) to \(m+O(1)\) under meaningful assumptions;
- derive an optimal compression or pruning procedure;
- characterize exact strong-duality regimes;
- prove a hardness result that explains why same-budget recovery is impossible;
- extend the theorem to multiple coupling constraints and identify the precise Carathéodory/resource tradeoff;
- or demonstrate the same feasibility mechanism in a second genuinely different OR model.

The present “ordered-interface allocation class” remains very close to the renewal formulation: a scalar ordered catalog, a common increasing concave reward, separable convex shortfall costs, branch caps, and eligibility thresholds. It is an abstraction of the same mathematics, not yet evidence of broad reuse.

The novelty table itself reinforces this concern. Most rows are “classical optimization mechanism plus contract-specific feasible cost or geometry.” That can be publishable when the operational model is independently important. Here the operational setting remains stipulated and uncalibrated, so the methodological increment must carry nearly the entire publication case.

---

# 5. The charged guarantee is exact bookkeeping but can be vacuous as an approximation result

The zero-charge theorem has a clean statement:

\(J_U \ge \mathcal V_{m,\mathcal A}^δ(B;0)-ε\)

with at most \(2m\) levels.

For nonnegative charges, the guarantee becomes

\(J_U \ge \mathcal V_{m,\mathcal A}^δ(B;ρ)-ε-Ω\),

where Ω may be as large as \(mρ_{\max}\). There is no relation between \(mρ_{\max}\) and the scale of the optimal net value. Consequently, this bound may be negative, may be worse than a trivial feasible policy, and may provide no approximation information at all.

This is not a technicality. Opening charges are introduced precisely to model the cost of additional levels. The strongest resource-augmentation theorem is clean only when those additional levels are free. Once the operational cost of extra memory is activated, the theorem says, in effect, “the convexified operating value can be recovered after paying whatever the union costs.” That is a correct identity, but not a nontrivial performance theorem without additional structure on the charges or overlap.

The reported scaling table demonstrates the issue. In the two affine-charge cases,

- \(m=4\) and the recovered union also has only four levels;
- \(J_U-U_m\) is approximately \(-0.00422\) and \(-0.01354\);
- Ω is approximately \(0.00445\) and \(0.01376\).

The companion table shows that the recovered union values, 0.70772 and 0.66893, are materially below the separately feasible original-budget lower policies, 0.71144 and 0.68144. Thus even when the union happens to satisfy the original memory limit, the charged recovery policy is not the sensible policy returned by the overall computation. The theorem remains true only because Ω absorbs the loss.

A stronger charged result would need at least one of the following:

- a charge-aware choice among multiple supported optimizers to maximize overlap;
- a bound on Ω in terms of the optimum or the marginal value of memory;
- a monotone or convex charge condition yielding nested books;
- a pruning or merging algorithm with a controlled loss;
- or a guarantee for the better of the union policy and the separately feasible original-budget policy.

Simply reporting Ω is transparent, but transparency does not make an uncontrolled penalty algorithmically meaningful.

---

# 6. The continuous-design corollary is formally valid but algorithmically and numerically weak

The continuous comparison combines two ingredients:

1. a one-sided mesh transport from the continuous \(m\)-level optimum to a catalog optimum;
2. the \(2m\)-level two-price recovery on that catalog.

For zero charges, this gives an additive η guarantee with a mesh denominator of order \(K_0/η\). The paper correctly states that the resulting running time is polynomial in the **numerical quantity** \(K_0/η\), not polynomial in the binary encoding length of η. It also correctly disclaims a same-budget FPTAS.

Those qualifications are necessary because this is a pseudo-polynomial accuracy dependence, not a strong complexity result. More importantly, the archived numbers show that the uniform mesh certificate is far too loose to be operationally informative at the tested resolutions.

The reported mesh terms include approximately

- 0.36616,
- 0.17251,
- 0.17762,
- 0.08831,
- and 0.04416,

while objective values are mostly between 0.16 and 0.72. In the price-accuracy path, the price error falls from roughly \(5.96\times 10^{-3}\) to \(2.09\times 10^{-10}\), but the mesh term remains 0.17251. Thus the continuous comparison is dominated by discretization even after the price calculation is essentially exact.

The fixed-input lower bound establishing linear order in \(h\) does not address this issue. Order-sharpness says nothing about the practical constant or whether an adaptive grid can be much better on the instances of interest.

To make the continuous result persuasive, the paper should provide:

- adaptive or nonuniform mesh selection;
- instance-dependent local Lipschitz bounds;
- a posteriori rather than purely worst-case discretization certificates;
- direct comparison against exact continuous optima on tractable instances;
- and evidence that the certified interval becomes useful at realistic catalog sizes.

At present the continuous corollary is mathematically correct but not a convincing algorithmic contribution.

---

# 7. The computational section validates identities; it does not establish performance or impact

The revision's software engineering is strong. Exact fractions, archived certificates, mutation tests, and explicit separation between original-budget and augmented values are all commendable. But the scientific question is not merely whether the implementation obeys the theorem. It is whether the method is useful, competitive, and structurally informative.

The current study does not answer that question.

## 7.1 Exhaustive tests are tiny and share substantial code structure

The 144 exhaustive comparisons use at most six branches, at most three installed levels, and catalogs with only five to eight points. They use one fixed random seed. These are appropriate regression tests, not an empirical evaluation.

The exhaustive solver, recovery implementation, and checker all share the same model primitives and canonical response formulas. This is acceptable for testing, but it is not the same as an independently formulated global optimization benchmark.

## 7.2 The scaling family is extremely narrow

The twelve declared scaling cases use:

- linearly spaced caps from 0.2 to 0.8;
- periodic deterministic weights;
- periodic deterministic shortfall curvatures;
- a fixed promise equal to \(0.8\bar b\);
- uniform catalogs;
- only two main risk tolerances;
- and, in the main scaling path, mostly zero charges.

Each timing is one instrumented run. There are no repeated samples, no uncertainty summaries, and no varied instance distributions. The largest cases demonstrate that the \(O((k+m)N^2)\) price dynamic program runs, which is already predicted by the theorem. They do not establish the quality of the recovered design.

## 7.3 There are no meaningful algorithmic baselines

The study does not compare against:

- direct optimization with \(m+1,…,2m\) levels;
- the best \(2m\)-level catalog policy;
- a merge-down or prune-down heuristic applied to the union;
- a mixed-integer or disjunctive formulation of the new recovery problem;
- generic global optimization on small instances;
- subgradient, bundle, or cutting-plane minimization of the price bound;
- alternative quantizer-design heuristics;
- or a simple policy that spends added memory greedily.

Without these comparisons, one cannot tell whether the two-price union is close to the best policy available at its enlarged budget, whether a much smaller expansion would suffice, or whether a trivial heuristic performs just as well.

## 7.4 The main table does not show a compelling gain

For zero-charge cases, \(J_U-U_m\) is often tiny and may be negative because the price-error allowance permits it. The table does not report the exact original optimum on the scaling family, the improvement over the best feasible original policy \(L_m\), or the gap to the best policy at the union's actual size. Consequently, it is impossible to judge the economic value of augmentation.

The strict-gap example gives a clean proof of concept, but its gain is about 0.67% of the original optimum and uses one additional level. This is useful logically, not persuasive computational evidence of a major operational benefit.

## 7.5 The resource bound itself is not studied

The paper should report at least:

- |\(c^U\)|\(-m\) and the percentage memory expansion;
- overlap between endpoint books;
- frequency of nested endpoint books;
- objective gain per extra level;
- performance after greedily deleting union levels;
- and instances deliberately constructed to maximize union size.

The current study records union size but does not build a theory or empirical narrative around it.

---

# 8. The checker is implementation-independent, not mathematically independent

The paper repeatedly emphasizes an independent checker. The distinction should be stated more carefully.

`check_augmentation.py` does not import the R44 recovery routine, fixed-book allocator, or continuous cell solver. That is good. It directly verifies policy support, probabilities, targets, intermediate tiers, realization limits, root promise, charges, values, the mixing identity, price error, and Ω.

However, for global price optimality it imports the R43 `BoundCheck` implementation and recomputes the same eligibility-prefix price dynamic program. This is a separate implementation path, but it is not a second mathematical formulation. It cannot detect a shared modeling error in the price decomposition itself.

The inherited SCIP comparisons are explicitly not newly executed R44 experiments and do not independently optimize the new union-recovery construction. Therefore the revision still lacks the type of independent validation requested in the prior report: for example, an MIQP/disjunctive model or a direct exhaustive \(2m\)-budget formulation on random small instances.

The correct description is “independent certificate replay and separate implementation of the same price bound,” not “independent global optimization verification.” The current package is excellent for reproducibility, but reproducibility and model validation are different claims.

---

# 9. Exact-oracle and exact-arithmetic assumptions need a robustness theory

The general theorem assumes an exact scalar shortfall oracle. The rational-quadratic implementation uses exact rational arithmetic and exact comparison of supported solutions. This is valuable for proof-of-concept verification, but it leaves a large gap between the theorem and practical optimization.

Real applications would use estimated parameters, floating-point arithmetic, and approximate oracle solutions. The paper does not analyze:

- approximate price bounds;
- approximate branch maximizers;
- target-bracket errors;
- feasibility repair when the mixed promise is not exact;
- risk repair under floating-point lotteries;
- error accumulation in Ω;
- or stability of the selected endpoint books under ties and perturbations.

This matters particularly because the union can change discontinuously when one supported book changes. A tiny data perturbation may add or remove several installed levels even if the value changes little.

A practically meaningful version of the theorem should permit ζ-optimal price oracles and derive a final value and feasibility guarantee in terms of ζ, price tolerance, and numerical repair. Without this, the polynomial theorem is tied to an exact computational model that is strongest precisely in the synthetic rational setting.

---

# 10. The operational motivation still does not support the resource relaxation

The manuscript is transparent that the renewal setting is stipulated, not calibrated. It does not claim customer data or a field deployment. That honesty is preferable to invented evidence.

It also means the operational narrative cannot justify the central bicriteria relaxation.

The paper does not establish:

- what an execution symbol physically represents;
- why the original limit is \(m\);
- whether doubling the interface is feasible;
- what latency, validation, safety, or governance cost an extra symbol creates;
- how the opening-charge function would be estimated;
- or why zero charge is a relevant regime.

The strongest theorem says that extra symbols solve the price-gap obstruction when symbols are free. But the motivation for studying a limited alphabet is that symbols are scarce. This tension must be confronted directly.

A credible applied version would quantify the memory-performance frontier for an actual restricted interface. A credible pure-theory version would de-emphasize the renewal story and deliver a stronger general theorem. R44 currently does neither.

---

# 11. Contribution relative to length is unfavorable

The main paper has 39 nonreference pages and the electronic companion has 38 pages. The manuscript now contains, among other things:

- saturated deterministic structure;
- expected-versus-pathwise institutional comparisons;
- continuous top-level optimization;
- Monge acceleration;
- robustness and phase diagrams;
- charged catalog recurrences;
- exact rational-quadratic continuous design;
- feasible mesh transport;
- prefix decomposition and anytime search;
- a nonmonotone-charge separation example;
- monotone-charge collapse;
- and the new resource-augmentation theorem.

This is too diffuse. Several results are technically competent, but the paper reads as the cumulative archive of many revision cycles rather than a sharply organized journal article with one dominant contribution.

The new theorem does not cure this problem. It adds another conceptual layer while leaving the old layers in place. A reader must traverse a large amount of saturated, nonsaturated, continuous, catalog, deterministic, randomized, charged, uncharged, exact, approximate, and augmented material before understanding the principal message.

For *Operations Research*, contribution relative to length matters. The paper should either be split or radically refocused. The current “Lengthy manuscript” label does not itself justify the breadth.

---

# 12. Claims that should be narrowed further

The authors are more careful than in earlier revisions, but several phrases remain liable to overreading.

1. **“Polynomial recovery” should always be paired with “at up to twice the memory budget.”** The unqualified phrase can be mistaken for polynomial optimization of the original problem.

2. **“Continuous-design comparison” should state the pseudo-polynomial \(1/η\) dependence and the \(2m\) memory budget at first mention.**

3. **“Independent checker” should be qualified as separate implementation and certificate replay of the same price decomposition.**

4. **“Charged-level guarantee” should not be presented as an approximation result unless Ω is controlled relative to the value scale.**

5. **“The method applies to a broader ordered-interface allocation class” should be supported by a second non-renewal example or reduced to a statement of mathematical abstraction.**

6. **The title's “Exact Quadratic Design and Resource Augmentation” is accurate only after careful parsing.** Exact continuous design is exponential and quadratic; polynomial recovery is finite-catalog and bicriteria. The abstract should make this division unmistakable in its opening claims, not only in later qualifications.

---

# 13. What would be required for a credible new submission

I do not recommend another incremental revision that merely adds experiments or prose. A credible new submission would need a substantial re-conception.

## 13.1 Decide whether the paper is about the original budget or bicriteria augmentation

If the original \(m\)-symbol problem remains central, provide a meaningful same-budget result: hardness, fixed-parameter tractability, a stronger polynomial subclass, a principled approximation algorithm, or a decomposition method with provable performance.

If resource augmentation is central, make that the paper's explicit problem and develop the memory-value tradeoff rather than treating \(2m\) as a byproduct of unioning two books.

## 13.2 Prove a tight or near-tight resource theorem

At least one of the following is needed:

- an instance family requiring close to \(2m\) levels;
- an \(m+O(1)\) theorem under meaningful conditions;
- a parameterized guarantee for \(m+r\);
- a union-compression theorem;
- or a lower bound showing why a better universal resource factor is impossible.

## 13.3 Make the charged case nonvacuous

Develop a charge-aware recovery rule or structural conditions under which Ω is bounded. Reporting an arbitrary exact penalty is not enough.

## 13.4 Add genuinely independent optimization validation

Formulate the finite problem independently as an exact mixed-integer, disjunctive, or exhaustive \(2m\)-budget model and compare it with the two-price recovery on random small instances. The study should report both value quality and resource usage.

## 13.5 Evaluate against serious baselines

Compare with direct enlarged-budget optimization, union pruning, greedy level addition, merge-down heuristics, and generic solvers. Report distributions across many instances, not one deterministic scaling family.

## 13.6 Provide an inexact-oracle theorem

Allow approximate price optimization and floating arithmetic, with explicit value and feasibility repair guarantees.

## 13.7 Either calibrate the operational setting or remove most of it

A real restricted-interface application with defensible parameters could make a model-specific theorem valuable. Without such an application, the paper should be shorter and more abstract, and the optimization theory must be substantially stronger.

## 13.8 Reduce the manuscript aggressively

Select one primary contribution. Move historical development and secondary institutional results out of the main article, or split them into separate papers. The current package is too broad for the incremental value of R44.

---

# 14. Minor and presentation comments

1. Add the two-price optimizer monotonicity inequality to the proof; do not leave the tie argument at the level of assertion.

2. State explicitly that \(U\) is the minimum of two valid endpoint bounds, not necessarily the minimized Lagrangian dual value.

3. Report the relative strict-gap magnitude \(1/150\), not only the exact fraction \(3/640\), so readers can judge scale.

4. Add |\(c^U\)|\(-m\), percentage memory expansion, endpoint-book overlap, and gain over \(L_m\) to the main table.

5. In charged cases, report the better of the recovered union and the separately feasible original-budget policy as the operational recommendation, while keeping the theorem-specific union value separate.

6. Report the best value found at the union's actual size on the small exhaustive cases. This would reveal how much is lost by the two-price construction relative to direct use of the same memory.

7. The main table should not rely on \(J_U-U_m\) alone. Because \(U_m\) is an upper bound for a different feasible set, this difference is not an optimality gap for the union policy.

8. The reported maximum bit length covers stored dynamic-programming values, not all exact-arithmetic intermediates. This limitation is acknowledged in the companion and should be kept near any complexity-performance claim.

9. Peak `tracemalloc` allocation is not resident memory and the sub-megabyte numbers are not informative about full process consumption. The paper already disclaims this; the main text should not imply otherwise.

10. The abstract remains too dense. It attempts to mention nearly every historical and new result, which obscures the actual R44 contribution.

11. The phrase “one fixed expanded alphabet that preserves every promise” is potentially ambiguous: the construction preserves the aggregate root promise and each mixed branch target it creates, not the two endpoint target vectors simultaneously.

12. The positive price-gap example should be labeled as a relaxation-gap example, not as evidence that the factor-two resource bound is necessary.

13. The zero-charge assumption deserves more prominence in the headline theorem discussion because it is what turns the Ω-accounting identity into a genuine approximation guarantee.

14. The paper should distinguish a catalog-size parameter \(N\) from the physical memory budget \(m\) consistently whenever claiming polynomial complexity.

15. The response document is clear and unusually complete, but several response claims about “independent global verification” are stronger than what the checker architecture supports.

---

# 15. Recommendation

**Reject in the present form.**

R44 deserves credit for technical seriousness. The authors corrected the identified theorem count, built a polynomial price oracle into a feasible union construction, preserved exact contractual constraints, exposed rather than concealed the price gap, and produced a high-quality exact-rational audit trail. I find the new recovery theorem plausible and useful as a lemma about this model class.

But the revision still does not cross the *Operations Research* publication threshold.

The scalable theorem buys performance by relaxing the defining memory constraint from \(m\) to as many as \(2m\). The clean guarantee assumes that the added levels are free. The charged extension can lose an uncontrolled Ω and is demonstrably inferior to a separately feasible original-budget policy in the reported charged runs. The factor two has no tightness theory, the continuous certificate is numerically loose, the experiments do not compare against meaningful alternatives, and the operational setting does not establish why doubling the interface is acceptable.

Thus the paper's central advance is best described as a correct bicriteria recovery construction whose present theoretical depth, empirical evidence, and operational grounding are insufficient for a flagship OR journal. A successful future paper would need either a substantially stronger same-budget optimization result or a focused and tight theory of resource augmentation, together with independent comparative computation and a much shorter presentation.