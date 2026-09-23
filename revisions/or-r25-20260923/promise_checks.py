"""Finite-action exact promise-state recursion vs exhaustive history policies.
This checks a finite-action institution; it does not discretize the continuous theorem.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import json,time
R=Path(__file__).resolve().parent

def case(H,actions,gamma):
    states=(-1,1)
    def cap(t,z):return F(3*(H-t)+z,4)
    def stage(t,z,q,x):return (F(3,4)+F(z,2))*x-x*x/2-gamma*(x-q)**2
    @lru_cache(None)
    def rec(t,z,q):
        if t==H:return {F(0):F(0)}
        ans={}
        for x in actions:
            left=rec(t+1,-1,x);right=rec(t+1,1,x)
            for bl,br in product(left,right):
                b=x+(bl+br)/2
                if t>0 and b>cap(t,z):continue
                value=stage(t,z,q,x)+(left[bl]+right[br])/2
                if b not in ans or value>ans[b]:ans[b]=value
        return ans
    computed=rec(0,0,F(1,2));N=2**H-1;best={};accepted=0
    depth=[(i+1).bit_length()-1 for i in range(N)];weights=[F(1,2**t) for t in depth]
    for x in product(actions,repeat=N):
        budgets=list(x)
        for i in range(N-1,-1,-1):
            if 2*i+1<N:budgets[i]+=(budgets[2*i+1]+budgets[2*i+2])/2
        if any(budgets[i]>cap(depth[i],-1 if i%2 else 1) for i in range(1,N)):continue
        val=sum((weights[i]*stage(depth[i],0 if i==0 else (-1 if i%2 else 1),F(1,2) if i==0 else x[(i-1)//2],x[i]) for i in range(N)),F(0))
        b=budgets[0];accepted+=1
        if b not in best or val>best[b]:best[b]=val
    assert computed==best
    return {'horizon':H,'nodes':N,'tiers':list(map(str,actions)),'gamma':str(gamma),'policies_enumerated':len(actions)**N,
    'accepted_policies':accepted,'root_promises':len(best),'recursive_subproblems':rec.cache_info().currsize,
    'values':{str(k):str(v) for k,v in sorted(best.items())}}
if __name__=='__main__':
    start=time.perf_counter();rows=[case(3,(F(0),F(1,2),F(1)),F(1,8)),case(3,(F(0),F(1,2),F(1)),F(3,8)),case(4,(F(0),F(1)),F(1,8))]
    out={'status':'PASS','cases':rows,'seconds':time.perf_counter()-start,'claim':'Exact finite-action recursion; not a polynomial-horizon claim for continuous promises.'}
    (R/'results/promise_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='cases'}))
