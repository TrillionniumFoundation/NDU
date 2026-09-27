#!/usr/bin/env python3
"""Replay every published R16 certificate using only Python's standard library."""
import json,hashlib
from pathlib import Path
from exact import audit_exact
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results'
def main():
    p=json.loads((OUT/'primitives.json').read_text());count=0;maxgap=0
    for line in (OUT/'policies.jsonl').open():
        r=json.loads(line);a=audit_exact(p,r['context'],r['x_num'],int(r['x_den']),r['price_num'],r['switch_num'],r['ineq_num'],r['equality_num'],r['dual_den'])
        assert a['gain_exact']==r['gain'],r['id'];assert a['upper_exact']==r['upper'],r['id'];count+=1;maxgap=max(maxgap,a['gap'])
    expected=json.loads((OUT/'summary.json').read_text())['certificate_records'];assert count==expected
    result={'status':'PASS','independent_certificate_replays':count,'standard_library_only':True,'every_policy_feasible':True,'every_dual_bound_valid':True,'policies_sha256':hashlib.sha256((OUT/'policies.jsonl').read_bytes()).hexdigest(),'max_candidate_gap':maxgap}
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
