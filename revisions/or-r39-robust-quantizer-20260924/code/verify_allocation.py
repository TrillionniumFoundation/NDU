"""Exact, independent event-search validation of the nonsaturated allocation."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
import random, json, time
from catalog import Model, solve as saturated_solve
from allocation import (solve_allocation, response, branch_maximum, certify,
                        solve_catalog_promise)
R = Path(__file__).resolve().parents[1]


def independent(model, book, B):
    """Scan dual events and interpolate between them, not primal water filling."""
    events = {F(0)}
    events.update((model.reward(v)-model.reward(u))/(v-u)
                  for u, v in zip(book, book[1:]))
    events.update(-g*(b-book[-1]) for b, g in zip(model.caps, model.gamma) if b > book[-1])
    events.update((max(events)+1, min(events)-1))
    old = None
    for lam in sorted(events, reverse=True):
        ranges = [branch_maximum(model, j, book, lam) for j in range(len(model.caps))]
        low = sum(p*x[1] for p, x in zip(model.probabilities, ranges))
        high = sum(p*x[2] for p, x in zip(model.probabilities, ranges))
        if low <= B <= high:
            t = [x[1] for x in ranges]
            rest = B-low
            for j, p in enumerate(model.probabilities):
                take = min(rest, p*(ranges[j][2]-ranges[j][1]))
                t[j] += take/p
                rest -= take
            return certify(model, book, B, tuple(t), lam)
        if old is not None and old[1] < B < low:
            prev, mass = old
            at = prev+(lam-prev)*(B-mass)/(low-mass)
            t = tuple(branch_maximum(model, j, book, at)[1] for j in range(len(model.caps)))
            return certify(model, book, B, t, at)
        old = lam, high
    raise AssertionError('No supporting price found.')


def verify():
    started = time.perf_counter()
    rng = random.Random(390924)
    counts = dict(allocation_dual_equalities=0, supporting_branch_maxima=0,
                  saturated_catalog_equalities=0, all_promise_catalog_checks=0,
                  pairwise_policy_transport_checks=0, invalid_inputs_rejected=0)
    cases = []
    for _ in range(96):
        k = rng.randint(1, 7)
        b = tuple(sorted(F(rng.randint(2, 15), 16) for _ in range(k)))
        weights = [rng.randint(1, 9) for _ in b]
        p = tuple(F(w, sum(weights)) for w in weights)
        g = tuple(F(rng.randint(0, 9), rng.randint(1, 5)) for _ in b)
        model = Model.make(b, p, g, r=F(5, 2), q=F(3, 2))
        lowest = F(rng.randint(0, int(b[0]*16)), 16)
        pool = [F(x, 16) for x in range(int(lowest*16)+1, 17)]
        book = (lowest, *sorted(rng.sample(pool, min(rng.randint(0, 4), len(pool)))))
        bar = sum(x*y for x, y in zip(b, p))
        promises = {lowest+(bar-lowest)*F(i, 16) for i in range(17)}
        # Include exactly all chord-boundary masses and all tail breakpoints.
        promises.update(sum(pj*min(bj, c) for pj, bj in zip(p, b)) for c in book)
        for B in sorted(promises):
            a, e = solve_allocation(model, book, B), independent(model, book, B)
            assert a.value == e.value == a.dual_bound
            counts['allocation_dual_equalities'] += 1
            counts['supporting_branch_maxima'] += k
        cases.append((model, book))

    # Independently enumerate all books at saturation and compare the existing DP.
    for case, (model, _) in enumerate(cases[:24]):
        a = (F(0), F(1, 8), F(1, 4), F(1, 2), F(3, 4), F(1))
        price = tuple(F((i+case)%4, 127) for i in range(len(a)))
        bar = sum(p*b for p, b in zip(model.probabilities, model.caps))
        for budget in (1, 2, 3):
            z = solve_catalog_promise(model, a, price, budget, bar)
            dp = saturated_solve(model, a, price, budget, delta=1)[-1]
            full = sum(p*model.reward(b) for p, b in zip(model.probabilities, model.caps))
            assert z['net_value'] == full-dp.total
            counts['saturated_catalog_equalities'] += 1
        # At nonsaturation each compared book carries an exact supporting bound.
        for B in (bar/3, 2*bar/3):
            winner = solve_catalog_promise(model, a, price, 2, B)
            rivals = []
            for n in (1, 2):
                for ids in combinations(range(len(a)), n):
                    book = tuple(a[i] for i in ids)
                    if book[0] <= min(B, model.caps[0]):
                        x = independent(model, book, B)
                        rivals.append(x.value-sum(price[i] for i in ids))
            assert winner['net_value'] == max(rivals)
            counts['all_promise_catalog_checks'] += 1

    # Arbitrary-promise contractions and partial lifts for E, P, and D policies.
    # P policies mix symbols with symbol-conditioned pre-decoder Y; D is one draw.
    for inst in ('expected', 'pathwise', 'deterministic'):
        for _ in range(80):
            model = cases[rng.randrange(len(cases))][0]
            b, p, g = model.caps, model.probabilities, model.gamma
            c = (min(b)/3, 2*min(b)/3)
            rows = []
            for bj in b:
                w = F(rng.randint(0, 8), 8) if inst != 'deterministic' else F(1)
                draws = (1-w, w)
                if inst == 'expected':
                    mean = sum(x*z for x, z in zip(draws, c))
                    y = (bj-mean)*F(rng.randint(0, 8), 8)
                    yy = (y, y)
                else:
                    yy = tuple((bj-z)*F(rng.randint(0, 8), 8) for z in c)
                rows.append((draws, yy))
            B1 = sum(pj*sum(w*(y+z) for w, y, z in zip(draws, yy, c))
                     for pj, (draws, yy) in zip(p, rows))
            bar = sum(pj*bj for pj, bj in zip(p, b))
            theta = F(rng.randint(0, 8), 8)
            B2 = B1+theta*(bar-B1)
            value1 = sum(pj*sum(w*(model.reward(z)-gj*y*y/2)
                         for w, y, z in zip(draws, yy, c))
                         for pj, gj, (draws, yy) in zip(p, g, rows))
            lifted = []
            for bj, (draws, yy) in zip(b, rows):
                mean = sum(w*z for w, z in zip(draws, c))
                lifted.append(tuple(y+theta*(bj-(mean if inst == 'expected' else z)-y)
                                    for y, z in zip(yy, c)))
            mass = sum(pj*sum(w*(y+z) for w, y, z in zip(draws, yy, c))
                       for pj, (draws, _), yy in zip(p, rows, lifted))
            value2 = sum(pj*sum(w*(model.reward(z)-gj*y*y/2) for w, y, z in zip(draws, yy, c))
                         for pj, gj, (draws, _), yy in zip(p, g, rows, lifted))
            assert mass == B2 and value1-value2 <= max(gj*bj for gj,bj in zip(g,b))*(B2-B1)
            alpha = F(0) if B2 == 0 else B1/B2
            contracted = sum(pj*sum(w*(model.reward(alpha*z)-gj*(alpha*y)**2/2)
                             for w, y, z in zip(draws, yy, c))
                             for pj, gj, (draws, _), yy in zip(p, g, rows, lifted))
            assert value2-contracted <= model.r*(B2-B1)
            for bj, (draws, _), yy in zip(b, rows, lifted):
                if inst == 'expected':
                    assert sum(w*(y+z) for w, y, z in zip(draws, yy, c)) <= bj
                else:
                    assert all(y+z <= bj for y, z in zip(yy, c))
            counts['pairwise_policy_transport_checks'] += 2

    model = Model.make(['1/4','1/2','3/4'], ['1/3']*3, ['1/4','1/2','3/4'])
    for book, B in [((), 0), ((F(1, 2),), F(1, 2)), ((0, 0),0),
                    ((-1,0),0), ((0,2),0), ((0,),1), ((0,),-1), ((0.0,),0)]:
        try:
            solve_allocation(model, book, B)
        except (ValueError, TypeError):
            counts['invalid_inputs_rejected'] += 1
        else:
            raise AssertionError('Invalid input accepted.')
    example = []
    for B in (F(1,4), F(11,24), F(23,48), F(1,2)):
        a = solve_allocation(model, (F(1,4), F(3,4)), B)
        example.append(dict(B=str(B),value=str(a.value),targets=list(map(str,a.targets)),
                            multiplier=str(a.multiplier),dual_gap=str(a.dual_bound-a.value)))
    out = dict(status='PASS', seed=390924, counts=counts, fixed_book_example=example,
               elapsed_seconds=time.perf_counter()-started,
               scope='Exact certificate and independent event-search regression; no proof by enumeration.')
    (R/'results').mkdir(exist_ok=True)
    (R/'results/allocation_validation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__ == '__main__':
    verify()
