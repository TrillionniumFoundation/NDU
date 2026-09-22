"""R21 fixed-primal certificate polishing and structured classical comparators.
All proposals are numerical; only the inherited independent rational verifier
licenses deployment. No historical source or frozen model is modified.
"""
from __future__ import annotations
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import sys, json
from pathlib import Path
from time import perf_counter
from fractions import Fraction as F
import numpy as np
from scipy import sparse
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'or-r16-20260922'
sys.path.insert(0,str(OLD))
from multiresource import Tree as OriginalTree, contexts
from qp import QP
from surrogates import Features, Surrogate, RBF
from certificate import audit_exact, decompose

class Tree(OriginalTree):
    """Identical R16 model, with optional capacity-count/curvature stress axes."""
    def __init__(self,nodes=63,services=2,rank=6,seed=15001,capacities=4,curvature=1):
        super().__init__(nodes,services,rank,seed)
        if capacities < 1 or curvature < 1: raise ValueError('Invalid stress axis')
        self.capacities=capacities; self.curvature=curvature
        if capacities!=4 or curvature!=1:
            rng=np.random.default_rng(seed+210000)
            self.C=rng.integers(0,5,(capacities,self.n))
            self.capnum=rng.integers(1,5,capacities)
            # Heterogeneous curvature, rather than uniformly rescaling the problem.
            self.qnum=self.qnum*np.where(np.arange(self.n)%2,curvature,1)
            self.d=self.qnum/16
            self._rebuild()
    def _rebuild(self):
        n=self.n; sv=self.services
        self.Aineq=np.vstack([self.Aacc,self.C])
        self.bineq=np.r_[np.zeros(len(self.Aacc)),self.capnum/8]
        I=sparse.eye(n,format='csc'); Z=sparse.csc_matrix((n,n))
        A=sparse.csc_matrix(self.Aineq); E=sparse.csc_matrix(self.E)
        self.row_ineq=slice(n,n+len(self.Aineq)); start=self.row_ineq.stop
        self.row_eq=slice(start,start+sv); start+=sv
        self.row_pos=slice(start,start+n); self.row_neg=slice(start+n,start+2*n)
        self.M=sparse.vstack([sparse.hstack([I,Z]),sparse.hstack([A,sparse.csc_matrix((A.shape[0],n))]),sparse.hstack([E,sparse.csc_matrix((sv,n))]),sparse.hstack([sparse.csc_matrix(self.B),-I]),sparse.hstack([-sparse.csc_matrix(self.B),-I])],format='csc')
        self.lower=np.r_[-self.znum/32,np.full(len(self.Aineq),-np.inf),np.zeros(sv),np.full(2*n,-np.inf)]
        self.upper=np.r_[(32-self.znum)/32,self.bineq,np.zeros(sv),-self.vnum/32,self.vnum/32]
        self.H=np.diag(self.d)+self.U.T@self.U
        P=sparse.block_diag([sparse.csc_matrix(self.H),sparse.csc_matrix((n,n))],format='csc')
        P0=sparse.diags(np.r_[self.d,np.zeros(n)],format='csc')
        self.base.close(); self.full.close(); self.previous_full.close()
        self.base=QP(P0,self.M,self.lower,self.upper)
        self.full=QP(P,self.M,self.lower,self.upper)
        self.previous_full=QP(P,self.M,self.lower,self.upper)
        self.K=self.U@np.linalg.solve(self.H,self.U.T)
        self.Lip=float(np.linalg.eigvalsh((self.U/self.d)@self.U.T)[-1])
        self.p=self.primitives()
    def audit(self,context,raw,dual,price=None,record=False):
        t=perf_counter(); xn,xd,repaired=self.repair(raw); den=10**9
        dual=np.asarray(dual)
        mu=np.maximum(0,np.rint(dual[self.row_ineq]*den)).astype(np.int64)
        nu=np.rint(dual[self.row_eq]*den).astype(np.int64)
        sn=np.rint((dual[self.row_pos]-dual[self.row_neg])*den).astype(np.int64)
        bound=den*int(context[-1])*self.knum//512
        sn=np.clip(sn,-bound,bound)
        pp=self.U@np.asarray(raw[:self.n]) if price is None else np.asarray(price)
        pn=np.rint(pp*den).astype(np.int64)
        rec={'context':list(map(int,context)),'x_num':list(map(str,xn)),'x_den':str(xd),'price_num':pn.tolist(),'switch_num':sn.tolist(),'ineq_num':mu.tolist(),'equality_num':nu.tolist(),'dual_den':den}
        a=check(self,rec); a['repaired']=repaired
        if record: a['record']=rec
        a['audit_seconds']=perf_counter()-t
        return a

def check(s,rec):
    return audit_exact(s.p,rec['context'],rec['x_num'],rec['x_den'],rec['price_num'],rec['switch_num'],rec['ineq_num'],rec['equality_num'],rec['dual_den'])

class Lifted:
    """OSQP on (x,t,u) with u=Ux: no dense U.T@U in its quadratic matrix.
    The resource equality multiplier carries -u, i.e. the coupling price.
    Both the primal state and all dual prices are retained for continuation.
    """
    def __init__(self,s,eps=1e-5,extra_equalities=None):
        self.s=s; n=s.n; r=s.rank
        P=sparse.diags(np.r_[s.d,np.zeros(n),np.ones(r)],format='csc')
        A=sparse.hstack([s.M,sparse.csc_matrix((s.M.shape[0],r))],format='csc')
        coupling=sparse.hstack([-sparse.csc_matrix(s.U),sparse.csc_matrix((r,n)),sparse.eye(r)],format='csc')
        self.price_rows=slice(A.shape[0],A.shape[0]+r)
        A=sparse.vstack([A,coupling],format='csc')
        lo=np.r_[s.lower,np.zeros(r)]; hi=np.r_[s.upper,np.zeros(r)]
        self.extra=extra_equalities
        if extra_equalities is not None:
            ee=sparse.csc_matrix(extra_equalities)
            A=sparse.vstack([A,sparse.hstack([ee,sparse.csc_matrix((ee.shape[0],n+r))])],format='csc')
            lo=np.r_[lo,np.zeros(ee.shape[0])]; hi=np.r_[hi,np.zeros(ee.shape[0])]
        t=perf_counter(); self.qp=QP(P,A,lo,hi,eps=eps); self.setup=perf_counter()-t
        self.P_nnz=P.nnz; self.A_nnz=A.nnz; self.last=None
    def solve(self,c,previous=False):
        s=self.s; b,lam=s.coefficients(c)
        x,d,it=self.qp.solve(np.r_[-b,lam*s.k,np.zeros(s.rank)],previous=previous)
        self.last=(x,d)
        return x[:2*s.n],d[:s.M.shape[0]],it,-d[self.price_rows]

class Polisher:
    """Monotone p/nu polishing at fixed implemented primal, tensions and mu.
    Clipped conjugates define a convex piecewise quadratic. Semismooth Newton
    proposals use Armijo damping. Exact outward bounds decide whether to keep
    a candidate; the original valid certificate is always available.
    """
    def __init__(self,s):
        self.s=s
        self.es=np.sqrt(np.sum(s.E*s.E/s.d,axis=1))
        self.V=np.vstack([s.U,s.E/self.es[:,None]])
        self.diag=np.r_[np.ones(s.rank),np.zeros(s.services)]
    def polish(self,rec,max_steps=12,initial=None):
        t=perf_counter(); s=self.s; r=s.rank; den=rec['dual_den']
        b,lam=s.coefficients(rec['context'])
        c=b-s.B.T@(np.array(rec['switch_num'])/den)-s.Aineq.T@(np.array(rec['ineq_num'])/den)
        w=np.r_[np.array(rec['price_num'])/den,np.array(rec['equality_num'])/den*self.es]
        lo=-s.znum/32; hi=(32-s.znum)/32
        def eval_(w):
            rr=c-self.V.T@w; z=np.clip(rr/s.d,lo,hi)
            val=float(rr@z-.5*np.dot(s.d*z,z)+.5*np.dot(w[:r],w[:r]))
            grad=self.diag*w-self.V@z
            return val,grad,z,rr
        initial=check(s,rec) if initial is None else initial; steps=0; stalled=False
        for _ in range(max_steps):
            val,g,z,rr=eval_(w)
            if np.linalg.norm(g,np.inf)<1e-11: break
            free=(rr/s.d>lo)&(rr/s.d<hi)
            H=(self.V[:,free]/s.d[free])@self.V[:,free].T+np.diag(self.diag)
            direction=np.linalg.lstsq(H+1e-12*np.eye(len(w)),-g,rcond=1e-13)[0]
            slope=float(g@direction)
            if not np.isfinite(slope) or slope>=-1e-16: direction=-g; slope=-float(g@g)
            step=1.
            for backtrack in range(35):
                wn=w+step*direction
                if eval_(wn)[0] <= val+1e-4*step*slope+1e-14:
                    w=wn; steps+=1; break
                step*=.5
            else: stalled=True; break
        out=dict(rec)
        out['price_num']=np.rint(w[:r]*den).astype(np.int64).tolist()
        out['equality_num']=np.rint(w[r:]/self.es*den).astype(np.int64).tolist()
        final=check(s,out)
        kept=F(final['upper_exact'])<=F(initial['upper_exact'])
        if not kept: out=dict(rec); final=initial
        assert out['x_num']==rec['x_num'] and out['x_den']==rec['x_den']
        assert out['switch_num']==rec['switch_num'] and out['ineq_num']==rec['ineq_num']
        final.update(record=out,polish_steps=steps,polish_kept=kept,stalled=stalled,
                     polishing_seconds=perf_counter()-t,original_gap=initial['gap'])
        return final

def thaw(d):
    if d['kind']=='cubic-rbf': return RBF().fit(np.array(d['X']),None,np.array(d['Y']))
    feat=Features(7,d['kind'])
    if feat.kind=='tanh': feat.W=np.array(d['W']); feat.bias=np.array(d['bias'])
    m=Surrogate(feat,d['mode'],d['rank']); m.coef=np.array(d['coef']); return m

def frozen_models():
    ff=json.loads((OLD/'results/frozen_models.json').read_text())
    return [{k:thaw(v) for k,v in f['models'].items()} for f in ff]

def normalize(c,rank=6):
    x=np.asarray(c,dtype=float).copy(); x[..., :rank]/=16; x[..., -1]=(x[..., -1]-17)/15
    return x

def time_equalities(s):
    rows=[]; cols=[]; vals=[]; k=0
    for j in range(s.nodes):
        dep=(j+1).bit_length()-1; rep=(1<<dep)-1
        if j==rep: continue
        for a in range(s.services):
            rows.extend([k,k]); cols.extend([j*s.services+a,rep*s.services+a]); vals.extend([1.,-1.]); k+=1
    return sparse.csc_matrix((vals,(rows,cols)),shape=(k,s.n))
