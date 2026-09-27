# Response to the independent R45 referee report

**Manuscript:** Limited-Memory Renewal Contracts: Harmonic Coarsening and Certified Joint Design  
**Revision:** R48, September 25, 2026  
**Report:** operation_research_referee_report_r45_independent_harsh_2026-09-25.md  
**Review commit:** 260a5224c55e0326d9da7f0c813b4a3fcab7671f  
**Immediate scientific base:** R47, df1e192fd0846315ff0938e57d797efcd04109aa

## Overview

We thank the referee for separating mathematical correctness from methodological significance. The report recognizes the conditional dynamic program and original-budget target net, but correctly requires a structural joint method, a meaningful complexity regime, and evidence that certifies original policies rather than only conditional designs. This revision addresses those requirements through the complete post-review development, while distinguishing what was already established in R46 and R47 from the new R48 results.

The current paper retains the original contractual and continuous-design scope. It does not use command augmentation as a prerequisite for the main approximation result, replace realized ceilings with mean constraints, remove opening charges, or substitute an easier acceptance problem. Every original mathematical statement and proof remains in the article or electronic companion. Forty-nine antecedent mathematical labels and four new results are checked during the build. Longer computational narratives are moved intact to a separately identified repository reproduction record; their measurements are not relabeled as new executions.

R46 supplies exact response-type aggregation, a two-sided price-path oracle on target boxes, an independently checkable adaptive target cover, and matched global-algorithm comparisons. R47 supplies guarded optimistic aggregation of distinct histories, an original-contract lift, and a variable-history additive scheme. R48 strengthens that reduction: weighted harmonic curvatures yield a dominating upper model; optimal within-group recovery improves the original policy; and square-root curvature bins improve the worst-case accuracy-dependent dimension. The new study deliberately includes wide cost dispersion and retained failures rather than only the clustered inputs on which R47 performs well.

## 1. Complexity frontier and the role of the full target grid

**Referee concern: the only original-budget global guarantee is a direct grid whose exponent is the raw branch count.**

The main guarantee no longer depends on running that full grid. The R46 adaptive method bounds entire target regions using a polynomial two-sided price-path oracle. Its lower-target constraints can require commands on the decreasing side of the priced reward; the proof and a counterexample explain why the older monotone priced-path deletion argument is insufficient. A checker verifies the complete target cover and every upper table. This is a joint bound over all feasible books in a region, not conditional optimization at one supplied target vector.

The R47 variable-history result then bounds the reduced dimension through eligibility complexity and cap/cost dispersion rather than the number of distinct histories. R48 improves this parameter dependence using harmonic pooling. For normalized rational quadratic data, the new dimension bound is

`1 + E (1 + ceil(2L/epsilon)) (1 + ceil(sqrt(2 Gamma/epsilon)))`.

The cost-coordinate factor is proportional to the inverse square root of accuracy rather than its inverse. This follows from a square-root arithmetic--harmonic dispersion bound, including zero curvature, not from assuming a positive lower curvature. Cap bins and the minimum-cap guard preserve the original feasible anchors and exact aggregate capacity. At fixed eligibility complexity, bounded primitive scales, and fixed positive accuracy, the algorithm is polynomial in the variable history count, catalog size, command budget, and rational input length.

We distinguish a positive parameterized algorithm from a hardness classification. Neither R48 nor its predecessors prove NP-hardness for unrestricted eligibility complexity, or prove that exponential dependence on the reduced dimension is unavoidable. The adaptive cover can still be exponentially large in that dimension. The dimension improvement from accuracy order minus two to minus three-halves is not claimed as a runtime exponent or an FPTAS. The retained R46 complexity proposition also identifies saturation, one response type, and fixed command budget as positive regimes; fixed-budget catalog enumeration is polynomial for each fixed budget, not fixed-parameter tractability in that parameter.

**Locations:** Sections on exact types, two-sided decomposition, adaptive target boxes, certified response coarsening, and harmonic pooling; Theorems r46-box, r46-adaptive, r47-variable, and r48-scheme; the theorem-level provenance table.

## 2. What is new beyond classical interval dynamic programming

**Referee concern: the conditional recurrence is useful but too modest as a centerpiece.**

We preserve the conditional recurrence as an exact oracle and identify the saturated charged-catalog result as an R42 antecedent. We do not claim interval dynamic programming, branch-and-bound, harmonic means, Jensen's inequality, or the scalar inequalities between means as new.

The structural increments are the eligibility-aware two-sided target-box support, the minimum-cap guard required for optimism without infeasible commands, and the original-contract recovery. R48 proves that harmonic pooling dominates the earlier minimum-curvature relaxation for the same partition. The proof aggregates terminal reward and intermediate service separately; simply replacing each individual cost by the harmonic mean would not be a valid pointwise argument. The harmonic curvature is the largest uniform quadratic lower cost for unrestricted pooled service, while cap feasibility is separately enforced in recovery. This distinction is explicit in the theorem and in the tight-cap examples.

The optimal within-group lift preserves the selected book and each reduced group mean, uses the original individual caps and costs, and has independently verifiable supporting prices. Its loss is controlled by the clipping comparison policy. These ingredients connect a classical pooling inequality to the constrained joint design problem; they are not a claim that a familiar scalar inequality is an optimization novelty by itself.

**Locations:** Theorems r48-harmonic and r48-lift, Lemma r48-square, and the discussion of classical antecedents in the introduction.

## 3. Scalable guaranteed joint computation and stronger large-history certificates

**Referee concern: the large experiments are conditional at ideal targets and do not test joint target choice.**

The retained R46 and R47 experiments use globally valid target-box or prefix bounds, not only a conditional frontier. R47 records original-space intervals on 24 distinct-history instances, including 256 distinct response types; it independently checks both the reduced global upper bound and the recovered original policy. Its clustered synthetic distribution and the stronger prefix outcomes on some antecedent cases remain stated.

The R48 paired study tests harmonic and minimum-curvature models on exactly the same cap/eligibility groups, catalog, charges, promise, budget, node limit, and price-refinement count. All 48 paired certificates are checked. Harmonic pooling achieves the original tolerance 0.001 on 14 of 24 cases; minimum-curvature pooling does so on 11. Ten harmonic cases remain unresolved, with largest original-space gap about 0.03160. They are retained, not treated as successful merely because a reduced solve completed. At the twelve primary all-book references, harmonic reduced optima are never larger and are strictly smaller in five cases.

A tighter reduced optimum does not imply every independently interrupted upper bound or runtime is better. The manuscript explicitly reports this distinction and permits taking the minimum of valid upper bounds and the maximum of feasible original values. Cap dispersion can dominate even after cost pooling is strengthened. Rational harmonic denominators and exact within-group recovery can also increase runtime. These outcomes delimit the mechanism rather than being suppressed by a success-only summary.

**Locations:** Joint computational evidence; Table r48-paired; Computational Reproduction Record, complete paired outcomes and raw certificate paths.

## 4. Testing the guaranteed method and separating heuristics

**Referee concern: the target-net tests are tiny and the 35/36 and 36/36 statements describe a heuristic portfolio.**

The complete target grid remains a baseline with explicit exponential dependence, completion checks, wall time, catalog and budget sizes, and scale-dependent accuracy. The R46 study compares its completed and interrupted runs against adaptive joint design, priced-prefix search, and exact references. These results and their failures remain intact; they are not pooled with R48 timing.

The previous heuristic exact-hit counts are not the new empirical headline. The current headline is an original-space interval checked independently of the optimizer. “Safeguarded exact in sample” remains a sample descriptor, not a theorem. The conditional scaling table is explicitly marked “targets fixed.” The adaptive candidate pool that includes exact ideal targets remains an oracle-candidate sanity check, not a universal adaptive-grid result.

The new cost-heterogeneity study is a targeted, locally specified ablation, not an externally preregistered holdout or field sample. The manuscript does not claim that twenty-four constructed cases establish universal runtime superiority. The complete generator, instance list, metrics, failed tolerances, and exact reference scope are supplied.

## 5. Independent comparisons and numerical provenance

**Referee concern: successful MIP containment alone is inadequate; report runtimes, nodes, errors, and limits.**

The retained R46 and R47 comparisons already provide matched baseline tables. R48 adds twelve primary original-model comparisons, each solved with tangent and secant envelopes: 24 direct mixed-integer solves. The formulation retains activation and support indicators, branch probabilities, pre-draw service, the root equality, individual caps, and realized-support implications. It does not use harmonic reduction or the canonical allocator.

Every case reports status, measured time, node count, primal--dual gap, quadratic-envelope approximation error, and signed bracket width. All final local solves completed; the protocol still retains any limit status in a reproduction. All-book references are independent of target search but share the exact fixed-book allocator; that limitation is stated. The MIP formulation is separate, but its floating-point bounds are not exact rational proofs. The exact certificates carry the mathematical guarantee.

An initial authoring execution used the older wrapper without node counts. The final metric pass uses the retained R46 node-accounting wrapper on the same instances and limits. Local measurement records identify their toolchain; publication measurements or verification replays must not silently overwrite those timing claims.

**Locations:** Computational Reproduction Record, independent numerical comparisons; PROTOCOL.json, results/mip.json, and certificate check outputs.

## 6. Inexact supports, local bounds, and policy recovery

**Referee concern: an inexact endpoint routine must supply certified global bounds and a bracket; its compression penalty can be large.**

Those assumptions remain explicit. We do not infer price monotonicity from approximate solutions, invent a call bound, or hide the compression term. The inexact-support theorem remains a conditional certificate-composition result. The main joint guarantee instead uses exact rational target-box supports and a complete checked cover. Its recovered policy must satisfy the original tolerance, including aggregation loss.

The Jensen and interpolation certificates remain useful comparison tools, with their catalog, headroom, charge, and scale assumptions. They are moved intact to the companion rather than used as substitutes for joint optimization. Harmonic relaxation supplies an additional target-sensitive global upper model. Its loss formula separates cap transport and the arithmetic--harmonic cost gap; the observed interval, not only the worst-case defect, determines completion. The upper-model dominance is proved even when the displayed uniform defect happens to be larger than the previous minimum-curvature bound.

## 7. Operational interpretation and resource accounting

**Referee concern: no independent application calibration is supplied, and command bits are not the entire implementation memory.**

The paper retains the restricted-interface institutional model and its original expected/pathwise distinctions. The command budget describes installed executable symbols, not all physical storage. The history encoder, public-state table, read-only constants, cap table, probabilities, and offline certificates remain separately accounted for. Coarsening does not erase the original history-indexed policy or make its implementation data free.

The new results address an operationally relevant distinction within the stipulated model: pooled low cost is not unlimited cheap capacity. Optimal original-group recovery and retained tight-cap failures expose that difference. No measured customer population, estimated level-opening charge, deployment result, or calibrated cap distribution is fabricated. The contribution rests on the explicit optimization model and proved algorithmic regime. Translating it into a calibrated application requires independently supplied operational data; synthetic numerical checks are not represented as such data.

## 8. Organization, length, and preservation

**Referee concern: the cumulative breadth obscures the strongest joint result.**

The article leads with canonical allocation, the conditional oracle, exact types, two-sided joint bounds, and controlled history reduction. R48 harmonic pooling and the paired experiment then strengthen that main argument. The theorem map distinguishes R42, R43, R45, R46, R47, and R48 contributions.

The Jensen/interpolation section and a resource appendix move intact from the article to the companion. The complete R46 and R47 computational narratives and protocols move intact to a separately named repository Computational Reproduction Record, alongside full new per-case metrics. These are relocations, not deletions or renamed new experiments. All 49 antecedent mathematical labels remain in the current article or companion, with four additional results. Predecessor sources and PDFs, historical derivations, reviews, and prior branches remain intact.

The current local build has 39 nonreference article pages, a 37-page companion, an equation-free introduction, an anonymous title page, an abstract of 180 words, one-and-a-half spacing, 11-point text, one-inch margins, author-year references, and horizontal-rule tables placed after references. The reproduction record is separately identified as repository implementation evidence, not silently merged into the journal companion. The validation script checks actual builds rather than inferring compliance from source intentions.

## 9. Implementation and minor comments

**Comments 1–3: one-branch net, genuine clipping, and independent coverage.** R46 contains the one-branch shortcut and nontrivial clipping/coverage checks. R48 additionally verifies harmonic representatives, cap clipping comparison policies, exact group masses, supporting prices, and the original lotteries. Its independent checker imports neither harmonic reduction nor the optimizer. Fourteen new semantic mutations are rejected, including altered means, missing histories, false upper values, inconsistent group prices, and invalid probabilities. The antecedent complete target-cover checker remains in use.

**Comments 4, 7, 13, and 16: runtime, dimensionality, catalog scope, and normalization.** The retained grid table includes time and completion. Finite-catalog scope is explicit in the abstract and theorems. Accuracy complexity is stated directly, with no FPTAS claim. The new table distinguishes reduced dimension from runtime and records the objective scale. Additive tolerances must scale with rewards, costs, and charges; dividing by a possibly negative optimum is not a valid normalization.

**Comments 5 and 14: antecedent contributions.** The saturated recurrence is identified as an R42 antecedent, the unrestricted priced path as R43, and the full target net as R45. The current theorem map separately identifies R46 two-sided bounds, R47 guarded coarsening, and R48 harmonic pooling. Their source histories are preserved.

**Comments 6, 8, 9, 11, and 12: title, sample exactness, counterexample, candidate pools, and conditional results.** The title now names harmonic coarsening and certified joint design. Certification refers to checked original-space intervals, not a heuristic's hit rate. The retained historical tables mark safeguarded exactness as sample-only, disclose the charged counterexample and objective scale, mark ideal-target candidate insertion as a sanity check, and label conditional timings “targets fixed.” These distinctions are not erased when moving the narrative to the reproduction record.

**Comments 10 and 18: numerical MIP diagnostics.** Every new primary case includes both envelopes, times, nodes, gaps, errors, and bracket width. Solver messages and any limit outcomes are retained. Numerical MIP bounds are never called rational certificates.

**Comment 15: selected versus used cardinality.** The budget counts installed distinct levels and their charges, whether or not a selected zero-charge level receives positive probability. Exact-cardinality frontiers can therefore contain unused selected levels. Original policy checks enforce the installed-level budget; an at-most-budget optimizer need not purchase an unnecessary charged level.

**Comment 17: aggregation before global search.** Exact type aggregation remains available, but R47 and R48 also group genuinely distinct histories while preserving eligibility and the minimum-cap guard. The theoretical bin count and the actual practical group count are reported separately. Square-root bins reduce the cost-dimension bound without assuming repeated histories or a positive minimum curvature.

## Closing statement

The revised submission preserves the original problem and contribution scope while replacing the full-grid-only joint argument with a structural, checkable decomposition and controlled dimension reduction. R48 provides a provably stronger relaxation, optimal original-group recovery, and an improved accuracy-dependent dimension bound. It also retains the cases where those improvements are insufficient at the chosen coarse partition. We submit the complete manuscript, companion, computational record, source, tests, and certificates for a new independent assessment; we do not equate successful validation with an editorial acceptance claim.
