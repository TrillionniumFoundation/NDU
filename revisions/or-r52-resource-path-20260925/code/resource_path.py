"""Selected-boundary resource paths; exact rational grids, no eligibility bins.

Fractions are used to generate payoffs. A single exact common denominator
converts the grid Bellman calculation to integer arithmetic; no rounding of
payoffs, solver tolerances or floating-point upper bounds are used.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from dataclasses import asdict
from math import lcm
import sys, time
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'revisions/or-r49-dispersion-certificates-20260925/code'))
from pooling import Instance, capped_cost, fixed_allocate, encode


def arc(data, u, v=None):
    """A selected edge owns terminal increments and histories exiting at u."""
    ids = tuple(j for j,t in enumerate(data.ceilings) if t>=u and (v is None or t<v))
    T = F(0) if v is None else sum((w*max(F(0),min(b,v)-u)
             for w,b,t in zip(data.weights,data.caps,data.ceilings) if t>=v), F(0))
    caps = tuple(max(F(0), data.caps[j]-u) for j in ids)
    Q = sum((data.weights[j]*c for j,c in zip(ids,caps)),F(0))
    return dict(ids=ids, caps=caps, terminal=T, service=Q, capacity=T+Q,
                slope=F(0) if v is None else (data.reward(v)-data.reward(u))/(v-u))


def arc_value(data, edge, x):
    if not 0<=x<=edge['capacity']: raise ValueError('Arc resource out of range')
    y=max(F(0),x-edge['terminal']);ids=edge['ids']
    z=capped_cost(tuple(data.weights[j] for j in ids),tuple(data.gamma[j] for j in ids),edge['caps'],y)
    return edge['slope']*min(x,edge['terminal'])-z['cost']


def book_resource_value(data, book, B, charges):
    """Independent-of-target-sweep resource allocation for a supplied book."""
    edges=[arc(data,u,v) for u,v in zip(book,book[1:])]+[arc(data,book[-1])]
    assert sum(e['capacity'] for e in edges)==data.cap_total-book[0]
    mass=B-book[0]; value=data.reward(book[0])-sum(charges[x] for x in book)
    for e in edges:
        take=min(mass,e['terminal']);value+=e['slope']*take;mass-=take
    if mass:
        ids=tuple(j for e in edges for j in e['ids'])
        caps=tuple(c for e in edges for c in e['caps'])
        assert sorted(ids)==list(range(len(data.caps)))
        value-=capped_cost(tuple(data.weights[j] for j in ids),tuple(data.gamma[j] for j in ids),caps,mass)['cost']
    return value


def max_convolution(values, kernel, limit):
    """Concave-kernel max-plus convolution by monotone divide and conquer.

    Both vectors are finite on a contiguous prefix. The previous value vector
    need NOT be concave. Ties select the smallest previous resource index.
    """
    R,C=len(values)-1,len(kernel)-1
    last=min(limit,R+C)
    out=[None]*(last+1);arg=[None]*(last+1)
    stack=[(0,last,0,R)]
    while stack:
        lo,hi,optlo,opthi=stack.pop()
        if lo>hi: continue
        s=(lo+hi)//2
        left=max(optlo,0,s-C);right=min(opthi,R,s)
        if left>right: raise AssertionError('Empty convolution interval')
        best=left;bv=values[left]+kernel[s-left]
        for t in range(left+1,right+1):
            z=values[t]+kernel[s-t]
            if z>bv:best,bv=t,z
        out[s]=bv;arg[s]=best
        stack.append((s+1,hi,best,opthi));stack.append((lo,s-1,optlo,best))
    return out,arg


def brute_convolution(values,kernel,limit):
    result=[]
    for s in range(min(limit,len(values)+len(kernel)-2)+1):
        result.append(max(values[t]+kernel[s-t] for t in range(max(0,s-len(kernel)+1),min(s,len(values)-1)+1)))
    return result


def solve(data, catalog, charges, B, budget, epsilon=F(1,100), step=None, certificate=True):
    start=time.perf_counter()
    a=tuple(map(F,catalog));rho=tuple(map(F,charges));B=F(B);eps=F(epsilon)
    if not a or len(a)!=len(rho) or a[0]<0 or a[-1]>1 or any(x>=y for x,y in zip(a,a[1:])) or any(z<0 for z in rho):
        raise ValueError('Ordered catalog and nonnegative charges required')
    if not isinstance(budget,int) or isinstance(budget,bool) or budget<1 or eps<=0:
        raise ValueError('Positive integer budget and positive accuracy required')
    if not 0<=B<=data.cap_total:raise ValueError('Infeasible aggregate promise')
    m=min(budget,len(a));L=max(data.r,max(data.gamma,default=F(0)))
    eta=eps/(2*L*m) if step is None else F(step)
    if eta<=0:raise ValueError('Positive grid step required')
    if 2*L*m*eta>eps:raise ValueError('Grid step exceeds the requested error guarantee')
    anchors=[i for i,u in enumerate(a) if u<=min(B,min(data.caps))]
    if not anchors:raise ValueError('No feasible anchor')
    Qmax=max(int((B-a[i])//eta) for i in anchors)
    edges={};fractions={};den=1
    for i,u in enumerate(a):
        for v in list(range(i+1,len(a)))+[len(a)]:
            e=arc(data,u,None if v==len(a) else a[v]);edges[i,v]=e
            row=[arc_value(data,e,q*eta) for q in range(min(Qmax,int(e['capacity']//eta))+1)]
            assert all(row[q+1]-row[q]>=row[q+2]-row[q+1] for q in range(len(row)-2))
            fractions[i,v]=row
            for z in row:den=lcm(den,z.denominator)
    for z in rho+tuple(data.reward(a[i]) for i in anchors):den=lcm(den,z.denominator)
    kernels={key:[int(x*den) for x in row] for key,row in fractions.items()}
    assert all(F(x,den)==z for key,row in kernels.items() for x,z in zip(row,fractions[key]))
    cscaled=[int(x*den) for x in rho]
    best=None;bestpath=None;all_tables={};statecount=0
    for anchor in anchors:
        qmax=int((B-a[anchor])//eta)
        # At most m arcs, including the terminal edge, are rounded down.
        qmin=max(0,-int(-(B-a[anchor]-m*eta)//eta))
        tables={};pointers={}
        tables[1,anchor]=[int(data.reward(a[anchor])*den)-cscaled[anchor]]
        for ell in range(2,m+1):
            for v in range(anchor+ell-1,len(a)):
                ans=[];ptr=[]
                for u in range(anchor,v):
                    prev=tables.get((ell-1,u))
                    if prev is None:continue
                    conv,arg=max_convolution(prev,kernels[u,v],qmax)
                    while len(ans)<len(conv):ans.append(None);ptr.append(None)
                    for s,z in enumerate(conv):
                        z-=cscaled[v]
                        if ans[s] is None or z>ans[s]:ans[s]=z;ptr[s]=(u,arg[s])
                if ans:tables[ell,v]=ans;pointers[ell,v]=ptr
        for (ell,u),values in tables.items():
            conv,arg=max_convolution(values,kernels[u,len(a)],qmax)
            for s in range(qmin,len(conv)):
                score=conv[s]
                if best is None or score>best:
                    best=score;path=[u];v=u;t=arg[s];e=ell
                    while e>1:
                        v,t=pointers[e,v][t];path.append(v);e-=1
                    bestpath=tuple(reversed(path))
        statecount+=sum(map(len,tables.values()))
        if certificate:all_tables[str(anchor)]={f'{ell},{v}':row for (ell,v),row in tables.items()}
    if best is None:raise AssertionError('Rounding band contains no path')
    policy=fixed_allocate(data,tuple(a[i] for i in bestpath),B,dict(zip(a,rho)))
    score=F(best,den);lower=policy['value'];upper=score+L*m*eta
    assert lower<=upper and upper-lower<=2*L*m*eta,(lower,upper,eta)
    cert=dict(schema='NDU-resource-path-v1',model=encode(asdict(data)),catalog=encode(a),charges=encode(rho),
              promise=str(B),budget=m,epsilon=str(eps),step=str(eta),lipschitz=str(L),
              denominator=str(den),tables={h:{key:[str(x) for x in row] for key,row in tab.items()} for h,tab in all_tables.items()},
              grid_score=str(score),lower=str(lower),upper=str(upper),policy=encode(policy)) if certificate else None
    return dict(lower=lower,upper=upper,gap=upper-lower,book=policy['book'],grid_score=score,
                step=eta,resource_states=statecount,grid_size=Qmax+1,denominator_bits=den.bit_length(),
                seconds=time.perf_counter()-start,certificate=cert)
