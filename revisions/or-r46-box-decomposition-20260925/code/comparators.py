"""Prospective extension to all 24 primary holdout instances; no selection by outcome."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
from benchmark import fixture
from box_solver import aggregate,encode,exhaustive_joint
from prefix_baseline import solve
from mip_baseline import direct_milp
R=Path(__file__).resolve().parents[1]
def run():
    specs=json.loads((R/'PROTOCOL.json').read_text())['joint_specs'][:24]
    protocol=dict(purpose='Unselected full primary holdout comparison; added after primary run, before these runs.',ids=[s['id'] for s in specs],prefix_seconds=8,prefix_nodes=5001,mip_seconds_each=4,mip_segments=64,notes='Rational prefix interval vs numerical MIP tangent/secant; total nominal solver allowance 8s each. Node expansions are atomic, so exact method allowance is soft.')
    (R/'COMPARATOR_PROTOCOL.json').write_text(json.dumps(protocol,sort_keys=True,indent=2)+'\n')
    path=R/'results'/'comparators.json';rows=json.loads(path.read_text()) if path.exists() else []
    for s in specs:
        if any(r['id']==s['id'] for r in rows):continue
        d,a,rho,B=fixture(s['seed'],s['k'],s['n'],s['charged']);d,_=aggregate(d,a)
        p=solve(d,a,rho,B,s['m'],seconds_limit=8,max_nodes=5001)
        tan=direct_milp(d,a,rho,B,s['m'],segments=64,envelope='tangent',time_limit=4)
        sec=direct_milp(d,a,rho,B,s['m'],segments=64,envelope='secant',time_limit=4)
        upper=tan['numerical_upper'];lower=sec.get('value');raw=None if upper is None or lower is None else upper-lower
        # Signed raw width is retained; display never interprets negative
        # floating residuals as exact negative mathematical intervals.
        rows.append(encode(dict(id=s['id'],prefix=p,tangent=tan,secant=sec,numerical_signed_width=raw,numerical_display_width=None if raw is None else max(0,raw))))
        path.write_text(json.dumps(rows,indent=2)+'\n')
        print(s['id'],p['status'],float(p['gap']),tan['status'],sec['status'],raw,flush=True)
if __name__=='__main__':run()
