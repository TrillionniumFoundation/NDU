"""Write R23 review entry points from the executed evidence, not a plan."""
from pathlib import Path
import hashlib,json,platform
R=Path(__file__).resolve().parent;ROOT=R.parent.parent
s=json.loads((R/'results/summary.json').read_text());rp=json.loads((R/'results/replay.json').read_text())
rows=[a for a in s['summary'] if a['r']==4]
readme=f'''# Neural Differential Utility — Operations Research R23

**Accepted Service Adaptation with Neural Differential Utility: Continuation Prices and Robust Certified Gains**

Revision: September 23, 2026. Branch: `revision/ndu-operations-research-r23-20260923`.

## Current review package

[Main manuscript](main.pdf) · [complete main source](main.tex) · [electronic companion](electronic_companion.pdf) · [complete companion source](electronic_companion.tex).

[Point-by-point referee response](revisions/or-r23-20260923/RESPONSE_TO_REFEREE.md) · [preservation map](revisions/or-r23-20260923/PRESERVATION_MAP.md) · [literature map](revisions/or-r23-20260923/LITERATURE_MAP.md) · [claim/evidence ledger](revisions/or-r23-20260923/CLAIM_EVIDENCE.md) · [reproduction guide](revisions/or-r23-20260923/README.md).

R23 addresses the September 23 R20 review report at `18381729edf8d15a536ebef16abf6660ee0db48f`. Its scientific base is the complete R22 publication `fef3bad92ab9c74530b530a885bb6f437e8b1c1a`. The reviewed R20 tip was a plan on R19; R23 does not claim that a newer referee has already reviewed R22. Exact R22 root documents are preserved in `revisions/or-r23-20260923/predecessor/`; all earlier revision directories, reviews and historical supplements remain unchanged.

## Scientific addition

The current paper retains the accepted-control, friction, transfer, value-gradient, inexact-response, component-certificate and complete-dual-repair results. It now proves robust accepted gains under **joint objective and participation/capacity coefficient uncertainty**. The gain is measured against the true model-specific reoptimized restricted contract. A common outer comparator class contains the union of those restricted classes; a scalar counterexample shows why separately optimized vertex comparators can miss a stronger interior comparator. The new exact repair preserves root equalities and every uncertain inequality, and explicitly charges its value effect.

The generic robust-counterpart and weak-duality ingredients are identified as classical. The accepted-service consequence, hidden-model comparator distinction and implemented rational certificate are explicit. The uncertainty set is specified rather than field-estimated.

## Newly executed R23 evidence

The predeclared study uses 96 fresh contexts, four uncertainty radii, the same frozen eight-model neural and RBF ensembles, and a classical robust-maximin QP. It records **1,152 protected implementations**, **3,072 vertex comparator upper certificates** and **768 nondeployed nominal diagnostics**. All protected decisions are exactly robust-feasible and all their gain lower certificates are positive in this sample. The independent Python-standard-library replay also checks 2,304 interior certificate mixtures, the scalar counterexample at 1,001 rational parameters, and six rejected invalid controls. Numerical solve failures: **{s['failed_solves']}**; failure and negative-certificate retention is part of the protocol.

At uncertainty radius 0.25:

| Implemented rule | Mean robust gain lower certificate | Minimum certificate |
|---|---:|---:|
| Protected tanh-gradient | {rows[0]['mean_robust_gain_lower']:.6f} | {rows[0]['min_robust_gain_lower']:.6f} |
| Protected RBF-direct | {rows[1]['mean_robust_gain_lower']:.6f} | {rows[1]['min_robust_gain_lower']:.6f} |
| Classical robust maximin | {rows[2]['mean_robust_gain_lower']:.6f} | {rows[2]['min_robust_gain_lower']:.6f} |

These are averages/minima of pointwise, uniformly valid certificates, **not** new population confidence bounds. Both nominal learned rules violate some uncertain restriction in every recorded positive-radius context; their violation magnitudes are retained. None of these unsafe diagnostics is deployed. The classical robust rule remains strongest; no neural speed or accuracy superiority is asserted.

## Preserved evidence and verification

All original unfavorable neural/direct-price comparisons, the complete R22 5,120-pipeline matched-cost study, deterministic IID/shift validation, full-polyhedron scaling and prior exact checks remain. Their original provenance and statistical targets are unchanged. Every predecessor mathematical statement/proof block is preserved verbatim across the current main and companion; only the full global-bridge proof is moved intact to the companion.

The current main and companion use the journal's anonymous 11-point, one-and-a-half-spaced, one-inch-margin Lengthy format, a text-only abstract below 200 words, a notation-free introduction, author-year references and tables after references. Actual page counts, reference resolution and preservation are in [package checks](revisions/or-r23-20260923/results/package_check.json). [Manifest](revisions/or-r23-20260923/MANIFEST.json) · [provenance](revisions/or-r23-20260923/PROVENANCE.json) · [exact replay](revisions/or-r23-20260923/results/replay.json).

The publication workflow attaches `ndu-or-r23/final-sha` only after independent verification of the actual final commit. Author approval of submission declarations is still required; this package is a research revision, not journal acceptance.
'''
(ROOT/'README.md').write_text(readme)
(R/'README.md').write_text('''# Reproducing the complete R23 revision

The root main manuscript and electronic companion are the review objects. This directory contains additive R23 derivations and executed evidence; earlier results remain in their original directories.

## Execution

Use Python 3.13, NumPy 2.3.5, SciPy 1.17.0, CasADi 3.7.2 (its bundled OSQP library), and PyMuPDF 1.26.7. A C compiler builds the inherited OSQP bridge. Limit BLAS/OpenMP to one thread. A TeX Live installation with newtx, natbib, endfloat and amsthm builds the paper.

```sh
python revisions/or-r23-20260923/robust_study.py
python -S revisions/or-r23-20260923/replay.py
python revisions/or-r23-20260923/analyze.py
python revisions/or-r23-20260923/materialize_revision.py
bash revisions/or-r23-20260923/build.sh
python revisions/or-r23-20260923/package_metadata.py
python revisions/or-r23-20260923/check_package.py
python revisions/or-r23-20260923/package_metadata.py --manifest
python revisions/or-r23-20260923/check_package.py --verify-manifest
```

For a nonmutating verification of published evidence:

```sh
python -S revisions/or-r23-20260923/replay.py --check
python -S revisions/or-r22-20260923/replay.py --check
python -S revisions/or-r22-20260923/complete_dual_checks.py --check
python -S revisions/or-r19-20260923/replay.py --check
python revisions/or-r23-20260923/check_package.py --verify-manifest
```

The raw `certificates.jsonl.gz` records retain the rational implemented decisions, all eight valid outer-class dual certificates and all nominal nondeployment diagnostics. `robust_exact.py` has no numerical-library dependency; `python -S` prevents it from loading site packages. The comparator geometry is reconstructed analytically before replay. `DESIGN.json` declares the context seed, counts, uncertainty law, failure policy and the excluded engineering pilot. No pilot record enters the final results. Reexecution may change wall-clock timing or last digits of numerical proposals across hosts; exact authorization is repeated on the resulting records.

## Interpretation

The new records certify per-context robust feasibility and gain against the actual model-specific optimized restricted contract, conditional on the true coefficients belonging to the specified uncertainty set. New averages are descriptive, not lower confidence bounds. R22's nominal-model population bounds remain separately identified. The eight comparator solves are real additional work; this study does not claim acceleration. The `predecessor/` snapshot and manifest preserve the full R22 sources and PDFs.
''')
(ROOT/'NDU_OR_submission_checklist.md').write_text('''# Operations Research R23 submission checklist

- Current review objects: root `main.pdf`, `main.tex`, `electronic_companion.pdf`, `electronic_companion.tex`; all show Revision R23.
- Prepared as a **Lengthy** manuscript: main at most 40 pages excluding references; companion no longer than the complete main PDF. Counts are checked from actual PDFs and TeX labels.
- Anonymous title pages and PDF author metadata; 11-point text, one-and-a-half spacing, one-inch margins; abstract at most 200 words and text only; introduction free of mathematical notation; author-year references; tables after references.
- Every original mathematical statement/proof block retained verbatim in the current main or companion; predecessor hashes checked; full global-bridge proof relocated intact with an exact cross-reference.
- Joint-misspecification protocol, all executed records, failed-run policy and independent standard-library verification included. Nominal statistical bounds and new pointwise robust certificates remain distinct.
- All cross-references and citations resolve; no overfull text lines; complete ordinary sources have no transport dependency.
- Primary guidelines checked September 23, 2026: https://pubsonline.informs.org/page/opre/submission-guidelines
- **Author sign-off required:** authorship, conflicts, prior/parallel submission status, data/code and any applicable AI-use disclosures, and the final journal submission declarations. The assistant has not submitted to the journal or certified these author-specific declarations.
''')
prov={'revision':'R23','review_branch':'review/operation-research-r20-harsh-20260923','review_sha':'18381729edf8d15a536ebef16abf6660ee0db48f','reviewed_plan_sha':'45553b28f40c92a14895b8b82d8739e608f6d4b1','complete_scientific_base_sha':'fef3bad92ab9c74530b530a885bb6f437e8b1c1a','branch':'revision/ndu-operations-research-r23-20260923','new_evidence':'Executed robust_study.py; replayed without numerical libraries','preserved_evidence':'R19 and R22 results retain their original source/run attribution','pilot':'Two engineering contexts, separate seed, excluded from final results','truth_in_set_required':True,'final_commit_status_context':'ndu-or-r23/final-sha'}
(R/'PROVENANCE.json').write_text(json.dumps(prov,indent=2)+'\n')
import sys
if '--manifest' in sys.argv:
 paths=[ROOT/n for n in ['main.tex','main.pdf','main.bib','main.bbl','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md','main-labels.aux','ec-labels.aux']]
 paths += [p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'pilot' not in p.parts and p.name!='MANIFEST.json']
 hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
 (R/'MANIFEST.json').write_text(json.dumps({'revision':'R23','sha256':hashes},indent=2)+'\n')
print('R23 review entry points written')
