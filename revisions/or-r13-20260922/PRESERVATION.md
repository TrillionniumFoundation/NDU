# R13 preservation and relocation map

The new branch is based on review commit `5b1a62679f890006d8f6a234160fa9a02dcdbc5a`. Its manuscript predecessor is published R12 commit `a0d25581c8895ab1b820467021e8e9d224ebd063`.

| Predecessor material | R13 disposition |
|---|---|
| R12 model, general stock-identification theory, full-tree balance/cuts/friction interval, margin | Original files unchanged; still inputs of `main.tex` |
| R7 canonical accepted information hierarchy and R10 essential tree appendix | Original files unchanged; still in the main paper |
| R12 acceptance-face theorem, residual theorem, pipeline-selection proposition and proofs | Retained in new `sections/learning_bridge.tex`; only a cross-reference sentence now distinguishes the old stress test from new independent validation; original R12 file remains unchanged |
| R12 noncentered nonlinear experiment, adverse projected gains, boundary instances, and complete timing comparisons | Original `sections/experiment.tex` unchanged and now included verbatim in the current electronic companion; explicitly summarized in the current main paper |
| Earlier diagnostics, failed 992-coordinate actors, cached classical comparisons | Existing companion/archive inputs and all data unchanged |
| Historical diffusion and continuous-time material | Original historical TeX source and subordinate inputs unchanged; archived PDF preserved separately |
| Root manuscript/companion/README/checklist and their prior PDFs | Exact predecessor copies in `predecessor/`; current roots updated for R13 |
| R12 referee report and all earlier reviews | Inherited unchanged from the review base |

`preserve.py` builds a SHA-256 inventory of the reviewed base, excluding only the explicitly replaced root documents. `check_package.py` verifies every inventoried file remains present and byte-identical. The archived root PDFs have their own SHA-256 record. No predecessor numerical observations are dropped or merged with the new sampling distribution.

The archive is preservation, not the burden of proof: all essential new R13 arguments are proved in the main paper. New technical implementation details are in the current electronic companion. No changes are authorized to `main`, any review branch, or another revision branch.
