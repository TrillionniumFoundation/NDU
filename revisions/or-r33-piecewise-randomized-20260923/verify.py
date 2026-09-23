"""Exact tests and a separate full-parametric active-set QP reference.

Run from any working directory: python path/to/verify.py
Writes verification.json and representation.csv beside this script.
No performance comparison to published solver implementations is implied.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import csv
import json
import random
import time
from exact_compiler import Piece, Reward, Vertex, Compiler

ROOT = Path(__file__).resolve().parent


def solve_two(matrix, rhs0, rhs1):
    a = [list(row)+[u, v] for row, u, v in zip(matrix, rhs0, rhs1)]
    n = len(a)
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        if pivot is None:
            return None
        a[j], a[pivot] = a[pivot], a[j]
        scale = a[j][j]
        a[j] = [z/scale for z in a[j]]
        for i in range(n):
            if i != j and a[i][j]:
                scale = a[i][j]
                a[i] = [z-scale*w for z, w in zip(a[i], a[j])]
    return [r[-2] for r in a], [r[-1] for r in a]


def active_set_path(vertices):
    """Enumerate the ENTIRE one-parameter solution path of the unfolded QP.

    Independent of price reflection/response merging; exact rational KKT systems
    for every independent active set. Small-instance reference, exponential cost.
    """
    occurrences = []
    def visit(v, weight):
        i = len(occurrences)
        occurrences.append([v, weight, None])
        descendants = [i]
        for j, p in vertices[v].edges:
            descendants += visit(j, weight*p)
        occurrences[i][2] = descendants
        return descendants
    visit(0, F(1))
    n = len(occurrences)
    assert n <= 5
    q, r, d, rows, bounds = [], [], [], [], []
    for i, (v, weight, _) in enumerate(occurrences):
        p, = vertices[v].reward.pieces
        q.append(weight*p.quadratic)
        r.append(weight*p.linear)
        d.append(weight*vertices[v].payment)
        for sign, bound in [(F(1), p.hi), (F(-1), -p.lo)]:
            row = [F(0)]*n
            row[i] = sign
            rows.append(row)
            bounds.append(bound)
    for v, weight, descendants in occurrences:
        row = [d[j] if j in descendants else F(0) for j in range(n)]
        bound = weight*vertices[v].cap
        physical_max = sum(row[j]*vertices[occurrences[j][0]].reward.pieces[-1].hi for j in range(n))
        if bound < physical_max:
            rows.append(row)
            bounds.append(bound)
    candidates, attempted = [], 0
    for count in range(n+1):
        for selected in combinations(range(len(rows)), count):
            attempted += 1
            active = [rows[i] for i in selected]
            mat = [[q[i] if i == j else F(0) for j in range(n)]
                   + [row[i] for row in active] for i in range(n)]
            mat += [row+[F(0)]*count for row in active]
            sol = solve_two(mat, r+[bounds[j] for j in selected], [-z for z in d]+[F(0)]*count)
            if sol is None:
                continue
            u, v = sol
            inequalities = [(sum(row[j]*u[j] for j in range(n))-b,
                             sum(row[j]*v[j] for j in range(n))) for row, b in zip(rows, bounds)]
            inequalities += [(-u[j], -v[j]) for j in range(n, n+count)]
            lo = hi = None
            valid = True
            for c, m in inequalities:
                if not m:
                    if c > 0:
                        valid = False
                        break
                elif m > 0:
                    z = -c/m
                    hi = z if hi is None else min(hi, z)
                else:
                    z = -c/m
                    lo = z if lo is None else max(lo, z)
            if valid and (lo is None or hi is None or lo < hi):
                candidates.append((lo, hi, sum(d[j]*v[j] for j in range(n)),
                                    sum(d[j]*u[j] for j in range(n))))
    assert candidates
    return candidates, attempted


def quadratic(r, q=1):
    return Reward((Piece(0, 1, 0, r, q),))


def kinked(r, q1, q2, jump):
    t = F(1, 2)
    p = Piece(0, t, 0, r, q1)
    r2 = r-q1*t+q2*t-jump
    c2 = p.value(t)-r2*t+q2*t*t/2
    return Reward((p, Piece(t, 1, c2, r2, q2)))


def probes(knots):
    knots = sorted(set(knots))
    if not knots:
        return [F(0)]
    return [knots[0]-1, *knots, *[(a+b)/2 for a, b in zip(knots, knots[1:])], knots[-1]+1]


def deterministic_frontier(caps, m):
    def cost(i, j):
        return sum((2-caps[i])*(caps[h]-caps[i]) for h in range(i, j))/len(caps)
    return min(sum(cost(a, b) for a, b in zip((0,)+cuts, cuts+(len(caps),)))
               for cuts in combinations(range(1, len(caps)), m-1))


def randomized_loss(caps, levels):
    if not levels or list(levels) != sorted(levels) or levels[0] > min(caps):
        raise ValueError('Invalid terminal alphabet')
    f = lambda x: 2*x-x*x/2
    loss = F(0)
    for b in caps:
        mean = min(b, levels[-1])
        if mean == levels[-1]:
            reward = f(mean)
        else:
            i = next(i for i in range(len(levels)-1) if levels[i] <= mean <= levels[i+1])
            u, v = levels[i:i+2]
            reward = f(u)+(mean-u)*(f(v)-f(u))/(v-u)
        loss += f(b)-reward+(b-mean)**2/2
    return loss/len(caps)


def run():
    start = time.perf_counter()
    checks, circuits, certs, inversions = 0, 0, 0, 0
    rng = random.Random(20260923)
    # Smooth joins, genuine kinks, redundant and binding caps, rational discounts,
    # recombination, plateaus, and exact endpoints.
    for trial in range(24):
        rewards = [kinked(F(rng.randint(1, 6)), F(rng.randint(1, 4)),
                           F(rng.randint(1, 4)), F(trial % 3, 2)) for _ in range(5)]
        edges = [((1, F(1, 3)), (2, F(2, 3))), ((3, F(1)),),
                 ((3, F(1)),), ((4, F(1)),), ()]
        vs = [Vertex(g, F(rng.randint(1, 3)), F(rng.randint(1, 7), 3), e)
              for g, e in zip(rewards, edges)]
        comp = Compiler(vs, F(9, 10))
        assert len(comp.global_knots) <= 2*10+5
        for eta in probes(comp.global_knots):
            for i, v in enumerate(vs):
                assert comp.local[i].value(eta) == v.reward.direct_max(eta, v.payment)
                checks += 1
            direct = comp.circuit_values(eta)
            assert direct == tuple(c.value(eta) for c in comp.responses)
            circuits += 1
            comp.certificate(eta)
            certs += 1
            b = direct[0]
            assert comp.responses[0].value(comp.circuit_inverse(b)) == b
            inversions += 1
    # Fixed interval and cap at the exact minimum, including complete flat output.
    fixed = Reward((Piece(F(1, 4), F(1, 4), 0, 2, 1),))
    c = Compiler([Vertex(fixed, 1, F(1, 4))])
    c.certificate(F(7))
    assert c.circuit_inverse(F(1, 4)) == 0
    c = Compiler([Vertex(quadratic(2), 1, 0)])
    c.certificate(F(-3))
    assert c.responses[0].value(9) == 0
    try:
        Compiler([Vertex(fixed, 1, 0)])
        raise AssertionError('Infeasible cap accepted')
    except ValueError:
        pass
    # Independent complete parametric QP paths, not isolated numerical queries.
    path_records = []
    for t in range(4):
        vs = [Vertex(quadratic(2+t, 1), 1, F(4, 3), ((1, F(1)),)),
              Vertex(quadratic(3, 2), 1, F(5, 4), ((2, F(1)),)),
              Vertex(quadratic(4-t, 3), 1, F(3, 4))]
        comp = Compiler(vs)
        candidates, attempted = active_set_path(vs)
        knots = sorted(set(comp.responses[0].knots) |
                       {x for item in candidates for x in item[:2] if x is not None})
        for eta in probes(knots):
            eligible = [m*eta+b for lo, hi, m, b in candidates
                        if (lo is None or lo <= eta) and (hi is None or eta <= hi)]
            assert eligible and set(eligible) == {comp.responses[0].value(eta)}
        # Equality of affine coefficients on EVERY open cell is the full-path test.
        intervals = [(None, knots[0])]+list(zip(knots, knots[1:]))+[(knots[-1], None)]
        for lo, hi in intervals:
            eta = hi-1 if lo is None else lo+1 if hi is None else (lo+hi)/2
            lines = {(m, b) for a, z, m, b in candidates
                     if (a is None or a < eta) and (z is None or eta < z)}
            assert lines == {comp.responses[0].line(eta)}
        path_records.append({'instance': t, 'active_sets_attempted': attempted,
                             'valid_kkt_regions': len(candidates),
                             'open_cells_compared': len(intervals), 'full_path_equal': True})
    representation = []
    for n in [2, 4, 8, 16, 32, 64, 128]:
        vs = [Vertex(quadratic(2*(i+1)), 1, n-i,
                     ((i+1, F(1)),) if i+1 < n else ()) for i in range(n)]
        before = time.perf_counter()
        comp = Compiler(vs)
        elapsed = time.perf_counter()-before
        segments = sum(len(c.lines) for c in comp.responses)
        assert segments == n*n+2*n
        assert len(set(t for c in comp.responses for t in c.knots)) == 2*n
        for eta in [F(-1), F(n, 2), F(2*n+1)]:
            assert comp.circuit_values(eta) == tuple(c.value(eta) for c in comp.responses)
        representation.append({'N': n, 'M': n-1, 'global_knots': 2*n,
                               'explicit_segments': segments, 'circuit_graph_nodes': n,
                               'local_curve_segments': sum(len(c.lines) for c in comp.local),
                               'compiler_seconds': elapsed})
    caps = [F(1, 4), F(1, 2), F(3, 4)]
    assert deterministic_frontier(caps, 2) == F(1, 8)
    assert randomized_loss(caps, [caps[0], caps[-1]]) == F(1, 96)
    # Rational endpoint search is only a regression check; the global proof is in text.
    for u in [F(j, 64) for j in range(17)]:
        for v in [F(j, 64) for j in range(17, 65)]:
            assert randomized_loss(caps, [u, v]) >= F(1, 96)
    assert randomized_loss(caps, caps) == 0
    record = {'status': 'PASS', 'arithmetic': 'fractions.Fraction; no numerical tolerances',
              'random_seed': 20260923, 'piecewise_dag_instances': 24,
              'local_optimality_checks': checks, 'whole_graph_circuit_checks': circuits,
              'primal_dual_certificates': certs+2, 'circuit_inversions': inversions,
              'parametric_active_set_reference': path_records,
              'chain_sizes': [r['N'] for r in representation],
              'deterministic_two_symbol_loss': '1/8', 'randomized_two_symbol_loss': '1/96',
              'runtime_seconds': time.perf_counter()-start,
              'limitations': ['Synthetic exact verification, not service data.',
                              'Active-set reference is exponential, not published solver software.',
                              'Timing is descriptive and environment-dependent.']}
    (ROOT/'verification.json').write_text(json.dumps(record, indent=2)+'\n')
    with (ROOT/'representation.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(representation[0]))
        writer.writeheader()
        writer.writerows(representation)
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    run()
