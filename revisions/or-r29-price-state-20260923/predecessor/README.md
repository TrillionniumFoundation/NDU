# Accepted Service Adaptation — Operations Research R28

**Revision branch:** `revision/ndu-operations-research-r28-20260923`  
**Review base:** `61aff783672ce39745713f5cefbcf83d8748ebd6`  
**Scientific predecessor:** R27 `85fe1a799a192758a93a423bbb6d213ab9f04cce`.

## Read the revision

- [Current paper](main.pdf) · [LaTeX](main.tex)
- [Electronic companion](electronic_companion.pdf) · [LaTeX](electronic_companion.tex)
- [Point-by-point referee response](revisions/or-r28-20260923/RESPONSE_TO_REFEREES.md)
- [Novelty and assumptions matrix](revisions/or-r28-20260923/NOVELTY_MATRIX.md)
- [Exact replay](revisions/or-r28-20260923/results/replay.json)
- [Full phase-resolved scaling evidence](revisions/or-r28-20260923/results/evidence.json)
- [Build/preservation report](revisions/or-r28-20260923/BUILD_REPORT.md)
- [Manifest](revisions/or-r28-20260923/MANIFEST.json)
- [Latest referee report, unchanged](reviews/operation_research_referee_report_r27_2026-09-23.md)

The central result is a shared-table bridge: one ex ante policy table survives the promised-payment recursion; normalized continuation and restriction prices produce an optimized-comparator certificate through a root table LP. A dual-completeness proof states explicitly that discovering an exact finite certificate need not have polynomial storage or construction cost. New results include a net implementation-cost decision, a certified refresh rule, and an interior-valid certificate for a declared adaptive policy.

The exact two-period example distinguishes the pooled value 37/50 from the unrestricted value 53/50. With unit linear release cost, the optimal release is 1/15. The adaptive continuum example certifies gain 9/1024. These are exact synthetic examples, not field estimates. The scaling design is deliberately block-separable and compares exact rational certificate accounting with a specialized exact solve; it is not a dense-QP speedup claim. Strict tolerances cause frequent cache refreshes.

## Reproduce

```bash
python -S revisions/or-r28-20260923/research.py
python -S revisions/or-r28-20260923/verify.py
python -S revisions/or-r28-20260923/make_tables.py
bash revisions/or-r28-20260923/build.sh
python revisions/or-r28-20260923/check_package.py --manifest
python -S revisions/or-r28-20260923/verify.py --check
```

The evidence generator and independent verifier require only Python's standard library. The checker does not import the generator. Linux subprocesses measure isolated configuration peak RSS; timings are platform observations, not reproducible performance constants. The inherited R24–R27 replays are unchanged. LaTeX dependencies match R27; the PDF inspection additionally uses PyMuPDF.

## Preservation and scientific status

All earlier derivations, reports, data, code, and revisions remain at their original paths. The six R27 reader files are preserved byte for byte under `revisions/or-r28-20260923/predecessor/`. Root reader files are updated; no unrelated branch is changed. Inherited-source hashes and final document hashes are verified independently. The latest review is part of the branch ancestry and remains unchanged.

This is a substantive author revision for another referee review, not a journal submission, acceptance claim, or independent proof of novelty. Its manuscript uses the Operations Research anonymous, author–year, 11-point, 1.5-spaced format; exact pagination is recorded in the build report.
