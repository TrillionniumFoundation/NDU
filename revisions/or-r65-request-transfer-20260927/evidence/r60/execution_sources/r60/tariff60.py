"""Exact tariff-exception algorithm for the ORIGINAL linear/free-service model.

The parameter is the number of catalog commands whose opening charge differs
from a declared standard fee. No resource grid or denominator enumeration is
used. A certificate includes all exception subsets and capacity Bellman rows.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'revisions/or-r58-structural-referee-20260926/code'))
from rational import F, encode, digest
from price_path import normalize, allocate

class NotApplicable(ValueError):
    pass


def standard_fee(charges):
    counts = Counter(charges)
    return min(counts, key=lambda x: (-counts[x], x))


def solve(spec, max_exceptions=12):
    d, a, fees, B, m = normalize(spec)
    if any(d.gamma) or any(d.reward_q) or len(set(d.reward_r)) != 1:
        raise NotApplicable('Common linear reward and zero service cost required')
    fee = standard_fee(fees)
    exceptions = [i for i, x in enumerate(fees) if x != fee]
    if len(exceptions) > max_exceptions:
        raise NotApplicable('Declared tariff-exception enumeration guard exceeded')
    n = len(a)
    edge = {}
    for u in range(n):
        for v in range(u+1, n):
            edge[u, v] = sum((w*(min(b,a[v])-min(b,a[u]))
                for w,b,t in zip(d.weights,d.caps,d.ceilings) if t >= a[v]), F(0))
    best = None
    bestbook = None
    branches = []
    operations = 0
    for mask in range(1 << len(exceptions)):
        required = {i for bit,i in enumerate(exceptions) if mask & (1 << bit)}
        banned = set(exceptions)-required
        allowed = [i for i in range(n) if i not in banned]
        counts = [sum(j < i for j in required) for i in range(n+1)]
        earliest = min(required, default=n)
        latest = max(required, default=-1)
        rows = [[None]*n for _ in range(m)]
        prev = {}
        for v in allowed:
            if v <= earliest and a[v] <= min(B, min(d.caps)):
                rows[0][v] = a[v]
        for s in range(1,m):
            for v in allowed:
                for u in allowed:
                    if u >= v or rows[s-1][u] is None or counts[v] != counts[u+1]:
                        continue
                    operations += 1
                    z = rows[s-1][u] + edge[u,v]
                    if rows[s][v] is None or z > rows[s][v]:
                        rows[s][v] = z
                        prev[s,v] = u
        branch_best = None
        for s in range(1,m+1):
            charge = (s-len(required))*fee+sum((fees[i] for i in required),F(0))
            for v in allowed:
                cap = rows[s-1][v]
                if v < latest or cap is None:
                    continue
                value = d.reward_r[0]*min(B,cap)-charge
                if branch_best is None or value > branch_best:
                    branch_best = value
                if best is None or value > best:
                    best = value
                    path = [v]
                    level, at = s-1, v
                    while level:
                        at = prev[level,at]
                        path.append(at)
                        level -= 1
                    bestbook = tuple(a[i] for i in reversed(path))
        branches.append(dict(mask=mask, rows=rows, upper=branch_best))
    if bestbook is None:
        raise ArithmeticError('Feasible input has no terminal Bellman state')
    policy = allocate(d, bestbook, B, dict(zip(a, fees)))
    if policy['value'] != best:
        raise ArithmeticError('Original allocation and tariff recurrence disagree')
    certificate = encode(dict(schema='NDU-R60-tariff-frontier-v1', spec=spec,
        instance_sha256=digest(spec), standard_fee=fee, exceptions=exceptions,
        branches=branches, policy=policy, lower=best, upper=best))
    return dict(status='EXACT', lower=best, upper=best, exceptions=len(exceptions),
        branches=len(branches), comparisons=operations, certificate=certificate)
