"""Deterministic additional R58 regressions; not pooled with timed comparisons."""
import copy, random
from pathlib import Path
from itertools import combinations
from rational import F, encode, digest, write
from price_path import Model, spec_for, normalize, allocate
from enumeration import solve as enumerate_books
from check_enumeration import verify as check_enumeration
from check_price import check_policy
from check_deficit import verify as check_deficit
from saturation import frontier, certificate
R = Path(__file__).resolve().parents[1]


def best_through(spec, bound):
    d, a, rho, B, _ = normalize(spec)
    best = None
    for s in range(1, min(bound, len(a)) + 1):
        for book in combinations(a, s):
            if book[0] > min(B, min(d.caps)):
                continue
            policy = allocate(d, book, B, dict(zip(a, rho)))
            if best is None or policy['value'] > best['value']:
                best = policy
    return best


def main():
    out = R / 'results'
    out.mkdir(exist_ok=True)
    rows, saturated, corruptions = [], [], []
    for seed in range(24):
        rng = random.Random(5800 + seed)
        k, n = 4, 7
        a = tuple(F(i, n - 1) for i in range(n))
        caps = [F(1, 2), F(1, 2), F(3, 4), F(3, 4)]
        weights = [F(1, k)] * k
        gamma = [F(rng.randrange(1, 5), 4) for _ in range(k)]
        ceilings = [min(F(1), b + F(rng.randrange(3), 8)) for b in caps]
        pr, pq = [F(2), F(2), F(5, 2), F(5, 2)], [F(1, 2)] * k
        # Exactly common prototypes and genuinely heterogeneous original rewards.
        dispersion = F(0) if seed % 6 == 0 else F(1, 100)
        rr = [r + dispersion * rng.randrange(-4, 5) for r in pr]
        qq = [q + dispersion * rng.randrange(-2, 3) for q in pq]
        charges = [F(rng.randrange(4), 100) for _ in a]
        d = Model.make(caps, weights, gamma, ceilings, rr, qq)
        p = Model.make(caps, weights, gamma, ceilings, pr, pq)
        B = d.cap_total * F(1 + seed % 3, 3)
        original = spec_for(d, a, charges, B, n)
        prototype = spec_for(p, a, charges, B, n)
        original_ref = enumerate_books(original)
        prototype_ref = enumerate_books(prototype)
        check_enumeration(original_ref['certificate'], digest(original))
        check_enumeration(prototype_ref['certificate'], digest(prototype))
        small = best_through(prototype, 4)
        assert small['value'] == prototype_ref['lower']
        recovered = allocate(d, tuple(small['book']), B, dict(zip(a, charges)))
        check_policy(original, encode(recovered))
        oscillations = []
        for j in range(k):
            errors = [d.reward(j, x) - p.reward(j, x) for x in a]
            oscillations.append(max(errors) - min(errors))
        Delta = sum(w * z for w, z in zip(weights, oscillations))
        regret = original_ref['lower'] - recovered['value']
        assert 0 <= regret <= Delta and len(recovered['book']) <= 4
        if dispersion == 0:
            assert regret == 0
        # Catalog offsets leave oscillation unchanged, even when sup errors grow.
        for j in range(k):
            shift = F(j + seed, 7)
            shifted = [d.reward(j, x) - p.reward(j, x) + shift for x in a]
            assert max(shifted) - min(shifted) == oscillations[j]
        rows.append(dict(seed=5800 + seed, original=original, prototype=prototype,
                         original_optimum=original_ref['lower'], prototype_optimum=prototype_ref['lower'],
                         recovered=encode(recovered), oscillations=oscillations,
                         Delta=Delta, regret=regret, prototype_groups=2))
        full = dict(original, promise=encode(d.cap_total))
        f = frontier(full)
        last = None
        for budget in range(1, n + 1):
            spec = dict(full, budget=budget)
            cert = certificate(full, f, budget)
            check_deficit(cert, digest(spec))
            ref = enumerate_books(spec)
            check_enumeration(ref['certificate'], digest(spec))
            assert f['values'][budget - 1] == ref['lower']
            assert last is None or last <= ref['lower']
            last = ref['lower']
            saturated.append(dict(seed=5800 + seed, budget=budget, spec=spec,
                                  value=last, certificate=cert,
                                  enumerated_books=ref['books_evaluated']))
        # A different obligation cannot inherit the saturated theorem/certificate.
        try:
            frontier(dict(full, promise=encode(d.cap_total - F(1, 100))))
        except ValueError:
            corruptions.append('off_saturation_rejected')
        else:
            raise AssertionError('Accepted nonsaturated promise')
        bad = copy.deepcopy(certificate(full, f, 2))
        bad['upper'] = encode(F(bad['upper']) - 1)
        try:
            check_deficit(bad, digest(dict(full, budget=2)))
        except (ValueError, ArithmeticError):
            corruptions.append('frontier_bound_corruption_rejected')
        else:
            raise AssertionError('Accepted corrupt frontier bound')
    write(out / 'STRUCTURAL_R58.json', dict(status='PASS', approximate_type_models=len(rows),
        saturated_models=24, independently_checked_budget_certificates=len(saturated),
        rejected_corruptions=len(corruptions), type_records=rows, saturation_records=saturated,
        note='Deterministic theorem regressions, not timed performance claims; independent checkers import no optimizer.'))
    print('R58 PASS:', len(rows), 'approximate-type models;', len(saturated), 'exact budget certificates;', len(corruptions), 'rejections')

if __name__ == '__main__':
    main()
