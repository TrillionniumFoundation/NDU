#!/usr/bin/env python3
"""Adversarial finite checks of structural statements, not substitutes for proofs."""
from fractions import Fraction as Q
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog

root=Path(__file__).resolve().parent
rng=np.random.default_rng(914210)
cases=[]
for depth in (2,3,4,5):
    N=2**depth-1;pa=[-1]+[(n-1)//2 for n in range(1,N)]
    # S maps node spending displacements y to descendant sums.
    S=np.eye(N)
    for n in range(N-1,0,-1):S[pa[n]]+=S[n]
    for index in range(30):
        k=rng.integers(-20,21,N).astype(float)/10
        if index%3==0:
            for n in range(1,N):k[n]=k[pa[n]]+abs(k[n])
        edge=any(k[n]<k[pa[n]]-1e-12 for n in range(1,N))
        res=linprog(-k,A_ub=S[1:],b_ub=np.zeros(N-1),A_eq=S[:1],b_eq=[0],bounds=[(-1,1)]*N,method='highs')
        assert res.success and ((-res.fun>1e-8)==edge)
        # Exact summation-by-parts identity on rational random displacements.
        y=[Q(int(v),10) for v in rng.integers(-10,11,N)]
        y[0]=-sum(y[1:],Q(0));sub=y.copy()
        for n in range(N-1,0,-1):sub[pa[n]]+=sub[n]
        kk=[Q(str(v)) for v in k]
        lhs=sum((a*b for a,b in zip(kk,y)),Q(0))
        rhs=sum(((kk[n]-kk[pa[n]])*sub[n] for n in range(1,N)),Q(0))
        assert lhs==rhs
        cases.append({'depth':depth,'index':index,'edge_improvable':edge,'lp_gain':float(-res.fun),'exact_identity':True})
# Two-review threshold: W(s)-W(0)=(Delta-lambda*K)s-q*s^2.
threshold=[]
for delta in (Q(-1,2),Q(0),Q(1,2),Q(3,2)):
    K=Q(7,3);q=Q(4,5);smax=Q(1,4);critical=max(Q(0),delta/K)
    for lam in (Q(0),critical,critical+Q(1,10)):
        slope=delta-lam*K;s=max(Q(0),min(smax,slope/(2*q)))
        gain=slope*s-q*s*s
        assert (gain>0)==(delta>lam*K)
        threshold.append({'delta':str(delta),'lambda':str(lam),'threshold':str(critical),'gain':str(gain)})
history=(Q(1,4)-Q(1,4)**2+Q(1,2)-Q(1,2)**2)/2
coarse=Q(1,4)-Q(1,4)**2
assert history-coarse==Q(1,32)
out={'status':'PASS','edge_cases':cases,'absolute_friction_cases':threshold,'zero_friction_promise_gap':str(history-coarse)}
(root/'results'/'structural_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS:',len(cases),'tree criteria;',len(threshold),'friction cases; exact promise gap',history-coarse)
