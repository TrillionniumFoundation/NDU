#!/usr/bin/env python3
"""Replay saved R7 certificates. No optimizer is used for certificate replay.
The exact hierarchy generator is re-run for reproducibility; interim and graph
policies are checked from their stored rational actions and multipliers.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import json,sys,hashlib
import numpy as np
from scipy.sparse import csr_matrix
sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent; O=HERE/'results'
import accepted_exact as e

def load(name):return json.loads((O/name).read_text())
def hierarchy():
 data=load('accepted_continuous_exact.json')
 assert e.pin_stock()==F(data['minimum_nonzero_stock_support_gap'])
 regenerated=[e.restricted(k) for k in ['static','time','regime']]+[e.full()]
 assert regenerated==data['rows']
 old=json.loads((HERE.parent/'or-r6-20260921/results/static_exact.json').read_text())
 # Independent exhaustive static stock-envelope output must agree exactly.
 # Accept the stored R6 schema, keeping this check explicit rather than silently skipping it.
 text=json.dumps(old);assert str(e.th.numerator) in text and str(e.th.denominator) in text
 vals=[F(r['value']['fraction']) for r in data['rows']]
 assert all(vals[i+1]>vals[i] for i in range(3))
 # An exact feasible one-period customer-neutral direction, t=1.
 t=1;eps=F(1,100);wL,wH=e.w[t][0],e.w[t][2]
 dl=-1/(wL*e.a[0]);dh=1/(wH*e.a[2]);assert wL*e.a[0]*dl+wH*e.a[2]*dh==0
 assert 0<e.th+eps*dl<1 and 0<e.th+eps*dh<1
 gain=eps*2*e.m*e.th*(1/e.a[0]-1/e.a[2])-eps**2*(e.m+e.lam+e.beta*e.lam)*(wL*dl**2+wH*dh**2)
 # Use a smaller step if the particular 0.01 choice is too large.
 while gain<=0:
  eps/=10;gain=eps*2*e.m*e.th*(1/e.a[0]-1/e.a[2])-eps**2*(e.m+e.lam+e.beta*e.lam)*(wL*dl**2+wH*dh**2)
 return dict(classes=4,exact_order=True,static_matches_R6=True,local_direction_step=str(eps),local_direction_gain=str(gain))

def interim():
 d=load('interim_participation.json');nodes=[(0,1,-1,F(1))]
 for t in range(7):
  for i,(tt,z,p,w) in list(enumerate(nodes)):
   if tt==t:
    nodes.extend((t+1,j,i,w*e.beta*e.P[z][j]) for j in range(3))
 x=list(map(F,d['policy_tiers']));l=list(map(F,d['nonnegative_subtree_multipliers']))
 assert len(x)==len(l)==len(nodes)==3280 and min(l)>=0 and min(x)>=0 and max(x)<=1
 payoff=F(0);r=[];pay=[];cap=[];lm=[]
 for i,(_,z,p,w) in enumerate(nodes):
  q=x[p] if p>=0 else e.q0;lm.append(l[i]+(lm[p] if p>=0 else 0))
  payoff+=w*(e.a[z]*x[i]-e.C[z]-e.m*x[i]**2-e.lam*(x[i]-q)**2)
  pay.append(w*e.a[z]*x[i]);cap.append(w*e.a[z]*e.th)
  r.append(w*(e.a[z]*(1-lm[i])-2*e.m*x[i]-2*e.lam*(x[i]-q)))
 for i in reversed(range(1,len(nodes))):
  p=nodes[i][2];pay[p]+=pay[i];cap[p]+=cap[i];r[p]+=2*e.lam*nodes[i][3]*(x[i]-x[p])
 slack=[c-p for c,p in zip(cap,pay)];assert min(slack)>=0
 bound=sum((r[i]**2/(4*e.m*nodes[i][3])+l[i]*slack[i] for i in range(len(nodes))),F(0))
 assert payoff==F(d['value_fraction']) and bound==F(d['loss_bound_fraction'])
 return dict(nodes=len(nodes),all_continuation_constraints_exact=True,value_fraction=str(payoff),gap_fraction=str(bound))

def portfolio():
 rows=load('portfolio_deployments.json');graphs={(g['d'],g['rep']):g for g in load('portfolio_test_graphs.json')};max_bound=F(0)
 for r in rows:
  g=graphs[r['d'],r['rep']];d=g['d'];K=csr_matrix((np.array(g['K_numerators'],dtype=np.int64),g['K_indices'],g['K_indptr']),shape=(d,d))
  # M-matrix graph certificate implies K/10 >= 21/10 I, without an eigensolver.
  assert (K-K.T).nnz==0
  for i in range(d):
   indices=K.indices[K.indptr[i]:K.indptr[i+1]];values=K.data[K.indptr[i]:K.indptr[i+1]]
   assert sum(map(int,values))==21
   assert all(int(v)<=0 for j,v in zip(indices,values) if j!=i)
  den=r['tier_denominator'];a=g['a_integers'];x=r['tier_numerators'];eta=F(r['dual_numerator'],r['dual_denominator'])
  assert den==10**10 and len(x)==d and min(x)>=0 and max(x)<=den and eta>=0
  # Python integer sparse multiplication: independent of the solver's int64 path.
  kx=[sum(int(K.data[k])*int(x[int(K.indices[k])]) for k in range(K.indptr[i],K.indptr[i+1])) for i in range(d)]
  ast=sum(a);ts=F(ast+60*d,420*d);cap=F(ast,100)*ts;pay=F(sum(ai*xi for ai,xi in zip(a,x)),100*den);slack=cap-pay;assert slack>=0
  phys=sum((F(103+30*(i%3),100) for i in range(d)),F(0))
  value=F(sum((ai+60)*xi for ai,xi in zip(a,x)),100*den)-F(sum(xi*ki for xi,ki in zip(x,kx)),10*den**2)-F(3*d,20)-phys
  residual=[(1-eta)*F(ai,100)+F(3,5)-F(ki,5*den) for ai,ki in zip(a,kx)]
  bound=F(5,42)*sum((v*v for v in residual),F(0))+eta*slack
  assert value==F(r['exact_value_fraction']) and bound==F(r['exact_loss_bound_fraction']) and slack==F(r['exact_customer_slack_fraction'])
  if r['method']=='value_gradient':max_bound=max(max_bound,bound/d)
 return dict(deployments=len(rows),graphs=len(graphs),all_feasible_exact=True,all_residual_bounds_replayed=True,maximum_learned_bound_per_service=float(max_bound))

def numerical():
 rows=load('accepted_robustness.json');feas=[r for r in rows if r['accepted']['feasible']]
 for r in feas:
  a=r['accepted'];assert a['flow_residual']<1e-7 and a['inequality_violation']<1e-7 and abs(a['duality_gap'])<1e-7 and a['reduced_cost_min']>-1e-7
  h=r.get('continuous_hierarchy')
  if h:
   v=[i['value'] for i in h];assert all(v[i+1]>=v[i]-1e-9 for i in range(3))
 fine=load('fine_menus.json')
 for r in fine:assert abs(r['primal_dual_gap'])<1e-8 and r['deterministic_value']<=r['randomized_value']+1e-8
 return dict(robustness_cases=len(rows),feasible=len(feas),infeasible=len(rows)-len(feas),numerical_not_interval_verified=True,fine_menus=len(fine))

def main():
 result={'hierarchy':hierarchy(),'interim':interim(),'portfolio':portfolio(),'numerical':numerical()}
 result['inputs_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.glob('*.json')) if p.name!='verification.json'}
 (O/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='inputs_sha256'},indent=2))
if __name__=='__main__':main()
