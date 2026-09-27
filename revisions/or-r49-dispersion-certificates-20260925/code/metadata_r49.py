"""Write reader pointers and measured metadata, never inferred build outcomes."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
BRANCH='revision/ndu-operations-research-r49-dispersion-certificates-20260925'
def run():
    summary=json.loads((R/'results/SUMMARY.json').read_text());buildpath=R/'BUILD_VALIDATION.json';build=json.loads(buildpath.read_text()) if buildpath.exists() else None
    status=('The reader build is pending.' if not build else f"The validated article has {build['main_nonreference_pages']} nonreference pages ({build['pages']['main']} total), the mathematical companion {build['pages']['electronic_companion']} pages, the response {build['pages'].get('RESPONSE_TO_REFEREES','not built')} pages, and the reproduction record {build['pages']['COMPUTATIONAL_RECORD']} pages. The abstract has {build['abstract_words']} words. Build status: {build['status']}.")
    text=f'''# NDU — Operations Research R49

**Limited-Memory Renewal Contracts: Exact Eligibility Pooling and Certified Joint Design**

Current branch: `{BRANCH}`. Scientific parent: `939cce84881a1d1eabf93aa3a2d3f4f4417ce53f` (R48). Latest reviewed report: the R45 independent report at `260a5224c55e0326d9da7f0c813b4a3fcab7671f`. No later referee report is invented. R46–R48 developments are preserved.

## Read and re-review

The repository root `main.pdf` and `electronic_companion.pdf` are the current article and mathematical companion. The directory `revisions/or-r49-dispersion-certificates-20260925/` contains `RESPONSE_TO_REFEREES.pdf`, `COMPUTATIONAL_RECORD.pdf`, readable source, the precommitted protocol, code, every result, and independent certificates. The computational record is separately identified code-and-experiment reproduction material, not another proof appendix.

## New mathematical contribution

Terminal-first pooling retains every individual cap and cost within a common eligible catalog prefix. Its exact service-cost correction depends only on the last eligible selected symbol and is paid once on the ordered path. One eligibility class therefore admits an exact polynomial joint algorithm for variable history count, catalog size and budget, including interior promises, nonuniform weights, opening charges and zero quadratic service costs. It does not enumerate books or use a larger alphabet.

For multiple eligibility classes, a second identity yields exact group-box price bounds. A repaired mean net and certified subdivision have an explicit accuracy exponent of E−1, where E is the number of eligible prefixes. This remains exponential when eligibility complexity varies. No unrestricted hardness result, fully polynomial relative approximation, or universal computational speed ranking is asserted. Classical resource allocation is credited as a subroutine, not relabeled as a new algorithm.

## Executed evidence

All 24 immutable paired instances meet tolerance 0.001, versus 14/24 historical harmonic intervals; 19 new intervals have zero rational width. Eighteen gaps improve, five are equal, and one slightly worsens while remaining below tolerance. All 16 common-eligibility cases are exactly solved in one node, through 1,024 histories. The 24 multi-class stress requests include 10 unresolved tighter requests; every case remains available.

All 64 semantic certificates pass independent primal-dual, Bellman, complete-cover, and original-policy checks. Regressions include 564 price/enumeration comparisons, 72 mean recoveries, 10 single-class global comparisons, 11 boundary optima, 5 multi-class intervals and 16 rejected certificate corruptions. The preceding R48 regression also passes. The 36 numerical MIP envelope solves expose every status, time, node count, gap, envelope allowance and bracket; numerical bounds are not rational certificates. Current recorded time-limit count: {summary['mip_time_limits']}.

These are declared synthetic inputs, not calibrated operational observations. `LOCAL_EXECUTION.json` preserves pre-publication metrics separately. `results/study.json` and `results/mip.json` identify the actual publication environment and timings after remote execution. R48 measurements remain historical; they are not new matched-machine timing claims.

## Reproduce

```bash
R=revisions/or-r49-dispersion-certificates-20260925
python "$R/code/tests.py"
python "$R/code/study_r49.py"
python "$R/code/verify_r49.py"
python "$R/code/response_r49.py"
python "$R/code/build_r49.py"
python "$R/code/metadata_r49.py"
python "$R/code/preservation_r49.py"
```

The study resumes complete saved cases without selecting new inputs. For fresh timings, use a separate checkout and remove only that copy's R49 generated `results/` directory before running; keep `PROTOCOL.json` unchanged. Never overwrite committed evidence. Check a single certificate without any optimizer with `python "$R/code/check_pooling.py" path/to/certificate.json.gz`. Publication pins Python 3.13, SciPy 1.17.0, SymPy 1.14.0, and PyMuPDF 1.26.7; the actual environment is recorded.

## Formatting and preservation

{status} The build checks undefined citations/references, duplicate labels, overfull boxes and the presence of all 53 antecedent mathematical statements plus four new theorems. The complete new proofs remain in the article. Format validation is not an editorial acceptance claim.

`CONTENT_MAP.json` records intact relocation of earlier mathematics and tables. `PRESERVATION_MANIFEST.json` compares every inherited Git blob with the immutable R48 parent. Exact predecessor copies preserve replaced reader entry points and indexes. The review branch, main branch, and all earlier revision branches are unchanged.
'''
    (ROOT/'README.md').write_text(text)
    (R/'README.md').write_text(text)
    (ROOT/'NDU_OR_submission_checklist.md').write_text('# Operations Research R49 submission checks\n\n'+status+'\n\nAnonymous title and PDF metadata; 11-point type; one-and-a-half spacing; one-inch margins; text-only abstract; equation-free introduction; author-year references; tables following references. All four new proofs remain in the article. Historical mathematics is preserved in the article or companion. No calibrated application, universal runtime claim, or unrestricted hardness result is asserted. Exact and numerical evidence are distinguished.\n')
if __name__=='__main__':run()
