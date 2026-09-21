#!/usr/bin/env python3
"""Continuous accepted protocol with customer exit at every review node.
Numerical sparse convex-QP dual solution proposes a deterministic tree policy.
A separate rational residual upper bound certifies the rounded feasible policy.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import sys,json,time
import numpy as np
from scipy.sparse import coo_matrix,csr_matrix
from scipy.sparse.linalg import splu
from scipy.optimize import minimize
sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent;OUT=HERE/'results'
sys.path.insert(0,str(HERE));import accepted_exact as ex
Q=10**9

def tree():
 nodes=[(0,1,-1,F(1))]
 for t in range(7):
  for i,(tt,z,parent,w) in list(enumerate(nodes)):
   if tt==t:
    for zp in range(3):nodes.append((t+1,zp,i,w*ex.beta*ex.P[z][zp]))
 return nodes

def main():
 nodes=tree();n=len(nodes);times=np.array([x[0] for x in nodes]);z=np.array([x[1] for x in nodes]);pa=np.array([x[2] for x in nodes]);wf=[x[3] for x in nodes];w=np.array([float(v) for v in wf]);sw=np.sqrt(w);a=np.array([float(ex.a[j]) for j in z]);theta=float(ex.th)
 rr=[];cc=[];vv=[];diag=np.full(n,float(ex.m+ex.lam));b=sw*a;b[0]+=2*float(ex.lam*ex.q0)
 for i in range(1,n):
  j=pa[i];ratio=w[i]/w[j];diag[j]+=float(ex.lam)*ratio;rr.extend([i,j]);cc.extend([j,i]);vv.extend([-float(ex.lam)*np.sqrt(ratio)]*2)
 rr.extend(range(n));cc.extend(range(n));vv.extend(diag)
 H=coo_matrix((vv,(rr,cc)),shape=(n,n)).tocsc();factor=splu(H)
 rr=[];cc=[];vv=[];hf=[];subA=np.zeros(n)
 for j in reversed(range(n)):
  subA[j]+=w[j]*a[j]
  if pa[j]>=0:subA[pa[j]]+=subA[j]
 for j in range(n):
  i=j
  while i>=0:rr.append(i);cc.append(j);vv.append(a[j]*sw[j]/sw[i]);i=pa[i]
 C=coo_matrix((vv,(rr,cc)),shape=(n,n)).tocsr();h=theta*subA/sw
 def fun(l):
  rhs=b-C.T@l;y=factor.solve(rhs)/2
  return float(rhs@y/2+l@h), h-C@y
 start=time.perf_counter();res=minimize(fun,np.zeros(n),jac=True,bounds=[(0,None)]*n,method='L-BFGS-B',options={'maxiter':20000,'ftol':1e-15,'gtol':1e-11,'maxcor':30,'maxls':50})
 ell=np.maximum(0,res.x);y=factor.solve(b-C.T@ell)/2;th=np.clip(y/sw,0,1)
 # Rational candidate; uniform contraction enforces every continuation budget.
 xI=np.floor(th*Q).astype(np.int64);xf=[F(int(k),Q) for k in xI]
 subpay=[wf[i]*ex.a[z[i]]*xf[i] for i in range(n)];subcap=[wf[i]*ex.a[z[i]]*ex.th for i in range(n)]
 for i in reversed(range(1,n)):subpay[pa[i]]+=subpay[i];subcap[pa[i]]+=subcap[i]
 scale=min([F(1)]+[subcap[i]/subpay[i] for i in range(n) if subpay[i]>0]);xf=[F((v*scale*Q).numerator//(v*scale*Q).denominator,Q) for v in xf]
 # Multiplier conversion for unnormalized, unconditional subtree constraints.
 lf=[F(max(0,int(round(float(ell[i]/sw[i])*Q))),Q) for i in range(n)]
 ancestors=[]
 for i in range(n):ancestors.append(lf[i]+(ancestors[pa[i]] if pa[i]>=0 else 0))
 physical=sum(wf[i]*ex.C[z[i]] for i in range(n));value=F(0);subpay=[F(0)]*n;subcap=[F(0)]*n;r=[]
 for i in range(n):
  parent=xf[pa[i]] if pa[i]>=0 else ex.q0;v=xf[i];wt=wf[i];aa=ex.a[z[i]]
  value+=wt*(aa*v-ex.C[z[i]]-ex.m*v*v-ex.lam*(v-parent)**2)
  subpay[i]=wt*aa*v;subcap[i]=wt*aa*ex.th
  r.append(wt*(aa*(1-ancestors[i])-2*ex.m*v-2*ex.lam*(v-parent)))
 for i in reversed(range(1,n)):
  subpay[pa[i]]+=subpay[i];subcap[pa[i]]+=subcap[i];r[pa[i]]+=2*ex.lam*wf[i]*(xf[i]-xf[pa[i]])
 slack=[subcap[i]-subpay[i] for i in range(n)];assert min(slack)>=0 and all(0<=v<=1 for v in xf)
 residual_bound=sum((r[i]*r[i]/(4*ex.m*wf[i]) for i in range(n)),F(0));dual_slack=sum((lf[i]*slack[i] for i in range(n)),F(0));bound=residual_bound+dual_slack
 stat=F(ex.restricted('static')['value']['fraction']);full=F(ex.full()['value']['fraction'])
 out={'scope':'continuous tiers and stock fixed only by exact fill/cost supporting-line lemma; customer continuation participation at every one of 3280 observable regime-history nodes', 'nodes':n,'solver_success':bool(res.success),'solver_message':str(res.message),'iterations':int(res.nit),'seconds_including_exact_audit':time.perf_counter()-start,'minimum_tier':float(min(xf)),'maximum_tier':float(max(xf)),'contraction_factor':str(scale),'value':float(value),'value_fraction':str(value),'gain_over_static':float(value-stat),'gain_over_static_fraction':str(value-stat),'loss_bound':float(bound),'loss_bound_fraction':str(bound),'commitment_value_lost':float(full-value),'numerical_active_review_constraints':int(np.sum((h-C@y)/sw<1e-6)),'maximum_conditional_customer_deficit':0,'exact_residual_term':str(residual_bound),'exact_dual_slack_term':str(dual_slack),'policy_tiers':[str(v) for v in xf],'nonnegative_subtree_multipliers':[str(v) for v in lf],'tree_order':'breadth first, root z=1; children z=0,1,2; T=8', 'note':'The rational upper bound, not optimizer status, determines numerical certainty. Opposite party remains committed; no hidden effort is introduced.'}
 (OUT/'interim_participation.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if not isinstance(v,list)})
if __name__=='__main__':main()
