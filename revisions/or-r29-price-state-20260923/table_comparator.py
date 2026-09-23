#!/usr/bin/env python3
"""Exact compact shared-table QP; conventional primal active-set method.
The graph condensation, not this textbook QP solver, is the structural claim.
"""
from fractions import Fraction as F
from pathlib import Path
import json,time
R=Path(__file__).resolve().parent


def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def linear(A,b):
    M=[list(r)+[s] for r,s in zip(A,b)];n=len(b)
    for j in range(n):
        pivot=next((i for i in range(j,n) if M[i][j]),None)
        if pivot is None:raise ArithmeticError('Dependent working constraints')
        M[j],M[pivot]=M[pivot],M[j];v=M[j][j];M[j]=[x/v for x in M[j]]
        for i in range(n):
            if i!=j and M[i][j]:
                v=M[i][j];M[i]=[a-v*b for a,b in zip(M[i],M[j])]
    return [M[i][-1] for i in range(n)]


def qp(q,r,E,e,A,b,x):
    assert dot(E,x)==e and all(dot(a,x)<=v for a,v in zip(A,b))
    active=[];n=len(x)
    for it in range(5000):
        W=[E]+[A[j] for j in active]; rhs=[r[i]-q[i]*x[i] for i in range(n)]
        S=[[sum(a[i]*z[i]/q[i] for i in range(n)) for z in W] for a in W]
        lam=linear(S,[sum(a[i]*rhs[i]/q[i] for i in range(n)) for a in W])
        p=[(rhs[i]-sum(a[i]*v for a,v in zip(W,lam)))/q[i] for i in range(n)]
        if all(t==0 for t in p):
            neg=[(mu,j) for mu,j in zip(lam[1:],active) if mu<0]
            if not neg:
                mu=[F(0)]*len(A)
                for j,v in zip(active,lam[1:]):mu[j]=v
                return x,lam[0],mu,it+1
            active.remove(min(neg)[1]);continue
        step=F(1);block=None
        for j,(a,v) in enumerate(zip(A,b)):
            if j in active:continue
            slope=dot(a,p)
            if slope>0:
                alpha=(v-dot(a,x))/slope
                if alpha<step or (alpha==step and alpha<1 and (block is None or j<block)):
                    step,block=alpha,j
        assert step>=0
        x=[v+step*d for v,d in zip(x,p)]
        if block is not None and step<1:active.append(block)
    raise ArithmeticError('Active-set iteration limit exceeded')


def compact(raw):
    nodes=raw['nodes'];N=len(nodes);beta=F(raw['beta']);K=max(v.get('cell',i) for i,v in enumerate(nodes))+1
    cells=[v.get('cell',i) for i,v in enumerate(nodes)]
    H=[[F(0)]*K for _ in nodes];w=[F(0)]*N;w[0]=1
    for i,v in enumerate(nodes):
        for j,p in v['edges']:w[j]+=w[i]*beta*F(p)
    for i in range(N-1,-1,-1):
        v=nodes[i];H[i][cells[i]]+=F(v['a'])
        for j,p in v['edges']:
            for k in range(K):H[i][k]+=beta*F(p)*H[j][k]
    q=[F(0)]*K;r=[F(0)]*K
    for i,v in enumerate(nodes):q[cells[i]]+=w[i]*F(v['q']);r[cells[i]]+=w[i]*F(v['r'])
    A=[row[:] for row in H[1:]];b=[F(v['cap']) for v in nodes[1:]]
    for k in range(K):
        a=[F(0)]*K;a[k]=1;A.append(a);b.append(F(1))
        a=[F(0)]*K;a[k]=-1;A.append(a);b.append(F(0))
    x=[F(0)]*K
    for i,v in enumerate(nodes):x[cells[i]]=F(v['center'])
    assert all(x[cells[i]]==F(v['center']) for i,v in enumerate(nodes))
    return q,r,H[0],F(raw['promise']),A,b,x,H,w


def run():
    evidence=json.loads((R/'results/evidence.json').read_text());out=[]
    for item in evidence['instances']:
        raw=item['instance'];des=raw.get('design',{})
        if des.get('corridor') or not des or des['T']>16:continue
        q,r,E,e,A,b,x,H,w=compact(raw)
        start=time.perf_counter();x,eta,mu,it=qp(q,r,E,e,A,b,x);secs=time.perf_counter()-start
        # Exact global feasibility and KKT; independent routine rechecks saved data.
        assert dot(E,x)==e and all(dot(a,x)<=v for a,v in zip(A,b))
        for i in range(len(x)):
            assert r[i]-q[i]*x[i]==eta*E[i]+sum(mu[j]*A[j][i] for j in range(len(A)))
        assert all(m>=0 and m*(v-dot(a,x))==0 for m,a,v in zip(mu,A,b))
        val=dot(r,x)-sum(t*z*z/2 for t,z in zip(q,x));full=F(item['certificate']['value'])
        assert full>=val
        def enc(o):
            if isinstance(o,F):return str(o)
            if isinstance(o,list):return [enc(v) for v in o]
            if isinstance(o,dict):return {k:enc(v) for k,v in o.items()}
            return o
        out.append(enc(dict(name=raw['name'],q=q,r=r,E=E,e=e,A=A,b=b,x=x,eta=eta,mu=mu,
                            table_value=val,full_value=full,gain=full-val,iterations=it,solve_seconds=secs,
                            graph_nodes=len(raw['nodes']),table_coordinates=len(x),H=H,weights=w)))
        print(raw['name'],len(x),it,float(full-val),round(secs,3),flush=True)
    (R/'results/tables.json').write_text(json.dumps({'method':'exact rational primal active-set QP','instances':out},indent=2)+'\n')

if __name__=='__main__':run()
