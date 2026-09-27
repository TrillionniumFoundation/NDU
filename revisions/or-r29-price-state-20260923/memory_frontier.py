#!/usr/bin/env python3
"""Exact operational value of a finite terminal memory alphabet.

The contract primitives force every branch budget to bind. For a memory cell,
the optimal common terminal tier is its smallest branch cap. Sorted contiguous
cells are optimal; the dynamic program is standard ordered segmentation.
"""
from fractions import Fraction as F
from pathlib import Path
import json, itertools
from price_solver import solve
from verify import check
R=Path(__file__).resolve().parent


def family(k):
    b=[F(i,k+1) for i in range(1,k+1)]
    nodes=[dict(label='root',r='0',q='1',a='1',lo='0',hi='0',cap='1',
                edges=[[j+1,str(F(1,k))] for j in range(k)])]
    for j,c in enumerate(b):
        nodes.append(dict(label=f'branch-{j+1}',r='0',q='1',a='1',lo='0',hi='1',cap=str(c),edges=[[k+1,'1']]))
    nodes.append(dict(label='merged-terminal',r='2',q='1',a='1',lo='0',hi='1',cap='1',edges=[]))
    return dict(name=f'memory-family-{k}',beta='1',promise=str(sum(b)/k),nodes=nodes),b


def loss(b,groups):
    k=len(b)
    return sum((2-min(b[i] for i in g))*sum(b[i]-min(b[j] for j in g) for i in g) for g in groups)/k


def partitions(n):
    if n==0:
        yield [];return
    for p in partitions(n-1):
        yield p+[[n-1]]
        for i in range(len(p)):
            yield p[:i]+[p[i]+[n-1]]+p[i+1:]


def frontier(b):
    k=len(b); dp={(0,0):F(0)}; parent={}
    prefix=[F(0)]
    for x in b:prefix.append(prefix[-1]+x)
    for m in range(1,k+1):
        for j in range(m,k+1):
            choices=[]
            for i in range(m-1,j):
                if (m-1,i) not in dp:continue
                c=(2-b[i])*(prefix[j]-prefix[i]-(j-i)*b[i])/k
                choices.append((dp[m-1,i]+c,i))
            dp[m,j],parent[m,j]=min(choices)
    rows=[]; full=sum(2*x-x*x/2 for x in b)/k
    for m in range(1,k+1):
        groups=[]; mm,j=m,k
        while mm:
            i=parent[mm,j];groups.append(list(range(i,j)));j=i;mm-=1
        groups.reverse();gap=loss(b,groups);assert gap==dp[m,k]
        rows.append(dict(symbols=m,bits=(m-1).bit_length(),loss=str(gap),value=str(full-gap),groups=groups))
    return rows


def run():
    rows=[]; exhaustive=[]
    for k in [2,3,4,5,6,8,16,32]:
        data,b=family(k);cert=solve(data);check({'instance':data,'certificate':cert})
        f=frontier(b);assert F(f[-1]['value'])==F(cert['value'])
        assert len({s['x'] for s in cert['states'] if s['node']==k+1})==k
        if k<=6:
            best={}
            for p in partitions(k):
                v=loss(b,p);m=len(p);best[m]=min(best.get(m,v),v)
            assert all(F(row['loss'])==best[row['symbols']] for row in f)
            exhaustive.append(k)
        rows.append(dict(k=k,caps=list(map(str,b)),full_value=cert['value'],frontier=f,
                         instance=data,certificate=cert))
    result={'status':'PASS','exhaustive_all_partitions_k':exhaustive,'families':rows,
            'interpretation':'Exact deterministic memory-value frontier for this contract family; no calibrated storage costs.'}
    (R/'results/memory.json').write_text(json.dumps(result,indent=2)+'\n')
    print('All partitions checked for k=2,...,6; exact frontier through k=32.')
    print(json.dumps(rows[-3]['frontier'],indent=2))

if __name__=='__main__':run()
