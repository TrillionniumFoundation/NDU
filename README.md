# NDU — Operations Research R53

## Current readers

**Finite-Catalog Renewal Design by Selected-Boundary Resource Paths**

Branch: `revision/ndu-operations-research-r53-catalog-safe-certificates-20260926`.
Scientific parent: R52 `7bdfda8f84b84f491e80b50a86089c37ea4c7f3a`.
Latest referee report: `4f0b662bd4184fc77fb57bd09c339bffb6213a69`, the second independent R49 report. The first independent report is also addressed. No later review of R52 is implied.

Read the root `main.pdf` and `electronic_companion.pdf`, followed by
`revisions/or-r53-catalog-safe-certificates-20260926/RESPONSE_TO_REFEREES.pdf`.
The same current manuscript sources and PDFs are in this revision directory.

## New results and direct referee response

R53 retains the full R52 finite-catalog joint-design theory and adds an eligibility-independent capacity potential for every arc; a sharp individual-target-box anchor envelope for simultaneous safe non-anchor command deletion; and refinement-safe global-certificate transfer to an explicitly bound original instance. Computing all screening bounds takes O(kN) arithmetic operations. Root promises, individual constraints, and command budgets are unchanged.

The general additive scheme still has no eligibility-class-dependent exponent; the exact common-prefix theorem remains exact. The corrected dyadic theorem, class-box support, threshold analysis, production-module extension, and all earlier proofs remain available. A positive-width certificate is not called an exact solution.

## Validation and reproduction

```bash
R=revisions/or-r53-catalog-safe-certificates-20260926
python "$R/code/assemble.py"  # in the Git checkout
python "$R/code/run.py"
python "$R/code/build.py"
python "$R/code/preservation.py"  # requires the scientific parent in Git
python "$R/code/package.py"
```

`run.py` reruns the unchanged R52 regression, restores its original committed result, and records the new execution only under R53. It then executes the fixed R53 study and regenerates its table. The protocol was committed before the experiments at `a2cbabde34abc94aa158367cd38ea6afcd789819`.

R53 checks 120 random models, 2,332 capacity identities, 542 neighboring-context envelopes, and 129,448 pointwise deletion inequalities. All 120 exhaustive before/after optima agree; 149 commands are screened. Twenty original-instance transfer certificates pass and fourteen corruptions are rejected. All twelve controlled refinement cases are reported, with full and reduced exact certificates, exhaustive optima, class counts, state counts, bytes, and separate timings. Their absolute tolerance is 1/10; they do not replace the inherited 1/1000 stress study. The first test expectation incorrectly retained an ineligible endpoint; the original diagnostic and correction are disclosed.

To check a transferred certificate independently:

```bash
python "$R/code/check_screening.py" "$R/results/certificates/k64-insert8.json.gz" \
  --expected-sha256 <digest-from-the-requested-instance>
```

The digest is found in the corresponding `results/CONTROLLED.json` record. An embedded self-hash is not authentication. Ordinary Python execution is required: the inherited resource checker rejects optimization flags that disable assertions. Standard-library rational arithmetic handles optimization and checking; PyMuPDF is used for the PDF audit, and a TeX installation with newtx is needed to build readers.

## Evidence boundaries and preservation

All inputs remain synthetic. Screening does not remove arbitrary anchors or certify free refinements without an exclusion proof. Its transfer certificate can be larger than a full certificate on small cases, and its independent context checker has an intentionally redundant polynomial cost. The underlying R52 mixed-integer evidence retains its numerical, rather than exact-rational, interpretation. No equal-memory or universal-speed ranking is claimed.

The 44 R52 requests, 42 subdivision comparisons, twelve numerical envelope solves, and historical unresolved requests are not overwritten. R53 reruns the inherited regression, not every historical experiment. `LOCAL_EXECUTION.json` separates the local summary from remote publication measurements. `BUILD_VALIDATION.json` records measured page counts, labels, hashes, and layout diagnostics. `PRESERVATION_MANIFEST.json` checks every inherited Git blob against the scientific parent; replaced root readers have exact predecessor copies. Main, review, and earlier revision branches are not modified. The code-and-data archive contains assembled readers and dependencies; in an unpacked archive without Git, start at `run.py` rather than reassembling or invoking the Git-only preservation audit.
