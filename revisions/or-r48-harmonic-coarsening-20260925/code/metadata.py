from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
B='revision/ndu-operations-research-r48-harmonic-coarsening-20260925'
def run():
    s=json.loads((R/'results/SUMMARY.json').read_text())
    build=json.loads((R/'BUILD_VALIDATION.json').read_text()) if (R/'BUILD_VALIDATION.json').exists() else None
    text=f'''# NDU — Operations Research R48

**Limited-Memory Renewal Contracts: Harmonic Coarsening and Certified Joint Design**

Branch: `{B}`. Scientific parent: `df1e192fd0846315ff0938e57d797efcd04109aa` (R47). The latest review remains the R45 report at `260a5224c55e0326d9da7f0c813b4a3fcab7671f`; R46 and R47 developments are retained, not overwritten.

## Read the revision

`main.pdf` and `electronic_companion.pdf` are the current paper and mathematical companion. `revisions/or-r48-harmonic-coarsening-20260925/RESPONSE_TO_REFEREES.pdf` answers the major and minor R45 comments. `COMPUTATIONAL_RECORD.pdf` in that directory preserves the complete earlier computational narratives and gives every new paired and MIP case. It is separately identified repository reproduction evidence.

## New mathematical results

Weighted harmonic curvatures give a dominating optimistic model for the same eligible groups and cap guard. The proof aggregates terminal rewards and intermediate service separately; it does not assume a false pointwise cost domination. Exact within-group allocation recovers the original contract with unchanged book, charges, group means, individual caps, promise, and realized ceilings. Its supporting prices and clipping comparison are independently checked.

Square-root curvature bins give a second-order cost dispersion bound, including zero costs. The accuracy-dependent dimension is at most `1 + E (1 + ceil(2L/epsilon)) (1 + ceil(sqrt(2 Gamma/epsilon)))`, replacing the preceding linear inverse-accuracy cost factor. This is a dimension improvement, not a polynomial runtime claim in accuracy. The adaptive cover remains potentially exponential in that dimension. There is no new hardness assertion for unrestricted eligibility complexity and no FPTAS claim.

## Executed evidence

The targeted 24-case paired study includes up to {s['max_histories']} histories. Harmonic aggregation certifies {s['harmonic_complete']}/24 original-space gaps within 0.001; the minimum-curvature comparator certifies {s['minimum_complete']}/24. All {24-s['harmonic_complete']} unresolved harmonic cases remain, with maximum gap {s['max_harmonic_gap']:.8f}. A tighter reduced optimum is not claimed to improve every interrupted bound or runtime. The twelve exact primary comparisons show {s['strict_harmonic_reference_improvements']} strict harmonic upper-model improvements and no reversals.

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

'''
    if build:text+=f"The validated build has {build['main_nonreference_pages']} nonreference article pages, {build['pages']['electronic_companion']} companion pages, an abstract of {build['abstract_words']} words, and zero undefined references, citations, duplicate labels, or overfull boxes. All {build['retained_math_labels']} antecedent mathematical labels remain in the article or companion, with four new statements.\n\n"
    text+='''Historical derivations, proofs, reports, measurements, and earlier revision branches are preserved. The current reader entry points and index files have exact predecessor copies. `CONTENT_MAP.json` identifies the intact relocation of mathematical and computational sections. `PRESERVATION_MANIFEST.json` audits every inherited Git blob against the immutable R47 base. Neither review, earlier revision, nor main branches are modified. Format validation is not an editorial acceptance claim.
'''
    (R/'README.md').write_text(text);(ROOT/'README.md').write_text(text)
    checklist='# Operations Research R48 submission checks\n\n'
    checklist+='Anonymous title and PDF metadata; 11-point text; one-and-a-half spacing; one-inch margins; author-year references; equation-free introduction; 180-word abstract; horizontal-rule tables after references.\n\n'
    if build:checklist+=f"Validated article: {build['main_nonreference_pages']} nonreference pages. Mathematical companion: {build['pages']['electronic_companion']} pages. Full response: {build['pages'].get('RESPONSE_TO_REFEREES','pending')} pages. See the complete BUILD_VALIDATION.json, not a source-only page estimate.\n\n"
    checklist+='The repository Computational Reproduction Record is separate from the journal companion. All prior mathematical statements/proofs remain in the main article or mathematical companion. No application calibration, empirical deployment, fully polynomial accuracy dependence, or unrestricted hardness classification is asserted. Exact and numerical certificates are distinguished.\n'
    (ROOT/'NDU_OR_submission_checklist.md').write_text(checklist)
if __name__=='__main__':run()
