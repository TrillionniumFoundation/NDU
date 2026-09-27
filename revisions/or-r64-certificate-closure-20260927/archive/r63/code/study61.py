"""Prospectively frozen exception-scaling and adversarial study.

No R59/R60 generator, seed, or lower-bound construction is used. Deterministic
physical arrays are held fixed under tariff interventions. Failed, censored,
guard-limited, and mathematically inapplicable requests remain in the record.
"""
from pathlib import Path
import csv,datetime,gzip,hashlib,json,math,os,platform,signal,statistics,subprocess,sys,time
from copy import deepcopy
from rational import F,encode,digest,write
from price_path import Model,spec_for,normalize
R=Path(__file__).resolve().parents[1]
CORE=['tariff','price','enumeration','scip','hybrid']
DS=[0,1,2,4,6,8,10,12]

def physical(n,k,m,pattern=0,bits=0):
    a=[F(i*i,(n-1)**2) for i in range(n)]
    caps=[F(j,k-1) for j in range(k)]
    weights=[1+(j*7)%11 for j in range(k)]
    if pattern==1:weights=[10000 if j==k//2 else 1 for j in range(k)]
    if pattern==2:caps=[F(0)]+[F(1,2)+F(j,1024) for j in range(1,k)]
    if bits:weights=[2**bits+j+1 for j in range(k)]
    w=[F(x,sum(weights)) for x in weights]
    ceilings=[min(F(1),b+(F(1,8) if j%3==1 else 0)) for j,b in enumerate(caps)]
    if pattern==3:ceilings=caps
    model=Model.make(caps,w,[0]*k,ceilings,1,0)
    return spec_for(model,a,[F(1,200)]*n,model.cap_total*F(17,20),m)

def perturb(spec,d):
    s=deepcopy(spec);n=len(s['catalog']);fees=list(map(F,s['charges']))
    order=[(7*i+1)%n for i in range(n)]
    assert len(set(order))==n
    for j,idx in enumerate(order[:d]):fees[idx]+=F(j+1,2000)
    s['charges']=encode(fees);return s

def design():
    out=[]
    def add(name,spec,group,budget,methods=CORE,fraction=.6,guard=12,**meta):
        d,a,fees,B,m=normalize(spec)
        from tariff60 import standard_fee
        fee=standard_fee(fees)
        cid=f'{name}-t{budget:g}-f{fraction:g}'
        out.append(encode(dict(id=cid,specification_id=name,spec=spec,family=group,total_seconds=budget,
            optimization_cutoff_seconds=budget*fraction,optimization_fraction=fraction,epsilon=F(1,500),guard=guard,
            methods=methods,metadata=dict(N=len(a),k=len(d.caps),m=m,d=sum(x!=fee for x in fees),
                bit_length=max(x.numerator.bit_length()+x.denominator.bit_length() for x in list(a)+list(fees)+list(d.weights)),**meta))))
    for n,k,m in [(17,12,8),(65,32,16),(129,48,32)]:
        base=physical(n,k,m)
        for d in DS:
            spec=perturb(base,d)
            for budget in (1.,6.):add(f'scale-N{n}-d{d}',spec,'scaling',budget)
            if n==17:add(f'scale-N{n}-d{d}',spec,'long_tariff',30.,['tariff'])
        add(f'guard-N{n}-d13',perturb(base,13),'guard',1.,['tariff'])
    # New formula-based adversarial axes, not graph-clique encodings or R60 RNG.
    for kind in range(6):
        for rep in range(2):
            n=(19,41)[rep];k=(10,20)[rep];s=physical(n,k,(6,12)[rep],pattern=kind%4)
            if kind==0:s=perturb(s,min(10,n-1))
            if kind==1:
                s['promise']=str(F(s['promise'])*F(1,20));s=perturb(s,4)
            if kind==2:
                s['charges']=[str(F(1,200)+F((i%5)-2,100000)) for i in range(n)]
            if kind in (3,4):
                s['model']['reward_q']=[str(F(3,4))]*k
                s['model']['reward_r']=[str(F(1))]*k
                s['model']['gamma']=[str(F((j%5)+1,4)) for j in range(k)]
            if kind==5:
                s['charges']=[str(F(1+(i%2)*9,200)) for i in range(n)]
            add(f'adversarial-{kind}-{rep}',s,'adversarial',6.,CORE+['deficit','robust'],axis=kind)
    # Same requests with different optimization/checking allocations.
    for n,k,m in [(17,12,8),(65,32,16)]:
        for d in (0,4,12):
            s=perturb(physical(n,k,m),d)
            for fraction in (.35,.8):add(f'split-N{n}-d{d}',s,'split_sensitivity',3.,CORE,fraction=fraction)
    for bits in (16,64,256,1024,4096):
        add(f'bits-{bits}',perturb(physical(17,12,8,bits=bits),4),'bit_scaling',15.,['tariff','price'],input_bits=bits)
    return out

def source_hashes():
    # Freeze only the actual execution closure, not future presentation scripts.
    names=['rational.py','price_path.py','tariff60.py','check_tariff60.py','check_price.py','enumeration.py','check_enumeration.py','deficit.py','check_deficit.py','robust61.py','check_robust61.py','diagnostics61.py','scip61.py','worker61.py','checker61.py','study61.py']
    return {name:hashlib.sha256((R/'code'/name).read_bytes()).hexdigest() for name in names}

def freeze():
    cases=design();p=R/'results/STUDY_FREEZE.json'
    f=dict(schema='NDU-R61-prospective-v1',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_hashes=source_hashes(),cases=cases,
        distinct_specifications=len({digest(c['spec']) for c in cases}),declared_requests=sum(len(c['methods']) for c in cases),
        protocol=dict(sequential=True,budgets=[1,6],d_values=DS,hybrid='one price node/three prices, at most one-quarter optimization allowance; robust tariff only if four exceptions suffice, otherwise price restart',
            failure_policy='Retain every request; no synthetic success for deadline, guard or inapplicability',checker_memory='Fresh subprocess high-water RSS, not optimizer-retained process memory',
            interpretation='Deterministic controlled and adversarial inputs, not independent observations or field data'))
    if p.exists():
        old=json.loads(p.read_text());assert old['source_hashes']==f['source_hashes'] and old['cases']==cases,'Frozen sources or cases changed';return
    for name in ('inputs','records','certificates'):(R/'results'/name).mkdir(parents=True,exist_ok=True)
    for c in cases:write(R/'results/inputs'/f"{c['id']}.json",c)
    write(p,f);print('FREEZE',f['distinct_specifications'],len(cases),f['declared_requests'],flush=True)

def run():
    freeze();f=json.loads((R/'results/STUDY_FREEZE.json').read_text());done=0
    for c in f['cases']:
        # Fixed digest permutation avoids a persistent first-method privilege.
        for method in sorted(c['methods'],key=lambda v:hashlib.sha256((c['id']+v).encode()).hexdigest()):
            dest=R/'results/records'/f"{c['id']}--{method}.json";done+=1
            if dest.exists() and json.loads(dest.read_text()).get('parent_finished'):continue
            begin=time.perf_counter();proc=subprocess.Popen([sys.executable,str(R/'code/worker61.py'),str(R/'results/inputs'/f"{c['id']}.json"),method,str(dest)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
            timeout=False
            try:output=proc.communicate(timeout=c['total_seconds'])[0]
            except subprocess.TimeoutExpired:
                timeout=True;os.killpg(proc.pid,signal.SIGKILL);output=proc.communicate()[0]
            elapsed=time.perf_counter()-begin;dest.with_suffix('.log').write_text(output)
            rec=json.loads(dest.read_text()) if dest.exists() else dict(id=c['id'],method=method,status='NO_OUTPUT',instance_sha256=digest(c['spec']))
            rec.update(parent_finished=True,parent_seconds=elapsed,parent_timeout=timeout,parent_returncode=proc.returncode,within_total_budget=not timeout and elapsed<=c['total_seconds'])
            rec['rational_target_met']=bool(rec.get('verification_status')=='PASS' and rec['within_total_budget'] and F(rec['upper'])-F(rec['lower'])<=F(c['epsilon']))
            rec['numerical_target_met']=bool(method=='scip' and rec.get('verification_status')=='PASS_LOWER_ONLY' and rec['within_total_budget'] and rec.get('numerical_bound_consistent') and rec.get('numerical_absolute_gap') is not None and rec['numerical_absolute_gap']<=float(F(c['epsilon']))+1e-8)
            write(dest,rec);print(done,f['declared_requests'],c['id'],method,rec['status'],rec.get('verification_status'),round(elapsed,3),flush=True)
    write(R/'results/ENVIRONMENT.json',dict(python=sys.version,platform=platform.platform(),run_id=os.environ.get('GITHUB_RUN_ID'),pip=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines()))
    summarize()

def records():
    f=json.loads((R/'results/STUDY_FREEZE.json').read_text());cases={c['id']:c for c in f['cases']}
    return [dict(json.loads(p.read_text()),case=cases[json.loads(p.read_text())['id']]) for p in sorted((R/'results/records').glob('*.json')) if not p.name.endswith('.check.json')]

def quantiles(values):
    values=sorted(values)
    if not values:return None
    def at(p):
        x=(len(values)-1)*p;i=int(x);return values[i]*(1-x+i)+values[min(i+1,len(values)-1)]*(x-i)
    return dict(n=len(values),median=at(.5),p90=at(.9),p95=at(.95),maximum=max(values))

def summarize():
    rows=records();f=json.loads((R/'results/STUDY_FREEZE.json').read_text());assert len(rows)==f['declared_requests'] and all(x['parent_finished'] for x in rows)
    keys=['family','N','d','total_seconds','optimization_fraction','method'];buckets={}
    for row in rows:
        flat={**row,**row['case'],**row['case']['metadata']};key=tuple(flat[k] for k in keys);buckets.setdefault(key,[]).append(row)
    groups=[]
    for key,rs in sorted(buckets.items()):
        z=dict(zip(keys,key));z.update(n=len(rs),rational_targets=sum(r['rational_target_met'] for r in rs),numerical_targets=sum(r['numerical_target_met'] for r in rs),deadlines=sum(r['parent_timeout'] for r in rs),guards=sum(r['status']=='ENGINEERING_GUARD' for r in rs),inapplicable=sum(r['status']=='MATHEMATICALLY_INAPPLICABLE' for r in rs),errors=sum(r['status']=='ERROR' for r in rs))
        for q in ('parent_seconds','setup_seconds','optimization_seconds','serialization_seconds','verification_seconds','optimizer_peak_rss_kib','checker_peak_rss_kib','proof_bytes','compressed_proof_bytes','max_depth','tree_leaves'):
            z[q]=quantiles([r[q] for r in rs if isinstance(r.get(q),(int,float))])
        groups.append(z)
    price=[]
    for row in rows:
        if row['method']!='price':continue
        probes=row.get('mechanics',{}).get('root_support',[])
        price.append(dict(id=row['id'],family=row['case']['family'],N=row['case']['metadata']['N'],d=row['case']['metadata']['d'],
            total_seconds=row['case']['total_seconds'],root_observed=bool(probes),root_same_book_support=any(v['supports_promise'] for v in probes),
            minimum_distance=min((F(v['distance']) for v in probes),default=None),root_gap=row.get('mechanics',{}).get('root_gap'),
            root_candidates=len(probes),support_seconds=sum(v['support_seconds'] for v in probes),splits=row.get('mechanics',{}).get('splits'),
            max_depth=row.get('max_depth'),tree_leaves=row.get('tree_leaves'),rational_target_met=row['rational_target_met'],parent_timeout=row['parent_timeout']))
    write(R/'results/PRICE_DIAGNOSTICS.json',price)
    summary=dict(status='COMPLETE_RECORD_SET',distinct_specifications=f['distinct_specifications'],budget_tagged_cases=len(f['cases']),method_requests=len(rows),groups=groups,
        failures_preserved=True,maximum_proof_bytes=max((r.get('proof_bytes',0) for r in rows),default=0),maximum_compressed_proof_bytes=max((r.get('compressed_proof_bytes',0) for r in rows),default=0),
        price_root_observed=sum(r['root_observed'] for r in price),price_root_supported=sum(r['root_same_book_support'] for r in price),price_requests=len(price))
    write(R/'results/SUMMARY.json',summary)
    cols=['id','family','method','N','k','m','d','bit_length','total_seconds','optimization_fraction','status','verification_status','rational_target_met','numerical_target_met','parent_timeout','parent_seconds','setup_seconds','optimization_seconds','serialization_seconds','verification_seconds','optimizer_peak_rss_kib','checker_peak_rss_kib','proof_bytes','compressed_proof_bytes','max_depth','tree_leaves','selected_route','lower','upper','numerical_upper']
    with (R/'results/ALL_RUNS.csv').open('w',newline='') as h:
        writer=csv.DictWriter(h,fieldnames=cols);writer.writeheader()
        for row in rows:
            flat={**row,**row['case'],**row['case']['metadata']};writer.writerow({k:flat.get(k,'') for k in cols})
    print('SUMMARY',len(rows),flush=True)

def verify():
    f=json.loads((R/'results/STUDY_FREEZE.json').read_text());assert f['source_hashes']==source_hashes();rows=records();assert len(rows)==f['declared_requests']
    assert len({(r['id'],r['method']) for r in rows})==len(rows)
    from worker61 import check
    checked=0
    for r in rows:
        assert r['instance_sha256']==digest(r['case']['spec']) and r['parent_finished']
        if r.get('certificate'):
            p=R/'results'/r['certificate'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['certificate_sha256']
            if r.get('verification_status') in ('PASS','PASS_LOWER_ONLY'):
                cert=json.loads(gzip.decompress(p.read_bytes()));ans=check(cert,r['case']['spec']);assert ans['status']==r['verification_status'];checked+=1
        if r['rational_target_met']:assert r['verification_status']=='PASS' and r['within_total_budget'] and F(r['upper'])-F(r['lower'])<=F(r['case']['epsilon'])
    print('VERIFIED',len(rows),checked,flush=True)
    return dict(status='PASS',requests=len(rows),certificates=checked)
if __name__=='__main__':
    for command in sys.argv[1:]:{'freeze':freeze,'run':run,'summarize':summarize,'verify':verify}[command]()
