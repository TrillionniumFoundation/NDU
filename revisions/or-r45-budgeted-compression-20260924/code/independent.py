"""Independent direct-support enumeration and direct mixed-integer formulation.

This file does not import compression, canonical branch rules, price dynamic
programming, or the inherited inner allocator. The direct mixed-integer model
contains every installed level, every branch-level usage indicator, every
probability, and the pre-draw intermediate service explicitly. Its numerical
HiGHS bounds are reported as numerical bounds, not exact-rational certificates.
"""
from fractions import Fraction as F
from itertools import combinations
import time


def direct_branch(r, q, gamma, ceiling, book, target):
    f = lambda x: r*x-q*x*x/2
    candidates = []
    for a in book:
        if a <= target:
            y = target-a
            if y+a <= ceiling:
                candidates.append(f(a)-gamma*y*y/2)
    for a, b in combinations(book, 2):
        # Optimizing pre-draw y over this support chooses its smallest feasible
        # value, because the chord reward increases and the cost decreases as
        # the terminal mean increases. Singletons cover degenerate supports.
        if a <= target <= b and b <= ceiling:
            p = (target-a)/(b-a)
            candidates.append((1-p)*f(a)+p*f(b))
    if not candidates: raise ValueError('No feasible explicit support.')
    return max(candidates)


def exhaustive_fixed(data, catalog, charges, targets, budget):
    f = lambda book: sum(w*direct_branch(data.r, data.curvature, g, tau, book, t)
        for w, g, tau, t in zip(data.weights, data.gamma, data.ceilings, targets))
    exact = []
    for count in range(1, min(budget, len(catalog))+1):
        best = None
        for ids in combinations(range(len(catalog)), count):
            book = tuple(catalog[i] for i in ids)
            if book[0] > min(targets): continue
            value = f(book)-sum(charges[i] for i in ids)
            if best is None or value > best['value']:
                best = dict(value=value, book=book)
        exact.append(best)
    at_most = []
    for i in range(len(exact)):
        at_most.append(max((p for p in exact[:i+1] if p is not None), key=lambda p:p['value']))
    return dict(exact=exact, at_most=at_most)


def verify_policy(data, catalog, charges, policy, promise, budget):
    """Exact arithmetic checks of the uneliminated original policy constraints."""
    book = tuple(F(x) for x in policy['book'])
    target = tuple(F(x) for x in policy['targets'])
    ys = tuple(F(x) for x in policy['intermediate'])
    laws = tuple(tuple((F(x), F(p)) for x, p in law) for law in policy['lotteries'])
    if not book or len(book) != len(set(book)) or len(book) > budget: raise ValueError('Memory')
    if any(x not in catalog for x in book): raise ValueError('Catalog')
    if any(len(z) != len(data.caps) for z in (target, ys, laws)): raise ValueError('Dimension')
    gross = F(0)
    for j, (y, law, t) in enumerate(zip(ys, laws, target)):
        if y < 0 or sum(p for x, p in law) != 1: raise ValueError('Normalization/service')
        if any(p < 0 or x not in book for x, p in law): raise ValueError('Support')
        if y+sum(p*x for x, p in law) != t or t > data.caps[j]: raise ValueError('Target/cap')
        if any(y+x > data.ceilings[j] for x, p in law if p > 0): raise ValueError('Risk')
        gross += data.weights[j]*(sum(p*(data.r*x-data.curvature*x*x/2) for x, p in law)-data.gamma[j]*y*y/2)
    if sum(w*t for w, t in zip(data.weights, target)) != promise: raise ValueError('Root promise')
    charge = sum(charges[catalog.index(x)] for x in book)
    if gross-charge != F(policy['value']) or charge != F(policy['charge']): raise ValueError('Payoff/charge')
    return True


def direct_milp(data, catalog, charges, promise, budget, segments=32,
                envelope='tangent', time_limit=20):
    import numpy as np
    from scipy.optimize import milp, Bounds, LinearConstraint
    from scipy.sparse import coo_array
    k, n = len(data.caps), len(catalog)
    # open[n], support[k*n], probability[k*n], intermediate[k], epigraph[k]
    use = n; prob = n+k*n; ybase = n+2*k*n; hbase = ybase+k; nv = hbase+k
    c = np.zeros(nv); lb = np.zeros(nv); ub = np.full(nv, np.inf)
    integer = np.zeros(nv, dtype=int); integer[:prob] = 1; ub[:ybase] = 1
    c[:n] = list(map(float, charges))
    rows, cols, vals, lo, hi = [], [], [], [], []
    def add(entries, lower=-np.inf, upper=np.inf):
        z = len(lo); lo.append(lower); hi.append(upper)
        for col, value in entries.items():
            if value: rows.append(z); cols.append(col); vals.append(float(value))
    add({l:1 for l in range(n)}, upper=budget)
    aggregate = {}
    for j in range(k):
        b, w, gamma, tau = map(float, (data.caps[j], data.weights[j], data.gamma[j], data.ceilings[j]))
        y, h = ybase+j, hbase+j; ub[y] = b; c[h] = w
        psum, total = {}, {y:1}; aggregate[y] = w
        for l, aa in enumerate(catalog):
            a = float(aa); z = use+j*n+l; p = prob+j*n+l
            psum[p] = 1; total[p] = a; aggregate[p] = w*a
            c[p] = -w*(float(data.r)*a-float(data.curvature)*a*a/2)
            add({p:1,z:-1}, upper=0); add({z:1,l:-1}, upper=0)
            if aa > data.ceilings[j]: ub[p] = ub[z] = 0
            M = max(0.0, b+a-tau)
            add({y:1,z:M}, upper=tau-a+M)
        add(psum,1,1); add(total,upper=b)
        nodes = np.linspace(0,b,segments+1)
        if envelope == 'tangent':
            for x in nodes: add({h:1,y:-gamma*x}, lower=-gamma*x*x/2)
        elif envelope == 'secant':
            for a, d in zip(nodes,nodes[1:]):
                add({h:1,y:-gamma*(a+d)/2}, lower=-gamma*a*d/2)
        else: raise ValueError('Unknown quadratic envelope.')
    add(aggregate,float(promise),float(promise))
    mat = coo_array((np.array(vals),(np.array(rows,dtype=np.int32),np.array(cols,dtype=np.int32))),shape=(len(lo),nv)).tocsc()
    started=time.perf_counter()
    result=milp(c,integrality=integer,bounds=Bounds(lb,ub),
                constraints=LinearConstraint(mat,np.array(lo),np.array(hi)),
                options={'mip_rel_gap':1e-9,'time_limit':float(time_limit)})
    out=dict(status=int(result.status),message=result.message,seconds=time.perf_counter()-started,
             formulation='direct support-indicator probability/service MILP',envelope=envelope,
             segments=segments,variables=nv,binaries=int(integer.sum()),constraints=len(lo),
             approximation_error=sum(float(w*g*b*b)/(8*segments*segments)
                 for w,g,b in zip(data.weights,data.gamma,data.caps)),
             bound_scope='floating-point HiGHS global solver bound, not a rational proof')
    dual=getattr(result,'mip_dual_bound',None)
    out['numerical_upper']=None if dual is None else -float(dual)
    out['mip_gap']=None if getattr(result,'mip_gap',None) is None else float(result.mip_gap)
    if result.x is not None:
        x=result.x; actual=0.0
        for j,w in enumerate(data.weights):
            actual+=float(w)*(sum(x[prob+j*n+l]*(float(data.r)*float(a)-float(data.curvature)*float(a)**2/2)
                for l,a in enumerate(catalog))-float(data.gamma[j])*x[ybase+j]**2/2)
        actual-=sum(float(rho)*round(x[l]) for l,rho in enumerate(charges))
        v=mat@x
        residual=max(float(np.max(np.maximum(np.array(lo)-v,0))),float(np.max(np.maximum(v-np.array(hi),0))),
                     float(np.max(np.abs(x[:prob]-np.rint(x[:prob])))))
        out.update(value=actual,objective=-float(result.fun),max_model_residual=residual,
                   installed=[str(a) for l,a in enumerate(catalog) if x[l]>.5],
                   probabilities=x[prob:ybase].reshape(k,n).tolist(),intermediate=x[ybase:hbase].tolist())
    return out
