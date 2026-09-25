# NDU — Operations Research R47

**Limited-Memory Renewal Contracts: Joint Design with Certified Response Coarsening**

Revision branch: `revision/ndu-operations-research-r47-joint-certificates-20260925`.

Read `main.pdf`, `electronic_companion.pdf`, and `revisions/or-r47-joint-certificates-20260925/RESPONSE_TO_REFEREES.pdf`.

## Review lineage and new mathematics

This revision responds to the independent R45 report at `260a5224c55e0326d9da7f0c813b4a3fcab7671f`, retaining the subsequent R46 development at `9f260e0d6c4e06cf4227f96865a88f4dab67e58e`. Neither review nor preceding revision branches are edited.

R47 adds four proved statements: optimistic response coarsening with an exact original-contract lift; a dispersion bound; a variable-history additive scheme for rational quadratic finite-catalog inputs with bounded eligibility complexity and primitive scales; and monotone refinement. Weighted average caps preserve total capacity, minimum curvatures give an upper relaxation, and a minimum-cap guard prevents infeasible anchors. Recovery restores every individual cap, exact promise, original ceiling, selected-command budget and charge. The complexity exponent no longer depends on raw history count under the theorem's bounded-parameter conditions. Accuracy dependence can still be very large; this is not a fully polynomial or multiplicative approximation scheme.

## Executed evidence and limitations

All 24 new joint instances achieve an independently checked original-space gap at most 0.001; the largest is approximately 0.000783098. Inputs include up to 256 distinct histories (256 exact response types), not replicated branches. Under the matched nominal limits, uncoarsened boxes complete 19/24 and priced-prefix completes 21/24. These are clustered synthetic inputs, not calibrated operational evidence or a universal runtime comparison.

Four separate stress cases deliberately fail the requested tolerance under coarse grouping, with gaps 0.0421875, 0.044375, 0.11 and 0.67. Refinement yields exact solutions in these four cases; no universal one-split claim is made. All eight stages remain in the record.

The package contains 56 exact semantic certificates, 72 exhaustive original/reduced comparisons, 602 fixed-book lifts, 441 dispersion checks, 216 accuracy partitions, 56 refinement comparisons and 18 rejected semantic certificate mutations. All 12 primary instances also have exact all-book joint references and separate uneliminated MIP envelope comparisons (24 numerical solves). Numerical solver bounds are explicitly not rational certificates. The four unresolved R46 box cases and its stronger prefix outcomes remain intact in the companion.

## Reproduction and timing provenance

Canonical benchmark times describe the recorded local Python 3.13.5 / SciPy 1.17.0 runs. Publication replays deterministic searches at the recorded node counts, checks semantic certificate hashes, and records replay/verification time separately. Semantic witnesses omit timing fields; the original measured times remain in case records. Protocols are locally frozen, not externally preregistered.

```bash
R=revisions/or-r47-joint-certificates-20260925
python "$R/code/tests.py"
python "$R/code/evidence.py"
python "$R/code/response.py"
python "$R/code/build.py"
python "$R/code/preservation.py"
```

The independent checker accepts a certificate JSON or gzip file:

```bash
python "$R/code/check_coarsening.py" "$R/results/certificates/primary-00-coarse.json.gz"
```

For fresh timings, copy the repository to a separate working directory and remove only that copy's generated R47 case records/certificates before running `benchmark.py`, `stress.py`, and `mip_compare.py`. Do not overwrite committed canonical evidence. `PROTOCOL.json`, `MIP_PROTOCOL.json`, and `STRESS_PROTOCOL.json` identify all requested cases, limits, and supplementary-study timing. `REPLAY_MANIFEST.json` and `results/REPLAY_VALIDATION.json` connect all semantic witnesses to their reconstructions.

## Readers, style, and preservation

The anonymous article uses 11-point type, one-and-a-half spacing, one-inch margins, an equation-free introduction, an abstract below 200 words, author-year references and horizontal-rule tables. `BUILD_VALIDATION.json` records actual page counts, references, layout warnings, all reader-input hashes, and 45 retained antecedent mathematical labels plus four new statements. The main has 39 nonreference pages and the companion 39 pages in the validated build. These are format checks, not an editorial acceptance claim.

All 2,308 inherited files are audited. Outside six explicitly replaced current readers/indexes, 2,302 inherited files remain byte-identical; the six original versions remain in `predecessor/`. `CONTENT_MAP.json` records the intact relocation of the R46 computational discussion to the companion. No historical derivation, theorem, numerical result, review or prior branch is deleted. The scope and original contributions are preserved.
