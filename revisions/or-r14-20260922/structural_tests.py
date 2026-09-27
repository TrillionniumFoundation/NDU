#!/usr/bin/env python3
"""Cross-check structural identities, classical solvers, and learning bounds."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import json,time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
from star import Star
OUT=Path(__file__).resolve().parent/'results'
def main():
    rng=np.random.default_rng(14077);checks=0;dense_checks=0;lp_checks=0;max_dense_error=0.;max_bound_ratio=0.;critical=[];bound_cases=[]
    for n in [1,3,7,31,127]:
        s=Star(n)
        for j in range(32):
            theta=np.array([rng.integers(-5000,5001),rng.integers(-3000,3001),rng.integers(1,2001)])/1000
            y,tau,meta=s.solve(theta,'newton');val=s.value(theta,y)
            for meth in ['brent','sort','bisect']:
                z,tt,mm=s.solve(theta,meth)
                assert abs(s.value(theta,z)-val)<1e-9
                assert np.max(abs(y-z))<2e-7;checks+=1
            if n<=31:
                z=s.dense(theta);e=abs(s.value(theta,z)-val);max_dense_error=max(max_dense_error,e)
                assert e<2e-8;dense_checks+=1
            # General tension LP: K=D*B, with all installation/continuation edges.
            a=s.d(theta)+theta[2]*s.t
            B=np.vstack([s.rho,-np.eye(n)])
            D=np.eye(n+1);D[1:,0]=-1;K=D@B;k=np.r_[1.,np.full(n,float(s.w))]
            c=np.r_[1.,np.zeros(n+1)]
            A=np.vstack([np.column_stack([np.zeros(n),-K.T]),
                         np.column_stack([-k,np.eye(n+1)]),np.column_stack([-k,-np.eye(n+1)])])
            rr=linprog(c,A_ub=A,b_ub=np.r_[-a,np.zeros(2*(n+1))],bounds=[(0,None)]+[(None,None)]*(n+1),method='highs')
            assert rr.success
            lc=s.critical(theta);assert abs(lc-rr.fun)<2e-8;lp_checks+=1
            vstar=s.rho@y;etastar=s.q0*vstar
            # Wrong predicted prices, cap binding, leaf bounds, and static cases.
            for eta in [0.,.03,.5,1.,float(rng.random())]:
                yp,tt,ep,cap=s.surrogate(theta,eta);vp=s.rho@yp
                regret=val-s.value(theta,yp)
                residual=.5*s.kappa*(ep-s.q0*vp)**2
                apriori=.5*s.R*(1+s.q0*s.R)*(ep-etastar)**2
                Hstar=s.d(theta)@y-.5*np.dot(s.q,y*y)-etastar*vstar
                Hep=s.d(theta)@yp-.5*np.dot(s.q,yp*yp)-ep*vp
                breg=Hstar-Hep+vp*(etastar-ep)
                ident=breg+.5*s.q0*(vp-vstar)**2
                assert abs(regret-ident)<2e-9 and regret<=min(residual,apriori)+2e-9
                if residual>1e-12:max_bound_ratio=max(max_bound_ratio,regret/residual)
                bound_cases.append({'n':n,'theta':theta.tolist(),'eta':ep,'regret':regret,'residual_bound':residual,
                                     'gradient_price_bound':apriori,'identity_error':regret-ident,'root_cap':bool(cap)})
        for ratio in [0.,.5,.99,1.,1.01,2.]:
            theta=[.8,.2,ratio*s.critical([.8,.2,0])]
            y,tt,_=s.solve(theta);gain=s.value(theta,y)
            if ratio<1:assert gain>0
            else:assert abs(gain)<1e-9
            critical.append({'n':n,'ratio':ratio,'critical_friction':s.critical(theta),'friction':theta[2],
                             'gain':gain,'root_transfer':float(s.rho@y),'nonzero_transfers':int(np.sum(y>1e-10))})
    scaling=[]
    for n in [31,127,511,2047,8191,32767]:
        s=Star(n);theta=[.4,-.3,.12]
        for method in ['critical','newton','brent','sort']:
            times=[];it=[]
            for _ in range(5):
                t=time.perf_counter_ns()
                if method=='critical':answer=s.critical(theta);count=n
                else:y,tt,mm=s.solve(theta,method);count=mm['iterations']
                times.append((time.perf_counter_ns()-t)/1e6);it.append(count)
            scaling.append({'leaves':n,'method':method,'median_ms':float(np.median(times)),'raw_ms':times,'iterations':it})
    summary={'solver_agreements':checks,'SLSQP_crosschecks':dense_checks,'general_tension_LP_crosschecks':lp_checks,
             'arbitrary_price_bound_checks':len(bound_cases),'max_dense_value_error':max_dense_error,
             'max_residual_bound_ratio':max_bound_ratio,'max_scaling_leaves':32767,
             'root_capacity_binding_bound_cases':sum(v['root_cap'] for v in bound_cases),'status':'PASS'}
    for name,obj in [('structural_checks.json',summary),('bound_cases.json',bound_cases),('friction_path.json',critical),('scaling.json',scaling)]:
        (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
