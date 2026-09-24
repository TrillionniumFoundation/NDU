"""Frozen deterministic holdout design; all outcomes including limits are kept."""
from fractions import Fraction as F
from pathlib import Path
from dataclasses import asdict
import time,json,random,hashlib,gzip,platform,sys
from box_solver import *
from check_certificate import check
from compression import ideal_targets,frontier
import target_net_reference
from mip_baseline import direct_milp
R=Path(__file__).resolve().parents[1]

def fixture(seed,k,n,charged,replicas=1):
    rng=random.Random(seed);caps=tuple(F(rng.randrange(3,19),20) for _ in range(k));weights0=[rng.randrange(1,8) for _ in caps]
    weights=tuple(F(z,sum(weights0)) for z in weights0);gam=tuple(F(rng.choice([1,2,4,8])) for _ in caps)
    tau=tuple(min(F(1),b+F(rng.choice([0,2,4]),20)) for b in caps)
    a=tuple(F(i,n-1) for i in range(n));rho=tuple(F(rng.randrange(0,9),100) if charged else F(0) for _ in a)
    if replicas>1:
        caps=tuple(x for x in caps for _ in range(replicas));weights=tuple(x/replicas for x in weights for _ in range(replicas));gam=tuple(x for x in gam for _ in range(replicas));tau=tuple(x for x in tau for _ in range(replicas))
    d=Instance.make(caps,weights,gam,tau);B=d.cap_total*F(17 if seed%2 else 13,20)
    return d,a,rho,B

def jensen(d,a,rho,B):
    t=ideal_targets(d,B)
    return sum(w*d.reward(z) for w,z in zip(d.weights,t))-min(r for x,r in zip(a,rho) if x<=min(B,min(d.caps)))

def greedy(d,a,rho,B,m):
    cmap=dict(zip(a,rho));best=max((fixed_allocate(d,(x,),B,cmap) for x in a if x<=min(B,min(d.caps))),key=lambda p:p['value'])
    for s in range(2,m+1):
        cand=[fixed_allocate(d,tuple(sorted(best['book']+(x,))),B,cmap) for x in a if x not in best['book']]
        nxt=max(cand,key=lambda p:p['value'])
        if nxt['value']<=best['value']:break
        best=nxt
    return best

def plan():
    specs=[]
    for k in (2,4,8):
        for n in (9,17):
            for charged in (False,True):
                for repeat in (0,1):
                    specs.append(dict(id=f'h{k}-{n}-{int(charged)}-{repeat}',seed=460100+len(specs),k=k,n=n,charged=charged,m=2+repeat,eps='1/1000',nodes=301,seconds=8))
    for k,n,rep in [(4,33,32),(4,33,64),(8,33,16),(16,33,1)]:
        for charged in (False,True):
            specs.append(dict(id=f's{k}-{n}-{rep}-{int(charged)}',seed=460700+k+int(charged),k=k,n=n,charged=charged,replicas=rep,m=3,eps='1/1000',nodes=101,seconds=8))
    grids=[dict(seed=461000+k,k=k,n=5,m=2,eps=eps,profiles=1000) for k in (2,3,4,5) for eps in ('1/10','1/100','1/1000')]
    mipids=[s['id'] for s in specs if s['n']==9 and s['k']<=4]
    return dict(schema='r46-frozen-holdout-v1',seed_policy='Independent fixed seeds; no deletion, retuning, or replacement after outcomes.',
       solver=dict(price_steps=8,axis='largest weighted side except dependent largest-weight type',warm_start='one ideal-target conditional book',epsilon_scale='absolute normalized utility'),
       joint_specs=specs,grid_specs=grids,mip_ids=mipids,mip_seconds_each=3,mip_segments=64,
       timing='Wall clock; exact solver limits are checked after a complete node. Net limited by profiles; no net accuracy on interruption.',
       comparisons='Exact all-book reference for N=9,k<=4; greedy and ideal-target conditional book on all holdout types. Numerical MIP tangent/secant each 3s. No heuristic exactness claim.',
       dataset_scope='Synthetic rational inputs, including explicitly constructed repeated-type cases; no application calibration.')

def run():
    protocol=plan();payload=json.dumps(protocol,sort_keys=True,indent=2)+'\n';p=R/'PROTOCOL.json'
    if p.exists() and p.read_text()!=payload:raise RuntimeError('Frozen protocol differs')
    p.write_text(payload)
    manifest=dict(protocol_sha256=hashlib.sha256(payload.encode()).hexdigest(),python=sys.version,platform=platform.platform(),code_sha256={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in Path(__file__).parent.glob('*.py')})
    (R/'results'/'execution_environment.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (R/'results'/'certificates').mkdir(exist_ok=True);rows=json.loads((R/'results'/'joint.json').read_text()) if (R/'results'/'joint.json').exists() else []
    for spec in protocol['joint_specs']:
        if any(row['id']==spec['id'] for row in rows):continue
        d,a,rho,B=fixture(spec['seed'],spec['k'],spec['n'],spec['charged'],spec.get('replicas',1));small,_=aggregate(d,a)
        start=time.perf_counter();cond=frontier(small,a,rho,ideal_targets(small,B),spec['m'])['at_most'][-1];condsec=time.perf_counter()-start
        start=time.perf_counter();gr=greedy(small,a,rho,B,spec['m']);grsec=time.perf_counter()-start
        ans=solve(d,a,rho,B,spec['m'],F(spec['eps']),max_nodes=spec['nodes'],seconds_limit=spec['seconds'],price_steps=8)
        record=encode(ans);start=time.perf_counter();validation=check(record);checktime=time.perf_counter()-start
        blob=gzip.compress(json.dumps(record,sort_keys=True,separators=(',',':')).encode(),mtime=0)
        fname=spec['id']+'.json.gz';(R/'results'/'certificates'/fname).write_bytes(blob)
        row=dict(**spec,raw_k=len(d.caps),types=ans['types'],promise=B,status=ans['status'],lower=ans['lower_bound'],upper=ans['upper_bound'],gap=ans['gap'],epsilon_guarantee=ans['epsilon_guarantee'],runtime=ans['seconds'],evaluated_nodes=ans['evaluated_nodes'],oracle_calls=ans['oracle_calls'],distinct_books=ans['distinct_books'],jensen_upper=jensen(d,a,rho,B),root_price_upper=ans['nodes'][0]['bound'],conditional_value=cond['value'],conditional_seconds=condsec,greedy_value=gr['value'],greedy_seconds=grsec,checker=validation,checker_seconds=checktime,certificate=f'certificates/{fname}',certificate_sha256=hashlib.sha256(blob).hexdigest(),
           objective_scale=d.r+max(d.gamma)/2+sum(sorted(rho,reverse=True)[:spec['m']]))
        if spec['n']==9 and spec['k']<=4:
            start=time.perf_counter();ref=exhaustive_joint(small,a,rho,B,spec['m']);row.update(exact_value=ref['value'],exact_seconds=time.perf_counter()-start,absolute_loss=ref['value']-ans['lower_bound'])
            assert ans['lower_bound']<=ref['value']<=ans['upper_bound']
        rows.append(encode(row));(R/'results'/'joint.json').write_text(json.dumps(rows,indent=2)+'\n')
        print(spec['id'],ans['status'],ans['evaluated_nodes'],round(float(ans['gap']),7),round(ans['seconds'],3),flush=True)
    grids=json.loads((R/'results'/'grid.json').read_text()) if (R/'results'/'grid.json').exists() else []
    for spec in protocol['grid_specs']:
        if any(row['k']==spec['k'] and row['eps']==spec['eps'] for row in grids):continue
        d,a,rho,B=fixture(spec['seed'],spec['k'],spec['n'],True)
        start=time.perf_counter();net=target_net_reference.solve(d,a,rho,B,spec['m'],F(spec['eps']),max_profiles=spec['profiles']);netsecs=time.perf_counter()-start
        adaptive=solve(d,a,rho,B,spec['m'],F(spec['eps']),max_nodes=1001,seconds_limit=8,price_steps=8)
        ref=exhaustive_joint(d,a,rho,B,spec['m']);check(encode(adaptive))
        truth=ref['value'];grid=dict(**spec,net_status=net['status'],net_profiles=net['evaluated_profiles'],net_seconds=netsecs,net_epsilon=net['epsilon_guarantee'],net_value=net['policy']['value'],net_loss=truth-net['policy']['value'],adaptive_status=adaptive['status'],adaptive_nodes=adaptive['evaluated_nodes'],adaptive_seconds=adaptive['seconds'],adaptive_gap=adaptive['gap'],adaptive_loss=truth-adaptive['lower_bound'],exact_value=truth,objective_scale=d.r+max(d.gamma)/2+sum(sorted(rho,reverse=True)[:spec['m']]))
        if net['status']=='COMPLETE':assert truth-net['policy']['value']<=F(spec['eps'])
        grids.append(encode(grid));(R/'results'/'grid.json').write_text(json.dumps(grids,indent=2)+'\n')
        print('grid',spec['k'],spec['eps'],net['status'],net['evaluated_profiles'],adaptive['status'],flush=True)
    mips=json.loads((R/'results'/'mip.json').read_text()) if (R/'results'/'mip.json').exists() else []
    for spec in protocol['joint_specs']:
        if spec['id'] not in protocol['mip_ids'] or any(row['id']==spec['id'] for row in mips):continue
        d,a,rho,B=fixture(spec['seed'],spec['k'],spec['n'],spec['charged']);rowsm={}
        for mode in ('tangent','secant'):
            rowsm[mode]=direct_milp(d,a,rho,B,spec['m'],segments=protocol['mip_segments'],envelope=mode,time_limit=protocol['mip_seconds_each'])
        exact=exhaustive_joint(d,a,rho,B,spec['m'])['value']
        upp=rowsm['tangent'].get('numerical_upper');low=rowsm['secant'].get('value')
        width=None if upp is None or low is None else upp-low
        mips.append(encode(dict(id=spec['id'],exact=exact,tangent=rowsm['tangent'],secant=rowsm['secant'],numerical_bracket_width=width)))
        (R/'results'/'mip.json').write_text(json.dumps(mips,indent=2)+'\n');print('mip',spec['id'],width,flush=True)
    print('BENCHMARK COMPLETE',len(rows),len(grids),len(mips),flush=True)
if __name__=='__main__':run()
