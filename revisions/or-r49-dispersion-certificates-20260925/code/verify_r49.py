"""Verify all protocol cases, original-space certificates and reference intervals."""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib,sys,platform,datetime
HERE=Path(__file__).resolve().parent;R=HERE.parent
sys.path.insert(0,str(HERE))
from check_pooling import check

def run():
    p=R/'PROTOCOL.json';h=hashlib.sha256(p.read_bytes()).hexdigest();protocol=json.loads(p.read_text())
    raw=json.loads((R/'results/study.json').read_text());mip=json.loads((R/'results/mip.json').read_text())
    assert raw['protocol_sha256']==mip['protocol_sha256']==h
    rows=raw['cases'];ids=[r['id'] for r in rows];assert len(ids)==len(set(ids))==64
    expected={f'paired-case-{j:02d}' for j in range(24)}
    expected|={f'common-k{k}-n{n}-s{s}' for k in protocol['additional_common_eligibility']['histories'] for n in protocol['additional_common_eligibility']['catalog_sizes'] for s in protocol['additional_common_eligibility']['seeds']}
    # The exact saved identifiers, not the order, determine protocol coverage.
    common_actual={r['id'] for r in rows if r['family']=='common'}
    assert len(common_actual)==16
    assert {(r['k'],r['n'],r['seed']) for r in rows if r['family']=='common'}=={(k,n,s) for k in protocol['additional_common_eligibility']['histories'] for n in protocol['additional_common_eligibility']['catalog_sizes'] for s in protocol['additional_common_eligibility']['seeds']}
    assert {r['id'] for r in rows if r['family']=='paired'}=={f'paired-case-{j:02d}' for j in range(24)}
    stress=protocol['eligibility_stress']
    assert {(r['seed'],r['epsilon'],r['node_limit']) for r in rows if r['family']=='stress'}=={(s,e,n) for s in stress['seeds'] for e in stress['epsilon'] for n in stress['node_limits']}
    checked=[]
    for r in rows:
        f=R/r['certificate'];data=f.read_bytes();assert hashlib.sha256(data).hexdigest()==r['certificate_sha256']
        c=json.loads(gzip.decompress(data));answer=check(c)
        for field in ['lower_bound','upper_bound','gap','status','evaluated_nodes']:
            assert c[field]==r[field],(r['id'],field)
        ref=r.get('exact_reference') or (r.get('historical_reference') or {}).get('original')
        if ref is not None:assert F(r['lower_bound'])<=F(ref)<=F(r['upper_bound'])
        checked.append(dict(id=r['id'],sha256=r['certificate_sha256'],check=answer))
    assert len(mip['cases'])==18 and len({r['id'] for r in mip['cases']})==18
    for r in mip['cases']:
        assert set(r['envelopes'])=={'tangent','secant'}
        ref=float(F(r['exact_reference']))
        for env,z in r['envelopes'].items():
            for key in ['status','seconds','approximation_error','segments']:assert key in z
            if env=='tangent' and z.get('numerical_upper') is not None:assert z['numerical_upper']+1e-6>=ref
            if env=='secant' and z.get('value') is not None:assert z['value']<=ref+1e-6
    result=dict(status='PASS',protocol_sha256=h,exact_certificates=len(checked),mip_solves=36,
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,platform=platform.platform(),cases=checked)
    (R/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: 64 exact certificates, complete protocol populations, 36 numerical envelope records')
if __name__=='__main__':run()
