"""Exact fixed-promise codebook frontier; no price-DP or allocator imports.

All quantities are rational. The frontier is globally optimal for the supplied
branch targets, NOT for endogenous targets. Every returned book meets its
stated memory budget. This distinction is also recorded in the certificates.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from fractions import Fraction as F
from typing import Sequence


def rat(x):
    if isinstance(x, (float, bool)):
        raise TypeError('Use integers, rational strings, or Fractions, not floats/bools.')
    return F(x)


@dataclass(frozen=True)
class Instance:
    caps: tuple[F, ...]
    weights: tuple[F, ...]
    gamma: tuple[F, ...]
    ceilings: tuple[F, ...]
    r: F = F(2)
    curvature: F = F(1)

    @classmethod
    def make(cls, caps, weights, gamma, ceilings, r=2, curvature=1):
        ans = cls(*(tuple(map(rat, v)) for v in (caps, weights, gamma, ceilings)),
                  rat(r), rat(curvature))
        k = len(ans.caps)
        if not k or any(len(v) != k for v in (ans.weights, ans.gamma, ans.ceilings)):
            raise ValueError('Equal nonempty branch arrays are required.')
        if (any(not 0 <= b <= 1 for b in ans.caps) or
            any(w <= 0 for w in ans.weights) or sum(ans.weights) != 1 or
            any(g < 0 for g in ans.gamma) or
            any(t < b for t, b in zip(ans.ceilings, ans.caps)) or
            ans.curvature < 0 or ans.r < ans.curvature or ans.r <= 0):
            raise ValueError('Invalid cap, weight, shape, or realization ceiling.')
        return ans

    def reward(self, x):
        return self.r*x - self.curvature*x*x/2

    @property
    def cap_total(self):
        return sum(w*b for w, b in zip(self.weights, self.caps))


def inputs(instance, catalog, charges, targets, budget):
    a, rho, t = (tuple(map(rat, z)) for z in (catalog, charges, targets))
    if (not a or len(a) != len(rho) or a[0] < 0 or a[-1] > 1 or
        any(u >= v for u, v in zip(a, a[1:])) or any(x < 0 for x in rho)):
        raise ValueError('Strict ordered catalog and nonnegative charges required.')
    if len(t) != len(instance.caps) or any(not a[0] <= z <= b for z, b in zip(t, instance.caps)):
        raise ValueError('Targets must lie between the smallest level and each cap.')
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
        raise ValueError('Positive integer symbol budget required.')
    return a, rho, t, min(budget, len(a))


def policy(instance, book, targets, charges):
    """Canonical reconstruction, including pre-draw service and realized totals."""
    book = tuple(book)
    if not book or any(u >= v for u, v in zip(book, book[1:])):
        raise ValueError('Ordered nonempty book required.')
    ys, laws, values = [], [], []
    for j, t in enumerate(targets):
        if not book[0] <= t <= instance.caps[j]:
            raise ValueError('Book cannot implement supplied target.')
        eligible = [x for x in book if x <= instance.ceilings[j]]
        d = eligible[-1]
        if t >= d:
            y, law = t-d, ((d, F(1)),)
        else:
            hi = next(i for i, x in enumerate(eligible) if x >= t)
            if eligible[hi] == t:
                y, law = F(0), ((t, F(1)),)
            else:
                u, v = eligible[hi-1], eligible[hi]
                z = (t-u)/(v-u)
                y, law = F(0), ((u, 1-z), (v, z))
        if any(y+x > instance.ceilings[j] for x, p in law if p > 0):
            raise AssertionError('Realization ceiling violated.')
        ys.append(y); laws.append(law)
        values.append(sum(p*instance.reward(x) for x, p in law)-instance.gamma[j]*y*y/2)
    charge = sum(charges[x] for x in book)
    gross = sum(w*v for w, v in zip(instance.weights, values))
    return dict(book=book, targets=tuple(targets), intermediate=tuple(ys),
                lotteries=tuple(laws), branch_values=tuple(values), charge=charge,
                gross=gross, value=gross-charge,
                promise=sum(w*t for w, t in zip(instance.weights, targets)))


def frontier(instance: Instance, catalog, charges, targets, budget: int):
    """All exact and at-most cardinalities in O((k+budget) N^2) arithmetic.

    An arc (u,v) owns precisely the targets u <= t_j < v. Its upper
    endpoint is usable only when v <= ceiling_j; otherwise that branch
    uses u and fixed pre-draw service t_j-u. No price admissibility pruning
    is permitted in this unpriced, fixed-target dynamic program.
    """
    a, rho, t, budget = inputs(instance, catalog, charges, targets, budget)
    n, f = len(a), instance.reward
    tail, edges = [], {}
    for i, u in enumerate(a):
        tail.append(sum((w*(f(u)-g*(z-u)**2/2)
            for w, g, z in zip(instance.weights, instance.gamma, t) if z >= u), F(0)))
        for l in range(i+1, n):
            v = a[l]; slope = (f(v)-f(u))/(v-u)
            edges[i, l] = sum((w*(f(u)+slope*(z-u) if v <= tau
                                      else f(u)-g*(z-u)**2/2)
                for w, g, tau, z in zip(instance.weights, instance.gamma, instance.ceilings, t)
                if u <= z < v), F(0))
    # Exactly r selected levels. None denotes infeasibility, not minus infinity.
    dp = [None, list(tail)]; nxt = [None, [None]*n]
    exact = []
    cmap = dict(zip(a, rho))
    for count in range(1, budget+1):
        if count > 1:
            row, route = [None]*n, [None]*n
            for i in range(n):
                candidates = [(edges[i, l]-rho[l]+dp[count-1][l], -l, l)
                              for l in range(i+1, n) if dp[count-1][l] is not None]
                if candidates:
                    row[i], _, route[i] = max(candidates)
            dp.append(row); nxt.append(route)
        candidates = [(dp[count][i]-rho[i], -i, i) for i, u in enumerate(a)
                      if u <= min(t) and dp[count][i] is not None]
        if not candidates:
            exact.append(None); continue
        value, _, i = max(candidates); ids = [i]; remaining = count
        while remaining > 1:
            i = nxt[remaining][i]; ids.append(i); remaining -= 1
        p = policy(instance, tuple(a[i] for i in ids), t, cmap)
        assert p['value'] == value and len(p['book']) == count
        exact.append(p)
    at_most, best = [], None
    for p in exact:
        if p is not None and (best is None or p['value'] > best['value']):
            best = p
        at_most.append(best)
    return dict(schema='ndu-r45-fixed-target-frontier-v1', model=asdict(instance),
                catalog=a, charges=rho, targets=t, budget=budget,
                scope='global codebook optimum conditional on the supplied targets',
                exact=exact, at_most=at_most,
                edge_entries=len(edges), dp_entries=n*budget,
                dp_table=dp[1:])


def ideal_targets(instance: Instance, promise):
    """Capped Jensen allocation, independent of the codebook and shortfall costs."""
    B = rat(promise)
    if not 0 <= B <= instance.cap_total:
        raise ValueError('Infeasible aggregate promise.')
    if B == instance.cap_total:
        return instance.caps
    remaining, weight = B, F(1)
    order = sorted(range(len(instance.caps)), key=lambda j: instance.caps[j])
    t = [None]*len(order)
    for j in order:
        level = remaining/weight
        if level <= instance.caps[j]:
            for h in order:
                if t[h] is None: t[h] = level
            break
        t[j] = instance.caps[j]
        remaining -= instance.weights[j]*t[j]; weight -= instance.weights[j]
    assert all(x is not None for x in t)
    assert sum(w*x for w, x in zip(instance.weights, t)) == B
    return tuple(t)


def jensen_certificate(instance, catalog, charges, promise, budget):
    t = ideal_targets(instance, promise)
    ans = frontier(instance, catalog, charges, t, budget)
    gross = sum(w*instance.reward(z) for w, z in zip(instance.weights, t))
    anchor_charge = min(rat(c) for a, c in zip(catalog, charges) if rat(a) <= min(t))
    upper = gross-anchor_charge
    ans['jensen_upper'] = upper
    ans['conditional_distortion_and_charge'] = tuple(gross-p['value'] for p in ans['at_most'])
    ans['same_budget_gaps'] = tuple(upper-p['value'] for p in ans['at_most'])
    assert all(x >= 0 for x in ans['same_budget_gaps'])
    return ans


def repair_targets(instance, targets, lower, promise):
    """Clip, then repair the single weighted equality by exact bounded transfers."""
    lower, B = rat(lower), rat(promise)
    if lower < 0 or lower > min(instance.caps) or not lower <= B <= instance.cap_total:
        raise ValueError('Feasibility repair requires a feasible common lower level.')
    raw = tuple(map(rat, targets))
    if len(raw) != len(instance.caps): raise ValueError('Wrong target dimension.')
    t = [min(b, max(lower, z)) for z, b in zip(raw, instance.caps)]
    clipping = sum(w*abs(z-x) for w, z, x in zip(instance.weights, raw, t))
    residual = B-sum(w*x for w, x in zip(instance.weights, t))
    cost = abs(residual)
    for j, w in enumerate(instance.weights):
        if residual > 0:
            mass = min(residual, w*(instance.caps[j]-t[j]))
        else:
            mass = -min(-residual, w*(t[j]-lower))
        t[j] += mass/w; residual -= mass
    assert residual == 0
    return tuple(t), clipping, cost


def encode(x):
    if isinstance(x, F): return str(x)
    if isinstance(x, dict): return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)): return [encode(v) for v in x]
    return x
