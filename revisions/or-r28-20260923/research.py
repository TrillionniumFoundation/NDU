#!/usr/bin/env python3
"""Generate exact, synthetic R28 evidence. No numerical optimizer is trusted.
Timings cover Python Fraction arithmetic; the fresh comparator is a specialized
closed-form solve, not a dense QP. See EC for the deliberately separable design.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import json, platform, statistics, sys, time, subprocess, resource
R=Path(__file__).resolve().parent

def enc(x):
    if isinstance(x,F): return str(x)
    if isinstance(x,dict): return {str(k):enc(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [enc(v) for v in x]
    return x

def clip(x,lo=F(0),hi=F(1)): return min(hi,max(lo,x))
def psi(d,h=F(1)):
    x=clip(d/h); return d*x-h*x*x/2

def bridge(delta):
    if delta<=F(1,10):
        x=[F(3,5)-delta,F(2,5),F(2,5)+2*delta]
        eta,t,ml,mh=F(2,5)+delta,F(3,5)-3*delta/2,F(1,5)-2*delta,F(0)
    elif delta<=F(3,10):
        x=[F(1,2),F(1,2)-delta,F(1,2)+delta]
        eta,t,ml,mh=F(1,2),F(1,2)-delta/2,F(0),F(0)
    elif delta<F(2,5):
        x=[F(1,5)+delta,F(4,5)-2*delta,F(4,5)]
        eta,t,ml,mh=F(4,5)-delta,F(4,5)-3*delta/2,F(0),2*delta-F(3,5)
    else:
        x=[F(3,5),F(0),F(4,5)]
        eta,t,ml,mh=F(2,5),F(0),F(0),F(2,5)
    children=[]
    for reward,cap,mu,plus,minus in [(F(0),F(2,5),ml,F(0),2*t),(F(2),F(4,5),mh,2*t,F(0))]:
        chi=2*mu; childeta=eta+chi
        d=reward-childeta-plus+minus
        children.append(dict(chi=chi,eta=childeta,B=childeta-chi,gamma=plus-minus,k=plus+minus,C=psi(d)+chi*cap,d=d))
    constant=psi(1-eta)+sum((c['C']/2 for c in children),F(0))
    plane=dict(B=eta,gamma=sum((c['gamma']/2 for c in children),F(0)),k=2*t,C=constant)
    val=x[0]-x[0]**2/2+x[2]-(x[1]**2+x[2]**2)/4
    upper=plane['B']+plane['k']*delta+plane['C']+max(F(0),plane['gamma'])
    assert upper==val
    return dict(delta=delta,x=x,table=[x[0],(x[1]+x[2])/2],value=val,eta=eta,t=t,mu=[ml,mh],children=children,plane=plane,upper=upper)

def theta(index,d):
    # Deterministic rational design; no fitted coefficients or hidden labels.
    return [F(((index+3)*(j*7+5)+j*j*3)%19-9,9) for j in range(d)]

def block(q,bid,unstable):
    d=len(q)
    z=sum((F(((bid+1)*(j+2))%7-3,3)*q[j] for j in range(d)),F(0))/d
    z2=sum((F(((bid+4)*(j+5))%9-4,4)*q[j] for j in range(d)),F(0))/d
    p0=F(1)+z/8; rl=F(1,5)+z2/4; rh=F(9,5)+z/2
    # Jointly changing continuation coefficients and caps. All roots stay feasible.
    al=F(1)+z/8; ah=F(1)-z/10
    if unstable: bl=F(1,2)+q[0]/5+z2/20; bh=F(1,2)-q[0]/5-z2/20
    else: bl=F(7,20)+z2/30; bh=F(7,10)-z2/30
    assert al>0 and ah>0 and 0<bl/al<1 and 0<bh/ah<1
    return dict(p0=p0,rl=rl,rh=rh,al=al,ah=ah,bl=bl,bh=bh)

def value(m,x):
    r,l,h=x
    return m['p0']*r-r*r/2+(m['rl']*l+m['rh']*h)/2-(l*l+h*h)/4

def audit(m,x,pooled=False):
    r,l,h=x
    assert all(0<=v<=1 for v in x)
    assert r+(l+h)/2==1 and m['al']*l<=m['bl'] and m['ah']*h<=m['bh']
    if pooled: assert l==h

def restricted(m):
    free=(1-m['p0']+(m['rl']+m['rh'])/2)/2
    capl,caph=m['bl']/m['al'],m['bh']/m['ah']
    v=clip(free,F(0),min(capl,caph))
    assert 0<v<1   # designed family: no lower-tier active cases
    nu=m['p0']-(1-v); total=2*(free-v)
    ml=total/m['al'] if capl<=caph else F(0)
    mh=total/m['ah'] if caph<capl else F(0)
    xi=(m['rl']-v-nu)/2-m['al']*ml
    x=[1-v,v,v]; a=dict(nu=nu,xi=xi,ml=ml,mh=mh)
    face='interior' if total==0 else ('low' if capl<=caph else 'high')
    audit(m,x,True); assert upper(m,a)==value(m,x)
    return x,a,face

def upper(m,a):
    nu,xi,ml,mh=(a[k] for k in ['nu','xi','ml','mh'])
    assert ml>=0 and mh>=0
    ds=[m['p0']-nu,m['rl']/2-nu/2-xi-m['al']*ml,m['rh']/2-nu/2+xi-m['ah']*mh]
    return nu+ml*m['bl']+mh*m['bh']+psi(ds[0])+psi(ds[1],F(1,2))+psi(ds[2],F(1,2))

def full(m):
    # Exact three-coordinate weighted water filling, with the same payment equation.
    r=[m['p0'],m['rl'],m['rh']]; caps=[F(1),m['bl']/m['al'],m['bh']/m['ah']]; w=[F(1),F(1,2),F(1,2)]
    knots=sorted(set(r+[r[i]-caps[i] for i in range(3)]),reverse=True)
    def demand(e): return [clip(r[i]-e,F(0),caps[i]) for i in range(3)]
    for hi,lo in zip(knots,knots[1:]):
        xhi,xlo=demand(hi),demand(lo)
        b_hi=sum((a*b for a,b in zip(w,xhi)),F(0)); b_lo=sum((a*b for a,b in zip(w,xlo)),F(0))
        if b_hi<=1<=b_lo and b_lo>b_hi:
            e=hi-(hi-lo)*(1-b_hi)/(b_lo-b_hi); x=demand(e); audit(m,x); return x
    raise AssertionError('No feasible water-filling interval')

def repair(m,old):
    v=min(old[1],m['bl']/m['al'],m['bh']/m['ah']); x=[1-v,v,v]; audit(m,x,True); return x

def experiment(cfg):
    blocks=cfg['cycles']*cfg['services']; d=cfg['d']; size=cfg['cache']; unstable=cfg['unstable']
    initial=[]; t0=time.perf_counter_ns()
    for i in range(size):
        q=theta(100+i,d); models=[block(q,j,unstable) for j in range(blocks)]
        triples=[restricted(m) for m in models]
        initial.append(dict(theta=q,x=[v[0] for v in triples],prices=[v[1] for v in triples]))
    init_ns=time.perf_counter_ns()-t0
    cache=list(initial); records=[]; previous=None
    tol=F(blocks,1000)
    for i in range(12):
        t0=time.perf_counter_ns(); q=theta(i,d); models=[block(q,j,unstable) for j in range(blocks)]; coeff_ns=time.perf_counter_ns()-t0
        t0=time.perf_counter_ns(); candidate=[full(m) for m in models]; candidate_ns=time.perf_counter_ns()-t0
        t0=time.perf_counter_ns()
        for m,x in zip(models,candidate): audit(m,x)
        fval=sum((value(m,x) for m,x in zip(models,candidate)),F(0)); audit_ns=time.perf_counter_ns()-t0
        t0=time.perf_counter_ns(); bounds=[sum((upper(m,a) for m,a in zip(models,c['prices'])),F(0)) for c in cache]; best=min(range(len(bounds)),key=bounds.__getitem__); u=bounds[best]; cache_ns=time.perf_counter_ns()-t0
        t0=time.perf_counter_ns(); witness=[repair(m,x) for m,x in zip(models,cache[best]['x'])]; lower=sum((value(m,x) for m,x in zip(models,witness)),F(0)); witness_ns=time.perf_counter_ns()-t0
        trigger=u-lower>tol
        # Independent exact fresh reference is evaluation-only except on a declared refresh.
        t0=time.perf_counter_ns(); triples=[restricted(m) for m in models]; k=sum((value(m,v[0]) for m,v in zip(models,triples)),F(0)); fresh_ns=time.perf_counter_ns()-t0
        face=[v[2] for v in triples]; changes=0 if previous is None else sum(a!=b for a,b in zip(face,previous)); previous=face
        refresh_ns=0; used_upper=u; a_new=None
        if trigger:
            t0=time.perf_counter_ns(); a_new=dict(theta=q,x=[v[0] for v in triples],prices=[v[1] for v in triples]); cache.append(a_new)
            if len(cache)>size: cache.pop(0)
            used_upper=sum((upper(m,a) for m,a in zip(models,a_new['prices'])),F(0)); assert used_upper==k
            refresh_ns=fresh_ns+time.perf_counter_ns()-t0
        assert used_upper-k<=tol and u>=k and fval>=k
        records.append(dict(index=i,theta=q,candidate=candidate,pre_upper=u,witness_lower=lower,reference=k,full_value=fval,used_upper=used_upper,refresh=trigger,face_changes=changes,faces=face,best_anchor=best,coeff_ns=coeff_ns,candidate_ns=candidate_ns,audit_ns=audit_ns,cache_ns=cache_ns,witness_ns=witness_ns,fresh_ns=fresh_ns,refresh_ns=refresh_ns,cache_bytes=len(json.dumps(enc(cache),sort_keys=True).encode())))
    return dict(config=cfg,blocks=blocks,n=3*blocks,tolerance=tol,initial_ns=init_ns,initial_cache=initial,records=records,peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

def main():
    R.joinpath('results').mkdir(exist_ok=True)
    deltas=[F(0),F(1,20),F(1,15),F(1,10),F(1,5),F(3,10),F(7,20),F(2,5),F(1,2)]
    configs=[dict(cycles=4,services=1,d=1,cache=1,unstable=False),dict(cycles=16,services=2,d=4,cache=1,unstable=False),dict(cycles=16,services=2,d=4,cache=4,unstable=False),dict(cycles=16,services=2,d=4,cache=4,unstable=True),dict(cycles=32,services=4,d=8,cache=4,unstable=True),dict(cycles=32,services=4,d=8,cache=8,unstable=True),dict(cycles=128,services=4,d=8,cache=8,unstable=True)]
    data=dict(schema='ndu-or-r28-exact-v1',provenance=dict(python=sys.version,platform=platform.platform(),processor=platform.processor(),clock='perf_counter_ns',arithmetic='fractions.Fraction',timings='single process, sequential; no speedup claim'),bridge=[bridge(x) for x in deltas],scaling=[])
    for cfg in configs:
        run=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),'--case',json.dumps(cfg)],check=True,capture_output=True,text=True)
        result=json.loads(run.stdout); data['scaling'].append(result)
        print('completed',cfg,'refresh',sum(x['refresh'] for x in result['records']),flush=True)
    R.joinpath('results/evidence.json').write_text(json.dumps(enc(data),indent=2,sort_keys=True)+'\n')
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--case':
        print(json.dumps(enc(experiment(json.loads(sys.argv[2]))),sort_keys=True))
    else: main()
