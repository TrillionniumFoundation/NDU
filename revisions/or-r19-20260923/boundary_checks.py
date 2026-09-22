#!/usr/bin/env python3
"""Deliberate geometry checks, not learned deployments or calibrated operations."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'; os.environ['OMP_NUM_THREADS']='1'
import sys,json,gzip
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'or-r16-20260922'))
import numpy as np
from scipy import sparse
from scipy.optimize import minimize,LinearConstraint
from multiresource import Tree,contexts
from qp import QP
from exact import prepare,audit_exact
OUT=ROOT/'results'
def configure(seed,nodes,rank,stratum):
    s=Tree(nodes,2,rank,seed)
    # Changes are explicit primitive modifications; every resulting instance is retained.
    if stratum in ['binding-capacity','tier-boundary']:
        s.C[:]=0; s.C[0,:2]=1
        s.capnum[:]=32 if stratum=='tier-boundary' else 1
        s.bnum[:2]=128
    if stratum=='switching-kinks':s.knum[:]*=8; s.k=s.knum/8
    s.Aineq=np.vstack([s.Aacc,s.C]);s.bineq=np.r_[np.zeros(len(s.Aacc)),s.capnum/8]
    n=s.n;I=sparse.eye(n,format='csc');Z=sparse.csc_matrix((n,n));A=sparse.csc_matrix(s.Aineq);E=sparse.csc_matrix(s.E)
    s.M=sparse.vstack([sparse.hstack([I,Z]),sparse.hstack([A,sparse.csc_matrix((len(s.Aineq),n))]),sparse.hstack([E,sparse.csc_matrix((s.services,n))]),sparse.hstack([sparse.csc_matrix(s.B),-I]),sparse.hstack([-sparse.csc_matrix(s.B),-I])],format='csc')
    s.upper=np.r_[(32-s.znum)/32,s.bineq,np.zeros(s.services),-s.vnum/32,s.vnum/32]
    for obj in [s.base,s.full,s.previous_full]:obj.close()
    s.base=QP(sparse.diags(np.r_[s.d,np.zeros(n)],format='csc'),s.M,s.lower,s.upper)
    full=sparse.block_diag([sparse.csc_matrix(s.H),sparse.csc_matrix((n,n))],format='csc')
    s.full=QP(full,s.M,s.lower,s.upper);s.previous_full=QP(full,s.M,s.lower,s.upper)
    s.p=s.primitives();prepare(s.p)
    return s

def run():
    OUT.mkdir(exist_ok=True);rows=[];records=[];independent=[]
    for si,stratum in enumerate(['heterogeneous','binding-capacity','tier-boundary','switching-kinks']):
        for k,seed in enumerate(range(19001,19005)):
            nodes=[15,31,15,31][k];rank=[2,4,4,2][k]
            s=configure(seed,nodes,rank,stratum);rng=np.random.default_rng(seed+1000)
            Kh=s.U@np.linalg.solve(.5*np.diag(s.d)+s.U.T@s.U,s.U.T)
            for j,c in enumerate(contexts(seed+500,4,rank)):
                xr,dr,it=s.solve(c); ref=s.audit(c,xr,dr,record=True)
                eta=s.U@xr[:s.n]+rng.normal(0,.3,rank)
                xb,db,ib=s.solve(c,price=eta); a=s.audit(c,xb,db,price=eta,record=True); rr=a['record']
                ex=[F(int(z),rr['dual_den'])-sum((F(int(u)*int(x),32*int(rr['x_den'])) for u,x in zip(row,rr['x_num'])),F(0)) for row,z in zip(s.Unum,rr['price_num'])]
                delta=F(rr['upper'])-F(a['raw_gain_exact'])-sum((v*v/2 for v in ex),F(0));assert delta>=0
                res=np.array(list(map(float,ex)));bound=2*float(delta)+.5*res@Kh@res
                ru=max(0.,ref['gain']+ref['gap']-a['raw_gain'])
                assert ru<=bound+ref['gap']+1e-9,(stratum,seed,j,ru,bound)
                row={'stratum':stratum,'seed':seed,'nodes':nodes,'rank':rank,'context':j,'gain':ref['gain'],'reference_gap':ref['gap'],'regret_upper':ru,'inexact_bound':float(bound),'base_gap':str(delta),'binding_capacities':int(np.sum(abs(s.C@xr[:s.n]-s.capnum/8)<1e-5)),'boundary_tiers':int(np.sum((xr[:s.n]+s.znum/32<1e-5)|(1-s.znum/32-xr[:s.n]<1e-5))),'near_kinks':ref['near_kinks'],'positive_switches':ref['positive_switches'],'negative_switches':ref['negative_switches'],'implemented_repair':a['repaired']}
                if stratum=='binding-capacity':assert row['binding_capacities']>=1
                if stratum=='tier-boundary':assert row['boundary_tiers']>=1
                if stratum=='switching-kinks':assert row['near_kinks']>=1
                if j==0:
                    b,lam=s.coefficients(c);q=np.r_[-b,lam*s.k];fd=[]
                    for r in range(rank):
                        e=1e-4;dq=np.r_[-e*s.U[r],np.zeros(s.n)]
                        xp,_,_=s.full.solve(q+dq);xm,_,_=s.full.solve(q-dq)
                        fd.append((s.value(c,xp[:s.n])+e*s.U[r]@xp[:s.n]-s.value(c,xm[:s.n])+e*s.U[r]@xm[:s.n])/(2*e))
                    row['gradient_fd_error']=float(max(abs(np.array(fd)-s.U@xr[:s.n])))
                    assert row['gradient_fd_error']<5e-4,row
                if stratum=='binding-capacity' and k==0 and j==0:
                    b,lam=s.coefficients(c)
                    def obj(w):
                        x=w[:s.n];return .5*x@s.H@x-b@x+lam*s.k@w[s.n:],np.r_[s.H@x-b,lam*s.k]
                    sol=minimize(obj,np.r_[np.zeros(s.n),abs(s.vnum/32)+.01],jac=True,method='SLSQP',constraints=LinearConstraint(s.M.toarray(),s.lower,s.upper),options={'ftol':1e-11,'maxiter':3000})
                    assert sol.success,sol.message
                    err=abs(s.value(c,sol.x[:s.n])-s.value(c,xr[:s.n]));assert err<2e-7
                    independent.append({'method':'SLSQP from outside protocol','objective_difference':err,'iterations':int(sol.nit)})
                rows.append(row);records.append({'primitive':s.primitives(),'reference':ref['record'],'proposal':rr,'base_gap':str(delta)})
            print(stratum,seed,'PASS',flush=True)
    replay=0
    for rec in records:
        for label in ['reference','proposal']:
            r=rec[label];a=audit_exact(rec['primitive'],r['context'],r['x_num'],int(r['x_den']),r['price_num'],r['switch_num'],r['ineq_num'],r['equality_num'],r['dual_den'])
            assert a['upper_exact']==r['upper'];assert a['gain_exact']==r['gain'];replay+=1
    (OUT/'boundary_checks.json').write_text(json.dumps({'status':'PASS','instances':len(rows),'rational_replays':replay,'rows':rows,'independent_solver':independent},indent=2)+'\n')
    with (OUT/'boundary_certificates.json.gz').open('wb') as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as g:g.write(json.dumps(records).encode())
if __name__=='__main__':run()
