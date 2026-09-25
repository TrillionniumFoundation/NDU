"""Generate the frozen, fully synthetic matched-limit study and model hashes."""
from fractions import Fraction as F
from pathlib import Path
import json,random
from price_path import Model,spec_for,digest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def synthetic(k=48,n=25,m=4,eps='1/1000',charge='1/1000',seed=540927,hetero=False):
    rng=random.Random(seed)
    caps=[F(rng.randint(15,90),100) for _ in range(k)];raw=[rng.randint(1,7) for _ in caps]
    weights=[F(x,sum(raw)) for x in raw];gamma=[F(rng.randint(0,12),3) for _ in caps]
    ceilings=[min(F(1),b+F(rng.randint(0,30),100)) for b in caps]
    r=[F(2)+F(rng.randint(-4,4),10) for _ in caps] if hetero else 2
    d=Model.make(caps,weights,gamma,ceilings,r,1)
    a=tuple(F(i,n-1) for i in range(n));rho=tuple(F(charge)*rng.randint(0,5) for x in a)
    B=d.cap_total*F(7,10)
    return dict(spec=spec_for(d,a,rho,B,m),epsilon=eps,k=k,n=n,m=m,
                E=len({sum(x<=t for x in a) for t in ceilings}),distinct_caps=len(set(caps)),heterogeneous=hetero)

def generate():
    cases=[]
    for k in (12,48,192,768):cases.append(dict(id=f'histories-{k}',family='histories',**synthetic(k=k)))
    for n in (9,17,33,65):cases.append(dict(id=f'catalog-{n}',family='catalog',**synthetic(n=n)))
    for m in (2,4,8,12):cases.append(dict(id=f'budget-{m}',family='budget',**synthetic(m=m)))
    for eps in ('1/100','1/1000','1/10000','1/1000000'):
        cases.append(dict(id='accuracy-'+eps.replace('/','_'),family='accuracy',**synthetic(eps=eps)))
    for charge in ('0','1/1000','1/100','1/10'):
        cases.append(dict(id='charge-'+charge.replace('/','_'),family='charges',**synthetic(charge=charge)))
    for k,n in ((12,9),(12,17),(24,9),(24,17)):
        cases.append(dict(id=f'heterogeneous-k{k}-n{n}',family='heterogeneous',**synthetic(k=k,n=n,hetero=True)))
    old=json.loads((ROOT/'revisions/or-r49-dispersion-certificates-20260925/results/study.json').read_text())['cases']
    stress=[x for x in old if x['family']=='stress'];seeds=sorted({x['seed'] for x in stress})
    for seed in seeds:
        row=next(x for x in stress if x['seed']==seed);z=row['model']
        d=Model.make(z['caps'],z['weights'],z['gamma'],z['ceilings'],z.get('r','2'),z.get('curvature','1'))
        a=tuple(map(F,row['catalog']));spec=spec_for(d,a,tuple(map(F,row['charges'])),F(row['promise']),row['m'])
        cases.append(dict(id=f'historical-{seed}',family='historical',spec=spec,epsilon='1/1000',k=len(d.caps),n=len(a),m=row['m'],
                          E=len({sum(x<=t for x in a) for t in d.ceilings}),distinct_caps=len(set(d.caps)),heterogeneous=False))
    for c in cases:c['instance_sha256']=digest(c['spec'])
    out=HERE.parent/'results';out.mkdir(exist_ok=True)
    (out/'CASES.json').write_text(json.dumps(cases,indent=2)+'\n');return cases
if __name__=='__main__':print(len(generate()),'cases generated')
