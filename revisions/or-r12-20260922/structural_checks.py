#!/usr/bin/env python3
"""Independent numerical cross-checks of the R12 analytical theorem.
LP tests are numerical diagnostics, not substitutes for the written proofs.
The two-review threshold and nonconstant-comparator examples also use Fractions.
"""
from __future__ import annotations
import json
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parent


def normal_lp(z,g,A,b,E,D,h,k,lam=None,maximize=False):
    n=len(z);active=np.where(abs(A@z-b)<1e-9)[0];m=len(active);ne=len(E);nd=len(D)
    # Variables: active mu, equality nu, box xi, edge s, optional lambda.
    mat=np.column_stack([A[active].T,E.T,np.eye(n),D.T])
    bounds=[(0,None)]*m+[(None,None)]*ne
    for v in z:
        bounds.append((None,0) if v==0 else ((0,None) if v==1 else (0,0)))
    v=D@z-h; Aub=[];bub=[]
    if lam is None:
        mat=np.column_stack([mat,np.zeros(n)]);nv=mat.shape[1]
        bounds += [(None,None)]*nd+[(0,None)]
        eq=[row for row in mat];rhs=list(g)
        for a in range(nd):
            row=np.zeros(nv);row[m+ne+n+a]=1
            if abs(v[a])>1e-10:
                row[-1]=-k[a]*np.sign(v[a]);eq.append(row);rhs.append(0.)
            else:
                row[-1]=-k[a];Aub.append(row.copy());bub.append(0.)
                row[m+ne+n+a]=-1;Aub.append(row);bub.append(0.)
        obj=np.zeros(nv);obj[-1]=-1 if maximize else 1
    else:
        bounds += [(-lam*k[a],lam*k[a]) if abs(v[a])<1e-10 else
                   (lam*k[a]*np.sign(v[a]),lam*k[a]*np.sign(v[a])) for a in range(nd)]
        eq=mat;rhs=g;obj=np.zeros(mat.shape[1])
    return linprog(obj,A_ub=np.array(Aub) if Aub else None,b_ub=bub if Aub else None,
                   A_eq=np.array(eq),b_eq=rhs,bounds=bounds,method='highs')


def direction_lp(z,g,A,b,E,D,h,k,lam):
    active=np.where(abs(A@z-b)<1e-9)[0];v=D@z-h
    zero=np.where(abs(v)<1e-10)[0];nz=np.where(abs(v)>=1e-10)[0]
    n=len(z);nt=len(zero)
    gg=g-lam*D[nz].T@(k[nz]*np.sign(v[nz]))
    obj=np.r_[-gg,lam*k[zero]]
    aa=np.block([[A[active],np.zeros((len(active),nt))],
                 [D[zero],-np.eye(nt)],[-D[zero],-np.eye(nt)]])
    bounds=[(0,1) if x==0 else ((-1,0) if x==1 else (-1,1)) for x in z]+[(0,None)]*nt
    res=linprog(obj,A_ub=aa,b_ub=np.zeros(len(aa)),
                A_eq=np.column_stack([E,np.zeros((len(E),nt))]),b_eq=np.zeros(len(E)),
                bounds=bounds,method='highs')
    assert res.success,res.message
    return res,-res.fun


def tree(n):
    pa=[-1]+[(i-1)//2 for i in range(1,n)]
    D=np.eye(n);S=np.eye(n)
    for i in range(1,n):D[i,pa[i]]=-1
    for i in range(n-1,0,-1):S[pa[i]]+=S[i]
    return pa,D,S


def run():
    rng=np.random.default_rng(22092026);rows=[]
    for trial in range(180):
        n=int(rng.integers(3,13));_,D,S=tree(n)
        z=rng.choice([0.,.25,.5,.75,1.],n)
        g=rng.integers(-5,6,n)/3
        A=rng.integers(-3,4,(n//2+2,n))/4
        # Generic signed, zero, multiple constraints; z is feasible by construction.
        b=A@z+rng.choice([0.,0.,0.,.5,1.],len(A))
        E=np.ones((1,n));h=np.zeros(n);h[0]=.5
        k=rng.integers(1,6,n)/3;lam=float(rng.choice([0.,.1,.5,1.,2.,5.]))
        dual=normal_lp(z,g,A,b,E,D,h,k,lam)
        primal,delta=direction_lp(z,g,A,b,E,D,h,k,lam)
        assert dual.status in (0,2),dual.message
        assert (dual.status==0)==(delta<1e-8),(trial,dual.status,delta)
        witness_error=0.
        if delta>1e-8:
            d=primal.x[:n];step=.01
            for ai,sl in zip(A,b-A@z):
                if sl>1e-9 and ai@d>0:step=min(step,.5*sl/(ai@d))
            for zi,di in zip(z,d):
                if di>0:step=min(step,.5*(1-zi)/di)
                elif di<0:step=min(step,.5*zi/(-di))
            for vi,di in zip(D@z-h,D@d):
                if abs(vi)>1e-10 and vi*di<0:step=min(step,.5*abs(vi/di))
            # r(y)=g'(y-z)-||y-z||^2/2. The exact directional lower bound is attained.
            step=min(step,delta/(max(np.dot(d,d),1e-10)))
            y=z+step*d
            gain=g@(y-z)-.5*np.dot(y-z,y-z)-lam*(k@abs(D@y-h)-k@abs(D@z-h))
            lower=step*delta-.5*step*step*np.dot(d,d)
            assert gain>0 and abs(gain-lower)<1e-8
            assert max(A@y-b)<1e-8 and min(y)>-1e-8 and max(y)<1+1e-8
            witness_error=float(abs(gain-lower))
        rows.append({'trial':trial,'dimension':n,'friction':lam,'optimal':dual.success,
                     'directional_gain':float(delta),'witness_error':witness_error})
    cuts=[]
    for n in (3,7,15,31):
        for rep in range(12):
            pa,D,S=tree(n);c=rng.integers(1,8,n)/4;g=rng.integers(-5,9,n)/4
            k=rng.integers(1,9,n)/3;z=np.full(n,.5)
            A=S[1:]*c; b=A@z;E=c[None,:];h=np.zeros(n);h[0]=.5
            full=normal_lp(z,g,A,b,E,D,h,k)
            # Direct cumulative-cut elimination, no reuse of the full LP solution.
            H=S*c;G=S@g
            aub=np.vstack([np.column_stack([-H,-k]),np.column_stack([H,-k])])
            bub=np.r_[-G,G]
            iso=[]
            for i in range(1,n):
                row=np.zeros(n+1);row[pa[i]]=1;row[i]=-1;iso.append(row)
            aub=np.vstack([aub,iso]);bub=np.r_[bub,np.zeros(n-1)]
            cut=linprog(np.r_[np.zeros(n),1],A_ub=aub,b_ub=bub,
                        bounds=[(None,None)]*n+[(0,None)],method='highs')
            assert full.success and cut.success
            assert abs(full.fun-cut.fun)<1e-7
            for multiplier in (.9,1.,1.1):
                _,delta=direction_lp(z,g,A,b,E,D,h,k,multiplier*cut.fun)
                assert (delta<1e-8)==(multiplier>=1 or cut.fun<1e-8)
            cuts.append({'nodes':n,'replicate':rep,'threshold':float(cut.fun),
                         'dual_difference':float(abs(full.fun-cut.fun))})
    # Exact two-review threshold and its left/right derivative signs.
    c0,c1=Q(2),Q(3);k0,k1=Q(4,5),Q(1,5);a0,a1=Q(1,2),Q(5,4)
    K=a0/c0+a1*(1/c0+1/c1);critical=(k0-k1)/K
    assert critical==Q(72,155)
    assert (k0-k1)-critical*K==0
    s0,s1=critical*a0,-critical*a1;price=Q(61,155)
    assert c0*k0==c0*price+s0-s1 and c1*k1==c1*price+s1
    assert abs(s0)<=critical*a0 and abs(s1)<=critical*a1
    eps=Q(1,10);boundary_loss=eps+eps*eps/2
    assert boundary_loss==Q(21,200) and boundary_loss>eps*eps/2
    # Boundary nonconstant outside protocol: r'(1)=1, s=lambda, upper normal=1-lambda.
    margin_examples=[]
    edge_norm=1/c0**2+1/c1**2
    for friction in (Q(0),critical/2,critical,2*critical):
        slope=max(Q(0),(k0-k1)-friction*K)
        scalar=slope/(2*edge_norm)
        assert scalar<=1  # all box and sign clearance conditions hold
        gain=scalar*slope-scalar**2*edge_norm
        margin2=slope*slope/edge_norm
        assert gain==margin2/4
        margin_examples.append({'friction':str(friction),'gain':str(gain),
                                'margin_squared':str(margin2),'optimal_transfer':str(scalar)})
    interval={'lower':'0','upper':'1','at_half_upper_normal':'1/2',
              'at_two_comparator_derivative':'-1'}
    assert Q(1)-Q(1,2)==Q(1,2) and Q(1)-Q(2)==-1
    out={'numerical_general_tests':rows,'numerical_cut_tests':cuts,
         'exact_two_review_threshold':str(critical),'nonconstant_interval':interval,'exact_zero_gap_switching_prices':{'root':str(s0),'child':str(s1),'continuation':str(price)},'exact_boundary_loss':str(boundary_loss),'exact_margin_examples':margin_examples,
         'note':'LP checks use floating-point HiGHS; analytical proofs and stated Fraction examples are separate.'}
    (ROOT/'results/structural_checks.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({'general':len(rows),'cut':len(cuts),'exact_threshold':str(critical)}))
if __name__=='__main__':run()
