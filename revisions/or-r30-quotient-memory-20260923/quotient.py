#!/usr/bin/env python3
"""Exact coefficient-event quotient compiler and minimal price controller.

Rational inputs only. Preprocessing never unfolds histories, solves a QP, or
uses an optimum supplied by another method. Coefficients are merged directly;
new cap crossings are NOT fed back as interpolation-generated coefficients.
"""
from __future__ import annotations
from bisect import bisect_right
from dataclasses import dataclass
from fractions import Fraction as F
from typing import Any


def rat(x: Any) -> F:
    if isinstance(x, float):
        raise TypeError('Rational strings or integers are required, not floats.')
    return F(x)


def clip(x: F, lo: F, hi: F) -> F:
    return max(lo, min(hi, x))


@dataclass(frozen=True)
class Curve:
    knots: tuple[F, ...]
    lines: tuple[tuple[F, F], ...]  # slope and intercept

    def at(self, eta: F) -> F:
        m, c = self.lines[bisect_right(self.knots, eta)]
        return m * eta + c

    @property
    def high(self) -> F:
        return self.lines[0][1]

    @property
    def low(self) -> F:
        return self.lines[-1][1]

    def inverse(self, b: F) -> F:
        if not self.low <= b <= self.high:
            raise ValueError(f'Promise {b} outside [{self.low}, {self.high}]')
        if not self.knots:
            return F(0)
        if b == self.high:
            return self.knots[0] - 1
        for i, (m, c) in enumerate(self.lines):
            if m < 0:
                x = (b-c)/m
                if (not i or self.knots[i-1] <= x) and (i == len(self.knots) or x <= self.knots[i]):
                    return x
        raise ArithmeticError('The continuous response failed to attain its range.')

    def json(self) -> dict:
        return {'knots': [str(k) for k in self.knots],
                'lines': [[str(m), str(c)] for m, c in self.lines]}


def read(raw: dict) -> tuple[list[dict], F]:
    beta = rat(raw.get('beta', 1))
    if not 0 < beta <= 1:
        raise ValueError('Discount factor must belong to (0,1].')
    nodes = []
    for i, row in enumerate(raw['nodes']):
        v = {k: rat(row[k]) for k in ('r','q','a','lo','hi','cap')}
        if not (v['q'] > 0 and v['a'] > 0 and 0 <= v['lo'] <= v['hi'] <= 1):
            raise ValueError(f'Invalid positive-payment quadratic primitives at {i}.')
        v['edges'] = [(int(j), rat(p)) for j,p in row.get('edges', [])]
        if any(not i < j < len(raw['nodes']) or p <= 0 for j,p in v['edges']):
            raise ValueError('Vertices must be topologically ordered with positive edges.')
        if len({j for j,p in v['edges']}) != len(v['edges']):
            raise ValueError('Aggregate duplicate edges before compilation.')
        if v['edges'] and sum(p for _,p in v['edges']) != 1:
            raise ValueError('Successor probabilities must sum to one.')
        nodes.append(v)
    if not nodes:
        raise ValueError('Empty public graph.')
    reachable = {0}
    for i, v in enumerate(nodes):
        if i in reachable:
            reachable.update(j for j,p in v['edges'])
    if len(reachable) != len(nodes):
        raise ValueError('Remove unreachable input vertices first.')
    return nodes, beta


@dataclass
class Compilation:
    nodes: list[dict]
    beta: F
    curves: list[Curve]
    barriers: list[F | None]

    def statistics(self) -> dict:
        coef = [x for c in self.curves for line in c.lines for x in line]
        knots = {k for c in self.curves for k in c.knots}
        return {'public_nodes': len(self.nodes),
                'public_edges': sum(len(v['edges']) for v in self.nodes),
                'global_breakpoints': len(knots),
                'stored_segments': sum(len(c.lines) for c in self.curves),
                'max_node_segments': max(len(c.lines) for c in self.curves),
                'coefficient_max_bits': max(max(abs(x.numerator).bit_length(),x.denominator.bit_length()) for x in coef),
                'knot_max_bits': max([0]+[max(abs(x.numerator).bit_length(),x.denominator.bit_length()) for x in knots])}


def compile_graph(raw: dict) -> Compilation:
    nodes, beta = read(raw)
    n = len(nodes)
    curves: list[Curve | None] = [None]*n
    barriers: list[F | None] = [None]*n
    for i in reversed(range(n)):
        v = nodes[i]
        a,r,q,lo,hi = (v[k] for k in ('a','r','q','lo','hi'))
        events: dict[F, tuple[F,F]] = {}
        def event(k: F, dm: F, dc: F) -> None:
            old = events.get(k, (F(0),F(0)))
            events[k] = old[0]+dm, old[1]+dc
        if lo < hi:
            lowk, highk = (r-q*hi)/a, (r-q*lo)/a
            event(lowk, -a*a/q, a*r/q-a*hi)
            event(highk, a*a/q, a*lo-a*r/q)
        high = a*hi
        low = a*lo
        for j,p in v['edges']:
            c = curves[j]
            assert c is not None
            high += beta*p*c.high
            low += beta*p*c.low
            for k, prev, nxt in zip(c.knots,c.lines,c.lines[1:]):
                event(k,beta*p*(nxt[0]-prev[0]),beta*p*(nxt[1]-prev[1]))
        if low > v['cap']:
            raise ValueError(f'Infeasible continuation at vertex {i}.')
        ks, lines = [], [(F(0), high)]
        for k,(dm,dc) in sorted(events.items()):
            if dm or dc:
                cur = (lines[-1][0]+dm, lines[-1][1]+dc)
                ks.append(k); lines.append(cur)
        pre = Curve(tuple(ks),tuple(lines))
        assert pre.low == low and pre.lines[-1][0] == 0
        if v['cap'] >= high:
            curves[i] = pre
            continue
        alpha = pre.inverse(v['cap'])
        barriers[i] = alpha
        idx = bisect_right(pre.knots,alpha)
        k2, l2 = [], [(F(0),v['cap'])]
        if pre.lines[idx] != l2[-1]:
            k2.append(alpha); l2.append(pre.lines[idx])
        for k,line in zip(pre.knots[idx:], pre.lines[idx+1:]):
            if line != l2[-1]:
                k2.append(k); l2.append(line)
        curves[i] = Curve(tuple(k2),tuple(l2))
    return Compilation(nodes,beta,curves,barriers)  # type: ignore[arg-type]


def execute(c: Compilation, promise: F, *, eta: F | None=None,
            serialize_curves: bool=True) -> dict:
    eta = c.curves[0].inverse(promise) if eta is None else eta
    if c.curves[0].at(eta) != promise:
        raise ValueError('Provided root price does not satisfy the exact promise.')
    reach: dict[int,dict[F,F]] = {0:{eta:F(1)}}
    states = []; reward_groups={}; payment_groups={}
    for i,v in enumerate(c.nodes):
        for incoming,w in sorted(reach.get(i,{}).items()):
            al = c.barriers[i]
            s = incoming if al is None else max(incoming,al)
            x = clip((v['r']-v['a']*s)/v['q'],v['lo'],v['hi'])
            grad = v['r']-v['q']*x-v['a']*s
            reward_groups[s] = reward_groups.get(s,F(0)) + w*(v['r']*x-v['q']*x*x/2)
            payment_groups[s] = payment_groups.get(s,F(0)) + w*v['a']*x
            states.append(dict(node=i,incoming=str(incoming),price=str(s),weight=str(w),
                               x=str(x),chi=str(s-incoming),lower=str(max(F(0),-grad)),
                               upper=str(max(F(0),grad)),payment=str(c.curves[i].at(incoming))))
            for j,p in v['edges']:
                dst = reach.setdefault(j,{})
                dst[s] = dst.get(s,F(0))+w*c.beta*p
    reward=sum(reward_groups.values(),F(0)); payment=sum(payment_groups.values(),F(0))
    assert payment == promise
    stats = c.statistics()
    stats['reachable_price_pairs'] = len(states)
    stats['distinct_incoming_prices'] = len({p for d in reach.values() for p in d})
    return dict(value=str(reward),payment=str(payment),root_price=str(eta),
                barriers=[None if a is None else str(a) for a in c.barriers],
                curves=[cv.json() for cv in c.curves] if serialize_curves else [],
                states=states,statistics=stats)


def solve(raw: dict) -> dict:
    return execute(compile_graph(raw),rat(raw['promise']))


def minimal_machine(raw: dict, certificate: dict) -> dict:
    """Backward behavioral quotient of reached (public vertex, incoming price) pairs.

    Class indices are local to a public vertex. A common writable alphabet can
    reuse those indices because the decoder observes the current public vertex.
    """
    by_v: dict[int,list[dict]] = {}
    for s in certificate['states']:
        by_v.setdefault(s['node'],[]).append(s)
    classes: dict[tuple[int,F],int] = {}
    groups=[]
    for v in reversed(range(len(raw['nodes']))):
        seen={}; rows=[]
        for s in sorted(by_v.get(v,[]),key=lambda s:F(s['incoming'])):
            price=F(s['price'])
            children=tuple((j,classes[(j,price)]) for j,p in raw['nodes'][v]['edges'])
            signature=(F(s['x']),children)
            k=seen.setdefault(signature,len(seen))
            classes[v,F(s['incoming'])]=k
            rows.append(dict(incoming=s['incoming'],label=k,action=s['x'],children=list(children)))
        sequence=[x['label'] for x in rows]
        # Each behavior class is a contiguous block in incoming price order.
        blocks=[x for i,x in enumerate(sequence) if not i or x!=sequence[i-1]]
        assert len(blocks)==len(set(sequence))
        groups.append(dict(node=v,classes=len(seen),states=rows))
    required=max(g['classes'] for g in groups)
    return dict(minimal_symbols=required,writable_bits=(required-1).bit_length(),
                max_raw_states_at_vertex=max(len(x) for x in by_v.values()),
                groups=list(reversed(groups)))
