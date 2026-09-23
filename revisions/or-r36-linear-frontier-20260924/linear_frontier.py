"""Linear-oracle-work exact renewal frontiers using classical SMAWK.

The economic reduction, rational moment oracle, and reconstruction convention
are inherited from R34/R35. This module changes only matrix search. The new
proof obligation is total monotonicity of the completed staircase, including
all-invalid submatrices and finite ties. No floating infinity or cache of
quadratically many matrix entries is used. Python standard library only.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
from typing import Callable, Sequence
import importlib.util
import sys

_PATH = Path(__file__).resolve().parents[1] / 'or-r35-monge-frontier-20260923' / 'monge_frontier.py'
_NAME = '_ndu_r35_linear_comparator'
if _NAME not in sys.modules:
    spec = importlib.util.spec_from_file_location(_NAME, _PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot load the inherited exact model: {_PATH}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[_NAME] = module
    spec.loader.exec_module(module)
previous = sys.modules[_NAME]
old = previous.old
Problem, Solution, Moments = old.Problem, old.Solution, old.Moments
Key = tuple[int, F, int]


@dataclass
class Work:
    """Instrument actual queries; these are not CPU instructions or bit counts."""
    tail_evaluations: int = 0
    edge_evaluations: int = 0
    cell_evaluations: int = 0
    key_requests: int = 0
    padded_requests: int = 0
    comparisons: int = 0
    searches: int = 0
    peak_recursion_depth: int = 0


def smawk_minima(rows: Sequence[int], columns: Sequence[int],
                  key: Callable[[int, int], Key], work: Work | None = None
                  ) -> dict[int, int]:
    """Return row argmins of an implicitly totally monotone ordered matrix.

    Precondition: if c<d and key(r,d)<key(r,c), then this strict preference
    persists in every later row. The keys used here break every tie. The
    routine does not test this mathematical precondition quadratically.
    Input row and column indices must be strictly increasing; empty row sets
    are allowed, but a nonempty row set requires at least one column.
    """
    work = work if work is not None else Work()
    rows, columns = list(rows), list(columns)
    if any(a >= b for a, b in zip(rows, rows[1:])) or any(a >= b for a, b in zip(columns, columns[1:])):
        raise ValueError('Rows and columns must be strictly increasing.')
    if rows and not columns:
        raise ValueError('A nonempty matrix needs a column.')
    answer: dict[int, int] = {}
    work.searches += 1

    def better(row: int, a: int, b: int) -> bool:
        work.comparisons += 1
        work.key_requests += 2
        return key(row, a) < key(row, b)

    def solve(rr: list[int], cc: list[int], depth: int) -> None:
        if not rr:
            return
        work.peak_recursion_depth = max(work.peak_recursion_depth, depth)
        reduced: list[int] = []
        for col in cc:
            while reduced and better(rr[len(reduced)-1], col, reduced[-1]):
                reduced.pop()
            if len(reduced) < len(rr):
                reduced.append(col)
        solve(rr[1::2], reduced, depth+1)
        # Positions are built once per level, never searched with list.index.
        position = {col: j for j, col in enumerate(reduced)}
        for at in range(0, len(rr), 2):
            row = rr[at]
            first = 0 if at == 0 else position[answer[rr[at-1]]]
            last = len(reduced)-1 if at+1 == len(rr) else position[answer[rr[at+1]]]
            winner = reduced[first]
            for j in range(first+1, last+1):
                if better(row, reduced[j], winner):
                    winner = reduced[j]
            answer[row] = winner
    solve(rows, columns, 1)
    return answer


def staircase_key(row: int, col: int, bounds: Callable[[int], tuple[int, int]],
                   cost: Callable[[int, int], F], work: Work) -> Key:
    """Finite ties go left. Left padding goes RIGHT; right padding goes left.

    Used only for the one-sided nested domains proved in the paper. This is
    an ordinal completion, not a claim that a numerical infinity matrix is
    Monge. A padded entry never calls the economic cost oracle.
    """
    lo, hi = bounds(row)
    if col < lo:
        work.padded_requests += 1
        return 1, F(0), -col
    if col > hi:
        work.padded_requests += 1
        return 1, F(0), col
    return 0, cost(row, col), col


def staircase_minima(rows: Sequence[int], columns: Sequence[int],
                      bounds: Callable[[int], tuple[int, int]],
                      cost: Callable[[int, int], F], work: Work
                      ) -> dict[int, tuple[F, int]]:
    winners = smawk_minima(rows, columns,
                          lambda i, j: staircase_key(i, j, bounds, cost, work), work)
    answer = {}
    for row, col in winners.items():
        lo, hi = bounds(row)
        if not lo <= col <= hi:
            raise RuntimeError('No feasible row minimum; check the staircase precondition.')
        answer[row] = cost(row, col), col
    return answer


def terminal_minima(p: Problem, work: Work | None = None) -> tuple[list[tuple[F, F, int]], Work]:
    work = work if work is not None else Work()
    oracle, k = previous.Oracle(p, work), len(p.caps)
    found = staircase_minima(range(k), range(k), lambda i: (i, k-1),
                             lambda i, ell: oracle.interval(i, ell)[0], work)
    result = []
    for i in range(k):
        value, ell = found[i]
        check, z = oracle.interval(i, ell)
        if value != check:
            raise AssertionError('The exact interval oracle changed its value.')
        result.append((value, z, ell))
    return result, work


def randomized_frontiers(p: Problem, max_symbols: int) -> tuple[list[Solution], Work]:
    """All globally optimal expected-participation budgets in O(m*k) work.

    For 1<=m<=k, storage is O(m*k+k) including all backpointers and codebooks.
    The output is a codebook per budget, not a secretly retained random seed.
    Larger budgets append zero-loss references after the k-symbol optimum.
    """
    old._budget(max_symbols)
    k, limit, work = len(p.caps), min(max_symbols, len(p.caps)), Work()
    base = Solution(old.codebook_loss(p, (p.caps[0],)), (p.caps[0],))
    answers = [base]
    if limit == 1:
        return answers * max_symbols, work
    tails, _ = terminal_minima(p, work)
    oracle = previous.Oracle(p, work)
    dp: list[F | None] = [None]*k
    dp[0] = F(0)
    back: dict[tuple[int, int], int] = {}
    for anchors in range(1, limit):
        incumbent, best_j = answers[-1], None
        best_loss = incumbent.loss
        for j in range(k):
            if dp[j] is not None:
                value = dp[j] + tails[j][0]
                if value < best_loss:
                    best_loss, best_j = value, j
        if best_j is not None:
            indices, at = [best_j], best_j
            for layer in range(anchors, 1, -1):
                at = back[layer, at]
                indices.append(at)
            levels = tuple(p.caps[t] for t in reversed(indices))
            top = tails[best_j][1]
            if top > levels[-1]:
                levels += (top,)
            incumbent = Solution(best_loss, levels)
        answers.append(incumbent)
        if anchors+1 >= limit:
            break
        left, right = anchors-1, (0 if anchors == 1 else k-2)
        def bounds(j: int) -> tuple[int, int]:
            return left, min(j-1, right)
        def cost(j: int, i: int) -> F:
            value = dp[i]
            if value is None:
                raise AssertionError('An infeasible predecessor was evaluated.')
            return value + oracle.edge(i, j)
        found = staircase_minima(range(anchors, k), range(left, right+1), bounds, cost, work)
        new: list[F | None] = [None]*k
        for j, (value, i) in found.items():
            new[j], back[anchors+1, j] = value, i
        dp = new
    answers.extend([answers[-1]]*(max_symbols-len(answers)))
    return answers, work


def deterministic_frontiers(p: Problem, max_symbols: int) -> tuple[list[Solution], Work]:
    """All deterministic/pathwise-participation budgets in O(m*k) work."""
    old._budget(max_symbols)
    k, limit, work = len(p.caps), min(max_symbols, len(p.caps)), Work()
    moments = Moments(p)
    dp: list[F | None] = [None]*(k+1)
    dp[0] = F(0)
    back: dict[tuple[int, int], int] = {}
    answers = []
    for symbols in range(1, limit+1):
        left, right = symbols-1, (0 if symbols == 1 else k-1)
        def bounds(j: int) -> tuple[int, int]:
            return left, min(right, j-1)
        def cost(j: int, i: int) -> F:
            work.cell_evaluations += 1
            value = dp[i]
            if value is None:
                raise AssertionError('An infeasible deterministic prefix was evaluated.')
            u = p.caps[i]
            w, wb, wb2, wg, wgb, wgb2 = moments.sums(i, j)
            return value + p.r*wb-p.q*wb2/2-p.reward(u)*w+(wgb2-2*u*wgb+u*u*wg)/2
        found = staircase_minima(range(symbols, k+1), range(left, right+1), bounds, cost, work)
        new: list[F | None] = [None]*(k+1)
        for j, (value, i) in found.items():
            new[j], back[symbols, j] = value, i
        at, levels = k, []
        for layer in range(symbols, 0, -1):
            at = back[layer, at]
            levels.append(p.caps[at])
        if new[k] is None:
            raise AssertionError('No feasible deterministic frontier.')
        answers.append(Solution(new[k], tuple(reversed(levels))))
        dp = new
    answers.extend([answers[-1]]*(max_symbols-len(answers)))
    return answers, work
