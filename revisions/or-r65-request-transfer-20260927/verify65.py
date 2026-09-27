"""Read-only request/transfer qualification and complete R64 preservation."""
from pathlib import Path
import argparse,gzip,hashlib,json,re,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'code'))
from rational import F,digest
from binding63 import verify_bound
from binding65 import canonical_request,ROBUST
from support63 import ground_truth

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def included(p):return p.is_file() and p!=R/'PACKAGE_MANIFEST.json' and not any(x in ('.build','__pycache__') for x in p.relative_to(R).parts)
def load(path):return json.loads((R/path).read_text())
def verify(manifest=True,replay_output=None):
    if manifest:
        m=load('PACKAGE_MANIFEST.json')
        assert set(m['files'])=={p.relative_to(R).as_posix() for p in R.rglob('*') if included(p)},'Incomplete package inventory'
        for name,h in m['files'].items():assert sha(R/name)==h,('Current package',name)
    old=load('archive/r64/PACKAGE_MANIFEST.json')
    for name,h in old['files'].items():
        p=R/'archive/r64'/name
        if not p.is_file():p=R/name
        assert sha(p)==h,('R64 preservation',name)
    math_counts={}
    for name in ('main','electronic_companion'):
        pattern=r'\\begin\{(theorem|proposition|lemma|corollary|proof)\}.*?\\end\{\1\}'
        a=[m.group(0) for m in re.finditer(pattern,(R/f'archive/r64/{name}.tex').read_text(),re.S)]
        b=[m.group(0) for m in re.finditer(pattern,(R/f'{name}.tex').read_text(),re.S)]
        assert a==b,('Mathematical content changed',name);math_counts[name]=len(a)
    freeze=load('results/r65/SOURCE_FREEZE65.json')
    for name,h in freeze['source_hashes'].items():assert sha(R/name)==h,('Current source',name)
    source=load('results/SUPPORT_FREEZE63.json')
    for name,h in source['source_hashes'].items():assert sha(R/'archive/r63/code'/name)==h,('Root source',name)
    cases={c['id']:c for c in source['cases']};roots=load('results/SUPPORT_STUDY63.json')['rows'];assert len(roots)==len(cases)==48
    for row in roots:
        spec=cases[row['id']]['spec'];assert digest(spec)==row['input_sha256'] and ground_truth(spec)==row['truth']
        p=R/'results'/row['certificate'];assert sha(p)==row['certificate_sha256']
        ans=verify_bound(json.loads(gzip.decompress(p.read_bytes())),spec)
        assert F(ans['lower'])==F(ans['upper'])==F(row['truth']['lower'])
    expected=dict(requests=405,certificates=389,PASS=342,PASS_LOWER_ONLY=47,no_certificate=16,
        different_input_bytes=16,newly_replayed_not_reclassified=45,request_bound_certificates=389,robust_transfer_and_request_bound=42)
    replay=load('results/r65/replay/REQUEST_REPLAY65.json')
    assert replay['status']=='PASS' and all(replay[k]==v for k,v in expected.items())
    rows=[json.loads(x) for x in (R/'results/r65/replay/REQUEST_RECEIPTS65.jsonl').read_text().splitlines()]
    frozen=load('evidence/r61/results/STUDY_FREEZE.json');cases={x['id']:x for x in frozen['cases']}
    assert len(rows)==405 and len({(x['id'],x['method']) for x in rows})==405
    for row in rows:
        p=R/'evidence/r61/results/records'/f"{row['id']}--{row['method']}.json";rec=json.loads(p.read_text())
        assert sha(p)==row['record_file_sha256']
        for key,field in [('historical_status','status'),('historical_verification_status','verification_status'),('historical_rational_target_met','rational_target_met')]:assert row[key]==rec.get(field)
        if not rec.get('certificate'):assert 'current_replay' not in row;continue
        req=row['external_request'];case=cases[row['id']];canon=canonical_request(req)
        assert req['spec']==case['spec'] and F(req['epsilon'])==F(case['epsilon'])
        assert req['certificate_class']==rec['certificate_schema']
        ans=row['current_replay'];assert ans['request_bound'] and digest(req)==row['external_request_sha256']
        assert digest(canon)==ans['request_binding']['canonical_request_sha256']
        assert row['certificate_file_sha256']==rec['certificate_sha256']
        if req['certificate_class']==ROBUST:
            assert ans['transfer_formula_certified'] and ans['equal_gross_certified'] and ans['request_binding']['projection_tolerance_checked']
            assert req['configured_guard']==(4 if rec['method']=='hybrid' else case.get('guard',12))
    tests=load('results/r65/REQUEST_TESTS65.json');assert tests['status']=='PASS'
    assert tests['positive_request_checks']==66 and tests['rejected_adversaries']==25 and tests['coordinated_witnesses_rejected']==2
    assert tests['legacy_witnesses_accepted']==dict(strict_tolerance='PASS',degraded_policy='PASS')
    assert tests['equal_gross_different_policy_accepted'] and tests['optimizer_free_request_checker']
    assert len(load('results/r65/REQUEST_ADVERSARIES65.json')['cases'])==25
    legacy=load('results/r65/legacy64/SEMANTIC_TESTS64.json');assert legacy['status']=='PASS'
    assert legacy['positive_robust_certificates']==577 and legacy['exhaustive_projection_instances']==288 and legacy['new_semantic_rejections']==10
    assert load('results/r65/STRUCTURAL60_REPLAY.json')['tariff']['books_cross_checked']==6302
    assert load('results/r65/STRUCTURAL61_REPLAY.json')['robust_certified_instances']==198
    assert load('results/r65/BINDING_TESTS63.json')['rejected_mutations']==21
    build=load('results/r65/BUILD65.json')
    assert build['main']['excluding_references']<=30 and build['main']['abstract_words']<=200
    assert build['electronic_companion']['pages']<=build['main']['pages']
    for item in build.values():assert not item['reference_warnings'] and not item['overfull']
    if manifest:
        qual=load('results/r65/QUALIFICATION65.json');assert qual['status']=='PASS'
        assert qual['source_freeze_sha256']==sha(R/'results/r65/SOURCE_FREEZE65.json')
        for command in qual['commands']:assert command['exit_code']==0 and sha(R/command['log'])==command['log_sha256']
    out=dict(status='PASS',r64_files_preserved=len(old['files']),unchanged_mathematical_environments=math_counts,
        root_cases_independently_rechecked=48,request_regressions=66,request_adversaries_rejected=25,
        archived_witnesses_accepted_and_current_rejected=2,valid_legacy_certificates=577,exhaustive_projections=288,
        **expected,manifest_checked=manifest)
    if replay_output is not None:
        assert not replay_output.resolve().is_relative_to(R.resolve())
        from replay65 import replay as run_replay
        out['fresh_full_replay']=run_replay(R/'evidence/r61',replay_output)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--no-manifest',action='store_true');p.add_argument('--replay-output',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    result=verify(not a.no_manifest,a.replay_output)
    if a.output:
        assert not a.output.resolve().is_relative_to(R.resolve());a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
