#!/usr/bin/env python3
"""Complete multi-tier, one-review premium-shift inaction regions.
Future continuation is held fixed; these are not permanent-parameter comparative statics.
"""
from pathlib import Path
import sys,json
import numpy as np
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent/'or-r6-20260921'))
from compute import Model,solve

def main():
 M=Model();V,pi,d=solve(M);q=d['theta'];rows=[]
 for t in range(M.T):
  B=d['B']+M.beta*d['P']@V[t+1]
  for z in range(3):
   for j in range(len(q)):
    lower=max([(B[z,i]-B[z,j])/(q[j]-q[i])-M.lam*(q[j]-q[i]) for i in range(j)],default=-np.inf)
    upper=min([(B[z,j]-B[z,i])/(q[i]-q[j])+M.lam*(q[i]-q[j]) for i in range(j+1,len(q))],default=np.inf)
    # Check representatives and both sides of any finite interval endpoints.
    probes=[0.,lower+1e-6 if np.isfinite(lower) else -10.,upper-1e-6 if np.isfinite(upper) else 10.]
    for shift in probes:
     obj=B[z]+shift*q-M.lam*(q-q[j])**2;greatest=len(q)-1-np.argmax(obj[::-1]);inside=lower<=shift<upper
     if abs(shift-lower)>1e-10 and abs(shift-upper)>1e-10:assert (greatest==j)==inside
    rows.append(dict(t=t,z=z,tier=float(q[j]),lower=None if not np.isfinite(lower) else float(lower),upper=None if not np.isfinite(upper) else float(upper),finite_width=None if not (np.isfinite(lower) and np.isfinite(upper)) else float(max(0,upper-lower)),nonempty=bool(lower<upper),retains_at_recorded_premium=bool(lower<=0<upper),continuation_grid_concave=bool(np.max(np.diff(B[z],2))<=1e-12)))
 (HERE/'results/inaction_regions.json').write_text(json.dumps(rows,indent=2)+'\n');print('nonempty',sum(r['nonempty'] for r in rows),'retaining',sum(r['retains_at_recorded_premium'] for r in rows),'total',len(rows))
if __name__=='__main__':main()
