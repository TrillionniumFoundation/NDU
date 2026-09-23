# Response to the independent R30 Operations Research report — R33

**Manuscript:** Accepted Service Adaptation: Exact Parametric Quotients and Minimal Additional Writable Memory.

**Review source:** `reviews/operation_research_referee_report_r30_independent_2026-09-23.md` at `a017f474619e86be533547acac87a3c8354f64cf`, reviewing `fdc1ed47d46dc9d3344b8bce47c1670f11dcd475`.

**Scientific predecessor:** R32, `238bfdb24d93439a545551d275a0c9189dbc017b`.

R31 and R32 already made substantial responses to this report. This response does not present their additions as newly proved in R33. We preserve their theorem modules and computational records and add a piecewise-quadratic extension, an exact shared-representation tradeoff, a randomized restricted-memory characterization, a solved strict separation, and new independent exact tests. The earlier same-day report based on an obsolete branch tip is not treated as the latest scientific assessment.

## 1. Version audit and genuine scientific changes

The new root manuscript and electronic companion input new R33 theorem and evidence modules. The exact predecessor wrappers are archived in `predecessor/` within this revision directory, along with their source identity. The new branch is isolated from `main`, all review branches, and earlier revision branches. Existing historical files are retained. The build records the scientific source commit, PDF hashes, and validation outcome. A branch name or a copied report is not offered as a revision.

## 2. Preserve the accepted R30 progress

The occurrence-to-vertex quotient, laminar allocation equivalence, cap reflection, binary coefficient bound, minimized reached transducer, heterogeneous deterministic renewal frontier, outside-option radial result, and shared-table supporting cuts remain in the article. R31's matching chain lower bound remains unchanged. Broader switching, deployment, and unfavorable cache evidence remain in the retained source volumes. No theorem is removed to evade a criticism.

## 3. Parametric optimization and residual priority (request A)

R31's model/literature section already cites and differentiates Klimm–Warode and Harks–Klimm–Peis, and acknowledges that normalized memoization gives the same recurrence. R33 adds a constructive flow reduction in `extensions.tex`: each occurrence has a subtree-flow arc with its continuation capacity and local allocation arcs with transformed piecewise-quadratic convex costs. Root supply is the primal parameter; the compiler uses the conjugate dual price, connected by inversion.

This answers the subsumption question constructively rather than by asserting that the model is unrelated to flow. Zero-cost tree arcs, bounds, and the size of the occurrence network must be handled before attributing applicability or timing to a particular published implementation. The claim is a compact-input event budget and representation tradeoff, not a new generic parametric path principle or a stronger theorem for all network-flow problems.

The new exact extension permits continuous piecewise-quadratic rewards with positive curvature on every piece and downward derivative jumps. Its event budget is `2J + N`, or `sum(m+1) + N` for differentiable joins, where J counts local nonfixed pieces. This is not merely a repartition of a fixed quadratic. Rational preprocessing includes reduced arithmetic, exact sorting, and comparisons. The quadratic result is retained as a specialization.

## 4. Classical minimization versus model-specific structure (request C)

R31's `memory_theory.tex` explicitly constructs a deterministic output transducer and identifies backward signatures as classical behavioral minimization. It cites the aggregation, MDP minimization, and Moore-machine literature requested by the referee. R33 retains this language and does not claim the partition-refinement principle as new.

The added model-specific result is that local piecewise curvature and marginal jumps do not enlarge the `N+1` raw carried-price bound. Only cap barriers write new prices. Price-order contiguity and the minimum additional writable alphabet continue to apply. Thus more complicated local service costs enlarge the compiler's local response data without automatically enlarging the changing record carried across recombination.

## 5. Observation architecture and three memory counts (request D)

The title and abstract explicitly say **additional writable** memory. The public vertex/date and read-only program are not charged to this alphabet; inherited branch identities, promises, tiers, and retained seeds are charged if they carry otherwise unobserved history. The query is fixed. `K_* = max_v c_v` and `C_* = sum_v c_v` remain separately reported.

R33 adds a fourth distinction within read-only storage: explicit vertex tables versus a shared circuit. The earlier quadratic lower bound counts separately materialized affine pieces. It is not a lower bound for every compressed representation. After compilation, local response curves, graph links, caps, barriers, and the global event list give a linear-size shared circuit in the piecewise input. Evaluation and inversion costs are stated explicitly. This is a persistent-storage result, not a claim of linear preprocessing peak memory or a free class-transition table.

## 6. Dynamic-contract policy graphs

R31's comparison to Zhang (2012) is retained in the model/literature section and foregrounded in the new introduction. Finite contract policy graphs themselves are predecessor ideas. The current subclass is public-information, finite-horizon, scalar-commitment, and exact for a fixed root promise. It does not solve adverse selection or inherit an approximation theorem as an exact result.

## 7. Tightness and meaningful generalization (request B)

R31 already proved the exact chain count: `2n` distinct knots and `n^2 + 2n` explicit response segments for an n-vertex polynomially encoded chain. Its renewal family also gives `K_* = N - 2`. R33 preserves all three results.

The new theorem goes beyond the alternative requested by the referee by also generalizing the exact compiler to genuine piecewise quadratics, including kink plateaus in the inverse marginal map. It states the event budget, explicit storage, arithmetic and bit complexity, exact conjugate certificate, and continued finite memory bound. The new circuit proposition explains why an explicit-output lower bound and smaller shared representation can simultaneously hold. A seven-size exact replay checks both counts on the same family; it is not used as the proof.

## 8. Dispersion scope (request E)

The ordered radial-spread theorem is retained with its original quantifiers: fixed positive probabilities and any fixed strictly ordered weighted-zero-mean direction. Neither the abstract nor the introduction claims an arbitrary convex-order, majorization, or variance monotonicity theorem. The main economic addition is instead a rigorously characterized role for restricted-memory lotteries, described under comment 13 below. No unsupported dispersion order is introduced.

## 9. Significance of the exact subclass

We respond mathematically rather than by relabeling the original narrow theorem. Positive-curvature piecewise quadratics with marginal jumps remain exactly compilable; the relevant complexity counts local primitive pieces and public caps. A circuit gives a different storage/query design point. A conditional-expectation renewal model supplies an exact randomized restricted-memory characterization and a strict solved example. These additions connect representation design to an operational memory allocation question.

Scalar commitments, separability, exogenous acyclic public transitions, and public-state-sufficient caps remain substantive assumptions. The new proof does not assert that coupled vector commitments or switching inherit the same closure. Their earlier theory is preserved rather than discarded.

## 10. Computational comparison aligned to complete paths (request F)

The inherited occurrence-indexed, generic convex, public-promise, and repeated-query studies remain unchanged and identifiable as inherited evidence. R33 adds an independently coded parametric KKT enumerator on small unfoldings. It constructs the entire rational optimizer path by active sets and compares every affine cell and finite boundary against the compiler, not just selected root promises. Four instances each enumerate 130 candidate sets, and all complete paths agree exactly.

Twenty-four recombining piecewise inputs add 4,170 direct local checks, 834 whole-graph circuit comparisons, 834 circuit inversions, and 836 exact primal–dual certificates including edge cases. Chain sizes through 128 compare explicit and circuit representation counts on identical inputs.

**Evidence limit:** the KKT enumerator is exponential and deliberately small. It is not an implementation of Klimm–Warode, an experiment on service data, or a performance comparison with a state-of-the-art specialized solver. Consequently this revision supplies a relevant complete-path reference and structural representation comparison, but does not report a published-solver timing result that was not run. Comparative speed superiority is not used to support the theoretical claims.

## 11. Bit-complexity and intermediate coefficients

The existing theorem already states lowest-term reduction and includes sorting/comparisons. The extension states this again for the piecewise coefficient-event compiler. Its coefficient sources include rational join values and local inverse-curvature slopes. Conceptual common denominators bound heights but are not materialized. Each cap crossing is a ratio of bounded-height coefficients. The bound is implementation-specific, polynomial in ordinary rational encoding, and not a strong-polynomial claim.

Aggregate certificate totals are distinguished from response coefficients. The new bounded-conjugate certificate handles a nondifferentiable local join without imposing a nonexistent derivative. Exact local conjugate equality, cap complementarity, and occupation-flow telescoping establish the dual equality.

## 12. Minimal-machine statement

The classical/model-specific decomposition in comment 4 is retained. New local breakpoints can increase the number of response segments without adding writable prices: this sharpens the relation between the compiled continuous problem and its reached transducer. No claim is made that `K_*` minimizes a query-uniform controller, total implementation bits, or a controller whose public observation must also be encoded.

## 13. Restricted randomized frontiers

The new theorem in `randomized_memory.tex` directly addresses the referee's proposed strengthening. For fixed terminal levels, the optimal expected reward at a mean payment is the adjacent-chord concave envelope. The branch mean is the smaller of its cap and the highest codeword. This yields an exact variational formula for the randomized frontier, including heterogeneous branch costs and probabilities. It removes the branchwise encoder optimization; it does not claim a general polynomial algorithm for globally choosing all continuous levels.

The accompanying proposition globally solves the three-branch quadratic example with caps `1/4, 1/2, 3/4`. Two deterministic symbols lose `1/8`; the best two-symbol expected-participation lottery loses `1/96`. Three distinct symbols are still necessary for the exact optimum. The proof optimizes all feasible two-level codebooks through three analytic cases, rather than relying on a numerical search.

On the middle branch, the high draw exceeds that branch's expected cap. The institution evaluates participation before this private draw. We expressly do not call the lottery pathwise feasible. The existing deterministic frontier and randomized exact-optimum lower bound retain their respective domains.

## 14. Shared-table comparator

The graph-sized quadratic zero-release formulation, fixed-query compiler, tied-normal splitting, and supporting cuts remain intact in the main article. The derivative-based original supporting-cut proof is used under its original quadratic assumptions. The new conjugate certificate is separately stated for the piecewise extension. No unsupported finite-cut outer-design guarantee is added.

## 15. Presentation

The new abstract has 183 whitespace-delimited words and is text-only. The introduction contains no equations or mathematical notation. The article retains 11-point type, one-and-a-half spacing, one-inch margins, anonymous author metadata, author–year references, numbered theorem statements, and proof-driven organization. New and inherited main tables appear after references. The earlier referee-facing accounting discussion is preserved as an electronic-companion concordance rather than leading the article with revision-process prose. Final reader PDFs, cross-document references, and layout warnings are checked by the build.

The source record separates preservation of prior results from claims about newly executed checks. Journal acceptance and exhaustive priority are not asserted by the authors' own response.

## 16–17. Consolidated response and editorial question

A: The literature distinctions are retained and strengthened by an explicit flow reduction.
B: Existing matching bounds are retained; a genuine piecewise extension and shared representation tradeoff are added.
C: Classical minimization remains explicitly classical; new local-complexity versus writable-price consequences are proved.
D: Writable alphabet, combined states, explicit read-only tables, shared read-only circuit, and coefficient precision are separated.
E: The radial result remains correctly scoped, with a new exact randomized economic result rather than an unsupported dispersion order.
F: New experiments compare complete parametric paths and representations; published-specialist comparative timing remains unperformed and is not claimed.

The resubmission therefore contains new mathematical and computational content, not only a priority matrix. All conclusions are tied to stated assumptions, exact proofs, and identifiable evidence for another independent review.
