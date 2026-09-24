"""Seeded exact disjunctive checks of every cardinality and boundary cases."""
from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import random, time, json, sys
from compression import Instance, frontier, ideal_targets, jensen_certificate, repair_targets, policy, encode
from independent import exhaustive_fixed, verify_policy
R=Path(__file__).resolve().parents[1]


def run():
    started=time.perf_counter(); rows=[]; repairs=0; rate_checks=0
    seeds=[104729,130363,155921,181081,205019,230003]
    for seed in seeds:
        rng=random.Random(seed)
        for z in range(24):
            k=1+z%5; den=4+z%4; a=tuple(F(i,den) for i in range(den+1))
            caps=tuple(F(rng.randint(2,15),16) for _ in range(k))
            w=[rng.randint(1,9) for _ in caps]; pi=tuple(F(x,sum(w)) for x in w)
            gamma=tuple(F(rng.randint(0,15),4) for _ in caps)
            tau=tuple(b+(F(0),F(1,8),F(1))[rng.randrange(3)] for b in caps)
            data=Instance.make(caps,pi,gamma,tau,r=2,curvature=1)
            charges=tuple(F(0) if z%3==0 else F(rng.randint(0,18),100) for _ in a)
            t=tuple(F(rng.randint(0,16),16)*b for b in caps)
            m=1+z%3; B=sum(w*x for w,x in zip(pi,t))
            got=frontier(data,a,charges,t,m); ref=exhaustive_fixed(data,a,charges,t,m)
            for p,q in zip(got['exact'],ref['exact']):
                assert (p is None and q is None) or p['value']==q['value']
            for q,(p,other) in enumerate(zip(got['at_most'],ref['at_most']),1):
                assert p['value']==other['value']; verify_policy(data,a,charges,p,B,q)
            jt=jensen_certificate(data,a,charges,B,m)
            for q,p in enumerate(jt['at_most'],1): verify_policy(data,a,charges,p,B,q)
            candidate=tuple(min(b,max(F(0),x+F(rng.randint(-2,2),64))) for b,x in zip(caps,t))
            fixed,clipping,residual=repair_targets(data,candidate,0,B)
            assert clipping==0
            base=policy(data,(a[0],),candidate,dict(zip(a,charges)))
            repaired=policy(data,(a[0],),fixed,dict(zip(a,charges)))
            L=max(data.r,max(g*b for g,b in zip(gamma,caps)))
            assert repaired['value']>=base['value']-L*residual
            verify_policy(data,a,charges,repaired,B,1); repairs+=1
            rows.append(dict(seed=seed,id=z,k=k,N=len(a),budget=m,promise=str(B),
                             conditional_values=[str(p['value']) for p in got['at_most']],
                             direct_support_match=True))
    # Zero and saturated promises, repeated caps, nonzero anchor, ceiling ties,
    # flat intermediate costs and all cardinalities including unused levels.
    boundary=[]
    for lower in [F(0),F(1,8)]:
        a=tuple(lower+i*(1-lower)/4 for i in range(5))
        data=Instance.make([F(1,4),F(1,4),F(3,4)],[F(1,3)]*3,[0,1,2],[F(1,4),F(1,4),F(7,8)])
        for B in [lower,data.cap_total]:
            t=ideal_targets(data,B)
            ans=frontier(data,a,[F(1,10)]*5,t,5)
            ref=exhaustive_fixed(data,a,[F(1,10)]*5,t,5)
            assert [p['value'] for p in ans['at_most']]==[p['value'] for p in ref['at_most']]
            boundary.append(dict(lower=str(lower),B=str(B)))
    # Quantitative original-budget rates with arbitrary ceilings and safe gaps.
    for den in [1,2,4,8,16]:
        a=tuple(F(i,den) for i in range(den+1)); h=F(1,den)
        for delta in [F(0),h,F(1)]:
            data=Instance.make([F(1,5),F(7,10),F(9,10)],[F(1,3)]*3,[1,2,3],
                               [F(1,5)+delta,F(7,10)+delta,F(9,10)+delta])
            ans=jensen_certificate(data,a,[0]*len(a),F(7,10)*data.cap_total,len(a))
            gap=ans['same_budget_gaps'][-1]
            assert gap<=data.r*h+sum(w*g*h*h/2 for w,g in zip(data.weights,data.gamma))
            if delta>=h: assert gap<=data.curvature*h*h/8
            rate_checks+=1
    # A genuinely charged book: replay mutations of the original constraints.
    data=Instance.make([F(1,3),F(5,6)],[F(1,2)]*2,[1,3],[F(1,3),F(5,6)])
    a=tuple(F(i,6) for i in range(7)); rho=tuple(F(i,1000) for i in range(7)); B=F(1,2)
    good=frontier(data,a,rho,ideal_targets(data,B),3)['at_most'][-1]
    rejections=[]
    def reject(name,mutator):
        bad=deepcopy(encode(good)); mutator(bad)
        try: verify_policy(data,a,rho,bad,B,3)
        except (ValueError,KeyError,TypeError,IndexError): rejections.append(name)
        else: raise AssertionError('Accepted mutation: '+name)
    reject('payoff',lambda p:p.__setitem__('value','999'))
    reject('charge',lambda p:p.__setitem__('charge','999'))
    reject('promise',lambda p:p['targets'].__setitem__(0,'1'))
    reject('pre_draw_service',lambda p:p['intermediate'].__setitem__(0,'1'))
    reject('probability_normalization',lambda p:p['lotteries'][0][0].__setitem__(1,'2'))
    reject('negative_probability',lambda p:p['lotteries'][0][0].__setitem__(1,'-1'))
    reject('uninstalled_support',lambda p:p['lotteries'][0][0].__setitem__(0,'1/101'))
    reject('duplicate_level',lambda p:p['book'].append(p['book'][0]))
    reject('missing_level',lambda p:p['book'].clear())
    reject('dimension',lambda p:p['targets'].pop())
    invalid=0
    for kw in [dict(budget=0),dict(charges=[-1]*7),dict(targets=[F(2),F(1)]),
               dict(catalog=[0,0]),dict(targets=[0.1,0.2])]:
        args=dict(instance=data,catalog=a,charges=rho,targets=ideal_targets(data,B),budget=3);args.update(kw)
        try: frontier(**args)
        except (ValueError,TypeError): invalid+=1
        else: raise AssertionError('Invalid input accepted.')
    out=dict(status='PASS',seeds=seeds,exact_instances=len(rows),cardinality_comparisons=sum(r['budget'] for r in rows),
             repair_checks=repairs,uniform_rate_checks=rate_checks,boundary_cases=boundary,
             corruption_rejections=rejections,invalid_rejections=invalid,rows=rows,
             seconds=time.perf_counter()-started)
    (R/'results').mkdir(exist_ok=True)
    (R/'results/tests.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
    return out

if __name__=='__main__': run()
