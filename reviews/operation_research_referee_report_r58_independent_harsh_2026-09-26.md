# Confidential Referee Report for *Operations Research*

**Manuscript:** *Finite-Catalog Renewal Design: Small Menus and Resource-Deficit Paths*  
**Revision reviewed:** `revision/ndu-operations-research-r58-structural-referee-20260926`  
**Audited revision tip:** `1edd6d929e20f50a14ec6ef9beab4a37fa44fe39`  
**Readable-source parent:** `debd4dfa4053cf5f3d6fcf06633b749ef6144ed6`  
**Last complete scientific predecessor:** R54, `eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9`  
**Governing prior report:** `review/operation-research-r56-independent-harsh-20260926`, report commit `1bf0400f3540605d2ac68d2a40e8bcfb377d5446`  
**Review branch:** `review/operation-research-r58-independent-harsh-20260926`  
**Date:** September 26, 2026  
**Recommendation:** **Reject in the present form, while encouraging a substantially refocused resubmission. R58 is a genuine, complete, and unusually well-audited scientific revision. I do not see an immediate counterexample to the new cap-count compression theorem, joint cap--reward compression, oscillation loss bound, merged-origin deficit identity, centered additive guarantee, zero-service lattice theorem, or saturated-promise frontier. The principal obstacle is no longer basic correctness or repository completeness. It is the publication threshold for *Operations Research*: the operational problem remains hypothetical and narrowly structured; the bibliography and novelty positioning are far too thin; the new tractability results are XP, pseudo-polynomial, perturbative, or boundary-case results rather than a decisive complexity or algorithmic breakthrough; exact global search remains exponential; and the new computational evidence is small, entirely synthetic, based on weak comparators, and in an important case affirmatively unfavorable—screening improves total time in 0 of 18 matched pairs and increases median total time by about 60%. These deficiencies require a new scientific positioning and study, not a routine revision.**

---

## Executive assessment

R58 corrects the most basic defect identified in the R56 report: there is now an actual manuscript to review. The branch contains a current article, electronic companion, response to referees, source-frozen code, declared inputs, raw records, certificates, independent checkers, generated tables, build validation, preservation records, and a self-contained code-and-data archive. The root readers identify and assemble R58 rather than silently serving R54. Reviewer-output commits were not merged into the author-revision delta. This is a meaningful and necessary improvement in scientific hygiene.

Scientifically, R58 also makes real progress. The paper now gives a tight `2q` command bound in the number of distinct expected caps under a common reward; extends conditional compression to finitely many joint cap--reward types; derives an oscillation-based loss guarantee for approximate reward types without changing feasibility; complements the selected-boundary resource coordinate to merge all anchors into one deficit dynamic program; reduces the catalog factor in the additive scheme; proves an exact pseudo-polynomial zero-service lattice regime; and isolates a saturated-promise regime in which all command-budget frontiers can be computed in one count-indexed pass. The heterogeneous deficit implementation and independent certificate checker are now present rather than promised.

I audited the mathematical statements and proofs, the source implementations, the independent checkers, the generated claims, the source/evidence manifests, and the workflow history. I also performed an external reproduction check described below. I found no fatal mathematical contradiction. The revision is therefore materially stronger than R54 and should not be rejected on the ground that the branch is empty, the paper is misidentified, or the principal theorems are obviously false.

That conclusion does not imply that the manuscript meets the bar of *Operations Research*. The paper currently combines a highly specialized hypothetical renewal-credit model, a long sequence of exact identities, several narrow tractability islands, classical Lagrangian and dynamic-programming machinery, and extensive artifact engineering. The manuscript has not demonstrated that this particular combination resolves an important operations problem, establishes a sufficiently broad methodological theorem, or produces a solver with a compelling advantage. Its current evidence instead shows a technically credible but fragmented theory project whose practical and disciplinary importance remains unestablished.

My recommendation is therefore rejection with encouragement to resubmit only after a major scientific re-conception. The authors should choose whether this is primarily a theory paper about a broad class of endogenous-support resource paths or an operations paper about a real service-design decision. The present manuscript tries to be both, and does not yet satisfy the strongest standard in either direction.

---

# 1. Version, build, and evidence audit

## 1.1 The reviewed object is a genuine revision

The audited tip is `1edd6d929e20f50a14ec6ef9beab4a37fa44fe39`. The current root `main.tex` assembles the R58 title, abstract, model, selected-boundary construction, complexity results, menu-compression results, price paths, deficit paths, computational evidence, and conclusion. The root `main.pdf` and `electronic_companion.pdf` are the corresponding current readers.

The R58 build record reports:

- 38 total article pages and 37 nonreference pages;
- a 30-page electronic companion;
- a six-page response to referees;
- a 188-word abstract;
- no undefined references or citations;
- no duplicate labels;
- no overfull boxes;
- and a `Lengthy manuscript` submission classification.

The current package declares 225 timed method records, 24 additional approximate-type comparisons, 168 saturated-budget certificates, and retained failures and state limits. The repository records a successful publication workflow, GitHub Actions run `36251828767`, whose structural regressions, 225-run execution, extended verification, table generation, reader build, and package checks all completed successfully.

## 1.2 Independent reproduction performed for this review

I did not merely accept the committed `PASS` labels. I downloaded the 35 MB workflow artifact `ndu-or-r58-referee-package` (artifact `10909752362`) into a separate work directory and performed the following checks.

1. I independently reran `tests56.py`. It passed 200 arbitrary-support convolution comparisons, 36 general models, 36 lattice models, 36 cap-compression models, four tight constructions, the 20,000-bit rational serialization case, the oversized-state rejection, and seven certificate-corruption classes.
2. I reran the 36 joint cap--reward regressions. They passed.
3. I reran the checker-import audit. The public checkers did not import the optimizer modules.
4. I reran the R58 structural suite. It passed 24 approximate-type models, all 168 saturated-budget certificates, and 48 expected rejection tests.
5. I extracted the nested `CODE_AND_DATA.zip` into a clean directory and ran `release58.py verify`. It reported: `Release verification PASS: source, reader graph and all 225 declared records`.
6. I independently dispatched representative price, deficit, lattice, enumeration, and screening certificates through `check_certificate56.py`, supplying the external instance digest. All five were accepted by the appropriate checker. The large heterogeneous deficit certificate required approximately 22.6 seconds to verify, consistent with the paper's warning that proof checking can substantially exceed optimization time.
7. Separately, I compared the implemented arbitrary-hole max-convolution routine against exhaustive convolution on many randomized small concave kernels with arbitrary finite support holes. I found no discrepancy.

I did not rerun all 225 timed optimization jobs from scratch. Repeating the same frozen timing campaign on another shared environment would not by itself establish external performance validity. I instead verified the complete source-bound record set, reran the theorem regressions, and rechecked representative certificates.

## 1.3 Two reproducibility qualifications remain

First, the top-level workflow artifact is not itself a directly self-contained checkout. Running `release58.py verify` at the artifact root fails because inherited R52--R54 source paths are absent there. The nested `CODE_AND_DATA.zip` is self-contained and does pass. This is not a scientific failure, but the artifact advertised for referees should either be flattened or explain immediately that the inner archive is the reproducible object.

Second, the successful workflow was triggered at source SHA `3394e38c...`, then generated and pushed later commits, including the reviewed tip, using `[skip ci]`. The workflow log and manifests bind the production sequence, but the exact final tip has no combined GitHub status attached to it. A cleaner release design would publish the candidate, then run a read-only verification job on the exact final SHA and attach a required status to that SHA. A self-modifying publication workflow is auditable here, but it is weaker than a protected final-commit qualification.

These qualifications do not motivate rejection. They matter because the manuscript devotes substantial attention to auditability and should satisfy the standard it sets for itself.

---

# 2. Scientific contributions and strengths

## 2.1 Exact selected-boundary and priced-path structure

The strongest part of the paper remains the selected-boundary representation. A chosen command book induces terminal layers and unique service-exit sets. The aggregate edge capacities telescope through the potential

\[
p(u)=\sum_j \pi_j\min\{b_j,u\},
\]

and the history-level packing argument reconstructs original lotteries and pre-draw service while preserving the aggregate promise, individual caps, realization ceilings, and command budget.

The heterogeneous price-path identity is also useful. At a fixed obligation price, each history contributes positive terminal chord increments and one last-eligible service support. These contributions localize on selected edges, producing a polynomial ordered-path oracle for a fixed price. The paper appropriately credits Lagrangian constrained-path bounding and inclusion/exclusion branching as established machinery; the model-specific contribution is the exact arc representation.

## 2.2 Tight cap-count compression

Theorem `thm:capcount56` is a genuine answer to one prior objection. Conditioning a supplied policy on each expected-cap class and applying the common-cap singleton/pair result yields a subset of the same book with at most twice the number of distinct caps. The union preserves each conditional promise, hence the global promise, while nonnegative opening charges cannot increase. The strict construction requiring all `2q` commands appears sound.

The joint cap--reward extension is likewise credible. Within a joint class, terminal rewards agree on the catalog and the common-cap argument applies to the conditional problem. The union of class-wise singleton/pair books preserves original feasibility.

These results identify an exact structural parameter and correctly distinguish XP enumeration from fixed-parameter tractability.

## 2.3 Merged-origin deficit representation

Complementing used capacity into unused capacity is an elegant observation. Because every selected edge has capacity `p(v)-p(u)`, every feasible anchor starts at deficit zero and every complete book ends at the same deficit `R=bar b-B`. This removes the separate anchor loop from the resource dynamic program.

The centered approximation argument is also internally coherent. Adding a common linear term centers the supergradient interval, rounding each edge deficit down loses at most `Km eta`, and the path has sufficient unused capacity to repair the missing total without changing its command book. The reconstructed fixed-book optimum provides an original-feasible lower policy. The paper is careful to state an additive, not multiplicative, guarantee.

The arbitrary-support convolution issue was worth addressing. The implementation and proof do not assume that Bellman rows are concave or have connected finite support. My independent randomized comparison against exhaustive convolution did not reveal an error in the monotone-search routine.

## 2.4 Encoding-sensitive exact regimes

The zero-service lattice theorem is consistent with the weak SUBSET SUM hardness result. Under a common rational lattice, every marginal segment length and the terminal deficit lie on the grid, so a fixed-path separable concave optimum has a grid representative. The resulting algorithm is correctly described as pseudo-polynomial in the numerical lattice size rather than polynomial in its binary encoding.

The saturated-promise corollary is also correct under the stated assumptions. Positive weights and `B=bar b` force every individual target to its cap; every deficit is zero; and a selected-count path dynamic program computes the at-most-budget frontier.

## 2.5 Artifact discipline

The authors retain unsuccessful cases, distinguish numerical MIP output from rational certificates, expose state limits, retain initial checker timeouts rather than rewriting them, and separate optimization, serialization, and checking. These practices are materially better than the selective reporting often seen in algorithm papers.

---

# 3. Mathematical and complexity assessment

I do not identify a theorem that must be withdrawn. The principal problem is the significance and completeness of the resulting complexity picture.

## 3.1 The cap-count theorem is structural, but the algorithm remains XP

The useful-book bound is `2q` under a common reward and `2g` under exact joint cap--reward types. Exhaustive optimization therefore costs approximately `N^(2q)` or `N^(2g)` up to polynomial factors. The paper correctly calls this XP.

This does not establish tractability when `q` or `g` is even moderately large. In the general model, nearly every history may have a distinct cap or reward type. The theorem becomes vacuous as an algorithmic reduction precisely in the heterogeneous settings used to motivate the paper.

The manuscript needs either:

- an FPT algorithm in a meaningful structural parameter;
- a matching parameterized-hardness result explaining why XP is the right frontier;
- a substantially stronger kernel or approximation result;
- or application evidence showing that real instances have very small `q` or `g`.

At present none of these is supplied.

## 3.2 Approximate reward types give a valid but generic perturbation bound

The oscillation theorem is mathematically correct: for two feasible policies, the difference in reward-model error is bounded by the weighted catalog oscillation, while service costs and charges cancel. Applying exact prototype compression yields a `Delta`-loss book bound.

However, the result is close to a generic uniform perturbation argument. The paper does not solve or characterize the choice of prototypes, the number of groups, or the menu-loss tradeoff. It does not show that natural reward data admit small-oscillation groups. The 24 regression models use four histories, seven commands, and two predefined prototype groups; they validate code but not operational usefulness.

The authors should either develop the grouping problem into a substantive optimization result or substantially lower the prominence of this theorem.

## 3.3 The lattice theorem is exact but numerically fragile

The exact lattice algorithm is a legitimate pseudo-polynomial result. It is not a broadly efficient exact algorithm for rational instances. The paper's own stress test makes the limitation concrete:

- the ordinary tests use median grid sizes only 22--73;
- the `2^8` stress case completes;
- the `2^16` and `2^32` cases hit the 600,000-state limit and return no interval.

This is precisely what pseudo-polynomial complexity predicts. The theorem helps complete the weak-hardness story, but it should not be marketed as a practical arbitrary-budget solution without evidence on realistically arising granularity.

Moreover, the relation to standard knapsack and resource-constrained path dynamic programming needs a much more complete literature comparison. Once the common lattice and zero service cost are imposed, the existence of a pseudo-polynomial resource-state algorithm is not surprising. The paper must isolate what is genuinely new beyond the renewal-specific arc derivation and source merge.

## 3.4 The saturated frontier is a boundary case

At `B=bar b`, the aggregate equality and individual upper bounds force `t_j=b_j` for every history. The target-allocation problem disappears. The remaining computation is a count-indexed longest path over full-capacity edge weights.

The corollary is correct and potentially useful, but it is a boundary-degenerate regime rather than evidence of broad positive-service tractability. The paper currently gives it more conceptual weight than its mathematical difficulty and operational range justify. Its importance depends on whether saturated promises are common in a real application, which the paper does not establish.

## 3.5 The exact global method remains exponential

The price-path oracle is polynomial per call, but global exact closure uses candidate inclusion/exclusion branching with a full worst-case binary cover. R58 does not change that worst-case fact.

The current exact-target extension is not a hard test of the branching method. At the two-second limit, seven of nine reported cases close at the root. Only two require branching; maximum depth is three and the maximum completed-oracle count is 45. These results demonstrate that the root relaxation is strong on those generated cases, not that the exponential mechanism is under control.

The retained SUBSET SUM challenge failures point in the opposite direction. A convincing exact-search contribution needs a systematic phase diagram over root gap, charges, cap heterogeneity, command budget, and catalog size, including cases designed to force deep branching.

## 3.6 The small-menu complexity frontier is still incomplete

The weak NP-completeness theorem uses a nonbinding command budget. The new `2q` theorem and lattice theorem narrow the gap, but they do not characterize the limited-menu problem.

Important unresolved questions include:

- fixed-parameter tractability or hardness in `m`;
- parameterized complexity in the number of distinct caps, joint types, or selected eligibility classes;
- hardness under bounded or uniform opening charges;
- hardness or tractability with a fixed small number of cap classes;
- and whether stronger approximation guarantees are possible without a numerical `1/epsilon` state space.

A top theory contribution should provide a sharper map, not merely several isolated tractable slices around a weak nonbinding-budget hardness construction.

---

# 4. The central *Operations Research* significance problem

## 4.1 The operational setting remains hypothetical

The electronic companion describes a possible service-credit architecture: a provider commits to an aggregate expected credit, observes account histories, chooses pre-draw deterministic service and a terminal promotional command, and pays configuration charges for installed command levels. This is a useful interpretation, but the manuscript explicitly states that it is not an observed deployment.

No field data establish:

- that providers face the exact aggregate equality used here;
- that a single paid command catalog is the relevant design object;
- that realization eligibility is always an upper prefix;
- that deterministic service must be fixed before the terminal draw;
- that configuration costs are additive by command level;
- that the proposed caps and ceilings are separately available and stable;
- or that the command alphabet, rather than policy logic, probability precision, or compliance burden, is the binding operational resource.

These assumptions may define a coherent mathematical model. They do not yet define an important operations problem.

The calibration proposition transfers bounded payoff errors while holding probabilities, caps, ceilings, promise, and budget fixed. The companion correctly admits that errors in those feasibility inputs are not covered. In an actual renewal setting, cohort weights, caps, and eligibility rules are unlikely to be known without uncertainty or drift. The paper therefore addresses only the easiest part of the external-validity problem.

## 4.2 The paper must choose a theory route or an application route

A purely theoretical *Operations Research* paper need not contain proprietary field data, but then the theory should apply to a recognizable broad class and be positioned against the best existing methodology. Here the exact representations depend on one aggregate equality, an ordered common catalog, prefix eligibility, separable concave history rewards, convex service costs, and one last-eligible service tail. The paper does not establish how much of the theory survives if any of these structures change.

An application-oriented paper may legitimately use stronger structure, but then it should document a real decision process, calibrate the primitives, validate the restrictions, and demonstrate decision impact. R58 does none of these.

The current manuscript occupies an unstable middle position: too model-specific to stand as a general path-optimization theory, but too synthetic to stand as an operations application.

---

# 5. Literature and novelty positioning are inadequate

The article bibliography contains only eleven entries. It is dominated by classical work on Lagrangian relaxation, constrained shortest paths, matrix searching, resource allocation, quantization, and complexity, plus SciPy and one adverse-selection policy-graph paper.

That bibliography is not sufficient to establish novelty for a 37-page article making claims about finite menus, command catalogs, stochastic service allocation, configuration charges, contract-like implementation, quantization, exact certificates, and parameterized structural complexity. The introduction mainly explains why the cited classical tools do not automatically prove the paper's identities. It does not demonstrate how the model and results relate to the modern literature most directly adjacent to the decision problem.

This is not a cosmetic request to add citations. Without a comprehensive literature map, a referee cannot determine whether:

- the `2q` compression is new relative to support-reduction and menu-complexity results;
- the source-complement transformation is new relative to constrained acyclic path formulations;
- the lattice algorithm is more than a standard pseudo-polynomial resource DP after model elimination;
- the oscillation bound advances robust or approximate aggregation theory;
- or the service-credit interpretation overlaps existing promotion, retention, assortment, or contract design models.

The paper must state the nearest theorem-level antecedents, compare assumptions and conclusions in a structured table, and explain what would remain new if all repository engineering and certificate machinery were removed.

---

# 6. Computational evidence does not support the current claims of practical importance

## 6.1 The main benchmark is small and synthetic

The current primary families have dimensions

- `(k,N,m)=(6,7,3)`;
- `(8,9,3)`;
- `(24,17,4)`; and
- `(96,25,4)`.

There are three seeds and two optimization limits, 0.5 and 2 seconds. The positive-tolerance price and deficit target is `1/20`. All instances are synthetic, use uniform probabilities in the new panel, and set the promise to three quarters of aggregate capacity.

These experiments are valuable implementation tests. They are not a convincing performance study for a top operations journal. The largest catalog has only 25 commands and budget four. The chosen tolerance is coarse. Three seeds do not characterize variability. Uniform probabilities avoid one source of numerical difficulty that the theory explicitly discusses.

## 6.2 Comparators are not strong enough

The direct MIP comparator is a SciPy/HiGHS support-indicator model with 32-segment tangent or secant envelopes for quadratic service cost. Its output is explicitly numerical rather than an original-space rational certificate. This is a useful engineering baseline, but it is not a definitive modern exact comparator.

A fair study should include, where applicable:

- an exact mixed-integer convex or conic formulation with certified gaps;
- a tuned commercial and/or strong open-source solver formulation;
- exact enumeration with dominance and incremental fixed-book updates;
- the prior resource DP under matched error;
- and ablations separating the path identity, source merge, monotone convolution, price selection, branching, and checker cost.

All methods should be compared under common value accuracy and common total wall-clock budgets. Current tables mix exact enumeration, `1/20` additive targets, numerical MIP status, interrupted rational intervals, and method-specific success definitions. The text discloses these differences, but disclosure does not make the aggregate comparison decisive.

## 6.3 The exact-target enumeration comparison is not meaningful

Table `tab:exact56` reports the feasible value of lexicographic enumeration stopped after the same number of distinct books seen in a mechanical replay. The paper correctly says this is not equal work or equal time. Precisely for that reason, it is not an informative algorithmic comparator and should not occupy a central table.

A useful comparison would match time, arithmetic operations, or evaluated fixed books chosen by a competitive enumeration order, and would report the certified gap of each method at common checkpoints.

## 6.4 Screening is empirically harmful in the reported study

This is the clearest negative result in R58. Across 18 paired cases under the same total allowance:

- screening improves total optimization-plus-serialization-plus-checking time in **0 of 18** pairs;
- the median paired total-time ratio is approximately **1.604**;
- and every family-level median ratio exceeds one.

The authors deserve credit for retaining this result. But the appropriate scientific conclusion is not that screening has been operationally validated. The current evidence says the proposed stronger screening procedure is a correct safe rule whose overhead dominates on the tested instances.

The manuscript should either reposition screening as a negative or diagnostic result, identify a theoretically or empirically justified regime where it pays, or remove it from the central contribution list. Removal counts and tighter widths are not substitutes for end-to-end benefit.

## 6.5 The deficit solver is certified but not yet shown to scale

The heterogeneous deficit method completes 27 of 30 requested primary and accuracy runs. Its observed regret is small on completed cases, but the guaranteed interval—not the realized regret against a known small-instance optimum—is the relevant certificate.

The independent checker can be much more expensive than optimization. In my external replay, one large certificate required about 22.6 seconds; the retained extended checks reach 36.36 seconds. This is scientifically honest, but it weakens the claim that the method supplies an economical certifying solution pipeline.

The study should scale `N`, `m`, `k`, and `1/epsilon` separately, report memory and certificate growth, and identify the crossover at which the monotone convolution helps after kernel construction and verification are included.

## 6.6 The study was inspected during development

The protocol explicitly states that the design was previously inspected and is not an unseen confirmatory sample. Fresh execution and source freezing protect against relabeling old timings, but they do not remove design adaptation. This is acceptable for deterministic algorithm engineering, yet the paper should not treat the run count as statistical evidence of broad robustness.

A stronger study would freeze a generator and evaluation protocol, include held-out instance families created independently of observed outcomes, and ideally include a third-party reproduction or public benchmark set.

---

# 7. The manuscript is overextended

The validated article has 37 nonreference pages, followed by a 30-page companion. It contains the original representation theory, common-cap tractability, weak hardness, exact price paths, exponential branching, forced-command screening, cap-count compression, joint reward types, approximate reward types, heterogeneous packing, a legacy additive algorithm, a merged-origin additive algorithm, a lattice regime, a saturated regime, two computational studies, certificate economics, and an operational architecture.

This breadth obscures the central scientific message. Several contributions are correct but incremental or highly specialized. The paper reads as a cumulative repository of every result obtained in the revision sequence rather than a sharply edited journal article.

The authors should choose one central spine. A plausible theory paper would focus on:

1. the selected-boundary/deficit representation;
2. one genuinely sharp complexity frontier;
3. one algorithm with a convincing guarantee and benchmark;
4. and a concise account of implementation certificates.

The remaining special cases and historical studies should move to an archive or separate papers. Preservation of prior work in Git does not require all prior work to remain in the journal narrative.

---

# 8. Required changes before a new submission

A future submission should not be another cumulative revision. It should satisfy the following substantive conditions.

## 8.1 Establish the problem's disciplinary importance

Choose one of two routes.

**Application route.** Provide a real decision setting, document the command catalog and cost semantics, calibrate or bound the primitives, validate prefix eligibility and pre-draw timing, and quantify operational benefit against the current practice.

**Theory route.** Abstract the renewal terminology into a broader endogenous-support resource-path class, state exactly which structural assumptions are necessary, and prove a result whose reach is visibly wider than the motivating service-credit story.

## 8.2 Complete the literature and novelty analysis

Develop a serious related-work section with theorem-level comparisons. Explain which parts are standard after reduction and which parts are new. The current eleven-reference bibliography is not adequate.

## 8.3 Sharpen the complexity frontier

At minimum, address the parameterized status of the limited-menu problem or provide a compelling alternative structural frontier. The paper should not rely on a nonbinding-budget weak hardness theorem plus XP enumeration as the final account of menu complexity.

## 8.4 Redesign the computational study

Use larger and more varied instances, nonuniform probabilities, several accuracy levels, deeper-search families, and substantially more than three seeds. Compare under matched total resources and matched solution guarantees. Include a strong exact mixed-integer baseline and meaningful DP/enumeration ablations. Treat certificate checking as part of the end-to-end cost.

## 8.5 Resolve the screening result honestly

Either identify a regime where screening improves end-to-end performance under a frozen protocol, or present the current result as evidence that safe fixing is not automatically economical. Do not list screening as a practical contribution while every matched pair is slower.

## 8.6 Reduce and reorganize the article

The main paper should not be a 37-page inventory of all historical results. Remove secondary special cases from the central narrative, shorten the abstract, and make the contribution hierarchy explicit.

## 8.7 Qualify the exact final release SHA

Run a read-only, required verification workflow on the exact final candidate commit, and make the downloadable referee artifact directly self-contained rather than requiring discovery of a nested archive.

---

# 9. Specific technical and presentation comments

1. **Infeasible-instance handling.** The exact-search exposition initializes a minimum-command singleton incumbent. State explicitly how the algorithms and certificates represent an infeasible instance when no catalog command can serve as a feasible anchor.
2. **Use of “polynomial.”** Every occurrence should distinguish polynomial in binary input length, polynomial in numerical grid size, pseudo-polynomial, XP, and polynomial per price oracle. The manuscript mostly does this, but the density of claims still invites misreading.
3. **Cap-count relevance.** Report `q` and `g` on every computational instance. A theorem parameter should appear in the empirical study designed to motivate it.
4. **Prototype selection.** The approximate-type theorem assumes prototypes and groups. Explain who chooses them and at what computational or statistical cost.
5. **Saturated regime.** State early that `B=bar b` forces all targets to their individual caps. This makes the source of tractability transparent.
6. **Lattice regime.** Report both the bit length of `D` and the numerical value driving the state count. The current stress test is useful and should be more prominent.
7. **Exact-target table.** Remove the lexicographic equal-book-count “Enum. L” comparison or replace it with a matched-work benchmark.
8. **MIP evidence.** Do not place numerical envelope output beside rational certificates without a clearer common metric. Report the envelope error and solver gap in the table itself.
9. **Screening terminology.** “Improvement” should refer to total decision/proof cost, not merely fewer commands or a narrower intermediate bound.
10. **Checker economics.** Include checker memory and scaling curves, not only isolated elapsed times. A certificate that is correct but expensive to verify may still be useful, but the tradeoff must be explicit.
11. **Reference coverage.** The related-work discussion belongs in the article, not only in a referee response or repository history.
12. **Abstract.** The 188-word abstract is a dense list of nearly every theorem and experiment. It should identify one main problem, one primary structural insight, one principal algorithmic implication, and one evidence conclusion.
13. **Title.** “Small Menus” risks implying an efficient small-menu algorithm. The main general guarantee is XP in the number of types, so the title should be calibrated to that fact.
14. **Operational units.** A future application version should specify units for rewards, service, caps, charges, and promise, and explain why an additive value error is decision-relevant.
15. **Final-SHA status.** Preserve the successful run, but attach a check to the exact published commit rather than relying only on manifests generated by an earlier workflow head.

---

# 10. Confidential note to the editor

R58 is not an empty or deceptive revision. The authors have made a serious effort, and the mathematical core appears technically credible. I found no evidence that unsuccessful runs were removed, that old timings were relabeled as new, or that the current reader silently points to an older manuscript. The artifact engineering is stronger than is typical.

I nevertheless recommend rejection rather than major revision. The changes required are not local. The manuscript needs a different contribution hierarchy, a substantially broader literature treatment, a sharper complexity result or real application validation, and a redesigned computational study. The current paper's strongest evidence supports correctness and reproducibility, not the importance or superiority of the proposed methodology.

A carefully re-conceived submission could become publishable. Another additive revision that appends more special cases, certificates, and synthetic runs would not address the central concern.
