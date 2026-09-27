# Response to the Operations Research referee: R12 to R13

**Manuscript:** Neural Differential Utility: Accepted Adaptive Service Control and Certified Value-Gradient Learning  
**Report answered:** `reviews/operation_research_referee_report_r12_2026-09-22.md`  
**Review base:** `5b1a62679f890006d8f6a234160fa9a02dcdbc5a`  
**New branch:** `revision/ndu-operations-research-r13-certified-faces-20260922`  
**Date:** September 22, 2026

We thank the referee for distinguishing the resolved R10 mathematical objections from the remaining scientific questions. We retain the integrated accepted-control and learning scope, but replace the dependence on an unavailable optimal face with a constructive, verifiable implementation. This revision supplies new proofs, nonzero-switching decisions, a sparse algorithmic consequence, frozen learning pipelines, and an executed independent-validation procedure. It does not relabel earlier unsuccessful neural transfer as successful.

The main new results are Proposition 4.5 (exact continuation-flow coordinates), Theorem 4.6 (two-pass tension repair, critical-friction brackets, and an explicit profitable policy), Theorem 6.4 (arbitrary-price approximate-face certificate), Theorem 6.5 (verified parameter cells, stability radius, and compatible scalar experts), and Proposition 6.6 (model-derived validation range and simultaneous gain/regret bounds). All essential proofs appear in the main paper. The full prior noncentered experiment is reproduced unchanged in the electronic companion.

## 1. Results the report already regards as resolved

The general full-tree balance, vector and boundary scope, signed coefficients, multiple commitments, nonconstant-comparator friction interval, canonical information hierarchy, and price-capacity margin are retained. Their original source files are unchanged. The new scalar coordinate and quadratic-cell results are additional specializations; they do not replace the more general theorems with narrower statements. The historical nonlinear study remains part of the evidence.

## 2. Beyond a restatement of convex duality

Sections 4.5–4.6 extract a concrete algorithm from continuation participation. A nonnegative transfer variable equals each subtree's unpaid continuation amount. The mapping to tiers is a bijection onto the entire accepted polytope, not a restricted actor class or a feasibility heuristic. It has two nonzero entries per column.

Theorem 4.6 turns *any* capacity-feasible tension proposal into an upper witness for critical friction by a forward price correction and backward subtree sum. A nonnegative transfer supplies a lower witness. Below that lower threshold, the same transfer yields a closed-form accepted policy and an exact quadratic profit calculation along its feasible ray. Thus the result supplies a decision and a certificate, not only a necessary optimality system.

A factored formulation has `9N-3` matrix entries. On a star, prematurely forming the composite incidence matrix produces quadratic fill-in. The paper and experiments distinguish this sparsity result, the standard accelerated-gradient convergence bound, and actual numerical runtime. We explicitly credit convex duality, total-variation paths, and FISTA rather than claiming their invention.

## 3. The nonsmooth theorem is now used in decisions and learning

Section 7.2 solves 81 epigraph quadratic programs over three contexts, three tree sizes, and nine friction levels. These paths include zero only as a control and cross the computed critical threshold. Table 2 reports actual gains, switching, binding continuation constraints, and fused edges. Every policy has an independently replayed rational gap.

More importantly, the learning distribution itself now has absolute friction between 0.01 and 0.20, never zero. Its cells jointly encode continuation constraints and nonsmooth switching signs. The new structural and learning studies therefore solve the same nonsmooth accepted-control model. The predecessor smooth experiment remains unchanged and separately labeled.

## 4. Removing the unknown-face oracle

Theorem 6.4 allows arbitrary predicted inequality prices, equality prices, box prices, and capacity-feasible tensions. A tension need not have the candidate's switching sign. The certificate explicitly adds the nonnegative Fenchel switching leakage. The resulting bound is squared stationarity error plus continuation, box, and switching leakage. It neither assumes nor queries an optimal multiplier or optimal face.

The same computable bound yields a safe primal radius and strict tests for inactive constraints and nonzero switching signs. We do **not** infer binding equalities from a small Euclidean error: that inference would be invalid.

Theorem 6.5 gives the requested independently usable face mechanism in the quadratic subclass. A full-row-rank candidate basis defines affine primal and price maps. Every query must pass all primal, price-sign, tension-capacity, and switching-sign inequalities. Passing establishes global optimality by a complete KKT certificate, not by the classifier's confidence. The theorem also gives an explicit parameter stability radius. A trained neural classifier only proposes indices; an incorrect or absent cell invokes the specified fallback. No full query optimization is needed for an accepted region.

The offline cost is explicit. This is not a claim that labels, multipliers, or faces arise without an offline solve. It is also not a new claim to multiparametric quadratic programming; Bemporad et al. are credited. The new operational bridge is a verified continuation/switching cell with a compatible scalar expert and an independent certificate even for a wrong proposed face.

## 5. The validation theorem is actually executed

The frozen policies, features, library, and rejection rules are saved before validation. Three complete policies are evaluated: one neural cell, three neural cells, and the nearest training anchor's cell, each with a static gate. The first independent sample uses a broad analytic gradient range; all its loose results are retained.

A second, prospective confirmation plan then fixes a tighter *model-derived* range from four deterministic forcing-box corners at minimum friction. Neither the neural model nor its policies are changed. A fresh seed generates 4,096 independent confirmation contexts. Proposition 6.6 gives simultaneous gain and regret statements with `M=3`, `n=4096`, and `delta=0.05`. The plan, corner certificates, model hashes, exact sample sums, and all failed cell lookups are saved.

Table 5 reports both types of bounds. The selected neural policy has a positive expected-gain floor relative to static in this declared synthetic distribution. Its expected-regret ceiling is still too wide to claim near-optimal raw deployment. Reporting that distinction is essential: the positive gain certificate is operationally nonvacuous, whereas high-accuracy deployment still requires the separately timed refinement rule. The concentration inequality is explicitly credited as standard.

## 6. Poor inherited neural actors are not hidden

The 48-instance nonlinear experiment, negative projected gains, 162 adverse projections, four-seed uncertainty, and lack of a resolved derivative-weighting benefit remain intact. No old result is pooled with the new experiment. The new neural classifier learns joint face labels for compatible value experts; it is not presented as a successful rerun of the old regressor.

The new rejection rates are also retained. The neural top-three policy covers only a fraction of the parameter distribution. Coverage, initial policy quality, and the final certified solution are distinct measurements. Claims about a universal architecture or gradient-supervision advantage are not made.

## 7. Candidate contribution versus classical rescue

Table 4 compares complete matched-accuracy pipelines. It includes a cold epigraph quadratic program, neural top-three lookup, nearest-anchor lookup, and sequential checking of the same frozen library. Times include membership checks, exact rational audit, and any actually executed refinement. Rejected cells use a cold feasible solve; they are not credited with hypothetical warm-start savings.

The table reports immediate certification, refinement frequency, first-proposal face accuracy, and added solver iterations. Full records include initial and final certificates, elapsed times, distances, and all refinement flags. Sequential cell checking is an important stronger comparator; the paper explicitly reports that its latency is better in the recorded run. Offline construction and the arithmetic break-even calculation are separate. The observed neural-versus-cold saving is not turned into a statistical speed claim or an advantage over the best classical lookup.

## 8–9. Title and integrated scientific identity

We retain the title and the integrated scope, addressing the stated evidentiary burden with constructive results rather than a branding change. The continuation-transfer structure is now the actual feasible representation for the nonsmooth learning experiment. Continuation prices and switching tensions define both the verified scalar experts and the policy certificate. The independent validation uses those complete accepted policies, including their rejections. These links are mathematical and executable.

The learning claim is specific: a trained router can reuse verified compatible experts without knowing the query optimum, and its frozen accepted policy can receive an out-of-sample expected-gain certificate. It is not a claim that a neural classifier is intrinsically better than every classical search of the same cells. The earlier acceptance-face decomposition remains a useful explanation, but it is no longer the only approximation-to-decision result.

## 10. Scale and algorithmic exploitation

Section 7.2 and Table 3 include binary and star trees up to 1,023 nodes. Both critical-friction LPs use the same HiGHS solver. The factored representation avoids quadratic fill-in on a star; on a bounded-degree tree the materialized formulation may be faster. The first-order implementation uses exact linear-time formulas for induced operator norms without forming the composite matrix.

Its iteration limit is enforced and reported. Some 12,000-iteration brackets do not meet the requested `1e-4` width, and those outcomes remain in the table and data. Each returned interval still has a rational lower direction and upper tension witness. The paper claims linear work per iteration and a structural sparsity benefit, not a linear-time total solver or a universal first-order speed advantage.

## 11. Meaning of the price-capacity margin

The original margin theorem and its assumptions remain. The introduction now states expressly that exact equality requires the quadratic-curvature and feasible-step-clearance conditions. It is not advertised as a universally exact adaptation-value formula near boundaries or kinks.

The new ray calculation has its own precise scope: a constant interior comparator with zero initial switching, nonnegative accepted transfers, and quadratic smooth resource. Along that ray switching is positively homogeneous, so the displayed profit calculation is exact up to the tier-bound step. This avoids importing an unstated switching-sign clearance condition.

## 12–13. Economic scope, units, and offline control

The observable, externally priced institution is unchanged. There is no invented private-information or hidden-action application. Section 7.1 states every new cost term, monetary normalization, tariff coefficient, physical-stock treatment, and sampling rule. A currency conversion is explicitly an illustration, not field calibration.

The new balanced-shock class has an exactly reoptimized constant static tier; its zero-sum forcing makes that conclusion provable. This favorable reusable context structure is not confused with the earlier noncentered boundary class. The paper continues to identify scenario-tree convex optimization and promised-resource recursion as established ideas. Its new contribution lies in the extracted continuation structure and its verified deployment.

## 14. Statistical claims

The four inherited training seeds remain a small transfer diagnostic and do not support representative training-variability claims. The old unresolved derivative-weighting comparison remains unresolved. New confirmation is conditional on one frozen classifier and a declared distribution; it does not establish superiority across random training runs. Timing observations remain descriptive. The confidence statement is about expected gain and regret of frozen *complete policies*, not about the neural training procedure or arbitrary shifts.

## 15. Technical and presentation comments: individual disposition

**15.1:** Executed model-range calculation and independent confirmation; `M,n,delta,B`, exact sums, positive gain floors, and wide regret ceilings are all reported in Table 5 and `results/confirmation.json`.

**15.2:** Nonzero absolute switching in every new learning context; 81 friction-path decisions and all policy audits are retained.

**15.3:** The 48 matched contexts have first-face accuracy and distances; `face_diagnostics.json.gz` additionally records 96 raw neural/nearest constraint masks, switching signs, membership decisions, and price-leakage certificates. Diagnostic mask tolerances are disclosed.

**15.4:** Table 4 separates immediate success, static-before-refinement, actual refinement, added iterations, and final accuracy. Full timing records contain both candidate and final outcomes. No classical rescue is counted as a successful raw actor.

**15.5:** The earlier first four frozen seeds are preserved as a computationally limited transfer diagnostic, not relabeled a representative sample. No new training-variability inference is built on them.

**15.6:** Exact payment coordinates, two-pass dual repair, a profitable lower-witness policy, factored LP, sparse accelerated feasibility iterations, and explicit iteration-cap outcomes are added.

**15.7:** Generalized-lasso and graph total-variation paths, their efficient implementation, FISTA, gap-based screening, and explicit parametric control are now separately credited. The continuation-specific one-sided cone condition and repair are identified rather than presented as new generic convex duality.

**15.8:** “Policy certificate” and “expected performance of a frozen complete pipeline” are kept distinct. Numerical region membership alone is not a certificate; rational replay checks the repaired policy and all switching leakage.

**15.9:** Section 7.1 specifies profit units, maintenance curvature, absolute reconfiguration prices, review normalization, and the status of an illustrative currency conversion.

**15.10:** Every essential new proof is in the main paper. The current electronic companion contains implementation details and the unabridged earlier nonlinear experiment. The historical supplement remains a preservation archive, not required support for a new theorem.

## 16–17. Requested routes to a stronger submission

We take the constructive integrated route. The revision supplies the explicitly requested non-oracular usable-face theorem, a verifiable face mechanism with stability, and a genuinely executed independent-validation example with a positive gain bound. It also exercises absolute switching and adds a continuation-specific algorithmic consequence. We do not treat these results as evidence of every alternative item in the referee's list: universal neural speed, high-dimensional cell coverage, and derivative-supervision superiority would be different claims.

The preserved title therefore rests on a specified learning contribution, not on hiding the classical component. Its scope is stated where each result is used. Editorial judgments about novelty and fit remain for the referee; numerical audit success is not presented as a substitute for them.

## 18–19. Reproducibility, preservation, and review package

The new branch starts from the exact reviewed report commit and changes no other manuscript branch. Ordinary TeX and Python sources, frozen coefficients, complete policy records, exact upper/lower witnesses, build scripts, hashes, and the response are committed. The standard-library-only verifier imports neither an optimizer nor numerical linear algebra. A separate package check verifies unchanged predecessor files, abstract length, page limits, references, and overfull lines.

The main paper follows the journal's lengthy-manuscript format: 11-point type, 1.5 spacing, one-inch margins, a text-only abstract below 200 words, a nonmathematical introduction, author-year references, and deferred tables. The electronic companion is shorter than the main paper. Current machine-generated counts and timings are authoritative in `results/verification.json`, `results/package_checks.json`, and `results/summary.json`.

The revision is offered for a fresh mathematical and scientific review of these additional results. It makes no claim that a favorable editorial recommendation has already been obtained.
