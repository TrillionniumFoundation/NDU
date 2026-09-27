# Confidential Independent Referee Report for Operations Research

**Manuscript:** *Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains*  
**Revision reviewed:** R24, September 23, 2026  
**Repository:** TrillionniumFoundation/NDU  
**Scientific base:** revision/ndu-operations-research-r24-20260923  
**Reviewed base commit:** 63bbb843e1bbe7cac2170dc7d317d4cf18bb2bb8  
**Review type:** Independent second-pass harsh review from the R24 revision tip  
**Area declared by the manuscript:** Stochastic Models  
**Recommendation:** **Reject in present form; encourage a substantially new, theory-centered submission rather than another incremental revision of the integrated manuscript.**

---

## Executive assessment

R24 is a serious and unusually auditable manuscript. It has improved materially relative to the predecessor described in the authors' R23 response: the title and opening now center accepted service adaptation rather than Neural Differential Utility; the restricted comparator is explicitly optimized; a new benchmark-relative transfer theorem connects continuation slack to that optimized comparator; the robust result is correctly demoted to a certification lemma; the authors quantify outer-comparator conservatism; and the new repeated-query experiment finally charges labels, fitting, audits, fallback, and a strong lifted classical baseline.

Those are real improvements. I also found no obvious mathematical failure in the new tree-transfer result after checking its telescoping algebra and its three-node example. The numerical package is far more transparent than is typical: adverse results are retained, independent rational audits are used, and the new timing study does not hide fallbacks or failed amortization.

My recommendation is nevertheless negative.

The reason is not reproducibility. It is the mismatch between the **size and breadth of the scientific package** and the **depth of the principal new contribution that remains after the manuscript's own strongest evidence is taken seriously**.

The new R24 theorem is useful, but its core content is an exact change of coordinates on a rooted tree plus direct substitution into a concave objective. It solves an important exposition problem—how to express accepted deviations around a non-cap-matching optimized comparator with slack—but it does not yet yield a comparably deep structural result about the optimizer of the expanded problem. The manuscript still asks that this coordinate result, together with several standard convex-analytic certificates and a large historical learning apparatus, carry a top-journal contribution burden that I do not believe they presently meet.

At the same time, R24's strongest new computational experiment answers an old question decisively and unfavorably for the learned methods. At the strict target, both Tanh and RBF routes fall back in **100%** of the 63-, 127-, and 255-node cases; both are slower than lifted continuation at every tested size; all reported paired savings intervals are negative; and the machine-readable analysis records **zero finite observed break-even cases**. Direct-price approximation also remains substantially more accurate than the neural value-gradient route in the frozen-policy validation. This is scientifically valuable negative evidence, but it means the learning machinery can no longer plausibly be treated as a coequal computational contribution.

I therefore do not recommend another incremental "R25" that adds more certificates, timings, robustness layers, or neural engineering to the present architecture. A publishable descendant should be a shorter and deeper accepted-control paper, with one or two genuinely strong results around the optimized restricted comparator, a clearer institution, a justified information/comparator hierarchy, and a much more economical formal narrative.

---

# 1. What I reviewed

I reviewed the R24 root manuscript, the formal electronic companion, the computational supplement, the response to the R23 report, the R24 submission checklist, the new transfer checks, the interior-comparator study, the repeated-query timing outputs, the robust cost outputs, and the package metadata.

The current package reports:

- 36 main-text pages excluding references;
- 30 pages in the formal electronic companion;
- a 28-page computational record kept outside the formal companion;
- 72 preserved mathematical statement/proof blocks;
- 1,728 new timing pipelines with no recorded timing-pipeline failures;
- 768 new interior uncertainty models and 1,536 comparator solves;
- 96 fresh robust policy certifications;
- independent replay and rational audit machinery.

The formal page counts appear compatible with the manuscript's chosen Lengthy format. I do not view page-limit compliance as the relevant problem. The problem is **contribution-to-length and contribution-to-complexity**.

The manuscript currently contains several distinct intellectual papers inside one submission:

1. an accepted-service expansion theory on finite trees;
2. continuation-price and switching-tension characterizations;
3. benchmark-relative transfer coordinates;
4. a value-gradient / resource-price bridge;
5. inexact-response and primal-dual certification;
6. fixed-primal and complete dual repair;
7. robust uncertainty certification;
8. frozen-policy validation;
9. learned-price and direct-price implementation studies;
10. repeated-query cost accounting;
11. a substantial archived history of earlier formulations and experiments.

Each component can be technically legitimate while the whole still lacks a sufficiently sharp top-level scientific statement.

---

# 2. What R24 gets right

Before the criticisms, I want to record several points that should not be lost in any rewrite.

## 2.1 The optimized comparator is now economically meaningful

The manuscript no longer measures gain only against an arbitrary outside protocol. It explicitly distinguishes the full accepted value J, the optimized restricted value K, and the expansion value Delta = J - K, with the restricted class contained in the full accepted class. It also charges restricted-solver error when a numerical comparator is used. This is the correct direction.

## 2.2 The new slack-aware transfer coordinates repair a real conceptual defect

For positive scalar continuation-payment coefficients, R24 correctly observes that an optimized restricted contract need not exhaust every continuation cap. Therefore the old nonnegative-flow coordinates cannot simply be centered at that comparator.

The new lower bound y_n >= -s_n/c_n has a clean operational interpretation: accepted expansion can spend participation slack already earned by the restricted contract.

I checked the subtree telescoping in Theorem thm:r24-transfers. The stated inverse and node-balance map are consistent. I also independently checked the arithmetic of the three-node example:

- restricted optimum z = (1/6, 2/3, 2/3);
- restricted value 5/24;
- accepted optimum (3/8, 3/4, 3/8);
- accepted value 21/64;
- expansion 23/192;
- relative transfer (-1/12, 7/24).

The example succeeds at its intended purpose: imposing y >= 0 around a slack comparator would wrongly exclude the accepted optimum.

## 2.3 The negative computational results are not hidden

This is a major credibility improvement. The R24 matched study is much more informative than the earlier timing record. The authors use a structure-aware lifted classical baseline, record the entire pipeline, keep all fallbacks, and report unfavorable paired differences.

## 2.4 The robustness claims are better delimited

The manuscript now distinguishes a designed uncertainty family, pointwise truth-in-set certification, frozen-policy validation, and field calibration. It explicitly does not claim that the synthetic coefficient cube is statistically calibrated to field uncertainty.

These corrections make the paper easier to evaluate. They also make the remaining scientific issue more visible.

---

# 3. The principal R24 theorem is still too close to a reparametrization

Theorem thm:r24-transfers is the main genuinely new object added in direct response to the R23 identity criticism. I believe it is useful. I do not believe it is yet enough.

The first half is a rooted-tree change of variables. Once the subtree-cap rows have the specified scalar structure, telescoping gives a bijection between feasible accepted policies with a fixed root payment and a transfer vector with shifted lower bounds.

The second half then substitutes x = z + B y into a quadratic-plus-absolute-value objective. Consequently, J_lambda - K_lambda is written as the maximum of the corresponding translated objective over the translated feasible set.

That equality is exact, but after the bijection is known, the objective formula is algebraically immediate.

For a top Operations Research paper, the question is what structural consequence follows **because** of these coordinates that was not already available from generic convex optimization or from the earlier balance/KKT formulation.

At present I do not see a result of comparable depth such as:

- a closed-form or efficiently computable characterization of the optimal accepted expansion around a general optimized comparator;
- a sharp threshold expressed in the comparator's slack profile;
- a decomposition of Delta into economically interpretable sources with nontrivial comparative statics;
- a monotonicity theorem for expansion value as continuation slack, switching friction, or information is varied;
- a recursion that avoids enumerating the history tree;
- a new complexity guarantee exploiting the transfer geometry;
- a sensitivity formula for the optimal expansion under perturbations of the restricted class;
- or a strong theorem comparing nested operational information classes under continuation participation.

The current theorem tells me how to write the problem in better coordinates. It does not yet tell me enough that I could not obtain by handing the translated convex program to a solver.

This is the single most important reason for my recommendation.

---

# 4. The optimized restricted comparator is still under-theorized

The manuscript correctly insists that the comparator must itself be optimized. But "optimized" does not make the comparator class economically canonical.

The expansion value Delta = J - K is only as meaningful as the restriction defining the restricted class.

In the canonical information hierarchy preserved in the companion, the numerical decomposition is already revealing:

- Static to Time: approximately 0.000817;
- Time to Time--Regime: approximately 0.616558;
- Time--Regime to Full State: approximately 0.019290;
- Total Static to Full State: approximately 0.636665.

Thus almost all of the canonical accepted information value is associated with admitting the current regime. Only a small fraction is attributable to the inherited-contract/full-state increment.

This does not invalidate the paper. It does mean that the economic story depends strongly on **which information is withheld from the restricted class**.

The main paper frequently uses a reoptimized time-only amendment as the restricted economic comparator. Why is that the natural operational baseline rather than:

- a static contract;
- time plus current regime;
- a Markov rule in an explicitly promised-service state;
- or another implementable service class used in practice?

A theory paper should not answer this merely by saying that Y is a subset of X. It should either derive Y from the institution or show how conclusions change across a nested hierarchy.

A stronger successor should give a theorem or at least a systematic continuation-participation decomposition across nested restricted classes, together with structural conditions explaining when each increment is zero, positive, or large.

Right now the comparator is mathematically well optimized but scientifically insufficiently justified.

---

# 5. The paper still contains two different participation institutions

This is a deeper identity problem than a presentation issue.

The canonical inventory model in the electronic companion is an **ex ante master agreement**. The customer commits to a contingent menu. The text explicitly says that the customer is not purchasing anew at each review and that the ex ante participation constraints are not a right to renegotiate after every realized regime.

Later, a different institution is introduced: the customer may leave at each review, so every reachable history carries a continuation participation condition.

The main manuscript now opens as though continuation exit is the primary economic institution: an improvement at the root is insufficient because every promised continuation must remain acceptable.

That is a coherent model. But it is not the same institution as the canonical ex ante master agreement from which much of the historical economic motivation, information hierarchy, and exact inventory example originate.

R24 acknowledges the distinction. Acknowledging it is not the same as conceptually unifying it.

The paper must decide what it is about.

If continuation participation is the main institution, then the principal motivating model, comparator hierarchy, and managerial interpretation should all be rebuilt around that institution. The ex ante master-agreement model can become a limiting or comparison case.

If the ex ante master agreement is the main institution, then the continuation-price theory is an additional extension and should not carry the entire title-level identity.

At present the main paper and the canonical companion are pulling in different directions.

---

# 6. The current Stochastic Models positioning is not yet convincing

The declared review area is Stochastic Models. The motivating primitives are stochastic, and the tree weights are generated by random demand regimes.

However, the principal R24 structural theorem is a deterministic finite-dimensional statement about a polyhedron on a rooted tree. The continuation-balance, transfer, and certification results are largely convex-analysis and network/tree algebra after the stochastic primitives have been converted into coefficients.

That is not a defect by itself. Many important stochastic models reduce to structured deterministic programs. But it raises the venue question: **where is the stochastic-modeling advance?**

If the intended contribution is Stochastic Models, I would expect the paper to extract a structural result that depends materially on the stochastic evolution—for example, a state compression, recursion, monotonicity, asymptotic property, or performance characterization that would disappear in an arbitrary deterministic tree program.

If the intended contribution is Optimization, the burden shifts to the algorithmic or structural novelty of the convex program. The new transfer bijection is then too elementary by itself.

If the intended contribution is Operations/Supply Chains, the inventory/service institution becomes central, and the methodological bar is high because the application setting is classical and the evidence is entirely synthetic.

The manuscript needs a clearer scientific home, not merely an area label.

---

# 7. The new timing study is a negative result for learning under the tested certified protocol

The most decisive empirical contribution in R24 is not an acceleration result. It is a falsification of one.

At the strict certificate target, the main R24 table reports:

| Nodes | Method | Mean total time (ms) | Fallback | Paired saving vs. lifted (ms) |
|---:|---|---:|---:|---:|
| 63 | Lifted | 10.34 | 40.6% | — |
| 63 | Tanh | 18.84 | 100.0% | -8.50 |
| 63 | RBF | 18.91 | 100.0% | -8.57 |
| 127 | Lifted | 96.24 | 62.5% | — |
| 127 | Tanh | 112.53 | 100.0% | -16.29 |
| 127 | RBF | 113.62 | 100.0% | -17.38 |
| 255 | Lifted | 239.93 | 81.2% | — |
| 255 | Tanh | 277.86 | 100.0% | -37.93 |
| 255 | RBF | 274.96 | 100.0% | -35.02 |

The reported descriptive paired-savings intervals are strictly negative for both learned methods at all three sizes.

The analysis file then records:

**finite_observed_break_even_cases = 0.**

This is not an ambiguous outcome. Under the tested certified deployment protocol, the learned routes do not amortize.

Moreover, the frozen independent validation continues to show that direct-price RBF is substantially more accurate than the Tanh value-gradient route. The reported regret upper bounds are:

- IID: Tanh 0.002501, RBF 0.000113;
- shifted domain: Tanh 0.015633, RBF 0.000566.

Therefore neither computational speed nor decision accuracy supports privileging the neural value-gradient route.

The right response is not to add another neural architecture. The right response is to demote learning to one of two roles:

1. an honest negative/diagnostic implementation study; or
2. a separate paper that studies a deployment regime in which expensive repeated exact optimization genuinely creates an amortization opportunity.

The current paper still devotes too much theorem and companion space to a learning route whose own strongest updated evidence says it is not competitive under the declared certified protocol.

---

# 8. There is a concrete sign error in the main amortization formula

This is a technical error that should be corrected irrespective of editorial outcome.

The main text defines C_off as the candidate method's incremental offline cost relative to lifted continuation and t_L, t_C as the matched per-query mean times for lifted and candidate methods.

It then writes the cost difference as

C_off + Q (t_L - t_C)

and states that a finite crossing exists only when t_C > t_L, with threshold

C_off / (t_C - t_L).

These statements are inconsistent.

If the intended quantity is

candidate total cost - lifted total cost,

then the correct expression is

C_off + Q (t_C - t_L)
= C_off - Q (t_L - t_C).

A finite break-even point can exist only if the candidate is faster online:

t_C < t_L,

in which case

Q* = C_off / (t_L - t_C).

The implementation in revisions/or-r24-20260923/analyze.py uses the correct convention: it defines saving as lifted minus candidate, creates a crossing only when that saving is positive, and evaluates offline - Q * saving.

Therefore the reported null break-even conclusions are not corrupted. The prose equation is still wrong and must be fixed.

For a manuscript whose empirical contribution emphasizes exact accounting, this sign error in the central amortization identity is particularly unfortunate.

---

# 9. The robust outer comparator becomes loose at the first tested positive radius

R24 was right to measure the conservatism of the common outer comparator. The result exposes an important methodological limitation.

The mean upper slack decomposition is approximately:

| Radius | Outer-set slack | Interpolation slack | Total slack |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 0.0625 | 0.070624 | 0.001173 | 0.071798 |
| 0.125 | 0.071246 | 0.004920 | 0.076166 |
| 0.25 | 0.075207 | 0.020896 | 0.096102 |

At radius 0.25, the total-slack median is approximately 0.092725 and the 95th percentile approximately 0.138898.

The striking feature is not merely that the certificate is conservative. It is that the outer-set component is already about 0.071 at the smallest positive radius tested and changes only modestly as the radius quadruples.

I do **not** infer a literal mathematical discontinuity at radius zero from four grid points. But the experiment shows rapid local loss of tightness on the tested scale.

The paper should explain the geometry causing this. If the common outer class is built by separately relaxing several coefficient-dependent restrictions, the construction may destroy correlations among those restrictions as soon as uncertainty is introduced. If so, the outer set is structurally too large.

A strong theory paper could turn this weakness into a useful result:

- characterize the first-order growth of outer-comparator slack as the uncertainty radius tends to zero;
- construct a radius-dependent outer class that preserves coefficient correlations;
- or derive a tighter parametric comparator bound without solving every model-specific comparator online.

As written, the manuscript measures the problem but does not solve or explain it.

---

# 10. The robust timing comparison is not quality matched

The fresh robust-cost experiment reports complete pointwise certification costs at radius 0.25:

- protected Tanh: about 158.14 ms;
- protected RBF: about 157.97 ms;
- classical robust maximin: about 178.15 ms.

Those times alone make the learned methods look modestly faster.

But the achieved certified robust gains differ materially. The same fresh study reports minimum gain lower bounds approximately:

- Tanh: 0.276082;
- RBF: 0.296677;
- classical robust maximin: 0.413329.

Mean lower gains also favor classical robust maximin.

The manuscript correctly disclaims a matched-quality speed comparison. That disclaimer is necessary but not sufficient to make the three times a substantive computational result.

The scientifically meaningful object is a **quality-time frontier**. If the robust computational study remains central, the paper should compare methods at a common certified-gain target or report the Pareto frontier between online work and certified robust value.

Otherwise these numbers should be described as accounting data, not algorithmic evidence.

---

# 11. Pointwise economic certification is dominated by the comparator, not the policy

The same fresh robust study exposes a second operational issue.

At radius 0.25, the common comparator batch costs approximately 134.52 ms.

For the protected learned methods:

- own policy work is about 23.5 ms;
- complete certification is about 158 ms.

Thus roughly 85% of the complete pointwise certification time is comparator work.

This observation matters more than shaving a millisecond off prediction.

The manuscript now usefully distinguishes:

1. accepted-policy implementation;
2. pointwise economic certification against an optimized restricted comparator;
3. offline population validation.

But the operational role remains unresolved.

If every online decision truly needs a pointwise proof of positive gain relative to a reoptimized restricted contract, then the dominant research problem is **reusable comparator certification**, not prediction.

If the comparator is only needed offline to validate a frozen deployment rule, then it should not be presented as a normal online cost of every decision.

The paper should choose one interpretation and design the method around it.

A particularly valuable new theorem would provide a reusable restricted-value envelope across nearby contexts, with a certified update rule cheaper than resolving the full comparator batch.

---

# 12. Linear in tree size is not a horizon-complexity result

R24 appropriately states that the forward and inverse transfer maps take linear work in the number of tree nodes.

That is correct and useful at the data-structure level.

It should not be allowed to masquerade as a favorable dynamic-programming complexity statement.

The canonical continuation-participation example already has 3,280 decision nodes. In a nonrecombining history tree, the number of nodes can grow exponentially in horizon.

Therefore a linear-in-N transfer operation can still be exponential in the primitive horizon.

This is precisely where the paper could make a deeper contribution. Continuation participation naturally suggests a promised-service or remaining-payment state. The companion itself notes that a promise-state representation is an alternative.

I would like to know:

- Can the continuation-price balance be represented recursively without enumerating histories?
- Is the transfer coordinate compressible into a low-dimensional promised-payment state?
- Under Markov exogenous regimes, can optimal accepted adaptation be characterized by a dynamic program whose state dimension does not grow with the number of histories?
- Which of the cut/critical-friction theorems survive such recombination?
- When does history dependence add value beyond a Markov promised-state rule?

A theorem answering even one of these questions would substantially strengthen the paper.

---

# 13. The public-information contract institution limits the scope of the contractual claim

The paper is careful to state that there is:

- no private type;
- no hidden effort;
- exogenous demand;
- publicly observable and contractible regime, stock, tier, demand, and fulfillment;
- fixed tariff and indemnity schedules.

This is legitimate.

But it means that the paper is not solving dynamic contract design in the usual adverse-selection or moral-hazard sense. It is solving a **contractually constrained stochastic control problem with participation restrictions**.

The title "Accepted Service Adaptation" is therefore much better than a broad "dynamic contracting" title would be.

The managerial interpretation should remain equally disciplined.

The paper should explain where continuation participation is operationally natural despite full contractibility. For example:

- service-level agreements with periodic cancellation rights;
- maintenance/service subscriptions with verifiable utilization and fulfillment;
- capacity or quality commitments where the customer can terminate after a public service history.

Without that institutional grounding, "customer acceptance" risks sounding like a generic inequality wrapper around a control problem.

---

# 14. The Operations Research dynamic-contract boundary remains incomplete

The related-literature section has improved and correctly cites classic recursive-contract and service-contract work. It nevertheless remains too selective for a paper making a continuation-contractual contribution in Operations Research.

At minimum, the authors should engage more directly with recent and journal-local work on dynamic contracts, monitoring, maintenance, and long-term capacity relationships. Examples include:

- Chen, Sun, and Xiao (2020), *Optimal Monitoring Schedule in Dynamic Contracts*, Operations Research;
- Tian, Sun, and Duenyas (2021), *Optimal Contract for Machine Repair and Maintenance*, Operations Research;
- Liu, Lewis, Song, and Kuribko (2019), *Long-Term Partnership for Achieving Efficient Capacity Allocation*, Operations Research;
- He (2023), *Dynamic Mechanism Design with Capacity Constraint*, Operations Research.

These papers often address private information, moral hazard, endogenous monitoring, or other institutions absent here. That difference is exactly why they belong in the boundary discussion.

The paper should explain, result by result:

- what is public versus private;
- whether continuation utility is a state or a constraint dual;
- whether the principal chooses transfers or only a fixed service protocol;
- whether participation is ex ante or sequential;
- what role switching/reconfiguration friction plays;
- and what structural theorem is new because of the present public-state service institution.

The phrase "continuation price" is potentially confusing in this literature. Here it is a **dual variable associated with continuation participation/cap constraints**, not promised continuation utility itself. That distinction should appear near the first use of the term.

---

# 15. The formal architecture remains too broad despite the new title

R24 is much better organized than the predecessor described in the response letter. It is still much too broad for the depth of its primary claim.

The main paper is 36 pages excluding references. The formal companion is another 30 pages. The computational record is 28 pages. Seventy-two predecessor theorem/proof blocks are preserved.

Preservation is good research hygiene. It is not a publication principle.

A journal paper should not be a lossless serialization of the research process.

The following material is scientifically secondary if the paper is now about accepted-control geometry:

- the full historical sequence of neural value-gradient constructions;
- verified-face learning machinery that is no longer central;
- multiple generations of price polishing and repair unless needed by the principal theorem;
- historical timing archaeology;
- older scalar/star studies whose main role is provenance;
- several empirical tables documenting methods that the new matched study has already shown to be dominated for the claimed certified deployment purpose.

I am not asking the authors to delete evidence from the repository. The repository can and should preserve it.

I am asking the journal manuscript to distinguish **what was learned during the project** from **what the final paper contributes**.

The archive can remain comprehensive while the paper becomes selective.

---

# 16. The manuscript's strongest positive contribution is currently smaller than its machinery

The most compelling scientific core I see is:

1. start from an optimized restricted service contract;
2. impose continuation participation on a finite public history tree;
3. characterize optimality through continuation prices and switching tensions;
4. express accepted deviations in slack-aware transfer coordinates;
5. use that structure to certify a constructive economic gain.

That is a coherent paper.

However, item 4 currently provides coordinates, and item 5 relies heavily on general convex certificates. The manuscript needs one more genuinely strong structural step.

A top-journal reader should be able to complete the sentence:

> "Because of Theorem X, we now know ___ about optimal accepted service adaptation that was not available from generic convex programming, network-flow duality, or standard dynamic-programming machinery."

I cannot yet fill in that blank with a result commensurate with the paper's size.

---

# 17. What I would require for a scientifically stronger new submission

I would not recommend answering this report with another large collection of patches. I would recommend designing a new submission around a small theorem chain.

## 17.1 A deeper optimized-comparator theorem

Use the R24 coordinates as a lemma, not the destination.

Possible directions include:

- an exact friction/slack threshold for when the optimized restricted comparator ceases to be optimal in the expanded class;
- comparative statics of expansion value with respect to continuation slack;
- a decomposition of expansion value into information, slack, and switching-friction components;
- a monotone or piecewise-analytic expansion path as restrictions are relaxed;
- a strongly polynomial/tree-linear algorithm for a nontrivial subclass;
- or a recursion that compresses history through a promised-payment state.

The result must be about the optimizer or value, not only about coordinates.

## 17.2 Derive the comparator class from the operating institution

Explain why the restricted class is the actual incumbent technology/contract, not merely one convenient subspace.

Then show how the theory behaves for nested alternatives.

The canonical static/time/time-regime/full-state decomposition is a useful start, but it should be rebuilt under the **continuation-participation institution** if that is the main paper's institution.

## 17.3 Unify the participation model

Choose continuation participation or ex ante participation as primary.

Do not make the main paper tell one institutional story while the canonical companion tells another.

## 17.4 Address horizon complexity

Show whether the tree theory admits Markov or promised-state compression.

"Linear in nodes" is not enough if nodes grow exponentially in horizon.

## 17.5 Reframe learning as evidence, not identity

The R24 results already answer the certified-amortization question negatively for the tested setup.

Keep one concise table if it helps delimit where approximation does not pay. Move the rest to the reproducibility archive unless a new deployment regime creates a genuine, fair advantage.

## 17.6 Fix the robust comparator, or reduce its role

Explain the rapid outer-set slack at the smallest tested positive radius and develop a tighter construction if robust pointwise economic certification remains central.

Otherwise move the robust study to a secondary illustration.

## 17.7 Clarify online versus offline certification

If pointwise comparator certification is online, attack the comparator cost directly.

If it is offline, stop presenting comparator solves as if they are required for every policy evaluation.

## 17.8 Repair the literature boundary and scientific area

Position the contribution relative to modern dynamic-contract and stochastic-control work using the actual information structure and participation institution.

Then choose the review area that matches the strongest theorem.

---

# 18. Specific technical and presentation comments

### 18.1 Correct the amortization sign immediately

This is an actual equation error, even though the code uses the correct sign.

### 18.2 Preserve the new title

*Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains* is much more accurate than a neural-centered title.

### 18.3 Shorten the abstract

The abstract still inventories too many layers: transfer coordinates, tension repair, primal-dual certificates, value gradients, neural/direct/classical methods, complete-dual repair, repeated-query measurements, robust uncertainty, and certificate conservatism.

A top-journal abstract should identify the decision problem, one or two principal structural results, and the main operational implication.

### 18.4 Define continuation price against continuation utility

Do this near the start. In recursive contracting, readers may otherwise infer a promised-utility state.

### 18.5 Do not call numerical optimizer labels exact

R24 is mostly careful about this. Retain the distinction between exact rational audit identities and numerically generated optimizer statistics certified to a tolerance.

### 18.6 Do not turn reproducibility counts into novelty evidence

The package checker, hashes, negative controls, and replay counts are excellent. They belong in the reproducibility statement, not the contribution argument.

### 18.7 Do not infer a learning theorem from frozen-policy validation

The positive expected-gain bounds are conditional on fixed frozen policies and a known synthetic model. The manuscript now says this. Keep that limitation explicit.

### 18.8 A time-versus-certified-value frontier would be more informative than isolated robust timings

The robust learned methods are faster in the fresh complete-certification table but achieve lower robust certified gains. This is a tradeoff, not a speed victory.

### 18.9 The exact three-node slack example is good pedagogy

Keep it if the transfer theorem remains. It efficiently demonstrates why nonnegative old coordinates cannot be reused around a slack optimized comparator.

### 18.10 The strongest negative results should stay

Do not remove the 100% fallback facts or the null break-even result. They are important evidence that the manuscript is not selecting only favorable computational regimes.

---

# 19. Recommendation to the editor

R24 is rigorous enough to deserve serious consideration, but I do not think the present integrated manuscript clears the Operations Research contribution bar.

The new benchmark-relative transfer theorem appears internally coherent and fixes an important conceptual gap. Yet it remains, in its present form, primarily an exact reparametrization of the accepted tree polyhedron followed by direct objective translation. The manuscript has not yet extracted the deeper optimizer-level structural theorem needed to make this the center of a top-journal paper.

The empirical revision also resolves the learning question against the learned methods under the declared certified protocol. Tanh and RBF are slower than lifted continuation at every size in the fresh strict-target study, they fall back in every strict-target case, and no finite observed amortization point exists. That result is valuable, but it removes the strongest remaining justification for the large learning apparatus.

The robust diagnostics are similarly honest but identify new bottlenecks: the common outer comparator becomes materially loose at the first tested positive radius, the robust timing comparison is not quality matched, and the restricted-comparator batch dominates pointwise certification time.

Finally, the manuscript still spans two participation institutions and has not fully justified why its chosen restricted comparator is the operationally canonical one.

These are not minor-revision problems. Nor, in my view, are they best addressed by another incremental expansion of the same manuscript.

I recommend **Reject in present form**.

I would encourage a **new, substantially shorter, theory-centered submission** if the authors can use the R24 transfer coordinates to prove a deeper theorem about optimal accepted expansion around an optimized restricted contract, derive the comparator from a unified continuation-participation institution, address tree/horizon complexity, and reduce the learning/certification history to the evidence genuinely needed for that scientific claim.

**Editorial recommendation: Reject; encourage resubmission as a fundamentally restructured accepted-control paper rather than another incremental revision of R24.**
