# Confidential Referee Report for Operations Research

**Manuscript:** *Limited-Memory Renewal Contracts: Budgeted Compression and Certified Joint Design*  
**Revision reviewed:** `revision/ndu-operations-research-r45-budgeted-compression-20260924`  
**Revision tip reviewed:** `9c52e2d58d69a8d653c3b50e2c860b35db04dc7f`  
**Immediate scientific predecessor:** R44, tip `fe066aac2862fc89fc8eb2e19fd98b4b96e6d5a3`  
**Predecessor independent report:** `reviews/operation_research_referee_report_r44_independent_harsh_2026-09-24.md`, commit `91583abe77208ec4ed25b5fbc5a15f89d54fcd6f`  
**Review branch:** `review/operation-research-r45-independent-harsh-20260925`  
**Date:** September 25, 2026  
**Recommendation:** **Reject in the present form. R45 genuinely repairs the most important conceptual defect of R44 by supplying an original-budget additive guarantee, and I do not see an immediate correctness failure in the new fixed-target dynamic program or target-net proof. However, the guarantee is obtained by a direct exhaustive Lipschitz grid in a target space of dimension \(k-1\), with catastrophic dependence on branch count and accuracy; the only scalable computations optimize the alphabet conditional on preselected targets rather than solve the joint problem. The fixed-target recurrence is a modest extension of the manuscript's already existing saturated catalog recurrence and of classical interval dynamic programming. The empirical section tests the provable global scheme only on tiny, coarse instances, while the favorable large-instance results concern heuristics or conditional optimization. In novelty, scalability, application evidence, and contribution relative to length, the paper remains below the standard of Operations Research.**

---

## Executive assessment

R45 is a serious revision. It does not evade the R44 criticism by merely renaming the doubled-memory union construction. It adds two mathematically substantive pieces:

1. an exact path dynamic program for choosing a finite catalog book at every cardinality when branch targets are fixed; and
2. a same-budget additive scheme that enumerates a feasible net of branch targets and invokes that conditional dynamic program.

At saturation, where all branch targets are forced to their caps, the conditional recurrence is a global polynomial catalog algorithm. At an interior promise, the target net keeps the original alphabet budget, arbitrary nonnegative level charges, the exact aggregate promise, and branchwise realization ceilings. This is the right direction and directly answers the principal problem-fidelity objection in my R44 report.

I audited the new theorem statements and proofs, the exact-rational implementations, the target-repair routine, the inexact-support theorem, the direct mixed-integer formulation, and the new numerical summaries. I do not presently see a counterexample to the target-crossing decomposition, the target-net coverage proof, the Jensen upper bound, or the algebra of the inexact-support certificate. My recommendation is therefore not based on manufacturing a theorem error.

The remaining problem is that the new global result is the most direct possible fixed-dimensional gridding argument. Its profile count is

\[
N\left(1+\frac{2L(k-1)}{\varepsilon}\right)^{k-1},
\]

and every profile invokes an \(O((k+m)N^2)\) conditional dynamic program. This is an exponential dependence on the number of branches and a high-degree dependence on the requested absolute accuracy. The theorem is meaningful only when \(k\) is very small. The operational motivation, however, begins with many distinguishable histories and the computational section advertises instances with 32, 128, and 256 branches. Those larger experiments do **not** run the global target-net algorithm. They optimize a book only at capped ideal targets and report a Jensen certificate.

The numerical evidence for the actual global scheme consists of two- and three-branch, two-symbol, five-candidate instances with very coarse tolerances. The favorable “35 of 36” and “36 of 36 with safeguard” statements refer to a finite target-portfolio heuristic and a greedy fallback, not to the proved target-net algorithm. The manuscript labels that distinction, which is commendable, but once the distinction is respected the evidence for a useful joint algorithm is thin.

R45 is therefore mathematically more coherent than R44, but it still does not make a sufficiently strong optimization contribution for *Operations Research*. The paper now has a correct conditional segmentation algorithm, a generic low-dimensional net, several local bounds, and extensive exact-arithmetic validation. It does not yet have a compelling complexity theory, a scalable joint algorithm, or an operational application that would justify a model-specific accumulation of results across a 32-page article and a 33-page companion.

---

# 1. Version audit and genuine progress over R44

The reviewed branch is rooted in the R44 review commit rather than an earlier manuscript. The current build reports 34 main-paper pages, 32 nonreference pages, a 33-page electronic companion, a six-page response, 176 abstract words, no unresolved references, no duplicate labels, and no overfull boxes. The repository preserves the prior theorem chain and numerical evidence while reorganizing the current readers.

The following changes are genuine improvements.

1. **Original-budget approximation is now addressed.** The target-net theorem returns a book with at most \(m\) levels, rather than using a \(2m\)-level union as the primary answer.

2. **Charges are optimized inside the same-budget conditional problem.** The new recurrence can discard expensive levels rather than paying an uncontrolled union charge after recovery.

3. **The distinction between conditional and joint optimality is explicit.** The manuscript repeatedly states that a globally optimal book for supplied targets need not solve the endogenous-target problem.

4. **The exact-price monotonicity argument is now written explicitly.** The revision correctly does not extend it to arbitrary approximate optimizers.

5. **The numerical validation is broader.** There is a separate uneliminated mixed-integer formulation, direct support enumeration, small exact joint comparisons, repeated conditional timing runs, and an explicit charged failure of the core target portfolio.

6. **The article is shorter and better organized than R44.** The original-budget results appear before the older augmentation theory, and several inherited results have moved to appendices or the companion.

These revisions materially improve the paper. They also sharpen the remaining editorial question: are the new original-budget results methodologically deep and computationally useful enough for a flagship OR journal? My answer remains no.

---

# 2. Mathematical audit of the new results

## 2.1 Conditional memory--charge frontier

For fixed targets \(t_j\), consecutive selected levels \(u<v\) partition branches with \(u\le t_j<v\). If \(v\le\tau_j\), the canonical response is the chord of \(f\) at \(t_j\). If \(v>\tau_j\), then every later level is also ineligible and branch \(j\) uses \(u\) plus fixed pre-draw service \(t_j-u\). Branches above the final level contribute the corresponding singleton tail.

This gives an additive path objective. The recurrence over increasing catalog indices pays each selected charge once and computes every exact cardinality. I find this decomposition correct under the manuscript's canonical-allocation theorem. It also correctly permits empty branch intervals and unused zero-charge levels when an exact-cardinality frontier is requested.

The result is useful as a conditional oracle. It is not, by itself, a solution of joint design away from saturation.

## 2.2 Saturated corollary

At \(B=\bar b\), positive branch weights and \(t_j\le b_j\) force \(t_j=b_j\) for every branch. The conditional recurrence therefore becomes a global catalog algorithm. This corollary is correct.

Its novelty should not be overstated. The preceding R42 material already contained a “Global catalog frontier with level-dependent charges” based on the same ordered-path partition at saturation, with complexity \(O(kN^2+mN^2)\). R45 generalizes the edge formula from forced caps to supplied targets and permits heterogeneous realization ceilings, but the saturated polynomial result is largely inherited rather than a new response to R44.

## 2.3 Target sensitivity and exact repair

For a fixed book, the piecewise-affine reward segment has slopes bounded by \(L_f\), and the shortfall tail has slopes bounded by \(L_{h,j}\). The response is therefore Lipschitz. The bounded-transfer repair changes all coordinates in the same direction until the weighted root equality holds, so its weighted \(L^1\) cost equals the aggregate residual. This lemma is correct.

## 2.4 Same-budget target net

The coverage argument also appears correct. For the anchor \(a=c_1^*\) of a global optimum, the proof rounds down \(k-1\) weighted target coordinates. Their total decrease is less than \((k-1)\eta\). The remaining coordinate and bounded increases restore the exact root promise. The final weighted distance from the optimal target vector is at most \(2(k-1)\eta\). The same optimal book remains feasible because every repaired target stays between its lowest level and its cap. The Lipschitz loss is therefore at most ε.

This is a valid original-budget additive scheme for a **finite catalog and fixed \(k\)**. It is also a straightforward ε-net argument once the conditional oracle is available.

## 2.5 Jensen and local certificates

The ideal capped target vector maximizes the Jensen upper objective ∑_j π_j f(t_j) subject to the root equality and caps. Every nonempty feasible book pays at least the minimum feasible anchor charge, so \(W_0-\rho_*\) is a valid upper bound. The reported conditional policy is a valid lower bound. The local interpolation inequalities and the first- and second-order comparison-book bounds are also standard and appear correct under their stated catalog, charge, and headroom assumptions.

These are certificates, not scalable joint optimization results. Their practical strength is entirely instance dependent.

## 2.6 Inexact-support theorem

The decomposition of loss into endpoint oracle defects, price-bracket error, target perturbation, and optimized compression penalty is algebraically sound. It improves on R44's uncontrolled union charge by optimizing the distortion--charge tradeoff at the returned budget.

However, it remains conditional on certified endpoint upper bounds and a feasible target bracket. The compression term \(Γ_s\) is not uniformly controlled and can absorb essentially all of the desired guarantee. The theorem is an accounting identity with a feasible recovery construction, not a general approximation theorem for practical inexact solvers.

## 2.7 Independent mixed-integer formulation

The direct formulation with activation binaries, support binaries, branch probabilities, pre-draw service, the root equality, target caps, and supportwise realization implications represents the original finite-catalog feasible set. The big-\(M\) value is valid given \(0\le y_j\le b_j\). Tangent and secant envelopes give the advertised quadratic-cost brackets. I see no immediate formulation error.

This is useful validation. Because the solver and bounds are floating point, it is appropriately described as numerical rather than an exact independent certificate.

---

# 3. Principal blocker: the global theorem is brute-force fixed-dimensional gridding

The target-net theorem is the only unconditional joint-design guarantee at an interior promise and the original memory budget. Its worst-case profile count is

\[
N\left(1+\frac{2L(k-1)}{\varepsilon}\right)^{k-1}.
\]

This is not a small technical qualification. It defines the practical scope of the result.

For illustration, using the paper's normalized quadratic scale \(L=2\):

- with \(k=3\) and ε=0.01, the factor per anchor is \(801^2=641{,}601\); with \(N=65\), the theorem allows 41,704,065 conditional optimizations;
- with \(k=5\) and the same ε, the factor per anchor is \(1601^4=6{,}569{,}999{,}366{,}401\), before multiplying by \(N\).

Each profile then runs an \(O((k+m)N^2)\) dynamic program. These are worst-case counts, but the manuscript offers no structural pruning theorem or empirical evidence that the guaranteed algorithm avoids them.

The dependence on \(L/\varepsilon\) is also numerical rather than strongly polynomial in the encoded data. Because the guarantee is additive, its meaning changes with objective scaling. A tolerance such as 1/4 may be large relative to the achievable net value, especially with opening charges.

The paper candidly states that \(k\) is fixed. That candor does not make the theorem a strong answer to the original OR problem. Fixed-dimensional gridding is a generic mechanism. The model-specific contribution is the conditional oracle and exact repair, not the global search principle.

A flagship optimization contribution should do substantially more than insert a polynomial subroutine into a rectangular net. At minimum I would expect one of the following:

- a hardness result showing that exponential dependence on \(k\) is unavoidable;
- a fixed-parameter algorithm with a meaningful parameter other than raw branch count;
- an adaptive target-space decomposition with certified pruning;
- a dual or convex-analytic method that exploits response concavity across books;
- a scheme parameterized by the number of distinct branch types, caps, or eligibility regimes;
- or a provable approximation with variable \(k\).

R45 provides none of these. Consequently, the main theorem is correct but algorithmically elementary.

---

# 4. The conditional dynamic program is useful but not a sufficiently novel centerpiece

The target-crossing edge is model specific: eligibility determines whether an interval contributes a lottery chord or a pre-draw shortfall tail. That is a clean reduction.

After this reduction, the optimization is classical interval/path dynamic programming. The manuscript itself acknowledges that the path recurrence and target net are established mechanisms. Moreover, the saturated version of this recurrence was already present in the manuscript pipeline before R45.

The extension from fixed cap targets to arbitrary supplied targets is natural and worthwhile, but limited:

- it does not optimize the targets;
- it does not exploit interactions among nearby target vectors;
- it does not produce nested optimal books across budgets;
- it does not establish Monge or total-monotonicity structure for the general conditional costs;
- and it does not reduce the \(N^2\) edge complexity.

Calling the result an “exact budgeted compression theorem” is defensible, but the optimization advance is modest. It is best viewed as a useful oracle lemma, not a stand-alone OR contribution sufficient to support the whole manuscript.

---

# 5. R45 still has no scalable guaranteed joint algorithm

The paper now has three different computational objects, and they must not be conflated.

1. **Conditional frontier:** polynomial and scalable, but targets are supplied.
2. **Completed target net:** globally valid at the original budget, but useful only for very small \(k\) and coarse ε.
3. **Finite target portfolio plus alternating improvement and greedy safeguard:** computationally cheap, but heuristic.

The large experiments with 32, 128, and 256 branches exercise only the first object at capped ideal targets. Their reported “Gap” is the Jensen upper bound minus the conditional policy at those targets. It is not an error to the unknown joint optimum and does not show that the target choice is good.

The favorable 35-of-36 core result and 36-of-36 safeguarded result concern the third object on small synthetic instances. There is no theorem for either the three-profile portfolio, the twelve-step alternating improvement, or the greedy fallback. The one retained charged failure already establishes that the portfolio is not generally exact.

Thus the revision has not demonstrated a scalable method for the joint problem it advertises. It has a scalable conditional optimizer and a non-scalable guaranteed outer enumeration.

---

# 6. The experiments do not meaningfully test the proved global scheme

## 6.1 Target-net tests are tiny and use coarse tolerances

The completed-net experiments use only:

- two or three branches;
- a five-point catalog;
- a two-symbol budget;
- four seeds;
- ε in {1/4, 1/8, 1/16} for two branches and {1/2, 1/4} for three branches.

The total evaluated profile counts are small. These tests establish that the implementation satisfies a loose bound on toy instances. They do not demonstrate computational viability at a journal-relevant accuracy or branch count.

No table reports target-net runtime as a function of \(k\), \(N\), and ε. No experiment approaches the regime in which the theorem's profile bound becomes difficult. No comparison is made with exhaustive book search, prefix branch-and-bound, generic global optimization, or adaptive target refinement at the same certified tolerance.

## 6.2 The 35/36 headline is about a heuristic selected after extensive model knowledge

The core portfolio contains:

- capped ideal targets;
- the two-price mixed targets;
- and the previous original-budget incumbent's targets.

It then performs alternating exact allocation and conditional book optimization. The safeguarded recommendation takes the better of this portfolio and a greedy-add policy. This is a reasonable heuristic ensemble, but it is tailored to the manuscript's own preceding algorithms and incumbents.

The sample contains only 36 instances with three or four branches, seven or nine catalog levels, and budgets two or three. Reporting “Safe exact 36” in the main table risks creating a stronger impression than the text permits. There is no reason to expect the safeguard to remain exact outside this small designed sample.

A stronger study would use a much larger preregistered distribution, hold out instance families, report failure rates rather than only aggregate exactness, and compare with independent optimization methods under matched time limits.

## 6.3 The large-scale study is conditional only

The 32- to 256-branch timings confirm the \(N^2\) conditional dynamic program. They do not test global target selection. Repeating the same instance three times characterizes implementation variability, not algorithmic robustness across inputs.

## 6.4 Independent MIP checks remain small validation exercises

The 24 MIP comparisons use selected small instances and two budgets. They verify that exact catalog values fall within floating-point envelope brackets. This is welcome, but it does not establish scalability, competitiveness, or the quality of the target-net or heuristic target selection.

The main paper should report MIP runtimes, bracket widths, node counts, and failure/time-limit behavior, not only successful containment.

## 6.5 Adaptive continuous examples are partly constructed to succeed

In the interior two-branch “target-adaptive” example, the candidate pool explicitly contains the ideal target values. Under the paper's own proposition, if the distinct ideal targets are available and fit within the symbol budget, the Jensen upper bound is attained. Exact recovery in that row is therefore a designed sanity check, not evidence for the midpoint adaptive heuristic.

The saturated adaptive examples are more informative, but still provide only a few hand-selected regimes and no universal candidate-generation result.

---

# 7. The local certificates are valid but often too weak to carry the paper

The Jensen certificate is useful because it produces a valid same-budget interval without solving target selection. Its gap combines at least three effects:

- intrinsic limited-memory distortion;
- loss from fixing capped ideal targets;
- and selected-level charges.

A large gap therefore does not diagnose which part of the design is deficient. In the scaling table, charged gaps are around 0.024 to 0.042 and uncharged gaps around 0.004 to 0.019. Without exact or stronger upper references, these intervals may be too wide for decision support.

The uniform comparison-book rates are also restrictive:

- the catalog must contain the full \(m\)-point uniform book;
- the clean first- and second-order statements are uncharged;
- the quadratic rate needs realization headroom at least one grid step;
- the charged extension adds \(R(G)-\rho_*\), which may dominate the bound.

The local chord inequality is standard interpolation analysis. It becomes useful only after a relevant candidate pool has already been identified. The manuscript provides no guaranteed adaptive candidate-generation method.

These results are legitimate secondary tools. They are not substitutes for a strong joint optimization theorem.

---

# 8. The inexact-oracle theorem is less practical than its title suggests

The theorem allows suboptimal endpoint policies only when each comes with a **certified global price upper bound** \(u_i\ge D(\lambda_i)\). This is a demanding object. A generic heuristic price solver usually supplies a feasible lower value, not a certified global upper bound for the maximization problem.

The theorem also assumes that the supplied endpoint totals already form a feasible bracket. Approximate optimizers need not preserve monotonicity, so the manuscript correctly refuses to give a call-complexity result. But this leaves the user responsible for finding the bracket and the certified defects.

Finally, the optimized compression penalty Γ_s can be large. The theorem computes and reports it, but does not bound it in terms of the original optimum, memory budget, catalog geometry, or opening-charge scale.

Accordingly, the theorem is best described as a robust certificate-composition result conditional on strong oracle outputs. It is not yet an algorithmic theory of practical inexact optimization.

---

# 9. Missing complexity classification

The paper repeatedly encounters exponential behavior:

- exponential stationary-face enumeration for continuous quadratic design;
- exponential prefix search for exact catalog design with endogenous targets;
- exponential-in-\(k\) target-net enumeration;
- and heuristic target selection at large \(k\).

Yet it gives no hardness result or parameterized-complexity map for the joint finite-catalog problem.

This omission now matters more than in R44. Once the authors present the target net as the principal same-budget answer, the natural question is whether the curse of dimensionality is intrinsic or merely an artifact of the most naive outer discretization.

The manuscript should determine, for example:

- whether the joint catalog problem is NP-hard with variable \(k\) and small \(m\);
- whether hardness persists with zero charges or common ceilings;
- whether the number of distinct caps or branch types is a useful parameter;
- whether repeated homogeneous branches can be aggregated before the net;
- whether fixed \(m\), fixed number of cap values, or fixed number of eligibility thresholds yields stronger algorithms;
- and whether an additive approximation with variable \(k\) is possible.

Without such results, the paper does not explain why its low-dimensional grid is the right complexity frontier.

---

# 10. Operational relevance remains insufficient

The manuscript is honest that all data are synthetic and that opening charges are supplied rather than estimated. That honesty is preferable to fabricated calibration.

It also leaves the paper without an independent application case.

The model begins with a planner who distinguishes many histories but communicates through a small command alphabet. The only globally guaranteed original-budget algorithm away from saturation requires the number of branches to be fixed and very small. The manuscript does not show that a realistic history space collapses to two or three homogeneous branch types.

The paper also equates an alphabet of \(m\) terminal commands with \(\lceil\log_2 m\rceil\) writable bits while treating read-only constants and public-state storage separately. This is a modeling convention, not a full memory accounting. The encoder, target table, branch-specific policies, certification metadata, and probability representation may dominate the physical implementation cost.

No operational evidence establishes:

- realistic caps, weights, shortfall curvatures, or realization limits;
- how level-opening charges are estimated;
- whether target-net accuracy at the reported scale affects decisions;
- or whether the proposed interface is implementable in the motivating setting.

A stylized model can certainly be publishable in *Operations Research*, but then the optimization theory must be correspondingly stronger. R45 does not yet meet that burden.

---

# 11. Contribution relative to length remains unfavorable

R45 reduces the main paper from 39 to 32 nonreference pages, which is progress. The complete package is still 65 pages before the response and preserved predecessor readers.

The article continues to carry or reference:

- canonical contractual allocation;
- deterministic and randomized institutional comparisons;
- saturated continuous design and Monge acceleration;
- exact continuous quadratic stationary-face search;
- finite-catalog mesh transport;
- price decomposition and prefix search;
- union augmentation;
- fixed-target compression;
- target nets;
- Jensen and interpolation certificates;
- inexact support recovery;
- heuristic portfolios;
- mixed-integer validation;
- and several distinct computational studies.

This breadth obscures the paper's strongest result and makes it difficult to assess novelty cleanly. The new centerpiece is not strong enough to justify an encyclopedic cumulative manuscript.

A focused paper on the conditional target-crossing oracle and a genuinely new joint algorithm could be effective. A separate paper could treat the institutional and continuous-design theory. The current package still reads as a sequence of revisions accumulated into one submission.

---

# 12. Required changes for a credible new submission

I would not recommend another revision that merely adds more synthetic rows. A credible new submission should make a deeper methodological choice.

## 12.1 Establish the complexity frontier

Prove hardness or a meaningful parameterized algorithm for endogenous-target catalog design. Explain whether exponential dependence on branch count is necessary.

## 12.2 Replace the full target grid with a structural global method

Possible directions include certified adaptive partitioning of target space, decomposition over branch types, a convex-envelope formulation, branch-and-bound with conditional-DP bounds, or an FPT algorithm in the number of distinct caps/ceilings.

## 12.3 Demonstrate the guaranteed algorithm at nontrivial accuracy

Run completed nets for progressively smaller ε and increasing \(k\), report runtime and profile growth, and compare with exact search and generic solvers. If the method becomes unusable at \(k=4\) or \(5\), document that boundary prominently.

## 12.4 Separate theorem-backed algorithms from heuristic portfolios

The 35/36 and 36/36 results should not be the main empirical headline unless accompanied by a broad out-of-sample study and strong independent baselines. Report failures and distributions, not only exact-hit counts.

## 12.5 Strengthen independent comparisons

Use the direct MIP on a larger range, report runtimes and bracket widths, and compare the target-net, portfolio, greedy, prefix search, and exact reference under common limits.

## 12.6 Develop nontrivial certificates for large \(k\)

The Jensen bound should be tightened by target-sensitive dual information or decomposable upper bounds so that large-instance intervals are decision relevant.

## 12.7 Either calibrate an application or shorten the paper substantially

A concrete restricted-interface application could justify model-specific structure. Without one, the manuscript should be recast as a concise optimization paper and shed most inherited material.

---

# 13. Minor and implementation comments

1. The implementation of the \(k=1\) target-net case still loops over anchors and invokes conditional optimization repeatedly, whereas the theorem says one call at \(t_1=B\) suffices. This is not a correctness issue, but the code and theorem should match.

2. The target-repair regression test constructs a candidate already clipped to \([0,b_j]\) with lower anchor zero, then asserts that the clipping distance is zero. It does not actually test the clipping branch that appears in the inexact-support theorem.

3. There is no independent checker for **net coverage**. The same implementation declares completion, counts profiles, and returns the ε certificate. A separate combinatorial coverage audit would be valuable.

4. The main target-net table should report runtime, \(N\), \(m\), objective scale, and relative loss, not only profile counts and absolute loss.

5. The phrase “polynomial global catalog algorithm at saturation” should be identified as an inherited result/generalization, since the saturated charged-catalog recurrence already appeared in R42.

6. The title phrase “Certified Joint Design” is broader than the scalable theory. At large branch count the scalable computation is conditional and the joint methods are heuristic or interval based.

7. The abstract's “accuracy exponent is explicit” is true but euphemistic. It should say directly that the algorithm is exponential in the number of branches.

8. The “Safe exact” column in the main table should be renamed “Safeguarded exact in sample” to avoid implying a safe algorithmic guarantee.

9. Report the charged counterexample's objective scale as well as its absolute loss \(101/3600\).

10. The direct MIP table should include solver time, node count, primal--dual gap, envelope error, and bracket width for every case, including any timeouts.

11. The interior target-adaptive exact row should be described as an oracle candidate-pool sanity check because the exact ideal targets are inserted explicitly.

12. The conditional scaling table should not sit visually beside global-approximation evidence without a prominent “conditional targets fixed” marker in the column heading.

13. The target-net theorem is for a finite catalog. The abstract should not allow it to be read as an unrestricted continuous-design scheme at the original budget.

14. Add a theorem-level comparison table that distinguishes what was already proved in R42--R44 from what is genuinely new in R45.

15. The fixed-target exact-cardinality frontier may include unused zero-charge levels. State whether reported “used” cardinality counts selected levels or levels that receive positive probability on at least one branch.

16. The absolute additive guarantee is not scale invariant. State the normalization assumptions needed to interpret a requested ε.

17. The paper should report how repeated homogeneous branches are aggregated before applying the target net, since this is the most obvious way to reduce its dimension.

18. Preserve the current caution that numerical MIP bounds are not exact rational certificates. That distinction is appropriate.

---

# 14. Recommendation

**Reject in the present form.**

R45 is the strongest revision I have seen in this sequence. It directly answers the R44 resource-budget objection, supplies a credible fixed-target dynamic program, proves a valid same-budget additive scheme for fixed branch count, and improves the honesty and independence of the computational evidence. I do not reject it for an apparent theorem error.

I reject it because the resulting contribution remains too elementary and too narrow for *Operations Research*. The global same-budget theorem is exhaustive low-dimensional gridding; its dependence on \(k\) and ε is prohibitive, and the experiments do not test it beyond tiny coarse cases. The scalable results are conditional on target choices, while the successful joint computations are heuristics on small synthetic instances. The saturated dynamic program substantially overlaps an existing theorem in the manuscript's own prior revisions. Local certificates and numerical cross-checks improve reliability but do not create a major optimization advance.

The paper would become substantially more compelling with a real complexity classification and a structurally nontrivial algorithm for endogenous targets, or with a concrete operational application that makes the conditional oracle independently important. In the absence of either, the cumulative 65-page technical package does not meet the journal's threshold for novelty, breadth of impact, or contribution relative to length.