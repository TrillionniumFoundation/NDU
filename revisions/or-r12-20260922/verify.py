#!/usr/bin/env python3
"""Independent Fraction verifier: imports neither optimizer nor NumPy/SciPy.
Reconstructs tier bounds, every subtree payment, polynomial value, stationarity,
box prices, and full-horizon certificate from committed primitives and records.
"""
from fractions import Fraction as Q
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent;OUT=HERE/'results';OLD=HERE.parent/'or-r10-20260921/results'


def build(spec):
    d=spec['d'];pa=spec['parents'];N=len(pa)*d
    return {'d':d,'pa':pa,'N':N,'w':list(map(Q,spec['weights'])),'a':list(map(Q,spec['tariffs'])),
            'p':list(map(Q,spec['forcing'])),'m':Q(spec['m']),'gamma':Q(spec['gamma']),
            'lambda':Q(spec['lambda']),'zeta':Q(spec['zeta']),'edges':spec['edges'],
            'static':list(map(Q,spec.get('static',['1/2']*N)))}


def evaluate(pr,x):
    d=pr['d'];N=pr['N'];pa=pr['pa'];w=pr['w'];p=pr['p'];m=pr['m'];ga=pr['gamma'];la=pr['lambda'];ze=pr['zeta']
    assert len(x)==N and all(0<=v<=1 for v in x)
    value=Q(0);grad=[w[i]*(p[i]-2*m*x[i]-4*ga*x[i]**3) for i in range(N)]
    pay=[]
    for n,parentnode in enumerate(pa):
        pay.append(sum((w[n*d+j]*pr['a'][n*d+j]*x[n*d+j] for j in range(d)),Q(0)))
        for j in range(d):
            i=n*d+j;q=Q(1,2) if n==0 else x[parentnode*d+j]
            value+=w[i]*(p[i]*x[i]-m*x[i]**2-ga*x[i]**4-la*(x[i]-q)**2)
            term=2*w[i]*la*(x[i]-q);grad[i]-=term
            if n:grad[parentnode*d+j]+=term
        for j,k,weight in pr['edges']:
            i=n*d+j;l=n*d+k;term=2*w[n*d]*ze*weight*(x[i]-x[l])
            value-=w[n*d]*ze*weight*(x[i]-x[l])**2;grad[i]-=term;grad[l]+=term
    for n in range(len(pa)-1,0,-1):pay[pa[n]]+=pay[n]
    return value,grad,pay


def check(pr,c):
    x=list(map(Q,c['policy']));mu=list(map(Q,c['budget_prices']));up=list(map(Q,c['upper_prices']));lo=list(map(Q,c['lower_prices']))
    assert len(mu)==len(pr['pa']) and len(up)==len(lo)==pr['N']
    assert all(v>=0 for v in mu+up+lo)
    val,grad,pay=evaluate(pr,x);static,_,caps=evaluate(pr,pr['static'])
    slack=[b-a for a,b in zip(pay,caps)];assert all(v>=0 for v in slack)
    assert min(slack)==Q(c['minimum_slack'])
    price=[]
    for n in range(len(mu)):price.append(mu[n]+(price[pr['pa'][n]] if n else 0))
    res=[grad[i]-pr['w'][i]*pr['a'][i]*price[i//pr['d']]-up[i]+lo[i] for i in range(pr['N'])]
    bound=sum((r*r/(4*pr['m']*w) for r,w in zip(res,pr['w'])),Q(0))
    bound+=sum((a*b for a,b in zip(mu,slack)),Q(0))
    bound+=sum((u*(1-v)+l*v for u,l,v in zip(up,lo,x)),Q(0))
    assert val==Q(c['value_fraction']) and bound==Q(c['bound_fraction'])
    assert abs(float(bound/sum(pr['w']))-c['bound'])<1e-12*max(1.,c['bound'])
    assert abs(float((val-static)/sum(pr['w']))-c['gain'])<1e-12*max(1.,abs(c['gain']))
    return len(slack),2*pr['N']


def certificates(obj):
    if isinstance(obj,dict):
        if 'budget_prices' in obj and 'policy' in obj:yield obj
        else:
            for v in obj.values():yield from certificates(v)
    elif isinstance(obj,list):
        for v in obj:yield from certificates(v)


def run():
    specs=json.loads((OUT/'new_problems.json').read_text());pr={p['id']:build(p) for p in specs}
    for spec in specs:
        p=pr[spec['id']];_,gg,_=evaluate(p,p['static']);d=p['d'];ww=sum(p['w'][::d]);bound=Q(0)
        for j in range(d):
            g=sum(gg[j::d],Q(0));z=p['static'][j]
            normal=g if (z==1 and g>0) or (z==0 and g<0) else Q(0)
            bound+=(g-normal)**2/(4*p['m']*ww)
        assert bound==Q(spec['static_bound'])
    seen=set();checks=0;subtrees=0;tiers=0
    newrows=json.loads((OUT/'new_records.json').read_text())
    allrows=list(newrows)
    timingrows=json.loads((OUT/'repeated_timing.json').read_text())
    allrows+=timingrows
    if (OUT/'old_diagnostics.json').exists():
        pr.update({p['id']:build(p) for p in json.loads((OLD/'nonlinear_problems.json').read_text())})
        allrows+=json.loads((OUT/'old_diagnostics.json').read_text())
    for row in allrows:
        for c in certificates(row):
            key=hashlib.sha256((row['problem']+json.dumps(c,sort_keys=True)).encode()).hexdigest()
            if key in seen:continue
            seen.add(key);a,b=check(pr[row['problem']],c);checks+=1;subtrees+=a;tiers+=b
        if 'pipeline' in row:
            p=pr[row['problem']]
            for tolerance,hit in row['pipeline']['hits'].items():
                assert Q(hit['certificate']['bound_fraction'])<=Q(tolerance)*sum(p['w'])
                assert Q(hit['certificate']['value_fraction'])>=evaluate(p,p['static'])[0]
    oracles=json.loads((OUT/'fd_oracles.json').read_text())
    for record in oracles:
        spec=record['problem'].copy();spec['static']=record['static']
        a,b=check(build(spec),record['certificate']);checks+=1;subtrees+=a;tiers+=b
    output={'verified_certificates':checks,'exact_subtree_checks':subtrees,'exact_tier_checks':tiers,
            'static_comparators_verified':len(specs),'new_deployments':len(newrows),
            'all_claimed_tolerances_exact':True,'all_final_new_rewards_at_least_static':True,
            'numerical_optimizer_imported':False,'retimed_deployments_verified':len(timingrows),
            'finite_difference_oracles_verified':len(oracles)}
    (OUT/'verification.json').write_text(json.dumps(output,indent=2));print(json.dumps(output))
if __name__=='__main__':run()
