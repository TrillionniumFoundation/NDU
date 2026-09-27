#!/usr/bin/env python3
"""Independent exact single-query feasibility/normal-cone/flow audit.

No imports from a compiler or optimizer. Does not assert whole-curve identities.
The latter are checked separately by the preserved R29 independent verifier.
"""
from fractions import Fraction as F

def check_policy(bundle):
    raw,cert=bundle['instance'],bundle['certificate'];ns=raw['nodes'];beta=F(raw['beta'])
    lookup={};expected={};pervertex={};checks=0
    for s in cert['states']:
        key=s['node'],F(s['incoming']);assert key not in lookup
        lookup[key]=s;pervertex.setdefault(key[0],[]).append(key)
    eta=F(cert['root_price']);expected[0,eta]=F(1);conditional={};rewardgroups={};paygroups={}
    for v in reversed(range(len(ns))):
        row=ns[v]
        for key in pervertex.get(v,[]):
            st=lookup[key];x=F(st['x']);s=F(st['price']);inc=key[1]
            r,q,a,lo,hi,B=[F(row[k]) for k in ('r','q','a','lo','hi','cap')]
            l,u,chi=[F(st[k]) for k in ('lower','upper','chi')]
            assert lo<=x<=hi and min(l,u,chi)>=0 and s==inc+chi
            assert r-q*x-a*s+l-u==0
            assert l*(x-lo)==0 and u*(hi-x)==0
            y=a*x+beta*sum(F(p)*conditional[j,s] for j,p in row['edges'])
            assert y<=B and chi*(B-y)==0 and y==F(st['payment'])
            conditional[key]=y;checks+=6
    assert conditional[0,eta]==F(raw['promise'])
    for v,row in enumerate(ns):
        for key in pervertex.get(v,[]):
            st=lookup[key];w=F(st['weight']);s=F(st['price']);x=F(st['x'])
            assert w==expected[key] and w>0
            rewardgroups[s]=rewardgroups.get(s,F(0))+w*(F(row['r'])*x-F(row['q'])*x*x/2)
            paygroups[s]=paygroups.get(s,F(0))+w*F(row['a'])*x
            for j,p in row['edges']:
                child=j,s;expected[child]=expected.get(child,F(0))+beta*w*F(p)
            checks+=1
    value=sum(rewardgroups.values(),F(0));payment=sum(paygroups.values(),F(0))
    assert value==F(cert['value']) and payment==F(raw['promise'])
    assert set(expected)==set(lookup)
    # Feasibility, multiplier propagation, stationarity and complementarity
    # imply exact primal-dual equality, without numerically minimizing anything.
    return dict(checked_relations=checks+3,exact_policy_feasible=True,exact_KKT=True,
                value=str(value),scope='single-query policy certificate; no whole-curve audit')
