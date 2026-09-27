# Response to the R9 referee report — Revision R10

**Manuscript:** Neural Differential Utility: Accepted Adaptive Service Control and Certified Value-Gradient Learning  
**Journal:** Operations Research  
**Report:** `reviews/operation_research_referee_report_r9_2026-09-21.md`, review head `c4cf05f40feb0eb690f4f0c65a0d6176b3d32b28`  
**Scientific predecessor:** `584296b1a22de455a482c6809f00eda1387b6dab`  
**New branch:** `revision/ndu-operations-research-r10-20260921`

We thank the referee for identifying an actual submission failure: the R8 general theory was not part of the active manuscript. R10 replaces the root manuscript and companion, compiles the complete theorem chain, and preserves rather than silently deletes earlier scientific content. It also goes beyond integration. The revision develops a primitive continuation-compatible tree criterion and a genuinely nonlinear multistage learning experiment with complete rational records. The response below separates mathematical corrections, new results, empirical findings, and matters of editorial judgment.

## 1. Report sections 1–2: an actual integrated manuscript

**Action completed.** Root `main.tex` is Revision R10 and inputs the corrected general formulation, primitive tree theory, accepted continuous hierarchy, retained quadratic audit, and new nonlinear multistage implementation. `electronic_companion.tex`, `historical_supplement.tex`, README, and the submission checklist identify the same revision. The earlier main and companion sources are preserved verbatim as `predecessor_main.tex` and `predecessor_electronic_companion.tex`.

The build runs all documents through three cross-reference passes. `check_package.py` traverses the input graph, confirms every substantive predecessor input has a current location, and checks that the replacement bibliography retains every predecessor entry. This is not a candidate section stored next to an unchanged R7 paper.

## 2. Report sections 3–4 and 16: standard tools versus structural content

**Action completed; originality and significance remain for editorial evaluation.** The normal-cone alternative, Bregman identity, and strong-convexity certificate are explicitly identified as standard convex tools, with Boyd and Vandenberghe (2004) cited. They are lemmas or specialized certificates, not advertised as new convex-analysis principles. Critical-fractile arguments likewise receive no claim of having been invented here.

The new structural centerpiece is the **complete continuation-compatible edge criterion**. In a scalar finite tree with an interior constant comparator, positive tariff rates, exact root payment neutrality, and a continuation payment cap at every nonroot node, let k be marginal reward per unit payment at the comparator. Static optimality is equivalent to k being nondecreasing on every parent–child edge. A violated edge yields an explicit two-coordinate payment transfer satisfying every continuation constraint. The proof uses exact subtree summation by parts, so the test requires O(N) primitive comparisons rather than unknown optimizer multipliers or a nonlinear solve. The underlying summation identity and convex reasoning are elementary; the economic content is which reallocations survive the customer's exit options.

The same analysis gives an interpretable finite-gain bound with all affected switching edges included, and an exact two-review **absolute-friction threshold**. These statements answer requests for primitive zero-gain conditions, positive-gain mechanisms, and friction comparative statics. They are not asserted for arbitrary scalar boundary tiers, arbitrary vector couplings, or endogenous tariffs. The general convex formulation handles those accepted programs; the complete edge theorem is clearly scoped to its stated scalar class.

Files: `sections/general_theory.tex`, `sections/tree_structure.tex`. An independent finite test compares 120 tree cases with normalized LPs, checks the summation identity with fractions, and exercises 12 threshold cases. These checks are diagnostics, not substitutes for the proofs.

## 3. Report section 5 and comment 15.5: joint graph coupling

**Corrected.** Decision variables are consistently vector-valued at tree nodes. The resource objective includes a joint convex function of all decision coordinates, with a displayed weighted graph-edge example. Parent–child and spatial graph couplings coexist. A sum of univariate node functions is no longer claimed to represent a Laplacian quadratic. The nonlinear computational objective uses this same vector tree convention.

## 4. Report section 6 and comments 15.1–15.3: stock identification

**Corrected and specified.** The theorem assumes an exogenous regime process whose occupation probabilities are unaffected by the policy. Both one-sided derivatives are displayed. Interior quantile conditions and lower/upper constrained endpoint conditions are distinct, and the text explicitly warns that a critical level between zero and one need not be attained in the feasible interval.

The exact atomic case is separated from the smooth quadratic-growth case. The density lower bound is required on the entire feasible stock interval. A concrete vector extension specifies additive physical costs, one fill commitment per service, a vector of positive supporting prices, a product feasible set, and the minimum coordinate curvature. Arbitrarily correlated demands are allowed under these additive expectations. Coupled stock feasibility is not assumed away or generalized by a tautological sentence.

## 5. Report section 7 and comment 15.6: all adjustment edges and continuation participation

**Addressed by a stronger, separately stated result.** The earlier customer-neutral perturbation result is retained. R10 adds an edge transfer whose subtree sums are exactly known: only the child's continuation sum changes, and it decreases. The full curvature expression includes incoming and outgoing adjustment terms, including unchanged children of perturbed nodes and initial installation. The new absolute-friction corollary gives the exact threshold at which the first-order benefit is exhausted. It does not incorrectly apply the smooth zero-derivative argument to a kink.

## 6. Report section 8 and comment 15.7: memory with continuation promises

**Corrected and extended.** The zero-friction conditional-mean proposition explicitly excludes history-specific promises in its heading and assumptions. We retain its valid ex ante bound, but do not use Jensen to erase history-dependent feasibility.

An exact two-history example demonstrates a positive promise-information gap of 1/32 even at zero physical switching friction. Both histories lead to the same terminal demand regime, but their public continuation caps differ. Earlier installed tiers can encode which obligation applies; this is contractual memory, not an extra demand signal.

The continuation model receives its own dynamic formulation. Remaining payment budget is an explicit state, child budgets are allocated jointly with the current tier, and backward induction proves equivalence with the full continuation-constrained tree program. When primitives and outside caps are Markov, time, regime, inherited tier, and remaining budget suffice. At zero switching friction the inherited tier disappears from the recursion, but the budget and the information determining outside caps do not.

## 7. Report sections 9–10 and 17: paper identity and genuinely nonlinear learning

**Substantive reconstruction completed; no unsupported superiority claim.** We retain the integrated control-and-learning question rather than remove learning to avoid the experimental objection. The title now says “Adaptive Service Control,” accurately identifying the fixed-tariff institution. Learning implements and audits accepted control; it is not the source of the economic gain and is not presented as a new contracting paradigm.

The additional experiment is a graph-coupled **quartic multistage** control problem, not a known SPD inverse. It has inherited tiers, binary scenario trees, a participation constraint at every history, and up to 992 contingent tier coordinates. Weighted-centered forcing makes the continuously optimized static comparator exactly one half. Training uses nonlinear compatible scalar potentials with 63 softplus features. The same three certified scalar endpoint values feed both fitting objectives. Central differences have a proved truncation-and-oracle-error bound rather than being called exact for a nonlinear value function.

Specific computational objections are addressed as follows:

| Referee concern | R10 action and evidence |
|---|---|
| Known quadratic inverse is not a dynamic nonlinear task | Added quartic, graph-coupled, multi-review tree model with all continuation inequalities; retained the old quadratic example only with its correct scope. |
| Direct baseline refactorizes each repeated query | Added cached sparse and dense factorization and Jacobi-PCG on the **unchanged R7 instances**, and cached baseline-Hessian preconditioning for changing Newton systems in the nonlinear task. Setup is reported separately. |
| Weak graph transfer | Added random-edge, geometric, and weighted-block graphs, plus changes in graph weights, degree, horizon, dimension, coupling, and quartic curvature. Strong-shift failures are retained. |
| No uncertainty in timing | Fifteen timed repetitions follow one warmup; raw observations and quantiles are stored. Learned timing uses a prespecified training seed, not the fastest fitted seed. |
| Missing end-to-end audit cost | New timings include candidate construction, acceptance repair, multiplier calibration/proposal, and exact rational verification. Training and one-time setup are separate. |
| No cumulative policy-quality guarantee | Full-tree strong-convexity residual certificate proves a discounted whole-policy value bound. The budget-state telescoping observation states the additional conditions needed for receding-horizon use. |
| Value-gradient superiority unestablished | Ten paired training-seed means are reported. Their 95% interval includes zero. Superiority remains **unestablished**, not relabeled successful. |
| Necessity of learning relative to analytic methods | The nonlinear critic no longer approximates a known quadratic inverse; classical nonlinear solvers remain strong baselines. A universal need for learning, or a speedup at matched certified accuracy, is **not established or claimed**. |

The final nonlinear run has 176 exactly feasible candidates, 2,640 continuation checks, 52,624 tier-bound checks, and 720 certified oracle values. Forty-three of 160 raw learned proposals are worse than the static benchmark, predominantly under the severe weighted-block shift. A proved exact static gate prevents adopting a negative incremental reward, while the raw failures remain in the table and records. A tolerance-triggered classical refinement must be costed, and its unmeasured performance is not presented as a result.

The paired mean effect is about 0.000577 per discounted service–review, with interval approximately [-0.003923, 0.005076] in the recorded local run. The exact recorded run and environment are versioned. This is a positive implementation and verification result with mixed approximation evidence, not a claim that every learning objection has been empirically decided in our favor.

## 8. Report section 11: institution and economic language

**Clarified.** The tariff is external, states and actions are public, and the provider selects an operating protocol. The customer may exit subject to the specified outside protocol. The title and introduction use adaptive service control rather than general contract design. We neither introduce private information by notation nor claim to solve hidden effort, incentive compatibility, bargaining, or endogenous pricing. This precision leaves the accepted-control theorem chain and ambition intact.

## 9. Report section 12: application evidence

**Not empirically resolved.** The expanded experiments are synthetic. No real dataset, field deployment, or calibrated service application has been fabricated or implied. The revision strengthens the structural and computational sides of the contribution. Whether that suffices for Operations Research's importance and utility threshold is an editorial question. The conclusion identifies calibration as further work, not a completed result.

## 10. Report section 13: independent archival reproducibility and real validation

**Addressed with inspectable records and executable checks.** R10 retains full rational policies, nonnegative multipliers, exact rewards and gap fractions, graph and tree primitives, all scalar oracle endpoint records, fitted coefficients, and raw timing arrays. The independent verifier reconstructs the polynomial objective and all ancestor/edge derivatives without importing the learner or numerical solver. The R7 hierarchy, robustness, continuation certificate, and portfolio are separately replayed with their own exact checker.

The workflow now performs scientific computation, independent verification, all three PDF builds, input-preservation checks, and publication of ordinary sources, records, and PDFs to this new branch. Its path filters include manuscripts and R10 scientific sources. A temporary payload is only an authenticated transport mechanism and is removed after materialization; it is not a substitute for the final committed manuscript. The commit manifest and compiled artifacts identify the run actually being reviewed. Reruns are not mislabeled as recovery of the original historical wall-clock observations.

## 11. Report section 14: contribution, length, and preservation

**Reorganized, not scientifically deleted.** The main theorem chain is now a coherent active manuscript. Current accounting, accepted comparison, switching, and diagnostic details occupy the electronic companion. The full earlier diffusion, continuous-review, and computational derivations are compiled into a separately labeled historical supplement. Every predecessor substantive input is checked for a destination. The complete old bibliography and root sources remain available.

This removes unrelated historical layering from the active theorem chain while honoring the requirement not to discard scientific content. The historical supplement is an archive for the referee, not an assertion that every historical page must be part of the journal's active electronic companion.

## 12. Remaining detailed comments 15.4 and 15.8–15.10

**Corrected.** Tangent and outward normal cones, the maximum feasible step, and the infinity-normalized direction LP are explicitly defined. Information equalities appear as an equality matrix with free multipliers; their contribution cancels in the Bregman identity. The multiplier-existence statement invokes the normal-cone representation of a polyhedron, not an indiscriminate Slater claim. The stock supporting function, demand CDF, physical fill, and joint tier resources have distinct notation. Payment weights versus reward forcing are stated locally in the nonlinear extension.

## 13. Minimum re-review requirements and final assessment

The actual root paper, metadata, complete input graph, corrected coupling, explicit literature positioning, point-by-point response, nonlinear multistage benchmark, cached baselines, and scientific validation are supplied. The original accepted continuous hierarchy and commitment-value comparison remain. No claim is made that a checker settles novelty or journal acceptance.

The unresolved items are substantive and visible: a real calibrated application is absent; gradient-supervision superiority is statistically inconclusive; severe distribution shift challenges the raw learned readout; and a matched-accuracy learned speed advantage is not established. The revision addresses these findings constructively with complete reporting and an exact deployment gate rather than deleting them, downgrading the project to a note, or declaring a research no-go.
