"""Reimplementation of the inherited R43 exact priced-prefix completion bound.

Uses the same root price budget and additive stopping tolerance as R46. This
baseline is separate from the simpler full-catalog relaxation baseline.
"""
from fractions import Fraction as F
import time,heapq
from box_solver import branch_support,fixed_allocate,root_prices,frontier,ideal_targets

def solve(data,a,rho,B,m,epsilon=F(1,1000),seconds_limit=8,max_nodes=5001):
    start=time.perf_counter();a=tuple(a);n=len(a);cmap=dict(zip(a,rho));lo=(F(0),)*len(data.caps)
    prices=root_prices(data,a,rho,B,m,lo,data.caps,8);tables=[]
    for lam in prices:
        g=[data.reward(x)-lam*x for x in a]
        def phi(j,x):
            cap=data.caps[j]-x;gam=data.gamma[j]
            y=F(0) if lam>=0 else cap if gam==0 else min(cap,-lam/gam)
            return -gam*y*y/2-lam*y
        edge={}
        for i,x in enumerate(a):
            for v in range(i+1,n):
                z=a[v];edge[i,v]=sum((w*(g[i]+(b-x)*(g[v]-g[i])/(z-x) if z<=tau else g[i]+phi(j,x)) for j,(w,b,tau) in enumerate(zip(data.weights,data.caps,data.ceilings)) if x<=b<z),F(0))
        tail=[sum((w*(g[i]+phi(j,x)) for j,(w,b) in enumerate(zip(data.weights,data.caps)) if b>=x),F(0)) for i,x in enumerate(a)]
        W=[None]+[tail[:]]
        for r in range(2,m+1):
            W.append([max([tail[i]]+[edge[i,v]-rho[v]+W[r-1][v] for v in range(i+1,n) if g[v]>=g[i]]) for i in range(n)])
        tables.append((lam,g,edge,W))
    def bound(ids):
        book=tuple(a[i] for i in ids);answers=[]
        for lam,g,E,W in tables:
            if not ids:
                val=max(W[m][i]-rho[i] for i,x in enumerate(a) if x<=min(B,min(data.caps)))
            elif all(g[i]<=g[j] for i,j in zip(ids,ids[1:])):
                val=sum(E[i,j] for i,j in zip(ids,ids[1:]))-sum(rho[i] for i in ids)+W[m-len(ids)+1][ids[-1]]
            else:
                val=sum(w*branch_support(data,j,book,F(0),data.caps[j],lam)[0] for j,w in enumerate(data.weights))-sum(rho[i] for i in ids)
            answers.append(lam*B+val)
        return min(answers)
    c=frontier(data,a,rho,ideal_targets(data,B),m)['at_most'][-1]
    best=fixed_allocate(data,c['book'],B,cmap);heap=[(-bound(()),0,())];serial=1;count=1;status='COMPLETE'
    while heap and -heap[0][0]>best['value']+epsilon:
        if count>=max_nodes or time.perf_counter()-start>=seconds_limit:status='INTERRUPTED';break
        neg,_,ids=heapq.heappop(heap);last=ids[-1] if ids else -1
        interrupted=False
        for i in range(last+1,n):
            child=ids+(i,);book=tuple(a[z] for z in child)
            if book[0]>min(B,min(data.caps)):continue
            p=fixed_allocate(data,book,B,cmap)
            if p['value']>best['value']:best=p
            if len(child)<m and i<n-1:
                heapq.heappush(heap,(-bound(child),serial,child));serial+=1;count+=1
            if time.perf_counter()-start>=seconds_limit or count>=max_nodes:
                # Retain the parent if not all children have been generated.
                # Overlap with generated children is safe for an upper cover.
                heapq.heappush(heap,(neg,serial,ids));serial+=1;status='INTERRUPTED';interrupted=True;break
        if interrupted:break
    upper=max([best['value']]+[-z[0] for z in heap])
    return dict(status=status,lower=best['value'],upper=upper,gap=upper-best['value'],seconds=time.perf_counter()-start,nodes=count,prices=prices,epsilon=epsilon,scope='inherited R43 priced-prefix bound reimplemented; rational interval')
