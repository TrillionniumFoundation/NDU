"""Current public interface; exact inherited engines are snapshotted by prepare.py.

All model inputs are integers, rational strings, or fractions.Fraction. PADS
substitution is process-local and deliberately not a thread-safe operation.
The return value is (solutions, measured oracle-work dictionary).
"""
from __future__ import annotations
from bisect import bisect_right
from contextlib import contextmanager
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import sys
from pads_excerpt import ConcaveMinima

HERE = Path(__file__).resolve().parent
PATH = HERE / 'snapshots/or-r36-linear-frontier-20260924/linear_frontier.py'
NAME = '_ndu_r37_exact_linear'
spec = importlib.util.spec_from_file_location(NAME, PATH)
if spec is None or spec.loader is None:
    raise ImportError('Run the revision prepare step before importing frontier.')
linear = importlib.util.module_from_spec(spec)
sys.modules[NAME] = linear
spec.loader.exec_module(linear)
quadratic, divide = linear.old, linear.previous
Problem, Solution = linear.Problem, linear.Solution


def pads_rows(rows, columns, key, work=None):
    if not rows:
        return {}
    if not columns:
        raise ValueError('A nonempty matrix needs a column.')
    if work is not None:
        work.searches += 1
    found = ConcaveMinima(list(columns), list(rows), lambda c, r: key(r, c))
    return {r: item[1] for r, item in found.items()}


@contextmanager
def external_search():
    original = linear.smawk_minima
    linear.smawk_minima = pads_rows
    try:
        yield
    finally:
        linear.smawk_minima = original


def solve(problem: Problem, budget: int, institution: str = 'expected',
          engine: str = 'linear'):
    if institution not in ('expected', 'pathwise'):
        raise ValueError('institution must be expected or pathwise')
    name = ('randomized_frontiers' if institution == 'expected'
            else 'deterministic_frontiers')
    if engine == 'quadratic':
        return getattr(quadratic, name)(problem, budget), {}
    if engine == 'divide':
        ans, work = getattr(divide, name)(problem, budget)
    elif engine == 'linear':
        ans, work = getattr(linear, name)(problem, budget)
    elif engine == 'pads':
        with external_search():
            ans, work = getattr(linear, name)(problem, budget)
    else:
        raise ValueError('Unknown engine: ' + engine)
    measured = asdict(work)
    if engine == 'pads':
        # PADS does not expose comparisons or recursion depth. Zero is not a
        # measurement of those quantities; use null rather than a false count.
        measured['comparisons'] = None
        measured['peak_recursion_depth'] = None
    return ans, measured


def instance(k: int) -> Problem:
    if k < 1:
        raise ValueError('k must be positive')
    return Problem.make([F(j, k+1) for j in range(1, k+1)],
                        [F(2*j, k*(k+1)) for j in range(1, k+1)],
                        [F(j % 5, 3) for j in range(1, k+1)])


def deterministic_loss(p: Problem, levels) -> F:
    c = tuple(sorted(set(levels)))
    if not c or c[0] > p.caps[0] or c[0] < 0 or c[-1] > 1:
        raise ValueError('Infeasible codebook')
    value = F(0)
    for b, w, g in zip(p.caps, p.probabilities, p.gamma):
        u = c[bisect_right(c, b)-1]
        value += w*(p.reward(b)-p.reward(u)+g*(b-u)**2/2)
    return value


def verify_solution(p: Problem, sol: Solution, budget: int, institution: str):
    if len(sol.codebook) > budget:
        raise AssertionError('Controller exceeds alphabet budget')
    got = (quadratic.codebook_loss(p, sol.codebook) if institution == 'expected'
           else deterministic_loss(p, sol.codebook))
    if got != sol.loss:
        raise AssertionError('Direct branch replay disagrees with frontier')
    if institution == 'expected':
        quadratic.audit(p, sol, budget)
    return True


def bounded_loss(p: Problem, levels, delta) -> F:
    """Fixed codebook under pre-draw deterministic Y and a.s. total <= b+delta."""
    delta = quadratic.rational(delta)
    c = tuple(sorted(set(map(quadratic.rational, levels))))
    if delta < 0 or not c or c[0] > p.caps[0] or c[0] < 0 or c[-1] > 1:
        raise ValueError('Invalid bounded-overrun problem')
    total = F(0)
    for b, w, g in zip(p.caps, p.probabilities, p.gamma):
        i = bisect_right(c, b)-1
        u = c[i]
        if u < b and i+1 < len(c) and c[i+1]-b <= delta:
            v = c[i+1]
            weight = (b-u)/(v-u)
            payoff = (1-weight)*p.reward(u)+weight*p.reward(v)
        else:
            payoff = p.reward(u)-g*(b-u)**2/2
        total += w*(p.reward(b)-payoff)
    return total


def bounded_pair_enumeration(p: Problem, levels, delta) -> F:
    """Independent all-pairs check; do not invoke adjacent-codeword structure."""
    c, delta = tuple(sorted(set(map(F, levels)))), F(delta)
    result = F(0)
    for b, w, g in zip(p.caps, p.probabilities, p.gamma):
        candidates = [p.reward(u)-g*(b-u)**2/2 for u in c if u <= b]
        for u in c:
            for v in c:
                if u >= v:
                    continue
                mu = min(b, v)
                if mu <= u or v > mu+delta:
                    continue
                t = (mu-u)/(v-u)
                candidates.append((1-t)*p.reward(u)+t*p.reward(v)-g*(b-mu)**2/2)
        if not candidates:
            raise ValueError('Infeasible branch')
        result += w*(p.reward(b)-max(candidates))
    return result


def serial_solutions(ans):
    return [{'loss': str(s.loss), 'codebook': list(map(str, s.codebook))} for s in ans]
