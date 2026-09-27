"""Exact eligibility pooling for heterogeneous quadratic renewal contracts.

No cap guard, cost binning, relaxed memory budget, or dispersion error is used.
The original R45/R46 reference routines remain unmodified for regression tests.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from dataclasses import asdict
from itertools import combinations, groupby
import sys, time, heapq
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'revisions/or-r46-box-decomposition-20260925/code'))
from box_solver import Instance, rat, policy, frontier, ideal_targets, encode, branch_support, fixed_allocate, project_box


def eligibility_groups(data, catalog):
    groups = {}
    for j, tau in enumerate(data.ceilings):
        groups.setdefault(sum(x<=tau for x in catalog), []).append(j)
    return tuple(tuple(v) for v in groups.values())


def subinstance(data, ids):
    W = sum(data.weights[j] for j in ids)
    return Instance.make([data.caps[j] for j in ids], [data.weights[j]/W for j in ids],
        [data.gamma[j] for j in ids], [data.ceilings[j] for j in ids], data.r, data.curvature)


def group_model(data, groups):
    # This object represents feasible group means, not a surrogate payoff model.
    return Instance.make([sum(data.weights[j]*data.caps[j] for j in ids)/sum(data.weights[j] for j in ids) for ids in groups],
        [sum(data.weights[j] for j in ids) for ids in groups], [F(0)]*len(groups), [F(1)]*len(groups), data.r, data.curvature)


def equalized_bounds(data, groups, lower, upper):
    lo, hi = [None]*len(data.caps), [None]*len(data.caps)
    for ids,l,u in zip(groups,lower,upper):
        sub = subinstance(data,ids)
        for j,x,y in zip(ids,ideal_targets(sub,l),ideal_targets(sub,u)):
            lo[j],hi[j]=x,y
    return tuple(lo),tuple(hi)


def capped_cost(weights, gamma, capacities, target):
    """Exact minimum cost at a supplied mean; return a primal/dual witness."""
    w,g,c = tuple(weights),tuple(gamma),tuple(capacities)
    total=sum(x*y for x,y in zip(w,c))
    if not 0<=target<=total: raise ValueError(('Infeasible service mean',target,total))
    zero=[i for i,x in enumerate(g) if x==0]
    free=sum(w[i]*c[i] for i in zero)
    y=[F(0)]*len(w)
    if target<=free:
        residual=target
        for i in zero:
            take=min(residual,w[i]*c[i]);y[i]=take/w[i];residual-=take
        alpha=F(0)
    else:
        for i in zero:y[i]=c[i]
        residual=target-free
        active=[i for i,x in enumerate(g) if x>0 and c[i]>0]
        reciprocal=sum(w[i]/g[i] for i in active)
        alpha=F(0)
        ordered=sorted(active,key=lambda i:g[i]*c[i])
        for threshold, hit_iter in groupby(ordered,key=lambda i:g[i]*c[i]):
            candidate=residual/reciprocal
            if candidate<=threshold:
                alpha=candidate;break
            hit=list(hit_iter)
            for i in hit:
                residual-=w[i]*c[i];reciprocal-=w[i]/g[i]
        else:
            if reciprocal:alpha=residual/reciprocal
            elif residual:raise AssertionError('Water-level residual')
        for i in range(len(w)):
            if g[i]>0:y[i]=min(c[i],alpha/g[i])
    cost=sum(wi*gi*yi*yi/2 for wi,gi,yi in zip(w,g,y))
    assert sum(wi*yi for wi,yi in zip(w,y))==target
    assert all(0<=yi<=ci for yi,ci in zip(y,c))
    return dict(target=target,service=tuple(y),marginal=alpha,cost=cost)


def priced_service(weights,gamma,capacities,qlo,qhi,price):
    """Box-mean support with a scalar dual certificate; all numbers rational."""
    w,g,c=tuple(weights),tuple(gamma),tuple(capacities)
    uncon=tuple(min(ci,max(F(0),-price/gi)) if gi else ci if price<0 else F(0) for gi,ci in zip(g,c))
    q=max(qlo,min(qhi,sum(wi*yi for wi,yi in zip(w,uncon))))
    z=capped_cost(w,g,c,q)
    nu=-price-z['marginal']
    effective=price+nu
    scalar=tuple(min(ci,max(F(0),-effective/gi)) if gi else ci if effective<0 else F(0) for gi,ci in zip(g,c))
    upper=nu*(qhi if nu>=0 else qlo)+sum(wi*(-gi*yi*yi/2-effective*yi) for wi,gi,yi in zip(w,g,scalar))
    primal=-z['cost']-price*q
    assert primal==upper,('Pooled support duality',primal,upper,q,nu,qlo,qhi)
    return dict(**z,price=price,multiplier=nu,value=upper,qlo=qlo,qhi=qhi)


def corrections(data,a,groups,lower,upper,plo,phi,price):
    """Last-eligible-symbol corrections, paid once per eligibility group."""
    corr={}; proof={}
    for h,ids in enumerate(groups):
        W=sum(data.weights[j] for j in ids);w=tuple(data.weights[j]/W for j in ids)
        gamma=tuple(data.gamma[j] for j in ids)
        for i,d in enumerate(a):
            if d>min(data.ceilings[j] for j in ids):continue
            D=sum(wt*min(data.caps[j],d) for wt,j in zip(w,ids))
            if upper[h]<D:
                corr[h,i]=F(0);proof[h,i]=None;continue
            cap=tuple(max(F(0),data.caps[j]-d) for j in ids)
            qlo=max(F(0),lower[h]-D);qhi=upper[h]-D
            z=priced_service(w,gamma,cap,qlo,qhi,price)
            naive=F(0)
            for wt,j in zip(w,ids):
                yl=max(F(0),plo[j]-d);yu=max(F(0),phi[j]-d);gam=data.gamma[j]
                y=yl if price>=0 else yu if gam==0 else min(yu,max(yl,-price/gam))
                naive+=wt*(-gam*y*y/2-price*y)
            corr[h,i]=W*(z['value']-naive)
            assert corr[h,i]>=0
            proof[h,i]=dict(multiplier=z['multiplier'],service=z['service'],mean=z['target'],value=z['value'],correction=corr[h,i])
    return corr,proof


def fixed_group_support(data,ids,book,lo,hi,price):
    """Independent reference: optimize the original fixed-book group directly."""
    sub=subinstance(data,ids);low=(book[0],)*len(ids)
    supports=[branch_support(sub,j,book,low[j],sub.caps[j],price) for j in range(len(ids))]
    mn=sum(w*z[1] for w,z in zip(sub.weights,supports));mx=sum(w*z[2] for w,z in zip(sub.weights,supports))
    if mx<lo:
        p=fixed_allocate(sub,book,lo,{x:F(0) for x in book});return p['gross']-price*lo,lo,lo
    if mn>hi:
        p=fixed_allocate(sub,book,hi,{x:F(0) for x in book});return p['gross']-price*hi,hi,hi
    return sum(w*z[0] for w,z in zip(sub.weights,supports)),max(mn,lo),min(mx,hi)


def price_path(data,catalog,charges,B,budget,groups,lower,upper,price,tables=False,reference_check=False):
    """Two-sided path oracle on group-mean boxes, with exact boundary costs."""
    a,rho,lam=tuple(catalog),tuple(charges),rat(price)
    n,m,k=len(a),min(budget,len(a)),len(data.caps)
    plo,phi=equalized_bounds(data,groups,lower,upper)
    g=tuple(data.reward(x)-lam*x for x in a)
    anchors=[i for i,x in enumerate(a) if x<=min(phi) and sum(w*max(l,x) for w,l in zip(data.weights,plo))<=B]
    if not anchors:return None
    corr,proof=corrections(data,a,groups,lower,upper,plo,phi,lam)
    K=tuple(sum(x<=min(data.ceilings[j] for j in ids) for x in a) for ids in groups)
    def extra(i,v=None):
        return sum((corr[h,i] for h,kh in enumerate(K) if i<kh and (v is None or v>=kh)),F(0))
    def service(j,u):
        low=max(F(0),plo[j]-u);high=phi[j]-u;gam=data.gamma[j]
        y=low if lam>=0 else high if gam==0 else min(high,max(low,-lam/gam))
        return -gam*y*y/2-lam*y
    up,down={},{}
    for i,u in enumerate(a):
        for v in range(i+1,n):
            z=a[v];slope=(g[v]-g[i])/(z-u)
            up[i,v]=extra(i,v)+sum((w*(g[i]+slope*(h-u) if z<=tau else g[i]+service(j,u))
                for j,(w,h,tau) in enumerate(zip(data.weights,phi,data.ceilings)) if u<=h<z),F(0))
            if lam>0:
                down[i,v]=extra(i,v)+sum((w*(g[i]+slope*(l-u) if z<=tau else g[i]-gam*(l-u)**2/2-lam*(l-u))
                    for w,l,tau,gam in zip(data.weights,plo,data.ceilings,data.gamma) if u<=l<z),F(0))
    alpha=[[None]*n for _ in range(m+1)];apre=[[None]*n for _ in range(m+1)]
    for i in anchors:alpha[1][i]=-rho[i]
    for r in range(2,m+1):
        for v in range(n):
            options=[(alpha[r-1][i]+up[i,v]-rho[v],-i,i) for i in range(v) if alpha[r-1][i] is not None and g[i]<=g[v]]
            if options:alpha[r][v],_,apre[r][v]=max(options)
    middle=[F(0)]*n;beta=None;bnext=None
    if lam<=0:
        tail=[extra(i)+sum((w*(g[i]+service(j,u)) for j,(w,h) in enumerate(zip(data.weights,phi)) if h>=u),F(0)) for i,u in enumerate(a)]
        candidates=[(alpha[r][i]+tail[i],-r,-i,r,i) for r in range(1,m+1) for i in range(n) if alpha[r][i] is not None]
    else:
        tail=[extra(i)+sum((w*(g[i]-gam*(l-u)**2/2-lam*(l-u)) for w,l,gam in zip(data.weights,plo,data.gamma) if l>=u),F(0)) for i,u in enumerate(a)]
        middle=[sum((w*g[i] for w,l,h in zip(data.weights,plo,phi) if l<u<=h),F(0)) for i,u in enumerate(a)]
        beta=[[None]*n]+[list(tail) for _ in range(m)];bnext=[[None]*n for _ in range(m+1)]
        for s in range(2,m+1):
            for i in range(n):
                options=[(tail[i],0,None)]+[(down[i,v]-rho[v]+beta[s-1][v],-v-1,v) for v in range(i+1,n) if g[v]<=g[i]]
                beta[s][i],_,bnext[s][i]=max(options,key=lambda z:(z[0],z[1]))
        candidates=[(alpha[r][i]+middle[i]+beta[m-r+1][i],-r,-i,r,i) for r in range(1,m+1) for i in range(n) if alpha[r][i] is not None]
    value,_,_,r,pivot=max(candidates);ids=[pivot];cur=pivot;rr=r
    while rr>1:cur=apre[rr][cur];ids.append(cur);rr-=1
    ids.reverse()
    if lam>0:
        cur,s=pivot,m-r+1
        while s>1 and bnext[s][cur] is not None:cur=bnext[s][cur];ids.append(cur);s-=1
    book=tuple(a[i] for i in ids)
    # Reference reconstruction is optional: it uses the untouched R46 allocator.
    ans=dict(price=lam,support=value,upper=lam*B+value,book=book)
    if reference_check:
        out=[fixed_group_support(data,grp,book,l,h,lam) for grp,l,h in zip(groups,lower,upper)]
        weights=tuple(sum(data.weights[j] for j in grp) for grp in groups)
        direct=sum(w*z[0] for w,z in zip(weights,out))-sum(rho[i] for i in ids)
        assert direct==value,('Group path reconstruction',lam,book,value,direct,lower,upper)
        ans.update(total_min=sum(w*z[1] for w,z in zip(weights,out)),total_max=sum(w*z[2] for w,z in zip(weights,out)))
    if tables:
        ans.update(alpha=alpha[1:],beta=None if beta is None else beta[1:],
            service_witnesses=[dict(group=h,index=i,**p) for (h,i),p in sorted(proof.items()) if p is not None])
    return ans


def exhaustive_box(data,a,rho,B,m,groups,lo,hi,lam):
    best=None
    weights=tuple(sum(data.weights[j] for j in grp) for grp in groups)
    for s in range(1,min(m,len(a))+1):
        for ids in combinations(range(len(a)),s):
            book=tuple(a[i] for i in ids)
            if book[0]>min(data.caps) or book[0]>min(hi) or sum(w*max(l,book[0]) for w,l in zip(weights,lo))>B:continue
            val=sum(w*fixed_group_support(data,grp,book,max(l,book[0]),h,lam)[0] for w,grp,l,h in zip(weights,groups,lo,hi))-sum(rho[i] for i in ids)
            if best is None or val>best:best=val
    return None if best is None else lam*B+best


def recover(data,groups,book,means,charges):
    targets=[None]*len(data.caps)
    for ids,s in zip(groups,means):
        sub=subinstance(data,ids);d=max(x for x in book if x<=min(sub.ceilings))
        D=sum(w*min(b,d) for w,b in zip(sub.weights,sub.caps))
        if s<=D:t=ideal_targets(sub,s)
        else:
            cap=tuple(max(F(0),b-d) for b in sub.caps)
            z=capped_cost(sub.weights,sub.gamma,cap,s-D)
            t=tuple(min(b,d)+y for b,y in zip(sub.caps,z['service']))
        for j,x in zip(ids,t):targets[j]=x
    return policy(data,book,tuple(targets),charges)


def solve(data,catalog,charges,B,budget,epsilon=F(1,1000),max_nodes=127,price_steps=4):
    """Globally valid original-budget interval; exponential search only in E-1."""
    started=time.perf_counter();a,rho=tuple(map(rat,catalog)),tuple(map(rat,charges));B,epsilon=rat(B),rat(epsilon)
    if not isinstance(budget,int) or isinstance(budget,bool) or budget<1 or epsilon<0 or max_nodes<1:raise ValueError('Invalid limits')
    if not a or len(a)!=len(rho) or a[0]<0 or a[-1]>1 or any(x>=y for x,y in zip(a,a[1:])) or any(x<0 for x in rho):raise ValueError('Invalid catalog')
    if not a[0]<=min(B,min(data.caps)) or B>data.cap_total:raise ValueError('Infeasible promise')
    groups=eligibility_groups(data,a);G=group_model(data,groups);E=len(groups);m=min(budget,len(a));cmap=dict(zip(a,rho))
    root=project_box(G,(a[0],)*E,G.caps,B);lo,hi=root
    prices={F(0)}
    if E>1 and price_steps:
        left,right=-max(data.gamma)-1,data.r+1
        for _ in range(price_steps):
            mid=(left+right)/2
            p=price_path(data,a,rho,B,m,groups,lo,hi,mid,reference_check=True)
            if p['total_min']<=B<=p['total_max']:
                prices.add(mid);break
            if p['total_min']>B:left=mid
            else:right=mid
        prices.update({left,right,(left+right)/2})
    prices=tuple(sorted(prices));cache={};best=None;nodes=[];heap=[];calls=0
    def incumbent(book,box=None):
        nonlocal best
        if E==1:
            candidate=recover(data,groups,book,(B,),cmap)
        else:
            if book not in cache:cache[book]=fixed_allocate(data,book,B,cmap)
            candidate=cache[book]
        if best is None or candidate['value']>best['value']:best=candidate
    warm=frontier(data,a,rho,ideal_targets(data,B),m)['at_most'][-1]
    incumbent(warm['book'])
    def evaluate(box,parent=None):
        nonlocal calls
        low,high=box;witnesses=[]
        for lam in prices:
            p=price_path(data,a,rho,B,m,groups,low,high,lam,tables=True);calls+=1
            if p is None:raise AssertionError('Box with no feasible anchor')
            witnesses.append(p);incumbent(p['book'])
        cert=min(witnesses,key=lambda z:z['upper']);idx=len(nodes)
        nodes.append(dict(id=idx,parent=parent,lower=low,upper_targets=high,bound=cert['upper'],witness=cert,children=None))
        heapq.heappush(heap,(-cert['upper'],idx))
    evaluate(root)
    dep=max(range(E),key=lambda j:G.weights[j]);axes=[j for j in range(E) if j!=dep]
    while heap and -heap[0][0]>best['value']+epsilon and len(nodes)+2<=max_nodes:
        _,idx=heapq.heappop(heap);node=nodes[idx];low,high=node['lower'],node['upper_targets']
        if not axes or max(G.weights[j]*(high[j]-low[j]) for j in axes)==0:raise AssertionError('Positive singleton gap')
        j=max(axes,key=lambda j:(G.weights[j]*(high[j]-low[j]),-j));cut=(low[j]+high[j])/2
        h1=list(high);h1[j]=cut;l2=list(low);l2[j]=cut;children=[]
        for raw in ((low,tuple(h1)),(tuple(l2),high)):
            box=project_box(G,*raw,B)
            if box is not None:children.append(len(nodes));evaluate(box,idx)
        node.update(children=children,split=(j,cut))
    upper=max([best['value']]+[-x[0] for x in heap]);gap=upper-best['value']
    return dict(schema='ndu-r49-eligibility-certificate-v1',status='COMPLETE' if gap<=epsilon else 'INTERRUPTED',
        model=asdict(data),groups=groups,catalog=a,charges=rho,promise=B,budget=m,requested_epsilon=epsilon,
        lower_bound=best['value'],upper_bound=upper,gap=gap,policy=best,nodes=nodes,leaves=tuple(i for _,i in heap),
        prices=prices,evaluated_nodes=len(nodes),oracle_calls=calls,raw_branches=len(data.caps),eligibility_groups=E,
        seconds=time.perf_counter()-started,scope='exact original-budget joint finite-catalog design; no pooling defect')
