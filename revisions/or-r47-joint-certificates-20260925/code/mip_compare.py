"""Uneliminated original-model MIP comparisons, all twelve primary cases."""
from pathlib import Path
from fractions import Fraction as F
import json,time,platform,sys
from benchmark import fixture,specs
from coarsening import encode
from mip_baseline import direct_milp
R=Path(__file__).resolve().parents[1]

def run():
    import scipy
    path=R/'results/mip.json';primary=[x for x in specs() if x['category']=='primary']
    protocol=dict(cases=[s['id'] for s in primary],segments=64,time_limit_per_envelope_seconds=2,
       envelopes=['tangent','secant'],scope='Floating-point direct original formulation, not exact rational certificates')
    (R/'MIP_PROTOCOL.json').write_text(json.dumps(protocol,indent=2)+'\n')
    results=json.loads(path.read_text()) if path.exists() else dict(protocol=protocol,python=sys.version,scipy=scipy.__version__,platform=platform.platform(),cases=[])
    old={x['id'] for x in results['cases']}
    refs={x['id']:F(x['reference']['value']) for x in json.loads((R/'results/joint.json').read_text())['cases'] if x['reference']}
    for s in primary:
        if s['id'] in old:continue
        D,a,rho,B=fixture(s['seed'],s['k'],s['n'],s['spread'],s['regimes'],s['charged'])
        t=direct_milp(D,a,rho,B,s['m'],segments=64,envelope='tangent',time_limit=2)
        c=direct_milp(D,a,rho,B,s['m'],segments=64,envelope='secant',time_limit=2)
        width=None if t['numerical_upper'] is None or c.get('value') is None else t['numerical_upper']-c['value']
        v=float(refs[s['id']])
        if t['numerical_upper'] is not None:assert v<=t['numerical_upper']+1e-6
        if c.get('value') is not None:assert c['value']<=v+1e-6
        row=dict(**s,tangent=t,secant=c,signed_bracket_width=width,exact_reference=str(refs[s['id']]))
        results['cases'].append(row);path.write_text(json.dumps(results,indent=2)+'\n')
        print(s['id'],'status',t['status'],c['status'],'width',width,flush=True)
if __name__=='__main__':run()
