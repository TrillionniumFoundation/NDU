"""Exact global randomized renewal-memory frontiers (R34).

Only the standard library is needed. All numerical inputs must be int, str,
or Fraction, not float. The institution checks participation before the
private symbol draw. A separate deterministic DP gives the pathwise frontier.
"""
from __future__ import annotations
from bisect import bisect_left
from dataclasses import dataclass
from fractions import Fraction as F
from typing import Sequence

Scalar = int | str | F


def rational(x: Scalar) -> F:
    if isinstance(x, bool) or not isinstance(x, (int, str, F)):
        raise TypeError('Use int, rational str, or Fraction; floats are rejected.')
    return F(x)


@dataclass(frozen=True)
class Problem:
    caps: tuple[F, ...]
    probabilities: tuple[F, ...]
    gamma: tuple[F, ...]
    r: F = F(2)
    q: F = F(1)

    @classmethod
    def make(cls, caps: Sequence[Scalar], probabilities: Sequence[Scalar],
             gamma: Sequence[Scalar], r: Scalar = 2, q: Scalar = 1) -> Problem:
        return cls(tuple(map(rational, caps)), tuple(map(rational, probabilities)),
                   tuple(map(rational, gamma)), rational(r), rational(q))

    def __post_init__(self) -> None:
        # Validate direct construction too; do not silently accept float fields.
        if any(not isinstance(x, F) for x in (*self.caps, *self.probabilities,
                                               *self.gamma, self.r, self.q)):
            raise TypeError('Use Problem.make or Fraction-valued fields.')
        k = len(self.caps)
        if not k or len(self.probabilities) != k or len(self.gamma) != k:
            raise ValueError('Nonempty input arrays must have equal length.')
        if any(not 0 < b < 1 for b in self.caps):
            raise ValueError('Caps must be strictly between zero and one.')
        if any(a >= b for a, b in zip(self.caps, self.caps[1:])):
            raise ValueError('Caps must be strictly increasing.')
        if any(p <= 0 for p in self.probabilities) or sum(self.probabilities) != 1:
            raise ValueError('Probabilities must be positive and sum exactly to one.')
        if any(g < 0 for g in self.gamma) or not self.r >= self.q > 0:
            raise ValueError('Require gamma >= 0 and r >= q > 0.')

    def reward(self, c: F) -> F:
        return self.r * c - self.q * c * c / 2


@dataclass(frozen=True)
class Solution:
    loss: F
    codebook: tuple[F, ...]


class Moments:
    """Prefix/suffix sufficient statistics; each edge/tail query is O(1)."""
    def __init__(self, p: Problem):
        self.p = p
        self.k = len(p.caps)
        self.prefix = [[F(0)] for _ in range(6)]
        for b, w, g in zip(p.caps, p.probabilities, p.gamma):
            for row, value in zip(self.prefix,
                                  (w, w*b, w*b*b, w*g, w*g*b, w*g*b*b)):
                row.append(row[-1] + value)

    def sums(self, first: int, end: int) -> tuple[F, ...]:
        return tuple(row[end] - row[first] for row in self.prefix)

    def edge(self, i: int, j: int) -> F:
        """Weighted chord loss on caps between anchored levels b_i,b_j."""
        u, v = self.p.caps[i], self.p.caps[j]
        w, wb, wb2, *_ = self.sums(i, j+1)
        return self.p.q / 2 * ((u+v)*wb - wb2 - u*v*w)

    def tail_polynomial(self, i: int, ell: int) -> tuple[F, F, F]:
        """Psi(z)=A*z^2+B*z+C for last level z in [b_ell,b_{ell+1}]."""
        p, u = self.p, self.p.caps[i]
        w, wb, wb2, *_ = self.sums(i+1, ell+1)
        t, tb, tb2, tg, tgb, tgb2 = self.sums(ell+1, self.k)
        A = (p.q*t + tg) / 2
        B = p.q/2*(wb-u*w) - p.r*t - tgb
        C = -p.q/2*(wb2-u*wb) + p.r*tb-p.q/2*tb2+tgb2/2
        return A, B, C

    def tail(self, i: int) -> tuple[F, F, int]:
        """Best final continuous level after anchored b_i, plus its cell."""
        best = None
        for ell in range(i, self.k):
            lo = self.p.caps[ell]
            hi = self.p.caps[min(ell+1, self.k-1)]
            A, B, C = self.tail_polynomial(i, ell)
            if A:
                z = max(lo, min(hi, -B/(2*A)))
            else:
                z = lo if B >= 0 else hi
            item = (A*z*z+B*z+C, z, ell)
            if best is None or item < best:
                best = item
        assert best is not None
        return best


def _budget(m: int) -> int:
    if isinstance(m, bool) or not isinstance(m, int) or m < 1:
        raise ValueError('The alphabet budget must be a positive integer.')
    return m


def codebook_loss(p: Problem, levels: Sequence[Scalar]) -> F:
    """Independent direct branchwise adjacent-lottery objective, no moments."""
    c = tuple(sorted(set(map(rational, levels))))
    if not c or c[0] < 0 or c[-1] > 1 or c[0] > p.caps[0]:
        raise ValueError('Infeasible codebook.')
    total = F(0)
    for b, w, g in zip(p.caps, p.probabilities, p.gamma):
        mu = min(b, c[-1])
        j = bisect_left(c, mu)
        if c[j] == mu:
            fhat = p.reward(mu)
        else:
            u, v = c[j-1], c[j]
            t = (mu-u)/(v-u)
            fhat = (1-t)*p.reward(u)+t*p.reward(v)
        total += w*(p.reward(b)-fhat+g*(b-mu)**2/2)
    return total


def randomized_frontiers(p: Problem, max_symbols: int) -> list[Solution]:
    """Solve all budgets 1..max_symbols in O(min(m,k)*k^2) rational work.

    Prefix DP keeps only cap-anchored codewords; one optimized continuous top
    level is added using the tail oracle. Memory is O(min(m,k)*k+k) scalars
    including reconstruction data. No codeword grid or tolerance is used.
    """
    _budget(max_symbols)
    k = len(p.caps)
    limit = min(max_symbols, k)
    base = Solution(codebook_loss(p, (p.caps[0],)), (p.caps[0],))
    answers = [base]
    if limit == 1:
        return answers * max_symbols
    moments = Moments(p)
    tails = [moments.tail(j) for j in range(k)]
    # dp[j] covers branches up to b_j with exactly s cap-anchored levels.
    dp: list[F | None] = [None]*k
    dp[0] = F(0)
    predecessors: dict[tuple[int, int], int] = {}
    for s in range(1, limit):
        best = answers[-1]
        for j in range(k):
            if dp[j] is None:
                continue
            loss = dp[j] + tails[j][0]
            if loss < best.loss:
                indices = [j]
                at = j
                for layer in range(s, 1, -1):
                    at = predecessors[layer, at]
                    indices.append(at)
                levels = tuple(p.caps[t] for t in reversed(indices))
                levels = tuple(sorted(set((*levels, tails[j][1]))))
                best = Solution(loss, levels)
        answers.append(best)
        new: list[F | None] = [None]*k
        if s+1 < limit:
            for j in range(s, k):
                choices = [(dp[i]+moments.edge(i, j), i)
                           for i in range(j) if dp[i] is not None]
                if choices:
                    value, i = min(choices)
                    new[j] = value
                    predecessors[s+1, j] = i
            dp = new
    while len(answers) < max_symbols:
        answers.append(answers[-1])
    return answers


def deterministic_frontiers(p: Problem, max_symbols: int) -> list[Solution]:
    """Ordered-cell frontier; also optimum under private-draw pathwise caps."""
    _budget(max_symbols)
    k, mm = len(p.caps), Moments(p)
    limit = min(max_symbols, k)
    def cell(i: int, j: int) -> F:
        u = p.caps[i]
        w, wb, wb2, wg, wgb, wgb2 = mm.sums(i, j)
        return p.r*wb-p.q*wb2/2-p.reward(u)*w+(wgb2-2*u*wgb+u*u*wg)/2
    dp: list[F | None] = [None]*(k+1)
    dp[0] = F(0)
    back: dict[tuple[int, int], int] = {}
    ans: list[Solution] = []
    for s in range(1, limit+1):
        new: list[F | None] = [None]*(k+1)
        for j in range(s, k+1):
            choices = [(dp[i]+cell(i, j), i) for i in range(s-1, j)
                       if dp[i] is not None]
            if choices:
                new[j], back[s, j] = min(choices)
        at, levels = k, []
        for layer in range(s, 0, -1):
            at = back[layer, at]
            levels.append(p.caps[at])
        assert new[k] is not None
        ans.append(Solution(new[k], tuple(reversed(levels))))
        dp = new
    return ans + [ans[-1]]*(max_symbols-len(ans))


def audit(p: Problem, solution: Solution, symbols: int) -> dict:
    """Replay an expected-participation controller using exact rational sums."""
    c = solution.codebook
    assert 1 <= len(c) <= symbols and tuple(sorted(set(c))) == c
    assert 0 <= c[0] <= p.caps[0] and c[-1] <= 1
    branches, weighted_payment, expected_reward = [], F(0), F(0)
    for b, pi, gamma in zip(p.caps, p.probabilities, p.gamma):
        mu = min(b, c[-1]); y = b-mu
        j = bisect_left(c, mu)
        if c[j] == mu:
            lottery = [(j, F(1))]
        else:
            t = (mu-c[j-1])/(c[j]-c[j-1])
            lottery = [(j-1, 1-t), (j, t)]
        assert sum(w for _, w in lottery) == 1
        assert all(w > 0 for _, w in lottery)
        mean = sum(w*c[i] for i, w in lottery)
        assert mean+y == b and 0 <= y <= 1
        weighted_payment += pi*(mean+y)
        expected_reward += pi*(sum(w*p.reward(c[i]) for i,w in lottery)-gamma*y*y/2)
        branches.append({'cap':str(b), 'intermediate':str(y),
                         'lottery': [[i,str(w)] for i,w in lottery],
                         'expected_cap_residual':'0',
                         'pathwise_cap_satisfied':all(y+c[i] <= b for i,_ in lottery)})
    full = sum(pi*p.reward(b) for pi,b in zip(p.probabilities,p.caps))
    assert weighted_payment == sum(pi*b for pi,b in zip(p.probabilities,p.caps))
    assert full-expected_reward == solution.loss == codebook_loss(p,c)
    return {'loss':str(solution.loss),'codebook':list(map(str,c)),
            'root_payment':str(weighted_payment),'branches':branches,
            'exact_replay':'PASS'}
