# NDU — Operations Research R46

**Limited-Memory Renewal Contracts: Two-Sided Decomposition and Certified Joint Design**

Revision branch: `revision/ndu-operations-research-r46-box-decomposition-20260925`.

Start with `main.pdf`, `electronic_companion.pdf`, and `revisions/or-r46-box-decomposition-20260925/RESPONSE_TO_REFEREES.pdf`.

## Review and scientific change

This revision responds to `reviews/operation_research_referee_report_r45_independent_harsh_2026-09-25.md` at `260a5224c55e0326d9da7f0c813b4a3fcab7671f`. The reviewed R45 manuscript tip was `9c52e2d58d69a8d653c3b50e2c860b35db04dc7f`.

The new core is an exact two-sided price-path decomposition on target boxes, exact catalog-response type aggregation, and an adaptive original-budget joint interval with a finite positive-accuracy theorem. A rising-only price oracle is not valid on general target boxes; the manuscript supplies an exact counterexample and the corrected two-sided recurrence. The method never changes the command budget, charges, root promise, or realized ceilings. Its worst-case accuracy dependence remains exponential in the number of distinct response types. No general hardness classification or uniformly superior runtime is claimed.

## Executed evidence

600 exact all-book price comparisons; 24 additional rational joint interval comparisons; 2,793 finite-lattice coverage checks; genuine clipping tests; one-call single-branch regression; 11 rejected semantic certificate mutations. All 32 primary/scaling joint intervals have independently checked coverage and original-space feasible policies. At absolute tolerance 0.001, 28 box runs complete and four remain unresolved. The inherited priced-prefix baseline completes all 32; its stronger outcomes are retained. The separate 12-case grid comparison retains incomplete nets, and the direct uneliminated MIP comparison includes all 24 primary instances and both envelopes (48 solves), with per-case times, nodes, gaps and numerical widths.

The 128/256-history experiments explicitly use exactly repeated types. All data are synthetic. No field calibration, deployment evidence, general-purpose polynomial joint solver, or guaranteed heuristic exactness is asserted.

## Reproduction

Canonical benchmark timings were measured in the recorded local Python 3.13.5 / SciPy 1.17.0 environment. They are not relabeled as GitHub Actions timings. Publication reconstructs the exact rational witnesses at their recorded node counts and checks their canonical byte hashes; regeneration/verification timings are recorded separately.

```bash
R=revisions/or-r46-box-decomposition-20260925
python "$R/code/tests.py"
python "$R/code/verify_saved.py"
python "$R/code/response.py"
python "$R/code/tables.py"
python "$R/code/assemble.py"
python "$R/code/build.py"
python "$R/code/preservation.py"
```

For a fresh timing study, copy the source hierarchy to a separate working directory, remove only that copy's R46 generated benchmark JSON and certificate directory, then run `benchmark.py`, `comparators.py`, and `price_compare.py`. Do not erase the canonical committed evidence. All protocols and code are supplied, and resumed runs retain completed cases.

The independent checker accepts an uncompressed certificate JSON via `python code/check_certificate.py certificate.json`. `results/certificates/` contains the gzip-compressed canonical certificates. Their file hashes appear in `results/joint.json`.

## Readers and preservation

The current main article and companion retain all 41 R45 mathematical statement labels. The local validated readers have 36 pages each (34 nonreference main pages); the remote build audit is authoritative. The 182-word abstract, anonymous title page, author-year references, layout checks and complete reader-input hashes are recorded in `BUILD_VALIDATION.json`.

All inherited derivations, source directories and numerical records remain unchanged. Exact former root readers are preserved in the new `predecessor/` directory. `PRESERVATION_MANIFEST.json` checks the full inherited Git tree; `CONTENT_MAP.json` identifies retained and relocated reader inputs. Historical numerical details are retained in complete predecessor readers rather than misrepresented as newly executed evidence. The report, preceding revision, main branch and other branches are not edited.
