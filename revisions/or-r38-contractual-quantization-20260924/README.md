# NDU — Operations Research R38

## Current readers

The current anonymous manuscript is **Limited-Memory Renewal Contracts: Participation, Quantization, and Exact Design**. Read `main.pdf` and `electronic_companion.pdf` at repository root. Their editable roots are `main.tex` and `electronic_companion.tex`.

This revision is based on the R37 independent report at review commit `1cf9c8df76437ee71d4291d1001e9c7f055781c5`. It belongs only to branch `revision/ndu-operations-research-r38-contractual-quantization-20260924`; no main/review/earlier-revision branch is modified.

The revision directory is `revisions/or-r38-contractual-quantization-20260924/`. It contains the response to referees in Markdown, TeX and PDF; new theorem sources; exact catalog design code; executable checks; source and preservation manifests; and the prior complete readers in `predecessor/`.

## Scientific changes

The retained saturated continuous frontier and all its proofs are supplemented by an exact full-information alphabet characterization for every root promise, budget-uniform promise stability and a strict nonsaturated institutional-advantage interval, an exact interior promise-allocation reduction, repeated-cap treatment, and global risk-limited catalog design with actual additive codeword charges. Scalar quantization, Wu's matrix-search algorithm, stochastic rounding, dual quantization, and quantized control are explicitly distinguished from the contractual increment.

The catalog theorem is exact for its declared finite feasible catalog. It is not described as an exact grid approximation to every continuous bounded-risk or codebook-cost problem. The 16,384-branch timings are preserved preceding measurements, whereas the R38 catalog studies and exact regressions are newly executed. No empirical service-provider calibration or independent journal acceptance is asserted.

## Reproduce

From the repository root, with Python 3.12 or later and a TeX installation containing newtx, pgfplots, natbib and the usual AMS packages:

```sh
python revisions/or-r38-contractual-quantization-20260924/code/build.py prepare
python revisions/or-r38-contractual-quantization-20260924/code/build.py build
```

The first command runs the new exact checks and synthetic catalog studies, then the unchanged R37/R33–R36 suites in isolated temporary directories. It generates focused reader sources and the referee response without changing any older revision directory. The second command compiles both readers and the response, resolves cross-document labels, rejects undefined references and overfull boxes, checks page/abstract limits, and writes `BUILD_VALIDATION.json` with source and evidence hashes. In a full Git checkout it also checks all inherited tracked paths against the immutable review base.

The publication workflow is scoped to this one revision branch and the revision's `BUILD` trigger. It commits prepared scientific sources before compiling and publishing PDF readers. It never force-pushes or merges another branch.

## Historical preservation

All prior revision directories, historical derivations, review reports and measured result files remain unchanged. Thirteen exact preceding proof blocks move into the current focused companion; their original sources and proof hashes are recorded in `PROOF_PRESERVATION.json`. The complete R37 main article and companion are also retained under `predecessor/`, including the broader compact-response, laminar-allocation, minimal-machine, shared-table and coefficient-event material. That material is preserved, not withdrawn; it need not inflate the submission companion for a renewal theorem that does not use it.
