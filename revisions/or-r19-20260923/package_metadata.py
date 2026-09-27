#!/usr/bin/env python3
"""Write the current review entry points and a verifiable publication manifest."""
import json, hashlib, os
from pathlib import Path
R=Path(__file__).resolve().parent; ROOT=R.parents[1]
P='revisions/or-r19-20260923'
def run():
    checks=json.loads((R/'results/package_check.json').read_text())
    paired=json.loads((R/'results/reanalysis.json').read_text())['paired_training_comparison']
    body=f'''# Neural Differential Utility — Operations Research R19

**Neural Differential Utility: Accepted Multistage Service Control and Certified Value-Gradient Decisions**

Revision date: September 23, 2026. Branch: `revision/ndu-operations-research-r19-20260923`.

## Current referee entry points

[Main manuscript](main.pdf) · [ordinary complete TeX](main.tex) · [current electronic companion](electronic_companion.pdf) · [companion TeX](electronic_companion.tex).

[Point-by-point response]({P}/RESPONSE_TO_REFEREE.md) · [preservation map]({P}/PRESERVATION_MAP.md) · [reproduction instructions]({P}/README.md) · [submission checklist](NDU_OR_submission_checklist.md).

The main PDF has {checks['main_pdf_pages']} pages, including {checks['main_reference_pages']} reference pages; its {checks['main_pages_excluding_references']} pages excluding references require the journal's **Lengthy** manuscript category. The current companion has {checks['companion_pdf_pages']} pages. The abstract has {checks['abstract_words']} words. Both use anonymous letter-size, 11-point, one-and-a-half-spaced text with one-inch margins, author–year references, and tables after the references.

## Version provenance

The latest actual complete report is [the R14 referee report](reviews/operation_research_referee_report_r14_2026-09-22.md). The branch named `review/operation-research-r16-harsh-20260922` points to R16 research results, not a later report. R17 contains an incomplete transport part and R18 a follow-up plan; neither updated the R14 root manuscript. R19 descends from R18 commit `d23de668070fc29a7073a9e4ef647c8159b0d580`, preserves those historical records, and publishes complete ordinary manuscript files instead of another partial transport.

## Scientific revision

The new global resource-price theorem applies on the complete accepted polyhedron with multistage vector decisions, multiple capacities, nonconstant outside protocols, and endogenous switching signs. An exact Bregman decomposition connects the specified scalar value gradient to regret without an optimal face. A separate inexact-response theorem charges the certified response error and actual implemented repair. The scalar star, verified-cell, full-tree friction, continuous acceptance, and prior nonlinear developments remain available in full at the locations in the preservation map.

All eight R16 training/deployment pairs and all seven methods are now integrated. Derivative supervision improves the specified paired neural comparison, while direct-price and non-neural methods are stronger. New matched-accuracy timing gives classical solvers the same initial tolerance and charges response, repair, certification, and actual refinement. Runtime and break-even counts are host-specific descriptive measurements, not a universal neural advantage. The finite-fleet expected-gain statement is conditional on the explicitly randomized eight frozen models, not every model or all future training. Every operational primitive is synthetic.

## Auditable results

[Package checks]({P}/results/package_check.json) · [16,640 independent rational policy replays]({P}/results/replay.json) · [64 deliberate multistage boundary checks]({P}/results/boundary_checks.json) · [64 exact quartic-coupling checks]({P}/results/nonquadratic_checks.json) · [4,608 matched-cost pipeline records]({P}/results/matched_cost_rows.json) · [complete timing summary]({P}/results/matched_cost.json) · [all-cohort reanalysis and strata]({P}/results/reanalysis.json) · [source/result hashes]({P}/MANIFEST.json).

The publication workflow validates the **final published commit**, checks its manifest and exact policy replay, and attaches commit-status context `ndu-or-r19/final-sha` to that SHA. The workflow run and source SHA are recorded in [provenance]({P}/PROVENANCE.json); a successful initial-source run alone is not represented as validation of the final commit.

No prior revision directory, review report, or other branch is modified. Exact previous root manuscripts and PDFs are preserved under [{P}/predecessor/]({P}/predecessor/). The [historical supplement](historical_supplement.pdf) remains unchanged. Author approval of authorship, conflicts, and final journal-submission declarations is still required; this branch is a reviewer-ready revision package, not a claim of journal acceptance.
'''
    (ROOT/'README.md').write_text(body)
    (ROOT/'NDU_OR_submission_checklist.md').write_text(f'''# Operations Research R19 submission checklist

## Manuscript and files

- Anonymous current main manuscript: {checks['main_pdf_pages']} total pages, {checks['main_pages_excluding_references']} excluding references; submit as **Lengthy**, not Regular.
- Current companion: {checks['companion_pdf_pages']} pages; no longer than the main manuscript.
- Abstract: one paragraph, {checks['abstract_words']} words; no displayed mathematics.
- 11-point type, one-inch margins, letter paper, one-and-a-half line spacing; introduction without equations.
- Author–year citations, alphabetic references, no footnotes, tables after references.
- Data/software accessibility statement in the manuscript; complete ordinary TeX, actual PDFs, sources, observations, reproducible scripts, response, preservation map, and manifest provided.
- Exact predecessor root PDFs and sources preserved, old revision directories and reports unchanged.

## Evidence and provenance

- 16,640 independent exact rational policy replays and four rejected negative controls.
- 64 deliberate multistage boundary instances, 128 current reference/proposal certificates, 64 exact quartic cases.
- Every current timing target passed for 4,608 complete pipelines; all seven models and both classical baselines included.
- Retrospective analysis, held-out deployment, deliberate structural checks, and new timing are distinguished.
- No universal neural-speed, calibration, model-misspecification, or arbitrary-retraining guarantee is asserted.
- Final published SHA is verified by the `ndu-or-r19/final-sha` commit status, not inferred from the initial source commit's workflow.

## Author decisions still required before journal submission

Confirm author names/order and affiliations outside the anonymous manuscript, funding and conflict declarations, related-submission disclosures, subject-area choice, and all ScholarOne submission confirmations. This technical package does not invent these declarations or submit to the journal on the authors' behalf.

Official format guidance: https://pubsonline.informs.org/page/opre/submission-guidelines
''')
    (R/'README.md').write_text('''# R19 reproduction and review guide

Run from the repository root with Python 3.13. Install `revisions/or-r16-20260922/requirements.txt` and `PyMuPDF==1.26.7`; LaTeX requires NewTX, endfloat, xr-hyper, and the packages imported by the ordinary root sources. A C compiler is needed for the existing CasADi/OSQP bridge. Set `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` for the recorded timing protocol.

## Reproduce the new scientific records

```sh
python revisions/or-r19-20260923/boundary_checks.py
python revisions/or-r19-20260923/nonquadratic_checks.py
python revisions/or-r19-20260923/matched_cost.py
python -S revisions/or-r19-20260923/replay.py
python revisions/or-r19-20260923/analyze.py
bash revisions/or-r19-20260923/build.sh
python revisions/or-r19-20260923/check_package.py
python revisions/or-r19-20260923/package_metadata.py
```

These commands leave earlier scientific directories untouched. The existing R16 frozen models and observations are inputs, not newly retrained replacements. The matched-cost program separately measures all label and model-fitting costs on the current host while deploying only the frozen models. Times and resulting tables will change with hardware; mathematical and exact-certificate checks must still pass. The complete publication workflow also rebuilds the predecessor label indices before current assembly; those indices are already included under `predecessor/` in the published package.

## Verify a frozen published checkout without recomputation or mutation

```sh
python -S revisions/or-r19-20260923/replay.py --check
python revisions/or-r19-20260923/check_package.py --verify-manifest
```

The first verification uses Python's standard library only. It independently replays all 16,384 multistage deployment policies, 128 inherited structural policies, and 128 new boundary reference/proposal policies; verifies 128 response-gap identities; and requires four intentionally invalid records to be rejected. The second checks the actual PDFs, final TeX logs and labels, exact predecessor blobs, scientific counts, and every manifest hash.

## Scientific and version navigation

`RESPONSE_TO_REFEREE.md` addresses the complete latest actual R14 report. `PRESERVATION_MAP.md` maps every retained component to current or immutable predecessor documents. `REVISION_PLAN.json` and `DEVELOPMENT_NOTE.md` distinguish new work from retrospective analysis and developmental corrections. `sections/general_bridge.tex` contains the full global and inexact-response proofs. `sections/experiment.tex` and `sections/companion.tex` interpret every cohort and comparator without suppressing unfavorable outcomes. `results/` holds all current primary evidence, while original R16 observations remain at their original paths.

The only current reviewer entry points are the root `main.pdf` and `electronic_companion.pdf`. Both root TeX sources are fully expanded ordinary text, with modular assembly scripts retained for reproducibility. The historical supplement and exact predecessor PDFs preserve older continuous-time, nonlinear, scalar, and verified-cell material in full. No encoded transport is needed to read or compile the published manuscript.
''')
    provenance={'revision':'R19','parent_commit':'d23de668070fc29a7073a9e4ef647c8159b0d580','research_input_commit':'a3ddde9d80ef5c390dbb019d13bb719ddc22e1ef','source_commit':os.getenv('GITHUB_SHA','local-development'),'workflow_run':os.getenv('GITHUB_SERVER_URL','https://github.com')+'/'+os.getenv('GITHUB_REPOSITORY','TrillionniumFoundation/NDU')+'/actions/runs/'+os.getenv('GITHUB_RUN_ID','local-development'),'final_sha_validation_context':'ndu-or-r19/final-sha','timing_provenance':'All published primary follow-up timings are generated on the recorded publication host; local development pilots are not substituted.','statistical_provenance':'R16 reanalysis is retrospective; frozen-fleet inference conditions on the eight models; developmental R19 follow-up is not external preregistration.'}
    (R/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
    paths=[]
    for name in ['README.md','NDU_OR_submission_checklist.md','main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','historical_supplement.tex','historical_supplement.pdf','main.bib','main.bbl','main-labels.aux','ec-labels.aux','legacy-main-labels.aux','legacy-ec-labels.aux','history-labels.aux']:
        paths.append(ROOT/name)
    for p in R.rglob('*'):
        if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts and not p.name.startswith('pilot_shared_state_') and p.name!='PILOT_NOTE.md':paths.append(p)
    # Hash every directly reused scientific input, excluding locally compiled caches.
    for dirname in ['revisions/or-r16-20260922','revisions/or-r14-20260922','revisions/or-r13-20260922','revisions/or-r12-20260922','revisions/or-r10-20260921','revisions/or-r7-20260921','archive','supplemental']:
        for p in (ROOT/dirname).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix in ['.py','.c','.tex','.bib','.json','.gz','.csv','.txt','.md']:paths.append(p)
    manifest={'revision':'R19','base_commit':provenance['parent_commit'],'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}}
    (R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Review entry points and manifest:',len(manifest['sha256']),'files')
if __name__=='__main__':run()
