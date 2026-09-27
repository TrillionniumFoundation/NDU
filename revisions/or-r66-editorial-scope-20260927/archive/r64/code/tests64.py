"""Semantic regression: internally valid intervals with false metadata.

Legacy checkers are run in a separate interpreter. The new checkers must reject
all adversaries even where the R63 checker accepts the mathematical interval.
No optimization routine is imported by any production checker.
"""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import argparse, itertools, json, random, subprocess, sys, time
from rational import F, encode, digest, write
from price_path import Model, spec_for, normalize, allocate
import tariff60
from robust61 import solve, simplify, error_budget
from check_tariff60 import verify as tariff_check
from check_robust61 import verify as robust_check
from check_projection64 import optimum
R=Path(__file__).resolve().parents[1]


def instance(fees):
    n=len(fees)
    mod=Model.make([0,F(1,3),F(2,3),1],[F(1,4)]*4,[0]*4,[0,F(1,3),F(2,3),1],1,0)
    return spec_for(mod,[F(i,n-1) for i in range(n)] if n>1 else [0],fees,F(2,5),min(4,n))


def conditional_tariff(spec, fee):
    original=tariff60.standard_fee
    try:
        tariff60.standard_fee=lambda charges: F(fee)
        return tariff60.solve(spec,max_exceptions=len(spec['catalog']))['certificate']
    finally:tariff60.standard_fee=original


def candidate(spec, epsilon, d, projection):
    surrogate=deepcopy(spec);surrogate['charges']=encode(projection['charges'])
    inner=tariff60.solve(surrogate,max_exceptions=len(spec['catalog']))['certificate']
    mod,a,fees,B,m=normalize(spec)
    policy=allocate(mod,tuple(map(F,inner['policy']['book'])),B,dict(zip(a,fees)))
    budget=error_budget(fees,projection['charges'],m)
    return encode(dict(schema='NDU-R61-robust-tariff-v1',spec=spec,instance_sha256=digest(spec),
        surrogate_certificate=inner,projection=projection,policy=policy,
        lower=policy['value'],upper=F(inner['upper'])+budget['negative_budget'],
        error_budget=budget,epsilon=F(epsilon),selected_exception_budget=d))


def run(output):
    begin=time.perf_counter();positive=exhaustive=0;adversaries=[]
    # Exhaustive retained subsets independently test optimal value and monotonicity.
    rng=random.Random(640927)
    for n in range(1,9):
        for rep in range(8):
            fees=[F(rng.randrange(12),100) for _ in range(n)]
            spec=instance(fees);last=None
            for d in range(n):
                proj=optimum(fees,d)
                costs=[]
                for kept in itertools.combinations(range(n),n-d):
                    values=sorted(fees[i] for i in kept);median=values[(len(values)-1)//2]
                    costs.append(sum((abs(fees[i]-median) for i in kept),F(0)))
                assert proj['absolute_deviation']==min(costs)
                assert last is None or last>=proj['absolute_deviation'];last=proj['absolute_deviation'];exhaustive+=1
                for eps in (last,last+F(1,1000)):
                    ans=solve(spec,eps,max_exceptions=n);receipt=robust_check(ans['certificate'],digest(spec));positive+=1
                    expected=next(t for t in range(n) if optimum(fees,t)['absolute_deviation']<=eps)
                    assert receipt['selected_exception_budget']==expected
                    assert receipt['tariff_exceptions']<=receipt['projected_exceptions']<=expected
    # Conditional tariff proofs are exact but violate the parameterization contract.
    spec=instance([F(1,100),F(1,100),F(1,100),F(2,100)])
    adversaries.append(('nonmodal-standard',conditional_tariff(spec,F(2,100))))
    spec=instance([F(1,100),F(2,100),F(1,100),F(2,100)])
    adversaries.append(('wrong-modal-tie',conditional_tariff(spec,F(2,100))))
    valid=tariff60.solve(spec)['certificate'];tariff_check(valid)
    # Fully coordinated surrogate proofs, not just stale hashes or invalid bounds.
    fees=[F(x,100) for x in (0,1,2,10,11)];spec=instance(fees);eps=F(1)
    wrong=simplify(fees,1);kept=[1,2,3,4];center=fees[2]
    wrong=dict(standard_fee=center,charges=[center if i in kept else x for i,x in enumerate(fees)],
        exceptions=[0],retained_window=kept,absolute_deviation=sum(abs(fees[i]-center) for i in kept))
    adversaries.append(('nonoptimal-retained-window',candidate(spec,eps,1,wrong)))
    wrong=simplify(fees,0);wrong['standard_fee']=F(0);wrong['charges']=[F(0)]*5;wrong['absolute_deviation']=sum(fees)
    adversaries.append(('incorrect-median',candidate(spec,eps,0,wrong)))
    adversaries.append(('nonminimal-selected-allowance',candidate(spec,eps,1,simplify(fees,1))))
    valid=solve(spec,eps,max_exceptions=5)['certificate']
    changes=[('false-distortion',('projection','absolute_deviation'),'999'),
             ('detached-projection-charges',('projection','charges'),['0']*5),
             ('false-projection-exceptions',('projection','exceptions'),[0]),
             ('invalid-budget-type',('selected_exception_budget',),True),
             ('out-of-range-budget',('selected_exception_budget',),5)]
    for name,path,value in changes:
        bad=deepcopy(valid);target=bad
        for key in path[:-1]:target=target[key]
        target[path[-1]]=value;adversaries.append((name,bad))
    # The minimum L1 budget is intentionally not the minimum interval-width budget.
    nonminimal=candidate(spec,F(1),1,simplify(fees,1))
    assert F(nonminimal['upper'])-F(nonminimal['lower'])<=F(nonminimal['epsilon'])
    output.mkdir(parents=True,exist_ok=True)
    write(output/'SEMANTIC_ADVERSARIES64.json',dict(adversaries=[dict(name=n,certificate=c) for n,c in adversaries]))
    old=R/'archive/r63/code'
    script="""import json,sys
sys.path.insert(0,sys.argv[1])
from check_tariff60 import verify as tariff
from check_robust61 import verify as robust
out=[]
for item in json.load(open(sys.argv[2]))['adversaries']:
 try:
  c=item['certificate'];r=(tariff if c['schema']=='NDU-R60-tariff-frontier-v1' else robust)(c)
  out.append({'name':item['name'],'status':r['status']})
 except Exception as e:out.append({'name':item['name'],'status':'REJECT','reason':str(e)})
print(json.dumps(out))
"""
    legacy=json.loads(subprocess.check_output([sys.executable,'-c',script,str(old),str(output/'SEMANTIC_ADVERSARIES64.json')],text=True,cwd='/tmp'))
    assert all(x['status']=='PASS' for x in legacy),legacy
    rejected=[]
    for name,cert in adversaries:
        check=tariff_check if cert['schema']=='NDU-R60-tariff-frontier-v1' else robust_check
        try:check(cert)
        except (ValueError,KeyError,AssertionError,ArithmeticError) as exc:rejected.append(dict(name=name,reason=str(exc)))
        else:raise AssertionError('Accepted adversary '+name)
    # Rational representations are semantic, not an arbitrary canonical-string requirement.
    alt=deepcopy(valid);p=alt['projection']
    for key in ('standard_fee','absolute_deviation'):p[key]=str(F(p[key]))
    p['charges']=[str(F(x)) for x in p['charges']]
    robust_check(alt);positive+=1
    # Production checker import closure must not include optimizer modules.
    closure="import sys;sys.path.insert(0,sys.argv[1]);import check_robust61;assert not {'tariff60','robust61','price_path'} & set(sys.modules)"
    subprocess.run([sys.executable,'-c',closure,str(R/'code')],check=True,cwd='/tmp')
    ans=dict(status='PASS',positive_robust_certificates=positive,exhaustive_projection_instances=exhaustive,
        legacy_accepts_false_metadata=len(legacy),new_semantic_rejections=len(rejected),rejections=rejected,
        optimizer_free_checker_imports=True,seconds=time.perf_counter()-begin,
        scope='Deterministic exact regression and witnessed semantic counterexamples; not a proof substitute.')
    write(output/'SEMANTIC_TESTS64.json',ans);return ans

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=R/'results/r64');a=p.parse_args();print(json.dumps(run(a.output),indent=2))
