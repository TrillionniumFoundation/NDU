# NDU — Operations Research R52

## Current manuscript

**Finite-Catalog Renewal Design by Selected-Boundary Resource Paths**

Branch: `revision/ndu-operations-research-r52-resource-path-20260925`.
Scientific source: R49 `2098592a99e47d36cc9fd16311f21d1858fa6e1e`.
Parent and latest report: `4f0b662bd4184fc77fb57bd09c339bffb6213a69`.
The first independent R49 report is also addressed. R50 and R51 contained no later scientific manuscript at inspection; neither is overwritten.

Read `main.pdf`, `electronic_companion.pdf`, and `revisions/or-r52-resource-path-20260925/RESPONSE_TO_REFEREES.pdf`.
The revision directory contains all readable source, code, frozen protocol, execution records, independent certificates, preservation manifest, and the code-and-data reproduction archive.

## Structural advance

The exact selected-boundary identity converts arbitrary-eligibility finite-catalog joint design into a scalar-resource path. A capacity identity permits recovery at the original promise and command budget. Rational quadratic primitives admit an additive scheme polynomial in histories, catalog size, budget, binary input length, and inverse normalized accuracy, with no eligibility-dependent exponent. Exact common-prefix optimization remains a stronger special case. The article gives full proofs, catalog and threshold robustness, and a separate compatible-production model.

This is not an exact unrestricted polynomial algorithm, a relative-error scheme, a hardness classification, or a universal solver-speed claim. All operational inputs are synthetic. Numerical mixed-integer optimization and enumeration are faster on the small comparison models.

## Reproduce

```bash
R=revisions/or-r52-resource-path-20260925
python "$R/code/tests.py"
python "$R/code/study.py" --phase all
python "$R/code/readers.py"
python "$R/code/build.py"
python "$R/code/preservation.py"
```

Python must run without `-O`, because independent checkers reject invalid witnesses with assertions. A single new certificate can be checked offline using `python "$R/code/check_resource.py" path/to/certificate.json.gz`. The study imports unchanged historical allocation modules; the reproduction archive includes those files at their original paths. Numerical comparisons use SciPy 1.17.0. Publication uses Python 3.13.5 and PyMuPDF 1.26.7; actual versions are recorded.

The protocol was committed before the full study and discloses development pilots. Completed cases resume only with the unchanged protocol hash. For fresh timings use a separate checkout and remove only its generated R52 `results/` directory; never overwrite committed evidence. Local execution is separately preserved in `LOCAL_EXECUTION.json`; journal tables use `results/` from the publication environment.

## Evidence and preservation

All 44 prescribed cases, 42 subdivision comparisons, and 12 numerical envelope solves are retained. The study verifies 80 exact certificates; the six difficult models meet tolerance 0.001. Positive-width certificates are not called exact solutions. The controlled two-class case returns a policy below its exhaustive optimum; its interval is valid. All 24 historical stress requests, including ten unresolved requests, remain unchanged.

Every inherited source and result is preserved. Replaced root reader entry points have exact predecessor copies. `PRESERVATION_MANIFEST.json` checks all inherited Git blobs; `CONTENT_MAP.json` identifies the preserved proof locations. Main and review branches, and all earlier revision branches, are unchanged. `BUILD_VALIDATION.json` gives measured page counts, mathematical labels, PDF hashes, abstract length, and typesetting diagnostics; a successful build is not an editorial acceptance claim.
