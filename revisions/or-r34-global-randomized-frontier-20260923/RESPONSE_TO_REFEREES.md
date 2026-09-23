# Response to the independent Operations Research referee report — R34

**Manuscript:** Accepted Service Adaptation: Exact Parametric Quotients and Minimal Additional Writable Memory  
**Revision branch:** `revision/ndu-operations-research-r34-global-randomized-frontier-20260923`  
**Reviewed report:** `reviews/operation_research_referee_report_r30_independent_2026-09-23.md`, report commit `a017f474619e86be533547acac87a3c8354f64cf`, report blob `2ea2deaa03f063e23665c7f6a9b1a12dd13573e7`  
**Scientific starting point:** R33, `38b3f264e371758054d94a9f94088ae17a816241`. The report reviewed R30 at `fdc1ed47d46dc9d3344b8bce47c1670f11dcd475`; it did not review R31–R34.

We thank the referee for separating correctness, priority, representation complexity, and institutional interpretation. We have retained the positive mathematical content of the reviewed paper and its subsequent revisions. This response identifies which requests were answered in R31–R33 and what is added in R34; it does not attribute inherited results to this revision.

R34 replaces a remaining variational design question by a global constructive theorem. In the heterogeneous quadratic renewal model, an optimal randomized codebook has cap-anchored levels except for one continuous highest level. The highest level is solved analytically on each cap interval, and an ordered dynamic program computes the exact frontier for every prescribed alphabet budget. A second theorem proves that private-draw pathwise participation restores the deterministic frontier at every budget. A new exact example has an optimal highest level strictly between branch caps. All proofs are in the main article.

## 1. Version audit and the actual revision delta (report §§1–2)

We agree that a branch name is not evidence of a scientific revision. R34 starts from the last successfully built R33 commit, not from the obsolete nominal R30 state. The new `global_frontier.tex` module is included in the root article. The article also adds a new evidence subsection, an exact frontier table, and updated introduction, abstract, conclusions, and reproducibility entry. The electronic companion adds implementation and independent-validation details. The original wrappers are archived verbatim in `predecessor/`; 35 inherited reader/source/evidence files are hash-checked for preservation. All broader historical files survive through the unchanged base tree.

The final `BUILD_VALIDATION.json` binds both reader PDFs to a scientific source commit and content hashes. A local or staged source is not called a remote validated reader. The source commit and publication commit can differ because the second commit adds the generated PDFs and build record.

## 2. Parametric optimization priority (report §§3, 11, 16A)

The R31–R33 article already incorporates the requested comparisons with Klimm and Warode, Harks–Klimm–Peis, classical laminar allocation, and modern nested resource-allocation algorithms. We retain those comparisons, the explicit occurrence-to-public-vertex normalization, the convex-cost-flow representation, the distinction between supply and price parameterizations, and the shared-circuit storage/query alternative. The reference list retains all requested papers. The claims remain attached to compact-input event bounds and their exact construction, not to the invention of marginal allocation, memoization, or generic parametric programming.

R34 does not rename a classical segmentation recurrence as a new principle. The new main section expressly calls that recurrence standard. The result being established is a reduction of the joint continuous randomized codebook problem to cap anchors plus one continuous terminal level, including the contractual tail cost created when that level is below a branch cap. That reduction is proved before the recurrence is used. The explicit rational terminal formula and the prefix dynamic program then provide the global optimum, not only an encoding optimum conditional on a codebook.

For the new implementation the Turing statement includes exact fraction reduction, comparisons, clamping, output reconstruction, and storage. The companion distinguishes conceptual common denominators from quantities actually constructed. The bound is for this algorithm on rational quadratic inputs. An optional general-convex-intermediate-cost observation retains a one-dimensional minimization oracle, not an unjustified exact rational claim.

## 3. Machine minimization and memory accounting (report §§4–5, 12, 16C–D)

The classical transducer-minimization interpretation, the citations to Bean–Birge–Smith, Givan–Dean–Greig, and Peyrière, and the separation of contract-specific price ordering from generic backward refinement are inherited intact. The article continues to distinguish the additional writable alphabet, combined reached public-state/class pairs, and read-only program/response storage. Its title and abstract retain the additional-writable-memory qualifier. The root query and current public observation remain free inputs under the stated architecture; past branch identity, a previous action, or a retained private seed cannot be introduced as an uncharged state.

R34 adds an institutional consequence rather than silently broadening that architecture. In the pathwise theorem, even draw-specific intermediate tiers are allowed. Root saturation forces branch payments to equal their caps almost surely. For any fixed terminal codebook, the highest eligible level dominates randomization over eligible levels, so optimizing codebooks yields the deterministic frontier. The proof explains why a fresh independent terminal draw cannot circumvent this conclusion and why a shared retained seed would change the charged state. Under expected participation, the different admissible class is solved by the new global randomized algorithm.

## 4. Dynamic-contract policy graphs (report §6, 16A)

The Zhang (2012) comparison is preserved in the introduction and model/literature module. The present fixed-query exact public-information machine is distinguished from finite policy graphs approximating an infinite-horizon adverse-selection continuation frontier. R34 adds a computable budget/value tradeoff for the former architecture; it does not assert a global solution to the latter model or transfer its memory accounting conventions.

## 5. Tightness and scope (report §§7, 9, 16B)

The R31 chain construction and linear memory family supply matching quadratic explicit-table and linear knot/alphabet orders. R33 additionally establishes continuous piecewise-quadratic closure, including downward marginal jumps, with a local-piece event budget. Both remain in the article without deleting the original quadratic theorem. The shared-circuit result is also retained: a lower bound for separately materialized vertex tables is not a lower bound for every shared representation.

R34 strengthens the renewal design result beyond the isolated two-symbol example. The main theorem permits arbitrary positive branch probabilities and heterogeneous nonnegative quadratic intermediate costs and computes all requested alphabet frontiers in exact polynomial time. Its one-free-level representation is proved; it is not inferred from numerical patterns. This is a new solved design problem inside the renewal family, not a claim that switching or vector promises satisfy the scalar compiler's assumptions.

## 6. Outside-option comparative statics (report §8, 16E)

The existing fixed-direction mean-preserving radial-spread theorem, its hypotheses, and its scope remain unchanged. We do not replace it by an unproved assertion about every convex-order or majorization comparison. R34 adds a different positive economic result: the complete expected-participation memory frontier can be computed, while imposing the cap on each private realization gives exactly the deterministic frontier. An operator can therefore compare alphabet costs across the two stated contractual institutions. This adds an institutional design conclusion without deleting or misdescribing the radial theorem.

## 7. Computational evidence and baselines (report §10, 16F)

The retained complete-parametric-path comparator is independently coded KKT enumeration; the piecewise compiler, circuit inversion, and conjugate certificates are rerun from unchanged scripts in a temporary directory. Their inherited result files are not overwritten.

The R34 comparator targets the new global optimization object. It enumerates every cap-anchored prefix and every final-level interval on small instances, recovers the interval quadratic from three direct branchwise evaluations, and minimizes it analytically. It does not use the production DP or moment routines. Reduction to these candidates is justified by the theorem, not by the test itself. Independent nonanchor grids provide further falsification tests, while replay checks actual symbol probabilities, intermediate tiers, expected caps, and the root promise. Realization-level cap violations are explicitly flagged rather than concealed by an expectation certificate.

The successful exact suite covers 51 small cases, 1,932 exhaustive candidate comparisons, 446 frontier equalities, 1,073 direct grid comparisons, 1,346 moment identities, 255 controller replays including the larger family, and ten rejected invalid inputs. Four scale sizes, 16–128 branches, compute every budget through eight. Runtime metadata are recorded rather than hard-coded as universal timings.

These are exact implementation and global-frontier comparisons. We have not run a published specialized parametric-flow solver, and we do not label an in-house KKT enumerator or the new exhaustive comparator as such an implementation. The paper does not rest its novelty on speed ratios against an un-memoized scenario tree. The service instances remain synthetic, not empirical calibration. These boundaries remain visible in the manuscript and reproducibility records.

## 8. Restricted randomized frontiers (report §13)

This request receives the principal new theorem-level response. The fixed-codebook adjacent-lottery formula is retained and now followed by a global optimization theorem for quadratic renewal primitives. Lemma `lem:r34-anchor` proves the cap-anchor representation; Theorem `thm:r34-global` gives the exact frontier, rational terminal optimizer, backtracking construction, arithmetic/storage counts, and a conservative bit bound. Proposition `prop:r34-offcap` demonstrates that optimizing only cap-valued codebooks is insufficient.

For caps `(1/4,1/2,3/4)` and probabilities `(7/20,3/5,1/20)`, the optimal two-level codebook is `(1/4,5/8)` with expected loss `23/1280`. Every feasible cap-only codebook with at most two levels has loss at least `3/160`. The deterministic/pathwise optimum is also `3/160`. The inherited uniform example is reproduced: randomized loss `1/96` versus deterministic loss `1/8`. Three symbols achieve zero loss in both examples and both participation institutions. Exact optimum thresholds and subthreshold randomized improvements are therefore kept logically separate.

## 9. Shared comparator and presentation (report §§14–15)

The optimized shared-table comparator, tied normal-cone splitting, and supporting inequalities remain unchanged. No finite-cut guarantee for the continuous outer problem is added. The new theorem package is incorporated additively, with its full proofs in the main article and implementation detail in the companion.

The reader keeps 11-point type, 1.5 spacing, one-inch margins, an anonymous title page, a text-only abstract under 200 words, an equation-free introduction, author–year references, and tables collected after the reference list. To preserve the complete inherited proofs and include the new global/institutional results, the build uses the journal's Lengthy Manuscript category rather than deleting scientific content to preserve a 30-page wrapper. The local build produced 36 total main pages and 17 companion pages; the committed build record is authoritative for the final PDFs. No submission to ScholarOne or declaration of author conflicts has been performed on the authors' behalf.

## Requested reassessment

We ask the referee to assess the retained exact quotient/representation results together with the new global randomized frontier and all-budget pathwise theorem. The new proofs make the contractual-memory component constructive at restricted budgets, and the off-cap example rules out a superficially plausible discrete shortcut. The response does not claim that a clean build, exact arithmetic, or a repository checklist determines publication priority or acceptance; it supplies identifiable mathematical results and reproducible evidence for that assessment.
