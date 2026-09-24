
# Confidential Referee Report for Operations Research

**Manuscript:** *Accepted Service Adaptation: Exact Parametric Quotients and Minimal Additional Writable Memory*  
**Revision reviewed:** revision/ndu-operations-research-r36-linear-frontier-20260924  
**Reviewed revision branch head:** 8b17bed9079aa8e3bcaf52e6a5847a60cbf7d7ca  
**Scientific source commit identified by the R36 build record:** a3a68823e30e7673684ea486a566ebdd84d0aab5  
**Scientific baseline:** R35 commit 7e49851cd04f0f7e015c2561b43a4e7591574e67  
**Review branch:** review/operation-research-r36-independent-harsh-20260924  
**Date:** September 24, 2026  
**Recommendation:** **Reject in the present form; a substantially consolidated and re-positioned resubmission could merit fresh review.**

---

## Executive assessment

R36 is technically serious, unusually well instrumented, and substantially stronger than the R30 manuscript addressed by the previous independent referee report. The authors have now closed many of the objections that were genuinely important at R30: they acknowledge the laminar-allocation and memoization lineage; add analytical tightness constructions; recast the finite-memory theorem through classical behavioral minimization; separate writable memory from read-only representation; extend the exact response compiler to continuous piecewise-quadratic rewards with marginal jumps; solve the globally optimized randomized restricted-memory frontier; distinguish expected from pathwise participation; prove Monge structure after continuous terminal minimization; and finally implement a linear-work search using classical SMAWK after an ordinal completion of the staircase domains.

I did not find a simple counterexample to the central R31--R36 mathematical chain. In particular, I do not see an immediate contradiction in the cap-reflection recursion, the tight chain construction, the behavioral equivalence theorem, the cap-anchored randomized representation, the off-cap optimal example, the pathwise-randomization theorem, the R35 Monge argument, or the R36 one-sided ordinal completion used by the code. The exact verification package is extensive and is appropriately described as verification rather than proof.

That is not enough for publication in *Operations Research*.

The principal problem at R36 is now **priority and significance after the paper's own successful reframing**. The newest theorem no longer changes the contract model or the optimal frontier. It changes only the matrix-search implementation of an already derived dynamic program, from quadratic search to monotone search and then to linear row-minimum search. That kind of improvement can be valuable, but it lies directly in a mature literature on Monge dynamic programming, totally monotone partial matrices, staircase matrices, and completion/search methods. R36 cites Aggarwal et al. (1987) and Yao (1980), but it does not engage the much closer literature on **partial/staircase Monge matrix search**. This omission is material because the new theorem's headline is exactly a linear-work treatment of triangular/staircase feasibility.

There is also a top-journal contribution-to-length problem. The validated R36 reader has 39 pages excluding references, essentially the ceiling for an OPRE lengthy manuscript, plus a 22-page electronic companion. The manuscript now contains at least six successive conceptual layers: compact parametric quotienting, tight response size, piecewise-quadratic closure, machine minimization, deterministic and randomized memory design, global continuous codebook optimization, Monge acceleration, and SMAWK acceleration. Each layer is individually defensible. Together they produce a paper whose central question is increasingly difficult to identify and whose latest algorithmic increment is much smaller than the full manuscript footprint.

The current *Operations Research* editorial statements emphasize innovative and impactful work that advances decision making, and the Optimization area explicitly evaluates the ratio of contribution to length. The Stochastic Models statement also emphasizes the importance of the modeled system, originality of analysis, quality of results, clarity, and utility to the broader OR/MS community. The present manuscript is rigorous, but rigor alone does not resolve the questions below.

My recommendation is therefore **Reject in the present form**. This is not a correctness rejection. It is a priority, contribution-to-length, and operational-significance rejection. A future paper could become compelling if it is reorganized around one coherent theorem package, if the staircase/partial-Monge priority issue is closed explicitly, and if the economic/operational meaning of the memory and randomization institutions is made substantially less architecture-dependent.

---

# 1. Version audit: R36 is a real scientific revision

R36 is not a cosmetic branch rename. Relative to R35 it adds a new theorem and implementation layer centered on linear-work row-minimum search.

The principal new claim is Theorem R36-linear:

- for ordered rational inputs and budgets 1 through m, both the expected-participation and deterministic/pathwise complete frontiers are computed in O(mk) exact rational operations and comparisons;
- one optimal codebook is returned for each budget;
- storage is O(mk+k);
- the highest randomized level remains continuously optimized rather than discretized;
- the bit-operation statement is inherited through the coefficient-height bound.

The implementation uses a standard SMAWK recursion over a model-specific key oracle. The completion distinguishes:

- feasible entries by a finite lexicographic key;
- infeasible entries to the left of a terminal row by an order that prefers larger columns;
- infeasible entries to the right of a program row by an order that prefers smaller columns.

The code does not numerically materialize infinity and does not construct the whole matrix.

The build record reports:

- 41 main-paper pages in total;
- 39 pages excluding the two bibliography pages;
- a 22-page electronic companion;
- no unresolved citations/references or overfull boxes;
- 100 new exact R36 cases;
- 4,232 frontier equalities against inherited algorithms;
- 2,116 controller replays;
- 43,431 exact submatrix row-argmin comparisons;
- 2,595 nonvacuous total-monotonicity implications;
- 402 primitive Monge checks;
- reruns of the inherited R33--R35 suites.

The version and reproducibility discipline are much better than in early revisions.

---

# 2. What is now convincing

Before giving the adverse assessment, I want to separate issues that I regard as substantially resolved.

## 2.1 The paper no longer misclaims laminar allocation or memoization as new

The R31 model/literature section now gives an explicit invertible mapping to separable concave allocation over laminar descendant constraints. It treats classical tree-constrained allocation, polymatroid sensitivity, and normalized memoization as predecessors.

This is the correct intellectual baseline.

## 2.2 The response-size story now has genuine upper and lower bounds

The chain construction with exactly 2n global clipping knots and n²+2n affine response pieces is a useful analytical tightness result. The paper also correctly distinguishes explicit per-vertex tables from the shared arithmetic circuit representation.

This closes an important R30 objection.

## 2.3 The memory theorem is now properly architecture-aware

The current manuscript is much more careful than R30 about the distinction among:

- additional writable alphabet;
- combined public-state/class pairs;
- read-only response/program storage.

It also explicitly identifies backward behavioral minimization as classical. This is a significant improvement.

## 2.4 The randomized frontier is no longer merely a fixed-codebook calculation

R34 gives a nontrivial structural reduction: all nonhighest levels can be cap-anchored while the highest level may need to remain continuous. The explicit off-cap optimum is valuable because it prevents the algorithmic result from collapsing to a finite cap-only segmentation problem.

## 2.5 Expected and pathwise participation are separated rather than conflated

The pathwise theorem makes clear that the benefit from restricted-memory randomization is institution-dependent. That is the right conceptual distinction, even though I remain unconvinced that the expected-participation institution is operationally motivated enough; see Section 7.

## 2.6 R35's continuously minimized terminal Monge result is more interesting than a generic Monge-DP citation

The argument that the optimized terminal array remains Monge after minimizing over a continuous highest service level is model-specific and worth retaining. This is a more substantive structural result than the statement that SMAWK searches a totally monotone matrix.

---

# 3. Major blocker: R36 does not engage the actual staircase/partial-Monge literature

This is my most important new objection.

R36 says, correctly, that ordinary monotone row minima do not by themselves justify SMAWK and that total monotonicity must hold in every submatrix. The revision then supplies an ordinal completion of the one-sided staircase domains and applies classical SMAWK.

However, the bibliography jumps from Yao (1980) and Aggarwal, Klawe, Moran, Shor, and Wilber (1987) directly to the model-specific result. That is not an adequate priority audit for a theorem whose new content is precisely **linear row-minimum search under triangular/staircase feasibility**.

At least the following literature must be confronted explicitly:

1. **Klawe and Kleitman (1990), "An Almost Linear Time Algorithm for Generalized Matrix Searching," SIAM Journal on Discrete Mathematics 3(1):81--97, DOI 10.1137/0403009.**  
   This paper gives an O(n alpha(n)) method for row maxima/minima in totally monotone partial matrices and explicitly connects the machinery to dynamic programs satisfying quadrangle inequalities.

2. **Chan (2021), "(Near-)Linear-Time Randomized Algorithms for Row Minima in Monge Partial Matrices and Related Problems," SODA 2021, pp. 1465--1482, DOI 10.1137/1.9781611976465.88.**  
   In particular, Chan gives an O(n) expected-time row-minimum algorithm for Monge staircase matrices, improving the longstanding O(n alpha(n)) partial-matrix bound.

3. **Kaplan, Mozes, Nussbaum, and Sharir (2017), "Submatrix Maximum Queries in Monge Matrices and Partial Monge Matrices, and Their Applications," ACM Transactions on Algorithms 13(2), DOI 10.1145/3039873.**  
   This literature explicitly studies transformations/completions from partial Monge structure to full matrices for algorithmic purposes. The authors need to explain whether their ordinal completion is genuinely model-specific, a simpler special case of known completion techniques, or merely a convenient implementation device.

4. **Emmerich (2026), "Exact and Fast Subset Selection Algorithms for the Bi-objective Integral R2 Indicator," arXiv:2606.23365.**  
   This is a different application, so it is not a priority claim over the contractual model. But it is highly relevant to positioning: it derives a Bellman DP, proves a Monge transition structure, obtains an O(kn log n) divide-and-conquer implementation, and then an O(kn) staircase matrix-search implementation with triangular feasibility. That sequence is almost exactly the generic algorithmic pattern advertised by R35--R36.

I am **not** claiming that any of these papers proves the contractual terminal-array identity, the cap-anchoring theorem, or the continuously minimized terminal Monge inequality. They do not appear to. My point is narrower and more damaging to the current R36 framing:

> Once R35 has proved the model-specific Monge structure, the move from a triangular/partial Monge dynamic program to a linear or near-linear staircase search belongs to a mature algorithmic literature and cannot be positioned only against the original full-matrix SMAWK paper.

The authors need a precise theorem-by-theorem novelty table answering:

- What does R35 prove that is not a standard Monge-DP consequence?
- What does R36 prove that is not a standard partial/staircase-Monge search consequence?
- Is the ordinal padding construction itself new, or is it a special completion of a known kind?
- Why does this special one-sided domain admit deterministic O(k) SMAWK after completion while generic partial totally monotone matrices carry the inverse-Ackermann obstruction?
- Which property of the contractual array removes the generic partial-matrix difficulty?
- Is the same property already formalized in earlier dynamic-programming or Monge-matrix literature under another name?

Until this is done, I do not regard the R36 "linear frontier" result as having a verified priority case.

---

# 4. The R36 total-monotonicity proof is plausible but too compressed for the theorem carrying the revision

I do not currently see a counterexample to the completion actually used by the code. Nevertheless, the proof in the main text is too compressed for a flagship theorem.

The proof currently moves through the following steps in a few sentences:

1. assign lexicographic keys to feasible and padded entries;
2. invoke R35 Monge when four entries are feasible;
3. argue informally that later terminal rows lose columns from the left;
4. argue that program-layer feasible prefixes expand;
5. conclude that the completion is totally monotone in arbitrary submatrices;
6. apply SMAWK.

Every one of these steps is reasonable. They should nevertheless be stated as a formal lemma with all cases.

At minimum I want to see:

### 4.1 A formal definition matched to the implementation

The paper should state total monotonicity for the exact row and column orders used by the implementation, including the strict-preference/tie convention. Because the implementation deliberately changes the order among infeasible entries, "Monge implies total monotonicity" is not by itself the full statement.

### 4.2 Separate completion lemmas for the two one-sided domains

The terminal array has a left-truncated feasible set: later rows lose feasible columns from the left.

The prefix/program array has a right-truncated feasible set whose feasible range expands with row index after globally unreachable predecessor columns have been removed.

These are different completions. Prove them separately. Do not make the generic helper routine with both left and right padding sound more general than the theorem actually is.

### 4.3 All tie cases

The finite key sends ties to the left. The padded keys impose the opposite internal order on left padding and right padding. The proof should explicitly show that a finite tie, a feasible/padded comparison, and a padded/padded comparison cannot create a forbidden reversal under row restriction.

### 4.4 The "all infeasible in the selected submatrix" case

This is exactly the case R36 advertises as missing from R35. It should not be dispatched by prose. Give the two-line order argument formally.

### 4.5 Preservation under addition of the previous DP layer

The previous-layer value is a column term. Therefore the Monge inequality is preserved. State this explicitly as a lemma rather than burying it inside the main theorem proof.

### 4.6 Reachability/contiguity of predecessor columns

The proof says that globally unreachable predecessor columns are discarded. The code exploits the fact that the remaining feasible predecessor set is a contiguous interval in each layer. That invariant should be proved and stated next to the algorithm.

The current exhaustive submatrix tests are excellent regression tests. They are not a substitute for this proof. Given that R36 exists specifically to close the all-submatrices gap, this part should be the most explicit proof in the revision, not one of the shortest.

---

# 5. The central contribution has become too diffuse for a 39-page OPRE lengthy manuscript

The current manuscript is formally within the lengthy-manuscript page limit. That does not settle the editorial question. The current Optimization-area statement explicitly says that the contribution-to-length ratio is part of evaluation.

The present paper contains, in one main article:

- a public-graph quotient of a laminar allocation problem;
- global response-knot and explicit-table complexity;
- matching response-size lower bounds;
- rational bit complexity;
- piecewise-quadratic exact closure;
- shared-circuit storage/query tradeoffs;
- behavioral transducer minimization;
- a worst-case linear writable alphabet;
- deterministic restricted-memory segmentation;
- a radial-spread comparative static;
- fixed-codebook randomization;
- globally optimized continuous randomized codebooks;
- a pathwise-randomization impossibility result;
- Monge structure;
- divide-and-conquer acceleration;
- staircase completion and SMAWK;
- a shared-table comparator with supporting cuts;
- several generations of computational evidence.

This reads less like one paper with a sharp central result and more like a research program compressed into the maximum admissible main-paper length.

The problem is visible even in the title. "Exact Parametric Quotients and Minimal Additional Writable Memory" describes the R31 core. R36's newest theorem is about linear matrix search for a restricted-memory renewal design problem. The two are connected, but not tightly enough for the latest acceleration to carry the significance burden of the entire 39-page article.

I recommend a structural decision rather than more additive revision:

### Option A: make the quotient/memory theorem the paper

Center the article on:

- compact parametric response closure;
- tight explicit-output versus shared-circuit representation;
- behavioral minimization and exact additional-memory complexity;
- one clean renewal example demonstrating economic value.

Move the globally optimized randomized frontier and Monge/SMAWK layers to a separate paper.

### Option B: make the restricted-memory design frontier the paper

Center the article on:

- deterministic versus expected-participation memory design;
- global continuous randomized codebooks;
- pathwise participation;
- Monge structure and exact linear frontier algorithms.

Then reduce the quotient compiler to the minimum background needed to motivate the memory budget.

I do not recommend keeping every R31--R36 result in the main article merely because each result is correct.

---

# 6. The exact compiler remains architecturally narrow, so the top-journal significance must come from the decision insight

The exact quotient/compiler requires a strong combination of assumptions:

- one scalar additive commitment;
- positive payment coefficients;
- separable concave local rewards;
- interval controls;
- exogenous public transitions;
- finite acyclic public graph;
- public-state-sufficient continuation caps;
- no switching cost in the scalar-reflection theorem;
- no coupled vector commitments.

R33 extends the local reward shape materially, which is useful. But the paper itself concedes that switching and coupled commitments break the scalar reflection argument.

This means the paper should not rely primarily on "we can solve a dynamic contract exactly" as the top-journal case. The unfolded optimization has already been mapped to classical laminar allocation. The compact parametric representation is the real mathematical object.

For *Operations Research*, I would therefore expect one of two stronger outcomes:

1. a broadly reusable structural theorem that applies across a significant class of operational models; or
2. a deep decision insight showing why the exact memory architecture changes an operational design problem in a way that would matter to OR researchers beyond this constructed renewal family.

At present, the mathematical structure is deep but specialized, while the operational interpretation is still too schematic.

---

# 7. The randomized-memory benefit is economically fragile because it disappears under pathwise participation

This is not a mathematical flaw. It is an interpretation problem that becomes more important precisely because the authors have now proved the pathwise theorem.

Under the expected-participation institution, a branch accepts before a private controller draw. The draw can produce a realized terminal payment above that branch's cap so long as the conditional expectation satisfies the cap.

Under pathwise participation, the benefit of randomization disappears entirely in the renewal architecture.

That is a sharp and potentially interesting result. But the manuscript currently treats the two institutions more symmetrically than their operational plausibility warrants.

The authors should explain, with a concrete service-contract mechanism:

- who observes the controller's private draw;
- when the customer can exit;
- whether the cap represents expected utility, an ex ante service guarantee, or an ex post enforceable constraint;
- whether violations on individual realizations are legally/operationally permitted;
- how the lottery is communicated;
- what makes the random seed private rather than contractually observable state;
- whether repeated customers can condition on realized service histories.

Without this mechanism, the striking randomized loss reductions can look like an artifact of moving participation before an internal randomization device.

A useful extension would analyze an intermediate institution rather than only the two extremes. Examples include:

- chance-constrained realization caps;
- bounded shortfall;
- CVaR-style continuation constraints;
- a contractible random seed;
- repeated participation after observing past lottery outcomes.

I am not requiring all of these. I am requiring enough institutional modeling to show that the expected-participation frontier represents a realistic decision problem rather than a mathematically permissive benchmark.

---

# 8. "Minimal additional writable memory" is now carefully qualified, but the operational resource tradeoff is still incomplete

The title is much better than earlier versions because it says **additional writable memory**.

Still, the operational optimization of memory cost remains only partially modeled.

The controller uses:

- a free public vertex;
- a writable symbol;
- a read-only program;
- potentially quadratic explicit response tables or a shared circuit;
- rational coefficients with nontrivial bit lengths;
- offline compilation.

The paper correctly reports these separately. But when it discusses "pricing a symbol budget," it prices only one resource dimension.

An actual implementation may trade:

- writable state;
- read-only table size;
- evaluation time;
- coefficient precision;
- compilation cost;
- communication/interpretability of randomized symbols.

The R33 shared-circuit result already demonstrates that read-only memory and query time can substitute for one another. This is evidence that "memory" is not one scalar operational resource.

The paper would be stronger if it formulated one integrated design objective, even a stylized one, such as:

minimize service loss + lambda_writable * writable bits + lambda_readonly * read-only storage + lambda_time * evaluation work.

Then the current exact frontiers would become primitives of a genuine resource-allocation decision rather than separate complexity statistics.

---

# 9. The R36 computational evidence verifies correctness but does not establish practical acceleration

The computational package is honest about this, which I appreciate.

For the expected-participation frontier:

- at 16 branches R36 uses 534 economic queries versus 289 for R35;
- at 512 branches R36 still uses 31,551 versus 27,600 and is slightly slower in wall time;
- at 1,024 branches it begins to beat R35 in the reported wall time;
- at 2,048 branches it uses 128,966 versus 135,597 and is faster in the reported run.

For the deterministic/pathwise frontier:

- at 2,048 branches R36 still uses 163,838 cell evaluations versus 153,180 for R35;
- the reported R36 wall time remains slower.

This is perfectly consistent with a better asymptotic bound and worse constants. But it means the empirical section supports **correctness and asymptotics**, not a strong practical-computation claim.

If R36 is to remain a major part of an OPRE submission, I would require a more meaningful algorithmic study:

1. Larger instances until the deterministic crossover is observed or a resource limit is reached and reported transparently.
2. Memory measurements, not only oracle counts and wall time.
3. A compiled/optimized implementation or at least an explanation of why Python Fraction timings are representative of the decision problem.
4. A comparison with a generic Monge/staircase implementation that is not authored specifically for this paper.
5. Where possible, comparison with a standard solver on the finite reduced problem, not because the solver should win asymptotically, but because practical relevance is part of the claim.
6. A decomposition of runtime into rational arithmetic, key evaluations, SMAWK book-keeping, and reconstruction.

The current same-input R34/R35/R36 comparison is a good scientific regression test. It is not enough to demonstrate operational computational value.

---

# 10. The complexity model should be stated in one place and made audit-proof

The manuscript uses several legitimate but different complexity notions:

- arithmetic operations;
- exact rational comparisons;
- coefficient/event height;
- conservative Turing bit complexity;
- oracle evaluations;
- Python wall time;
- persistent storage;
- output reconstruction.

These are currently distributed across R31, R32, R34, R35, and R36.

For the main R36 theorem, I recommend a single accounting table stating:

| Cost component | Included? | Bound |
|---|---|---|
| Input sorting | conditional on already ordered caps; otherwise add sorting |
| Prefix moments | yes |
| Terminal interval minimization | yes |
| SMAWK key comparisons | yes |
| Repeated feasible-cost reevaluation | yes |
| Padding comparisons | yes |
| Backpointers | yes |
| Reconstructing all codebooks through budget m | yes |
| Writing the output codebooks | yes |
| Integer/gcd cost | in bit bound |
| Read-only inherited model data | explicitly state |
| External solver preprocessing | not applicable |

The theorem should also say directly why every rational value evaluated by the SMAWK implementation has no greater algebraic/bit-height dependence than a candidate already present in R34. That fact is plausible, but currently the reader must infer it from "the arithmetic expressions are unchanged."

One more point: the O(mk) theorem assumes ordered rational inputs. This is acceptable. But the abstract should not present "linear work per budget layer" without reminding readers that ordering is part of the interface and exact rational arithmetic is the computational model.

---

# 11. The latest priority problem is not cured by saying "SMAWK is classical"

The response letter repeatedly says that SMAWK itself is classical. That is necessary but not sufficient.

There are at least three levels of prior art:

1. **full totally monotone matrix search** -- classical SMAWK;
2. **partial/staircase totally monotone or Monge matrix search** -- a specialized literature since at least Klawe--Kleitman;
3. **Monge-optimized dynamic programming with triangular predecessor feasibility** -- a broad algorithmic pattern across applications.

R36 currently acknowledges level 1 and partly level 3 through Yao. It does not adequately acknowledge level 2.

The paper's actual novelty may still be real. A defensible statement might be:

> For these two contractual arrays, the feasible domains have a special one-sided nesting and the model-specific finite costs satisfy a strict single-crossing property. This permits an explicit deterministic ordinal completion to a full totally monotone matrix, after which standard SMAWK applies. The new result is the proof that the continuously minimized contractual terminal cost and each DP layer admit this completion; it is not a general algorithm for staircase Monge matrices.

If that is the intended claim, prove it and compare it directly with the partial-matrix literature.

Without that comparison, the current wording leaves the reader to infer more novelty than is justified.

---

# 12. Area fit is increasingly unclear

The manuscript labels itself for **Stochastic Models**.

Yet the newest major results are:

- exact parametric representation;
- automata/state minimization;
- finite-alphabet design;
- Monge dynamic programming;
- SMAWK acceleration;
- bit complexity.

The stochastic process itself is exogenous and finite. There is little stochastic-process analysis in the conventional sense; randomness mainly weights branches and distinguishes expected from pathwise feasibility.

This does not make the paper inappropriate for *Operations Research*, but the authors should reconsider whether the natural editorial home is Optimization, Data/Software/Computation, or Stochastic Models. The current area label makes the operational-system significance question harder, because the model is deliberately stripped down to expose algorithmic structure.

A clearer editorial identity would also force the authors to decide what the paper is fundamentally about.

---

# 13. The manuscript still lacks real or calibrated operational evidence

The authors are admirably explicit that the computational instances are synthetic and not calibrated service data.

For a pure theory paper this is not automatically a problem.

But the paper repeatedly motivates itself through service agreements, renewals, customer exit, continuation obligations, and operational memory. If those are not merely metaphors, the paper should demonstrate at least one credible operational setting in which:

- the cap architecture arises naturally;
- recombination is operationally meaningful;
- the same public state can hide different accepted continuation obligations;
- writable state is actually costly;
- the expected/pathwise participation distinction has an institutional interpretation;
- the size of the exact or approximate memory frontier is decision-relevant.

A calibrated case study is one route. A carefully documented stylized industry mechanism is another. What is not enough is to keep adding exact synthetic cases while making broad service-design claims.

---

# 14. Reproducibility is strong, but the packaging has become over-engineered

This is a minor issue compared with the scientific objections, but it is worth fixing.

The R36 branch contains an unusually elaborate transport/build system, preservation manifests, base64 transport chunks, workflow materialization, predecessor wrappers, multiple generations of supplementary material, and a root computational supplement that still identifies itself as an older revision.

The validated record is impressive, but a reader should not need to understand the revision machinery to identify the authoritative scientific package.

For a submission-ready branch, I recommend:

- one authoritative main source;
- one authoritative electronic companion;
- one code directory;
- one reproducibility script;
- one machine-readable manifest;
- a short version-history note.

The historical preservation archive can remain in the repository, but it should not compete with the current reader for attention.

---

# 15. Required changes before I would support another OPRE review

I would not recommend another incremental R37 that adds one more theorem layer. I would want a structural revision.

The minimum package is:

1. **Close the staircase/partial-Monge priority gap.** Add Klawe--Kleitman, Chan, and the relevant partial-Monge completion/search literature; explain precisely what is new in R36.
2. **Rewrite the R36 proof as a formal completion theorem.** Treat terminal and prefix domains separately, cover ties and all-infeasible submatrices, and prove the predecessor-contiguity invariant used by the implementation.
3. **Choose one central paper identity.** Either the compact quotient/minimal-memory paper or the restricted-memory frontier/Monge algorithm paper. Do not continue accumulating both at maximum length.
4. **Strengthen the operational institution.** Explain when expected-participation lotteries are contractually meaningful and why writable symbols are the scarce resource.
5. **Integrate resource accounting.** Writable state, read-only representation, query work, and bit precision should enter one operational design discussion rather than four disconnected complexity statements.
6. **Rework the computational section around the actual residual claims.** Keep exact regression tests, but add practical scale, memory, and external algorithmic comparators.
7. **Reconsider the submission area and narrative.** The paper should read as one contribution aimed at one OPRE audience.
8. **Cut aggressively.** The paper is technically rich enough that removal of material would improve, not weaken, the case for significance.

I emphasize the last point. The repository's cumulative development history should not dictate the final article structure.

---

# 16. Minor and presentation comments

1. The abstract is admirably precise but too dense: nearly every sentence introduces a different theorem family.
2. "Symbolic staircase completion" should not be used as if it names a new general algorithmic primitive unless priority is established.
3. The distinction between deterministic memory and pathwise participation is easy to lose because both eventually use the deterministic frontier. A small institutional diagram would help.
4. The role of the saturated root promise should appear earlier in the randomized-memory discussion. It is not a cosmetic normalization; it drives branchwise binding and several structural reductions.
5. The exact threshold "k symbols" depends on distinct full-information actions. The uniqueness assumptions should remain visible whenever that threshold is summarized.
6. The shared-circuit proposition is useful, but "linear storage" should always specify post-compilation persistent storage, as the paper mostly does.
7. The term "global randomized optimum" should always be read under the paper's expected-participation architecture and charged-information convention.
8. The conclusions currently summarize too many theorem families. They should instead explain the one or two takeaways that an OR reader should remember.
9. If R36 remains, give pseudocode in the main paper for the two completed matrix interfaces. The generic SMAWK code itself can remain in the companion.
10. The bibliography should distinguish full-matrix SMAWK, partial/staircase matrix search, Monge DP optimization, and model-specific contractual structure as four different layers of prior work.

---

# 17. Confidential comments to the editor

This is a difficult paper to evaluate because the revision history is unusually rapid and the latest version is much stronger than the manuscript that generated the earlier independent rejection.

I would not reject R36 for lack of rigor. I would also not reject it because the authors use synthetic data. The mathematical package is sophisticated and the reproducibility discipline is above average.

My concern is that the manuscript has responded to every objection by adding another mathematically valid layer, and as a result the publication case has become less focused rather than more focused. The latest R36 contribution is an algorithmic acceleration on a Monge/staircase dynamic program. That is exactly the point at which the missing partial-Monge literature matters most. A top OR journal should not publish the linear-work claim as a principal novelty until that literature has been confronted carefully.

I therefore recommend **Reject**, rather than another major-revision cycle on the same cumulative manuscript. I would be open to a fresh submission that makes a decisive structural choice:

- a compact parametric quotient and exact controller-memory paper; or
- a restricted-memory service-design and Monge-frontier paper.

Either could be strong. The current union is too broad, too close to the page ceiling, and insufficiently differentiated from mature algorithmic machinery at the point of its newest claimed advance.

---

# 18. External literature and editorial material specifically consulted for this review

The following items are not asserted to solve the paper's contractual model. They are relevant to evaluating the claimed algorithmic priority and journal fit.

- Aggarwal A, Klawe MM, Moran S, Shor P, Wilber R (1987), "Geometric applications of a matrix-searching algorithm," *Algorithmica* 2:195--208.
- Klawe MM, Kleitman DJ (1990), "An Almost Linear Time Algorithm for Generalized Matrix Searching," *SIAM Journal on Discrete Mathematics* 3(1):81--97. DOI: https://doi.org/10.1137/0403009
- Kaplan H, Mozes S, Nussbaum Y, Sharir M (2017), "Submatrix Maximum Queries in Monge Matrices and Partial Monge Matrices, and Their Applications," *ACM Transactions on Algorithms* 13(2). DOI: https://doi.org/10.1145/3039873
- Chan TM (2021), "(Near-)Linear-Time Randomized Algorithms for Row Minima in Monge Partial Matrices and Related Problems," *Proceedings of SODA 2021*, 1465--1482. DOI: https://doi.org/10.1137/1.9781611976465.88
- Emmerich MTM (2026), "Exact and Fast Subset Selection Algorithms for the Bi-objective Integral R2 Indicator," arXiv:2606.23365. https://arxiv.org/abs/2606.23365
- *Operations Research*, Editor-in-Chief Editorial Statement: https://pubsonline.informs.org/page/opre/editorial-statement
- *Operations Research*, Area Editors' Statements: https://pubsonline.informs.org/page/opre/editorial-statement/area-editors-statements
- *Operations Research*, Submission Guidelines: https://pubsonline.informs.org/page/opre/submission-guidelines

---

## Bottom line

R36 is a strong piece of mathematical engineering and a genuine improvement over R30. The main theorem chain appears plausible, the authors have been unusually responsive, and the evidence package is careful.

But a top-journal referee should not confuse responsiveness and volume of technically correct results with a sufficiently sharp publication contribution.

**I cannot recommend publication of the present 39-page cumulative manuscript.** The newest linear-frontier theorem sits too close to an established partial/staircase-Monge algorithmic literature that the paper does not yet discuss; the proof of the special completion is too compressed relative to its role; the randomized-memory insight remains institution-sensitive; the practical algorithmic gain is not yet demonstrated across both frontiers; and the manuscript has reached the point where adding results is reducing rather than increasing its editorial clarity.

The next revision should be a **reconstruction**, not another additive layer.
