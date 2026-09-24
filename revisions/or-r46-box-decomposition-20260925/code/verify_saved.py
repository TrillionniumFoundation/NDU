"""Regenerate canonical rational witnesses; do not relabel local timing as CI timing."""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib,time,sys
from benchmark import fixture
from box_solver import solve,encode
from check_certificate import check
R=Path(__file__).resolve().parents[1]
def run():
    rows=json.loads((R/'results/joint.json').read_text());checks=[]
    (R/'results/certificates').mkdir(exist_ok=True)
    for row in rows:
        data,a,rho,B=fixture(row['seed'],row['k'],row['n'],row['charged'],row.get('replicas',1))
        target=R/'results'/row['certificate']
        start=time.perf_counter()
        if target.exists():
            blob=target.read_bytes();record=json.loads(gzip.decompress(blob));mode='existing canonical bytes checked'
        else:
            ans=solve(data,a,rho,B,row['m'],F(row['eps']),max_nodes=row['evaluated_nodes'],seconds_limit=None,price_steps=8)
            assert (ans['lower_bound'],ans['upper_bound'],ans['status'])==(F(row['lower']),F(row['upper']),row['status'])
            ans['seconds']=row['runtime'];record=encode(ans)
            blob=gzip.compress(json.dumps(record,sort_keys=True,separators=(',',':')).encode(),mtime=0)
            target.write_bytes(blob);mode='rational solver regenerated canonical witness'
        validated=check(record);elapsed=time.perf_counter()-start
        digest=hashlib.sha256(blob).hexdigest()
        assert digest==row['certificate_sha256'],(row['id'],'Canonical witness mismatch')
        checks.append(dict(id=row['id'],mode=mode,certificate_sha256=digest,verification_seconds=elapsed,independent_check=validated))
        (R/'results/verification_checkpoints.json').write_text(json.dumps(checks,indent=2)+'\n')
        print(row['id'],'rational witness and coverage PASS',flush=True)
    comparators=json.loads((R/'results/comparators.json').read_text());small={x['id']:x for x in rows}
    for c in comparators:
        r=small[c['id']];tol=1e-6
        assert c['tangent']['numerical_upper']+tol>=float(F(r['lower']))
        assert c['secant']['value']<=float(F(r['upper']))+tol
        assert all(c[z]['max_model_residual']<tol for z in ['tangent','secant'])
        if 'exact_value' in r:
            exact=float(F(r['exact_value']));assert c['tangent']['numerical_upper']+tol>=exact and c['secant']['value']<=exact+tol
    out=dict(status='PASS',canonical_witnesses=len(checks),numeric_comparisons_checked=len(comparators),note='Local measured times are retained as provenance, not rerun CI benchmark timings. Regeneration uses each recorded exact node count rather than a wall-clock stop.',checks=checks)
    (R/'results/CERTIFICATE_REGENERATION.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':run()
