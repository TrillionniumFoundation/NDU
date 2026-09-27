# Operations Research review package — R33

## Version and reader files

New branch: `revision/ndu-operations-research-r33-piecewise-randomized-20260923`.
Scientific base: `238bfdb24d93439a545551d275a0c9189dbc017b`.
Effective report: independent R30 review at `a017f474619e86be533547acac87a3c8354f64cf`.
Entry points: `main.tex`, `electronic_companion.tex`, and the corresponding rebuilt PDFs.

## Scientific changes

R31/R32 results and adverse evidence are preserved. R33 adds the piecewise-quadratic event theorem, shared-circuit storage/query theorem, kink-safe conjugate certificate, explicit flow reduction, adjacent-lottery characterization, and globally solved strict two-symbol advantage. See `revisions/or-r33-piecewise-randomized-20260923/RESPONSE_TO_REFEREES.md` for every referee item and the inherited/new distinction.

## Style and reproducibility

The abstract has 183 words and no mathematical notation. The introduction contains no equations or mathematical notation. Main text uses 11-point type, one-and-a-half spacing, and one-inch margins. Author-year references are alphabetized. All tables remain after references. Only forced page breaks in a derived copy of the old tables are removed; every number and note is retained. The complete new theorem proofs remain in the article.

The build rejects undefined citations/references, multiply defined labels, and overfull boxes. It requires at most 30 total main-PDF pages, including title, references, and tables, and an EC no longer than the article. The authoritative page counts, source commit, PDF hashes, and exact-test results are in `revisions/or-r33-piecewise-randomized-20260923/BUILD_VALIDATION.json` after a successful build. Absence of that record means reader publication is not yet validated.

New exact tests and the retained tightness checker are rerun. Historical large-scale timings are retained records, not represented as new runs. No published specialized flow solver or real service dataset is claimed.

## Author-only declarations not supplied

Author identities, affiliations, ORCIDs, coauthor approval, funding/conflicts, permissions, overlapping-submission disclosures, and journal-system submission are not fabricated or certified. This is a repository referee package, not a ScholarOne submission or acceptance decision.
