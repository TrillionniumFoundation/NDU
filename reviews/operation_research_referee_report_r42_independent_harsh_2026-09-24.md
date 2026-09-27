# Confidential Referee Report for Operations Research

**Manuscript:** *Limited-Memory Renewal Contracts: Participation, Quantization, and Exact Design*  
**Revision reviewed:** revision/ndu-operations-research-r42-certified-joint-design-20260924  
**Published revision tip:** 0ddec75b39724266005f90aa9998407807df5259  
**Validated scientific source:** 7805e725ae08da2e6440fa01256efa2f935a30ec  
**Review baseline recorded by the revision:** 6e48c4858a54317f8189664f5a57fb5cc4ac6e4f  
**Predecessor independent report:** reviews/operation_research_referee_report_r39_independent_harsh_2026-09-24.md  
**Review branch:** review/operation-research-r42-independent-harsh-20260924  
**Date:** September 24, 2026  
**Recommendation:** **Reject in the present form. R42 closes the principal mathematical incompleteness identified in R39, but the new global result is still an exponential enumeration theorem rather than a sufficiently strong optimization advance, the computational and operational evidence remain too thin for Operations Research, and the stated face-enumeration complexity bound is incorrect as written.**

---

## Executive assessment

R42 is a serious revision and is materially stronger than R39. The authors did not merely relabel the fixed-book allocation problem as a global solution. They introduced a unified model with endogenous branch promises, a realization ceiling, and charges on the actual selected terminal levels; they reduced each fixed-book branch to an eligibility prefix and a canonical adjacent lottery; they eliminated lottery probabilities to obtain finitely many quadratic cells; and they supplied an exhaustive stationary-face procedure that, for rational quadratic data, attains the global continuous optimum. They also added a one-sided rounding theorem that preserves every branch target and every risk ceiling exactly and gives a uniform additive catalog bound.

Those additions directly address the two largest conceptual deficiencies in the prior report: the continuous outer design problem is now solved in principle at every promise, and the finite-catalog extension is now quantitatively connected to unrestricted continuous design.

I do not see an immediate counterexample to the central eligibility-prefix theorem, the closed-cell representation, the stationary-face existence lemma, or the downward-rounding/probability-repair argument. The current recommendation is therefore not a blanket correctness rejection.

However, the paper still falls short of the standard I would apply at *Operations Research*, particularly in the Optimization area. The journal's current editorial statement emphasizes innovative and impactful research and the Optimization-area statement asks a paper to excel in at least one of modeling, theory, algorithms, computation, or applications, with relevance to a broad audience and attention to contribution relative to length. R42 is now mathematically coherent, but its new general algorithmic contribution is essentially exactness by exhaustive disjunctive enumeration. Its computational evidence is intentionally limited to very small global continuous instances. Its operational story remains a carefully stipulated synthetic architecture rather than a calibrated or implemented decision problem. In that setting, the theory and algorithms must carry almost the entire publication case. I do not think the new general result is yet strong enough to do so.

There is also one concrete theorem-level error that must be fixed: the number of inequalities per lottery cell is undercounted in Theorem “Exact joint continuous design,” so the displayed exponential bound understates the worst-case active-set enumeration by a factor exponential in the number of branches.

My recommendation is therefore **Reject in the present form**, while recognizing that R42 is a substantial mathematical improvement over R39.

---

# 1. Version audit: what R42 genuinely fixes

The revision reports a 35-page main paper, 33 nonreference pages, a 24-page electronic companion, a 177-word abstract, no undefined references, no overfull boxes, a clean source tree, and preservation of the inherited revision history. The source package includes exact-rational implementations of the new fixed-book allocation, continuous face search, catalog enumeration, mesh certificate, and regression tests.

The substantive improvements over R39 are real:

1. **The formerly open continuous outer problem is now addressed.** For rational quadratic primitives, the paper enumerates branch modes and book sizes and optimizes the resulting quadratic objective over each compact polytope.

2. **Promise, risk, and selected-level charges are placed in one model.** This is a meaningful unification relative to the previous separation between nonsaturated allocation and saturated finite catalogs.

3. **The catalog is no longer presented as an unexplained surrogate for continuous design.** The mesh theorem supplies a uniform additive comparison to the continuous optimum while preserving the exact promise and risk constraints.

4. **The priority discussion is better.** The paper now directly acknowledges optimized one-dimensional dual-grid work, classical fixed-opening-cost ideas, rational quadratic optimization, Monge dynamic programming, stochastic rounding, and communication-constrained control.

5. **The computational claims are more disciplined.** The text explicitly says that the continuous global solver is exponential and intended as a small-instance reference algorithm.

These are not cosmetic changes. The R39 objection that the paper contained three only partially connected exact problems is substantially resolved at the level of mathematical formulation.

---

# 2. Mathematical audit of the new unified model

## 2.1 Eligibility-prefix reduction

For a fixed ordered book, the branch-specific risk ceiling removes all codewords above $b_j+delta$. Given a branch target $t$, increasing the terminal mean improves terminal reward and weakly reduces the intermediate-service cost. Hence the optimum pushes the terminal mean to $min{t,d_j}$, where $d_j$ is the largest eligible codeword, and uses the adjacent lottery in the eligible prefix when the target lies below $d_j$.

I find this reduction correct under the manuscript's stated assumptions. The endpoint identifications are also credible: $delta=0$ reproduces the pathwise institution after the Jensen reduction, and a sufficiently large ceiling reproduces expected participation.

This is the key contract-specific reduction in R42.

## 2.2 Closed quadratic cells

For quadratic reward and quadratic intermediate cost, eliminating the adjacent-lottery probability indeed produces a quadratic polynomial in the target and the two neighboring codewords. Singleton modes are likewise quadratic. The branch mode assignment therefore yields a quadratic objective over a rational polytope once the root-promise equality is included.

This is a useful formulation. It is also the point at which the genuinely model-specific work largely ends and generic nonconvex quadratic optimization machinery begins.

## 2.3 Stationary-face existence

The stationary-face lemma is essentially correct. If a global maximizer lies in the relative interior of a minimal-dimensional maximizing face, the gradient vanishes along the tangent space. If the restricted Hessian has a null direction, negative semidefiniteness and symmetry imply that the quadratic is constant along that direction, allowing the maximizer to be moved to a proper subface, contradicting minimality. Hence a maximizing face can be chosen with negative-definite restricted Hessian, or it is a vertex.

This justifies a finite exact candidate set.

It does **not**, by itself, constitute a strong new optimization algorithm. It is an exhaustive active-face principle for a union of polyhedra.

## 2.4 The mesh theorem

The one-sided catalog transport is technically cleaner than the usual informal “round the grid” argument. Flooring codewords preserves eligibility; recomputing the adjacent lottery rather than keeping the old probabilities is essential for exact risk feasibility; and the branch target is left unchanged. The resulting loss bound of order $h$ follows from Lipschitz control of terminal reward, intermediate cost, and level charges.

I do not see a defect in the stated $O(h)$ bound.

The important question is not correctness but significance: it is a robust, constraint-preserving Lipschitz discretization lemma, not a deep approximation result in the algorithmic sense.

---

# 3. Major correctness issue: the face-enumeration complexity bound is wrong

Theorem “Exact joint continuous design” states that, after eliminating one target, each cell has at most

$s+1+3k$

inequalities and therefore gives the all-subsets upper bound

$sum_{s=1}^m (2s-1)^k 2^{s+1+3k}$

linear systems.

That inequality count is not correct for the general bounded-overrun model.

For an adjacent-lottery mode $L_ell$, the cell requires all of the following:

1. $c_ell le t_j$;
2. $t_j le c_{ell+1}$;
3. $t_j le b_j$;
4. $c_{ell+1} le b_j+delta$.

For $delta>0$ with $b_j+delta<1$, none of the last three constraints is generally implied by the others. In particular:

- $t_jle c_{ell+1}$ and $c_{ell+1}le b_j+delta$ do not imply $t_jle b_j$;
- $t_jle b_j$ does not imply $c_{ell+1}le b_j+delta$.

The implementation in revisions/or-r42-certified-joint-design-20260924/code/faces.py in fact enforces these four branch inequalities in the relevant regime. Thus the code itself reveals the mismatch with the theorem statement.

A uniform safe count is therefore at least

$s+1+4k$

in the general case, giving the crude all-subsets bound

$sum_{s=1}^m (2s-1)^k 2^{s+1+4k}$.

There may be sharper regime-specific counts when $delta=0$ or when the risk ceiling is redundant, but the displayed theorem is stated for arbitrary $deltage0$.

This does not invalidate the existence of a finite exact algorithm, nor the computed small instances. It does invalidate the claimed worst-case bound as written. Because the paper advertises exact complexity explicitly, this must be corrected at theorem level, in the implementation discussion, and in any response-to-referees text that cites the old count.

---

# 4. Major blocker: the new global algorithm is exact by exhaustive enumeration, not an OR-level algorithmic advance

R42 solves the previously open global problem, but it does so in the weakest possible algorithmic sense compatible with exactness.

At book size $s$ it enumerates:

- every branch mode assignment, up to $(2s-1)^k$;
- every candidate active face of each cell;
- every nonsingular KKT system generated by those active sets.

The resulting method is exponential in the number of branches before active-set enumeration begins, and then exponential again in the number of inequalities.

That is a valid reference solver. It is not yet a compelling optimization algorithm for a flagship OR journal.

The paper itself appropriately avoids claiming polynomial complexity, but this leaves a publication-level gap. Once the contractual reduction has produced a finite union of rational quadratic programs, “enumerate every cell and every face” is a generic global strategy. The authors cite Del Pia, Dey, and Molinaro for polynomial-size witnesses, which is the right intellectual boundary, but the paper does not go on to exploit any additional structure of its own nonconvex problem.

I would expect at least one of the following before viewing the general theorem as a major Optimization contribution:

- a nontrivial parameterized algorithm whose dependence on $k$, $m$, or the number of distinct caps is materially better than raw mode enumeration;
- a provable branch-and-bound, dynamic-programming, or decomposition structure that uses the ordered codebook and eligibility prefixes;
- a hardness result showing that the exponential behavior is intrinsic in an appropriate input regime;
- a polynomial-time result for a meaningful nontrivial subclass substantially broader than the saturated Monge endpoint;
- or an approximation result for variable $m$ and variable $k$ whose complexity is more informative than exhaustive catalog subset enumeration.

At present the strongest broad statement is: the optimum can be found by finite exhaustive search because every cell is quadratic and every maximizing cell has a rational stationary-face witness. That is mathematically useful, but I do not think it is enough as the main new algorithmic pillar.

---

# 5. Major blocker: the mesh certificate is useful but too elementary to carry the general case

Theorem “Uniform exactly feasible catalog certificate” is a nice feasibility-preserving lemma. It successfully avoids promise slack and risk slack, which is better than naive rounding.

But the algorithmic consequence remains limited.

For a uniform mesh, the error is $K_mh$, and exact catalog optimization enumerates every subset up to size $m$. The resulting scheme is polynomial only for fixed $m$ and scales essentially as $N^m$ with $N$ proportional to $1/arepsilon$.

This is not misrepresented in the paper; the authors explicitly state these limitations. The problem is that, once they are stated honestly, the theorem is not a strong substitute for the missing scalable continuous algorithm.

The paper needs a sharper reason why this particular approximation result matters to a broad OR audience. Possibilities include:

- a minimax lower bound showing that $O(h)$ is order-sharp under the declared constraint-preserving requirement;
- an adaptive mesh or structural sparsification result;
- a variable-budget approximation guarantee;
- or a computational study demonstrating that the certificate gives practically useful bounds at realistic problem sizes.

Without such an addition, the mesh theorem reads as a careful Lipschitz discretization argument rather than a flagship approximation result.

---

# 6. Major blocker: computation does not test the claimed general continuous algorithm at meaningful scale

The new computational section is transparent about its limitations, which I appreciate.

However, those limitations are severe.

The exact continuous face solver is benchmarked primarily on three-branch instances, with one-branch and two-branch special checks. The paper explicitly says it does not establish large-scale performance of the exponential algorithm.

That is not enough for a paper whose new general contribution is an algorithmic global solution.

The implementation validation mostly establishes internal consistency:

- exact rational replay;
- fixed-book dual equality;
- support-oracle checks;
- inherited saturated comparisons;
- grid enclosures;
- a few analytic continuous global equalities;
- symbolic checks of small linear systems.

These are good software-engineering tests. They do not establish scalability, robustness of the exhaustive search, or competitiveness with standard global optimization technology.

A stronger computational section should include, at minimum:

1. a systematic grid in $(k,m,delta)$ showing cell counts, active-set counts, memory, and wall time;
2. the fraction of cells discarded as infeasible;
3. bit-length growth in exact arithmetic;
4. independent cross-checks against a separate global solver or an alternative MIQP/disjunctive formulation on random small instances;
5. a clear boundary beyond which the exact face method becomes impractical;
6. performance of the certified catalog approximation beyond the tiny continuous instances;
7. sensitivity of the bound to $mL_ho$ and to heterogeneous $gamma_j$.

At present the code is auditable, but the computational contribution is not yet persuasive.

---

# 7. Major blocker: “global certificate” language is stronger than the independent evidence supports

The paper distinguishes the fixed-book multiplier certificate from the global continuous search, which is good.

Still, some of the prose around “certified” global design should be tightened.

The reconstructed fixed-book multiplier independently certifies the **inner allocation conditional on the winning book**. It does not independently certify that no other cell or face has a better book. Globality comes from trusting that the exhaustive enumeration procedure has generated and evaluated every required candidate.

The build hashes and preservation records certify provenance and replay integrity. They do not certify completeness of the mathematical enumeration.

The current test suite checks several exact cases and compares the winning book to the fixed-book oracle. It does not independently solve the same random nonconvex global instances by a second method.

I therefore recommend reserving “certificate” for:

- the conditional supporting-price equality;
- the explicit mesh lower/upper interval;
- and any independently verifiable finite global witness if the authors create one.

If “global certificate” is retained, the paper should provide a checkable enumeration summary or a second global formulation that independently verifies the optimum on the reported benchmark instances.

---

# 8. Major blocker: the operational model is still too stylized to compensate for the modest general algorithmics

R42 improves the economic and operational explanation. The expected cap is now explicitly tied to quasilinear risk-neutral continuation utility or an actuarial budget; the realization ceiling is separated from expected participation; the acceptance timing is explicit; and the execution boundary is described as an allowlisted downstream gateway.

This is better.

But the model remains entirely stipulated.

The NIST SP 800-82 analogy supports the existence of restricted operational interfaces and allowlisting. It does not validate:

- the three-date renewal timing;
- the particular continuation-payment interpretation;
- the absence of a post-draw exit option;
- the choice of branch caps;
- the level-charge function;
- or the economic importance of the memory bottleneck.

The manuscript says this honestly. That honesty also means the paper cannot claim practical relevance as the main reason for publication.

For *Operations Research*, a heavily stylized application can certainly be publishable if the mathematical structure is powerful enough. Here that puts even more pressure on the new general optimization results, which, as discussed above, remain exhaustive.

A much stronger submission would either:

- connect the model to a concrete operational setting with realistic parameter magnitudes and a decision consequence that could matter to practice; or
- abstract away the renewal story and present a broader mathematical class for which the contractual structure yields a genuinely new optimization theory.

R42 currently sits between those two positions.

---

# 9. The charged pathwise-randomization example is mathematically valid but operationally contrived

Proposition “Pathwise randomization can matter in the interior” is useful as a logical counterexample to importing the saturated deterministic-collapse result into the nonsaturated charged model.

However, the example uses

$ho(c)=3c(1-c)$,

which is nonnegative but nonmonotone and has zero charge at both endpoints with its maximum in the interior.

That is a mathematically admissible selected-level charge. It is not an especially natural engineering, testing, or certification cost.

Because this example carries an important conceptual message, the authors should show whether the phenomenon survives under a more operationally plausible charge family, such as:

- a nondecreasing affine charge;
- a nondecreasing convex charge;
- a fixed opening fee plus a monotone level-dependent surcharge;
- or, ideally, zero charge.

If no such example exists, the paper should state clearly that the separation currently depends on a deliberately shaped nonmonotone opening cost and should not be interpreted as a generic pathwise-randomization advantage.

---

# 10. Scope inflation remains a risk: the global exact theorem is quadratic and rational

The paper is much more careful than earlier revisions, but the title and abstract still create a broad “exact design” impression.

The exact continuous outer theorem requires:

- rational quadratic terminal reward;
- rational quadratic intermediate costs;
- rational caps, probabilities, promise, and risk tolerance;
- and a rational quadratic nonnegative selected-level charge.

For general concave $f$, convex $h_j$, and Lipschitz $ho$, the manuscript has the canonical fixed-book reduction and the mesh transfer, but not the same exact unrestricted continuous global algorithm.

That is a respectable division of results. It should be made even more visually explicit.

I recommend that the introduction and conclusion state, in one sentence each, something like:

> The general concave model admits exact fixed-book structure and a feasible discretization bound; exact unrestricted continuous codebook optimization is proved only for the rational quadratic subclass.

That distinction is currently present in pieces, but a reader can still come away with a stronger generality impression than the theorem actually supports.

---

# 11. Novelty relative to the closest antecedents is improved but still not fully convincing

The updated literature section now discusses Jourdain and Pagès (2021), which is the correct close predecessor for optimized one-dimensional dual grids. That is a meaningful improvement over earlier versions.

The manuscript also correctly states that:

- unbiased adjacent random splitting is classical;
- optimized scalar grids are classical;
- selected-level opening costs are classical;
- finite-rate encoder/decoder restrictions are classical;
- Monge matrix search is classical;
- rational quadratic witness arguments are classical.

Once those ingredients are removed from the novelty claim, the distinct contribution is the contractual feasible-set geometry: eligibility prefixes, endogenous branch targets, heterogeneous intermediate shortfall costs, and exact promise/risk preservation.

I agree that this combination is not identical to the cited predecessors.

I am not yet convinced that the combination produces enough new optimization methodology for *Operations Research*. The theorem-level comparison table often has the form “classical method + model-specific feasible cost.” That can be publishable when the model itself is operationally important. Here the model is synthetic.

The paper therefore needs a sharper theorem-level statement of what a subsequent optimization researcher could reuse outside this particular renewal architecture.

---

# 12. Relation to current Operations Research editorial standards

I checked the current *Operations Research* editorial statement and Optimization-area statement on September 24, 2026:

- https://pubsonline.informs.org/page/opre/editorial-statement
- https://pubsonline.informs.org/page/opre/editorial-statement/area-editors-statements

The journal describes itself as seeking innovative and impactful research, with methodological rigor, and the Optimization area evaluates modeling, theory, algorithms, computation, and applications, asking accepted papers to excel in at least one dimension and remain relevant to a broad audience.

R42 is rigorous. The remaining question is whether it excels strongly enough in one of those dimensions.

My assessment is:

- **Modeling:** coherent but highly stylized and uncalibrated;
- **Theory:** correct-looking and careful, but much of the general machinery after reduction is classical quadratic optimization;
- **Algorithms:** the broad exact method is exhaustive and exponential, with a misstated worst-case count;
- **Computation:** reproducible but confined to small global instances;
- **Applications:** no empirical or implemented application.

That combination does not yet clear the journal bar in my view.

---

# 13. Required changes for a credible new submission

I would not recommend another incremental revision cycle. A credible new submission should make a material advance along the following lines.

## 13.1 Correct the theorem statement immediately

Fix the inequality count and the resulting active-set bound in the exact continuous-design theorem. Audit every place in the manuscript, response, code comments, tables, and README that repeats the old exponent.

## 13.2 Add a genuine complexity result

The paper needs more than “finite exact enumeration.” Establish at least one of:

- hardness;
- fixed-parameter tractability;
- a nontrivial polynomial subclass;
- a decomposition algorithm;
- or a variable-budget approximation result.

A negative complexity theorem would be valuable if it explains why the exponential reference algorithm is conceptually the right baseline.

## 13.3 Strengthen independent global validation

Formulate the small-instance problem independently, for example as a disjunctive MIQP or another exact global program, and cross-check random instances against the rational face enumerator. Report discrepancies, if any, and the domain where both methods remain tractable.

## 13.4 Expand the computational study

Move beyond $kle3$ for the continuous solver. Even if the algorithm becomes unusable quickly, documenting that frontier is scientifically important. For the grid method, show nontrivial $k$ and $m$ and report the actual certificate gap, not only the point estimate.

## 13.5 Either deepen the operational application or broaden the mathematical class

A real decision setting with defensible parameterization would raise the value of a model-specific theorem. Alternatively, a broader abstract optimization theorem showing that eligibility-prefix structure recurs in other limited-interface allocation models would make the methodological contribution more reusable.

## 13.6 Replace or qualify the nonmonotone-charge separation example

Provide a pathwise-randomization separation under a more natural charge class, or explicitly quarantine the current example as a mathematical possibility driven by a specially shaped charge.

---

# 14. Minor and presentation comments

1. The new abstract is clearer, but it is still dense with phrases such as “closed quadratic cells,” “contractual tail costs,” and “Monge after minimization.” The journal's current submission guidance asks the abstract and introduction to be comprehensible beyond technical specialists. A lighter abstract would help.

2. The phrase “exact stationary-face enumeration solves the continuous outer problem” is mathematically accurate after the complexity correction, but “solves” can sound computationally stronger than intended. “Provides a finite exact reference algorithm” is better.

3. The title “Exact Design” is defensible for the quadratic subclass but invites overgeneralization. A subtitle or abstract qualifier should make the quadratic scope unmistakable.

4. The novelty table is useful. It should add a row or note separating “structural contribution” from “generic optimization mechanism” for the stationary-face theorem.

5. The paper should report the number of face systems actually solved in every continuous benchmark, not only elapsed time.

6. The build-validation record is excellent provenance documentation, but it should not be mixed rhetorically with theorem verification.

7. The current code uses exact rational arithmetic. This is a strength for auditability, but the manuscript should discuss bit-size growth empirically, because arithmetic-operation counts can conceal very large integer costs.

8. The fixed-budget mesh result should avoid any phrasing that could be read as an FPTAS claim. The manuscript is already mostly careful here.

9. The paper correctly cites Jourdain and Pagès (2021), *Journal of Approximation Theory* 267, 105581, DOI 10.1016/j.jat.2021.105581. Keep that comparison explicit.

10. The discussion of Del Pia, Dey, and Molinaro (2017), *Mixed-integer quadratic programming is in NP*, should clarify that polynomial-size witnesses do not imply that the exhaustive face search is efficient.

---

# 15. Recommendation

**Reject in the present form.**

R42 has crossed an important line: I now believe the authors have a coherent exact mathematical theory for the declared quadratic joint-design model, modulo the complexity-count correction above. This is a substantially stronger position than R39.

But the revision still does not, in my assessment, cross the *Operations Research* publication line.

The core difficulty is no longer “the outer problem is unsolved.” The new difficulty is that the outer problem is solved by a generic exhaustive mechanism whose worst-case complexity is even larger than the paper states, while the application remains synthetic and the computation remains small-scale.

A future submission could become much more compelling if it converts the elegant contractual reduction into a nontrivial complexity or algorithmic theorem, or if it demonstrates that the stylized model captures an operational decision problem of sufficient independent importance. Without one of those advances, I would not recommend acceptance at this journal.

