"""Rational eligibility-prefix price DP and finite catalog branch-and-bound.

A price relaxation is an upper bound, not an assertion of strong outer duality.
All reported bounds are Fractions. Interrupting the search retains an explicit
frontier certificate. The implementation imports only the inherited fixed-book
primal allocation and branch-support oracle, never the continuous cell solver.
"""
from __future__ import annotations
from fractions import Fraction as F
from dataclasses import dataclass
from pathlib import Path
from itertools import combinations
import heapq
import sys

sys.path.append(str(Path(__file__).resolve().parents[2] /
                    'or-r42-certified-joint-design-20260924' / 'code'))
from unified import Model, rational, solve_allocation, branch_maximum

@dataclass
class PriceDP:
    model: Model
    catalog: tuple
    charges: tuple
    budget: int
    promise: F
    delta: F
    lam: F

    def __post_init__(self):
        self.catalog = tuple(map(rational, self.catalog))
        self.charges = tuple(map(rational, self.charges))
        self.promise, self.delta, self.lam = map(rational,
            (self.promise, self.delta, self.lam))
        a = self.catalog
        if (not a or len(a) != len(self.charges) or a[0] < 0 or a[-1] > 1
            or any(u >= v for u,v in zip(a,a[1:]))
            or any(x < 0 for x in self.charges) or self.delta < 0):
            raise ValueError('Ordered distinct levels and nonnegative charges/tolerance required.')
        if isinstance(self.budget,bool) or not isinstance(self.budget,int) or self.budget < 1:
            raise ValueError('Positive integer budget required.')
        self.budget = min(self.budget,len(a))
        bar = sum(p*b for p,b in zip(self.model.probabilities,self.model.caps))
        if not 0 <= self.promise <= bar or a[0] > min(self.promise,min(self.model.caps)):
            raise ValueError('Infeasible catalog or promise.')
        self.g = tuple(self.model.reward(x)-self.lam*x for x in a)
        n = len(a)
        self.tail = [sum((p*(self.g[i]+self.phi(j,b-u))
                         for j,(p,b) in enumerate(zip(self.model.probabilities,self.model.caps))
                         if b >= u), F(0)) for i,u in enumerate(a)]
        self.edge = {}
        for i,u in enumerate(a):
            for l in range(i+1,n):
                if self.g[l] < self.g[i]:
                    continue
                v = a[l]
                slope = (self.g[l]-self.g[i])/(v-u)
                self.edge[i,l] = sum((p*(self.g[i] +
                    (slope*(b-u) if v <= b+self.delta else self.phi(j,b-u)))
                    for j,(p,b) in enumerate(zip(self.model.probabilities,self.model.caps))
                    if u <= b < v), F(0))
        # W includes the current level but excludes its already paid charge.
        self.W = [None, list(self.tail)]
        self.next = [None, [None]*n]
        for remaining in range(2,self.budget+1):
            row, nxt = list(self.tail), [None]*n
            for i in range(n):
                for l in range(i+1,n):
                    if (i,l) not in self.edge:
                        continue
                    value = self.edge[i,l]-self.charges[l]+self.W[remaining-1][l]
                    if value > row[i]:
                        row[i],nxt[i] = value,l
            self.W.append(row); self.next.append(nxt)

    def phi(self,j,z):
        if z < 0:
            raise ValueError('Negative tail capacity.')
        gam = self.model.gamma[j]
        y = F(0) if self.lam >= 0 else (min(z,-self.lam/gam) if gam else z)
        return -gam*y*y/2-self.lam*y

    def suffix(self,i,remaining):
        ids = [i]
        while remaining > 1 and self.next[remaining][i] is not None:
            i = self.next[remaining][i]
            ids.append(i); remaining -= 1
        return tuple(ids)

    def bound(self,prefix=()):
        """Exact priced maximum over all books extending this fixed prefix.

        Returns (Lagrangian upper bound, maximizing book indices).
        A prefix is a mandatory consecutive initial segment, not merely a subset.
        """
        p = tuple(prefix)
        if not p:
            choices = [(self.W[self.budget][i]-self.charges[i],-i,i)
                for i,u in enumerate(self.catalog)
                if u <= min(self.promise,min(self.model.caps))]
            value,_,i = max(choices)
            return self.lam*self.promise+value,self.suffix(i,self.budget)
        if (len(p)>self.budget or any(i<0 or i>=len(self.catalog) for i in p)
            or any(i>=j for i,j in zip(p,p[1:]))
            or self.catalog[p[0]]>min(self.promise,min(self.model.caps))):
            raise ValueError('Invalid feasible prefix.')
        if any(self.g[j]<self.g[i] for i,j in zip(p,p[1:])):
            book = tuple(self.catalog[i] for i in p)
            score = sum((w*branch_maximum(self.model,j,book,self.lam,self.delta)[0]
                for j,w in enumerate(self.model.probabilities)), F(0))
            score -= sum(self.charges[i] for i in p)
            return self.lam*self.promise+score,p
        remaining = self.budget-len(p)+1
        score = sum((self.edge[i,j] for i,j in zip(p,p[1:])),F(0))
        score -= sum(self.charges[i] for i in p)
        score += self.W[remaining][p[-1]]
        return self.lam*self.promise+score,p[:-1]+self.suffix(p[-1],remaining)

    def max_bits(self):
        values = list(self.g)+list(self.tail)+list(self.edge.values())
        values += [x for row in self.W[1:] for x in row]
        return max(max(x.numerator.bit_length(),x.denominator.bit_length()) for x in values)


def candidate_prices(model,a,charges,m,B,delta,iterations=8):
    """Rational bisection samples valid prices; no exact dual minimum is assumed."""
    B,delta = rational(B),rational(delta)
    lo = -max((g*b for g,b in zip(model.gamma,model.caps)), default=F(0))-1
    hi = model.r+1
    dps = {}; tested = set(); lower = None; best = None
    def evaluate(lam):
        nonlocal lower,best
        lam = rational(lam)
        if lam in dps:
            return dps[lam]
        dp = PriceDP(model,tuple(a),tuple(charges),m,B,delta,lam); dps[lam]=dp
        _,ids = dp.bound()
        if ids not in tested:
            ans = solve_allocation(model,tuple(a[i] for i in ids),B,delta)
            value = ans.value-sum(charges[i] for i in ids)
            if lower is None or value>lower:
                lower,best=value,(ids,ans)
            tested.add(ids)
        return dp
    for lam in (lo,F(0),hi): evaluate(lam)
    for _ in range(iterations):
        mid=(lo+hi)/2; dp=evaluate(mid)
        _,ids=dp.bound(); book=tuple(a[i] for i in ids)
        # Any maximizer defines a valid subgradient; choose smallest tied target.
        total=sum(p*branch_maximum(model,j,book,mid,delta)[1]
                  for j,p in enumerate(model.probabilities))
        if total>B: lo=mid
        else: hi=mid
    # Supporting prices of feasible winning books often close the outer gap.
    for _ in range(2):
        if best is not None: evaluate(best[1].multiplier)
    return list(dps.values())


def solve_prefix(model,catalog,charges,budget,promise,delta=0,*,prices=None,
                 iterations=8,max_nodes=None):
    """Exact when frontier is empty; otherwise a rigorous catalog interval.

    max_nodes counts expanded prefix nodes. All partitions, bounds and their
    price witnesses are returned so a separate checker can audit global coverage.
    """
    a,charges=tuple(map(rational,catalog)),tuple(map(rational,charges))
    B,delta=rational(promise),rational(delta)
    if max_nodes is not None and (not isinstance(max_nodes,int) or max_nodes<0):
        raise ValueError('Nonnegative node limit required.')
    dps=(candidate_prices(model,a,charges,budget,B,delta,iterations) if prices is None
         else [PriceDP(model,a,charges,budget,B,delta,l) for l in prices])
    if not dps: raise ValueError('At least one price is needed.')
    m=dps[0].budget
    cache={}; incumbent=None; win=None
    def primal(ids):
        nonlocal incumbent,win
        ids=tuple(ids)
        if ids not in cache:
            ans=solve_allocation(model,tuple(a[i] for i in ids),B,delta)
            cache[ids]=(ans.value-sum(charges[i] for i in ids),ans)
        value,ans=cache[ids]
        if incumbent is None or value>incumbent:
            incumbent,win=value,(ids,ans)
        return value
    def bound(prefix):
        candidates=[]
        for dp in dps:
            upper,ids=dp.bound(prefix)
            primal(ids)
            candidates.append((upper,dp.lam))
        return min(candidates)
    U,lam=bound(())
    heap=[(-U,(),lam)]; ledger=[]; expanded=0
    while heap:
        neg,p,lam=heapq.heappop(heap); upper=-neg
        if upper<=incumbent:
            ledger.append(dict(prefix=p,kind='pruned',upper=upper,price=lam)); continue
        if max_nodes is not None and expanded>=max_nodes:
            heapq.heappush(heap,(neg,p,lam)); break
        expanded+=1
        leaf=primal(p) if p else None
        if len(p)==m:
            ledger.append(dict(prefix=p,kind='leaf',value=leaf,inner_price=cache[p][1].multiplier)); continue
        start=p[-1]+1 if p else 0
        children=[p+(i,) for i in range(start,len(a))
            if p or a[i]<=min(B,min(model.caps))]
        ledger.append(dict(prefix=p,kind='split',value=leaf,children=children,inner_price=cache[p][1].multiplier if p else None))
        for child in children:
            up,l=bound(child)
            if up<=incumbent:
                ledger.append(dict(prefix=child,kind='pruned',upper=up,price=l))
            else:
                heapq.heappush(heap,(-up,child,l))
    frontier=[dict(prefix=p,upper=-neg,price=l) for neg,p,l in heap]
    U=max([incumbent]+[x['upper'] for x in frontier])
    return dict(lower=incumbent,upper=U,exact=(U==incumbent),
        codebook=tuple(a[i] for i in win[0]),winner_ids=win[0],allocation=win[1],
        prices=tuple(dp.lam for dp in dps),ledger=ledger,frontier=frontier,
        expanded_nodes=expanded,books_evaluated=len(cache),
        max_dp_bits=max(dp.max_bits() for dp in dps),
        dp_edge_entries=sum(len(dp.edge) for dp in dps))
