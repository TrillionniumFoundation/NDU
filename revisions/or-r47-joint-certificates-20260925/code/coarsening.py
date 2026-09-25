"""Certified response coarsening without changing the original contract.

The optimistic reduced model is an upper relaxation, not a replacement for
participation constraints. An exact, group-mass-preserving lift returns an
original-space feasible policy. All numerical quantities are rational.
"""
from __future__ import annotations
from bisect import bisect_right
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path
import sys, time
R46 = Path(__file__).resolve().parents[2] / 'or-r46-box-decomposition-20260925' / 'code'
sys.path.insert(0, str(R46))
from box_solver import Instance, rat, policy, solve as box_solve, fixed_allocate, encode
sys.path.insert(0, str(Path(__file__).resolve().parent))


def bin_partition(data: Instance, catalog, cap_width, cost_width):
    """Keep eligibility exact, bin caps/costs, isolate one minimum-cap guard."""
    beta, eta = rat(cap_width), rat(cost_width)
    if beta <= 0 or eta <= 0:
        raise ValueError('Strictly positive bin widths required')
    a = tuple(map(rat, catalog))
    guard = min(range(len(data.caps)), key=lambda j: (data.caps[j], j))
    buckets = {}
    for j, (b, g, tau) in enumerate(zip(data.caps, data.gamma, data.ceilings)):
        if j == guard:
            continue
        key = (bisect_right(a, tau), b // beta, g // eta)
        buckets.setdefault(key, []).append(j)
    return ((guard,),) + tuple(tuple(buckets[key]) for key in sorted(buckets))


def reduced_model(data: Instance, catalog, groups):
    """Weighted caps/minimum quadratic costs with a preserved feasible anchor."""
    a = tuple(map(rat, catalog))
    groups = tuple(tuple(g) for g in groups)
    flat = [j for g in groups for j in g]
    if any(not g for g in groups) or any(type(j) is not int for j in flat) or sorted(flat) != list(range(len(data.caps))):
        raise ValueError('Groups must partition original branch indices')
    if not a or any(x >= y for x, y in zip(a, a[1:])):
        raise ValueError('Strict nonempty catalog required')
    if a[0] > min(data.caps):
        raise ValueError('No original feasible anchor')
    weights, caps, gamma, ceilings, bounds = [], [], [], [], []
    for group in groups:
        prefixes = {bisect_right(a, data.ceilings[j]) for j in group}
        if len(prefixes) != 1:
            raise ValueError('Coarsening may not mix eligibility prefixes')
        w = sum(data.weights[j] for j in group)
        cap = sum(data.weights[j] * data.caps[j] for j in group) / w
        cost = min(data.gamma[j] for j in group)
        ceiling = max(data.ceilings[j] for j in group)
        lipschitz = max(data.r, cost * max(data.caps[j] for j in group))
        cap_defect = 2 * lipschitz * sum(data.weights[j] * max(F(0), cap-data.caps[j]) for j in group)
        cost_defect = sum(data.weights[j] * (data.gamma[j]-cost) * (data.caps[j]-a[0])**2 / 2 for j in group)
        weights.append(w); caps.append(cap); gamma.append(cost); ceilings.append(ceiling)
        bounds.append(dict(weight=w, cap=cap, gamma=cost, ceiling=ceiling,
                           lipschitz=lipschitz, cap_defect=cap_defect,
                           cost_defect=cost_defect, defect=cap_defect+cost_defect))
    small = Instance.make(caps, weights, gamma, ceilings, data.r, data.curvature)
    if min(small.caps) != min(data.caps):
        raise ValueError('Minimum-cap anchor guard is missing')
    assert small.cap_total == data.cap_total
    return small, groups, tuple(bounds)


def lift(data: Instance, small: Instance, groups, reduced_policy, catalog, charges):
    """Clip at each ORIGINAL cap, then fill deficits inside the same group."""
    book = tuple(map(rat, reduced_policy['book']))
    means = tuple(map(rat, reduced_policy['targets']))
    target = [None] * len(data.caps)
    for g, mean, w in zip(groups, means, small.weights):
        for j in g:
            target[j] = min(mean, data.caps[j])
        residual = w * mean - sum(data.weights[j] * target[j] for j in g)
        for j in g:
            amount = min(residual, data.weights[j]*(data.caps[j]-target[j]))
            target[j] += amount / data.weights[j]
            residual -= amount
        if residual != 0:
            raise AssertionError('Insufficient group capacity')
    ans = policy(data, book, tuple(target), dict(zip(catalog, charges)))
    distance, defect = F(0), F(0)
    for z, group in enumerate(groups):
        mean = means[z]
        dist = sum(data.weights[j] * abs(target[j]-mean) for j in group)
        clipped = 2 * sum(data.weights[j]*max(F(0), mean-data.caps[j]) for j in group)
        assert dist == clipped
        L = max(data.r, small.gamma[z]*max(data.caps[j] for j in group))
        defect += L*dist + sum(data.weights[j]*(data.gamma[j]-small.gamma[z])*ans['intermediate'][j]**2/2 for j in group)
        distance += dist
    assert ans['promise'] == rat(reduced_policy['promise'])
    assert rat(reduced_policy['value']) - ans['value'] <= defect
    return ans, distance, defect


def solve(data: Instance, catalog, charges, B, budget, groups, epsilon=F(1,1000),
          inner_epsilon=None, max_nodes=301, seconds_limit=None, price_steps=8,
          improve_original=False):
    """Return an original-space global interval; no accuracy on interruption.

    A coarse partition can be used even if its a priori defect is large:
    the measured upper-minus-feasible-lower interval is authoritative.
    """
    started = time.perf_counter()
    a, rho, B, eps = tuple(map(rat,catalog)), tuple(map(rat,charges)), rat(B), rat(epsilon)
    if eps <= 0:
        raise ValueError('Positive original-space tolerance required')
    small, groups, bounds = reduced_model(data, a, groups)
    inner_eps = eps/2 if inner_epsilon is None else rat(inner_epsilon)
    if inner_eps < 0:
        raise ValueError('Nonnegative inner tolerance required')
    certificate = box_solve(small,a,rho,B,budget,inner_eps,max_nodes=max_nodes,
        seconds_limit=seconds_limit,price_steps=price_steps,aggregate_types=False,record_tables=True)
    before = time.perf_counter()
    lifted, distance, posterior = lift(data,small,groups,certificate['policy'],a,rho)
    incumbent = lifted
    if improve_original:
        better = fixed_allocate(data,lifted['book'],B,dict(zip(a,rho)))
        assert better['value'] >= lifted['value']
        incumbent = better
    lift_seconds = time.perf_counter()-before
    upper, lower = certificate['upper_bound'], incumbent['value']
    gap = upper-lower
    delta = sum(z['defect'] for z in bounds)
    assert gap >= 0 and gap <= certificate['gap']+delta
    return dict(schema='ndu-r47-coarsening-certificate-v1', original_model=asdict(data),
        reduced_model=asdict(small), groups=groups, group_bounds=bounds,
        catalog=a, charges=rho, promise=B, budget=min(budget,len(a)),
        requested_epsilon=eps, inner_certificate=certificate, lifted_policy=lifted,
        policy=incumbent, lower_bound=lower, upper_bound=upper, gap=gap,
        uniform_defect=delta, posterior_defect=posterior, weighted_lift_distance=distance,
        status='COMPLETE' if gap <= eps else 'UNRESOLVED',
        epsilon_guarantee=eps if gap <= eps else None,
        original_branches=len(data.caps), groups_count=len(groups),
        original_exact_types=len(set(zip(data.caps,data.gamma,(bisect_right(a,t) for t in data.ceilings)))),
        lift_seconds=lift_seconds, seconds=time.perf_counter()-started,
        scope='Original finite-catalog joint problem; no change to caps, ceilings, promise, charges or budget')


def accuracy_partition(data, catalog, epsilon):
    """The theorem's conservative variable-history additive scheme partition."""
    eps=rat(epsilon)
    if eps <= 0:
        raise ValueError('Positive tolerance required')
    L=max(data.r,max(data.gamma))
    return bin_partition(data,catalog,eps/(2*L),eps/2)


def certified_scheme(data, catalog, charges, B, budget, epsilon):
    """Completed variable-history additive scheme, without a resource cutoff.

    This theorem implementation can be very expensive. Experimental callers
    should instead use solve(), which honestly returns unresolved intervals.
    The depth bound is deliberately conservative and uses no floating logs.
    """
    eps=rat(epsilon)
    groups=accuracy_partition(data,catalog,eps)
    q=len(groups); L=max(data.r,max(data.gamma))
    ratio=4*L*max(0,q-1)/eps
    depth=0
    while ratio>1:
        ratio/=2; depth+=1
    nodes=(1<<((q-1)*depth+1))-1
    out=solve(data,catalog,charges,B,budget,groups,eps,inner_epsilon=eps/2,
              max_nodes=nodes,seconds_limit=None)
    assert out['uniform_defect'] <= eps/2 and out['gap'] <= eps
    out['algorithm']='Completed accuracy-binned scheme'
    out['theoretical_node_limit']=nodes
    return out


def refine_partition(data, catalog, groups):
    """Split a positive-defect group; return None when exact aggregation suffices."""
    _,G,bounds=reduced_model(data,catalog,groups)
    candidates=[z for z,g in enumerate(G) if len(g)>1 and bounds[z]['defect']>0]
    if not candidates:return None
    z=max(candidates,key=lambda z:(bounds[z]['defect'],-z))
    # Theorem requires refinement, not this heuristic choice of coordinate.
    caps=bounds[z]['cap_defect'];cost=bounds[z]['cost_defect']
    key=(lambda j:(data.caps[j],data.gamma[j],j)) if caps>=cost else (lambda j:(data.gamma[j],data.caps[j],j))
    ordered=sorted(G[z],key=key);mid=len(ordered)//2
    return G[:z]+(tuple(ordered[:mid]),tuple(ordered[mid:]))+G[z+1:]
