"""Publish a complete branch-local R65 revision and verify the exact published commit."""
from pathlib import Path,PurePosixPath
import base64,hashlib,io,json,lzma,os,shutil,subprocess,sys,zipfile
ROOT=Path.cwd();REV=ROOT/os.environ['REV'];TMP=Path(os.environ['RUNNER_TEMP'])
BASE='5704e3b4572da9726cab8bdcc8d74d0194f77d9e'
REVIEW='3fa2fc1db4257a15af4b3a437c54b306a4589e63'
REPORT='reviews/operation_research_referee_report_r64_independent_harsh_2026-09-27.md'
REPORT_BLOB='4c8f3d94cfa14cf76d1834b0adb1c5251ded056b'
BRANCH='revision/ndu-operations-research-r65-request-transfer-20260927'
ZIP_SHA='d050036b3ba721eca9c902650a90ba6b95f405d111775a0d69f80dd8dd6d4984'
PAYLOAD_SHA='c393bfff4a67dde2cb2ddb8763a16598af71d304d360eda4a3b652515f5db458'
assert os.environ['GITHUB_REF_NAME']==BRANCH
assert REV.relative_to(ROOT).as_posix()=='revisions/or-r65-request-transfer-20260927'
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
    if REV.exists():shutil.rmtree(REV)
    REV.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for item in z.infolist():
            path=PurePosixPath(item.filename)
            assert path.parts[0]=='NDU_R64' and '..' not in path.parts
            if item.is_dir():continue
            p=REV/Path(*path.parts[1:]);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(item))
    m=json.loads((REV/'PACKAGE_MANIFEST.json').read_text());assert len(m['files'])==6992
    for name,h in m['files'].items():assert sha(REV/name)==h,name
    archive=REV/'archive/r64';archive.mkdir(parents=True,exist_ok=True)
    for p in list(REV.iterdir()):
        if p.is_file():shutil.copy2(p,archive/p.name)
    shutil.copytree(REV/'code',archive/'code',ignore=shutil.ignore_patterns('__pycache__'))
    parts=sorted(Path('.r65-source').glob('part*'));assert [p.name for p in parts]==['part00','part01','part02']
    payload=base64.b64decode(''.join(p.read_text().strip() for p in parts),validate=True)
    assert hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA
    source=json.loads(lzma.decompress(payload))
    for name,text in source.items():
        p=REV/name;assert p.resolve().is_relative_to(REV.resolve()) and isinstance(text,str)
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    (REV/'GOVERNING_REFEREE_REPORT_R64.md').write_bytes(subprocess.check_output(['git','show',REVIEW+':'+REPORT]))
    out=REV/'results/r65';out.mkdir(parents=True,exist_ok=True)
    (out/'MATERIALIZATION65.json').write_text(json.dumps(dict(status='PASS',scientific_parent=BASE,governing_review=REVIEW,review_blob=REPORT_BLOB,source_trigger_commit=os.environ['GITHUB_SHA'],reviewed_zip_sha256=ZIP_SHA,change_payload_sha256=PAYLOAD_SHA,changed_source_files=len(source),preserved_r64_manifest_files=6992),indent=2)+'\n')
    print('Materialized',len(source),'source files; preserved all 6992 reviewed files.')
elif phase=='publish':
    call([sys.executable,str(REV/'publish65.py'),'--repo',str(ROOT)])
    call([sys.executable,str(REV/'verify65.py')])
    for p in list(REV.rglob('__pycache__')):
        if p.is_dir():shutil.rmtree(p)
    if (REV/'.build').exists():shutil.rmtree(REV/'.build')
    assert get(['git','ls-remote','origin','refs/heads/'+BRANCH]).split()[0]==os.environ['GITHUB_SHA'],'Concurrent update; refusing overwrite'
    call(['git','config','user.name','github-actions[bot]'])
    call(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'])
    names=[str(REV.relative_to(ROOT)),'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','RESPONSE_TO_REFEREES.tex','RESPONSE_TO_REFEREES.pdf','README.md','CURRENT_REVISION.json','CURRENT_SUBMISSION.zip']
    call(['git','add','-f','--']+names)
    call(['git','commit','-m','revision(or-r65): bind external requests and exact transferred policies; publish complete referee revision [skip ci]'])
    call(['git','push','origin','HEAD:refs/heads/'+BRANCH])
    (TMP/'r65-published-sha.txt').write_text(get(['git','rev-parse','HEAD'])+'\n')
elif phase=='exact':
    head=get(['git','rev-parse','HEAD']);assert head==(TMP/'r65-published-sha.txt').read_text().strip()
    call([sys.executable,str(REV/'verify65.py'),'--replay-output',str(TMP/'r65-exact-replay'),'--output',str(TMP/'r65-exact-check.json')])
    call(['git','diff','--exit-code','HEAD','--',str(REV.relative_to(ROOT)),'main.pdf','electronic_companion.pdf','RESPONSE_TO_REFEREES.pdf','CURRENT_SUBMISSION.zip'])
    assert get(['git','ls-remote','origin','refs/heads/'+BRANCH]).split()[0]==head
    manifest=json.loads((REV/'PACKAGE_MANIFEST.json').read_text())
    with zipfile.ZipFile('CURRENT_SUBMISSION.zip') as z:
        expected={'NDU_R65/'+p for p in manifest['files']}|{'NDU_R65/PACKAGE_MANIFEST.json'}
        assert set(z.namelist())==expected
        for p,h in manifest['files'].items():assert hashlib.sha256(z.read('NDU_R65/'+p)).hexdigest()==h,p
        assert z.read('NDU_R65/PACKAGE_MANIFEST.json')==(REV/'PACKAGE_MANIFEST.json').read_bytes()
    readers={}
    for name in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
        for ext in ('.tex','.pdf'):assert (ROOT/(name+ext)).read_bytes()==(REV/(name+ext)).read_bytes()
        readers[name]=sha(REV/(name+'.pdf'))
    receipt=dict(schema='NDU-R65-exact-head-receipt-v1',status='PASS',published_commit=head,
        published_tree=get(['git','rev-parse','HEAD^{tree}']),source_trigger_commit=os.environ['GITHUB_SHA'],
        scientific_parent_commit=BASE,governing_review_commit=REVIEW,
        run_url=f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
        payload_manifest_sha256=sha(REV/'PACKAGE_MANIFEST.json'),manifest_files=len(manifest['files']),
        reader_pdf_sha256=readers,build=json.loads((REV/'results/r65/BUILD65.json').read_text()),
        qualification=json.loads((REV/'results/r65/QUALIFICATION65.json').read_text()),
        exact_commit_read_only_check=json.loads((TMP/'r65-exact-check.json').read_text()),
        historical_deadlines_and_failures_preserved=True,
        certified_scope='External-request agreement, projection minimality at requested tolerance, equal-gross exact transfer lower, verified objective intervals, artifact and source closure. No runtime guard attestation or editorial acceptance.')
    (TMP/'R65_EXACT_HEAD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
    call(['gh','api','--method','POST',f"repos/{os.environ['GITHUB_REPOSITORY']}/statuses/{head}",'-f','state=success','-f','context=ndu/r65-exact-head','-f','description=Readers, request/transfer semantics, 48 exact cases and 389 frozen proofs verified','-f','target_url='+receipt['run_url']])
else:raise ValueError(phase)
