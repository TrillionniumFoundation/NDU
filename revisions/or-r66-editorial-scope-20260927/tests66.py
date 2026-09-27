"""Document existing receipt semantics; do not change an accepted checker."""
from pathlib import Path
from copy import deepcopy
import argparse, gzip, hashlib, json, sys, time
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'code'))
from binding65 import bind_legacy, verify_request, NUMERICAL, ROBUST
from rational import digest
EXTENSIONS={
    'authenticated_origin': {'claimed': True, 'authority': 'unverified-extension'},
    'runtime_attestation': {'guard_used': 999, 'on_time': True},
    'editorial_approval': {'accepted': True},
    'unreported_optimality_claim': {'globally_exact': True},
    'vendor_extension': {'certified': True, 'payload': 'not-a-receipt-conclusion'}}

def mathematical_receipt(value):
    # Elapsed seconds are an execution diagnostic, not a certified mathematical conclusion.
    if isinstance(value,dict):return {k:mathematical_receipt(v) for k,v in value.items() if k!='seconds'}
    if isinstance(value,list):return [mathematical_receipt(v) for v in value]
    return value

def run(output):
    start=time.perf_counter(); output.mkdir(parents=True,exist_ok=True)
    rows=[json.loads(x) for x in (R/'results/r65/replay/REQUEST_RECEIPTS65.jsonl').read_text().splitlines()]
    chosen={}
    for row in rows:
        if 'external_request' not in row: continue
        rec=json.loads((R/'evidence/r61/results/records'/f"{row['id']}--{row['method']}.json").read_text())
        p=R/'evidence/r61/results'/rec['certificate'];cls=row['external_request']['certificate_class']
        if cls not in chosen or p.stat().st_size<chosen[cls][0]: chosen[cls]=(p.stat().st_size,p,row)
    assert len(chosen)==6
    accepted=[];rejected=[];witnesses=[];nested=0
    for cls,(_,p,row) in sorted(chosen.items()):
        cert=json.loads(gzip.decompress(p.read_bytes()));req=row['external_request']
        env=bind_legacy(cert,req);baseline=verify_request(env,req)
        if cls==NUMERICAL:
            assert baseline['status']=='PASS_LOWER_ONLY' and 'upper' not in baseline and not baseline['tolerance_met']
        for key,value in EXTENSIONS.items():
            assert key not in cert and key not in baseline
            changed=deepcopy(env);changed['certificate'][key]=value
            assert mathematical_receipt(verify_request(changed,req))==mathematical_receipt(baseline),(cls,key)
            accepted.append({'class':cls,'extension':key,'mathematical_receipt_unchanged':True})
            # The same fields are forbidden at all exact-schema boundaries.
            for where in ('envelope','external_request','embedded_request'):
                e=deepcopy(env);r=deepcopy(req)
                if where=='envelope':e[key]=value
                elif where=='external_request':r[key]=value
                else:
                    e['request'][key]=value
                    e['request_sha256']=digest(e['request'])
                try: verify_request(e,r)
                except ValueError as exc: rejected.append({'class':cls,'extension':key,'boundary':where,'reason':str(exc)})
                else:raise AssertionError((cls,key,where))
        if cls==ROBUST:
            for key,value in EXTENSIONS.items():
                e=deepcopy(env);e['certificate']['surrogate_certificate'][key]=value
                assert mathematical_receipt(verify_request(e,req))==mathematical_receipt(baseline)
                nested+=1
        witnesses.append({'class':cls,'source_file':p.relative_to(R).as_posix(),
            'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'external_request':req,'certificate':cert,'receipt':baseline})
    assert len(accepted)==30 and len(rejected)==90 and nested==5
    ans={'schema':'NDU-R66-receipt-scope-regression-v1','status':'PASS','baseline_classes':6,
         'legacy_extension_receipts_unchanged':len(accepted),'nested_tariff_receipts_unchanged':nested,
         'exact_schema_extensions_rejected':len(rejected),'numerical_lower_only_preserved':True,
         'excluded_comparison_fields':['seconds (per-execution diagnostic)'],
         'accepted_cases':accepted,'rejected_cases':rejected,'seconds':time.perf_counter()-start,
         'scope':'Finite documentation regression of unchanged checker behavior; not authentication, runtime attestation or new optimization evidence.'}
    (output/'SCOPE_TESTS66.json').write_text(json.dumps(ans,indent=2)+'\n')
    (output/'SCOPE_WITNESSES66.json').write_text(json.dumps({'extensions':EXTENSIONS,'cases':witnesses},indent=2)+'\n')
    return ans
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=R/'results/r66');a=p.parse_args()
    print(json.dumps(run(a.output),indent=2))
