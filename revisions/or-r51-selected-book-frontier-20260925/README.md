# R51 revision package

See the [root README](../../README.md) for readers, exact guarantees and complete reproduction commands.

## Substantive changes

The new mandatory-selected-prefix recurrence supplies exact original-budget price bounds. A binary completion cover combines those bounds with a free-union relaxation and charge-aware safe deletion. Its standard-library checker independently checks original-space policies, mandatory levels, Bellman inequalities and complete coverage. The elementary fixed-budget XP enumeration implication is inherited from the earlier complexity proposition, not presented as a new result; the new algorithm contributes bounds, pruning and compact certificates.

Catalog refinement now has an explicit partition theorem, an unused-splitting-level example, selected-book class bounds, exact signature-cell stability, a threshold-robust formulation, and an affected-history bound. A derived capacity-reservation model is checked by integrating uniform demand. The group-mean method retains an explicit initial-width dyadic product, zero-width handling and a clearly stated stopping rule. A one-third stopping width needs four leaves; the coarse constant depends on whether the stopping step is epsilon/(2Ld) or epsilon/(4Ld).

## Executed evidence

All 182 declared certificate requests pass independent verification: 134 are exact zero-width rational intervals and 48 remain open. All six unchanged difficult instances close exactly in at most 21 visited nodes, agreeing with the preexisting exhaustive values. All 20 strict interior common-prefix instances are exact, including 1,024 histories. The 48 matched-class requests, 24 catalog-refinement requests, and 12 near-boundary requests retain every interruption. Prices reduce nodes but increase measured time in all displayed matched pairs; no universal speedup is claimed.

All 18 direct tangent/secant mixed-integer solves are retained with statuses, variables, binaries, nodes, elapsed and full wall times, primal/dual values, residuals and envelope errors. Each envelope and each timed tree receives its own three-second allowance; the two-envelope pair is not charged as one solve. Floating-point MIP bounds are not exact rational certificates.

The new tests pass 664 fixed-book comparisons, 720 mandatory-price comparisons, 80 global comparisons, 40 interruption checks and 20 dyadic cases; 15 corrupted certificates are rejected. Boundary checks add 18 joint and 276 price comparisons. All 64 inherited certificates are revalidated, and the complete old regression suite is rerun in an isolated output directory. Maximum current certificate size is 54454 gzip bytes; largest numerator and denominator lengths are 96 and 103 bits.

All data are synthetic. The protocol was frozen before local execution, not preregistered remotely. Local and publication-run environments and results are distinguished. No calibrated demand data, full variable-budget complexity classification, FPT guarantee, or universal solver ranking is asserted.

## Reproduction

Run from the repository root in a separate checkout:

```sh
R=revisions/or-r51-selected-book-frontier-20260925
python "$R/code/tests.py"
python "$R/code/study.py"
python "$R/code/additional_checks.py"
python "$R/code/tables.py"
python "$R/code/build.py"
python "$R/code/metadata.py"
# To validate saved intervals without rerunning optimization:
python "$R/code/study.py" --verify
python "$R/code/check_completion.py" path/to/certificate.json.gz
```

The exact checker uses only the Python standard library. Optimization uses inherited exact modules, SciPy 1.17.0 and SymPy 1.14.0; the publication environment pins Python 3.13.5 and PyMuPDF 1.26.7. TeX uses newtx with standard LaTeX packages. `PROTOCOL.json` freezes the population; `results/study.json` records every input, rational endpoint and saved certificate; `results/mip.json` records both numerical formulations. Rerunning the optimizer should use a clean results directory in a separate checkout to obtain new timings, not silently replace the committed measured record.

## Preservation and scope

All 57 reviewed mathematical statements remain in the current readers or complete unchanged archive. The original derivation sources and earlier successful and failed experiments are unchanged. Only six root reader/entry files are replaced, and each original is copied byte for byte into `revisions/or-r51-selected-book-frontier-20260925/predecessor/`. `CONTENT_MAP.json` enumerates each statement and `PRESERVATION_MANIFEST.json` audits the entire reviewed tree. No review branch, main branch, or other revision branch is modified. Author disclosures and any ScholarOne submission remain the authors' responsibility; see `NDU_OR_submission_checklist.md`.
