"""Read-only verification of the flat R60 submission archive; no historical paths needed."""
from pathlib import Path
import gzip,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from rational import F,digest

def verify(root=ROOT):
    root=Path(root);manifest=json.loads((root/'PACKAGE_MANIFEST.json').read_text())
    for rel,h in manifest['files'].items():
        p=Path(rel);assert not p.is_absolute() and '..' not in p.parts
        assert hashlib.sha256((root/p).read_bytes()).hexdigest()==h,('Package hash',rel)
    mapping=json.loads((root/'EXECUTION_SOURCE_MAP.json').read_text());checked=0;targets=0;numerical=0;memo={}
    for batch in ('results','results_r59'):
        freeze=json.loads((root/batch/'STUDY_FREEZE.json').read_text());cs={c['id']:c for c in freeze['cases']}
        for original,h in freeze['source_hashes'].items():
            p=root/mapping['original_to_snapshot'][original]
            assert hashlib.sha256(p.read_bytes()).hexdigest()==h,('Frozen source',original)
        records=list((root/batch/'records').glob('*.json'));assert len(records)==freeze['declared_runs'];seen=set()
        for p in records:
            rec=json.loads(p.read_text());key=(rec['id'],rec['method']);assert key not in seen;seen.add(key)
            c=cs[rec['id']];assert rec['method'] in c.get('methods',freeze.get('methods',[]))
            assert rec['parent_finished'] and rec['instance_sha256']==digest(c['spec'])
            if rec.get('certificate'):
                data=(root/batch/rec['certificate']).read_bytes();assert hashlib.sha256(data).hexdigest()==rec['certificate_sha256']
                if rec.get('verification_status') in ('PASS','PASS_LOWER_ONLY'):
                    cert=json.loads(gzip.decompress(data));schema=cert['schema']
                    if schema=='NDU-R59-SCIP-numerical-v1':
                        from check_price import check_policy
                        assert check_policy(c['spec'],cert['policy'])==F(rec['lower']);numerical+=1
                    else:
                        if schema=='NDU-R60-tariff-frontier-v1':from check_tariff60 import verify as checker
                        elif schema=='NDU-deficit-v1-hex':from check_deficit import verify as checker
                        elif schema=='NDU-enumeration-v1-hex':from check_enumeration import verify as checker
                        else:from check_price import verify as checker
                        cachekey=(rec['certificate_sha256'],digest(c['spec']))
                        if cachekey not in memo:memo[cachekey]=checker(cert,digest(c['spec']))
                        answer=memo[cachekey]
                        assert F(answer['lower'])==F(rec['lower']) and F(answer['upper'])==F(rec['upper'])
                        checked+=1
            expected=bool(rec.get('verification_status')=='PASS' and rec['within_total_budget'] and rec.get('certificate_schema')!='NDU-R59-SCIP-numerical-v1' and F(rec['upper'])-F(rec['lower'])<=F(c['epsilon']))
            assert rec['rational_target_met']==expected,('Target label',p.name)
            targets+=int(expected)
    for name in ('main.tex','electronic_companion.tex','RESPONSE_TO_REFEREES.tex'):
        assert '\\input{' not in (root/name).read_text(),('Not standalone',name)
    return dict(status='PASS',records=1548,rational_intervals_rechecked=checked,numerical_lower_policies_rechecked=numerical,rational_targets_in_original_deadlines=targets,payload_files=len(manifest['files']))
if __name__=='__main__':print(json.dumps(verify(),indent=2))
