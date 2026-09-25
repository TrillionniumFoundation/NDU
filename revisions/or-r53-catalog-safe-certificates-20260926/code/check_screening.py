"""Independent screening-chain verifier using breakpoint maxima.

Does not import screening.py or a design optimizer. The unchanged R52 semantic
resource checker verifies the reduced problem. A separately supplied instance
hash binds the certificate to the instance requested by the verifier.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse,gzip,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/or-r52-resource-path-20260925/code'))
from check_resource import verify as verify_resource


def require(condition,message):
    if not condition:raise ValueError(message)


def checksum(record):
    return hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def canonical_value(t,book,r,q,g):
    if t>=book[-1]:return r*book[-1]-q*book[-1]**2/2-g*(t-book[-1])**2/2
    for u,v in zip(book,book[1:]):
        if u<=t<=v:
            return ((v-t)*(r*u-q*u*u/2)+(t-u)*(r*v-q*v*v/2))/(v-u)
    raise ValueError('Target outside the local canonical interval')


def independent_bound(model,catalog,z):
    """For quadratic primitives, maxima occur at canonical breakpoints."""
    w,b,g,tau=[tuple(map(F,model[key])) for key in ('weights','caps','gamma','ceilings')]
    r,q=F(model['r']),F(model['curvature']);answer=None
    for u in catalog:
        if u>=z:continue
        for v in [x for x in catalog if x>z]+[None]:
            total=F(0)
            for pj,bj,gj,tj in zip(w,b,g,tau):
                if tj<z or bj<=u:continue
                old=[u];new=[u,z]
                if v is not None and tj>=v:old.append(v);new.append(v)
                candidates={u,bj}|{x for x in new if u<=x<=bj}
                vals=[canonical_value(t,new,r,q,gj)-canonical_value(t,old,r,q,gj) for t in candidates]
                total+=pj*max(vals)
            answer=total if answer is None else max(answer,total)
    require(answer is not None,'A deleted candidate has no predecessor')
    return answer


def verify(cert,expected_sha256=None):
    start=time.perf_counter();require(cert['schema']=='NDU-catalog-screen-v1','Unsupported screening schema')
    orig=cert['original'];sha=checksum(orig)
    require(sha==cert['instance_sha256'],'Original-instance digest mismatch')
    if expected_sha256 is not None:require(sha==expected_sha256,'Certificate is for a different requested instance')
    model=orig['model'];w,b,g,tau=[tuple(map(F,model[key])) for key in ('weights','caps','gamma','ceilings')]
    require(len(b)>0 and len(w)==len(b)==len(g)==len(tau),'Inconsistent history vectors')
    require(all(x>0 for x in w) and sum(w)==1,'Invalid weights')
    require(all(0<=bj<=1 and tj>=bj and gj>=0 for bj,tj,gj in zip(b,tau,g)),'Invalid primitives')
    r,q=F(model['r']),F(model['curvature']);require(r>0 and 0<=q<=r,'Invalid reward')
    a=list(map(F,orig['catalog']));rho=list(map(F,orig['charges']));B=F(orig['promise']);eps=F(orig['epsilon']);budget=orig['budget']
    require(a and a==sorted(set(a)) and 0<=a[0]<=a[-1]<=1,'Invalid catalog')
    require(len(a)==len(rho) and all(x>=0 for x in rho),'Invalid charges')
    require(type(budget)==int and budget>=1 and eps>0,'Invalid budget or accuracy')
    require(0<=B<=sum(x*y for x,y in zip(w,b)) and a[0]<=min(B,min(b)),'Infeasible original instance')
    for rec in cert['deletions']:
        z=F(rec['candidate']);require(z in a,'Missing or duplicated deletion')
        require(z>min(B,min(b)),'Possible anchor cannot be deleted by this theorem')
        actual=independent_bound(model,a,z)
        require(F(rec['gain_bound'])==actual,'False deletion bound')
        i=a.index(z);require(F(rec['charge'])==rho[i] and rho[i]>=actual,'Undominated deletion')
        require(type(rec['strict'])==bool and rec['strict']==(rho[i]>actual),'Incorrect strictness flag')
        u=F(rec['predecessor']);v=None if rec['successor'] is None else F(rec['successor'])
        require(u==a[0] and u<z and v is None,'Invalid anchor-envelope maximizing context')
        a.pop(i);rho.pop(i)
    base=cert['resource_certificate']
    for key in ('model','promise'):
        require(base[key]==orig[key],f'Reduced certificate changed {key}')
    require(list(map(F,base['catalog']))==a and list(map(F,base['charges']))==rho,'Retained model mismatch')
    require(base['budget']==min(budget,len(a)) and F(base['epsilon'])==eps,'Reduced budget or accuracy mismatch')
    checked=verify_resource(base)
    return dict(status='PASS',instance_sha256=sha,deleted=len(cert['deletions']),retained=len(a),
                lower=checked['lower'],upper=checked['upper'],gap=checked['gap'],
                seconds=time.perf_counter()-start)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('certificate');p.add_argument('--expected-sha256');args=p.parse_args()
    opener=gzip.open if args.certificate.endswith('.gz') else open
    with opener(args.certificate,'rt') as f:cert=json.load(f)
    print(json.dumps(verify(cert,args.expected_sha256),indent=2))
