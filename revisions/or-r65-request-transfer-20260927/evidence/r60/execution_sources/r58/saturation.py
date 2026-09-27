"""One-pass exact all-budget frontier at B = weighted cap total."""
from rational import F, encode, digest, qstr
from price_path import normalize, allocate


def frontier(spec):
    d, a, rho, B, _ = normalize(spec)
    if B != d.cap_total:
        raise ValueError('The exact saturated frontier requires promise = cap total')
    n = len(a)
    edge = {}
    for i, u in enumerate(a):
        for j in list(range(i + 1, n)) + [n]:
            v = a[j] if j < n else None
            value = F(0)
            for h, (b, w, gam, tau) in enumerate(zip(d.caps, d.weights, d.gamma, d.ceilings)):
                if v is not None and tau >= v:
                    value += w * (d.reward_r[h] - d.reward_q[h] * (u + v) / 2) * max(F(0), min(b, v) - u)
                if tau >= u and (v is None or tau < v):
                    value -= w * gam * max(F(0), b - u) ** 2 / 2
            edge[i, j] = value
    states = [[None] * n for _ in a]
    previous = {}
    for i, u in enumerate(a):
        if u <= min(d.caps):
            states[0][i] = d.mean_reward(u) - rho[i]
    for ell in range(1, n):
        for v in range(n):
            for u in range(v):
                if states[ell - 1][u] is None:
                    continue
                value = states[ell - 1][u] + edge[u, v] - rho[v]
                if states[ell][v] is None or value > states[ell][v]:
                    states[ell][v] = value
                    previous[ell, v] = u
    values, books = [], []
    best, endpoint = None, None
    for ell in range(n):
        for i in range(n):
            if states[ell][i] is not None:
                value = states[ell][i] + edge[i, n]
                if best is None or value > best:
                    best, endpoint = value, (ell, i)
        level, i = endpoint
        ids = [i]
        while level:
            i = previous[level, i]
            ids.append(i)
            level -= 1
        values.append(best)
        books.append(list(reversed(ids)))
    return dict(values=values, books=books, states=states, edge_count=len(edge))


def certificate(spec, result, budget):
    """Export a budget slice; check_deficit verifies it independently."""
    spec = dict(spec, budget=budget)
    d, a, rho, B, m = normalize(spec)
    if budget != m or B != d.cap_total:
        raise ValueError('Invalid saturated certificate request')
    ids = result['books'][m - 1]
    p = allocate(d, tuple(a[i] for i in ids), B, dict(zip(a, rho)))
    value = result['values'][m - 1]
    if p['value'] != value:
        raise ArithmeticError('Frontier path and original policy disagree')
    center = (max(d.reward_r) - max(d.gamma)) / 2
    return dict(schema='NDU-deficit-v1-hex', spec=spec, instance_sha256=digest(spec),
                mode='additive', epsilon=qstr(F(0)), eta=qstr(F(1)), center=qstr(center),
                error=qstr(F(0)), D=None, states=encode([[[v] for v in row] for row in result['states'][:m]]),
                best=qstr(value), book_indices=ids, rounded_deficits=encode([F(0)] * len(ids)),
                repaired_deficits=encode([F(0)] * len(ids)), policy=encode(p),
                lower=qstr(value), upper=qstr(value))
