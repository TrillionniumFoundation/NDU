# Response to both September 23 R24 reports — Operations Research R27

**Manuscript:** *Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains*  
**Delivery branch:** `revision/ndu-operations-research-r27-20260923`  
**Scientific predecessor:** R26, `38f99a5b46d8cfe4f1197fc869735d5f798c499a`  
**Reports addressed:** the ordinary R24 report at `9080e29443191f9bb415ab0a213af446d4ce3be3`, and the later independent R24 report at `ded3e34349631cd6dc7a4aa35d58a9d248c77d47`. Both reviewed scientific R24 commit `63bbb843e1bbe7cac2170dc7d317d4cf18bb2bb8`.

The revised argument starts from the optimized restricted contract, identifies the value of releasing its information restrictions, implements accepted controls through a sufficient stochastic state, and certifies their gain against the same optimized restriction. We retain the R25 and R26 advances rather than restart from the superseded R24 root or present inherited work as new R27 work. The present revision directly addresses the remaining connection between comparator geometry and reusable economic certification.

## 1. From transfer coordinates to optimizer and value results

**Independent §§3–4, 16, 17.1–17.2; ordinary §§3–5 and 16.1–16.2.**

The transfer identity is a foundation, not the endpoint of the current paper. Retained Theorem 4.1 gives the optimized restriction-release frontier, its active-segment policy, marginal restriction rent, reduced curvature, and first continuation-slack bottleneck. The inverse target calculation determines how much initial release is needed for a specified gain. Retained Theorem 5.1 compares full-class and restricted-class continuation rents, so a capacity increase is not automatically attributed to the adaptation premium. Proposition 5.2 reoptimizes both classes along the friction path and supplies the corresponding value derivative. The exact examples include a rising premium with greater friction and a falling premium under a capacity change. These statements and their proofs remain intact.

R27 adds Theorem 7.3 about the optimized restricted value when continuation matrices, budgets, payment/information equalities, rewards, and friction move together. A normalized switching-price cache supplies a valid upper bound for every query in the stated common-cost family. The theorem identifies the exact four sources of reuse loss: coupled-resource mismatch, coordinate-response error, unused capacity carrying a cached continuation price, and switching-price mismatch. On an explicitly retained priced face, an exact anchor has a quadratic reuse loss, with an explicit constant in EC.11.2. This is a value-loss statement, not a transfer-coordinate substitution.

The local assumptions matter. A new exact two-cap example gives linear reuse loss after a degenerate priced face changes. An approximate numerical anchor is not called exact merely to invoke the quadratic conclusion. The globally valid upper bound and its exact gap decomposition remain usable in those cases.

The paper identifies what these results add operationally: an accepted expansion can be traced from the best implementable restriction, and its economic value can be certified under changed commitments without replacing the restriction by a substantially looser outer class or solving it afresh for every certificate. Weak duality, strong concavity, and parametric optimization are credited as established tools; reproducibility counts do not stand in for the structural claim.

## 2. Restriction classes and the operating institution

**Independent §§4–5, 13, 17.2–17.3; ordinary §§5–6 and 14.**

Section 3 keeps participation at every review primary. The customer can exit before implementation; the announced public service protocol and fixed tariff remain contractible. Root payment equality is an independent contractual commitment, not a consequence silently inferred from a participation inequality. Ex ante participation retains only the root participation row and is explicitly distinguished from continued participation.

The five-level hierarchy uses fixed, scheduled, current-regime, limited-memory, and full-history rules on matched accepted sets. The legacy family pools amendments to heterogeneous inherited tiers; the public-Markov family pools actual tiers. Neither is relabeled as the other. The model explains the implementability restriction behind each comparator, rather than asserting that time-only is universally canonical. The value increments and their ordering dependence remain explicit.

R26's exact omitted-state examples and distance bound are preserved. They separate the value of retaining the payment promise from that of retaining the inherited tier, and distinguish these endogenous states from the public regime. The new R27 comparisons retain the time-only restriction's actual pooling equalities at every query; an easier, unconstrained surrogate is not substituted for the optimized comparator.

The historical master-agreement model remains in its original archive, with its original institution. It has not been retroactively rewritten to imply customer exit rights. Public, verifiable service-level agreements and maintenance subscriptions with periodic cancellation are the motivating retention institutions. No hidden effort, private type, endogenous tariff design, or optimized termination action is claimed.

## 3. Stochastic state and horizon complexity

**Independent §§6, 12, 17.4, 17.8; ordinary §13.**

Retained Theorem 6.1 gives the sufficient state consisting of date, public regime, inherited tier, and exact remaining payment, under the stated Markov and additive-commitment conditions. Retained Theorem 6.2 constructs continuous feasible policies and global value bounds through deterministic mixtures and recursive price planes. Participation and exact promises are maintained in every positive-probability child, including boundary promises.

The six R26 continuum designs, 4,414 lower witnesses, 1,123 upper planes, and exact examples remain unchanged and are independently replayed. These are inherited evidence, not fresh R27 experiments. The distinction between linear tree work and polynomial horizon work is retained. Continuous-state approximation, successor allocation, rational bit cost, and the cost of increasing accuracy are all charged or explicitly delimited.

R27 does not attach a new polynomial-horizon claim to its cache. Its affine-parameter evaluation uses order n(d+1) arithmetic operations per stored price after matrix-price preprocessing. This is a comparator-query arithmetic statement, not a general horizon complexity or measured wall-clock theorem.

## 4. Correlated uncertainty and the loose outer comparator

**Independent §§9, 17.6; ordinary §10 and 16.7.**

The retained radius-refined study and Proposition 7.2 explain why a shrinking outer construction can have a steep local loss without a discontinuity at zero. Its uniform-anchor assumptions remain explicit. We do not infer a mathematical jump from the four earlier radii.

R27 also supplies a tighter construction rather than stopping at that explanation. Theorem 7.3 evaluates the real continuation coefficients, budgets, and equalities at the same parameter vector. It does not independently relax each uncertain row. Normalized switching tensions remain dual-feasible as friction changes, while the stored continuation and equality prices can be reused without being optimal at the query.

Corollary 7.4 addresses unknown coefficients over an entire affine polytope. Fixed-price upper functions are convex in the parameter; a fixed implemented policy's payoff is affine. On each parameter cell, a single cached price is selected outside the vertex minimum, yielding a valid uniform economic-gain lower bound. Cell subdivision and adding cached prices are monotone improvements of this certificate without new comparator solves.

We include an exact positive uniform example with jointly changing reward, friction, and participation coefficients. Four cells certify at least 0.04919921 against the optimized restricted contract, below the exact worst gain 0.05125. The claim covers the continuous interval, not just its evaluated vertices. An exact counterexample shows why choosing the best anchor separately at vertices and then interpolating can produce a false uniform bound; the verifier rejects this operation. We do not exchange the extrema without justification.

## 5. New matched certificate-quality evidence

**Independent §§9–11, 17.6–17.7; ordinary §§10–12.**

Table 5 separates two studies. The first reuses 56 non-anchor queries from the recorded R25 radius design; these are new envelope evaluations of old optimization records, not new optimizer runs. The second uses 24 freshly generated coefficient vectors that are not on those inherited rays. The same 24 historical anchors—three for each of eight contexts—are used in both studies.

For each new query, a true restricted optimization, the historical outer optimization, and a full accepted optimization generate 72 new proposals. Their rational feasible policies and dual bounds are independently recomputed. Query optimizers, values, and duals are not provided to the deployed cache. They are offline evidence for its tightness and for the implemented policies' quality.

Across the 24 new queries, the mean upper slack relative to the certified restricted lower endpoint is at most 0.016632 for the three-price cache, versus at most 0.064069 for the historical outer bound; the exact means and enclosing intervals are in the machine-readable record. All 24 cached bounds are tighter, and all 24 implemented policies have positive cached gain certificates. Their minimum certified gain is at least 0.762195 in the recorded objective units. The independently audited optimizer gaps are below 6e-8 in the local execution; the final published execution is checked against the stated main-text bound and recorded in its manifest.

These are finite designed comparisons, not population confidence statements or calibrated field uncertainty. A finite cache need not dominate every outer bound everywhere. The one-price column worsens with larger perturbations; the full records are retained. The continuous uniform guarantee is Corollary 7.4, not an extrapolation from this pointwise table.

## 6. Online versus offline work and unmatched timings

**Independent §§10–11, 17.7, 18.8; ordinary §§11–12.**

The new operational path is explicit: load the fixed primitives and stored normalized prices, evaluate the actual query coefficients, and compute the scalar conjugates. `query_cache.py` has no optimizer dependency and receives no query optimizer labels. A feasible implemented-policy value minus the resulting upper comparator bound gives the economic-gain lower certificate. A comparator upper bound alone is not advertised as a positive gain.

Initial optimization, storage, exact rational arithmetic, implemented-policy acceptance, and a possible requested refresh are not free. Their costs are separate from the absence of a new restricted solve in the query interface. The 72 fresh optimizations are offline quality checks. Historical and new solver seconds are labeled separately from complete certificate verification. We make no unmatched wall-clock speed claim.

The old robust learned/classical timings remain descriptive accounting because their achieved gains differ. Their complete coordinates and the stronger classical robust certificates are preserved. The new cache is not retroactively inserted into those historical runs. A fair new quality-time study would require a new matched deployment protocol; no such unperformed experiment is claimed here.

## 7. Learning evidence and the amortization correction

**Independent §§7–8, 17.5, 18.1/18.7/18.10; ordinary §§8–9.**

The corrected candidate-minus-lifted identity remains in the current main text: C_off + Q(t_C − t_L). For positive offline cost, a finite crossing requires t_C < t_L. The R24 code's already-correct accounting is unchanged, and its erroneous prose remains traceable only in the preserved predecessor source.

The strict-target 100% learned fallback rates, slower Tanh and RBF totals at all three sizes, unfavorable paired comparisons, and absence of finite observed amortization remain visible. The fixed-policy validation is not turned into a learning theorem. No neural model is fitted in R27, and no adverse learning result is removed to make the new theory look stronger.

## 8. Literature, terminology, and scientific area

**Independent §§14, 17.8, 18.4; ordinary §7.**

The R26 journal-local literature discussion is preserved, including Chen–Sun–Xiao, Liang–Sun–Tang–Zhang, Tian–Sun–Duenyas, Liu–Lewis–Song–Kuribko, and He. It distinguishes private information and incentive provision from the public-state, fixed-tariff retention institution studied here. Continuation price means a dual constraint multiplier; promised payment is a primal recursive state. Neither is conflated with the other.

The Stochastic Models positioning is supported by the state sufficiency and continuous accepted-policy results, in addition to the optimizer-level restriction and rent results. The new comparator certificate supports that contractual-control argument rather than claiming that generic convex duality alone is a new stochastic model.

## 9. Preservation and Operations Research presentation

**Independent §§15, 17–19; ordinary §§15–18.**

The title is retained. The journal-facing main paper and electronic companion preserve every R26 mathematical statement and proof, including the included continuous-state files; R25/R24 and older research files remain unchanged. Thirteen byte-identical R26 root files are copied into the new predecessor directory. `INHERITED_SHA256.json` pins all inherited files, and the package check rejects changes outside the six expressly revised root documents. Earlier computational and historical root PDFs and sources are unchanged.

The new proof and experiment are integrated into the existing comparator-certification section and EC.11, not another disconnected neural or timing layer. The abstract is text-only and 181 words. The introduction remains equation-free. The manuscript uses anonymous 11-point, one-and-a-half-spaced text, one-inch margins, author–year references, and end tables without vertical rules. The compiled main and shorter companion satisfy the Regular format; their actual PDF counts and cross-reference checks are recorded in the final package check.

The point-by-point response distinguishes inherited improvements from R27 contributions. The source, complete new and inherited data, exact counterexamples, independent replay, package checks, and final-commit validation are provided for another substantive examination. Successful tests establish the reported calculations and package integrity; they do not assert editorial acceptance or replace assessment of the mathematical arguments.
