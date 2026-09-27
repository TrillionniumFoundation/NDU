# Response to the Operations Research R27 referee report

**Manuscript:** *Accepted Service Adaptation: Shared Policy Tables, Continuation Prices, and Certified Design*  
**Revision:** R28, September 23, 2026  
**Report:** `reviews/operation_research_referee_report_r27_2026-09-23.md`  
**Review commit:** `61aff783672ce39745713f5cefbcf83d8748ebd6`  
**Reviewed scientific predecessor:** `85fe1a799a192758a93a423bbb6d213ab9f04cce`  
**New branch:** `revision/ndu-operations-research-r28-20260923`

We thank the referee for identifying the missing connection rather than requesting another layer of generic certificates. R28 centers the paper on a single shared-table representation: a contractual information restriction must remain one common commitment across stochastic successors. We prove that the optimized restriction can be represented through the promised-payment state and certified by recursively assembled continuation and restriction prices, with a root linear program over the shared table. This is the principal revision. The cache-governance and adaptive-policy results address the two deployment qualifications attached to that same theorem chain.

All historical derivations, earlier revisions, numerical records, and adverse learning evidence remain in the repository. The six R27 reader files are preserved byte for byte under `predecessor/`. The original report is unchanged. New measurements are explicitly separated from inherited evidence. We distinguish a proved representation and arithmetic verification from an editorial finding of novelty or acceptance.

## 1. Review object and preservation

We revised the R27 scientific tip identified in the report, not an earlier R24 manuscript. The new branch descends from the report commit itself. The current main paper and electronic companion contain the revised theorem chain; `INHERITED_SHA256.json` pins the inherited files, and the build checker verifies every unchanged inherited file and each predecessor reader copy. The final manifest includes the actual current PDFs, sources, evidence, and replay results. The publication workflow validates a fresh checkout of the final scientific commit rather than attaching a successful status only to the source-transport commit.

## 2. The principal novelty claim and the theorem-by-theorem comparison

The title, abstract, introduction, conclusion, and main closest-results table now identify the **shared-table continuation-price bridge** as the central result. The result does not call generic parametric QP, Bellman recursion, or weak duality new. Its additional conclusion is precise:

A finite-memory pooled contract is selected through one ex ante table. For that table, inherited tier and remaining payment promise are sufficient state. The same table appears in every child recursion. Participation prices accumulate under conditional probability normalization, and the globally aggregated table coefficient retains the cross-history stationarity condition. A root table LP then certifies the **optimized** restricted value, rather than the value of a fixed table or of separately reoptimized child tables. A tight supporting plane also recovers the restriction-release rent.

The closest-results matrix is in main Table 1 and `NOVELTY_MATRIX.md`. It distinguishes mathematical representation, operational specialization, and computational certification, and identifies the indispensable assumptions for each. The general frontier and envelope statements remain explicitly credited to their established theorem classes. The new result is not asserted to establish bibliographic priority over every possible combination of those literatures; its proof isolates the additional structural statement supplied here.

## 3. Stochastic Models positioning

The stochastic structure is now used in the core proof, not only in the origin of a matrix. The bridge requires conditional remaining payments, Markov sufficiency, positive-probability successor normalization, and nested continuation caps. Its normalized payment prices obey the edge relation

`eta_child - chi_child = eta_parent`,

where `chi_child` is the child's normalized participation price. This relation is obtained from discounted conditional subtree weights. It need not hold for arbitrary polyhedral rows. Meanwhile, the shared table couples stochastic successors that an unconstrained Bellman recursion would separate.

This is why the revised paper retains Stochastic Models as its proposed area. We do not infer that area fit follows from an exogenous scenario tree alone, and we do not extend the scalar state result to arbitrary signed or nonadditive accepted constraints.

## 4. Bridge between the full-vector and augmented-state engines

**Location:** Section 6, Theorem “Shared-table, continuation-price bridge”; EC section “The Shared-Table Bridge: Complete Proof and Representation Costs.”

The model imposes `|x_h-u_(t,m(h))| <= delta*omega_(t,m(h))`, with one globally selected finite-memory table `u`. At zero release it gives exact pooling. Eliminating the scalar table yields the pairwise bounds `|x_h-x_h'| <= 2*delta*omega` within each cell. Thus the bridge connects to the original restriction-release family, with the correct factor two.

The fixed-table promise recursion is exactly equivalent to the corresponding history problem in both directions. Maximizing once over the table gives the optimized restricted class. The recursive affine certificate carries inherited-tier, payment, shared-table, release, and constant coefficients. Nonnegative participation and corridor prices, admissible switching tensions, and scalar box conjugates generate globally valid planes. The root master maximizes the minimum of the stored planes over the same table, giving an upper bound on the optimized comparator. A feasible state policy with one shared table supplies the lower bound and hence a two-sided release-value certificate.

The complete proof also establishes **finite-horizon dual completeness**. Starting from any optimal joint tree primal–dual pair, normalize prices by discounted reach probabilities and construct planes backward. Nested participation makes the child payment coefficients match the parent's price; complementarity and local box optimality make the construction tight; global table stationarity makes the optimizing table maximize the root plane. This proves the existence of an exact recursive certificate at the query.

The existence proof is not a promise that a small exact plane family can always be found without substantial work. Multiple planes can be needed at the same public state, and the certificate DAG can be large. The computational claim is conditional on the stored family and its audited witnesses: query certification uses that state representation and the table master, rather than a newly reconstructed history vector. The manuscript now makes both statements explicit.

The exact two-period example has pooled value `37/50` and unrestricted value `53/50`. Independently reselecting child tables would incorrectly report `53/50` at zero release. Nine rational releases, including cap changes, match independent exhaustive KKT-basis enumeration; their recursive root prices are exact. All 81 anchor/query release comparisons satisfy the supporting inequality. An additional two-plane table master has the exact value `3/8`.

## 5. Endogenous implementation and information costs

**Location:** Section 6, “Choosing an implementable architecture”; EC exact bridge/design example.

We added a specified installation, memory, and release-cost model and optimize net value over the offered architectures and release choices. Within a regular segment an interior design equates the release rent with marginal implementation cost; segment boundaries and alternative architectures are also compared. The same certified lower/upper values give an epsilon-optimal discrete design rule.

This is no longer only exogenous feasible-set accounting. In the exact example, a unit linear release cost selects `delta=1/15`, with net value `56/75` and net improvement `1/150` over no release. Full flexibility has a larger gross value but is not the net-optimal design at this cost. An all-or-nothing flexibility upgrade is worthwhile precisely below the incremental cost `8/25`. These costs are declared decision inputs, not estimated sensor costs or causal information effects.

## 6. Certified cache governance and the retained-face qualification

**Location:** Section 7, “A certified cache-governance rule”; EC “Computable Cache Governance and Complete Query Accounting.”

For any independently audited restricted witness `z^w`, the computed width `U-W(z^w)` bounds the true cache error `U-K`. It is the existing four-term decomposition evaluated at a feasible witness, so it does not require the unknown query optimizer. The controller retains the cache only when that width meets tolerance; otherwise it refreshes or declares the requested tolerance uncertified. A poor witness may trigger an unnecessary refresh, but cannot create a false quality certificate. Full-policy acceptance and net economic gain are checked separately.

We also provide a sufficient face-retention test: solve the equality-constrained KKT linear system on a stored independent active basis, then verify all original primal inequalities, sign conditions, switching tension bounds, and complementarity. A passing test proves query optimality by convex balance. The additional cached-price face conditions then make the local quadratic bound computable. A singular or unsuitable basis is rejected, not inverted or treated as a proof of failure of the true model. Fixed-matrix factorization reuse is distinguished from query refactorization when coefficients change.

The original degenerate two-cap example and its linear loss remain. The attractive quadratic regime is neither treated as global nor needed for the witness-width rule. The new scaling results deliberately charge refresh costs; strict tolerances cause 83 refreshes in 84 queries.

## 7. Uniform certification of an adaptive, not fixed, policy

**Location:** Section 7, Proposition “Adaptive, correlation-preserving cell certificate”; EC corresponding proof and exact example.

We retain the fixed-policy corollary and add a certificate for a **declared piecewise-affine policy map**. On each simplex, affine query constraints composed with the affine policy are quadratic. Vertex checks alone are insufficient. We derive their degree-two Bernstein coefficients, including cross-vertex terms; nonnegative inequality coefficients and zero accepted-equality coefficients certify the entire cell. The implemented full policy is checked against accepted equalities `E`, not comparator-only pooling rows in `F`.

After refinement at switching-sign hyperplanes, the implemented value is quadratic. Convexity of each fixed-price upper bound supplies a vertex chord. A Bernstein lower bound for the remaining quadratic, with the correct cell/anchor/coefficient extremum order, gives a uniform gain certificate. Boundary assignments are part of a piecewise policy's declared implementation.

The exact nonconstant policy on `[1/8,3/8]` is feasible throughout the interval under jointly changing rewards, a continuation coefficient, and switching-friction scale. The restricted witness is feasible throughout too. Its gain certificate is `9/1024`, with all three gain coefficients and the feasibility coefficients recomputed exactly. A separate negative control passes endpoint feasibility but violates the interior; the new cross coefficient rejects it. The inherited R27 off-ray optimizer proposals remain pointwise evidence and are not relabeled as a certified continuous policy map.

## 8. Compact scaling and the scope of operational evidence

**Location:** Section 8, new scaling table; EC “R28 Exact Evidence and Scaling Protocol”; raw `results/evidence.json`.

The study varies tier dimension from 12 to 1,536, services from one to four, parameter dimension from one to eight, cache size from one to eight, and stable versus changing active-cap patterns. It reports pre-governance certificate loss, final error, cache evaluation, candidate generation, candidate audit, witness repair/audit, refresh frequency and cost, initial cache construction, serialized cache bytes, and isolated-process peak RSS.

The same exact full-policy generator and its audit are charged to the cached and fresh pipelines. The fresh comparator is an exact specialized solve for the deliberately block-separable design; it meets a stronger zero-gap criterion within the common requested tolerance. We do not manufacture an advantage by comparing the cache with a slower generic optimizer. Evaluation-only reference solves are charged as online work exactly when the declared trigger refreshes.

All 84 final certificates meet the requested tolerance. However, 83 queries refresh and the cached pipeline is not faster in the measured configurations. This adverse result is retained. The study measures certificate accounting and active-face sensitivity; it is not offered as a dense-QP, calibrated field, or general long-horizon speedup claim. No new neural experiments were added.

## 9. State sufficiency versus accuracy and complexity

**Location:** EC “What is compressed, and what accuracy costs.”

We separate exact state sufficiency, existence of tight finite-horizon dual representations, finite stored a posteriori bounds, approximation assumptions, storage/evaluation, and table/master costs. The paper does not identify any of these with a dimension-free algorithm.

A conditional proposition gives mesh-width bounds under stated domain-relative Lipschitz/support assumptions, and a sharper quadratic mesh bound under a Lipschitz-gradient assumption. The associated covering exponents depend on continuous-state dimension; including the table in a joint mesh includes its dimension too. Boundary conditions and nonsmooth face transitions are treated explicitly. Without the assumptions, the original a posteriori certificate remains valid but no prescribed anchor-count rate is asserted. Branchwise allocation and rational bit costs are additional.

## 10. Closest-results literature comparison

The main literature section and main comparison table now directly address multiparametric QP, promised/resource states, policy aggregation and nonanticipativity, Benders decomposition, stochastic dual value cuts, and reusable Lagrangian bounds. The references add the original Benders (1962) and Rockafellar–Wets (1991) papers. The response matrix states what each general tool supplies and what the nested continuation/shared-table proof adds. The generic engines are credited rather than presented as discoveries.

## 11. Consolidation of the paper

The abstract and introduction no longer present three coequal, disconnected contributions. The central chain is: **precommitted implementable table → promised-state implementation → recursively accumulated continuation/restriction prices → optimized-comparator and net-design certificate**. The older frontier and rent results describe this chain's sensitivity, and the governance/adaptive extensions specify what its deployment certificate actually covers. The historical mathematical results and adverse empirical record are retained, not moved to an undeclared separate project or deleted.

## 12. Specific technical comments

**12.1 — Degenerate release events.** The companion now states an exhaustive finite active/sign-pattern procedure with KKT feasibility checks, simultaneous events, dependent-row multiplier feasibility, and isolated cells. Its correctness and finite termination are explained; no polynomial event count is asserted. The main text distinguishes global structure from a cheap regular-cell continuation algorithm.

**12.2 — Nonunique continuation prices.** The exact bridge example distinguishes left and right derivatives at its kink. A selected dual supports the value but need not be its unique directional price. The scaling labels describe active-cap patterns only; no solver multiplier is interpreted as the directional economic derivative. The inherited minimum-over-optimal-multipliers rule is unchanged.

**12.3 — Friction zero-set cost.** The main proposition now explicitly describes the method as a structural reduction, not a general complexity improvement. Enumeration and KKT projection costs remain visible.

**12.4 — Institution-dependent promise state.** The bridge expressly assumes positive additive payments, public Markov sufficiency, and the stated continuation caps. Arbitrary signed or nonadditive constraints do not inherit the scalar representation automatically.

**12.5 — Query optimization language.** Reuse avoids a new restricted solve only when the certificate is retained. Candidate full policies must still be generated and audited. Refresh queries are counted and charged; no “no query optimization” claim is made for the complete deployment pipeline.

**12.6 — Complete certificate cost.** The companion displays the full cost sum and phase table. Coefficient formation, candidate generation, feasibility/value audits, witness repair, refresh solve/dual audit/update, initial cache cost, and memory are all separate from nominal cached arithmetic.

**12.7 — Uniform feasibility and nonemptiness.** The adaptive proposition prominently assumes every restricted query class is nonempty and verifies full-policy feasibility throughout each cell. Its exact example includes a uniformly feasible restricted witness. Comparator-only equality rows are not mistakenly imposed on the adaptive full policy.

**12.8 — Fixed geometry.** The text explicitly fixes the box, curvature/resource loading, switching operator/offset, and switching weights for the correlated cache family. It describes variation in rewards, commitments, continuation coefficients, and the switching-friction **scale**, not arbitrary cost geometry.

**12.9 — Adverse learning evidence.** The inherited strict-target fallbacks and absence of observed finite amortization remain. No new learned architecture was introduced.

**12.10 — Data and code.** R28 retains the current-paper/archive distinction and adds source assembly, exact evidence generation, independent verification, build/preservation checks, a final-source/PDF manifest, and final-commit validation.

## 13. Minimum deliverables and review status

Each requested deliverable has a concrete revision location: the central bridge and its complete proof; main closest-results table; endogenous implementation cost; witness/face cache governance; adaptive-policy continuum certificate; phase-resolved scaling; and explicit state/accuracy/storage distinctions. The build report records actual pagination and reference/overflow checks. These are completed changes in the submitted revision package, not a declaration that the referee must accept the novelty argument or that finite tests replace proof review. The next referee can inspect the shared-table quantifier order, normalized price recursion, global table stationarity, adaptive cross coefficients, and measured refresh costs directly.
