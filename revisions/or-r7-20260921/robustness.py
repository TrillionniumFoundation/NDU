#!/usr/bin/env python3
"""Accepted, not provider-relaxation, sensitivity and fine-menu experiments.
Default/perturbed static tiers are reoptimized for each primitive vector.
All-stock LPs use numerical primal/dual checks. Exact canonical proof is separate.
"""
from __future__ import annotations
from dataclasses import dataclass,replace,asdict
from pathlib import Path
import csv,json,time,sys
import numpy as np
from scipy.optimize import linprog, minimize_scalar
from scipy.sparse import coo_matrix
HERE=Path(__file__).resolve().parent;OUT=HERE/'results';OUT.mkdir(exist_ok=True)
@dataclass(frozen=True)
class Model:
 T:int=8;beta:float=.97;lam:float=.6;m:float=1.5;power:float=2.;kappa:float=1.2
 slope:float=1.4;r0:float=.6;nu:float=2.;persistence:float=1.;n:int=10;stock_step:float=.5
 probabilities:tuple=(.1,.3,.4,.2);dispersion:float=1.;q0:float=.5
 fill_delta:float=0.;utility_delta:float=0.;cost_delta:float=0.

def primitives(M):
 stock=np.unique(np.r_[np.arange(0,6+1e-10,M.stock_step),6.]);S=len(stock)
 demand=np.arange(3)[:,None]+1.7+M.dispersion*(np.arange(4)[None,:]-1.7)
 prob=np.array(M.probabilities);lo=(np.maximum(demand[:,None,:]-stock[None,:,None],0)*prob).sum(-1)
 ov=(np.maximum(stock[None,:,None]-demand[:,None,:],0)*prob).sum(-1)
 C=.3*stock[None,:]+.6*ov+.65*lo;mean=demand@prob;f=mean[:,None]-lo
 a=(M.r0+M.slope*np.arange(3))[:,None]-M.kappa*lo
 P=M.persistence*np.array([[.7,.25,.05],[.15,.7,.15],[.05,.25,.7]])+(1-M.persistence)*np.tile([.25,.5,.25],(3,1))
 assert P.min()>=0
 dist=np.zeros((M.T,3));dist[0,1]=1
 for t in range(1,M.T):dist[t]=dist[t-1]@P
 w=dist*M.beta**np.arange(M.T)[:,None];alpha=w.sum(0)
 return dict(stock=stock,C=C,f=f,a=a,P=P,mean=mean,w=w,alpha=alpha)

def static(M,d):
 # Breakpoints of every stock-line pair suffice; unused crossings are harmless.
 cuts={0.,1.};a=d['a'];C=d['C'];alpha=d['alpha'];H=alpha.sum()
 for z in range(3):
  for i in range(len(d['stock'])):
   for j in range(i):
    if abs(a[z,i]-a[z,j])>1e-14:
     x=(C[z,i]-C[z,j])/(a[z,i]-a[z,j])
     if 0<x<1:cuts.add(float(x))
 candidates=list(sorted(cuts))
 for l,r in zip(sorted(cuts)[:-1],sorted(cuts)[1:]):
  si=np.argmax(a*((l+r)/2)-C,axis=1);A=alpha@a[np.arange(3),si]
  if M.power==2:
   x=(A+2*M.lam*M.q0)/(2*(M.m*H+M.lam))
   if l<=x<=r:candidates.append(float(x))
  else:
   result=minimize_scalar(lambda x:-A*x+M.m*H*x**M.power+M.lam*(x-M.q0)**2,bounds=(l,r),method='bounded',options={'xatol':1e-14})
   candidates.append(float(result.x))
 def value(th):return alpha@np.max(a*th-C,axis=1)-M.m*H*th**M.power-M.lam*(th-M.q0)**2
 th=max(candidates,key=value);si=np.argmax(a*th-C,axis=1)
 out=dict(theta=th,value=float(value(th)),stock_indices=si.tolist(),physical=float(alpha@C[np.arange(3),si]),filled=float(alpha@d['f'][np.arange(3),si]),payment=float(th*(alpha@a[np.arange(3),si])),demand=float(alpha@d['mean']))
 out['customer']=M.nu*out['filled']-out['payment'];return out

def supporting(d,base):
 s=base['stock_indices'];c=d['C']-d['C'][np.arange(3),s,None];f=d['f']-d['f'][np.arange(3),s,None]
 mask=np.ones_like(c,bool);mask[np.arange(3),s]=False
 lb=max(0.,np.max((c/f)[mask&(f< -1e-12)]) if np.any(mask&(f< -1e-12)) else 0.)
 ub=np.min((c/f)[mask&(f>1e-12)]) if np.any(mask&(f>1e-12)) else lb+2
 if ub<=lb+1e-10 or np.any(c[mask&(abs(f)<1e-12)]<=0):return None
 gamma=(lb+ub)/2;gap=(c-gamma*f)[mask]
 return {'price':float(gamma),'gap':float(gap.min())} if gap.min()>1e-10 else None

def accepted_lp(M,d,base):
 N=M.n+1;th=np.linspace(0,1,N);S=len(d['stock']);T=M.T
 t,z,i,j,s=np.indices((T,3,N,N,S)).reshape(5,-1);nv=len(t);cols=np.arange(nv);rows=(t*3+z)*N+i
 rr=[rows];cc=[cols];vv=[np.ones(nv)];active=t<T-1
 for zp in range(3):rr.append(((t[active]+1)*3+zp)*N+j[active]);cc.append(cols[active]);vv.append(-d['P'][z[active],zp])
 A=coo_matrix((np.concatenate(vv),(np.concatenate(rr),np.concatenate(cc))),shape=(T*3*N,nv)).tocsr();b=np.zeros(T*3*N);b[N+int(round(M.q0*M.n))]=1
 wt=M.beta**t;C=wt*d['C'][z,s];F=wt*d['f'][z,s];pay=wt*d['a'][z,s]*th[j]
 reward=pay-C-wt*(M.m*th[j]**M.power+M.lam*(th[j]-th[i])**2);U=M.nu*F-pay
 rhs=np.array([-base['filled']-M.fill_delta*base['demand'],-base['customer']-M.utility_delta,base['physical']+M.cost_delta]);ineq=np.vstack([-F,-U,C])
 start=time.perf_counter();res=linprog(-reward,A_ub=ineq,b_ub=rhs,A_eq=A,b_eq=b,bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});elapsed=time.perf_counter()-start
 out={'status':res.message,'feasible':bool(res.success),'seconds':elapsed,'variables':nv}
 if not res.success:return out
 val=float(reward@res.x);slack=rhs-ineq@res.x
 denom=np.asarray(coo_matrix((res.x,(rows,cols)),shape=(len(b),nv)).sum(1)).ravel()[rows]
 nz=res.x>1e-9;row_counts=np.bincount(rows[nz],minlength=len(b));random_states=int((row_counts>1).sum())
 red=-reward-A.T@res.eqlin.marginals-ineq.T@res.ineqlin.marginals
 out.update(value=val,gain=val-base['value'],filled=float(F@res.x),customer=float(U@res.x),physical=float(C@res.x),slacks=slack.tolist(),multipliers=(-res.ineqlin.marginals).tolist(),randomized_reachable_states=random_states,flow_residual=float(abs(A@res.x-b).max()),inequality_violation=float(max(0,-slack.min())),duality_gap=float((-reward@res.x)-(b@res.eqlin.marginals+rhs@res.ineqlin.marginals)),reduced_cost_min=float(red.min()),positive_columns=int(nz.sum()))
 return out

def quadratic_hierarchy(M,d,base):
 if M.power!=2 or M.fill_delta!=0 or M.cost_delta!=0 or supporting(d,base) is None:return None
 s=np.array(base['stock_indices']);a=d['a'][np.arange(3),s];C=d['C'][np.arange(3),s];w=d['w'];dist=w/M.beta**np.arange(M.T)[:,None];cap=base['payment']-M.utility_delta
 if cap<0:return None
 rows=[]
 for kind in ['static','time','regime']:
  keys=([0] if kind=='static' else list(range(M.T)) if kind=='time' else [(t,z) for t in range(M.T) for z in range(3) if dist[t,z]>0]);ind={k:i for i,k in enumerate(keys)};n=len(keys)
  def ix(t,z):return ind[0 if kind=='static' else t if kind=='time' else (t,z)]
  H=np.zeros((n,n));b=np.zeros(n);c=np.zeros(n)
  for t in range(M.T):
   for z in range(3):
    if dist[t,z]==0:continue
    i=ix(t,z);wt=w[t,z];H[i,i]+=M.m*wt;b[i]+=a[z]*wt;c[i]+=a[z]*wt
    if t==0:H[i,i]+=M.lam*wt;b[i]+=2*M.lam*M.q0*wt
    else:
     for zp in range(3):
      if dist[t-1,zp]==0:continue
      j=ix(t-1,zp);e=M.lam*M.beta**t*dist[t-1,zp]*d['P'][zp,z]
      H[i,i]+=e;H[j,j]+=e;H[i,j]-=e;H[j,i]-=e
  x0=np.linalg.solve(H,b)/2;xc=np.linalg.solve(H,c)/2;eta=max(0,(c@x0-cap)/(c@xc));x=x0-eta*xc
  if min(x)<0 or max(x)>1:return None
  rows.append(dict(policy_class=kind,value=float(-x@H@x+b@x-base['physical']-M.lam*M.q0**2),eta=float(eta),stationarity=float(abs(2*H@x-b+eta*c).max()),customer_slack=float(cap-c@x)))
 def pol(eta):
  A=0.;B=np.zeros(3);p=[]
  for t in reversed(range(M.T)):
   K=M.m+M.lam+M.beta*A;L=(1-eta)*a+M.beta*d['P']@B;p.append((M.lam/K,L/(2*K)));A=M.lam-M.lam*M.lam/K;B=M.lam*L/K
  return p[::-1]
 def evaluate(p):
  mass=np.array([0.,1.,0.]);mean=mass*M.q0;sq=mass*M.q0**2;pay=0.;cost=0.
  for t,(k,b) in enumerate(p):
   mt=k*mean+b*mass;st=k*k*sq+2*k*b*mean+b*b*mass;dd=(k-1)**2*sq+2*(k-1)*b*mean+b*b*mass
   pay+=M.beta**t*(a@mt);cost+=M.beta**t*(M.m*st.sum()+M.lam*dd.sum());mass=mass@d['P'];mean=mt@d['P'];sq=st@d['P']
  return pay-base['physical']-cost,pay
 p0=evaluate(pol(0))[1];p1=evaluate(pol(1))[1];eta=max(0,(p0-cap)/(p0-p1));p=pol(eta)
 if any(min(b)<-1e-12 or max(b+k)>1+1e-12 for k,b in p):return None
 val,pay=evaluate(p);rows.append(dict(policy_class='full',value=val,eta=eta,customer_slack=cap-pay))
 return rows

def grid_dp(M,d,base,n,eta):
 th=np.linspace(0,1,n+1);a=d['a'][np.arange(3),base['stock_indices']];C=d['C'][np.arange(3),base['stock_indices']];V=np.zeros((3,n+1));pol=[]
 for t in reversed(range(M.T)):
  obj=(1-eta)*a[:,None,None]*th[None,None,:]-C[:,None,None]-M.m*th[None,None,:]**M.power-M.lam*(th[:,None]-th[None,:])**2+M.beta*(d['P']@V)[:,None,:]
  pi=obj.argmax(2);V=np.take_along_axis(obj,pi[:,:,None],2)[:,:,0];pol.append(pi)
 pol=pol[::-1];mass=np.zeros((3,n+1));mass[1,n//2]=1;val=pay=0.
 for t,pi in enumerate(pol):
  z,i=np.nonzero(mass);j=pi[z,i];w=M.beta**t*mass[z,i];pay+=float(np.sum(w*a[z]*th[j]));val+=float(np.sum(w*(a[z]*th[j]-C[z]-M.m*th[j]**M.power-M.lam*(th[j]-th[i])**2)))
  nxt=np.zeros_like(mass)
  for zp in range(3):np.add.at(nxt[zp],j,mass[z,i]*d['P'][z,zp])
  mass=nxt
 return dict(value=val,payment=pay,dual_value=float(V[1,n//2]+eta*base['payment']),eta=eta)

def fine_menus():
 M=Model();d=primitives(M);base=static(M,d);rows=[]
 for n in [10,20,40,80,160,320]:
  start=time.perf_counter();lo=0.;hi=1.;rlo=grid_dp(M,d,base,n,lo);rhi=grid_dp(M,d,base,n,hi)
  for k in range(44):
   mid=(lo+hi)/2;r=grid_dp(M,d,base,n,mid)
   if r['payment']>base['payment']:lo=mid;rlo=r
   else:hi=mid;rhi=r
  mix=(base['payment']-rhi['payment'])/(rlo['payment']-rhi['payment']);val=mix*rlo['value']+(1-mix)*rhi['value'];upper=min(rlo['dual_value'],rhi['dual_value'])
  rows.append(dict(intervals=n,randomized_value=val,deterministic_value=rhi['value'],randomized_gain=val-base['value'],deterministic_gain=rhi['value']-base['value'],numerical_upper=upper,primal_dual_gap=upper-val,deterministic_to_upper=upper-rhi['value'],seconds=time.perf_counter()-start))
 (OUT/'fine_menus.json').write_text(json.dumps(rows,indent=2)+'\n');return rows

def main():
 cases=[('canonical',{})]
 for key,values in [('lam',[.1,1.2,4.]),('m',[1.2,1.8]),('power',[1.5,3.]),('kappa',[.9,1.5]),('slope',[1.1,1.7]),('r0',[.3,.9]),('nu',[1.,3.]),('persistence',[.6,1.2]),('dispersion',[.8,1.2]),('utility_delta',[-.2,.2,.8]),('fill_delta',[-.015,.015]),('stock_step',[1.,.25])]:
  cases.extend((f'{key}={v}',{key:v}) for v in values)
 cases.extend([('lower_variance_prob',{'probabilities':(.05,.35,.45,.15)}),('higher_variance_prob',{'probabilities':(.15,.25,.35,.25)}),('higher_service_with_cost_slack',{'fill_delta':.015,'cost_delta':.6}),('zero_regime_premium',{'slope':0.})])
 rows=[]
 for label,kw in cases:
  M=replace(Model(),**kw);d=primitives(M);base=static(M,d)
  with np.errstate(divide='ignore',invalid='ignore'):pin=supporting(d,base);hier=quadratic_hierarchy(M,d,base)
  r=accepted_lp(M,d,base);item=dict(case=label,primitives=asdict(M),reference=base,reference_meets_changed_reservation=(M.utility_delta<=1e-12 and M.fill_delta<=1e-12 and M.cost_delta>=-1e-12),stock_support=pin,accepted=r,continuous_hierarchy=hier)
  if hier is not None and r['feasible']:item['accepted']['gain_over_accepted_static']=r['value']-hier[0]['value']
  rows.append(item);(OUT/'accepted_robustness.json').write_text(json.dumps(rows,indent=2)+'\n');print(label, r.get('value','infeasible'),r.get('gain'),flush=True)
 fine=fine_menus();print('fine',fine,flush=True)
if __name__=='__main__':main()
