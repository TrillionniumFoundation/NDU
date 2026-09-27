"""Exact-rational two-price recovery with a fixed union execution alphabet.

The original m-symbol upper bound is NOT an upper bound for a 2m-symbol
policy. They are reported separately, with the actual opening-charge excess.
"""
from __future__ import annotations
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'or-r43-prefix-decomposition-20260924'/'code'))
from decomposition import PriceDP, Model, rational, solve_allocation, branch_maximum
from unified import branch_rule


def policy(model, book, targets, delta, cost):
    """Reconstruct a canonical policy at supplied exact branch targets."""
    ys=[]; laws=[]; operating=F(0)
    for j,(p,t) in enumerate(zip(model.probabilities,targets)):
        y,law=branch_rule(model,j,book,t,delta)
        ys.append(y); laws.append(law)
        operating+=p*(sum(prob*model.reward(x) for x,prob in law)-model.gamma[j]*y*y/2)
    return dict(book=tuple(book),targets=tuple(targets),intermediate=tuple(ys),
                lotteries=tuple(laws),charge=cost,value=operating-cost,
                total=sum(p*t for p,t in zip(model.probabilities,targets)))


def recover(model: Model, catalog, charges, budget: int, promise, delta=0,
            epsilon=F(1,10000)):
    """Return exact feasibility, [L_m,U_m], and a distinct augmented policy.

    Only two endpoint policies are retained; old price tables are discarded.
    Nonnegative charges and positive epsilon are mandatory. Floats are rejected.
    """
    a=tuple(map(rational,catalog)); rho=tuple(map(rational,charges))
    B,delta,eps=map(rational,(promise,delta,epsilon))
    if eps<=0: raise ValueError('Positive rational epsilon required.')
    low=-max(g*b for g,b in zip(model.gamma,model.caps))-1
    high=model.r+1
    bar=sum(p*b for p,b in zip(model.probabilities,model.caps))
    calls=0; bits=0; total_edges=0
    def oracle(lam):
        nonlocal calls,bits,total_edges
        dp=PriceDP(model,a,rho,budget,B,delta,lam)
        upper,ids=dp.bound()
        book=tuple(a[i] for i in ids)
        targets=tuple(branch_maximum(model,j,book,lam,delta)[1]
                      for j in range(len(model.caps)))
        ans=policy(model,book,targets,delta,sum(rho[i] for i in ids))
        assert ans['value']+lam*(B-ans['total'])==upper
        calls+=1; bits=max(bits,dp.max_bits()); total_edges+=len(dp.edge)
        return dict(price=lam,upper=upper,policy=ans)
    left,right=oracle(low),oracle(high)
    assert left['policy']['total']>=B>=right['policy']['total']
    while (right['price']-left['price'])*(bar-a[0])/4>eps:
        if left['policy']['total']==B or right['policy']['total']==B: break
        mid=oracle((left['price']+right['price'])/2)
        if mid['policy']['total']>=B: left=mid
        else: right=mid
    m=min(budget,len(a))
    exact=next((v for v in (left,right) if v['policy']['total']==B),None)
    if exact is not None:
        left=right=exact; theta=F(1); spread=F(0)
        union=exact['policy']; mixed=union['value']; excess=F(0)
    else:
        minus,plus=left['policy'],right['policy']
        s0,s1=minus['total'],plus['total']
        theta=(B-s1)/(s0-s1)
        targets=tuple(theta*x+(1-theta)*y for x,y in zip(minus['targets'],plus['targets']))
        book=tuple(sorted(set(minus['book'])|set(plus['book'])))
        cost=sum(rho[a.index(x)] for x in book)
        union=policy(model,book,targets,delta,cost)
        mixed=theta*minus['value']+(1-theta)*plus['value']
        excess=cost-theta*minus['charge']-(1-theta)*plus['charge']
        spread=(right['price']-left['price'])*(s0-B)*(B-s1)/(s0-s1)
    upper=min(left['upper'],right['upper'])
    original=[]
    for book in {left['policy']['book'],right['policy']['book']}:
        ans=solve_allocation(model,book,B,delta)
        original.append(policy(model,book,ans.targets,delta,sum(rho[a.index(x)] for x in book)))
    if len(union['book'])<=m: original.append(union)
    feasible=max(original,key=lambda p:(p['value'],-len(p['book']),p['book']))
    assert feasible['value']<=upper
    assert union['total']==B and len(union['book'])<=min(2*m,len(a))
    assert 0<=spread<=eps and excess>=0
    assert union['value']>=mixed-excess>=upper-spread-excess
    return dict(schema='ndu-r44-two-price-v1',model=asdict(model),catalog=a,charges=rho,
                budget=m,promise=B,delta=delta,epsilon=eps,left=left,right=right,
                theta=theta,mixed_value=mixed,price_error=spread,charge_excess=excess,
                original_lower=feasible['value'],original_upper=upper,
                original_policy=feasible,augmented_policy=union,
                oracle_calls=calls,max_dp_bits=bits,edge_entries_total=total_edges)


def encode(x):
    if isinstance(x,F): return str(x)
    if isinstance(x,dict): return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)): return [encode(v) for v in x]
    return x
