"""Self-contained current package and final-checkout closure; never rewrite timed records."""
from pathlib import Path
import datetime,gzip,hashlib,json,os,re,shutil,subprocess,sys,tempfile,zipfile
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];REL=R.relative_to(ROOT).as_posix()
OLD=ROOT/'revisions/or-r59-parameterized-deficit-20260927';CORE=ROOT/'revisions/or-r58-structural-referee-20260926/code'
BASE='cc7ac349969adc9186e9a75f8d01f76ad485c3ba'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def tails():
    s=json.loads((R/'results/SUMMARY.json').read_text());assert s['method_requests']==1260
    lines=[r'\begin{table}[p]\centering\caption{Three-second request tail costs in the prospective study}\label{tab:tails60}',r'\begin{tabular}{llrrrr}\toprule Family & Method & Checks & Total 95th & Check 95th & Largest proof\\\midrule']
    for row in s['groups']:
        if row['budget']!=3:continue
        ck=row['verification_seconds'];val='--' if ck is None else f"{ck['p95']:.3f}"
        proof=row['proof_bytes'];size='--' if proof is None else f"{proof['maximum']/1024:.1f}"
        lines.append(f"{row['family'].capitalize()} & {row['method'].capitalize()} & {row['checks']}/30 & {row['parent_seconds']['p95']:.3f} & {val} & {size}"+r'\\')
    lines+=[r'\bottomrule\end{tabular}\par\smallskip\begin{minipage}{\textwidth}\small Time columns are seconds; proof size is uncompressed kibibytes. Checks count complete interval checks for rational methods and lower-policy checks for SCIP, within the original deadline. Checking-time percentiles condition on a recorded checking phase, including phases that did not finish within the total allowance. Full phase denominators, medians, 90th percentiles and all three budgets are in the machine-readable summary.\end{minipage}\end{table}']
    (R/'generated/tail_table.tex').write_text('\n'.join(lines)+'\n')
    # Reanalyse, do not rerun or alter, the reviewed record set.
    sys.path.insert(0,str(CORE));from rational import digest,F
    f=json.loads((OLD/'results/STUDY_FREEZE.json').read_text());cs={x['id']:x for x in f['cases']};rs=[json.loads(p.read_text()) for p in (OLD/'results/records').glob('*.json')]
    assert len(rs)==288
    def qs(vals):
        v=sorted(vals)
        if not v:return None
        def at(a):x=(len(v)-1)*a;i=int(x);return v[i]*(1-x+i)+v[min(i+1,len(v)-1)]*(x-i)
        return dict(n=len(v),median=at(.5),p90=at(.9),p95=at(.95),maximum=max(v))
    g=[]
    for family in sorted({x['family'] for x in cs.values()}):
        for method in ('price','deficit','enumeration','scip'):
            ss=[x for x in rs if cs[x['id']]['family']==family and x['method']==method]
            row=dict(family=family,method=method,n=len(ss),rational_targets=sum(x['rational_target_met'] for x in ss),numerical_targets=sum(x['numerical_target_met'] for x in ss),deadlines=sum(x['parent_timeout'] for x in ss))
            for k in ('parent_seconds','optimization_seconds','serialization_seconds','verification_seconds','proof_bytes','compressed_proof_bytes'):row[k]=qs([x[k] for x in ss if isinstance(x.get(k),(int,float))])
            g.append(row)
    save(R/'results/R59_REANALYSIS.json',dict(scope='Post-hoc reanalysis of byte-identical historical records; not new executions',distinct_specifications=len({digest(x['spec']) for x in cs.values()}),tolerance_tagged_cases=len(cs),requests=len(rs),groups=g,source_freeze_sha256=sha(OLD/'results/STUDY_FREEZE.json'),records_sha256={p.name:sha(p) for p in (OLD/'results/records').glob('*.json')}))

def documentation():
    b=json.loads((R/'BUILD_VALIDATION.json').read_text());s=json.loads((R/'results/SUMMARY.json').read_text())
    body=f'''# NDU — Operations Research R60

**Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier**

Current readers: `main.pdf`, `electronic_companion.pdf`. New revision: `{REL}`.
Based on latest report `reviews/operation_research_referee_report_r59_independent_harsh_2026-09-27.md` at review commit `{BASE}`. Author branch: `revision/ndu-operations-research-r60-tariff-frontier-20260927`.

## New substantive results

Theorem 6.2 gives exact allocation with a standard opening fee and d exceptional commands in O(k N^2 + 2^d m N^2) rational operations, and 2^d poly(L) bit time, for common linear rewards and free preliminary service. Arbitrary expected caps, realization ceilings, probabilities and rational denominators remain allowed. Uniform fees give a polynomial algorithm without a resource grid. This is a positive counterpart to the retained original-model W[1]-hardness in menu allowance plus cap count. The manuscript also adds same-book price-support and gap results, bounded-path recognition with witnesses, and a corridor-rehabilitation mapping. Scope and all earlier proofs remain explicit.

## Review entry points

- `{REL}/RESPONSE_TO_REFEREES.pdf`: complete point-by-point R59 response.
- `{REL}/CURRENT_SUBMISSION.zip`: standalone readers and a flat, independently verifiable code/data package.
- `{REL}/PRESERVATION.json`: hashes, source origins and retained mathematical labels.
- `{REL}/retained_r59/`: byte-identical reviewed root readers and entry points.
- `{REL}/results/ALL_RUNS.csv`: every new method request, including failures and deadlines.
- `{REL}/results/STUDY_FREEZE.json` and `SOURCE_FREEZE_COMMIT.txt`: sources and inputs committed before timing.
- `{REL}/results/SUMMARY.json`: actual family/budget/method success and tail costs.
- `{REL}/results/R59_REANALYSIS.json`: separately labeled reanalysis of unchanged historical records.
- `{REL}/BUILD_VALIDATION.json` and `RELEASE_MANIFEST.json`: reader and payload closure.

The prospective study has {s['distinct_specifications']} distinct models, {s['budget_tagged_cases']} budget-tagged cases and {s['method_requests']} requests. Thirty seeds per family recur across interventions and three budgets; these requests are not independent observations. Rationally certified global intervals and SCIP numerical-bound results are reported separately. SCIP's selected book is reoptimized exactly for its lower policy; its global upper bound remains numerical. No field validation or unexecuted hybrid advantage is claimed.

## Build and verify

Python 3.13.5 and pinned dependencies: `{REL}/requirements.txt`. TeX Live needs newtx, xr-hyper and xurl. Ordinary scientific sources are committed before compilation.

```sh
python {REL}/code/tests60.py --output /tmp/STRUCTURAL60.json
python {REL}/code/study60.py verify
python {REL}/code/package60.py tails
python {REL}/code/build60.py
python {REL}/code/package60.py finish
python {REL}/code/package60.py verify
```

The standalone ZIP requires no historical directory tree: run `python code/flat_verify60.py`, then `python rebuild_readers.py` to compile. `python rerun_study.py --output /absolute/new/directory` reproduces the design in a fresh directory without overwriting recorded evidence. New timings are new executions, not replacements for the published receipts.

## Publication validation

Abstract: {b['abstract_words']} words. Main: {b['pages']['main']} PDF pages, {b['main_nonreference_pages']} excluding references. Companion: {b['pages']['electronic_companion']} pages. Category: {b['submission_category']}. Anonymous 11-point type, 1.5 spacing and one-inch margins; equation-free introduction; author-year alphabetical references; tables after references. Build diagnostics: {b['status']}. Exact final-checkout verification is separately bound to the published commit by CI, not conflated with the execution freeze. The review branch and all earlier revision directories remain unchanged.
'''
    (ROOT/'README.md').write_text(body);(R/'README.md').write_text(body)
    (ROOT/'NDU_OR_submission_checklist.md').write_text(f'''# Operations Research R60 checklist

Reader category: {b['submission_category']}. Main: {b['main_nonreference_pages']} nonreference pages; companion: {b['pages']['electronic_companion']} pages, no longer than main ({b['pages']['main']}). Abstract: {b['abstract_words']} words, text only. Introduction: equation-free. Anonymous 11-point type; 1.5 spacing; one-inch margins; author-year alphabetized references; no footnotes; tables after references.

All original-model constraints and previous mathematical results preserved. Complete English R59 response provided. Positive tariff theorem, bounded-path extension, price support, exact tests and all 1,260 prospective requests included. Rational and numerical evidence separated. Current flat source/code/data package and independently verified original policies included. Financial-interest, author identity, ORCID and duplicate-submission declarations must be supplied by the authors at submission; no declarations are invented here. No journal submission or acceptance is claimed.
''')
    (R/'CONTENT_MAP.md').write_text('''# R60 scientific preservation map

## Main
1 Introduction and modern literature. 2 Original model and feasibility. 3 Constructive resource path, capacity potential and packing. 4 Full-graph conservation and approximation. 5 Encoded decision language and complete W[1] reduction. 6 New tariff-sensitive exact frontier and comparative statics. 7 Complete deficit approximation, holes and bit costs. 8 New same-book price support and gap distinction. 9 Retained prototype selection. 10 Historical and prospective computation. 11 Conclusion. Alphabetical references and evidence tables follow.

## Companion
All prior exact-cap, SUBSET SUM, tight cap-count, joint-type, oscillation, price-search, branching, uniform-grid, saturated, numerical-lattice, exact MICP and resource-recurrence results are present in full. Added: bounded-path recognition and witnesses, oracle/bit distinction, corridor rehabilitation, evidence semantics, structural checks and cost tails. Historical tables are labeled as such.

## Preservation
The `retained_r59` directory copies the reviewed root readers byte-for-byte. The full R52–R59 source and evidence trees remain unchanged in the repository, including negative screening and deficit results. `PRESERVATION.json` records every source expanded into the current readers and verifies retention of the earlier scientific labels. Rewritten introduction, interpretation and conclusion do not remove mathematical results. The latest referee report remains on the unchanged review branch and is inherited by the new revision branch.
''')

def flat_package(stage):
    stage.mkdir(parents=True);(stage/'code').mkdir()
    for n in ('main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','RESPONSE_TO_REFEREES.tex','RESPONSE_TO_REFEREES.pdf','requirements.txt','BUILD_VALIDATION.json','CONTENT_MAP.md'):
        shutil.copyfile(R/n,stage/n)
    core_names=['rational.py','price_path.py','check_price.py','deficit.py','check_deficit.py','enumeration.py','check_enumeration.py']
    for n in core_names:shutil.copyfile(CORE/n,stage/'code'/n)
    adaptations={}
    for n in ('tariff60.py','check_tariff60.py','paths60.py','tests60.py','worker60.py','study60.py','flat_verify60.py'):
        p=R/'code'/n;text=p.read_text();original=text
        text=text.replace("ROOT = Path(__file__).resolve().parents[3]\nsys.path.insert(0, str(ROOT/'revisions/or-r58-structural-referee-20260926/code'))","ROOT = Path(__file__).resolve().parents[1]\nsys.path.insert(0, str(ROOT/'code'))")
        text=text.replace("ROOT=Path(__file__).resolve().parents[3]\nsys.path.insert(0,str(ROOT/'revisions/or-r58-structural-referee-20260926/code'))","ROOT=Path(__file__).resolve().parents[1]\nsys.path.insert(0,str(ROOT/'code'))")
        text=text.replace("R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];OLD=ROOT/'revisions/or-r58-structural-referee-20260926/code'","R=Path(__file__).resolve().parents[1];ROOT=R;OLD=R/'code'")
        (stage/'code'/n).write_text(text)
        if text!=original:adaptations['code/'+n]=dict(original=REL+'/code/'+n,original_sha256=sha(p),adapted_sha256=sha(stage/'code'/n),change='Repository-root and core-import paths only; algorithm text and timed original snapshot retained separately.')
    mapping={}
    for d in (R,OLD):
        f=json.loads((d/'results/STUDY_FREEZE.json').read_text())
        for original,h in f['source_hashes'].items():
            src=ROOT/original;assert sha(src)==h
            sub='execution_sources/'+('r60/' if '/or-r60-' in original else 'r59/' if '/or-r59-' in original else 'r58/')+src.name
            if original in mapping:assert mapping[original]==sub
            mapping[original]=sub;dest=stage/sub;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
    save(stage/'EXECUTION_SOURCE_MAP.json',dict(original_to_snapshot=mapping,path_only_adaptations=adaptations))
    shutil.copytree(R/'results',stage/'results',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(OLD/'results',stage/'results_r59',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(R/'generated',stage/'generated')
    (stage/'rebuild_readers.py').write_text('''from pathlib import Path
import subprocess,os
root=Path(__file__).resolve().parent;out=root/'.build/r60';out.mkdir(parents=True,exist_ok=True)
for cycle in range(4):
    for name in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
        subprocess.run(['pdflatex','-halt-on-error','-interaction=nonstopmode','-output-directory='+str(out),name+'.tex'],cwd=root,check=True)
print('Rebuilt PDFs are in .build/r60; recorded PDFs remain unchanged.')
''')
    (stage/'rerun_study.py').write_text('''from pathlib import Path
import argparse,shutil,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();dest=Path(a.output).resolve();root=Path(__file__).resolve().parent
if dest.exists() and any(dest.iterdir()):raise SystemExit('Output directory must be empty; recorded evidence is immutable.')
dest.mkdir(parents=True,exist_ok=True);shutil.copytree(root/'code',dest/'code');shutil.copyfile(root/'requirements.txt',dest/'requirements.txt')
(dest/'results').mkdir();(dest/'generated').mkdir()
subprocess.run([sys.executable,str(dest/'code/study60.py'),'freeze','run','verify'],cwd=dest,check=True)
print('New execution only:',dest)
''')
    (stage/'README.md').write_text('''# R60 standalone submission

Read main.pdf, electronic_companion.pdf and RESPONSE_TO_REFEREES.pdf. Their complete sources have no scientific input dependencies outside this package. The archived BUILD_VALIDATION.json describes the published readers.

With Python 3.13.5, install `python -m pip install -r requirements.txt`. Run `python code/flat_verify60.py` for read-only validation of file hashes, both source/input freezes, 1,548 recorded requests, all completed rational certificates and all completed numerical-solver lower policies. It imports no optimizer to check tariff certificates. Exact global intervals and numerical upper bounds are not conflated. Post-study checks do not relabel original deadline failures.

Run `python code/tests60.py --output /tmp/STRUCTURAL60.json` for exact structural tests. Run `python rebuild_readers.py` with TeX Live/newtx/xr-hyper/xurl for four-pass cross-referenced PDF compilation; new PDFs are in .build/r60 and do not overwrite the recorded PDFs. Run `python rerun_study.py --output /absolute/empty/directory` for a new execution of the prospective 90-specification, three-budget design. That directory must be empty. This uses a path-only-adapted flat runtime and generates a new freeze, environment and timings; these are not the original experiment.

`results` holds R60's 1,260 requests. `results_r59` holds the retained R59 study's 288 requests; it has 56 distinct specifications and 72 tolerance cases. `EXECUTION_SOURCE_MAP.json` maps every original frozen-source path to a byte-identical flat snapshot under execution_sources. The code directory contains runnable current methods and their minimal core dependencies, with path-only changes mapped and hashed separately. The remaining original execution snapshots are provenance, not required for import resolution. No earlier revision directory tree or live repository is needed to check the package.

All measurements are model-derived, not field observations. The SCIP formulation is algebraically exact, but its upper bound is numerical; only its reconstructed original lower policy is independently checked exactly. Timeouts, phase costs, proof sizes and errors remain visible. No acceptance or external-benchmark performance is claimed.
''')
    files={p.relative_to(stage).as_posix():sha(p) for p in stage.rglob('*') if p.is_file()};save(stage/'PACKAGE_MANIFEST.json',dict(schema='NDU-R60-flat-package-v1',files=files))

def finish():
    b=json.loads((R/'BUILD_VALIDATION.json').read_text());assert b['status']=='PASS'
    for n in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
        assert sha(R/(n+'.pdf'))==b['pdf_sha256'][n]
        assert 'TEMPORARY LOCAL' not in (R/(n+'.tex')).read_text()
    documentation()
    with tempfile.TemporaryDirectory() as tmp:
        stage=Path(tmp)/'current_submission';flat_package(stage)
        p=subprocess.run([sys.executable,str(stage/'code/flat_verify60.py')],capture_output=True,text=True,cwd=stage)
        if p.returncode:raise RuntimeError(p.stdout+p.stderr)
        (R/'FLAT_PACKAGE_VERIFICATION.json').write_text(p.stdout)
        # Verify the path-adapted deterministic generator remains the frozen design.
        cmd="import sys,json;from pathlib import Path;sys.path.insert(0,'code');from study60 import cases;from rational import encode;assert encode(cases())==json.loads(Path('results/STUDY_FREEZE.json').read_text())['cases'];print('flat generator identity PASS')"
        subprocess.run([sys.executable,'-c',cmd],cwd=stage,check=True)
        with zipfile.ZipFile(R/'CURRENT_SUBMISSION.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for p in sorted(stage.rglob('*')):
                if p.is_file() and '__pycache__' not in p.parts:z.write(p,p.relative_to(stage))
    paths=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('RELEASE_MANIFEST.json','PUBLICATION_STATUS.json')]
    paths += [ROOT/p for p in ('main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md')]
    save(R/'RELEASE_MANIFEST.json',dict(schema='NDU-R60-release-manifest-v1',review_commit=BASE,files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}))
    save(R/'PUBLICATION_STATUS.json',dict(status='PUBLISHED_PAYLOAD_READY_FOR_EXACT_HEAD_CHECK',archive_sha256=sha(R/'CURRENT_SUBMISSION.zip'),manifest_sha256=sha(R/'RELEASE_MANIFEST.json'),freeze_commit=(R/'results/SOURCE_FREEZE_COMMIT.txt').read_text().strip(),note='Final checkout SHA is recorded by the separate read-only verification job.'))
    print('R60 PACKAGE CLOSED',len(paths))

def verify():
    m=json.loads((R/'RELEASE_MANIFEST.json').read_text());status=json.loads((R/'PUBLICATION_STATUS.json').read_text())
    assert sha(R/'RELEASE_MANIFEST.json')==status['manifest_sha256'];assert sha(R/'CURRENT_SUBMISSION.zip')==status['archive_sha256']
    for rel,h in m['files'].items():assert sha(ROOT/rel)==h,('Release hash',rel)
    frozen=(R/'results/SOURCE_FREEZE_COMMIT.txt').read_text().strip();final=git('rev-parse','HEAD')
    subprocess.run(['git','merge-base','--is-ancestor',frozen,final],cwd=ROOT,check=True)
    before=json.loads(subprocess.check_output(['git','show',frozen+':'+REL+'/results/STUDY_FREEZE.json'],cwd=ROOT,text=True))
    assert before==json.loads((R/'results/STUDY_FREEZE.json').read_text())
    olddirs=[p for p in (ROOT/'revisions').iterdir() if p.is_dir() and p.name!=R.name]
    changed=git('diff','--name-only',BASE,'HEAD','--',*[str(p.relative_to(ROOT)) for p in olddirs]);assert not changed,('Changed historical material',changed)
    with tempfile.TemporaryDirectory() as tmp:
        stage=Path(tmp)
        with zipfile.ZipFile(R/'CURRENT_SUBMISSION.zip') as z:
            for n in z.namelist():assert not Path(n).is_absolute() and '..' not in Path(n).parts
            z.extractall(stage)
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
        p=subprocess.run([sys.executable,str(stage/'code/flat_verify60.py')],cwd=stage,env=env,capture_output=True,text=True)
        if p.returncode:raise RuntimeError(p.stdout+p.stderr)
        certs=json.loads(p.stdout)
        out=stage/'recomputed_structural.json';subprocess.run([sys.executable,str(stage/'code/tests60.py'),'--output',str(out)],cwd=stage,env=env,check=True,capture_output=True)
        assert json.loads(out.read_text())==json.loads((R/'results/STRUCTURAL60.json').read_text())
    result=dict(status='PASS',exact_commit=final,source_freeze_commit=frozen,review_base=BASE,release_files=len(m['files']),archive_sha256=status['archive_sha256'],historical_changes=[],certificate_check=certs,structural_regression='PASS',build=json.loads((R/'BUILD_VALIDATION.json').read_text())['status'])
    dest=Path(os.environ.get('R60_VERIFY_OUTPUT','/tmp/NDU_R60_EXACT_HEAD_VERIFICATION.json'));save(dest,result);print(json.dumps(result,indent=2))
if __name__=='__main__':
    for cmd in sys.argv[1:]:{'tails':tails,'finish':finish,'verify':verify}[cmd]()
