# Response to the R10 referee report — Revision R12

**Manuscript:** *Neural Differential Utility: Accepted Adaptive Service Control and Certified Value-Gradient Learning*  
**Journal:** Operations Research  
**Revision date:** September 22, 2026  
**Review addressed:** `reviews/operation_research_referee_report_r10_2026-09-21.md`, on `review/operation-research-r10-harsh-20260921`, commit `b3abde1e805f36292f03c7ee65df7ef9298020b0`.  
**Reviewed scientific manuscript:** R10, commit `3f5bc42f0fa053453ca82f8ab3d66b5b46d88372`.  
**New branch:** `revision/ndu-operations-research-r12-20260922`.

We thank the referee for distinguishing the mathematical and reproducibility repairs already made in R10 from the remaining scientific burden. We agree that another packaging change or an unmatched-accuracy timing table would not answer that burden. R12 therefore adds a full-tree nonsmooth theory, a quantitative price–capacity margin, a learning-to-decision theorem with its necessary acceptance-face qualification, a finite-sample certificate for pipeline selection, and an actually executed matched-tolerance implementation study. All essential new proofs are in the main manuscript. The previous theory, computations, adverse outcomes, and source files remain available; their destinations are documented in `PRESERVATION.md`.

We retain the integrated title and address the alternative offered in the report—develop substantive structural and learning results—rather than removing the learning question. The revised meaning of certification is explicit. Deterministic policy certificates, an approximation-to-decision theorem on an identified acceptance face, and independent-validation selection guarantees are different statements with different assumptions. None implies that every learned actor generalizes across graph families, that gradient weighting is statistically superior in the present experiments, or that learning is faster at matched accuracy.

## A. New results and where to read them

**Full-tree structure (main Section 4).** The capacitated continuation-balance theorem treats an arbitrary feasible comparator in a compact polyhedron, including vector tiers, smooth graph coupling, multiple commitments, equality/information restrictions, boundary coordinates, and signed or zero net-payment coefficients. Absolute switching enters through bounded edge tensions, with saturation on already-changing edges. Optimality of a fixed comparator is equivalent to feasibility of an explicit linear program. On scalar trees, eliminating tensions produces subtree cuts and an isotonic critical-friction program. The scalar ratio formula is used only where its positive-tariff assumptions hold.

**Quantitative adaptation (main Section 4).** The distance from marginal operating reward to the continuation-price/switching-capacity set defines a price–capacity margin. Its squared value gives two-sided accepted-gain bounds with explicit curvature and feasible/sign-clearance conditions. The bounds coincide for the stated quadratic subclass, yielding an exact gain and an optimal improving policy. This goes beyond a binary normal-cone membership test. We also prove friction and continuation-tightness comparative statics and show why a nonconstant outside protocol can have a bounded optimal-friction interval instead of an upper ray.

**Structural learning connection (main Section 6).** An exact loss decomposition separates smooth Bregman error, continuation-price slack, boundary-price loss, and switching-face loss. On the exposed acceptance/switching face, projecting a compatible predicted actor yields a quadratic gradient-error-to-regret bound. A boundary counterexample shows that dropping the face hypothesis produces a false theorem. The independent residual certificate remains available without knowing the optimal face. A separate finite-sample result selects among frozen, complete learning pipelines from independent bounded-certificate validation observations. Standard convex analysis and concentration tools are credited as such.

**Executed implementation study (main Section 7 and current EC diagnostics).** There are 48 noncentered instances, twelve in each of four fixed graph families, and 432 new deployments. Service-specific static tiers are reoptimized and independently certified; fifteen comparators have a boundary coordinate. Four frozen training seeds per learned method are evaluated without fitting on the new instances. The pipeline actually generates, projects, rounds, audits, gates, and refines until its rational certificate meets the same declared tolerance as cold SLSQP. All 432 deployments meet the tighter tolerance of `1e-7` per discounted service-review, and their exact final reward is at least the static reward. All forty failed original 992-coordinate weighted-block proposals also receive an actually measured classical fallback. These successful final decisions do not erase the failed raw actors or demonstrate a learning speed advantage.

The build writes exact run counts and environment-specific timing summaries to `results/verification.json`, `results/summary.json`, and the generated tables. `results/structural_checks.json` distinguishes numerical cross-checks from exact examples and from the analytic proofs.

## B. Responses to the numbered report

### 1. Repairs already achieved in R10

We preserve the repaired stock identification, vector resource formulation, continuation participation, exact canonical hierarchy, nonlinear quartic task, all adverse transfer observations, cached classical re-audit, and independent rational verification. R12 does not reopen a closed objection by reverting to the previous scalar/univariate graph notation or by calling a nonlinear finite difference exact. The R10 nonlinear and quadratic verification script is replayed in the R12 reproduction command. Original historical directories are not rewritten to make their old outputs resemble the new study.

### 2. Contribution and paper identity

The revised sequence is now institution, full-tree structural prices and capacities, exact economic illustration, the corresponding learning/decision loss decomposition, and measured certified implementation. In R10, the tree theorem and vector experiment shared a vocabulary but little mathematical machinery. In R12, the general balance equation, continuation/boundary prices, and switching faces also determine the full-horizon certificate and the approximation-to-decision theorem. The price–capacity margin makes this connection quantitative. We do not count a generic KKT identity or a Hoeffding inequality alone as a new scientific principle.

### 3. Generality and novelty of the scalar edge criterion

The new main result is not limited to a constant interior scalar tier. The general theorem accepts nonconstant feasible comparators, boundary coordinates, vector services, arbitrary linear commitments, and signed payment coefficients. Its subgradient optimality principle is established convex analysis. Its operational specialization yields a complete full-tree capacity system, and the scalar corollary eliminates all edge tensions into cumulative payment-price cuts. The old two-coordinate perturbation survives as a special case, not as the flagship generality claim.

For zero-switching scalar comparators, the critical friction minimizes the largest normalized subtree imbalance over isotonic continuation prices. The program has a linear number of variables and sparse balance constraints; evaluating a proposed price vector takes a backward tree pass. We do not claim that solving the entire linear program takes linear time. For a nonconstant comparator, saturated switching edges can prevent monotonicity in friction. The optimality set is a closed interval, possibly empty, bounded, a singleton, or unbounded. The exact example with a fixed root tier zero and outside child tier one has optimality interval `[0,1]`, and directly refutes an overgeneralized upper-threshold assertion.

The sharp price–capacity margin further provides lower and upper bounds on the amount of accepted value, not only existence of an improving direction. The lower bound keeps tier-boundary and switching-sign clearance explicit; the quadratic equality case gives an exact optimum when the specified step remains feasible. These are proved in the main text, with exact rational examples in the test file.

### 4. Stock identification and exogenous occupation weights

We retain the complete supporting-price proposition, including atoms, endpoints, slack commitments, and the additive vector extension. It is identified as a standard supporting-price/newsvendor argument specialized to accepted service control. It is a reduction supporting the new theorems, not a separate claim of flagship novelty. Regime occupation probabilities are still exogenous and policy invariant. The new structural extensions do not silently extend stock identification to tier-dependent demand, retention, or transition laws. Such a model would require an additional argument; no endogenous-demand theorem is claimed.

### 5. Remaining-payment and promise states

Altman (1999), Spear and Srivastava (1987), and Thomas and Worrall (1988) are now discussed in the main literature section and at the budget recursion. We distinguish constrained-resource states, promised utility, and self-enforcement from our observable fixed-tariff institution. The remaining-payment construction is not described as a new dynamic-programming principle. The new contribution is the price/capacity structure induced by these continuation rows.

The current normalization paragraph states that a node budget is conditional and discounted from that node. Multiplication by the node's discounted reach probability gives the unconditional subtree row. The child term is the discount factor times the conditional child probability. This prevents counting reach probabilities twice. Several commitments lead to a vector budget state.

### 6. Zero-friction memory and its interpretation

The original zero-friction proposition and exact `1/32` counterexample are retained in the main appendix. The proposition requires only ex-ante linear commitments and no additional history-dependent feasibility; it is not transferred to arbitrary continuation promises. Contractual memory can identify past obligations without adding a demand signal. The canonical inherited-tier increment remains `0.019290378765...`, about three percent of the total accepted gain `0.636665271611...`; neither number is relabeled to make memory appear dominant.

### 7. Severe shifted-family failure and usefulness of the certificates

All forty original weighted-block failures and their negative raw gains remain in the current companion and records. We add three distinct diagnostics: feasibility before repair, a policy's certified optimality gap, and the exact reward-based gate decision. The new ratio table reports proposal-bound/classical-gain and selected-decision-bound/classical-gain separately. On the original weighted-block cases, the typical proposed bound is over a thousand times the available classical gain. The tighter static-aware gate is still far from an economically tight optimality certificate.

The response is to execute refinement rather than declare a no-harm gate equivalent to successful learning. Every one of those forty original cases now has a measured cached classical fallback and a tight final rational certificate. This is labeled a classical fallback, not a beneficial learned warm start. It solves the implementation tolerance in those cases without pretending that the raw representation transferred successfully.

### 8. What is certified about learning

We preserve the title but now distinguish its supported meanings in the abstract, introduction, and Section 6. The full-horizon certificate is method-independent. The acceptance-face theorem is an approximation guarantee connecting a compatible critic's gradient to accepted regret under explicit structural conditions. The validation proposition is a finite-sample guarantee for selecting an entire frozen learning/repair/refinement pipeline. It requires independent validation from the deployment distribution and a valid uniform certificate bound.

We do not claim that the fixed-feature regression has a universal convergence rate, an unrestricted distribution-shift guarantee, or a statistical advantage over value-only fitting. Nor is the unknown optimal face granted to the implemented actor. The theorem states when such a face can be used and why a merely predicted face does not establish the guarantee. The deterministic audit is the available safeguard when that condition is not known.

### 9. Unresolved empirical advantage of derivative weighting

The R10 paired interval is preserved and remains explicitly conditional on its eight fixed test problems. In the new noncentered study, the paired projection-gain difference is approximately `0.043611`, with descriptive crossed-bootstrap interval approximately `[-0.404368, 0.450732]`. This also includes zero. We therefore do not claim statistical superiority of derivative weighting. The positive theoretical results concern approximation under the stated acceptance-face structure and independently validated pipeline selection; they are not represented as a significance result in these data.

### 10. Training variation versus problem variation

The new design crosses four previously frozen training seeds with twelve independently generated instances in each of four fixed graph families. We separate training-seed variation, within-family instance variation, the deliberate family shifts, and timing repetitions. Replication identifiers are reused across graph families, creating common-random-number blocks. The bootstrap resamples training seeds and these replication blocks jointly across all four fixed families, rather than treating the family draws as independent. Four training seeds and four selected families do not justify a population claim over every possible training run or graph family; the reported interval is described accordingly. Five timing repetitions after a warmup are a separate latency experiment, not sixty extra economic test problems.

### 11. The engineered one-half static comparator

The new forcing is not weighted-centered. Each service's constant-in-time tier is reoptimized including initial installation and spatial coupling, and the outside protocol is certified in that stronger vector static class. Recorded comparators range from zero to one, with fifteen boundary-inclusive cases. Their largest unnormalized static-class gap is approximately `3.9e-14`. This is a rigorously bounded numerical static comparator, not a claim of symbolic exactness for an irrational optimizer. Continuation caps are defined once from that recorded outside protocol and are identical for learned and classical methods.

### 12. Repair distortion and feasibility-aware actors

The new records retain box-clipped pre-repair gains and violations, global scaling factors, exact radial-repair losses, projection losses, and alternative actor outcomes. Weighted Euclidean projection minimizes discounted tier distortion subject to all constraints; it is not mislabeled an objective-maximizing projection. A separate nonnegative child-to-parent flow actor is feasible by construction after a box-limited step. Root payment is unchanged and every nonroot subtree payment changes by minus its incoming flow. This is a useful structural class, not a claim that it spans all vector feasible policies or knows the optimal face.

Of the 384 new learned proposals, 162 remain worse than static after weighted projection. Thus a better repair alone does not solve the shifted representation error. The face-loss decomposition explains how repair can add expensive first-order commitment slack, while the records show that the remaining issue can also be a poor actor. These cases are retained before and after fallback.

### 13. Matched accuracy and mature classical software

The new comparison uses SciPy's SLSQP implementation, in addition to the retained Newton/direct, cached-Newton/PCG, and cached quadratic solvers. Each method receives the same objective, analytic gradients, box bounds, all continuation inequalities, and exact certificate with explicit boundary prices. Initial candidates, every fifth iteration, and termination are checked under the same audit schedule. The stopping condition compares the rational bound directly with the rational tolerance times discounted service-review mass.

Both `1e-5` and `1e-7` tolerances are reported. Learned end-to-end time includes feature evaluation, projection, rounding/repair, certification, gating, and the refinement that actually occurred. Comparator construction and common setup are separate. The experiment does not establish a learning speed advantage; cold SLSQP is faster in the recorded matched-accuracy comparisons. We report that result rather than compare an inaccurate learned actor to a much more accurate classical policy and call the difference a speedup.

### 14. The cached quadratic re-audit

The complete old quadratic learned-control section and the corrective cached re-audit are now in the current companion, not a coequal main-paper contribution. The original observations and the correction remain adjacent enough to prevent the old uncached timing interpretation from being mistaken for the current conclusion. No sparse-solver disadvantage is manufactured by moving setup inside every classical call. The historical rows remain available for inspection.

### 15. Architecture scope

The inherited architecture is still a fixed 63-feature softplus potential with fitted linear readouts and local graph/tree transforms. It is not claimed as an architectural invention. The R12 methods contribution is the acceptance-aware approximation/certificate connection and the specified deployed pipeline, not a new universal neural architecture. All four frozen coefficient vectors and their original scalar teaching records remain in the predecessor scientific directory.

### 16. Finite-difference and oracle-error sensitivity

The new sensitivity study uses twelve independently generated training-sized problems and step sizes `1/80`, `1/40`, and `1/20`. It solves and certifies both endpoints and the central policy. Full endpoint primitives, policies, multipliers, and certificates are recorded in `results/fd_oracles.json`, and the independent verifier reconstructs all of them. The deterministic step-size/oracle-gap bound is reported alongside the measured directional discrepancy.

The additional endpoint-error allowances zero, `1e-7`, and `1e-5` per service-review are analytic sensitivity allowances, not falsely described as new noisy-oracle trials. The reference derivative uses the computed central policy; its observed error is not called an exact derivative error. The rigorous directional-target bound uses the value-oracle bounds and the proved Lipschitz constant. A small target bound still does not establish a statistical advantage of derivative fitting.

### 17. Meaning of the value-only baseline

The main text now explicitly says that value-only fitting uses no derivative targets but shares feature scaling computed partly from derivative-feature geometry. It is not described as derivative-free preprocessing. Both fitting procedures continue to receive the same scalar observations, so no additional scalar oracle access is hidden in the derivative-weighted comparison.

### 18. Application evidence

The studies remain synthetic. We have not invented customer contracts, field observations, or a calibration. Instead, we have materially broadened the structural model and supplied exact full-tree conditions, quantitative gain bounds, and boundary-inclusive implementation tests. The new theory does not require the centered canonical instance, a particular graph family, or an empirical speed advantage. A field calibration would constitute additional evidence, not something supplied by renaming the synthetic stress tests.

### 19. Literature positioning

The main discussion adds constrained Markov decision processes, promised-utility and self-enforcement methods, approximate dynamic programming, constrained-policy learning, modern numerical software, and generalized-lasso duality. In particular, the subgradient machinery, absolute-value duality, supporting-price stock reduction, concentration inequality, and generic strong-convexity residual bound are credited as standard tools. The incremental claims are their continuation-compatible tree/capacity structure, quantitative margin and feasible improvement, and the acceptance-face distinction for implemented value-gradient proposals. Primary publisher, proceedings, or author sources were checked for the new bibliography; `LITERATURE_SOURCES.md` records those checks.

### 20. The connection between the two parts of the paper

The relevant common object is no longer just the service-control vocabulary. Continuation prices, boundary normals, and switching tensions decide whether the comparator is optimal; their best balance residual quantifies the gain; their policy residual certifies deployment; and their complementary faces decide whether actor-gradient error creates quadratic or first-order loss. This is a single structural dependency across the main results. The experiment tests precisely the distinction between feasibility, acceptance-price distortion, and useful certified output. Generality of the structural theorem is not inferred from empirical performance of the frozen critic.

### 21. The suggested theory-focused route

We have solved several of the requested generalizations, not merely listed them: arbitrary feasible comparators, boundary tiers, vector and multiple-commitment polyhedra, signed coefficients, and full-tree absolute switching. We also add friction, capacity, and continuation-tightness comparisons and the sharp gain margin. Promise-state positioning is repaired. The exact canonical hierarchy is now an illustration of the structural results. The old quadratic implementation has moved out of the main chain. We retain learning in the title because R12 also supplies the structural learning theorem and the validation-selection statement, with their assumptions made explicit. No field calibration is claimed.

### 22. The suggested learning-focused route

The response is both theoretical and operational. The new acceptance-face theorem specifies a positive approximation-to-decision guarantee; the selection proposition gives a finite-sample guarantee for complete frozen pipelines under independent bounded-certificate validation. The implemented pipeline is actually benchmarked at matched certified tolerances, on many more noncentered and boundary-inclusive instances, with repair diagnostics and mature classical software. All original severe-shift failures are measured through their eventual certified fallback. These additions establish the declared pipeline guarantees, but they do not establish that the raw learned representation now transfers reliably or that learning improves latency. Those are separate empirical claims and remain unsupported by this run.

### 23. Reproducibility and ordinary active sources

Every active manuscript input is now an ordinary committed TeX source. Building R12 does not invoke the predecessor preparation script. The copies generated by that script for R7 are preserved as ordinary files under `retained/`, and its historical inputs remain untouched. R12 reproduction separately executes scientific tests, generates tables from actual results, runs an independent standard-library Fraction verifier, replays the predecessor verifier, builds all three documents, and records source/result/PDF hashes. Temporary publication transport is not the reading package: the published branch contains ordinary sources, full rational records, and actual PDFs.

## C. Detailed technical comments in Section 24

| Comment | Revision and precise location |
|---|---|
| 24.1 Abstract scope | The abstract now describes the arbitrary-polyhedral balance result, then explicitly identifies the scalar-tree cut specialization. The narrow earlier criterion is retained in the main appendix. |
| 24.2 Root equality versus weak acceptance | Section 4 allows general linear inequalities and equalities; the scalar-cut corollary separately gives free, nonnegative, and zero root-price cases. |
| 24.3 Positive tariffs | The balance theorem does not divide by tariffs. The scalar isotonic ratio/cut representation states positivity. Expected indemnity can make a net rate nonpositive without a negative gross premium. |
| 24.4 Boundary comparators | Explicit outward box normals enter the theorem, residual audit, loss decomposition, and new boundary-inclusive experiments. |
| 24.5 Vector scope | Vector tiers and smooth graph coupling are covered by the general balance theorem; scalar subtree elimination is not mislabeled a vector ratio formula. |
| 24.6 Full-tree absolute switching | Main Section 4 gives saturated/unsaturated edge capacities, cumulative subtree cuts, and the exact critical-friction program. |
| 24.7 Budget normalization | The closing paragraph of Section 4 defines conditional budgets and their unconditional subtree conversion. |
| 24.8 Selected static gap | Section 6 uses the minimum of the proposal and static upper bounds minus the selected reward. EC diagnostics show the selected bound, not just the rejected proposal's bound. |
| 24.9 Certificate scale | EC ratio table and `old_diagnostics.json` report proposal and selected bounds divided by classical achievable gain. |
| 24.10 Step-size sensitivity | EC sensitivity table, `fd_sensitivity.json`, and all central/endpoint witnesses in `fd_oracles.json`. |
| 24.11 Value-only preprocessing | Main Section 7 states that derivative-feature geometry is shared even though derivative targets are not used by value-only regression. |
| 24.12 Timing environment | `summary.json` records Python, NumPy, SciPy, platform, and thread settings; repeated raw observations are retained. No hardware-independent millisecond ranking is asserted. |
| 24.13 Classical solver breadth | SLSQP matched-tolerance pipeline plus the retained cached quadratic and Newton/direct/PCG baselines. |
| 24.14 Noncentered comparator | Forty-eight new uncentered instances; per-service static optimization; fifteen boundary-inclusive comparators; exact static-loss bounds. |
| 24.15 Test independence | Original seed-only interval stays conditional on eight problems. New crossed bootstrap stays conditional on the four selected families. Neither is repurposed as the independent-validation theorem. |
| 24.16 Historical supplement | The historical file is explicitly an archive, not the current journal electronic companion or a prerequisite for understanding the new results. |
| 24.17 Main-paper length | Old quadratic results move to the current EC; earlier extensions remain in the archive. The build checks the main-paper page limit excluding references and the current EC length. |
| 24.18 Terminology | Candidate-specific discussion uses certificate-checked proposals; learning-specific guarantees refer explicitly to the acceptance-face theorem or independent-validation selection proposition. |

### 25. Minimum bar for a new full review

This is not an R11-style addition of tables around the same theorem. It supplies the requested full-tree nonsmooth structure, material generalizations, quantitative comparative statics, revised literature positioning, a new learning/decision theorem, and a measured tolerance-controlled implementation study. The existing R11 structural branch contained only two incomplete transport fragments; R12 preserves those historical commits but publishes a complete ordinary-source package on its own new branch. Whether the incremental results satisfy the journal's editorial novelty threshold remains a question for independent review, not something a build script or certificate can decide.

### 26. Final assessment and scope of the response

We have responded by adding proofs and executed evidence rather than deleting the question or replacing negative observations with positive rhetoric. The generalized balance/cut/margin results and acceptance-face analysis are the main positive scientific additions. The fallback pipeline demonstrably obtains feasible, certified high-quality decisions on the declared finite test sets. Raw learned transfer and latency superiority are not established, and the manuscript states that distinction directly. All historical claims can be traced to their original source, all new claims have named assumptions and witnesses, and no empirical calibration or journal acceptance is represented as accomplished.
