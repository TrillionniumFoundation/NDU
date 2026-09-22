# R22 reproduction and review guide

Run from the repository root using Python 3.13, a C compiler, the pinned R16 requirements, PyMuPDF 1.26.7, and LaTeX packages imported by the current sources. Set `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1` and `MKL_NUM_THREADS=1`. Do not run another CPU-intensive benchmark concurrently with timing.

```sh
python -m pip install -r revisions/or-r16-20260922/requirements.txt PyMuPDF==1.26.7
bash revisions/or-r22-20260923/run_all.sh
```

`run_all.sh` executes matched cost, fresh final deterministic validation and structural scaling sequentially, then exact theory checks, independent new and inherited rational replay, automatic table analysis, complete manuscript assembly and four-pass cross-reference resolution, package checks and metadata/hashes. It reuses the eight frozen R16 models; scale models are separately fitted on the declared scale training populations. It never changes earlier scientific directories or review reports. The `predecessor/` snapshot is already present in a completed checkout and is not regenerated from the new root manuscripts.

The initial publication source checkpoint takes the exact R19 snapshot and verifies `PREDECESSOR_SHA256.json`; this is not a completed manuscript claim. The workflow subsequently commits actual ordinary R22 manuscripts and data, then checks out that final SHA independently. A failed source checkpoint is not mislabeled a publication.

## Frozen final-checkout verification without recomputation or mutation

```sh
python -S revisions/or-r22-20260923/complete_dual_checks.py --check
python -S revisions/or-r22-20260923/replay.py --check
python -S revisions/or-r19-20260923/replay.py --check
python revisions/or-r22-20260923/check_package.py --verify-manifest
```

The replay needs the Python standard library only. It reconstructs rational feasibility, full and restricted equality constraints, independent upper bounds, monotone fixed-decision repair, all final target checks, the four conditional lower bounds and intentionally invalid-record rejections. It does not trust a solver status or rounded table. The package check verifies actual PDF/source/label counts, pinned predecessor hashes, verbatim mathematical preservation and all manifest hashes. It does not rerun timing or rewrite results.

`DESIGN.json` specifies seeds, final populations, model counts and targets. `audit_notes/` discloses the state-isolation correction and engineering label-backend amendment; these are not external preregistration. Timings vary across hosts, while exact feasibility and certificate inequalities must verify. `CLAIM_EVIDENCE.md` identifies the exact scope of each result. The main/companion PDFs at repository root are the current review objects; historical source, PDFs and experiments remain available at their original paths.
