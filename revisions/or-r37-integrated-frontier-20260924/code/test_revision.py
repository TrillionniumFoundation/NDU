"""Exact R37 verification. Finite tests are regression evidence, not proofs."""
from __future__ import annotations
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement
from pathlib import Path
import hashlib
import json
import random
import shutil
import subprocess
import sys
import tempfile
from frontier import (Problem, bounded_loss, bounded_pair_enumeration, instance,
                      linear, pads_rows, solve, verify_solution)

R = Path(__file__).resolve().parents[1]
ROOT = R.parents[1]
OUT = R / 'results'
OUT.mkdir(exist_ok=True)
counts = {'completed_matrices': 0, 'strict_implications': 0,
          'all_selected_submatrix_row_minima': 0, 'padded_selected_rows': 0,
          'frontier_equalities': 0, 'controller_replays': 0,
          'bounded_all_pairs_equalities': 0, 'risk_frontier_equalities': 0,
          'nonanchor_grid_falsification_checks': 0, 'priced_resource_checks': 0}


def subsets(n):
    return [s for length in range(1, n+1) for s in combinations(range(n), length)]


def completion_tests():
    for n in range(1, 5):
        selections = subsets(n)
        offsets = ([0]*n, [(-1)**j*j for j in range(n)])
        for cuts in combinations_with_replacement(range(n+1), n):
            for orientation in ('suffix', 'prefix'):
                for slope in (0, 1):
                    for column_offset in offsets:
                        def feasible(r, c):
                            return c >= cuts[r] if orientation == 'suffix' else c < cuts[r]
                        def key(r, c):
                            if feasible(r, c):
                                return (0, F(r*r+column_offset[c]-slope*r*c), c)
                            return (1, F(0), -c if orientation == 'suffix' else c)
                        counts['completed_matrices'] += 1
                        for r, s in combinations(range(n), 2):
                            for c, d in combinations(range(n), 2):
                                if key(r, d) < key(r, c):
                                    assert key(s, d) < key(s, c)
                                    counts['strict_implications'] += 1
                        for rows in selections:
                            for cols in selections:
                                expected = {r: min(cols, key=lambda c: key(r, c)) for r in rows}
                                assert linear.smawk_minima(rows, cols, key) == expected
                                assert pads_rows(rows, cols, key) == expected
                                counts['all_selected_submatrix_row_minima'] += len(rows)
                                counts['padded_selected_rows'] += sum(
                                    not any(feasible(r, c) for c in cols) for r in rows)
    # Uniform infinity plus ordinary left ties reverses the suffix minima.
    bad = lambda r, c: (0, 0, c) if c >= r+1 else (1, 0, c)
    assert [min((0, 1), key=lambda c: bad(r, c)) for r in (0, 1)] == [1, 0]
    # Arbitrary two-sided domains are NOT covered by the theorem.
    assert [min((0, 1), key=lambda c: (0 if c == 1-r else 1, c)) for r in (0, 1)] == [1, 0]


def economic_tests():
    rng = random.Random(370924)
    problems = [instance(k) for k in range(1, 13)]
    for trial in range(48):
        k = 2 + trial % 7
        raw = sorted(rng.sample(range(1, 61), k))
        weights = [rng.randint(1, 12) for _ in range(k)]
        problems.append(Problem.make([F(j, 64) for j in raw],
                                     [F(w, sum(weights)) for w in weights],
                                     [F(rng.randint(0, 12), 5) for _ in range(k)],
                                     r=3, q=2))
    for p in problems:
        k = len(p.caps)
        for institution in ('expected', 'pathwise'):
            baseline, _ = solve(p, k, institution, 'quadratic')
            for engine in ('divide', 'linear', 'pads'):
                answers, _ = solve(p, k, institution, engine)
                for budget, (actual, wanted) in enumerate(zip(answers, baseline), 1):
                    assert actual.loss == wanted.loss
                    verify_solution(p, actual, budget, institution)
                    counts['frontier_equalities'] += 1
                    counts['controller_replays'] += 1
            assert baseline[-1].loss == 0


def institution_tests():
    p = Problem.make(['1/4', '1/2', '3/4'], ['7/20', '3/5', '1/20'], [1, 1, 1])
    grids = (F(1, 8), F(1, 4), F(3, 8), F(1, 2), F(5, 8), F(3, 4), F(7, 8))
    for size in (1, 2, 3):
        for book in combinations(grids, size):
            if book[0] > p.caps[0]:
                continue
            for delta in (F(0), F(1, 32), F(1, 8), F(1, 4), F(1)):
                assert bounded_loss(p, book, delta) == bounded_pair_enumeration(p, book, delta)
                counts['bounded_all_pairs_equalities'] += 1
    for delta in [F(j, 64) for j in range(33)]:
        z = F(1, 2)+min(delta, F(1, 8))
        value = z*z/20-z/16+F(3, 80)
        assert bounded_loss(p, (F(1, 4), z), delta) == value
        counts['risk_frontier_equalities'] += 1
        # Deliberately allow nonanchored low levels. This finite falsification
        # check supplements, and does not establish, the global proof.
        for u in (F(0), F(1, 16), F(1, 8), F(3, 16), F(1, 4)):
            for v in [F(j, 32) for j in range(8, 33)]:
                if v <= u:
                    continue
                assert bounded_loss(p, (u, v), delta) >= value
                counts['nonanchor_grid_falsification_checks'] += 1
    equal = Problem.make(['1/4', '1/2', '3/4'], ['1/3']*3, [1]*3)
    expected, _ = solve(equal, 3, 'expected')
    pathwise, _ = solve(equal, 3, 'pathwise')
    assert [s.loss for s in expected] == [F(7, 16), F(1, 96), F(0)]
    assert [s.loss for s in pathwise] == [F(7, 16), F(1, 8), F(0)]
    for price in (F(1, 48), F(1, 24), F(1, 12)):
        for institution, ans, selected in [('expected', expected, 1), ('pathwise', pathwise, 2)]:
            objective = [ans[0].loss, ans[1].loss+price, ans[2].loss+2*price]
            assert min(range(3), key=objective.__getitem__) == selected
            counts['priced_resource_checks'] += 1


def inherited_tests():
    folders = ['or-r33-piecewise-randomized-20260923',
               'or-r34-global-randomized-frontier-20260923',
               'or-r35-monge-frontier-20260923',
               'or-r36-linear-frontier-20260924']
    results = {}
    with tempfile.TemporaryDirectory(prefix='ndu-r37-inherited-') as tmp:
        dest = Path(tmp) / 'revisions'
        for folder in folders:
            (dest/folder).mkdir(parents=True)
            for source in (ROOT/'revisions'/folder).glob('*.py'):
                shutil.copy2(source, dest/folder/source.name)
        for version, folder in zip(('R33', 'R34', 'R35', 'R36'), folders):
            cmd = [sys.executable, str(dest/folder/'verify.py')]
            completed = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            (OUT/(version+'_inherited.log')).write_text(completed.stdout+'\n'+completed.stderr)
            if completed.returncode:
                raise RuntimeError(version+' inherited verification failed; see log')
            data = json.loads((dest/folder/'verification.json').read_text())
            assert data['status'] == 'PASS'
            results[version] = {'status': 'PASS', 'record': data,
                'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in (ROOT/'revisions'/folder).glob('*.py')}}
            print(version, 'inherited PASS', flush=True)
    return results


if __name__ == '__main__':
    completion_tests()
    print('All-submatrix completion tests PASS', flush=True)
    economic_tests()
    institution_tests()
    inherited = inherited_tests()
    result = {'status': 'PASS', 'counts': counts, 'inherited_suites': inherited,
              'scope': 'Exact finite regression, independent PADS search substitution, direct economic replay, and unchanged inherited suites. Not a proof by testing.'}
    (OUT/'verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(counts, indent=2), flush=True)
