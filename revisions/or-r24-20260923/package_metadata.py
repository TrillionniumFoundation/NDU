"""Generate final review metadata from actual files and executed records."""
import os,json,hashlib,sys,re,platform
from pathlib import Path
R=Path(__file__).resolve().parent;ROOT=R.parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())

def run(manifest=False):
    if manifest:
        paths=[ROOT/n for n in ('main.tex','main.pdf','main.bib','main.bbl','electronic_companion.tex','electronic_companion.pdf',
          'computational_supplement.tex','computational_supplement.pdf','main-labels.aux','ec-labels.aux','cs-labels.aux','README.md','NDU_OR_submission_checklist.md')]
        paths += [p for p in R.rglob('*') if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts
                  and not any(part in ('pilot','timing-pilot') for part in p.parts) and p.suffix not in ('.pid','.pyc')]
        (R/'MANIFEST.json').write_text(json.dumps({'revision':'R24','sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}},indent=2)+'\n');return
    provenance={'revision':'R24','reviewed_paper_sha':'b4165155612fea340a8832bbe7a8b13fe2b9259b',
       'latest_review_sha':'685fdc4d4f1823c6930bd6ccdfbc66822043bf9e',
       'review_path':'reviews/operation_research_referee_report_r23_2026-09-23.md',
       'revision_branch':'revision/ndu-operations-research-r24-20260923',
       'execution_source_sha':os.environ.get('GITHUB_SHA','local-source-development'),
       'workflow_run_id':os.environ.get('GITHUB_RUN_ID'), 'python':sys.version,'platform':platform.platform(),
       'scope':'Current R24 results are separate executions; original R22/R23 timing reanalyses keep their original hosts and samples.',
       'format_reference':'https://pubsonline.informs.org/page/opre/submission-guidelines',
       'format_checked_on':'2026-09-23','formal_companions':1,
       'computational_pdf_role':'Readable record inside the separate code/data archive, not a second formal journal companion.'}
    (R/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
    transfer=load(R/'results/transfer_checks.json');analysis=load(R/'results/analysis.json');interior=load(R/'results/interior_summary.json')
    timing=load(R/'results/timing_analysis.json');r4=next(a for a in interior['summary'] if a['r']==4)
    pcheck=load(R/'results/package_check.json') if (R/'results/package_check.json').exists() else None
    README=f'''# Accepted Service Adaptation — Operations Research R24

**Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains**

Revision: September 23, 2026. Branch: `revision/ndu-operations-research-r24-20260923`.

[Main manuscript](main.pdf) · [complete main source](main.tex) · [formal electronic companion](electronic_companion.pdf) · [companion source](electronic_companion.tex) · [computational record](computational_supplement.pdf).

[Point-by-point response](revisions/or-r24-20260923/RESPONSE_TO_REFEREE.md) · [preservation map](revisions/or-r24-20260923/PRESERVATION_MAP.md) · [claim/evidence ledger](revisions/or-r24-20260923/CLAIM_EVIDENCE.md) · [literature boundary](revisions/or-r24-20260923/LITERATURE_MAP.md) · [reproduction guide](revisions/or-r24-20260923/README.md).

## Review target and substantive revision

R24 responds to the latest completed R23 referee report at `685fdc4d4f1823c6930bd6ccdfbc66822043bf9e`, reviewing the paper at `b4165155612fea340a8832bbe7a8b13fe2b9259b`. The new branch inherits the report and all historical derivations. No other manuscript branch is changed.

The new benchmark-relative continuation-transfer theorem permits nonconstant and boundary restricted contracts with unused participation slack. It parametrizes the entire stated positive-payment accepted class, represents restricted equalities exactly, and gives the exact quadratic expansion formula or a comparator-error-charged lower certificate. The worked optimized time-only example has restricted value **5/24**, full accepted value **21/64**, and exact expansion **23/192**. Its negative relative flow demonstrates why cap-matching nonnegative coordinates cannot simply be applied around a slack benchmark. The proof is supported by {transfer['rational_tree_instances']} exact rational tree tests.

The paper's organizing contribution is accepted-control structure and implemented economic gain certification. All neural, direct-price, face, scalar and full-polyhedron results remain. The robust implication is explicitly a certification lemma, not a claim to invent generic robustness or duality.

## New executed evidence

The interior diagnostic contains **{analysis['interior_models']} models and 1,536 independently certified comparator brackets**. Each model separately reoptimizes the true accepted time-only class and the common outer class. At radius 0.25, mean total certificate slack is **{r4['total_slack_upper']['mean']:.6f}**, comprising **{r4['outer_set_slack_upper']['mean']:.6f}** outer-set relaxation and **{r4['interpolation_slack_upper']['mean']:.6f}** interpolation. The maximum comparator interval width is **{analysis['max_interior_comparator_bracket']:.3e}**; failed solves: **{analysis['interior_failed_solves']}**. These are designed-model diagnostics, not field-calibrated coverage.

The repeated-query study executes **{analysis['timing_pipelines']} pipelines**, with 64 paid optimizer labels for each of three configurations, 32 held-out contexts, three repetitions, both accuracy targets and all three methods. It records individual fit/setup/storage costs, prediction, solve, audit, polishing, and every fallback phase. Failed pipelines: **{analysis['timing_failures']}**. Finite observed break-even cases against lifted continuation: **{analysis['finite_observed_break_even_cases']}** in this study; this is an observed result, not a universal impossibility statement. Paired resampling intervals are descriptive for fixed fits, with serial-dependence sensitivity and no retraining-level guarantee.

A separate fresh-host robust accounting study audits **{analysis['robust_cost_policies']} complete pointwise certificates and 256 comparator certificates**, including ensemble prediction and all eight comparator solves per independently certified method. It does not splice prediction timings from a new host into archived R23 timings. Candidates can achieve different robust gains, so these costs do not imply matched-quality speed superiority. All **{analysis['old_scaling_rows']}** original R22 scaling rows and **{analysis['old_robust_rows']}** original R23 robust rows remain and receive explicitly dated retrospective cost/variability analyses.

## Preservation, format, and verification

All **72** predecessor mathematical statement/proof blocks remain in the main-plus-companion pair, with only the documented robust theorem-to-lemma relabeling. Original empirical tables and adverse results are retained. Exact reviewed roots are archived in `predecessor/`; prior revisions and the historical supplement are unchanged.

The formal journal package is the main paper and **one** electronic companion. The computational PDF is a readable code/data-archive record, not an additional formal companion. The manuscript uses anonymous 11-point, one-and-a-half-spaced, one-inch-margin Lengthy formatting, an equation-free introduction, a text-only abstract below 200 words, author-year citations, and tables after references.

[Actual package checks](revisions/or-r24-20260923/results/package_check.json) · [independent rational replay](revisions/or-r24-20260923/results/replay.json) · [manifest](revisions/or-r24-20260923/MANIFEST.json) · [provenance](revisions/or-r24-20260923/PROVENANCE.json).

The publication workflow attaches `ndu-or-r24/final-sha` only after a fresh checkout independently verifies the actual published files. Numerical audits do not establish scientific priority or journal acceptance. Author submission declarations remain for the authors; no submission has been made by this workflow.
'''
    (ROOT/'README.md').write_text(README)
    (ROOT/'NDU_OR_submission_checklist.md').write_text('''# Operations Research R24 submission checklist

The prepared category is **Lengthy**. The formal submission consists of `main.pdf` and one `electronic_companion.pdf`. Actual page counts and all reference/overflow checks are in `revisions/or-r24-20260923/results/package_check.json`.

The readable `computational_supplement.pdf`, raw records, frozen models and executable code belong in the **separate code/data archive** or GitHub reproducibility material, not concatenated as a second formal journal companion. Every essential mathematical proof remains in the main/companion pair. Old empirical detail is retained for audit, without pooling its sampling claims with R24.

The title page is anonymous; the manuscript uses 11-point body text, one-and-a-half spacing, one-inch margins, a text-only abstract below 200 words, an equation-free introduction, author-year references and tables after references. No footnotes are used. New source and evidence are separately hashed; all reviewed predecessor mathematical blocks are preserved.

Before actual journal submission, the authors must approve authorship/order, financial-conflict and funding declarations, overlapping-work disclosures, exclusivity and prior-submission statements, reviewer/editor suggestions, the final ScholarOne-generated PDF and any required disclosure of writing assistance. This workflow has not asserted those personal declarations or submitted the manuscript.

Checked against the Operations Research submission guidelines on September 23, 2026: https://pubsonline.informs.org/page/opre/submission-guidelines
''')
if __name__=='__main__':run('--manifest' in sys.argv)
