# Confidential Referee Report for Operations Research

**Manuscript:** *Limited-Memory Renewal Contracts: Participation, Quantization, and Exact Design*  
**Revision reviewed:** revision/ndu-operations-research-r39-robust-quantizer-20260924  
**Published revision tip:** 0b3a5c5eeca55149631a6cf509f627aeeffed43b  
**Validated scientific source:** 37f5395fdfb058205995f6a0eba9a1f38bfd9633  
**Review baseline identified by the authors:** 1cf9c8df76437ee71d4291d1001e9c7f055781c5  
**Predecessor independent report:** reviews/operation_research_referee_report_r37_independent_harsh_2026-09-24.md  
**Review branch:** review/operation-research-r39-independent-harsh-20260924  
**Date:** September 24, 2026  
**Recommendation:** **Reject in the present form. The correctness case is now substantially stronger, but the remaining contribution is not yet sufficiently unified or significant for Operations Research. A materially deeper resubmission could merit fresh review.**

---

## Executive assessment

R39 is the strongest version of this manuscript that I have reviewed. It directly and intelligently addresses most of the concrete objections in the R37 report.

The paper now says plainly that ordered scalar-quantizer dynamic programming, adjacent unbiased randomization, dual quantization, finite-rate encoder/decoder architectures, and matrix-search acceleration are established ideas. It cites Wu, Croci et al., Pagès--Wilbertz, Fu, and the classical Monge/matrix-search literature. It no longer presents stochastic rounding or SMAWK as contractual inventions. It narrows the title to renewal contracts. It gives a theorem-level predecessor table. It also adds mathematically nontrivial material away from the saturated endpoint: the clipped full-information phase diagram, uniform value transport between arbitrary root promises, a strict nonsaturated interval where the expected-participation advantage survives, an exact fixed-book allocation certificate, repeated-cap treatment, and a finite-catalog dynamic program with actual selected-level charges and bounded-overrun eligibility.

I also find the proof hygiene and computational provenance unusually careful. I did not find an obvious counterexample to the cap-anchoring lemma, the continuous-top-level reduction, the post-minimization Monge inequality, the all-promise transport bounds, the fixed-book supporting-price certificate, or the finite-catalog path recurrence. The current recommendation is therefore **not a correctness rejection**.

The remaining problem is more fundamental for a top OR journal.

Once the classical quantization and matrix-search components are correctly subtracted, the genuinely distinctive mathematical core is substantially narrower than the manuscript's theorem inventory suggests. The strongest part remains the saturated quadratic contract: a dual-quantization-like interior combined with a heterogeneous one-sided contractual tail, an off-cap highest codeword, and a crossing-difference identity that preserves Monge structure after continuous minimization. That is elegant.

The new R39 results do not yet turn this into a broad exact-design theory away from the saturated boundary. The nonsaturated theorem is primarily a Lipschitz policy-transport result plus a fixed-book resource-allocation certificate; the globally optimized continuous codebook at an interior promise remains unsolved. The risk-and-charge theorem moves instead to an exogenously finite catalog and back to the saturated root promise, where the global optimization is an ordered shortest-path dynamic program. Thus the revision now contains three clean but only partially connected problems:

1. an unrestricted continuous codebook at the saturated promise;
2. a nonsaturated expected-participation allocation problem whose **fixed-book** inner problem is solved exactly, but whose continuous outer codebook problem is not;
3. a saturated, bounded-overrun, **finite-catalog** problem with additive level charges.

That is useful progress, but it does not yet supply the single broad theorem family or operationally grounded model that would make the contribution compelling for *Operations Research*. The current Optimization area statement says a paper should excel in at least one of modeling, theory, algorithms, computation, or applications and be relevant to a broad audience; it also explicitly asks authors to consider contribution relative to length. R39 is much shorter and better focused than R37, but I still do not think the remaining model-specific advances clear that bar.

My recommendation is therefore **Reject in the present form**, with a materially more favorable assessment than R37. A new submission could be attractive if it solves or sharply characterizes the genuinely joint nonsaturated design problem and either unifies the risk/charge extension with that theory or substantially strengthens the operational motivation.

---

# 1. Version audit and what R39 genuinely fixes

The current build record is internally consistent and reports:

- 24 main-paper pages;
- 22 main-paper pages excluding references;
- a 23-page electronic companion;
- a 174-word abstract;
- zero undefined references;
- zero overfull boxes;
- a clean scientific source tree;
- preservation checks against 1,854 inherited paths;
- explicit hashes for all transitive reader inputs and outputs.

The new verification layer reports, among other checks:

- 768 catalog-frontier equalities;
- 26,604 direct-support book checks;
- 600 scaling/lift checks;
- 660 clipped-allocation checks;
- 2,460 fixed-book response-concavity checks;
- 128 repeated-cap equalities;
- 1,715 primal/dual-event allocation equalities;
- 6,955 supporting branch maxima;
- 72 saturated catalog/path-DP equalities;
- 48 interior-promise catalog comparisons;
- 480 arbitrary-promise transport checks.

These are regression and implementation checks rather than proofs, and the manuscript now describes them that way.

The revision also corrects the most serious R37 positioning problem. The first two sections now explicitly state that:

- Wu's 1991 quantization DP already has the matrix-search O(KN) pattern;
- adjacent mean-preserving two-point randomization is classical stochastic rounding;
- dual quantization is a closer predecessor than ordinary rounding;
- encoder/channel/decoder finite-alphabet architectures are standard in communication-constrained control;
- the Monge/SMAWK machinery is classical once the model-specific cost arrays have the required structure.

This is the right intellectual baseline. I no longer regard the R37 quantization-priority objection, by itself, as a reason to reject the paper.

The R37 companion-bloat objection is also substantially reduced. The current main paper is a much more coherent scientific unit, and the 23-page companion is now plausibly a companion rather than a second full paper.

---

# 2. Mathematical audit of the current core

Before explaining the remaining blockers, I want to record what I believe is technically sound and potentially publishable.

## 2.1 Cap anchoring and the continuous highest level

For the saturated quadratic expected-participation problem, the in-hull loss

q/2 (b-u)(v-b)

is affine in either moving interior endpoint while the set of bracketed cap points is fixed. The proof therefore can push every nonhighest unanchored codeword to a cap or a collision without increasing loss. The highest codeword is different because branches above it invoke intermediate service and hence a heterogeneous tail.

I find this reduction credible. The manuscript also now correctly avoids claiming that endpoint-pushing is a new generic quantization principle.

The off-cap example with top level 5/8 remains useful because it demonstrates that the contractual tail is not reproduced by simply restricting a dual quantizer to the cap grid.

## 2.2 The continuously minimized Monge identity is the strongest technical result

The proof of the terminal-array Monge property is much more important than the eventual SMAWK complexity statement.

For i<j, the manuscript derives an explicit crossing difference for Psi_i(z)-Psi_j(z), with the heterogeneous intermediate-curvature terms cancelling. The remaining expression is nondecreasing in z. This yields the four-point inequality after minimizing over ordered terminal intervals.

This is a real model-specific structural theorem. It is not merely “convexity implies Monge,” and the paper is now careful about that distinction.

The subsequent completion, tie-breaking, reachability, and column-offset arguments are detailed enough for the claimed use of classical matrix search. I do not see the staircase-domain gap that affected earlier versions.

## 2.3 The clipped full-information phase diagram is correct and useful

For arbitrary root promise B, strict concavity and increasing terminal reward imply that the full-information optimum equalizes uncapped terminal actions at a common level tau and clips at the branch caps:

C_j = min(b_j,tau), Y_j=0.

The resulting exact-symbol threshold is the number of distinct clipped actions. This is a clean result and it usefully shows that the saturated k-symbol threshold is not generic across promises.

It also exposes an important fact that should receive more emphasis: for B at or below the smallest cap, memory is completely irrelevant.

## 2.4 The all-promise transport bound appears correct, but its strength should not be overstated

The contraction from B2 to B1 and the partial lift from B1 to B2 preserve the alphabet and give the displayed Lipschitz-type bounds. The pathwise lift is valid under the manuscript's explicit timing convention that allows draw-specific intermediate service and no uncharged correlated terminal seed.

I do not see a flaw in the argument.

But this is a stability bound, not a solution of the nonsaturated restricted-memory problem. This distinction is central to my recommendation below.

## 2.5 The fixed-book allocation certificate is clean

For a fixed codebook under quadratic primitives, the branch response is piecewise affine up to the top codeword and then concave quadratic in the tail. Filling common chord slopes and then performing the tail water-level sweep gives a valid supporting multiplier. Equality in the separable Lagrangian upper bound is an exact certificate.

This is useful algorithmically and makes the nonsaturated reduction executable for a fixed book.

Again, however, the hard outer problem over unrestricted continuous books is left open.

## 2.6 The finite-catalog risk-and-charge DP is correct as stated

For a declared finite catalog, the bounded-overrun rule assigns each branch either an adjacent unbiased lottery or the largest feasible lower codeword. The total book cost decomposes into ordered edge costs, a tail, and nonnegative additive vertex charges. Increasing catalog paths therefore enumerate all books, and the recurrence is a standard exact shortest-path/segmentation dynamic program.

The theorem is correct for the declared model. The question is its novelty and role, not its validity.

---

# 3. Major blocker 1: saturation robustness is demonstrated, but the nonsaturated frontier is still not solved

The R37 report identified saturation as a structural knife edge. R39 responds with more than a token example, and I credit that. The response is nevertheless incomplete.

The key new inequality says that every fixed-memory value is Lipschitz in the root promise and therefore any strict saturated expected-versus-pathwise gap survives sufficiently close to saturation. In the three-cap example this proves a strict gap for

11/24 < B <= 1/2.

That is a genuine robustness theorem.

But it is only **local persistence of a value gap**. It does not determine the restricted-memory frontier at an interior B.

The manuscript itself correctly concedes all of the following:

- the original cap anchors need not remain optimal away from saturation;
- pathwise randomization need not reduce to the deterministic frontier by the saturated proof;
- the original O(mk) finite-anchor algorithm does not solve the interior problem;
- the branch targets become endogenous;
- repeated-cap aggregation is not asserted for the general restricted-alphabet interior problem.

These are not marginal details. They are precisely the structural questions raised by relaxing saturation.

Proposition 8.4 (the joint promise-allocation formulation) writes the expected-participation problem as an outer maximization over a continuous codebook and an inner separable concave allocation. The companion then solves the **inner fixed-book problem**. That is useful, but it is not an exact algorithm or structural characterization for the joint unrestricted continuous problem.

Thus the strongest R39 robustness claim is still:

> the saturated institutional advantage cannot disappear immediately when B moves a small distance into the interior.

That is materially weaker than:

> the restricted-memory contract has a tractable or structurally characterized nonsaturated frontier.

For a top OR paper, I would want at least one of the following:

1. a global exact algorithm for the unrestricted continuous expected-participation frontier for every B;
2. a structural theorem reducing that problem to finitely many events or anchors;
3. an exact pathwise frontier away from saturation and a characterization of when randomization remains useless or becomes useful;
4. a sharp counterexample map proving that no analogous finite-anchor/Monge structure can survive, together with a meaningful alternative algorithm or approximation theorem.

At present the paper stops exactly where the economically more general problem begins.

The local interval in the illustrative example is also narrow: its width is 1/24 on a feasible B-range of length 1/2. I do not object to a conservative bound, but the manuscript should not let this one certified interval carry the burden of a general nonsaturation claim.

**Bottom line:** the knife-edge concern is softened, not closed.

---

# 4. Major blocker 2: R39 contains three exact problems rather than one unified exact-design theory

The revised title ends with “Exact Design.” The individual theorems are exact within their declared domains, but the paper's extensions do not combine.

The continuous frontier theorem has:

- saturated root promise;
- continuous codewords;
- quadratic terminal and intermediate primitives for the global randomized solution;
- no codeword-dependent charges;
- unrestricted expected participation or the saturated pathwise endpoint.

The nonsaturated allocation theorem has:

- arbitrary root promise;
- continuous codewords;
- no codeword charges;
- expected participation for the exact joint formulation;
- an exact algorithm only after the book is fixed.

The risk-limited catalog theorem has:

- saturated root promise again;
- an exogenously finite certification catalog;
- a pre-draw intermediate action;
- additive per-selected-level charges;
- bounded realization overrun.

These are related, but they are not a hierarchy in which each theorem strictly generalizes the previous one.

In particular, the manuscript does **not** solve the problem a reader naturally reaches after reading all three sections:

> jointly choose a continuous codebook, allocate a nonsaturated root promise, impose a bounded-overrun participation rule, and charge the actual selected codewords.

Nor does it provide a reduction showing why such a unified problem decomposes into the three solved components.

This fragmentation matters because many of the new claims are individually based on classical optimization patterns:

- concave separable resource allocation for a fixed book;
- Lipschitz feasible-policy transport across B;
- ordered shortest paths for a finite catalog;
- additive vertex charges.

A unified theorem could make the contractual interaction itself the contribution. Without it, the paper risks reading as a strong saturated theorem surrounded by several technically correct but comparatively routine extensions.

I recommend either:

- **unify the theory** substantially; or
- **narrow the paper again**, making the saturated continuous theorem the central contribution and treating nonsaturation/catalog material as carefully delimited sensitivity and implementation extensions rather than coequal “exact design” pillars.

The current manuscript tries to have both breadth and a narrow core, and the result is not yet fully convincing.

---

# 5. Major blocker 3: after the priority audit, the incremental novelty is still thinner than the theorem count suggests

The R39 literature audit is a major improvement. It also makes the novelty accounting easier.

The paper now explicitly gives away, correctly, the following generic claims:

- ordered scalar quantizer dynamic programming;
- contiguous scalar cells;
- optimized reproduction points as a generic quantization idea;
- adjacent unbiased stochastic rounding;
- dual/random-splitting quantization;
- finite-rate encoder/decoder architecture;
- Monge DP;
- SMAWK/matrix searching;
- separable concave allocation as the inner structure;
- ordered shortest-path optimization over a finite catalog.

What remains most distinctive is:

1. the contractual one-sided tail above the largest codeword;
2. cap anchoring for nonhighest levels in the saturated discrete-source model;
3. the continuously optimized off-cap highest level;
4. the cancellation proving Monge order after tail minimization;
5. the expected-versus-pathwise feasibility interpretation under the stipulated acceptance timing.

I find items 3--5 interesting. I am less persuaded that the additional R39 theorems, by themselves, add enough new optimization methodology to lift the package to the *Operations Research* bar.

The current Optimization area statement says a paper should excel in at least one dimension and be relevant to a broad audience. Here the generic algorithmic machinery is classical, the application is stylized, and the nonsaturated global problem remains open. The paper therefore needs the model-specific structural theorem to be exceptionally compelling and broadly reusable. I am not yet convinced that it is.

### A missing close comparison: optimal one-dimensional dual grids

R39 cites Pagès and Wilbertz's foundational dual-quantization work, which is essential. It should also confront the later direct optimization literature on one-dimensional dual quantizers. In particular:

- Benjamin Jourdain and Gilles Pagès (2021), *Optimal dual quantizers of 1D log-concave distributions: Uniqueness and Lloyd like algorithm*, Journal of Approximation Theory 267:105581, DOI 10.1016/j.jat.2021.105581.

That paper studies optimized one-dimensional dual grids and, in the quadratic case, gives a Lloyd-like algorithm. It does not obviously solve the manuscript's heterogeneous contractual tail, and I am **not** claiming it subsumes R39. But it is closer to the manuscript's “optimize the unbiased random-splitting grid” problem than a generic stochastic-rounding survey. The novelty boundary around the continuously optimized grid should cite and compare against it directly.

### Implementation charges also need a sharper antecedent boundary

The finite-catalog theorem adds an arbitrary nonnegative charge for each selected level. That is useful, but once the book is restricted to a finite ordered candidate set, adding vertex costs to a path recurrence is a very standard construction.

The paper should explain more explicitly what is new relative to penalized quantizer/codebook selection, variable-rate or entropy-constrained quantization, and fixed-charge selection models. The authors are correct that a per-selected-level certification charge is not the same object as entropy coding. Precisely because it is different, the paper should say what operational technology produces this cost and what established penalized-codebook model is the closest mathematical predecessor.

A literature audit that merely says “entropy coding is not silently solved here” is not yet the same as establishing the closest prior optimization model for charged codebook design.

---

# 6. Major blocker 4: the contractual interpretation remains more stipulated than modeled

The manuscript is commendably candid that the renewal architecture is an abstraction and not an empirical description of a named service provider.

That honesty does not resolve the significance issue.

The branch is public. There is no hidden type report. There is no incentive-compatibility constraint. The customer-facing economics enters primarily through branch caps and through whether a lottery is tested in conditional expectation before the draw or realization by realization after it.

This is enough to define a contract, but the mechanism-design content is light. In particular, the expected-participation institution effectively treats the customer's relevant acceptance constraint as linear in the expected remaining obligation. The pathwise institution instead imposes a hard realization-level cap. These are very different risk/timing primitives, and the paper obtains a large value difference precisely from that distinction.

I would like a stronger microfoundation or operational foundation for why these are the two institutions to compare.

Questions the manuscript should answer more concretely include:

- What class of customer preferences makes the expected pre-draw cap the correct participation condition?
- Is the customer risk neutral over monetary/service obligations, or is the cap a regulatory/accounting rule rather than utility?
- What prevents renegotiation or exit after the high draw in realistic renewal settings?
- In the bounded-overrun model, why must the intermediate tier be committed before the draw?
- What real certification or execution technology makes a small writable alphabet costly while leaving the larger read-only contract unavailable to the downstream gateway?
- What is an example in which a per-selected-level certification charge, rather than a per-use or bit/entropy charge, is the right implementation cost?

The paper need not become empirical to be publishable in the Optimization area. But if the application remains completely stylized, the mathematical novelty must carry almost the entire significance burden. As explained above, much of the machinery is now correctly acknowledged as classical.

A documented operational analogue would materially improve the paper even without proprietary data.

---

# 7. Major blocker 5: the finite-catalog theorem is exact but algorithmically routine and computationally lightly exercised

Theorem 9.1 is presented as a general exact design theorem for arbitrary finite certification catalogs, arbitrary branch counts and symbol budgets, heterogeneous costs, bounded-overrun tolerance, and selected-level charges.

All of that is true.

But once the fixed-book branch rule is established, the global problem is an increasing path through an ordered catalog with edge costs, a terminal tail, and additive vertex charges. The O(mN^2) layered DP is immediate.

The theorem therefore needs a clearer reason to matter beyond being an exact finite enumeration structure.

At least one of the following would strengthen it substantially:

- prove Monge or another structure under meaningful conditions and obtain a faster algorithm;
- derive an approximation theorem linking a catalog mesh to the unrestricted continuous risk/charge problem;
- design the catalog itself rather than taking it as exogenous;
- prove sensitivity/monotonicity in delta or the charges that yields operational policy structure;
- use a realistic certification catalog in which the chosen levels and charges have interpretable meaning.

The current synthetic studies use N up to 32 and k up to 128 for the new catalog theorem. They are adequate unit/regression studies but do not establish computational significance. The inherited continuous-frontier benchmark at k=16,384 is useful provenance but is not a benchmark of the new charged catalog problem.

The paper is therefore not, in my view, an algorithmic-computation paper on the strength of Section 9.

---

# 8. The computational package is excellent verification infrastructure, not yet a substantive computational contribution

I want to separate praise for reproducibility from the scientific role of the experiments.

The repository does several things extremely well:

- exact rational replay;
- independent support enumeration;
- independent primal/dual allocation checks;
- search-layer substitution;
- preserved predecessor artifacts;
- immutable source hashes;
- explicit timing scopes;
- rejection of malformed inputs;
- clear distinction between theorem verification and external solver checks.

This is better than the reproducibility practice of many theory papers.

But the counts of verified identities are not evidence of operational relevance, and the manuscript no longer claims they are.

The R39-specific numerical study still consists of synthetic cap/weight landscapes and relatively small finite catalogs. It does not explore the unsolved outer continuous codebook problem away from saturation, because the paper does not have an algorithm for that problem. It does not quantify how conservative the nonsaturation Lipschitz interval is relative to the true institutional gap except through finite small-catalog reference calculations. It does not use real data.

If the authors want computation to be one of the dimensions in which the paper “excels,” the study should be redesigned around substantive questions rather than primarily regression.

For example:

- map the true expected/pathwise gap across B for rich finite catalogs and compare it with the theorem's certified interval;
- study how the optimal book changes jointly with B, delta, and codeword prices;
- identify phase transitions and test whether they suggest a stronger theorem;
- compare exact finite-catalog solutions with a continuous benchmark as catalog density increases.

Otherwise, I would keep the computational section short and present it as validation infrastructure.

---

# 9. What R39 has resolved from the R37 report

For clarity, I would **not** ask the authors to re-litigate the following points.

## 9.1 Scalar-quantization priority

Substantially resolved. The paper now acknowledges Wu and explicitly states that ordered quantizer DP and linear matrix search are classical.

## 9.2 Stochastic-rounding priority

Substantially resolved. Equation (1) displays the distance-proportional probabilities and calls the primitive classical.

## 9.3 Dual-quantization relevance

Largely resolved at the foundational level. Pagès--Wilbertz is now treated as a closer predecessor and the in-hull quadratic identity is stated explicitly. The remaining request is to extend that comparison to later optimized one-dimensional dual-grid work.

## 9.4 Finite-rate control

Adequately acknowledged for the present scope. The paper no longer claims a generic finite-rate architecture contribution.

## 9.5 Saturation as a hidden assumption

Resolved as a disclosure problem. It is no longer hidden. R39 also adds real robustness theory. My remaining objection is that the interior **joint design problem** is not solved.

## 9.6 Resource pricing as mere after-the-fact accounting

Partly resolved. The new finite-catalog theorem genuinely puts actual level charges inside book selection. The remaining question is whether that finite shortest-path theorem is sufficiently novel and operationally motivated.

## 9.7 Companion focus and revision hygiene

Substantially resolved. I no longer consider repository preservation or companion organization a major reason for rejection.

---

# 10. Specific technical and presentation requests

These are secondary to the major issues above.

1. **State the unsolved joint nonsaturated problem more prominently.** The introduction currently says the exact fixed-book reduction “identifies the remaining joint promise-allocation problem.” A reader can still miss that the unrestricted continuous outer codebook optimization is not solved. Say this in one direct sentence.

2. **Do not let “exact interior promise-allocation reduction” read like an exact global interior frontier.** The adjective “exact” is mathematically correct but easy to overread. Use “exact fixed-book allocation” whenever that is what is meant.

3. **Separate theorem families in the abstract even more sharply.** The abstract is accurate, but the sequence can still sound as if all-promise robustness, interior allocation, and risk-limited charged design belong to one common global algorithm.

4. **Quantify the robustness interval as a sufficient certificate.** In the three-cap example, emphasize that 11/24 < B <= 1/2 is a lower-bound guarantee from transport, not the actual maximal interval of institutional separation.

5. **Clarify the economic meaning of expected participation.** “Expectation conditional on branch and before the private draw” is mathematically clear. Add the preference/accounting assumption under which this is a participation constraint rather than merely a mathematical budget.

6. **Add Jourdain--Pagès (2021) to the optimized dual-grid comparison.** Explain specifically why the contractual tail and heterogeneous intermediate costs take the problem outside that framework.

7. **Position selected-level charges against penalized codebook design.** Do not claim novelty for “a cost on selected representatives” generically. The distinctive object should be the interaction with the bounded-overrun contractual edge rule.

8. **Explain catalog origin.** Is A a regulatory list, hardware certification set, product menu, or discretization chosen by the operator? The answer changes the interpretation of Theorem 9.1.

9. **Report new-algorithm scaling separately from inherited scaling.** The manuscript already warns that timing scopes differ; a dedicated small table of complexity versus N and k would make this cleaner.

10. **Keep the O(mk) result as a contractual corollary of classical matrix search.** The current heading does this correctly. Do not re-promote the asymptotic bound in later marketing language.

11. **Be cautious with “general.”** The catalog theorem is general over a declared finite catalog but not over continuous codebooks, arbitrary codebook costs, or draw-dependent intermediate protocols.

12. **Explain whether the strict off-cap result survives small codeword charges.** This is an easy and operationally meaningful sensitivity question that may connect the continuous and charged theorem families.

13. **Investigate pathwise nonsaturation.** Even a sharp two- or three-branch characterization would add more conceptual value than another layer of finite regression tests.

14. **Consider whether repeated caps can be treated away from saturation under additional conditions.** The current proposition correctly refuses to overclaim. A useful sufficient condition could strengthen the all-promise theory.

15. **Avoid using verification volume as a proxy for theorem importance.** The evidence section is responsible, but the response letter still devotes substantial space to check counts.

---

# 11. What would change my recommendation

A fresh version would become substantially more compelling if it did **two** of the following, with the first item the most important.

### 1. Solve or sharply characterize the unrestricted nonsaturated finite-memory frontier

The best revision would derive a global structure/algorithm for

- endogenous branch promises,
- a jointly optimized continuous codebook,
- finite writable alphabet,
- at least expected participation,
- and preferably a comparison with pathwise participation.

A finite event reduction, a new Monge/submodular structure, or a provable approximation scheme would all qualify.

### 2. Unify the risk/charge extension with the promise-allocation theory

Rather than returning to saturation and a finite catalog, show how bounded overrun or selected-level charges interact with an interior root promise. Even a nontrivial subclass with a clean algorithm would make the paper feel like one theory rather than three adjacent exact problems.

### 3. Establish a stronger operational foundation

Provide a documented architecture in which:

- upstream renewal information is unavailable downstream;
- only a certified symbol crosses the boundary;
- pre-draw expected participation is the relevant acceptance rule;
- alphabet expansion has a real cost;
- and bounded overrun or per-level certification charges are meaningful.

This need not be a full empirical paper, but it should be more than an invented dispatch-gateway story.

### 4. Deepen the quantization priority comparison

Add the one-dimensional optimal dual-grid literature, and identify the closest penalized/variable-rate codebook-design antecedents. The paper should make it possible for a quantization expert to see, theorem by theorem, exactly what the contractual tail adds.

### 5. Turn the computations into a scientific study or shorten them

If computation remains a contribution pillar, study economically meaningful parameter paths and scaling of the **new** problems. Otherwise keep the excellent exact verification package but reduce its role in the publication case.

---

# 12. Confidential comments to the editor

This manuscript has improved considerably.

I would not reject R39 for sloppiness, missing proofs, irreproducibility, or the priority mistakes that affected earlier revisions. The authors have responded unusually carefully. I believe the core saturated theorem package is now credible, and the post-minimization Monge identity is technically interesting.

My concern is whether the paper is sufficiently important for *Operations Research* after the authors correctly subtract the classical quantization and matrix-search machinery.

The R39 additions are mathematically valid, but they mostly take the form of:

- a generic Lipschitz transport argument showing local persistence away from saturation;
- a standard separable concave allocation solved exactly after fixing the codebook;
- a standard layered shortest path after restricting codewords to a finite catalog and assigning additive charges.

The hard nonsaturated continuous outer design problem remains open. The risk/charge problem is solved only after changing the model back to saturation and to an exogenous finite catalog. The application remains deliberately stylized.

The current *Operations Research* Optimization statement says manuscripts are judged across modeling, theory, algorithms, computation, and applications, should excel in at least one dimension, and should be relevant to a broad audience. In my view R39 is good on rigor and reproducibility but does not yet excel enough on novelty, unified theory, or operational relevance.

For that reason I recommend **Reject in the present form**, while explicitly inviting a fresh review if the authors solve the genuinely joint nonsaturated problem or give the model a significantly stronger operational foundation.

This is a much closer call than R37.

---

# 13. External literature and editorial material consulted for this review

The following sources are used to evaluate contribution boundaries. I am not asserting that any one of them solves the R39 contractual model.

### Scalar and dual quantization

- Wu X (1991), “Optimal quantization by matrix searching,” *Journal of Algorithms* 12(4):663--673. DOI: https://doi.org/10.1016/0196-6774(91)90039-2.  
  Relevant to the classical ordered quantizer DP and O(KN) matrix-search pattern.

- Croci M, Fasi M, Higham NJ, Mary T, Mikaitis M (2022), “Stochastic rounding: implementation, error analysis and applications,” *Royal Society Open Science* 9:211631. DOI: https://doi.org/10.1098/rsos.211631.  
  Relevant to the adjacent distance-proportional unbiased randomization primitive.

- Pagès G, Wilbertz B (2012), “Intrinsic stationarity for vector quantization: Foundation of dual quantization,” arXiv:1010.4642v2. https://arxiv.org/abs/1010.4642.  
  Relevant to mean-preserving random splitting, optimized grids, and the closer dual-quantization interpretation.

- Jourdain B, Pagès G (2021), “Optimal dual quantizers of 1D log-concave distributions: Uniqueness and Lloyd like algorithm,” *Journal of Approximation Theory* 267:105581. DOI: https://doi.org/10.1016/j.jat.2021.105581.  
  Relevant because it studies optimization of one-dimensional dual-quantization grids directly. It does not appear to contain R39's heterogeneous contractual tail.

### Quantized control

- Fu M (2024), “A Tutorial on Quantized Feedback Control,” *IEEE/CAA Journal of Automatica Sinica* 11(1):5--17. DOI: https://doi.org/10.1109/JAS.2023.123972.  
  Relevant to the fact that finite-alphabet encoder/decoder architectures and information constraints are standard outside contracting.

### Current Operations Research editorial standard

- *Operations Research*, “Area Editors' Statements,” Optimization area, current page accessed September 24, 2026: https://pubsonline.informs.org/page/opre/editorial-statement/area-editors-statements.  
  The Optimization statement says manuscripts are evaluated on modeling, theory, algorithms, computation, or applications; should excel in at least one dimension; should be clear, concise, and relevant to a broad audience; and are evaluated with attention to contribution relative to length.

---

# 14. Bottom line

R39 successfully fixes the **R37 positioning problem** and substantially improves the **saturation robustness story**.

I find the paper technically serious and, as far as I can determine from this review, mathematically coherent. The authors have been appropriately conservative about what is classical.

But that very correction exposes the remaining publication question.

The paper's strongest distinctive theorem is still a specialized saturated quadratic quantizer-with-contractual-tail result. Away from saturation, the revision proves continuity and solves only the fixed-book allocation subproblem. With risk limits and actual codeword charges, it solves a different saturated finite-catalog problem by a standard ordered path DP.

That is not yet the unified, broadly significant exact-design theory I would expect from a top *Operations Research* paper with a completely stylized application.

**Recommendation: Reject in the present form.**

A fresh submission would be worth serious consideration if it closes the unrestricted nonsaturated joint-design problem, unifies the risk/charge extension with that theory, or supplies an operational foundation strong enough that the current model-specific structural theorem has clear practical significance.
