"""Exact rational two-sided price paths and certified adaptive joint design.

The optimizer never changes the original installed-level budget, opening
charges, root equality, or realization ceilings. All upper bounds are rational.
No commercial/global optimization solver is used by this module.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from dataclasses import asdict
import sys, heapq, time
BASE = Path(__file__).resolve().parents[2] / 'or-r45-budgeted-compression-20260924' / 'code'
sys.path.insert(0, str(BASE))
from compression import Instance, rat, policy, frontier, ideal_targets, encode


def aggregate(data, catalog):
    """Exact types use cap, cost and eligible catalog prefix, not branch count."""
    groups = {}
    for j, (b, g, tau) in enumerate(zip(data.caps, data.gamma, data.ceilings)):
        signature = (b, g, sum(x <= tau for x in catalog))
        groups.setdefault(signature, []).append(j)
    ids = list(groups.values())
    small = Instance.make([data.caps[g[0]] for g in ids],
        [sum(data.weights[j] for j in g) for g in ids],
        [data.gamma[g[0]] for g in ids],
        [min(data.ceilings[j] for j in g) for g in ids], data.r, data.curvature)
    return small, tuple(tuple(g) for g in ids)


def project_box(data, lower, upper, B):
    """Exact coordinate projections of a box intersected with one equality."""
    lo, hi = tuple(map(rat, lower)), tuple(map(rat, upper))
    if len(lo) != len(data.caps) or len(hi) != len(lo):
        raise ValueError('Wrong box dimension')
    if any(l > u or l < 0 or u > b for l, u, b in zip(lo, hi, data.caps)):
        return None
    sl = sum(w*l for w,l in zip(data.weights, lo))
    su = sum(w*u for w,u in zip(data.weights, hi))
    if not sl <= B <= su: return None
    return (tuple(max(l, (B-su+w*u)/w) for w,l,u in zip(data.weights,lo,hi)),
            tuple(min(u, (B-sl+w*l)/w) for w,l,u in zip(data.weights,lo,hi)))


def branch_value(data, j, book, t):
    eligible = [a for a in book if a <= data.ceilings[j]]
    d = eligible[-1]
    if t >= d:
        return data.reward(d)-data.gamma[j]*(t-d)**2/2
    for u,v in zip(eligible, eligible[1:]):
        if u <= t <= v:
            return data.reward(u)+(t-u)*(data.reward(v)-data.reward(u))/(v-u)
    raise ValueError('Target below anchor')


def branch_support(data, j, book, lower, upper, price):
    """Independent scalar maximization at knots and clipped stationary tails."""
    lo, hi = max(lower, book[0]), upper
    if lo > hi: raise ValueError('Infeasible book for box')
    eligible = tuple(a for a in book if a <= data.ceilings[j])
    d, g = eligible[-1], data.gamma[j]
    points = {lo,hi} | {x for x in eligible if lo <= x <= hi}
    if g > 0 and hi >= d:
        points.add(min(hi,max(lo,d,d-price/g)))
    vals = [(branch_value(data,j,book,t)-price*t,t) for t in points]
    value = max(x for x,t in vals)
    opt = [t for x,t in vals if x == value]
    return value, min(opt), max(opt)


def fixed_allocate(data, book, B, charges, lower=None, upper=None):
    """Exact fixed-book concave allocation using derivative breakpoints.

    The simple reference sweep deliberately favors auditability over the
    inherited optimized water-level allocator. Complexity is polynomial.
    """
    k = len(data.caps)
    lower = tuple(F(0) for _ in range(k)) if lower is None else lower
    upper = data.caps if upper is None else upper
    lo = tuple(max(book[0],z) for z in lower)
    if any(l>u for l,u in zip(lo,upper)) or not sum(w*l for w,l in zip(data.weights,lo)) <= B <= sum(w*u for w,u in zip(data.weights,upper)):
        raise ValueError('Infeasible fixed-book equality')
    events = {data.r+1, -max(data.gamma,default=F(0))-1, F(0)}
    for j in range(k):
        e = [a for a in book if a <= data.ceilings[j]]
        for a,b in zip(e,e[1:]):
            if max(lo[j],a) < min(upper[j],b):
                events.add((data.reward(b)-data.reward(a))/(b-a))
        if upper[j] >= e[-1]:
            events.add(-data.gamma[j]*(max(lo[j],e[-1])-e[-1]))
            events.add(-data.gamma[j]*(upper[j]-e[-1]))
    def support(lam):
        out = [branch_support(data,j,book,lo[j],upper[j],lam) for j in range(k)]
        return out, sum(w*z[1] for w,z in zip(data.weights,out)), sum(w*z[2] for w,z in zip(data.weights,out))
    prev = None
    for lam in sorted(events,reverse=True):
        out, smin, smax = support(lam)
        if smin <= B <= smax: break
        if prev is not None and prev[2] < B < smin:
            oldlam,oldmin,oldmax = prev
            lam = oldlam-(oldlam-lam)*(B-oldmax)/(smin-oldmax)
            out,smin,smax = support(lam)
            if not smin <= B <= smax: raise AssertionError(('Sweep interpolation',B,smin,smax))
            break
        prev = (lam,smin,smax)
    else: raise AssertionError('No supporting multiplier')
    target = [z[1] for z in out]; residual = B-smin
    for j,w in enumerate(data.weights):
        take = min(residual,w*(out[j][2]-target[j]))
        target[j] += take/w; residual -= take
    assert residual == 0
    ans = policy(data,book,tuple(target),charges)
    assert ans['gross'] == lam*B+sum(w*z[0] for w,z in zip(data.weights,out))
    ans['allocation_price'] = lam
    return ans


def price_path(data, catalog, charges, B, budget, lower, upper, price, tables=False):
    """Exact support over ALL books and box targets, using a priced peak.

    For positive price the increasing side owns upper-target crossings;
    the decreasing side owns lower-target crossings. The peak owns intervals
    containing it. Dropping the decreasing side is in general invalid.
    """
    a, rho, lam = tuple(catalog), tuple(charges), rat(price)
    n, m, k = len(a), min(budget,len(a)), len(data.caps)
    if n == 0 or m < 1: raise ValueError('Nonempty catalog and budget required')
    g = tuple(data.reward(x)-lam*x for x in a)
    anchors = [i for i,x in enumerate(a) if x <= min(upper) and
               sum(w*max(l,x) for w,l in zip(data.weights,lower)) <= B]
    if not anchors: return None
    def service(j,u):
        low = max(F(0),lower[j]-u); high = upper[j]-u
        gam = data.gamma[j]
        if lam >= 0: y = low
        elif gam == 0: y = high
        else: y = min(high,max(low,-lam/gam))
        return -gam*y*y/2-lam*y
    up, down = {}, {}
    for i,u in enumerate(a):
        for v in range(i+1,n):
            z = a[v]; slope = (g[v]-g[i])/(z-u)
            up[i,v] = sum((w*(g[i]+slope*(h-u) if z<=tau else g[i]+service(j,u))
                for j,(w,h,tau) in enumerate(zip(data.weights,upper,data.ceilings)) if u<=h<z),F(0))
            if lam > 0:
                down[i,v] = sum((w*(g[i]+slope*(l-u) if z<=tau else
                      g[i]-gam*(l-u)**2/2-lam*(l-u))
                    for w,l,tau,gam in zip(data.weights,lower,data.ceilings,data.gamma) if u<=l<z),F(0))
    alpha = [[None]*n for _ in range(m+1)]
    apre = [[None]*n for _ in range(m+1)]
    for i in anchors: alpha[1][i] = -rho[i]
    for r in range(2,m+1):
        for v in range(n):
            options = [(alpha[r-1][i]+up[i,v]-rho[v],-i,i)
                       for i in range(v) if alpha[r-1][i] is not None and g[i]<=g[v]]
            if options:
                alpha[r][v],_,apre[r][v] = max(options)
    middle = [F(0)]*n; beta = None; bnext = None
    if lam <= 0:
        tail = [sum((w*(g[i]+service(j,u)) for j,(w,h) in enumerate(zip(data.weights,upper)) if h>=u),F(0)) for i,u in enumerate(a)]
        candidates = [(alpha[r][i]+tail[i],-r,-i,r,i) for r in range(1,m+1) for i in range(n) if alpha[r][i] is not None]
    else:
        tail = [sum((w*(g[i]-gam*(l-u)**2/2-lam*(l-u)) for w,l,gam in zip(data.weights,lower,data.gamma) if l>=u),F(0)) for i,u in enumerate(a)]
        middle = [sum((w*g[i] for w,l,h in zip(data.weights,lower,upper) if l<u<=h),F(0)) for i,u in enumerate(a)]
        beta = [[None]*n]+[list(tail) for _ in range(m)]
        bnext = [[None]*n for _ in range(m+1)]
        for s in range(2,m+1):
            for i in range(n):
                options = [(tail[i],0,None)]+[(down[i,v]-rho[v]+beta[s-1][v],-v-1,v) for v in range(i+1,n) if g[v]<=g[i]]
                beta[s][i],_,bnext[s][i] = max(options,key=lambda x:(x[0],x[1]))
        candidates = [(alpha[r][i]+middle[i]+beta[m-r+1][i],-r,-i,r,i) for r in range(1,m+1) for i in range(n) if alpha[r][i] is not None]
    value,_,_,r,pivot = max(candidates)
    ids = [pivot]; cur = pivot; rr = r
    while rr>1:
        cur = apre[rr][cur]; ids.append(cur); rr-=1
    ids.reverse()
    if lam>0:
        cur,s = pivot,m-r+1
        while s>1 and bnext[s][cur] is not None:
            cur=bnext[s][cur]; ids.append(cur); s-=1
    book = tuple(a[i] for i in ids)
    support = [branch_support(data,j,book,lower[j],upper[j],lam) for j in range(k)]
    direct = sum(w*z[0] for w,z in zip(data.weights,support))-sum(rho[i] for i in ids)
    assert value == direct, ('Path reconstruction mismatch',price,book,value,direct,lower,upper)
    ans = dict(price=lam,support=value,upper=lam*B+value,book=book,
               target_min=tuple(z[1] for z in support),target_max=tuple(z[2] for z in support),
               total_min=sum(w*z[1] for w,z in zip(data.weights,support)),
               total_max=sum(w*z[2] for w,z in zip(data.weights,support)))
    if tables: ans.update(alpha=alpha[1:],beta=None if beta is None else beta[1:])
    return ans


def exhaustive_price(data,a,rho,B,m,lo,hi,lam):
    best=None
    for s in range(1,min(m,len(a))+1):
        for ids in combinations(range(len(a)),s):
            book=tuple(a[i] for i in ids)
            if book[0]>min(hi) or sum(w*max(l,book[0]) for w,l in zip(data.weights,lo))>B: continue
            val=sum(w*branch_support(data,j,book,lo[j],hi[j],lam)[0] for j,w in enumerate(data.weights))-sum(rho[i] for i in ids)
            if best is None or val>best: best=val
    return None if best is None else best+lam*B


def exhaustive_joint(data,a,rho,B,m):
    best=None; cmap=dict(zip(a,rho))
    for s in range(1,min(m,len(a))+1):
        for book in combinations(a,s):
            if book[0]>min(B,min(data.caps)): continue
            p=fixed_allocate(data,book,B,cmap)
            if best is None or p['value']>best['value']: best=p
    return best


def root_prices(data,a,rho,B,m,lo,hi,steps):
    left,right=-max(data.gamma)-1,data.r+1
    prices={F(0),left,right}
    for _ in range(steps):
        mid=(left+right)/2; prices.add(mid)
        p=price_path(data,a,rho,B,m,lo,hi,mid)
        if p['total_min']<=B<=p['total_max']: return tuple(sorted({F(0),mid}))
        if p['total_min']>B: left=mid
        else: right=mid
    return tuple(sorted({F(0),left,right,(left+right)/2}))


def solve(data,catalog,charges,B,budget,epsilon=F(1,1000),max_nodes=10000,
          seconds_limit=None,price_steps=10,aggregate_types=True,record_tables=True):
    a,rho=tuple(map(rat,catalog)),tuple(map(rat,charges)); B,epsilon=rat(B),rat(epsilon)
    if epsilon<0 or isinstance(budget,bool) or not isinstance(budget,int) or budget<1: raise ValueError('Invalid budget/tolerance')
    if len(a)!=len(rho) or not a or any(x>=y for x,y in zip(a,a[1:])) or a[0]<0 or a[-1]>1 or any(x<0 for x in rho): raise ValueError('Invalid catalog/charges')
    if a[0]>min(B,min(data.caps)) or B>data.cap_total: raise ValueError('Infeasible promise')
    original=data; data,groups=aggregate(data,a) if aggregate_types else (data,tuple((j,) for j in range(len(data.caps))))
    k=len(data.caps); m=min(budget,len(a)); cmap=dict(zip(a,rho)); started=time.perf_counter()
    root=project_box(data,(a[0],)*k,data.caps,B)
    lo,hi=root
    prices=root_prices(data,a,rho,B,m,lo,hi,price_steps)
    cache={}; best=None; nodes=[]; heap=[]; evaluated=0; oracle_calls=0
    def incumbent(book):
        nonlocal best
        if book not in cache: cache[book]=fixed_allocate(data,book,B,cmap)
        ans=cache[book]
        if best is None or ans['value']>best['value']: best=ans
    # One declared feasible warm start; never used as an upper bound.
    ft=frontier(data,a,rho,ideal_targets(data,B),m)['at_most'][-1]
    incumbent(ft['book'])
    def evaluate(box,parent=None):
        nonlocal oracle_calls,evaluated
        low,high=box
        witnesses=[]
        for lam in prices:
            p=price_path(data,a,rho,B,m,low,high,lam,tables=record_tables)
            oracle_calls+=1; witnesses.append(p); incumbent(p['book'])
        certificate=min(witnesses,key=lambda z:z['upper'])
        idx=len(nodes)
        node=dict(id=idx,parent=parent,lower=low,upper_targets=high,bound=certificate['upper'],witness=certificate,children=None)
        nodes.append(node); evaluated+=1
        heapq.heappush(heap,(-node['bound'],idx))
    evaluate(root)
    dependent=max(range(k),key=lambda j:data.weights[j]); split_axes=[j for j in range(k) if j!=dependent]
    status='COMPLETE'
    while heap:
        current=-heap[0][0]
        if current<=best['value']+epsilon: break
        if evaluated+2>max_nodes or (seconds_limit is not None and time.perf_counter()-started>=seconds_limit):
            status='INTERRUPTED'; break
        _,idx=heapq.heappop(heap); node=nodes[idx]
        low,high=node['lower'],node['upper_targets']
        if not split_axes or max(data.weights[j]*(high[j]-low[j]) for j in split_axes)==0:
            raise AssertionError('Singleton target cell has a positive certification gap')
        j=max(split_axes,key=lambda j:(data.weights[j]*(high[j]-low[j]),-j)); cut=(low[j]+high[j])/2
        h1=list(high); h1[j]=cut; l2=list(low); l2[j]=cut
        children=[]
        for raw in ((low,tuple(h1)),(tuple(l2),high)):
            box=project_box(data,*raw,B)
            if box is not None:
                child=len(nodes); evaluate(box,idx); children.append(child)
        node['children']=children; node['split']=(j,cut)
    upper=max([best['value']]+[-z[0] for z in heap])
    # Closed leaves remain in heap. The union of their cells covers the root.
    types_policy=best
    expanded=[None]*len(original.caps)
    for t,group in zip(best['targets'],groups):
        for j in group: expanded[j]=t
    lifted=policy(original,best['book'],tuple(expanded),cmap)
    assert lifted['value']==best['value']
    return dict(schema='ndu-r46-box-certificate-v1',status=status,
                model=asdict(data),original_model=asdict(original),groups=groups,
                catalog=a,charges=rho,promise=B,budget=m,requested_epsilon=epsilon,
                epsilon_guarantee=epsilon if upper-best['value']<=epsilon else None,
                lower_bound=best['value'],upper_bound=upper,gap=upper-best['value'],
                policy=lifted,type_policy=types_policy,prices=prices,nodes=nodes,
                leaves=tuple(idx for _,idx in heap),evaluated_nodes=evaluated,
                oracle_calls=oracle_calls,distinct_books=len(cache),raw_branches=len(original.caps),
                types=k,seconds=time.perf_counter()-started,
                scope='global original-budget joint catalog design; exact rational interval')
