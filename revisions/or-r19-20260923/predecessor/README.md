# Neural Differential Utility — Operations Research revision R14

**Neural Differential Utility: Accepted Adaptive Service Control and Certified Value-Gradient Learning**

This new revision responds to the latest R12 referee report and builds on the completed R13 manuscript rather than reverting to an older version.

**Revision branch:** `revision/ndu-operations-research-r14-20260922`  
**Scientific parent:** `808b8f0353051581134d3b8b5a7424422d4e48a8`  
**Review:** `reviews/operation_research_referee_report_r12_2026-09-22.md` at `5b1a62679f890006d8f6a234160fa9a02dcdbc5a`.

## Current review documents

- [Main manuscript](main.pdf), [ordinary TeX source](main.tex), and [current electronic companion](electronic_companion.pdf).
- [Point-by-point response to the referee](revisions/or-r14-20260922/RESPONSE_TO_REFEREE.md).
- [Preservation and relocation map](revisions/or-r14-20260922/PRESERVATION.md).
- [Reproduction instructions](revisions/or-r14-20260922/README.md) and [submission checklist](NDU_OR_submission_checklist.md).

## New scientific content

Main Section 7 supplies an explicit critical friction and a single-price exact algorithm on accepted two-review trees. Its global scalar-value-gradient regret bound requires no optimal query-time face, face library, or strict complementarity. An observable residual and independent rational conjugate bound certify the actual implemented policy, including rounding and capacity repair.

Main Section 9 trains eight paired scalar neural critics, separates raw policy quality from classical refinement, compares against strong scalar solvers, and executes a new independent 2,048-context expected-gain confirmation. Every learned deployment has positive absolute friction. The full vector, boundary, signed-coefficient, nonconstant-comparator, and multistage theory remains in the main manuscript. The previous verified-cell experiment and all unfavorable nonlinear results remain intact.

The new direct neural policies are accurate before full-objective refinement in the specified synthetic family. Complete audit-inclusive latency still favors classical scalar solvers, and the paired derivative-training comparison is unresolved. These outcomes are reported rather than hidden.

## Verification and preservation

The authoritative records are [rational replay](revisions/or-r14-20260922/results/verification.json), [structural checks](revisions/or-r14-20260922/results/structural_checks.json), [independent confirmation](revisions/or-r14-20260922/results/validation.json), [paired study and complete timings](revisions/or-r14-20260922/results/summary.json), [package checks](revisions/or-r14-20260922/results/package_checks.json), and [source/data hashes](revisions/or-r14-20260922/results/manifest.json).

All earlier scientific directories and data are unchanged. Exact R13 root documents and PDFs are under `revisions/or-r14-20260922/predecessor/`. The [historical supplement](historical_supplement.pdf) preserves the earlier continuous-time and diffusion development; no new theorem depends on uninspected archival material. The root PDFs are rebuilt actual documents, not encoded placeholders or instructions for the next reviewer to finish.
