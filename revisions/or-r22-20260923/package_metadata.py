"""Write current review entry points, provenance, and non-circular artifact hashes."""
from pathlib import Path
import os,json,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[1];P='revisions/or-r22-20260923'
def j(p):return json.loads((R/p).read_text())
def run():
 c=j('results/package_check.json');v=j('results/validation_summary.json');rep=j('results/replay.json')
 title='Accepted Service Adaptation with Neural Differential Utility: Continuation Prices and Certified Gains'
 intro=f'''# Neural Differential Utility — Operations Research R22

**{title}**

Revision: September 23, 2026. Branch: `revision/ndu-operations-research-r22-20260923`.

## Current reviewer entry points

[Main manuscript](main.pdf) · [ordinary complete main source](main.tex) · [electronic companion](electronic_companion.pdf) · [ordinary complete companion source](electronic_companion.tex).

[Point-by-point referee response]({P}/RESPONSE_TO_REFEREE.md) · [preservation map]({P}/PRESERVATION_MAP.md) · [literature/novelty map]({P}/LITERATURE_MAP.md) · [claim/evidence ledger]({P}/CLAIM_EVIDENCE.md) · [reproduction guide]({P}/README.md).

This is the complete R22 review package, not the earlier R20 plan. It responds to the [September 23 R20 report](reviews/operation_research_referee_report_r20_2026-09-23.md), review commit `18381729edf8d15a536ebef16abf6660ee0db48f`. The reviewed plan-only R20 tip was `45553b28f40c92a14895b8b82d8739e608f6d4b1`; its complete manuscript was R19 at `cb4f8644652ebe92f0aac5294baaff898d97f5cf`. Exact original root files are preserved under [{P}/predecessor/]({P}/predecessor/). Earlier revision directories, reviews, historical supplement and other branches are not overwritten.

## Scientific revision

The common target is the certified gain from expanding an already optimized accepted policy class. The full continuation, friction, transfer, resource-price and inexact-response theory is retained. New proofs separate certificate error into box, resource, switching and participation terms, identify a price-repair floor, establish monotone resource/equality-price repair, prove complete dual attainment and a convergent full-price repair without strict feasibility, certify context transport, charge regularization bias, and connect implemented decisions with a reoptimized restricted contract. A theorem-level literature map distinguishes accepted-control consequences from established sensitivity, duality, decision-focused learning, dual prediction and learned warm starts.

The original neural and non-neural results, including adverse comparisons, remain in a dated companion section. New experiments include a structure-aware lifted primal--dual classical continuation baseline, full-polyhedron scaling, frozen deterministic neural and direct-price ensembles, an optimized time-only-amendment comparator, and independent in-distribution/shifted validation with fresh numerical workspaces. Positive gain against an optimized restricted class is not equated with neural acceleration or field validity. All operational primitives are synthetic and known.

## Executed and independently checked evidence

[5,120 matched-cost pipelines]({P}/results/matched_rows.json) include prediction, response, repair, audit, price polishing and actual fallback under identical final tolerances. [Final deterministic validation]({P}/results/validation_summary.json) contains 2,048 IID and 512 shifted contexts for each of two frozen ensembles, with four simultaneous conditional expected-gain bounds against the true optimized restricted value. [Full-class scaling]({P}/results/scaling_summary.json) contains ten geometries, 640 audited training labels and 800 deployment attempts; failures are retained. [Independent rational replay]({P}/results/replay.json) checks {rep['independent_policy_replays']:,} new policy records, 320 component identities and four rejected invalid controls. [Complete dual-repair checks]({P}/results/complete_dual_checks.json) additionally verify 225 exact optima, 3,600 projected-gradient steps and 450 context transports. The inherited R19 standard-library replay is also rerun without modifying historical inputs.

The lower confidence bounds in the final recorded study are:

| Population | Frozen deterministic rule | Conditional expected-gain lower bound |
|---|---|---:|
'''
 for row in v['summary']:intro+=f"| {row['domain']} | {row['method']} | {row['expected_restricted_gain_lower']:.6f} |\n"
 intro+=f'''
These are four simultaneous 95% one-sided bounds conditional on the frozen rules, for their respective declared synthetic context laws. The comparator gate itself requires optimization and is not evidence of a speed advantage. The stateful developmental pilot is excluded; [the correction record]({P}/audit_notes/STATE_ISOLATION_CORRECTION.json) identifies the fresh final protocol.

## Format, provenance and verification

The main PDF has {c['main_pdf_pages']} pages ({c['main_pages_excluding_references']} excluding references); the companion has {c['companion_pdf_pages']} pages. The {c['abstract_words']}-word abstract, 11-point text, one-and-a-half spacing, one-inch margins, anonymous title pages, mathematical-notation-free introduction, author-year references and tables after references are checked against the journal's **Lengthy** manuscript format. All current references resolve. Verbatim preservation checks cover {c['preserved_mathematical_blocks']} original mathematical statements/proofs.

[Package checks]({P}/results/package_check.json) · [manifest]({P}/MANIFEST.json) · [provenance]({P}/PROVENANCE.json) · [submission checklist](NDU_OR_submission_checklist.md).

The workflow attaches `ndu-or-r22/final-sha` to the actual final published commit after independent final-checkout replay, PDF and hash verification. A successful source checkpoint alone is not called a completed revision. Author approval of authorship, conflicts and submission declarations is still required. This branch is a referee-ready research package, not journal acceptance.
'''
 (ROOT/'README.md').write_text(intro)
 (ROOT/'NDU_OR_submission_checklist.md').write_text(f'''# Operations Research R22 submission checklist

## Current artifacts and journal format

- Current ordinary root R22 main source/PDF and electronic companion source/PDF exist and agree.
- Main: {c['main_pdf_pages']} total pages, {c['main_pages_excluding_references']} excluding {c['main_reference_pages']} reference pages; **Lengthy** category.
- Companion: {c['companion_pdf_pages']} pages, no longer than main.
- Anonymous letter-size pages, 11-point font, 1.5 line spacing, one-inch margins.
- One-paragraph abstract: {c['abstract_words']} words, no mathematical notation. Introduction has no equations or mathematical notation.
- Author-year alphabetized references; no text footnotes; tables after references with no vertical rules.
- No unresolved references/citations or overfull text lines; current sources are expanded ordinary TeX, not wrappers or encoded transports.
- Subject classifications and area of review appear on the title page; current code/data availability statement follows the last main section.

## Scientific/provenance checks

- Latest actual R20 referee report is addressed point by point, not replaced by a generic response to an older report.
- Exact complete R19 root files have pinned hashes; {c['preserved_mathematical_blocks']} original mathematical blocks remain verbatim across current manuscripts.
- Full original experimental block and adverse outcomes are retained in the companion.
- Matched-cost, deterministic validation, full-class scaling, theory checks and independent rational replays are actual executed records.
- Scale failures, numerical-state correction, engineering-label amendment and known-model/conditional-inference scope are disclosed.
- Neural, direct-price and classical methods are distinguished; no unsupported universal neural acceleration, misspecified-model validity or field calibration claim is made.
- Final published SHA, not merely an input-source SHA, must have `ndu-or-r22/final-sha` success before a clean final-checkout claim.

## Author-side declarations still requiring approval

Authorship/order, ORCID, funding, financial conflicts, overlapping publications, duplicate-submission declarations, permissions and final journal submission must be confirmed by the authors. No declaration is fabricated by this package.

Official preparation source checked September 23, 2026: https://pubsonline.informs.org/page/opre/submission-guidelines
''')
 (R/'README.md').write_text('''# R22 reproduction and review guide

Run from the repository root using Python 3.13, a C compiler, the pinned R16 requirements, PyMuPDF 1.26.7, and LaTeX packages imported by the current sources. Set `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1` and `MKL_NUM_THREADS=1`. Do not run another CPU-intensive benchmark concurrently with timing.

```sh
python -m pip install -r revisions/or-r16-20260922/requirements.txt PyMuPDF==1.26.7
bash revisions/or-r22-20260923/run_all.sh
```

`run_all.sh` executes matched cost, fresh final deterministic validation and structural scaling sequentially, then exact theory checks, independent new and inherited rational replay, automatic table analysis, complete manuscript assembly and four-pass cross-reference resolution, package checks and metadata/hashes. It reuses the eight frozen R16 models; scale models are separately fitted on the declared scale training populations. It never changes earlier scientific directories or review reports. The `predecessor/` snapshot is already present in a completed checkout and is not regenerated from the new root manuscripts.

The initial publication source checkpoint takes the exact R19 snapshot and verifies `PREDECESSOR_SHA256.json`; this is not a completed manuscript claim. The workflow subsequently commits actual ordinary R22 manuscripts and data, then checks out that final SHA independently. A failed source checkpoint is not mislabeled a publication.

## Frozen final-checkout verification without recomputation or mutation

```sh
python -S revisions/or-r22-20260923/complete_dual_checks.py --check
python -S revisions/or-r22-20260923/replay.py --check
python -S revisions/or-r19-20260923/replay.py --check
python revisions/or-r22-20260923/check_package.py --verify-manifest
```

The replay needs the Python standard library only. It reconstructs rational feasibility, full and restricted equality constraints, independent upper bounds, monotone fixed-decision repair, all final target checks, the four conditional lower bounds and intentionally invalid-record rejections. It does not trust a solver status or rounded table. The package check verifies actual PDF/source/label counts, pinned predecessor hashes, verbatim mathematical preservation and all manifest hashes. It does not rerun timing or rewrite results.

`DESIGN.json` specifies seeds, final populations, model counts and targets. `audit_notes/` discloses the state-isolation correction and engineering label-backend amendment; these are not external preregistration. Timings vary across hosts, while exact feasibility and certificate inequalities must verify. `CLAIM_EVIDENCE.md` identifies the exact scope of each result. The main/companion PDFs at repository root are the current review objects; historical source, PDFs and experiments remain available at their original paths.
''')
 prov={'revision':'R22','inherited_unexecuted_source':'c2d25791bd1f4c2b1801a446376a86c50eb381fe','evidence_workflow_run':os.getenv('EVIDENCE_RUN','local-development'),'evidence_artifact':os.getenv('EVIDENCE_ARTIFACT','local-development'),'review_commit':'18381729edf8d15a536ebef16abf6660ee0db48f','complete_manuscript_base':'cb4f8644652ebe92f0aac5294baaff898d97f5cf',
   'source_checkpoint':os.getenv('SOURCE_CHECKPOINT',os.getenv('GITHUB_SHA','local-development')),
   'workflow_run':os.getenv('GITHUB_SERVER_URL','https://github.com')+'/'+os.getenv('GITHUB_REPOSITORY','TrillionniumFoundation/NDU')+'/actions/runs/'+os.getenv('GITHUB_RUN_ID','local-development'),
   'final_sha_validation_context':'ndu-or-r22/final-sha','timing':'Actual recorded publication-host measurements; development pilots not substituted.',
   'inference':'Conditional frozen deterministic rules; independent final populations after state-isolation correction; no future-training or field-validity claim.'}
 (R/'PROVENANCE.json').write_text(json.dumps(prov,indent=2)+'\n')
 names=['README.md','NDU_OR_submission_checklist.md','main.tex','main.pdf','main.bib','main.bbl','electronic_companion.tex','electronic_companion.pdf','historical_supplement.tex','historical_supplement.pdf','main-labels.aux','ec-labels.aux','legacy-main-labels.aux','legacy-ec-labels.aux','history-labels.aux']
 paths=[ROOT/n for n in names]
 for directory in [R,ROOT/'revisions/or-r16-20260922',ROOT/'revisions/or-r19-20260923',ROOT/'reviews']:
  for p in directory.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts and p.name!='MANIFEST.json' and p.suffix not in ['.pid','.so'] and p.name not in ['run-all.log','execution.log']:
    paths.append(p)
 manifest={'revision':'R22','sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}}
 (R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('R22 review metadata and manifest:',len(manifest['sha256']),'files')
if __name__=='__main__':run()
