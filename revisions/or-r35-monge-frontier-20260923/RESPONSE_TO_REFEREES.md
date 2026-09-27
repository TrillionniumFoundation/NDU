# Response to the independent Operations Research referee report — R35

**Manuscript:** Accepted Service Adaptation: Exact Parametric Quotients and Minimal Additional Writable Memory  
**New revision branch:** `revision/ndu-operations-research-r35-monge-frontier-20260923`  
**Scientific baseline:** R34, `fbfdf24b370201c810425f633f5fc06048282b5c`  
**Report answered:** `reviews/operation_research_referee_report_r30_independent_2026-09-23.md`, at `a017f474619e86be533547acac87a3c8354f64cf`  
**Commit evaluated by that report:** R30, `fdc1ed47d46dc9d3344b8bce47c1670f11dcd475`.

We thank the referee for distinguishing the substantial R30 revision from an earlier stale version audit and for identifying the precise burden of the remaining contribution. We respond through additional structural results, explicit attribution, and same-input computational evidence. This response accounts for the whole report, but does not pretend that the referee has already evaluated R31–R34. The unchanged R31–R34 modules provide the intervening responses; R35 adds a new theorem, two algorithms, and their verification.

The principal new result is **Monge structure after continuous terminal optimization**. Under the heterogeneous quadratic renewal primitives, both the globally optimized randomized frontier and the deterministic/pathwise frontier can be computed through budget m in O(m k log(k+1)) rational operations and comparisons, rather than the O(m k²) scan of R34. Storage remains O(m k+k), including backpointers and reconstructed codebooks, for m≤k. The highest randomized service level remains continuously optimized, not restricted to a cap or numerical grid. The critical step is a monotone difference between two terminal-anchor objectives; it establishes the Monge inequality for their interval-minimized cost array. Heterogeneous intermediate curvatures cancel in that difference.

## 1. Version identity and preservation (report §§1–2)

The reviewed R30 commit, the independent report commit, and the R34 scientific baseline are recorded separately above and in `DERIVATION_PROVENANCE.md`. The new branch is a descendant of the validated R34 reader commit. We do not use the older report that treated an obsolete remote view as the current R30 paper.

Every inherited R31–R34 theorem module used by the reader remains byte-identical. The four root wrappers that are updated for the new reader are archived under `predecessor/`. The preservation manifest verifies the inherited reader, code, and evidence files available in the baseline build. The remote Git tree inherits all other historical files without deletion, including earlier switching, deployment, and computational supplements. The main article, electronic companion, and response are new readers, not predecessor PDFs relabeled as R35.

## 2. Parametric optimization priority and residual contribution (report §§3, 11, 16A)

The retained model/literature section compares the unfolded laminar problem with Mjelde and Tang, the piecewise-quadratic flow results of Klimm and Warode, and the integral polymatroid sensitivity results of Harks, Klimm, and Peis. The R32 companion gives the explicit convex-cost-flow representation and distinguishes a primal supply parameter from the conjugate price parameter. The complete response is recognized as a structured parametric convex solution map. Normalized memoization yields the same recursion; neither that principle nor generic parametricity is attributed to this paper.

The contribution is the compact-input event budget and exact representation: tight linear global-knot and quadratic explicit-table orders, reduced-rational construction, the local-piece extension, and the storage/query alternative. These distinctions are retained in the article, not relegated solely to this letter. The input measure is the public graph and its local pieces, rather than the possibly much larger unfolding. The bit statements identify their implementation, exact comparisons, reduction after rational operations, conceptual denominators, and the difference between coefficient and aggregate-value heights.

R35 follows the same attribution discipline for its new algorithmic result. Quadrangle inequalities and monotone matrix search are classical; the new section cites Yao (1980) and Aggarwal, Klawe, Moran, Shor, and Wilber (1987). We prove the contractual cost inequalities first and then apply elementary divide-and-conquer search. In particular, a minimum over continuous intervals is not simply assumed to preserve Monge structure: equation `eq:r35-difference` and an ordered-minimizer uncrossing argument prove it. The implementation does not claim to be SMAWK or to attain an unimplemented linear-search bound.

The new Turing bound, O(m k log(k+1) S³), uses the same conservative reduced-rational height S as the retained global-frontier theorem. Search changes the number of evaluated entries, not their algebraic form. The companion accounts for exact comparisons, terminal clamping, recursion stack, and reconstruction once per winning budget. This is a bound for the stated quadratic input interface, not for arbitrary convex-cost oracles.

## 3. Machine minimization and memory accounting (report §§4–5, 12, 16C–D)

The reached price system remains explicitly a deterministic output transducer driven by public transitions. The classical minimization principle is attributed to the machine/model-minimization and aggregation literature, including Bean–Birge–Smith, Givan–Dean–Greig, and Peyrière. The model-specific content remains finite price reachability from continuous controls, ordered behavioral classes, exact implementation of the unique optimum, strict collapse of distinct numerical prices, and the linear worst-case contractual alphabet.

The title, abstract, and theorem statements distinguish **additional writable memory** from combined public-state/class pairs and read-only representation. Public vertex/date and a fixed root query are inputs under the specified architecture. A previous branch, previous action, or retained private seed cannot silently become an uncharged input. R35's reconstruction and controller replay use exactly that architecture. The improvement is in offline computation of the memory-value frontier, not a new free execution register or a redefinition of the measured alphabet.

## 4. Dynamic-contract policy graphs (report §6)

The introduction and model section retain the comparison with Zhang (2012). A fixed-query, finite-horizon, public-information exact transducer is distinguished from a finite policy-graph approximation for an infinite-horizon adverse-selection model. Both concern continuation contracts, but have different information, incentive, and approximation structures. The new result makes the former model's restricted-memory design problem faster to solve; it does not transfer an exact finite-alphabet theorem to the latter model.

## 5. Tightness, representation choice, and a substantive extension (report §§7, 9, 16B)

The retained R31 chain proves matching linear knot and quadratic separately materialized response-table orders; the renewal construction gives a linear additional-writable-alphabet lower bound. The R33 theorem additionally extends closure to continuous piecewise-quadratic rewards with changing curvature and downward marginal jumps, with complexity measured in local pieces and public caps. The shared-circuit representation is retained as a separate storage/query tradeoff, so an explicit-table lower bound is not presented as an impossibility for every shared representation.

R34 solved the global randomized codebook problem rather than only the fixed-codebook assignment problem. R35 now proves a further structural acceleration on those same heterogeneous inputs. The theorem covers both expected-participation randomization and deterministic/pathwise participation. This is a stronger computational characterization of the contractual-memory design problem, while the exact compiler's one-commitment, exogenous-public-graph assumptions remain explicit. No earlier switching or vector-commitment result is deleted or used without its own assumptions.

## 6. Outside-option comparative statics and institutional design (report §8, 16E)

The radial-spread proposition and its proof remain intact. Its statements concern a fixed ordered mean-preserving radial family; they do not assert arbitrary convex-order or majorization monotonicity. R35 does not replace that theorem with an unsupported broader claim.

The positive economic extension is instead constructive institutional comparison. The retained all-budget theorem equates private-draw pathwise participation with the deterministic frontier, while expected participation can admit a strictly better randomized frontier. R35 computes both frontiers with the improved exact work bound. A designer may therefore combine either loss frontier with an explicit symbol-budget charge and compare institutions without treating expected feasibility as realized feasibility. This extends, rather than removes, the original comparative-static result.

## 7. Evidence aligned with the algorithmic object (report §10, 16F)

The retained R33 independent active-set enumerator compares whole parametric paths, not only a selected promise. Its piecewise compiler, circuit, inversion, and certificate tests are rerun in isolation. The unchanged R34 suite is likewise rerun; inherited evidence files are not overwritten. Earlier laminar, generic convex, and public-promise comparisons remain available with their original interpretation.

The new comparison is on **identical renewal inputs and identical global optimization targets**. The unchanged R34 exact algorithm is the baseline for the newly accelerated randomized algorithm. Both optimize all requested budgets and the continuous highest level. The deterministic implementation is compared against its unchanged exact baseline in the small-case suite. We report oracle counts separately from wall-clock measurements and do not use an un-memoized unfolding to create the new speed ratio.

The new exact suite passes 98 cases, 1,712 frontier equalities, and 1,712 controller replays. It checks 2,092 interpolation-edge Monge inequalities, 2,092 deterministic-cell inequalities, and 3,846 interval-minimized terminal inequalities. Further checks include 1,401 independently evaluated terminal cells, 384 leftmost terminal argmins, 156 exhaustive frontier equalities, 550 exhaustive candidates, 176 nonanchor-grid comparisons, 196 work-bound checks, and 14 rejected invalid inputs. The nonanchor grids are falsification tests, not a proof over a continuum. The exhaustive comparator shares the proved anchor reduction but not the production recurrence or moment arithmetic. Shared primitive evaluation between the two production versions is disclosed.

The scale family computes budgets one through eight on 16, 32, 64, 128, 256, 512, and 1,024 branches. The first five sizes have exact equality with the unchanged global randomized baseline. At 256 branches, combined terminal/prefix calls fall from 192,546 to 12,177, about 15.8-fold. Larger baseline runs are marked **NOT_RUN**, not estimated timings or timeouts. Both accelerated institutions undergo exact replay. `benchmark.json` and `scaling.csv` retain the environment, actual times, exact losses, work counters, and source hashes; the reader table is generated from that run.

No published specialized parametric-flow implementation has been run in this package. The complete-path KKT comparator and the new same-input Monge ablation answer distinct, explicitly stated questions; neither is labeled an external solver benchmark. The service inputs are synthetic. These boundaries do not change the proved frontier or complexity results.

## 8. Restricted randomized frontiers and pathwise feasibility (report §13)

The exact-optimum alphabet theorem and the restricted-budget frontier remain logically separate. R34's cap-anchor reduction, global randomized theorem, and off-cap example are retained without alteration. For caps (1/4, 1/2, 3/4), probabilities (7/20, 3/5, 1/20), and the stated quadratic primitives, the optimal two-level expected-participation codebook is (1/4, 5/8), with loss 23/1280, whereas the cap-only and deterministic/pathwise optima have loss 3/160. R35 must recover that off-cap optimum, and its exact tests do so.

The terminal Monge proof allows heterogeneous intermediate curvatures because their terms cancel when two anchor objectives are subtracted. Ordered interval minimization remains continuous, including shared endpoints and the final singleton interval. Leftmost tie handling and triangular feasible domains are proved and tested; no artificial infinity padding is assumed to preserve the required property. Consequently the accelerated frontier is the global frontier, not a restriction to convenient candidate codewords.

The retained pathwise proof allows draw-specific intermediate tiers and uses root saturation. Fresh terminal randomness cannot carry an uncharged earlier seed, and the highest eligible codeword dominates lotteries under realized participation. Those institutional hypotheses are preserved in both the theorem and replay interface.

## 9. Shared-table comparator, presentation, and reading package (report §§14–15)

The shared-table supporting inequality and tied normal-cone argument remain unchanged. No finite-cut guarantee for the continuous outer design problem is added. The main article contains the new structural theorem and its main proof; the companion supplies algebraic factorization, search boundaries, exact arithmetic, and reproduction details.

The reader follows the Operations Research manuscript format: 11-point text, one-and-a-half spacing, one-inch margins, anonymous title page, a text-only abstract below 200 words, equation-free introduction, author–year references, and tables after the reference list. The full theory is retained under the Lengthy Manuscript category, with the final page counts and reference/layout checks recorded in `BUILD_VALIDATION.json`. This repository revision is prepared for further review; no ScholarOne submission, author conflict declaration, or editorial decision is made here.

## 10. Requested reassessment (report §§16–17)

The report's residual-priority questions are answered in the retained theorem-level literature comparison; its tightness and generalization requests are answered by matching constructions and piecewise-quadratic closure; its machine-accounting requests are answered through explicit transducer attribution and separate storage conventions. The restricted-randomization question has progressed from a fixed-codebook formula to a global exact design theorem, a participation-institution separation, and now a Monge acceleration of both complete frontiers.

We ask that the revised manuscript be evaluated on this cumulative theorem package and the new same-input evidence. The contribution claimed is specific and constructive: compact exact continuation representation and the computation and implementation of contractual memory. The manuscript and evidence are offered for independent mathematical and editorial assessment; test success is not presented as a substitute for that assessment.
