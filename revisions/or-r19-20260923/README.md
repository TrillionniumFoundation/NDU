# R19 reproduction and review guide

Run from the repository root with Python 3.13. Install `revisions/or-r16-20260922/requirements.txt` and `PyMuPDF==1.26.7`; LaTeX requires NewTX, endfloat, xr-hyper, and the packages imported by the ordinary root sources. A C compiler is needed for the existing CasADi/OSQP bridge. Set `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` for the recorded timing protocol.

## Reproduce the new scientific records

```sh
python revisions/or-r19-20260923/boundary_checks.py
python revisions/or-r19-20260923/nonquadratic_checks.py
python revisions/or-r19-20260923/matched_cost.py
python -S revisions/or-r19-20260923/replay.py
python revisions/or-r19-20260923/analyze.py
bash revisions/or-r19-20260923/build.sh
python revisions/or-r19-20260923/check_package.py
python revisions/or-r19-20260923/package_metadata.py
```

These commands leave earlier scientific directories untouched. The existing R16 frozen models and observations are inputs, not newly retrained replacements. The matched-cost program separately measures all label and model-fitting costs on the current host while deploying only the frozen models. Times and resulting tables will change with hardware; mathematical and exact-certificate checks must still pass. The complete publication workflow also rebuilds the predecessor label indices before current assembly; those indices are already included under `predecessor/` in the published package.

## Verify a frozen published checkout without recomputation or mutation

```sh
python -S revisions/or-r19-20260923/replay.py --check
python revisions/or-r19-20260923/check_package.py --verify-manifest
```

The first verification uses Python's standard library only. It independently replays all 16,384 multistage deployment policies, 128 inherited structural policies, and 128 new boundary reference/proposal policies; verifies 128 response-gap identities; and requires four intentionally invalid records to be rejected. The second checks the actual PDFs, final TeX logs and labels, exact predecessor blobs, scientific counts, and every manifest hash.

## Scientific and version navigation

`RESPONSE_TO_REFEREE.md` addresses the complete latest actual R14 report. `PRESERVATION_MAP.md` maps every retained component to current or immutable predecessor documents. `REVISION_PLAN.json` and `DEVELOPMENT_NOTE.md` distinguish new work from retrospective analysis and developmental corrections. `sections/general_bridge.tex` contains the full global and inexact-response proofs. `sections/experiment.tex` and `sections/companion.tex` interpret every cohort and comparator without suppressing unfavorable outcomes. `results/` holds all current primary evidence, while original R16 observations remain at their original paths.

The only current reviewer entry points are the root `main.pdf` and `electronic_companion.pdf`. Both root TeX sources are fully expanded ordinary text, with modular assembly scripts retained for reproducibility. The historical supplement and exact predecessor PDFs preserve older continuous-time, nonlinear, scalar, and verified-cell material in full. No encoded transport is needed to read or compile the published manuscript.
