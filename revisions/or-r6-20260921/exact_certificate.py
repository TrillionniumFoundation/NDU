#!/usr/bin/env python3
"""Independent Fraction verification of the R6 same-service, same-customer gain.
A two-policy mixture gives an EXACT feasible lower bound. A Lagrange Bellman
recursion over ALL stock/contract actions gives an EXACT upper bound. Solver
multipliers propose coefficients but their validity is checked without a solver.
"""
from fractions import Fraction as F
from collections import defaultdict
from pathlib import Path
import json
H=Path(__file__).resolve().parent;O=H/'results'
B=F(97,100);P=[[F(v,20) for v in row] for row in [(14,5,1),(3,14,3),(1,5,14)]]
T=8;DW=(1,3,4,2);LAM=F(3,5);KAP=F(6,5);MAINT=F(3,2)

def components(z,i,j,s2):
    th=F(j,10);q=F(i,10);S=F(s2,2)
    lo=sum(F(w,10)*max(F(z+d)-S,0) for d,w in enumerate(DW))
    ov=sum(F(w,10)*max(S-z-d,0) for d,w in enumerate(DW))
    fill=F(z)+F(17,10)-lo;C=F(3,10)*S+F(3,5)*ov+F(13,20)*lo
    prem=(F(3,5)+F(7,5)*z)*th;lia=KAP*th*lo;mov=LAM*(th-q)**2
    return dict(reward=prem-C-lia-MAINT*th*th-mov,customer=2*fill+lia-prem,filled=fill,physical=C)

def eval_policy(pol):
    state={(1,5):F(1)};ans={k:F(0) for k in ('reward','customer','filled','physical')}
    for t in range(T):
      nxt=defaultdict(F)
      for (z,i),mass in state.items():
        j=pol[t,z,i];a=components(z,i,j,2*(z+2))
        for k in ans:ans[k]+=B**t*mass*a[k]
        for zp in range(3):nxt[zp,j]+=mass*P[z][zp]
      state=nxt
    return ans

def static_ledger(theta):
    ans={k:F(0) for k in ('reward','customer','filled','physical')};dist=[F(0),F(1),F(0)]
    for t in range(T):
      for z in range(3):
        choices=[]
        for s2 in range(13):
          S=F(s2,2);lo=sum(F(w,10)*max(F(z+d)-S,0) for d,w in enumerate(DW));ov=sum(F(w,10)*max(S-z-d,0) for d,w in enumerate(DW))
          C=F(3,10)*S+F(3,5)*ov+F(13,20)*lo;fill=F(z)+F(17,10)-lo
          prem=(F(3,5)+F(7,5)*z)*theta;lia=KAP*theta*lo
          reward=prem-C-lia-MAINT*theta*theta-(LAM*(theta-F(1,2))**2 if t==0 else 0)
          choices.append((reward,s2,dict(reward=reward,customer=2*fill+lia-prem,filled=fill,physical=C)))
        a=max(choices,key=lambda a:(a[0],a[1]))[2]
        for k in ans:ans[k]+=B**t*dist[z]*a[k]
      dist=[sum(dist[z]*P[z][zp] for z in range(3)) for zp in range(3)]
    return ans

def lagrange_bound(mu,eta,reference):
    assert mu>=0 and eta>=0
    base={}
    for z in range(3):
      for j in range(11):
        vals=[]
        for s2 in range(13):
          a=components(z,0,j,s2)
          vals.append(a['reward']+LAM*F(j,10)**2+mu*a['filled']+eta*a['customer'])
        base[z,j]=max(vals)
    V=[[F(0)]*11 for _ in range(3)]
    for t in reversed(range(T)):
      W=[[F(0)]*11 for _ in range(3)]
      cont=[[B*sum(P[z][zp]*V[zp][j] for zp in range(3)) for j in range(11)] for z in range(3)]
      for z in range(3):
       for i in range(11):
        W[z][i]=max(base[z,j]-LAM*F(j-i,10)**2+cont[z][j] for j in range(11))
      V=W
    return V[1][5]-mu*reference['filled']-eta*reference['customer']

def main():
    data=json.loads((O/'service_policies.json').read_text())['same_service_customer_cost'];by=defaultdict(list)
    for r in data:
        assert r['stock_index']==2*(r['z']+2)
        by[r['t'],r['z'],r['inherited']].append(r['contract'])
    multi=[k for k,v in by.items() if len(v)>1]
    assert len(multi)==1
    polA={(t,z,i):6 for t in range(T) for z in range(3) for i in range(11)}
    for k,v in by.items():polA[k]=min(v)
    polB=polA.copy();polB[multi[0]]=max(by[multi[0]])
    A=eval_policy(polA);BB=eval_policy(polB)
    sx=json.loads((O/'static_exact.json').read_text());ref=static_ledger(F(sx['theta_fraction']))
    assert ref['reward']==F(sx['value_fraction'])
    weight=(ref['customer']-A['customer'])/(BB['customer']-A['customer'])
    assert 0<=weight<=1
    mix={k:(1-weight)*A[k]+weight*BB[k] for k in A}
    for k in ('customer','filled','physical'):assert mix[k]==ref[k]
    gain=mix['reward']-ref['reward'];assert gain>0
    prices=json.loads((O/'lp_certificates.json').read_text())['same_service_customer']['multipliers']
    mu=F(prices[0]).limit_denominator(10**9)
    eta=F(prices[1]).limit_denominator(10**9)
    upper=lagrange_bound(mu,eta,ref)
    assert upper>=mix['reward'];assert upper-mix['reward']<F(1,10**8)
    obj=dict(method='exact rational feasible mixture and Lagrange Bellman upper bound',
        randomization_state=list(multi[0]),low_contract=polA[multi[0]]/10,high_contract=polB[multi[0]]/10,
        probability_high_fraction=str(weight),probability_high=float(weight),
        static={k:str(v) for k,v in ref.items()},mixture={k:str(v) for k,v in mix.items()},
        gain_fraction=str(gain),gain=float(gain),lower_bound_fraction=str(mix['reward']),upper_bound_fraction=str(upper),
        upper_bound=float(upper),lower_bound=float(mix['reward']),duality_gap_fraction=str(upper-mix['reward']),duality_gap=float(upper-mix['reward']),
        mu_fraction=str(mu),eta_fraction=str(eta),equal_service=True,equal_customer=True,equal_physical=True,
        policy_low=[dict(t=t,z=z,q_index=i,theta_index=j,stock_index=2*(z+2)) for (t,z,i),j in sorted(polA.items())])
    (O/'exact_service_certificate.json').write_text(json.dumps(obj,indent=2)+'\n')
    print({k:v for k,v in obj.items() if k not in ('policy_low','static','mixture')})
if __name__=='__main__':main()
