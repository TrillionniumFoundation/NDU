# Confidential Referee Report for Operations Research

**Submission identifier used for this audit:** `revision/ndu-operations-research-r55-lattice-small-menu-20260926`  
**Audited branch tip:** `06e570120ed00e55b662855c98b7c726ccf7c8b4`  
**Scientific reader actually present at the audited tip:** R54, *Exact Path Representations for Finite-Catalog Renewal Design*  
**Antecedent report:** `reviews/operation_research_referee_report_r54_independent_harsh_2026-09-26.md`, commit `4aad7e553b9d1801a59feab9540363c5f9f46fac`  
**Review branch:** `review/operation-research-r55-independent-harsh-20260926`  
**Date:** September 26, 2026  
**Recommendation:** **Return without external review / reject as an incomplete submission. The audited R55 branch does not contain an R55 manuscript revision. It contains two prospective study protocols and one implementation-amendment record, while the repository root reader, README, paper sources, response, PDFs, build validation, code-and-data record, and scientific results remain those of R54. There is therefore no new paper whose mathematical correctness, novelty, computational evidence, or journal suitability can be assessed. Planned claims and planned experiments are not a manuscript.**

---

## Executive assessment

I was asked to review the newest paper revision in the NDU repository. I therefore audited the highest numbered Operations Research branch rather than assuming that its branch name established the existence of a manuscript.

The highest branch is labeled R55, but the audited tip is not a paper revision in any ordinary editorial sense.

The branch is three commits ahead of the R54 review parent. Those commits do the following:

1. freeze an R55 experimental protocol;
2. add a protocol addendum for selected large-case replays; and
3. record a certificate-serialization amendment after a local development run encountered Python's decimal-string conversion limit for an extremely large integer.

The R55 revision directory at the audited tip contains only:

- `PROTOCOL.json`;
- `PROTOCOL_LARGE_REPLAY_ADDENDUM.json`; and
- `IMPLEMENTATION_AMENDMENT.json`.

It does **not** contain an R55 article source, electronic companion, response to referees, theorem files, bibliography, generated tables, build record, executable implementation, checker, committed result set, publication summary, or R55 PDF.

The repository root confirms the same point. `main.tex` still assembles the R54 article entirely from R54 and earlier source paths. The root README is headed “NDU — Operations Research R54,” identifies `revision/ndu-operations-research-r54-exact-price-path-20260926` as the current paper, and gives R54 reproduction instructions and evidence counts.

This is not a subtle provenance issue. There is no R55 manuscript to read.

Accordingly, I cannot responsibly issue a scientific recommendation on the proposed R55 mathematics. I cannot verify theorem statements that are absent, inspect proofs that are absent, reproduce computations whose code and official records are absent, or judge whether the future revision has answered the R54 report. Any purported detailed review of “R55 results” would be invented from a protocol.

The only defensible recommendation is to return the branch as incomplete.

---

# 1. Version audit

## 1.1 Branch identity

The audited branch is:

`revision/ndu-operations-research-r55-lattice-small-menu-20260926`

at commit:

`06e570120ed00e55b662855c98b7c726ccf7c8b4`.

No R56 branch was present at the time of audit.

The R55 branch was created from the R54 review history rather than from an independently published R55 scientific tip. Its protocol declares:

- review parent `4aad7e553b9d1801a59feab9540363c5f9f46fac`;
- scientific parent `eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9`;
- and a planned scope involving lattice optimization, menu compression, a merged-origin resource scheme, price-tree diagnostics, and certified fixing.

That declaration is useful development metadata. It is not evidence that the planned manuscript exists.

## 1.2 Commit-level changes

Relative to the R54 review parent, the branch contains three development commits:

1. `ded848c9cfdd93fefe7994f19b60d691c9d6455c` — freeze the initial validation protocol;
2. `8f0394447134d0c2aa8e6b039d145d2a118161a8` — freeze a large-replay and fine-heterogeneous comparison addendum; and
3. `06e570120ed00e55b662855c98b7c726ccf7c8b4` — record a binary-rational serialization amendment after a development failure.

These commits establish that work is in progress. They do not establish that a revised paper was completed.

## 1.3 Reader audit

At the R55 tip, root `main.tex` still has the R54 title:

*Exact Path Representations for Finite-Catalog Renewal Design*.

It inputs:

- `revisions/or-r54-exact-price-path-20260926/introduction.tex`;
- the R54 model, constructive, exact-cap, hardness, price, packing, branching, fallback, study, conclusion, references, and generated tables;
- plus inherited R52/R53 material already present in R54.

It does not input any R55 file.

The root README likewise names R54 as the current paper and points readers to the R54 branch, R54 response, R54 code, and R54 result archive.

Thus the only journal-facing manuscript at the audited tip is the already reviewed R54 manuscript.

## 1.4 Missing R55 scientific artifacts

The following expected artifacts are absent from the audited R55 directory:

- `main.tex` or an equivalent R55 article source;
- `main.pdf`;
- an R55 electronic companion source and PDF;
- `RESPONSE_TO_REFEREES.tex`, `.md`, or `.pdf`;
- theorem/proof source files;
- references;
- generated tables or figures;
- `BUILD_VALIDATION.json`;
- a preservation/content map for a completed reader;
- an R55 code directory;
- an independent R55 checker;
- official R55 result records;
- a publication execution audit;
- a source manifest binding results to code;
- and a final R55 README identifying the paper and reproduction entry points.

A branch without these materials is not ready for external peer review.

---

# 2. What the committed R55 materials actually establish

The three JSON files establish only prospective or developmental facts.

## 2.1 Initial protocol

The initial protocol proposes to investigate:

- exact zero-service lattice optimization at arbitrary command budgets;
- a menu-compression statement related to the number of distinct caps;
- a centered merged-origin heterogeneous resource scheme;
- richer price-tree diagnostics;
- end-to-end certified fixing;
- multi-seed principal cases;
- positive-gap challenge cases;
- lattice-scaling cases;
- and screening break-even studies.

It also declares intended limits, seeds, methods, and diagnostics.

This is good experimental hygiene. It supplies no theorem, proof, algorithm, implementation, or result.

## 2.2 Replay addendum

The addendum states that it was written after inspecting development regressions and partial outcomes. It proposes replays of two R54 large cases and finer heterogeneous cases under additional time allowances.

Again, this is a plan. It is explicitly not the original pre-execution protocol for all contemplated evidence, and no replay results are committed at the audited tip.

## 2.3 Implementation amendment

The amendment reports that an initial local 269-run development study encountered a failure when Python attempted to convert an extremely large integer denominator to a decimal string beyond its default digit limit.

It proposes a revised certificate schema using hexadecimal rational serialization and states that a new regression passed before rerun.

The amendment is commendably transparent about the failure. It simultaneously confirms that the official publication study had not yet been committed. The referenced development archive is said to exist in conversation artifacts rather than in the repository branch available to a referee.

An external reviewer cannot audit an absent archive, absent implementation, absent checker, or absent rerun.

---

# 3. Why a protocol cannot substitute for a manuscript

Peer review evaluates claims that authors have actually made and supported. A protocol describes claims that authors may later make.

For each proposed R55 contribution, the present branch lacks the material needed for review.

## 3.1 “Exact zero-service lattice optimization”

The branch does not state:

- the exact input lattice assumption;
- whether the lattice parameter is unary or binary encoded;
- the state space;
- the recurrence;
- the dependence on command budget;
- the bit-complexity argument;
- the relation to the weak SUBSET SUM hardness in R54;
- the boundary between pseudo-polynomial and polynomial behavior;
- or a reconstruction theorem for original policies.

The phrase in the protocol is not reviewable mathematics.

## 3.2 “Cap-count menu compression”

The protocol hints at a menu-size result related to the number of distinct caps. The branch does not provide:

- a formal theorem;
- its assumptions on reward, ceilings, charges, and service costs;
- a proof;
- a tightness example;
- an algorithm for finding the compressed menu;
- or a comparison with the R54 two-command theorem under common caps.

A referee cannot determine whether this is a genuine structural theorem, an immediate corollary, a loose upper bound, or an incorrect conjecture.

## 3.3 “Centered merged-origin heterogeneous resource scheme”

The branch does not provide:

- the resource origin transformation;
- the exact feasibility repair;
- the approximation interval;
- a complexity theorem;
- the treatment of arbitrary support holes;
- the relation to R54's selected-boundary packing;
- or an implementation and independent checker.

The amendment's serialization discussion presupposes such an implementation, but that implementation is not committed in the audited tree.

## 3.4 Search diagnostics and fixing

The protocol asks for node counts, root gaps, pruning events, live leaves, depth, mandatory-set statistics, price bit lengths, proof sizes, trajectories, and screening break-even.

Those are appropriate diagnostics and directly answer the R54 report. None of the corresponding records is present.

## 3.5 Computational claims

The protocol lists hundreds of intended runs and several time budgets. There is no official R55 result archive at the audited tip.

Consequently, the branch establishes none of the following:

- that the methods ran;
- that the planned cases were retained;
- that failures were not suppressed;
- that intervals passed independent verification;
- that exact references were computed correctly;
- that the hexadecimal certificate amendment fixed the publication run;
- that the new method improves upon R54;
- or that screening provides end-to-end benefit.

---

# 4. Editorial consequences

## 4.1 The submission is not self-contained

A journal submission must contain the paper being reviewed. The scientific content cannot be reconstructed from branch names, protocols, local artifacts, or author intentions.

## 4.2 The submission has no stable claim set

Because there is no R55 manuscript, there is no fixed abstract, contribution list, theorem numbering, assumptions, conclusion, or response to the R54 report.

A referee cannot determine what is being claimed.

## 4.3 There is no reproducible R55 evidence package

The branch lacks the code and exact records needed to reproduce the planned study. The local development archive identified in the amendment is not part of the audited repository branch.

## 4.4 The branch is actively developmental

The amendment was made because a development study exposed a serialization failure. This is precisely the stage at which authors should continue development, not request formal external review.

## 4.5 Re-reviewing R54 would be inappropriate

R54 has already received a complete independent report. Repeating that report under an R55 branch name would create a false paper trail and would not evaluate the proposed new work.

---

# 5. Preliminary scientific concerns raised by the protocol

The following are not findings about an R55 paper, because no such paper is present. They are requirements that the eventual manuscript will need to meet.

## 5.1 The lattice result must clarify encoding complexity

R54's hardness is weak and encoding-sensitive. A lattice exact algorithm may be valuable, but only if the manuscript clearly distinguishes:

- polynomial time in binary input length;
- pseudo-polynomial time in a numerical denominator or capacity;
- fixed-parameter dependence on menu budget;
- and exponential dependence hidden in a common denominator.

The reported decimal-serialization failure suggests that exact denominators may become enormous. Hexadecimal serialization avoids a Python conversion limit; it does not by itself control bit complexity, memory, or certificate size.

The eventual paper must report denominator bit lengths and prove that every claimed polynomial bound counts bits rather than merely arithmetic operations.

## 5.2 “Arbitrary command budgets” needs a genuine parameterized statement

The R54 report asked about the small-menu regime. An algorithm that is exact for arbitrary budgets but pseudo-polynomial in another large numerical parameter may not resolve that concern.

The eventual paper should state whether its running time is:

- fixed-parameter tractable in the command budget;
- XP in the budget;
- pseudo-polynomial in a lattice denominator;
- or exponential in a combined parameter.

## 5.3 Menu compression needs tightness and algorithmic consequences

A bound expressed as a multiple of the number of distinct caps may be loose when caps are nearly all distinct. The paper should show:

- whether the bound is tight;
- whether it improves the command budget in the intended regime;
- whether zero-charge unused commands affect the statement;
- and how the compressed book is constructed without enumerating the original optimum.

## 5.4 The heterogeneous merged-origin scheme must not overclaim

If the scheme is additive and based on a shared grid, the paper must expose:

- its accuracy dependence;
- its catalog and budget exponents;
- the cost of exact rational scaling;
- its behavior with support holes;
- and its implementation scope relative to the theorem.

The previous revision was careful to distinguish implemented common-reward kernels from theoretical heterogeneous kernels. R55 must preserve that discipline.

## 5.5 Official evidence must not be replaced by development evidence

The amendment says that the initial local study and failing record are retained separately. The final repository should include enough immutable material to verify:

- the original failure;
- the exact code change;
- the complete official rerun;
- and the fact that model inputs, limits, and reporting rules did not change.

A statement that a conversation artifact exists is insufficient for journal reproducibility.

## 5.6 Protocol amendments must be separated from post hoc choices

The large-replay addendum was written after partial initial outcomes were inspected. That is acceptable if disclosed, but the final paper must not describe the entire study as preregistered or untouched.

The results should be partitioned into:

- initial protocol cases;
- development diagnostics;
- post-inspection addendum cases;
- official reruns after the serialization amendment;
- and any further amendments.

## 5.7 Accuracy targets must remain comparable

The initial protocol uses tolerance `1/100` for several principal cases, while replay and historical cases use `1/1000` or smaller positive gaps. The final comparison must not pool those outcomes into one success rate without respecting their different targets.

## 5.8 End-to-end screening value must be shown

The R54 report requested screening plus downstream solve under the same total budget. The protocol promises this. The eventual paper must report:

- screening cost;
- reduced solve cost;
- verification cost;
- total elapsed time;
- nodes or states saved;
- proof-size changes;
- and cases where screening loses time or removes nothing.

---

# 6. Minimum materials required before re-review

A new review request should not be made until the branch contains all of the following.

## 6.1 A complete R55 reader

At minimum:

- an R55 title and abstract;
- complete article source;
- complete PDF;
- a companion if relied upon;
- references;
- generated tables and figures;
- and a code/data statement.

The root reader and README must identify R55 rather than R54.

## 6.2 A stable theorem set

The manuscript must contain formal statements and proofs for every headline claim, including:

- the lattice exact algorithm;
- the cap-count menu bound;
- the merged-origin heterogeneous scheme;
- any new complexity classification;
- and any certificate-transfer or screening result.

## 6.3 A response to the R54 report

The response should map every major R54 criticism to:

- a theorem;
- an experiment;
- a narrowed claim;
- or an explicit unresolved limitation.

## 6.4 Complete implementation and checker

The exact code used for publication results must be committed. Independent certificate verification must be available from the audited branch.

## 6.5 Immutable official results

The branch should contain:

- all planned cases;
- every failure and resource limit;
- official rerun records after the serialization change;
- source manifests;
- instance hashes;
- execution environment;
- certificate hashes;
- and generated table provenance.

## 6.6 Build and preservation validation

A final `BUILD_VALIDATION.json` should report actual page counts, references, labels, layout diagnostics, and reader hashes. A preservation manifest should identify the scientific parent and every changed reader entry point.

## 6.7 Clear status labels

The repository should distinguish:

- protocol branch;
- development branch;
- completed scientific revision;
- publication result commit;
- and referee copy.

Calling a protocol-only branch a paper revision invites exactly the present confusion.

---

# 7. Minor comments on the current development records

1. The protocol is detailed and generally well designed, but it should not be presented as a scientific contribution.

2. The amendment appropriately avoids disabling Python's integer-string security limit globally.

3. Hexadecimal serialization may reduce conversion overhead, but the paper must report actual encoded bit lengths and storage, not merely successful serialization.

4. The local 269-run archive should be committed or otherwise made available through the repository's durable code/data package before review.

5. The large-replay addendum should retain exact instance hashes copied from R54 and document that only run identifiers and time allowances changed.

6. Planned multi-budget and positive-gap comparisons should not aggregate different requested accuracies into a single completion statistic.

7. A regression pass is not a substitute for publication-run evidence.

8. If official runs are still pending, the branch should be named as a research or protocol branch rather than a revision branch.

9. The final paper should say explicitly whether the serialization amendment changes only the proof encoding or also checker complexity and proof size.

10. Any theorem whose implementation requires a denominator with thousands of decimal digits needs a sober numerical and bit-complexity discussion.

---

# 8. Recommendation

**Return without external review / reject as incomplete.**

The audited R55 branch is a development protocol branch, not a completed manuscript revision. The repository's actual current paper remains R54, which has already been reviewed. No responsible referee can assess absent R55 theorems, proofs, implementation, results, or response.

This recommendation should not be misread as a judgment that the proposed R55 ideas are false. There is simply no committed scientific object on which to make that judgment.

The correct next step is to finish and validate the R55 manuscript, commit the complete reader and evidence package, and only then request a new review from the resulting immutable scientific tip.