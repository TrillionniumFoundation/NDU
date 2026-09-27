from pathlib import Path
from fractions import Fraction as F
import json
from box_solver import aggregate,encode
from benchmark import fixture
from price_prefix_baseline import solve
R=Path(__file__).resolve().parents[1]
def run():
    specs=json.loads((R/'PROTOCOL.json').read_text())['joint_specs']
    p=R/'results'/'priced_prefix.json';rows=json.loads(p.read_text()) if p.exists() else []
    for s in specs:
        if any(x['id']==s['id'] for x in rows):continue
        d,a,rho,B=fixture(s['seed'],s['k'],s['n'],s['charged'],s.get('replicas',1));d,_=aggregate(d,a)
        ans=solve(d,a,rho,B,s['m'],F(s['eps']),seconds_limit=8,max_nodes=5001)
        rows.append(encode(dict(id=s['id'],**ans)));p.write_text(json.dumps(rows,indent=2)+'\n')
        print(s['id'],ans['status'],ans['nodes'],float(ans['gap']),ans['seconds'],flush=True)
if __name__=='__main__':run()
