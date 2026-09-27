# R24 reproduction and review guide

This revision responds to the completed R23 referee report. Start with the root `main.pdf`, its formal `electronic_companion.pdf`, and `RESPONSE_TO_REFEREE.md`. `computational_supplement.pdf` is a readable computation/history record inside the separate reproducibility archive. It is not an additional formal journal companion. All 72 predecessor formal statements and proofs remain in the main/companion pair.

## Provenance and source organization

`PREDECESSOR_SHA256.json` pins exact reviewed roots. `predecessor/` preserves them. `PROVENANCE.json` distinguishes the reviewed scientific SHA, latest review SHA, execution source SHA and workflow run. Earlier revision directories and their frozen models/observations are unchanged. `MANIFEST.json` identifies the complete final reviewed package; the independent final-checkout workflow validates the actual published commit.

`sections/` holds the new prose and transfer theorem; `materialize_revision.py` builds ordinary, standalone root TeX files from the pinned predecessors plus those sections and generated tables. The manuscript is not an overlay that requires a reader to infer missing text. The code/data package retains all relocated numerical tables and historical execution detail.

## Reproduce all new results

Use one numerical process at a time for timing work. Set `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and `MKL_NUM_THREADS=1`. The publication workflow records exact dependency versions and execution-host information. The numerical proposal layer uses the inherited CasADi OSQP library through the existing C bridge, not a new solver asserted to be the state of the art.

```bash
python revisions/or-r24-20260923/transfer_checks.py
python revisions/or-r24-20260923/interior_study.py
python revisions/or-r24-20260923/timing_study.py
python revisions/or-r24-20260923/robust_cost.py
python -S revisions/or-r24-20260923/replay.py
python revisions/or-r24-20260923/analyze.py
python revisions/or-r24-20260923/materialize_revision.py
bash revisions/or-r24-20260923/build.sh
python revisions/or-r24-20260923/package_metadata.py
python revisions/or-r24-20260923/check_package.py
python revisions/or-r24-20260923/package_metadata.py --manifest
python revisions/or-r24-20260923/check_package.py --verify-manifest
```

The pre-execution design is in `DESIGN.json`; the supplementary fresh robust-cost protocol was committed before that additional execution in `ROBUST_COST_PROTOCOL.md`. They are design declarations, not external preregistrations. Pilot executions are not used as final evidence. `interior_study.py --pilot` and `timing_study.py --pilot` write to separate pilot directories.

## Independent checking without numerical dependencies

```bash
python -S revisions/or-r24-20260923/replay.py --check
python -S revisions/or-r23-20260923/replay.py --check
python -S revisions/or-r22-20260923/complete_dual_checks.py --check
```

R24 replay reconstructs every new rational feasibility/dual calculation and recomputes the inherited vertex upper certificates used by the interior diagnostic. It checks the 1,728 deployed decisions, 192 optimizer-label certificates, 1,536 interior-comparator certificates, 96 fresh robust decisions and 256 fresh robust comparator certificates. Negative controls exercise invalid primal, equality, dual, and coefficient/interpolation inputs. The mathematical proof of the new transfer theorem is separately supported by 64 rational identity tests and an exact KKT example; testing is not substituted for the proof.

## Main machine-readable outputs

`interior_summary.json`, `interior_rows.json`, and `interior_certificates.jsonl.gz` give two-sided comparator brackets and total/outer/interpolation slack distributions. `timing_rows.json` gives all seven timed components, both certificate targets, fallback decisions and conditional iterations; `timing_setup.json` and `timing_fits.json` disclose labels, individual fits and memory scopes. `timing_analysis.json` reports paired savings, descriptive resampling intervals, a serial-dependence sensitivity analysis and costs at six query volumes. `robust_cost_summary.json` separates candidate, prediction, comparator and complete online times. The two retrospective reanalysis files retain the original R22/R23 host observations without splicing new-host timing into old totals.

The exact arithmetic applies to the audit. Optimizer training labels are numerical statistics certified to the stated tolerance, not mathematical optima obtained at no cost. Bootstrap intervals are descriptive conditional summaries, not guarantees over retraining; the robust timing candidates can achieve different maximin certificate values and are not a matched-quality speed comparison.

## Submission and review

The formal Lengthy submission is `main.pdf` plus one `electronic_companion.pdf`. Supply the source, code, frozen models, raw records and this README separately as a code/data ZIP or the GitHub archive. The computational PDF belongs in that archive and need not be concatenated into the formal journal submission. The final package checker records actual page counts, 72-block preservation, complete cross-references and PDF hashes. Author approval is still required for authorship, conflicts, overlapping submissions, funding, and final submission declarations. No submission or editorial acceptance is performed by this revision workflow.
