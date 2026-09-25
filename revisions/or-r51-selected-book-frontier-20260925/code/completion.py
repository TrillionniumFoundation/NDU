"""Original-budget selected-prefix search with exact rational upper certificates.

The fixed-book sweep is inherited mathematics, not claimed as a new result.
The search state fixes selected symbols, not full-catalog eligibility classes.
All computations are exact except recorded wall-clock times and stopping limits.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from dataclasses import asdict
from bisect import bisect_right
from itertools import combinations
import sys, time, heapq
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'revisions/or-r49-dispersion-certificates-20260925/code'))
from pooling import Instance, capped_cost, policy, encode, rat
from box_solver import branch_support


def validate(data, catalog, charges, B, budget):
    a, rho, B = tuple(map(rat,catalog)), tuple(map(rat,charges)), rat(B)
    if not a or len(a)!=len(rho) or a[0]<0 or a[-1]>1 or any(x>=y for x,y in zip(a,a[1:])) or any(x<0 for x in rho):
        raise ValueError('Ordered normalized catalog and nonnegative rational charges required.')
    if isinstance(budget,bool) or not isinstance(budget,int) or budget<1: raise ValueError('Positive integer budget required.')
    if not a[0]<=min(data.caps) or not a[0]<=B<=data.cap_total: raise ValueError('Infeasible root promise or catalog anchor.')
    return a,rho,B,min(budget,len(a))


def fixed_book(data, book, B, charges):
    """Fast exact implementation of the inherited common-interpolant sweep.

    All eligible curves are restrictions of one book interpolant. Their effective
    caps are min(b_j,last eligible symbol). Pool those caps before buying service.
    A scalar support price is returned for independent primal-dual checking.
    """
    c=tuple(book);k=len(data.caps)
    if not c or any(x>=y for x,y in zip(c,c[1:])) or c[0]>min(data.caps) or not c[0]<=B<=data.cap_total:
        raise ValueError('Infeasible fixed book.')
    d=tuple(c[bisect_right(c,tau)-1] for tau in data.ceilings)
    e=tuple(min(b,x) for b,x in zip(data.caps,d));D=sum(w*x for w,x in zip(data.weights,e))
    if B<D:
        residual,weight=B,F(1);level=c[0]
        for j in sorted(range(k),key=lambda j:e[j]):
            level=residual/weight
            if level<=e[j]:break
            residual-=data.weights[j]*e[j];weight-=data.weights[j]
        target=tuple(min(x,level) for x in e)
        if level==c[0] and B==c[0]:lam=data.r+1
        else:
            idx=bisect_right(c,level)-1
            lam=(data.reward(c[idx+1])-data.reward(c[idx]))/(c[idx+1]-c[idx])
    else:
        capacities=tuple(b-x for b,x in zip(data.caps,e))
        z=capped_cost(data.weights,data.gamma,capacities,B-D)
        target=tuple(x+y for x,y in zip(e,z['service']));lam=-z['marginal']
    ans=policy(data,c,target,charges)
    ans['allocation_price']=lam
    # The independent checker, not this reconstruction, supplies the certificate.
    return ans


def priced_prefix(data,catalog,charges,B,budget,mandatory,price,tables=False):
    """Exact scalar-price support over books containing the first p candidates.

    Mandatory candidates are the selected prefix of a binary include/exclude
    search state. Edges cannot jump over its next mandatory level; stopping is
    forbidden until the last mandatory level has been visited. The two-sided
    path ownership is inherited from R46. This constrained oracle is new here.
    """
    a,rho,lam=tuple(catalog),tuple(charges),rat(price)
    n,m,p=len(a),min(budget,len(a)),mandatory
    if not 0<=p<=m:raise ValueError('Invalid mandatory prefix length.')
    score=tuple(data.reward(x)-lam*x for x in a)
    anchors=[i for i,x in enumerate(a) if x<=min(data.caps) and x<=B and (p==0 or i==0)]
    if not anchors:return None
    def allowed(i,v):return i>=p-1 or v==i+1
    def can_stop(i):return i>=p-1
    def service(j,u):
        hi=data.caps[j]-u;gam=data.gamma[j]
        y=F(0) if lam>=0 else hi if gam==0 else min(hi,-lam/gam)
        return -gam*y*y/2-lam*y
    up={};down={}
    for i,u in enumerate(a):
        for v in range(i+1,n):
            if not allowed(i,v):continue
            z=a[v];slope=(score[v]-score[i])/(z-u)
            up[i,v]=sum((w*(score[i]+slope*(b-u) if z<=tau else score[i]+service(j,u))
                for j,(w,b,tau) in enumerate(zip(data.weights,data.caps,data.ceilings)) if u<=b<z),F(0))
            # The root target box is [0,b_j]. A positive anchor is accounted for
            # by the peak term, not by pretending the target can be below it.
            if lam>0:
                down[i,v]=sum((w*score[i] for w in data.weights),F(0)) if u==0 else F(0)
    alpha=[[None]*n for _ in range(m+1)];prev=[[None]*n for _ in range(m+1)]
    for i in anchors:alpha[1][i]=-rho[i]
    for r in range(2,m+1):
        for v in range(n):
            opts=[(alpha[r-1][i]+up[i,v]-rho[v],-i,i) for i in range(v)
                  if alpha[r-1][i] is not None and allowed(i,v) and score[i]<=score[v]]
            if opts:alpha[r][v],_,prev[r][v]=max(opts)
    beta=None;nxt=None
    if lam<=0:
        tail=[sum((w*(score[i]+service(j,u)) for j,(w,b) in enumerate(zip(data.weights,data.caps)) if b>=u),F(0)) for i,u in enumerate(a)]
        opts=[(alpha[r][i]+tail[i],-r,-i,r,i) for r in range(1,m+1) for i in range(n) if alpha[r][i] is not None and can_stop(i)]
    else:
        # With lower bound zero only the zero candidate can own a lower tail.
        tail=[score[i] if u==0 else F(0) for i,u in enumerate(a)]
        middle=[sum((w*score[i] for w,b in zip(data.weights,data.caps) if 0<u<=b),F(0)) for i,u in enumerate(a)]
        beta=[[None]*n for _ in range(m+1)];nxt=[[None]*n for _ in range(m+1)]
        for s in range(1,m+1):
            for i in range(n-1,-1,-1):
                choices=[(tail[i],0,None)] if can_stop(i) else []
                if s>1:
                    choices += [(down[i,v]-rho[v]+beta[s-1][v],-v-1,v) for v in range(i+1,n)
                                if allowed(i,v) and score[v]<=score[i] and beta[s-1][v] is not None]
                if choices:beta[s][i],_,nxt[s][i]=max(choices,key=lambda x:(x[0],x[1]))
        opts=[(alpha[r][i]+middle[i]+beta[m-r+1][i],-r,-i,r,i) for r in range(1,m+1) for i in range(n)
              if alpha[r][i] is not None and beta[m-r+1][i] is not None]
    if not opts:return None
    val,_,_,r,pivot=max(opts);ids=[pivot];i=pivot;rr=r
    while rr>1:i=prev[rr][i];ids.append(i);rr-=1
    ids.reverse()
    if lam>0:
        i,s=pivot,m-r+1
        while s>1 and nxt[s][i] is not None:i=nxt[s][i];ids.append(i);s-=1
    book=tuple(a[i] for i in ids)
    support=[branch_support(data,j,book,book[0],data.caps[j],lam) for j in range(len(data.caps))]
    direct=sum(w*z[0] for w,z in zip(data.weights,support))-sum(rho[i] for i in ids)
    assert direct==val,('Mandatory price path',p,price,book,val,direct)
    assert set(a[:p])<=set(book)
    ans=dict(kind='price',price=lam,upper=lam*B+val,book=book,
        mean_low=sum(w*z[1] for w,z in zip(data.weights,support)),mean_high=sum(w*z[2] for w,z in zip(data.weights,support)))
    if tables:ans.update(alpha=alpha[1:],beta=None if beta is None else beta[1:])
    return ans


def solve(data,catalog,charges,B,budget,*,node_limit=100000,time_limit=None,price_steps=2,screen=True):
    """Best-bound include/exclude tree; every interrupted answer is certified.

    price_steps=0 uses only a free-completion bound; positive values evaluate
    the mandatory-prefix price oracle and node-local bisection. A time limit
    is checked between oracle calls, not claimed to interrupt an atomic call.
    """
    a,rho,B,m=validate(data,catalog,charges,B,budget)
    if node_limit<1 or price_steps<0:raise ValueError('Invalid search allowance.')
    start=time.perf_counter();cmap=dict(zip(a,rho));full=fixed_book(data,a,B,cmap)
    best=fixed_book(data,(a[0],),B,cmap);allocations=2;price_calls=0
    # Feasible greedy incumbents do not alter the upper cover or its scope.
    current=best
    for _ in range(1,m):
        candidates=[]
        for x in a:
            if x in current['book']:continue
            q=fixed_book(data,tuple(sorted(current['book']+(x,))),B,cmap);allocations+=1
            candidates.append(q)
        q=max(candidates,key=lambda x:x['value']) if candidates else current
        if q['value']<=current['value']:break
        current=q
        if current['value']>best['value']:best=current
    screening_lower=best['value'];free_gross=full['gross']
    removed=[i for i,cost in enumerate(rho) if screen and free_gross-cost<screening_lower]
    active=[i for i in range(len(a)) if i not in removed]
    ac=tuple(a[i] for i in active);rc=tuple(rho[i] for i in active);n=len(ac)
    nodes=[];queue=[]
    def eval_node(cursor,selected):
        nonlocal best,allocations,price_calls
        node={'cursor':cursor,'selected':selected,'state':'OPEN'};nid=len(nodes);nodes.append(node)
        terminal=len(selected)==m or cursor==n
        ids=selected if terminal else selected+tuple(range(cursor,n))
        if not ids or ac[ids[0]]>min(data.caps) or ac[ids[0]]>B:
            node['state']='INFEASIBLE';return nid
        book=tuple(ac[i] for i in ids);q=fixed_book(data,book,B,cmap);allocations+=1
        committed=sum(rc[i] for i in selected)
        ub=q['gross']-committed
        if terminal:ub=q['value']
        node['bound']={'kind':'free','price':q['allocation_price'],'upper':ub}
        if selected:
            incumbent=q if terminal else fixed_book(data,tuple(ac[i] for i in selected),B,cmap)
            allocations+=not terminal
            if incumbent['value']>best['value']:best=incumbent
        if not terminal and price_steps and ub>best['value']:
            prices=[q['allocation_price']];low=-max(data.gamma)-1;high=data.r+1
            for step in range(price_steps):
                lam=prices[-1]
                z=priced_prefix(data,book,tuple(cmap[x] for x in book),B,m,len(selected),lam,tables=True);price_calls+=1
                if z is None:raise AssertionError('Feasible completion missing price path')
                candidate=fixed_book(data,z['book'],B,cmap);allocations+=1
                if candidate['value']>best['value']:best=candidate
                if z['upper']<node['bound']['upper']:node['bound']={key:z[key] for key in ['kind','price','upper','alpha','beta']}
                if node['bound']['upper']<=best['value']:break
                if B<z['mean_low']:low=max(low,lam)
                elif B>z['mean_high']:high=min(high,lam)
                else:break
                prices.append((low+high)/2)
        if node['bound']['upper']<=best['value']:node['state']='CLOSED'
        else:heapq.heappush(queue,(-node['bound']['upper'],nid))
        return nid
    eval_node(0,())
    while queue:
        neg,nid=heapq.heappop(queue);node=nodes[nid]
        if -neg<=best['value']:node['state']='CLOSED';continue
        if len(nodes)+2>node_limit or (time_limit is not None and time.perf_counter()-start>=time_limit):
            heapq.heappush(queue,(neg,nid));break
        i,chosen=node['cursor'],node['selected']
        if i>=n or len(chosen)>=m:raise AssertionError('A terminal bound was not closed')
        left=eval_node(i+1,chosen);right=eval_node(i+1,chosen+(i,))
        node['state']='SPLIT';node['children']=[left,right]
    for node in nodes:
        if node['state']=='OPEN' and node['bound']['upper']<=best['value']:node['state']='CLOSED'
    upper=max([best['value']]+[z['bound']['upper'] for z in nodes if z['state']=='OPEN'])
    # State indices are reconstructed by the verifier; they are not trusted.
    compact=[{k:v for k,v in z.items() if k not in ['cursor','selected']} for z in nodes]
    return dict(schema='ndu-r51-selected-prefix-v1',model=asdict(data),catalog=a,charges=rho,promise=B,budget=m,
        screening=dict(price=full['allocation_price'],gross_upper=free_gross,lower=screening_lower,removed=removed),
        active=active,policy=best,nodes=compact,lower_bound=best['value'],upper_bound=upper,gap=upper-best['value'],
        status='EXACT' if upper==best['value'] else 'OPEN',evaluated_nodes=len(nodes),allocation_calls=allocations,
        price_calls=price_calls,price_steps=price_steps,node_limit=node_limit,time_limit=time_limit,seconds=time.perf_counter()-start)


def enumerate_joint(data,a,rho,B,m):
    """Unpruned baseline using the new fast sweep, separate from tree logic."""
    charges=dict(zip(a,rho));best=None;calls=0
    for s in range(1,min(m,len(a))+1):
        for c in combinations(a,s):
            if c[0]>min(data.caps) or c[0]>B:continue
            q=fixed_book(data,c,B,charges);calls+=1
            if best is None or q['value']>best['value']:best=q
    return best,calls
