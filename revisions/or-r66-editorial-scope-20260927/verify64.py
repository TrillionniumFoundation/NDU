"""Read-only R64 validation, with optional full replay outside the package."""
from pathlib import Path
import argparse, csv, gzip, hashlib, json, sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'code'))
from rational import F,digest
from binding63 import verify_bound
from support63 import ground_truth

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def included(p):return p.is_file() and p!=R/'PACKAGE_MANIFEST.json' and not any(x in ('.build','__pycache__') for x in p.relative_to(R).parts)
def verify(manifest=True,replay_output=None):
    if manifest:
        m=json.loads((R/'PACKAGE_MANIFEST.json').read_text())
        assert set(m['files'])=={p.relative_to(R).as_posix() for p in R.rglob('*') if included(p)},'Incomplete inventory'
        for name,h in m['files'].items():assert sha(R/name)==h,('Package hash',name)
    old=json.loads((R/'archive/r63/PACKAGE_MANIFEST.json').read_text())
    for name,h in old['files'].items():
        p=R/'archive/r63'/name
        if not p.is_file():p=R/name
        assert sha(p)==h,('R63 preservation',name)
    frozen=json.loads((R/'results/r64/SOURCE_FREEZE64.json').read_text())
    for name,h in frozen['source_hashes'].items():assert sha(R/name)==h,('Current source',name)
    source=json.loads((R/'results/SUPPORT_FREEZE63.json').read_text())
    for name,h in source['source_hashes'].items():assert sha(R/'archive/r63/code'/name)==h,('Original root source',name)
    cases={c['id']:c for c in source['cases']};rows=json.loads((R/'results/SUPPORT_STUDY63.json').read_text())['rows']
    assert len(cases)==len(rows)==48
    for row in rows:
        spec=cases[row['id']]['spec'];assert digest(spec)==row['input_sha256']
        assert ground_truth(spec)==row['truth']
        p=R/'results'/row['certificate'];assert sha(p)==row['certificate_sha256']
        answer=verify_bound(json.loads(gzip.decompress(p.read_bytes())),spec)
        assert F(answer['lower'])==F(answer['upper'])==F(row['truth']['lower'])
    replay=json.loads((R/'results/r64/replay/BINDING_REPLAY.json').read_text())
    expected={'requests':405,'certificates':389,'PASS':342,'PASS_LOWER_ONLY':47,'no_certificate':16,
        'different_input_bytes':16,'newly_replayed_not_reclassified':45}
    assert replay['status']=='PASS' and all(replay[k]==v for k,v in expected.items())
    receipts=[json.loads(x) for x in (R/'results/r64/replay/BINDING_RECEIPTS.jsonl').read_text().splitlines()]
    assert len(receipts)==405 and len({(x['id'],x['method']) for x in receipts})==405
    for row in receipts:
        p=R/'evidence/r61/results/records'/f"{row['id']}--{row['method']}.json"
        record=json.loads(p.read_text());assert sha(p)==row['record_file_sha256']
        assert row['historical_status']==record['status']
        assert row['historical_verification_status']==record.get('verification_status')
        assert row['historical_rational_target_met']==record['rational_target_met']
    semantic=json.loads((R/'results/r64/SEMANTIC_TESTS64.json').read_text())
    assert semantic['status']=='PASS'
    # Counts are bound to actual test execution, not inferred from source text.
    assert semantic['positive_robust_certificates']==577 and semantic['exhaustive_projection_instances']==288
    assert len(semantic['rejections'])==10 and semantic['new_semantic_rejections']==10 and semantic['legacy_accepts_false_metadata']==10
    structure=json.loads((R/'results/r64/STRUCTURAL61_REPLAY.json').read_text())
    assert structure['status']=='PASS' and structure['robust_certified_instances']==198
    assert json.loads((R/'results/r64/STRUCTURAL60_REPLAY.json').read_text())['tariff']['books_cross_checked']==6302
    assert json.loads((R/'results/r64/BINDING_TESTS63.json').read_text())['rejected_mutations']==21
    table=json.loads((R/'results/r64/PROJECTION_QUALITY64.json').read_text())
    assert table['new_optimization_runs']==0 and len(table['rows'])==12
    assert table['source_csv_sha256']==sha(R/'evidence/r61/results/ALL_RUNS.csv')
    for row in table['rows']:
        p=R/'evidence/r61/results/records'/f"{row['id']}--robust.json";rec=json.loads(p.read_text())
        assert sha(p)==row['record_sha256'] and row['original_status']==rec['status']
        assert row['original_timed_target']==rec['rational_target_met']
        for key in ('optimization_seconds','proof_bytes','compressed_proof_bytes'):
            assert row[key]==rec.get(key),(row['id'],key)
        assert row['original_check_seconds']==rec.get('verification_seconds')
    build=json.loads((R/'results/r64/BUILD64.json').read_text())
    assert build['main']['excluding_references']<=30 and build['main']['abstract_words']<=200
    assert build['electronic_companion']['pages']<=build['main']['pages']
    for b in build.values():assert not b['reference_warnings'] and not b['overfull']
    result={'status':'PASS','root_cases_independently_rechecked':48,'r63_files_preserved':len(old['files']),
        'historical_requests_preserved':405,'two_sided_replay':342,'numerical_lower_only_replay':47,
        'no_certificate_preserved':16,'later_replay_not_reclassified':45,'semantic_adversaries_rejected':10,
        'valid_semantic_certificates':577,'projection_cases':288,'manifest_checked':manifest}
    if replay_output is not None:
        assert not replay_output.resolve().is_relative_to(R.resolve()),'Replay output must be outside the sealed package'
        from replay63 import replay as run_replay
        result['fresh_full_replay']=run_replay(R/'evidence/r61',replay_output)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--no-manifest',action='store_true');p.add_argument('--replay-output',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    result=verify(not a.no_manifest,a.replay_output)
    if a.output:
        assert not a.output.resolve().is_relative_to(R.resolve()),'Read-only verification output belongs outside package'
        a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
