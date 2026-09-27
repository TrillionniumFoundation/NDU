"""Finite reduced-network comparison using SciPy's compiled HiGHS dual simplex.

All costs below are assembled from direct branch sums, not prefix moments.
HiGHS uses floating point. Its selected integral path is repriced in Fraction,
and an exact shortest-path potential certifies its reduced-network optimum.
This checks a finite reduction already proved in the paper, not the reduction
itself. Construction, solver, and certification times are recorded separately.
"""
from __future__ import annotations
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
from time import perf_counter
import json
import platform
import sys
import numpy as np
import scipy
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from frontier import Problem, Solution, instance, solve, verify_solution

R = Path(__file__).resolve().parents[1]
OUT = R/'results'
OUT.mkdir(exist_ok=True)


class DirectCosts:
    def __init__(self, p):
        self.p = p

    @lru_cache(None)
    def edge(self, i, j):
        p = self.p
        u, v = p.caps[i], p.caps[j]
        return p.q/2*sum((w*(b-u)*(v-b) for b, w in
                         zip(p.caps[i:j+1], p.probabilities[i:j+1])), F(0))

    @lru_cache(None)
    def cell(self, i, j):
        p, u = self.p, self.p.caps[i]
        return sum((p.probabilities[h]*(p.reward(p.caps[h])-p.reward(u)
                    +p.gamma[h]*(p.caps[h]-u)**2/2) for h in range(i, j)), F(0))

    @lru_cache(None)
    def tail(self, i):
        p, k = self.p, len(self.p.caps)
        u, best = p.caps[i], None
        for ell in range(i, k):
            low, high = p.caps[ell], p.caps[min(ell+1, k-1)]
            A = sum((p.probabilities[h]*(p.q+p.gamma[h])/2
                     for h in range(ell+1, k)), F(0))
            B = p.q/2*sum((p.probabilities[h]*(p.caps[h]-u)
                           for h in range(i+1, ell+1)), F(0))
            B -= sum((p.probabilities[h]*(p.r+p.gamma[h]*p.caps[h])
                      for h in range(ell+1, k)), F(0))
            z = max(low, min(high, -B/(2*A))) if A else (low if B >= 0 else high)
            value = p.q/2*sum((p.probabilities[h]*(p.caps[h]-u)*(z-p.caps[h])
                               for h in range(i+1, ell+1)), F(0))
            value += sum((p.probabilities[h]*(p.reward(p.caps[h])-p.reward(z)
                          +p.gamma[h]*(p.caps[h]-z)**2/2)
                          for h in range(ell+1, k)), F(0))
            item = (value, z, ell)
            if best is None or item < best:
                best = item
        assert best is not None
        return best


def network(p, m, institution):
    k, d = len(p.caps), DirectCosts(p)
    source, sink = (-1, -1), (m+1, k+1)
    arcs = []
    def add(u, v, c, meta=None):
        arcs.append((u, v, c, meta))
    if institution == 'expected':
        add(source, sink, d.cell(0, k), ('single',))
        if m >= 2:
            add(source, (1, 0), F(0))
            for s in range(1, m):
                for i in ([0] if s == 1 else range(s-1, k)):
                    cost, z, ell = d.tail(i)
                    add((s, i), sink, cost, ('top', z))
                    if s+1 < m:
                        for j in range(i+1, k):
                            add((s, i), (s+1, j), d.edge(i, j))
    else:
        add(source, (0, 0), F(0))
        for s in range(1, m+1):
            for i in ([0] if s == 1 else range(s-1, k)):
                for j in range(i+1, k+1):
                    add((s-1, i), (s, j), d.cell(i, j), ('cell', i))
            add((s, k), sink, F(0))
    return source, sink, arcs


def certify(source, sink, arcs, selected):
    nodes = sorted({v for a in arcs for v in a[:2]})
    outgoing = {v: [] for v in nodes}
    for index, (u, v, cost, _) in enumerate(arcs):
        assert u < v, 'The certificate relies on the displayed DAG order.'
        outgoing[u].append(index)
    distance = {source: F(0)}
    for u in nodes:
        if u not in distance:
            continue
        for index in outgoing[u]:
            _, v, cost, _ = arcs[index]
            candidate = distance[u]+cost
            if v not in distance or candidate < distance[v]:
                distance[v] = candidate
    assert sink in distance
    for u, v, cost, _ in arcs:
        if u in distance:
            assert distance[v] <= distance[u]+cost
    chosen = set(selected)
    at, path, cost = source, [], F(0)
    while at != sink:
        candidates = [i for i in outgoing[at] if i in chosen]
        assert len(candidates) == 1
        index = candidates[0]
        chosen.remove(index)
        path.append(index)
        _, at, amount, _ = arcs[index]
        cost += amount
    assert not chosen and cost == distance[sink]
    return cost, path, distance


def compare(k, m, institution):
    p = instance(k)
    begin = perf_counter()
    source, sink, arcs = network(p, m, institution)
    nodes = sorted({v for a in arcs for v in a[:2]})
    indices = {v: i for i, v in enumerate(nodes)}
    rows, columns, values = [], [], []
    for j, (u, v, _, _) in enumerate(arcs):
        rows.extend((indices[u], indices[v]))
        columns.extend((j, j))
        values.extend((1.0, -1.0))
    incidence = coo_matrix((values, (rows, columns)), shape=(len(nodes), len(arcs))).tocsr()
    demand = np.zeros(len(nodes))
    demand[indices[source]], demand[indices[sink]] = 1, -1
    costs = np.array([float(a[2]) for a in arcs])
    construction = perf_counter()-begin
    begin = perf_counter()
    lp = linprog(costs, A_eq=incidence, b_eq=demand, bounds=(0, None),
                 method='highs-ds', options={'time_limit': 120})
    solver_time = perf_counter()-begin
    if not lp.success:
        raise AssertionError(f'HiGHS failed at {(k, m, institution)}: {lp.message}')
    begin = perf_counter()
    deviation = float(np.max(np.minimum(np.abs(lp.x), np.abs(lp.x-1))))
    assert deviation < 1e-7, 'Floating solution was not an integral path.'
    chosen = [i for i, value in enumerate(lp.x) if value > .5]
    value, path, potentials = certify(source, sink, arcs, chosen)
    levels = []
    if institution == 'expected':
        for index in path:
            u, v, _, meta = arcs[index]
            if v != sink and v[0] >= 1:
                levels.append(p.caps[v[1]])
            if meta and meta[0] == 'top':
                levels.append(meta[1])
            elif meta and meta[0] == 'single':
                levels.append(p.caps[0])
    else:
        for index in path:
            meta = arcs[index][3]
            if meta and meta[0] == 'cell':
                levels.append(p.caps[meta[1]])
    solution = Solution(value, tuple(sorted(set(levels))))
    verify_solution(p, solution, m, institution)
    baseline, _ = solve(p, m, institution, 'linear')
    assert value == baseline[-1].loss
    certification_time = perf_counter()-begin
    return {'k': k, 'budget': m, 'institution': institution, 'status': 'PASS',
            'nodes': len(nodes), 'arcs': len(arcs), 'construction_seconds': construction,
            'highs_seconds': solver_time, 'exact_reprice_replay_and_frontier_seconds': certification_time,
            'float_objective': float(lp.fun), 'integrality_deviation': deviation,
            'exact_objective': str(value), 'codebook': list(map(str, solution.codebook)),
            'selected_arcs': path, 'exact_sink_potential': str(potentials[sink]),
            'solver_iterations': int(lp.nit)}


if __name__ == '__main__':
    records = []
    for k in (8, 16, 32, 64):
        for m in (2, 4, 8):
            for institution in ('expected', 'pathwise'):
                record = compare(k, m, institution)
                records.append(record)
                print(k, m, institution, 'PASS', flush=True)
    data = {'status': 'PASS', 'python': sys.version, 'scipy': scipy.__version__,
            'platform': platform.platform(), 'records': records,
            'scope': 'Compiled floating-point HiGHS on independently assembled exact-cost finite networks; each returned path is repriced and certified with exact rational shortest-path potentials. Not an external continuous-model proof or an optimized native SMAWK benchmark.'}
    (OUT/'external_solver.json').write_text(json.dumps(data, indent=2)+'\n')
