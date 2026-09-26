# Confidential Referee Report for Operations Research

**Manuscript:** *Exact Path Representations for Finite-Catalog Renewal Design*  
**Revision reviewed:** `revision/ndu-operations-research-r54-exact-price-path-20260926`  
**Revision tip reviewed:** `eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9`  
**Scientific parent:** R53, commit `2e07a4cfb41d8fbc16cd64c3048877d3c8c2a288`  
**Antecedent referee report:** `reviews/operation_research_referee_report_r53_independent_harsh_2026-09-26.md`, commit `fcd7b7ab1719f00e547cd29e94cbb421fab59b0a`  
**Review branch:** `review/operation-research-r54-independent-harsh-20260926`  
**Date:** September 26, 2026  
**Recommendation:** **Reject in the present form, while encouraging a focused resubmission. R54 is the strongest and most coherent version in this sequence. I do not see an immediate counterexample to the selected-boundary identity, the heterogeneous-reward packing theorem, the exact priced-path identity, the common-cap two-command result, or the stated SUBSET SUM reduction. The paper has therefore moved beyond the correctness and problem-fidelity objections that dominated earlier rounds. The remaining blockers are now significance and algorithmic completeness: the hardness result is weak and uses a nonbinding command budget, so it does not characterize the small-menu regime motivating the paper; the grid-free exact method is classical inclusion/exclusion branching equipped with a new node oracle but retains a full \(2^N\) worst-case tree; the polynomial fallback is computationally severe and its heterogeneous-reward extension is not implemented; the main study reports favorable rational intervals but provides too little evidence about node counts, pruning, scaling in accuracy and budget, or end-to-end benefit over exact enumeration and modern mixed-integer optimization; and no calibrated operational setting establishes that this highly structured renewal model has independent practical importance.**

---

## Executive assessment

R54 is a substantial scientific advance over R53. The authors have supplied several results that I explicitly requested in the prior report:

1. a direct complexity result rather than an inference from observed runtime;
2. a fully constructive selected-boundary proof;
3. a broader heterogeneous-reward extension;
4. an exact original-instance Lagrangian path oracle;
5. a finite exact branching algorithm with independently checkable intervals;
6. stronger matched-limit computational evidence;
7. and a much clearer separation between classical machinery and model-specific structure.

The manuscript is also now focused. The validated article has 25 nonreference pages and a 20-page companion, rather than the cumulative hundred-page package seen in earlier revisions. The title and abstract identify a finite-catalog theory paper rather than an application study.

The strongest theorem is still the selected-boundary representation. A selected book determines disjoint terminal layers and service exit sets. The aggregate capacity telescopes to the original obligation capacity. This is what permits both the scalar-resource formulation and the exact price decomposition. The new history-level component-packing argument plausibly extends the primal identity to heterogeneous increasing concave terminal rewards without imposing a common cross-history marginal ordering.

The exact priced-path theorem is also useful. At a fixed price, each history contributes positive terminal chord increments and one last-eligible service support. These pieces localize at selected boundaries, so one ordered path dynamic program maximizes the exact book-level Lagrangian support. The resulting bound is for the original finite-catalog problem, not for a target grid, enlarged command budget, or representative-history relaxation.

I audited the mathematical statements, proofs, exact-arithmetic implementation, independent checker, regression suite, protocols, generated tables, and the new hardness and screening experiments. I do not presently see a fatal theorem error. My recommendation is not based on manufacturing a correctness objection.

The question is now whether this body of work meets the methodological and impact threshold of *Operations Research*. I do not believe it does yet.

The NP-completeness theorem is a valid weak SUBSET SUM reduction, but it sets \(m=N=2n\). The command budget is therefore explicitly nonbinding. The reduction proves that paid activation and heterogeneous caps can encode a high-precision subset target; it does not explain the complexity of the small command alphabets that motivate the manuscript. For every fixed \(m\), direct book enumeration is polynomial in \(N\). The unresolved issue is the parameterized and encoding complexity as \(m\) varies, not simply whether a nonbinding-budget instance can encode SUBSET SUM.

The grid-free exact method is finite and certifying, but its discrete search is standard candidate inclusion/exclusion branching. Its worst-case cover has \(2^{N+1}-1\) nodes. The new contribution is the node oracle, not the branching principle. The paper does not yet show that this oracle creates a robust algorithmic advantage over exact book enumeration, mixed-integer optimization, or a carefully engineered dynamic program in the regimes of interest.

The evidence is mixed. Price paths produce 10 exact closures, 19 positive-width tolerance completions, and one limited run across the 30 principal cases. Certificates are compact and independently verified. On the six historical fine cases, however, exact enumeration takes only 0.017--0.023 seconds, numerical mixed-integer optimization 0.020--0.044 seconds, and price paths 0.006--0.154 seconds. The uniform fallback times out on almost every principal case. At 768 histories the price method hits the time limit and returns width 0.00252 against a requested 0.001. These results demonstrate correctness and some favorable instances, but not a compelling general solver.

The manuscript is therefore close to a publishable theory paper, but it still needs a sharper complexity boundary, a more informative exact-search evaluation, and either broader mathematical scope or an operational setting that makes the model-specific structure important.

---

# 1. Version audit and substantive progress

The audited tip is `eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9`. The build record reports:

- 26 total article pages and 25 nonreference pages;
- a 20-page electronic companion;
- a five-page response;
- a 189-word abstract;
- no undefined references or citations;
- no duplicate labels;
- and no overfull boxes.

The branch starts from the R53 review history and preserves prior material. The journal-facing manuscript is substantially reorganized and shortened.

R54 adds the following genuine contributions.

1. **Constructive selected-boundary recovery.** The nested-layer lemma and implementable-rearrangement lemma make the original history-level policy construction explicit.

2. **Common-cap exact tractability.** Under a common expected cap and common reward, some optimum uses at most two commands, despite heterogeneous realization ceilings and service costs.

3. **A direct NP-completeness reduction.** The rational decision problem is weakly NP-complete under unit linear reward, zero service cost, uniform weights, cap-equal ceilings, and a nonbinding command budget.

4. **Heterogeneous-reward extensions.** Both a primal history-level packing identity and an exact priced-path identity allow history-specific increasing concave rewards.

5. **A polynomial priced-book oracle.** For rational quadratic primitives, one price call takes \(O(kN^2+mN^2)\) arithmetic operations.

6. **Grid-free finite exact search.** Candidate inclusion/exclusion branching retains a valid original-space rational interval at interruption and terminates exactly when the discrete cover is completed.

7. **Anchor-capable safe fixing.** Forced-command price bounds complement the cheaper non-anchor envelope.

8. **Matched-limit studies and hard challenge cases.** The revision records successful and unsuccessful runs rather than presenting only favorable closures.

These additions directly answer much of the previous report. The current concerns are correspondingly narrower and more demanding.

---

# 2. Mathematical audit

## 2.1 Canonical response and terminal-first exchange

The canonical fixed-book response remains correct under the stated assumptions. The best terminal mean is the largest feasible one because the terminal interpolant is increasing and the service cost is nondecreasing. Adjacent eligible randomization implements the interpolation point, and a sure last eligible command plus pre-draw service implements the tail.

The global terminal-first exchange is also sound for a common reward. The weighted transfer is explicit and preserves the root equality. Moving target mass away from service and into unfinished terminal capacity weakly lowers service cost and strictly increases terminal reward.

## 2.2 Nested terminal layers and constructive recovery

The nested-layer lemma fills an important gap in R53. If a history contributes positive capacity to a selected edge \((u,v)\), it is eligible for all earlier selected commands. Its earlier terminal increments telescope to \(u-a\), so after prior layers are filled it is indeed at target \(u\). The greedy weighted allocation realizes every aggregate amount in the current layer.

After all terminal layers are full, each history has target \(\min(b_j,d_j)\), and its remaining service capacity belongs to exactly one exit set. The exit sets are disjoint. This yields a legitimate original policy with all realization ceilings intact.

The rearrangement lemma is stated carefully: an arbitrary feasible arc vector need not itself be implementable at exactly its original payoff, but it can be rearranged to an implementable vector with no smaller payoff. This is the comparison required to prove equality of optimal values.

I find the selected-boundary resource identity credible.

## 2.3 Heterogeneous-reward component packing

The heterogeneous extension is mathematically plausible and is stronger than a superficial replacement of one common chord slope by history-specific slopes.

The relaxation introduces bounded terminal components for every history and selected edge, plus one service component. Within each history, moving service into unfinished positive terminal capacity and moving later terminal mass into earlier, higher-slope segments weakly improves the objective while preserving that history's total target. At termination the components are in canonical order.

Regrouping the relaxed components by selected edge produces the concave within-edge terminal profile \(R_{uv}\) and the service cost \(H_{uv}\). The capacity identity is unchanged.

This proof depends critically on three properties that should remain prominent:

- every terminal reward is increasing, so terminal marginal returns are positive;
- each history's own chord slopes are nonincreasing;
- and there is only one aggregate resource equality.

The theorem does not extend automatically to nonmonotone rewards, multiple aggregate obligations, or nonprefix eligibility.

## 2.4 Common-cap two-command theorem

The three-case proof appears correct.

- If the book contains \(B\), the singleton \(\{B\}\) attains the Jensen upper bound and pays no more charge.
- If every selected command is below \(B\), all histories traverse the full terminal book to its top command and use service for the residual; deleting lower commands preserves the gross policy.
- If selected neighbors \(u<B<v\) bracket the promise, earlier layers are fully traversed. The pair \(\{u,v\}\) preserves the relevant partial layer. When \(v>b\), later commands cannot affect any target because every target is capped below \(v\).

The result is nontrivial because common caps do not imply common realization ceilings.

Its publication significance is less clear. It identifies a useful exact subclass, but it also emphasizes that heterogeneous expected caps are the source of the difficult combinatorics. The operational role and empirical plausibility of those heterogeneous caps therefore deserve more attention.

## 2.5 NP-completeness reduction

The SUBSET SUM reduction is internally consistent.

The free lower commands are ordered below the paid optional commands. Adding all free commands never hurts and remains within the nonbinding \(2n\)-command budget. Selecting optional commands of total integer weight \(s\) increases aggregate terminal capacity by \(s/K\) and incurs charge \(s/(2K)\). The exact optimized value is

\[
\zeta-rac{|s-W|}{2K}.
\]

Thus reaching \(\zeta\) is equivalent to exact subset sum. The rational encoding length is polynomial, and fixed-book verification supplies membership in NP.

This is a valid **weak** NP-completeness theorem. Its limitations are not cosmetic:

- the command budget is nonbinding;
- the reduction relies on paid activation;
- the separating value gap can be \(1/(2K)\), exponentially small in the bit length of the numerical total;
- it gives no strong NP-hardness;
- it gives no hardness at any fixed \(m\);
- and it gives no parameterized lower bound in \(m\).

The theorem therefore rules out a general exact polynomial algorithm, but it does not characterize the main small-menu regime.

## 2.6 Exact priced-path identity

The fixed-book price identity appears correct.

For a given history, subtracting a price selects exactly the positive terminal chord increments. Because the history's terminal slopes are positive and nonincreasing, this selection respects segment order. At a nonnegative price, service cannot improve the objective. At a negative price, all terminal increments are traversed before the concave service tail is optimized.

The terminal increments are owned by selected edges, and the one service support is owned by the history's exit edge or the terminal edge. Summing over histories yields an additive ordered-path value. No common ordering across histories is needed.

The restricted mandatory/forbidden path construction is also credible. Starting after the first mandatory vertex, crossing over a mandatory vertex, or terminating before the last mandatory vertex would omit it; disallowing those operations characterizes the required family.

## 2.7 Finite exact branching

The interval logic is correct. Each leaf represents a disjoint family of books. A completed price call supplies an upper bound for that family. A recovered book is allocated at the original promise and supplies a feasible lower policy. Splitting on an undecided command partitions the family exactly, and inherited upper bounds remain valid for both children.

When all candidates are decided, the family contains at most one book. Concavity of the fixed-book value supplies a supporting price at the accepted promise, so the leaf can be closed exactly. The worst-case binary cover is finite.

This theorem should not be overstated. The full tree contains up to \(2^{N+1}-1\) nodes. The exact finite termination is fundamentally complete subset branching. The methodological contribution is the strength and checkability of the price-path node bound, not the fact that exhaustive binary branching eventually terminates.

## 2.8 Forced-command exclusion

The strict forced-command rule is valid. If a price bound for all books containing \(z\) lies below a feasible incumbent, no optimum contains \(z\). Strictly excluded commands can be removed simultaneously.

The weak-inequality qualification is also correct: an independently retained incumbent avoiding the entire deletion set is needed.

The rule is a standard Lagrangian fixing inference instantiated through the new oracle. Its value should be judged by end-to-end computational benefit, not by removal percentage alone.

---

# 3. The complexity frontier remains incomplete

The paper now has a real complexity theorem, but calling the resulting picture a completed frontier is premature.

## 3.1 The hardness instance does not use the limited-menu constraint

The motivating resource is a small terminal alphabet. The reduction sets \(m=N=2n\). The menu-size constraint does no work. Hardness is generated by optional paid commands and a high-precision aggregate target.

This is mathematically legitimate, but it does not explain the complexity of limited-memory design when \(m\) is small. For every fixed \(m\), enumeration of \(O(N^m)\) books is polynomial.

The natural missing questions are:

- Is the problem W[1]-hard or W[2]-hard parameterized by \(m\)?
- Is there an \(f(m)\operatorname{poly}(N,k)\) exact algorithm?
- Is exact optimization fixed-parameter tractable in the number of distinct caps, exit sets, or selected eligibility classes?
- Does hardness persist under bounded or uniform opening charges?
- Can one prove strong NP-hardness under a more operationally stable normalization?
- Is there a pseudo-polynomial exact algorithm after rational scaling, consistent with the weak SUBSET SUM reduction?

Without this map, the role of the additive scheme remains uncertain.

## 3.2 The reduction is encoding-sensitive

The no-instance gap can be \(1/(2K)\). Distinguishing yes from no may require inverse accuracy proportional to the numerical SUBSET SUM total. This is exactly the type of weak hardness compatible with pseudo-polynomial methods.

The paper acknowledges this point, but it should do more than acknowledge it. Either derive a pseudo-polynomial exact algorithm for an appropriate integral encoding, or explain why the general rational instance prevents one.

## 3.3 The common-cap result and hardness theorem leave a wide gap

At one extreme, common caps imply a two-command optimum. At the other, arbitrary caps with nonbinding budget are weakly NP-complete. The practically important middle ground remains largely unclassified:

- a small number of distinct caps;
- ordered or clustered caps;
- bounded cap dispersion;
- fixed command budget;
- zero or uniform charges;
- common ceilings;
- and small numbers of selected exit sets.

A top journal paper should identify more of this structure.

---

# 4. The exact search is standard branching with a new oracle

The paper now cites the relevant Lagrangian path and problem-reduction literature, which is appropriate. Once the exact price oracle has been derived, however, the global exact procedure is conventional:

1. maintain an incumbent;
2. compute a Lagrangian upper bound;
3. branch on inclusion or exclusion of a candidate;
4. inherit or recompute bounds;
5. terminate when every leaf is closed or pruned.

This is not a criticism of correctness. It is a novelty and evaluation issue.

The manuscript must demonstrate what the new oracle changes relative to straightforward alternatives. The main tables currently report seconds, final width, certificate bytes, checking time, and memory, but omit the most informative search diagnostics:

- evaluated tree nodes;
- live leaves;
- price calls;
- root gap;
- percentage of the gap closed before branching;
- pruning caused by the incumbent;
- pruning caused by forced commands;
- average and maximum mandatory-set size;
- and comparison with direct book enumeration at the same explored-book count.

The raw records may contain some of these quantities, but they are load-bearing algorithmic evidence and belong in the article.

The four SUBSET SUM challenge cases confirm that the method can fail under the declared limits. This is useful. The table should report their exact node counts, oracle counts, incumbent gaps, and time-to-bound trajectories rather than only “Exact” or “Time limit.”

---

# 5. The polynomial fallback is theoretically useful but computationally severe

After substituting normalized accuracy \(\delta=arepsilon/L\), the stated arithmetic bound contains

\[
O\!\left(rac{kmN^2}{\delta}\log(k+1)+
rac{m^2N^3}{\delta}\log(m/\delta+2)ight).
\]

The cubic catalog dependence and quadratic budget dependence are substantial. The study confirms the issue: the inherited uniform grid reaches tolerance in only one of 26 applicable principal runs and hits a resource limit in the other 25.

This does not invalidate the guarantee. It does mean that the fallback currently functions as a worst-case existence theorem rather than a usable algorithm.

The heterogeneous-reward extension is theorem-only. The paper explicitly states that the inherited uniform implementation supports only common rewards. That honesty is welcome, but a headline heterogeneous polynomial guarantee should either be implemented and tested or moved out of the empirical narrative.

The authors should investigate whether the new price oracle can strengthen the polynomial fallback, for example through:

- adaptive resource discretization with certified error;
- state compression;
- scaling based on local marginal ranges;
- column or path generation;
- or a combined price/resource method with a formal complexity bound.

---

# 6. Computational evidence is improved but still insufficient

## 6.1 Principal study composition

The principal study has 30 cases and 142 applicable method runs. It is substantially better designed than earlier experiments. It includes unsuccessful cases, resource limits, heterogeneous rewards, and exact verification.

Nevertheless, much of it is a one-factor sweep around a single base instance. Repeated base points across history, catalog, budget, accuracy, and charge sweeps are paired comparisons, not a broad distribution of optimization instances.

A stronger evaluation should include multiple seeds or structured families for every scale setting.

## 6.2 The favorable large cases lack independent exact references

The price certificates themselves are valid upper and lower bounds, so exact references are not needed for correctness. They are still needed to evaluate tightness, incumbent quality, and comparative solver performance.

For larger catalogs and histories, the paper often knows only the returned interval. It does not show whether the lower policy is actually optimal, nearly optimal, or far from optimal inside that interval.

A numerical MIP incumbent, a longer-run solver, or a separate decomposition could provide comparative lower values even when exact proof is unavailable.

## 6.3 Small exact cases do not show a solver advantage

On the six historical fine cases:

- exact enumeration takes about 0.017--0.023 seconds;
- numerical MIP takes about 0.020--0.044 seconds;
- price paths take about 0.006--0.154 seconds.

The new method is competitive on some cases and slower on others. Its principal advantage is a compact exact rational proof, not speed. The article should say this even more directly.

The paper should also report exhaustive-enumeration time for all small principal cases, not only the historical six.

## 6.4 The 768-history case misses the requested tolerance

The largest history case reaches the time limit and returns width 0.00252 for a requested 0.001. This is a useful retained failure.

One such point does not characterize scaling. The study needs several large-history instances, longer budgets, and time-to-gap curves showing whether the method is approaching the requested width smoothly or stalling.

## 6.5 Catalog and budget sweeps are surprisingly nonmonotone

The 33- and 65-candidate cases finish faster than some smaller catalog cases, and budgets 4, 8, and 12 have similar times. This may be a legitimate consequence of data-dependent pruning, but it means the study is measuring one search trajectory, not asymptotic scaling.

Report node and oracle counts so readers can understand the nonmonotonicity.

## 6.6 Accuracy sweep is favorable but narrow

The \(10^{-4}\) and \(10^{-6}\) requests close exactly on the chosen base model, so their runtime is nearly identical. This demonstrates the potential benefit of exact price closure, but it does not measure difficult positive-width behavior as accuracy tightens.

Include cases where the tree does not close exactly and plot width versus time and requested tolerance.

## 6.7 Reduction challenge methods use different targets

On the SUBSET SUM challenges, price and enumeration request exact closure while grid and box methods request width \(1/(8K)\). The manuscript discloses this difference, but the combined outcome table still invites direct comparison.

Use separate panels or run a second matched-target experiment.

## 6.8 Four heterogeneous-reward cases are not enough

Only four principal cases use heterogeneous rewards, with at most 24 histories and 17 catalog points. The primal heterogeneous resource implementation is not exercised.

The broader theorem is potentially important and deserves a dedicated study varying reward dispersion, slope crossings, catalog size, and history count.

---

# 7. Screening evidence does not show end-to-end value

The forced price rule removes a median of 62.5% of the eight commands in the 24 screening cases and reaches possible anchors. This is stronger than the target-box envelope.

However:

- the median forced-bound calculation takes 0.0368 seconds;
- the median exact reference calculation takes 0.0241 seconds;
- the forced rule still misses strictly irrelevant commands in several families;
- some removals are wholly ineligible commands;
- and the study does not report the total time to screen and then solve the reduced problem versus solving the original problem directly.

Removal rates are not sufficient. The relevant metric is end-to-end proof time, memory, and certificate size.

The study should include harder instances where exact enumeration is unavailable and measure whether screening materially improves the price tree or resource grid.

The sharpness examples are useful but deliberately one-dimensional around the constructed threshold. They validate the inequality; they do not establish typical screening strength.

---

# 8. Operational and modeling significance remains weak

The manuscript is transparent that all inputs are synthetic. That is acceptable for a theory paper.

It places more burden on the theory to demonstrate broad relevance. The model still assumes:

- one aggregate accepted obligation;
- an ordered common command catalog;
- prefix eligibility induced by scalar realization ceilings;
- pre-draw intermediate service;
- additive level-opening charges;
- and history-separable rewards and costs.

These assumptions are exactly what make the path representation work. The paper needs a sharper argument that an important class of operational systems genuinely has this structure.

The compatible-production model shows mathematical reuse of the capacity-repair abstraction, but it remains another synthetic construction. Nine exact configurations are not operational validation.

The authors should either:

- provide a calibrated case study;
- identify a concrete system architecture and parameter-estimation procedure;
- or recast the paper more abstractly as a theorem about selected-boundary resource paths and show at least two genuinely independent model derivations.

---

# 9. Novelty positioning needs one more level of precision

The introduction now properly credits Lagrangian constrained-path methods, generic branching, separable resource allocation, discretization, and monotone matrix search.

The new claims should be isolated even more sharply:

1. the exact original-constraint selected-boundary resource identity;
2. the heterogeneous history-level packing theorem;
3. the exact priced-path identity with caps, service, and endogenous books;
4. the common-cap two-command theorem;
5. and the specific weak NP-completeness reduction.

The finite branching method, incumbent-based command fixing, and uniform resource gridding are applications of established mechanisms once the identities are available.

A theorem-by-theorem comparison with the nearest constrained shortest-path, quantizer-design, and charged segmentation formulations would improve the novelty case.

---

# 10. What is required for a credible resubmission

I would not recommend another revision consisting mainly of more prose or more seeded tests. The following changes are substantive.

## 10.1 Complete more of the complexity map

Provide at least one of:

- a parameterized-complexity result in \(m\);
- a strong NP-hardness theorem under a meaningful normalization;
- an exact pseudo-polynomial algorithm that matches the weak reduction;
- an FPT algorithm for a structural parameter such as distinct caps or exit sets;
- or a provable approximation result stronger than the current uniform additive grid.

The paper should explain the computational status of the small-menu regime, not only the nonbinding-budget regime.

## 10.2 Expose search mechanics in the main evidence

For every price-path case, report:

- node count;
- oracle calls;
- root price gap;
- final live leaves;
- incumbent updates;
- forced-command prunes;
- and book cardinality.

For the challenge cases, report complete trajectories.

## 10.3 Add meaningful matched comparisons

Use several time budgets, not only four seconds. Compare:

- exact enumeration;
- price branching;
- resource gridding;
- mixed-integer optimization;
- and any state-of-the-art constrained-path or segmentation baseline.

Separate exact proof time, optimization time, and numerical incumbent quality.

## 10.4 Implement the heterogeneous primal algorithm or narrow the claim

The heterogeneous resource theorem is a headline extension. Either implement and test its kernels or clearly present it as an unimplemented theoretical corollary.

## 10.5 Demonstrate end-to-end screening benefit

Measure solve-before versus screen-plus-solve on instances where the downstream solve is nontrivial. Report commands removed by category and the effect on node count, time, proof size, and gap.

## 10.6 Strengthen generality or operational relevance

A calibrated application would materially help. Otherwise provide a more abstract path theorem and a second independently motivated OR model whose assumptions and data are not chosen to mirror renewal design.

---

# 11. Minor and presentation comments

1. The abstract should say “weakly NP-complete via SUBSET SUM” rather than only “NP-complete,” because the encoding sensitivity is central.

2. State in the abstract that the hardness construction uses a nonbinding command budget.

3. The phrase “complexity frontier” is too strong until parameterized or strong complexity is addressed. “Initial complexity boundary” would be more accurate.

4. The common-cap theorem should state explicitly that the singleton \(\{B\}\) case requires \(B\) to be a catalog command; the proof already conditions on that event.

5. In the common-cap proof, emphasize that all selected commands below \(B\) are eligible because \(	au_j\ge b\ge B\).

6. The exact branching theorem should distinguish total nodes from completed price calls; a node can use multiple prices.

7. The universal upper bound should be described as gross terminal reward only, with nonnegative charges and service costs dropped.

8. Report the maximum rational price bit length in the price certificates.

9. Report tree depth as well as node count.

10. The certificate-size statement should specify whether bytes are compressed JSON and whether the original input is included.

11. The main scaling table should include nodes and oracle calls, even if this requires removing one less informative column.

12. The price-check time for the 768-history case is more than half a second; discuss checker scaling explicitly.

13. “Exact closure” should continue to mean zero rational width, not agreement with a numerical solver.

14. In the outcome table, separate exact-target and positive-tolerance experiments.

15. Add exact-reference objective values to the historical fine table so widths can be interpreted relative to scale.

16. The mixed-integer envelope rows with tiny negative numerical width should be labeled “roundoff reversal,” not displayed as a meaningful negative interval.

17. The production example should report what operational interpretation is assigned to its module return parameters, even if they are synthetic.

18. The screening table should separate possible anchors, wholly ineligible commands, and ordinary non-anchor commands in the main article rather than only the companion.

19. Report the downstream solve after screening; current screening-time comparisons are incomplete.

20. Keep the explicit statement that rational bit-complexity claims require rationally encoded charges and rewards.

21. The heterogeneous packing theorem assumes a common catalog and prefix eligibility; include those assumptions in the theorem statement itself.

22. The history-level component packing proof should mention compactness or finite-dimensional attainment for the within-edge profile.

23. In the price identity proof, state explicitly that \(K_j=0\) at nonnegative prices because \(h_j\ge0\) and \(y=0\) is feasible.

24. The fixed-book supporting price at boundary promises deserves a one-sentence one-sided-supergradient explanation.

25. The four-second limit is useful for a controlled comparison but should not be described as a general scalability threshold.

26. The one-factor sweeps should be labeled as sensitivity analysis, not as independent benchmark instances.

27. Repository preservation, source hashes, and format checks should remain outside the contribution summary.

---

# 12. Recommendation

**Reject in the present form.**

R54 is a serious and technically credible manuscript. It contains a genuine structural reduction, a useful exact price oracle, a valid weak NP-completeness result, and strong reproducibility practices. It has also become substantially more focused.

The current paper nevertheless stops short of the *Operations Research* bar.

The hardness theorem does not characterize the limited-menu regime because the budget is nonbinding. The global exact method is standard exponential inclusion/exclusion branching once the new oracle is available. The polynomial fallback is too expensive to function as more than a worst-case theorem in the reported implementation. The computational study demonstrates valid certificates but not a durable advantage over exact enumeration or modern numerical optimization. Heterogeneous rewards and command screening are supported by too little end-to-end evidence. Finally, the operational importance of the model remains uncalibrated.

A focused resubmission could become competitive. The selected-boundary and priced-path identities are worth preserving. The next version should complete more of the complexity map, make the exact-search mechanics visible, test the general algorithm at meaningful scale, and either broaden the mathematical abstraction or establish a concrete operational use case.