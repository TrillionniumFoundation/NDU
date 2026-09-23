# Response to the Referee: Revision R36

**Manuscript:** Accepted Service Adaptation: Exact Parametric Quotients and Minimal Additional Writable Memory.

**Report addressed:** the independent Operations Research report at `a017f474619e86be533547acac87a3c8354f64cf`, reviewing R30 at `fdc1ed47d46dc9d3344b8bce47c1670f11dcd475`. **Scientific baseline:** the complete R35 reader at `7e49851cd04f0f7e015c2561b43a4e7591574e67`. **New branch:** `revision/ndu-operations-research-r36-linear-frontier-20260924`. September 24, 2026.

We thank the referee for identifying the scientific question left after the laminar and memoization connections were made explicit. The present revision preserves the complete R31–R35 theorem package and responds with an additional proved and implemented improvement to the exact contractual frontier. We distinguish those inherited responses from new R36 work below. The independent report reviewed R30, not the subsequent tightness, piecewise-quadratic, global-randomization, or Monge results. We do not attribute any view of R31–R36 to that report.

## 1. Version identity and the scientific change

The report's version-audit concern is addressed by immutable identities rather than branch names alone. The baseline, report, and scientific source are separately recorded in `DERIVATION_PROVENANCE.md` and the machine-readable build record. The four original reader/entry wrappers are archived under `predecessor/`. Every inherited theorem module remains unchanged, and a full remote base-tree audit rejects deletion or unrelated modification.

The new result is Theorem `thm:r36-linear`. It computes each complete expected-participation or deterministic/pathwise memory frontier through budget m on k ordered branches in O(mk) exact rational operations and comparisons, with O(mk+k) stored scalars and indices. It includes one optimal codebook per budget and exact continuous optimization of the highest randomized level. The preceding R34 construction required quadratic work per layer; R35 proved and implemented logarithmic-factor monotone search. R36 proves the missing all-submatrices property, implements classical SMAWK, and retains both preceding algorithms as exact same-input comparators.

## 2. Parametric optimization and the residual priority question

We retain the explicit literature and reduction work in the model/literature section, the compact-response theory, and the R32 companion addendum. The article identifies the unfolded feasible problem as classical separable laminar allocation. It supplies a convex-cost-flow representation, distinguishes the primal supply parameter in parametric flow from the dual price used by the response compiler, and compares its compact-input event bound with the output-sensitive focus of Klimm and Warode. Integral polymatroid sensitivity is discussed separately rather than represented as a continuous quadratic theorem.

The six questions in report Section 3 have explicit answers. The response is indeed a structured parametric convex-program solution map. Existing parametric-flow methods can be applied after the stated unfolding/reduction, but their general output-sensitive guarantees do not by themselves give this compact-DAG event budget. Normalized memoization is granted, not claimed as a new principle. The contribution is the structural shared-knot budget in compact input, its tight explicit-output interpretation, exact coefficient-event construction, and the representation/execution consequences. The binary bound applies to that construction, not to every conceivable recursive implementation. These are distinctions in proved scope and representation, not an assertion that the predecessor literatures are unrelated.

R36 also attributes SMAWK explicitly to Aggarwal, Klawe, Moran, Shor, and Wilber. Neither quadrangle inequalities nor generic linear matrix search is presented as new. The added argument proves that the contract's interval-minimized terminal costs and prefix layers admit an ordinal completion that satisfies the classical algorithm's hypotheses, including entirely infeasible rows in selected submatrices. A constant numerical infinity with ordinary leftmost ties fails that test. This separates the inherited generic algorithm from the model-specific interface and its resulting complexity bound.

## 3. Matching bounds and broader exact closure

The tightness requests in report Section 7 are met by the retained analytical chain construction, not by a dense timing example. The quadratic family has exactly 2n global clipping knots and n²+2n affine pieces across its separately materialized vertex responses. The article states the resulting linear and quadratic orders with their representation qualification. The renewal family supplies a linear worst-case additional alphabet, and raw price labels, behavioral symbols, combined public-state/class pairs, and read-only storage remain separate quantities.

The retained R33 extension also follows the referee's alternative route: continuous piecewise-quadratic strictly concave rewards with curvature changes and downward marginal jumps. Its event budget depends on local pieces and public caps; its compiler retains exact reflection, inversion, and rational certificates. Shared circuits use linear persistent space in the local-piece and graph input after compilation, with a different query cost. Thus the explicit-table lower bound is not claimed for arbitrary compressed representations.

R36 adds a sharper restricted-memory design algorithm without deleting these results. The all-budget linear-work theorem is specific to the heterogeneous quadratic renewal interface already used by the global randomized frontier. It is not a claim that the piecewise-quadratic general DAG compiler or arbitrary switching model has the same bound.

## 4. Classical machine minimization and the accounting convention

Report Sections 4, 5, and 12 asked for the classical minimization principle to be separated from its contractual consequences. The retained memory theorem does so. The reached continuous-price controller is reduced to a finite deterministic output transducer with public-transition inputs. Backward equality of output and successor signatures is classical behavioral minimization, with explicit references to machine minimization, MDP equivalence, and dynamic-program aggregation.

The contract-specific statements remain foregrounded: finite reachability from the continuous optimum; at most N+1 raw fixed-query prices; contiguous behavioral classes in price order; strict collapse of distinct prices with the same future behavior; coupling to the unique optimal contract; and a linear worst-case contractual alphabet. The reported minimum is additional writable memory conditional on a freely observed current public vertex and a read-only program, for one fixed root query. The title and abstract make that qualification explicit. Combined reached states and read-only coefficients/precision are reported separately.

The new search changes offline compilation, not the controller architecture. Its codebook output does not smuggle past branch identity or a retained random seed into the free public state. The companion explains how the same codebooks implement the expected and pathwise institutions. No assertion is made that additional symbols equal total implementation memory or that a fixed-query result is automatically query-uniform.

## 5. Finite contract policy graphs and operational interpretation

The retained discussion of Zhang's Operations Research policy-graph work responds directly to report Section 6. It acknowledges the established use of finite policy graphs for continuation contracts, then distinguishes information, horizon, and guarantee: the present result is exact for a fixed-query public-information finite-horizon subclass, rather than a general exact solution of infinite-horizon adverse selection. The current public vertex and behavioral symbol together form an exact contract implementation graph in the stated architecture.

The operational design question is now computable at every alphabet budget: what loss is incurred when the institution requires participation before the private service draw, and what changes when every realized draw must satisfy the cap? This comparison uses the same primitive instance. The offline matrix-search improvement is useful because it computes the complete tradeoff rather than timing two different feasible problems.

## 6. Randomization, global design, and participation

The suggestion in report Section 13 has been developed beyond a fixed-codebook formula. The retained R33 analysis gives adjacent-lottery objectives and a strict restricted-budget benefit. R34 proves a global anchoring result: all but the highest optimal randomized level can be placed at caps, while the highest level must remain continuous. Its exact terminal optimization and codebook dynamic program are preserved. Under private-draw pathwise participation, the separate theorem proves equality with the deterministic frontier at every budget in the stated renewal architecture.

R36 computes precisely those same two global frontiers. It does not replace continuous optimization by a grid. The non-cap regression remains exact: for caps (1/4, 1/2, 3/4), probabilities (7/20, 3/5, 1/20), quadratic reward parameters r=2 and q=1, and unit intermediate curvatures, the two-symbol randomized codebook is (1/4, 5/8) with loss 23/1280. The best cap-only and deterministic two-symbol loss is 3/160. These figures are reproduced by the new implementation and by direct reduced-candidate enumeration.

Conditional-expectation participation is not described as pathwise feasibility. It corresponds to accepting the branch's expected continuation before the private service draw. The pathwise alternative is computed separately. The root-saturation and renewal observation assumptions remain explicit, rather than being silently imposed on the broader accepted-adaptation model.

## 7. Comparative statics and the scope of dispersion

The report correctly distinguishes a fixed mean-preserving radial path from arbitrary convex order or majorization. The retained theorem states the ordered radial family explicitly, and the current abstract does not make a general dispersion claim. R36 preserves that theorem, its proof, and the scope statement in the introduction and conclusions. We have not replaced a missing general-order proof with stronger prose. The deeper new service-design statement is instead the exact global comparison of expected and pathwise frontiers, with the implemented improvement applying to both institutions.

## 8. Bit complexity, comparisons, and intermediate arithmetic

The coefficient-event compiler's bit theorem and the R32 accounting addendum are retained. They distinguish reduced stored coefficients from conceptual common denominators and from aggregate values/certificates; comparisons and sorting are charged. The construction is not described as strongly polynomial or as a generic bit bound for every implementation.

The new theorem is likewise explicit. On ordered inputs, linear search performs O(mk) rational operations and comparisons. The moment and continuous-terminal expressions are unchanged, so the existing coefficient-height bound S gives the conservative O(mkS³) Turing bound. Symbolic keys require only an order tag and a column index in addition to a finite exact cost. Sorting unordered caps adds its own O(k log(k+1)) rational comparisons. Winner re-queries, terminal scans, backpointers, and all-budget reconstruction are counted. No quadratic table or unlimited memoization cache is concealed in the linear-work claim.

## 9. Computational alignment, independent evidence, and negative results

Report Section 10 asks for comparisons aligned with the residual contribution, not a speed claim against an intentionally unfolded implementation. The retained whole-parametric-path active-set comparator tests every affine region on small instances. The new study isolates a different residual contribution: exact all-budget global frontier computation on the identical compact renewal problem. R34, R35, and R36 share the reduction and moment interface; we state that dependence rather than labeling them independent mathematical validations.

Independence is supplied separately. A direct branchwise enumerator checks every theorem-permitted anchored prefix and minimizes each final quadratic from three direct evaluations, without production moments or dynamic programming. Search-specific enumeration tests arbitrary row and column subsets, including all-missing selected rows, against direct row minima. This attacks the precise extra hypothesis required for SMAWK.

The new suite passes 100 rational instances, 4,232 old-algorithm objective equalities, 2,116 controller replays, 156 independent reduced-candidate frontier equalities, and 43,431 submatrix row-minimum checks. The detailed record also includes 2,595 nonvacuous single-crossing implications, 255 direct interval checks, 402 feasible Monge inequalities, 176 nonanchor-grid falsification checks, two padding regressions, 16,273 work checks, and 17 invalid-input rejections. The unchanged R33, R34, and R35 suites are separately rerun in temporary directories; their original evidence files are preserved.

The scale comparison computes all budgets one through eight on 16–2,048 branches. Both expected and pathwise frontiers agree with R35 at every size; the quadratic randomized R34 baseline is rerun through 256 branches. Larger quadratic entries are NOT_RUN, not timeouts or estimates. Complete exact losses and codebooks are stored alongside actual timing, work counts, environment, and source hashes.

The linear implementation is not uniformly faster. At 16 branches it makes 534 expected-frontier economic queries versus 289 for monotone search; at 2,048 branches the counts are 128,966 versus 135,597. The deterministic search at 2,048 still makes more calls, 163,838 versus 153,180. The article retains this overhead and separates asymptotic complexity from measured constants. No published external flow solver was benchmarked, and all instances are synthetic. The evidence supports the specified algorithmic comparison, not a claim of universal solver superiority or empirical calibration.

## 10. Supporting theory, presentation, and review readiness

The shared-table supporting-cut result and its tied-bound/singleton handling remain unchanged. No finite-cut guarantee is added to the continuous outer design problem. The broader switching, vector-commitment, comparator, and deployment theory remains in the base repository with its own assumptions and evidence. The complete R31–R35 theorem inputs remain in the reader; no result is deleted to manufacture a shorter or narrower contribution. The new conclusions consolidate repeated discussion, while the original wrapper is archived byte-for-byte.

The reader uses the Operations Research lengthy-manuscript layout: anonymous title page, text-only abstract under 200 words, nonmathematical expository introduction, 11-point type, one-and-a-half spacing, one-inch margins, author–year references, tables after references, and a code/data statement. The build checks page accounting, unresolved references/citations, overfull boxes, source preservation, and exact test status; its record gives the actual resulting counts and source identity. The article, electronic companion, response, and reproduction package are provided together on the new branch.

The report's Sections 16 and 17 are addressed by this cumulative theorem and evidence package: explicit residual priority, analytical tightness and a broader exact class, standard-language machine minimization, separated memory metrics, precise comparative-static scope, and same-input complete-frontier comparisons. R36 adds a proved and executed improvement rather than a nominal branch rename. We submit these materials for further referee examination; the build and test results are not an editorial decision or a claim that literature priority can be certified by software.
