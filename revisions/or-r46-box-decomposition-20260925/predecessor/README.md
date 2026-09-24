# NDU — Operations Research R45

**Limited-Memory Renewal Contracts: Budgeted Compression and Certified Joint Design**

Read `main.pdf`, `electronic_companion.pdf`, and `revisions/or-r45-budgeted-compression-20260924/RESPONSE_TO_REFEREES.pdf`.

Revision branch: `revision/ndu-operations-research-r45-budgeted-compression-20260924`.

Latest report: `reviews/operation_research_referee_report_r44_independent_harsh_2026-09-24.md`, on review commit `91583abe77208ec4ed25b5fbc5a15f89d54fcd6f`. The reviewed R44 manuscript tip is `fe066aac2862fc89fc8eb2e19fd98b4b96e6d5a3`.

## New results

Exact conditional memory--charge frontier, global polynomial catalog optimization at saturation, a same-budget additive scheme for fixed branch count, local distortion certificates, and charge-aware compression with inexact price supports and exact target/risk repair. The conditional frontier is not mislabeled as global target optimization. The target net has accuracy exponent k - 1 and does not assert an FPTAS with variable k. All original memory budgets, opening charges, root promises and realized ceilings remain explicit.

## Executed evidence

The new package records 288 exact conditional budget comparisons on 144 instances; 144 repairs; ten semantic mutation rejections; twenty completed same-budget target-net comparisons; 36 joint comparisons with all budgets through twice the original limit; 24 independently formulated MIP comparisons (48 envelope solves); twelve heterogeneous scaling cases with three timing repeats; 22 exact continuous-reference comparisons; and ten inexact-support error checks. The MIP brackets are numerical, not rational global certificates.

The core target portfolio attains 35 of 36 original-budget optima. Its charged exception is retained. A declared greedy safeguard attains all 36 on these synthetic inputs; this observation is not a theorem about all instances. No customer data, field calibration or deployment is claimed.

## Reproduction

Use Python 3.12, SciPy 1.17.0 and SymPy. Readers require pdflatex with newtx and pgfplots, and poppler.

```bash
R=revisions/or-r45-budgeted-compression-20260924
python "$R/code/tests.py"
python "$R/code/study.py"
python "$R/code/extended.py"
python "$R/code/tables.py"
python "$R/code/build.py" prepare
# Scientific sources and prepared evidence are committed before final build.
python "$R/code/build.py" build
```

`code/target_net.py` returns its requested global accuracy only when its target net is complete. An interrupted run still supplies a feasible incumbent and explicitly withholds that certificate.

## Preservation and provenance

The current article and companion retain all 34 mathematical label identifiers from the R44 readers and add seven labeled results. `CONTENT_MAP.json` maps every old root reader input to its current or preserved-reader location. All older source directories and results remain byte-preserved. The complete predecessor main and companion PDFs are in `predecessor/`. No prior branch is updated.

`PRESERVATION_MANIFEST.json` checks the full inherited Git tree. `BUILD_VALIDATION.json` records the committed scientific source, actual toolchain, complete reader input hashes, PDF hashes, reference/layout checks and executed evidence. Only the exact R45 branch is allowed to publish these readers. The publication workflow commits human-readable sources before building and then pushes the validated PDFs/evidence to this branch.
