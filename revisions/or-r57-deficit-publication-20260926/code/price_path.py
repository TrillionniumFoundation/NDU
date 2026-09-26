"""Grid-free rational renewal optimization, with complete branching certificates.

Heterogeneous increasing concave quadratic terminal rewards are allowed.
Every interrupted search returns a mathematically valid enclosing interval.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from fractions import Fraction
from rational import F, qstr
from math import lcm
import hashlib, json, time


class DeadlineExceeded(Exception):
    """Raised by the external, measured algorithm-time alarm."""


def encode(x):
    if isinstance(x,Fraction): return qstr(x)
    if isinstance(x,dict): return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)): return [encode(v) for v in x]
    return x


def digest(spec):
    return hashlib.sha256(json.dumps(encode(spec),sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class Model:
    caps: tuple
    weights: tuple
    gamma: tuple
    ceilings: tuple
    reward_r: tuple
    reward_q: tuple

    @classmethod
    def make(cls,caps,weights,gamma,ceilings,reward_r=2,reward_q=1):
        b,w,g,t=map(lambda v:tuple(map(F,v)),(caps,weights,gamma,ceilings));k=len(b)
        vector=lambda v:tuple(map(F,v)) if isinstance(v,(list,tuple)) else (F(v),)*k
        r,q=vector(reward_r),vector(reward_q)
        if not k or any(len(v)!=k for v in (w,g,t,r,q)):raise ValueError('Inconsistent model lengths')
        if sum(w)!=1 or any(x<=0 for x in w):raise ValueError('Positive probabilities summing to one required')
        if any(not (0<=bj<=1 and tj>=bj and gj>=0 and rj>0 and 0<=qj<=rj) for bj,tj,gj,rj,qj in zip(b,t,g,r,q)):
            raise ValueError('Invalid model primitives')
        return cls(b,w,g,t,r,q)

    @property
    def cap_total(self):return sum(w*b for w,b in zip(self.weights,self.caps))
    @property
    def common(self):return len(set(zip(self.reward_r,self.reward_q)))==1
    def reward(self,j,x):return self.reward_r[j]*x-self.reward_q[j]*x*x/2
    def mean_reward(self,x):return sum(w*self.reward(j,x) for j,w in enumerate(self.weights))


def normalize(spec):
    d=Model.make(**spec['model']);a=tuple(map(F,spec['catalog']));rho=tuple(map(F,spec['charges']))
    B=F(spec['promise']);m=spec['budget']
    if not a or a!=tuple(sorted(set(a))) or not 0<=a[0]<=a[-1]<=1:raise ValueError('Invalid catalog')
    if len(rho)!=len(a) or any(x<0 for x in rho):raise ValueError('Invalid charges')
    if type(m)!=int or m<1 or not 0<=B<=d.cap_total or a[0]>min(B,min(d.caps)):raise ValueError('Infeasible problem')
    return d,a,rho,B,min(m,len(a))


def spec_for(d,a,rho,B,m):
    return encode(dict(model=asdict(d),catalog=a,charges=rho,promise=B,budget=m))


def allocate(d,book,B,charges):
    """Exact fixed-book allocation by original history-level marginal segments."""
    book=tuple(book);a=book[0];mass=B-a;k=len(d.caps)
    if mass<0 or a>min(d.caps) or B>d.cap_total:raise ValueError('Infeasible fixed book')
    targets=[a]*k;last=[];segments=[]
    for j,(b,tau,w) in enumerate(zip(d.caps,d.ceilings,d.weights)):
        eligible=[z for z in book if z<=tau];last.append(eligible[-1])
        for ix,(u,v) in enumerate(zip(eligible,eligible[1:])):
            c=max(F(0),min(b,v)-u)
            if c:segments.append((d.reward_r[j]-d.reward_q[j]*(u+v)/2,j,ix,c))
    segments.sort(key=lambda z:(-z[0],z[1],z[2]))
    price=max((x[0] for x in segments),default=F(0))
    for slope,j,ix,c in segments:
        if not mass:break
        take=min(mass,d.weights[j]*c);targets[j]+=take/d.weights[j];mass-=take;price=slope
    ys=[F(0)]*k
    if mass:
        caps=[max(F(0),b-z) for b,z in zip(d.caps,last)]
        for j,(g,c,w) in enumerate(zip(d.gamma,caps,d.weights)):
            if not g:
                take=min(mass,w*c);ys[j]=take/w;mass-=take
        price=F(0)
        if mass:
            active=[j for j,(g,c) in enumerate(zip(d.gamma,caps)) if g and c]
            remaining=mass;recip=sum(d.weights[j]/d.gamma[j] for j in active)
            alpha=F(0)
            for j in sorted(active,key=lambda i:d.gamma[i]*caps[i]):
                candidate=remaining/recip
                if candidate<=d.gamma[j]*caps[j]:alpha=candidate;break
                remaining-=d.weights[j]*caps[j];recip-=d.weights[j]/d.gamma[j]
            else:
                if remaining:raise ArithmeticError('Unallocated service')
            for j in active:ys[j]=min(caps[j],alpha/d.gamma[j])
            price=-alpha
        for j in range(k):targets[j]+=ys[j]
    laws=[];gross=F(0)
    for j,t in enumerate(targets):
        mu=t-ys[j];eligible=[z for z in book if z<=d.ceilings[j]]
        if mu in eligible:law=[(mu,F(1))]
        else:
            u=max(z for z in eligible if z<mu);v=min(z for z in eligible if z>mu)
            law=[(u,(v-mu)/(v-u)),(v,(mu-u)/(v-u))]
        laws.append(law);gross+=d.weights[j]*(sum(p*d.reward(j,z) for z,p in law)-d.gamma[j]*ys[j]**2/2)
    if sum(w*t for w,t in zip(d.weights,targets))!=B:raise ArithmeticError('Root promise not restored')
    return dict(book=book,targets=targets,intermediate=ys,lotteries=laws,gross=gross,
                value=gross-sum(charges[z] for z in book),price=price)


def support_range(d,book,lam):
    """Compute the minimizing/maximizing targets among a book's price optima."""
    low=high=F(0);a=book[0]
    for j,(w,b,tau,g) in enumerate(zip(d.weights,d.caps,d.ceilings,d.gamma)):
        e=[z for z in book if z<=tau];candidates={a,b}|{z for z in e if z<=b};last=e[-1]
        if g and lam<=0:candidates.add(min(b,max(a,last-lam/g)))
        vals=[]
        for t in candidates:
            mu=min(t,last);cost=g*max(F(0),t-last)**2/2
            if mu in e:f=d.reward(j,mu)
            else:
                u=max(z for z in e if z<mu);v=min(z for z in e if z>mu)
                f=((v-mu)*d.reward(j,u)+(mu-u)*d.reward(j,v))/(v-u)
            vals.append((f-cost-lam*t,t))
        best=max(x for x,t in vals);ts=[t for x,t in vals if x==best]
        low+=w*min(ts);high+=w*max(ts)
    return low,high


class Oracle:
    def __init__(self,d,a,rho,B,m):
        self.d,self.a,self.rho,self.B,self.m=d,a,rho,B,m;self.n=len(a);self.calls=0
        self.alpha=min(B,min(d.caps));self.cache={};self.rows=[];self.T={};self.hetero={}
        p=[sum(w*min(b,u) for w,b in zip(d.weights,d.caps)) for u in a]
        for i,u in enumerate(a):
            row=sorted((tau,j,w,g,b-u) for j,(tau,w,g,b) in enumerate(zip(d.ceilings,d.weights,d.gamma,d.caps)) if b>u)
            self.rows.append(row);pos=0;capacity=F(0)
            for v in range(i+1,self.n):
                while pos<len(row) and row[pos][0]<a[v]:
                    _,j,w,g,c=row[pos];capacity+=w*c;pos+=1
                self.T[i,v]=p[v]-p[i]-capacity
                if not d.common:
                    self.hetero[i,v]=tuple((d.reward_r[j]-d.reward_q[j]*(u+a[v])/2,
                            w*max(F(0),min(b,a[v])-u)) for j,(w,b,tau) in enumerate(zip(d.weights,d.caps,d.ceilings)) if tau>=a[v] and b>u)

    def weights(self,lam):
        if lam in self.cache:return self.cache[lam]
        d,a,n=self.d,self.a,self.n;edges={};tail=[]
        for i,u in enumerate(a):
            row=self.rows[i];pos=0;service=F(0)
            def val(item):
                tau,j,w,g,c=item
                z=min(c,-lam/g) if g else c
                return w*(-g*z*z/2-lam*z)
            for v in range(i+1,n):
                while pos<len(row) and row[pos][0]<a[v]:
                    if lam<0:service+=val(row[pos])
                    pos+=1
                if d.common:terminal=max(F(0),d.reward_r[0]-d.reward_q[0]*(u+a[v])/2-lam)*self.T[i,v]
                else:terminal=sum(max(F(0),s-lam)*c for s,c in self.hetero[i,v])
                edges[i,v]=terminal+service
            if lam<0:
                while pos<len(row):service+=val(row[pos]);pos+=1
            tail.append(service)
        base=[d.mean_reward(u)-lam*u-rho for u,rho in zip(a,self.rho)]
        den=1
        for x in list(edges.values())+tail+base+list(self.rho):den=lcm(den,x.denominator)
        data=(den,{key:int(x*den) for key,x in edges.items()},[int(x*den) for x in tail],
              [int(x*den) for x in base],[int(x*den) for x in self.rho])
        if len(self.cache)<128:self.cache[lam]=data
        return data

    def run(self,lam,required=frozenset(),forbidden=frozenset()):
        self.calls+=1;n,a,m=self.n,self.a,self.m
        if len(required)>m or required&forbidden:return None
        den,edge,tail,base,charges=self.weights(lam)
        allowed=[i for i in range(n) if i not in forbidden]
        first=min(required,default=n);last=max(required,default=-1)
        counts=[sum(x<i for x in required) for i in range(n+1)]
        rows=[{i:base[i] for i in allowed if a[i]<=self.alpha and i<=first}];ptr={}
        best=None;end=None
        for ell in range(1,m+1):
            if ell>1:
                new={}
                for v in allowed:
                    choices=[(score+edge[u,v]-charges[v],-u,u) for u,score in rows[-1].items()
                             if u<v and counts[v]-counts[u+1]==0]
                    if choices:
                        score,_,u=max(choices);new[v]=score;ptr[ell,v]=u
                rows.append(new)
            for u,score in rows[-1].items():
                if u>=last and (best is None or score+tail[u]>best):best=score+tail[u];end=(ell,u)
        if best is None:return None
        ell,u=end;path=[u]
        while ell>1:u=ptr[ell,u];path.append(u);ell-=1
        path.reverse();book=tuple(a[i] for i in path)
        return dict(upper=F(best,den)+lam*self.B,book=book,indices=tuple(path),price=lam)


def leaves(root):
    stack=[(root,frozenset(),frozenset())]
    while stack:
        node,req,ban=stack.pop()
        if 'split' in node:
            s=node['split'];i=s['index']
            stack.append((s['included'],req|{i},ban));stack.append((s['excluded'],req,ban|{i}))
        else:yield node,req,ban


def solve(spec,epsilon=F(0),price_steps=12,max_nodes=255,seconds=None):
    start=time.perf_counter();d,a,rho,B,m=normalize(spec);eps=F(epsilon)
    if eps<0 or price_steps<1 or max_nodes<1:raise ValueError('Invalid search parameters')
    incumbent=allocate(d,(a[0],),B,dict(zip(a,rho)))
    tree={'proof':{'type':'universal','upper':qstr(d.mean_reward(F(1)))}};trace=[];evaluated=0
    oracle=None;status='NODE_LIMIT'
    mechanics={'evaluations':[], 'splits':0, 'incumbent_updates':0, 'bound_prunes':0, 'infeasible_prunes':0, 'fixed_book_closures':0, 'root_gap':None}
    def upper():return max([incumbent['value']]+[F(n['proof']['upper']) for n,r,f in leaves(tree) if n['proof']['type']!='infeasible'])
    def snapshot():
        trace.append(dict(seconds=time.perf_counter()-start,lower=qstr(incumbent['value']),upper=qstr(upper()),
                          nodes=evaluated,oracle_calls=0 if oracle is None else oracle.calls))
    def checktime():
        if seconds is not None and time.perf_counter()-start>=seconds:raise DeadlineExceeded()
    try:
        oracle=Oracle(d,a,rho,B,m)
        while evaluated<max_nodes:
            pending=[(F(n['proof']['upper']),n,r,f) for n,r,f in leaves(tree) if n['proof']['type']!='infeasible' and F(n['proof']['upper'])>incumbent['value']+eps]
            if not pending:status='EXACT' if upper()==incumbent['value'] else 'TOLERANCE';break
            _,node,required,forbidden=max(pending,key=lambda x:x[0]);checktime();evaluated+=1
            mechanics['evaluations'].append(dict(required=len(required),forbidden=len(forbidden),depth=len(required|forbidden),lower=qstr(incumbent['value']),upper=qstr(upper()),oracle_start=oracle.calls))
            lo=-max(d.gamma);hi=max(d.reward_r);lam=sum(w*(r-q*B) for w,r,q in zip(d.weights,d.reward_r,d.reward_q))
            tested=set();chosen=None
            for step in range(price_steps):
                checktime();ans=oracle.run(lam,required,forbidden)
                if ans is None:node['proof']={'type':'infeasible','upper':None};chosen=None;break
                chosen=ans
                if ans['upper']<F(node['proof']['upper']):node['proof']={'type':'price','price':qstr(lam),'upper':qstr(ans['upper'])}
                policy=allocate(d,ans['book'],B,dict(zip(a,rho)))
                if policy['value']>incumbent['value']:incumbent=policy;mechanics['incumbent_updates']+=1
                snapshot()
                if F(node['proof']['upper'])<=incumbent['value']+eps:break
                mn,mx=support_range(d,ans['book'],lam);tested.add(lam)
                if B<mn:lo=max(lo,lam)
                elif B>mx:hi=min(hi,lam)
                else:raise ArithmeticError('A price-feasible book should close this node')
                candidate=policy['price']
                lam=candidate if lo<=candidate<=hi and candidate not in tested else (lo+hi)/2
                if lam in tested:break
            if evaluated==1:mechanics['root_gap']=qstr(upper()-incumbent['value'])
            if node['proof']['type']=='infeasible':mechanics['infeasible_prunes']+=1;continue
            if F(node['proof']['upper'])<=incumbent['value']+eps:mechanics['bound_prunes']+=1;continue
            checktime()
            optional=[i for i in (chosen['indices'] if chosen else range(len(a))) if i not in required|forbidden]
            if not optional:optional=[i for i in range(len(a)) if i not in required|forbidden]
            if len(required)==m or not optional:
                book=tuple(a[i] for i in sorted(required))
                if not book:raise ArithmeticError('Missing feasible fixed book')
                pol=allocate(d,book,B,dict(zip(a,rho)));exact=oracle.run(pol['price'],required,forbidden)
                if exact is None or exact['upper']!=pol['value']:raise ArithmeticError('Fixed-book duality failed')
                node['proof']={'type':'price','price':qstr(pol['price']),'upper':qstr(pol['value'])}
                mechanics['fixed_book_closures']+=1
                if pol['value']>incumbent['value']:incumbent=pol
            else:
                mechanics['splits']+=1
                idx=optional[len(optional)//2];proof=dict(node['proof'])
                node['split']={'index':idx,'excluded':{'proof':dict(proof)},'included':{'proof':dict(proof)}}
            snapshot()
        if upper()-incumbent['value']<=eps:status='EXACT' if upper()==incumbent['value'] else 'TOLERANCE'
    except DeadlineExceeded:status='TIME_LIMIT'
    snapshot();U=upper()
    cert=dict(schema='NDU-price-path-v2-hex',spec=spec_for(d,a,rho,B,spec['budget']),epsilon=qstr(eps),tree=tree,
              policy=encode(incumbent),lower=qstr(incumbent['value']),upper=qstr(U))
    cert['instance_sha256']=digest(cert['spec'])
    return dict(status=status,lower=incumbent['value'],upper=U,gap=U-incumbent['value'],
                seconds=time.perf_counter()-start,nodes=evaluated,oracle_calls=0 if oracle is None else oracle.calls,
                trace=trace,mechanics=mechanics,certificate=cert)
