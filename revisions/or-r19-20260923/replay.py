#!/usr/bin/env python3
"""Independent replay, usable with python -S and standard library only."""
import sys,json,gzip,hashlib
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parent;OLD=R.parent/'or-r16-20260922';sys.path.insert(0,str(OLD))
from exact import audit_exact

def audit(p,r):
    a=audit_exact(p,r['context'],r['x_num'],int(r['x_den']),r['price_num'],r['switch_num'],r['ineq_num'],r['equality_num'],r['dual_den'])
    assert a['gain_exact']==r['gain'],'stored primal value differs'
    assert a['upper_exact']==r['upper'],'stored dual value differs'
    return a

def run():
    p=json.loads((OLD/'results/primitives.json').read_text());count=0;digest=hashlib.sha256();maxgap=0.;first=None
    with gzip.open(OLD/'results/policies.jsonl.gz','rb') as stream:
        for line in stream:
            digest.update(line);r=json.loads(line);a=audit(p,r);count+=1;maxgap=max(maxgap,a['gap'])
            if first is None:first=r
    assert count==16384
    assert digest.hexdigest()==json.loads((OLD/'results/verification.json').read_text())['policies_sha256']
    structural=0
    for src in [OLD/'results/structural_certificates.json',R/'results/boundary_certificates.json.gz']:
        records=json.loads(gzip.decompress(src.read_bytes()) if src.suffix=='.gz' else src.read_text())
        for item in records:
            for key in ['reference','proposal']:audit(item['primitive'],item[key]);structural+=1
            rr=item['proposal'];a=audit(item['primitive'],rr)
            res=[F(int(z),rr['dual_den'])-sum((F(int(u)*int(x),32*int(rr['x_den'])) for u,x in zip(row,rr['x_num'])),F(0)) for row,z in zip(item['primitive']['Unum'],rr['price_num'])]
            delta=F(rr['upper'])-F(a['raw_gain_exact'])-sum((v*v/2 for v in res),F(0))
            assert delta==F(item['base_gap']) and delta>=0
    assert structural==256
    negative=0
    for mutation in ['box','negative_price','switch_capacity','stored_upper']:
        r=json.loads(json.dumps(first))
        if mutation=='box':r['x_num'][0]=str(2*int(r['x_den']))
        elif mutation=='negative_price':r['ineq_num'][0]=-1
        elif mutation=='switch_capacity':r['switch_num'][0]=10**30
        else:r['upper']=str(F(r['upper'])-1)
        try:audit(p,r)
        except AssertionError:negative+=1
        else:raise AssertionError(('tampered certificate accepted',mutation))
    result={'status':'PASS','standard_library_only':True,'primary_policy_replays':count,'structural_policy_replays':structural,'total_independent_policy_replays':count+structural,'negative_controls_rejected':negative,'policies_uncompressed_sha256':digest.hexdigest(),'max_primary_gap':maxgap,'response_gap_identities_verified':128}
    if '--check' in sys.argv:assert json.loads((R/'results/replay.json').read_text())==result
    else:(R/'results/replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
if __name__=='__main__':run()
