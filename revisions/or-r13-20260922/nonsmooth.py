#!/usr/bin/env python3
"""R13 nonsmooth accepted control. Ordinary sources; no hidden services.
The numerical optimizers only propose primal/dual records. Fraction replay in
verify.py independently checks feasibility, reward, and arbitrary-tension gaps.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from fractions import Fraction as F
import json, time, platform, hashlib, sys
import numpy as np
import scipy
from scipy import sparse
from scipy.optimize import minimize, linprog, LinearConstraint
from scipy.linalg import qr
HERE=Path(__file__).resolve().parent
DEN=10**9

def q(v): return F(int(round(float(v)*DEN)),DEN)
def dump(path,obj):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

class Tree:
    """Scalar binary scenario tree. Tier transfers enforce exact acceptance."""
    def __init__(self,depth=4,seed=1301):
        self.depth=depth;self.seed=seed;self.N=2**depth-1;self.m=self.N-1
        self.pa=np.array([-1]+[(i-1)//2 for i in range(1,self.N)])
        self.wq=[F(9,20)**int(np.floor(np.log2(i+1))) for i in range(self.N)]
        self.cq=[w*F(8+(i%5),10) for i,w in enumerate(self.wq)]
        self.kq=self.wq.copy();self.w=np.array(list(map(float,self.wq)))
        self.c=np.array(list(map(float,self.cq)));self.k=self.w.copy()
        self.mass=float(sum(self.wq));self.z=np.full(self.N,.5)
        self.B=np.zeros((self.N,self.m));self.D=np.eye(self.N)
        for i in range(1,self.N):
            self.B[i,i-1]=-1;self.B[self.pa[i],i-1]=self.c[i]/self.c[self.pa[i]]
            self.D[i,self.pa[i]]=-1
        self.K=self.D@self.B
        # Real maintenance is convex. Linear resource offsets vary by context.
        self.Q=2*np.diag(self.w)+F(1,5).__float__()*self.D[1:].T@np.diag(self.w[1:])@self.D[1:]
        self.Qf=self.B.T@self.Q@self.B
        rng=np.random.default_rng(seed)
        forces=[]
        for j in range(3):
            v=[F(int(a),20)*w for a,w in zip(rng.integers(-14,15,self.N),self.wq)]
            avg=sum(v)/sum(self.wq);forces.append([a-avg*w for a,w in zip(v,self.wq)])
        self.gq=forces;self.G=np.array([[float(a) for a in v] for v in forces]).T
        # theta=(two cost-shock coordinates, strictly positive friction).
        # Offset is nonzero; balanced shocks keep the *reoptimized* static tier .5.
        self.af=np.column_stack((self.B.T@self.G[:,0],self.B.T@self.G[:,1],
                                  self.B.T@self.G[:,2],np.zeros(self.m)))
        self.L=np.vstack((-np.eye(self.m),self.B,-self.B))
        self.h=np.r_[np.zeros(self.m),np.full(2*self.N,.5)]
        # Explicit epigraph QP; initial static feasible for all parameters.
        self.J=np.block([[self.L,np.zeros((len(self.L),self.N))],
                         [self.K,-np.eye(self.N)],[-self.K,-np.eye(self.N)]])
        self.ub=np.r_[self.h,np.zeros(2*self.N)]
    def pars(self,theta):
        t=np.r_[1.,theta];return self.af@t,float(theta[2])
    def solve(self,theta,start=None):
        a,lam=self.pars(theta);n=self.m
        def obj(v):
            u=v[:n];return (.5*u@self.Qf@u-a@u+lam*self.k@v[n:],
                              np.r_[self.Qf@u-a,lam*self.k])
        v=np.zeros(n+self.N) if start is None else np.r_[start,np.abs(self.K@start)]
        st=time.perf_counter()
        res=minimize(obj,v,jac=True,method='SLSQP',constraints=LinearConstraint(self.J,-np.inf,self.ub),
                     options={'ftol':2e-12,'maxiter':700})
        if not res.success and np.max(self.J@res.x-self.ub)>2e-7:
            raise RuntimeError('QP feasibility failure: '+res.message)
        return res.x[:n],time.perf_counter()-st,int(res.nit),bool(res.success)
    def cell(self,theta,u):
        """Recover a dual basic solution; verify the resulting affine region.
        Zero-price active rows need not be included. Saturated zero-edge tensions
        become signed cells. This avoids assuming LICQ for every active row.
        """
        a,lam=self.pars(theta)
        for tol in (2e-5,2e-6,2e-4):
            active=np.where(self.h-self.L@u<tol)[0]
            zero=np.where(np.abs(self.K@u)<tol)[0]
            fixed=np.setdiff1d(np.arange(self.N),zero)
            signs=np.sign(self.K@u)
            C=np.vstack((self.L[active],self.K[zero]))
            d=np.r_[self.h[active],np.zeros(len(zero))]
            if len(C):
                _,R,piv=qr(C.T,pivoting=True,mode='economic')
                rank=int(np.sum(np.abs(np.diag(R))>1e-9));ids=np.sort(piv[:rank])
                CC=C[ids];dd=d[ids]
            else: CC=np.empty((0,self.m));dd=np.empty(0)
            kk=np.block([[self.Qf,CC.T],[CC,np.zeros((len(CC),len(CC)))]])
            try: uu=np.linalg.solve(kk,np.r_[a-self.K[fixed].T@(lam*self.k[fixed]*signs[fixed]),dd])[:self.m]
            except np.linalg.LinAlgError:continue
            Aeq=np.column_stack((self.L[active].T,self.K[zero].T))
            rhs=a-self.Qf@uu-self.K[fixed].T@(lam*self.k[fixed]*signs[fixed])
            bounds=[(0,None)]*len(active)+[(-lam*self.k[i],lam*self.k[i]) for i in zero]
            lp=linprog(np.r_[np.ones(len(active)),np.zeros(len(zero))],A_eq=Aeq,b_eq=rhs,
                       bounds=bounds,method='highs')
            if not lp.success:continue
            mu=np.zeros(len(self.L));mu[active]=lp.x[:len(active)]
            s=lam*self.k*signs;s[zero]=lp.x[len(active):]
            ai=np.where(mu>1e-8)[0]
            zi=np.where(np.abs(s)<lam*self.k-1e-8)[0]
            fi=np.setdiff1d(np.arange(self.N),zi)
            sg=np.sign(s);at_zero=sg==0;sg[at_zero]=np.sign(self.K@uu)[at_zero];sg[sg==0]=1
            C=np.vstack((self.L[ai],self.K[zi]));d=np.r_[self.h[ai],np.zeros(len(zi))]
            if len(C) and np.linalg.matrix_rank(C,tol=1e-9)<len(C):continue
            mat=np.block([[self.Qf,C.T],[C,np.zeros((len(C),len(C)))]])
            rhs=self.af.copy();rhs[:,3]-=self.K[fi].T@(self.k[fi]*sg[fi])
            rhs=np.vstack((rhs,np.column_stack((d,np.zeros((len(C),3))))))
            sol=np.linalg.solve(mat,rhs);U=sol[:self.m]
            MU=np.zeros((len(self.L),4));MU[ai]=sol[self.m:self.m+len(ai)]
            S=np.zeros((self.N,4));S[fi,3]=self.k[fi]*sg[fi];S[zi]=sol[self.m+len(ai):]
            # Every inequality has form R*[1,theta]>=0. All equalities hold by construction.
            R=np.vstack((np.column_stack((self.h,np.zeros((len(self.h),3))))-self.L@U,
                         MU[ai],np.column_stack((np.zeros((self.N,3)),self.k))-S,
                         np.column_stack((np.zeros((self.N,3)),self.k))+S,
                         sg[fi,None]*(self.K[fi]@U)))
            if np.min(R@np.r_[1.,theta]) < -2e-7:continue
            # Store only nontrivial inequalities for membership, preserving all for diagnostics.
            keep=np.linalg.norm(R,axis=1)>1e-9
            key=(tuple(ai.tolist()),tuple(zi.tolist()),tuple(sg[fi].astype(int).tolist()))
            return {'key':str(key),'U':U,'MU':MU,'S':S,'R':R[keep],
                    'active':ai,'fused':zi,'signed':fi,'signs':sg[fi]}
        raise RuntimeError('No verified affine face for training proposal')
    def critical_lp(self,theta):
        a,_=self.pars(theta);n=self.N
        # Variables (s,v,lambda). Keep B and D factored: O(N) nonzeros.
        obj=np.r_[np.zeros(2*n),1.]
        Aeq=sparse.hstack((sparse.csr_matrix(self.D.T),-sparse.eye(n),sparse.csr_matrix((n,1))))
        Aub=sparse.vstack((sparse.hstack((sparse.csr_matrix((self.m,n)),-sparse.csr_matrix(self.B.T),sparse.csr_matrix((self.m,1)))),
                           sparse.hstack((sparse.eye(n),sparse.csr_matrix((n,n)),-sparse.csr_matrix(self.k[:,None]))),
                           sparse.hstack((-sparse.eye(n),sparse.csr_matrix((n,n)),-sparse.csr_matrix(self.k[:,None])))))
        st=time.perf_counter();r=linprog(obj,A_ub=Aub,b_ub=np.r_[-a,np.zeros(2*n)],A_eq=Aeq,b_eq=np.zeros(n),
                                       bounds=[(None,None)]*(2*n)+[(0,None)],method='highs')
        if not r.success:raise RuntimeError(r.message)
        return float(r.x[-1]),time.perf_counter()-st,int(Aub.nnz+Aeq.nnz)
    def friction_bracket(self,theta,tolerance=2e-5,maxit=200000):
        """Accelerated box projection + certified separator/repair brackets.
        Stopping uses a bracket, not a residual or optimization success flag.
        """
        a,_=self.pars(theta)
        M=(self.K.T*self.k)/self.c[1:,None];b=a/self.c[1:]
        lip=np.linalg.norm(M,1)*np.linalg.norm(M,np.inf)
        def repair(t,lam):
            r=np.maximum(b-M@t,0);v=np.zeros(self.N)
            for i in range(1,self.N):v[i]=self.c[i]/self.c[self.pa[i]]*v[self.pa[i]]-self.c[i]*r[i-1]
            ds=v.copy()
            for i in range(self.N-1,0,-1):ds[self.pa[i]]+=ds[i]
            upper=lam+np.max(np.abs(ds)/self.k)
            d=r/self.c[1:];den=self.k@np.abs(self.K@d)
            lower=max(0.,a@d/den) if den>1e-18 else 0.
            return lower,upper
        lo,hi=repair(np.zeros(self.N),0.);count=0;outer=0
        st=time.perf_counter()
        while hi-lo>tolerance and count<maxit:
            lam=(hi+lo)/2;t=np.zeros(self.N);y=t.copy();acc=1.;outer+=1
            for j in range(maxit-count):
                rr=np.maximum(b-M@y,0);new=np.clip(y+M.T@rr/lip,-lam,lam)
                nxt=(1+np.sqrt(1+4*acc*acc))/2;y=new+(acc-1)/nxt*(new-t);t=new;acc=nxt;count+=1
                if j%20==0:
                    ll,hh=repair(t,lam);lo=max(lo,ll);hi=min(hi,hh)
                    if hi-lo<=tolerance or ll>lam+1e-12 or hh<lam+tolerance/4:break
        return {'lower':lo,'upper':hi,'iterations':count,'outer':outer,'seconds':time.perf_counter()-st,
                'attained':bool(hi-lo<=tolerance),'tolerance':tolerance}
    def audit(self,theta,u,mu,s):
        """Exact rational flow repair and arbitrary-tension certificate."""
        st=time.perf_counter();uq=[max(F(0),q(v)) for v in u]
        def tiers(uu):
            x=[F(1,2)]*self.N
            for i,v in enumerate(uu,1):x[i]-=v;x[self.pa[i]]+=self.cq[i]/self.cq[self.pa[i]]*v
            return x
        x=tiers(uq);scale=min([F(1)]+[F(1,2)/abs(v-F(1,2)) for v in x if abs(v-F(1,2))>F(1,2)])
        uq=[v*scale for v in uq];x=tiers(uq);th=list(map(q,theta));lam=th[2]
        muq=[max(F(0),q(v)) for v in mu]
        sq=[min(lam*k,max(-lam*k,q(v))) for k,v in zip(self.kq,s)]
        g=[self.gq[0][i]+th[0]*self.gq[1][i]+th[1]*self.gq[2][i]-2*self.wq[i]*(x[i]-F(1,2)) for i in range(self.N)]
        diff=[x[0]-F(1,2)]+[x[i]-x[self.pa[i]] for i in range(1,self.N)]
        smooth=sum((self.wq[i]*(x[i]-F(1,2))**2 for i in range(self.N)),F(0))
        for i in range(1,self.N):
            v=F(1,5)*self.wq[i]*diff[i];g[i]-=v;g[self.pa[i]]+=v
            smooth+=F(1,10)*self.wq[i]*diff[i]**2
        dt=sq.copy()
        for i in range(1,self.N):dt[self.pa[i]]-=sq[i]
        up=muq[self.m:self.m+self.N];low=muq[self.m+self.N:]
        acc=[F(0)]*self.N
        for i in range(1,self.N):acc[i]=acc[self.pa[i]]+muq[i-1]/self.cq[i]
        pre=[g[i]-dt[i]-up[i]+low[i]-self.cq[i]*acc[i] for i in range(self.N)]
        nu=sum((pre[i]*self.cq[i]/self.wq[i] for i in range(self.N)),F(0))/sum((self.cq[i]**2/self.wq[i] for i in range(self.N)),F(0))
        e=[pre[i]-nu*self.cq[i] for i in range(self.N)]
        quad=sum((v*v/(4*w) for v,w in zip(e,self.wq)),F(0))
        slack=sum((m*v for m,v in zip(muq[:self.m],uq)),F(0))+sum((up[i]*(1-x[i])+low[i]*x[i] for i in range(self.N)),F(0))
        fenchel=sum((lam*self.kq[i]*abs(diff[i])-sq[i]*diff[i] for i in range(self.N)),F(0))
        linear=sum(((self.gq[0][i]+th[0]*self.gq[1][i]+th[1]*self.gq[2][i])*(x[i]-F(1,2)) for i in range(self.N)),F(0))
        gain=linear-smooth-sum((lam*k*abs(d) for k,d in zip(self.kq,diff)),F(0))
        cert=quad+slack+fenchel
        assert min(x)>=0 and max(x)<=1 and min(uq+[F(0)])>=0 and cert>=0
        return {'theta':list(map(str,th)),'flows':list(map(str,uq)),'multipliers':list(map(str,muq)),
                'tensions':list(map(str,sq)),'root_price':str(nu),'gain_fraction':str(gain),'bound_fraction':str(cert),
                'quadratic':str(quad),'acceptance_leakage':str(slack),'switching_leakage':str(fenchel),
                'gain':float(gain)/self.mass,'bound':float(cert)/self.mass,'repair_scale':float(scale),
                'seconds':time.perf_counter()-st}

def eval_cell(cell,theta):
    v=np.r_[1.,theta]
    return cell['U']@v,cell['MU']@v,cell['S']@v

def contains(cell,theta,tol=2e-9):return bool(np.min(cell['R']@np.r_[1.,theta],initial=0.)>=-tol)

if __name__=='__main__':
    tr=Tree(4)
    for t in ([.2,-.4,.02],[-.8,.4,.1],[.9,-.7,.05]):
        u,tt,it,ok=tr.solve(t);ce=tr.cell(t,u);uu,mu,s=eval_cell(ce,t);au=tr.audit(t,uu,mu,s)
        print(t,it,len(ce['active']),len(ce['fused']),au['gain'],au['bound'],contains(ce,t))
    print(tr.critical_lp([.2,-.4,.02]));print(tr.friction_bracket([.2,-.4,.02]))
