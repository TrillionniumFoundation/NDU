# Neural Differential Utility — Operations Research R19

**Neural Differential Utility: Accepted Multistage Service Control and Certified Value-Gradient Decisions**

Revision date: September 23, 2026. Branch: `revision/ndu-operations-research-r19-20260923`.

## Current referee entry points

[Main manuscript](main.pdf) · [ordinary complete TeX](main.tex) · [current electronic companion](electronic_companion.pdf) · [companion TeX](electronic_companion.tex).

[Point-by-point response](revisions/or-r19-20260923/RESPONSE_TO_REFEREE.md) · [preservation map](revisions/or-r19-20260923/PRESERVATION_MAP.md) · [reproduction instructions](revisions/or-r19-20260923/README.md) · [submission checklist](NDU_OR_submission_checklist.md).

The main PDF has 38 pages, including 3 reference pages; its 35 pages excluding references require the journal's **Lengthy** manuscript category. The current companion has 35 pages. The abstract has 172 words. Both use anonymous letter-size, 11-point, one-and-a-half-spaced text with one-inch margins, author–year references, and tables after the references.

## Version provenance

The latest actual complete report is [the R14 referee report](reviews/operation_research_referee_report_r14_2026-09-22.md). The branch named `review/operation-research-r16-harsh-20260922` points to R16 research results, not a later report. R17 contains an incomplete transport part and R18 a follow-up plan; neither updated the R14 root manuscript. R19 descends from R18 commit `d23de668070fc29a7073a9e4ef647c8159b0d580`, preserves those historical records, and publishes complete ordinary manuscript files instead of another partial transport.

## Scientific revision

The new global resource-price theorem applies on the complete accepted polyhedron with multistage vector decisions, multiple capacities, nonconstant outside protocols, and endogenous switching signs. An exact Bregman decomposition connects the specified scalar value gradient to regret without an optimal face. A separate inexact-response theorem charges the certified response error and actual implemented repair. The scalar star, verified-cell, full-tree friction, continuous acceptance, and prior nonlinear developments remain available in full at the locations in the preservation map.

All eight R16 training/deployment pairs and all seven methods are now integrated. Derivative supervision improves the specified paired neural comparison, while direct-price and non-neural methods are stronger. New matched-accuracy timing gives classical solvers the same initial tolerance and charges response, repair, certification, and actual refinement. Runtime and break-even counts are host-specific descriptive measurements, not a universal neural advantage. The finite-fleet expected-gain statement is conditional on the explicitly randomized eight frozen models, not every model or all future training. Every operational primitive is synthetic.

## Auditable results

[Package checks](revisions/or-r19-20260923/results/package_check.json) · [16,640 independent rational policy replays](revisions/or-r19-20260923/results/replay.json) · [64 deliberate multistage boundary checks](revisions/or-r19-20260923/results/boundary_checks.json) · [64 exact quartic-coupling checks](revisions/or-r19-20260923/results/nonquadratic_checks.json) · [4,608 matched-cost pipeline records](revisions/or-r19-20260923/results/matched_cost_rows.json) · [complete timing summary](revisions/or-r19-20260923/results/matched_cost.json) · [all-cohort reanalysis and strata](revisions/or-r19-20260923/results/reanalysis.json) · [source/result hashes](revisions/or-r19-20260923/MANIFEST.json).

The publication workflow validates the **final published commit**, checks its manifest and exact policy replay, and attaches commit-status context `ndu-or-r19/final-sha` to that SHA. The workflow run and source SHA are recorded in [provenance](revisions/or-r19-20260923/PROVENANCE.json); a successful initial-source run alone is not represented as validation of the final commit.

No prior revision directory, review report, or other branch is modified. Exact previous root manuscripts and PDFs are preserved under [revisions/or-r19-20260923/predecessor/](revisions/or-r19-20260923/predecessor/). The [historical supplement](historical_supplement.pdf) remains unchanged. Author approval of authorship, conflicts, and final journal-submission declarations is still required; this branch is a reviewer-ready revision package, not a claim of journal acceptance.
