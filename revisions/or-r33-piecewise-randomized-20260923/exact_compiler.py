"""Exact scalar-price compiler. Python >=3.10, standard library only.

All numerical input is Fraction/int (floats are rejected). Vertices are in
rooted topological order; edge targets must have larger indices. Local rewards
are continuous strictly concave piecewise quadratics, including downward
marginal jumps. This implementation neither unfolds histories nor uses a QP
solver. The separate active-set reference in verify.py does not call it.
"""
from __future__ import annotations
from bisect import bisect_right
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from typing import Optional


def rational(x):
    if isinstance(x, float):
        raise TypeError('Use Fraction or integer, not binary floating point')
    return F(x)


@dataclass(frozen=True)
class Piece:
    lo: F
    hi: F
    constant: F
    linear: F
    quadratic: F

    def __post_init__(self):
        for k in self.__dataclass_fields__:
            object.__setattr__(self, k, rational(getattr(self, k)))
        if not 0 <= self.lo <= self.hi <= 1 or self.quadratic <= 0:
            raise ValueError('Invalid interval or nonpositive curvature')

    def value(self, x):
        return self.constant + self.linear*x - self.quadratic*x*x/2


@dataclass(frozen=True)
class Reward:
    pieces: tuple[Piece, ...]

    def __post_init__(self):
        if not self.pieces:
            raise ValueError('Empty reward')
        for p, q in zip(self.pieces, self.pieces[1:]):
            if p.hi != q.lo or p.lo == p.hi or q.lo == q.hi:
                raise ValueError('Pieces must tile a nondegenerate interval')
            t = p.hi
            if p.value(t) != q.value(t):
                raise ValueError('Reward is discontinuous')
            if p.linear-p.quadratic*t < q.linear-q.quadratic*t:
                raise ValueError('Marginal reward increases at a join')

    def value(self, x):
        x = rational(x)
        for p in self.pieces:
            if p.lo <= x <= p.hi:
                return p.value(x)
        raise ValueError('Action outside reward domain')

    def direct_max(self, eta, a):
        # Independent one-dimensional check: maximize on every local piece.
        candidates = [min(p.hi, max(p.lo, (p.linear-a*eta)/p.quadratic))
                      for p in self.pieces]
        return max(candidates, key=lambda x: self.value(x)-a*eta*x)

    def response(self, a):
        a = rational(a)
        if a <= 0:
            raise ValueError('Payment coefficient must be positive')
        events = {}
        for p in reversed(self.pieces):
            if p.lo == p.hi:
                continue
            events[(p.linear-p.quadratic*p.hi)/a] = (-a/p.quadratic, p.linear/p.quadratic)
            events[(p.linear-p.quadratic*p.lo)/a] = (F(0), p.lo)
        return Curve.from_events((F(0), self.pieces[-1].hi), events)


@dataclass(frozen=True)
class Curve:
    knots: tuple[F, ...]
    lines: tuple[tuple[F, F], ...]  # slope, intercept, one more than knots

    @classmethod
    def from_events(cls, left, events):
        knots, lines = [], [left]
        for t, line in sorted(events.items()):
            if line != lines[-1]:
                old = lines[-1]
                if old[0]*t+old[1] != line[0]*t+line[1]:
                    raise AssertionError('Discontinuous response')
                if line[0] > 0:
                    raise AssertionError('Increasing response')
                knots.append(t)
                lines.append(line)
        return cls(tuple(knots), tuple(lines))

    def line(self, eta):
        return self.lines[bisect_right(self.knots, eta)]

    def value(self, eta):
        m, c = self.line(eta)
        return m*eta+c

    @classmethod
    def weighted_sum(cls, terms):
        m = c = F(0)
        changes = {}
        for weight, curve in terms:
            m += weight*curve.lines[0][0]
            c += weight*curve.lines[0][1]
            for i, t in enumerate(curve.knots):
                dm, dc = changes.get(t, (F(0), F(0)))
                changes[t] = (dm+weight*(curve.lines[i+1][0]-curve.lines[i][0]),
                              dc+weight*(curve.lines[i+1][1]-curve.lines[i][1]))
        left, events = (m, c), {}
        for t, (dm, dc) in sorted(changes.items()):
            m, c = m+dm, c+dc
            events[t] = m, c
        return cls.from_events(left, events)

    def inverse(self, b):
        b = rational(b)
        if not self.lines[-1][1] <= b <= self.lines[0][1]:
            raise ValueError('Infeasible payment')
        if not self.knots:
            return F(0)
        if b == self.lines[0][1]:
            return self.knots[0]
        for i, t in enumerate(self.knots):
            if self.value(t) == b:
                return t
            m, c = self.lines[i+1]
            if m:
                eta = (b-c)/m
                if eta >= t and (i+1 == len(self.knots) or eta <= self.knots[i+1]):
                    return eta
        raise AssertionError('Missing finite crossing')

    def cap(self, b):
        if b < self.lines[-1][1]:
            raise ValueError('Infeasible continuation cap')
        if b >= self.lines[0][1]:
            return self, None
        alpha = self.inverse(b)
        events = {t: self.lines[i+1] for i, t in enumerate(self.knots) if t > alpha}
        events[alpha] = self.line(alpha)
        return Curve.from_events((F(0), b), events), alpha


@dataclass(frozen=True)
class Vertex:
    reward: Reward
    payment: F
    cap: F
    edges: tuple[tuple[int, F], ...] = ()

    def __post_init__(self):
        object.__setattr__(self, 'payment', rational(self.payment))
        object.__setattr__(self, 'cap', rational(self.cap))
        object.__setattr__(self, 'edges', tuple((j, rational(p)) for j, p in self.edges))
        if self.payment <= 0 or any(p <= 0 for _, p in self.edges):
            raise ValueError('Nonpositive payment/probability')
        if self.edges and sum(p for _, p in self.edges) != 1:
            raise ValueError('Transition probabilities must sum to one')


class Compiler:
    def __init__(self, vertices, beta=F(1)):
        self.vertices, self.beta = tuple(vertices), rational(beta)
        n = len(self.vertices)
        if not n or not 0 < self.beta <= 1:
            raise ValueError('Invalid graph or discount')
        reachable = {0}
        for i, v in enumerate(self.vertices):
            if i not in reachable or any(not i < j < n for j, _ in v.edges):
                raise ValueError('Require reachable topologically ordered DAG')
            reachable.update(j for j, _ in v.edges)
        self.local = [v.reward.response(v.payment) for v in self.vertices]
        self.responses = [None]*n
        self.barriers: list[Optional[F]] = [None]*n
        for i in reversed(range(n)):
            v = self.vertices[i]
            terms = [(v.payment, self.local[i])]
            terms += [(self.beta*p, self.responses[j]) for j, p in v.edges]
            self.responses[i], self.barriers[i] = Curve.weighted_sum(terms).cap(v.cap)
        self.global_knots = tuple(sorted({t for c in self.local for t in c.knots}
                                        | {a for a in self.barriers if a is not None}))

    def circuit_values(self, eta):
        # Does not access any per-vertex compiled payment-response list.
        values = [F(0)]*len(self.vertices)
        for i in reversed(range(len(values))):
            v = self.vertices[i]
            values[i] = min(v.cap, v.payment*self.local[i].value(eta)
                            + self.beta*sum(p*values[j] for j, p in v.edges))
        return tuple(values)

    def circuit_inverse(self, b):
        # Binary search on global events, then reconstruct one affine segment.
        b = rational(b)
        knots = self.global_knots
        if not knots:
            if self.circuit_values(F(0))[0] != b:
                raise ValueError('Infeasible payment')
            return F(0)
        high, low = self.circuit_values(knots[0])[0], self.circuit_values(knots[-1])[0]
        if not low <= b <= high:
            raise ValueError('Infeasible payment')
        if b == high:
            return knots[0]
        if b == low:
            return knots[-1]
        left, right = 0, len(knots)-1
        while right-left > 1:
            mid = (left+right)//2
            value = self.circuit_values(knots[mid])[0]
            if value == b:
                return knots[mid]
            if value > b:
                left = mid
            else:
                right = mid
        u, v = knots[left], knots[right]
        yu, yv = self.circuit_values(u)[0], self.circuit_values(v)[0]
        return u+(b-yu)*(v-u)/(yv-yu)

    def certificate(self, eta0):
        eta0 = rational(eta0)
        @lru_cache(None)
        def continuation(i, eta):
            v, alpha = self.vertices[i], self.barriers[i]
            s = eta if alpha is None else max(eta, alpha)
            x = self.local[i].value(s)
            assert x == v.reward.direct_max(s, v.payment)
            successors = [(p, continuation(j, s)) for j, p in v.edges]
            payment = v.payment*x+self.beta*sum(p*z[0] for p, z in successors)
            reward = v.reward.value(x)+self.beta*sum(p*z[1] for p, z in successors)
            assert payment == self.responses[i].value(eta) and payment <= v.cap
            assert (s-eta)*(v.cap-payment) == 0
            return payment, reward
        b, value = continuation(0, eta0)
        flow = [{eta0: F(1)}]+[{} for _ in self.vertices[1:]]
        dual, labels, states = eta0*b, {eta0}, 0
        for i, v in enumerate(self.vertices):
            for eta, weight in flow[i].items():
                alpha = self.barriers[i]
                s = eta if alpha is None else max(eta, alpha)
                x = self.local[i].value(s)
                states += 1
                labels.add(s)
                dual += weight*((s-eta)*v.cap+v.reward.value(x)-v.payment*s*x)
                for j, p in v.edges:
                    flow[j][s] = flow[j].get(s, F(0))+self.beta*p*weight
        assert dual == value and len(labels) <= len(self.vertices)+1
        return {'payment': b, 'reward': value, 'dual': dual,
                'states': states, 'labels': len(labels)}
