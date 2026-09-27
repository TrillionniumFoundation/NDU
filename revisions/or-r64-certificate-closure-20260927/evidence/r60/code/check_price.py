"""Independent exact verifier. Imports no design optimizer or antecedent module.

Price support is constructed from marginal segments and endpoint/stationary
maxima. A backward at-most-budget recurrence checks each covering-tree leaf.
"""
from rational import F, qstr
import json,gzip,hashlib,time,sys


def require(ok,message):
    if not ok:raise ValueError(message)


def fingerprint(spec):return hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def model(spec):
    z=spec['model'];w,b,g,t,r,q=[tuple(map(F,z[key])) for key in ('weights','caps','gamma','ceilings','reward_r','reward_q')]
    k=len(b);require(k and all(len(v)==k for v in (w,g,t,r,q)),'Invalid history dimensions')
    require(all(x>0 for x in w) and sum(w)==1,'Invalid probabilities')
    require(all(0<=bj<=1 and tj>=bj and gj>=0 and rj>0 and 0<=qj<=rj for bj,tj,gj,rj,qj in zip(b,t,g,r,q)),'Invalid primitives')
    a=tuple(map(F,spec['catalog']));rho=tuple(map(F,spec['charges']));B=F(spec['promise']);m=spec['budget']
    require(a and a==tuple(sorted(set(a))) and 0<=a[0]<=a[-1]<=1,'Invalid catalog')
    require(len(a)==len(rho) and all(x>=0 for x in rho),'Invalid charges')
    require(type(m)==int and 1<=m and 0<=B<=sum(x*y for x,y in zip(w,b)),'Invalid promise/budget')
    require(a[0]<=min(B,min(b)),'Infeasible model')
    return w,b,g,t,r,q,a,rho,B,min(m,len(a))


def check_policy(spec,p):
    w,b,g,t,r,q,a,rho,B,m=model(spec);book=tuple(map(F,p['book']))
    require(book==tuple(sorted(set(book))) and 1<=len(book)<=m and all(x in a for x in book),'Invalid book')
    y=tuple(map(F,p['intermediate']));target=tuple(map(F,p['targets']));laws=p['lotteries']
    require(len(y)==len(target)==len(laws)==len(b),'Invalid allocation dimensions')
    value=root=F(0)
    for j,law in enumerate(laws):
        law=[(F(x),F(prob)) for x,prob in law]
        require(y[j]>=0 and law and all(x in book and p>=0 for x,p in law) and sum(p for x,p in law)==1,'Invalid lottery')
        require(all(y[j]+x<=t[j] for x,p in law if p),'Realization ceiling violated')
        tj=y[j]+sum(x*p for x,p in law)
        require(tj==target[j] and 0<=tj<=b[j],'Expected cap violated')
        root+=w[j]*tj
        value+=w[j]*(sum(p*(r[j]*x-q[j]*x*x/2) for x,p in law)-g[j]*y[j]*y[j]/2)
    value-=sum(rho[a.index(x)] for x in book)
    require(root==B and value==F(p['value']),'Invalid root equality or payoff')
    return value


def support_weights(spec,lam):
    w,b,g,t,r,q,a,rho,B,m=model(spec);n=len(a);same=len(set(zip(r,q)))==1
    potential=[sum(p*min(c,u) for p,c in zip(w,b)) for u in a]
    reward=lambda j,x:r[j]*x-q[j]*x*x/2
    edge={};tail=[]
    for i,u in enumerate(a):
        events=sorted((t[j],j) for j in range(len(b)) if b[j]>u)
        costs=[]
        for threshold,j in events:
            c=b[j]-u;points={F(0),c}
            if g[j]>0 and 0<=-lam/g[j]<=c:points.add(-lam/g[j])
            costs.append((w[j]*c,w[j]*max(-g[j]*x*x/2-lam*x for x in points)))
        pos=0;cap=cost=F(0)
        for v in range(i+1,n):
            while pos<len(events) and events[pos][0]<a[v]:
                dc,df=costs[pos];cap+=dc;cost+=df;pos+=1
            if same:
                delta=potential[v]-potential[i]-cap
                require(delta>=0,'Negative terminal capacity')
                terminal=max(F(0),r[0]-q[0]*(u+a[v])/2-lam)*delta
            else:
                terminal=sum(w[j]*max(F(0),min(b[j],a[v])-u)*max(F(0),(reward(j,a[v])-reward(j,u))/(a[v]-u)-lam)
                             for j in range(len(b)) if t[j]>=a[v])
            edge[i,v]=cost+terminal
        tail.append(sum((c for mass,c in costs),F(0)))
    base=[sum(w[j]*reward(j,u) for j in range(len(b)))-lam*u-rho[i] for i,u in enumerate(a)]
    return edge,tail,base


def price_bound(spec,lam,required,forbidden,cache):
    w,b,g,t,r,q,a,rho,B,m=model(spec);n=len(a)
    if len(required)>m or required&forbidden:return None
    if lam not in cache:cache[lam]=support_weights(spec,lam)
    edge,tail,base=cache[lam];available=[i for i in range(n) if i not in forbidden]
    finish=lambda u:not any(z>u for z in required)
    follow=lambda u,v:not any(u<z<v for z in required)
    # At most s commands starting with u. Never relies on the optimizer's tables.
    old={u:tail[u] if finish(u) else None for u in available}
    for slots in range(2,m+1):
        new={}
        for u in reversed(available):
            choices=([tail[u]] if finish(u) else [])+[edge[u,v]-rho[v]+old[v] for v in available
                     if v>u and old[v] is not None and follow(u,v)]
            new[u]=max(choices) if choices else None
        old=new
    choices=[base[u]+old[u] for u in available if a[u]<=min(B,min(b)) and old[u] is not None and not any(z<u for z in required)]
    return lam*B+max(choices) if choices else None


def verify(cert,expected_sha256=None):
    begin=time.perf_counter();require(cert['schema']=='NDU-price-path-v2-hex','Unsupported certificate')
    spec=cert['spec'];sha=fingerprint(spec)
    require(sha==cert['instance_sha256'],'Instance digest mismatch')
    if expected_sha256 is not None:require(sha==expected_sha256,'Wrong requested instance')
    w,b,g,t,r,q,a,rho,B,m=model(spec);lower=check_policy(spec,cert['policy'])
    require(lower==F(cert['lower']),'False lower bound');require(F(cert['epsilon'])>=0,'Invalid accuracy')
    cache={};stack=[(cert['tree'],set(),set())];bounds=[];count=0;splitcount=0
    while stack:
        node,required,forbidden=stack.pop()
        if 'split' in node:
            s=node['split'];i=s['index'];require(type(i)==int and 0<=i<len(a) and i not in required|forbidden,'Invalid tree split')
            require(set(s)=={'index','included','excluded'},'Incomplete binary cover')
            stack.append((s['included'],required|{i},forbidden));stack.append((s['excluded'],required,forbidden|{i}));splitcount+=1
            continue
        proof=node['proof'];kind=proof['type'];count+=1
        if kind=='universal':
            ub=sum(p*(rr-qq/2) for p,rr,qq in zip(w,r,q));require(ub==F(proof['upper']),'Invalid universal upper')
        elif kind=='price':
            ub=price_bound(spec,F(proof['price']),required,forbidden,cache)
            # An inherited parent price bound may be deliberately looser.
            require(ub is None or ub<=F(proof['upper']),'Invalid price upper')
            ub=F(proof['upper'])
        elif kind=='infeasible':
            ub=price_bound(spec,F(0),required,forbidden,cache);require(ub is None and proof['upper'] is None,'False infeasibility')
        else:raise ValueError('Unknown leaf type')
        if ub is not None:bounds.append(ub)
    upper=max([lower]+bounds);require(upper==F(cert['upper']),'Invalid global upper')
    require(lower<=upper,'Reversed interval')
    return dict(status='PASS',lower=qstr(lower),upper=qstr(upper),gap=qstr(upper-lower),
                tolerance_met=upper-lower<=F(cert['epsilon']),leaves=count,splits=splitcount,prices=len(cache),
                seconds=time.perf_counter()-begin,instance_sha256=sha)


def verify_common_cap(cert,expected_sha256=None):
    """Independent original-response support check for every singleton/pair."""
    from itertools import combinations
    begin=time.perf_counter();require(cert['schema']=='NDU-common-cap-v1','Unsupported common-cap schema')
    spec=cert['spec'];sha=fingerprint(spec);require(sha==cert['instance_sha256'],'Instance mismatch')
    if expected_sha256 is not None:require(sha==expected_sha256,'Wrong requested instance')
    w,b,g,t,r,q,a,rho,B,m=model(spec)
    require(len(set(b))==1 and len(set(zip(r,q)))==1,'Common-cap theorem does not apply')
    expected={ids for size in range(1,min(m,2)+1) for ids in combinations(range(len(a)),size) if a[ids[0]]<=min(B,b[0])}
    require(len(cert['books'])==len(expected),'Incomplete singleton/pair cover')
    seen=set();bounds=[]
    for rec in cert['books']:
        ids=tuple(rec['indices']);require(ids in expected and ids not in seen,'Invalid/duplicate pair');seen.add(ids)
        lam=F(rec['price']);upper=lam*B-sum(rho[i] for i in ids)
        for j in range(len(b)):
            knots=[a[i] for i in ids if a[i]<=t[j]];d=knots[-1]
            candidates={knots[0],b[j]}|{x for x in knots if x<=b[j]}
            if g[j]>0:candidates.add(min(b[j],max(knots[0],d-lam/g[j])))
            def reward(x):return r[j]*x-q[j]*x*x/2
            scores=[]
            for target in candidates:
                mu=min(target,d)
                if mu in knots:value=reward(mu)
                else:
                    u=max(x for x in knots if x<mu);v=min(x for x in knots if x>mu)
                    value=((v-mu)*reward(u)+(mu-u)*reward(v))/(v-u)
                scores.append(value-g[j]*max(F(0),target-d)**2/2-lam*target)
            upper+=w[j]*max(scores)
        require(upper==F(rec['upper']),'Invalid fixed-book supporting-price bound');bounds.append(upper)
    lower=check_policy(spec,cert['policy']);upper=max(bounds)
    require(lower==upper==F(cert['lower'])==F(cert['upper']),'Common-cap global equality failed')
    return dict(status='PASS',books=len(seen),lower=qstr(lower),upper=qstr(upper),seconds=time.perf_counter()-begin)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('certificate');p.add_argument('--expected-sha256');args=p.parse_args()
    opener=gzip.open if args.certificate.endswith('.gz') else open
    with opener(args.certificate,'rt') as f:certificate=json.load(f)
    check=verify_common_cap if certificate.get('schema')=='NDU-common-cap-v1' else verify
    print(json.dumps(check(certificate,args.expected_sha256),indent=2))

