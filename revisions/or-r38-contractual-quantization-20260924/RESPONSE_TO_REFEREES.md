# Response to the R37 independent Operations Research report

**Revision:** R38 — Limited-Memory Renewal Contracts: Participation, Quantization, and Exact Design  
**Review baseline:** `1cf9c8df76437ee71d4291d1001e9c7f055781c5`  
**Report:** `reviews/operation_research_referee_report_r37_independent_harsh_2026-09-24.md`  
**Reviewed scientific source:** `0afd833f6d0f16195579399334426aebd3ea1b20`  
**New branch:** `revision/ndu-operations-research-r38-contractual-quantization-20260924`

We thank the referee for distinguishing the resolved correctness and staircase-search questions from the newly exposed quantization and robustness questions. This revision addresses the new report rather than repeating the preceding response. No preceding scientific source, proof, result file, or review is deleted or overwritten. The preceding complete readers are preserved in this revision's `predecessor/` directory; all earlier revision directories remain unchanged.

## 1. Scalar quantization and the theorem-level contribution boundary

The introduction and Section 2 now start from quantizer design. Wu (1991) is discussed directly: optimal mean-square scalar quantization already has the dynamic-programming/matrix-search route to O(KN). We also discuss the later one-dimensional clustering treatment of Gronlund et al. Generic ordered cells, optimized reproduction points, and linear work per layer are not assigned independent priority here.

Table 1 compares every main result with its predecessor principle and the precise contractual statement being proved. The deterministic cost is a one-sided, cap-constrained distortion with heterogeneous intermediate-service costs, not an unconstrained mean-square centroid objective. The executable comparison computes the ordinary mean-square centroids in the three-cap example and checks their contractual infeasibility. It is not an inappropriate runtime contest between solvers for different objectives.

## 2. Adjacent stochastic rounding and the closer dual-quantization predecessor

Equation (1) explicitly displays both distance-proportional probabilities and the preserved mean. Croci et al. (2022) receive direct attribution for the stochastic-rounding primitive. The audit goes further than the requested minimum: Pages and Wilbertz's dual quantization optimizes intrinsically stationary splitting and grids, and its extended formulation already handles out-of-hull points. Those antecedents are now acknowledged, not just ordinary rounding.

The interior quadratic loss is identified exactly with q/2 times the quadratic dual-quantization error. Above the top level, the contract instead has a level-dependent linear term and heterogeneous intermediate-service curvature. The combined structural result concerns that contractual tail, its continuously optimized highest level, and the crossing-difference cancellation after minimization. The sufficient conditions for cap anchoring are isolated; the argument is not claimed unchanged with arbitrary code prices or endogenous nonsaturated branch targets. The existing representation, continuous-optimum, and Monge proofs remain complete.

## 3. Communication-constrained control and operational scope

Section 2 discusses Fu's quantized-feedback tutorial and the standard encoder/channel/decoder architecture. This is not a new finite-rate communication architecture, a stabilization theorem, or an incentive-compatibility theorem. The contractual addition is continuation-payment allocation and the institution-dependent feasible randomization.

The title now says *Limited-Memory Renewal Contracts*. The main model and detailed companion protocol specify the three-date architecture, acceptance conditioning, disclosure, charged seeds, and the absence of an additional post-draw exit option. The mechanism remains explicitly stipulated; the revision does not invent a documented real deployment or empirical calibration. This follows the report's alternative of accurate renewal scope rather than an unsupported industrial claim.

## 4. Saturation robustness: new theorems, not only a historical example

Section 8 now treats every aggregate promise B between zero and the sum of the branch caps weighted by their probabilities.

**Exact full-information alphabet for all promises.** The full optimum is Y_j=0 and C_j=min(b_j,tau), where the weighted clipped mean equals B. The exact alphabet is the number of distinct resulting terminal actions. This gives the phase diagram in B and handles repeated caps. For B no larger than the smallest cap, one symbol is fully efficient under every institution.

**Uniform stability of every budget.** Same-alphabet scaling and saturation lifts prove

`V_m^I(bar b) - L_f epsilon <= V_m^I(bar b-epsilon) <= V_m^I(bar b) + H epsilon`

for deterministic, expected, and pathwise institutions. The pathwise lift explicitly handles fresh decoder randomness and permits draw-specific intermediate service without retaining an uncharged seed. Therefore every strictly positive saturated institutional advantage persists whenever epsilon is smaller than its saturated gap divided by L_f+H. The equal-probability three-cap example gives the explicit strict interval `11/24 < B <= 1/2`.

**Exact interior allocation reduction.** For a fixed codebook, the endogenous branch promises solve a separable concave allocation problem with response `F_c(min(t,c_max))-h_j((t-c_max)_+)`. Optimizing it jointly with the book gives an exact formulation for every B. We do not incorrectly claim that the original cap anchors or O(mk) recurrence automatically solve that interior joint problem. The strict advantage interval is a theorem, while the full-information phase diagram shows where memory ceases to matter.

## 5. A general bounded-overrun family, with its timing stated

Section 9 adds a globally solved family for arbitrary finite certified catalogs, arbitrary numbers of branches and symbols, any nonnegative overrun tolerance, and heterogeneous costs. The catalog is an explicit feasible set, not an undocumented approximation of a continuous problem. The fixed-book risk rule yields edge and tail costs; a shortest-path dynamic program optimizes all books and reconstructs their policies. Zero tolerance gives the deterministic/pathwise catalog optimum, and tolerance at least one gives the expected-participation catalog optimum.

This is a general third theorem family, not a promotion of the original three-branch calculation into a general continuous theorem. The continuous off-cap and bounded-overrun example is preserved in full, including its global proof. The main text now reports both high-realization probability `(1/4)/(z_delta-1/4)` and maximum overrun `z_delta-1/2` along the whole example. Figure 1 displays the analytic loss profile and the off-cap minimum.

The intermediate tier is explicitly committed before the draw in this risk-limited institution. We do not claim this restriction is without loss in every possible bounded-risk mechanism.

## 6. Actual codebook-dependent implementation cost is now optimized

The new catalog theorem puts an arbitrary nonnegative additive price rho(a) on each selected level *inside* the path recurrence. Thus codebook choice and its actual level charges are optimized jointly. In the heterogeneous example, pricing level 5/8 at 1/640 switches the optimal book away from the uncharged optimum: that old book costs 25/1280, whereas the newly selected cap-only book costs 24/1280. The comparison is exact and executed.

The separate capacity/implementation-menu expression is retained, explicitly described as accounting and finite comparison. Its exogenous institutional charge is not estimated risk preference. Additive level prices do not purport to solve entropy coding, arbitrary joint compression costs, correlated repeated use, or every possible multidimensional implementation problem.

## 7. Focused submission companion, complete repository preservation

Thirteen complete preceding proof blocks are mapped into the focused companion with exact source hashes in `PROOF_PRESERVATION.json`. This includes cap anchoring, continuous top-level optimization, pathwise equivalence, terminal Monge cancellation, column offsets, both completion orientations, wholly padded selected rows, reachability, and rational complexity. Main and companion references are regenerated with clean current numbering; source label names are internal and do not become theorem names.

The broader compact-response, piecewise-quadratic, minimal-machine, laminar-allocation, shared-table, and coefficient-event work remains intact in its original revision directories and in the preserved complete R37 readers. It is no longer required reading in the submission companion for a theorem that does not use it. No historical theorem is withdrawn or erased. A preservation manifest audits the unchanged older paths and the predecessor reader hashes.

## 8. Computational evidence and validation scope

The new exact suite compares the charged risk DP with independent exhaustive book/support enumeration, verifies clipped allocations, scaling and saturation lifts, repeated-cap aggregation, fixed-book response concavity, invalid-input rejection, the resource-price switch, and the ordinary scalar-quantizer comparison. Three additional synthetic landscapes—uniform, clustered, and concentrated weights—supply 18 reconstructed catalog study cases.

The entire R37 exact suite and its unchanged R33–R36 regressions are rerun in isolated directories. The old 16,384-branch measurements are preserved as old measurements, not claimed to have been newly rerun or as empirical service evidence. HiGHS remains a validation of the finite reduced network, not independent verification of cap anchoring. PADS remains an independently authored search-layer substitution with a shared economic oracle. Its upstream commit, source blob, and MIT notice are identified in the companion.

## 9. Presentation and minor comments

The abstract immediately scopes the continuous global theorem to the saturated quadratic model and separately states the nonsaturated and catalog results. The main exact-memory statements distinguish distinct actions from branch count; the repeated-cap proposition accounts for heterogeneous intermediate costs. The linear complexity is a corollary package using O(k) exact-rational oracle/comparison work per layer, not a new general matrix-search theorem. Writable fixed-width state is distinguished from read-only representation, and the bit-price comparison is explicitly conditional on exogenous protocol prices.

All 15 minor comments are covered by the changes above: abstract scope (1), draw conditioning (2,12), distinct/repeated actions (3), exact-work terminology (4), writable-state terminology (5), protocol prices (6), risk probability and overrun (7), solver scale and interpretation (8), PADS identity/license (9), the loss figure (10), quantizer framing (11), and clean current numbering with preservation outside the reader narrative (13–15).

## 10. Claims presented for renewed review

The submission retains the original continuous global solution and full proofs, and adds positive nonsaturated robustness, an exact all-promise alphabet characterization, an interior allocation reduction, and global charged/risk-limited catalog design. It does not substitute test counts for proofs or assertion for publication priority. The neighboring literature is explicitly identified, including the additional dual-quantization comparison. The precise scope of each theorem is kept visible so that the referee can evaluate the actual mathematical increment rather than a generic quantization or matrix-search claim.
