#!/usr/bin/env python3
"""Independent, explicitly defined comparison algorithms.

laminar(): exact occurrence-indexed marginal-response reduction, NOT claimed
as original authors' code or the fastest Mjelde/Tang implementation.
qp(): SciPy sparse trust-region interior point on independently expanded rows.
promise_grid(): primal promise DP on the PUBLIC graph (no history unfolding).
None imports or calls the quotient compiler.
"""
from __future__ import annotations
from fractions import Fraction as F
from bisect import bisect_right
import math


def unfold(raw: dict, limit: int=100000) -> list[dict]:
    ns=raw['nodes']; beta=F(raw['beta']); out=[]
    stack=[(0,F(1),None,())]
    while stack:
        v,w,parent,anc=stack.pop(); i=len(out)
        if i>=limit: raise MemoryError(f'Explicit tree exceeds declared {limit} occurrence limit.')
        out.append(dict(vertex=v,weight=w,children=[],ancestors=anc+(i,)))
        if parent is not None: out[parent]['children'].append(i)
        for j,p in reversed(ns[v]['edges']):
            stack.append((j,w*beta*F(p),i,anc+(i,)))
    return out


def laminar(raw: dict) -> dict:
    """Unnormalized allocation z_h=w_h a_v x_h; scalar subtree water filling."""
    tree=unfold(raw); curves={}; barriers={}
    def value(curve,eta):
        ks,ls=curve; m,b=ls[bisect_right(ks,eta)];return m*eta+b
    def invert(curve,target):
        ks,ls=curve
        if not ls[-1][1]<=target<=ls[0][1]:raise ValueError('Tree promise infeasible.')
        if not ks:return F(0)
        if target==ls[0][1]:return ks[0]-1
        for i,(m,b) in enumerate(ls):
            if m<0:
                z=(target-b)/m
                if (not i or ks[i-1]<=z) and (i==len(ks) or z<=ks[i]):return z
        raise ArithmeticError('Tree response crossing missing.')
    def interpolate(knots,values,hi,lo):
        if not knots:return ([],[(F(0),hi)])
        ls=[(F(0),hi)]
        for x,y,fx,fy in zip(knots,knots[1:],values,values[1:]):
            m=(fy-fx)/(y-x);ls.append((m,fx-m*x))
        ls.append((F(0),lo)); kk=[];ll=[ls[0]]
        for k,l in zip(knots,ls[1:]):
            if l!=ll[-1]:kk.append(k);ll.append(l)
        return kk,ll
    for i in reversed(range(len(tree))):
        h=tree[i];v=raw['nodes'][h['vertex']];w=h['weight']
        a,r,q,lo,hi,cap=[F(v[k]) for k in ('a','r','q','lo','hi','cap')]
        keys={(r-q*hi)/a,(r-q*lo)/a} if lo<hi else set()
        for ch in h['children']:keys.update(curves[ch][0])
        keys=sorted(keys)
        def pre(eta):return w*a*max(lo,min(hi,(r-a*eta)/q))+sum(value(curves[ch],eta) for ch in h['children'])
        high=w*a*hi+sum(curves[ch][1][0][1] for ch in h['children'])
        low=w*a*lo+sum(curves[ch][1][-1][1] for ch in h['children'])
        cap=w*cap
        if cap<low:raise ValueError('Infeasible tree cap.')
        before=interpolate(keys,[pre(k) for k in keys],high,low)
        alpha=None if cap>=high else invert(before,cap)
        barriers[i]=alpha
        if alpha is None:curves[i]=before
        else:
            keys=sorted(set(keys)|{alpha})
            curves[i]=interpolate(keys,[min(cap,value(before,k)) for k in keys],cap,low)
    eta=invert(curves[0],F(raw['promise'])); price={0:eta}; reward=F(0);payment=F(0)
    for i,h in enumerate(tree):
        v=raw['nodes'][h['vertex']];r,q,a,lo,hi=[F(v[k]) for k in ('r','q','a','lo','hi')]
        al=barriers[i];s=price[i] if al is None else max(price[i],al)
        x=max(lo,min(hi,(r-a*s)/q));w=h['weight']
        reward+=w*(r*x-q*x*x/2);payment+=w*a*x
        for ch in h['children']:price[ch]=s
    assert payment==F(raw['promise'])
    return dict(value=str(reward),payment=str(payment),history_nodes=len(tree),
                stored_segments=sum(len(c[1]) for c in curves.values()),
                root_price=str(eta),exact=True)


def qp(raw: dict) -> dict:
    import numpy as np
    import scipy.sparse as sp
    import scipy
    from scipy.optimize import minimize, LinearConstraint, Bounds
    tree=unfold(raw);n=len(tree);nodes=raw['nodes']
    weights=np.array([float(h['weight']) for h in tree])
    a=np.array([float(F(nodes[h['vertex']]['a'])) for h in tree])
    q=np.array([float(F(nodes[h['vertex']]['q'])) for h in tree])
    r=np.array([float(F(nodes[h['vertex']]['r'])) for h in tree])
    lo=np.array([float(F(nodes[h['vertex']]['lo'])) for h in tree])
    hi=np.array([float(F(nodes[h['vertex']]['hi'])) for h in tree])
    cap=np.array([float(F(nodes[h['vertex']]['cap'])) for h in tree])
    rr=[];cc=[];vv=[]
    for j,h in enumerate(tree):
        for i in h['ancestors']:
            rr.append(i);cc.append(j);vv.append(float(h['weight']/tree[i]['weight'])*a[j])
    caps=sp.csc_matrix((vv,(rr,cc)),shape=(n,n))
    root=sp.csc_matrix((weights*a).reshape(1,-1))
    A=sp.vstack([root,caps,sp.eye(n,format='csc')],format='csc')
    b=float(F(raw['promise']))
    lower=np.r_[b,np.full(n,-np.inf),lo];upper=np.r_[b,cap,hi]
    objective=lambda x: float(np.dot(weights,q*x*x/2-r*x))
    jac=lambda x: weights*(q*x-r)
    Hess=sp.diags(weights*q,format='csc')
    # This constant starting point is not obtained from the quotient optimum.
    x0=np.clip(np.full(n,b/max(float(weights@a),1e-15)),lo,hi)
    constraint=LinearConstraint(A[:n+1,:],lower[:n+1],upper[:n+1])
    ans=minimize(objective,x0,jac=jac,hess=lambda x:Hess,
                 bounds=Bounds(lo,hi),constraints=[constraint],method='trust-constr',
                 options=dict(gtol=1e-12,xtol=1e-12,barrier_tol=1e-12,
                              initial_barrier_parameter=1e-10,initial_barrier_tolerance=1e-10,
                              maxiter=1000,sparse_jacobian=True,verbose=0))
    x=ans.x;act=A@x
    residual=max(float(np.max(np.maximum(lower-act,0))),float(np.max(np.maximum(act-upper,0))))
    return dict(value=-float(ans.fun),history_nodes=n,status=ans.message,success=bool(ans.success),
                iterations=int(ans.niter),primal_residual=residual,dual_residual=float(ans.optimality),
                matrix_nonzeros=A.nnz,scipy_version=scipy.__version__,exact=False)


def promise_grid(raw: dict, resolution: int=20) -> dict:
    """Feasible primal policy-graph DP; child promises on multiples of 1/resolution.

    Uniform binary transitions, beta=a=1, boxes [0,1]. Local actions are
    continuous residuals; the root promise is NOT rounded. Max-plus convolution
    eliminates the two-child allocation loop. Policies are replayed rationally.
    """
    import numpy as np
    if F(raw['beta'])!=1:raise ValueError('Grid benchmark requires beta=1.')
    ns=raw['nodes']; values={}; choices={}; splits={};Q=resolution
    if Q<=0:raise ValueError('Positive resolution required.')
    for v in reversed(range(len(ns))):
        row=ns[v]
        if (F(row['a']),F(row['lo']),F(row['hi']))!=(F(1),F(0),F(1)):
            raise ValueError('Grid benchmark requires a=1 and physical box [0,1].')
        children=row['edges']
        if children and (len(children)!=2 or any(F(p)!=F(1,2) for j,p in children)):
            raise ValueError('Grid benchmark requires uniform binary transitions.')
        r,q,cap=[F(row[k]) for k in ('r','q','cap')]
        if children:
            u,w=[j for j,p in children];a=values[u];b=values[w]
            best=np.full(len(a)+len(b)-1,-np.inf);arg=np.full(len(best),-1,dtype=np.int32)
            for i,aval in enumerate(a):
                cand=.5*(aval+b);sl=best[i:i+len(b)];take=cand>sl
                sl[take]=cand[take];arg[i:i+len(b)][take]=i
            ymax=min(cap,F(1)+F(len(a)+len(b)-2,2*Q))
            count=math.floor(ymax*Q)+1
            def evaluate(y):
                xs=y-.5*np.arange(len(best))/Q
                valid=(xs>=-1e-12)&(xs<=1+1e-12)
                obj=np.where(valid,float(r)*xs-float(q)*xs*xs/2+best,-np.inf)
                k=int(np.argmax(obj));return float(obj[k]),k
            vals=[];pick=[]
            for k in range(count):
                z,s=evaluate(k/Q);vals.append(z);pick.append(s)
            values[v]=np.array(vals);choices[v]=pick;splits[v]=arg
        else:
            count=math.floor(min(cap,F(1))*Q)+1;y=np.arange(count)/Q
            values[v]=float(r)*y-float(q)*y*y/2
    b0=F(raw['promise']); root=ns[0]
    if b0>F(root['cap']):raise ValueError('Root cap violated.')
    if root['edges']:
        u,w=[j for j,p in root['edges']];a=values[u];b=values[w]
        best=np.full(len(a)+len(b)-1,-np.inf);arg=np.full(len(best),-1,dtype=np.int32)
        for i,aval in enumerate(a):
            cand=.5*(aval+b);sl=best[i:i+len(b)];take=cand>sl
            sl[take]=cand[take];arg[i:i+len(b)][take]=i
        xs=float(b0)-.5*np.arange(len(best))/Q
        valid=(xs>=-1e-12)&(xs<=1+1e-12)
        score=np.where(valid,float(F(root['r']))*xs-float(F(root['q']))*xs*xs/2+best,-np.inf)
        root_sum=int(np.argmax(score))
        if not np.isfinite(score[root_sum]):raise ValueError('No feasible grid recourse for exact root promise.')
        root_split=int(arg[root_sum]);root_float=float(score[root_sum])
    else:root_sum=root_split=0;root_float=float(F(root['r'])*b0-F(root['q'])*b0*b0/2)
    flows={(0,b0):F(1)};reward=F(0);pay=F(0);pairs=0
    for v,row in enumerate(ns):
        for (node,y),weight in list(flows.items()):
            if node!=v:continue
            children=row['edges']
            if children:
                u,w=[j for j,p in children]
                if v==0:s,i=root_sum,root_split
                else:s=choices[v][int(y*Q)];i=int(splits[v][s])
                j=s-i;by,bz=F(i,Q),F(j,Q);x=y-(by+bz)/2
                for ch,target in [(u,by),(w,bz)]:
                    key=(ch,target);flows[key]=flows.get(key,F(0))+weight/2
            else:x=y
            assert 0<=x<=1 and 0<=y<=F(row['cap'])
            reward+=weight*(F(row['r'])*x-F(row['q'])*x*x/2);pay+=weight*x;pairs+=1
    assert pay==b0 and abs(float(reward)-root_float)<1e-8
    return dict(value=str(reward),payment=str(pay),resolution=Q,stored_primal_states=sum(len(a) for a in values.values()),
                executed_pairs=pairs,exact_feasibility=True,continuous_optimum=False)
