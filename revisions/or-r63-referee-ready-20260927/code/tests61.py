"""Finite regression evidence, not a replacement for the mathematical proofs."""
from pathlib import Path
import argparse,itertools,json,random,sys
from copy import deepcopy
from rational import F,encode,digest,write
from price_path import Model,spec_for,normalize,allocate
from tariff60 import solve as exact,GuardExceeded,NotApplicable,standard_fee
from robust61 import simplify,error_budget,solve,frontier
from check_robust61 import verify
from check_tariff60 import verify as check_exact
from paths60 import bounded_recognize
R=Path(__file__).resolve().parents[1]

def books(spec):
    d,a,rho,B,m=normalize(spec)
    for s in range(1,m+1):
        for book in itertools.combinations(a,s):
            if book[0]<=min(B,min(d.caps)):yield allocate(d,book,B,dict(zip(a,rho)))

def run():
    rng=random.Random(61927);instances=comparisons=projections=mutations=0
    for n in range(3,9):
        for rep in range(6):
            k=4;caps=[F(0),F(1,3),F(2,3),F(1)];mod=Model.make(caps,[F(1,4)]*4,[0]*4,caps,1,0)
            fees=[F(rng.randrange(1,14),500) for _ in range(n)]
            a=[F(i,n-1) for i in range(n)];spec=spec_for(mod,a,fees,F(2,5),min(4,n));allbooks=list(books(spec));opt=max(p['value'] for p in allbooks)
            for limit in range(n):
                projection=simplify(fees,limit)
                # Exhaust over every retained subset, independently checking trimmed median.
                costs=[]
                for kept in itertools.combinations(range(n),n-limit):
                    vals=sorted(fees[i] for i in kept);center=vals[(len(vals)-1)//2]
                    costs.append(sum(abs(fees[i]-center) for i in kept))
                assert projection['absolute_deviation']==min(costs);projections+=1
                eps=projection['absolute_deviation'];ans=solve(spec,eps,max_exceptions=n)
                result=verify(ans['certificate'],digest(spec));assert F(result['lower'])<=opt<=F(result['upper']) and opt-ans['lower']<=eps
                instances+=1
                budget=error_budget(fees,projection['charges'],min(4,n))
                for p in allbooks:
                    ids=[a.index(x) for x in p['book']];err=sum((budget['error'][i] for i in ids),F(0))
                    assert -budget['negative_budget']<=err<=budget['positive_budget'];comparisons+=1
                if limit==0:
                    for mode in range(3):
                        broken=deepcopy(ans['certificate'])
                        if mode==0:broken['upper']=str(F(broken['upper'])-1)
                        elif mode==1:broken['surrogate_certificate']['spec']['promise']='0'
                        else:broken['error_budget']['negative_budget']='100'
                        try:verify(broken,digest(spec))
                        except (ValueError,KeyError,ArithmeticError,AssertionError):mutations+=1
                        else:raise AssertionError('Corrupt robustness certificate accepted')
    # Twelve-exception test independently compared with all small-cardinality books.
    from study61 import physical,perturb
    spec=perturb(physical(17,8,3),12);ans=exact(spec);check_exact(ans['certificate']);brute=list(books(spec));assert max(p['value'] for p in brute)==ans['lower']
    comparisons+=len(brute)
    try:exact(perturb(physical(17,8,3),13),max_exceptions=12)
    except GuardExceeded:pass
    else:raise AssertionError('Missing engineering guard')
    # Modal ties: both decompositions have the same exhaustive global optimum.
    assert standard_fee([F(1,20),F(1,10),F(1,20),F(1,10)])==F(1,20)
    graph=([0,1,2],[(0,2,F(2)),(0,1,F(1)),(1,2,F(2))],[0],2)
    assert bounded_recognize(*graph,1)['accepted']
    huge=bounded_recognize(*graph,10**100)
    assert not huge['accepted'] and huge['effective_h']==2
    assert max(len(p)-1 for p in huge['witness'])<=2
    # Degenerate source=sink and zero allowance remain meaningful after truncation.
    assert bounded_recognize([0],[],[0],0,10**100)['source_capacity']=={0:F(0)}
    assert bounded_recognize([0],[],[0],0,0)['effective_h']==0
    # Exact envelope and original lotteries of the worked service-credit case.
    cap=[F(0),F(1,3),F(2,3),F(1)];mod=Model.make(cap,[F(1,4)]*4,[0]*4,cap,1,0)
    worked=spec_for(mod,cap,[F(1,30)]*4,F(2,5),4);envelope=frontier(worked)
    assert [F(x['fee']) for x in envelope['switches']]==[F(1,15),F(1,3)]
    assert [x['size'] for x in envelope['segments']]==[3,2,1]
    decision=[]
    for name,spec in [('worked',worked)]+[(f'physical-{n}',physical(n,k,m)) for n,k,m in [(17,12,8),(65,32,16),(129,48,32)]]:
        env=frontier(spec);check_exact(env['capacity_certificate']);samples=[]
        for seg in env['segments']:
            left=F(seg['left']);right=None if seg['right'] is None else F(seg['right']);fee=left+1 if right is None else (left+right)/2
            d,a,rho,B,m=normalize(spec);policy=allocate(d,tuple(map(F,seg['book'])),B,{v:fee for v in a})
            samples.append(dict(fee=fee,policy=policy))
        decision.append(dict(name=name,spec=spec,envelope=env,samples=samples))
    p=deepcopy(worked);p['charges']=[str(F(1,30)+F(z,6000)) for z in (1,-2,3,-1)]
    rob=solve(p,F(1,1000));verify(rob['certificate']);decision.append(dict(name='near_standard_worked',spec=p,robust=rob))
    write(R/'results/DECISION_FRONTIERS.json',decision)
    return dict(status='PASS',robust_certified_instances=instances,exhaustive_fee_projections=projections,book_error_comparisons=comparisons,
        rejected_corrupt_certificates=mutations,max_exact_exception_count=12,guard_checked_at=13,
        largest_declared_h=str(10**100),effective_h=2,fee_switches=['1/15','1/3'],complete_frontiers=4,
        scope='Finite exact regression tests, not a proof of theorem novelty or general correctness')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default=str(R/'results/STRUCTURAL61.json'));a=p.parse_args()
    ans=run();write(Path(a.output),ans);print(json.dumps(ans),flush=True)
