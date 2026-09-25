"""Exact SUBSET SUM reduction checks and predeclared structural challenges."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json,random,subprocess,os,sys,time
from price_path import Model,spec_for,allocate,digest
R=Path(__file__).resolve().parents[1];OUT=R/'results'

def reduction(weights,target):
    n=len(weights);A=sum(weights);K=n*n*A
    if n<2 or any(w<=0 for w in weights) or not 1<=target<=A:raise ValueError('Nontrivial positive SUBSET SUM instance required')
    low=tuple(F(i,n) for i in range(n));high=tuple(u+F(w,n*A) for u,w in zip(low,weights))
    d=Model.make(high,[F(1,n)]*n,[0]*n,high,1,0)
    a=tuple(sorted(low+high));rho=tuple(F(0) if x in low else F(weights[high.index(x)],2*K) for x in a)
    D0=sum(low)/n;B=D0+F(target,K);zeta=D0+F(target,2*K)
    return spec_for(d,a,rho,B,2*n),low,high,K,zeta

def exact_subset_value(weights,target,K,zeta):
    reachable={0}
    for w in weights:reachable|={x+w for x in tuple(reachable)}
    distance=min(abs(x-target) for x in reachable)
    return zeta-F(distance,2*K),distance,len(reachable)

def regress():
    start=time.perf_counter();rng=random.Random(541000);rows=[];subsets=books=0
    for case in range(60):
        n=rng.randint(2,6);weights=[rng.randint(1,9) for _ in range(n)];target=rng.randint(1,sum(weights))
        spec,low,high,K,zeta=reduction(weights,target)
        d=Model.make(**spec['model']);a=tuple(map(F,spec['catalog']));rho=tuple(map(F,spec['charges']));B=F(spec['promise']);cost=dict(zip(a,rho))
        optimum=None;yes=False
        for size in range(n+1):
            for ids in combinations(range(n),size):
                s=sum(weights[i] for i in ids);c=tuple(sorted(low+tuple(high[i] for i in ids)))
                v=allocate(d,c,B,cost)['value'];assert v==zeta-F(abs(s-target),2*K)
                optimum=v if optimum is None else max(optimum,v);yes|=s==target;subsets+=1
        if n<=4:
            full=None
            for size in range(1,len(a)+1):
                for c in combinations(a,size):
                    if c[0]>min(B,min(d.caps)):continue
                    v=allocate(d,c,B,cost)['value'];full=v if full is None else max(full,v);books+=1
            assert full==optimum
        reference,distance,_=exact_subset_value(weights,target,K,zeta)
        assert optimum==reference and (optimum>=zeta)==yes
        rows.append(dict(case=case,weights=weights,target=target,K=K,threshold=str(zeta),optimum=str(optimum),yes=yes,distance=distance,instance=spec))
    result=dict(status='PASS',models=len(rows),optional_subsets=subsets,full_catalog_books=books,
                yes_cases=sum(x['yes'] for x in rows),no_cases=sum(not x['yes'] for x in rows),seconds=time.perf_counter()-start,rows=rows)
    (OUT/'HARDNESS_REGRESSION.json').write_text(json.dumps(result,indent=2)+'\n')
    print({k:v for k,v in result.items() if k!='rows'},flush=True)
    return result

def challenges():
    rng=random.Random(541001);cases=[];records=[]
    for n in [6,10,14,18]:
        w=[2*rng.randint(1,100) for _ in range(n)];target=sum(w)//2
        if target%2==0:target+=1
        spec,low,high,K,zeta=reduction(w,target);v,dist,states=exact_subset_value(w,target,K,zeta)
        case=dict(id=f'subsetsum-{n}',spec=spec,instance_sha256=digest(spec),epsilon='0',histories=n,catalog_size=2*n,budget=2*n,heterogeneous=False,
                  integer_weights=w,target=target,K=K,threshold=str(zeta),exact_value=str(v),subset_sum_distance=dist,integer_dp_states=states)
        cases.append(case)
        for method in ['price','uniform','enumeration','classbox','mip']:
            effective=dict(case,epsilon=str(F(1,8*K)) if method in ['uniform','classbox'] else '0')
            inp=OUT/'inputs'/(case['id']+'-'+method+'.json');inp.write_text(json.dumps(effective,indent=2)+'\n')
            dest=OUT/'runs'/(case['id']+'--'+method+'.json');phase=dest.with_suffix('.phase')
            if not dest.exists():
                env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
                with (OUT/'logs'/(case['id']+'--'+method+'.log')).open('w') as log:
                    p=subprocess.Popen([sys.executable,str(R/'code/worker.py'),str(inp),method],stdout=log,stderr=subprocess.STDOUT,env=env)
                    start=time.monotonic();last=None
                    while p.poll() is None:
                        if phase.exists():
                            try:last=json.loads(phase.read_text())
                            except json.JSONDecodeError:pass
                        limit=70 if last and last['phase']=='verification' else 5 if last else 45
                        if time.monotonic()-(last['time'] if last else start)>limit:p.kill();p.wait();break
                        time.sleep(.03)
                if not dest.exists():dest.write_text(json.dumps(dict(id=case['id'],method=method,status='PROCESS_LIMIT',returncode=p.returncode,last_phase=last,instance_sha256=digest(spec)),indent=2))
            rec=json.loads(dest.read_text());rec['reference_exact']=str(v)
            if rec.get('verification_status')=='PASS':assert F(rec['lower'])<=v<=F(rec['upper'])
            if method=='enumeration' and rec['status']=='EXACT':assert F(rec['lower'])==v
            records.append(rec);print(case['id'],method,rec['status'],flush=True)
    report=dict(status='PASS' if all(x['status']!='ERROR' and x.get('verification_status') not in ['FAIL','TIME_LIMIT'] for x in records) else 'FAIL',
                cases=cases,runs=records,interpretation='Deliberate NP-reduction stress family; parity makes the source target infeasible, and integer subset DP supplies exact references. No industrial representativeness is claimed.')
    (OUT/'CHALLENGE.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':regress();challenges()
