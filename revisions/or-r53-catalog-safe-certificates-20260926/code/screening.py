"""Exact, target-preserving screening of non-anchor catalog commands.

Every removed command is dominated in every possible neighboring context.
The base resource optimizer and all earlier scientific files are unchanged.
"""
from __future__ import annotations
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/or-r52-resource-path-20260925/code'))
from resource_path import Instance,solve,encode,fixed_allocate


def instance_record(data,catalog,charges,promise,budget,epsilon):
    return dict(model=encode(asdict(data)),catalog=encode(tuple(catalog)),
                charges=encode(tuple(charges)),promise=str(F(promise)),
                budget=int(budget),epsilon=str(F(epsilon)))


def digest(record):
    return hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def context_gain(data,u,z,v=None):
    """Uniform gross-payoff gain bound for adding z between selected u and v."""
    u,z=F(u),F(z);v=None if v is None else F(v)
    if not u<z or (v is not None and not z<v):
        raise ValueError('An ordered predecessor/candidate/successor is required')
    gain=F(0);slope=(data.reward(z)-data.reward(u))/(z-u)
    gap=F(0) if v is None else data.reward(z)-((v-z)*data.reward(u)+(z-u)*data.reward(v))/(v-u)
    for w,b,g,tau in zip(data.weights,data.caps,data.gamma,data.ceilings):
        if tau<z:continue
        mass=max(F(0),b-u)
        if v is not None and tau>=v:
            local=gap*min(F(1),mass/(z-u))
        else:
            local=slope*min(mass,z-u)+g*(mass*mass-max(F(0),b-z)**2)/2
        if local<0:raise ArithmeticError('Nonnegative interpolation gain expected')
        gain+=w*local
    return gain


def bound_for(data,catalog,z):
    a=tuple(map(F,catalog));z=F(z)
    if z not in a:raise ValueError('Candidate not in current catalog')
    if not a[0]<z:raise ValueError('A non-anchor candidate must have predecessors')
    return context_gain(data,a[0],z,None),(a[0],None)


def screen(data,catalog,charges,B):
    start=time.perf_counter();a=list(map(F,catalog));rho=list(map(F,charges));B=F(B)
    if not a or len(a)!=len(rho) or a!=sorted(set(a)) or any(x<0 for x in rho):
        raise ValueError('Ordered catalog and nonnegative matching charges required')
    anchor_limit=min(B,min(data.caps));records=[];deleted=set()
    # Bounds use the retained minimum, so they do not depend on deletion order.
    for z,cost in reversed(tuple(zip(a,rho))):
        if z<=anchor_limit:continue
        bound=context_gain(data,a[0],z,None)
        if cost>=bound:
            records.append(dict(candidate=str(z),gain_bound=str(bound),charge=str(cost),
                                predecessor=str(a[0]),successor=None,strict=cost>bound))
            deleted.add(z)
    return dict(catalog=tuple(x for x in a if x not in deleted),
                charges=tuple(c for x,c in zip(a,rho) if x not in deleted),
                deletions=records,seconds=time.perf_counter()-start)


def solve_screened(data,catalog,charges,B,budget,epsilon=F(1,10)):
    original=instance_record(data,catalog,charges,B,budget,epsilon)
    reduced=screen(data,catalog,charges,B)
    ans=solve(data,reduced['catalog'],reduced['charges'],B,budget,epsilon)
    envelope=dict(schema='NDU-catalog-screen-v1',original=original,
                  instance_sha256=digest(original),deletions=reduced['deletions'],
                  resource_certificate=ans['certificate'])
    return dict(answer=ans,screening=reduced,envelope=envelope)
