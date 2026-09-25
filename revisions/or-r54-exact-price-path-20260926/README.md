# NDU — Operations Research R54

## Current paper and review target

**Exact Path Representations for Finite-Catalog Renewal Design**

Revision branch: `revision/ndu-operations-research-r54-exact-price-path-20260926`.
This revision starts from the latest R53 review, commit `fcd7b7ab1719f00e547cd29e94cbb421fab59b0a`, which reviews scientific R53 commit `2e07a4cfb41d8fbc16cd64c3048877d3c8c2a288`.

Read `main.pdf`, `electronic_companion.pdf`, and the R54 `RESPONSE_TO_REFEREES.pdf`.
The current reader sources and duplicate PDFs are also in this revision directory.
`BUILD_VALIDATION.json` contains the measured page counts, mathematical-label checks, source hashes, and PDF hashes. A successful build is not an editorial acceptance decision.

## Scientific changes

The paper gives a direct SUBSET SUM reduction proving NP-completeness of the rational decision problem even with common unit linear reward, zero service costs, uniform probabilities, realization ceilings equal to caps, and a nonbinding command budget. It does not claim strong NP-hardness or a fixed-budget hardness classification.

A separate exact theorem proves that common expected caps admit an optimal singleton or pair under a common reward, even with different full-catalog eligibility prefixes. General heterogeneous caps are not subjected to that restriction.

The selected-boundary proof now includes explicit nested-layer reconstruction and a converse implementation lemma. History-level component packing further extends the primal resource identity to heterogeneous increasing concave terminal rewards. Exact priced paths also support heterogeneous rewards and yield a rational original-instance bound in O((k+m)N^2) arithmetic per oracle. Complete discrete branching gives finite exact termination with potentially exponential worst-case size. It retains valid intervals on controlled interruptions. The polynomial additive resource guarantee and exact common-prefix result remain available. The historical uniform implementation is benchmarked only with its original common-reward kernels.

Forced-command price bounds provide complementary safe fixing for possible anchors. The original non-anchor envelope remains intact and is treated as a sufficient, potentially conservative preprocessing rule, not a general compression guarantee.

## Reproduce

The scientific scripts use exact `fractions.Fraction` arithmetic for proofs. Numerical MIP comparisons use SciPy/HiGHS and have a separate evidence status.

```bash
python -m pip install scipy==1.17.0 sympy==1.14.0 PyMuPDF==1.26.7
R=revisions/or-r54-exact-price-path-20260926
python "$R/code/publication.py"
python "$R/code/build.py"
python "$R/code/preservation.py"  # full Git checkout with the reviewed parent
python "$R/code/package.py"
```

`publication.py` runs every R54 regression, the 142-method comparison, ten anytime runs, 24 screening cases, three sharp screening neighbors, 60 reduction checks, twenty reduction-challenge method runs, and nine production configurations. It generates all journal table values from the actual records. Every method receives the same declared four-second algorithm alarm and 2-GiB process address-space cap. The numerical solver additionally receives two seconds per envelope. Verification has a separate allowance. Actual wall times, native-process overruns, resident memory, and unsuccessful runs are retained. These are controlled synthetic studies, not calibrated operational evidence.

The initial protocol was committed at `310f7d42ad45ff529f40c4cd0c3ac1c1b12cfe14`; the separately disclosed reduction/packing addendum was committed at `97f4fd9b356cfbaadddc96a135952d10c9ef6f6b`. The latter followed the initial study but preceded its reduction checks and challenge executions. Development examples are not described as an unseen test set.

Existing complete run records are resumed only for the unchanged instance. For new timings, make a separate working copy and remove its R54 `results/` directory before running `publication.py`; never overwrite the published evidence in place. The run archive is tied to code hashes by `results/SOURCE_MANIFEST.json` and `results/EXECUTION_AUDIT.json`. Table generation and compilation do not invent completion counts. Local execution summaries are retained separately from the publication run.

For a quick mathematical regression without the full timed comparisons:

```bash
python "$R/code/tests.py"
```

To verify one global certificate independently:

```bash
python "$R/code/check_price.py" path/to/certificate.json.gz --expected-sha256 EXPECTED_MODEL_HASH
```

The expected hash comes from the requested input record, not from trusting the certificate's own declaration. The checker imports neither the new optimizer nor any historical optimizer. It verifies original lotteries and all bounds using a backward at-most-budget recurrence. The optimizer uses a forward exact-count recurrence. The same command dispatches the independently checked singleton/pair certificate format. A valid interval need not meet the requested tolerance; `tolerance_met` states that separately.

Inherited assertion-based checkers require ordinary Python without `-O`. The new checker uses explicit exceptions, but regression assertions are still intended to run enabled. Linux process resource limits are part of the timed protocol; a different operating system requires an explicitly documented protocol adaptation rather than silently omitting the limits.

PDF building needs `pdflatex`, `newtx`, standard mathematical packages, and the retained LaTeX dependencies. `build.py` assembles readers from immutable parent entry points. A source archive without Git already contains the exact predecessor copies and can build directly. The full inherited-file audit requires the Git parent and is not represented as a complete audit of an unpacked subset.

## What the records establish

`results/EXECUTION_AUDIT.json` reports actual completion and limit counts for all 172 timed method runs: the initial 142, ten separate anytime runs, and twenty structural challenge runs. Exact closure, positive-width rational certification, numerical MIP brackets, and fallback bounds have different meanings. All planned results or explicit failures are retained. The reduction challenge is intentionally difficult and includes cases where the new method also fails to meet exact closure within its allowance.

The fixed rational regression verifies 130 models, 2,644 fixed books, 390 restricted price supports, 2,035 nested reconstructions, and 2,644 heterogeneous component packings and optimal-component equalities. Sixty common-cap certificates include forty models with multiple eligibility classes. Thirty models have heterogeneous rewards. The corruption suite includes incomplete binary covers, invalid bounds, wrong instance binding, and invalid original lotteries. The NP reduction is separately checked on sixty integer instances. These finite checks support implementation consistency; the universal statements rely on the manuscript's proofs.

The screening record includes every candidate's charge, envelope slack, exact inclusion/exclusion values, forced-price bound, anchor eligibility, and wholly-ineligible status. Removal rates are reported with quantiles, and the stronger rule's cost includes incumbent search and bound checking. It is not compared to undisclosed internal MIP presolve statistics.

## Preservation and code/data package

Every file inherited from the latest review is retained unchanged unless it is one of the six current root reader entry points. Those six have exact predecessor copies. `PRESERVATION_MANIFEST.json` checks every inherited Git blob and both immutable protocol files. Old main, review, and revision branches are not changed. The original R52/R53 results are not overwritten or described as a full historical rerun.

`CODE_AND_DATA.zip` retains the earlier runnable code/data dependencies at their original relative paths, overlays all R54 source, inputs, results, and certificates, and includes the exact current root-reader predecessors. Complete older reader PDFs also remain in the Git repository. The source transport is only a publication mechanism; readable scientific files are committed before the completed artifact is reported. No transport decoding is needed to read or reproduce the final manuscript.
