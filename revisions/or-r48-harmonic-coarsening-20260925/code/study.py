"""Frozen paired harmonic/minimum-curvature study, with all failures retained.

This is a targeted synthetic ablation, not an external holdout or calibration.
No soft time limit determines rational search: each method receives 31 nodes
and four price refinements. Timings are measured and identified by toolchain.
"""
from fractions import Fraction as F
from pathlib import Path
from dataclasses import asdict
import json,gzip,time,random,hashlib,platform,sys
from harmonic import Instance,solve,reduce,sqrt_partition,encode
from coarsening import solve as minimum_solve,bin_partition,reduced_model
from check_harmonic import check
from check_coarsening import check as minimum_check
from box_solver import exhaustive_joint
from mip_baseline import direct_milp
R=Path(__file__).resolve().parents[1]

def specs():
    return [dict(id=f'case-{i:02d}',seed=48000+i,k=(4,6,8)[i%3] if i<12 else (32,128,256)[(i-12)//4],
                 n=7 if i<12 else 9,m=1 if i%4==0 else 2+(i%2),family=i%4,reference_required=i<12) for i in range(24)]

def fixture(s):
    rng=random.Random(s['seed']);k=s['k'];f=s['family']
    caps=[F(4,5) if f==0 else F(1,5)+F(j+1,k+1)*F(7,10) if f==1 else F(3+(j%3)*2,10)+F(j+1,200*(k+1)) for j in range(k)]
    costs=[F(1,8)+F(31,8)*F(j+1,k+1)**2 if f<2 else F((j%4+1)**2,2)+F(j+1,100*(k+1)) for j in range(k)]
    if f==3:costs[1]=F(0)
    w=[rng.randint(1,5) for _ in caps];weights=[F(x,sum(w)) for x in w]
    ceilings=[F(1) if f<2 else min(F(1),b+F(1,5)) for b in caps]
    D=Instance.make(caps,weights,costs,ceilings)
    a=tuple(F(i,s['n']-1) for i in range(s['n']));rho=tuple(F(rng.randint(0,3),200) if f%2 else F(0) for _ in a)
    B=D.cap_total*(F(4,5) if f<2 else F(1) if f==2 else F(19,20))
    G=sqrt_partition(D,a,F(1,3),F(100)) # one curvature bin; test effective pooling, not cherry-picked bins
    return D,a,rho,B,G

def save(c,name,checker):
    obj=encode(c);t=time.perf_counter();v=checker(obj);ct=time.perf_counter()-t
    data=json.dumps(obj,sort_keys=True,separators=(',',':')).encode();p=R/'results/certificates'/f'{name}.json.gz';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress(data,mtime=0))
    return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),check_seconds=ct,checked=v)

def run():
    proto=dict(cases=specs(),epsilon='1/1000',inner_epsilon='1/2000',node_limit=31,price_steps=4,
        partition='same eligibility, cap bins width 1/3, all costs in one bin, minimum-cap guard',
        mip='all 12 primary cases, both envelopes, 32 segments, 3 seconds per solve',
        scope='Targeted, locally frozen synthetic cost-heterogeneity ablation, not independent application data',
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        instrumentation_note='Final MIP pass uses retained R46 node-accounting wrapper; same 24 cases and solver limits as initial authoring execution.')
    pp=R/'PROTOCOL.json'
    if pp.exists() and json.loads(pp.read_text())!=proto:raise ValueError('Frozen protocol differs')
    pp.write_text(json.dumps(proto,indent=2)+'\n')
    path=R/'results/study.json';out=json.loads(path.read_text()) if path.exists() else dict(python=sys.version,platform=platform.platform(),protocol_sha256=hashlib.sha256(pp.read_bytes()).hexdigest(),cases=[])
    done={x['id'] for x in out['cases']}
    for s in specs():
        if s['id'] in done:continue
        D,a,rho,B,G=fixture(s)
        h=solve(D,a,rho,B,s['m'],G,F(1,1000),max_nodes=31,price_steps=4)
        mc=minimum_solve(D,a,rho,B,s['m'],G,F(1,1000),inner_epsilon=F(1,2000),max_nodes=31,price_steps=4)
        hcert=save(h,s['id']+'-harmonic',check);mcert=save(mc,s['id']+'-minimum',minimum_check)
        ref=None
        if s['reference_required']:
            t=time.perf_counter();po=exhaustive_joint(D,a,rho,B,s['m']);origtime=time.perf_counter()-t
            H,_,_=reduce(D,a,G);M,_,_=reduced_model(D,a,G)
            ph=exhaustive_joint(H,a,rho,B,s['m']);pm=exhaustive_joint(M,a,rho,B,s['m'])
            assert po['value']<=ph['value']<=pm['value']
            assert h['lower_bound']<=po['value']<=h['upper_bound'] and mc['lower_bound']<=po['value']<=mc['upper_bound']
            ref=dict(original=po['value'],harmonic=ph['value'],minimum=pm['value'],original_seconds=origtime)
        keep=['lower_bound','upper_bound','gap','uniform_defect','posterior_defect','status','seconds','lift_seconds']
        summary=lambda c:{**{x:c[x] for x in keep},'nodes':c['inner_certificate']['evaluated_nodes'],'inner_gap':c['inner_certificate']['gap']}
        lo=max(h['lower_bound'],mc['lower_bound']);hi=min(h['upper_bound'],mc['upper_bound'])
        # Compare theorem partition dimensions at tolerances, without pretending to solve those potentially large instances.
        partitions=[]
        for e in [F(1,10),F(1,100),F(1,1000)]:
            L=max(D.r,max(D.gamma));bg=e/(2*L)
            hs=sqrt_partition(D,a,bg,e/2);ms=bin_partition(D,a,bg,e/2)
            partitions.append(dict(epsilon=e,harmonic_groups=len(hs),minimum_groups=len(ms)))
        row=dict(**s,model=asdict(D),catalog=a,charges=rho,promise=B,groups=G,
            harmonic=summary(h),minimum=summary(mc),harmonic_certificate=hcert,minimum_certificate=mcert,
            combined=dict(lower=lo,upper=hi,gap=hi-lo,status='COMPLETE' if hi-lo<=F(1,1000) else 'UNRESOLVED'),reference=ref,
            accuracy_partitions=partitions,objective_scale=D.r+max(D.gamma)/2+sum(sorted(rho,reverse=True)[:s['m']]))
        out['cases'].append(encode(row));path.write_text(json.dumps(out,indent=2)+'\n')
        print(s['id'],s['k'],len(G),'H',float(h['gap']),'M',float(mc['gap']),'seconds',round(h['seconds'],2),round(mc['seconds'],2),flush=True)
    # The direct formulation is independent of harmonic pooling and path DPs.
    mp=R/'results/mip.json';mo=json.loads(mp.read_text()) if mp.exists() else dict(cases=[])
    done={x['id'] for x in mo['cases']}
    for s in specs()[:12]:
        if s['id'] in done:continue
        D,a,rho,B,G=fixture(s);rr=next(x for x in out['cases'] if x['id']==s['id'])['reference'];pv=float(F(rr['original']))
        records={}
        for mode in ('tangent','secant'):
            v=direct_milp(D,a,rho,B,s['m'],segments=32,envelope=mode,time_limit=3)
            records[mode]=v
        upper=records['tangent'].get('numerical_upper');lower=records['secant'].get('value')
        if upper is not None:assert upper+1e-6>=pv
        if lower is not None:assert lower<=pv+1e-6
        mo['cases'].append(dict(id=s['id'],exact_value=pv,envelopes=records,bracket_width=None if upper is None or lower is None else upper-lower))
        mp.write_text(json.dumps(mo,indent=2)+'\n');print('MIP',s['id'],[v['status'] for v in records.values()],flush=True)
    summarise()

def summarise():
    rows=json.loads((R/'results/study.json').read_text())['cases'];mip=json.loads((R/'results/mip.json').read_text())['cases']
    out=dict(cases=len(rows),max_histories=max(r['k'] for r in rows),certificates=2*len(rows),
        harmonic_complete=sum(r['harmonic']['status']=='COMPLETE' for r in rows),minimum_complete=sum(r['minimum']['status']=='COMPLETE' for r in rows),
        combined_complete=sum(r['combined']['status']=='COMPLETE' for r in rows),
        strict_harmonic_reference_improvements=sum(F(r['reference']['harmonic'])<F(r['reference']['minimum']) for r in rows if r['reference']),
        reference_cases=sum(bool(r['reference']) for r in rows),mip_solves=2*len(mip),
        mip_time_limits=sum(v['status']==1 for r in mip for v in r['envelopes'].values()),
        max_harmonic_gap=max(float(F(r['harmonic']['gap'])) for r in rows),
        max_combined_gap=max(float(F(r['combined']['gap'])) for r in rows),
        statement='Unresolved paired coarsening cases are retained. Successes are original-space intervals, not reduced solver statuses.')
    (R/'results/SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
