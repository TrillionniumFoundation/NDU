# NDU — Operations Research R42

## Current manuscript

Read the repository-root **main.pdf** and **electronic_companion.pdf**: *Limited-Memory Renewal Contracts: Participation, Quantization, and Exact Design*. The editable roots are `main.tex` and `electronic_companion.tex`. This is an anonymous lengthy Operations Research manuscript, with theorem-critical new proofs in the article.

This revision responds to the R39 independent referee report at immutable review commit `6e48c4858a54317f8189664f5a57fb5cc4ac6e4f`. It belongs only to `revision/ndu-operations-research-r42-certified-joint-design-20260924`. No main, review, R40, R41, or earlier revision branch is changed. R40 remained at the review base and the observed R41 tip contained only an initial transport fragment; neither was mistaken for a new reviewed manuscript.

## Scientific additions

The new eligible-prefix theorem unifies arbitrary root promises, bounded realization overrun, continuous codebooks, and actual selected-level charges. The pathwise and expected institutions are endpoints. For rational quadratic primitives and a quadratic charge nonnegative on the action interval, a finite cell and stationary-face algorithm globally optimizes the continuous book and endogenous targets. It is an exponential exact reference algorithm, not a new polynomial Monge algorithm.

For nonnegative Lipschitz charges, a mesh theorem bounds continuous-versus-grid value loss while preserving every branch target, the root promise, and realization ceilings exactly. This yields an additive approximation scheme for each fixed symbol budget. New results also cover homogeneous repeated-cap aggregation, strict off-cap stability under small charges, and an exact interior charged example where pathwise randomization improves on every deterministic book.

The new computational study includes continuous promise-gap paths, 32 joint promise/risk/price designs, exact continuous-versus-grid comparisons, and separate scaling measurements of the new all-promise catalog problem. All data are synthetic. Previous 16,384-branch measurements are inherited saturated-frontier evidence, not timings of the new algorithm.

## Reproduce

Use Python 3.12 or later, SymPy for the independent test oracle, and a TeX installation with newtx, pgfplots, natbib, xurl and standard AMS packages. From the repository root:

```sh
python revisions/or-r42-certified-joint-design-20260924/code/build.py prepare
# In a Git checkout, commit the prepared scientific inputs before building.
python revisions/or-r42-certified-joint-design-20260924/code/build.py build
```

`prepare` reruns new exact checks and synthetic studies, runs predecessor verification in isolated temporary copies, generates tables directly from result JSON, and prepares the referee response. It does not rewrite older revision directories. `build` compiles and cross-references both readers and the response, checks abstract and page limits, rejects undefined references and overfull boxes, and writes `BUILD_VALIDATION.json` with transitive source, result, and PDF hashes. Full-checkout validation also compares inherited tracked paths against the immutable review base.

The key modules are `code/unified.py` (conditional allocation and catalog/grid certificates), `code/faces.py` (global continuous reference), `code/verify.py` (independent checks), and `code/study.py` (parameter studies). `RESPONSE_TO_REFEREES.md`, `.tex`, and `.pdf` provide point-by-point responses to the major concerns and all fifteen specific requests.

## Historical preservation and provenance

All earlier revision directories, proofs, review reports, raw results, and historical supplements remain unchanged. Earlier root readers are copied byte-for-byte to this revision's `predecessor/`. The current manuscript retains the preceding scientific sections and adds the joint design and approximation results; preserved source inputs are recorded in `PRESERVATION_MANIFEST.json`. New publication commits are confined to the named revision branch and do not force-push or merge.

The source transport exists only to deliver locally tested files through the GitHub connector. Its assembler checks every file hash and rejects unsafe paths. The publication workflow expands and commits the actual editable sources before compiling and publishing PDFs; a transport-only commit is not described as a finished reader publication.

No external acceptance decision, formal proof-assistant validation, empirical calibration, or generic polynomial-time continuous algorithm is asserted.
