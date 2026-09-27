# Response to the R24 Operations Research referee

**Manuscript:** *Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains*  
**Revision:** R25, September 23, 2026  
**Revision branch:** `revision/ndu-operations-research-r25-20260923`  
**Controlling report:** `reviews/operation_research_referee_report_r24_2026-09-23.md`  
**Review commit:** `9080e29443191f9bb415ab0a213af446d4ce3be3`  
**Reviewed scientific predecessor:** `63bbb843e1bbe7cac2170dc7d317d4cf18bb2bb8`.

We thank the referee for identifying the remaining distinction between a representation of accepted deviations and a theorem about their optimized value. The revision is centered on that distinction. The main result is now the restriction-release frontier, followed by the comparator-adjusted rent decomposition. The transfer bijection is retained as a supporting lemma, not promoted as a deep optimization theorem. The title is retained. All predecessor documents and earlier derivations remain available, including every unfavorable learned-method comparison.

The journal-facing argument is `main.pdf` and `electronic_companion.pdf`. The complete R24 versions are archived byte-for-byte in `revisions/or-r25-20260923/predecessor/`; the former computational record and historical supplement also remain at their existing paths. The current paper is not an appended layer that must be read after the predecessor. It states its institution, principal results, proofs, and new evidence directly. The guide and preservation manifest distinguish the current argument from research history.

## 1. Review object and reproducibility (report Section 1)

The new branch starts from the review commit itself, so the controlling report is included in its ancestry. No review branch or default branch is modified. `PREDECESSOR_SHA256.json` pins the predecessor source, PDFs, bibliography, and reading guides. New source, tables, certificate records, and exact verification code have their own revision directory. The final publication workflow checks the actual published commit rather than only the commit containing a build instruction.

The new scientific evidence comprises 240 hierarchy optimization certificates, 160 true/outer comparator certificates, and 36 cache-anchor/query-validation certificates. Separate exact checks cover 49 release-path witnesses, 40 capacity-rent witnesses, 65 friction witnesses, and 24 rational regular cells. Three finite-action promise problems are checked against all 37,142 deterministic history policies before acceptance filtering. These counts describe verification coverage, not mathematical novelty. `replay.py` uses Python's standard library and reconstructs the models and bounds independently of the numerical optimizer. Nine malformed-evidence controls must be rejected.

The older R24 rational verifier is also run against the preserved records. Its results are not relabeled as new experiments. Numerical timings in the new solver logs are proposal diagnostics; the new work makes no elapsed-time superiority claim.

## 2. Scientific identity and title (report Section 2)

We retain *Accepted Service Adaptation* and keep continued participation and optimized contract restrictions at the front. The abstract now emphasizes the release frontier, its first continuation bottleneck, and the comparator-adjusted capacity/friction effects. The introduction does not present a value-gradient network as the paper's central contribution. The historical value-gradient and Neural Differential Utility results are preserved with their assumptions and proofs in the indexed archive.

This is prioritization rather than withdrawal of valid results. Learned implementations remain part of the scientific record, but the evidence does not support presenting them as the cheapest certified implementation under the tested protocol.

## 3. Beyond a coordinate identity (report Sections 3–4 and requirement 1)

**Changes:** main Section 4, Theorem 4.1 (`thm:release`), equations (7)–(13); EC Section EC.3; exact examples in EC.4.

For the optimized restricted comparator, we release the information equalities through a specified vector of allowable discrepancies while retaining every accepted participation, capacity, box, and payment constraint. The resulting optimized value is continuous, nondecreasing, concave, and piecewise quadratic. Its derivative is the total price of the release bounds, and integrating those prices recovers the value of the restriction expansion.

The regular-cell statement is more specific. A nullspace reduction of the currently binding accepted rows gives an explicit release matrix and reduced curvature. The gain is exactly

`initial restriction rent × release − 1/2 × reduced curvature × release²`

until the first primal, switching-sign, or dual-capacity event. This is the value of the best accepted deviation at each release level, not direct evaluation of an arbitrary direction. The proof supplies a full accepted KKT certificate along the segment. It checks inactive constraints and old active multipliers, not merely the equality-constrained quadratic subproblem.

Unused continuation slack has an explicit operational consequence: a slack subtree can bind first only at its remaining slack divided by its positive payment-consumption rate along this optimal release path. Equivalently, its negative-transfer lower bound is reached at that ratio. Sorting numerical slacks without accounting for their consumption rates would generally identify the wrong bottleneck. The result also inverts the optimized initial frontier to give the minimum release required for a prescribed gain.

The three-node example starts from the already optimized restricted value 5/24. Its first cap binds at release 1/6; its second segment ends at release 3/8 with value improvement 23/192. The relative transfer has coordinate −1/12, using the comparator's existing continuation slack. The entire two-segment optimum, including the dual prices and breakpoint feasibility, is checked exactly.

We explicitly delimit this contribution. Parametric quadratic programming, KKT conditions, and reduced curvature are established tools. The global piecewise description does not require the local regularity conditions, but the signed-corner formula does. Degenerate prices or dependent constraints require the stated refined quadratic problem rather than an invalid matrix inverse. The number of active cells is not asserted polynomial. Nor do we claim that all eventual gain is supported on one cut: the result identifies the first bottleneck and then the next active segment.

## 4. Reoptimizing the comparator changes comparative statics (report Sections 3–4)

**Changes:** main Section 5, Theorem 5.1 (`thm:rents`) and Proposition 5.2 (`prop:friction`); EC.4–EC.5.

Both the full and restricted values increase when accepted capacity is expanded, but their difference need not increase. We derive the premium's directional derivative as the difference between the two optimized continuation rents, with an integral decomposition along the capacity path. At a degenerate point, the right directional derivative uses the minimum projected multiplier and the left derivative the maximum; the two values must be differentiated separately. An arbitrary subtraction of unrelated optimizer multipliers is not justified.

A fully solved example has premium `9(2b−1)²/16` for the continuation cap between 1/4 and 2/3. It decreases to zero at 1/2 and then increases. Both contracts are reoptimized and have explicit stationarity witnesses. This is a positive characterization of which scarcity matters: the difference of rents across contractual classes, not the magnitude of either rent alone.

For switching friction, the premium derivative is restricted-optimum switching minus full-optimum switching. The restricted parametric policy path, coupled with linear feasibility of the full accepted balance certificate, yields the exact no-expansion set on every bounded friction interval. This computes the threshold set without a full-class optimization at every friction value. The set can consist of intervals and isolated points, rather than a universal upper ray.

The exact friction example has premium `lambda²` up to 1/4 and `lambda/2−1/16` thereafter. A restriction forces a tier difference, so greater switching friction increases the value of removing it. This does not contradict the earlier zero-switching constant-comparator result: that result has a different restriction and benchmark. We retain it in the archive and do not apply it outside its assumptions.

## 5. Which restriction is economically relevant? (report Section 5 and requirement 2)

**Changes:** main Sections 3.2, 5.3, and 8.1; Table 1; EC.9.1–EC.9.2.

There is no assertion that time-only is the canonical restriction for every operation. We compare five predeclared nested classes on each instance: fixed, time-only, current-regime, two-period-memory, and full-history. Each optimized value uses the same objective and accepted rows. The increments sum to the total expansion value, but their allocation is conditional on the ordering of information features, not an invariant causal or Shapley decomposition.

The legacy experiment needed an additional distinction. It pools amendments to heterogeneous legacy tiers. Equal amendments are not equal actual tiers, and a regime annotation does not make arbitrary historical coefficients Markov. We now say so explicitly. Exact root payment makes the fixed-amendment class the singleton zero amendment; its value is obtained algebraically rather than presented as a numerically optimized nontrivial constant tier.

A second, separately specified public-Markov family has a common baseline, Markov rewards/curvature/conditional caps, and the same five restrictions on actual tiers. It addresses the literal contract hierarchy without changing the interpretation of the legacy data. There are 24 seeded contexts in each family and no dropped instances. In the executed record, approximately 67.36% of the legacy total comes after two-period memory, whereas approximately 99.34% of the Markov-family total comes from moving from time-only to current-regime control. These are within-family shares; their raw objective units differ and are not compared cardinally.

Small memory/full-history increments can be zero within the certified bracket on individual Markov instances. Regime-only control still omits the inherited tier and remaining promise. Thus the results do not refute the sufficient augmented-state formulation. The enclosing interval for each optimized increment is retained; tiny lower-endpoint differences are not manufactured into positive effects.

## 6. Continuation participation is now the primary institution (report Section 6 and requirement 3)

**Changes:** main Section 3.1, equation (2), and Section 6; EC.1.

The customer can leave before implementation at every public review, while the provider commits to its contingent protocol. We derive each subtree payment cap by multiplying conditional customer participation by the node's discounted probability. The customer's utility, premium, indemnity, service level, and outside continuation are stated first. Ex ante participation is then the special case retaining only the root row. A root payment equality is a separately stipulated commitment, not an equality inferred from participation.

The model is a verifiable service-level agreement. Regime, demand, fulfillment, tiers, and transfers are public and contractible. There is no private type, hidden effort, or incentive-compatibility claim. Termination is not an optimized action in this retention model; adding it would require a different control. Stock can be specified, or identified by the physical service/cost commitments whose retained proof is in EC.1. Without those conditions, stock cannot silently be removed.

The quadratic accepted model permits linear components of convex operating costs as well as net receipts, so the reward vector is not incorrectly equated with the root payment coefficients. The exact structural examples and designed Markov study are instances of this stated accepted quadratic model, not claimed estimates of an inventory system.

## 7. Operations Research dynamic-contract boundary (report Section 7 and requirement 4)

**Changes:** main Section 2 and bibliography.

We explicitly compare with Chen, Sun, and Xiao, *Optimal Monitoring Schedule in Dynamic Contracts*, Operations Research 68(5):1285–1314 (2020), DOI 10.1287/opre.2019.1968, and Liang, Sun, Tang, and Zhang, *Efficient Resource Allocation Contracts to Reduce Adverse Events*, Operations Research 71(5):1889–1907 (2023, first online in 2022), DOI 10.1287/opre.2022.2322.

The comparison distinguishes information, participation, state, and structural object. Those papers solve dynamic incentive problems with unobserved effort, monitoring or resource allocation, and recursive promised utility/self-generating structure. Our paper has public-state service controls, fixed transfer schedules, and an optimized restriction-release problem. Its continuation price is a **dual multiplier**, not promised continuation utility. Its remaining-payment promise is a **primal recursive state**. We do not claim to invent promised-state dynamic programming or solve their incentive problems.

We also explicitly attribute the general convex-sensitivity, multiparametric quadratic-programming, generalized-lasso, and robust-containment tools. The paper's structural claims are the identified restriction rents, continuation-slack bottlenecks, and comparator-adjusted value consequences under its institution.

## 8. Learning is implementation evidence, not an unsupported speed claim (report Section 8 and requirement 6)

**Changes:** main Section 8.3 and Table 4; complete predecessor records retained.

The strict-target table is generated directly from the unchanged R24 analysis JSON. Both learned routes fall back in all measured cases at every size; their paired saving intervals are negative. The coarse target also has no observed finite learned amortization crossing. We preserve optimizer label cost, fitting, prediction, audit, polishing, fallback, and all individual cases. We conduct no new learned-method race and do not use additional neural variants to distract from the referee's structural requirement.

The robust comparison achieved materially different gains. The roughly 20-millisecond differences are explicitly described as bookkeeping at different quality, not dominance or a matched-quality computational result. The complete gain–time coordinates remain in the archived computational record. Because the revised main paper no longer uses that comparison as a performance claim, it does not present three points as a Pareto frontier.

## 9. Amortization algebra corrected (report Section 9 and requirement 5)

**Change:** main equation (23), label `eq:amortization`.

With candidate-minus-lifted accounting, the difference is `C_off + Q(t_C−t_L) = C_off−Q delta`, where `delta=t_L−t_C`. For positive incremental offline cost, a finite positive crossing requires `t_C<t_L` and occurs at `C_off/(t_L−t_C)`. Strict savings require a larger query count. The manuscript now matches the already-correct R24 analysis code. A sign-reversal negative control is rejected by the new verifier. The corrected equation does not alter any historical numerical conclusion.

## 10. Positive-radius outer-comparator loss (report Section 10 and requirement 7)

**Changes:** main Proposition 7.2 (`prop:outer`), Section 8.2 and Table 2; EC.8.

Inspection of the actual old construction shows that its outer radius already shrinks continuously to the nominal set. It did not replace radius zero with a fixed large union-containing set at every positive radius. The coarse observations therefore could not establish a jump.

We provide a local error theorem. Under a common strict reduced-coordinate anchor and a uniform row-perturbation bound, mixing an outer optimizer with the anchor yields true feasibility with movement at most the largest `2 rho eta/(gamma+2 rho eta)`. A Lipschitz objective then bounds outer-comparator value loss by the diameter times that fraction. This is an explicit O(radius) bound; its constant reflects small accepted margins. No rate is asserted without the stated anchor.

We also perform a new fixed-context sweep down to radius 1/65536, optimizing both true and outer comparators directly at ten radii. The observed mean outer slack is approximately 0.0000474 at that smallest positive radius, versus 0.07377 at 1/16. It approaches zero and rises steeply before the old study's first positive point. This explains the sampled plateau without claiming the old certificate was exact.

The companion gives equality-aware and successive outer-set envelope refinements with a containment proof. These are available analytic constructions, not retroactively credited for the new numbers: the reported fine-radius experiment intentionally uses the original box envelope. Both old and new uncertainty sets remain designed and uncalibrated.

## 11. Robust quality–time comparison (report Section 11)

The relevant achieved gains and costs are retained together in the predecessor computational record and raw R24 files. We no longer include the unmatched robust timing table among the current main-paper computational findings or imply that faster prediction compensates for materially lower guaranteed gain. No invented matched-quality benchmark or unexecuted Pareto frontier is substituted. The new evidence concerns contract-class value, local outer-comparator loss, and reusable upper bounds.

## 12. Reducing repeated comparator work (report Section 12 and requirement 9)

**Changes:** main Section 7.1, Proposition 7.1 (`prop:cache`), Table 3; EC.7.

We separate accepted-policy deployment, pointwise economic certification, and offline validation. A new comparator need not be solved every time a feasible policy is deployed. When an economic certificate is required and only reward coordinates vary over a fixed accepted restricted set, a cache of certified anchors supplies a reusable upper envelope.

The bound uses restricted-space curvature and includes the error in each approximate optimizer anchor. This error is not silently dropped. An exact rational trace bounds the required eigenvalue, and the square-root terms are rounded outward. Taking the minimum over valid anchor envelopes remains valid. Query arithmetic uses stored low-dimensional reward/resource coordinates; it makes no new restricted optimization call. Geometry, commitment, or friction changes invalidate the fixed-geometry premise and need a different cache or new certification.

The executed study builds four anchors and checks 32 nearby queries, with a maximum envelope-minus-certified-lower gap approximately 0.00024849. Those 32 optimizer solves are **offline validation**, not secretly omitted online work. The four anchor solves, storage, policy acceptance, and misses remain costs. This addresses a reusable comparator mechanism without claiming a measured end-to-end speedup for the older uncertain-geometry robust protocol.

## 13. Tree versus horizon complexity (report Section 13 and requirement 8)

**Changes:** main Section 6, Theorem 6.1 (`thm:recursion`); exact finite-action checks.

The root commitment is an exact remaining conditional payment promise. The Bellman state consists of date, public regime, inherited tier, and that promise. The current action allocates child promises satisfying the conditional payment recursion, and every child promise is capped by that child's participation obligation. An induction proves equality with the full history-tree value and constructs a deterministic state-based optimum. With several additive commitments, the promise becomes a vector.

The assumptions are explicit: transitions, rewards, action feasibility, and outside continuation caps must have the displayed Markov representation; missing physical state or nonadditive history constraints must be added. Regime alone is not sufficient. An arbitrary selected full-history optimizer need not preserve distinctions between equivalent states; the existence of an equivalent state-based optimum is the assertion.

The paper states the exponential history-node count in horizon and the continuous-state cost of the recursion. A finite grid is an approximation unless actions and attainable promises are genuinely finite. Child-promise allocation and the number of commitment coordinates can remain expensive. We do not claim that an O(nodes) transfer map is an O(horizon) solver. The exact finite-action tests compare every attainable root promise with exhaustive policy enumeration and are labeled as such.

## 14. Scope of the public-state institution (report Section 14)

The institution is now stated before the general accepted polyhedron. It is contractually constrained service adaptation with verifiable outcomes and customer exit rights, not a general theory of moral hazard or private-information contracting. This limitation is not used to retreat from the accepted-control results. Instead it identifies where continuation participation, the restriction being released, and the promised-payment state have direct operational meaning.

## 15. A shorter theorem chain without deleting the record (report Section 15 and requirement 10)

The current main chain is: accepted continuation and optimized restrictions; restriction-release value and its bottleneck; comparator-adjusted capacity/friction rents; sufficient promise state; implemented-gain certification. The transfer representation and balance theorem are foundational results, not parallel novelty claims. Auxiliary proofs and exact specification are in the formal EC. Historical value-gradient/NDU, repair generations, and timing archaeology are in a separately indexed complete archive.

The R24 source/PDF pairs are preserved byte-for-byte; earlier revision and review directories are not rewritten. Thus reducing the journal-facing narrative does not remove derivations or hide unfavorable measurements. The preservation guide names which prior materials support which retained foundations.

## 16. Required-action checklist (report Section 16)

All ten requested actions have concrete manuscript or evidence destinations: (1) Theorem 4.1 and Section 5; (2) five-class Table 1; (3) Section 3.1; (4) Section 2; (5) corrected accounting equation; (6) Section 8.3 and archived negative results; (7) Proposition 7.2 and Table 2; (8) Theorem 6.1 and its complexity discussion; (9) Proposition 7.1 and Table 3; (10) the core/EC/archive separation and preservation manifest. This checklist records the response locations, not a claim that a referee must judge every scientific concern resolved.

## 17. Presentation (report Section 17)

The title is unchanged. The abstract is 182 words and contains no mathematical notation. The introduction is equation-free. The anonymous manuscript uses 11-point type, one-inch margins, one-and-a-half spacing, author–year references, and tables after references. We distinguish exact proofs and rational certificates from numerical optimizer proposals. Continuation price and promised payment are defined as different dual and primal objects. Package counts remain in this response and the reproducibility guide, not the novelty argument. The complete current PDFs are checked for unresolved citations/references and overflowing lines.

## 18. Closing response (report Section 18)

The revision responds to the theory-centered request with an optimized release frontier and comparator-adjusted structural effects, rather than another neural or certificate layer carrying the publication claim. The data stress-test the restriction itself and preserve the negative implementation conclusion. The new branch is submitted for another substantive referee examination; build success and exact replay are not substitutes for that assessment or guarantees of journal acceptance.
