"""Read-only R66 preservation, editorial invariants and exact proof verification."""
from pathlib import Path
import argparse, gzip, hashlib, json, re, sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'code'))
from rational import F,digest
from binding63 import verify_bound
from binding65 import canonical_request,ROBUST
from support63 import ground_truth
EXPECTED=dict(requests=405,certificates=389,PASS=342,PASS_LOWER_ONLY=47,no_certificate=16,
    different_input_bytes=16,newly_replayed_not_reclassified=45,request_bound_certificates=389,
    robust_transfer_and_request_bound=42)
REPORT_BLOB='3d1c9c5ef76988894b624b9872e3a5332566cf07'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def included(p):return p.is_file() and p!=R/'PACKAGE_MANIFEST.json' and not any(x in ('.build','__pycache__') for x in p.relative_to(R).parts)
def load(path):return json.loads((R/path).read_text())
def segments(s,pattern):return [x.group(0) for x in re.finditer(pattern,s,re.S)]
def invariants():
    old=load('archive/r65/PACKAGE_MANIFEST.json');assert len(old['files'])==7080
    for name,h in old['files'].items():
        p=R/'archive/r65'/name
        if not p.is_file():p=R/name
        assert sha(p)==h,('R65 preservation',name)
        if name.startswith(('code/','evidence/','generated/','sections/','results/')):
            assert sha(R/name)==h,('Changed accepted implementation or evidence',name)
    blocks={};displays={};tables={}
    for name in ('main','electronic_companion'):
        a=(R/f'archive/r65/{name}.tex').read_text();b=(R/f'{name}.tex').read_text()
        pattern=r'\\begin\{(theorem|proposition|lemma|corollary|proof)\}.*?\\end\{\1\}'
        aa,bb=segments(a,pattern),segments(b,pattern)
        assert aa==bb,('Mathematical environment changed',name);blocks[name]=len(aa)
        pattern=r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}|\\\[.*?\\\]'
        aa,bb=segments(a,pattern),segments(b,pattern)
        assert aa==bb,('Display changed',name);displays[name]=len(aa)
        pattern=r'\\begin\{table\}.*?\\end\{table\}'
        aa,bb=segments(a,pattern),segments(b,pattern)
        assert aa==bb,('Table changed',name);tables[name]=len(aa)
        pattern=r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}'
        assert segments(a,pattern)==segments(b,pattern),('Bibliography changed',name)
    assert blocks=={'main':36,'electronic_companion':42}
    return dict(r65_files_preserved=7080,unchanged_mathematical_environments=blocks,
        unchanged_displays=displays,unchanged_tables=tables,
        existing_code_files_unchanged=sum(k.startswith('code/') for k in old['files']),
        accepted_request_schema_unchanged=True,existing_historical_evidence_unchanged=True)

def verify(manifest=True,replay_output=None):
    if manifest:
        m=load('PACKAGE_MANIFEST.json')
        assert m['schema']=='NDU-R66-payload-manifest-v1'
        assert set(m['files'])=={p.relative_to(R).as_posix() for p in R.rglob('*') if included(p)}
        for name,h in m['files'].items():assert sha(R/name)==h,('Package hash',name)
    preserved=invariants()
    report=(R/'GOVERNING_REFEREE_REPORT_R65.md').read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(report)).encode()+b'\0'+report).hexdigest()
    assert blob==REPORT_BLOB,'Governing report bytes differ from the pinned review'
    freeze=load('results/r66/SOURCE_FREEZE66.json')
    for name,h in freeze['source_hashes'].items():assert sha(R/name)==h,('Executed source',name)
    tests=load('results/r66/SCOPE_TESTS66.json')
    assert tests['status']=='PASS' and tests['baseline_classes']==6
    assert tests['legacy_extension_receipts_unchanged']==30 and tests['nested_tariff_receipts_unchanged']==5
    assert tests['exact_schema_extensions_rejected']==90 and tests['numerical_lower_only_preserved']
    request=load('results/r66/request/REQUEST_TESTS65.json')
    assert request['status']=='PASS' and request['positive_request_checks']==66 and request['rejected_adversaries']==25
    assert request['coordinated_witnesses_rejected']==2 and request['equal_gross_different_policy_accepted']
    semantic=load('results/r66/semantic/SEMANTIC_TESTS64.json')
    assert semantic['status']=='PASS' and semantic['positive_robust_certificates']==577
    assert semantic['exhaustive_projection_instances']==288 and semantic['new_semantic_rejections']==10
    assert load('results/r66/STRUCTURAL60_REPLAY.json')['tariff']['books_cross_checked']==6302
    assert load('results/r66/STRUCTURAL61_REPLAY.json')['robust_certified_instances']==198
    assert load('results/r66/BINDING_TESTS63.json')['rejected_mutations']==21
    source=load('results/SUPPORT_FREEZE63.json')
    for name,h in source['source_hashes'].items():assert sha(R/'archive/r63/code'/name)==h
    cases={c['id']:c for c in source['cases']};rows=load('results/SUPPORT_STUDY63.json')['rows']
    assert len(cases)==len(rows)==48
    for row in rows:
        spec=cases[row['id']]['spec'];assert digest(spec)==row['input_sha256']
        assert ground_truth(spec)==row['truth']
        p=R/'results'/row['certificate'];assert sha(p)==row['certificate_sha256']
        out=verify_bound(json.loads(gzip.decompress(p.read_bytes())),spec)
        assert F(out['lower'])==F(out['upper'])==F(row['truth']['lower'])
    replay=load('results/r66/replay/REQUEST_REPLAY65.json')
    assert replay['status']=='PASS' and all(replay[k]==v for k,v in EXPECTED.items())
    rows=[json.loads(x) for x in (R/'results/r66/replay/REQUEST_RECEIPTS65.jsonl').read_text().splitlines()]
    frozen=load('evidence/r61/results/STUDY_FREEZE.json');cases={c['id']:c for c in frozen['cases']}
    assert len(rows)==405 and len({(x['id'],x['method']) for x in rows})==405
    for row in rows:
        p=R/'evidence/r61/results/records'/f"{row['id']}--{row['method']}.json"
        rec=json.loads(p.read_text());assert sha(p)==row['record_file_sha256']
        for k,f in [('historical_status','status'),('historical_verification_status','verification_status'),
                    ('historical_rational_target_met','rational_target_met')]:assert row[k]==rec.get(f)
        if not rec.get('certificate'):assert 'current_replay' not in row;continue
        req=row['external_request'];case=cases[row['id']];canon=canonical_request(req)
        assert req['spec']==case['spec'] and F(req['epsilon'])==F(case['epsilon'])
        assert req['certificate_class']==rec['certificate_schema']
        ans=row['current_replay'];assert ans['request_bound'] and digest(req)==row['external_request_sha256']
        assert digest(canon)==ans['request_binding']['canonical_request_sha256']
        assert row['certificate_file_sha256']==rec['certificate_sha256']
        if req['certificate_class']==ROBUST:
            assert ans['transfer_formula_certified'] and ans['equal_gross_certified']
            assert ans['request_binding']['projection_tolerance_checked']
            assert req['configured_guard']==(4 if rec['method']=='hybrid' else case.get('guard',12))
    build=load('results/r66/BUILD66.json')
    assert build['main']['excluding_references']<=30 and build['main']['abstract_words']<=200
    assert build['electronic_companion']['pages']<=build['main']['pages']
    for item in build.values():assert not item['reference_warnings'] and not item['overfull']
    if manifest:
        q=load('results/r66/QUALIFICATION66.json');assert q['status']=='PASS'
        assert q['source_freeze_sha256']==sha(R/'results/r66/SOURCE_FREEZE66.json')
        for cmd in q['commands']:assert cmd['exit_code']==0 and sha(R/cmd['log'])==cmd['log_sha256']
    result=dict(status='PASS',**preserved,governing_report_blob=blob,root_cases_independently_rechecked=48,
        scope_baseline_classes=6,legacy_extensions_not_endorsed=35,exact_schema_extensions_rejected=90,
        request_regressions=66,request_adversaries_rejected=25,semantic_certificates=577,
        exhaustive_projections=288,**EXPECTED,manifest_checked=manifest)
    if replay_output is not None:
        assert not replay_output.resolve().is_relative_to(R.resolve())
        from replay65 import replay as run_replay
        result['fresh_full_replay']=run_replay(R/'evidence/r61',replay_output)
        assert all(result['fresh_full_replay'][k]==v for k,v in EXPECTED.items())
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--no-manifest',action='store_true');p.add_argument('--replay-output',type=Path)
    p.add_argument('--output',type=Path);a=p.parse_args();ans=verify(not a.no_manifest,a.replay_output)
    if a.output:
        assert not a.output.resolve().is_relative_to(R.resolve());a.output.write_text(json.dumps(ans,indent=2)+'\n')
    print(json.dumps(ans,indent=2))
