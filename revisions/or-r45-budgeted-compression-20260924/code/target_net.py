"""Same-budget additive scheme on a finite catalog with fixed branch count.

The algorithm enumerates weighted target nets, not codebook subsets. The
requested guarantee is returned only after the entire net is processed.
Charges, root promise and realization limits are never relaxed.
"""
from fractions import Fraction as F
from itertools import product
from compression import rat, frontier, repair_targets


def solve(instance, catalog, charges, promise, budget, epsilon, max_profiles=None):
    a=tuple(map(rat,catalog)); rho=tuple(map(rat,charges)); B=rat(promise); eps=rat(epsilon)
    if eps<=0: raise ValueError('Positive additive accuracy required.')
    # Also validates the model/catalog/budget, including feasible anchor existence.
    from compression import ideal_targets
    frontier(instance,a,rho,ideal_targets(instance,B),budget)
    k=len(instance.caps); last=max(range(k),key=lambda j:instance.weights[j])
    others=[j for j in range(k) if j!=last]
    L=max(instance.r,max(instance.gamma))
    eta=eps/(2*L*max(1,k-1))
    best=None; evaluated=0; feasible_anchors=0; candidates=0
    for i,low in enumerate(a):
        if low>min(B,min(instance.caps)): break
        feasible_anchors+=1
        capacity=[p*(b-low) for p,b in zip(instance.weights,instance.caps)]
        available=B-low
        ranges=[range(int(capacity[j]//eta)+1) for j in others]
        for indices in product(*ranges):
            candidates+=1
            masses=[F(0)]*k
            for j,n in zip(others,indices): masses[j]=n*eta
            if sum(masses)>available: continue
            masses[last]=min(capacity[last],available-sum(masses))
            t=tuple(low+x/p for x,p in zip(masses,instance.weights))
            t,_,_=repair_targets(instance,t,low,B)
            if max_profiles is not None and evaluated>=max_profiles:
                return dict(status='INTERRUPTED',policy=best,evaluated_profiles=evaluated,
                    epsilon_guarantee=None,requested_epsilon=eps,
                    scope='feasible incumbent only; net coverage incomplete')
            ans=frontier(instance,a[i:],rho[i:],t,budget)['at_most'][-1]
            evaluated+=1
            if best is None or ans['value']>best['value']: best=ans
    assert best is not None
    return dict(status='COMPLETE',policy=best,evaluated_profiles=evaluated,
                cartesian_candidates=candidates,anchors=feasible_anchors,
                epsilon_guarantee=eps,weighted_mass_step=eta,L=L,
                scope='global additive guarantee at the original catalog symbol budget')
