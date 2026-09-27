"""Exact common-cap optimization by the proved two-command reduction."""
from itertools import combinations
from fractions import Fraction as F
import time
from price_path import normalize,allocate,encode,digest

def solve_common_cap(spec):
    begin=time.perf_counter();d,a,rho,B,m=normalize(spec)
    if len(set(d.caps))!=1 or not d.common:raise ValueError('Common expected caps and terminal reward required')
    best=None;proof=[]
    for size in range(1,min(2,m)+1):
        for ids in combinations(range(len(a)),size):
            book=tuple(a[i] for i in ids)
            if book[0]>min(B,d.caps[0]):continue
            policy=allocate(d,book,B,dict(zip(a,rho)))
            proof.append(dict(indices=list(ids),price=str(policy['price']),upper=str(policy['value'])))
            if best is None or policy['value']>best['value']:best=policy
    cert=dict(schema='NDU-common-cap-v1',spec=spec,instance_sha256=digest(spec),policy=encode(best),
              lower=str(best['value']),upper=str(best['value']),books=proof)
    return dict(status='EXACT',lower=best['value'],upper=best['value'],books=len(proof),seconds=time.perf_counter()-begin,certificate=cert)
