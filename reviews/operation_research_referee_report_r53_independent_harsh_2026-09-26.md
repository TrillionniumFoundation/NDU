# Confidential Referee Report for Operations Research

**Manuscript:** *Finite-Catalog Renewal Design by Selected-Boundary Resource Paths*  
**Revision reviewed:** `revision/ndu-operations-research-r53-catalog-safe-certificates-20260926`  
**Revision tip reviewed:** `2e07a4cfb41d8fbc16cd64c3048877d3c8c2a288`  
**Scientific parent:** R52, commit `7bdfda8f84b84f491e80b50a86089c37ea4c7f3a`  
**Latest antecedent referee report:** `reviews/operation_research_referee_report_r49_second_independent_harsh_2026-09-25.md`, commit `4f0b662bd4184fc77fb57bd09c339bffb6213a69`  
**Review branch:** `review/operation-research-r53-independent-harsh-20260926`  
**Date:** September 26, 2026  
**Recommendation:** **Reject in the present form, while encouraging a substantially strengthened and more focused resubmission. R53/R52 contains a credible and potentially publishable structural core: the selected-boundary identity appears to convert the original finite-catalog joint menu/allocation problem into a scalar-resource path without relaxing the promise or command budget. I do not see an immediate counterexample to that identity, the capacity-repair certificate, or the new safe-deletion theorem. The present publication case nevertheless remains incomplete. The exact problem has no hardness or parameterized-complexity classification, so the necessity and quality of the additive scheme are unknown; after the structural reduction, the approximation mechanism is largely classical resource gridding; the general variable-eligibility algorithm is tested only on very small catalogs and budgets and is orders of magnitude slower than the reported numerical MIP and exhaustive references; and the R53 screening study is deliberately easy, uses a coarse certificate, and does not establish useful screening on plausible hard instances. With no calibrated application, these gaps leave the manuscript below the current Operations Research bar for theory, algorithms, and impact.**

---

## Executive assessment

This is a much stronger and more focused manuscript than R49. The authors no longer rely on an eligibility-class grid as the only general same-budget answer. The key new structural statement, developed in R52 and retained in R53, is that a selected book itself partitions terminal reward and intermediate-service capacity into arc resources. Histories eligible for a later selected command contribute terminal capacity to the corresponding chord, whereas histories whose eligibility ends between two selected commands contribute service capacity at the lower selected level. The total capacity of every selected path telescopes to the same original-obligation capacity.

That identity is important. It makes the path, rather than a full-catalog type partition, the fundamental object. A scalar resource grid can then be rounded and repaired on the same selected path, preserving the exact root promise, individual expected caps, supportwise realization ceilings, opening charges, and command budget. The exact common-prefix result remains available as a stronger special case.

R53 adds an eligibility-independent capacity potential and a sufficient safe-deletion rule for non-anchor commands. The deletion rule is global: it bounds a command in every predecessor-successor context and preserves individual targets. When the opening charge covers the bound, a reduced-catalog global certificate transfers back to the original catalog. This is substantially more rigorous than arguing from an unchanged incumbent.

I audited the model reduction, selected-boundary proof, repair theorem, dynamic program, concave convolution argument, rational implementation, independent resource checker, capacity-potential identity, screening theorem, transfer checker, protocols, and numerical records. I do not presently see an immediate mathematical counterexample to the central identities. My recommendation is therefore not a correctness rejection manufactured around a minor implementation detail.

The problem is that the manuscript has not yet completed the methodological and empirical case that would make the result suitable for *Operations Research*.

First, the exact finite-catalog problem is not classified. The paper introduces an additive scheme but proves no hardness result, no lower bound on the accuracy dependence, and no parameterized-complexity boundary. It remains possible, based on the present manuscript, that the selected-boundary structure admits a stronger exact or more efficient algorithm. Without that classification, the algorithmic significance of the resource grid is uncertain.

Second, once the selected-boundary identity is granted, the remaining approximation mechanism is a familiar scalar-resource discretization for a resource-constrained path. The model-specific reduction is the real contribution. The paper must make that distinction sharper and show that the reduction itself is sufficiently reusable or consequential.

Third, the evidence for the general algorithm is weak. The fine-tolerance variable-eligibility experiments have only 12 histories, 9 candidates, and budget 3. The exact numerical MIP and exhaustive references solve those cases much faster. Large-history experiments exercise the exact common-prefix special case, not the general additive method. No systematic scaling in catalog size, command budget, or inverse accuracy is reported.

Fourth, the R53 screening theorem is safe but limited. It cannot delete possible anchors, uses a deliberately conservative minimum-command envelope, and has no guarantee on the number of removals. The controlled experiment chooses caps, promise, candidate locations, and charges so that all inserted commands are plainly unattractive, and it requests an absolute tolerance of 0.1. This validates code paths, not practical preprocessing strength.

Finally, there is still no calibrated operational application. A pure optimization paper can succeed without one, but then the complexity theory, algorithmic comparison, and generality must carry the paper. They do not yet do so.

---

# 1. Version audit and substantive changes

The audited R53 publication tip is `2e07a4cfb41d8fbc16cd64c3048877d3c8c2a288`. The branch is four commits ahead of the validated R52 scientific parent. The current build reports:

- 24 total article pages and 23 nonreference pages;
- an 11-page electronic companion;
- a four-page response;
- a 182-word abstract;
- no undefined references or citations;
- no duplicate labels;
- and no overfull boxes.

The article is now within a reasonable journal length. This is a significant improvement over the cumulative R49 package.

R52 introduced the main scientific advance:

1. a global terminal-first exchange lemma that does not require common full-catalog eligibility;
2. the exact selected-boundary resource-path identity;
3. an original-obligation capacity-repair theorem;
4. a rational quadratic additive scheme with a scalar grid;
5. exact common-prefix optimization as a special case;
6. catalog and threshold-stability results;
7. and a generic compatible-production corollary.

R53 adds:

1. the local capacity potential \(p(v)-p(u)\);
2. the anchor-envelope command-screening theorem;
3. simultaneous safe deletion of certified non-anchor commands;
4. transfer of a reduced-catalog global interval to the original instance;
5. an independent screening-chain checker;
6. and a controlled screening study.

These are genuine changes. R53 is not merely a repackaging of the R49 common-eligibility theorem.

It is also important to note that the core R52 resource-path manuscript was not the subject of the antecedent R49 reports. The current report therefore reviews the R52 core as new scientific material, not just the R53 screening increment.

---

# 2. Mathematical audit of the structural reduction

## 2.1 Canonical fixed-book response

The canonical response is credible. For a fixed book, terminal mean should be pushed to the largest feasible value because the terminal interpolant is increasing and intermediate service cost is nondecreasing. An adjacent eligible lottery or a singleton plus pre-draw service attains the bound. The resulting branch response is concave.

This result is inherited, but it remains load-bearing. The present article correctly distinguishes expected caps from supportwise realization ceilings and does not weaken the latter during reconstruction.

## 2.2 Global terminal-first allocation

The weighted exchange in Lemma “Global terminal-first allocation” is correct-looking. If one history uses intermediate service while another has unfinished terminal capacity, the donor's terminal reward does not change when its service is reduced, its cost weakly decreases, and the recipient's strictly increasing terminal interpolant improves. The explicit probability-ratio adjustment preserves the weighted root equality.

This establishes a global ordering: positive terminal increments precede intermediate service. The common terminal reward is essential because it gives a common ordering of chord slopes.

## 2.3 Selected-boundary resource path

For adjacent selected commands \(u<v\), the paper defines:

- terminal capacity from histories eligible for \(v\);
- an exit set of histories whose last eligible selected command is \(u\);
- and a capped convex service-cost function on that exit set.

For a fixed selected path, every history contributes terminal increments along eligible selected edges until its last eligible command, then contributes its remaining service capacity exactly once. The capacity telescopes history by history to \(b_j-a\), and hence globally to ̅b-a.

The exact value identity is plausible. Concavity orders selected chord slopes. Earlier terminal layers can be filled before later ones; all terminal layers can be filled before service; and the disjoint exit sets turn residual service allocation into an infimal convolution of convex cost functions.

I do not see an immediate counterexample.

The proof is nevertheless too compressed for the theorem that carries the paper. The phrase “within the partial layer, distribute its mass among histories” hides the principal feasibility construction. A rigorous version should state and prove a nested-capacity lemma showing that:

1. full completion of every earlier aggregate layer places each history at the correct lower endpoint for the next layer;
2. every amount up to the aggregate capacity of the unique partial layer has a feasible individual allocation;
3. that individual allocation can be combined with the service allocations on exit sets;
4. and the reconstructed targets and lotteries exactly reproduce the path value.

The converse rearrangement also deserves a formal majorization or exchange lemma. It currently moves resources among arcs and then asserts implementability. The argument is persuasive, but this is the central novelty and should not read as a proof sketch.

## 2.4 Capacity potential

The R53 identity

\[
T_{uv}+Q_{uv}=p(v)-p(u),
\qquad
p(u)=\sum_j\pi_j\min\{b_j,u\},
\]

is correct and useful. It explains why eligibility changes arc payoff but not total scalar capacity when every ceiling is at least the corresponding cap.

It is also algebraically direct once the selected-boundary definitions are in place. I view it as clarification of the R52 structure, not a second major theorem.

## 2.5 Capacity-repair certificate

The general repair theorem is sound-looking. Rounding each coordinate of an optimal path down loses less than \(h\eta\) total resource and at most \(Lh\eta\) objective. A maximizing rounded path has enough unused capacity to absorb its residual, and increasing its coordinates by the residual changes payoff by at most another \(Lh\eta\).

For renewal paths, the capacity identity verifies the otherwise nontrivial repair assumption. The final fixed-book allocator can only improve the repaired value.

This is a clean use of a standard resource-discretization argument.

## 2.6 Renewal dynamic program and convolution

The dynamic program enumerates anchors, command counts, final catalog vertices, and scalar resource states. A concave arc kernel gives a Toeplitz anti-Monge transition matrix, so divide-and-conquer row maximization is valid even when the preceding Bellman vector is not concave. The implementation's separate brute-force and totally monotone checks support this claim.

The stated arithmetic bound

\[
O\!\left(kN^2Q\log(k+1)+mN^3Q\log(Q+1)\right)
\]

is plausible for the reference implementation, where \(Q\) is proportional to \(Lm/\varepsilon\). Exact rational scaling by a common denominator also appears defensible as a bit-complexity argument polynomial in the numerical grid size.

The paper should emphasize that the second term is effectively quadratic in the command budget after substituting \(Q=\Theta(Lm/\varepsilon)\), and cubic in the catalog size. The theorem is polynomial but not obviously scalable.

## 2.7 Exact common-prefix special case

The common-prefix theorem remains valid and useful. When the full catalog gives one eligibility class, the root promise fixes its mean, and the exact heterogeneous service correction depends only on the last eligible selected command. The ordered path can therefore optimize the book exactly.

This is a stronger special case, not evidence that the general resource-grid interval should close exactly.

---

# 3. Principal blocker: the exact problem has no complexity classification

The manuscript now provides a genuine additive algorithm for arbitrary prefix eligibility. That makes the missing complexity classification more, not less, important.

The reader is not told whether exact joint finite-catalog renewal design is:

- polynomially solvable under the current assumptions;
- weakly NP-hard;
- strongly NP-hard;
- fixed-parameter tractable in \(m\), the number of selected exit sets, or another structural parameter;
- or approximable more efficiently than the current scalar grid.

The paper observes that fixed-budget book enumeration is polynomial with an exponent depending on the budget. That is not a classification of the variable-budget problem.

The selected-boundary reduction may make a hardness proof accessible. At minimum the authors should investigate reductions from knapsack, constrained shortest path, or partition using simple catalogs and quadratic or piecewise-linear arc returns. Conversely, the common potential and concave kernels may permit a stronger exact algorithm. The present manuscript does not establish which possibility is true.

Without such a result, the resource grid may be:

- the right complexity frontier;
- a convenient but unnecessarily weak algorithm;
- or an approximation for a problem that is actually exactly tractable by exploiting additional Monge or discrete-convex structure.

For a flagship optimization journal, that uncertainty is a major gap.

A credible resubmission should provide at least one of the following:

1. a hardness theorem under a clean restricted regime;
2. a fixed-parameter algorithm with a meaningful parameter;
3. a stronger exact polynomial subclass broader than common eligibility;
4. an approximation lower bound;
5. or a substantially faster certified algorithm exploiting the selected-boundary structure.

---

# 4. The approximation guarantee is absolute and numerically pseudo-polynomial

The paper is careful not to call the result a relative-error FPTAS. That caution is appropriate.

For an absolute tolerance ε, the grid size scales with the numerical ratio \(L/\varepsilon\), not its binary encoding length. The normalized form replaces ε by ε/L, but this is still an additive guarantee in a chosen payoff scale.

This matters because:

- net values can be close to zero;
- opening charges can dominate operating returns;
- the optimum can be negative;
- and the operational meaning of an absolute tolerance is not calibrated.

The manuscript reports relative widths when an exact positive reference is available, which is good. The theorem itself supplies no multiplicative interpretation.

The difficult-model table illustrates the issue. An absolute width near \(5\times10^{-4}\) is only 0.09%--0.17% of most references, but it is 1.63% of the small positive value in seed 49503. Other applications could make the same absolute tolerance far less meaningful.

The paper should discuss whether the dependence on \(1/\varepsilon\) is order-optimal and whether data-dependent local Lipschitz constants or adaptive resource grids can reduce it. The current uniform grid is the most direct construction.

---

# 5. The computational evidence does not establish a useful general solver

## 5.1 Fine-tolerance general cases remain tiny

The six difficult variable-eligibility instances have:

- 12 histories;
- 9 catalog candidates;
- a command budget of 3;
- and requested width 0.001.

The resource method takes approximately 3.5 to 19.8 seconds on these cases. Every returned lower policy happens to equal the exhaustive optimum, but the rational resource certificates retain positive widths of about \(4.2\times10^{-4}\) to \(5.0\times10^{-4}\).

These are useful validation cases. They are not evidence of scalability in \(N\), \(m\), or \(1/\varepsilon\).

## 5.2 Numerical MIP and exhaustive references dominate the reported small cases

The direct MIP envelope formulation solves the same six cases in roughly 0.015 to 0.038 seconds, uses one branch-and-bound node, and returns numerical upper and lower values agreeing to floating-point precision. Exhaustive book enumeration is also reported as competitive.

The manuscript correctly says that numerical status is not an exact rational certificate. Even so, the empirical comparison is unfavorable by orders of magnitude.

A rational certificate can justify overhead, but the paper must identify regimes where that overhead buys something operationally or computationally unavailable from the alternatives. The current experiments do not.

## 5.3 Large-history scaling exercises a special exact regime

The 16--1,024-history experiments use a strict common eligible prefix. They are valuable because they avoid the trivial all-levels-eligible geometry criticized in R49. But they still exercise the exact common-prefix special case, not the arbitrary-eligibility approximation scheme.

The largest configurations take up to roughly four seconds, which is encouraging for that special case. It does not demonstrate scalability of the \(N^3mQ\) general algorithm.

## 5.4 The eligibility sweep is still small and coarse

The controlled sweep uses:

- 12 histories;
- 17 candidates;
- budget 3;
- and tolerance 0.01.

It records about 18,671 resource states and two- to three-second runtimes. This is informative, but it is a single modest scale. There is no systematic experiment varying:

- \(N\) at fixed \(k,m,\varepsilon\);
- \(m\) at fixed \(k,N,\varepsilon\);
- \(1/\varepsilon\);
- charge magnitude;
- or selected-path exit-set complexity.

## 5.5 Certificate economics are nontrivial

On the fine cases, compressed resource certificates range from about 0.216 MB to 6.628 MB and contain roughly 17,500 to 94,600 serialized rational entries. Numerator and denominator lengths reach hundreds of bits. Verification costs about 15%--17% of optimization time.

Those numbers are not necessarily prohibitive, but they show that “small terminal memory” is unrelated to proof storage. The paper says this, correctly. It should go further and identify the practical decision settings in which such certificates are worth maintaining.

## 5.6 Needed computational evidence

A stronger study should include:

1. a full factorial or carefully sampled scaling design over \(k,N,m,\varepsilon\);
2. matched wall-clock and memory comparisons with MIP, exhaustive enumeration, and class-box subdivision;
3. instances beyond the range where exhaustive enumeration is possible;
4. time-to-certified-gap curves rather than one requested tolerance;
5. adaptive versus uniform resource grids;
6. certificate-size scaling;
7. and failure or resource-limit cases for every method.

Without this, the theorem is validated, but the algorithm is not convincingly evaluated.

---

# 6. R53 safe screening is rigorous but too limited to carry a separate contribution claim

## 6.1 The theorem is only for non-anchor commands

The rule applies to \(z>\min\{B,\min_j b_j\}\), so \(z\) cannot be the first selected command. It does not screen possible anchors.

This matters. Fine catalogs often proliferate low commands precisely in the region where anchors are feasible. The screening theorem does not control that part of catalog growth.

The manuscript should state the limitation prominently and investigate complementary safe rules for anchors.

## 6.2 The envelope is intentionally conservative

The bound uses the minimum catalog command as a universal predecessor and the full individual target box up to each cap. It ignores:

- the accepted aggregate promise except for the anchor test;
- incumbent information;
- dual prices;
- the command budget;
- and other selected commands.

This makes the rule easy to compute and stable under deletion order, but potentially very loose. There is no guarantee that it screens a nontrivial fraction of candidates or yields an asymptotic improvement.

## 6.3 The controlled experiment is engineered to be easy

The twelve controlled cases use:

- caps equal to \(1/4\) for every history;
- promise \(1/8\);
- a base catalog already containing \(0\) and \(1/4\);
- inserted commands strictly above \(1/2\);
- inserted-command charge \(1/2\);
- command budget 2;
- and requested absolute width \(1/10\).

The exact winning book is always \((0,1/4)\). The inserted commands are economically and geometrically unattractive. The experiment also removes the zero-charge command 1 because it is ineligible for every history.

This is a good regression test. It is not a persuasive screening benchmark.

The transferred resource interval is \([15/64,91/320]\), with width \(1/20=0.05\). Relative to the exact value \(15/64\approx0.2344\), the certificate width is about 21%. Exact equality is known only from exhaustive enumeration, not from the transferred interval.

## 6.4 The random regression is correctness evidence, not performance evidence

The 120 random models have at most six histories, eight candidates, and budget four. They remove 149 commands in total and preserve every exhaustive optimum. This is useful implementation evidence.

The study does not report:

- the distribution of screening rates;
- how close charges are to the exclusion threshold;
- how many truly irrelevant candidates are missed;
- comparison with leave-one-out exact relevance;
- comparison with LP/MIP presolve or reduced-cost fixing;
- or end-to-end break-even points.

## 6.5 Transfer certificates can cost more than full certificates

The manuscript openly reports that a transferred certificate can exceed the unscreened certificate on small cases because it stores the original instance and exclusion witnesses. This is honest and important.

It also means the screening result should be presented as a correctness-preserving preprocessing option, not as a general certificate-compression result.

## 6.6 Needed screening evidence

The authors should test:

- charges just below, equal to, and just above \(G(z)\);
- commands that are genuinely useful in neighboring instances;
- mixed retained and deleted insertions;
- nonuniform caps and promises;
- larger budgets;
- low-level possible anchors;
- multiple sequential refinements;
- and catalogs where only a small subset is safely removable.

The paper should compare the new rule with stronger problem-dependent baselines and report how often each rule removes candidates.

---

# 7. Novelty and positioning need sharper boundaries

The manuscript appropriately credits:

- separable convex resource allocation;
- constrained-shortest-path discretization;
- totally monotone matrix search;
- ordered quantization;
- and adjacent mean-preserving randomization.

After those ingredients are removed, the distinct contribution is the selected-boundary decomposition and its capacity identity.

I agree that this contribution is not merely a relabeling of a standard constrained shortest path. The original histories, eligibility ceilings, terminal chords, and service tails must be shown to aggregate exactly along a selected path.

However, the novelty discussion should compare more directly with the closest formulations in:

- concave resource allocation on paths;
- resource-constrained shortest paths with separable arc returns;
- ordered menu or facility selection with a global resource equality;
- scalar quantizer design with opening charges;
- and preprocessing or dominance rules for path and mixed-integer models.

The current discussion lists classical tools but does not isolate the nearest theorem-level antecedent to the selected-boundary identity.

The screening result is also positioned mostly against one crude bound \(f(1)-v_0\). A top-journal contribution requires comparison with stronger safe-screening and presolve ideas, not only with an intentionally gross benchmark.

---

# 8. Generality is narrower than the narrative suggests

The structural reduction depends critically on:

1. a common increasing concave terminal reward across histories;
2. one scalar aggregate equality;
3. prefix eligibility in a common ordered catalog;
4. separable convex intermediate costs;
5. additive command-opening charges;
6. and pre-draw intermediate service.

The paper acknowledges some of these limits, but their consequences deserve more emphasis.

History-dependent terminal rewards can destroy the common order of chord slopes. A second aggregate resource can destroy scalar repair. Nonadditive certification costs can destroy path separability. Nonprefix feasibility can destroy the exit-set partition.

The compatible-production model does not independently validate generality. It assumes a capacity-conservative path and parallel divisible resource assignment precisely so that the same repair theorem applies. It is a mathematical restatement of the abstraction, not a demonstrated second operational domain.

A broader methodological paper should either:

- prove extensions to multiple resources or heterogeneous rewards;
- derive the structure in another substantive OR model;
- or narrow the claims to the renewal architecture actually solved.

---

# 9. Operational relevance remains unestablished

All experiments are synthetic. The manuscript does not estimate:

- history probabilities;
- participation caps;
- realization ceilings;
- intermediate-service costs;
- command charges;
- or the value of a requested certificate tolerance.

The paper correctly states that the terminal alphabet is not total implementation memory. Target tables, encoder logic, probability precision, and certificates can dominate storage.

This honesty is a strength. It also means the publication case is almost entirely methodological.

For *Operations Research*, the authors should either provide a defensible application or strengthen the pure optimization theory. At present there is no evidence that the specific renewal mechanism captures a decision problem of broad practical importance, and the generic production example is uncalibrated.

---

# 10. Required changes for a credible resubmission

I would not recommend another revision that simply adds more regressions or another safe bound. The following changes would materially alter the publication case.

## 10.1 Establish the complexity frontier

Prove hardness or give a stronger exact algorithm. Identify meaningful parameters such as command budget, number of selected exit sets, distinct caps, or number of service-cost regimes.

## 10.2 Strengthen the central proof

Give a fully constructive, history-level proof of the selected-boundary identity, including the nested terminal-layer allocation and the converse implementation of an arbitrary rearranged resource vector.

## 10.3 Improve or justify the approximation mechanism

Provide an adaptive resource grid, an instance-dependent error bound, or a lower bound showing that the current \(1/\varepsilon\) dependence is unavoidable. Clarify the scale interpretation of additive accuracy.

## 10.4 Evaluate the general algorithm at meaningful scale

Vary \(N\), \(m\), \(k\), and ε systematically. Compare under matched time and memory with direct MIP, enumeration, and subdivision. Include cases where at least one baseline fails.

## 10.5 Rework the screening section

Treat screening as secondary unless it is shown to remove difficult candidates in non-engineered instances. Add anchor-screening ideas, stronger baselines, near-threshold tests, and removal-rate diagnostics.

## 10.6 Decide between theory and application

A pure theory paper needs the complexity and generality advances above. An applied paper needs a calibrated setting and decision consequences. The current manuscript sits between those positions.

## 10.7 Sharpen contribution claims

Make explicit that:

- the exact path identity is general under the declared convex assumptions;
- the implemented polynomial additive algorithm is for rational quadratic primitives;
- the guarantee is finite-catalog and additive;
- and safe screening is sufficient, non-anchor, and potentially conservative.

---

# 11. Minor and presentation comments

1. The abstract should state the asymptotic dependence on \(N\), \(m\), and normalized accuracy, not merely “polynomial.”

2. The selected-boundary theorem should include a short constructive reconstruction algorithm in its statement or immediately after its proof.

3. The capacity potential is a proposition-level clarification; do not let it appear as an independent major contribution comparable to the path identity.

4. In the complexity theorem, substitute \(Q=\Theta(Lm/\varepsilon)\) once so readers can see the effective dependence on \(m\) and \(N\).

5. Distinguish arithmetic complexity from bit complexity and from measured Python time in every table discussion.

6. The direct MIP table should report the time allowance and actual solver times in separate columns. “Allowance” currently refers to envelope approximation, which is easy to misread.

7. Report exhaustive-enumeration times alongside MIP and resource times on every fine case.

8. Add time-to-gap plots or tables for the resource method. One final tolerance conceals its anytime behavior.

9. The R53 screening table should include the transferred interval width and its ratio to the exact reference.

10. Separate removals that are wholly ineligible and zero-charge from removals where the new envelope performs substantive economic screening.

11. Report \(G(z)\), ρ(z), and their slack for every controlled inserted command.

12. The claim that the envelope is sharp should state the needed budget and feasibility conditions for the two-command comparison.

13. The independent screening checker has intentionally redundant context enumeration. Give its formal worst-case complexity.

14. State prominently that possible anchors are outside Theorem “Anchor-envelope screening.”

15. The phrase “refinement-safe” should always be tied to certified deletion. Arbitrary free refinement is not covered.

16. The random screening regression should report medians and quantiles of the fraction of commands removed.

17. Positive-width resource certificates should continue to be distinguished from exact optima, even when an external exhaustive reference equals the returned lower policy.

18. Keep the explicit requirement that exact bit-complexity claims use rationally encoded charges.

19. The production-module section would be stronger with one nontrivial numerical example that is not just a renamed renewal instance.

20. Repository preservation and source hashes are useful reproducibility features, but they should remain outside the scientific contribution summary.

---

# 12. Recommendation

**Reject in the present form.**

R53/R52 contains the strongest scientific contribution in this repository sequence. The selected-boundary identity appears to be a genuine structural result, and the capacity-repair argument gives a legitimate original-budget additive certificate without an eligibility-dependent exponent. The current article is also much better focused and formatted than its predecessors.

Those strengths warrant further work rather than dismissal of the research direction.

They do not yet support acceptance at *Operations Research*. The manuscript lacks a complexity classification for the exact problem; the approximation step after the reduction is classical and uniform; the general algorithm is validated only on very small cases and is dramatically slower than the reported numerical alternatives; the screening theorem is conservative and demonstrated on an engineered coarse-tolerance family; and no operational application establishes independent importance.

A focused resubmission centered on the selected-boundary decomposition could become competitive if it adds the missing complexity theory, gives a more complete constructive proof, demonstrates the arbitrary-eligibility algorithm at meaningful scale, and either deepens the operational setting or broadens the mathematical class. R53 is a credible foundation for that paper, but it is not yet the finished paper.