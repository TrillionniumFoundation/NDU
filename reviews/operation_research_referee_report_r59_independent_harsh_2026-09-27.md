# Independent Referee Report on R59

**Manuscript:** *Finite-Catalog Resource Allocation: Exact Path Representations and Menu Complexity*  
**Journal standard applied:** *Operations Research*, regular manuscript  
**Reviewed source branch:** `revision/ndu-operations-research-r59-parameterized-deficit-20260927`  
**Reviewed source commit:** `87c3988525e25527c7b3c5f1d731ceb101144f58`  
**Source tree:** `ff583ae09b9f59e1725342c2f0c41bb2aecccd3c`  
**Review date:** 2026-09-27  
**Recommendation:** **Reject and Resubmit**

---

## 1. Executive assessment

R59 is a serious and substantive revision. It is not a cosmetic response to the previous report. The authors have added a genuine original-model parameterized lower bound, a mathematically exact mixed-integer convex comparator, an explicit infeasibility preflight, a more disciplined computational protocol, a cap-preserving prototype-selection problem, a recognizable conservative-path abstraction, and a substantially cleaner article. They have also repaired the exact-head publication chain: the reviewed source commit carries a successful `ndu-r59/exact-head-verification` status, and the current code-and-data package has a direct, inspectable layout.

The strongest new result is Theorem 5.1: W[1]-hardness of the rational finite-catalog decision problem parameterized jointly by command budget and the number of distinct expected caps, with the two parameters equal in the reduction. I audited the group-sum construction, the no-carry multicolored-clique encoding, the renewal embedding, the threshold arithmetic, the baseline-forcing argument, and the command-count accounting. I did not find a fatal logical defect in that reduction. The result materially closes the most important complexity gap in R58: the paper can no longer be read as confusing an XP enumeration bound with fixed-parameter tractability.

I also did not identify a fatal correctness error in the conservative-path potential theorem, the complement-coordinate repair argument, the heterogeneous component-packing construction, the cap-preserving one-dimensional medoid dynamic program, or the mathematical mixed-integer convex formulation. This statement is an independent referee assessment, not a formal verification or a guarantee that every proof detail is beyond dispute.

Nevertheless, R59 still does not meet the publication bar of *Operations Research*. The remaining problem is no longer primarily correctness or reproducibility. It is the hierarchy, significance, and empirical support of the contribution:

1. the W[1]-hardness theorem is real and useful, but the rest of the claimed general theory is closer to a careful synthesis of potential-based path conservation, resource scaling, separable allocation, and one-dimensional medoid machinery than the paper currently admits;
2. the broader conservative-path theorem is a sufficient abstraction, but its recognition component is mathematically elementary and its relationship to the bounded-path problem is not stated with enough precision;
3. the new computational study does not validate the deficit method as an attractive practical algorithm—on the authors' own panel, price search supplies 71 of 72 rationally certified targets, whereas the deficit method supplies only 5 of 72 and misses the end-to-end deadline 17 times;
4. the study remains a small deterministic synthetic engineering panel with one short time budget, repeated underlying model specifications, no standard benchmark family, and no operational data;
5. the related-work section is much improved but still too thin and too category-level for a paper whose novelty depends on fine distinctions from resource-constrained shortest paths, restricted shortest-path approximation, fixed-charge support design, separable resource allocation, clustering, and parameterized knapsack-type problems.

I therefore recommend **Reject and Resubmit**, rather than a routine major revision. The paper now contains publishable ideas, but addressing the remaining issues requires a new scientific and narrative center, not merely local corrections. I would be willing to review a substantially reconstructed resubmission.

---

## 2. Referee scorecard

| Dimension | Assessment | Comment |
|---|---:|---|
| Technical correctness | 4/5 | No fatal flaw found in the new central reduction or main reconstruction arguments; several scope and presentation qualifications remain necessary. |
| Originality | 3/5 | The original-model W[1]-hardness result is a genuine advance; several surrounding components are standard or elementary adaptations. |
| Significance for OR | 2.5/5 | Potentially meaningful, but the decision relevance and generality are not yet commensurate with the breadth of the article. |
| Algorithmic contribution | 2.5/5 | Strong certification architecture and a valid additive scheme; the nominal centerpiece performs poorly on the submitted panel. |
| Computational evidence | 2/5 | Honest and reproducible, but too small, too dependent on one generator and one time limit, and not designed to support general algorithmic conclusions. |
| Exposition | 4/5 | Considerably clearer and more focused than R58; the contribution hierarchy remains overloaded. |
| Reproducibility | 5/5 | Exceptional source, result, certificate, preservation, and exact-head discipline. |
| Overall | Reject and Resubmit | Good ideas are present, but there is not yet a clear, routine path to acceptance. |

---

## 3. What R59 successfully resolves

### 3.1 The XP-versus-FPT gap is now addressed

Theorem 5.1 is the most important improvement. The reduction consumes the actual command budget: the zero anchor and all group baselines are forced into every threshold-achieving book, leaving exactly one optional command per group. This avoids the central weakness of a nonbinding-budget subset-sum reduction. The construction remains inside the stated renewal model and retains a fixed linear reward, free service, uniform positive history probabilities, ceilings equal to caps, and nonnegative rational opening charges.

The proof's arithmetic is coherent. With \(m=2g+1\), the zero command and \(g\) forced baselines consume \(g+1\) slots, the threshold equality forces \(S(c)=W\), equality in the capacity bound excludes multiple positive options from one group, and the no-carry group digits force one option from every group. Because \(m=q_b=2g+1=O(r^2)\), the reduction is parameter preserving. The manuscript also correctly refrains from claiming W[1]-membership, strong NP-hardness, a sharp exponent lower bound, or hardness under uniform positive charges.

This result should remain the principal theorem of any resubmission.

### 3.2 The direct comparator now models the original semantics

The mixed-integer convex formulation uses a history-level pre-draw service variable and terminal-command probabilities, with binary linking variables enforcing the realized ceiling. The big-\(M\) value is sufficient to make an unused command constraint redundant and an active command constraint exact. The formulation is mathematically equivalent to the quadratic original model; no piecewise-linear service envelope remains.

The implementation also distinguishes a numerical solver bound from a rationally reconstructed feasible policy. This is an important improvement over earlier versions. The manuscript does not call a floating-point SCIP status an exact rational proof.

### 3.3 Infeasibility is no longer hidden behind an incumbent convention

The preflight condition for a well-formed nonempty catalog is stated explicitly: \(m\ge 1\), \(0\le B\le \bar b\), and the smallest command does not exceed either the promise or any history cap. The singleton-and-service sufficiency argument is valid. The associated record contains a failed inequality and input digest rather than a fabricated policy or finite objective interval.

### 3.4 The negative screening result is reported honestly

The manuscript retains the unfavorable matched result: screening improved total end-to-end time in none of the 18 earlier pairs, with a median ratio around 1.604. It no longer presents a safe fixing rule as an empirically validated acceleration. This is exactly the distinction an OR paper should make between a correct reduction and an economical preprocessing decision.

### 3.5 The release and exact-head discipline are now strong

The current manuscript, companion, response, frozen inputs, row-level records, certificates, independent checkers, source hashes, and preservation map are all present. The final reviewed source commit—not merely an earlier build commit—has a successful read-only verification status. This resolves the previous exact-head qualification objection. The repository engineering is now a strength, although it cannot substitute for scientific significance.

---

## 4. Major concerns that still block publication

### 4.1 The paper still lacks a disciplined contribution hierarchy

The article currently asks one manuscript to carry all of the following:

- exact elimination of history-level lotteries and realized ceilings;
- a selected-path representation;
- a potential/capacity-conservation characterization on acyclic graphs;
- a source-independent deficit coordinate;
- a resource-grid additive approximation and exact repair;
- a heterogeneous reward packing theorem;
- W[1]-hardness in menu size and cap count;
- exact cap-count compression and inherited exact regimes;
- a cap-preserving prototype-selection problem;
- a one-dimensional weighted-median dynamic program;
- price-based exact certificates;
- a mixed-integer convex comparator;
- screening, proof checking, and publication infrastructure.

This breadth is not itself a contribution. It makes it difficult to determine what the paper is asking an *Operations Research* reader to remember. The strongest item is the original-model W[1]-hardness theorem. The exact model-to-path representation is also valuable. By contrast, the potential-recognition result, the generic resource-grid rounding argument, and the common-curvature grouping dynamic program are much closer to standard tools once the model has been reduced.

The paper should be rebuilt around one of two credible spines:

1. **A complexity-frontier paper.** Make the exact model reduction and parameterized lower bound central, add a sharper positive/negative frontier, and use computation only to illustrate the regimes predicted by that frontier.
2. **A decision-support paper.** Retain the exact representation but add a credible operational instance or benchmark family, develop a competitive hybrid solution strategy, and demonstrate why the menu-opening decision changes decisions or cost in a practically relevant range.

The current manuscript attempts both routes and fully completes neither.

### 4.2 The W[1]-hardness theorem is meaningful, but the frontier is still incomplete

Theorem 5.1 is valid enough to deserve publication consideration, but a top-journal complexity contribution should do more than establish one lower bound and juxtapose it with inherited XP and pseudo-polynomial algorithms.

At minimum, a resubmission should:

- state the parameterized decision problem formally in one place, including the rational threshold, binary encoding, and yes/no language;
- distinguish clearly between parameterization by \(m+q_b\), by \(m\), and by \(q_b\), rather than placing the two single-parameter consequences in one sentence;
- explain precisely how equality of rational caps defines \(q_b\) and how duplicate caps are represented in the input;
- compare the reduction with parameterized grouped-sum, multiple-choice knapsack, fixed-charge support-selection, and related packing constructions;
- state what remains open: W[1]-membership, ETH-style exponent lower bounds, strong NP-hardness, uniform-charge hardness, bounded-denominator complexity, and kernelization;
- provide at least one additional positive structural regime that is not simply “enumerate for fixed \(m\)” or “run a pseudo-polynomial grid in a numerical denominator.”

I am not requiring the authors to solve every open item above. I am requiring a sharper theorem-level frontier. A natural route would be an FPT result under an additional economically interpretable parameter, a dichotomy for charge/cap structure, a lower bound under coarser numerical encoding, or a proof that a proposed strengthening is impossible. Without such a counterpart, the W[1] result remains somewhat isolated from the rest of the paper.

The authors should also be careful about the operational interpretation of the hardness construction. The construction deliberately uses fine rational scales. That is legitimate for binary-encoded complexity, and the manuscript says so. It does not by itself demonstrate hardness in a naturally discretized service system. The paper should keep those two claims separate.

### 4.3 The conservative-path generalization is sound but currently over-positioned

The equivalence between path-independent capacity sums and a suffix potential \(H_v\), with \(C_{uv}=H_u-H_v\), is correct. The reverse-topological recognition procedure and the two-path witness are also correct. However, this is a short path-independence/potential argument, not by itself a major new OR theory contribution.

There is also an important scope nuance. The abstract decision problem permits paths of at most \(h\) edges, whereas Theorem 4.1 recognizes equality of total capacity over **all** source-to-sink paths in the retained graph. Therefore the theorem identifies a clean sufficient class for the length-bounded problem. It is not a necessary characterization of equality over only the \(h\)-admissible paths: longer paths may violate conservation while every admissible short path still has the same capacity. The current prose should say this explicitly. Alternatively, the authors could develop a length-aware recognition result, with the state augmented by path length, and state its complexity and witness structure.

The additive approximation theorem is also useful but must be positioned carefully. Its running time is polynomial in the numerical grid size \(Q\), not in \(\log(1/\varepsilon)\) or necessarily in binary input length. The manuscript already says this, but the abstract and contribution table can still leave a stronger impression. The result is a pseudo-polynomial additive scheme with exact equality repair on the chosen path, not a general FPTAS for the abstract class.

The broader-class claim would be more convincing if the paper supplied at least one nontrivial non-renewal model whose exact primitives lead to the stated conservative paths and whose decisions are substantively interesting. The current modular-allocation sentence is an illustration, not an application. Without such an example, the generalization reads as an abstraction extracted from the proof rather than a demonstrated reusable OR model class.

Finally, the related-work discussion must compare this theorem and algorithm directly with the modern resource-constrained and restricted shortest-path literature. The manuscript cites classic foundations, but does not engage with the last decade of exact labeling, bidirectional search, bucket-graph methods, primal adjacency, multiphase dynamic programming, or modern benchmark practice. Relevant starting points include the survey by Di Puglia Pugliese and Guerriero, the exact RCSP work by Ahmadi and coauthors, the bucket-graph labeling work by Sadykov, Uchoa, and Pessoa, and recent exact acyclic SPPRC algorithms. Merely classifying all of these as “constrained paths” in one table is not enough.

### 4.4 The submitted computational evidence undercuts the deficit algorithm

The main computational table is unusually honest, but its results do not support the algorithmic narrative currently attached to the deficit method.

Under the common three-second end-to-end allowance:

| Method | Checked outputs | Rationally certified target | Numerically certified target | Median total time | Deadlines |
|---|---:|---:|---:|---:|---:|
| Price search | 72/72 | 71/72 | 0 | 0.339 s | 0 |
| Deficit | 55/72 | 5/72 | 0 | 1.852 s | 17 |
| Enumeration | 72/72 | 12/72 | 0 | 1.827 s | 0 |
| SCIP | 72/72 lower-policy checks | 0 | 72/72 | 0.527 s | 0 |

The numerical SCIP bound is not a rational certificate, and the authors correctly separate those columns. Even with that qualification, the deficit algorithm is not competitive on the submitted panel. It certifies the requested rational tolerance in only five cases and fails to complete within the total budget in seventeen. Price search is both faster and dramatically more successful in rational certification. This is not a minor implementation issue that can be hidden by emphasizing a worst-case bound.

A resubmission must choose one of two honest responses:

- **Recast the deficit algorithm as a structural worst-case guarantee**, not the practical centerpiece. Center the implementation around price search and the exact convex formulation, explain when the grid method is the only applicable guarantee, and identify the instance features that trigger that regime.
- **Redesign the deficit implementation and evidence** so that it has a demonstrated domain of advantage. This would require more than changing a state limit or increasing the time budget; the paper must explain the mechanism producing the advantage.

The study design also needs substantial expansion and correction of terminology:

1. The 72 method-level “instances” contain only 56 distinct model specifications. The `base`, `accuracy20`, and `accuracy500` cells reuse the same eight underlying models and vary only the requested tolerance. These are useful tolerance requests, but they should not be counted as 24 independent structural instances.
2. Eight seeds per one-factor cell are too few for broad performance conclusions.
3. The single three-second budget measures one operating point. Performance profiles or target-attainment curves over multiple budgets are needed.
4. Aggregate medians hide the effects of catalog size, number of histories, command budget, tolerance, cap count, joint type count, and probability denominator. The paper should report outcomes by family and model those drivers.
5. Rationally certified global intervals and numerical SCIP global bounds are different evidence objects. They should be shown in separate primary panels before any cross-method summary.
6. Proof size, serialization time, checker time, and optimization time should be reported by quantile and family, not only through conditional medians.
7. The paper needs either a standard benchmark translation or a credible application-derived family. A deterministic in-house generator is suitable for regression testing, not sufficient for an OR computational claim.
8. The exact grouped-sum oracle is appropriate for the small challenge cases, but those cases are derived from the authors' own lower-bound construction and should not be treated as independent external validation.

The current evidence is still worth publishing as a transparent negative/diagnostic study. It simply does not establish that the deficit algorithm is an attractive decision method.

### 4.5 The literature positioning remains below the required standard

R59 expands the bibliography and explicitly acknowledges antecedent tools. That is progress. The remaining problem is depth. The theorem-level table uses broad labels—constrained paths, continuous allocation, moment support, auction menus, parameterized complexity, clustering—but does not compare assumptions, complexity, guarantees, and recoverability against the nearest results.

The resubmission should contain a genuine comparison matrix with at least the following columns:

- endogenous versus fixed path/support;
- one versus multiple resource equalities;
- binary versus numerical complexity;
- exact, pseudo-polynomial, FPT, XP, or approximation status;
- fixed charges and cardinality limits;
- source-dependent versus source-independent resources;
- feasibility recovery in the original model;
- numerical versus independently checkable bounds;
- benchmark and application evidence.

The modern constrained-shortest-path literature is the largest omission. The current paper cannot claim a meaningful path-algorithm contribution while comparing only with classic work from 1980–2001. The resource-allocation discussion should also distinguish the paper's endogenous support problem from fixed-charge and cardinality-constrained separable allocation more directly. The grouping section should be explicit that the common-curvature result reduces to weighted one-dimensional \(k\)-median segmentation and should compare with the associated dynamic-programming and Monge-optimization literature, rather than merely citing general metric \(k\)-median.

The phrase “menu complexity” also needs careful handling. The introduction now distinguishes the model from incentive-compatible auction menus, which is good. Nevertheless, the title invites that comparison. Either make the cross-literature distinction central and precise, or use “command-support complexity” or another term that better identifies the object being counted.

### 4.6 The operational significance remains hypothetical

The paper explicitly chooses a theory route and does not claim field adoption. I agree that an OR theory paper need not contain proprietary field data. But a theory route still has to demonstrate why the abstraction captures a sufficiently important and reusable decision problem.

At present, the service-credit narrative fixes the timing and feasibility semantics, but there is no evidence that real operators face the stated combination of accepted aggregate promise, history-observed command lotteries, fixed opening charges, history-independent terminal symbols, and pre-draw deterministic service. Nor is there a calibrated stylized example showing the economic magnitude of jointly choosing expected targets and a shared command catalog.

A resubmission should add at least one of the following:

- a documented application setting with defensible primitive ranges and a decision comparison against current practice;
- a calibrated or semi-synthetic case study showing when command opening costs materially change the optimal policy;
- a broader model theorem that covers multiple recognizable OR applications, each mapped rigorously into the abstract path class;
- comparative statics or structural thresholds that translate the mathematics into managerial or design implications.

The paper should not manufacture a field claim. It should either provide evidence or make the theory broad and sharp enough that the application motivation is not carrying the significance burden.

---

## 5. Detailed technical comments

### 5.1 Formalize the parameterized decision language

Theorem 5.1 refers to the “rational finite-catalog decision problem,” but the complete language should be displayed before the theorem: encoded primitives, objective threshold, feasibility convention, parameter map, and binary input length. This would remove ambiguity over whether the threshold is part of the parameter and whether exact comparison is assumed.

### 5.2 Separate the single-parameter corollaries

Because the reduction has \(m=q_b\), W[1]-hardness transfers to parameterization by \(m\) alone and by \(q_b\) alone. State these as explicit corollaries with the parameter maps. This is clearer than appending both claims to the joint theorem.

### 5.3 Clarify the status of duplicate group values

The proof says equal integers within a group can be merged. State explicitly that commands from different groups remain distinct because their baselines differ, even if the encoded integer values coincide. This is implicit and correct but worth making formal.

### 5.4 Clarify what the finite reduction tests establish

The 4,240-book tests, 51 allocation cross-checks, and 48 graph encodings are useful regression tests. They do not test the general parameterized reduction over arbitrary graph size, and they do not independently establish the theorem. The manuscript says this in general terms; the structural-test table should also list the maximum \(g\), graph size, and numerical bit length covered.

### 5.5 Make the edge-limit scope explicit in Theorem 4.1

As noted above, recognition is over all source-to-sink paths, while optimization is over paths with at most \(h\) edges. State that this is a sufficient full-graph condition. If a length-aware extension is not developed, do not call it an exact characterization of the bounded-path class.

### 5.6 Expose the kernel-oracle model in Theorem 4.2

The arithmetic count is stated “apart from kernel evaluation.” Specify what access is assumed: value oracle, piecewise-linear representation, quadratic closed form, or exact rational circuit. State the bit complexity under each representation. Otherwise the abstract complexity result can hide the dominant work.

### 5.7 Add tests for the abstract recognition and repair results

`structural59.py` tests the grouped-sum reduction and prototype frontier, but I did not find comparable randomized tests for:

- recognition acceptance on potential-generated DAGs;
- rejection and witness validation on perturbed DAGs;
- source merging with multiple sources;
- the distinction between full-graph and \(h\)-bounded conservation;
- grid rounding followed by exact-capacity repair;
- arbitrary support holes in the abstract convolution path.

These should be included if the abstract class remains a headline contribution.

### 5.8 Report the computational panel by distinct specification and by request

Use separate counts such as “56 distinct model specifications, 72 tolerance-tagged cases, and 288 method requests.” This is exact and avoids overstating independence.

### 5.9 Replace “rational target” with “rationally certified target”

The current table heading is too compressed. The distinction is not that one objective target is rational and another is numerical; it is that one target attainment is supported by an independently checked rational interval while the other relies on a numerical global bound.

### 5.10 Explain the SCIP projection step more visibly

The implementation obtains a numerical incumbent, extracts the selected book, and reoptimizes that book through the rational fixed-book allocator. Thus the checked lower policy can differ from the solver's raw continuous variables while retaining the same installed book. This is a sensible strengthening, but the main article should explain it explicitly.

### 5.11 Keep “exact formulation” separate from “exact solve”

The mathematical MICP is exact. The SCIP execution is floating point and its dual bound is numerical. The manuscript generally respects this distinction. Preserve it in every abstract, table, and response statement.

### 5.12 Explain why the price method is so successful

Price search branches in only 7 of 72 cases, with maximum recorded depth 16. This is one of the most interesting empirical facts in the study, yet it is not analyzed. Which structural conditions make the supporting-price bound exact or nearly exact? Can this be proved for a broader class? A theorem or diagnostic model explaining the observed success would be more valuable than treating price search merely as a comparator.

### 5.13 Reconcile the algorithmic hierarchy

The article currently presents the deficit method as the general additive guarantee, price search as a certificate method, enumeration as a baseline, and SCIP as a numerical comparator. The data suggest a different hierarchy: price search is the practical rational method on this panel, SCIP is the practical numerical method, and the deficit method is a worst-case fallback. The text should follow the evidence.

### 5.14 Avoid using repository engineering as a scientific contribution

The source freeze, digest binding, exact-head status, certificate checking, and preservation map are excellent research practice. They should remain available but occupy little main-text space. They are evidence for the claims, not one of the paper's mathematical contributions.

### 5.15 Produce a self-contained archival submission tree

The current build correctly records dependencies on retained R52–R58 source files. For an editorial resubmission, also produce a clean, self-contained source tree containing the current manuscript and companion without requiring readers to infer which historical revision paths are normative. Preservation copies can remain elsewhere in the repository.

---

## 6. Required changes for a credible resubmission

A resubmission should not merely append another theorem and a larger timing table. I would expect the following package.

### Required scientific changes

1. **Choose and enforce one contribution spine.** The recommended route is the exact representation plus the parameterized complexity frontier.
2. **Deepen the frontier.** Add at least one meaningful positive regime, stronger lower-bound qualification, or structural dichotomy, and compare directly with the nearest parameterized packing/support-selection results.
3. **Narrow or strengthen the conservative-path claim.** Clarify the role of the edge limit, position the potential theorem honestly, and either add a nontrivial reusable application or reduce its prominence.
4. **Reframe or materially improve the deficit algorithm.** The submitted evidence cannot support it as the practical centerpiece.
5. **Explain the success of price search.** This is the most promising bridge between theory and observed computation.
6. **Strengthen decision relevance.** Add an application-derived case, a rigorous multi-application mapping, or substantive comparative statics.

### Required literature changes

7. Replace the category-level antecedent table with theorem- and guarantee-level comparisons.
8. Add modern exact and approximate resource-constrained shortest-path work, fixed-charge/cardinality-constrained allocation, and the relevant parameterized grouped-selection literature.
9. Position the one-dimensional prototype dynamic program as an application of weighted line clustering unless the authors prove a genuinely new algorithmic result.

### Required computational changes

10. Report distinct specifications, tolerance requests, and method requests separately.
11. Add multiple time budgets, per-family results, performance profiles, proof-size/checking-cost distributions, and explanatory regressions or stratified summaries.
12. Include an external benchmark translation or a defensible application-derived family.
13. Separate rational-certification and numerical-bound panels before presenting any joint summary.
14. Preserve all failures and negative results exactly as R59 does; do not tune away the unfavorable cases.

### Required reproducibility changes

15. Preserve the current exact-head, source-freeze, row-level evidence, and independent-checking discipline.
16. Add abstract-path recognition/repair regression tests and a clean self-contained current-source snapshot.

---

## 7. Minor and editorial comments

1. The journal name is *Operations Research*, not “Operation Research.”
2. The revised title is better than the earlier small-menu title, but “menu complexity” still risks confusion with incentive-compatible auction menus.
3. The abstract should identify the W[1]-hardness result as parameterized complexity, not merely “hardness,” and should call the approximation pseudo-polynomial in its resource grid.
4. In the introduction, distinguish “representation theorem,” “complexity theorem,” “approximation theorem,” and “computational method.” They currently blend into one three-part narrative.
5. The phrase “linear-time recognition” should specify arithmetic-operation complexity and the rational bit-cost assumption.
6. In the grouping section, state whether ties among weighted medians affect only the selected prototype or also the backtracking convention.
7. The theorem-level comparison table should include formal citations in each row.
8. The computational tables should report denominators for every rate and use consistent capitalization of SCIP.
9. Conditional checking-time medians should remain labeled conditional; add unconditional end-to-end quantiles.
10. Report the maximum uncompressed and compressed certificate sizes, not only row-level availability.
11. The exact grouped-sum challenge family should be labeled “construction-derived challenge family.”
12. State the number of distinct input hashes in the main computational section.
13. The conclusion should not give the deficit method equal practical prominence to price search unless the evidence changes.
14. Replace “rational target” throughout with “rationally certified target.”
15. Update preprint citations to final published versions where available and ensure that the bibliography contains the nearest modern algorithmic work, not only foundational references.

---

## 8. Recommendation to the editor

R59 has crossed an important threshold relative to R58. It now contains a credible central theorem, a coherent exact model reduction, an honest negative computational story, and unusually strong reproducibility. I would not recommend rejection without invitation to return.

I nevertheless do not recommend Major Revision. The missing work is not a bounded list of repairs. The authors must decide what the paper is fundamentally about, deepen or narrow the theory accordingly, rewrite the literature positioning, and either redesign the computational contribution or openly demote the deficit method to a worst-case guarantee. Those changes are likely to alter the title, introduction, theorem hierarchy, experiments, and conclusion.

**Final recommendation: Reject and Resubmit.** A substantially reconstructed paper centered on the exact representation and a sharpened parameterized complexity frontier could become a strong contribution. The present R59 is not yet at the *Operations Research* acceptance standard.
