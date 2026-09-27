"""Exact all-promise, bounded-overrun allocation and certified catalog design.

Rational inputs only. Complexity is polynomial for a fixed book and exponential
in the selected-symbol budget for a catalog. No floating-point optimization.
The eligibility prefix is branch-specific; the root promise is never rounded.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations
from bisect import bisect_right
from pathlib import Path
import sys

OLD = Path(__file__).resolve().parents[2] / 'or-r39-robust-quantizer-20260924' / 'code'
sys.path.append(str(OLD))
from catalog import Model, rational

@dataclass(frozen=True)
class Allocation:
    value: F
    targets: tuple[F, ...]
    multiplier: F
    dual_bound: F
    intermediate: tuple[F, ...]
    lotteries: tuple[tuple[tuple[F, F], ...], ...]


def eligible(model, j, book, delta):
    return book[:bisect_right(book, model.caps[j]+delta)]


def branch_rule(model, j, book, t, delta):
    """Canonical optimum at the EXACT branch target t, including risk equality."""
    c = eligible(model, j, book, delta)
    if not c or not c[0] <= t <= model.caps[j]:
        raise ValueError('Infeasible branch target or empty eligible prefix.')
    if t >= c[-1]:
        return t-c[-1], ((c[-1], F(1)),)
    i = bisect_right(c, t)-1
    u, v = c[i:i+2]
    return F(0), tuple((x, p) for x, p in
                       ((u, (v-t)/(v-u)), (v, (t-u)/(v-u))) if p)


def response(model, j, book, t, delta):
    y, draws = branch_rule(model, j, book, t, delta)
    return sum((p*model.reward(c) for c, p in draws), F(0))-model.gamma[j]*y*y/2


def branch_maximum(model, j, book, lam, delta):
    """Independent supporting-price oracle: kinks, cap and tail stationary point."""
    c = eligible(model, j, book, delta)
    b, g = model.caps[j], model.gamma[j]
    scored = [(model.reward(x)-lam*x,x) for x in c if x <= b]
    candidates = {b}
    if b > c[-1] and g:
        candidates.add(max(c[-1], min(b, c[-1]-lam/g)))
    scored.extend((response(model,j,book,t,delta)-lam*t,t) for t in candidates)
    best = max(v for v, _ in scored)
    ties = [t for v, t in scored if v == best]
    return best, min(ties), max(ties)


def certify(model, book, B, delta, targets, lam):
    if len(targets) != len(model.caps):
        raise ValueError('Wrong target dimension.')
    if sum(p*t for p,t in zip(model.probabilities,targets)) != B:
        raise ValueError('Nonzero exact root promise residual.')
    ys, laws, value = [], [], F(0)
    for j, (p,t) in enumerate(zip(model.probabilities,targets)):
        y, draws = branch_rule(model,j,book,t,delta)
        if sum(a for _,a in draws) != 1:
            raise ValueError('Lottery does not normalize.')
        if any(a < 0 or y+c > model.caps[j]+delta for c,a in draws):
            raise ValueError('Risk/support violation.')
        if y+sum(c*a for c,a in draws) != t:
            raise ValueError('Branch promise not preserved.')
        ys.append(y); laws.append(draws)
        value += p*(sum(a*model.reward(c) for c,a in draws)-model.gamma[j]*y*y/2)
    dual = lam*B+sum(p*branch_maximum(model,j,book,lam,delta)[0]
                     for j,p in enumerate(model.probabilities))
    if value != dual:
        raise ValueError('Nonzero exact supporting-price gap.')
    return Allocation(value, tuple(targets), lam, dual, tuple(ys), tuple(laws))


def solve_allocation(model: Model, codebook, promise, delta=0) -> Allocation:
    book, B, delta = tuple(map(rational,codebook)), rational(promise), rational(delta)
    if not book or any(u >= v for u,v in zip(book,book[1:])):
        raise ValueError('Nonempty strictly increasing codebook required.')
    bar = sum(p*b for p,b in zip(model.probabilities,model.caps))
    if not 0 <= book[0] <= min(B,min(model.caps)) or book[-1] > 1:
        raise ValueError('Infeasible book.')
    if not B <= bar or delta < 0:
        raise ValueError('Invalid promise or negative tolerance.')
    p,b,g = model.probabilities, model.caps, model.gamma
    k = len(b)
    t, need = [book[0]]*k, B-book[0]
    def finish(lam):
        return certify(model,book,B,delta,tuple(t),lam)
    for u,v in zip(book,book[1:]):
        slope = model.r-model.q*(u+v)/2
        cap = [max(F(0),min(b[j],v)-u) if v <= b[j]+delta else F(0)
               for j in range(k)]
        room = sum(pj*d for pj,d in zip(p,cap))
        if need <= room:
            for j,d in enumerate(cap):
                take = min(need,p[j]*d); t[j] += take/p[j]; need -= take
            return finish(slope)
        for j,d in enumerate(cap):
            t[j] += d
        need -= room
    for j in range(k):
        if g[j] == 0:
            take=min(need,p[j]*(b[j]-t[j])); t[j]+=take/p[j]; need-=take
    if not need:
        return finish(F(0))
    base=t.copy()
    active={j for j in range(k) if b[j]>base[j] and g[j]>0}
    events=sorted((g[j]*(b[j]-base[j]),j) for j in active)
    inverse=sum((p[j]/g[j] for j in active),F(0))
    prev=used=F(0)
    for level,j in events:
        width=(level-prev)*inverse
        if need <= used+width:
            water=prev+(need-used)/inverse
            for h in range(k):
                if g[h]>0 and b[h]>base[h]:
                    t[h]=base[h]+min(b[h]-base[h],water/g[h])
            return finish(-water)
        used+=width; prev=level; inverse-=p[j]/g[j]
        t[j]=b[j]; active.remove(j)
    raise AssertionError('Feasible target not covered by slope events.')


def solve_catalog(model, catalog, charges, budget, promise, delta=0):
    a,prices=tuple(map(rational,catalog)),tuple(map(rational,charges))
    B,delta=rational(promise),rational(delta)
    if not a or len(a)!=len(prices) or any(u>=v for u,v in zip(a,a[1:])):
        raise ValueError('Ordered catalog and matching charges required.')
    if a[0]<0 or a[-1]>1 or any(x<0 for x in prices) or delta<0:
        raise ValueError('Invalid level, charge or risk tolerance.')
    if isinstance(budget,bool) or not isinstance(budget,int) or budget<1:
        raise ValueError('Positive integer symbol budget required.')
    bar=sum(p*b for p,b in zip(model.probabilities,model.caps))
    if not 0<=B<=bar:
        raise ValueError('Promise outside feasible range.')
    winner=None; count=0
    for size in range(1,min(budget,len(a))+1):
        for ids in combinations(range(len(a)),size):
            book=tuple(a[i] for i in ids)
            if book[0]>min(B,min(model.caps)):
                continue
            ans=solve_allocation(model,book,B,delta)
            cost=sum((prices[i] for i in ids),F(0))
            key=(ans.value-cost,-size,tuple(-x for x in book))
            count+=1
            if winner is None or key>winner[0]:
                winner=(key,book,cost,ans)
    if winner is None:
        raise ValueError('Catalog cannot implement the promise.')
    return dict(net_value=winner[0][0],codebook=winner[1],charge=winner[2],
                allocation=winner[3],books_certified=count)


def certified_grid(model,budget,promise,delta,denominator,charge=lambda c:F(0),
                   charge_lipschitz=0):
    if isinstance(denominator,bool) or not isinstance(denominator,int) or denominator<1:
        raise ValueError('Positive integer denominator required.')
    L=rational(charge_lipschitz)
    if L<0:
        raise ValueError('Nonnegative certified charge Lipschitz bound required.')
    a=tuple(F(i,denominator) for i in range(denominator+1))
    ans=solve_catalog(model,a,[charge(x) for x in a],budget,promise,delta)
    H=sum(p*g*b for p,g,b in zip(model.probabilities,model.gamma,model.caps))
    error=(model.r+H+budget*L)/denominator
    # A supplied charge oracle and its Lipschitz bound are model assumptions.
    return dict(**ans,continuous_lower=ans['net_value'],
                continuous_upper=ans['net_value']+error,certified_error=error)
