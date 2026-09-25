# Confidential Referee Report for Operations Research

**Manuscript:** *Limited-Memory Renewal Contracts: Exact Eligibility Pooling and Certified Joint Design*  
**Revision reviewed:** `revision/ndu-operations-research-r49-dispersion-certificates-20260925`  
**Revision tip reviewed:** `2098592a99e47d36cc9fd16311f21d1858fa6e1e`  
**Scientific parent:** R48, commit `939cce84881a1d1eabf93aa3a2d3f4f4417ce53f`  
**Predecessor independent report:** `reviews/operation_research_referee_report_r45_independent_harsh_2026-09-25.md`, commit `260a5224c55e0326d9da7f0c813b4a3fcab7671f`  
**Review branch:** `review/operation-research-r49-independent-harsh-20260925`  
**Date:** September 25, 2026  
**Recommendation:** **Reject in the present form, while recognizing that R49 contains the first potentially publishable core result in this revision sequence. The terminal-first pooling identity and the resulting exact common-eligibility algorithm appear mathematically credible and directly address the central weakness identified in R45. Nevertheless, the tractable parameter is a catalog-dependent eligibility partition that is structurally fragile, the general multi-class problem remains exponentially difficult and empirically unresolved even at five to eight classes, the novelty beyond classical separable resource allocation plus ordered-path dynamic programming is too model-specific for the current breadth and length, and the computational study is dominated by deliberately favorable common-eligibility instances rather than a convincing evaluation of the hard joint problem.**

---

## Executive assessment

R49 is a substantial revision. It does not merely add another heuristic target portfolio or another conditional alphabet optimizer. Its principal new theorem identifies a genuine structural reduction: histories that admit the same finite-catalog prefix share the same terminal interpolant, and their heterogeneous caps and service costs can be handled through an exact terminal-first allocation rule. The difference between capped equalization and the true heterogeneous service allocation depends on the selected book only through the last eligible level. This makes the correction compatible with an ordered-path recurrence.

For a single eligibility class, the group mean is fixed by the root promise. The corrected path dynamic program therefore jointly optimizes the installed book and all individual targets at the original symbol budget. This is materially stronger than R45's fixed-target dynamic program and target-space grid. It applies at interior promises, allows heterogeneous caps and quadratic service curvatures, includes nonnegative level-opening charges, and is polynomial in the number of histories, catalog size, and symbol budget.

For multiple eligibility classes, R49 also derives an exact price support over boxes of group means and combines it with a checked subdivision procedure. This is a real original-space upper bound, not a representative-curvature relaxation with an added dispersion allowance. The independent checker verifies the pooled service corrections, Bellman inequalities, anchor feasibility, cover completeness, and the uneliminated policy.

I audited the new pooling theorem, the correction formula, the fixed-mean recurrence, the group-box price identity, the accuracy theorem, the implementation, checker, tests, protocol, and reported results. I do not presently see an immediate counterexample to the terminal-first identity or to the exact common-eligibility algorithm. My recommendation is therefore not based on inventing a mathematical failure.

The remaining objections concern scope, complexity, novelty, evidence, and presentation. The parameter that makes the problem tractable is not an exogenous number of economic or operational types. It is the number of distinct eligible prefixes induced jointly by the realization thresholds and the chosen catalog. It can increase sharply when a catalog is refined or when a threshold crosses one candidate level. The common-eligibility scaling experiment sets every realization ceiling to one, creating the easiest possible eligibility structure. Once eligibility complexity reaches only five to eight classes, ten of twelve requests at tolerance 0.001 remain unresolved under the larger declared node allowance, even with only twelve histories, nine catalog points, and budget three.

Thus R49 establishes an elegant polynomial special case and an exact fixed-parameter-style decomposition, but not a broadly scalable joint-design method. The manuscript also remains an enormous cumulative package: 39 nonreference main pages, a 39-page mathematical companion, and a 28-page computational record, carrying 53 antecedent mathematical statements plus four new theorems. In my assessment, the structural insight is not yet developed into a sufficiently general complexity theory, robust algorithm, or operational application to justify this scale at *Operations Research*.

---

# 1. Version audit and genuine progress

The reviewed R49 branch is eleven commits ahead of the validated R48 tip. The final publication commit reports a 42-page article with 39 nonreference pages, a 39-page electronic companion, a five-page response, and a 28-page computational record. The build reports no unresolved references, duplicate labels, or overfull boxes, and the repository preserves the inherited source tree.

R49 makes four genuine advances.

1. **It replaces approximate cap/cost aggregation with exact eligibility pooling.** Histories inside a class retain their original caps, weights, curvatures, and policies. They are not replaced by a representative branch.

2. **It solves endogenous target allocation in the common-eligibility regime.** This is the first scalable theorem in the manuscript pipeline that jointly selects targets and a charged finite-catalog alphabet at an interior promise without enlarging the symbol budget.

3. **It produces a locally exact multi-class price oracle.** The correction is inserted at the unique path edge leaving a class's eligible prefix, or at the terminal node if the path never leaves it.

4. **It improves certificate independence.** The checker does not import the pooling optimizer and verifies weak-duality witnesses and the complete target-space cover rather than trusting a completion flag.

These changes directly answer several criticisms in the R45 report. They should not be minimized.

They also make it possible to state the current blockers more sharply. The issue is no longer that the paper has only conditional optimization. The issue is whether exact eligibility pooling is sufficiently broad, stable, novel, and empirically consequential to carry the publication case.

---

# 2. Mathematical audit

## 2.1 Terminal-first pooling

For a fixed book and an eligibility class, every member has the same eligible selected levels and hence the same terminal interpolant. The exchange argument is persuasive: if one member uses positive intermediate service while another still has unused terminal capacity, transferring weighted target mass from service to terminal allocation weakly lowers service cost and strictly raises terminal reward. An optimum therefore fills terminal capacity before assigning service.

Below the aggregate terminal capacity

\[
D_g(d)=\sum_{j\in G_g}w_{j|g}\min\{b_j,d\},
\]

capped equalization is optimal for the common concave interpolant. Above it, all terminal capacities are filled and the residual is an ordinary separable capped-cost allocation. This yields the displayed piecewise value formula.

The correction

\[
\Delta_g(d;s)=\sum_{j\in G_g}\pi_j h_j((\theta_j^g(s)-d)_+)
-W_g C_g((s-D_g(d))_+;d)
\]

is nonnegative because the equalized service vector is feasible for the capped-cost problem. I find this argument correct.

The proof should nevertheless be expanded in two places. First, the weighted exchange should be written explicitly because histories have unequal weights. Second, at the kink \(s=D_g(d)\), the equality of the two representations and the feasibility of the equalized service vector should be stated directly rather than left implicit.

## 2.2 Exact eligibility-mean frontier

The path-local placement of the correction is convincing. Every book has one last selected level within a class's eligible prefix. That level is identified either by the unique crossing edge into the ineligible catalog suffix or by the book's terminal node. Adding the correction exactly once therefore converts the fixed-target path value at the equalized targets into the true pooled value at the supplied class mean.

The claimed arithmetic count is plausible for rational quadratic costs. Equalized targets are computed once. For every class and candidate last eligible level, the capped quadratic allocation can be solved after ordering the breakpoints \(\gamma_j(b_j-d)_+\). The original crossing terms and path recurrence remain polynomial.

For \(E=1\), the root equality fixes the only class mean at \(B\), so no outer target search remains. This gives a genuine exact polynomial special case.

The theorem statement should explicitly require rational opening charges when asserting exact rational bit complexity. “Arbitrary nonnegative charges” is an optimization statement; polynomial rational encoding requires representable charges.

## 2.3 Exact group-box price decomposition

The box identity is the technically most delicate part of R49. The artificial individual bounds obtained from capped equalization have weighted endpoint sums equal to the group lower and upper means. In the service region, their coordinatewise service bounds induce aggregate service inside the declared interval. The true group service support is therefore a relaxation of the artificial separate supports, and the correction \(\Xi_g\) is nonnegative.

The case split by price sign and by the position of the box relative to \(D_g(d)\) is coherent:

- below the terminal-capacity threshold, capped equalization handles the terminal-only problem;
- at a positive price, avoidable service is never optimal;
- when service is unavoidable, the difference is exactly the pooled service support minus the independent service supports;
- at a nonpositive price, terminal capacities are filled before service is optimized.

I do not see an immediate defect in this identity.

However, the manuscript should prove rather than merely assert the key endpoint relation

\[
\sum_j w_{j|g}(\theta_j^g(u_g)-d)_+=u_g-D_g(d)
\]

when \(u_g\ge D_g(d)\), and its lower-end analogue. This is what makes every vector admitted by the independent service box have total service in \([q_-,q_+]\). It is simple, but load-bearing.

## 2.4 Eligibility-parameterized accuracy

The repaired group-mean net is a valid analogue of the R45 target net with dimension \(E-1\) rather than \(k-1\). The same optimal book remains feasible at the rounded and repaired means, and the group response inherits the individual Lipschitz constant. The additive error proof is credible.

The subdivision convergence argument is also conceptually sound because price zero alone yields local tightness proportional to the total weighted box width.

The displayed cover-size bound needs a more explicit derivation. The proof introduces an unnamed threshold \(\eta\), invokes dyadic bisection, and then jumps to

\[
\left(\max\{1,4L(E-1)/\varepsilon\}\right)^{E-1}.
\]

The intended reasoning appears to be: choose \(\eta=\varepsilon/[2L(E-1)]\), require each free weighted width to be at most \(\eta\), and use

\[
2^{\lceil\log_2(1/\eta)\rceil}<2/\eta.
\]

This should be written explicitly, preferably first as the exact product

\[
\prod_{g\ne g_0}2^{\max\{0,\lceil\log_2(w_g^0/\eta)\rceil\}},
\]

and only then simplified. The current proof is too compressed for a theorem whose contribution is partly its complexity dependence.

## 2.5 What the mathematics does not establish

The paper does not establish that exponential dependence on \(E\) is necessary. It gives neither hardness nor a lower bound for variable eligibility complexity. It also does not establish an FPT running time of the form \(f(E)\operatorname{poly}(|I|)\) under binary accuracy encoding; the dependence is polynomial in numerical \(1/\varepsilon\) only for fixed \(E\).

These limitations are stated, but they remain central to the publication assessment.

---

# 3. Principal blocker: eligibility complexity is catalog-dependent and structurally fragile

The manuscript presents \(E\), the number of distinct eligible prefixes, as the relevant dimension. This is a useful exact parameterization. It is not yet a stable structural explanation of the operational problem.

Eligibility classes are induced by the finite catalog itself. A history's class is the number of candidate levels below its realization threshold. Consequently:

- adding a candidate level can split an existing class even if the underlying contracts are unchanged;
- refining a catalog to reduce discretization error can increase \(E\);
- a small perturbation of a realization threshold across one catalog point can change the algorithmic dimension discontinuously;
- and a dense catalog with heterogeneous thresholds can make \(E\) approach the number of histories.

This is a serious unresolved interaction. The paper treats catalog design as part of the optimization problem, yet its complexity parameter is determined by the candidate catalog supplied before optimization. A richer candidate set can improve the feasible value while simultaneously destroying the tractable class structure.

The manuscript needs a theorem or at least a systematic analysis connecting candidate resolution, threshold separation, \(E\), and approximation quality. Natural directions include:

- a threshold-aware candidate coarsening result with an original-space error bound;
- robustness when thresholds move inside a catalog gap;
- a joint choice of candidate levels and eligibility partition;
- or a complexity theorem parameterized by the number of distinct realization thresholds rather than exact finite-catalog prefixes.

Without such analysis, the strongest exact theorem is vulnerable to being an artifact of a coarse or deliberately aligned catalog.

---

# 4. The common-eligibility scaling experiment is deliberately favorable

The 16 large-history cases are generated with every realization ceiling equal to one. Thus every history admits the entire catalog. Common eligibility is guaranteed by construction, and terminal support eligibility is effectively nonbinding.

The instances vary caps, weights, curvatures, and opening charges, which is useful for testing the service pooling calculation. But they do not test the most distinctive part of the theorem: common eligibility at a nontrivial truncated prefix with heterogeneous ceilings inside the same catalog gap.

The remaining design choices are also narrow:

- budget is always three;
- catalog size is only nine or seventeen;
- the root promise is always nine-tenths of aggregate capacity;
- reward is always the same normalized quadratic;
- and there are only two seeds per scale.

Closing a one-class root node in 0.01--1.58 seconds confirms the polynomial implementation. It does not establish broad practical relevance or algorithmic robustness.

A convincing evaluation should include large one-class instances where the common eligible prefix is a strict subset of the catalog, several promise levels, several symbol budgets, nonuniform catalog geometry, and thresholds located close to catalog points. It should also study how runtime and policy value change when one threshold perturbation splits the class.

---

# 5. The general multi-class problem remains difficult

The stress experiment is more informative than the common-class scaling study. It uses only twelve histories, nine catalog points, and budget three, yet with five to eight eligibility classes:

- all requests at tolerance 0.01 finish;
- only two of twelve requests at tolerance 0.001 finish;
- the ten unresolved 127-node gaps range from roughly 0.00129 to 0.00591;
- one exact value is approximately 0.0302, so a gap around 0.0015 is economically nontrivial in relative terms.

This is an honest negative result. It also reveals the current method's limitation. The paper's general joint algorithm remains exponential in the effective class count and becomes weak at very small absolute tolerances on tiny instances.

The manuscript does not compare the group-box subdivision with:

- the completed repaired group-mean net;
- the earlier individual-box method under matched computational budgets;
- direct book enumeration or prefix search under the same wall-clock limit;
- modern spatial branch-and-bound or disjunctive global optimization;
- or adaptive selection of additional prices at child nodes.

The current solver uses a fixed finite price set selected at the root. Zero is enough for validity, but the numerical performance of the multi-class method may be dominated by this implementation choice. Before drawing methodological conclusions, the authors should investigate node-local price refinement, bundle or cutting-plane lower envelopes, and stronger incumbent generation.

---

# 6. Missing complexity classification

R49 improves the algorithmic map but still does not explain the intrinsic complexity of joint finite-catalog design.

The central unanswered questions now include:

1. Is the problem NP-hard when \(E\) is variable but the symbol budget is two or three?
2. Does hardness persist with zero opening charges or a common service curvature?
3. Is the problem fixed-parameter tractable in \(E+m\), or only polynomial for fixed \(E\) and numerical accuracy?
4. Can the group response be represented by a polynomial-size piecewise-quadratic object and optimized without a full box cover?
5. Are there meaningful Monge, submodular, or discrete-convex structures in the class-mean problem?
6. Can one obtain a variable-\(E\) approximation guarantee under threshold separation or bounded catalog density?

The absence of such results matters because the paper's headline is now a structural complexity claim. Showing a polynomial one-class case and an exponential class-mean scheme is not a complete complexity theory.

A negative hardness theorem would materially strengthen the paper by explaining why the class parameter is the right frontier. A stronger positive result would be even better. At present, the manuscript leaves the main algorithmic boundary unresolved.

---

# 7. Novelty relative to established methods

The terminal-first identity is the manuscript's genuine new idea. Once it is established, the remaining machinery combines:

- capped equalization for a common concave reward;
- separable convex resource allocation;
- ordered interval/path dynamic programming;
- Lagrangian price bounds;
- and box subdivision.

All of these mechanisms are classical, as the manuscript appropriately acknowledges.

The model-specific last-eligible-level correction is elegant. The question is whether this correction is broad enough to support a flagship OR paper of the present scale. The current abstraction still requires:

- a scalar ordered command catalog;
- a common terminal reward across histories;
- separable intermediate-service costs;
- prefix eligibility;
- one aggregate equality;
- additive opening charges;
- and canonical adjacent lotteries.

No second OR model is developed in which the same correction produces a new algorithm. The service-gateway language remains an interpretation of the same mathematical structure, not independent evidence of reuse.

I would view the pooling theorem as a strong lemma or a focused paper contribution. I do not yet view the accumulated 106-page package of pooling, continuous design, Monge theory, institutional comparisons, augmentation, harmonic coarsening, and historical algorithms as proportionate to the novelty of that lemma.

---

# 8. Computational evidence: strengths and limitations

## 8.1 Strengths

The computational protocol was frozen before execution. All specified cases are retained. Exact-rational intervals, original-space policies, coverage trees, service dual witnesses, and certificate hashes are archived. The independent checker is substantially stronger than a replay of solver status. The study also preserves failures rather than silently dropping them.

These are exemplary reproducibility practices.

## 8.2 Reuse of preceding cases

Twenty-four of the 64 exact runs are the immutable R48 paired instances. Reusing them is appropriate for a controlled comparison, but it does not provide an independent new distribution of problems. The “18 improved, five equal, one worse” comparison is against a different relaxation and historical execution environment. It shows bound quality, not a general performance ranking.

## 8.3 Limited exact references

The stress exact references rely on exhaustive enumeration with twelve histories, nine candidates, and budget three. The common-eligibility cases do not have an independent global optimization reference at large \(k\); they rely on the theorem and checker. That is acceptable for certification, but it means the large-scale experiment is not a competitive benchmark.

## 8.4 Mixed-integer comparisons

The 36 direct MIP envelope solves are useful model checks. They all terminate under the declared three-second limit. They remain small local-validation cases and use floating-point envelopes. The main article gives almost none of the detailed solver diagnostics; those are relegated to the computational record.

A journal reader should see at least distributions of bracket width, node count, solver gap, and time, not only the sentence that all solves succeeded.

## 8.5 Absolute tolerance

The headline tolerance \(10^{-3}\) is not scale invariant. The record includes normalized diagnostics, but the main article predominantly reports absolute gaps. For small positive objective values, a gap below \(10^{-3}\) can still be several percent. The stress table should include relative gaps wherever the reference value is positive.

---

# 9. Certificates do not by themselves establish practical usefulness

The R49 certificate chain is strong:

- a scalar multiplier certifies each pooled service support;
- Bellman inequalities certify path upper bounds;
- the tree verifies a complete class-mean cover;
- and the original policy is checked without canonical reconstruction.

This establishes validity of the reported intervals.

It does not establish that the algorithm is computationally attractive in the hard regimes. Certificate size grows with every recorded node and every path table. The paper gives asymptotic per-node storage, but no systematic study of certificate growth, checking cost, or serialization size as \(E\), \(N\), and the requested tolerance increase.

The 28-page computational record and compressed JSON certificates are offline artifacts. A practitioner would still need to generate them. The paper should distinguish more sharply among:

- mathematical verifiability;
- optimization time;
- certificate generation time;
- certificate checking time;
- and deployment memory.

The conclusion acknowledges that terminal alphabet size is not total implementation memory. That important qualification should appear earlier and more prominently.

---

# 10. Operational relevance remains unestablished

The manuscript is commendably explicit that all instances are synthetic. It does not invent calibration.

It consequently still lacks an independent application case. There is no evidence for realistic values of:

- the history probabilities;
- participation caps;
- realization thresholds;
- intermediate-service curvatures;
- level-opening charges;
- or the allowed absolute optimality tolerance.

The common-eligibility regime may or may not be operationally common. The paper provides no data showing how many eligibility classes arise in a realistic command catalog, how stable those classes are under threshold uncertainty, or whether a provider controls the catalog finely enough to engineer a small \(E\).

Because the model is highly specialized, this missing application evidence puts additional pressure on the methodological contribution. At present the paper remains a sophisticated synthetic theory exercise.

---

# 11. Contribution relative to length and organization

The article has improved its narrative, but the total package remains excessive:

- 39 nonreference article pages;
- 39 mathematical companion pages;
- 28 computational-record pages;
- 53 inherited labeled mathematical statements;
- four new R49 theorems;
- and a long chain of historical revision-specific methods.

Preserving every prior result in the current submission is not automatically a virtue. It makes the paper read as a repository history rather than a focused journal article.

R49 should be rebuilt around the new structural contribution:

1. canonical response and eligibility definition;
2. terminal-first pooling;
3. common-eligibility exact algorithm;
4. multi-class price oracle and complexity boundary;
5. a focused computational study.

The continuous-design, Monge, institution-comparison, union-augmentation, harmonic-coarsening, and earlier target-net material should be removed from this submission or placed in separately cited papers. A short appendix can state only the prerequisites actually used by R49.

Without such refocusing, contribution relative to length remains unfavorable.

---

# 12. Required changes for a credible new submission

I do not recommend another revision that merely increases node limits or adds more certificates. A credible new submission should make structural changes.

## 12.1 Clarify and stabilize the eligibility parameter

Provide a formal analysis of how \(E\) changes under catalog refinement and threshold perturbation. Develop a robust or approximate pooling theorem when thresholds lie near catalog points.

## 12.2 Establish the complexity frontier

Prove hardness for variable \(E\), or produce a materially stronger algorithm. At minimum, give a parameterized-complexity map in \(E\), \(m\), the number of distinct thresholds, and accuracy encoding.

## 12.3 Strengthen the multi-class algorithm

Investigate node-local price generation, stronger lower envelopes, dominance across boxes, and reuse of service-frontier breakpoints. Compare these variants under matched budgets.

## 12.4 Expand the common-eligibility evaluation

Use strict common prefixes rather than only ceiling one, vary promises and budgets, place thresholds near catalog boundaries, and include substantially larger and nonuniform catalogs.

## 12.5 Evaluate the hard regime competitively

Compare against direct MIP/global optimization, individual-box subdivision, repaired group nets, and exact enumeration where feasible, under matched time and memory limits.

## 12.6 Report relative and normalized errors in the article

Absolute \(10^{-3}\) gaps are insufficient when objective scales vary substantially.

## 12.7 Refocus the manuscript

Split the R49 pooling paper from the accumulated historical theory. The current package is not an efficient vehicle for communicating the new result.

## 12.8 Either calibrate an application or broaden the abstraction

A real restricted-interface application could justify a specialized structural theorem. Otherwise, demonstrate the same last-eligible-boundary correction in another optimization model.

---

# 13. Minor and presentation comments

1. Define the eligibility signature explicitly as an integer prefix length before introducing classes.

2. State prominently that eligibility classes depend on the candidate catalog, not only on primitive contracts.

3. In Theorem “Exact eligibility-mean frontier,” include rational charges in the bit-complexity assumptions.

4. Expand the weighted terminal-to-service exchange in the pooling proof.

5. Show the endpoint identities that justify the service interval \([q_-,q_+]\) in the box theorem.

6. Define \(\eta\) explicitly in the subdivision proof and give the exact dyadic product bound before the simplified cover count.

7. “Exact joint design” should always be qualified by “finite catalog.”

8. The abstract should say that the one-class regime is exact and polynomial, while the multi-class regime is exact per box but globally exponential in \(E\).

9. The large-history table should state that all ceilings equal one and all catalog levels are eligible.

10. Add relative gaps to the eligibility-stress table.

11. The 19 zero-width paired cases should be separated into structural one-class closures and price-bound coincidences in multi-class cases.

12. Report actual certificate sizes and checking-to-optimization time ratios.

13. Explain whether the class partition is recomputed when a catalog is changed in candidate-generation or continuous-approximation workflows.

14. The title “Certified Joint Design” is broad. A more precise title would foreground finite catalogs and eligibility pooling.

15. The computational record should remain supplementary; the article should contain the load-bearing diagnostics needed to assess the claims.

16. The response repeatedly emphasizes preservation of all historical labels. That is repository provenance, not an editorial contribution.

17. The study uses only quadratic rewards and costs. Distinguish clearly between the general convex pooling identity and the implemented exact algorithm.

18. Avoid describing a tolerance-complete interval as an “exact solution” unless its rational width is zero.

---

# 14. Recommendation

**Reject in the present form.**

R49 is the strongest revision in this sequence. The terminal-first pooling theorem appears to be a genuine and useful structural observation. The common-eligibility path algorithm is a real original-budget joint optimizer rather than a conditional or augmented-budget substitute. The group-box certificate is carefully constructed, and the repository's reproducibility and independent checking are unusually strong.

Those strengths make the paper worth further development.

They do not yet make the current submission suitable for *Operations Research*. The tractable parameter is catalog-dependent and fragile; the hard multi-class regime remains exponential and empirically unresolved at very small scale; the complexity frontier is not characterized; the large-history experiment is engineered to have completely nonbinding eligibility; no calibrated application supports the model's practical importance; and the cumulative manuscript is far too broad for the incremental methodological scope.

A focused paper centered on exact eligibility pooling could become compelling if it establishes the intrinsic complexity boundary, analyzes robustness to catalog and threshold changes, and demonstrates the method on nontrivial eligibility structures. The present 106-page package does not yet meet the journal's standards for generality, impact, and contribution relative to length.