"""Execute the precommitted R49 protocol. All records, including failures, persist."""
from pathlib import Path
from fractions import Fraction as F
from dataclasses import asdict
import json,gzip,hashlib,platform,sys,time,random,runpy,importlib.util,os
HERE=Path(__file__).resolve().parent;R=HERE.parent;ROOT=R.parents[1]
sys.path.insert(0,str(HERE))
from pooling import Instance,solve,encode
from check_pooling import check
from box_solver import exhaustive_joint
from mip_baseline import direct_milp
fixture_test=runpy.run_path(str(HERE/'tests.py'))['fixture']

def save_case(path,row,certificate):
    encoded=encode(certificate);start=time.perf_counter();verified=check(encoded);seconds=time.perf_counter()-start
    certpath=R/'results/certificates'/f"{row['id']}.json.gz";certpath.parent.mkdir(parents=True,exist_ok=True)
    certpath.write_bytes(gzip.compress(json.dumps(encoded,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    row.update(certificate=str(certpath.relative_to(R)),certificate_sha256=hashlib.sha256(certpath.read_bytes()).hexdigest(),
        independent_check=verified,check_seconds=seconds,eligibility_groups=certificate['eligibility_groups'],
        **{k:certificate[k] for k in ['lower_bound','upper_bound','gap','status','seconds','evaluated_nodes','oracle_calls']})
    out=json.loads(path.read_text());out['cases'].append(encode(row));path.write_text(json.dumps(out,indent=2)+'\n')
    print(row['id'],'k',row['k'],'E',row['eligibility_groups'],'gap',float(certificate['gap']),'sec',round(certificate['seconds'],3),'check',round(seconds,3),flush=True)


def init(path,protocol):
    if not path.exists():path.write_text(json.dumps(dict(protocol_sha256=hashlib.sha256(protocol.read_bytes()).hexdigest(),
        python=sys.version,platform=platform.platform(),cases=[]),indent=2)+'\n')
    out=json.loads(path.read_text())
    if out['protocol_sha256']!=hashlib.sha256(protocol.read_bytes()).hexdigest():raise ValueError('Protocol changed')
    return {x['id'] for x in out['cases']}


def common(seed,k,n):
    rng=random.Random(seed);caps=tuple(F(1,10)+F(4*(j+1),5*(k+1)) for j in range(k))
    gamma=tuple(F((j%7)**2,3) for j in range(k));raw=[rng.randint(1,5) for _ in caps]
    D=Instance.make(caps,[F(x,sum(raw)) for x in raw],gamma,[F(1)]*k)
    a=tuple(F(i,n-1) for i in range(n));rho=tuple(F(rng.randint(0,6),100) for _ in a)
    return D,a,rho,D.cap_total*F(9,10)


def run():
    protocol=R/'PROTOCOL.json';p=json.loads(protocol.read_text());path=R/'results/study.json';done=init(path,protocol)
    oldpath=ROOT/'revisions/or-r48-harmonic-coarsening-20260925/results/study.json';old=json.loads(oldpath.read_text())['cases']
    for r in old:
        caseid='paired-'+r['id']
        if caseid in done:continue
        raw=r['model'];D=Instance.make(raw['caps'],raw['weights'],raw['gamma'],raw['ceilings'],raw['r'],raw['curvature'])
        a,rho=tuple(map(F,r['catalog'])),tuple(map(F,r['charges']));B=F(r['promise']);m=r['m']
        ans=solve(D,a,rho,B,m,epsilon=F(p['paired_epsilon']),max_nodes=p['paired_node_limit'],price_steps=p['price_steps'])
        if r['reference']:
            ref=F(r['reference']['original']);assert ans['lower_bound']<=ref<=ans['upper_bound']
        row=dict(id=caseid,family='paired',k=r['k'],n=r['n'],m=m,model=asdict(D),catalog=a,charges=rho,promise=B,epsilon=p['paired_epsilon'],node_limit=p['paired_node_limit'],
            historical_reference=r['reference'],historical_r48_harmonic=r['harmonic'],historical_r48_minimum=r['minimum'],
            historical_source_sha256=hashlib.sha256(oldpath.read_bytes()).hexdigest())
        save_case(path,row,ans)
    commonp=p['additional_common_eligibility']
    for k in commonp['histories']:
        for n in commonp['catalog_sizes']:
            for seed in commonp['seeds']:
                caseid=f'common-k{k}-n{n}-s{seed}'
                if caseid in done:continue
                D,a,rho,B=common(seed,k,n)
                ans=solve(D,a,rho,B,commonp['budget'],epsilon=F(commonp['epsilon']),max_nodes=commonp['node_limit'],price_steps=0)
                assert ans['gap']==0 and ans['eligibility_groups']==1 and ans['evaluated_nodes']==1
                row=dict(id=caseid,family='common',k=k,n=n,m=commonp['budget'],seed=seed,model=asdict(D),catalog=a,charges=rho,promise=B,epsilon='0',node_limit=1)
                save_case(path,row,ans)
    stress=p['eligibility_stress']
    for seed in stress['seeds']:
        D,a,rho,B=fixture_test(seed,stress['histories'],stress['catalog_size'],False)
        refid=f'stress-reference-{seed}'
        refpath=R/'results'/f'{refid}.json'
        if refpath.exists():ref=json.loads(refpath.read_text())
        else:
            t=time.perf_counter();z=exhaustive_joint(D,a,rho,B,stress['budget']);elapsed=time.perf_counter()-t
            ref=encode(dict(policy=z,seconds=elapsed));refpath.write_text(json.dumps(ref,indent=2)+'\n')
        for eps in stress['epsilon']:
            for nodes in stress['node_limits']:
                caseid=f'stress-s{seed}-e{eps.replace("/","_")}-n{nodes}'
                if caseid in done:continue
                ans=solve(D,a,rho,B,stress['budget'],epsilon=F(eps),max_nodes=nodes,price_steps=p['price_steps'])
                assert ans['lower_bound']<=F(ref['policy']['value'])<=ans['upper_bound']
                row=dict(id=caseid,family='stress',k=stress['histories'],n=stress['catalog_size'],m=stress['budget'],seed=seed,model=asdict(D),catalog=a,charges=rho,promise=B,
                    epsilon=eps,node_limit=nodes,exact_reference=ref['policy']['value'],exhaustive_seconds=ref['seconds'],reference_file=refpath.name)
                save_case(path,row,ans)
    # Independent uneliminated formulation; every status and numerical bound retained.
    mp=R/'results/mip.json';mdone=init(mp,protocol)
    allrows=json.loads(path.read_text())['cases']
    selected=[r for r in allrows if r['family']=='paired' and r['historical_reference']]
    selected += [next(r for r in allrows if r['family']=='stress' and r['seed']==seed) for seed in stress['seeds']]
    for row in selected:
        cid='mip-'+row['id']
        if cid in mdone:continue
        raw=row['model'];D=Instance.make(raw['caps'],raw['weights'],raw['gamma'],raw['ceilings'],raw['r'],raw['curvature']);a=tuple(map(F,row['catalog']));rho=tuple(map(F,row['charges']));B=F(row['promise'])
        ref=F(row['historical_reference']['original']) if row['family']=='paired' else F(row['exact_reference'])
        runs={}
        for envelope in p['independent_mip']['envelopes']:
            runs[envelope]=direct_milp(D,a,rho,B,row['m'],segments=p['independent_mip']['segments'],envelope=envelope,time_limit=p['independent_mip']['seconds_per_solve'])
        upper=runs['tangent'].get('numerical_upper');lower=runs['secant'].get('value')
        if upper is not None:assert upper+1e-6>=float(ref)
        if lower is not None:assert lower<=float(ref)+1e-6
        out=json.loads(mp.read_text());out['cases'].append(dict(id=cid,source_case=row['id'],exact_reference=str(ref),envelopes=runs,bracket_width=None if upper is None or lower is None else upper-lower));mp.write_text(json.dumps(out,indent=2)+'\n')
        print(cid,'statuses',[v['status'] for v in runs.values()],flush=True)
    summarise()


def summarise():
    rows=json.loads((R/'results/study.json').read_text())['cases'];mip=json.loads((R/'results/mip.json').read_text())['cases']
    paired=[r for r in rows if r['family']=='paired'];commonrows=[r for r in rows if r['family']=='common'];stress=[r for r in rows if r['family']=='stress']
    out=dict(cases=len(rows),paired_cases=len(paired),paired_complete=sum(r['status']=='COMPLETE' for r in paired),
        paired_exact=sum(F(r['gap'])==0 for r in paired),paired_harmonic_historical_complete=sum(r['historical_r48_harmonic']['status']=='COMPLETE' for r in paired),
        paired_harmonic_upper_improved=sum(F(r['upper_bound'])<F(r['historical_r48_harmonic']['upper_bound']) for r in paired),
        paired_harmonic_gap_improved=sum(F(r['gap'])<F(r['historical_r48_harmonic']['gap']) for r in paired),
        paired_harmonic_gap_equal=sum(F(r['gap'])==F(r['historical_r48_harmonic']['gap']) for r in paired),
        paired_harmonic_gap_worse=sum(F(r['gap'])>F(r['historical_r48_harmonic']['gap']) for r in paired),
        paired_max_gap=max(float(F(r['gap'])) for r in paired),common_cases=len(commonrows),common_exact=sum(F(r['gap'])==0 for r in commonrows),
        max_histories=max(r['k'] for r in rows),stress_runs=len(stress),stress_complete=sum(r['status']=='COMPLETE' for r in stress),
        stress_unresolved=sum(r['status']!='COMPLETE' for r in stress),stress_max_gap=max(float(F(r['gap'])) for r in stress),
        mip_solves=2*len(mip),mip_time_limits=sum(v['status']==1 for r in mip for v in r['envelopes'].values()),
        exact_certificates=len(rows),timing_scope=os.environ.get('R49_EXECUTION_SCOPE','R49 local execution')+'; R48 timings remain historical, not matched-machine claims')
    (R/'results/SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
