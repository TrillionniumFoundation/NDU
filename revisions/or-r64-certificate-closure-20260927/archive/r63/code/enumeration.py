"""Complete book enumeration and independent support-price verification."""
from itertools import combinations
import time
from rational import F,qstr,encode,digest
from price_path import normalize,allocate,DeadlineExceeded
from check_price import model,check_policy,price_bound,require

def solve(spec,seconds=None,progress=None):
    started=time.perf_counter();d,a,rho,B,m=normalize(spec);rows=[]
    best=allocate(d,(a[0],),B,dict(zip(a,rho)));complete=True
    if progress is not None:progress.update(policy=best,books_evaluated=0)
    try:
        for ell in range(1,m+1):
            for ids in combinations(range(len(a)),ell):
                if a[ids[0]]>min(B,min(d.caps)):continue
                if seconds is not None and time.perf_counter()-started>=seconds:raise DeadlineExceeded()
                p=allocate(d,tuple(a[i] for i in ids),B,dict(zip(a,rho)))
                rows.append({'indices':ids,'price':p['price'],'upper':p['value']})
                if p['value']>best['value']:best=p
                if progress is not None:progress.update(policy=best,books_evaluated=len(rows))
    except DeadlineExceeded:complete=False
    U=best['value'] if complete else d.mean_reward(F(1))
    cert={'schema':'NDU-enumeration-v1-hex','spec':spec,'instance_sha256':digest(spec),'complete':complete,'books':encode(rows),'policy':encode(best),'lower':qstr(best['value']),'upper':qstr(U)}
    return {'status':'EXACT' if complete else 'TIME_LIMIT','lower':best['value'],'upper':U,'gap':U-best['value'],'books_evaluated':len(rows),'seconds':time.perf_counter()-started,'certificate':cert}

from check_enumeration import verify  # Compatibility alias; independent checker module.
