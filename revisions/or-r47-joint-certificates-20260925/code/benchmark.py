"""Fixed-protocol distinct-history experiments. Every requested case is saved.

Times are local wall time, not GitHub Actions times. Soft limits are checked
between complete oracle blocks. Certificates are separately independently checked.
"""
from pathlib import Path
from fractions import Fraction as F
from dataclasses import asdict
from bisect import bisect_right
import hashlib,json,gzip,sys,platform,time,random
from coarsening import Instance,bin_partition,solve,encode
from check_coarsening import check
from box_solver import solve as raw_solve,exhaustive_joint
from check_certificate import check as raw_check
from price_prefix_baseline import solve as prefix_solve
R=Path(__file__).resolve().parents[1]

def fixture(seed,k,n,spread,regimes,charged):
    rng=random.Random(seed);s=F(spread)
    centers=(F(3,10),F(1,2),F(7,10),F(9,10));cost=(F(1),F(2),F(4),F(8))
    caps=tuple(centers[j%4]+s*F(j+1,k+1) for j in range(k))
    gamma=tuple(cost[j%4]+s*F(k-j,k+1) for j in range(k))
    raw=[rng.randint(1,7) for _ in range(k)];weights=tuple(F(x,sum(raw)) for x in raw)
    ceilings=tuple(F(1) if regimes==1 else centers[j%4]+F(1,10) for j in range(k))
    data=Instance.make(caps,weights,gamma,ceilings)
    a=tuple(F(i,n-1) for i in range(n));rho=tuple(F(rng.randint(0,24),1000) if charged else F(0) for i in range(n))
    B=data.cap_total*(F(1) if seed%3==0 else F(19,20) if seed%3==1 else F(4,5))
    return data,a,rho,B

def specs():
    ans=[]
    # Twelve small/medium cases with all-book joint reference.
    for z in range(12):
        ans.append(dict(id=f'primary-{z:02d}',seed=100+z,k=(4,8,12)[z%3],n=9,
            m=2+(z%2),spread=('1/1000' if z<6 else '1/50'),regimes=1 if z%2 else 4,
            charged=bool(z%3),category='primary'))
    # Distinct histories, not replicas; two dispersion levels, two regimes.
    for k in (32,128,256):
        for regimes in (1,4):
            for spread in ('1/1000','1/50'):
                z=len(ans);ans.append(dict(id=f'scale-{k}-{regimes}-{spread.replace("/","-")}',
                    seed=200+z,k=k,n=17,m=3,spread=spread,regimes=regimes,
                    charged=bool(z%2),category='scaling'))
    return ans

def manifest():
    return dict(protocol_version=1,cases=specs(),absolute_epsilon='1/1000',
        coarse_cap_bin='2 * spread',coarse_cost_bin='2 * spread',
        price_bisections=8,node_limit=101,soft_seconds=4,
        baseline='R46 unaggregated boxes and R43 priced-prefix, same epsilon/node/soft limits',
        exact_reference='all books on all 12 primary cases',
        independence='R47 lift/aggregation checker plus inherited Bellman and full-cover checker',
        scope='Synthetic distinct-history perturbation study; no application calibration or external preregistration',
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())

def savecert(name,c,checker):
    value=encode(c);started=time.perf_counter();checkresult=checker(value);seconds=time.perf_counter()-started
    raw=json.dumps(value,sort_keys=True,separators=(',',':')).encode();path=R/'results/certificates'/f'{name}.json.gz'
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(gzip.compress(raw,mtime=0))
    return dict(path=str(path.relative_to(R)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        checked=checkresult,check_seconds=seconds,uncompressed_bytes=len(raw))

def run():
    protocol=R/'PROTOCOL.json';doc=manifest()
    if protocol.exists():
        if json.loads(protocol.read_text())!=doc:raise ValueError('Protocol changed; do not overwrite completed evidence')
    else:protocol.write_text(json.dumps(doc,indent=2)+'\n')
    path=R/'results/joint.json'
    results=json.loads(path.read_text()) if path.exists() else dict(protocol_sha256=hashlib.sha256(protocol.read_bytes()).hexdigest(),
        python=sys.version,platform=platform.platform(),cases=[])
    done={r['id'] for r in results['cases']}
    for spec in specs():
        if spec['id'] in done:continue
        D,a,rho,B=fixture(spec['seed'],spec['k'],spec['n'],spec['spread'],spec['regimes'],spec['charged'])
        G=bin_partition(D,a,2*F(spec['spread']),2*F(spec['spread']))
        c=solve(D,a,rho,B,spec['m'],G,F(1,1000),max_nodes=101,seconds_limit=4,price_steps=8)
        cert=savecert(spec['id']+'-coarse',c,check)
        raw=raw_solve(D,a,rho,B,spec['m'],F(1,1000),max_nodes=101,seconds_limit=4,price_steps=8,aggregate_types=True,record_tables=True)
        rawcert=savecert(spec['id']+'-raw',raw,raw_check)
        prefix=prefix_solve(D,a,rho,B,spec['m'],F(1,1000),seconds_limit=4,max_nodes=101)
        ref=None
        if spec['category']=='primary':
            t=time.perf_counter();p=exhaustive_joint(D,a,rho,B,spec['m']);ref=dict(value=p['value'],seconds=time.perf_counter()-t,book=p['book'])
            assert c['lower_bound']<=p['value']<=c['upper_bound']
            assert raw['lower_bound']<=p['value']<=raw['upper_bound']
            assert prefix['lower']<=p['value']<=prefix['upper']
        scale=D.r+max(D.gamma)/2+sum(sorted(rho,reverse=True)[:spec['m']])
        keep=('status','lower_bound','upper_bound','gap','uniform_defect','posterior_defect','weighted_lift_distance','seconds','lift_seconds','groups_count','original_exact_types')
        record=dict(**spec,model=asdict(D),catalog=a,charges=rho,promise=B,objective_scale=scale,
            actual_eligibility_regimes=len(set(bisect_right(a,t) for t in D.ceilings)),
            coarse={x:c[x] for x in keep},coarse_certificate=cert,
            raw={x:raw[x] for x in ('status','lower_bound','upper_bound','gap','seconds','evaluated_nodes','oracle_calls','types')},
            raw_certificate=rawcert,priced_prefix=prefix,reference=ref)
        record['coarse'].update(evaluated_nodes=c['inner_certificate']['evaluated_nodes'],oracle_calls=c['inner_certificate']['oracle_calls'],inner_gap=c['inner_certificate']['gap'])
        record['coarse']['scaled_gap']=c['gap']/scale;record['raw']['scaled_gap']=raw['gap']/scale
        results['cases'].append(encode(record));path.write_text(json.dumps(results,indent=2)+'\n')
        print(spec['id'],'k/q',spec['k'],len(G),'gap',float(c['gap']),'raw',float(raw['gap']),'times',round(c['seconds'],3),round(raw['seconds'],3),'prefix',round(prefix['seconds'],3),flush=True)
    print('ALL CASES SAVED',len(results['cases']),flush=True)
if __name__=='__main__':run()
