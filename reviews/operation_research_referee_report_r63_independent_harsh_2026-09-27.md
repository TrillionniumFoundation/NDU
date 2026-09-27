# Confidential Referee Report for *Operations Research*

**Manuscript:** *Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier*  
**Revision reviewed:** `revision/ndu-operations-research-r63-referee-ready-20260927`  
**Audited revision tip:** `653cc617af4a18dac533200de8606f083ca341fb`  
**Audited source tree:** `00dff3a22a9c74699e15285b9100207f8f9aab5b`  
**Governing prior report:** `review/operation-research-r60-independent-harsh-20260927`, report commit `65c1b64efcf596e12a0134e4696f4bb5a7183f99`  
**Review branch:** `review/operation-research-r63-independent-harsh-20260927`  
**Date:** September 27, 2026  
**Recommendation:** **Minor Revision.** The central representation, the original-model parameterized lower bound, and the tariff-exception FPT upper bound now form a coherent and potentially publishable *Operations Research* theory contribution. I find no fatal mathematical error in the new fee-perturbation theorem, sparse-exception projection, exact installation-fee frontiers, length-aware conservation result, or same-book price-support theorem. R63 also supplies the exception-count scaling, adversarial panel, executed hybrid, exact external-input binding, and clean author-only provenance requested in my R60 report. The remaining work is bounded: close two certificate-semantic gaps, position the sparse projection and perturbation results more accurately against antecedent machinery, remove wording that can be read as exact tractability for near-standard tariffs, and add one compact projection-quality table from the already frozen records. No new central theorem or new large computational campaign is required.

---

## Executive assessment

R63 is a substantial and successful response to the R60 Major Revision report. The paper now has a dominant scientific argument rather than a collection of loosely connected results:

1. the history-level model is reduced constructively to a selected-boundary resource path while preserving the accepted aggregate equality, expected caps, realization ceilings, and command allowance;
2. arbitrary command-specific opening charges remain W[1]-hard when parameterized by the menu allowance and distinct-cap count, already under common linear reward and free preliminary service;
3. under those same physical primitives, exact optimization is fixed-parameter tractable in the number of commands whose fee differs from a standard tariff;
4. uniform fees yield an exact polynomial-time regime and a complete fee-versus-installed-cardinality frontier;
5. near-standard tariffs admit an original-policy value interval after a sparse-exception fee projection;
6. the broader concave model retains a feasible additive resource-deficit guarantee and same-book price certificates;
7. and the computational evidence now varies the exception count, physical size, proof size, checker cost, numerical encoding, and adversarial structure while preserving every failed or interrupted request.

The exact tariff theorem remains the strongest positive result. Conditional on an included subset of exceptional commands and a book size, all admissible books pay the same opening charge. Under a common linear reward and free service, gross value is monotone in attainable terminal capacity. A layered longest-capacity dynamic program may therefore keep a single label for each exception subset, cardinality, and endpoint. Enumerating the exception subsets contributes the factor `2^d`; the polynomial exponent is independent of `d`. The recovered label yields an original feasible policy rather than only an auxiliary path value. I find the theorem and its implementation sound under the stated assumptions.

The near-standard result is also correct. Re-evaluating a surrogate-optimal policy under the original fees gives a feasible lower bound, while the sum of the largest possible fee decreases in a book gives a valid upper bound. The resulting interval preserves every physical constraint because only the objective coefficients change. The sparse-exception projection correctly reduces to a one-dimensional trimmed absolute-deviation location problem: after sorting, an optimal retained block may be taken consecutive, and its median minimizes absolute deviation.

R63 also resolves the central evidentiary objections from R60. The study includes `d=0,1,2,4,6,8,10,12`, larger catalogs and book allowances, optimization/checking/memory/proof-size accounting, a separate adversarial generator, an executed hybrid, and an independent 48-case root-support diagnostic. The paper does not hide the unfavorable deficit results or claim that the hybrid is universally superior. That honesty materially improves the manuscript.

I therefore no longer see a scientific reason to reject the paper or require another major reconstruction. The remaining issues matter because the paper makes unusually strong auditability claims. They can, however, be addressed by a focused minor revision.

---

## Referee scorecard

| Dimension | Assessment | Comment |
|---|---:|---|
| Technical correctness | 4.5/5 | No fatal flaw found in the principal lower bound, tariff algorithm, perturbation interval, projection, or policy recovery. |
| Originality | 3.5/5 | The model-specific representation and tariff-sensitive parameterized frontier are genuine; the perturbation and trimmed-L1 projection use more standard principles. |
| Significance for OR | 3.5/5 | A credible theory contribution once the exact scope and operational interpretation are maintained. |
| Algorithmic contribution | 4/5 | Exact FPT regime, exact policy recovery, fee frontier, and independently checkable certificates. |
| Computational evidence | 4/5 | Much better aligned with the theorem; still constructed rather than field calibrated, as the paper appropriately states. |
| Exposition | 4/5 | The main argument is now visible, although some accumulated machinery remains. |
| Reproducibility | 5/5 | Exceptional exact-head, source-freeze, failure-preservation, external-binding, and proof-replay discipline. |
| Overall | Minor Revision | The central paper is publishable after a bounded set of corrections. |

---

# 1. Version, provenance, and independent audit

## 1.1 Reviewed object

The exact reviewed branch tip is `653cc617af4a18dac533200de8606f083ca341fb`, with tree `00dff3a22a9c74699e15285b9100207f8f9aab5b`. The root reader identifies itself as R63. The branch continues the author-only scientific history and pins the R60 report by immutable commit and blob rather than taking the reviewer commit as a scientific parent. A direct comparison confirms that the R60 review commit and the R63 author history have no common ancestry.

The final exact commit carries a successful `ndu/r63-exact-head` status. The associated receipt binds the published commit, source-trigger commit, 6,848 delivered files, reader hashes, build diagnostics, root-support checks, and proof replay. The current readers comprise:

- 28 article pages, 26 excluding references;
- a 28-page electronic companion;
- a five-page response to referees;
- a 172-word text-only abstract;
- no unresolved references;
- and no reported overfull boxes.

## 1.2 Independent checks performed for this report

I downloaded and unpacked the 12.4 MB `ndu-or-r63-referee-package-and-exact-head-receipt` artifact and audited the flat submission rather than relying only on committed `PASS` fields.

I independently ran the current package verification and structural suites. They passed the following checks:

- all 405 frozen historical/current requests were inventoried;
- all 389 available certificates were independently replayed against external frozen inputs;
- 342 two-sided rational certificates passed;
- 47 numerical-solver lower policies passed exact original-policy checking;
- 16 requests correctly had no certificate;
- 16 certificate/input pairs used different but exactly equivalent rational serializations;
- and 45 later-successful replays remained classified by their original timing/failure outcomes rather than being retroactively promoted.

The complete independent replay took approximately 197 seconds on my review environment. Its counts agree with the delivered exact-head receipt, apart from ordinary machine-dependent runtime.

I also reran the structural suites covering:

- 172 exact tariff instances and 6,302 exhaustive book comparisons;
- 198 robust-transfer instances and 198 exhaustive sparse-fee projections;
- 6,623 original-book error comparisons;
- exact exception counts through 12 and the engineering guard at 13;
- 108 corrupted robust/tariff certificates rejected;
- 160 conservative and 160 perturbed path graphs;
- 480 bounded-path checks against exhaustive paths;
- 400 exact rounding-and-repair cases;
- 400 concave convolutions with support holes;
- the huge declared edge allowance `10^100`, correctly clamped to an effective allowance of two;
- and the rational fee-switch example with switching points `1/15` and `1/3`.

Finally, I generated an additional 300 small rational instances not contained in the submitted panel. I cross-checked the exact tariff result against exhaustive book enumeration, the robust interval against every book under the original fees, and sampled uniform-fee frontiers against brute force. I found no discrepancy.

These checks are strong evidence about the implementation and certificate semantics. They do not replace mathematical proof or establish novelty by experiment.

---

# 2. Mathematical assessment

## 2.1 Exact selected-boundary representation

The constructive decomposition remains one of the paper's strongest contributions. For a fixed selected book, the terminal layers and disjoint service tails reproduce the canonical history responses. Capacity telescopes independently of realization-ceiling eligibility, while eligibility affects edge payoff. The rearrangement argument moves resource from costly service to positive terminal increments and from later to earlier concave terminal layers without weakening feasibility or value. The reconstruction returns lotteries and deterministic preliminary service satisfying all original constraints.

This is more than a generic resource-constrained path formulation: the paper proves why the individual expected and realized constraints collapse to its edge capacities and payoffs. I find the representation internally coherent.

## 2.2 Original-model W[1] lower bound

The retained group-sum/multicolored-clique reduction continues to answer the main negative-complexity question. The zero command and all group baselines consume actual slots, equality excludes multiple paid options from one group, and the no-carry digits enforce consistency. The reduction remains in the original model with linear reward, free service, uniform positive probabilities, caps equal to ceilings, and nonnegative rational charges.

R63 now juxtaposes this lower bound with a positive parameter that is genuinely different: fee exceptions rather than command allowance or cap count. This is a credible complexity frontier, provided the manuscript continues to avoid claiming a complete dichotomy for every tariff or reward class.

## 2.3 Exact FPT algorithm for tariff exceptions

Let `E` be the commands whose charge differs from the selected standard fee and `d=|E|`. For each subset `J` of exceptional commands, the algorithm requires `J`, forbids `E\J`, and disallows transitions that skip a required command. Start and end conditions force every required exception into the path. For fixed `J` and cardinality `s`, every feasible book pays the same charge. Keeping only maximum terminal capacity at each endpoint is therefore exact.

The stated operation count

`O(k N^2 + 2^d m N^2)`

is consistent with the implementation. The bit-complexity qualification is also necessary and correctly stated: rational arithmetic operations are not unit-cost bit operations, but the represented capacities retain polynomial encoding length. Uniform fees set `d=0` and remove the resource grid.

I did not find a counterexample in the recurrence, exception-cover logic, endpoint restrictions, charge accounting, or original-policy recovery.

## 2.4 Near-standard fee transfer

For original charges `rho`, surrogate charges `rho_tilde`, and differences `delta_i=rho_i-rho_tilde_i`, the paper defines the maximum positive and negative fee changes that can occur in a book of at most `m` commands. The surrogate-optimal policy evaluated under the original charges is a valid lower policy. Any original book's value can exceed its surrogate value by at most the negative-error budget, giving the upper bound.

The theorem is correct and useful. Its precise contribution is an objective-coefficient transfer certificate around an exact tractable surrogate. It does **not** make a general near-standard instance exactly FPT, and the manuscript mostly says this correctly. The distinction must be made completely explicit in the abstract and contribution summary; see Required Revision 2 below.

The strict surrogate-margin condition for book stability is also correct: the relative value of the selected book and a competitor can deteriorate by at most the sum of the one-sided error budgets.

## 2.5 Minimum-distortion sparse-exception projection

The projection proposition is correct. Once fees are sorted, there exists an optimal set of `N-d` values replaced by a common standard that forms a consecutive window. For a fixed window, a median minimizes absolute deviation. Minimizing over all windows therefore solves the stated projection problem, and allowing more exceptions cannot increase the minimum distortion.

This is useful preprocessing, but it should not be marketed as an independent algorithmic novelty. It is a one-dimensional trimmed absolute-deviation or median-with-outliers argument. The paper should credit that antecedent class directly and describe the novelty as its integration with the original-policy fee-transfer certificate and tariff solver.

## 2.6 Uniform-fee decision frontier

The exact envelope over cardinalities is correctly derived. Each exact-size capacity table supplies an affine value line in the uniform fee; their maximum is convex, nonincreasing, and piecewise affine. The smallest optimal cardinality is nonincreasing. R63 wisely does not claim that the actual installed command sets are nested.

The four-history example is particularly helpful because it reports not only switching fees but also the selected books and the transition from terminal delivery to preliminary service. The larger rational frontiers in the package make the result inspectable.

## 2.7 Same-book price support

The same-book support theorem correctly separates an implementable price certificate from a bound formed by mixing different books. Equality holds exactly when one active book supports the accepted promise. The distance inequality follows from the Lipschitz property of the fixed-book value function.

The independent 48-case diagnostic is a strong addition. It builds the complete concave hull by exhaustive enumeration rather than reusing the price-path recurrence, finds 20 same-book-supported cases and 28 positive-gap cases, and then checks the price implementation against that truth. This is substantially more informative than reporting shallow search trees alone.

---

# 3. Assessment of the response to the R60 report

R63 resolves the major revision requests to a degree sufficient for publication consideration.

### Contribution hierarchy

The main article now centers the exact representation, lower bound, tariff-exception upper bound, near-standard transfer, and fee frontier. Secondary heterogeneous, prototype, and recognition material is more visibly subordinate or moved to the companion.

### Scaling in the distinctive parameter

The controlled panel now varies `d=0,1,2,4,6,8,10,12`, rather than testing only `d=0` and `d=2`. At six seconds, tariff certification succeeds on 8/8, 5/8, and 3/8 cases at catalog sizes 17, 65, and 129. At the fixed 17-command size, optimization rises from roughly 0.005 seconds at `d=0` to 0.819 seconds at `d=12`, independent checking rises from roughly 0.209 to 1.116 seconds, and proof size rises from 4,143 to 3,964,865 bytes. These results expose, rather than conceal, the `2^d` and proof-checking burden.

### Larger physical dimensions and encodings

The study includes `(N,k,m)=(17,12,8),(65,32,16),(129,48,32)` and rational encodings through 4,096 bits. Enumeration fails to certify any of the 48 controlled scaling requests under the assigned budgets. This is not an asymptotic proof, but it is an appropriately aligned engineering test.

### Adversarial coverage

The separate 12-case panel varies exception density, small promises, fee dispersion, curvature, service cost, eligibility geometry, and alternating fees. The reported outcomes are not selectively favorable: price attains 12/12 rational targets, robust tariff 7/12, hybrid 8/12, exact tariff 4/12, and deficit/enumeration 0/12. Numerical SCIP bounds attain 12/12 but remain separately labeled.

### Executed hybrid

The hybrid is now an executed method, not a proposed routing story. It attains 27/48 controlled scaling targets versus 25/48 for tariff and 24/48 for price, but loses to price on the adversarial panel, 8/12 versus 12/12. The manuscript appropriately declines to claim universal routing superiority.

### Edge allowance, guard semantics, and provenance

The implementation clamps binary-encoded `h` before constructing the layered graph. Mathematical inapplicability, exception-guard refusal, optimization deadline, parent timeout, and checker failure are distinct statuses. R63 also uses a clean author-only ancestry and immutable review reference. These were all explicit R60 requests and are now satisfied.

---

# 4. Remaining required revisions

The following changes are necessary but bounded. I do not require a new central theorem or a new large study.

## Required Revision 1: close the certificate-semantic gaps

The mathematical intervals are checked correctly, but two claims made by the solver are not yet independently certified by the corresponding checkers.

### 1(a). Standard-fee selection

`check_tariff60.py` verifies the complete exception inventory relative to the **supplied** standard fee and checks every Bellman state and exception subset. It does not verify that the supplied standard fee is a most-frequent original charge or that the declared smallest-rational tie rule was followed. Exact optimality remains valid for any supplied standard fee, but the reported exception parameter `d`, preprocessing rule, and scaling interpretation depend on this choice.

The checker should recompute the modal fee and tie rule, or the certificate schema should state explicitly that it certifies exact optimality conditional on a supplied standard fee but not optimality of the chosen parameterization. The former is preferable and trivial to add.

### 1(b). Sparse-projection optimality and minimum exception allowance

`check_robust61.py` verifies the external original input, physical-input invariance, inner exact tariff proof, error budgets, returned policy, and final interval. It does not independently verify the submitted projection, its minimum absolute distortion, or that `selected_exception_budget` is the smallest `d` meeting the tolerance. A malicious certificate could therefore carry a valid original-fee interval while making false claims about projection optimality or minimum `d`.

The checker should recompute the sorted-window/median projection for the claimed `d`, verify its distortion, and verify failure of `d-1` when minimality is claimed. Alternatively, separate those fields from the mathematically certified schema and describe them only as optimizer metadata. Given the paper's auditability emphasis, recomputation is preferable.

The mutation tests should include a nonoptimal retained window, an incorrect median, and a nonminimal selected `d`.

## Required Revision 2: state that near-standard tariffs give approximation, not exact tractability

The abstract says that the paper “extends this result to near-standard tariffs.” A reader can interpret “this result” as the exact FPT tractability theorem. The actual result is different: an exact tractable surrogate plus an original-policy additive interval whose width is charged to fee distortion.

Revise the abstract, introduction, and conclusion to use wording such as:

> “We transfer the exact sparse-exception solution to near-standard tariffs through an original-policy additive certificate.”

Do not call arbitrary near-standard fees exactly FPT unless an exact algorithm for the original fees is proved. The body already contains the correct qualification; the high-level statements should match it.

## Required Revision 3: position the projection and perturbation results against their nearest antecedents

The minimum-distortion projection is an instance of one-dimensional trimmed absolute-deviation location / median estimation with outliers. The fee-transfer theorem is a sharp, model-compatible objective-coefficient perturbation bound, but its bounding principle is elementary sensitivity analysis.

Add a short related-work paragraph that:

- credits trimmed absolute-deviation and median-with-outliers antecedents;
- states that consecutive windows and medians are not claimed as a new general clustering algorithm;
- distinguishes the paper's contribution: choosing a sparse-exception tariff surrogate whose exact solution can be transferred back to an original feasible policy with a certified value interval;
- and separates this from distributional robustness or statistical estimation.

This correction will sharpen, rather than weaken, the genuinely original tariff frontier.

## Required Revision 4: add one compact near-standard projection-quality table

The new study contains robust-tariff requests, and the manuscript gives one detailed example, but the practical approximation tradeoff is harder to read than the exact-`d` scaling results. From the already frozen records, add a compact table for the near-standard/adversarial cases with columns such as:

- original catalog size;
- tolerance;
- selected exception allowance;
- actual projected exception count;
- `E_+`, `E_-`, and certified interval width;
- exact or best available realized regret when an exact comparator closes the value;
- optimizer and checker time;
- and proof bytes.

No rerun is necessary. The purpose is to show what the perturbation theorem buys, not merely how often the robust method meets a target.

## Required Revision 5: distinguish original timed checking from post-study external binding in every summary table

The manuscript correctly states that later replay does not reclassify original failures. Preserve that distinction in the captions of the primary computational tables. A reader should be able to tell immediately that:

- original target attainment uses the originally recorded end-to-end deadline and checker outcome;
- the R63 binding replay is a later integrity audit against external frozen inputs;
- and a later successful replay does not make an originally late or failed request successful.

The underlying data already implement this rule. The requested change is presentation-level.

---

# 5. Detailed technical and editorial comments

1. **Journal name.** Use *Operations Research*, not “Operation Research,” in repository-facing prose and future correspondence.

2. **Parameter notation.** Distinguish consistently among the allowed projection budget `d`, the actual number of charges different from the selected standard, and the implementation guard. These quantities can differ.

3. **Mode ties.** State in the theorem or algorithm box that choosing a most frequent fee minimizes the exact exception count; choosing the smallest rational mode only makes the implementation deterministic and does not affect exact optimal value.

4. **Conditional exactness.** The tariff recurrence is exact for any declared standard fee after all relative exceptions are enumerated. What changes is its parameter value and cost. This observation should accompany the tie-rule discussion.

5. **Projection tolerance.** Clarify whether the user-supplied tolerance constrains total absolute fee distortion or the final certified value width. The implementation selects by total absolute distortion, which is sufficient but can be conservative relative to `E_+ + E_-`.

6. **Book stability.** The strict-margin corollary is useful, but computing the margin over all books may itself require solving a second-best problem. State whether the implementation reports such a margin or whether this is a theoretical diagnostic only.

7. **Norm bound.** In the main statement, retain `bar_m=min(m,N)` explicitly in the `2 bar_m ||delta||_infinity` bound so the result is not read with an untruncated allowance.

8. **Projection novelty.** The sorted-window proof is concise and correct. It should be labeled as specialized preprocessing, not another principal theorem on par with the tariff frontier.

9. **Uniform-fee frontiers.** Keep the careful statement that optimal cardinality is monotone but installed sets need not be nested. This is an important and correct limitation.

10. **Root support terminology.** “Root supported” should always mean support by one active original book, not merely that the promise lies in the convex hull of targets of several active books.

11. **Hybrid accounting.** Retain the charged restart and probe costs. Do not retrospectively compare the hybrid with an oracle selector.

12. **Guard outcomes.** `ENGINEERING_GUARD` should remain separate from `MATHEMATICALLY_INAPPLICABLE`, and neither should be counted as a mathematical failure of the theorem.

13. **SCIP evidence.** Continue to call SCIP's global bound numerical. Exact reoptimization of its selected book certifies only the lower policy.

14. **Proof size.** The multi-megabyte tariff certificates demonstrate auditability but also expose a deployment cost. Report compressed and uncompressed tails together, and avoid treating proof generation/checking as negligible.

15. **Synthetic scope.** The expanded panel is well designed for theorem-aligned stress testing but remains constructed. Preserve the current disclaimer and avoid managerial adoption claims.

16. **Application interpretation.** The service-credit interpretation now explains standard and exceptional setup charges more concretely. It remains a stylized model, which is acceptable for a theory paper if stated plainly.

17. **Main-text focus.** The main article is substantially improved. If page pressure arises, move additional checker and historical-algorithm detail to the companion rather than reducing the exact representation, lower bound, tariff theorem, robust transfer, or computational denominators.

18. **Reproducibility language.** Exact-head and replay receipts support integrity and reproducibility; they do not themselves establish theorem correctness, novelty, or editorial acceptance. The manuscript mostly respects this distinction and should continue to do so.

19. **Historical failures.** Retaining 16 no-certificate requests and 45 later-replayed but not reclassified checks is scientifically appropriate. Do not replace those records in a future package.

20. **Clean ancestry.** The author-only ancestry and immutable review reference resolve the R60 provenance objection. Preserve this model for subsequent revisions.

---

# 6. Required revision checklist

A satisfactory minor revision should:

1. make the tariff checker verify the modal standard fee and deterministic tie rule, or narrow its certified claim explicitly;
2. make the robust checker verify projection optimality and minimum selected `d`, or remove those claims from the certificate schema;
3. add mutation tests for a wrong projection window, wrong median, and nonminimal `d`;
4. rewrite high-level “near-standard extension” language as an additive transfer certificate rather than exact tractability;
5. add the nearest trimmed-L1 / median-with-outliers and objective-perturbation positioning;
6. add one compact projection-quality table from the already frozen evidence;
7. label post-study external binding separately from original on-time certification in primary captions;
8. preserve all existing failures, guards, proof costs, and evidence-class distinctions.

These are bounded corrections. I do not request another new algorithm, a new hardness theorem, a new large simulation campaign, or field data as a condition of publication.

---

# 7. Recommendation to the editor

R63 has crossed the publication threshold in substance. The paper now offers a coherent exact representation and a meaningful negative/positive parameterized frontier inside the original allocation model. The new robust-transfer layer and installed-command frontiers improve operational interpretability, while the expanded study directly probes the parameter that makes the positive theorem distinctive. The authors have also responded unusually well to adverse results: price remains superior on the adversarial panel, the hybrid is not universally best, proof checking can dominate, and historical failures are preserved.

The remaining concerns do not undermine the central theorems. They concern certificate closure, novelty attribution for two supporting lemmas, wording of the near-standard guarantee, and presentation of an already-computed approximation tradeoff. These can be resolved without changing the scientific core.

**Final recommendation: Minor Revision.** Subject to the eight checklist items above, I would support acceptance of the revised manuscript in *Operations Research*.
