#!/usr/bin/env python3
"""Independent expanded-tree matrix audit and numerical comparison.

Only small test instances are expanded. The production solver never calls this.
The exact matrix KKT checks prove these test solutions; SLSQP is a separately
labelled floating-point cross-check initialized by a feasibility LP.
"""
from fractions import Fraction as F
from pathlib import Path
import json, time
import numpy as np
from scipy.optimize import minimize, linprog, LinearConstraint, Bounds
R=Path(__file__).resolve().parent


def audit(bundle):
    raw=bundle['instance'];c=bundle['certificate'];nodes=raw['nodes'];beta=F(raw['beta'])
    states={(s['node'],F(s['incoming'])):s for s in c['states']}
    tree=[]
    def expand(v,price,weight,anc):
        s=states[v,price];i=len(tree);tree.append((v,s,weight,anc+[i]))
        for j,p in nodes[v]['edges']:expand(j,F(s['price']),weight*beta*F(p),anc+[i])
    expand(0,F(c['root_price']),F(1),[])
    N=len(tree);A=[[F(0)]*N for _ in range(N)]
    q=[];r=[];b=[];x=[];mu=[];lo=[];hi=[];lm=[];um=[]
    for j,(v,s,w,anc) in enumerate(tree):
        n=nodes[v]
        q.append(w*F(n['q']));r.append(w*F(n['r']));x.append(F(s['x']))
        b.append(F(n['cap']));mu.append(w*F(s['chi']))
        lo.append(F(n['lo']));hi.append(F(n['hi']));lm.append(w*F(s['lower']));um.append(w*F(s['upper']))
        for i in anc:A[i][j]=w/tree[i][2]*F(n['a'])
    def dot(a,z):return sum(t*y for t,y in zip(a,z))
    eta=F(c['root_price']);promise=F(raw['promise'])
    assert dot(A[0],x)==promise
    for i in range(N):
        assert dot(A[i],x)<=b[i] and mu[i]>=0 and mu[i]*(b[i]-dot(A[i],x))==0
        assert lo[i]<=x[i]<=hi[i]
        assert r[i]-q[i]*x[i]==eta*A[0][i]+sum(A[j][i]*mu[j] for j in range(N))+um[i]-lm[i]
    val=dot(r,x)-sum(t*z*z/2 for t,z in zip(q,x));assert val==F(c['value'])
    af=np.array(A,float);bf=np.array(b,float);rf=np.array(r,float);qf=np.array(q,float)
    bounds=list(zip(map(float,lo),map(float,hi)))
    start=time.perf_counter()
    lp=linprog(np.linspace(-.3,.7,N),A_ub=af,b_ub=bf,A_eq=af[:1],b_eq=[float(promise)],bounds=bounds,method='highs')
    assert lp.success,lp.message
    result=minimize(lambda z:.5*np.dot(qf*z,z)-np.dot(rf,z),lp.x,
                    jac=lambda z:qf*z-rf,method='SLSQP',bounds=Bounds(np.array(lo,float),np.array(hi,float)),
                    constraints=[LinearConstraint(af[:1],[float(promise)],[float(promise)]),
                                 LinearConstraint(af[1:],-np.inf,bf[1:])],
                    options={'ftol':1e-12,'maxiter':3000})
    elapsed=time.perf_counter()-start
    gap=abs(-result.fun-float(val));viol=max(0,float(np.max(af@result.x-bf)),abs(float(af[0]@result.x)-float(promise)))
    assert result.success and gap<1e-7 and viol<1e-8,(raw['name'],result.message,gap,viol)
    return dict(name=raw['name'],tree_nodes=N,exact_matrix_kkt='PASS',exact_value=str(val),
                numerical_value=float(-result.fun),absolute_value_difference=gap,max_constraint_violation=viol,
                feasibility_lp_plus_slsqp_seconds=elapsed,iterations=result.nit)


def run():
    e=json.loads((R/'results/evidence.json').read_text());out=[]
    for b in e['instances']:
        raw=b['instance'];d=raw.get('design',{})
        if (d and d['T']<=5) or raw['name']=='strict_value_of_price_memory':
            rec=audit(b);out.append(rec);print(rec['name'],rec['tree_nodes'],rec['absolute_value_difference'],flush=True)
    (R/'results/tree_comparison.json').write_text(json.dumps({'exact_method':'expanded conditional-incidence matrix KKT',
        'floating_method':'SciPy HiGHS feasibility LP then SLSQP, ftol=1e-12','instances':out},indent=2)+'\n')

if __name__=='__main__':run()
