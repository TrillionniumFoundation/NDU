"""Constructive heterogeneous terminal components followed by history packing."""
from fractions import Fraction as F
from pathlib import Path
import sys
from price_path import encode
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/or-r49-dispersion-certificates-20260925/code'))
from pooling import capped_cost

def edges(d,book):
    ans=[]
    for u,v in list(zip(book,book[1:]))+[(book[-1],None)]:
        terminal=[]
        if v is not None:
            for j,(b,t,w) in enumerate(zip(d.caps,d.ceilings,d.weights)):
                cap=max(F(0),min(b,v)-u) if t>=v else F(0)
                if cap:terminal.append((d.reward_r[j]-d.reward_q[j]*(u+v)/2,j,cap))
        ids=[j for j,t in enumerate(d.ceilings) if t>=u and (v is None or t<v)]
        caps=[max(F(0),d.caps[j]-u) for j in ids]
        T=sum(d.weights[j]*c for slope,j,c in terminal);Q=sum(d.weights[j]*c for j,c in zip(ids,caps))
        ans.append(dict(u=u,v=v,terminal=terminal,ids=ids,caps=caps,T=T,Q=Q,C=T+Q))
    return ans

def reconstruct(d,book,B,charges,resources):
    es=edges(d,book);require=lambda x:None if x else (_ for _ in ()).throw(ValueError('Invalid component resources'))
    require(len(resources)==len(es) and sum(resources)==B-book[0])
    targets=[book[0]]*len(d.caps);score=d.mean_reward(book[0])
    for edge,x in zip(es,resources):
        require(0<=x<=edge['C']);mass=min(x,edge['T'])
        for slope,j,c in sorted(edge['terminal'],reverse=True):
            take=min(mass,d.weights[j]*c);targets[j]+=take/d.weights[j];score+=slope*take;mass-=take
        require(mass==0);y=max(F(0),x-edge['T']);ids=edge['ids']
        alloc=capped_cost(tuple(d.weights[j] for j in ids),tuple(d.gamma[j] for j in ids),tuple(edge['caps']),y)
        score-=alloc['cost']
        for j,z in zip(ids,alloc['service']):targets[j]+=z
    laws=[];ys=[];gross=F(0)
    for j,t in enumerate(targets):
        eligible=[z for z in book if z<=d.ceilings[j]];last=eligible[-1];y=max(F(0),t-last);mu=t-y
        if mu in eligible:law=[(mu,F(1))]
        else:
            u=max(z for z in eligible if z<mu);v=min(z for z in eligible if z>mu);law=[(u,(v-mu)/(v-u)),(v,(mu-u)/(v-u))]
        laws.append(law);ys.append(y);gross+=d.weights[j]*(sum(p*d.reward(j,z) for z,p in law)-d.gamma[j]*y*y/2)
    require(gross>=score)
    return dict(book=book,targets=targets,intermediate=ys,lotteries=laws,gross=gross,value=gross-sum(charges[z] for z in book)),score

def from_policy(d,book,policy):
    resource=[]
    for e in edges(d,book):
        x=F(0)
        if e['v'] is not None:
            for slope,j,c in e['terminal']:
                mu=policy['targets'][j]-policy['intermediate'][j]
                x+=d.weights[j]*max(F(0),min(mu,e['v'])-e['u'])
        x+=sum(d.weights[j]*policy['intermediate'][j] for j in e['ids'])
        resource.append(x)
    return resource
