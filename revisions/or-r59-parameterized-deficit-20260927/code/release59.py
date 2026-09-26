"""Publishable source/archive closure and read-only exact-head verification."""
from pathlib import Path
import datetime,gzip,hashlib,json,os,shutil,subprocess,sys,tempfile,zipfile
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];REL=R.relative_to(ROOT).as_posix();BASE='1edd6d929e20f50a14ec6ef9beab4a37fa44fe39'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def prepare():
    from build59 import preserve
    preserve()
    body='''# NDU — Operations Research R59

Current article: **Finite-Catalog Resource Allocation: Exact Path Representations and Menu Complexity**.

The current root `main.pdf` and `electronic_companion.pdf` are the R59 readers. The revision directory holds the complete response to the September 26 R58 referee report, ordinary LaTeX sources, exact structural tests, the frozen matched-resource study and publication validation. All earlier scientific paths remain unchanged; predecessor root files are copied under `retained_r58/` before replacement.

The primary additions are original-model W[1]-hardness jointly in menu budget and cap count, recognition/approximation for conservative resource paths, optimized common-curvature prototype grouping, and an exact mixed-integer convex comparator. Numerical SCIP bounds and rational certificates are deliberately distinguished. No editorial acceptance or field calibration is claimed.

## Entry points

- `main.pdf`: current article, central new proofs included.
- `electronic_companion.pdf`: full secondary structural/price/lattice results and direct formulation.
- `REV/RESPONSE_TO_REFEREES.pdf`: point-by-point response to the latest R58 report.
- `REV/CONTENT_MAP.md`: current and retained scientific reading map.
- `REV/results/ALL_RUNS.csv`: every new timed request, including failures and limits.
- `REV/results/STUDY_FREEZE.json`: input and execution-source freeze.
- `REV/BUILD_VALIDATION.json`: actual compiled reader graph and diagnostics.
- `REV/CODE_AND_DATA.zip`: flat self-contained current code/data and reader package.

## Reproduction from this root

Use Python 3.13.5; pinned dependencies are in `REV/requirements.txt`. PDF compilation needs TeX Live with `newtx`, `xr-hyper` and `xurl`.

```sh
python REV/code/structural59.py
python REV/code/feasibility59.py
python REV/code/build59.py
python REV/code/release59.py verify
```

The committed study is immutable evidence. To repeat timing, copy the extracted archive to a separate directory and remove only the **new R59** `results/records`, `results/inputs`, `results/certificates`, `results/STUDY_FREEZE.json` and `results/SUMMARY.json` in that copy; then run `python REV/code/study59.py freeze run`. Never relabel new timings as the preserved execution. The panel uses 72 inputs × four methods, sequential three-second total allowances, and a 1.8-second internal optimization cutoff. It is a deterministic synthetic engineering panel, not an independently sampled field study.

SCIP's quadratic formulation has zero envelope error, but floating-point global bounds are not exact rational proofs. Its reconstructed lower policy is checked independently. Process high-water RSS during checking includes retained optimizer allocations. Read-only verification records the exact checkout SHA externally; it does not modify the paper commit or claim administrative branch-protection settings.
'''.replace('REV',REL)
    (R/'ROOT_README.md').write_text(body);(ROOT/'README.md').write_text(body)
    (R/'requirements.txt').write_text('scipy==1.17.0\nsympy==1.14.0\nPyMuPDF==1.26.7\nmatplotlib==3.10.8\npyscipopt==6.2.1\n')
    content='''# R59 content preservation and reading map

## Current main article
Model and timing, canonical response, constructive path identity, capacity potential, history-level packing, conservative-DAG recognition and repair, W[1] reduction, centered deficit algorithm with holes and bit complexity, optimized prototype grouping, current study and synthesis.

## Current electronic companion
Exact two-command common-cap theorem; full SUBSET SUM construction; tight 2q and joint-type support bounds; reward-oscillation theorem; full price-path duality and branch/certificate analysis; generic uniform-grid fallback; saturated and numerical-lattice regimes; exact convex formulation and experimental accounting; complete retained resource-grid recurrence.

## Complete historical readers (nothing deleted)
`retained_r58/main.pdf` and `retained_r58/electronic_companion.pdf` are byte-identical copies of the preceding root readers. Their original entry-point LaTeX and README are alongside them. Every source and evidence file under `revisions/or-r58-structural-referee-20260926/` and earlier revision directories remains at its original path. This includes all earlier diagnostics, formal proofs, operational architecture, 225 timed records, 24 prototype tests, 168 saturated-budget certificates, negative screening results, earlier tables and figures, and predecessor readers. Those original execution counts are not claims about rerunning them in R59.

The new current article changes the organization, not the scope or underlying constraints. Essential new proofs are in the main paper. Historical numerical content is deliberately not duplicated into a misleading current table; it remains completely accessible with provenance. Git comparison against author base `1edd6d929e20f50a14ec6ef9beab4a37fa44fe39` must show no deletion or modification under any prior revision path.

## Latest report
Review branch `review/operation-research-r58-independent-harsh-20260926`, report `reviews/operation_research_referee_report_r58_independent_harsh_2026-09-26.md`, review SHA `fe068d2a978a44548688b6052d4f210473394417`. The new author branch is based on the reviewed author tip, not on reviewer-authored artifacts.
'''
    (R/'CONTENT_MAP.md').write_text(content)

def finish():
    build=json.loads((R/'BUILD_VALIDATION.json').read_text());summary=json.loads((R/'results/SUMMARY.json').read_text())
    assert build['status']=='PASS' and summary['actual_runs']==288
    (ROOT/'NDU_OR_submission_checklist.md').write_text(f"# Operations Research R59 submission checklist\n\nAnonymous article, companion and point-by-point R58 response. 11-point type, 1.5 spacing, one-inch margins. Text-only abstract: {build['abstract_words']} words. Main nonreference pages: {build['main_nonreference_pages']}; category: {build['submission_category']}. Companion pages: {build['pages']['electronic_companion']}. All new central proofs retained in the main article. Prior readers and scientific files preserved. Full frozen 288-request record set includes numerical/exact distinctions and failures. No field calibration, editorial acceptance or branch-protection administration is asserted.\n\nSee `{REL}/BUILD_VALIDATION.json`, `CONTENT_MAP.md`, `results/SUMMARY.json` and the exact-head verification artifact.\n")
    paths=set(build['source_sha256'])
    paths.update(str(p.relative_to(ROOT)) for p in R.rglob('*') if p.is_file() and p.suffix not in ('.zip','.pyc') and '__pycache__' not in str(p) and p.name not in ('RELEASE_MANIFEST.json','PUBLICATION_STATUS.json'))
    paths.update(['README.md','main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','NDU_OR_submission_checklist.md'])
    old=ROOT/'revisions/or-r58-structural-referee-20260926'
    for p in old.rglob('*'):
        if p.is_file() and p.suffix in ('.py','.tex','.json','.csv','.md','.txt','.pdf','.gz') and '__pycache__' not in str(p):paths.add(str(p.relative_to(ROOT)))
    # Include older dependencies of retained readers, not merely the current FLS.
    for parent in [ROOT/'revisions'/name for name in ('or-r52-resource-path-20260925','or-r53-catalog-safe-certificates-20260926','or-r54-exact-price-path-20260926')]:
        if parent==R:continue
        for p in parent.rglob('*'):
            if p.is_file() and p.suffix in ('.tex','.py','.json','.csv','.md','.txt','.pdf','.png','.gz') and '__pycache__' not in str(p):paths.add(str(p.relative_to(ROOT)))
    hashes={p:sha(ROOT/p) for p in sorted(paths)}
    (R/'RELEASE_MANIFEST.json').write_text(json.dumps(dict(schema='NDU-R59-release-v1',author_base=BASE,files=hashes,scope='Payload hashes exclude this manifest and archive to avoid recursive hashing. Exact checkout commit is recorded by the read-only verification job.'),indent=2)+'\n')
    paths.add(f'{REL}/RELEASE_MANIFEST.json')
    with zipfile.ZipFile(R/'CODE_AND_DATA.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(paths):z.write(ROOT/p,p)
    # The archive has root readers and their actual relative dependencies, not a hidden nested archive.
    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(R/'CODE_AND_DATA.zip') as z:z.extractall(td)
        root=Path(td)
        for p,h in hashes.items():assert sha(root/p)==h
        assert (root/'main.tex').exists() and (root/'main.pdf').exists() and (root/REL/'code/build59.py').exists()
    (R/'PUBLICATION_STATUS.json').write_text(json.dumps(dict(status='COMPLETE_CANDIDATE',build_status=build['status'],timed_requests=288,archive_sha256=sha(R/'CODE_AND_DATA.zip'),archive_layout='root-level current entry points and all dependency paths',exact_head_status='Recorded separately after this payload is committed; do not infer from production source SHA.',scope='No editorial acceptance claim'),indent=2)+'\n')
    print('Flat complete archive:',(R/'CODE_AND_DATA.zip').stat().st_size,'bytes;',len(hashes),'hashed payload files')

def verify():
    manifest=json.loads((R/'RELEASE_MANIFEST.json').read_text())
    for p,h in manifest['files'].items():assert sha(ROOT/p)==h,('Changed published payload',p)
    b=json.loads((R/'BUILD_VALIDATION.json').read_text());assert b['status']=='PASS'
    for p,h in b['source_sha256'].items():assert sha(ROOT/p)==h
    for n,h in b['pdf_sha256'].items():assert sha(R/f'{n}.pdf')==h
    from study59 import verify as studyverify,rows
    studyverify();checked=0
    # Public proof checker imports no design optimizer. Run separately for every accepted rational record.
    checker=ROOT/'revisions/or-r58-structural-referee-20260926/code/check_certificate56.py'
    for rec in rows():
        if rec.get('verification_status')=='PASS':
            p=R/'results'/rec['certificate']
            subprocess.run([sys.executable,str(checker),str(p),'--expected-sha256',rec['instance_sha256']],check=True,stdout=subprocess.DEVNULL,timeout=60,cwd=ROOT);checked+=1
        elif rec.get('verification_status')=='PASS_LOWER_ONLY':
            p=R/'results'/rec['certificate'];c=json.loads(gzip.decompress(p.read_bytes()))
            # Separate Python process prevents accidental dependence on imported optimizer modules.
            code="import sys,json,gzip;sys.path.insert(0,sys.argv[1]);from check_price import check_policy;from rational import F;c=json.loads(gzip.decompress(open(sys.argv[2],'rb').read()));assert check_policy(c['instance'],c['policy'])==F(c['policy']['value'])"
            subprocess.run([sys.executable,'-c',code,str(checker.parent),str(p)],check=True,timeout=60,cwd=ROOT);checked+=1
    prior_delta=[];head='extracted-archive-no-git'
    if (ROOT/'.git').exists():
        head=git('rev-parse','HEAD');prior_delta=[x for x in git('diff','--name-only',BASE,'--','revisions').splitlines() if not x.startswith(REL+'/')]
        assert not prior_delta,('Historical scientific paths changed',prior_delta)
    out=dict(status='PASS',checked_commit=head,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),payload_files=len(manifest['files']),independent_proofs_rechecked=checked,complete_records=288,historical_path_deltas=prior_delta,read_only=True)
    dest=Path(os.environ.get('R59_VERIFY_OUTPUT',str(ROOT/'.build/r59/EXACT_HEAD_VERIFICATION.json')));dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':
    for command in sys.argv[1:]:{'prepare':prepare,'finish':finish,'verify':verify}[command]()
