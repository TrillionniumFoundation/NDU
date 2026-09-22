#!/usr/bin/env python3
"""Accepted star control: exact structure, scalar algorithms, auditable policies.
Numerical routines propose decisions. verify.py recomputes rational feasibility,
profit and Fenchel upper bounds independently, without importing this module.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from fractions import Fraction as F
import numpy as np
from scipy.optimize import brentq, minimize, LinearConstraint
DEN=10**9

class Star:
    def __init__(self, leaves: int=127, seed: int=14001):
        if leaves<1: raise ValueError('At least one continuation is required')
        self.n=leaves; self.seed=seed; self.w=F(9,10*leaves)
        self.q0=2.;self.b0=.5;self.b=np.full(leaves,.5)
        self.q=np.full(leaves,2*float(self.w));self.mass=1.9
        rng=np.random.default_rng(seed)
        self.tariff=rng.integers(8,13,leaves)
        self.v0=rng.integers(-28,5,leaves)  # divided by 20: heterogeneous offsets
        self.v1=rng.integers(-20,21,leaves)
        self.rho=9*self.tariff.astype(float)/(80*leaves)
        # Balanced primitive forcing: sum(g)=0, so static is reoptimized at .5.
        g00=-float(self.w)*self.v0.sum()/20
        g01=-float(self.w)*self.v1.sum()/20
        self.a0=self.rho*g00-float(self.w)*self.v0/20
        self.a1=self.rho*g01-float(self.w)*self.v1/20
        self.t=float(self.w)+1.9*self.rho
        self.R=float(np.sum(self.rho**2/self.q))
        self.kappa=self.R/(1+self.q0*self.R)
    def primitives(self):
        return {'leaves':self.n,'seed':self.seed,'tariff_integers':self.tariff.tolist(),
                'offset0_integers':self.v0.tolist(),'offset1_integers':self.v1.tolist(),
                'leaf_weight':str(self.w),'root_curvature':'2','leaf_upper':'1/2','root_upper':'1/2'}
    def d(self,theta):
        h,alpha,lam=np.asarray(theta,dtype=float)
        if lam<0:raise ValueError('Nonnegative switching friction required')
        return self.a0+alpha*self.a1+h*self.rho-lam*self.t
    def critical(self,theta):
        h,alpha,_=theta
        return max(0.,float(np.max((self.a0+alpha*self.a1+h*self.rho)/self.t)))
    def response(self,d,tau):
        y=np.clip((d-self.rho*tau)/self.q,0,self.b)
        return y,float(self.rho@y)
    def rootfun(self,d,tau):
        return self.response(d,tau)[1]-min(self.b0,max(0.,tau/self.q0))
    def solve(self,theta,method='brent',initial=None):
        d=self.d(theta);hi=max(0.,float(np.max(d/self.rho)))
        if hi==0:return np.zeros(self.n),0.,{'evaluations':1,'iterations':0,'method':method}
        count=0
        def f(t):
            nonlocal count
            count+=1;return self.rootfun(d,t)
        if method=='brent':
            tau,res=brentq(f,0,hi,xtol=5e-14,rtol=1e-14,full_output=True)
            its=res.iterations
        elif method=='bisect':
            lo=0.
            for its in range(1,90):
                tau=(lo+hi)/2;v=f(tau)
                if abs(v)<2e-14:break
                if v>0:lo=tau
                else:hi=tau
        elif method=='newton':
            lo=0.;tau=np.clip(self.q0*self.b0/2 if initial is None else initial,lo,hi)
            for its in range(1,100):
                v=f(tau)
                if abs(v)<2e-14:break
                if v>0:lo=tau
                else:hi=tau
                raw=(d-self.rho*tau)/self.q
                slope=-float(np.sum(self.rho[(raw>0)&(raw<self.b)]**2/self.q[(raw>0)&(raw<self.b)]))
                if tau<self.q0*self.b0:slope-=1/self.q0
                nxt=tau-v/slope if slope<0 else (lo+hi)/2
                tau=nxt if lo<nxt<hi else (lo+hi)/2
            else:raise RuntimeError('Safeguarded scalar Newton did not converge')
        elif method=='sort':
            # S(t)=A-B*t between the 2n leaf breakpoints and the root breakpoint.
            enter=(d-self.q*self.b)/self.rho;leave=d/self.rho
            y0,S=self.response(d,0.);active=(d>0)&(d<self.q*self.b)
            B=float(np.sum(self.rho[active]**2/self.q[active]));A=S
            # Events at zero already incorporated in the right derivative.
            active=(d>0)&(d<=self.q*self.b)
            B=float(np.sum(self.rho[active]**2/self.q[active]));A=S
            events=[]
            for i in range(self.n):
                if enter[i]>0:events.append((float(enter[i]),float(self.rho[i]**2/self.q[i])))
                if leave[i]>0:events.append((float(leave[i]),-float(self.rho[i]**2/self.q[i])))
            events.append((self.q0*self.b0,0.));events.append((hi,0.));events.sort()
            left=0.;idx=0;its=0
            while idx<len(events):
                right=events[idx][0];its+=1
                if left<self.q0*self.b0:
                    candidate=A/(B+1/self.q0)
                elif B>1e-14:candidate=(A-self.b0)/B
                else:candidate=left if abs(A-self.b0)<1e-12 else np.inf
                if left-1e-11<=candidate<=right+1e-11:
                    tau=max(left,min(right,candidate));break
                while idx<len(events) and events[idx][0]==right:
                    delta=events[idx][1];B+=delta;A+=right*delta;idx+=1
                left=right
            else:tau=hi
            count=its
            if abs(self.rootfun(d,tau))>1e-8:raise RuntimeError('Breakpoint scan inconsistency')
        else:raise ValueError(method)
        y,v=self.response(d,float(tau))
        return y,float(tau),{'evaluations':int(count),'iterations':int(its),'method':method}
    def surrogate(self,theta,eta):
        """Feasible response to a predicted coupling price, not a predicted face."""
        d=self.d(theta);eta=float(np.clip(eta,0,self.q0*self.b0))
        y,v=self.response(d,eta);projection=False;tau=eta
        if v>self.b0:
            projection=True
            hi=max(eta,float(np.max(d/self.rho)))
            tau=brentq(lambda t:self.response(d,t)[1]-self.b0,eta,hi,xtol=5e-14,rtol=1e-14)
            y,v=self.response(d,tau)
        return y,float(tau),eta,projection
    def value(self,theta,y):
        v=float(self.rho@y)
        return float(self.d(theta)@y-.5*np.dot(self.q,y*y)-.5*self.q0*v*v)
    def targets(self,theta):
        y,tau,meta=self.solve(theta,'newton');v=float(self.rho@y)
        return self.value(theta,y),v,2*v
    def dense(self,theta):
        d=self.d(theta)
        def f(y):
            v=self.rho@y
            return (.5*np.dot(self.q,y*y)+.5*self.q0*v*v-d@y,self.q*y+(self.q0*v)*self.rho-d)
        res=minimize(f,np.zeros(self.n),jac=True,method='SLSQP',bounds=[(0,.5)]*self.n,
                     constraints=LinearConstraint(self.rho[None,:],-np.inf,self.b0),
                     options={'ftol':2e-13,'maxiter':800})
        if not res.success:raise RuntimeError(res.message)
        return res.x
    def audit(self,theta,y,tau):
        """Exact rational primal/dual certificate, including rounding losses."""
        n=self.n;w=self.w;rho=[F(9*int(k),80*n) for k in self.tariff]
        th=[F(int(round(float(t)*1000)),1000) for t in theta]
        g0=-w*sum(map(int,self.v0))/20;g1=-w*sum(map(int,self.v1))/20
        d=[r*g0-w*int(z)/20+th[1]*(r*g1-w*int(z1)/20)+th[0]*r-th[2]*(w+F(19,10)*r)
           for r,z,z1 in zip(rho,self.v0,self.v1)]
        yy=[F(max(0,min(DEN//2,int(np.floor(float(v)*DEN)))),DEN) for v in y]
        root=sum((r*v for r,v in zip(rho,yy)),F(0))
        scale=min(F(1),F(1,2)/root) if root else F(1)
        yy=[v*scale for v in yy];root*=scale
        tt=F(int(round(float(tau)*DEN)),DEN)
        def conj(s,q,b):
            v=min(b,max(F(0),s/q));return s*v-q*v*v/2
        upper=conj(tt,F(2),F(1,2))
        leaf=[]
        for di,ri in zip(d,rho):leaf.append(conj(di-ri*tt,2*w,F(1,2)))
        upper+=sum(leaf,F(0))
        gain=sum((di*yi-w*yi*yi for di,yi in zip(d,yy)),F(0))-root*root
        gap=upper-gain
        assert 0<=root<=F(1,2) and all(0<=v<=F(1,2) for v in yy) and gap>=0
        return {'theta':list(map(str,th)),'flows':list(map(str,yy)),'total_price':str(tt),
                'root_transfer':str(root),'gain_fraction':str(gain),'dual_upper_fraction':str(upper),
                'gap_fraction':str(gap),'gain':float(gain/F(19,10)),
                'gap':float(gap/F(19,10)),'scale':str(scale)}
