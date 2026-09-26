# Confidential Referee Report for *Operations Research*

**Manuscript:** *Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier*  
**Revision reviewed:** `revision/ndu-operations-research-r60-tariff-frontier-20260927`  
**Audited revision tip:** `b6833bc77786db5902b5562f985f2201de58e40f`  
**Audited source tree:** `6ff3105d3f10c4ffe61f96d5078f5f6ca296f65d`  
**Governing prior report:** `review/operation-research-r59-independent-harsh-20260927`, report commit `cc7ac349969adc9186e9a75f8d01f76ad485c3ba`  
**Review branch:** `review/operation-research-r60-independent-harsh-20260927`  
**Date:** September 27, 2026  
**Recommendation:** **Major Revision. R60 has crossed the threshold from an interesting but insufficiently centered resubmission to a potentially publishable theory paper. I find no fatal error in the new tariff-exception algorithm, the retained original-model W[1]-hardness result, the bounded-path conservation construction, or the same-book price-support theorem. The new positive result is a genuine counterpart to the lower bound: in the common-linear, free-service subclass, exact optimization is fixed-parameter tractable in the number of commands whose fee differs from a standard tariff, and uniform fees yield an exact polynomial algorithm without a resource grid. However, acceptance still requires a materially sharper account of the theorem's novelty and operational meaning, an empirical study that actually probes the exception parameter rather than only the cases d=0 and d=2, a cleaner separation of the central frontier from accumulated secondary results, and correction of several implementation and provenance details.**

---

## Executive assessment

R60 is the first revision in this sequence for which I do not recommend rejection. The authors have responded substantively to the R59 report rather than appending another isolated special case. The manuscript now has a coherent theoretical spine:

1. an exact, constructive reduction from the original history-level allocation problem to selected resource paths;
2. a retained W[1]-hardness theorem parameterized by command allowance and cap count under common linear reward and free service;
3. a new exact FPT algorithm, under the same physical primitives, parameterized by the number of tariff exceptions;
4. a uniform-fee polynomial regime and an associated fee-versus-cardinality frontier;
5. a length-aware version of the path-conservation test;
6. a same-book support characterization explaining when a price bound is already an implementable exact decision;
7. and a prospectively frozen computational panel that distinguishes rational global certificates from numerical solver bounds.

The tariff theorem is not a restatement of the price method and not a disguised capacity grid. Conditional on the included exceptional commands and the book cardinality, all remaining books have the same installation charge. The exact gross value is monotone in the attainable terminal capacity. Therefore a longest-capacity dynamic program may keep only one label per cardinality and endpoint. Enumerating exceptional-command subsets gives a factor `2^d` multiplying a polynomial with exponent independent of `d`. The proof also recovers a policy satisfying the original aggregate equality, expected caps, realization ceilings, and command allowance. I did not find a counterexample to this argument.

The revised manuscript is also more honest about computation. It states that the deficit algorithm is unfavorable as a general short-budget solver, retains the negative screening result, separates numerical SCIP bounds from rational certificates, reports dependent requests as requests rather than independent observations, and correctly identifies 56 distinct specifications in the historical R59 panel. This is a substantial improvement in scientific interpretation.

The remaining objections are nevertheless important. The positive theorem is exact only under common linear terminal rewards and free preliminary service. The tariff parameter depends on exact equality to a selected standard fee. The new study tests only zero or two exceptions, catalogs of at most 25 commands, and command allowances of at most six; consequently, the 30/30 tariff success rates do not test the claimed parameterized scaling. The service-credit interpretation remains hypothetical, while the corridor example is a mathematically valid illustration rather than a calibrated operations model. The paper also remains broader than its contribution hierarchy warrants: the 28-page nonreference article and 28-page companion still read partly as a repository of accumulated results.

These deficiencies now admit a bounded revision path. The central theorem need not be replaced. The authors must establish why the tariff parameter is an important and robust structural feature, test the algorithm in the dimension in which its theorem is distinctive, sharpen the closest-literature comparison, and reorganize the paper around the representation/lower-bound/upper-bound frontier. I would be willing to review that revision.

---

# 1. Version, provenance, build, and evidence audit

## 1.1 Reviewed object

The reviewed branch tip is `b6833bc77786db5902b5562f985f2201de58e40f`, with source tree `6ff3105d3f10c4ffe61f96d5078f5f6ca296f65d`. The root article identifies itself as R60 and compiles the tariff-sensitive manuscript rather than an earlier reader.

The committed build receipt reports:

- 30 article pages and 28 nonreference pages;
- a 28-page electronic companion;
- a four-page response to referees;
- a 169-word text-only abstract;
- standalone current sources;
- no undefined references or citations;
- no duplicate labels;
- no overfull boxes;
- and no undefined control sequences.

The exact final commit carries the successful status `ndu-r60/exact-head-verification`. I downloaded the corresponding verification artifact. It binds the final exact commit, the source-freeze commit, and the R59 review base; reports a clean historical-change list; and records successful structural, build, archive, and certificate checks.

## 1.2 Independent reproduction performed for this review

I downloaded and unpacked the 12.9 MB `ndu-or-r60-referee-package` workflow artifact and then extracted its flat `CURRENT_SUBMISSION.zip`. I did not rely only on committed `PASS` strings.

I independently reran `code/tests60.py` from the flat package. It passed:

- 172 tariff instances;
- 6,302 exhaustive book comparisons;
- five large-rational cases with input denominators up to 513 bits;
- 48 deliberately corrupted tariff certificates;
- 160 potential-generated conservative graphs;
- 160 perturbed nonconservative graphs with checked witnesses;
- 480 bounded-path comparisons against exhaustive path enumeration;
- 400 exact rounding-and-repair cases;
- 400 concave max-convolutions with arbitrary support holes;
- and the exact uniform-fee positive-price-gap example.

I also independently dispatched representative committed certificates through the flat checkers:

- an exception-tariff certificate covering all four exception subsets;
- a price-path certificate;
- a deficit certificate;
- an enumeration certificate;
- and a numerical SCIP-selected book whose lower policy was reoptimized and checked in exact rational arithmetic.

All representative checks passed. The tariff checker recomputed all supplied Bellman states and all exception subsets without importing the tariff optimizer.

I attempted the flat package's complete `flat_verify60.py` over all historical and current records. That full local replay did not complete within my review execution cap, so I do **not** claim an independent recheck of all 1,548 records. The exact-head workflow artifact reports the complete check as passing, with 1,221 rational intervals and 236 numerical lower policies rechecked. My independent conclusion about the central mathematics does not depend on treating that workflow receipt as a proof of the theorems.

## 1.3 Provenance qualification

R60 is openly based on the R59 referee-report commit `cc7ac349...`, and the prior referee report is therefore an ancestor and file in the author-revision branch. The preservation map discloses this fact, and I found no evidence that the reviewer-authored report was silently used as manuscript text or altered.

Nevertheless, this is not a clean author/reviewer provenance model. A future author revision should branch from the reviewed manuscript's scientific tip and refer to the review commit by immutable SHA, rather than place reviewer-authored output in the ancestry of the author branch. Alternatively, the final author commits should be replayed onto a clean scientific base before submission. This is a repository-hygiene issue, not a mathematical reason for rejection.

---

# 2. Main scientific contribution

## 2.1 Exact capacity value under linear reward and free service

For a feasible book `c`, the manuscript defines

`D(c) = sum_j pi_j min{b_j, d_j(c)}`,

where `d_j(c)` is the largest selected command eligible for history `j`. Under common linear terminal reward `r x` and free preliminary service, the exact gross value is

`r min{B, D(c)}`.

This identity is correct. If the terminal capacity covers the accepted promise, adjacent eligible lotteries attain the needed terminal means. If it does not, the histories with residual cap fill the remaining promise through deterministic preliminary service, and the realized total remains at most `b_j <= tau_j`.

The telescoping gain formula is also correct. It converts a selected ordered book into an initial level plus consecutive edge gains. This is the model-specific structural fact that makes the tariff result possible.

## 2.2 FPT algorithm in the number of tariff exceptions

Choose a standard fee `rho_0` and let `E` be the commands with a different fee. For each subset `J` of exceptional commands, the algorithm requires exactly `J` and forbids `E \ J`. Start, transition, and end restrictions prevent a selected path from skipping a required exception.

For fixed `J` and fixed book size `s`, every feasible book pays

`(s - |J|) rho_0 + sum_{i in J} rho_i`.

Because gross value is nondecreasing in terminal capacity, retaining only the largest capacity for each `(J,s,endpoint)` state is exact. This gives the stated arithmetic count

`O(k N^2 + 2^d m N^2)`

and bit complexity `2^d poly(L)`. The predecessor path plus the capacity lemma recovers an original feasible policy.

I find this theorem sound as stated under its declared assumptions. The independent checker is appropriately stronger than a replay of the optimizer: it verifies the complete exception cover, recomputes every capacity state, checks every branch optimum, and then checks the original-space policy.

## 2.3 Uniform-fee frontier

When `d=0`, the algorithm is polynomial and contains no resource-grid factor. The fee frontier

`V(rho) = max_s { r min(B,D_s) - s rho }`

is a maximum of decreasing affine functions and is therefore convex, nonincreasing, and piecewise affine. The smallest optimal cardinality is nonincreasing in the fee. These comparative statics are valid.

This is the most direct operational consequence of the new theorem, but it is currently underdeveloped in the manuscript and absent from the computational interpretation. The revision should turn the fee frontier into a substantive decision result rather than leave it as a short corollary.

## 2.4 Relation to the retained W[1] lower bound

The positive and negative results are compatible and form a genuine frontier. The retained hard instances have unrestricted command-specific charges and do not have a bounded number of exceptions from one standard tariff. Enumerating all books yields an XP dependence on command allowance or cap count, whereas enumerating tariff exceptions yields an exponential parameter factor multiplying a fixed-exponent polynomial.

The paper correctly avoids claiming a complete dichotomy. It also correctly avoids claiming W[1]-membership, strong NP-hardness, an ETH exponent lower bound, or a kernel lower bound.

---

# 3. Other new theoretical results

## 3.1 Length-aware conservation

The layered construction for an explicit edge allowance repairs an important scope issue from R59. It is correct to distinguish:

- conservation over every path in the retained graph; and
- conservation only over paths admissible under an edge limit.

Lifting a vertex to `(v,ell)` and connecting all sink layers to a zero-capacity artificial sink gives a bijection between admissible original paths and lifted paths. Applying the suffix-potential test to this layered graph gives the claimed witness and source capacities. The approximation recurrence already tracks elapsed edge count, so the lifted interpretation does not introduce another multiplicative layer factor beyond the stated count.

The theorem is useful as a precise abstraction, although the underlying recognition argument remains elementary once the graph is lifted.

## 3.2 Same-book price support

The price-support theorem is correct and clarifies the evidence produced by the price method. Equality of a global price bound with the original optimum requires one price-active book whose own maximizing target interval contains the accepted promise. Bracketing the promise with targets from different active books is only a relaxation certificate, not an implementable original decision.

The distance-to-support inequality is a valid instance-specific gap bound under a fixed-book Lipschitz condition. The uniform-positive-fee example correctly shows that tariff tractability does not imply zero price gap.

This theorem provides a promising bridge between structure and computation. At present, however, the manuscript stops at diagnosis. It does not develop a complete, measured method-selection or hybrid algorithm from the criterion.

## 3.3 Corridor rehabilitation example

The corridor model is a mathematically legitimate nonrenewal interpretation: contract edges span physical lengths, treated length is a divisible scalar resource, and untreated length is the complement coordinate. It demonstrates that the conservation theorem is not logically tied to command lotteries.

It is not an empirical application. Its fixed treated-length equality, separable edge benefits, divisible treatment, and absence of spillovers are strong assumptions. The paper states these boundaries, which is appropriate. The example supports interpretation but does not yet establish broad operational importance.

---

# 4. Major issues requiring revision

## 4.1 The tariff parameter needs a stronger novelty and robustness argument

The new theorem is correct, but its scientific importance depends on whether “few commands differ from one exact standard fee” is a meaningful and stable feature of real design problems.

The manuscript currently chooses a most frequent exact fee and calls the remaining commands exceptions. This minimizes `d` mechanically, but exact equality of rational fee inputs is brittle. Two nearly identical tariffs count as different, while two exactly identical fees may arise only because a modeler rounded them to one number. The paper needs to distinguish three claims:

1. a mathematical FPT result for exact fee equality;
2. an operational tariff policy in which one standard charge and a small exception list are institutionally real;
3. and numerical preprocessing that groups approximately equal fees.

Only the first is currently proved. A strong revision should provide at least one of the following:

- an application-grounded reason why fees are generated by a standard-plus-exceptions policy;
- a sensitivity theorem for perturbing fees away from the standard tariff;
- an approximation bound based on total tariff deviation or a declared fee clustering;
- or a precise discussion showing why exact equality is the intended policy object rather than an artifact of encoding.

The title advertises a “tariff-sensitive complexity frontier.” The current result is an important positive island, not a full tariff dichotomy. The manuscript should use “frontier” carefully and state which adjacent tariff structures remain open.

## 4.2 The computational study does not test the theorem's distinctive parameter

The prospective design is much better than R59, but it does not empirically probe FPT behavior in `d`.

The standard family has `d=0`. The exception family has exactly `d=2`. Catalog size is at most 25, history count at most 32, and command allowance at most six. The tariff method succeeds on 30/30 requests at every tested allowance in both applicable families. This validates the implementation on small instances; it does not reveal the `2^d` frontier, certificate growth, crossover points, or practical exception limit.

The revision should add a dedicated scaling experiment with, at minimum:

- several values such as `d=0,1,2,4,6,8,10,12` where feasible;
- larger catalogs and command allowances;
- fixed physical instances with controlled tariff perturbations;
- optimizer, checker, serialization, memory, and proof-size scaling in `d`;
- and comparison with price search, enumeration, and SCIP at matched end-to-end budgets.

The implementation currently uses a guard of 12 exceptions. That guard is sensible engineering but is not part of the theorem. Its operational consequence should be measured and stated explicitly.

The paper should also compute and display several complete uniform-fee frontiers, including switching fees and selected books. This would connect Corollary 6.3 to a decision rather than use computation only as a solver race.

## 4.3 The evidence remains internal and synthetic

The authors correctly call the study model-derived and dependent. There are 90 distinct specifications, 270 budget-tagged cases, and 1,260 method requests—not 1,260 independent problems. The source and inputs were frozen before timing, unsuccessful requests were retained, and the numerical/rational evidence classes are separated. These are strengths.

However, all specifications come from one in-house generator. There is no external benchmark, application-derived input set, independent generator, or field-calibrated range. The same seeds recur across interventions and budgets. The three families differ in exactly the dimensions selected to illustrate the theorem.

For a theory paper, field data are not mandatory. Some external validity is still needed. The authors should add one of:

- a documented service-credit or promotion-design case with defensible primitive ranges;
- a corridor or maintenance data set mapped into the model;
- an independently designed benchmark family;
- or a broad adversarial suite that is not derived from the same generator used during algorithm development.

The current study supports correctness and short-budget behavior on its own generator. It does not establish general computational superiority or operational prevalence of the tractable tariff regime.

## 4.4 The price method remains empirically central but theoretically secondary

At three seconds, price search reaches the rational target on 29/30 standard instances, 29/30 exception instances, and 28/30 curved instances. It therefore remains the strongest broadly applicable rational-certification method in the submitted study.

The same-book support theorem explains root exactness, but the manuscript does not report:

- how often the root has one-book support;
- the distribution of distance to the active support interval;
- how that distance predicts branching or final gap;
- the cost of computing and independently checking the support interval;
- or whether the support test can safely select between price, tariff, and deficit methods.

The manuscript currently proposes a hierarchy but does not execute it. Either implement and benchmark a declared method-selection policy, or reduce the practical claims to the measured standalone methods. An unexecuted hybrid should not appear as an algorithmic contribution.

## 4.5 Operational significance is still asserted more than demonstrated

The service-credit narrative fixes the timing and feasibility semantics, but the manuscript still does not show that an operator actually faces:

- a fixed accepted aggregate promise;
- history-observed controlled terminal lotteries;
- command-level fixed opening fees;
- a common command alphabet without free history labels;
- and preliminary service selected before the terminal draw.

The corridor example is structurally valid but generic. A “funding requirement” usually constrains financial cost rather than fixes treated physical length exactly; the manuscript should either motivate that equality carefully or call it a mandated service/coverage target.

The new fee frontier offers a natural route to stronger OR relevance. The authors should show how simplifying a tariff, changing the standard fee, or approving an exception changes the optimal command book and expected value in a defensible setting. Comparative statics should be translated into an actual design decision.

## 4.6 The manuscript remains overextended

The current main article is more focused than R59, yet it still contains:

- the original representation;
- full-graph conservation;
- W[1]-hardness;
- tariff FPT;
- the deficit approximation and holey convolution;
- price support;
- prototype grouping;
- historical and prospective computation;
- and extensive certificate interpretation.

The companion retains another 28 pages of exact regimes, old algorithms, formulations, proofs, application mapping, and evidence semantics.

The central paper should be reorganized around:

1. the original model and implementable path representation;
2. the W[1] lower bound;
3. the tariff-exception FPT upper bound and fee frontier;
4. one concise price-support consequence;
5. and a computational study designed around those claims.

The prototype-selection section, historical approximation variants, and most repository mechanics can remain in an archival companion without sharing equal narrative weight. Preservation in Git does not require every previous result to remain part of the journal submission.

## 4.7 Literature positioning is improved but still not theorem-level enough

R60 adds modern resource-constrained path work, parameterized knapsack, and fixed-charge nonlinear allocation. This is a meaningful improvement.

The paper still needs a sharper closest-result comparison for the new tariff theorem. The relevant question is not whether generic constrained-path, Benders, or knapsack algorithms exist. It is whether an ordered support-selection problem with cardinality charges and a monotone path-capacity objective has already been solved under uniform or nearly uniform activation costs.

The revision should compare assumptions and conclusions in a table containing at least:

- fixed versus endogenous support/path;
- common versus command-specific activation charges;
- cardinality limit;
- exact versus approximate optimization;
- FPT, XP, pseudo-polynomial, or polynomial complexity;
- binary versus numerical dependence;
- recovery of an original allocation;
- and the number of resource dimensions.

The weighted-median grouping theorem should remain explicitly secondary and credited as a one-dimensional clustering dynamic program applied to the model-specific loss function.

---

# 5. Implementation and reproducibility issues

## 5.1 `bounded_recognize` does not enforce the theorem's `h` truncation

The companion theorem first replaces `h` by `min(h, |V|-1)` for an acyclic graph. The public `bounded_recognize` implementation constructs all layers through the supplied `h` without applying this truncation.

This does not change correctness on the tested small DAGs, because superfluous layers are pruned logically. It can violate the stated complexity and create avoidable memory exhaustion when a large binary-encoded `h` is supplied. The implementation should clamp `h` before allocating the lifted graph, and tests should include extremely large declared edge allowances.

## 5.2 The tariff guard must be separated from theorem applicability

`tariff60.solve` defaults to `max_exceptions=12` and raises `NotApplicable` above the guard. The theorem has no such limit. The paper generally distinguishes the guard from the theorem, but the certificate, result tables, and method-selection description should expose:

- the selected standard fee;
- the resulting `d`;
- the configured guard;
- and whether nonexecution is mathematical inapplicability or an engineering guard decision.

## 5.3 Standard-fee ties

The code chooses a most frequent fee, breaking ties by the smaller rational fee. Any modal fee minimizes `d`, and the algorithm is exact for the chosen fee. State this deterministic convention in the article or companion and clarify that a tie can produce different exception decompositions even though the global optimum is unchanged.

## 5.4 Strongly polynomial terminology

The article says the uniform-fee algorithm has a “strongly polynomial arithmetic count.” This is defensible in an arithmetic-operation sense, but the term is easy to overread. State separately:

- the number of arithmetic operations;
- the polynomial bound on intermediate rational encoding length;
- and the resulting bit complexity.

Do not imply unit-cost independence from rational arithmetic in an implemented wall-clock sense.

## 5.5 Source ancestry

As noted above, the author revision inherits the previous referee-report commit. Future revisions should restore a clean manuscript lineage. The newly created review branch for this report starts directly from the exact R60 tip and adds only this report; the R60 source branch itself has not been modified by this review.

---

# 6. Computational assessment

## 6.1 What the new study establishes

The new panel establishes that, on the submitted generator and short budgets:

- the tariff algorithm closes exact rational intervals reliably in the `d=0` and `d=2` regimes;
- price search remains broadly effective, including outside the tariff theorem;
- deficit certification remains expensive and incomplete in many cases;
- enumeration is competitive only on the smaller/easier cases;
- and SCIP often supplies a tight numerical bound after enough setup time, but not an exact rational global certificate.

At three seconds, the submitted target counts are:

| Family | Price rational | Tariff rational | Deficit rational | Enumeration rational | SCIP numerical |
|---|---:|---:|---:|---:|---:|
| Standard | 29/30 | 30/30 | 12/30 | 19/30 | 30/30 |
| Two exceptions | 29/30 | 30/30 | 12/30 | 19/30 | 30/30 |
| Curved/costly | 28/30 | inapplicable | 10/30 | 18/30 | 27/30 |

These numbers are clearly labeled as dependent requests, which is correct.

## 6.2 What it does not establish

The panel does not establish:

- scaling in the exception parameter;
- superiority on larger catalogs or books;
- performance under more than one generator;
- operational prevalence of standard tariffs;
- or performance after long-budget tuning.

The 0.5-second SCIP results are dominated partly by process construction and solver startup. They should not be interpreted as a formulation-quality comparison. Retain them as end-to-end evidence, but analyze setup and optimization separately.

The fixed 60 percent optimization cutoff is a protocol choice. Add a sensitivity analysis or explain why this split is appropriate for all methods, since proof generation and checking costs differ sharply across methods.

## 6.3 Certificate economics

The maximum uncompressed and compressed proofs are approximately 340 KB and 55 KB, respectively, which is modest in this panel. The important missing result is how tariff certificate size grows with `2^d`, because the checker verifies every subset and every state. Report optimizer and checker scaling separately as `d` increases.

---

# 7. Required revision before acceptance

A satisfactory revision should complete the following items.

## 7.1 Central scientific narrative

1. Make the exact representation, W[1] lower bound, tariff-exception FPT upper bound, and uniform-fee frontier the dominant article spine.
2. State explicitly that the tariff result is a positive regime, not a complete dichotomy over fee structures.
3. Reduce the prominence of inherited grouping, historical algorithms, and repository mechanics.

## 7.2 Tariff meaning and robustness

4. Justify standard-plus-exceptions tariffs through an operational policy or application.
5. Analyze sensitivity to near-standard fees, or clearly delimit exact equality as the policy object.
6. Develop the uniform-fee frontier into a concrete design analysis with switching fees and selected books.

## 7.3 Computational evidence

7. Add a controlled `d`-scaling study and report optimizer, checker, memory, and proof growth.
8. Increase catalog and command-budget ranges sufficiently to expose the claimed FPT/XP distinction.
9. Add an external, application-derived, independently generated, or adversarial benchmark family.
10. Report root same-book support frequency and its relation to price branching and gap.
11. Either implement the proposed method-selection policy or remove any implication that it was empirically validated.

## 7.4 Technical corrections

12. Clamp `h` in `bounded_recognize` and test large declared edge allowances.
13. Expose the tariff exception guard separately from mathematical applicability.
14. Clarify strongly polynomial arithmetic versus bit complexity.
15. Document modal-fee tie handling.

## 7.5 Provenance and release

16. Preserve the successful exact-head and flat-package verification discipline.
17. Publish the next author revision on a clean scientific ancestry that references, rather than contains, reviewer-authored commits.

---

# 8. Specific presentation comments

1. The correct journal name is *Operations Research*, not “Operation Research.”
2. Define `d` in the abstract as a count of exceptional commands, not distinct fee values.
3. State the linear/free-service restriction in every summary of the uniform-fee theorem.
4. Avoid implying that uniform fees make the full concave/costly model polynomial.
5. In Corollary 6.3, state the tie convention behind the “smallest optimal book size.”
6. Explain whether all fee-switch intersections are computed exactly and how dominated lines are removed.
7. Add a small worked tariff example showing the DP states and recovered original lotteries.
8. In the price section, distinguish the cost of obtaining an active book from the cost of testing its support interval.
9. Report the fraction of new price requests that close at the root.
10. Report price-tree depth and leaf distributions by family and allowance, not only target attainment.
11. Separate exact tariff nonexecution due to `d` guard from genuine model inapplicability.
12. Label corridor `B` as a required treated length or service target unless financial cost is explicitly modeled.
13. Move source-freeze and manifest details out of the central contribution discussion.
14. Preserve the negative deficit and screening results; they materially improve the paper's credibility.
15. State that finite regression tests support implementation correctness and are not evidence for theorem novelty.
16. Add the maximum exception count covered by structural regression tests; the current random suite reaches only a few exceptions.
17. Report wall-clock scaling with rational bit length separately from state-count scaling.
18. Keep numerical SCIP upper bounds out of any table labeled “certified” without the qualifier “numerical.”
19. Clarify that rational reoptimization of the selected SCIP book can change continuous variables but not the installed book.
20. Reduce the conclusion to the proven frontier and its operational interpretation; do not give all retained side results equal weight.

---

# 9. Confidential note to the editor

R60 is a substantial improvement and, in my judgment, contains a technically credible publishable core. The new tariff-exception theorem is not merely another computational artifact: it supplies a true fixed-parameter upper bound under the same linear/free-service primitives used by the retained lower bound. The authors have also demonstrated unusually strong evidence discipline and have corrected the most serious interpretive weaknesses of R59.

I do not recommend acceptance in the present form. The positive theorem is narrower and more encoding-sensitive than the title may initially suggest, the operational role of a standard tariff remains unvalidated, and the computational study does not vary the theorem's key parameter. The paper is still too cumulative for its central message.

Unlike the previous round, however, these are revision problems rather than reasons to require an entirely new submission. The authors have a clear path: center the paper on the lower/upper complexity frontier, justify or robustify the tariff parameter, run the experiment that the theorem actually calls for, tighten the application interpretation, and clean the implementation/provenance details.

**Final recommendation: Major Revision.** If the next revision does not demonstrate exception-count scaling and a credible reason why standard-plus-exception tariffs matter in an operations setting, I would revert to rejection. If those issues are addressed while preserving the current mathematical and reproducibility quality, the paper could meet the *Operations Research* standard.
