"""Read-only exact proof, source, row-accounting, and package verification."""
from pathlib import Path
import argparse, csv, gzip, hashlib, json, sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'code'))
from rational import F,digest
from binding63 import verify_bound
from support63 import ground_truth

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(manifest=True):
    if manifest:
        m=json.loads((R/'PACKAGE_MANIFEST.json').read_text())
        for name,h in m['files'].items():assert sha(R/name)==h,('Package hash',name)
    freeze=json.loads((R/'results/SUPPORT_FREEZE63.json').read_text())
    for name,h in freeze['source_hashes'].items():assert sha(R/'code'/name)==h,('Diagnostic source',name)
    results=json.loads((R/'results/SUPPORT_STUDY63.json').read_text());cases={c['id']:c for c in freeze['cases']}
    assert len(cases)==len(results['rows'])==48
    for row in results['rows']:
        spec=cases[row['id']]['spec'];assert digest(spec)==row['input_sha256']
        assert ground_truth(spec)==row['truth']
        p=R/'results'/row['certificate'];assert sha(p)==row['certificate_sha256']
        proof=verify_bound(json.loads(gzip.decompress(p.read_bytes())),spec)
        assert proof['status']=='PASS' and F(proof['upper'])==F(proof['lower'])==F(row['truth']['lower'])
    replay=json.loads((R/'results/BINDING_REPLAY.json').read_text())
    assert replay['status']=='PASS' and replay['requests']==405 and replay['certificates']==389
    assert replay['PASS']==342 and replay['PASS_LOWER_ONLY']==47 and replay['no_certificate']==16
    rr=list(csv.DictReader((R/'evidence/r61/results/ALL_RUNS.csv').open()));assert len(rr)==405
    structure=json.loads((R/'results/STRUCTURAL61_REPLAY.json').read_text())
    assert structure['status']=='PASS' and structure['robust_certified_instances']==198
    assert json.loads((R/'results/BINDING_TESTS63.json').read_text())['rejected_mutations']==21
    build=json.loads((R/'results/BUILD63.json').read_text())
    assert build['main']['excluding_references']<=30 and build['electronic_companion']['pages']<=build['main']['pages']
    for data in build.values():assert not data['reference_warnings'] and not data['overfull']
    return {'status':'PASS','root_cases_independently_rechecked':48,'historical_requests_preserved':405,
            'current_two_sided_replay':342,'numerical_lower_only_replay':47,'manifest_checked':manifest}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--no-manifest',action='store_true');a=p.parse_args();print(json.dumps(verify(not a.no_manifest),indent=2))
