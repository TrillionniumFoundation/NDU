"""Exact fee simplification, original-fee certificates, and fee frontiers.

Fee perturbations never modify probabilities, caps, rewards, or policy timing.
All arithmetic and interval comparisons in this module are rational.
"""
from __future__ import annotations
from copy import deepcopy
from rational import F, encode, digest
from price_path import normalize, allocate
from tariff60 import solve as exact_tariff


def simplify(charges, d):
    """Minimize total absolute deviation with at most d unchanged outliers.

    Sorted contiguous windows and lower medians give a deterministic optimum.
    Fee and index ties use their original catalog index.
    """
    fees = list(map(F, charges)); n = len(fees)
    if not n or type(d) is not int or not 0 <= d < n:
        raise ValueError('0 <= d < number of commands required')
    order = sorted(range(n), key=lambda i: (fees[i], i))
    vals = [fees[i] for i in order]; prefix = [F(0)]
    for x in vals: prefix.append(prefix[-1]+x)
    length = n-d; best = None
    for left in range(d+1):
        right = left+length; mid = left+(length-1)//2; fee = vals[mid]
        cost = fee*(mid-left)-(prefix[mid]-prefix[left]) + (prefix[right]-prefix[mid+1])-fee*(right-mid-1)
        key = (cost, fee, left)
        if best is None or key < best[0]: best = (key, left, right)
    (cost, fee, _), left, right = best
    projected = list(fees)
    for i in order[left:right]: projected[i] = fee
    ex = [i for i,x in enumerate(projected) if x != fee]
    return dict(standard_fee=fee, charges=projected, exceptions=ex,
                absolute_deviation=cost, retained_window=order[left:right])


def error_budget(charges, projected, m):
    error = [F(x)-F(y) for x,y in zip(charges, projected)]
    plus = sum(sorted((max(F(0),x) for x in error), reverse=True)[:m], F(0))
    minus = sum(sorted((max(F(0),-x) for x in error), reverse=True)[:m], F(0))
    return dict(error=error, positive_budget=plus, negative_budget=minus,
                regret_bound=plus+minus, absolute_deviation=sum(map(abs,error),F(0)))


def solve(spec, epsilon, max_exceptions=12):
    eps=F(epsilon); data,a,fees,B,m=normalize(spec)
    if eps<0: raise ValueError('Nonnegative accuracy required')
    # L1 threshold is monotone in the permitted exception count.
    lo,hi=0,len(a)-1
    while lo<hi:
        mid=(lo+hi)//2
        if simplify(fees,mid)['absolute_deviation']<=eps: hi=mid
        else: lo=mid+1
    projection=simplify(fees,lo)
    surrogate=deepcopy(spec); surrogate['charges']=encode(projection['charges'])
    answer=exact_tariff(surrogate,max_exceptions=max_exceptions)
    book=tuple(map(F,answer['certificate']['policy']['book']))
    policy=allocate(data,book,B,dict(zip(a,fees)))
    budget=error_budget(fees,projection['charges'],m)
    upper=answer['upper']+budget['negative_budget']
    assert policy['value']<=upper and upper-policy['value']<=eps
    cert=encode(dict(schema='NDU-R61-robust-tariff-v1',spec=spec,
        instance_sha256=digest(spec),surrogate_certificate=answer['certificate'],
        projection=projection,policy=policy,lower=policy['value'],upper=upper,
        error_budget=budget,epsilon=eps,selected_exception_budget=lo))
    return dict(status='EXACT' if upper==policy['value'] else 'TOLERANCE',
        lower=policy['value'],upper=upper,certificate=cert,
        selected_exception_budget=lo,projected_exceptions=len(projection['exceptions']),
        regret_bound=budget['regret_bound'])


def verify(cert, expected_sha256=None):
    """Compatibility entry point; all certified claims use the independent checker."""
    from check_robust61 import verify as independent_verify
    return independent_verify(cert, expected_sha256)


def frontier(spec):
    """Complete uniform-fee envelope, exact endpoints, deterministic size ties.

    The existing zero-fee certificate supplies maximum capacities per size.
    Paths attaining each capacity are reconstructed using the same recurrence;
    no continuous price grid is used to identify switching fees.
    """
    data,a,fees,B,m=normalize(spec); free=deepcopy(spec); free['charges']=['0']*len(a)
    solved=exact_tariff(free,max_exceptions=0)
    table=[[None if x is None else F(x) for x in row] for row in solved['certificate']['branches'][0]['rows']]
    gain={(u,v):sum((w*max(F(0),min(b,a[v])-a[u]) for w,b,t in zip(data.weights,data.caps,data.ceilings) if a[v]<=t),F(0)) for u in range(len(a)) for v in range(u+1,len(a))}
    lines=[]
    for size,row in enumerate(table,1):
        if all(x is None for x in row): continue
        cap=max(x for x in row if x is not None); v=row.index(cap); indices=[v]
        for level in range(size-2,-1,-1):
            u=next(u for u in range(v) if table[level][u] is not None and table[level][u]+gain[u,v]==table[level+1][v])
            indices.append(u);v=u
        lines.append(dict(size=size,intercept=data.reward_r[0]*min(B,cap),capacity=cap,book=[a[i] for i in reversed(indices)]))
    cuts={F(0)}
    for p in lines:
        for q in lines:
            if p['size']!=q['size']:
                x=(p['intercept']-q['intercept'])/(p['size']-q['size'])
                if x>=0: cuts.add(x)
    cuts=sorted(cuts); segments=[]
    def winner(fee): return max(lines,key=lambda row:(row['intercept']-row['size']*fee,-row['size']))
    for i,left in enumerate(cuts):
        right=cuts[i+1] if i+1<len(cuts) else None
        selected=winner(left+1 if right is None else (left+right)/2)
        if segments and segments[-1]['size']==selected['size']:
            segments[-1]['right']=right
        else: segments.append(dict(left=left,right=right,**selected))
    return encode(dict(lines=lines,segments=segments,
        switches=[dict(fee=s['left'],**winner(s['left'])) for s in segments[1:]],
        zero_fee_winner=winner(F(0)),tie_rule='smallest optimal cardinality; deterministic earliest predecessor',
        capacity_certificate=solved['certificate']))
