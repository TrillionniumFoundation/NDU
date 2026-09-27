"""Exact risk-limited certified-catalog renewal design with additive level prices.
The catalog is model input, not a claimed exact grid for a continuous problem.
Inputs are int, str or Fraction; floating point is deliberately rejected.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from bisect import bisect_right


def rational(x):
    if isinstance(x, bool) or not isinstance(x, (int, str, F)):
        raise TypeError('Use int, rational str, or Fraction, not floating point.')
    return F(x)


@dataclass(frozen=True)
class Model:
    caps: tuple[F, ...]
    probabilities: tuple[F, ...]
    gamma: tuple[F, ...]
    r: F = F(2)
    q: F = F(1)

    @classmethod
    def make(cls, caps, probabilities, gamma, r=2, q=1):
        b, p, g = (tuple(map(rational, xs)) for xs in (caps, probabilities, gamma))
        r, q = rational(r), rational(q)
        if not b or len(b) != len(p) or len(b) != len(g):
            raise ValueError('Equal nonempty branch arrays required.')
        if any(not 0 < x < 1 for x in b) or tuple(sorted(b)) != b:
            raise ValueError('Sorted caps in (0,1) required; ties allowed.')
        if sum(p) != 1 or any(x <= 0 for x in p):
            raise ValueError('Positive probabilities summing exactly to one required.')
        if any(x < 0 for x in g) or not r >= q > 0:
            raise ValueError('Require nonnegative curvatures and r >= q > 0.')
        return cls(b, p, g, r, q)

    def reward(self, x):
        return self.r*x-self.q*x*x/2


@dataclass(frozen=True)
class Answer:
    total: F
    service_loss: F
    level_charge: F
    codebook: tuple[F, ...]


def branch_rule(model, j, book, delta):
    """Return intermediate tier and (terminal level, probability) pairs."""
    b = model.caps[j]
    i = bisect_right(book, b)-1
    if i < 0:
        raise ValueError('Book has no feasible lowest level.')
    u = book[i]
    if u == b or i+1 == len(book) or book[i+1]-b > delta:
        return b-u, ((u, F(1)),)
    v = book[i+1]
    return F(0), ((u, (v-b)/(v-u)), (v, (b-u)/(v-u)))


def replay(model, book, delta):
    loss = F(0)
    for j, (b, p, g) in enumerate(zip(model.caps, model.probabilities, model.gamma)):
        y, draws = branch_rule(model, j, book, delta)
        assert sum(prob for _, prob in draws) == 1
        assert all(prob >= 0 and y+c <= b+delta for c, prob in draws if prob)
        assert y+sum(c*prob for c, prob in draws) == b
        loss += p*(model.reward(b)-sum(prob*model.reward(c) for c, prob in draws)+g*y*y/2)
    return loss


def solve(model, catalog, charges, budget, delta=0):
    """Optimal at-most-s result for each s=1,...,budget, with deterministic ties."""
    a, price = tuple(map(rational, catalog)), tuple(map(rational, charges))
    delta = rational(delta)
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
        raise ValueError('budget must be a positive integer')
    if not a or len(a) != len(price) or tuple(sorted(set(a))) != a:
        raise ValueError('Distinct increasing catalog and matching charges required.')
    if a[0] < 0 or a[-1] > 1 or a[0] > model.caps[0]:
        raise ValueError('Catalog must be in [0,1] with a feasible lowest level.')
    if delta < 0 or any(c < 0 for c in price):
        raise ValueError('Tolerance and charges must be nonnegative.')
    n, edges = len(a), {}
    for i, u in enumerate(a):
        for j in range(i+1, n):
            v, cost = a[j], F(0)
            for b, p, g in zip(model.caps, model.probabilities, model.gamma):
                if not u <= b < v:
                    continue
                if v-b <= delta:
                    cost += p*(model.reward(b)-((v-b)*model.reward(u)+(b-u)*model.reward(v))/(v-u))
                else:
                    cost += p*(model.reward(b)-model.reward(u)+g*(b-u)**2/2)
            edges[i, j] = cost
    tails = [sum((p*(model.reward(b)-model.reward(u)+g*(b-u)**2/2)
                  for b, p, g in zip(model.caps, model.probabilities, model.gamma) if b >= u), F(0))
             for u in a]
    values = {i: price[i] for i in range(n) if a[i] <= model.caps[0]}
    parents = {(1, i): None for i in values}
    best, answer = None, []
    for s in range(1, min(budget, n)+1):
        if s > 1:
            new = {}
            for j in range(n):
                candidates = [(value+edges[i, j]+price[j], i) for i, value in values.items() if i < j]
                if candidates:
                    new[j], parent = min(candidates)
                    parents[s, j] = parent
            values = new
        for j, value in values.items():
            candidate = (value+tails[j], s, j)
            if best is None or candidate < best:
                best = candidate
        assert best is not None
        cost, length, end = best
        ids, node = [], end
        for level in range(length, 0, -1):
            ids.append(node)
            parent = parents[level, node]
            if level > 1:
                assert parent is not None
                node = parent
        ids.reverse()
        book = tuple(a[i] for i in ids)
        charge = sum((price[i] for i in ids), F(0))
        service = replay(model, book, delta)
        assert cost == service+charge
        answer.append(Answer(cost, service, charge, book))
    while len(answer) < budget:
        answer.append(answer[-1])
    return answer


def clipped(model, promise):
    """Full-information optimum for every root promise, including repeated caps."""
    B = rational(promise)
    bar = sum(p*b for p, b in zip(model.probabilities, model.caps))
    if not 0 <= B <= bar:
        raise ValueError('Promise outside feasible interval.')
    if B == bar:
        return model.caps
    used, remaining = F(0), F(1)
    for b, p in zip(model.caps, model.probabilities):
        tau = (B-used)/remaining
        if tau <= b:
            return tuple(min(x, tau) for x in model.caps)
        used += p*b
        remaining -= p
    raise AssertionError('Unreachable clipped allocation case')
