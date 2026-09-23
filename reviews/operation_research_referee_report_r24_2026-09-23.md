# Confidential Referee Report for Operations Research

**Manuscript:** *Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains*  
**Review date:** September 23, 2026  
**Repository:** TrillionniumFoundation/NDU  
**Reviewed branch:** revision/ndu-operations-research-r24-20260923  
**Reviewed SHA:** 63bbb843e1bbe7cac2170dc7d317d4cf18bb2bb8  
**Prior report considered:** reviews/operation_research_referee_report_r23_2026-09-23.md  
**Current recommendation:** **Major Revision. I would not recommend acceptance in the present form. This should not be another layer-adding revision: the next version needs to strengthen and simplify the theory-centered core. If the central accepted-control contribution cannot be made materially deeper than the present coordinate representation and model-specific convex consequences, I would recommend rejection.**

## Executive assessment

R24 is a real scientific rewrite, not a cosmetic response to R23. The title and contribution hierarchy now center accepted service adaptation rather than Neural Differential Utility. The robust result is correctly demoted to a certification lemma. The paper adds benchmark-relative continuation-transfer coordinates around an optimized restricted contract, quantifies the conservatism of the robust outer comparator, gives substantially more honest end-to-end cost accounting, and preserves unfavorable computational comparisons. The resulting manuscript is much more coherent than R23.

I also find the new benchmark-relative transfer theorem internally consistent on the cases I checked. The subtree telescoping argument is correct under the stated positive scalar-payment assumptions, the inverse map is the natural tree-flow inverse, and the three-node example is arithmetically consistent: the restricted value is 5/24, the accepted value is 21/64, the difference is 23/192, and the optimal relative transfer indeed has a negative coordinate that would be ruled out by the older nonnegative-flow parametrization. I did not find a fatal algebraic contradiction in the new R24 theorem or in the new interior-comparator diagnostic.

The remaining issue is no longer “the paper is organized around neural learning although the evidence is classical.” R24 has substantially fixed that. The issue is now more fundamental: **is the accepted-control contribution, in its present mathematical and economic form, strong enough for Operations Research?** I am not yet convinced.

The centerpiece added in R24 is exact and useful, but it is essentially a tree-incidence change of coordinates with lower bounds induced by pre-existing continuation slack, followed by direct substitution into a quadratic objective. The manuscript itself calls the tree algebra elementary. Meanwhile, the more general balance theorem already accommodates nonconstant benchmarks, vector services, signed payment coefficients, boundary points, and general polyhedral constraints. Thus the new theorem improves the economic alignment with the optimized comparator, but it does not obviously expand the general mathematical frontier of the paper.

The new computational evidence is even clearer. In the fresh matched study, the learned routes do not have a single positive amortization case against lifted continuation. At the strict target, both tanh-gradient and RBF-direct fall back in 100% of the measured cases at 63, 127, and 255 nodes and are slower than lifted continuation in every configuration, with paired intervals entirely on the unfavorable side. Even at the coarse target, tanh falls back in 100% of cases at all three sizes, and RBF remains slower overall. This is valuable negative evidence, but it means the learning layer should no longer be carrying any publication burden.

R24 also contains one concrete mathematical-writing error in the new repeated-query economics section. The manuscript’s amortization equation and the condition for a finite crossing have the signs reversed relative to each other and relative to the analysis code. The code is correct and does not manufacture a false advantage; the prose formula is not.

I therefore recommend major revision, with the burden now concentrated on the accepted-control theory, the economic comparator, and the connection to the dynamic-contract literature.

# 1. Review object and reproducibility are not the problem

The review object is complete. I reviewed branch revision/ndu-operations-research-r24-20260923 at SHA 63bbb843e1bbe7cac2170dc7d317d4cf18bb2bb8.

The R24 package check reports 39 main-PDF pages, 36 pages excluding references, a 30-page formal electronic companion, and a 28-page computational record in the separate code/data archive. It reports preservation of 72 predecessor mathematical blocks, 64 new rational tree tests, 1,536 interior-comparator certificates, 1,728 timing deployment certificates, 192 optimizer-label certificates, 96 fresh robust-policy certificates, 256 fresh robust-comparator certificates, and rejection of seven negative controls. References resolve and the build passes.

The provenance organization is unusually careful. R24 pins the reviewed R23 scientific SHA, preserves predecessor files and hashes, distinguishes the R24 execution source from the reviewed R23 paper, and separates formal companion material from the computational archive.

I therefore do not base this report on missing files, an incomplete branch, or a reproducibility concern. The scientific issues below remain after giving the package full credit for provenance and auditability.

# 2. R24 genuinely resolves the central identity objection from R23

The previous report argued that the integrated manuscript had demonstrated that its strongest contribution was accepted-control geometry, while the title and organization remained neural-centered. R24 has fixed this in a meaningful way.

The new title is appropriate. The abstract begins with accepted continuation and optimized restricted contracts. The introduction separates class-expansion value, implementation loss, and computational cost. Neural Differential Utility is explicitly presented as one implementation route rather than the scientific identity of the paper. Direct-price and classical methods are retained as full comparators. The robust theorem is no longer advertised as a major robust-optimization result.

This is the right direction and is not a superficial change.

I also credit the paper for keeping adverse evidence. R24 does not delete the cases where classical continuation is better. It charges optimizer-generated labels, fitting, prediction, auditing, polishing, and fallback. It explicitly distinguishes truth-in-set robustness from calibrated or field robustness. Those are all substantial improvements.

The remaining review should therefore not recycle the R23 objection that “the title is neural but the evidence is not.” That particular objection is largely closed.

# 3. The new benchmark-relative transfer theorem is correct-looking but too close to a reparametrization to carry the top-journal novelty burden by itself

Theorem thm:r24-transfers is the central new structural result. Under positive scalar payment coefficients and a fixed root payment, the accepted subtree constraints around any feasible comparator z can be represented by the transfer coordinates y, with lower bounds y_n >= -s_n/c_n determined by unused continuation slack. The tree incidence matrix B maps y to x-z, and subtree telescoping supplies the inverse.

This is useful. It repairs a genuine conceptual defect in applying the older y >= 0 coordinates around a comparator that does not saturate all continuation caps. The negative-coordinate three-node example makes that point cleanly.

However, the theorem’s mathematical content is still limited in three ways.

First, the bijection follows directly from conservation on a rooted tree. Once the relative subtree payment f_n is defined, the forward and inverse relations are forced. The exact objective formula is then W(z+By)-W(z) written in the new coordinates. I do not see a deep optimization theorem in that second step.

Second, the paper’s earlier general balance theorem is actually broader in several dimensions. It allows nonconstant comparison protocols, vector services, zero or negative net payments, boundary decisions, multiple commitments, and general accepted polyhedra. The R24 coordinate theorem narrows to the positive scalar-payment specialization. It gives a cleaner representation, but not a more general feasibility characterization.

Third, the strongest exact friction formula remains tied to the constant, interior, cap-matching case. For the economically important object introduced in R24—an arbitrary optimized restricted comparator with slack—the paper does not obtain an equally sharp critical-friction theorem, a clean monotone comparative static, or a new threshold characterization. Indeed, the manuscript correctly notes that monotone-friction conclusions can fail for nonconstant comparators.

For Operations Research, I would like the benchmark-relative theorem to generate a result that is not merely a coordinate identity. Examples of the needed strengthening include a sharp characterization of profitable expansion around a general optimized comparator, a nontrivial comparative static in continuation slack/capacity/friction, a decomposition of expansion value across contractual restrictions, or a structural algorithm whose complexity or optimality consequence cannot be obtained by directly handing the original polyhedron to a generic convex solver.

As written, the theorem is a very good lemma or representation theorem. I am not yet persuaded that it is sufficient as the principal novelty claim of a top-journal paper.

# 4. The paper needs a stronger theorem specifically around the optimized restricted comparator

R24 correctly identifies the optimized restricted comparator as the economically relevant benchmark. But once that comparator is made central, the strongest structural statements should also be centered there.

At present there is an asymmetry:

- the new transfer coordinates are general in z but mainly algebraic;
- the sharp critical-friction formula is for a constant interior cap-matching comparator;
- the constructive direction result uses tangent-cone optimization in a general polyhedron;
- the exact quadratic expansion formula is a restatement of objective improvement in the new coordinates.

The next revision should close this gap. The most interesting question is not merely whether every accepted x can be represented relative to z. It is: **what can be said sharply about the value and structure of the best accepted deviation from an already optimized restricted contract?**

For example, the lower bounds y_n >= -s_n/c_n should enter a new structural statement. How does expansion value change when a particular continuation slack increases? Which subtrees can consume slack first? Is there a generalized price/capacity certificate for strict positive expansion relative to a nonconstant z? When does the time-only restriction bind in the transfer representation? Can the optimal expansion be localized to a cut or a small set of critical continuation constraints? Those would turn the R24 coordinates into a substantive theory rather than a correct representation.

Without such a result, the paper still risks being read as a careful synthesis of standard KKT/normal-cone ideas, tree flow identities, total-variation duality, and model-based certification.

# 5. The economic content of the restricted comparator remains under-justified

The formal framework allows a generic restricted class Y inside the accepted class X. The experiments, however, emphasize an optimized time-only amendment as the economic comparator.

That is much better than comparing the adaptive policy with an arbitrary fixed outside protocol. But the paper still needs to explain why “time-only” is the canonical operational restriction.

The full accepted class can condition on history. A time-only comparator cannot. Therefore a positive expansion value may largely measure the value of adding history dependence, rather than a specifically contractual value of continuation-transfer adaptation. That may be an important value, but it should be named and decomposed.

The existing theorem is well suited to a comparator hierarchy, and I strongly recommend using it. At minimum I would like to see the same instances evaluated against several economically meaningful optimized restrictions, such as:

1. a fixed contract;
2. a time-only contract;
3. a current-regime/Markov contract where appropriate;
4. a limited-memory or restricted-history contract;
5. the full accepted history-dependent class.

The incremental gains between these classes would tell the reader what economic flexibility actually creates the value.

A top-journal structural paper should not allow the main positive gain to depend on one convenient restriction without demonstrating that the restriction corresponds to a real status quo or implementation constraint.

# 6. The main manuscript’s continuation-participation story should be aligned more tightly with the canonical institution

The main paper now opens with the statement that when a customer may leave at a review, every promised continuation must remain acceptable. That is the correct institutional interpretation for the continuation constraints that drive the tree theory.

But the electronic companion first presents a canonical master agreement in which the customer commits to the contingent menu before period zero. Its participation constraint is ex ante, and the text explicitly says it is not a right to renegotiate after each regime realization. Only later does the companion introduce the extension in which the customer may leave at each review and continuation participation is imposed at every history.

This is not a logical inconsistency—the companion clearly distinguishes the two institutions—but it is an expositional and scientific-priority mismatch. The main paper is now being sold as a continuation-participation paper. The continuation-participation institution should therefore be the primary model from which the principal results are derived, not an extension after an ex ante baseline.

The next revision should make the “customer may leave at each review” institution primary and derive the finite-tree constraints directly from service primitives. The ex ante master agreement can then be shown as a simpler special case.

This would also force the paper to explain more carefully when full history dependence is genuinely required and when a promised-utility or remaining-payment state can compress the tree.

# 7. The dynamic-contract literature review is still incomplete for an Operations Research submission

R24 has a much better general literature boundary than earlier versions. It correctly cites promised-utility ideas and acknowledges that dynamic programming, duality, total variation, and learned dual information are established.

However, I do not think the comparison with the Operations Research dynamic-contract literature is yet adequate. In particular, I did not find the following directly relevant OR papers in the repository source search:

- Mingliu Chen, Peng Sun, and Yongbo Xiao (2020), “Optimal Monitoring Schedule in Dynamic Contracts,” Operations Research 68(5):1285–1314, DOI 10.1287/opre.2019.1968.
- Yong Liang, Peng Sun, Runyu Tang, and Chong Zhang (2022), “Efficient Resource Allocation Contracts to Reduce Adverse Events,” Operations Research 71(5):1889–1907, DOI 10.1287/opre.2022.2322.

The first is especially relevant because it uses continuation utility as a dynamic state in an OR contract-design problem with continued participation. The second is relevant to dynamic resource-allocation contracts and the OR standard for deriving simple implementable contract structure from a dynamic contracting model.

These papers are not the same model—moral hazard and information frictions differ materially from the current public-state service institution—but that is exactly why the manuscript should compare itself to them explicitly. The question is not whether R24 duplicates their assumptions. The question is what is structurally new about “continuation prices” and accepted expansion when placed next to the OR contract-design literature that already uses continuation utilities, self-generating sets, and dynamic contract states.

The current manuscript compares broadly to classical economics references but needs a sharper Operations Research-specific contract-design boundary.

# 8. The new timing study is scientifically useful because it decisively rejects an amortized learning advantage under the tested certified protocol

R24’s new matched study is much better than the historical timing evidence. It uses 32 held-out contexts, three repetitions, fixed fits, explicit label costs, phase-resolved timings, actual fallback, and a structure-aware lifted baseline.

The result is unfavorable to the learned methods, and the paper should lean into that fact rather than continue treating the learning routes as coequal computational candidates.

At target 1e-5:

- 63 nodes: lifted 10.34 ms; tanh 18.84 ms; RBF 18.91 ms.
- 127 nodes: lifted 96.24 ms; tanh 112.53 ms; RBF 113.62 ms.
- 255 nodes: lifted 239.93 ms; tanh 277.86 ms; RBF 274.96 ms.

Both learned methods fall back in 100% of strict-target cases at all three sizes. Their paired savings intervals are strictly negative.

At target 1e-3, tanh again falls back in 100% of cases at all three sizes. RBF avoids some fallbacks at 63 and 255 nodes, but its total mean cost is still worse than lifted continuation in all three configurations. The paired intervals are again unfavorable.

The analysis JSON consequently reports no observed finite break-even query count for any learned method/configuration/target pair.

This closes the old amortization question more strongly than any additional benchmark could. Under the tested certification protocol, the learned routes do not amortize.

That is not a reason to reject the accepted-control theory. It is a reason to stop making learning a substantial part of the paper’s contribution architecture. Neural and direct-price methods can be retained as negative or diagnostic implementation studies, but they should not occupy scientific space as if the computational race remains unresolved.

# 9. There is a concrete sign error in the R24 amortization paragraph

This is the clearest technical correction required in the new R24 text.

The manuscript defines C_off as the candidate’s incremental offline cost relative to lifted continuation and defines t_L and t_C as the matched per-query mean times for lifted and candidate methods. It then writes the measured cost difference as

C_off + Q (t_L - t_C)

and says that a finite crossing exists only when t_C > t_L, with threshold C_off/(t_C - t_L).

These statements cannot all be correct.

If the quantity is “candidate total cost minus lifted total cost,” the correct difference is

C_off + Q (t_C - t_L),

and a crossing exists only when t_C < t_L, at

Q = C_off/(t_L - t_C).

Equivalently, if one defines online saving delta = t_L - t_C, then candidate-minus-lifted cost is C_off - Q delta, and a finite crossing requires delta > 0.

The R24 analysis code uses the correct convention. It computes paired savings as lifted minus candidate, sets observed_crossing_queries only when the mean saving is positive, and evaluates cost_difference = offline - Q * saving. Therefore the numerical conclusions are not corrupted by the prose error. In the current data all learned crossings are null anyway.

Nevertheless, the manuscript equation and inequality are wrong and must be corrected before any further review.

# 10. The outer-comparator diagnostic reveals a new issue: the robust certificate loses local tightness very quickly

I asked in R23 for the conservatism of the common outer comparator to be quantified. R24 does this, and I credit the authors for answering the question directly.

The resulting numbers are informative:

- radius 0: mean outer-set slack 0;
- radius 0.0625: mean outer-set slack about 0.070624;
- radius 0.125: about 0.071246;
- radius 0.25: about 0.075207.

Total mean certificate slack is about 0.071798, 0.076166, and 0.096102 at the three positive radii, with a total 95th percentile of about 0.138898 at radius 0.25.

The surprising feature is that most of the outer-set slack appears almost immediately at the first positive radius and then changes only modestly as the radius quadruples. The paper should explain whether this is a structural consequence of how the common outer class is constructed or an artifact of the designed family.

If the containing comparator class effectively jumps from the exact model-specific set at radius zero to a much larger union-containing set for any positive uncertainty, then the robust certificate is not locally tight as uncertainty shrinks. That is a real methodological limitation. A radius-dependent outer class or a tighter parametric bound could materially improve the certificate.

The current text says that the certificate is “informative but not exact.” That is true, but insufficient. The shape of the slack curve deserves a theorem or at least an explicit explanation.

# 11. The robust computational comparison is not a matched-quality comparison, and the current data show a nontrivial quality-time tradeoff

At radius 0.25, the fresh pointwise certification times are approximately:

- protected tanh: 158.14 ms, minimum reported gain 0.276082;
- protected RBF: 157.97 ms, minimum reported gain 0.296677;
- classical robust maximin: 178.15 ms, minimum reported gain 0.413329.

The paper correctly states that these are not matched-quality times. That disclaimer is necessary.

But once quality differs this much, the useful computational object is a Pareto frontier of time versus certified robust gain, not three isolated method points. A roughly 20 ms saving against robust maximin is not interpretable without accounting for the material reduction in worst-case certified gain.

If the robust computational study remains in the main paper, I recommend either matching the gain target across methods or plotting/reporting a quality-time frontier. Otherwise the timing comparison should be treated as descriptive bookkeeping rather than a computational result.

# 12. Pointwise economic certification is dominated by the comparator batch, which weakens the practical role of prediction

The fresh robust table makes the cost anatomy unusually clear. At radius 0.25, the comparator batch alone costs about 134.52 ms. The candidate’s own work is only about 23.5 ms for the protected learned methods and 43.6 ms for classical robust maximin.

Thus most of the pointwise economic-certification cost is not policy computation. It is the repeated restricted-comparator certification.

R24 now distinguishes accepted-policy implementation, pointwise economic certification, and offline population validation. That clarification resolves the ambiguity in R23.

But it also exposes the next operational bottleneck. If pointwise certification is meant to be an online deployment primitive, the paper needs a reusable or substantially cheaper restricted-comparator upper-bound mechanism. If comparator work is instead an offline validation device, then the paper should avoid presenting pointwise economic certification as the normal online policy path.

In either interpretation, reducing candidate prediction time is secondary until the comparator bottleneck is addressed.

# 13. Linear complexity in tree size is not linear complexity in horizon

The transfer map and inverse take linear work in the number of history-tree nodes. That is correct and useful.

However, the number of history nodes can grow exponentially with horizon under branching. The companion itself notes a canonical continuation tree with thousands of decision nodes and mentions promise-state representations as an alternative.

The manuscript should not let “O(N) on an N-node tree” read as a general scalability statement for long-horizon dynamic contracting. The relevant complexity discussion should include horizon, regime branching, and any state-compression structure.

This is especially important because the paper’s main economic novelty now comes from continuation constraints at every history. Those same constraints create the tree growth.

A stronger OR contribution would either derive a recursive promised-state formulation for the accepted expansion problem or state conditions under which the transfer/price structure can be computed without materializing the full history tree.

# 14. The synthetic institution is coherent but deliberately frictionless in information, which limits the breadth of the contractual claim

The canonical model assumes public, contractible regime, tier, stock, demand, and fulfillment; fixed premium and indemnity schedules; exogenous demand; no private type; and no hidden effort. This is a legitimate modeling choice.

But it means that the paper is not solving contract design in the usual incentive sense. It is optimizing a contingent service protocol under participation and physical constraints.

That distinction should remain front and center. The accepted-control results may still be valuable, but the managerial interpretation should be about contractually constrained service adaptation, not a general theory of dynamic contracts.

The strongest version of the paper would explain where this public-state assumption is operationally natural—for example, a service-level agreement with verifiable demand and fulfillment—and why continuation participation, rather than only ex ante participation, is institutionally required.

# 15. The manuscript remains broader than the revised scientific identity requires

R24 is much better organized, but the preservation strategy still leaves a very large formal and computational footprint: 36 main pages excluding references, a 30-page formal companion, and a 28-page computational record, while retaining 72 predecessor mathematical blocks.

Preservation is valuable for research history. It is not the same thing as prioritization for a journal reader.

The accepted-control paper I now see has a relatively clear core:

- the accepted expansion problem relative to an optimized restriction;
- continuation-price/switching-capacity optimality;
- benchmark-relative transfer coordinates;
- constructive positive-gain certificates;
- implemented economic certification.

The value-gradient/NDU bridge, historical neural variants, multiple generations of repair/certificate machinery, and extensive timing archaeology are secondary to that core. They can remain in the archive without all being part of the formal scientific narrative.

I am not asking the authors to hide negative evidence or delete derivations. I am asking them to distinguish the journal paper from the repository history.

# 16. What I would require in the next revision

A publishable next version should address the following points directly.

1. **Strengthen the theory around the optimized restricted comparator.** The new coordinates should yield a nontrivial structural theorem, threshold, comparative static, decomposition, or algorithmic consequence beyond the bijection and objective substitution.

2. **Justify and stress-test the restricted comparator class.** Show what portion of expansion value comes from moving from fixed to time-only, time-only to state-dependent, and state-dependent to full history dependence, or give an equally compelling operational rationale for the chosen Y.

3. **Make continuation participation the primary institution.** Align the main paper’s opening story with the canonical model rather than introducing customer exit only as a later extension.

4. **Repair the dynamic-contract literature boundary.** Compare explicitly to the Operations Research dynamic-contract papers cited above and explain the distinction in state representation, participation, information, and structural result.

5. **Correct the amortization algebra.** The main-text sign convention must match the analysis code.

6. **Reframe the learning evidence.** The fresh matched study establishes no amortization advantage. Treat neural/direct-price routes as implementation diagnostics or negative results unless a genuinely different protocol produces a fair and reproducible advantage.

7. **Explain or improve the positive-radius outer comparator.** The near-immediate jump in outer-set slack requires structural explanation and, ideally, a tighter radius-sensitive construction.

8. **Address horizon complexity.** Explain how the continuation-price/transfer structure interacts with exponential history-tree growth and whether a promised-state recursion can preserve the structural results.

9. **Clarify the role of online certification.** If pointwise economic certification is an online requirement, reduce or reuse comparator work. If it is an offline evaluation tool, say so consistently and avoid implying that every deployment bears the comparator batch.

10. **Simplify the formal scientific narrative.** Preserve the archive, but make the paper’s theorem chain short enough that a reader can identify the one or two principal contributions without traversing the history of the NDU project.

# 17. Minor and presentation comments

The title change is successful and should be retained.

The abstract is now much more accurate than the R23 abstract, but it still tries to carry too many theorem families and diagnostics. Once the core theory is strengthened, the abstract should spend more space on the structural managerial result and less on the inventory of certificate layers.

The phrase “exact” is generally used carefully, but the paper should continue distinguishing exact identities/certificates from numerical optimizer labels. R24 already does this better than prior revisions.

The term “continuation price” is intuitive, but because the OR dynamic-contract literature often uses continuation utility as a state variable, the manuscript should define very early that its continuation price is a dual object attached to continuation participation/cap constraints, not the promised utility itself.

The robust uncertainty study is appropriately labeled as designed rather than calibrated. I would not require field data for a theory paper, but I would not allow field-robustness language to re-enter later revisions without calibration.

The package-check and replay counts should remain in the reproducibility guide rather than becoming part of the novelty argument.

# 18. Recommendation to the editor

R24 is the first version in this review sequence that I regard as having a coherent primary scientific identity. The authors took the central R23 criticism seriously: they moved accepted service adaptation and continuation-transfer structure to the front, demoted the neural machinery to an implementation role, quantified robust-certificate conservatism, strengthened computational accounting, and retained adverse results.

I do not recommend acceptance yet.

The principal new R24 theorem is useful and, on the material I checked, internally correct, but it is still too close to an exact tree reparametrization plus direct objective expansion to establish the top-journal novelty burden by itself. The paper needs a deeper theorem about optimal accepted expansion around the optimized restricted comparator, not merely coordinates for expressing that expansion.

The empirical record also now makes clear that the learned implementations are not a source of computational advantage under the tested certified protocol. That is not fatal once the paper is theory-centered, but it means further neural engineering would be the wrong response.

The right next step is therefore a **major theory-centered revision**: strengthen the optimized-comparator structure, justify the economic restriction, align the continuation institution, repair the OR dynamic-contract literature boundary, correct the amortization formula, and simplify the manuscript around the accepted-control contribution.

**Decision recommendation: Major Revision. If the next revision adds more computational/certification layers without deepening the accepted-control theorem, I would recommend Reject.**
