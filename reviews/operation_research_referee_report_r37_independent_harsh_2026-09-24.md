# Confidential Referee Report for Operations Research

**Manuscript:** *Service Contracts with Limited Memory: Participation, Randomization, and Exact Design*  
**Revision reviewed:** `revision/ndu-operations-research-r37-integrated-frontier-20260924`  
**Reviewed scientific source commit:** `0afd833f6d0f16195579399334426aebd3ea1b20`  
**Predecessor independent report:** `reviews/operation_research_referee_report_r36_independent_harsh_2026-09-24.md`  
**Predecessor review commit inherited by R37:** `f26f4da71207a7613735b0504bc34dbe231813c1`  
**Review branch:** `review/operation-research-r37-independent-harsh-20260924`  
**Date:** September 24, 2026  
**Recommendation:** **Reject in the present form. A substantially better-positioned and more robust resubmission could merit fresh review.**

---

## Executive assessment

R37 is a major and serious reconstruction of R36. It is not another additive theorem layer.

The authors have done several things I explicitly asked for in the previous report. They have rebuilt the main article around one restricted-memory service-design problem; moved much of the cumulative response-compiler material to the electronic companion; changed the proposed area to Optimization; confronted the partial/staircase Monge literature; stated clearly that the easy-direction completion and SMAWK are classical; expanded the total-monotonicity proof to cover ties, wholly padded selected rows, predecessor reachability, and previous-layer column offsets; supplied a concrete timing protocol for expected versus pathwise participation; added a bounded-overrun variant; separated writable bits from read-only representation and evaluation work; and extended the computational study to larger instances, an independently authored matrix-search implementation, and externally assembled HiGHS network solves.

The resulting paper is much better. The R36 priority objection about staircase matrix search is, in my view, **substantially resolved**. I do not presently see a simple counterexample to the cap-anchoring theorem, the continuously minimized terminal Monge identity, the expected/pathwise separation, the one-sided completion lemmas, or the exact frontier reconstruction. The current build and regression discipline are also unusually strong.

I nevertheless cannot recommend publication in *Operations Research*.

The reason has changed. Once the paper is correctly reconstructed around a **small retained service code**, the natural neighboring literature is no longer only dynamic contracting and Monge dynamic programming. The mathematical object is also a **finite-level scalar quantizer / rate-limited codebook**, and the expected-participation encoder is, branch by branch, an **adjacent unbiased stochastic quantizer**. This is not a superficial analogy. The deterministic theorem groups ordered scalar branch states into contiguous cells and assigns a common reconstruction level; the randomized theorem maps a branch target to the two adjacent codewords with distance-proportional probabilities so that the mean equals the target; the code budget is a finite alphabet; and the linear frontier algorithm follows the same dynamic-programming-plus-matrix-search pattern that has appeared in optimal scalar quantization for decades.

The current R37 bibliography and positioning section do not discuss scalar quantization, optimal quantizer design, stochastic rounding, or communication-constrained control at all. This is now a material priority and significance gap. For example, Xiaolin Wu's 1991 paper *Optimal quantization by matrix searching* already takes a K-level discrete scalar quantization dynamic program from quadratic time per level to **O(KN)** using matrix searching. The objectives are not identical, and that paper does not appear to prove the authors' contractual cap-anchoring or continuously minimized highest-level result. But the algorithmic pattern is so close that an R37 paper titled around a limited code cannot claim a verified novelty boundary without confronting it. Likewise, the paper's adjacent mean-preserving lottery is mathematically the same local randomization rule that the stochastic-rounding literature calls mapping to the two nearest adjacent levels with probabilities chosen to preserve the mean. Again, the service objective is different; the point is that the randomization primitive is established and must be separated from the genuinely new contractual result.

There is a second, more conceptual problem. Almost every clean frontier statement rests on the **saturated root promise**
[
ar b=sum_jpi_j b_j,
]
which forces every branch participation cap to bind. That single equality is doing enormous structural work: it identifies the full-information action, converts participation into a mean-preserving representation problem, creates the exact stochastic-rounding interpretation, and makes the pathwise randomization theorem collapse to the deterministic frontier. The paper is candid about the assumption, but it does not yet establish whether the headline conclusions are robust to slack root promises, endogenous continuation budgets, repeated participation, or other economically natural departures. A nonsaturated two-branch example from the historical theory is not a robustness theorem for the restricted-memory frontier.

The bounded-overrun material helps interpretation but does not solve this problem. The general result is only a fixed-codebook rule under an additional pre-draw intermediate-action restriction; the global optimization result is one three-branch, two-code example. It is therefore too narrow to function as a general bridge between the two headline institutions.

Finally, the new "integrated" resource objective is mostly an outer enumeration over an already computed loss frontier plus exogenously specified prices. It is useful accounting, but it is not yet a deep joint implementation-design theorem. The authors explicitly concede that if read-only cost depends on the particular codebook, the one-dimensional frontier is insufficient. That caveat is correct—and it also limits how much operational significance can be assigned to the resource-pricing section.

The paper is thus in an unusual position. Its correctness case is stronger than ever, but the reconstruction has made the relevant neighboring literatures and the knife-edge structural assumptions easier to see. At a top OR journal, that is enough to stop the paper again.

My recommendation is **Reject in the present form**, not because R37 failed to respond to R36—it responded very well—but because the correct R37 framing creates a new and more fundamental novelty/robustness burden that the manuscript has not yet met.

---

# 1. Version audit: R37 is a genuine reconstruction

The reviewed scientific source is commit

`0afd833f6d0f16195579399334426aebd3ea1b20`.

The validated reader is materially different from R36.

The current build record reports:

- 32 total main-paper pages;
- 30 main-paper pages excluding references, including title and tables;
- a 27-page electronic companion;
- a 182-word abstract;
- 11-point type, one-and-a-half spacing, and one-inch margins;
- proposed area: Optimization;
- no undefined citations or references;
- no overfull boxes;
- 784 completed completion-test matrices;
- 282,832 selected-submatrix row-minimum checks;
- 98,728 wholly padded selected rows;
- 1,890 exact frontier equalities and direct controller replays;
- 190 bounded-overrun all-pairs equalities;
- 33 solved tolerance-frontier evaluations;
- unchanged R33--R36 regression suites passing in isolation;
- 24 externally assembled HiGHS cases with exact reduced-network certification.

The current paper also gives a precise preservation map and identifies the previous R36 reader and independent report by immutable commit.

This is strong revision hygiene. I do not regard R37 as a cosmetic response.

---

# 2. What R37 convincingly fixes

Before giving the new objections, I want the record to be clear about what is now substantially satisfactory.

## 2.1 The paper finally has one main identity

The main article is now about a restricted-memory renewal/service-code design problem:

1. a branch-specific accepted continuation is observed;
2. only a small symbol crosses a later execution boundary;
3. deterministic and randomized codebooks are optimized;
4. participation timing changes the feasible randomization;
5. the complete loss frontier is computed exactly.

This is a much better article than the R36 union of compact response compilation, machine minimization, piecewise-quadratic closure, randomized memory, Monge acceleration, and several historical algorithmic layers competing for attention.

The companion is still broad, but the main-paper identity is now intelligible.

## 2.2 The partial/staircase Monge priority problem is substantially repaired

The current related-work section correctly distinguishes:

- quadrangle-inequality dynamic programming;
- full totally monotone matrix search;
- partial/staircase matrix search;
- model-specific contractual cost structure.

It cites Klawe--Kleitman, Chan, Kaplan--Mozes--Nussbaum--Sharir, and Emmerich in addition to Yao and Aggarwal et al.

More importantly, it does not merely add citations. It says what I believe is the right thing: the contractual arrays fall into a favorable one-sided staircase orientation for which direct completion and ordinary SMAWK are classical consequences once the finite costs have the required Monge order.

I no longer regard "the authors ignored the relevant partial-Monge literature" as a valid rejection reason for R37.

## 2.3 The completion proof is now proportionate to its role

The main paper separately proves suffix and prefix completion, fixes the finite left-tie convention, chooses opposite internal orders for left and right padding, covers fully padded selected rows, proves previous-layer column offsets, proves the exact reachable predecessor intervals, and matches these statements to three explicit search interfaces.

That is the level of proof R36 needed.

The finite all-submatrix tests now function appropriately as implementation regression tests rather than as a substitute for the theorem.

## 2.4 The expected-versus-pathwise timing is now explicit

The renewal-desk/dispatch-gateway mechanism is stylized, but it finally states:

- who observes the branch;
- which information crosses the execution boundary;
- when the customer accepts;
- when the private draw occurs;
- what a later disclosed realization means;
- why a retained seed is not free memory;
- why a hard realization cap requires the pathwise model;
- why repeated customers require an enlarged state.

This is a substantial improvement over R36.

## 2.5 The computational claims are more disciplined

The authors now distinguish:

- exact theorem verification;
- search-implementation substitution;
- reduced-network external solver comparison;
- wall time;
- resident memory;
- Python-tracked heap;
- arithmetic versus search overhead;
- rational-operation complexity versus finite-precision performance.

They also report unfavorable small cases and do not claim uniform speed dominance.

This is good scientific practice.

---

# 3. New major blocker: the paper is now a quantizer-design paper but does not engage the quantization literature

This is the most important issue in R37.

The authors' reconstruction correctly strips the problem down to a small alphabet passed from an informed renewal desk to a common execution gateway. Mathematically, that produces a finite-level encoding/decoding problem.

The paper should therefore answer the following question directly:

> What is new here relative to classical scalar quantization, randomized/unbiased quantization, and rate-limited/quantized control?

At present it does not.

## 3.1 The deterministic frontier has the form of ordered scalar quantization

Under the saturated renewal model, branch (j) has target cap (b_j). A deterministic codebook selects finitely many terminal levels. Branches assigned to one symbol share one terminal reconstruction level.

The paper proves that optimal cells are contiguous in the ordered caps and that a cell (i,ldots,j) uses reconstruction (b_i), with distortion
[
C(i,j)=sum_{h=i}^jpi_h
{f(b_h)-f(b_i)+h_h(b_h-b_i)}.
]

This is, mathematically, an ordered scalar clustering/quantization problem with a particular one-sided reconstruction rule and a branch-dependent distortion.

The segmentation recurrence is classical, as the authors already say. But the correct neighboring literature is not exhausted by saying "segmentation is standard."

The quantization literature has studied optimal K-level scalar quantizers, contiguous cells, dynamic programming, and accelerated matrix-search implementations for decades.

A particularly direct missing comparison is:

**Xiaolin Wu (1991), "Optimal quantization by matrix searching," Journal of Algorithms 12(4):663--673, DOI 10.1016/0196-6774(91)90039-2.**

Wu starts from a K-level discrete scalar quantization dynamic program with an (O(KN^2)) bound and obtains (O(KN)) using the Aggarwal et al. matrix-search technique.

I am not claiming that Wu solves this service-contract distortion. The mean-square distortion is different. The reconstruction rule is different. The expected-participation continuous highest level is absent. Those differences may contain the real novelty.

But after R37, an (O(mk)) codebook frontier reached by Monge structure and matrix searching cannot be positioned responsibly without this literature.

The current paper discusses Emmerich's recent Monge-DP application but misses a 1991 paper whose title is literally *Optimal quantization by matrix searching*.

That is a serious priority-audit failure.

## 3.2 The expected-participation lottery is mathematically an unbiased adjacent stochastic quantizer

For a fixed ordered codebook (c_1<cdots<c_s), R37's expected-participation theorem sends a branch target (mu_j) to the two adjacent levels bracketing it. The probabilities are chosen so that
[
mathbb E[C_j]=mu_j.
]

This is exactly the local mathematical primitive usually called stochastic rounding or unbiased randomized quantization: map a scalar to its two adjacent representable levels with distance-proportional probabilities so that the expectation equals the original scalar.

For example:

**Croci, Fasi, Higham, Mary, and Mikaitis (2022), "Stochastic rounding: implementation, error analysis and applications," Royal Society Open Science 9:211631, DOI 10.1098/rsos.211631.**

That survey describes stochastic rounding as mapping a real scalar to the next smaller or larger representable value, with probabilities determined by relative distance. The mechanism is old and widely used.

Again, the paper's contractual objective is not numerical roundoff, and the institutional interpretation is potentially new. But that is exactly why the authors must say:

- the **adjacent unbiased lottery primitive is classical**;
- the new claim, if any, is that the participation and cost structure makes that primitive globally optimal inside this service contract;
- the cap-anchored codebook theorem and continuous top level are the model-specific part;
- the value difference between ex ante and pathwise participation is a contractual feasibility statement, not a discovery of adjacent unbiased randomization itself.

Right now the paper presents the fixed-codebook adjacent lottery as if its closest intellectual parent were the earlier deterministic memory theorem. That is too local a comparison.

## 3.3 "Writable service code" also sits inside communication-constrained control

The manuscript's observation architecture is:

- an informed component observes a branch/history;
- only a finite symbol is transmitted/retained;
- a downstream controller/decoder acts using the symbol plus public state;
- bit capacity is scarce;
- read-only programs and communication/state memory are distinct.

This is a standard information-constrained control architecture in broad form.

There is an extensive quantized-feedback and control-under-communication-constraints literature, including finite-level quantized control and minimal-information questions. A modern tutorial is:

**"A Tutorial on Quantized Feedback Control," IEEE/CAA Journal of Automatica Sinica (2023/2024), DOI 10.1109/JAS.2023.123972.**

That literature is not identical to a renewal contract: it often studies stabilization, dynamic plants, noisy measurements, and feedback channels. But the manuscript's general language about a scarce writable alphabet and an execution gateway risks sounding more novel than it is unless this neighboring field is acknowledged.

The authors do not need a fifty-paper control survey. They do need a clear boundary:

- What is specifically contractual rather than generic finite-rate control?
- Which lower bounds concern participation and continuation promises rather than communication alone?
- Which codebook-design results would remain true if all contract language were replaced by scalar source points and a distortion function?
- Which results genuinely require the contractual saturation and participation institution?

## 3.4 This priority gap affects the paper's strongest claims

This is not a bibliography cosmetic.

It changes how I read at least four headline results:

1. **Deterministic contiguous cells:** likely a special scalar-quantizer/segmentation structure with a contractual distortion.
2. **Adjacent randomized encoding:** a classical unbiased adjacent quantizer under a contractual feasibility condition.
3. **Linear matrix search:** a known quantizer-DP acceleration pattern once the particular distortion is Monge.
4. **Writable bits:** a finite-rate code budget, a standard resource in communication-constrained control.

The remaining potentially distinctive claims are narrower and, in my view, more interesting:

- cap anchoring of all nonhighest randomized levels;
- a continuously optimized highest level that can be strictly off-cap;
- preservation of the Monge inequality after that continuous minimization;
- the sharp expected-versus-pathwise feasibility separation under the saturated renewal institution.

Those should be the publication case.

But until the manuscript is rewritten against the correct quantization/control baseline, I cannot verify that even these claims are new in the relevant form.

---

# 4. The saturated root promise is a structural knife edge, not a harmless normalization

The paper now states the saturated root promise early, which is good:
[
sum_jpi_jmathbb E[Y_j+C_j]
=sum_jpi_jb_j.
]

With positive probabilities and branchwise upper bounds, this forces **every branch cap to bind**.

The manuscript is explicit about this. The problem is not hidden assumptions. The problem is how much of the headline theory depends on this one equality.

It drives:

- (Y_j+C_j=b_j) in expectation under the expected-participation model;
- (Y_j+C_j=b_j) almost surely under pathwise participation;
- the full-information solution (Y_j=0,C_j=b_j);
- the mean-preserving randomized-quantizer interpretation;
- the deterministic cell cost;
- the pathwise theorem that randomization cannot help;
- the clean exact-memory threshold when all (b_j) are distinct.

This is an extraordinarily strong structural device.

## 4.1 What happens when the root promise is slack?

Suppose instead that
[
sum_jpi_jmathbb E[Y_j+C_j] < sum_jpi_j b_j.
]

Then not all branch caps must bind. Some continuation slack can be allocated across branches. The branch target is no longer mechanically (b_j). The encoder and service decisions interact with an allocation of the root promise itself.

Several R37 reductions may break or change:

- the reconstruction level of a deterministic cell need not be its smallest cap;
- the expected-participation lottery need not preserve each (b_j);
- the pathwise deterministic equivalence may fail in its stated proof form;
- the cap-anchoring theorem may require a different anchor set;
- the Monge cost may change;
- the relevant finite-rate decision may become a joint promise-allocation/quantizer design.

That is not an obscure perturbation. A saturated aggregate promise is exactly the boundary at which all local upper bounds are exhausted.

The paper needs to tell the reader whether this is:

1. the economically natural case of interest;
2. a deliberately sharp special case used to expose a new phenomenon;
3. one endpoint of a broader theorem.

At present it oscillates between (1) and (2).

## 4.2 The old nonsaturated example is not enough

The main article briefly retains an earlier nonsaturated two-branch example. That example is useful for showing that public-only execution can lose value even without saturation.

It does **not** establish that the R37 restricted-memory frontier, randomization gap, codebook structure, or pathwise theorem are robust away from saturation.

A top-journal paper centered on the institutional value of memory should do more.

I would want at least one of:

- a general theorem for an interval of root promises below saturation;
- a structural characterization showing exactly which R37 conclusions survive and which fail;
- a counterexample map that honestly identifies saturation as the boundary of the theory and shows why that boundary is operationally central.

Without this, the main result is closer to an elegant exact solution of a knife-edge coding model than to a broadly informative service-design theorem.

---

# 5. The expected-versus-pathwise insight remains interesting, but the bounded-overrun section is not yet a general bridge

R37 improves the institutional story considerably. I now understand the modeled timing.

The remaining issue is the strength of the intermediate result.

## 5.1 The general bounded-overrun result fixes the codebook

The general proposition says, for a **fixed** codebook and a pre-draw intermediate action:

- if the next codeword above (b_j) lies within the overrun tolerance, use the adjacent mean-preserving lottery;
- otherwise use the highest codeword below the cap deterministically.

This is a clean result.

But it does not solve the global bounded-overrun codebook problem.

## 5.2 The global result is one three-branch, two-code example

The paper then solves one heterogeneous three-branch example and obtains
[
z_delta=rac12+min{delta,1/8}.
]

This is a nice illustration. It shows continuous movement from the deterministic endpoint to the unrestricted expected-participation optimum.

It is not a general frontier theorem.

In particular, the paper explicitly does **not** prove that under bounded overrun:

- all but the highest level remain cap anchored;
- the global problem has the same dynamic program;
- the terminal cost remains Monge;
- the full budget frontier remains linearly searchable.

That caution is correct. It also means the section should not carry more editorial weight than it has.

## 5.3 The pre-draw intermediate-action restriction matters

The intermediate model requires (Y_j) to be fixed before the ticket draw.

The authors explicitly say this is not claimed without loss for every bounded-risk model.

Good.

But then the bounded-overrun institution is not simply a continuous interpolation between the two original institutions. It is one particular third institution with an extra timing restriction. At (delta=0) the endpoint agrees with the stronger pathwise theorem, and at sufficiently large (delta) the solved example agrees with the expected model, but the interior is model-specific.

The abstract currently says "A bounded-overrun mechanism makes the institutional tradeoff explicit." That is defensible. Stronger language about a general bridge would not be.

For publication, I would either:

- generalize the bounded-overrun frontier enough that it becomes a genuine third theorem family; or
- demote it to an interpretive example and keep the two endpoint institutions as the formal core.

---

# 6. The "integrated implementation-resource accounting" is useful accounting, not yet a substantive joint optimization theorem

The resource section introduces
[
min_{I,m,t}
left{
D_m^I
+lambda_wlceillog_2mceil
+lambda_R R_{I,t}
+lambda_T Q_{I,t}
+C_{I,t}/H
+kappa_I
ight}.
]

This is a sensible way to prevent "few writable symbols" from being confused with "small implementation."

I support including such accounting.

But the paper oversells it if it is presented as a major integrated design contribution.

## 6.1 The difficult codebook optimization has already been solved before the resource objective is formed

For each institution (I) and capacity (m), (D_m^I) is already the minimum service loss.

The new step is then a finite comparison across capacities and implementation menu entries under exogenously supplied prices.

When the charges (R,Q,C) depend only on the menu entry and declared capacity, this outer minimization is almost tautological.

## 6.2 The paper itself identifies the important case it does not solve

The manuscript correctly says that if read-only representation cost depends on the actual codebook, the loss-minimizing codebook need not minimize total service-plus-storage cost.

That is precisely the more interesting integrated design problem.

Likewise, communication complexity may depend on:

- entropy rather than fixed-width capacity;
- unequal codeword probabilities;
- variable-length codes;
- decoder-table regularity;
- numerical precision of individual levels;
- branch-specific encoder complexity;
- correlated reuse across repeated service episodes.

The current objective intentionally fixes those issues outside the theorem.

That is fine as a scoped accounting framework. It is not yet a reason by itself for *Operations Research* significance.

## 6.3 The one-bit versus two-bit example is algebraically informative but not deep evidence

The three-branch example shows that for a bit price between (1/96) and (1/8), expected participation selects one writable bit whereas pathwise participation selects two.

This is a clear illustration of the loss-frontier difference.

But once the two losses are known, the threshold comparison is immediate. It does not validate an operational cost model for gateway certification or communication.

I would retain the example but present it as interpretation, not as an additional optimization theorem.

---

# 7. The computational section is now strong verification, but still weak evidence of operational importance

The current computational package is much better than R36.

At 16,384 branches and budgets through eight, the reported exact-rational implementation gives:

- expected participation: approximately 26.6 seconds for the retained SMAWK implementation versus 37.4 seconds for divide-and-conquer;
- pathwise participation: approximately 44.1 seconds versus 52.1 seconds.

The independently authored PADS search layer is slightly faster again in the reported largest cases. The paper also reports memory and profile decomposition, and the exact arithmetic itself dominates runtime.

These are useful results.

They support the claim that the algorithm has the intended scaling in the implementation tested.

They do not solve the significance problem.

## 7.1 The large study is one synthetic structured input family

The large-scale instances use one deterministic pattern for caps, probabilities, and curvatures.

There are heterogeneous random rational instances in the verification suite, but the performance story is not a broad computational study across qualitatively different cost landscapes.

That is acceptable for a theorem paper. It simply means the computation should not be used to compensate for a narrow model.

## 7.2 PADS substitutes only the search layer

This is exactly the right way to test whether the authors' own SMAWK code is responsible for the results.

It is not an independent algorithm for the economic model. The moments, cost oracle, and reconstruction are shared.

The manuscript is transparent about this.

## 7.3 HiGHS checks the finite reduction, not the core continuous reduction

The external network is assembled independently from branch sums, which is valuable.

But it still uses the paper's analytically derived continuously minimized terminal costs. Therefore HiGHS does not independently test:

- cap anchoring;
- the reduction of the continuous codebook problem to the finite network;
- the participation interpretation.

Again, the manuscript says this correctly.

## 7.4 The missing comparator is now quantization, not another Monge routine

Given the new priority issue, I would much rather see a comparison or at least a conceptual implementation mapping to a standard scalar-quantizer DP than another bespoke search engine.

If the authors believe the contractual distortion puts the problem outside classical optimal quantizer algorithms, they should demonstrate exactly where.

---

# 8. The main paper is more focused, but the companion still functions as a second paper

The main article is now 30 nonreference pages, a meaningful improvement over R36.

The electronic companion is 27 pages and contains:

- compact response quotient theory;
- tight response-size results;
- piecewise-quadratic closure;
- minimal reached transducer theory;
- dispersion;
- shared-table comparison;
- laminar polymatroid details;
- coefficient-event compilation;
- bit bounds;
- additional behavioral-quotient examples;
- divide-and-conquer material.

Some of this supports the main paper. Much of it is a preserved historical research program.

The preservation motive is understandable. A repository can and should retain history.

A journal electronic companion should be optimized for the current paper, not for preserving every theorem previously developed in the repository.

The main article itself says that the broader compact-response theory is "retained" in the companion. That wording reveals the issue: retention is a version-control goal, not an editorial criterion.

I recommend separating:

1. a **submission companion** containing only proofs, implementation details, and extensions directly needed by the current paper; and
2. a **repository archive** preserving the broader historical NDU theory.

This would make the scientific unit easier to evaluate and would further improve the contribution-to-length ratio emphasized by the current Optimization area statement.

---

# 9. Correctness comments on the new core

I did not find an obvious fatal mathematical error in the new core. The following comments are therefore requests for clarification or strengthening, not claimed counterexamples.

## 9.1 The fixed-codebook randomized theorem should explicitly identify its quantization form

For a target (b) between adjacent codewords (u<v), the lottery probabilities are necessarily
[
Pr(C=v)=rac{b-u}{v-u},qquad
Pr(C=u)=rac{v-b}{v-u}.
]

The main paper should display this once and call the mapping what it is: the unique adjacent mean-preserving/unbiased two-point quantizer.

That will make the connection to existing literature transparent.

## 9.2 The cap-anchoring lemma is likely the real structural theorem

The proof moves a nonhighest codeword inside an interval between caps and neighboring codewords, observes affine dependence of total interpolation loss, and pushes the codeword to an endpoint until it hits a cap or collision.

This is elegant.

The authors should isolate exactly which properties are essential:

- quadratic terminal reward;
- branch targets located at the cap points;
- unbiased interpolation;
- no codeword-dependent fixed cost;
- only the highest level interacting with intermediate-service cost.

This is the theorem I would most like to see compared with randomized quantizer-design results.

## 9.3 The continuously minimized Monge identity is also a genuine candidate contribution

The cancellation of heterogeneous intermediate curvatures in the crossing difference is nontrivial and should remain central.

However, after the quantization literature audit, the authors should state whether analogous Monge preservation under optimal reproduction-point minimization is known in quantizer design.

The burden is now on them to search that literature rather than assume the contractual notation makes the result isolated.

## 9.4 The exact linear-work theorem should be described as a corollary package

R37 already moves in this direction.

I would go further.

Once:

- the finite costs are Monge,
- the one-sided domains are in the favorable orientation,
- the oracle is constant rational work,

the (O(mk)) row-minimum layer is classical.

The publication theorem should therefore emphasize the **contractual structural facts that make the classical algorithm applicable**, not the asymptotic bound as if it were independently novel.

## 9.5 Distinct caps are doing double duty

Strictly ordered caps simplify both the full-information uniqueness statement and the codebook threshold.

In many service designs, contractual tiers are discrete and repeated.

This is not a fatal omission, but the manuscript should give a short proposition or remark for repeated caps:

- whether branches with identical caps can be aggregated;
- what happens when their intermediate cost functions differ;
- whether the exact-symbol threshold becomes the number of distinct optimal terminal actions rather than (k).

The current text hints at this in the companion but the main statement remains cleaner than many plausible applications.

---

# 10. The operational mechanism is now understandable but still entirely stipulated

I appreciate the authors' honesty: they do not call the dispatch-gateway story empirical calibration.

The question is whether that is enough for *Operations Research*.

The current Optimization area statement says that papers are evaluated on modeling, theory, algorithms, computation, or applications and should excel in at least one while remaining relevant to a broad audience. R37 can clearly be a theory/algorithm paper. It therefore does not need real data merely to be admissible.

But if the theory and algorithmic primitives are substantially inherited from quantization and matrix searching, then the operational insight has to carry more of the significance burden.

At present, the mechanism is a stipulated architecture chosen to make a writable code scarce:

- the renewal desk sees the branch;
- the gateway does not;
- billing may retain the contract but the gateway cannot access it;
- a seed is charged if it carries history;
- the customer cannot costlessly exit after the draw.

This is coherent. It is not demonstrated to be an important service architecture.

I would like one documented operational analogue—not necessarily proprietary data—showing why:

- the accepted obligation is known upstream;
- downstream execution genuinely receives only a small certified instruction set;
- the instruction alphabet is costly to expand;
- expected pre-draw participation is a plausible contractual object.

Without that, the paper needs the mathematical novelty boundary to be exceptionally strong.

---

# 11. The current title is clearer, but still broader than the solved model

"Service Contracts with Limited Memory: Participation, Randomization, and Exact Design" is much better than the R36 title.

It is also broad.

The exact global randomized frontier requires:

- a three-date renewal architecture;
- exogenous branch probabilities;
- recombination to one terminal public state;
- a saturated aggregate promise;
- scalar terminal service;
- quadratic terminal reward;
- heterogeneous quadratic intermediate costs for the exact global rational algorithm;
- no endogenous transition effects of the service code;
- no switching costs;
- no repeated customer-history effect inside the theorem.

The deterministic and pathwise results are somewhat more general in (f) and (h_j), but the flagship continuous codebook/linear-frontier theorem is not a generic service-contract result.

A title such as "Limited-Memory Renewal Contracts..." would be more accurate unless the authors broaden the theory.

This is editorial rather than mathematical, but at a top journal scope signaling matters.

---

# 12. Required changes before I would support a fresh OPRE review

I do not recommend an R38 that simply adds another theorem to the existing stack.

The next revision should close the novelty boundary and stress-test the key assumption.

At minimum:

1. **Add a serious scalar-quantization priority section.**  
   Confront optimal scalar quantization, contiguous-cell dynamic programming, randomized/unbiased quantization, and matrix-search acceleration. At minimum discuss Wu (1991) directly.

2. **Identify the adjacent expected-participation lottery as a classical unbiased adjacent quantizer.**  
   Explain precisely what the contract adds beyond stochastic rounding/randomized quantization.

3. **Position the finite writable alphabet against communication-constrained/quantized control.**  
   The paper need not solve stabilization problems, but it must explain why its memory theorem and service codebook problem are not generic finite-rate control under different terminology.

4. **Produce a theorem-level novelty table against these literatures.**  
   For each main result, state predecessor principle and model-specific increment.

5. **Address saturation robustness.**  
   Give either a nontrivial nonsaturated frontier theorem or a sharp characterization/counterexample map showing which headline results require exact saturation.

6. **Decide what role bounded overrun plays.**  
   Either generalize it beyond the solved three-branch example or clearly demote it to an interpretive illustration.

7. **Stop calling the resource wrapper an integrated optimization contribution unless codebook-dependent implementation cost is actually optimized.**  
   Keep the accounting, but distinguish accounting from a joint resource-design theorem.

8. **Slim the submission companion.**  
   Preserve historical theory in the repository, not necessarily in the journal EC.

9. **Strengthen the operational motivation or narrow the title.**  
   A documented real architecture would help; otherwise use "renewal" language consistently and rely on the formal contribution.

10. **Rebuild the introduction after the priority audit.**  
    The first page should tell the reader what is new relative to quantizer design, not only what is new relative to R36's Monge literature.

---

# 13. Minor and presentation comments

1. The abstract is far better than R36's, but "globally optimal lottery codebook" should be immediately scoped to the quadratic saturated renewal model.
2. "Approval before a private draw permits lotteries" is correct in the model; "private" should continue to mean private at the acceptance conditioning stage, not permanently secret.
3. The deterministic theorem should mention explicitly that the number of exact symbols equals the number of distinct full-information terminal actions, with (k) only under strict cap ordering.
4. The phrase "linear rational work per layer" is accurate but unusual. I would prefer "O(k) exact-rational oracle/comparison work per DP layer" once the classical search attribution is given.
5. The paper should not use "memory" unqualified when it means fixed-width writable state. R37 is already much better about this.
6. The resource equation includes an institutional charge (kappa_I). State plainly that the comparative result is conditional on this exogenous protocol price.
7. The bounded-overrun example should report both the high-realization probability and the maximum overrun in the main text, not only later exposition.
8. The external solver table is useful, but 64 branches is not a practical scale comparison with the 16,384-branch specialized algorithm. Its purpose should remain validation, not performance.
9. The PADS substitution is well designed. Include the exact upstream source identity and license in the EC, as the package already does.
10. If the authors keep the off-cap example, plot loss as a function of the top codeword once. This would make the continuous optimum intuitive to a broad OR reader.
11. The phrase "service value each additional code buys" is an effective framing. A quantization comparison would make it even sharper: the service code is a reproduction alphabet, but the distortion is institution-generated rather than exogenously chosen.
12. The paper should use "expected participation" carefully: what is averaged is the remaining payment/obligation conditional on branch and before the draw, not participation probability.
13. The theorem numbering inherited from R33/R34 in a reconstructed R37 article still makes the paper feel like a revision archive. Renumber the final submission cleanly.
14. Historical labels such as "R34" in theorem names and source paths are excellent for the repository but should disappear from the reader-facing manuscript.
15. The preservation map is valuable for reviewers, but it should not dictate the final article's exposition.

---

# 14. Confidential comments to the editor

R37 is much stronger than R36.

I want to emphasize that point because a superficial comparison of recommendations would miss the progress. The authors did what the previous report asked on focus, staircase priority, completion rigor, institutional timing, resource accounting, and computational transparency. I do not see a reason to reject R37 on those old grounds.

My new concern arises precisely because the paper is now focused enough to reveal its true mathematical neighbors.

A finite retained service code is a quantizer. A deterministic ordered codebook is an ordered scalar quantizer. The expected-participation adjacent lottery is an unbiased randomized quantizer/stochastic-rounding rule. A K-level quantizer dynamic program accelerated from quadratic to linear work by matrix searching has direct classical precedent. A writable-bit budget in a downstream controller sits in the broad control-under-communication-constraints literature.

The paper may still contain publishable new theory. I suspect the cap-anchored randomized codebook with one continuously optimized top level and the Monge preservation after continuous terminal minimization are the strongest candidates. The expected-versus-pathwise contract interpretation may also be genuinely valuable.

But the authors have not yet established that novelty boundary.

The second concern is the saturated aggregate promise. It is doing most of the economic and mathematical work. The paper gives a good exact solution on that boundary, but it has not shown that the decision insight persists away from it.

For *Operations Research*, especially in the Optimization area, I would therefore reject rather than continue an internal major-revision loop. A fresh submission could be attractive if it:

- closes the quantization/control priority audit;
- proves a meaningful saturation-robustness result;
- keeps only the genuinely distinctive contractual structure in the main theorem package;
- treats the classical matrix-search machinery as implementation consequence.

This is no longer a correctness rejection. It is a novelty-boundary and generality/significance rejection.

---

# 15. External literature and editorial material consulted for this R37 review

The following items are relevant to the novelty and positioning questions. I am **not** asserting that they solve the R37 contractual model.

### Quantization and randomized finite-level representation

- Wu X (1991), "Optimal quantization by matrix searching," *Journal of Algorithms* 12(4):663--673. DOI: https://doi.org/10.1016/0196-6774(91)90039-2.  
  The abstract explicitly describes an (O(KN^2)) discrete optimal K-level quantization DP accelerated to (O(KN)) using matrix searching.

- Croci M, Fasi M, Higham NJ, Mary T, Mikaitis M (2022), "Stochastic rounding: implementation, error analysis and applications," *Royal Society Open Science* 9:211631. DOI: https://doi.org/10.1098/rsos.211631.  
  This survey describes adjacent randomized rounding with probabilities determined by relative distance; the mean-preserving primitive is directly relevant to the R37 fixed-codebook lottery.

### Communication-constrained and quantized control

- "A Tutorial on Quantized Feedback Control," *IEEE/CAA Journal of Automatica Sinica*, DOI: https://doi.org/10.1109/JAS.2023.123972.  
  Relevant as a broad entry point to finite-level quantizer design, minimal information, and control over digital communication constraints.

The manuscript should also consider the classical control-under-communication-constraints literature cited by that tutorial, including early optimal quantized-control work and finite-data-rate control. The point is conceptual positioning, not a claim that those papers have the same participation constraints.

### Monge / matrix searching already addressed in R37

- Aggarwal A, Klawe MM, Moran S, Shor P, Wilber R (1987), "Geometric applications of a matrix-searching algorithm," *Algorithmica* 2:195--208.
- Klawe MM, Kleitman DJ (1990), "An Almost Linear Time Algorithm for Generalized Matrix Searching," *SIAM Journal on Discrete Mathematics* 3(1):81--97.
- Chan TM (2021), "(Near-)Linear-Time Randomized Algorithms for Row Minima in Monge Partial Matrices and Related Problems," *SODA 2021*.
- Kaplan H, Mozes S, Nussbaum Y, Sharir M (2017), "Submatrix Maximum Queries in Monge Matrices and Partial Monge Matrices, and Their Applications," *ACM Transactions on Algorithms* 13(2).

Unlike R36, R37 now engages these sources in a materially adequate way.

### Journal fit

- *Operations Research*, current Area Editors' Statements, Optimization area: https://pubsonline.informs.org/page/opre/editorial-statement/area-editors-statements .  
  The current statement says papers are evaluated across modeling, theory, algorithms, computation, and applications; should excel in at least one dimension; should be clear, concise, relevant to a broad audience; and are evaluated on contribution relative to length.

---

# 16. Bottom line

R37 is a successful response to the **previous** referee report.

It is focused, technically careful, and much more honest about what is classical. The staircase-search objection is no longer the main issue. The completion proof is now credible at the level needed for the claimed algorithm. The expected/pathwise mechanism is specified. The computational evidence is well disciplined.

But the reconstructed paper has now exposed a more fundamental question:

> Is this a new service-contract optimization theory, or a contract-specific scalar quantizer design sitting on classical quantization, stochastic rounding, and finite-rate control machinery?

The answer may well be "a genuinely new contract-specific quantizer theory." The current manuscript has not demonstrated that because it does not engage those literatures.

At the same time, the strongest economic conclusions are tied to an exactly saturated root promise that forces every branch cap to bind. The bounded-overrun example and resource-pricing wrapper do not yet supply the missing robustness/generalization.

Therefore:

**Recommendation: Reject in the present form.**

I would be willing to review a fresh, more mature resubmission centered on the genuinely new contractual quantizer structure—especially the cap-anchored global codebook, off-cap top level, Monge preservation after continuous minimization, and participation-dependent feasibility—provided the authors first establish the correct priority boundary and demonstrate that the insight is not confined to a knife-edge saturated promise.
