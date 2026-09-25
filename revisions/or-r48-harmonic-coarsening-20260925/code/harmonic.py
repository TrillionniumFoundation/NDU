"""R48 harmonic coarsening. Exact rational arithmetic; no changed contract.

A reduced optimum is an upper bound, never an original policy. Original
policies are constructed and checked separately. Classical Cauchy--Schwarz
and arithmetic--harmonic inequalities supply the pooling step.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from dataclasses import asdict
from bisect import bisect_right
from math import isqrt
import sys, time
R47=Path(__file__).resolve().parents[2]/'or-r47-joint-certificates-20260925'/'code'
sys.path.insert(0,str(R47))
from coarsening import reduced_model as minimum_model
from box_solver import Instance,rat,policy,fixed_allocate,solve as box_solve,encode


def reduce(data,catalog,groups):
    """Validate via antecedent guard/eligibility, then rebuild harmonic costs."""
    minimum,groups,_=minimum_model(data,catalog,groups)
    costs=[]; metadata=[]
    for g in groups:
        w=sum(data.weights[j] for j in g)
        h=F(0) if any(data.gamma[j]==0 for j in g) else w/sum(data.weights[j]/data.gamma[j] for j in g)
        avg=sum(data.weights[j]*data.gamma[j] for j in g)/w
        b=sum(data.weights[j]*data.caps[j] for j in g)/w
        bmax=max(data.caps[j] for j in g)
        L=max(data.r,max(data.gamma[j] for j in g)*bmax)
        cap=2*L*sum(data.weights[j]*max(F(0),b-data.caps[j]) for j in g)
        cost=w*(avg-h)*(b-catalog[0])**2/2
        assert min(data.gamma[j] for j in g)<=h<=avg
        costs.append(h)
        metadata.append(dict(weight=w,cap=b,gamma=h,arithmetic_gamma=avg,lipschitz=L,
                             cap_defect=cap,cost_defect=cost,defect=cap+cost))
    small=Instance.make(minimum.caps,minimum.weights,costs,minimum.ceilings,data.r,data.curvature)
    return small,groups,metadata


def sqrt_partition(data,catalog,cap_width,squared_cost_width):
    """Gamma bins [l^2*z,(l+1)^2*z); no floating roots at boundaries."""
    beta,z=rat(cap_width),rat(squared_cost_width)
    if beta<=0 or z<=0: raise ValueError('Positive bin widths required')
    groups={};guard=min(range(len(data.caps)),key=lambda j:data.caps[j])
    for j,(b,g,tau) in enumerate(zip(data.caps,data.gamma,data.ceilings)):
        if j==guard: continue
        q=g/z;root=isqrt(q.numerator//q.denominator)
        key=(bisect_right(catalog,tau),b//beta,root)
        groups.setdefault(key,[]).append(j)
    return tuple([(guard,)]+[tuple(g) for g in groups.values()])


def clipped_targets(data,small,groups,means):
    target=[None]*len(data.caps)
    for z,g in enumerate(groups):
        s=means[z];rest=small.weights[z]*s
        for j in g:
            target[j]=min(s,data.caps[j]);rest-=data.weights[j]*target[j]
        for j in g:
            add=min(rest,data.weights[j]*(data.caps[j]-target[j]))
            target[j]+=add/data.weights[j];rest-=add
        if rest:raise AssertionError('Group repair failed')
    return tuple(target)


def lift(data,small,groups,source,catalog,charges):
    """Exact optimal within-group lift, with a clipping comparison witness."""
    book=tuple(map(rat,source['book']));means=tuple(map(rat,source['targets']))
    charge_map=dict(zip(catalog,charges));clipped=clipped_targets(data,small,groups,means)
    comparison=policy(data,book,clipped,charge_map)
    target=list(clipped);supports=[];post=F(0)
    for z,g in enumerate(groups):
        w=small.weights[z];s=means[z]
        group=Instance.make([data.caps[j] for j in g],[data.weights[j]/w for j in g],
            [data.gamma[j] for j in g],[data.ceilings[j] for j in g],data.r,data.curvature)
        p=fixed_allocate(group,book,s,{x:F(0) for x in book})
        for j,t in zip(g,p['targets']):target[j]=t
        supports.append(dict(price=p['allocation_price'],gross=p['gross']))
        d=max(x for x in book if x<=small.ceilings[z]);bmax=max(data.caps[j] for j in g)
        distance=sum(data.weights[j]*max(data.r,data.gamma[j]*bmax)*abs(clipped[j]-s) for j in g)
        av=sum(data.weights[j]*data.gamma[j] for j in g)/w
        post+=distance+w*(av-small.gamma[z])*max(F(0),s-d)**2/2
    ans=policy(data,book,tuple(target),charge_map)
    assert ans['value']>=comparison['value']
    assert source['value']-ans['value']>=0
    assert source['value']-comparison['value']<=post
    return ans,comparison,supports,post


def solve(data,catalog,charges,B,budget,groups,epsilon=F(1,1000),
          inner_epsilon=None,max_nodes=101,seconds_limit=None,price_steps=8):
    start=time.perf_counter();a=tuple(map(rat,catalog));rho=tuple(map(rat,charges));B=rat(B);eps=rat(epsilon)
    if eps<=0:raise ValueError('Positive tolerance required')
    small,groups,bounds=reduce(data,a,groups)
    inner=box_solve(small,a,rho,B,budget,eps/2 if inner_epsilon is None else rat(inner_epsilon),
        max_nodes=max_nodes,seconds_limit=seconds_limit,price_steps=price_steps,
        aggregate_types=False,record_tables=True)
    lt=time.perf_counter();lifted,clipped,group_supports,post=lift(data,small,groups,inner['policy'],a,rho)
    delta=sum(z['defect'] for z in bounds)
    assert post<=delta
    upper=inner['upper_bound'];lower=lifted['value'];gap=upper-lower
    assert gap>=0 and gap<=inner['gap']+delta
    return dict(schema='ndu-r48-harmonic-certificate-v1',original_model=asdict(data),reduced_model=asdict(small),
        groups=groups,group_bounds=bounds,catalog=a,charges=rho,promise=B,budget=budget,
        requested_epsilon=eps,inner_certificate=inner,policy=lifted,clipped_policy=clipped,
        group_supports=group_supports,lower_bound=lower,upper_bound=upper,gap=gap,
        uniform_defect=delta,posterior_defect=post,actual_lift_defect=inner['policy']['value']-lower,
        status='COMPLETE' if gap<=eps else 'UNRESOLVED',epsilon_guarantee=eps if gap<=eps else None,
        original_branches=len(data.caps),groups_count=len(groups),seconds=time.perf_counter()-start,
        lift_seconds=time.perf_counter()-lt)


def accuracy_partition(data,catalog,epsilon):
    eps=rat(epsilon);L=max(data.r,max(data.gamma))
    return sqrt_partition(data,catalog,eps/(2*L),eps/2)
