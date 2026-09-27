# Second Confidential Referee Report for Operations Research

**Manuscript:** *Limited-Memory Renewal Contracts: Exact Eligibility Pooling and Certified Joint Design*  
**Revision reviewed:** `revision/ndu-operations-research-r49-dispersion-certificates-20260925`  
**Revision tip reviewed:** `2098592a99e47d36cc9fd16311f21d1858fa6e1e`  
**First independent R49 report:** `reviews/operation_research_referee_report_r49_independent_harsh_2026-09-25.md`, commit `2ac1490e5a4149f8c7e154407fbe6fa6208979db`  
**This review branch:** `review/operation-research-r49-second-independent-harsh-20260925`  
**Date:** September 25, 2026  
**Recommendation:** **Reject in the present form. This second independent audit agrees that the terminal-first pooling identity is the first genuinely strong structural result in the revision sequence, and I do not find an immediate counterexample to the exact common-eligibility algorithm. However, Theorem “Eligibility-parameterized joint accuracy” contains a concrete incorrect worst-case leaf-count bound: midpoint bisection and dyadic rounding require an additional factor that the displayed formula omits. More fundamentally, the claimed tractability parameter is induced by the full candidate catalog rather than by the selected book or an exogenous operational type system, so harmless catalog refinement can split classes and destroy the polynomial regime. The large-history study forces the easiest case by setting every realization ceiling to one, while the multi-class method remains unresolved on very small instances. The paper therefore still lacks a stable complexity frontier, persuasive hard-regime evidence, and a focused contribution commensurate with its 106-page package.**

---

## Executive assessment

I conducted a second source-level review of R49 rather than simply repeating the first report. I concentrated on the exact pooling proofs, the advertised subdivision complexity, the definition of eligibility classes, the independent checker, and the relationship between the theoretical parameter and the computational protocol.

The positive assessment remains substantial. R49 contains a real structural idea. For histories admitting the same catalog prefix, the common terminal interpolant and a terminal-first exchange argument separate terminal allocation from heterogeneous intermediate-service allocation. The resulting service correction depends on the selected book through the last eligible level and can be charged once on an ordered path. With one eligibility class, the aggregate promise fixes the sole group mean and the corrected path recurrence jointly optimizes individual targets and the finite-catalog book at the original memory budget. This is materially stronger than the preceding conditional, augmented-budget, or gridded results.

The exact group-box support is also a serious construction. It corrects the artificial individual target box by an exact capped-service support, provides a valid original-space price bound, and is accompanied by an unusually strong checker that verifies service primal-dual equality, Bellman domination, anchors, cover completeness, and the uneliminated policy.

I nevertheless recommend rejection for four central reasons.

First, one of the new theorem-level complexity statements is wrong as written. The claimed worst-case number of leaves for midpoint subdivision omits the ceiling incurred by dyadic refinement. A one-dimensional free-coordinate example with ratio three already needs four leaves although the theorem claims three. This does not invalidate the interval algorithm, but it invalidates the displayed finite-cover bound and the associated node count.

Second, the eligibility dimension is not intrinsic to the optimization problem. It is defined using the entire candidate catalog, while the book is itself a decision variable. Adding a candidate level that is never selected can split an eligibility class, increase the exponent, and move an unchanged optimum from the polynomial one-class regime to the exponential multi-class regime. The current theory therefore has an anti-monotonic relationship with catalog refinement: a richer approximation catalog can make the complexity classification worse even when the decision problem and optimal selected book are unchanged.

Third, the computational evidence does not test the structural fragility. Every 16-to-1,024-history “common eligibility” instance sets every realization ceiling to one, making all catalog levels eligible by construction. The difficult multi-class study has only twelve histories, nine candidates, and budget three, yet ten of twelve requests at tolerance \(10^{-3}\) remain unresolved at the larger node allowance. The favorable scale headline and the difficult-regime evidence are therefore about different problems.

Fourth, the manuscript remains far too broad. The potentially publishable contribution is exact eligibility pooling. It is embedded in a 39-nonreference-page article, a 39-page mathematical companion, and a 28-page computational record carrying the cumulative history of many earlier papers. Repository preservation is admirable, but archival completeness is not a substitute for editorial focus.

---

# 1. Audit scope and version isolation

The reviewed scientific tip is exactly `2098592a99e47d36cc9fd16311f21d1858fa6e1e`. No later Operations Research revision was present when this report was prepared. This second review branch is created directly from that tip rather than from the first R49 review branch. It therefore adds only this report and does not import or modify the first report, manuscript, code, evidence, or historical branches.

The build record reports:

- 42 total main-paper pages, 39 nonreference pages;
- 39 pages in the mathematical electronic companion;
- a five-page response;
- a 28-page computational record;
- a 186-word abstract;
- no unresolved references, duplicate labels, or overfull boxes.

The source package is unusually disciplined about provenance, immutable protocols, exact certificates, and preservation. These are strengths. They do not determine journal suitability.

---

# 2. Mathematical audit of the new pooling theory

## 2.1 Terminal-first pooling

For a fixed selected book and one eligibility class, all members see the same eligible selected levels and hence the same piecewise-affine terminal reward interpolant. The central exchange argument is persuasive. If one history uses positive intermediate service while another still has unused terminal capacity, moving an equal amount of weighted target mass from the former to the latter weakly lowers intermediate cost and strictly increases terminal reward. Thus intermediate service and unfinished terminal capacity cannot coexist at an optimum.

Below the aggregate terminal-capacity threshold

\[
D_g(d)=\sum_{j\in G_g} w_{j|g}\min\{b_j,d\},
\]

capped equalization maximizes the common concave interpolant. Above this threshold, every terminal capacity is filled and the residual mean is allocated through a separable capped convex-cost problem. The value formula and the nonnegative correction

\[
\Delta_g(d;s)
=\sum_{j\in G_g}\pi_j h_j((\theta_j^g(s)-d)_+)
-W_g C_g((s-D_g(d))_+;d)
\]

are credible. The equalized service vector is feasible for the capped-cost problem, so the second term cannot exceed the first.

I recommend expanding the proof in three small but load-bearing places:

1. Write the weighted transfer explicitly. If target mass \(\delta\) is removed from history \(i\), the receiving history must be increased by \(\pi_i\delta/\pi_j\), subject to capacities. The current verbal argument is correct in spirit but should display the weighted conservation equation.

2. State continuity and equality of the two value formulas at \(s=D_g(d)\). At that point the residual service is zero and both expressions reduce to the same fully filled terminal value.

3. State explicitly why \(s>D_g(d)\) implies the equalization water level exceeds \(d\), and hence why \(\theta_j^g(s)\ge \min\{b_j,d\}\) coordinatewise. This is used in identifying the equalized service vector.

These are presentation improvements, not reasons for rejection.

## 2.2 Exact eligibility-mean frontier

The correction can be assigned exactly once because every selected book has one last selected level within each eligibility prefix. If a later selected level leaves the prefix, the crossing edge owns the correction; otherwise the terminal node owns it. This transforms the supplied-mean fixed-target path value into the true pooled value without changing the selected-level charges.

For a single eligibility class, the root equation sets the class mean to \(B\). The corrected recurrence therefore solves the finite-catalog joint problem, not merely a conditional book problem. I find this theorem to be the manuscript’s strongest result.

The arithmetic count is plausible for rational quadratic primitives. For every candidate last eligible level, the capped quadratic service allocation is found by sorting breakpoints \(\gamma_j(b_j-d)_+\), filling zero-cost capacity, and solving one linear water-level equation. The ordered-path recurrence then has the advertised polynomial arithmetic structure.

The theorem statement should separate two assertions that are currently combined:

- optimization permits arbitrary nonnegative opening charges as mathematical inputs;
- exact rational arithmetic and polynomial bit complexity require rationally encoded opening charges.

The second assertion is not meaningful for arbitrary real charges.

## 2.3 Group-box price identity

The group-box construction is technically delicate but appears coherent. Capped equalization maps group-mean endpoints to artificial individual-coordinate endpoints. In the service region, the true group support optimizes over one aggregate service interval, whereas the artificial individual box optimizes each service coordinate independently. The exact difference is the correction \(\Xi_g\).

The sign and price cases are sensible:

- below the terminal-capacity threshold, no service is needed;
- with a positive price, avoidable service is dominated;
- with unavoidable service, both formulations choose their smallest allowed mean and differ by the pooled-versus-separate service support;
- with a nonpositive price, terminal capacities are filled before the service support is selected.

The proof should explicitly include the endpoint identities

\[
\sum_{j\in G_g}w_{j|g}(\theta_j^g(u_g)-d)_+=u_g-D_g(d)
\]

when \(u_g\ge D_g(d)\), and the analogous lower-end identity. These relations are what ensure that every independently bounded service vector has aggregate service inside \([q_-,q_+]\). The claim is true, but it is sufficiently central that it should not be left implicit.

---

# 3. Concrete theorem error: the subdivision leaf bound is false as written

Theorem “Eligibility-parameterized joint accuracy” states that the completed projected subdivision has at most

\[
\left(\max\left\{1,\frac{4L(E-1)}{\varepsilon}\right\}\right)^{E-1}
\]

leaves, with fewer than twice as many nodes.

This formula omits the dyadic ceiling required by midpoint bisection.

Let

\[
\eta=\frac{\varepsilon}{4L(E-1)}.
\]

For a free weighted coordinate with initial width \(w_j^0\), midpoint subdivision needs

\[
q_j=\max\left\{0,\left\lceil\log_2\frac{w_j^0}{\eta}\right\rceil\right\}
\]

splits along a fully refined root-to-leaf path. A complete tensor cover can therefore require

\[
\prod_{j\ne j_0}2^{q_j}
\]

leaves.

The displayed theorem bound drops the ceilings. This is not harmless.

### One-dimensional counterexample

Take \(E=2\), so there is one free coordinate, and suppose its initial weighted width is one. Choose the tolerance so that

\[
\frac{4L(E-1)}{\varepsilon}=3.
\]

The theorem claims at most three leaves. Midpoint bisection of an interval of width one cannot cover it with three dyadic leaves all of width at most \(1/3\): after three leaves the widths must be \(1/2,1/4,1/4\) up to order, so one leaf is still too wide. Four leaves of width \(1/4\) are required.

Thus the theorem’s worst-case leaf count is false even in the first nontrivial dimension.

A safe product statement is

\[
\prod_{j\ne j_0}
2^{\max\{0,\lceil\log_2(w_j^0/\eta)\rceil\}}.
\]

Using \(w_j^0\le1\), a simple coarse bound is

\[
\left(2\max\left\{1,\frac{4L(E-1)}{\varepsilon}\right\}\right)^{E-1}.
\]

The total number of nodes in a full binary tree is then less than twice this corrected leaf bound.

This error does **not** invalidate weak duality, certificate validity, convergence, or the computed intervals. The independent checker verifies a realized cover, not the a priori combinatorial bound. It therefore correctly accepts the certificates while being unable to detect this theorem-count error.

The manuscript, abstract, response, complexity table, and any implementation documentation repeating the old count must be corrected.

---

# 4. Eligibility complexity is catalog-induced, not an intrinsic problem dimension

The paper presents \(E\), the number of distinct eligible catalog prefixes, as the relevant dimension. It is a useful sufficient parameter. It is not an intrinsic or stable parameter of the underlying operational problem.

Eligibility classes are defined using the **entire candidate catalog**, while the algorithm ultimately selects only a small book. Two histories may have different full-catalog prefixes yet admit exactly the same levels in every optimal or near-optimal selected book. The current partition separates them anyway.

This creates several problematic consequences.

## 4.1 Unused candidates can worsen the complexity classification

Suppose two histories have thresholds on opposite sides of a candidate level that is never selected by any optimal book. Removing that unused candidate merges the histories into one eligibility class without changing the feasible selected books of interest or the optimum. Adding the candidate back splits the class and raises the exponent.

Thus an irrelevant level can move the same decision problem from \(E=1\) exact polynomial optimization to \(E=2\) outer search.

## 4.2 Catalog refinement is anti-monotone for the theory

A denser candidate catalog is normally introduced to approximate continuous design better. Here refinement can create new threshold crossings and increase \(E\). The finite-catalog approximation can improve while the theoretical search dimension deteriorates.

The paper currently treats candidate generation, continuous approximation, and eligibility pooling as largely separate components. They are not separate from a complexity perspective. Any adaptive catalog method may change the eligibility partition after every inserted level.

## 4.3 The selected book induces a coarser endogenous partition

For a fixed book, only selected levels matter. The true equality condition for pooling is equality of the selected eligible sets, not equality of full-catalog prefixes. Because the book is a decision variable, the most natural class structure is endogenous.

The manuscript should investigate whether the path state can merge histories until a selected level crosses a threshold, rather than committing to the full-catalog partition in advance. Even a partial result could materially improve the generality of the method.

## 4.4 Dense catalogs can make \(E\approx k\)

With heterogeneous thresholds and a sufficiently dense catalog, nearly every history can have a distinct prefix. In that regime the new accuracy scheme reverts to essentially the same dimensional curse as the individual-target method.

The paper should therefore describe \(E\) as a catalog-dependent sufficient parameter, not “the relevant dimension” without qualification.

Required additions include:

- a monotonicity or sensitivity theorem for \(E\) under catalog refinement;
- threshold-perturbation analysis;
- examples where an unused level splits classes without changing the optimum;
- and, ideally, a dynamic or book-dependent pooling algorithm.

---

# 5. The large-history experiment tests the easiest possible eligibility structure

The 16 common-eligibility instances contain up to 1,024 histories, which sounds impressive. Their protocol sets every realization ceiling to one. Because the catalog lies in \([0,1]\), every level is eligible for every history. Hence \(E=1\) is guaranteed by construction.

This experiment usefully tests arithmetic scaling in \(k\), heterogeneous caps, heterogeneous quadratic costs, zero curvatures, weights, charges, and exact checking. It does **not** test the robustness of the common-prefix theorem.

A convincing structural study should include at least the following common-prefix families:

1. **Strict-prefix common eligibility:** all ceilings lie in the same interior catalog gap, so the common eligible prefix excludes a nonempty suffix.

2. **Different ceilings within one gap:** thresholds vary substantially but do not cross a catalog candidate.

3. **Near-boundary perturbations:** thresholds are just below and just above a candidate, demonstrating the class split and its computational effect.

4. **Catalog-refinement paths:** begin with a common-prefix catalog and insert levels one at a time, recording value improvement, \(E\), runtime, and certificate size.

5. **Unused splitting levels:** add a candidate that changes \(E\) but is never selected, testing whether the current method pays a complexity cost for an irrelevant option.

Without such cases, the 1,024-history result demonstrates the theorem on a deliberately degenerate eligibility geometry.

---

# 6. The multi-class regime remains computationally difficult at very small scale

The hard-regime study has only:

- 12 histories;
- 9 catalog levels;
- budget 3;
- 5 to 8 eligibility classes.

At tolerance \(10^{-3}\), only two of the twelve requests finish at the larger 127-node allowance. Ten remain unresolved. The displayed gaps range up to approximately \(0.0059058\).

Several relative gaps are not negligible. For example, an absolute interval of roughly \(0.0015092\) around an exact value near \(0.030152\) is about five percent of the value scale. The main table reports only absolute gaps, which obscures this point.

The paper correctly retains the failures. That honesty strengthens the evidence. It also shows that the general method is not presently scalable beyond modest eligibility complexity.

The study should be expanded along the parameter that the theorem says matters:

- \(E=1,2,3,\ldots\) under otherwise matched instances;
- multiple node budgets on a logarithmic scale;
- price-set size and selection strategy;
- certificate size and checker time;
- gap reduction per node;
- and comparison with direct MIP under matched time limits.

Currently the large-\(k\) results and the large-\(E\) results are disjoint. The former are easy by construction; the latter are tiny and often unresolved.

---

# 7. Missing complexity classification

R49 has now isolated a meaningful structural parameter. This makes the absence of a complexity boundary more conspicuous.

The paper should address at least some of the following questions.

1. Is the finite-catalog joint problem NP-hard when \(E\) is part of the input?

2. Does hardness persist with zero opening charges, common quadratic curvature, or budget \(m=2\) or \(m=3\)?

3. Is there an FPT algorithm of the form \(f(E,m)\operatorname{poly}(k,N,\text{bit length})\), as distinct from an approximation scheme whose exponent is \(E-1\)?

4. Can the catalog thresholds be incorporated into a dynamic state so that the dependence is on selected threshold crossings rather than all catalog-induced classes?

5. Are there Monge, discrete-convex, or submodular structures in the group-mean outer problem?

6. Is there a variable-\(E\) additive approximation with polynomial dependence on \(k,N,1/\varepsilon\)?

7. What lower bound shows that the current exponential dependence on \(E\) is intrinsic rather than a consequence of rectangular subdivision?

Without a hardness theorem or a stronger algorithm, the manuscript cannot convincingly claim to have identified the correct tractability frontier.

---

# 8. Novelty relative to established mechanisms

The terminal-first identity and last-eligible-level localization appear novel within the declared model. They deserve credit.

After that identity, the remaining machinery is assembled from established components:

- capped equalization;
- separable convex resource allocation;
- scalar Lagrangian support;
- ordered path dynamic programming;
- and box subdivision with Lipschitz convergence.

A model-specific structural identity can certainly support an OR paper. Here the model remains narrow: common scalar terminal reward, prefix eligibility, one aggregate equality, branchwise caps, separable service costs, adjacent terminal lotteries, and additive level charges.

The paper would be much stronger if the pooling identity were demonstrated in a second substantially different OR setting, such as:

- a restricted-command service network;
- a menu-design problem with safety thresholds;
- an inventory or capacity allocation interface;
- or a finite-actuator control model.

A mere verbal “service gateway” interpretation is not enough. The question is whether the last-eligible-level correction recurs as reusable optimization structure.

---

# 9. Certificate strength and missing certificate diagnostics

The certificate design is excellent. The checker independently verifies:

- the eligibility partition;
- capped equalization;
- pooled service primal-dual equality;
- nonnegative corrections;
- Bellman domination on both path sides;
- anchor feasibility;
- complete binary cover reconstruction;
- the lower policy in the uneliminated constraints;
- and the final global interval.

This is substantially stronger than source hashes or optimizer-status replay.

The paper should nevertheless report actual certificate economics:

- compressed certificate bytes;
- uncompressed rational-entry counts;
- maximum numerator and denominator bit lengths;
- checker time divided by optimizer time;
- and growth with \(k,N,E\), and node count.

In the common-eligibility table, checker times are often of the same order as optimization times. That is acceptable, but it should be discussed. In a deployable audit setting, certificate size and verification cost are part of the method’s contribution.

The checker verifies a realized tree and therefore cannot validate the incorrect a priori leaf-count theorem. The test suite should add a direct combinatorial regression for the corrected cover bound.

---

# 10. Independent MIP evidence remains secondary

The direct formulation is genuinely different and all 36 envelope solves return successful status in the reported run. This is welcome.

However, the main article reduces the result to a sentence. To assess the strength of the evidence, readers need at least a compact table with:

- variables and binaries;
- branch-and-bound node counts;
- wall times;
- primal and dual values;
- solver relative gaps;
- envelope errors;
- and final bracket widths.

The computational record apparently contains these fields, but load-bearing evidence should not require navigating a 28-page auxiliary record.

The MIP comparison also remains small. It does not test the 1,024-history regime, and it is not presented as a matched-runtime competitor for the multi-class subdivision. That limitation should be prominent.

---

# 11. Operational relevance remains weak

The paper is explicit that its inputs are synthetic and its opening charges are stipulated. This is better than fabricated calibration.

It still leaves the manuscript without an independent application case. In particular, no evidence establishes:

- that a real system has few full-catalog eligibility prefixes;
- that eligibility remains stable as command candidates are refined;
- how realization thresholds and opening charges are estimated;
- whether a tolerance of \(10^{-3}\) changes a real decision;
- or whether the terminal alphabet dominates total implementation cost.

The conclusion now correctly distinguishes terminal alphabet size from target tables, encoder logic, constants, probability precision, and certificate storage. This clarification further weakens any literal memory interpretation of the headline model.

Without a calibrated application, the optimization theory must carry the paper. That increases the importance of the missing complexity boundary and robustness theory.

---

# 12. Contribution relative to length

The current package totals approximately 106 pages across the article, mathematical companion, and computational record. It retains 53 antecedent mathematical statements and adds four R49 theorems.

The repository should preserve the full historical record. The journal submission should not reproduce the whole history as one cumulative manuscript.

A focused paper should center on:

1. the canonical fixed-book response;
2. terminal-first pooling;
3. the corrected path recurrence;
4. the exact common-eligibility algorithm;
5. the multi-class oracle and a correct complexity theorem;
6. a complexity lower bound or stronger parameterized result;
7. and a focused experiment on nontrivial eligibility geometry.

The continuous-design, institution-comparison, Monge, resource-augmentation, harmonic-coarsening, and historical portfolio results should be separate papers or repository supplements unless directly needed for the proof chain.

---

# 13. Required changes for a credible resubmission

## 13.1 Correct the subdivision theorem

Replace the false leaf bound with the exact dyadic product bound and a valid coarse simplification. Audit the response, abstract, theorem tables, and code documentation for repeats.

## 13.2 Develop catalog and threshold robustness

Prove how \(E\) changes under candidate insertion and threshold perturbation. Give examples and bounds. Explain how eligibility classes are recomputed in any candidate-generation or continuous-approximation procedure.

## 13.3 Address endogenous selected-book eligibility

Investigate a dynamic partition that depends on selected threshold crossings, or prove why the full-catalog partition is unavoidable. At minimum, quantify the conservatism of full-catalog \(E\).

## 13.4 Establish a complexity frontier

Provide hardness or a stronger parameterized algorithm for variable \(E\). A statement that the current scheme is exponential is not a classification.

## 13.5 Replace the trivial common-eligibility scaling family

Add strict-prefix, near-boundary, refinement, and unused-splitting-level experiments. The all-ceilings-equal-one family should remain only as an arithmetic scaling check.

## 13.6 Expand hard-regime computation

Report relative gaps, gap-per-node curves, price sensitivity, certificate size, and matched-time MIP comparisons. Preserve every failure.

## 13.7 Refocus the manuscript

Submit the exact pooling theory as one coherent article. Move the accumulated historical pipeline out of the journal-facing manuscript.

## 13.8 Strengthen external relevance

Either demonstrate the correction in another OR model or provide a calibrated restricted-interface application. A second verbal interpretation is insufficient.

---

# 14. Minor and implementation comments

1. The theorem should say “rationally encoded nonnegative charges” in every exact-bit-complexity claim.

2. The phrase “relevant dimension” should become “a sufficient catalog-dependent dimension.”

3. The abstract should state that the one-class polynomial result concerns a finite catalog.

4. The abstract should not imply that the multi-class method is scalable merely because its exponent is independent of raw history count.

5. Add a strict-prefix common-eligibility example to the main text.

6. Add the one-dimensional ratio-three counterexample to the corrected cover-count discussion.

7. The exact product leaf bound should retain the initial weighted widths \(w_j^0\); replacing all of them by one hides easy anisotropic instances.

8. Distinguish structural zero-width root closures at \(E=1\) from zero-width coincidences produced by prices at \(E>1\).

9. Report relative as well as absolute gaps in the stress table.

10. Report certificate bytes and rational bit lengths.

11. The main article should display a compact MIP diagnostic table instead of only stating that all solves succeeded.

12. Clarify that candidate insertion can change the eligibility partition and invalidate reuse of a previous certificate tree.

13. Explain whether two histories with different full-catalog prefixes but identical eligibility on the winning book can be merged after optimization for certificate compression.

14. The common-eligibility timing table should be labeled “all catalog levels eligible” for the current protocol.

15. A tolerance-complete interval with positive rational width should not be called an exact solution.

16. The title remains broad. “Finite-Catalog Joint Design by Exact Eligibility Pooling” would be more precise.

17. Repository label preservation belongs in reproducibility documentation, not in the contribution narrative.

18. Keep the current distinction between numerical MIP brackets and exact rational certificates.

---

# 15. Recommendation

**Reject in the present form.**

This second review reaches the same editorial recommendation as the first, but for an additional concrete reason: the advertised worst-case subdivision leaf bound is mathematically incorrect as written. The error is repairable and does not invalidate the computed certificates.

More importantly, R49's exact pooling insight has not yet been developed into a stable and general complexity theory. The parameter \(E\) is induced by the full catalog, can increase under harmless refinement, and may substantially overstate the eligibility distinctions of the selected book. The impressive 1,024-history experiment removes this difficulty by making every level eligible, while the genuinely multi-class method remains unresolved on small instances.

I regard terminal-first pooling as potentially publishable. A focused paper that fixes the theorem count, characterizes hardness or parameterized complexity, treats catalog-dependent class instability, and evaluates nontrivial eligibility geometry could become a strong submission. The current cumulative 106-page manuscript does not yet meet the novelty, generality, evidence, and contribution-to-length standards of *Operations Research*.