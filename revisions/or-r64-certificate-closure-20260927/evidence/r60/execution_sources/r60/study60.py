"""R60 prospectively frozen, sequential experiment; immutable completed requests.
Three model-derived service-contract families, 30 structural seeds each, three
end-to-end budgets. These are NOT field observations or independent RCSP data.
"""
from pathlib import Path
import datetime,gzip,hashlib,json,math,os,platform,random,statistics,subprocess,sys,time,csv
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];OLD=ROOT/'revisions/or-r58-structural-referee-20260926/code'
sys.path.insert(0,str(OLD))
from rational import F,encode,digest,write
from price_path import Model,spec_for,normalize
METHODS=('price','deficit','enumeration','scip');BUDGETS=(.5,1.5,3.0)
def cases():
    out=[]
    for family in ('standard','exceptions','curved'):
        for rep in range(30):
            rng=random.Random(600927+rep);k=(8,16,32)[rep%3];N=(9,17,25)[(rep//3)%3];m=(2,4,6)[(rep//9)%3]
            caps=[F(rng.randrange(8,30),32) for _ in range(k)];raw=[rng.randrange(1,9) for _ in caps];weights=[F(x,sum(raw)) for x in raw]
            ceilings=[min(F(1),b+F(rng.randrange(0,5),32)) for b in caps]
            r=F(3,2);gamma=[F(0)]*k;q=F(0)
            if family=='curved':gamma=[F(rng.randrange(1,9),4) for _ in caps];q=F(3,4)
            model=Model.make(caps,weights,gamma,ceilings,r,q);a=[F(i,N-1) for i in range(N)]
            standard=F(1+(rep%4),200);fees=[standard]*N
            if family=='exceptions':
                for i in rng.sample(range(N),2):fees[i]=standard+F(rng.randrange(1,6),100)
            B=model.cap_total*F((rep%3)+1,4);spec=spec_for(model,a,fees,B,m);eps=F(1,(20,100,500)[(rep//3)%3])
            d,a,fees,B,m=normalize(spec)
            meta=dict(k=k,N=N,m=m,q_b=len(set(caps)),joint_types=len(set(zip(caps,d.reward_r,d.reward_q))),exceptions=2 if family=='exceptions' else 0,
                weight_denominator_bits=max(w.denominator.bit_length() for w in weights),promise_fraction=B/d.cap_total,deficit=d.cap_total-B,
                epsilon=eps,grid_Q=int((d.cap_total-B)*(max(d.reward_r)+max(gamma))*m/eps)+1)
            for bi,budget in enumerate(BUDGETS):
                out.append(dict(id=f'{family}-{rep:02d}-b{bi}',specification_id=f'{family}-{rep:02d}',family=family,seed=600927+rep,
                    spec=spec,epsilon=eps,metadata=meta,total_seconds=budget,optimization_cutoff_seconds=budget*.6,
                    methods=METHODS+(() if family=='curved' else ('tariff',))))
    return out

def sources():
    files=[R/'code'/x for x in ('study60.py','worker60.py','tariff60.py','check_tariff60.py')]+list(OLD.glob('*.py'))
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}

def freeze():
    cs=cases();payload=encode(dict(schema='NDU-R60-prospective-study-v1',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_hashes=sources(),cases=cs,distinct_specifications=len({digest(c['spec']) for c in cs}),declared_runs=sum(len(c['methods']) for c in cs),
        protocol=dict(budgets=BUDGETS,optimization_fraction=.6,sequential=True,scope='model-derived stress study, not operational observations',
                      randomization='same seed pairs across tariff/curvature interventions; requests are dependent',include_startup_serialization_checking=True)))
    p=R/'results/STUDY_FREEZE.json'
    if p.exists():
        old=json.loads(p.read_text());assert old['source_hashes']==payload['source_hashes'] and old['cases']==payload['cases'],'Do not overwrite a frozen study';return
    (R/'results/inputs').mkdir(parents=True,exist_ok=True);(R/'results/records').mkdir(exist_ok=True)
    for c in cs:write(R/'results/inputs'/f"{c['id']}.json",c)
    write(p,payload);print('FROZEN',payload['distinct_specifications'],len(cs),payload['declared_runs'],flush=True)

def run():
    freeze();f=json.loads((R/'results/STUDY_FREEZE.json').read_text());order=[]
    for c in f['cases']:
        methods=list(c['methods']);random.Random(c['seed']+int(c['total_seconds']*1000)).shuffle(methods)
        order.extend((c,method) for method in methods)
    for i,(c,method) in enumerate(order):
        dest=R/'results/records'/f"{c['id']}--{method}.json"
        if dest.exists() and json.loads(dest.read_text()).get('parent_finished'):continue
        st=time.perf_counter();proc=subprocess.Popen([sys.executable,str(R/'code/worker60.py'),str(R/'results/inputs'/f"{c['id']}.json"),method,str(dest)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
        timeout=False
        try:output=proc.communicate(timeout=c['total_seconds'])[0]
        except subprocess.TimeoutExpired:timeout=True;proc.kill();output=proc.communicate()[0]
        elapsed=time.perf_counter()-st;dest.with_suffix('.log').write_text(output)
        rec=json.loads(dest.read_text()) if dest.exists() else dict(id=c['id'],method=method,instance_sha256=digest(c['spec']),status='NO_OUTPUT')
        rec.update(parent_finished=True,parent_seconds=elapsed,parent_timeout=timeout,parent_returncode=proc.returncode,within_total_budget=not timeout and elapsed<=c['total_seconds'])
        rec['accepted_rational_interval']=rec.get('verification_status')=='PASS' and rec['within_total_budget'] and rec.get('certificate_schema')!='NDU-R59-SCIP-numerical-v1'
        rec['rational_target_met']=bool(rec['accepted_rational_interval'] and F(rec['upper'])-F(rec['lower'])<=F(c['epsilon']))
        rec['numerical_target_met']=bool(method=='scip' and rec['within_total_budget'] and rec.get('verification_status')=='PASS_LOWER_ONLY' and rec.get('numerical_bound_consistent',False) and rec.get('numerical_absolute_gap') is not None and rec['numerical_absolute_gap']<=float(F(c['epsilon']))+1e-8)
        write(dest,rec)
        print(f"{i+1}/{len(order)}",c['id'],method,rec['status'],rec.get('verification_status'),round(elapsed,3),flush=True)
    write(R/'results/ENVIRONMENT.json',dict(python=sys.version,platform=platform.platform(),processor=platform.processor(),workflow_run=os.environ.get('GITHUB_RUN_ID'),execution_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip() if (ROOT/'.git').exists() else None,pip=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines()))
    tables()

def rows():
    f=json.loads((R/'results/STUDY_FREEZE.json').read_text());cs={c['id']:c for c in f['cases']}
    return [dict(json.loads(p.read_text()),case=cs[json.loads(p.read_text())['id']]) for p in sorted((R/'results/records').glob('*.json'))]

def quantiles(values):
    v=sorted(values)
    if not v:return None
    def q(p):
        x=(len(v)-1)*p;i=int(x);return v[i]*(1-(x-i))+v[min(i+1,len(v)-1)]*(x-i)
    return dict(n=len(v),p50=q(.5),p90=q(.9),p95=q(.95),maximum=max(v))

def tables():
    rs=rows();f=json.loads((R/'results/STUDY_FREEZE.json').read_text());assert len(rs)==f['declared_runs'] and all(r['parent_finished'] for r in rs)
    groups=[]
    for family in ('standard','exceptions','curved'):
        for budget in BUDGETS:
            for method in METHODS+('tariff',):
                ss=[r for r in rs if r['case']['family']==family and r['case']['total_seconds']==budget and r['method']==method]
                if not ss:continue
                row=dict(family=family,budget=budget,method=method,n=len(ss),rationally_certified=sum(r['rational_target_met'] for r in ss),numerically_bounded=sum(r['numerical_target_met'] for r in ss),timeouts=sum(r['parent_timeout'] for r in ss),errors=sum(r['status']=='ERROR' for r in ss),state_limits=sum(r['status']=='STATE_LIMIT' for r in ss),checks=sum(r.get('verification_status') in ('PASS','PASS_LOWER_ONLY') and r['within_total_budget'] for r in ss))
                for key in ('parent_seconds','optimization_seconds','serialization_seconds','verification_seconds','proof_bytes','compressed_proof_bytes','peak_rss_kib'):
                    row[key]=quantiles([r[key] for r in ss if isinstance(r.get(key),(float,int))])
                groups.append(row)
    summary=dict(schema='NDU-R60-study-summary-v1',status='COMPLETE_RECORD_SET',distinct_specifications=f['distinct_specifications'],budget_tagged_cases=len(f['cases']),method_requests=len(rs),groups=groups,
        all_request_seconds=quantiles([r['parent_seconds'] for r in rs]),maximum_proof_bytes=max((r.get('proof_bytes',0) for r in rs),default=0),maximum_compressed_proof_bytes=max((r.get('compressed_proof_bytes',0) for r in rs),default=0),failures_preserved=True)
    write(R/'results/SUMMARY.json',summary)
    with (R/'results/ALL_RUNS.csv').open('w',newline='') as h:
        keys=['id','specification_id','family','total_seconds','method','k','N','m','q_b','joint_types','exceptions','weight_denominator_bits','grid_Q','epsilon','status','verification_status','rational_target_met','numerical_target_met','parent_timeout','parent_seconds','optimization_seconds','serialization_seconds','verification_seconds','proof_bytes','compressed_proof_bytes','lower','upper','numerical_upper','max_depth']
        w=csv.DictWriter(h,fieldnames=keys);w.writeheader()
        for r in rs:
            flat={**r,**r['case'],**r['case']['metadata']};w.writerow({k:flat.get(k,'') for k in keys})
    # Primary panels separate evidence semantics, with explicit denominators.
    tex=''
    for numerical in (False,True):
        methods=('scip',) if numerical else ('price','tariff','deficit','enumeration')
        caption='Numerical-bound target attainment; independently checked lower policies only' if numerical else 'Rationally certified target attainment by family and total allowance'
        tex+=r'\begin{table}[p]\centering\caption{'+caption+r'}\label{tab:newnumerical60}'+'\n' if numerical else r'\begin{table}[p]\centering\caption{'+caption+r'}\label{tab:newrational60}'+'\n'
        tex+=r'\begin{tabular}{llrrr}\toprule Family & Method & 0.5 seconds & 1.5 seconds & 3 seconds\\\midrule'+'\n'
        for family in ('standard','exceptions','curved'):
            for method in methods:
                cells=[]
                for budget in BUDGETS:
                    row=next((x for x in groups if x['family']==family and x['method']==method and x['budget']==budget),None)
                    cells.append('--' if row is None else str(row['numerically_bounded' if numerical else 'rationally_certified'])+'/'+str(row['n']))
                tex+=family.capitalize()+' & '+('SCIP' if method=='scip' else method.capitalize())+' & '+' & '.join(cells)+r'\\'+'\n'
        tex+=r'\bottomrule\end{tabular}\par\smallskip\begin{minipage}{\textwidth}\small Each denominator counts requests, not independent observations. Thirty specifications per family recur across budgets. Standard and exceptions have common linear rewards and free service; curved has quadratic rewards and positive service costs. Tariff is inapplicable, not failed, on curved instances. The numerical panel uses SCIP bounds with a reporting tolerance of $10^{-8}$; it is not a rational upper certificate.\end{minipage}\end{table}'+'\n'
    (R/'generated/new_tables.tex').write_text(tex)
    text=f"The prospectively frozen study has {f['distinct_specifications']} distinct input hashes, {len(f['cases'])} budget-tagged cases and {len(rs)} method requests. Tables~\\ref{{tab:newrational60}} and~\\ref{{tab:newnumerical60}} separate rational certification from numerical-bound evidence. The maximum uncompressed and compressed proof sizes are {summary['maximum_proof_bytes']:,} and {summary['maximum_compressed_proof_bytes']:,} bytes. All request times have median {summary['all_request_seconds']['p50']:.3f} seconds and 95th percentile {summary['all_request_seconds']['p95']:.3f} seconds, including deadlines. "
    for family in ('standard','exceptions','curved'):
        vals=[x for x in groups if x['family']==family and x['budget']==3]
        text+=family.capitalize()+': '+', '.join(('SCIP' if x['method']=='scip' else x['method'])+f" {x['numerically_bounded'] if x['method']=='scip' else x['rationally_certified']}/{x['n']}" for x in vals)+' targets at three seconds. '
    (R/'generated/new_outcomes.tex').write_text(text+'\n')
    # One standalone curve per evidence class; no combined rational/numerical success line.
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for numerical in (False,True):
        fig,ax=plt.subplots(figsize=(6.2,3.3))
        for method in (('scip',) if numerical else ('price','tariff','deficit','enumeration')):
            yy=[]
            for budget in BUDGETS:
                ss=[x for x in groups if x['method']==method and x['budget']==budget];yy.append(sum(x['numerically_bounded'] if numerical else x['rationally_certified'] for x in ss)/sum(x['n'] for x in ss))
            ax.plot(BUDGETS,yy,marker='o',label=method.upper() if method=='scip' else method.capitalize())
        ax.set(xlabel='Total end-to-end allowance (seconds)',ylabel='Fraction of eligible requests attaining target',ylim=(0,1.05));ax.legend();fig.tight_layout();fig.savefig(R/'generated'/('numerical_attainment.pdf' if numerical else 'rational_attainment.pdf'));plt.close(fig)
    print('COMPLETE',len(rs),flush=True)

def verify():
    f=json.loads((R/'results/STUDY_FREEZE.json').read_text());assert f['source_hashes']==sources();rs=rows();assert len(rs)==f['declared_runs'];assert len({(r['id'],r['method']) for r in rs})==len(rs)
    for r in rs:
        assert r['parent_finished'] and r['instance_sha256']==digest(r['case']['spec'])
        if r.get('certificate'):
            p=R/'results'/r['certificate'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['certificate_sha256']
            if r.get('verification_status') not in ('PASS','PASS_LOWER_ONLY'):continue
            cert=json.loads(gzip.decompress(p.read_bytes()));schema=cert['schema']
            if schema=='NDU-R59-SCIP-numerical-v1':
                from check_price import check_policy
                assert check_policy(r['case']['spec'],cert['policy'])==F(r['lower'])
            else:
                if schema=='NDU-R60-tariff-frontier-v1':from check_tariff60 import verify as check
                elif schema=='NDU-deficit-v1-hex':from check_deficit import verify as check
                elif schema=='NDU-enumeration-v1-hex':from check_enumeration import verify as check
                else:from check_price import verify as check
                check(cert,digest(r['case']['spec']))
        if r['rational_target_met']:assert r['accepted_rational_interval'] and F(r['upper'])-F(r['lower'])<=F(r['case']['epsilon'])
    print('READ-ONLY VERIFIED',len(rs),flush=True)
if __name__=='__main__':
    for c in sys.argv[1:]:{'freeze':freeze,'run':run,'tables':tables,'verify':verify}[c]()
