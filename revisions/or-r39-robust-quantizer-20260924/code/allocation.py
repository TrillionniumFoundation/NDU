"""Exact nonsaturated expected-participation allocation and dual certificates.

This module uses the renewal Model from catalog.py. All inputs and certificates
are rational. Catalog search enumerates subsets: it is an exact small-instance
reference method, not the polynomial saturated catalog dynamic program.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations
from bisect import bisect_right
from catalog import Model, rational


@dataclass(frozen=True)
class Allocation:
    value: F
    targets: tuple[F, ...]
    multiplier: F
    dual_bound: F


def response(model: Model, j: int, book: tuple[F, ...], t: F) -> F:
    """Concave branch response, computed from adjacent terminal levels."""
    if not book[0] <= t <= model.caps[j]:
        raise ValueError('Target outside this book/branch feasible interval.')
    if t >= book[-1]:
        return model.reward(book[-1])-model.gamma[j]*(t-book[-1])**2/2
    i = bisect_right(book, t)-1
    u, v = book[i:i+2]
    return ((v-t)*model.reward(u)+(t-u)*model.reward(v))/(v-u)


def branch_maximum(model: Model, j: int, book: tuple[F, ...], lam: F):
    """Independent certificate oracle: enumerate every kink and tail vertex."""
    b, g = model.caps[j], model.gamma[j]
    # Codeword kinks have known values f(c); avoid a binary search per kink.
    scored = [(model.reward(c)-lam*c, c) for c in book if c <= b]
    extra = {b}
    if b > book[-1] and g:
        extra.add(max(book[-1], min(b, book[-1]-lam/g)))
    scored.extend((response(model, j, book, t)-lam*t, t) for t in extra)
    best = max(v for v, _ in scored)
    ties = [t for v, t in scored if v == best]
    return best, min(ties), max(ties)


def certify(model: Model, book: tuple[F, ...], B: F,
            targets: tuple[F, ...], lam: F) -> Allocation:
    if len(targets) != len(model.caps):
        raise ValueError('Wrong number of branch targets.')
    if sum(p*t for p, t in zip(model.probabilities, targets)) != B:
        raise ValueError('Promise residual is not zero.')
    value = sum((p*response(model, j, book, t)
                 for j, (p, t) in enumerate(zip(model.probabilities, targets))), F(0))
    maxima = [branch_maximum(model, j, book, lam)[0] for j in range(len(targets))]
    dual = lam*B+sum(p*v for p, v in zip(model.probabilities, maxima))
    if dual != value:
        raise ValueError('Nonzero exact duality gap.')
    return Allocation(value, targets, lam, dual)


def solve_allocation(model: Model, codebook, promise) -> Allocation:
    """O(k*s+k*log(k+1)) rational work, including a separate certificate check."""
    book, B = tuple(map(rational, codebook)), rational(promise)
    if not book or tuple(sorted(set(book))) != book:
        raise ValueError('Codebook must be nonempty, strictly increasing.')
    bar = sum(p*b for p, b in zip(model.probabilities, model.caps))
    if not 0 <= book[0] <= min(model.caps) or book[-1] > 1:
        raise ValueError('Infeasible codebook.')
    if not book[0] <= B <= bar:
        raise ValueError('Promise outside the fixed-book feasible interval.')
    p, b, g = model.probabilities, model.caps, model.gamma
    k = len(b)
    t = [book[0]]*k
    need = B-book[0]

    def finish(lam):
        return certify(model, book, B, tuple(t), lam)

    # All branches have the same strictly decreasing adjacent chord slopes.
    for u, v in zip(book, book[1:]):
        slope = (model.reward(v)-model.reward(u))/(v-u)
        capacities = [max(F(0), min(x, v)-u) for x in b]
        room = sum(pj*d for pj, d in zip(p, capacities))
        if need <= room:
            for j, d in enumerate(capacities):
                take = min(need, p[j]*d)
                t[j] += take/p[j]
                need -= take
            assert need == 0
            return finish(slope)
        for j, d in enumerate(capacities):
            t[j] += d
        need -= room

    # Free intermediate service has zero marginal cost; fill it before losses.
    for j in range(k):
        if g[j] == 0:
            take = min(need, p[j]*(b[j]-t[j]))
            t[j] += take/p[j]
            need -= take
    if need == 0:
        return finish(F(0))

    # Positive-curvature tails share a water level w=-lambda, truncated by caps.
    active = {j for j in range(k) if b[j] > t[j] and g[j] > 0}
    events = sorted((g[j]*(b[j]-t[j]), j) for j in active)
    inverse = sum((p[j]/g[j] for j in active), F(0))
    previous, used = F(0), F(0)
    base = t.copy()
    for level, j in events:
        width = (level-previous)*inverse
        if need <= used+width:
            water = previous+(need-used)/inverse
            for h in active:
                t[h] = base[h]+min(b[h]-base[h], water/g[h])
            for h in range(k):
                if h not in active and g[h] > 0:
                    t[h] = b[h] if base[h] < b[h] else base[h]
            return finish(-water)
        used += width
        previous = level
        inverse -= p[j]/g[j]
        t[j] = b[j]
        active.remove(j)
    raise AssertionError('Water-level sweep failed to cover a feasible promise.')


def solve_catalog_promise(model: Model, catalog, charges, budget: int, promise):
    """Return best value minus actual selected-level charges and its certificate.

    Complexity is exponential in catalog size. Used to audit the nonsaturated
    extension on small certified catalogs; never labeled a continuous solver.
    """
    a, prices = tuple(map(rational, catalog)), tuple(map(rational, charges))
    B = rational(promise)
    if not a or tuple(sorted(set(a))) != a or len(a) != len(prices):
        raise ValueError('Distinct ordered catalog and matching charges required.')
    if a[0] < 0 or a[-1] > 1 or any(x < 0 for x in prices):
        raise ValueError('Invalid catalog level or negative charge.')
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
        raise ValueError('Positive integer budget required.')
    bar = sum(p*b for p, b in zip(model.probabilities, model.caps))
    if not 0 <= B <= bar:
        raise ValueError('Promise outside the model feasible interval.')
    winner, count = None, 0
    for size in range(1, min(budget, len(a))+1):
        for ids in combinations(range(len(a)), size):
            book = tuple(a[i] for i in ids)
            if book[0] > min(B, model.caps[0]):
                continue
            ans = solve_allocation(model, book, B)
            charge = sum((prices[i] for i in ids), F(0))
            key = (ans.value-charge, -size, tuple(-x for x in book))
            count += 1
            if winner is None or key > winner[0]:
                winner = (key, book, charge, ans)
    if winner is None:
        raise ValueError('Catalog cannot implement this promise.')
    return {'net_value': winner[0][0], 'codebook': winner[1],
            'charge': winner[2], 'allocation': winner[3], 'books_certified': count}
