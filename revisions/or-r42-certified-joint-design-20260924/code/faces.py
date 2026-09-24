"""Finite exact continuous design by contractual cells and quadratic faces.

This is an exponential reference algorithm, NOT a scalable nonconvex solver.
Every solve and feasibility comparison is rational. Singular stationary systems
are skipped legitimately: a quadratic maximum on a compact polytope has a
maximizer on a face with nonsingular reduced Hessian, possibly a vertex.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product, combinations
from math import lcm
from unified import Model, rational, solve_allocation


def linear_solve(A,b):
    """Fraction-free integer Gaussian elimination, then rational back substitution."""
    n=len(b)
    if not n:
        return []
    M=[]
    for row,y in zip(A,b):
        row=list(row)+[y]
        den=lcm(*(z.denominator for z in row))
        M.append([int(z*den) for z in row])
    previous=1
    for k in range(n-1):
        pivot=next((i for i in range(k,n) if M[i][k]),None)
        if pivot is None:
            return None
        if pivot!=k:
            M[k],M[pivot]=M[pivot],M[k]
        v=M[k][k]
        for i in range(k+1,n):
            w=M[i][k]
            for j in range(k+1,n+1):
                num=v*M[i][j]-w*M[k][j]
                if num % previous:
                    raise ArithmeticError('Fraction-free division failed.')
                M[i][j]=num//previous
            M[i][k]=0
        previous=v
    if not M[-1][-2]:
        return None
    x=[F(0)]*n
    for i in range(n-1,-1,-1):
        x[i]=(F(M[i][-1])-sum(M[i][j]*x[j] for j in range(i+1,n)))/M[i][i]
    return x


def cell(model,s,modes,B,delta,price):
    k=len(model.caps); n=s+k
    H=[[F(0)]*n for _ in range(n)]; a=[F(0)]*n; constant=F(0)
    G=[]; h=[]
    def inequality(terms,rhs):
        row=[F(0)]*n
        for i,v in terms:
            row[i]+=v
        rhs=F(rhs)
        if (row,rhs) not in list(zip(G,h)):
            G.append(row); h.append(rhs)
    inequality([(0,-1)],0)
    for i in range(s-1):
        inequality([(i,1),(i+1,-1)],0)
    inequality([(s-1,1)],1)
    alpha,beta,eta=price
    for i in range(s):
        H[i][i]-=2*alpha; a[i]-=beta; constant-=eta
    def cross(i,j,v):
        H[i][j]+=v; H[j][i]+=v
    for j,(kind,i) in enumerate(modes):
        p,g,b=model.probabilities[j],model.gamma[j],model.caps[j]
        t=s+j
        inequality([(i,1),(t,-1)],0)
        if kind=='S':
            inequality([(t,1)],b)
            a[i]+=p*model.r
            H[i][i]-=p*(model.q+g); H[t][t]-=p*g
            cross(i,t,p*g)
        else:
            v=i+1
            inequality([(t,1),(v,-1)],0)
            if delta:
                inequality([(t,1)],b)
            if b+delta<1:
                inequality([(v,1)],b+delta)
            a[t]+=p*model.r
            cross(i,t,-p*model.q/2); cross(v,t,-p*model.q/2)
            cross(i,v,p*model.q/2)
    # Eliminate the final target using the exact root promise.
    d=n-1; last=n-1
    offset=B/model.probabilities[-1]
    v=[F(0)]*d
    for j in range(k-1):
        v[s+j]=-model.probabilities[j]/model.probabilities[-1]
    Hr=[[H[i][j]+H[i][last]*v[j]+v[i]*H[last][j]+v[i]*H[last][last]*v[j]
         for j in range(d)] for i in range(d)]
    ar=[a[i]+H[i][last]*offset+v[i]*(a[last]+H[last][last]*offset) for i in range(d)]
    cr=constant+a[last]*offset+H[last][last]*offset*offset/2
    Gr=[[row[i]+row[last]*v[i] for i in range(d)] for row in G]
    hr=[rhs-row[last]*offset for row,rhs in zip(G,h)]
    return Hr,ar,cr,Gr,hr,v,offset


def qp_faces(H,a,c,G,h):
    """Enumerate every independent active-set candidate; no tolerance or pruning."""
    d=len(a); M=len(G); best=None
    counts=dict(systems=0,nonsingular=0,feasible=0)
    for length in range(min(d,M)+1):
        for ids in combinations(range(M),length):
            A=[G[i] for i in ids]; b=[h[i] for i in ids]
            K=[list(H[i])+[row[i] for row in A] for i in range(d)]
            K.extend([list(row)+[F(0)]*length for row in A])
            rhs=[-x for x in a]+b
            counts['systems']+=1
            sol=linear_solve(K,rhs)
            if sol is None:
                continue
            counts['nonsingular']+=1
            x=tuple(sol[:d])
            if any(sum(g*z for g,z in zip(row,x))>v for row,v in zip(G,h)):
                continue
            counts['feasible']+=1
            val=c+sum(ai*xi for ai,xi in zip(a,x))
            val+=sum(x[i]*H[i][j]*x[j] for i in range(d) for j in range(d))/2
            if best is None or (val,tuple(-z for z in x))>best[0]:
                best=((val,tuple(-z for z in x)),x,ids)
    return best,counts


def solve_continuous(model: Model,budget,promise,delta=0,price=(0,0,0),deterministic=False):
    """Global exact value for quadratic level charge alpha*c^2+beta*c+eta.

    The charge is checked to be nonnegative everywhere on the unit interval,
    including its interior minimum; coefficients themselves may be negative.
    deterministic=True enumerates singleton modes only and solves V_m^D(B).
    """
    B,delta=rational(promise),rational(delta)
    price=tuple(map(rational,price))
    if len(price)!=3 or delta<0:
        raise ValueError('Three price coefficients and nonnegative tolerance required.')
    alpha,beta,eta=price
    minima=[eta,alpha+beta+eta]
    if alpha>0 and 0<-beta/(2*alpha)<1:
        minima.append(eta-beta*beta/(4*alpha))
    if min(minima)<0:
        raise ValueError('Quadratic charge must be nonnegative on [0,1].')
    if isinstance(budget,bool) or not isinstance(budget,int) or budget<1:
        raise ValueError('Positive integer symbol budget required.')
    bar=sum(p*b for p,b in zip(model.probabilities,model.caps))
    if not 0<=B<=bar:
        raise ValueError('Promise outside feasible range.')
    winner=None
    totals=dict(cells=0,systems=0,nonsingular=0,feasible=0)
    for s in range(1,budget+1):
        types=[('S',i) for i in range(s)]
        if not deterministic:
            types += [('L',i) for i in range(s-1)]
        for modes in product(types,repeat=len(model.caps)):
            H,a,c,G,h,v,offset=cell(model,s,modes,B,delta,price)
            ans,count=qp_faces(H,a,c,G,h)
            totals['cells']+=1
            for key,val in count.items():
                totals[key]+=val
            if ans is None:
                continue
            x=ans[1]; full=tuple(x)+(offset+sum(u*z for u,z in zip(v,x)),)
            rawbook=full[:s]; targets=full[s:]
            book=tuple(sorted(set(rawbook)))
            key=(ans[0][0],-s,tuple(-z for z in book))
            if winner is None or key>winner[0]:
                winner=(key,book,targets,modes,ans[2])
    if winner is None:
        raise AssertionError('No candidate despite a feasible singleton zero book.')
    _,book,targets,modes,active=winner
    alpha,beta,eta=price
    charge=sum(alpha*z*z+beta*z+eta for z in book)
    answer=dict(net_value=winner[0][0],codebook=book,targets=targets,
                charge=charge,modes=modes,active_set=active,counts=totals)
    if not deterministic:
        allocation=solve_allocation(model,book,B,delta)
        if allocation.value-charge!=answer['net_value']:
            raise AssertionError('Continuous optimum failed independent fixed-book replay.')
        answer['allocation']=allocation
    return answer
