#!/usr/bin/env python3
"""R12 crossed, noncentered service-control audit and measured refinement.
No old result is overwritten. All reported policies have exact Fraction audits.
Four frozen R10 training seeds, twelve new instances per graph family; no fitting
or parameter selection uses these test instances. Both pipeline methods use the
same SLSQP objective, constraints, stopping certificates, and audit schedule.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from fractions import Fraction as Q
import sys,json,time,platform,argparse,hashlib
import numpy as np
import scipy
from scipy import sparse
from scipy.optimize import minimize,nnls
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'or-r10-20260921'
sys.path.insert(0,str(OLD))
from nonlinear_control import Problem
DEN=10**10


def exact_gradient(pr,x):
    g=[pr.wq[i]*(pr.pq[i]-2*pr.m*x[i]-4*pr.gamma*x[i]**3) for i in range(pr.N)]
    for n in range(pr.nodes):
        for j in range(pr.d):
            i=n*pr.d+j;par=pr.bar if n==0 else x[pr.pa[n]*pr.d+j]
            t=2*pr.lam*pr.wq[i]*(x[i]-par);g[i]-=t
            if n:g[pr.pa[n]*pr.d+j]+=t
        for j,k,v in pr.edges:
            i=n*pr.d+j;l=n*pr.d+k;t=2*pr.wn[n]*pr.zeta*v*(x[i]-x[l]);g[i]-=t;g[l]+=t
    return g


def exact_value(pr,x):
    val=Q(0)
    for n in range(pr.nodes):
        for j in range(pr.d):
            i=n*pr.d+j;par=pr.bar if n==0 else x[pr.pa[n]*pr.d+j]
            val+=pr.wq[i]*(pr.pq[i]*x[i]-pr.m*x[i]**2-pr.gamma*x[i]**4-pr.lam*(x[i]-par)**2)
        for j,k,v in pr.edges:val-=pr.wn[n]*pr.zeta*v*(x[n*pr.d+j]-x[n*pr.d+k])**2
    return val


def payments(pr,x):
    p=[sum((pr.wq[n*pr.d+j]*pr.aq[n*pr.d+j]*x[n*pr.d+j] for j in range(pr.d)),Q(0)) for n in range(pr.nodes)]
    for n in range(pr.nodes-1,0,-1):p[pr.pa[n]]+=p[n]
    return p


def prepare(pr,noncentered=False,seed=0):
    pr.test_seed=seed
    pr.massq=sum(pr.wq)
    if noncentered:
        rng=np.random.default_rng(seed+812731)
        # Uncentered rational forcing: no subtraction of a weighted mean.
        mode=seed%6
        if mode==0:latent=[Q(23,20)]*pr.d
        elif mode==1:latent=[Q(-1,5)]+[Q(1,3)]*(pr.d-1)
        else:latent=[Q(int(v),20) for v in rng.integers(1,22,pr.d)]
        shocks=rng.integers(-60,61,pr.N)
        pr.pq=[2*pr.m*latent[i%pr.d]+4*pr.gamma*latent[i%pr.d]**3+Q(int(shocks[i]),100) for i in range(pr.N)]
        pr.p=np.array(list(map(float,pr.pq)))
        def fun(z):
            x=np.tile(z,pr.nodes)
            return -pr.value(x), (pr.grad(x)-pr.w*pr.p).reshape(pr.nodes,pr.d).sum(axis=0)
        t=time.perf_counter()
        res=minimize(fun,np.full(pr.d,.5),jac=True,method='L-BFGS-B',bounds=[(0,1)]*pr.d,
                     options={'ftol':1e-15,'gtol':1e-11,'maxiter':1500,'maxls':40})
        zz=np.clip(res.x,0,1)
        zq=[Q(int(round(v*DEN)),DEN) for v in zz]
        pr.static=np.tile(np.array(list(map(float,zq))),pr.nodes)
        pr.staticq=zq*pr.nodes
        pr.static_setup_seconds=time.perf_counter()-t
        gs=exact_gradient(pr,pr.staticq)
        agg=[sum((gs[n*pr.d+j] for n in range(pr.nodes)),Q(0)) for j in range(pr.d)]
        ww=sum(pr.wn);bd=Q(0)
        for z,g in zip(zq,agg):
            normal=g if (z==1 and g>0) or (z==0 and g<0) else Q(0)
            bd+=(g-normal)**2/(4*pr.m*ww)
        pr.static_gap=bd
    else:
        pr.static=np.full(pr.N,.5);pr.staticq=[Q(1,2)]*pr.N
        pr.static_gap=Q(0);pr.static_setup_seconds=0.
    pr.capq=payments(pr,pr.staticq);pr.cap=np.array(list(map(float,pr.capq)))
    pr.b=pr.cap/pr.row_scale
    pr.gbar=pr.grad(pr.static)/pr.w
    pr.staticvalue=exact_value(pr,pr.staticq)
    pr.constraints={'type':'ineq','fun':lambda x:pr.b-pr.C@x,'jac':lambda x:-pr.C.toarray()}
    return pr


def audit(pr,proposal):
    start=time.perf_counter();xx=np.clip(np.asarray(proposal),0,1)
    x=pr.staticq.copy() if np.array_equal(xx,pr.static) else [Q(int(np.floor(v*DEN)),DEN) for v in xx]
    pay=payments(pr,x);scale=min([Q(1)]+[c/v for c,v in zip(pr.capq,pay) if v>0])
    x=[Q((v*scale*DEN).numerator//(v*scale*DEN).denominator,DEN) for v in x]
    pay=payments(pr,x);slack=[b-v for b,v in zip(pr.capq,pay)]
    assert all(s>=0 for s in slack) and all(0<=v<=1 for v in x)
    xf=np.array(list(map(float,x)));g=pr.w*pr.p-pr.grad(xf)
    # Restrict the multiplier proposal to almost-active rows. Exact nonzero
    # complementarity slacks are retained in the certificate, never ignored.
    ia=np.where((pr.cap-pr.A@xf)/np.maximum(pr.row_scale,1e-15)<1e-6)[0]
    upper=np.where(xf>1-1e-6)[0];lower=np.where(xf<1e-6)[0]
    col=[pr.A[ia].T.toarray()]
    if len(upper):col.append(np.eye(pr.N)[:,upper])
    if len(lower):col.append(-np.eye(pr.N)[:,lower])
    M=np.column_stack(col)
    eta=np.zeros(pr.nodes);up=np.zeros(pr.N);lo=np.zeros(pr.N)
    if M.shape[1]:
        sol=nnls(M/pr.sw[:,None],g/pr.sw,maxiter=30*max(M.shape))[0]
        eta[ia]=sol[:len(ia)];p=len(ia)
        up[upper]=sol[p:p+len(upper)];p+=len(upper);lo[lower]=sol[p:]
    eq=[Q(max(0,int(round(v*DEN))),DEN) for v in eta]
    uq=[Q(max(0,int(round(v*DEN))),DEN) for v in up]
    lq=[Q(max(0,int(round(v*DEN))),DEN) for v in lo]
    accum=[]
    for n in range(pr.nodes):accum.append(eq[n]+(accum[pr.pa[n]] if n else 0))
    rg=exact_gradient(pr,x)
    residual=[rg[i]-pr.wq[i]*pr.aq[i]*accum[i//pr.d]-uq[i]+lq[i] for i in range(pr.N)]
    bd=sum((r*r/(4*pr.m*w) for r,w in zip(residual,pr.wq)),Q(0))
    bd+=sum((v*s for v,s in zip(eq,slack)),Q(0))
    bd+=sum((u*(1-v)+l*v for u,l,v in zip(uq,lq,x)),Q(0))
    val=exact_value(pr,x)
    return {'value':float(val),'gain':float(val-pr.staticvalue)/pr.mass,'bound':float(bd)/pr.mass,
            'value_fraction':str(val),'bound_fraction':str(bd),'policy':list(map(str,x)),
            'budget_prices':list(map(str,eq)),'upper_prices':list(map(str,uq)),
            'lower_prices':list(map(str,lq)),'minimum_slack':str(min(slack)),
            'scale':float(scale),'audit_seconds':time.perf_counter()-start}


def projection(pr,a):
    # Weighted Euclidean projection, solved independently of the economic objective.
    res=minimize(lambda x:(.5*np.dot(pr.w,(x-a)**2),pr.w*(x-a)),pr.static.copy(),
                 jac=True,method='SLSQP',bounds=[(0,1)]*pr.N,constraints=pr.constraints,
                 options={'ftol':1e-12,'maxiter':600})
    if not res.success and np.max(pr.C@res.x-pr.b)>1e-7:raise RuntimeError(res.message)
    return res.x,{'success':bool(res.success),'iterations':int(res.nit)}


class StopCertified(Exception):pass

def refine(pr,x0,thresholds=(1e-5,1e-7),prefix_seconds=0.):
    start=time.perf_counter();records=[];best=None;iteration=0;hits={}
    static_audit=audit(pr,pr.static)
    def check(x):
        nonlocal best
        c=audit(pr,x)
        if Q(c['value_fraction'])<pr.staticvalue:c=static_audit
        if best is None or c['bound']<best['bound']:best=c
        elapsed=prefix_seconds+time.perf_counter()-start
        for tol in thresholds:
            if str(tol) not in hits and Q(best['bound_fraction'])<=Q(str(tol))*pr.massq:
                hits[str(tol)]={'seconds':elapsed,'bound':best['bound'],'gain':best['gain'],
                                'iteration':iteration,'certificate':best}
        records.append({'iteration':iteration,'seconds':elapsed,'bound':c['bound'],'gain':c['gain']})
        return Q(best['bound_fraction'])<=Q(str(min(thresholds)))*pr.massq
    if check(x0):return {'hits':hits,'trace':records,'final':best,'solver_success':True,'iterations':0}
    def callback(x):
        nonlocal iteration
        iteration+=1
        if iteration%5==0 and check(x):raise StopCertified
    xstart=x0.copy();status=False
    try:
        res=minimize(lambda x:(-pr.value(x),pr.grad(x)-pr.w*pr.p),xstart,jac=True,
                     method='SLSQP',bounds=[(0,1)]*pr.N,constraints=pr.constraints,
                     callback=callback,options={'ftol':1e-13,'maxiter':1000})
        status=bool(res.success);iteration=int(res.nit);check(res.x)
    except StopCertified:status=True
    return {'hits':hits,'trace':records,'final':best,'solver_success':status,'iterations':iteration}


def read_models():
    return json.loads((OLD/'results/nonlinear_training.json').read_text())


def diagnose(pr,actor):
    clipped=np.clip(actor,0,1);before=pr.value(clipped)
    radial=audit(pr,actor)
    t=time.perf_counter();projected,pstatus=projection(pr,actor);projtime=time.perf_counter()-t
    proj=audit(pr,projected)
    # Feasible actor parameterization: radial segment from the accepted comparator,
    # taking the largest feasible step. Unlike global scaling it never moves away
    # from the comparator simply to reduce all payments.
    direction=clipped-pr.static;ad=np.asarray(pr.A@direction);sl=pr.cap-pr.A@pr.static
    alpha=min([1.]+[max(0.,v)/a for v,a in zip(sl,ad) if a>1e-12])
    segment=audit(pr,pr.static+alpha*direction)
    # Acceptance-cone actor from the tree-transfer construction. Each nonnegative
    # coefficient shifts payment from a child to its parent within one service;
    # its only nonzero continuation slack is at that child subtree.
    B=np.zeros((pr.N,(pr.nodes-1)*pr.d))
    for n in range(1,pr.nodes):
        for j in range(pr.d):
            col=(n-1)*pr.d+j; i=n*pr.d+j; parent=pr.pa[n]*pr.d+j
            B[parent,col]=1/(pr.w[parent]*pr.a[parent]);B[i,col]=-1/(pr.w[i]*pr.a[i])
    coefficients=nnls(pr.sw[:,None]*B,pr.sw*(actor-pr.static),maxiter=30*pr.N)[0]
    direction=B@coefficients
    alpha=min([1.]+[(1-z)/v if v>0 else -z/v for z,v in zip(pr.static,direction) if abs(v)>1e-14])
    flow=audit(pr,pr.static+max(0.,alpha)*direction)
    return {'before_feasible':bool(np.max(pr.C@clipped-pr.b)<=1e-10),
            'before_max_normalized_violation':float(max(0.,np.max(pr.C@clipped-pr.b))),
            'before_gain':(before-float(pr.staticvalue))/pr.mass,
            'radial':radial,'projection':proj,'segment':segment,'flow_actor':flow,'flow_alpha':float(alpha),
            'radial_reward_loss':(before-radial['value'])/pr.mass,
            'projection_reward_loss':(before-proj['value'])/pr.mass,
            'projection_seconds':projtime,'projection_status':pstatus}


def run_new(instances=12,model_count=4):
    models=read_models()[:model_count];rows=[];problems=[]
    fams=[('cycle',3,3,1,Q(1,4)),('erdos',4,4,1,Q(1,4)),
          ('geometric',6,4,2,Q(1,2)),('weighted_block',8,4,3,Q(1))]
    for family,d,depth,gamma,zeta in fams:
        for rep in range(instances):
            seed=920000+rep
            pr=prepare(Problem(d,depth,family,seed,gamma,zeta),True,seed)
            key=f'{family}-{seed}'
            record=pr.record();record.update({'id':key,'static':list(map(str,pr.staticq)),
                 'static_bound':str(pr.static_gap),'static_setup_seconds':pr.static_setup_seconds})
            problems.append(record)
            static_cert=audit(pr,pr.static)
            cold=refine(pr,pr.static)
            rows.append({'problem':key,'family':family,'method':'cold_slsqp','seed':None,
                         'pipeline':cold,'static_certificate':static_cert})
            for model in models:
                for mode in ('value','gradient'):
                    start=time.perf_counter();_,_,basis=pr.features(pr.p)
                    actor=pr.static+basis@np.array(model['coefficients'][mode])
                    generation=time.perf_counter()-start
                    diag=diagnose(pr,actor)
                    candidate=diag['projection']
                    # Independent diagnosis of radial/segment is NOT charged to the
                    # deployable projection pipeline. Its own construction and
                    # audit cost ARE charged, as is generation.
                    prefix=generation+diag['projection_seconds']+candidate['audit_seconds']
                    x0=np.array(list(map(float,map(Q,candidate['policy']))))
                    # The no-harm gate is measured and followed by actual refinement.
                    gt=time.perf_counter();chosen=candidate
                    if Q(candidate['value_fraction'])<pr.staticvalue:x0=pr.static.copy();chosen=static_cert
                    gate_seconds=time.perf_counter()-gt
                    pipe=refine(pr,x0,prefix_seconds=prefix+gate_seconds)
                    rows.append({'problem':key,'family':family,'method':mode,'seed':model['seed'],
                         'generation_seconds':generation,'diagnosis':diag,
                         'initial_gated_static':chosen is static_cert,
                         'selected_initial_bound':min(candidate['value']+float(Q(candidate['bound_fraction'])),
                              static_cert['value']+float(Q(static_cert['bound_fraction'])))-chosen['value'],
                         'pipeline':pipe})
            print(key,'static range',pr.static.min(),pr.static.max(),'cold gap',cold['final']['bound'],flush=True)
            (HERE/'results/new_problems.json').write_text(json.dumps(problems))
            (HERE/'results/new_records.json').write_text(json.dumps(rows))
    return rows


def old_diagnostics():
    models=read_models();rows=[]
    specs=json.loads((OLD/'results/nonlinear_problems.json').read_text())
    oldrecords=json.loads((OLD/'results/nonlinear_records.json').read_text())
    for spec in specs:
        seed=int(spec['id'].split('-')[-1]);pr=prepare(Problem(spec['d'],spec['depth'],spec['family'],seed,Q(spec['gamma']),Q(spec['zeta'])))
        assert list(map(str,pr.pq))==spec['forcing'] and pr.edges==[tuple(v) for v in spec['edges']]
        sc=audit(pr,pr.static)
        classical=max(r['certificate']['gain_over_static']/pr.mass for r in oldrecords if r['problem']==spec['id'] and r['seed'] is None)
        # Projection diagnostics on original large cases use SLSQP only up to 120
        # coordinates; 992-coordinate cases retain radial diagnostics and actual
        # cached-Newton refinement, not a fabricated projection comparison.
        for model in models:
            for mode in ('value','gradient'):
                t=time.perf_counter();_,_,basis=pr.features(pr.p);actor=.5+basis@np.array(model['coefficients'][mode]);gen=time.perf_counter()-t
                before=pr.value(np.clip(actor,0,1));cert=audit(pr,actor)
                chosenvalue=max(cert['value'],float(pr.staticvalue))
                gatebound=min(cert['value']+float(Q(cert['bound_fraction'])),sc['value']+float(Q(sc['bound_fraction'])))-chosenvalue
                row={'problem':spec['id'],'family':pr.family,'seed':model['seed'],'method':mode,
                     'before_gain':(before-float(pr.staticvalue))/pr.mass,
                     'before_feasible':bool(np.max(pr.C@np.clip(actor,0,1)-pr.b)<=1e-10),
                     'before_violation':float(max(0.,np.max(pr.C@np.clip(actor,0,1)-pr.b))),
                     'radial_reward_loss':(before-cert['value'])/pr.mass,'radial':cert,
                     'selected_gap':gatebound/pr.mass,'classical_gain':classical,
                     'proposal_bound_gain_ratio':cert['bound']/classical if classical>0 else None,
                     'selected_bound_gain_ratio':gatebound/pr.mass/classical if classical>0 else None}
                if pr.N==992:
                    t=time.perf_counter();x,eta,status=pr.solve(linear='cached_pcg');ref=audit(pr,x)
                    row['refined']=ref;row['refine_status']=status
                    row['pipeline_seconds']=gen+cert['audit_seconds']+time.perf_counter()-t
                rows.append(row)
        print('old',spec['id'],flush=True)
    (HERE/'results/old_diagnostics.json').write_text(json.dumps(rows))


def sensitivity():
    rows=[];oracles=[]
    for seed in range(12):
        pr=prepare(Problem(seed=99100+seed));rng=np.random.default_rng(731+seed);direction=rng.choice([-1,1],pr.N)
        pq=pr.pq.copy();p=pr.p.copy();central,_,_=pr.solve();true=float(np.dot(pr.w*direction,central-pr.static))/pr.mass
        central_cert=audit(pr,central)
        oracles.append({'seed':seed,'role':'central','problem':pr.record(),
                        'static':list(map(str,pr.staticq)),'certificate':central_cert})
        for h in (Q(1,80),Q(1,40),Q(1,20)):
            vals=[];gaps=[]
            for sign in (-1,1):
                pr.pq=[v+sign*h*int(u) for v,u in zip(pq,direction)];pr.p=np.array(list(map(float,pr.pq)))
                pr.staticvalue=exact_value(pr,pr.staticq)
                x,_,_=pr.solve();c=audit(pr,x);vals.append((c['value']-float(exact_value(pr,pr.staticq)))/pr.mass);gaps.append(c['bound'])
                oracles.append({'seed':seed,'role':'endpoint','h':str(h),'sign':sign,
                                'direction':list(map(int,direction)),'problem':pr.record(),
                                'static':list(map(str,pr.staticq)),'certificate':c})
            deriv=(vals[1]-vals[0])/(2*float(h));bound=float(h)/(4*float(pr.m))+sum(gaps)/(2*float(h))
            assert abs(deriv-true)<=bound+1e-8
            for extra in (0.,1e-7,1e-5):
                rows.append({'seed':seed,'h':str(h),'extra_endpoint_gap_per_review':extra,
                    'measured_directional_error':abs(deriv-true),'bound':bound+extra/float(h)})
            pr.pq=pq;pr.p=p;pr.staticvalue=exact_value(pr,pr.staticq)
    (HERE/'results/fd_sensitivity.json').write_text(json.dumps(rows,indent=2))
    (HERE/'results/fd_oracles.json').write_text(json.dumps(oracles))


def summary():
    rows=json.loads((HERE/'results/new_records.json').read_text());problems=json.loads((HERE/'results/new_problems.json').read_text())
    out={'environment':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),
                        'processor':platform.processor(),'threads':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')}},
         'instances':len(problems),'deployments':len(rows),'frozen_training_seeds':sorted({r['seed'] for r in rows if r['seed'] is not None}),
         'noncentered_static_min':min(float(Q(x)) for p in problems for x in p['static']),
         'noncentered_static_max':max(float(Q(x)) for p in problems for x in p['static']),
         'static_boundary_instances':sum(any(Q(x) in (0,1) for x in p['static']) for p in problems),
         'static_max_bound':max(float(Q(p['static_bound'])) for p in problems),'groups':[]}
    for family in ('cycle','erdos','geometric','weighted_block'):
        for method in ('cold_slsqp','value','gradient'):
            rr=[r for r in rows if r['family']==family and r['method']==method];q={'family':family,'method':method,'n':len(rr)}
            q['final_max_bound']=max(r['pipeline']['final']['bound'] for r in rr)
            q['final_mean_gain']=float(np.mean([r['pipeline']['final']['gain'] for r in rr]))
            for tol in ('1e-05','1e-07'):
                hits=[r['pipeline']['hits'].get(tol) for r in rr];good=[v for v in hits if v]
                q[tol]={'met':len(good),'median_ms':float(np.median([v['seconds']*1000 for v in good])) if good else None,
                        'mean_ms':float(np.mean([v['seconds']*1000 for v in good])) if good else None}
            if method!='cold_slsqp':
                q.update({'pre_repair_feasible':sum(r['diagnosis']['before_feasible'] for r in rr),
                    'mean_radial_scale':float(np.mean([r['diagnosis']['radial']['scale'] for r in rr])),
                    'mean_before_gain':float(np.mean([r['diagnosis']['before_gain'] for r in rr])),
                    'mean_radial_gain':float(np.mean([r['diagnosis']['radial']['gain'] for r in rr])),
                    'mean_projection_gain':float(np.mean([r['diagnosis']['projection']['gain'] for r in rr])),
                    'mean_segment_gain':float(np.mean([r['diagnosis']['segment']['gain'] for r in rr])),
                    'mean_flow_gain':float(np.mean([r['diagnosis']['flow_actor']['gain'] for r in rr])),
                    'mean_radial_loss':float(np.mean([r['diagnosis']['radial_reward_loss'] for r in rr])),
                    'mean_projection_loss':float(np.mean([r['diagnosis']['projection_reward_loss'] for r in rr])),
                    'initial_static':sum(r['initial_gated_static'] for r in rr),
                    'immediate_1e7':sum(r['pipeline']['hits'].get('1e-07',{}).get('iteration')==0 for r in rr)})
            out['groups'].append(q)
    # Crossed instance/training-seed descriptive bootstrap, stratified by family.
    # No claim of inference across an unspecified population of graph families.
    fams=('cycle','erdos','geometric','weighted_block');seeds=out['frozen_training_seeds']
    grid=np.zeros((4,len(problems)//4,len(seeds)))
    for fi,f in enumerate(fams):
        ids=sorted({r['problem'] for r in rows if r['family']==f})
        for ii,ident in enumerate(ids):
            for si,seed in enumerate(seeds):
                pair={r['method']:r['diagnosis']['projection']['gain'] for r in rows if r['problem']==ident and r['seed']==seed}
                grid[fi,ii,si]=pair['gradient']-pair['value']
    rng=np.random.default_rng(122209);boot=[]
    for _ in range(2000):
        ss=rng.integers(0,len(seeds),len(seeds))
        ii=rng.integers(0,grid.shape[1],grid.shape[1])
        boot.append(np.mean([grid[f][ii][:,ss].mean() for f in range(4)]))
    out['crossed_projection_difference']={'mean':float(grid.mean()),'percentile95':np.quantile(boot,[.025,.975]).tolist(),
          'interpretation':'Descriptive crossed bootstrap over training seeds and common replication blocks jointly across four fixed graph families; only four training seeds.'}
    (HERE/'results/summary.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

def repeated_timing():
    model=read_models()[0];records=[];setups=[]
    specs=[('cycle',3,3,1,Q(1,4)),('erdos',4,4,1,Q(1,4)),('geometric',6,4,2,Q(1,2)),('weighted_block',8,4,3,Q(1))]
    rng=np.random.default_rng(123941)
    for family,d,depth,gamma,zeta in specs:
        t=time.perf_counter();pr=prepare(Problem(d,depth,family,920000,gamma,zeta),True,920000)
        staticcert=audit(pr,pr.static);setups.append({'family':family,'shared_setup_seconds':time.perf_counter()-t})
        for rep in range(-1,5):
            for method in rng.permutation(['cold_slsqp','value','gradient']):
                start=time.perf_counter();x0=pr.static.copy();prefix=0.
                if method!='cold_slsqp':
                    _,_,basis=pr.features(pr.p);actor=pr.static+basis@np.array(model['coefficients'][method])
                    x,_=projection(pr,actor);c=audit(pr,x)
                    if Q(c['value_fraction'])>=pr.staticvalue:x0=np.array(list(map(float,map(Q,c['policy']))))
                    prefix=time.perf_counter()-start
                pipe=refine(pr,x0,prefix_seconds=prefix)
                if rep>=0:records.append({'problem':f'{family}-920000','family':family,'method':str(method),'replicate':rep,'pipeline':pipe})
        print('timing',family,flush=True)
    (HERE/'results/repeated_timing.json').write_text(json.dumps(records))
    (HERE/'results/common_setup.json').write_text(json.dumps(setups,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['new','old','fd','summary','timing'],default='new');ap.add_argument('--instances',type=int,default=12);ap.add_argument('--models',type=int,default=4);args=ap.parse_args()
    (HERE/'results').mkdir(exist_ok=True)
    if args.mode=='new':run_new(args.instances,args.models)
    elif args.mode=='old':old_diagnostics()
    elif args.mode=='fd':sensitivity()
    elif args.mode=='timing':repeated_timing()
    else:summary()
