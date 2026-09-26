# Confidential Referee Report for *Operations Research*

**Submission identifier audited:** `revision/ndu-operations-research-r56-complete-structural-20260926`  
**Audited branch tip:** `b5235c54d2a466227b6546d7eff2f307a6c46c79`  
**Immediate parent:** `revision/ndu-operations-research-r55-lattice-small-menu-20260926`, tip `06e570120ed00e55b662855c98b7c726ccf7c8b4`  
**Last scientific manuscript actually present:** R54, *Exact Path Representations for Finite-Catalog Renewal Design*, scientific tip `eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9`  
**Antecedent reports inspected:** `reviews/operation_research_referee_report_r54_independent_harsh_2026-09-26.md` and `reviews/operation_research_referee_report_r55_independent_harsh_2026-09-26.md`  
**Review branch:** `review/operation-research-r56-independent-harsh-20260926`  
**Date:** September 26, 2026  
**Recommendation:** **Return without scientific review / reject as an incomplete and misidentified revision. The R56 branch contains no R56 manuscript, theorem, proof, response, implementation, official result archive, or journal-facing build. Relative to R55 it adds exactly one file: the referee report explaining that R55 itself was incomplete. Relative to the last genuine scientific tip, R54, it adds only two referee reports and three prospective/development JSON records. The root reader and README still identify and assemble R54. There is therefore no new scientific object on which an *Operations Research* recommendation can responsibly be based.**

---

## Executive assessment

I was asked to review the latest paper revision in the NDU repository. I audited the repository state rather than accepting the branch label `r56-complete-structural` as evidence that a completed revision exists.

The audit produces a decisive result: **R56 is not a paper revision.** Its tip is a review commit whose sole change relative to the R55 tip is the addition of the R55 completeness report. The scientific reader, article sources, PDFs, companion, bibliography, build records, code, evidence archive, and README remain those of R54. The only R55-specific scientific-development directory contains two study protocols and one implementation amendment. There is no R56-specific directory at all.

This is not a minor packaging omission. Peer review requires a stable claim set: a manuscript, formal statements, proofs, computational evidence where invoked, and a response explaining what changed. None of these exists for R56. A detailed review of purported R56 mathematics would necessarily invent claims that are not in the repository.

The correct editorial action is therefore to return the submission as incomplete. The authors may later submit a genuine revision built from a clean scientific parent, but the present branch cannot be treated as such.

My recommendation is not a judgment that the underlying R54 paper has no merit. The previous report found the central selected-boundary and price-path results mathematically credible and regarded R54 as the strongest version in the sequence. The problem is more elementary and more serious: **the branch submitted for review does not contain the claimed revision.**

---

# 1. Version-control audit

## 1.1 Branch identity and tip

The highest-numbered Operations Research revision branch available at the time of this audit is

`revision/ndu-operations-research-r56-complete-structural-20260926`

at commit

`b5235c54d2a466227b6546d7eff2f307a6c46c79`.

The tip commit message is:

`review(or-r55): add independent harsh Operations Research completeness report`.

That message accurately describes the commit. It is a referee-output commit, not an author-revision commit.

## 1.2 Exact R55-to-R56 delta

Comparing

- base: `revision/ndu-operations-research-r55-lattice-small-menu-20260926` at `06e570120ed00e55b662855c98b7c726ccf7c8b4`, and
- head: `revision/ndu-operations-research-r56-complete-structural-20260926` at `b5235c54d2a466227b6546d7eff2f307a6c46c79`,

shows that R56 is one commit ahead and changes exactly one path:

`reviews/operation_research_referee_report_r55_independent_harsh_2026-09-26.md`.

No paper source, proof, PDF, response, code file, input, result record, certificate, figure, table, or build manifest changes between R55 and R56.

Accordingly, the branch label “complete structural” has no corresponding scientific delta.

## 1.3 Delta from the last genuine scientific manuscript

The last scientific manuscript tip identifiable in the branch lineage is R54 at

`eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9`.

Comparing that scientific tip to the R56 tip yields only five added files:

1. `reviews/operation_research_referee_report_r54_independent_harsh_2026-09-26.md`;
2. `reviews/operation_research_referee_report_r55_independent_harsh_2026-09-26.md`;
3. `revisions/or-r55-lattice-small-menu-20260926/PROTOCOL.json`;
4. `revisions/or-r55-lattice-small-menu-20260926/PROTOCOL_LARGE_REPLAY_ADDENDUM.json`; and
5. `revisions/or-r55-lattice-small-menu-20260926/IMPLEMENTATION_AMENDMENT.json`.

These are two referee reports and three development-governance records. They do not constitute a revised paper.

## 1.4 Root reader remains R54

The root `main.tex` at the R56 tip is titled

*Exact Path Representations for Finite-Catalog Renewal Design*.

It assembles its substantive sections from

`revisions/or-r54-exact-price-path-20260926/...`

with inherited R52/R53 components. It does not input any R55 or R56 paper source.

The root README is headed:

`NDU — Operations Research R54`.

It identifies

`revision/ndu-operations-research-r54-exact-price-path-20260926`

as the current paper branch, gives R54 reproduction instructions, describes R54 evidence counts, and points to R54 code, records, and certificates.

Thus a reader following the repository’s own entry points receives R54, not R56.

## 1.5 The R55 development directory is not a manuscript

The directory

`revisions/or-r55-lattice-small-menu-20260926/`

contains only:

- `PROTOCOL.json`;
- `PROTOCOL_LARGE_REPLAY_ADDENDUM.json`; and
- `IMPLEMENTATION_AMENDMENT.json`.

The initial protocol proposes future work on exact lattice optimization, cap-count menu compression, a centered merged-origin heterogeneous resource scheme, price-tree diagnostics, and end-to-end screening. It expressly states that no R55 numerical experiments had run at the protocol commit.

The replay addendum was written after development regressions and partial initial outcomes were inspected. It plans additional inherited and fine-heterogeneous runs. It contains no completed result.

The implementation amendment records a decimal-string serialization failure involving an extremely large exact denominator, specifies a hexadecimal certificate encoding, and states that an official publication rerun would occur later. It refers to a large local development archive retained outside the audited repository branch.

These records are useful for development provenance. They are not article sources, proofs, implementations, independently checkable publication results, or a response to reviewers.

## 1.6 No R56 scientific directory or release object exists

At the audited tip there is no directory analogous to

`revisions/or-r56-.../`

containing a manuscript package. There is no R56:

- article source;
- article PDF;
- electronic companion source or PDF;
- response to referees;
- theorem or proof source;
- bibliography;
- generated table or figure set;
- build validation record;
- content map or preservation manifest;
- executable implementation;
- independent checker;
- official input and result archive;
- execution audit;
- source manifest binding code to records;
- or code-and-data package.

There is therefore no journal-facing R56 release to audit.

---

# 2. Why a substantive scientific review is impossible

## 2.1 There is no stable claim set

A revision should state what it claims. Here there is no R56 title, abstract, introduction, contribution list, model, theorem numbering, proof set, computational section, conclusion, or response letter.

The phrase “complete structural” appears only in a branch name. It is not a scientific statement and cannot be refereed.

## 2.2 There are no R56 theorem statements or proofs

The protocol names several prospective contributions, but no formal statements are committed. A referee cannot determine:

- the exact assumptions;
- the domain of each result;
- whether the result is stronger than R54;
- whether a proposed algorithm is exact, approximate, pseudo-polynomial, fixed-parameter, or exponential;
- whether bit complexity is controlled;
- whether reconstruction into original policies is proved;
- or whether the claims are correct.

A protocol sentence is not a theorem, and a regression plan is not a proof.

## 2.3 There is no R56 response to the prior report

The R54 report identified concrete remaining blockers: the weak and nonbinding-budget hardness construction, the unresolved small-menu complexity regime, the exponential worst-case branching tree, severe fallback complexity, incomplete heterogeneous implementation, limited search diagnostics, weak end-to-end comparisons, and lack of a calibrated operational setting.

R55’s protocol announces work that might address some of these concerns. R56 contains no response showing that the work was completed. There is no point-by-point mapping from criticism to theorem, experiment, narrowed claim, or acknowledged limitation.

## 2.4 There is no official computational evidence

The R55 protocol specifies many planned runs, diagnostics, resource limits, and comparison methods. The amendment acknowledges a development failure and says every prescribed case will be rerun under a revised encoding.

No official rerun archive is present. Therefore the branch does not establish:

- that the proposed algorithms were implemented as stated;
- that all prescribed cases ran;
- that failures and limits were retained;
- that certificates verify independently;
- that the serialization change preserved mathematical outputs;
- that large denominators are manageable in bit complexity or storage;
- that the new method improves on R54;
- that screening helps end to end;
- or that any proposed table or numerical claim is true.

An external referee cannot replace absent records with trust in a local archive or conversation artifact.

## 2.5 The existing R54 reader cannot be silently re-labeled R56

R54 has already been reviewed. Reissuing its unchanged source and evidence under a higher branch number would not answer the report. It would merely duplicate the same scientific object under a different identifier.

A new revision requires a new, inspectable scientific delta.

---

# 3. Status of the R54 scientific baseline

Because R56 contains no new paper, I do not re-review R54 in full. The following summary is included only to identify what remains unresolved in the absence of a revision.

## 3.1 Strengths already recognized

The R54 report found no immediate fatal counterexample to the central mathematical components, including:

- the selected-boundary resource identity;
- constructive recovery into original policies;
- heterogeneous-reward component packing;
- the exact priced-path identity;
- the common-cap two-command theorem;
- the stated weak SUBSET SUM reduction;
- finite exact branching with original-instance intervals; and
- forced-command exclusion through valid price bounds.

R54 also improved the manuscript’s focus, exact-arithmetic verification, and separation between structural theory and empirical claims.

## 3.2 Unresolved publication threshold

The prior recommendation nevertheless remained rejection in the present form because:

1. the hardness result is weak and uses a nonbinding command budget;
2. it does not characterize the small-menu regime motivating finite-catalog design;
3. exact search still has a complete inclusion/exclusion tree with exponential worst-case size;
4. the polynomial additive fallback has severe dependence and its heterogeneous extension was not fully implemented;
5. computational evidence did not sufficiently expose node counts, pruning, accuracy scaling, budget scaling, proof sizes, or total screening-plus-solve benefit;
6. comparisons did not establish robust superiority over exact enumeration or modern mixed-integer optimization; and
7. no calibrated operational setting established independent practical importance.

The current R56 branch changes none of the underlying manuscript or evidence and therefore resolves none of these blockers.

## 3.3 A plan to address a criticism is not resolution

The R55 protocol is well targeted to several prior criticisms. In particular, it proposes lattice complexity work, menu compression, heterogeneous resource computation, richer tree diagnostics, and end-to-end screening comparisons.

That planning is encouraging. It is not a scientific answer until the corresponding statements, proofs, code, official records, and manuscript interpretation are committed and auditable.

---

# 4. Provenance and editorial-process concerns

## 4.1 A referee report has been used as the sole R56 revision delta

The R56 branch is created by adding the R55 referee report to the R55 development tip. This conflates two different objects:

- author scientific revisions; and
- external referee output.

A clean review workflow should branch a review from an immutable scientific tip and add the report only on the review branch. The scientific revision should not acquire its revision number solely because a reviewer report was committed to it.

## 4.2 Circular review ancestry

The branch presented as R56 contains the report that says R55 is incomplete, but contains no author response or scientific revision following that report. Treating this as a completed R56 would create a circular record:

1. R55 is incomplete;
2. a report states that R55 is incomplete;
3. the report itself is committed and the branch is renamed R56;
4. R56 is then described as a completed scientific revision.

That sequence does not produce new science.

## 4.3 Misleading branch nomenclature

The suffix `complete-structural` suggests that a structural revision was completed. The Git tree contradicts that implication. Branch names are not evidence, but misleading names make auditability worse and increase the risk that downstream reviewers or automation inspect the wrong scientific object.

## 4.4 Reviewer artifacts should not contaminate author-revision branches

Referee reports should remain in dedicated review branches. Author revisions should start from a declared scientific parent and contain author-produced revisions and responses. This separation is particularly important in a repository with many rapid review/revision cycles, because otherwise ancestry no longer identifies which changes are scientific and which are evaluative.

## 4.5 External artifacts are not a substitute for repository evidence

The implementation amendment identifies a local development archive retained in conversation artifacts. Such an archive may help the authors preserve debugging history, but it is not part of the audited branch and cannot support a journal claim. Any evidence relied upon by the paper must be committed, content-addressed, and independently reproducible from the reviewed scientific tip.

---

# 5. Minimum requirements before another review request

A further review request should not be made until all of the following are present on one immutable scientific branch.

## 5.1 A genuine R56 or later manuscript reader

The branch must contain and expose through its root entry points:

- a revision-specific title and abstract;
- complete article source;
- a compiled article PDF;
- a complete electronic companion if relied upon;
- references;
- final tables and figures generated from committed records;
- a code-and-data statement; and
- a README identifying the correct revision, scientific parent, and reproduction commands.

The root reader must actually input the new revision files rather than R54 files.

## 5.2 A complete response to referees

The response should address every major R54 and R55 concern and point to exact locations in the new manuscript and evidence package. Each response should identify one of:

- a new theorem and proof;
- a new experiment and record;
- a corrected implementation and independent check;
- a narrowed claim;
- or an explicit unresolved limitation.

Merely stating that a concern was “addressed” is insufficient.

## 5.3 Formal structural results

If the prospective R55 contributions remain part of the revision, the manuscript must formally state and prove at least:

- the exact zero-service lattice algorithm and its reconstruction guarantee;
- the precise cap-count menu-compression theorem;
- the centered merged-origin heterogeneous resource scheme and its approximation interval;
- all claimed complexity bounds, including bit complexity;
- the relationship of these results to R54’s weak hardness theorem and common-cap exact tractability; and
- any new screening or transfer theorem used by the implementation.

## 5.4 Exact complexity accounting

The serialization failure is a warning that arithmetic-operation counts alone may hide very large integers. The revision must specify:

- binary input encoding;
- denominator and numerator bit lengths;
- state-count dependence on numerical lattice parameters;
- arithmetic versus bit complexity;
- memory complexity;
- certificate-size bounds;
- and whether the method is polynomial, pseudo-polynomial, XP, fixed-parameter tractable, or exponential in each relevant parameter.

Hexadecimal serialization removes a decimal-conversion limit. It does not establish a polynomial bit bound.

## 5.5 A reproducible implementation and independent checker

The exact publication implementation must be committed with:

- immutable source hashes;
- exact input records;
- official outputs;
- all failures and resource limits;
- independent certificate verification;
- corruption tests;
- execution audits;
- and a manifest binding manuscript tables to result records.

The checker should not import the optimizer whose output it verifies.

## 5.6 Completed official reruns

The official study promised after the encoding amendment must be completed and committed. The evidence should clearly separate:

- initial protocol cases;
- development runs;
- the post-inspection replay addendum;
- the failing decimal-serialization record;
- the code change;
- official reruns under the revised schema; and
- any later amendments.

Results at different tolerances and time budgets must not be pooled into a single success statistic without qualification.

## 5.7 End-to-end algorithmic evidence

For exact search and screening, report at minimum:

- generated and evaluated nodes;
- oracle calls;
- root and final gaps;
- pruning counts by reason;
- incumbent updates;
- live-leaf counts;
- depth;
- mandatory-set statistics;
- time-to-bound trajectories;
- rational price bit lengths;
- uncompressed and compressed certificate sizes;
- verification time;
- screening time;
- reduced solve time;
- total screening-plus-solve time;
- and cases in which the new methods lose to the baselines.

Comparisons must use the same original instances and total algorithm allowances within each row.

## 5.8 A defensible Operations Research contribution

The revision must explain why the model-specific structure matters at the journal’s threshold. This can be done through either:

- a broader and sharper structural/complexity theory; or
- a calibrated operational setting showing that the finite-catalog renewal problem arises independently, that its assumptions are meaningful, and that the proposed methods change decisions or tractability.

Synthetic validation is valuable, but it cannot by itself establish operational significance.

## 5.9 Clean branch hygiene

The next scientific revision should:

- name its scientific parent explicitly;
- exclude new referee-output commits from the author-revision delta;
- place the subsequent referee report only on a new review branch;
- preserve all predecessor evidence without silently overwriting it; and
- make the scientific diff independently inspectable.

---

# 6. Scientific questions the eventual revision must answer

These questions remain central if the planned structural work is completed.

## 6.1 What is the true small-menu complexity frontier?

R54 proves weak NP-completeness with a nonbinding command budget, while fixed command budget permits polynomial enumeration. The important middle ground remains open. The revision should determine whether exact optimization is:

- fixed-parameter tractable in command budget;
- XP but unlikely to be FPT;
- pseudo-polynomial in a lattice denominator;
- tractable in the number of distinct caps or eligibility classes;
- or hard under a genuinely binding small-menu constraint.

A lattice dynamic program is meaningful only when its parameter dependence and encoding are made explicit.

## 6.2 Does cap-count compression produce a useful and tight structural boundary?

A theorem of the form “at most twice the number of distinct caps” must clarify:

- exact assumptions on rewards, service, ceilings, and charges;
- whether unused zero-charge commands matter;
- whether the bound is tight;
- whether it remains useful when most caps are distinct;
- how a compressed optimum is constructed;
- and whether construction itself avoids enumerating the unknown optimum.

## 6.3 Does the heterogeneous resource method match its theorem?

The paper should distinguish carefully between:

- a theorem for fully heterogeneous increasing concave rewards;
- an implementation that actually supports those rewards;
- a finite arithmetic guarantee;
- and the performance regime tested in the official study.

Support holes, exact feasibility repair, and original-policy reconstruction must be covered both mathematically and in the checker.

## 6.4 Does the price oracle generate a material exact-search advantage?

The value of the method is not established by the existence of a valid Lagrangian bound. The revision must show whether the bound reduces the combinatorial tree enough to matter relative to:

- complete book enumeration;
- carefully engineered dynamic programming;
- modern mixed-integer optimization;
- and the polynomial resource approximation.

The hard cases, not only favorable closures, should drive the assessment.

## 6.5 Does certified screening help under the same total budget?

Removal percentages are insufficient. The relevant quantity is total cost:

screening + reduced optimization + verification.

The revision should include cases where screening removes nothing, costs more than it saves, or produces large proof objects, as well as favorable cases.

## 6.6 Are exact denominators an algorithmic bottleneck rather than a formatting issue?

The reported 4,300-digit conversion failure may be only a serialization problem, but it may also reveal rapid growth in exact arithmetic. The revision should empirically and theoretically report:

- maximum rational bit lengths by stage;
- their scaling with histories, catalog size, budget, and accuracy;
- state and certificate memory;
- and whether large integers dominate runtime.

Without this accounting, a claim of polynomial or practical exact computation is incomplete.

---

# 7. Recommendation

**Return without scientific review / reject as an incomplete submission.**

The audited R56 branch does not contain an R56 paper. Its sole change relative to R55 is the addition of the report explaining that R55 was incomplete. The journal-facing reader and all scientific artifacts remain R54. No new claim, proof, response, implementation, result, or release package is available for evaluation.

This conclusion is stronger than “major revision.” A major-revision recommendation presupposes that a manuscript has been submitted. Here the purported revision is absent.

A future submission may merit serious consideration if the planned structural work is completed, cleanly packaged, independently verified, and shown to resolve the R54 concerns. Until then, the branch should not enter substantive peer review and should not be represented as a completed scientific revision.
