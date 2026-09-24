"""Exact Monge acceleration for the R34 randomized renewal frontier.

Run from any directory. Python standard library only; all economic inputs
are exact Fractions through the inherited validated Problem.make interface.
Both terminal-interval and prefix searches use leftmost ties. No floating
sentinels, codeword grid, tolerance, or quadratic cost array is used.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
from typing import Callable
import importlib.util
import sys

_OLD = Path(__file__).resolve().parents[1] / 'or-r34-global-randomized-frontier-20260923' / 'randomized_frontier.py'
_NAME = '_ndu_r34_exact_frontier'
if _NAME not in sys.modules:
    _spec = importlib.util.spec_from_file_location(_NAME, _OLD)
    if _spec is None or _spec.loader is None:
        raise ImportError(f'Cannot load inherited frontier from {_OLD}')
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_NAME] = _module
    _spec.loader.exec_module(_module)
old = sys.modules[_NAME]
Problem, Solution, Moments = old.Problem, old.Solution, old.Moments


@dataclass
class Work:
    """Count economic oracle calls, not hardware-independent runtime."""
    tail_evaluations: int = 0
    edge_evaluations: int = 0
    cell_evaluations: int = 0
    peak_recursion_depth: int = 0


def monotone_minima(first: int, last: int, column_first: int,
                    column_last: int, bounds: Callable[[int], tuple[int, int]],
                    cost: Callable[[int, int], F], work: Work) -> dict[int, tuple[F, int]]:
    """Leftmost minima of a staircase matrix with proved monotone argmins.

    The caller must establish the monotonicity property; this routine is not
    a general optimizer for arbitrary matrices. Every supplied row is feasible.
    It evaluates only valid entries and does not pad with an infinity value.
    """
    result: dict[int, tuple[F, int]] = {}
    def solve(lo: int, hi: int, left: int, right: int, depth: int) -> None:
        if lo > hi:
            return
        work.peak_recursion_depth = max(work.peak_recursion_depth, depth)
        row = (lo + hi) // 2
        valid_first, valid_last = bounds(row)
        start, end = max(left, valid_first), min(right, valid_last)
        if start > end:
            raise RuntimeError('Empty search interval: violated monotone-search invariant')
        winner = start
        value = cost(row, winner)
        for col in range(start + 1, end + 1):
            candidate = cost(row, col)
            if candidate < value:  # Strict comparison preserves the LEFTMOST tie.
                value, winner = candidate, col
        result[row] = (value, winner)
        solve(lo, row - 1, left, winner, depth + 1)
        solve(row + 1, hi, winner, right, depth + 1)
    if first <= last:
        solve(first, last, column_first, column_last, 1)
    return result


class Oracle:
    def __init__(self, p: Problem, work: Work):
        self.p, self.work, self.moments = p, work, Moments(p)
        self.k = len(p.caps)

    def interval(self, i: int, ell: int) -> tuple[F, F]:
        if not 0 <= i <= ell < self.k:
            raise IndexError('Terminal cell requires 0 <= i <= ell < k')
        self.work.tail_evaluations += 1
        A, B, C = self.moments.tail_polynomial(i, ell)
        lo = self.p.caps[ell]
        hi = self.p.caps[min(ell + 1, self.k - 1)]
        z = max(lo, min(hi, -B / (2 * A))) if A else (lo if B >= 0 else hi)
        return A * z * z + B * z + C, z

    def edge(self, i: int, j: int) -> F:
        if not 0 <= i < j < self.k:
            raise IndexError('Prefix edge requires 0 <= i < j < k')
        self.work.edge_evaluations += 1
        return self.moments.edge(i, j)


def terminal_minima(p: Problem, work: Work | None = None) -> tuple[list[tuple[F, F, int]], Work]:
    """Optimize the continuous highest level for every possible final anchor."""
    work = work if work is not None else Work()
    oracle, k = Oracle(p, work), len(p.caps)
    rows = monotone_minima(0, k - 1, 0, k - 1, lambda i: (i, k - 1),
                          lambda i, ell: oracle.interval(i, ell)[0], work)
    answer = []
    for i in range(k):
        value, ell = rows[i]
        check, z = oracle.interval(i, ell)
        if check != value:
            raise AssertionError('Inconsistent exact terminal oracle')
        answer.append((value, z, ell))
    return answer, work


def randomized_frontiers(p: Problem, max_symbols: int) -> tuple[list[Solution], Work]:
    """Return all requested globally optimal frontiers and measured oracle work.

    For m <= k: O(m*k*log(k+1)) rational work, O(m*k+k) scalar/index
    storage including all backpointers and output codebooks. m > k adds only
    repeated zero-loss output entries. This is the proved divide-and-conquer
    implementation, not an implementation or complexity claim for SMAWK.
    """
    old._budget(max_symbols)
    k, limit, work = len(p.caps), min(max_symbols, len(p.caps)), Work()
    base = Solution(old.codebook_loss(p, (p.caps[0],)), (p.caps[0],))
    answers = [base]
    if limit == 1:
        return answers * max_symbols, work
    tails, _ = terminal_minima(p, work)
    oracle = Oracle(p, work)
    dp: list[F | None] = [None] * k
    dp[0] = F(0)
    predecessors: dict[tuple[int, int], int] = {}
    for anchors in range(1, limit):
        incumbent, best_j = answers[-1], None
        best_loss = incumbent.loss
        for j in range(k):
            if dp[j] is not None:
                value = dp[j] + tails[j][0]
                if value < best_loss:
                    best_loss, best_j = value, j
        # Reconstruct only the winning codebook, once per budget.
        if best_j is not None:
            indices, at = [best_j], best_j
            for layer in range(anchors, 1, -1):
                at = predecessors[layer, at]
                indices.append(at)
            levels = tuple(p.caps[t] for t in reversed(indices))
            top = tails[best_j][1]
            if top > levels[-1]:
                levels += (top,)
            incumbent = Solution(best_loss, levels)
        answers.append(incumbent)
        if anchors + 1 >= limit:
            break
        new: list[F | None] = [None] * k
        # With one anchor the only reachable endpoint is b_1. Subsequently
        # exactly 'anchors' anchors allow all endpoint indices >= anchors-1.
        col_lo = anchors - 1
        col_hi = 0 if anchors == 1 else k - 2
        def bounds(j: int) -> tuple[int, int]:
            return col_lo, min(j - 1, col_hi)
        def value(j: int, i: int) -> F:
            previous = dp[i]
            if previous is None:
                raise AssertionError('Search touched an infeasible prefix state')
            return previous + oracle.edge(i, j)
        rows = monotone_minima(anchors, k - 1, col_lo, col_hi, bounds, value, work)
        for j, (cost, i) in rows.items():
            new[j] = cost
            predecessors[anchors + 1, j] = i
        dp = new
    answers.extend([answers[-1]] * (max_symbols - len(answers)))
    return answers, work


def deterministic_frontiers(p: Problem, max_symbols: int) -> tuple[list[Solution], Work]:
    """Monge-accelerated deterministic (equivalently pathwise) frontiers."""
    old._budget(max_symbols)
    k, limit, work = len(p.caps), min(max_symbols, len(p.caps)), Work()
    moments = Moments(p)
    dp: list[F | None] = [None] * (k + 1)
    dp[0] = F(0)
    back: dict[tuple[int, int], int] = {}
    answers = []
    for symbols in range(1, limit + 1):
        left, right = symbols - 1, (0 if symbols == 1 else k - 1)
        def bounds(j: int) -> tuple[int, int]:
            return left, min(right, j - 1)
        def cost(j: int, i: int) -> F:
            work.cell_evaluations += 1
            previous = dp[i]
            if previous is None:
                raise AssertionError('Infeasible deterministic prefix')
            u = p.caps[i]
            w, wb, wb2, wg, wgb, wgb2 = moments.sums(i, j)
            return previous + p.r*wb-p.q*wb2/2-p.reward(u)*w+(wgb2-2*u*wgb+u*u*wg)/2
        rows = monotone_minima(symbols, k, left, right, bounds, cost, work)
        new: list[F | None] = [None] * (k + 1)
        for j, (value, i) in rows.items():
            new[j], back[symbols, j] = value, i
        at, levels = k, []
        for layer in range(symbols, 0, -1):
            at = back[layer, at]
            levels.append(p.caps[at])
        if new[k] is None:
            raise AssertionError('No full deterministic solution')
        answers.append(Solution(new[k], tuple(reversed(levels))))
        dp = new
    answers.extend([answers[-1]] * (max_symbols - len(answers)))
    return answers, work
