#!/usr/bin/env python3
"""Independent exact replay. Standard library only; no optimizer imports."""
from fractions import Fraction as F
from pathlib import Path
import gzip,json,hashlib,math
HERE=Path(__file__).resolve().parent;OUT=HERE/'results'
def read(p):
    return json.load(gzip.open(p,'rt')) if str(p).endswith('.gz') else json.loads(Path(p).read_text())
COUNTS={'policies':0,'subtrees':0,'tier_coordinates':0,'critical_brackets':0}
def check(p,r):
    pa=p['parent'];n=len(pa);m=n-1;w=list(map(F,p['weights']));c=list(map(F,p['tariffs']));gg=[list(map(F,z)) for z in p['forcing']]
    th=list(map(F,r['theta']));u=list(map(F,r['flows']));mu=list(map(F,r['multipliers']));s=list(map(F,r['tensions']));nu=F(r['root_price'])
    assert len(u)==m and len(mu)==m+2*n and len(s)==n and min(u)>=0 and min(mu)>=0
    x=[F(1,2)]*n
    for i in range(1,n):x[i]-=u[i-1];x[pa[i]]+=c[i]/c[pa[i]]*u[i-1]
    assert all(0<=z<=1 for z in x)
    subtree=[c[i]*(x[i]-F(1,2)) for i in range(n)]
    for i in range(n-1,0,-1):subtree[pa[i]]+=subtree[i]
    assert subtree[0]==0 and all(subtree[i]==-c[i]*u[i-1]<=0 for i in range(1,n))
    diff=[x[i]-(x[pa[i]] if i else F(1,2)) for i in range(n)]
    g0=[gg[0][i]+th[0]*gg[1][i]+th[1]*gg[2][i] for i in range(n)]
    assert sum(g0)==0 and th[2]>=0 and all(abs(s[i])<=th[2]*w[i] for i in range(n))
    g=[g0[i]-2*w[i]*(x[i]-F(1,2)) for i in range(n)]
    for i in range(1,n):d=w[i]*diff[i]/5;g[i]-=d;g[pa[i]]+=d
    ds=s.copy()
    for i in range(1,n):ds[pa[i]]-=s[i]
    anc=[F(0)]*n
    for i in range(1,n):anc[i]=anc[pa[i]]+mu[i-1]/c[i]
    up=mu[m:m+n];low=mu[m+n:];e=[g[i]-ds[i]-up[i]+low[i]-c[i]*(anc[i]+nu) for i in range(n)]
    quad=sum(e[i]**2/(4*w[i]) for i in range(n))
    slack=sum(mu[i]*u[i] for i in range(m))+sum(up[i]*(1-x[i])+low[i]*x[i] for i in range(n))
    leak=sum(th[2]*w[i]*abs(diff[i])-s[i]*diff[i] for i in range(n))
    smooth=sum(w[i]*(x[i]-F(1,2))**2 for i in range(n))+sum(w[i]*diff[i]**2/10 for i in range(1,n))
    gain=sum(g0[i]*(x[i]-F(1,2)) for i in range(n))-smooth-sum(th[2]*w[i]*abs(diff[i]) for i in range(n))
    assert quad>=0 and slack>=0 and leak>=0
    assert F(r['quadratic'])==quad and F(r['acceptance_leakage'])==slack and F(r['switching_leakage'])==leak
    assert F(r['bound_fraction'])==quad+slack+leak and F(r['gain_fraction'])==gain
    assert abs(r['gain']-float(gain/sum(w)))<1e-12 and abs(r['bound']-float((quad+slack+leak)/sum(w)))<1e-12
    COUNTS['policies']+=1;COUNTS['subtrees']+=n;COUNTS['tier_coordinates']+=n
    return gain,(quad+slack+leak),sum(w)
def brackets():
    for r in read(OUT/'scaling.json.gz')['records']:
        p=r['primitives'];pa=p['parent'];N=len(pa);c=list(map(F,p['tariffs']));k=list(map(F,p['weights']));g=list(map(F,p['gradient']))
        cert=r['certificate'];s=list(map(F,cert['upper_tensions']));u=list(map(F,cert['direction']));lo=F(cert['lower_fraction']);hi=F(cert['upper_fraction'])
        a=[c[i]/c[pa[i]]*g[pa[i]]-g[i] for i in range(1,N)];dt=s.copy()
        for i in range(1,N):dt[pa[i]]-=s[i]
        assert all(c[i]/c[pa[i]]*dt[pa[i]]-dt[i]>=a[i-1] for i in range(1,N))
        assert all(abs(s[i])<=hi*k[i] for i in range(N)) and min(u)>=0
        x=[F(0)]*N
        for i in range(1,N):x[i]-=u[i-1];x[pa[i]]+=c[i]/c[pa[i]]*u[i-1]
        den=sum(k[i]*abs(x[i]-(x[pa[i]] if i else 0)) for i in range(N))
        ratio=max(F(0),sum(a[i]*u[i] for i in range(N-1))/den) if den else F(0)
        assert ratio==lo and lo<=hi
        assert r['attained']==(hi-lo<=F(str(r['tolerance']))+F(1,10**12))
        COUNTS['critical_brackets']+=1

def main():
    paths=read(OUT/'friction_paths.json.gz');models=paths['models'];base=models['5'];mass=sum(map(F,base['weights']))
    for r in paths['records']:
        _,C,S=check(models[str(r['depth'])],r['audit']);assert C/S<F(1,10**7)
    for name in ('validation','confirmation'):
        samples=[]
        for file in sorted(OUT.glob(name+'-*.json.gz')):
            part=read(file)
            for r in part['records']:
                gain,_,_=check(base,r);assert gain>=0
            for row in part['samples']:
                samples.append(row['sample']);assert all(part['records'][j]['theta']==part['records'][row['records'][0]]['theta'] for j in row['records'])
        assert sorted(samples)==list(range(4096))
    plan=read(OUT/'confirmatory_plan.json');B=F(plan['range_fraction']);upper=[]
    for r in plan['corner_records']:
        g,C,S=check(base,r);upper.append((g+C)/S)
        assert F(r['theta'][2])==F(1,100) and all(F(t) in (-1,1) for t in r['theta'][:2])
    assert B==max(upper)
    ph=hashlib.sha256((OUT/'confirmatory_plan.json').read_bytes()).hexdigest();mh=hashlib.sha256((OUT/'frozen_model.json.gz').read_bytes()).hexdigest()
    assert mh==plan['model_sha256']
    cs=[F(0)]*3;gs=[F(0)]*3
    for file in OUT.glob('confirmation-*.json.gz'):
        data=read(file);assert data['plan_sha256']==ph and data['model_sha256']==mh
        for row in data['samples']:
            for j,idx in enumerate(row['records']):
                r=data['records'][idx];cs[j]+=min(B,F(r['bound_fraction'])/mass);gs[j]+=F(r['gain_fraction'])/mass
    rep=read(OUT/'confirmation.json');assert list(map(F,rep['certificate_sums_fraction']))==cs and list(map(F,rep['gain_sums_fraction']))==gs
    rad=float(B)*math.sqrt(math.log(6/.05)/(2*4096));assert abs(rad-rep['radius'])<1e-14
    for j in range(3):
        assert abs(rep['expected_regret_upper_bounds'][j]-(float(cs[j]/4096)+rad))<1e-12
        assert abs(rep['expected_gain_lower_bounds'][j]-max(0,float(gs[j]/4096)-rad))<1e-12
    for row in read(OUT/'matched_records.json.gz')['records']:
        check(base,row['reference'])
        for data in row['methods'].values():
            check(base,data['candidate']);_,C,S=check(base,data['final']);assert C/S<=F(1,10**7)
    for row in read(OUT/'face_diagnostics.json.gz')['records']:
        gain,C,S=check(base,row['audit']);assert F(row['reference_gain_fraction'])-gain<=C
    brackets()
    # Exact necessity witnesses: omitting either linear leakage invalidates a bound.
    for x in (F(1,10),F(1,100),F(1,1000)):
        regret=x+x*x/2;quadratic=x*x/2;assert quadratic<regret and quadratic+x==regret
    result={'status':'pass','arithmetic':'fractions.Fraction','optimizer_imports':False,'numerical_library_imports':False,
            **COUNTS,'model_sha256':mh,'confirmation_plan_sha256':ph,'confirmation_simultaneous_confidence':.95,
            'note':'Exact replay checks finite submitted policies and critical brackets; analytic proofs establish the general theorems.'}
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
