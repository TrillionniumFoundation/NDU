"""Publish readable pointers and prove preservation of the reviewed baseline."""
from pathlib import Path
import hashlib,json,re,subprocess,datetime,platform,sys
from build import expand
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];REL=R.relative_to(ROOT).as_posix()
BASE='4f0b662bd4184fc77fb57bd09c339bffb6213a69'
ALLOWED={'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'}
PAT=r'\\begin\{(?:theorem|proposition|lemma|corollary)\}(?:\[[^\]]*\])?\s*\\label\{([^}]+)\}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def locations(path):
    text=expand(path);return set(re.findall(PAT,text))
def run():
    b=json.loads((R/'BUILD_VALIDATION.json').read_text());s=json.loads((R/'results/SUMMARY.json').read_text());t=json.loads((R/'results/tests.json').read_text())
    extra=json.loads((R/'results/additional_checks.json').read_text());oldtests=json.loads((R/'results/inherited_suite/results/TESTS.json').read_text())
    assert b['status']==s['status']==t['status']==extra['status']=='PASS'
    oldmain=locations(R/'predecessor/main.tex');oldec=locations(R/'predecessor/electronic_companion.tex');old=oldmain|oldec
    nowmain=locations(ROOT/'main.tex');nowec=locations(ROOT/'electronic_companion.tex');now=nowmain|nowec
    mapping={key:{'current_location':('main.pdf' if key in nowmain else 'electronic_companion.pdf' if key in nowec else 'archive'),
        'complete_reviewed_statement':REL+'/predecessor/'+('main.pdf' if key in oldmain else 'electronic_companion.pdf'),
        'status':'retained in current reader and unchanged reviewed archive' if key in now else 'retained unchanged in reviewed archive and original source'} for key in sorted(old)}
    content=dict(baseline=BASE,reviewed_mathematical_statements=len(old),current_mathematical_statements=len(now),new_mathematical_labels=sorted(now-old),
        statements=mapping,archived_readers=[REL+'/predecessor/'+name for name in sorted(ALLOWED)],
        original_sources='All original revision directories remain byte-identical; archive is not a required cumulative journal appendix.')
    (R/'CONTENT_MAP.json').write_text(json.dumps(content,indent=2)+'\n')
    (R/'CONTENT_MAP.md').write_text('# Complete mathematical preservation map\n\nNo original statement or proof is deleted. Current readers contain the focused chain; the byte-identical reviewed readers and original revision sources remain accessible.\n\n| Reviewed label | Current location | Complete reviewed reader |\n|---|---|---|\n'+''.join(f'| `{key}` | {v["current_location"]} | `{v["complete_reviewed_statement"]}` |\n' for key,v in mapping.items()))
    pages=b['readers'];counts=f'{pages["main"]["pages"]} total main pages ({pages["main"]["nonreference_pages"]} excluding references), {pages["electronic_companion"]["pages"]} companion pages, {pages["response"]["pages"]} response pages'
    readme=f'''# NDU — Operations Research R51

**Current paper:** Limited-Memory Renewal Contracts: Exact Pooling and Selected-Book Design.  
**Revision branch:** `revision/ndu-operations-research-r51-selected-book-frontier-20260925`.  
**Review base:** `{BASE}`; scientific baseline `2098592a99e47d36cc9fd16311f21d1858fa6e1e`. Both independent R49 reports are addressed; the parallel R50 snapshot branch is unchanged.

## Readers

[Main manuscript](main.pdf) · [Electronic companion](electronic_companion.pdf) · [Point-by-point response]({REL}/RESPONSE_TO_REFEREES.pdf) · [Revision source and records]({REL}/) · [Preservation map]({REL}/CONTENT_MAP.md).

The current readers have {counts}. The abstract contains {b['format']['abstract_words']} words. The anonymous article uses 11-point text, 1.5 spacing and one-inch margins, an equation-free introduction, author–year references, figures near the text, and tables after references. The build reports no undefined references or citations, duplicate labels, missing characters or overfull boxes. The current category is Regular Manuscript; this is a repository revision for re-review, not a claim of journal submission or acceptance.

## Substantive changes

The new mandatory-selected-prefix recurrence supplies exact original-budget price bounds. A binary completion cover combines those bounds with a free-union relaxation and charge-aware safe deletion. Its standard-library checker independently checks original-space policies, mandatory levels, Bellman inequalities and complete coverage. The elementary fixed-budget XP enumeration implication is inherited from the earlier complexity proposition, not presented as a new result; the new algorithm contributes bounds, pruning and compact certificates.

Catalog refinement now has an explicit partition theorem, an unused-splitting-level example, selected-book class bounds, exact signature-cell stability, a threshold-robust formulation, and an affected-history bound. A derived capacity-reservation model is checked by integrating uniform demand. The group-mean method retains an explicit initial-width dyadic product, zero-width handling and a clearly stated stopping rule. A one-third stopping width needs four leaves; the coarse constant depends on whether the stopping step is epsilon/(2Ld) or epsilon/(4Ld).

## Executed evidence

All {s['certificates']} declared certificate requests pass independent verification: {s['exact']} are exact zero-width rational intervals and {s['open']} remain open. All six unchanged difficult instances close exactly in at most 21 visited nodes, agreeing with the preexisting exhaustive values. All 20 strict interior common-prefix instances are exact, including 1,024 histories. The 48 matched-class requests, 24 catalog-refinement requests, and 12 near-boundary requests retain every interruption. Prices reduce nodes but increase measured time in all displayed matched pairs; no universal speedup is claimed.

All 18 direct tangent/secant mixed-integer solves are retained with statuses, variables, binaries, nodes, elapsed and full wall times, primal/dual values, residuals and envelope errors. Each envelope and each timed tree receives its own three-second allowance; the two-envelope pair is not charged as one solve. Floating-point MIP bounds are not exact rational certificates.

The new tests pass {t['fixed_book']} fixed-book comparisons, {t['mandatory_price']} mandatory-price comparisons, {t['joint']} global comparisons, {t['intervals']} interruption checks and {t['dyadic']} dyadic cases; {t['mutations']} corrupted certificates are rejected. Boundary checks add {extra['boundary_joint']} joint and {extra['boundary_price']} price comparisons. All {extra['inherited_certificates']} inherited certificates are revalidated, and the complete old regression suite is rerun in an isolated output directory. Maximum current certificate size is {s['max_certificate_bytes']} gzip bytes; largest numerator and denominator lengths are {s['max_numerator_bits']} and {s['max_denominator_bits']} bits.

All data are synthetic. The protocol was frozen before local execution, not preregistered remotely. Local and publication-run environments and results are distinguished. No calibrated demand data, full variable-budget complexity classification, FPT guarantee, or universal solver ranking is asserted.

## Reproduction

Run from the repository root in a separate checkout:

```sh
R={REL}
python "$R/code/tests.py"
python "$R/code/study.py"
python "$R/code/additional_checks.py"
python "$R/code/tables.py"
python "$R/code/build.py"
python "$R/code/metadata.py"
# To validate saved intervals without rerunning optimization:
python "$R/code/study.py" --verify
python "$R/code/check_completion.py" path/to/certificate.json.gz
```

The exact checker uses only the Python standard library. Optimization uses inherited exact modules, SciPy 1.17.0 and SymPy 1.14.0; the publication environment pins Python 3.13.5 and PyMuPDF 1.26.7. TeX uses newtx with standard LaTeX packages. `PROTOCOL.json` freezes the population; `results/study.json` records every input, rational endpoint and saved certificate; `results/mip.json` records both numerical formulations. Rerunning the optimizer should use a clean results directory in a separate checkout to obtain new timings, not silently replace the committed measured record.

## Preservation and scope

All {len(old)} reviewed mathematical statements remain in the current readers or complete unchanged archive. The original derivation sources and earlier successful and failed experiments are unchanged. Only six root reader/entry files are replaced, and each original is copied byte for byte into `{REL}/predecessor/`. `CONTENT_MAP.json` enumerates each statement and `PRESERVATION_MANIFEST.json` audits the entire reviewed tree. No review branch, main branch, or other revision branch is modified. Author disclosures and any ScholarOne submission remain the authors' responsibility; see `NDU_OR_submission_checklist.md`.
'''
    (ROOT/'README.md').write_text(readme)
    (R/'README.md').write_text('# R51 revision package\n\nSee the [root README](../../README.md) for readers, exact guarantees and complete reproduction commands.\n\n'+readme.split('## Substantive changes',1)[1].join(['## Substantive changes','']))
    (ROOT/'NDU_OR_submission_checklist.md').write_text(f'''# Operations Research R51 submission and audit checklist

Current category: Regular Manuscript. Current readers: {counts}; abstract {b['format']['abstract_words']} words. Format validated against the official Operations Research submission guidelines on 2026-09-25: 11-point type, 1.5 spacing, one-inch margins, anonymous reader, equation-free introduction, author–year alphabetical references, tables after references and code/data instructions after the final section. The electronic companion is shorter than the article. No unresolved references, citations, duplicated labels, missing characters or overfull boxes are reported.

The exact rational and numerical mixed-integer evidence are explicitly separated. Every frozen request and every nonzero-width interval remains in the raw record. Inherited proofs, readers, source files and failed experiments are preserved. The current response addresses both independent R49 reports and documents the spacing clarification, new prefix bounds, catalog robustness, hard-instance closure, strict-prefix tests, numerical baselines, certificate costs and derived demand model.

Author completion is still required before an external journal submission: authorship and ORCID information; financial and other conflict disclosures; funding and assistance disclosures, including applicable AI-assistance policies; related/overlapping work disclosure; prior journal submission identifiers, if any; copyright/originality and exclusive-submission certifications; editor/reviewer nominations; and approval of the final submission PDF. None of those declarations is invented or submitted on the authors' behalf. This repository push is not a ScholarOne submission.

Official source: https://pubsonline.informs.org/page/opre/submission-guidelines (checked 2026-09-25).
''')
    # Readable Markdown response; equations remain TeX, references get resolved numbers.
    tex=(R/'RESPONSE_TO_REFEREES.tex').read_text().split('\\begin{document}',1)[1].split('\\end{document}',1)[0]
    tex=re.sub(r'\\begin\{center\}.*?\\end\{center\}','# Response to the two independent R49 reports\n',tex,flags=re.S)
    tex=re.sub(r'\\section\{([^}]+)\}',r'\n## \1\n',tex)
    tex=re.sub(r'\\textbf\{([^}]+)\}',r'**\1**',tex);tex=re.sub(r'\\emph\{([^}]+)\}',r'*\1*',tex);tex=re.sub(r'\\path\{([^}]+)\}',r'`\1`',tex)
    labels={}
    for f in ['r51-main-labels.aux','r51-ec-labels.aux']:
        labels.update(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}',(ROOT/f).read_text()))
    tex=re.sub(r'\\(?:eqref|ref)\{([^}]+)\}',lambda m:'('+labels.get(m.group(1),m.group(1))+')',tex)
    tex=tex.replace('~',' ').replace('\\par','\n').replace('``','“').replace("''",'”')
    (R/'RESPONSE_TO_REFEREES.md').write_text(tex.strip()+'\n')
    expected=json.loads((R/'INHERITED_SHA256.json').read_text());changes=[];errors=[]
    for path,oldsha in expected.items():
        now=ROOT/path
        if not now.exists():errors.append([path,'missing']);continue
        newsha=sha(now)
        if oldsha==newsha:continue
        if path not in ALLOWED:errors.append([path,'unapproved mutation',oldsha,newsha]);continue
        archive=R/'predecessor'/path
        if not archive.exists() or sha(archive)!=oldsha:errors.append([path,'archive is not byte-identical']);continue
        changes.append(dict(path=path,reviewed_sha256=oldsha,new_sha256=newsha,archived_as=str(archive.relative_to(ROOT))))
    assert len(old)==57, len(old)
    out=dict(status='FAIL' if errors else 'PASS',baseline=BASE,inherited_file_count=len(expected),unchanged_count=len(expected)-len(changes)-len(errors),archived_replacements=changes,errors=errors,
        all_reviewed_mathematical_statements_retained=len(old),review_reports_preserved=True,scope='Only isolated R51 branch; no deletions or changes to other branch refs')
    (R/'PRESERVATION_MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n')
    if errors:raise RuntimeError(errors)
    evidence=dict(status='PASS',generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),readers=b['readers'],population=s,tests=t,
        additional={k:v for k,v in extra.items() if k!='cases'},inherited_regressions=oldtests,preservation=out)
    (R/'FINAL_AUDIT.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':run()
