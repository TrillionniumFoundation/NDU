#!/usr/bin/env python3
"""Deterministic heterogeneous multistage checks, not training observations."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from fractions import Fraction as F
import json
import numpy as np
from scipy.optimize import minimize,LinearConstraint
from multiresource import Tree,contexts
OUT=Path(__file__).resolve().parent/'results'
def run():
    rows=[];proof_records=[];independent=[]
    for seed,nodes,rank in zip(range(15201,15205),[15,31,63,127],[2,4,6,8]):
        s=Tree(nodes,2,rank,seed);rng=np.random.default_rng(seed+200)
        Khalf=s.U@np.linalg.solve(.5*np.diag(s.d)+s.U.T@s.U,s.U.T)
        for j,c in enumerate(contexts(seed+100,16,rank)):
            xr,dr,it=s.solve(c);ref=s.audit(c,xr,dr,record=True)
            eta=s.U@xr[:s.n]+rng.normal(0,.15,rank)
            xb,db,ib=s.solve(c,price=eta);a=s.audit(c,xb,db,price=eta,record=True)
            rr=a['record'];y=np.array([float(F(int(x),int(rr['x_den']))) for x in rr['x_num']]);ep=np.array(rr['price_num'])/rr['dual_den'];res=ep-s.U@y
            # Full Fenchel upper = base Fenchel upper + ||eta-Uy||^2/2.
            # Derive a certified base-oracle gap in exact rational arithmetic.
            exactres=[F(int(z),rr['dual_den'])-sum((F(int(u)*int(x),32*int(rr['x_den'])) for u,x in zip(row,rr['x_num'])),F(0)) for row,z in zip(s.Unum,rr['price_num'])]
            delta=F(rr['upper'])-F(a['raw_gain_exact'])-sum((r*r/2 for r in exactres),F(0))
            assert delta>=0,('invalid base oracle certificate',delta)
            bound=2*float(delta)+.5*float(res@Khalf@res)
            actual_upper=max(0.,ref['gain']+ref['gap']-a['raw_gain'])
            # A positive reference gap means the true regret is bracketed. The
            # lower end must obey the theorem; the upper end includes this width.
            assert actual_upper<=bound+ref['gap']+5e-10
            row={'seed':seed,'nodes':nodes,'services':2,'rank':rank,'context':j,'reference_gain':ref['gain'],'reference_gap':ref['gap'],'regret_upper':actual_upper,'inexact_bound':bound,'base_gap':str(delta),'positive_switches':ref['positive_switches'],'negative_switches':ref['negative_switches'],'near_kinks':ref['near_kinks'],'capacity_binding':int(np.sum(abs(s.C@xr[:s.n]-s.capnum/8)<1e-5)),'tiers_on_boundary':int(np.sum((xr[:s.n]+s.znum/32<1e-5)|(1-s.znum/32-xr[:s.n]<1e-5)))}
            rows.append(row);proof_records.append({'primitive':s.primitives(),'reference':ref['record'],'proposal':rr,'base_gap':str(delta)})
            if j==0:
                # Envelope finite differences perturb the linear resource reward,
                # holding acceptance, comparator, friction, and every other
                # primitive fixed. They do not round h to a context-grid value.
                a0,lam=s.coefficients(c);q=np.r_[-a0,lam*s.k];fd=[]
                for k in range(rank):
                    eps=1e-4;deltaq=np.r_[-eps*s.U[k],np.zeros(s.n)]
                    xp,_,_=s.full.solve(q+deltaq);xm,_,_=s.full.solve(q-deltaq)
                    vp=s.value(c,xp[:s.n])+eps*(s.U[k]@xp[:s.n]);vm=s.value(c,xm[:s.n])-eps*(s.U[k]@xm[:s.n]);fd.append((vp-vm)/(2*eps))
                row['gradient_fd_max_error']=float(np.max(abs(np.array(fd)-s.U@xr[:s.n])))
                assert row['gradient_fd_max_error']<3e-4
                if nodes==15:
                    H=np.diag(s.d)+s.U.T@s.U
                    def obj(w):
                        x=w[:s.n];return .5*x@H@x-a0@x+lam*s.k@w[s.n:],np.r_[H@x-a0,lam*s.k]
                    start=np.r_[np.zeros(s.n),abs(s.vnum/32)+.01]
                    res2=minimize(obj,start,jac=True,method='SLSQP',constraints=LinearConstraint(s.M.toarray(),s.lower,s.upper),options={'ftol':1e-11,'maxiter':2500})
                    if not res2.success:raise RuntimeError(('independent SLSQP check failed',res2.message))
                    err=abs(s.value(c,res2.x[:s.n])-s.value(c,xr[:s.n]));assert err<1e-7
                    independent.append({'method':'SciPy SLSQP, zero decision initialization','seed':seed,'dimension':2*s.n,'objective_difference':err,'iterations':int(res2.nit)})
        print('structural',seed,nodes,rank,'PASS',flush=True)
    OUT.mkdir(exist_ok=True);(OUT/'structural.json').write_text(json.dumps({'status':'PASS','instances':len(rows),'rows':rows,'independent_optimization':independent},indent=2)+'\n')
    (OUT/'structural_certificates.json').write_text(json.dumps(proof_records)+'\n')
if __name__=='__main__':run()
