"""Conventional subset-prefix branch-and-bound baseline with rational bounds.

Relax an unfinished prefix to the entire allowed remaining catalog, ignore
future opening charges and future cardinality, and optimize targets exactly.
This is a benchmark baseline, not the new two-sided path theorem.
"""
from fractions import Fraction as F
import heapq,time
from box_solver import fixed_allocate

def solve(data,catalog,charges,B,m,seconds_limit=8,max_nodes=5001):
    start=time.perf_counter();a=tuple(catalog);cmap=dict(zip(a,charges));zero={x:F(0) for x in a};best=None;heap=[];count=0;serial=0
    def add(prefix,last):
        nonlocal best,count,serial
        if prefix:
            if prefix[0]>min(B,min(data.caps)):return
            p=fixed_allocate(data,prefix,B,cmap)
            if best is None or p['value']>best['value']:best=p
        if len(prefix)==m or last==len(a)-1:return
        available=prefix+a[last+1:]
        if available[0]>min(B,min(data.caps)):return
        upper=fixed_allocate(data,available,B,zero)['gross']-sum(cmap[x] for x in prefix)
        heapq.heappush(heap,(-upper,serial,prefix,last));serial+=1;count+=1
    add((),-1);status='COMPLETE'
    while heap:
        if best is not None and -heap[0][0]<=best['value']:break
        if count>=max_nodes or time.perf_counter()-start>=seconds_limit:
            status='INTERRUPTED';break
        _,_,prefix,last=heapq.heappop(heap)
        for i in range(last+1,len(a)):add(prefix+(a[i],),i)
    if best is None:raise AssertionError('No incumbent')
    upper=max([best['value']]+[-x[0] for x in heap])
    return dict(status=status,lower=best['value'],upper=upper,gap=upper-best['value'],seconds=time.perf_counter()-start,nodes=count,policy=best,scope='rational combinatorial prefix relaxation; atomic expansions; exact iff gap zero')
