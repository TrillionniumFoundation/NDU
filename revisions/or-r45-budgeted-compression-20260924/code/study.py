"""Comparative study: six seeds, three cap families, free/charged interfaces.

All instances and every budget value are retained. Runtime repeats are not
statistical replications of a real population. External MILP is a different
uneliminated formulation and is labelled numerical, not an exact certificate.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
from dataclasses import asdict
import sys, random, json, time, platform, statistics
from compression import Instance, frontier, ideal_targets, jensen_certificate, policy, encode
from independent import direct_milp, verify_policy
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]
sys.path.insert(0,str(R.parent/'or-r44-resource-augmentation-20260924'/'code'))
from augmentation import Model, recover
from unified import solve_allocation


def joint_policy(model,data,book,B,delta,cmap):
    ans=solve_allocation(model,book,B,delta)
    return policy(data,tuple(book),ans.targets,cmap)


def exhaustive_joint(model,data,a,rho,B,delta,Q):
    exact=[]; cmap=dict(zip(a,rho))
    for q in range(1,Q+1):
        best=None
        for book in combinations(a,q):
            if book[0]>min(B,min(data.caps)): continue
            p=joint_policy(model,data,book,B,delta,cmap)
            if best is None or p['value']>best['value']: best=p
        exact.append(best)
    return [max((p for p in exact[:q] if p is not None),key=lambda p:p['value']) for q in range(1,Q+1)]


def greedy_add(model,data,a,rho,B,delta,Q):
    cmap=dict(zip(a,rho)); options=[joint_policy(model,data,(x,),B,delta,cmap)
        for x in a if x<=min(B,min(data.caps))]
    best=max(options,key=lambda p:p['value']); out=[best]
    for q in range(2,Q+1):
        options=[best]+[joint_policy(model,data,tuple(sorted(set(best['book'])|{x})),B,delta,cmap)
            for x in a if x not in best['book']]
        best=max(options,key=lambda p:p['value']); out.append(best)
    return out


def prune(model,data,book,B,delta,cmap,q):
    best=joint_policy(model,data,book,B,delta,cmap)
    while len(best['book'])>q:
        options=[]
        for x in best['book']:
            d=tuple(z for z in best['book'] if z!=x)
            if d and d[0]<=min(B,min(data.caps)):
                options.append(joint_policy(model,data,d,B,delta,cmap))
        best=max(options,key=lambda p:p['value'])
    return best


def run():
    seeds=[104729,130363,155921,181081,205019,230003]; rows=[]; independent=[]
    for si,seed in enumerate(seeds):
        rng=random.Random(seed)
        for z in range(6):
            family=z%3; k=3+si%2; den=6+2*(si%2); m=2+si%2
            a=tuple(F(i,den) for i in range(den+1))
            if family==0: b=sorted(F(rng.randint(3,28),32) for _ in range(k))
            elif family==1: b=sorted(F(rng.choice([5,6,7,24,25,26]),32) for _ in range(k))
            else: b=sorted(F(rng.choice([1,2,3]),4) for _ in range(k))
            weights=[rng.randint(1,8) for _ in b]; p=tuple(F(x,sum(weights)) for x in weights)
            g=tuple(F(rng.randint(0,12),4) for _ in b)
            delta=(F(0),F(1,8),F(1))[family]
            rho=tuple(F(0) if z<3 else F(rng.randint(0,25),200) for _ in a)
            data=Instance.make(b,p,g,[x+delta for x in b]); model=Model.make(b,p,g)
            B=(F(2,5),F(4,5),F(1))[family]*data.cap_total
            start=time.perf_counter(); r44=recover(model,a,rho,m,B,delta,F(1,10**6)); r44secs=time.perf_counter()-start
            Q=min(2*m,len(a)); cmap=dict(zip(a,rho))
            profiles=[ideal_targets(data,B),r44['augmented_policy']['targets'],r44['original_policy']['targets']]
            times=[]
            for repeat in range(3):
                start=time.perf_counter(); fronts=[frontier(data,a,rho,t,Q) for t in profiles]
                times.append(time.perf_counter()-start)
            chosen=[]; polish_iterations=[]
            for q in range(1,Q+1):
                best=max((ans['at_most'][q-1] for ans in fronts),key=lambda p:p['value'])
                # Monotone two-block improvement; no global convergence claim.
                it=0
                while it<12:
                    allocated=joint_policy(model,data,best['book'],B,delta,cmap)
                    nxt=frontier(data,a,rho,allocated['targets'],q)['at_most'][-1]
                    assert nxt['value']>=allocated['value']>=best['value']
                    if nxt['value']==best['value']: break
                    best=nxt; it+=1
                chosen.append(best); polish_iterations.append(it)
                verify_policy(data,a,rho,best,B,q)
            ex=exhaustive_joint(model,data,a,rho,B,delta,Q)
            greedy=greedy_add(model,data,a,rho,B,delta,Q)
            recommended=[max((x,y),key=lambda p:p['value']) for x,y in zip(chosen,greedy)]
            U=min(r44['original_upper'],jensen_certificate(data,a,rho,B,m)['jensen_upper'])
            original=chosen[m-1]; union=r44['augmented_policy']; actual=len(union['book'])
            compressed=frontier(data,union['book'],[cmap[x] for x in union['book']],union['targets'],actual)
            down=prune(model,data,union['book'],B,delta,cmap,m)
            assert original['value']>=r44['original_lower']
            for q,ans in enumerate(chosen,1): assert ans['value']<=ex[q-1]['value']
            row=dict(seed=seed,family=['spread','clustered','repeated'][family],charged=z>=3,
                model=asdict(data),catalog=a,charges=rho,B=B,m=m,Q=Q,
                profiles=profiles,frontier=chosen,exact_joint_frontier=ex,greedy_frontier=greedy,
                recommended_frontier=recommended,
                recommended_same_budget_gap=ex[m-1]['value']-recommended[m-1]['value'],
                union_pruned=down,conditional_union_frontier=compressed['at_most'],r44=r44,
                exact_same_budget_gap=ex[m-1]['value']-original['value'],
                certified_same_budget_gap=U-original['value'],upper=U,
                gain_over_r44_incumbent=original['value']-r44['original_lower'],
                gap_vs_greedy=original['value']-greedy[m-1]['value'],
                union_size=actual,extra_levels=actual-m,
                actual_extra_levels=max(0,actual-m),overlap=len(set(r44['left']['policy']['book'])&set(r44['right']['policy']['book'])),
                nested=(set(r44['left']['policy']['book'])<=set(r44['right']['policy']['book']) or set(r44['right']['policy']['book'])<=set(r44['left']['policy']['book'])),
                union_gap_at_actual_budget=ex[actual-1]['value']-union['value'],
                new_gap_at_union_budget=ex[actual-1]['value']-chosen[actual-1]['value'],
                r44_seconds=r44secs,compression_seconds=times,polish_iterations=polish_iterations)
            rows.append(row)
            # Twelve independent full-model comparisons, both original and
            # enlarged budgets when they differ, and both quadratic envelopes.
            if z in (si%3,3+si%3):
                for q in sorted({m,min(Q,max(m+1,actual))}):
                    tangent=direct_milp(data,a,rho,B,q,segments=32,envelope='tangent')
                    secant=direct_milp(data,a,rho,B,q,segments=32,envelope='secant')
                    exact=float(ex[q-1]['value'])
                    for result in [tangent,secant]:
                        assert result['status']==0,result
                        assert result['max_model_residual']<1e-6,result
                    assert tangent['numerical_upper']+1e-7>=exact
                    assert secant['objective']<=exact+1e-7
                    assert secant['value']<=exact+1e-6
                    assert tangent['numerical_upper']-secant['objective']<=2*tangent['approximation_error']+2e-6
                    independent.append(dict(seed=seed,family=row['family'],charged=z>=3,budget=q,exact=ex[q-1]['value'],tangent=tangent,secant=secant))
            print('comparison',len(rows),seed,family,z>=3,'gap',float(row['exact_same_budget_gap']),flush=True)
    groups=[]
    for charged in [False,True]:
        subset=[x for x in rows if x['charged']==charged]
        groups.append(dict(charged=charged,n=len(subset),
            zero_exact_gap=sum(x['exact_same_budget_gap']==0 for x in subset),
            safeguarded_zero_exact_gap=sum(x['recommended_same_budget_gap']==0 for x in subset),
            median_exact_gap=statistics.median(float(x['exact_same_budget_gap']) for x in subset),
            max_exact_gap=max(float(x['exact_same_budget_gap']) for x in subset),
            median_certified_gap=statistics.median(float(x['certified_same_budget_gap']) for x in subset),
            max_certified_gap=max(float(x['certified_same_budget_gap']) for x in subset),
            improved_incumbents=sum(x['gain_over_r44_incumbent']>0 for x in subset),
            greedy_wins=sum(x['gap_vs_greedy']<0 for x in subset),
            new_wins=sum(x['gap_vs_greedy']>0 for x in subset),
            max_gain_over_incumbent=max(float(x['gain_over_r44_incumbent']) for x in subset),
            union_max_size=max(x['union_size'] for x in subset),
            nested_count=sum(x['nested'] for x in subset)))
    output=dict(status='PASS',seeds=seeds,instances=len(rows),rows=rows,groups=groups,
                independent_formulations=len(independent),independent=independent,
                independent_scope='direct original constraints; numerical MIP brackets compared to exact exhaustive catalog values',
                platform=platform.platform(),python=sys.version)
    (R/'results/comparison.json').write_text(json.dumps(encode(output),indent=2)+'\n')
    print(json.dumps(encode(groups),indent=2));print('direct model comparisons',len(independent))
    return output

if __name__=='__main__': run()
