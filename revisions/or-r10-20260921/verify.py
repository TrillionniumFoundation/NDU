#!/usr/bin/env python3
"""Independent exact replay. Does not import the solver or the learner.

Reconstructs every tree constraint, quartic objective, and derivative directly
from serialized rational primitives. Floating solver status is never evidence.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib, json

BASE=Path(__file__).resolve().parent
R=BASE/'results'

def replay(p,c,static_optimal=True):
    d=p['d'];pa=p['parents'];nodes=len(pa);N=d*nodes
    w=list(map(Q,p['weights']));a=list(map(Q,p['tariffs']));f=list(map(Q,p['forcing']))
    x=list(map(Q,c['policy']));eta=list(map(Q,c['multipliers']))
    m=Q(p['m']);gam=Q(p['gamma']);lam=Q(p['lambda']);zeta=Q(p['zeta']);bar=Q(1,2)
    assert len(x)==N and len(eta)==nodes
    assert all(0<=v<=1 for v in x) and min(eta)>=0
    A=[];b=[]
    for n in range(nodes):
        A.append(sum((w[n*d+j]*a[n*d+j]*x[n*d+j] for j in range(d)),Q(0)))
        b.append(sum((w[n*d+j]*a[n*d+j]*bar for j in range(d)),Q(0)))
    for n in range(nodes-1,0,-1):A[pa[n]]+=A[n];b[pa[n]]+=b[n]
    slack=[v-u for u,v in zip(A,b)]
    assert min(slack)>=0
    grad=[w[i]*(2*m*x[i]+4*gam*x[i]**3) for i in range(N)]
    def value(y):
        total=sum((w[i]*(f[i]*y[i]-m*y[i]**2-gam*y[i]**4) for i in range(N)),Q(0))
        for n in range(nodes):
            for j in range(d):
                i=n*d+j;q=bar if n==0 else y[pa[n]*d+j]
                total-=lam*w[i]*(y[i]-q)**2
            for j,k,v in p['edges']:total-=zeta*w[n*d]*v*(y[n*d+j]-y[n*d+k])**2
        return total
    for n in range(nodes):
        for j in range(d):
            i=n*d+j;q=bar if n==0 else x[pa[n]*d+j]
            term=2*lam*w[i]*(x[i]-q);grad[i]+=term
            if n:grad[pa[n]*d+j]-=term
        for j,k,v in p['edges']:
            i=n*d+j;l=n*d+k;term=2*zeta*w[n*d]*v*(x[i]-x[l])
            grad[i]+=term;grad[l]-=term
    r=[]
    for i in range(N):
        n=i//d;mult=Q(0)
        while n>=0:mult+=eta[n];n=pa[n]
        r.append(w[i]*f[i]-grad[i]-w[i]*a[i]*mult)
    gap=sum((v*v/(4*m*wi) for v,wi in zip(r,w)),Q(0))+sum((v*s for v,s in zip(eta,slack)),Q(0))
    assert value(x)==Q(c['value_fraction'])
    assert value([bar]*N)==Q(c['static_fraction'])
    assert gap==Q(c['bound_fraction'])
    assert min(slack)==Q(c['minimum_slack_fraction'])
    if static_optimal:assert sum((wi*(fi-2*m*bar-4*gam*bar**3) for wi,fi in zip(w,f)),Q(0))==0
    return len(slack),N

def replay_quadratic(p,c):
    d=p['d'];den=c['tier_denominator'];x=[Q(v,den) for v in c['tier_numerators']]
    eta=Q(c['dual_numerator'],c['dual_denominator']);a=[Q(v,100) for v in p['a_integers']]
    K={}
    for i in range(d):
        for k in range(p['K_indptr'][i],p['K_indptr'][i+1]):
            K[i,p['K_indices'][k]]=Q(p['K_numerators'][k],10)
    assert all(K[i,j]==K.get((j,i),0) for i,j in K)
    for i in range(d):
        assert sum((v for (ii,j),v in K.items() if ii==i),Q(0))==Q(21,10)
    assert all(v<=0 for (i,j),v in K.items() if i!=j)
    kx=[Q(0)]*d
    for (i,j),v in K.items():kx[i]+=v*x[j]
    As=sum(a,Q(0));theta=(As+Q(3*d,5))/Q(21*d,5);cap=As*theta
    C=sum((Q(103+30*(i%3),100) for i in range(d)),Q(0))
    value=sum(((ai+Q(3,5))*xi-xi*ki for ai,xi,ki in zip(a,x,kx)),Q(0))-Q(3*d,20)-C
    static=As*theta-Q(3*d,2)*theta**2-Q(3*d,5)*(theta-Q(1,2))**2-C
    slack=cap-sum((ai*xi for ai,xi in zip(a,x)),Q(0))
    assert slack>=0 and eta>=0 and all(0<=xi<=1 for xi in x)
    r=[(1-eta)*ai+Q(3,5)-2*ki for ai,ki in zip(a,kx)]
    bound=Q(5,42)*sum((v*v for v in r),Q(0))+eta*slack
    assert value==Q(c['exact_value_fraction'])
    assert value-static==Q(c['exact_gain_fraction'])
    assert slack==Q(c['exact_customer_slack_fraction']) and bound==Q(c['exact_loss_bound_fraction'])

def run():
    problems={p['id']:p for p in json.loads((R/'nonlinear_problems.json').read_text())}
    records=json.loads((R/'nonlinear_records.json').read_text());nodes=0;coordinates=0
    for r in records:
        n,N=replay(problems[r['problem']],r['certificate']);nodes+=n;coordinates+=N
    train=json.loads((R/'nonlinear_training.json').read_text());teachers=0;max_oracle_gap=0.;max_fd_error=0.
    for seed in train:
        for t in seed['teacher_records']:
            p=t['problem'];dire=t['direction']
            for endpoint in t['certified_oracle_records']:
                q=dict(p);s=endpoint['sign']
                q['forcing']=[str(Q(v)+Q(s,40)*u) for v,u in zip(p['forcing'],dire)]
                replay(q,endpoint['certificate'],static_optimal=(s==0));teachers+=1
                max_oracle_gap=max(max_oracle_gap,endpoint['certificate']['upper_gap'])
            max_fd_error=max(max_fd_error,t['directional_error_bound'])
    qp={f"{p['d']}-{p['rep']}":p for p in json.loads((R/'cached_quadratic_problems.json').read_text())}
    qr=json.loads((R/'cached_quadratic_records.json').read_text())
    for record in qr:replay_quadratic(qp[record['problem']],record['certificate'])
    summary={'status':'PASS','independent_of_solver':True,'deployment_records':len(records),
        'cached_quadratic_records':len(qr),'exact_continuation_checks':nodes,'exact_tier_checks':coordinates,'oracle_records':teachers,
        'max_teacher_upper_gap':max_oracle_gap,'max_normalized_directional_error_bound':max_fd_error,
        'method':'Python fractions; objective, all subtree inequalities and nonlinear residual reconstructed from primitives',
        'source_sha256':{x:hashlib.sha256((BASE/x).read_bytes()).hexdigest() for x in ['nonlinear_control.py','verify.py']}}
    (R/'independent_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
