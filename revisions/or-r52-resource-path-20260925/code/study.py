"""Execute the frozen R52 study; preserve every case and every solver status.

Each record is appended immediately. Resume skips only a completed case with
an unchanged protocol hash. Fresh measurements require a fresh checkout.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from dataclasses import asdict
import json,gzip,hashlib,platform,sys,time,random,math,argparse,importlib,os
HERE=Path(__file__).resolve().parent;R=HERE.parent;ROOT=R.parents[1]
sys.path.insert(0,str(HERE))
from resource_path import Instance,solve,encode
from check_resource import verify
from pooling import solve as group_solve,eligibility_groups
from check_pooling import check as group_check
from box_solver import exhaustive_joint,solve as individual_solve
from mip_baseline import direct_milp
P=json.loads((R/'PROTOCOL.json').read_text());PH=hashlib.sha256((R/'PROTOCOL.json').read_bytes()).hexdigest()
OUT=R/'results';OUT.mkdir(exist_ok=True)
NEW_RECORDS=0


def load(name):
    path=OUT/name
    if not path.exists():path.write_text(json.dumps(dict(protocol_sha256=PH,protocol_commit='f2361236d6338c8af81a9c2e15908f961539c33d',python=sys.version,platform=platform.platform(),cases=[]),indent=2)+'\n')
    out=json.loads(path.read_text());assert out['protocol_sha256']==PH
    return out


def append(name,row):
    global NEW_RECORDS
    path=OUT/name;out=load(name);out['cases'].append(encode(row));path.write_text(json.dumps(out,indent=2)+'\n')
    print(name,row['id'],row.get('gap',''),row.get('seconds',''),flush=True)
    NEW_RECORDS+=1
    if int(os.environ.get('R52_MAX_NEW','0')) and NEW_RECORDS>=int(os.environ['R52_MAX_NEW']):raise SystemExit(0)


def model(c):return Instance.make(**c['model'])

def spec(cid,family,D,a,rho,B,m,**extra):
    return dict(id=cid,family=family,model=asdict(D),catalog=a,charges=rho,promise=B,m=m,k=len(D.caps),n=len(a),E=len(eligibility_groups(D,a)),**extra)


def diagnostics(cert,den=None):
    count=0;nb=0;db=0
    def walk(x):
        nonlocal count,nb,db
        if isinstance(x,dict):
            for val in x.values():walk(val)
        elif isinstance(x,(list,tuple)):
            for val in x:walk(val)
        elif isinstance(x,str):
            try:z=F(x)
            except (ValueError,ZeroDivisionError):return
            count+=1;nb=max(nb,abs(z.numerator).bit_length());db=max(db,z.denominator.bit_length())
    walk(cert)
    # A Bellman integer is the numerator of its rational value over this denominator.
    if den:db=max(db,int(den).bit_length())
    return dict(rational_entry_count=count,maximum_numerator_bits=nb,maximum_denominator_bits=db)


def store_certificate(cid,cert,kind,solve_seconds):
    start=time.perf_counter();verified=verify(cert) if kind=='resource' else group_check(encode(cert));checkseconds=time.perf_counter()-start
    raw=json.dumps(encode(cert),sort_keys=True,separators=(',',':')).encode();packed=gzip.compress(raw,mtime=0)
    path=OUT/'certificates'/f'{cid}.json.gz';path.parent.mkdir(exist_ok=True);path.write_bytes(packed)
    return dict(certificate=str(path.relative_to(R)),certificate_sha256=hashlib.sha256(packed).hexdigest(),
                compressed_bytes=len(packed),uncompressed_bytes=len(raw),checker_seconds=checkseconds,
                checker_to_optimization_ratio=checkseconds/max(solve_seconds,1e-12),independent_check=verified,
                **diagnostics(encode(cert),cert.get('denominator')))


def exact_reference(D,a,rho,B,m):
    start=time.perf_counter();z=exhaustive_joint(D,a,rho,B,m)
    return z['value'],time.perf_counter()-start


def resource_case(row,eps,reference=True):
    done={x['id'] for x in load('study.json')['cases']}
    if row['id'] in done:return
    D=Instance.make(**row['model']);a=tuple(map(F,row['catalog']));rho=tuple(map(F,row['charges']));B=F(row['promise']);m=row['m']
    ref,rt=exact_reference(D,a,rho,B,m) if reference else (None,None)
    ans=solve(D,a,rho,B,m,F(eps));cert=ans.pop('certificate')
    if ref is not None:assert ans['lower']<=ref<=ans['upper']
    row.update(ans,epsilon=eps,exact_reference=ref,exhaustive_seconds=rt,
               normalized_gap=ans['gap']/F(cert['lipschitz']),relative_gap=None if ref is None or ref<=0 else ans['gap']/ref,
               attained_error=None if ref is None else ref-ans['lower'],selected_classes=len(eligibility_groups(D,ans['book'])),status='COMPLETE')
    row.update(store_certificate(row['id'],cert,'resource',ans['seconds']));append('study.json',row)


def historical():
    old=json.loads((ROOT/'revisions/or-r49-dispersion-certificates-20260925/results/study.json').read_text())['cases']
    rows=[c for c in old if c['family']=='stress']
    (OUT/'historical_stress_requests.json').write_text(json.dumps(rows,indent=2)+'\n')
    return [next(c for c in rows if c['seed']==seed) for seed in P['historical_stress']['seeds']]


def grid():
    for c in historical():
        for eps in P['historical_stress']['accuracies']:
            row=spec(f"stress-{c['seed']}-e{eps.replace('/','_')}",'stress',model(c),tuple(map(F,c['catalog'])),tuple(map(F,c['charges'])),F(c['promise']),c['m'],seed=c['seed'])
            resource_case(row,eps)


def geometry():
    done={x['id'] for x in load('study.json')['cases']}
    for k in P['strict_prefix']['histories']:
        for n,m,bfrac in P['strict_prefix']['configurations']:
            cid=f'strict-k{k}-n{n}-m{m}'
            if cid in done:continue
            rng=random.Random(P['strict_prefix']['seed']+k+n+m)
            caps=tuple(F(j,2*(k+1)) for j in range(1,k+1));raw=[rng.randint(1,5) for _ in caps]
            gamma=tuple(F((j%7)**2,3) for j in range(k))
            ceilings=tuple(F(1,2)+F(1,4*(n-1))+F(j,4*(n-1)*(k+1)) for j in range(1,k+1))
            D=Instance.make(caps,[F(x,sum(raw)) for x in raw],gamma,ceilings);a=tuple(F(i,n-1) for i in range(n));rho=tuple(F(rng.randint(0,6),100) for _ in a);B=D.cap_total*F(bfrac)
            ans=group_solve(D,a,rho,B,m,epsilon=F(0),max_nodes=1,price_steps=0)
            assert ans['gap']==0 and ans['eligibility_groups']==1
            row=spec(cid,'strict-prefix',D,a,rho,B,m,promise_fraction=bfrac,epsilon='0',lower=ans['lower_bound'],upper=ans['upper_bound'],gap=ans['gap'],seconds=ans['seconds'],selected_classes=1,status='EXACT',evaluated_nodes=1)
            row.update(store_certificate(cid,ans,'group',ans['seconds']));append('study.json',row)
    p=P['eligibility_sweep'];k=p['histories'];n=p['catalog_size'];rng=random.Random(p['seed'])
    caps=tuple(F(j,14) for j in range(1,k+1));raw=[rng.randint(1,5) for _ in caps];weights=tuple(F(x,sum(raw)) for x in raw)
    gamma=tuple(F(rng.randint(0,8),4) for _ in caps);a=tuple(F(i,n-1) for i in range(n));rho=tuple(F(rng.randint(0,4),100) for _ in a)
    for E in p['requested_classes']:
        ceilings=[None]*k
        for group in range(E):
            ids=list(range(group*k//E,(group+1)*k//E));tau=F(math.ceil(max(caps[j] for j in ids)*16),16)+F(1,64)
            for j in ids:ceilings[j]=tau
        D=Instance.make(caps,weights,gamma,ceilings);B=D.cap_total*F(p['promise_fraction'])
        row=spec(f'eligibility-E{E}','eligibility-sweep',D,a,rho,B,p['budget'],requested_classes=E)
        assert row['E']==E
        resource_case(row,p['accuracy'])
    p=P['robustness'];k=p['histories'];rng=random.Random(p['seed']);caps=tuple(F(j+2,25) for j in range(k));gamma=tuple(F(j%5,2) for j in range(k));weights=(F(1,k),)*k
    base=tuple(map(F,p['base_catalog']));ceilings=tuple(F(2,5)+F(j+1,40) for j in range(k));B=sum(w*b for w,b in zip(weights,caps))*F(9,10)
    for family,taus in [('within-gap-low',tuple(t-F(1,1000) for t in ceilings)),('within-gap-high',tuple(t+F(1,1000) for t in ceilings))]:
        D=Instance.make(caps,weights,gamma,taus);rho=tuple(F(0) if x==0 else F(1,100) for x in base)
        resource_case(spec(family,'robustness',D,base,rho,B,p['budget']),p['accuracy'])
    for side in [-1,1]:
        taus=tuple(F(1,2)+F(side,10000) if j<k//2 else F(3,5) for j in range(k));a=tuple(sorted(base+(F(1,2),)));D=Instance.make(caps,weights,gamma,taus);rho=tuple(F(0) if x==0 else F(1,100) for x in a)
        resource_case(spec('boundary-'+('below' if side<0 else 'above'),'robustness',D,a,rho,B,p['budget']),p['accuracy'])
    for charge in [F(0),F(p['dominated_opening_charge'])]:
        for count in range(0,len(p['insertions'])+1):
            ins=tuple(map(F,p['insertions'][:count]));a=tuple(sorted(base+ins));rho=tuple(charge if x in ins else F(0) if x==0 else F(1,100) for x in a);D=Instance.make(caps,weights,gamma,ceilings)
            row=spec(f"refinement-{'free' if charge==0 else 'dominated'}-{count}",'robustness',D,a,rho,B,p['budget'],inserted_count=count,insertion_charge=charge)
            resource_case(row,p['accuracy'])
            actual=next(z for z in load('study.json')['cases'] if z['id']==row['id'])
            if charge:assert all(F(x) not in ins for x in actual['book'])


def baselines():
    rows=historical();done={x['id'] for x in load('baselines.json')['cases']}
    for c in rows:
        D=model(c);a=tuple(map(F,c['catalog']));rho=tuple(map(F,c['charges']));B=F(c['promise']);m=c['m'];ref,rt=exact_reference(D,a,rho,B,m)
        plans=[('group',n,4) for n in P['matched_baselines']['group_nodes']]+[('group',31,s) for s in [0,8]]+[('individual',31,4)]
        for method,nodes,prices in plans:
            cid=f'{method}-{c["seed"]}-n{nodes}-p{prices}'
            if cid in done:continue
            routine=group_solve if method=='group' else individual_solve
            z=routine(D,a,rho,B,m,epsilon=F(1,1000),max_nodes=nodes,price_steps=prices)
            assert z['lower_bound']<=ref<=z['upper_bound']
            row=dict(id=cid,seed=c['seed'],method=method,node_limit=nodes,price_steps=prices,exact_reference=ref,exhaustive_seconds=rt,
                lower=z['lower_bound'],upper=z['upper_bound'],gap=z['gap'],relative_gap=z['gap']/ref if ref>0 else None,
                normalized_gap=z['gap']/max(D.r,max(D.gamma)),seconds=z['seconds'],nodes=z['evaluated_nodes'],oracle_calls=z['oracle_calls'],status=z['status'])
            if method=='group':row.update(store_certificate(cid,z,'group',z['seconds']))
            append('baselines.json',row)
        # Two MIP envelopes share the grid solver's measured optimization allowance.
        cid=f'mip-{c["seed"]}'
        if cid in done:continue
        study=next(x for x in load('study.json')['cases'] if x['id']==f'stress-{c["seed"]}-e1_1000')
        limit=max(0.1,study['seconds']/2)
        z={e:direct_milp(D,a,rho,B,m,segments=P['mip']['segments'],envelope=e,time_limit=limit) for e in P['mip']['envelopes']}
        up=z['tangent'].get('numerical_upper');low=z['secant'].get('value')
        if up is not None:assert up+1e-6>=float(ref)
        if low is not None:assert low<=float(ref)+1e-6
        append('baselines.json',dict(id=cid,method='mip',seed=c['seed'],exact_reference=str(ref),envelopes=z,seconds_per_envelope=limit,
              grid_comparison_seconds=study['seconds'],bracket_width=None if up is None or low is None else up-low,
              scope='Floating-point envelope diagnostics, not an exact rational certificate'))


def summary():
    rows=load('study.json')['cases'];base=load('baselines.json')['cases'];stress=[r for r in rows if r['family']=='stress'];strict=[r for r in rows if r['family']=='strict-prefix']
    fine=[r for r in stress if r['epsilon']=='1/1000'];old=json.loads((OUT/'historical_stress_requests.json').read_text())
    out=dict(status='PASS',study_cases=len(rows),resource_certificates=len(rows)-len(strict),strict_prefix_certificates=len(strict),
        fine_stress_complete=len(fine),fine_stress_max_gap=max(float(F(r['gap'])) for r in fine),
        fine_stress_attained_exact=sum(F(r['attained_error'])==0 for r in fine),historical_requests=len(old),historical_unresolved=sum(r['status']!='COMPLETE' for r in old),
        max_histories=max(r['k'] for r in rows),max_eligibility_classes=max(r['E'] for r in rows),
        baseline_cases=len(base),mip_solves=sum(2 for r in base if r['method']=='mip'),
        mip_time_limits=sum(v['status']==1 for r in base if r['method']=='mip' for v in r['envelopes'].values()),
        caveat='Synthetic structural evidence. A positive-width certificate is an additive interval, not an exact global solution. Root exact closures and attained exact optima are reported separately.')
    (OUT/'SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['grid','geometry','baselines','all'],default='all');args=parser.parse_args()
    for name in ['grid','geometry','baselines']:
        if args.phase in [name,'all']:globals()[name]()
    if args.phase=='all':summary()
