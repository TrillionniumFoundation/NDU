"""R15 accepted multistage instances and exact rational deployment audits.
The numerical solver only proposes. Integer/rational arithmetic independently
checks acceptance, boundaries, switching, resource capacities and Fenchel gaps.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import lcm
from time import perf_counter
import numpy as np
from scipy import sparse
from qp import QP
from exact import audit_exact,prepare

class Tree:
    def __init__(self,nodes=63,services=2,rank=6,seed=15001):
        if nodes<3 or services<1 or rank<1:raise ValueError('Invalid dimensions')
        self.nodes=nodes;self.services=services;self.rank=rank;self.seed=seed
        self.n=nodes*services;n=self.n;rng=np.random.default_rng(seed)
        self.parent=np.array([-1]+[(j-1)//2 for j in range(1,nodes)])
        depth=np.array([(j+1).bit_length()-1 for j in range(nodes)])
        self.cnode=rng.integers(8,13,(nodes,services))*2**(depth.max()-depth[:,None])
        self.c=self.cnode.ravel()
        self.znum=rng.integers(13,20,n) # outside tier, denominator 32
        self.qnum=rng.integers(8,25,n);self.d=self.qnum/16
        self.bnum=rng.integers(-8,9,n);self.Unum=rng.integers(-4,5,(rank,n));self.U=self.Unum/32
        self.knum=rng.integers(4,9,n);self.k=self.knum/8
        B=np.eye(n,dtype=np.int64)
        for j in range(1,nodes):
            for a in range(services):B[j*services+a,self.parent[j]*services+a]=-1
        self.B=B;self.vnum=B@self.znum;self.vnum[:services]-=16
        acc=[];eq=[]
        for j in range(nodes):
            sub=[]
            for k in range(j,nodes):
                t=k
                while t>j:t=self.parent[t]
                if t==j:sub.append(k)
            for a in range(services):
                row=np.zeros(n,dtype=np.int64);inds=np.array(sub)*services+a;row[inds]=self.c[inds]
                (eq if j==0 else acc).append(row)
        self.Aacc=np.array(acc);self.E=np.array(eq)
        self.C=rng.integers(0,5,(4,n));self.capnum=rng.integers(1,5,4) # cap denominator 8
        self.Aineq=np.vstack([self.Aacc,self.C]);self.bineq=np.r_[np.zeros(len(acc)),self.capnum/8]
        self.Aeq=self.E
        # Exact transfer map, nonnegative y => every continuation accepted.
        self.Lden=1
        for j in range(1,nodes):
            for a in range(services):self.Lden=lcm(self.Lden,F(int(self.cnode[j,a]),int(self.cnode[self.parent[j],a])).denominator)
        self.Lnum=np.zeros((n,(nodes-1)*services),dtype=np.int64)
        for j in range(1,nodes):
            for a in range(services):
                col=(j-1)*services+a;self.Lnum[j*services+a,col]=-self.Lden
                self.Lnum[self.parent[j]*services+a,col]=int(F(int(self.cnode[j,a]),int(self.cnode[self.parent[j],a]))*self.Lden)
        assert np.all(self.E@self.Lnum==0)
        # Rows: x boxes; continuation/cap inequalities; root equality; two switching epigraphs.
        I=sparse.eye(n,format='csc');Z=sparse.csc_matrix((n,n));A=sparse.csc_matrix(self.Aineq);E=sparse.csc_matrix(self.E)
        self.row_box=slice(0,n);self.row_ineq=slice(n,n+len(self.Aineq));start=self.row_ineq.stop
        self.row_eq=slice(start,start+services);start+=services
        self.row_pos=slice(start,start+n);self.row_neg=slice(start+n,start+2*n)
        self.M=sparse.vstack([sparse.hstack([I,Z]),sparse.hstack([A,sparse.csc_matrix((A.shape[0],n))]),sparse.hstack([E,sparse.csc_matrix((services,n))]),sparse.hstack([sparse.csc_matrix(B),-I]),sparse.hstack([-sparse.csc_matrix(B),-I])],format='csc')
        self.lower=np.r_[-self.znum/32,np.full(len(self.Aineq),-np.inf),np.zeros(services),np.full(2*n,-np.inf)]
        self.upper=np.r_[(32-self.znum)/32,self.bineq,np.zeros(services),-self.vnum/32,self.vnum/32]
        P0=sparse.diags(np.r_[self.d,np.zeros(n)],format='csc')
        P=sparse.block_diag([sparse.csc_matrix(np.diag(self.d)+self.U.T@self.U),sparse.csc_matrix((n,n))],format='csc')
        t=perf_counter();self.base=QP(P0,self.M,self.lower,self.upper);self.base_setup=perf_counter()-t
        t=perf_counter();self.full=QP(P,self.M,self.lower,self.upper);self.full_setup=perf_counter()-t
        t=perf_counter();self.previous_full=QP(P,self.M,self.lower,self.upper);self.previous_setup=perf_counter()-t
        self.H=np.diag(self.d)+self.U.T@self.U
        self.K=self.U@np.linalg.solve(self.H,self.U.T)
        self.Lip=float(np.linalg.eigvalsh((self.U/self.d)@self.U.T)[-1])
        self.p=self.primitives();prepare(self.p)
    def primitives(self):
        return {k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in vars(self).items() if k in ['nodes','services','rank','seed','parent','c','znum','qnum','bnum','Unum','knum','B','vnum','Aacc','E','C','capnum','Lnum','Lden']}
    def coefficients(self,context):
        h=np.asarray(context[:self.rank],dtype=int);lam=int(context[-1]);return (16*self.bnum+self.Unum.T@h)/512,lam/64
    def solve(self,context,price=None,previous=False,warm=None):
        b,lam=self.coefficients(context);q=np.r_[-b if price is None else -b+self.U.T@price,lam*self.k]
        return (self.full if price is None else self.base).solve(q,previous=previous,warm=warm)
    def solve_previous(self,context):
        b,lam=self.coefficients(context)
        return self.previous_full.solve(np.r_[-b,lam*self.k],previous=True)
    def value(self,context,x):
        b,lam=self.coefficients(context)
        return float(b@x-.5*np.dot(self.d*x,x)-.5*np.sum((self.U@x)**2)-lam*np.dot(self.k,np.abs(self.B@x+self.vnum/32)-np.abs(self.vnum/32)))
    def repair(self,raw):
        n=self.n;sv=self.services;raw=np.asarray(raw[:n]);sub=(self.c*raw).reshape(self.nodes,sv).copy()
        for j in range(self.nodes-1,0,-1):sub[self.parent[j]]+=sub[j]
        y=np.maximum(0.,-sub[1:]/self.cnode[1:]).ravel()
        yn=np.floor(y*10**8).astype(np.int64);xd=int(self.Lden*10**8)
        xn=self.Lnum.astype(object)@yn.astype(object)
        # A radial rational contraction preserves all continuation/equality rows.
        factor=F(1)
        for i,xi in enumerate(xn):
            if xi>0:factor=min(factor,F(int((32-self.znum[i])*xd),int(32*xi)))
            elif xi<0:factor=min(factor,F(int(self.znum[i]*xd),int(-32*xi)))
        for ci,cap in zip(self.C,self.capnum):
            v=sum(int(a)*int(x) for a,x in zip(ci,xn))
            if v>0:factor=min(factor,F(int(cap*xd),8*v))
        if factor<1:
            # Exact scaling, rather than independently rounding each repaired tier.
            xn=np.array([int(x)*factor.numerator for x in xn],dtype=object);xd*=factor.denominator
        return [int(x) for x in xn],xd,bool(factor<1)
    def audit(self,context,raw,dual,price=None,record=False):
        t=perf_counter();xn,xd,repaired=self.repair(raw);pnorm=10**9;n=self.n
        d=np.asarray(dual);mu=np.maximum(0,np.rint(d[self.row_ineq]*pnorm)).astype(np.int64)
        nu=np.rint(d[self.row_eq]*pnorm).astype(np.int64)
        sn=np.rint((d[self.row_pos]-d[self.row_neg])*pnorm).astype(np.int64)
        lam=int(context[-1]);bounds=pnorm*lam*self.knum//512;sn=np.clip(sn,-bounds,bounds)
        price=self.U@np.asarray(raw[:n]) if price is None else np.asarray(price)
        pn=np.rint(price*pnorm).astype(np.int64)
        out=audit_exact(self.p,context,xn,xd,pn.tolist(),sn.tolist(),mu.tolist(),nu.tolist(),pnorm)
        out['repaired']=repaired;out['audit_seconds']=perf_counter()-t
        if record:out['record']={'context':list(map(int,context)),'x_num':list(map(str,xn)),'x_den':str(xd),'price_num':pn.tolist(),'switch_num':sn.tolist(),'ineq_num':mu.tolist(),'equality_num':nu.tolist(),'dual_den':pnorm,'gain':out['gain_exact'],'upper':out['upper_exact']}
        return out


def contexts(seed,count,rank=6):
    rng=np.random.default_rng(seed);return np.c_[rng.integers(-16,17,(count,rank)),rng.integers(2,33,count)]
