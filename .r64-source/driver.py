"""Materialize, publish, and verify a complete R64 revision on its own branch."""
from pathlib import Path, PurePosixPath
import base64,hashlib,io,json,lzma,os,shutil,subprocess,sys,zipfile
ROOT=Path.cwd();REV=Path(os.environ['REV']);TMP=Path(os.environ['RUNNER_TEMP'])
BASE='653cc617af4a18dac533200de8606f083ca341fb'
REVIEW='ddeb5f75febffd585eaf2d2c6e99a99b5c86cbdb'
BRANCH='revision/ndu-operations-research-r64-certificate-closure-20260927'
ZIP_SHA='419d92b78520923e639a62331053c53db343a059e2137ec3e8e4e4f5ba2902cf'
PAYLOAD_SHA='a06b5ff9dc69b5b02e062be376b55da521ef428bc73486bc2acbf09eb6258117'
assert os.environ['GITHUB_REF_NAME']==BRANCH
assert REV.as_posix()=='revisions/or-r64-certificate-closure-20260927'
def call(args):subprocess.run(args,check=True)
def get(args):return subprocess.check_output(args,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
phase=sys.argv[1]
if phase=='source':
    call(['git','merge-base','--is-ancestor',BASE,'HEAD'])
    assert get(['git','rev-list','--max-parents=0','HEAD'])=='447eb4ca5783720a14d1135ea7022eae35ab4a7e'
    assert subprocess.run(['git','merge-base','--is-ancestor',REVIEW,'HEAD']).returncode==1
    assert get(['git','rev-parse',REVIEW+':reviews/operation_research_referee_report_r63_independent_harsh_2026-09-27.md'])=='b194f2a645b2e1a736326c14018943daad5d17af'
    raw=subprocess.check_output(['git','show',BASE+':CURRENT_SUBMISSION.zip'])
    assert hashlib.sha256(raw).hexdigest()==ZIP_SHA
    if REV.exists():shutil.rmtree(REV)
    REV.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for item in z.infolist():
            path=PurePosixPath(item.filename)
            assert path.parts[0]=='NDU_R63' and '..' not in path.parts
            if item.is_dir():continue
            p=REV/Path(*path.parts[1:]);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(item))
    m=json.loads((REV/'PACKAGE_MANIFEST.json').read_text());assert len(m['files'])==6848
    for name,h in m['files'].items():assert sha(REV/name)==h,name
    archive=REV/'archive/r63';archive.mkdir(parents=True,exist_ok=True)
    for p in list(REV.iterdir()):
        if p.is_file():shutil.copy2(p,archive/p.name)
    for name in ('code','results','sections'):
        shutil.copytree(REV/name,archive/name,ignore=shutil.ignore_patterns('__pycache__'))
    parts=sorted(Path('.r64-source').glob('part*'))
    assert [p.name for p in parts]==['part00','part01','part02','part03']
    payload=base64.b64decode(''.join(p.read_text().strip() for p in parts),validate=True)
    assert hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA
    source=json.loads(lzma.decompress(payload))
    for name,text in source.items():
        p=REV/name;assert p.resolve().is_relative_to(REV.resolve()) and isinstance(text,str)
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    result=REV/'results/r64';result.mkdir(parents=True,exist_ok=True)
    (result/'MATERIALIZATION64.json').write_text(json.dumps({'status':'PASS','scientific_parent':BASE,
        'governing_review':REVIEW,'source_trigger_commit':os.environ['GITHUB_SHA'],
        'reviewed_zip_sha256':ZIP_SHA,'change_payload_sha256':PAYLOAD_SHA,'change_source_files':len(source),
        'preserved_r63_manifest_files':6848},indent=2)+'\n')
    print('Materialized',len(source),'changed source files; all 6848 reviewed files preserved.')
elif phase=='publish':
    call([sys.executable,str(REV/'publish64.py'),'--repo',str(ROOT)])
    call([sys.executable,str(REV/'verify64.py')])
    for p in list(REV.rglob('__pycache__')):
        if p.is_dir():shutil.rmtree(p)
    if (REV/'.build').exists():shutil.rmtree(REV/'.build')
    remote=get(['git','ls-remote','origin','refs/heads/'+BRANCH]).split()[0]
    assert remote==os.environ['GITHUB_SHA'],'Concurrent branch update; refusing to overwrite'
    call(['git','config','user.name','github-actions[bot]'])
    call(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'])
    names=[str(REV),'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf',
        'RESPONSE_TO_REFEREES.tex','RESPONSE_TO_REFEREES.pdf','README.md','CURRENT_REVISION.json','CURRENT_SUBMISSION.zip']
    call(['git','add','-f','--']+names)
    call(['git','commit','-m','revision(or-r64): close certificate semantics and publish complete referee revision with frozen projection evidence [skip ci]'])
    call(['git','push','origin','HEAD:refs/heads/'+BRANCH])
    (TMP/'r64-published-sha.txt').write_text(get(['git','rev-parse','HEAD'])+'\n')
elif phase=='exact':
    head=get(['git','rev-parse','HEAD']);assert head==(TMP/'r64-published-sha.txt').read_text().strip()
    call([sys.executable,str(REV/'verify64.py'),'--replay-output',str(TMP/'r64-exact-replay'),
        '--output',str(TMP/'r64-exact-check.json')])
    call(['git','diff','--exit-code','HEAD','--',str(REV),'main.pdf','electronic_companion.pdf','RESPONSE_TO_REFEREES.pdf','CURRENT_SUBMISSION.zip'])
    assert get(['git','ls-remote','origin','refs/heads/'+BRANCH]).split()[0]==head
    manifest=json.loads((REV/'PACKAGE_MANIFEST.json').read_text())
    with zipfile.ZipFile('CURRENT_SUBMISSION.zip') as z:
        expected={'NDU_R64/'+p for p in manifest['files']}|{'NDU_R64/PACKAGE_MANIFEST.json'}
        assert set(z.namelist())==expected
        for p,h in manifest['files'].items():assert hashlib.sha256(z.read('NDU_R64/'+p)).hexdigest()==h,p
        assert z.read('NDU_R64/PACKAGE_MANIFEST.json')==(REV/'PACKAGE_MANIFEST.json').read_bytes()
    readers={}
    for name in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
        for ext in ('.tex','.pdf'):assert Path(name+ext).read_bytes()==(REV/(name+ext)).read_bytes()
        readers[name]=sha(REV/(name+'.pdf'))
    receipt={'schema':'NDU-R64-exact-head-receipt-v1','status':'PASS','published_commit':head,
        'source_trigger_commit':os.environ['GITHUB_SHA'],'scientific_parent_commit':BASE,'governing_review_commit':REVIEW,
        'run_url':f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
        'payload_manifest_sha256':sha(REV/'PACKAGE_MANIFEST.json'),'manifest_files':len(manifest['files']),
        'reader_pdf_sha256':readers,'build':json.loads((REV/'results/r64/BUILD64.json').read_text()),
        'qualification':json.loads((REV/'results/r64/QUALIFICATION64.json').read_text()),
        'exact_commit_read_only_check':json.loads((TMP/'r64-exact-check.json').read_text()),
        'historical_deadlines_and_failures_preserved':True}
    (TMP/'R64_EXACT_HEAD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    call(['gh','api','--method','POST',f"repos/{os.environ['GITHUB_REPOSITORY']}/statuses/{head}",
        '-f','state=success','-f','context=ndu/r64-exact-head',
        '-f','description=Readers, semantics, 48 exact cases and 389 frozen proofs verified on published SHA',
        '-f','target_url='+receipt['run_url']])
else:raise ValueError(phase)
