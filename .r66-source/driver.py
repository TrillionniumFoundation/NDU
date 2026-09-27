"""Publish the complete R66 editorial revision and verify its actual remote head."""
from pathlib import Path, PurePosixPath
import base64, hashlib, io, json, lzma, os, shutil, subprocess, sys, zipfile
ROOT=Path.cwd();REV=ROOT/os.environ['REV'];TMP=Path(os.environ['RUNNER_TEMP'])
BASE='6bc195dcdbc93d1a796b1388639c053c0a11ddd0'
REVIEW='0382789afc96be20497063930602d5a6be96909a'
REPORT='reviews/operation_research_referee_report_r65_independent_harsh_2026-09-27.md'
REPORT_BLOB='3d1c9c5ef76988894b624b9872e3a5332566cf07'
BRANCH='revision/ndu-operations-research-r66-editorial-scope-20260927'
ZIP_SHA='479d13fbc740c3202cf89cd80ad66af1d0ff6decc0d29768b8c95542b09c903d'
PAYLOAD_SHA='31a78d01d0c9bdd7eb1cd9adbb586b9ca84b4ba6091eddbf5a82c913015eb433'
assert os.environ['GITHUB_REF_NAME']==BRANCH
assert REV.relative_to(ROOT).as_posix()=='revisions/or-r66-editorial-scope-20260927'
def call(args):subprocess.run(args,check=True)
def get(args):return subprocess.check_output(args,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
phase=sys.argv[1]
if phase=='source':
    call(['git','merge-base','--is-ancestor',BASE,'HEAD'])
    assert subprocess.run(['git','merge-base','--is-ancestor',REVIEW,'HEAD']).returncode==1
    assert get(['git','rev-parse',REVIEW+':'+REPORT])==REPORT_BLOB
    raw=subprocess.check_output(['git','show',BASE+':CURRENT_SUBMISSION.zip'])
    assert hashlib.sha256(raw).hexdigest()==ZIP_SHA
    assert not REV.exists(),'Refusing to replace a pre-existing R66 payload during materialization'
    REV.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for item in z.infolist():
            path=PurePosixPath(item.filename)
            assert path.parts[0]=='NDU_R65' and '..' not in path.parts
            if item.is_dir():continue
            p=REV/Path(*path.parts[1:]);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(item))
    manifest=json.loads((REV/'PACKAGE_MANIFEST.json').read_text());assert len(manifest['files'])==7080
    for name,h in manifest['files'].items():assert sha(REV/name)==h,name
    payload=base64.b64decode(Path('.r66-source/payload.b64').read_text().strip(),validate=True)
    assert hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA,'Editorial payload hash mismatch'
    source=json.loads(lzma.decompress(payload))
    expected={'compile66.py','editorial66.py','publish66.py','qualify66.py','verify66.py'}
    assert set(source)==expected and all(isinstance(t,str) for t in source.values())
    stage=TMP/'r66-source';stage.mkdir(exist_ok=True)
    for name,text in source.items():(stage/name).write_text(text)
    call([sys.executable,str(stage/'editorial66.py'),str(REV)])
    for name in sorted(source):shutil.copy2(stage/name,REV/name)
    report=subprocess.check_output(['git','show',REVIEW+':'+REPORT])
    (REV/'GOVERNING_REFEREE_REPORT_R65.md').write_bytes(report)
    (REV/'results/r66/MATERIALIZATION66.json').write_text(json.dumps(dict(status='PASS',scientific_parent=BASE,
        governing_review=REVIEW,review_blob=REPORT_BLOB,source_trigger_commit=os.environ['GITHUB_SHA'],
        reviewed_zip_sha256=ZIP_SHA,change_payload_sha256=PAYLOAD_SHA,preserved_r65_manifest_files=7080,
        scope='Editorial receipt clarification only; all accepted code, mathematics and historical evidence unchanged'),indent=2)+'\n')
    print('Materialized complete R66 sources from the exact R65 package and pinned R65 referee report.')
elif phase=='publish':
    call([sys.executable,str(REV/'publish66.py'),'--repo',str(ROOT)])
    call([sys.executable,str(REV/'verify66.py')])
    for p in list(REV.rglob('__pycache__')):
        if p.is_dir():shutil.rmtree(p)
    if (REV/'.build').exists():shutil.rmtree(REV/'.build')
    assert get(['git','ls-remote','origin','refs/heads/'+BRANCH]).split()[0]==os.environ['GITHUB_SHA'],'Concurrent update; refusing overwrite'
    call(['git','config','user.name','github-actions[bot]'])
    call(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'])
    names=[str(REV.relative_to(ROOT)),'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf',
        'RESPONSE_TO_REFEREES.tex','RESPONSE_TO_REFEREES.pdf','README.md','CURRENT_REVISION.json','CURRENT_SUBMISSION.zip']
    call(['git','add','-f','--']+names)
    call(['git','commit','-m','revision(or-r66): clarify receipt scope; preserve accepted science and publish complete referee package [skip ci]'])
    call(['git','push','origin','HEAD:refs/heads/'+BRANCH])
    (TMP/'r66-published-sha.txt').write_text(get(['git','rev-parse','HEAD'])+'\n')
elif phase=='exact':
    head=get(['git','rev-parse','HEAD']);assert head==(TMP/'r66-published-sha.txt').read_text().strip()
    call([sys.executable,str(REV/'verify66.py'),'--replay-output',str(TMP/'r66-exact-replay'),'--output',str(TMP/'r66-exact-check.json')])
    call(['git','diff','--exit-code','HEAD','--',str(REV.relative_to(ROOT)),'main.pdf','electronic_companion.pdf','RESPONSE_TO_REFEREES.pdf','CURRENT_SUBMISSION.zip'])
    assert get(['git','ls-remote','origin','refs/heads/'+BRANCH]).split()[0]==head
    manifest=json.loads((REV/'PACKAGE_MANIFEST.json').read_text())
    with zipfile.ZipFile('CURRENT_SUBMISSION.zip') as z:
        expected={'NDU_R66/'+p for p in manifest['files']}|{'NDU_R66/PACKAGE_MANIFEST.json'}
        assert set(z.namelist())==expected
        for p,h in manifest['files'].items():assert hashlib.sha256(z.read('NDU_R66/'+p)).hexdigest()==h,p
        assert z.read('NDU_R66/PACKAGE_MANIFEST.json')==(REV/'PACKAGE_MANIFEST.json').read_bytes()
    readers={}
    for name in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
        for ext in ('.tex','.pdf'):assert (ROOT/(name+ext)).read_bytes()==(REV/(name+ext)).read_bytes()
        readers[name]=sha(REV/(name+'.pdf'))
    receipt=dict(schema='NDU-R66-exact-head-receipt-v1',status='PASS',published_commit=head,
        published_tree=get(['git','rev-parse','HEAD^{tree}']),source_trigger_commit=os.environ['GITHUB_SHA'],
        scientific_parent_commit=BASE,governing_review_commit=REVIEW,governing_report_blob=REPORT_BLOB,
        run_url=f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
        payload_manifest_sha256=sha(REV/'PACKAGE_MANIFEST.json'),manifest_files=len(manifest['files']),
        reader_pdf_sha256=readers,build=json.loads((REV/'results/r66/BUILD66.json').read_text()),
        qualification=json.loads((REV/'results/r66/QUALIFICATION66.json').read_text()),
        exact_commit_read_only_check=json.loads((TMP/'r66-exact-check.json').read_text()),
        historical_deadlines_and_failures_preserved=True,
        certified_scope='Delivered artifact identity, accepted-science and checker preservation, executed receipt-scope regressions and fresh request-bound integrity replay. No request authentication, runtime attestation or editorial decision.')
    (TMP/'R66_EXACT_HEAD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
    call(['gh','api','--method','POST',f"repos/{os.environ['GITHUB_REPOSITORY']}/statuses/{head}",'-f','state=success',
        '-f','context=ndu/r66-exact-head','-f','description=Complete R66 readers, preservation, receipt scope and 389 frozen proofs verified',
        '-f','target_url='+receipt['run_url']])
else:raise ValueError(phase)
