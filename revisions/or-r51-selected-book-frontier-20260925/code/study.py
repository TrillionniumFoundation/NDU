"""Execute the frozen R51 population; save all interruptions and diagnostics."""
from pathlib import Path
from fractions import Fraction as F
from dataclasses import asdict
import sys,json,time,hashlib,gzip,platform,random,runpy,math
from completion import solve,encode,Instance,ROOT,enumerate_joint
from check_completion import check
from pooling import solve as group_solve,eligibility_groups
from check_pooling import check as group_check
from mip_baseline import direct_milp
R=Path(__file__).resolve().parents[1];OLD=ROOT/'revisions/or-r49-dispersion-certificates-20260925'
fixture=runpy.run_path(str(OLD/'code/tests.py'))['fixture']
P=R/'PROTOCOL.json';PROTOCOL=json.loads(P.read_text());HASH=hashlib.sha256(P.read_bytes()).hexdigest()


def init(path):
    if not path.exists():path.write_text(json.dumps(dict(protocol_sha256=HASH,python=sys.version,platform=platform.platform(),cases=[]),indent=2)+'\n')
    raw=json.loads(path.read_text());assert raw['protocol_sha256']==HASH
    return {x['id'] for x in raw['cases']}


def rational_metrics(obj):
    count=nb=db=0
    def scan(x):
        nonlocal count,nb,db
        if isinstance(x,dict):
            for v in x.values():scan(v)
        elif isinstance(x,list):
            for v in x:scan(v)
        elif isinstance(x,str):
            try:q=F(x)
            except (ValueError,ZeroDivisionError):return
            count+=1;nb=max(nb,abs(q.numerator).bit_length());db=max(db,q.denominator.bit_length())
    scan(obj);return dict(rational_entries=count,max_numerator_bits=nb,max_denominator_bits=db)


def save(row,cert,solver='tree'):
    raw=encode(cert);start=time.perf_counter();answer=(check(raw) if solver=='tree' else group_check(raw));elapsed=time.perf_counter()-start
    plain=json.dumps(raw,sort_keys=True,separators=(',',':')).encode();packed=gzip.compress(plain,mtime=0)
    path=R/'results/certificates'/(row['id']+'.json.gz');path.write_bytes(packed)
    D=row.pop('_data');a=row.pop('_a');rho=row.pop('_rho');B=row.pop('_B')
    row.update(model=asdict(D),catalog=a,charges=rho,promise=B,k=len(D.caps),n=len(a),solver=solver,
        E=len(eligibility_groups(D,a)),selected_E=len(eligibility_groups(D,tuple(F(x) for x in raw['policy']['book']))),
        lower_bound=raw['lower_bound'],upper_bound=raw['upper_bound'],gap=raw['gap'],status=raw['status'],
        exact=F(raw['gap'])==0,evaluated_nodes=raw['evaluated_nodes'],seconds=cert['seconds'],check_seconds=elapsed,
        certificate=str(path.relative_to(R)),certificate_sha256=hashlib.sha256(packed).hexdigest(),
        gzip_bytes=len(packed),uncompressed_bytes=len(plain),check_over_search_seconds=elapsed/max(cert['seconds'],1e-12),
        relative_gap=float(F(raw['gap'])/max(abs(F(raw['lower_bound'])),abs(F(raw['upper_bound'])),F(1,1000000))),
        independent_check=answer,**rational_metrics(raw))
    if solver=='tree':
        row.update(active_E=len(eligibility_groups(D,tuple(a[i] for i in cert['active']))),removed=len(cert['screening']['removed']),allocation_calls=cert['allocation_calls'],price_calls=cert['price_calls'])
    data=json.loads((R/'results/study.json').read_text());data['cases'].append(encode(row));(R/'results/study.json').write_text(json.dumps(data,indent=2)+'\n')
    print(row['id'],'E',row['E'],'gap',float(F(row['gap'])),'nodes',row['evaluated_nodes'],'sec',round(row['seconds'],3),flush=True)


def strict(k,n,seed,Bfrac,m):
    rng=random.Random(seed);a=tuple(F(i*i,(n-1)**2) for i in range(n));idx=2*(n-1)//3
    l=a[idx]+(a[idx+1]-a[idx])/5;u=a[idx+1]-(a[idx+1]-a[idx])/5
    caps=tuple(l*(F(1,5)+F(4*(j+1),5*(k+1))) for j in range(k));w=[rng.randint(1,7) for _ in caps]
    tau=tuple(l+(u-l)*F(j+1,k+1) for j in range(k));gam=tuple(F((j%7)**2,5) for j in range(k))
    D=Instance.make(caps,[F(x,sum(w)) for x in w],gam,tau);rho=tuple(F(rng.randint(0,6),100) for x in a)
    return D,a,rho,D.cap_total*F(Bfrac)


def matched(E):
    k,n=16,17;rng=random.Random(PROTOCOL['matched_classes']['seed']);a=tuple(F(i,16) for i in range(17))
    b=tuple(F(4*(j+1),5*(k+1)) for j in range(k));raw=[rng.randint(1,7) for _ in b]
    gam=tuple(F((j%5)**2,4) for j in range(k))
    tau=tuple(a[math.ceil(16*math.ceil((j+1)*E/k)/E)] for j in range(k))
    D=Instance.make(b,[F(x,sum(raw)) for x in raw],gam,tau);rho=tuple(F(rng.randint(0,4),100) for x in a)
    assert len(eligibility_groups(D,a))==E
    return D,a,rho,D.cap_total*F(9,10)


def boundary_base():
    k=8;rng=random.Random(PROTOCOL['near_boundary']['seed']);b=tuple(F(1,5)+F(6*(j+1),25*(k+1)) for j in range(k));raw=[rng.randint(1,5) for _ in b]
    w=tuple(F(x,sum(raw)) for x in raw);gam=tuple(F((j%5)**2,4) for j in range(k));tau=tuple(F(9,20)+F(j+1,10*(k+1)) for j in range(k))
    return Instance.make(b,w,gam,tau)


def run():
    done=init(R/'results/study.json');limit=PROTOCOL['study_seconds_per_search'];oldrows=json.loads((OLD/'results/study.json').read_text())['cases']
    def run_tree(cid,family,D,a,rho,B,m,**kw):
        if cid in done:return
        meta=kw.pop('meta',{});z=solve(D,a,rho,B,m,**kw)
        row=dict(id=cid,family=family,_data=D,_a=a,_rho=rho,_B=B,m=m,settings=kw,**meta)
        save(row,z);done.add(cid)
    for seed in PROTOCOL['stress_seeds']:
        D,a,rho,B=fixture(seed,12,9,False);old=next(r for r in oldrows if r['family']=='stress' and r['seed']==seed and r['epsilon']=='1/1000' and r['node_limit']==127)
        meta={'seed':seed,'historical_r49_gap':old['gap'],'exact_reference':old['exact_reference'],'historical_source_sha256':hashlib.sha256((OLD/'results/study.json').read_bytes()).hexdigest()}
        for steps in PROTOCOL['stress_prices']:
            for nodes in PROTOCOL['stress_nodes']:
                run_tree(f'stress-{seed}-p{steps}-n{nodes}','stress',D,a,rho,B,3,node_limit=nodes,time_limit=limit,price_steps=steps,meta=meta)
        q=PROTOCOL['closure'];run_tree(f'closure-{seed}','closure',D,a,rho,B,3,node_limit=q['stress_node_limit'],price_steps=q['prices'],time_limit=q['seconds'],meta=meta)
    sp=PROTOCOL['strict_prefix'];settings=[(k,n,B,sp['budget']) for k in sp['histories'] for n in sp['catalog_sizes'] for B in sp['promise_fractions']]
    settings += [(k,sp['extra_catalog_size'],'9/10',m) for k in sp['extra_histories'] for m in sp['extra_budgets']]
    for k,n,bfrac,m in settings:
        cid=f'strict-k{k}-n{n}-b{bfrac.replace("/","_")}-m{m}'
        if cid in done:continue
        D,a,rho,B=strict(k,n,sp['seed'],bfrac,m);z=group_solve(D,a,rho,B,m,epsilon=F(0),max_nodes=1,price_steps=0)
        assert z['gap']==0 and z['eligibility_groups']==1 and max(D.ceilings)<a[-1] and len(set(D.ceilings))==k
        save(dict(id=cid,family='strict',_data=D,_a=a,_rho=rho,_B=B,m=m,promise_fraction=bfrac,ceiling_gap=[str(min(D.ceilings)),str(max(D.ceilings))]),z,'one_class');done.add(cid)
    mp=PROTOCOL['matched_classes']
    for E in mp['classes']:
        D,a,rho,B=matched(E)
        for nodes in mp['nodes']:
            for steps in mp['prices']:
                run_tree(f'matched-E{E}-p{steps}-n{nodes}','matched',D,a,rho,B,mp['budget'],node_limit=nodes,time_limit=limit,price_steps=steps)
    rp=PROTOCOL['refinement'];D=boundary_base();base=tuple(map(F,rp['base_catalog']));ins=tuple(map(F,rp['insertions']));B=D.cap_total*F(9,10)
    for charge in rp['new_charges']:
        for stop in range(len(ins)+1):
            a=tuple(sorted(base+ins[:stop]));rho=tuple(F(1,100) if x in base else F(charge) for x in a)
            for screen in rp['screening']:
                run_tree(f'refine-c{charge.replace("/","_")}-j{stop}-s{int(screen)}','refinement',D,a,rho,B,3,node_limit=10000,time_limit=30,price_steps=2,screen=screen,meta={'insertions':stop,'new_charge':charge})
    bp=PROTOCOL['near_boundary'];baseD=boundary_base();a=tuple(F(i,4) for i in range(5));rho=(F(1,100),)*5;B=baseD.cap_total*F(9,10)
    for eps in bp['epsilon']:
        for above in bp['above_counts']:
            tau=tuple(F(1,2)+(F(eps) if j<above else -F(eps)) for j in range(8));D=Instance.make(baseD.caps,baseD.weights,baseD.gamma,tau)
            run_tree(f'boundary-e{eps.replace("/","_")}-a{above}','boundary',D,a,rho,B,3,node_limit=10000,time_limit=30,price_steps=2,meta={'perturbation':eps,'above_count':above})
    # Matched solver allowance; each MIP envelope has its own separate allowance.
    path=R/'results/mip.json';mdone=init(path);spec=PROTOCOL['mip'];mips=[]
    for seed in PROTOCOL['stress_seeds']:mips.append((f'stress-{seed}',fixture(seed,12,9,False)))
    for E in spec['matched_classes']:mips.append((f'matched-E{E}',matched(E)))
    for cid,(D,a,rho,B) in mips:
        if cid in mdone:continue
        out={}
        for env in spec['envelopes']:
            t=time.perf_counter();z=direct_milp(D,a,rho,B,3,segments=spec['segments'],envelope=env,time_limit=spec['seconds_each']);z['wall_seconds']=time.perf_counter()-t;out[env]=z
        t=time.perf_counter();reference,calls=enumerate_joint(D,a,rho,B,3);etime=time.perf_counter()-t
        for env,z in out.items():
            if z.get('numerical_upper') is not None:assert z['numerical_upper']+1e-6>=float(reference['value']) if env=='tangent' else True
            if z.get('value') is not None:assert z['value']<=float(reference['value'])+1e-6
        row=dict(id=cid,model=asdict(D),catalog=a,charges=rho,promise=B,m=3,envelopes=out,exact_reference=reference['value'],enumeration_seconds=etime,enumeration_calls=calls)
        data=json.loads(path.read_text());data['cases'].append(encode(row));path.write_text(json.dumps(data,indent=2)+'\n');print('MIP',cid,[z['status'] for z in out.values()],flush=True)
    verify()


def verify():
    raw=json.loads((R/'results/study.json').read_text());assert raw['protocol_sha256']==HASH;rows=raw['cases'];ids=[r['id'] for r in rows];assert len(ids)==len(set(ids))
    counts={f:sum(r['family']==f for r in rows) for f in ['stress','closure','strict','matched','refinement','boundary']}
    assert counts=={'stress':72,'closure':6,'strict':20,'matched':48,'refinement':24,'boundary':12},counts
    for r in rows:
        path=R/r['certificate'];assert hashlib.sha256(path.read_bytes()).hexdigest()==r['certificate_sha256'];c=json.loads(gzip.decompress(path.read_bytes()))
        answer=check(c) if r['solver']=='tree' else group_check(c)
        assert all(c[key]==r[key] for key in ['lower_bound','upper_bound','gap','evaluated_nodes'])
        for key in ['model','catalog','charges','promise']:assert c[key]==r[key]
        if r.get('exact_reference') is not None:assert F(r['lower_bound'])<=F(r['exact_reference'])<=F(r['upper_bound'])
    # The insertion certificates prove deletion safe; these comparisons additionally
    # test that high-charge class splitting does not alter the winning value.
    high=[r for r in rows if r['family']=='refinement' and r['new_charge']=='3'];assert len({r['lower_bound'] for r in high})==1 and all(r['exact'] for r in high)
    for above in PROTOCOL['near_boundary']['above_counts']:
        rr=[r for r in rows if r['family']=='boundary' and r['above_count']==above];assert len({r['lower_bound'] for r in rr})==1 and all(r['exact'] for r in rr)
    mip=json.loads((R/'results/mip.json').read_text())['cases'];assert len(mip)==9
    summary=dict(status='PASS',protocol_sha256=HASH,population=counts,certificates=len(rows),exact=sum(r['exact'] for r in rows),open=sum(not r['exact'] for r in rows),closure_exact=sum(r['exact'] for r in rows if r['family']=='closure'),mip_solves=18,
        mip_time_limits=sum(z['status']==1 for r in mip for z in r['envelopes'].values()),max_certificate_bytes=max(r['gzip_bytes'] for r in rows),max_numerator_bits=max(r['max_numerator_bits'] for r in rows),max_denominator_bits=max(r['max_denominator_bits'] for r in rows),
        results_sha256=hashlib.sha256((R/'results/study.json').read_bytes()).hexdigest())
    (R/'results/SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary,flush=True)
if __name__=='__main__':
    if '--verify' in sys.argv:verify()
    else:run()
