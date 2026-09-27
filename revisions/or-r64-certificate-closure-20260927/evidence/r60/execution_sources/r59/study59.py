"""Frozen, sequential, process-isolated R59 study. No timing record is overwritten.
Commands: freeze, run, tables, verify. Linux deadlines include setup and checking.
"""
from __future__ import annotations
from pathlib import Path
import datetime, gzip, hashlib, json, math, os, platform, random, statistics, subprocess, sys, time
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];OLD=ROOT/'revisions/or-r58-structural-referee-20260926/code'
sys.path.insert(0,str(OLD))
from rational import F,encode,digest,write
from price_path import Model,spec_for,normalize
from structural59 import grouped_sum_model
METHODS=('price','deficit','enumeration','scip')
CELLS=[('base',24,17,4,F(1,100)),('catalog33',24,33,4,F(1,100)),('catalog65',24,65,4,F(1,100)),('histories96',96,17,4,F(1,100)),('budget2',24,17,2,F(1,100)),('budget8',24,17,8,F(1,100)),('accuracy20',24,17,4,F(1,20)),('accuracy500',24,17,4,F(1,500))]
TOTAL=3.0;OPT=1.8

def cases():
    out=[]
    for cell,k,N,m,eps in CELLS:
        for rep in range(8):
            rng=random.Random(590927+rep)
            caps=[F(rng.randrange(16,61),64) for _ in range(k)]
            w=[rng.randrange(1,17) for _ in range(k)];weights=[F(v,sum(w)) for v in w]
            ceilings=[min(F(1),b+F(rng.randrange(0,9),64)) for b in caps]
            gam=[F(rng.randrange(0,13),4) for _ in range(k)]
            rr=[F(rng.randrange(8,17),8) for _ in range(k)];qq=[F(rng.randrange(0,8),8) for _ in range(k)]
            d=Model.make(caps,weights,gam,ceilings,rr,qq)
            a=[F(i,N-1) for i in range(N)];rho=[F(0)]+[F(rng.randrange(0,9),400) for _ in a[1:]]
            B=d.cap_total*F((rep%3)+1,4)
            out.append(dict(id=f'{cell}-{rep}',family=cell,seed=590927+rep,spec=spec_for(d,a,rho,B,m),epsilon=eps))
    for g in (2,3,4,5):
        for rep in range(2):
            rng=random.Random(595000+g*10+rep)
            groups=[sorted(rng.sample(range(1,81),3)) for _ in range(g)]
            W=min(sum(map(max,groups)),sum(rng.choice(v) for v in groups)+(1 if rep else 0))
            spec,meta=grouped_sum_model(groups,W)
            from itertools import product
            # Exact structured oracle: keep only the largest installed option per group,
            # then add all free baselines within 2g+1 slots; gross value cannot fall.
            bestdist=min(abs(sum(v)-W) for v in product(*[[0]+v for v in groups]))
            oracle=meta['zeta']-F(bestdist,2*meta['K'])
            out.append(dict(id=f'group{g}-{rep}',family='group-sum',seed=595000+g*10+rep,spec=spec,epsilon=F(0),groups=groups,target=W,structured_exact_value=oracle))
    for c in out:
        d,a,rho,B,m=normalize(c['spec']);eps=c['epsilon'];K=(max(d.reward_r)+max(d.gamma))/2;D=math.lcm(*[x.denominator for x in list(d.weights)+list(d.caps)+list(a)+[B]])
        c['metadata']=dict(k=len(d.caps),N=len(a),m=m,q_b=len(set(d.caps)),joint_types=len(set(zip(d.caps,d.reward_r,d.reward_q))),min_weight=min(d.weights),max_weight=max(d.weights),weight_denominator_bits=max(x.denominator.bit_length() for x in d.weights),promise_fraction=B/d.cap_total if d.cap_total else F(0),deficit=d.cap_total-B,centered_K=K,grid_Q=int((d.cap_total-B)*2*K*m/eps)+1 if eps else None,lattice_D=str(D),lattice_D_bits=D.bit_length())
        c.update(total_seconds=TOTAL,optimization_cutoff_seconds=OPT)
    return out

def sources():
    paths=[R/'code'/n for n in ('study59.py','worker59.py','structural59.py','feasibility59.py')]+list(OLD.glob('*.py'))
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

def freeze():
    dest=R/'results/STUDY_FREEZE.json';cs=cases();records=R/'results/records'
    payload=encode(dict(schema='NDU-R59-study-freeze-v1',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_hashes=sources(),cases=cs,methods=METHODS,declared_runs=len(cs)*len(METHODS),protocol=dict(total_seconds=TOTAL,optimization_cutoff_seconds=OPT,sequential=True,include_setup_serialization_checking=True,phase_memory='process high-water RSS, not incremental allocation',scope='deterministic engineering panel; not field data or independent confirmatory sample',retained_r58_timings='not rerun or relabeled')))
    if dest.exists():
        old=json.loads(dest.read_text());assert old['source_hashes']==payload['source_hashes'] and old['cases']==payload['cases'],'Frozen inputs/source changed: use a separately named study, do not overwrite evidence';return
    (R/'results/inputs').mkdir(parents=True,exist_ok=True);records.mkdir(parents=True,exist_ok=True)
    for c in cs:write(R/'results/inputs'/f"{c['id']}.json",c)
    write(dest,payload);print('FROZEN',len(cs),len(cs)*len(METHODS),flush=True)

def run():
    freeze();f=json.loads((R/'results/STUDY_FREEZE.json').read_text());order=[]
    for i,c in enumerate(f['cases']):
        methods=list(METHODS);random.Random(c['seed']+123).shuffle(methods)
        for method in methods:order.append((c,method))
    for i,(c,method) in enumerate(order):
        dest=R/'results/records'/f"{c['id']}--{method}.json"
        if dest.exists() and json.loads(dest.read_text()).get('parent_finished'):continue
        case=R/'results/inputs'/f"{c['id']}.json";log=dest.with_suffix('.log');start=time.perf_counter()
        proc=subprocess.Popen([sys.executable,str(R/'code/worker59.py'),str(case),method,str(dest)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
        timeout=False
        try:stdout=proc.communicate(timeout=c['total_seconds'])[0]
        except subprocess.TimeoutExpired:
            timeout=True;proc.kill();stdout=proc.communicate()[0]
        elapsed=time.perf_counter()-start;log.write_text(stdout)
        rec=json.loads(dest.read_text()) if dest.exists() else dict(id=c['id'],method=method,instance_sha256=digest(c['spec']),status='NO_OUTPUT')
        rec.update(parent_finished=True,parent_seconds=elapsed,parent_timeout=timeout,parent_returncode=proc.returncode)
        rec['within_total_budget']=not timeout and elapsed<=c['total_seconds']
        rec['accepted_rational_interval']=rec.get('verification_status')=='PASS' and rec['within_total_budget'] and rec.get('certificate_schema') not in (None,'NDU-R59-SCIP-numerical-v1')
        rec['rational_target_met']=bool(rec['accepted_rational_interval'] and F(rec['upper'])-F(rec['lower'])<=F(c['epsilon']))
        rec['numerical_target_met']=bool(method=='scip' and rec['within_total_budget'] and rec.get('verification_status')=='PASS_LOWER_ONLY' and rec.get('numerical_bound_consistent',False) and rec.get('numerical_absolute_gap') is not None and rec['numerical_absolute_gap']<=float(F(c['epsilon']))+1e-8)
        write(dest,rec);print(f"{i+1}/{len(order)}",c['id'],method,rec['status'],rec.get('verification_status'),round(elapsed,3),flush=True)
    write(R/'results/ENVIRONMENT.json',dict(python=sys.version,platform=platform.platform(),processor=platform.processor(),run_id=os.environ.get('GITHUB_RUN_ID'),source_commit=os.environ.get('GITHUB_SHA'),pip=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines()))
    tables()

def rows():
    f=json.loads((R/'results/STUDY_FREEZE.json').read_text());cs={c['id']:c for c in f['cases']};rs=[]
    for p in sorted((R/'results/records').glob('*.json')):
        r=json.loads(p.read_text());r['case']=cs[r['id']];rs.append(r)
    return rs

def tables():
    rs=rows();f=json.loads((R/'results/STUDY_FREEZE.json').read_text());assert len(rs)==f['declared_runs'] and all(r['parent_finished'] for r in rs)
    aggregate=[]
    for method in METHODS:
        ss=[r for r in rs if r['method']==method];done=[r for r in ss if r.get('verification_status') in ('PASS','PASS_LOWER_ONLY') and r['within_total_budget']]
        med=lambda key:statistics.median([r[key] for r in ss if isinstance(r.get(key),(float,int))]) if any(isinstance(r.get(key),(float,int)) for r in ss) else None
        aggregate.append(dict(method=method,runs=len(ss),rational_targets=sum(r['rational_target_met'] for r in ss),numerical_targets=sum(r['numerical_target_met'] for r in ss),checked_outputs=len(done),total_median=med('parent_seconds'),optimization_median=med('optimization_seconds'),checking_median=med('verification_seconds'),peak_rss_median_mib=(med('peak_rss_kib') or 0)/1024,checker_peak_rss_median_mib=(med('checker_peak_rss_kib') or 0)/1024,timeouts=sum(r['parent_timeout'] for r in ss),states=sum(r['status']=='STATE_LIMIT' for r in ss),errors=sum(r['status']=='ERROR' for r in ss)))
    summary=dict(schema='NDU-R59-study-summary-v1',declared_runs=f['declared_runs'],actual_runs=len(rs),aggregate=aggregate,source_hashes=f['source_hashes'],max_price_depth=max([r.get('max_depth',0) for r in rs if r['method']=='price'],default=0),price_cases_branched=sum(r.get('max_depth',0)>0 for r in rs if r['method']=='price'),status='COMPLETE_RECORD_SET')
    write(R/'results/SUMMARY.json',summary)
    tex=r'''\begin{table}[p]\centering\caption{Matched three-second end-to-end panel (72 instances per method)}\label{tab:study59}
\begin{tabular}{lrrrrr}\toprule
Method & Checked & Rational target & Numerical target & Time (s) & RSS (MiB)\\\midrule
'''
    for a in aggregate:
        tex+=f"{a['method'].capitalize()} & {a['checked_outputs']} & {a['rational_targets']} & {a['numerical_targets']} & {a['total_median']:.3f} & {a['peak_rss_median_mib']:.1f}"+r'\\'+'\n'
    tex+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{\textwidth}\small Checked counts completed independent checks within the total allowance. SCIP checks only its rationally reconstructed feasible policy; its global bound remains numerical. Numerical targets use the same additive target with a stated $10^{-8}$ reporting tolerance, and are not exact proofs. Time includes process startup, construction, optimization, serialization and checking. RSS is a process high-water mark. No unfinished output counts as a certified target.\end{minipage}\end{table}
'''
    tex+=r'''\begin{table}[p]\centering\caption{Independent-checking cost and retained resource limits}\label{tab:checking59}
\begin{tabular}{lrrrrr}\toprule
Method & Check time (s) & Check RSS (MiB) & Deadline & State limit & Error\\\midrule
'''
    for a in aggregate:
        ct='--' if a['checking_median'] is None else f"{a['checking_median']:.4f}"
        tex+=f"{a['method'].capitalize()} & {ct} & {a['checker_peak_rss_median_mib']:.1f} & {a['timeouts']} & {a['states']} & {a['errors']}"+r'\\'+'\n'
    tex+=r'''\bottomrule\end{tabular}\par\smallskip\begin{minipage}{\textwidth}\small Checking medians are conditional on a recorded completed checking phase, not on all requests. The checker runs in the same process; its RSS includes inherited optimizer allocations and is a conservative end-to-end memory measure, not incremental checker memory. Deadline includes killed jobs; internal optimization interruption may instead return a checked fallback interval.\end{minipage}\end{table}'''
    (R/'generated/study_tables.tex').write_text(tex)
    text=f"The new panel contains {len(rs)} method requests. Price search branches in {summary['price_cases_branched']} of 72 cases, with maximum recorded depth {summary['max_price_depth']}. Table~\\ref{{tab:study59}} reports completed outputs and target attainment rather than optimizer status alone. Table~\\ref{{tab:checking59}} retains end-to-end deadlines, grid rejections, and checking costs. "
    text+='The heterogeneous grid and binary-encoded challenge cases intentionally expose numerical-state and proof-cost limits. A common time allowance does not turn a numerical global bound into a rational certificate. These results identify method-dependent tradeoffs on this generator; they do not establish universal solver superiority or field performance.\n'
    (R/'generated/outcomes.tex').write_text(text)
    # Complete instance-by-method observations, not only medians, are in CSV.
    import csv
    with (R/'results/ALL_RUNS.csv').open('w',newline='') as h:
        keys=['id','method','family','k','N','m','q_b','joint_types','epsilon','status','verification_status','parent_seconds','within_total_budget','rational_target_met','numerical_target_met','lower','upper','numerical_upper','numerical_absolute_gap','optimization_seconds','verification_seconds','peak_rss_kib','checker_peak_rss_kib','proof_bytes','max_depth']
        w=csv.DictWriter(h,fieldnames=keys);w.writeheader()
        for r in rs:
            flat={**r,**r['case']['metadata'],'family':r['case']['family'],'epsilon':r['case']['epsilon']};w.writerow({k:flat.get(k,'') for k in keys})
    print(json.dumps(summary,indent=2))

def verify():
    f=json.loads((R/'results/STUDY_FREEZE.json').read_text());assert f['source_hashes']==sources(),'Execution source differs from freeze'
    rs=rows();assert len(rs)==f['declared_runs'];assert len({(r['id'],r['method']) for r in rs})==len(rs)
    for r in rs:
        assert r['parent_finished'] and r['instance_sha256']==digest(r['case']['spec'])
        if r.get('certificate'):
            p=R/'results'/r['certificate'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['certificate_sha256']
        if r['rational_target_met']:assert r['accepted_rational_interval'] and F(r['upper'])-F(r['lower'])<=F(r['case']['epsilon'])
    print('R59 frozen source/inputs/records/certificate bytes verified:',len(rs))
if __name__=='__main__':
    for command in sys.argv[1:]:{'freeze':freeze,'run':run,'tables':tables,'verify':verify}[command]()
