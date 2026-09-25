# NDU — Operations Research R48

**Limited-Memory Renewal Contracts: Harmonic Coarsening and Certified Joint Design**

Branch: `revision/ndu-operations-research-r48-harmonic-coarsening-20260925`. Scientific parent: `df1e192fd0846315ff0938e57d797efcd04109aa` (R47). The latest review remains the R45 report at `260a5224c55e0326d9da7f0c813b4a3fcab7671f`; R46 and R47 developments are retained, not overwritten.

## Read the revision

`main.pdf` and `electronic_companion.pdf` are the current paper and mathematical companion. `revisions/or-r48-harmonic-coarsening-20260925/RESPONSE_TO_REFEREES.pdf` answers the major and minor R45 comments. `COMPUTATIONAL_RECORD.pdf` in that directory preserves the complete earlier computational narratives and gives every new paired and MIP case. It is separately identified repository reproduction evidence.

## New mathematical results

Weighted harmonic curvatures give a dominating optimistic model for the same eligible groups and cap guard. The proof aggregates terminal rewards and intermediate service separately; it does not assume a false pointwise cost domination. Exact within-group allocation recovers the original contract with unchanged book, charges, group means, individual caps, promise, and realized ceilings. Its supporting prices and clipping comparison are independently checked.

Square-root curvature bins give a second-order cost dispersion bound, including zero costs. The accuracy-dependent dimension is at most `1 + E (1 + ceil(2L/epsilon)) (1 + ceil(sqrt(2 Gamma/epsilon)))`, replacing the preceding linear inverse-accuracy cost factor. This is a dimension improvement, not a polynomial runtime claim in accuracy. The adaptive cover remains potentially exponential in that dimension. There is no new hardness assertion for unrestricted eligibility complexity and no FPTAS claim.

## Executed evidence

The targeted 24-case paired study includes up to 256 histories. Harmonic aggregation certifies 14/24 original-space gaps within 0.001; the minimum-curvature comparator certifies 11/24. All 10 unresolved harmonic cases remain, with maximum gap 0.03159548. A tighter reduced optimum is not claimed to improve every interrupted bound or runtime. The twelve exact primary comparisons show 5 strict harmonic upper-model improvements and no reversals.

All 48 new exact semantic certificates are independently checked. The 24 direct MIP solves expose status, time, node count, solver gap, envelope error, and numerical bracket width. Numerical MIP bounds are not rational certificates. Exact regression tests report 32 ordered joint comparisons, 199 lifts, 65 dispersion checks, 96 accuracy partitions, 32 refinements, and 14 rejected certificate mutations. Prior R46/R47 failures and successful cases remain intact.

`PROTOCOL.json` specifies all cases, limits, and the final node-accounting wrapper. `results/study.json` and `results/mip.json` identify actual publication-run measurements. `LOCAL_EXECUTION.json` separately preserves earlier local metrics; timings are not silently exchanged across environments. These are declared synthetic inputs, not independently calibrated operational data.

## Reproduce and check

```bash
R=revisions/or-r48-harmonic-coarsening-20260925
python "$R/code/tests.py"
python "$R/code/study.py"
python "$R/code/verify.py"
python "$R/code/response.py"
python "$R/code/build.py"
python "$R/code/preservation.py"
```

`study.py` resumes its completed records without selecting new cases. For fresh measured timings, work in a separate copy and remove only that copy's generated R48 results and final protocol. Do not overwrite the committed evidence. A certificate can be checked without rerunning the optimizer with `python "$R/code/check_harmonic.py" path/to/certificate.json.gz`.

## Readers and preservation

The validated build has 39 nonreference article pages, 37 companion pages, an abstract of 180 words, and zero undefined references, citations, duplicate labels, or overfull boxes. All 49 antecedent mathematical labels remain in the article or companion, with four new statements.

Historical derivations, proofs, reports, measurements, and earlier revision branches are preserved. The current reader entry points and index files have exact predecessor copies. `CONTENT_MAP.json` identifies the intact relocation of mathematical and computational sections. `PRESERVATION_MANIFEST.json` audits every inherited Git blob against the immutable R47 base. Neither review, earlier revision, nor main branches are modified. Format validation is not an editorial acceptance claim.
