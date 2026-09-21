#!/usr/bin/env python3
"""R6 operational experiments. No network. All baselines use identical primitives.
Run: python revisions/or-r6-20260921/compute.py [core|restrictions|all].
The floating LP/MIP certificates below are numerical, not exact rational proofs.
"""
from __future__ import annotations
from dataclasses import dataclass, replace, asdict
from pathlib import Path
from fractions import Fraction as F
import json, csv, sys, time, platform
import numpy as np
from scipy.optimize import linprog, milp, Bounds, LinearConstraint
from scipy.sparse import coo_matrix, vstack, hstack, csr_matrix

HERE=Path(__file__).resolve().parent
OUT=HERE/'results'; OUT.mkdir(exist_ok=True)
@dataclass(frozen=True)
class Model:
    T:int=8
    n:int=10
    beta:float=.97
    c:float=.3
    h:float=.6
    p:float=.65
    kappa:float=1.2
    m:float=1.5
    lam:float=.6
    r0:float=.6
    slope:float=1.4
    persistence:float=1.0
    nu:float=2.
    q0:float=.5

def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')
def csvsave(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def primitives(M=Model()):
    theta=np.linspace(0,1,M.n+1); stock=np.arange(13)/2
    demand=np.arange(3)[:,None]+np.arange(4)[None,:]
    prob=np.array([.1,.3,.4,.2])
    lost=(np.maximum(demand[:,None,:]-stock[None,:,None],0)*prob).sum(-1)
    over=(np.maximum(stock[None,:,None]-demand[:,None,:],0)*prob).sum(-1)
    phys=M.c*stock[None,:]+M.h*over+M.p*lost
    P0=np.array([[.70,.25,.05],[.15,.70,.15],[.05,.25,.70]])
    P=M.persistence*P0+(1-M.persistence)*np.tile([.25,.5,.25],(3,1))
    if (P < -1e-12).any(): raise ValueError('Invalid transition')
    mean=demand@prob
    r=M.r0+M.slope*np.arange(3)
    stage=r[:,None,None]*theta[None,None,:]-phys[:,:,None]-M.kappa*lost[:,:,None]*theta[None,None,:]-M.m*theta[None,None,:]**2
    # greatest stock at ties, independent of inherited q
    si=12-np.argmax(stage[:,::-1,:],axis=1)
    B=np.take_along_axis(stage,si[:,None,:],axis=1)[:,0,:]
    return dict(theta=theta,stock=stock,lost=lost,phys=phys,P=P,mean=mean,r=r,stage=stage,si=si,B=B)

def solve(M=Model(),kind='full',fixed=None):
    d=primitives(M); th=d['theta']; N=M.n+1
    V=np.zeros((M.T+1,3,N)); pol=np.zeros((M.T,3,N),int)
    if kind=='time':
        dist=np.zeros((M.T,3));dist[0,1]=1
        for t in range(1,M.T):dist[t]=dist[t-1]@d['P']
        U=np.zeros((M.T+1,N)); acts=np.zeros((M.T,N),int)
        for t in reversed(range(M.T)):
            obj=dist[t]@d['B']-M.lam*(th[:,None]-th[None,:])**2+M.beta*U[t+1]
            acts[t]=N-1-np.argmax(obj[:,::-1],axis=1);U[t]=obj[np.arange(N),acts[t]]
        q=int(round(M.q0*M.n))
        for t in range(M.T):
            a=acts[t,q];pol[t,:,:]=a;q=a
    for t in reversed(range(M.T)):
        obj=d['B'][:,None,:]-M.lam*(th[:,None]-th[None,:])**2+M.beta*(d['P']@V[t+1])[:,None,:]
        if kind=='full':pol[t]=N-1-np.argmax(obj[:,:,::-1],axis=2)
        if kind=='fixed':pol[t,:,:]=fixed
        V[t]=np.take_along_axis(obj,pol[t,:,:,None],2)[:,:,0]
    return V,pol,d

KEYS=('reward','physical','premium','liability','maintenance','adjustment','filled','lost','demand','customer','movement','tier2','exposure','tier')
def ledger(pol,M=Model(),d=None):
    if d is None:d=primitives(M)
    mass=np.zeros((3,M.n+1));mass[1,int(round(M.q0*M.n))]=1
    ans={k:0. for k in KEYS}
    for t in range(M.T):
        nxt=np.zeros_like(mass)
        for z,i in zip(*np.nonzero(mass)):
            j=pol[t,z,i]; th=d['theta'][j]; q=d['theta'][i]; s=d['si'][z,j]
            lo=d['lost'][z,s];fill=d['mean'][z]-lo
            v=dict(physical=d['phys'][z,s],premium=d['r'][z]*th,liability=M.kappa*th*lo,maintenance=M.m*th**2,
                adjustment=M.lam*(th-q)**2,filled=fill,lost=lo,demand=d['mean'][z],movement=(th-q)**2,tier2=th**2,exposure=th*lo,tier=th)
            v['reward']=v['premium']-sum(v[k] for k in ('physical','liability','maintenance','adjustment'))
            v['customer']=M.nu*fill+v['liability']-v['premium']
            for k in KEYS:ans[k]+=M.beta**t*mass[z,i]*v[k]
            nxt[:,j]+=mass[z,i]*d['P'][z]
        mass=nxt
    ans['fill_rate']=ans['filled']/ans['demand']
    return ans

def static_exact():
    """Exact rational, continuous theta. Enumerate all stock-envelope breakpoints.
    Charge installation lambda*(theta-q0)^2 at t=0, as in every dynamic class.
    """
    P=[[F(x,20) for x in row] for row in [[14,5,1],[3,14,3],[1,5,14]]]
    beta=F(97,100); lam=F(3,5);m=F(3,2);kap=F(6,5);q0=F(1,2)
    alpha=[F(0)]*3;dist=[F(0),F(1),F(0)]
    for t in range(8):
        alpha=[alpha[z]+beta**t*dist[z] for z in range(3)]
        dist=[sum(dist[z]*P[z][zp] for z in range(3)) for zp in range(3)]
    lines=[];knots={F(0),F(1)}
    for z in range(3):
        zz=[]
        for s2 in range(13):
            S=F(s2,2);lo=sum(F(w,10)*max(z+d-S,0) for d,w in enumerate([1,3,4,2]));ov=sum(F(w,10)*max(S-z-d,0) for d,w in enumerate([1,3,4,2]))
            C=F(3,10)*S+F(3,5)*ov+F(13,20)*lo
            zz.append((-C, F(3,5)+F(7,5)*z-kap*lo))
        for a,b in zz:
            for aa,bb in zz:
                if b!=bb and 0<(x:=(aa-a)/(b-bb))<1:knots.add(x)
        lines.append(zz)
    cuts=sorted(knots); candidates=set(cuts);A=m*sum(alpha)+lam
    for l,r in zip(cuts,cuts[1:]):
        x=(l+r)/2;active=[max(enumerate(zz),key=lambda it:(it[1][0]+it[1][1]*x,it[0]))[1] for zz in lines]
        B=sum(alpha[z]*active[z][1] for z in range(3))+2*lam*q0
        x=B/(2*A)
        if l<=x<=r:candidates.add(x)
    def val(x):return sum(alpha[z]*max(a+b*x for a,b in lines[z]) for z in range(3))-m*sum(alpha)*x*x-lam*(x-q0)**2
    opt=max(candidates,key=lambda x:(val(x),x));grid=max((F(j,10) for j in range(11)),key=lambda x:val(x))
    ans=dict(theta_fraction=str(opt),theta=float(opt),value_fraction=str(val(opt)),value=float(val(opt)),best_grid_theta=float(grid),best_grid_value=float(val(grid)),frozen_value=float(val(F(1,2))),candidate_count=len(candidates),installation_cost='charged at t=0')
    save('static_exact.json',ans);return ans

def occupancy(M=Model(),reduced=False):
    """Undiscounted flow variables; discount is in payoff/constraint coefficients.
    unreduced includes ALL stock actions, essential under service constraints.
    """
    d=primitives(M);N=M.n+1;NS=M.T*3*N
    cols=[];r=[];c=[];v=[]; rewards=[];metrics={k:[] for k in KEYS}
    for t in range(M.T):
      for z in range(3):
       for i in range(N):
        for j in range(N):
         stocks=[int(d['si'][z,j])] if reduced else range(13)
         for s in stocks:
          col=len(cols);cols.append((t,z,i,j,s));row=(t*3+z)*N+i
          r.append(row);c.append(col);v.append(1.)
          if t<M.T-1:
           for zp in range(3):r.append(((t+1)*3+zp)*N+j);c.append(col);v.append(-d['P'][z,zp])
          th=d['theta'][j];q=d['theta'][i];lo=d['lost'][z,s]; fill=d['mean'][z]-lo
          a=dict(physical=d['phys'][z,s],premium=d['r'][z]*th,liability=M.kappa*th*lo,maintenance=M.m*th**2,
                 adjustment=M.lam*(th-q)**2,filled=fill,lost=lo,demand=d['mean'][z],movement=(th-q)**2,tier2=th**2,exposure=th*lo,tier=th)
          a['reward']=a['premium']-sum(a[k] for k in ('physical','liability','maintenance','adjustment'))
          a['customer']=M.nu*fill+a['liability']-a['premium']
          for k in KEYS:metrics[k].append(M.beta**t*a[k])
    A=coo_matrix((v,(r,c)),shape=(NS,len(cols))).tocsr();rhs=np.zeros(NS);rhs[N+int(round(M.q0*M.n))]=1
    return A,rhs,np.array(cols),{k:np.array(v) for k,v in metrics.items()},d

def continuous_static_ledger(M=Model()):
    d=primitives(M);th=static_exact()['theta'];dist=np.array([0.,1.,0.]);ans={k:0. for k in KEYS}
    for t in range(M.T):
      for z in range(3):
        obj=d['r'][z]*th-d['phys'][z]-M.kappa*th*d['lost'][z]-M.m*th*th
        si=12-np.argmax(obj[::-1]);lo=d['lost'][z,si];fill=d['mean'][z]-lo
        move=(th-M.q0)**2 if t==0 else 0.
        v=dict(physical=d['phys'][z,si],premium=d['r'][z]*th,liability=M.kappa*th*lo,maintenance=M.m*th*th,adjustment=M.lam*move,filled=fill,lost=lo,demand=d['mean'][z],movement=move,tier2=th*th,exposure=th*lo,tier=th)
        v['reward']=v['premium']-sum(v[k] for k in ('physical','liability','maintenance','adjustment'))
        v['customer']=M.nu*fill+v['liability']-v['premium']
        for k in KEYS:ans[k]+=M.beta**t*dist[z]*v[k]
      dist=dist@d['P']
    ans['fill_rate']=ans['filled']/ans['demand'];return ans

def constrain_core(M=Model()):
    A,b,idx,met,d=occupancy(M)
    base=continuous_static_ledger(M)
    rows=[];policies={};certs={}
    # Floor is imposed on discounted expected fill, not sample fill ratios.
    # Expected demand is exogenous, so this is the corresponding fill-rate floor.
    for label,gamma,participation,physcap in [
      ('unconstrained',0,False,False),('service_90',.90,False,False),('service_92',.92,False,False),
      ('same_service',base['fill_rate'],False,False),('same_service_customer',base['fill_rate'],True,False),
      ('same_service_customer_cost',base['fill_rate'],True,True),('service_95_customer',.95,True,False),('service_98_customer',.98,True,False)]:
        C=[-met['filled']];h=[-gamma*base['demand']]
        if participation:C.append(-met['customer']);h.append(-base['customer'])
        if physcap:C.append(met['physical']);h.append(base['physical'])
        C=np.array(C);h=np.array(h)
        res=linprog(-met['reward'],A_ub=C,b_ub=h,A_eq=A,b_eq=b,bounds=(0,None),method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
        if not res.success:raise RuntimeError((label,res.message))
        out={k:float(a@res.x) for k,a in met.items()};out['fill_rate']=out['filled']/out['demand']
        primal=float(-met['reward']@res.x);dual=float(b@res.eqlin.marginals+h@res.ineqlin.marginals)
        station=-met['reward']-A.T@res.eqlin.marginals-C.T@res.ineqlin.marginals
        certs[label]=dict(primal_min=primal,dual_min=dual,gap=primal-dual,flow_residual=float(np.max(np.abs(A@res.x-b))),max_inequality_violation=float(max(0,np.max(C@res.x-h))),min_reduced_cost=float(station.min()),max_complementarity=float(np.max(np.abs(res.x*station))),active_columns=int((res.x>1e-10).sum()),multipliers=(-res.ineqlin.marginals).tolist(),status=res.message)
        rows.append(dict(policy=label,**out,gain_over_best_continuous_static=out['reward']-base['reward']))
        nz=np.flatnonzero(res.x>1e-10)
        policies[label]=[dict(t=int(idx[k,0]),z=int(idx[k,1]),inherited=int(idx[k,2]),contract=int(idx[k,3]),stock_index=int(idx[k,4]),occupancy=float(res.x[k])) for k in nz]
    csvsave('service_frontier.csv',rows);save('lp_certificates.json',certs);save('service_policies.json',policies);save('static_service_reference.json',base)
    return rows

def restricted(kind,M=Model(),time_limit=15):
    """Globally optimize deterministic time-regime / time-inherited contract rules.
    Binary selectors force one contract at all hidden-state realizations; q-blind
    policies are NOT incorrectly optimized with a fully observed Bellman backup.
    Feasible incumbent and solver dual bound are both stored.
    """
    A,b,idx,met,d=occupancy(M,reduced=True);N=M.n+1;nc=len(idx)
    group=(idx[:,0]*3+idx[:,1]) if kind=='regime' else (idx[:,0]*N+idx[:,2])
    ng=M.T*(3 if kind=='regime' else N);ny=ng*N
    y=group*N+idx[:,3]
    gate=coo_matrix((-np.ones(nc),(np.arange(nc),y)),shape=(nc,ny)).tocsr()
    G=hstack([csr_matrix(np.eye(1))]) if False else hstack([coo_matrix((np.ones(nc),(np.arange(nc),np.arange(nc))),shape=(nc,nc)),gate]).tocsr()
    Y=coo_matrix((np.ones(ny),(np.repeat(np.arange(ng),N),np.arange(ny))),shape=(ng,ny)).tocsr()
    C=vstack([hstack([A,csr_matrix((len(b),ny))]),G,hstack([csr_matrix((ng,nc)),Y])]).tocsr()
    low=np.r_[b,np.full(nc,-np.inf),np.ones(ng)];high=np.r_[b,np.zeros(nc),np.ones(ng)]
    start=time.perf_counter()
    res=milp(np.r_[-met['reward'],np.zeros(ny)],integrality=np.r_[np.zeros(nc),np.ones(ny)],bounds=Bounds(0,1),constraints=LinearConstraint(C,low,high),options={'time_limit':time_limit,'mip_rel_gap':1e-8})
    if res.x is None:raise RuntimeError((kind,res.message))
    x=res.x[:nc];ym=res.x[nc:].reshape(ng,N);rule=ym.argmax(1).reshape(M.T,3 if kind=='regime' else N)
    pol=np.empty((M.T,3,N),int)
    for t in range(M.T):
      for z in range(3):
       for i in range(N):pol[t,z,i]=rule[t,z if kind=='regime' else i]
    ev=ledger(pol,M,d);assert abs(ev['reward']+res.fun)<1e-6
    cert=dict(kind=kind,**ev,lower_bound=ev['reward'],upper_bound=-float(res.mip_dual_bound),mip_gap=float(res.mip_gap),nodes=int(res.mip_node_count),wall_seconds=time.perf_counter()-start,status=res.message,flow_residual=float(np.max(np.abs(A@x-b))),rule=rule.tolist())
    save('restriction_'+kind+'.json',cert)
    return cert

def core():
    static=static_exact();M=Model();rows=[]
    for label,kind,j in [('frozen_0.5','fixed',5),('best_static_grid','fixed',6),('time_only','time',None),('full','full',None)]:
        val,pol,d=solve(M,kind,j);v=ledger(pol,M,d)
        assert abs(val[0,1,5]-v['reward'])<1e-11
        rows.append(dict(policy=label,**v))
        if label=='full':
            save('full_policy.json',dict(policy=pol.tolist(),value=val.tolist()))
            import importlib.util
            spec=importlib.util.spec_from_file_location('r4',HERE.parent/'or-r4-20260920/execute.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
            exact=old.int_dp(factored=True); oldled=old.exact_ledger(exact)
            assert abs(v['reward']-float(oldled['net_reward']))<1e-12
            save('exact_replay.json',dict(full_value_fraction=str(oldled['net_reward']),full_value=float(oldled['net_reward']),states_checked=M.T*3*(M.n+1),policy_matches=bool(np.array_equal(pol,np.array(exact['policy'])[:,:,:,1]))))
    csvsave('adaptivity.csv',rows)
    sens=[]
    for param,vals in [('lam',[0,.15,.3,.6,1.2,2.4,4.8]),('kappa',[.3,.6,1.2,2.4]),('m',[.75,1.5,3.]),('slope',[.4,.8,1.2,1.4,2.]),('persistence',[0.,.5,1.]),('beta',[.8,.9,.97,1.])]:
      for x in vals:
        m=replace(M,**{param:x});_,p,d=solve(m);r=ledger(p,m,d)
        candidates=[(ledger(solve(m,'fixed',j)[1],m,d)['reward'],j) for j in range(m.n+1)]
        best,j=max(candidates)
        sens.append(dict(parameter=param,level=x,**r,static_best=best,static_theta=j/m.n,adaptive_gain=r['reward']-best,monotone_regime=bool(np.all(np.diff(p,axis=1)>=0)),monotone_inherited=bool(np.all(np.diff(p,axis=2)>=0))))
    csvsave('comparative_statics.csv',sens)
    frontier=constrain_core(M)
    save('environment.json',dict(python=sys.version,platform=platform.platform(),model=asdict(M)))
    print(json.dumps(dict(static=static,adaptivity=rows,frontier=frontier),indent=2))

if __name__=='__main__':
    which=sys.argv[1] if len(sys.argv)>1 else 'all'
    if which in ('core','all'):core()
    if which in ('restrictions','all'):
        print(json.dumps(restricted('regime',time_limit=60),indent=2))
        # q-only rules cannot observe z: q remains deterministic from fixed q0.
        _,pol,d=solve(Model(),'time');v=ledger(pol)
        save('restriction_inherited.json',dict(kind='inherited',**v,lower_bound=v['reward'],upper_bound=v['reward'],status='Analytic equality with time-only class; see Proposition in manuscript'))
