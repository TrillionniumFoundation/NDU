"""Reproducible synthetic catalog study; no empirical calibration claim."""
from fractions import Fraction as F
from pathlib import Path
import json, time, platform
from catalog import Model, solve
R=Path(__file__).resolve().parents[1]
rows=[]
for family in ('uniform','clustered','concentrated_weights'):
    for k,n in ((32,16),(128,32)):
        if family=='clustered':
            caps=sorted([F(1,4)+F(j,16*k) for j in range(k//2)]
                        +[F(3,4)+F(j,16*k) for j in range(k//2)])
        else:
            caps=[F(j,k+1) for j in range(1,k+1)]
        raw=([1 if j<k-1 else k*k for j in range(k)]
             if family=='concentrated_weights' else [1]*k)
        p=Model.make(caps,[F(w,sum(raw)) for w in raw],
                     [F((j*7)%11,3) for j in range(k)])
        catalog=tuple(F(j,n-1) for j in range(n))
        charges=tuple(F((j*5)%7,6400) for j in range(n))
        for delta in (F(0),F(1,8),F(1)):
            start=time.perf_counter()
            answers=solve(p,catalog,charges,8,delta)
            elapsed=time.perf_counter()-start
            rows.append(dict(family=family,k=k,N=n,budget=8,delta=delta,
                             total=answers[-1].total,service_loss=answers[-1].service_loss,
                             level_charge=answers[-1].level_charge,
                             symbols=len(answers[-1].codebook),seconds=elapsed,
                             codebook=answers[-1].codebook))
(R/'results/catalog_study.json').write_text(json.dumps(dict(
    status='PASS',python=platform.python_version(),platform=platform.platform(),
    timing_scope='One process, perf_counter around solve including validation, reconstruction and direct replay; not comparable to legacy process-isolated frontier timings.',
    rows=rows),indent=2,default=str)+'\n')
print('Catalog study PASS:',len(rows),'cases')
