# Accepted Service Adaptation — Operations Research R25

**Current manuscript:** *Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains*.

R25 is a theory-centered response to the September 23 R24 referee report. The isolated delivery branch is `revision/ndu-operations-research-r25-20260923`. It starts from review commit `9080e29443191f9bb415ab0a213af446d4ce3be3`; the reviewed scientific predecessor is `63bbb843e1bbe7cac2170dc7d317d4cf18bb2bb8`. No default or review branch is edited.

## Referee reading order

Read `main.pdf` (source `main.tex`), then `electronic_companion.pdf` for extended proofs and exact experimental specification. The point-by-point reply is `revisions/or-r25-20260923/RESPONSE_TO_REFEREE.md`. The key results are Theorem 4.1 (restriction-release frontier, reduced curvature, first continuation-slack bottleneck), Theorem 5.1 (comparator-adjusted continuation rents), Proposition 5.2 (optimized friction path), and Theorem 6.1 (sufficient promised-payment state). Propositions 7.1–7.2 support comparator reuse and local outer-comparator loss.

The new experiments compare all five optimized contract classes on 48 common instances, examine eight contexts at ten uncertainty radii, and validate a four-anchor comparator cache. The raw coefficients, policies, dual bounds, exact examples, and separate verifier are under `revisions/or-r25-20260923/`. The current matched-learning conclusion remains negative; no new speed advantage is asserted.

## Preserved research archive

`revisions/or-r25-20260923/predecessor/` contains byte-identical R24 source/PDF pairs for the main paper, formal companion, computational record, and historical supplement, together with its bibliography and reading guides. `PREDECESSOR_SHA256.json` verifies them. All previous revision directories and review reports remain unchanged. The root `computational_supplement.pdf` and `historical_supplement.pdf` remain the historical documents, not new R25 evidence. Their original labels and provenance are retained.

Use `revisions/or-r25-20260923/ARCHIVE_GUIDE.md` for the theory lineage and evidence boundaries. The current main/EC are the journal-facing argument; the archive is not an extra chain of required formal supplements.

## Replay, regeneration, and build

Independent replay requires only Python's standard library:

```bash
python -S revisions/or-r25-20260923/replay.py --check
python -S revisions/or-r24-20260923/replay.py --check
```

To regenerate the new designed evidence, install the pinned packages in `requirements.txt` within the R25 directory. The numerical proposals use OSQP and CasADi's HiGHS/IPOPT interfaces; acceptance is determined by the independent rational verifier, not solver status. No neural model is fitted in R25.

```bash
R=revisions/or-r25-20260923
python "$R/structural_checks.py"
python -S "$R/promise_checks.py"
python "$R/study.py" all
python -S "$R/replay.py"
bash "$R/build.sh"
python "$R/check_package.py"
```

The LaTeX build needs the standard AMS, NewTX, natbib, endfloat, geometry, and xr-hyper packages. The build filters external-label files to labels only and runs four paired passes; `main.bib` preserves and extends the bibliography while the current manual bibliography is `revisions/or-r25-20260923/references.tex`. `MANIFEST.json` records the actual published source, PDF, and evidence hashes. The publication workflow checks out the final generated commit for a second replay and attaches status `ndu-or-r25/final-sha` to that commit.

Exact replay proves statements about the stored models, bounds, and finite examples. It does not establish field robustness, a continuous-state grid error rate, an end-to-end learning speedup, or journal acceptance. This repository delivery is for further author/referee review, not a journal submission.
