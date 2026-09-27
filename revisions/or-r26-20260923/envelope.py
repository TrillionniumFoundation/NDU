#!/usr/bin/env python3
"""Continuous promised-payment envelopes. SciPy proposes; replay.py certifies.
No history tree is constructed. Every stored number is a rational string.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse, json, time
import numpy as np
from scipy.optimize import linprog
R=Path(__file__).resolve().parent

def f(x): return F(str(x))
def clip(x,l,h): return min(h,max(l,x))
SCALE=10**12
def down(v): return F((v*SCALE).__floor__(),SCALE)
def up(v): return F((v*SCALE).__ceil__(),SCALE)

def support_quadratic(v,d):
    x=clip(v/d,F(0),F(1)); return v*x-d*x*x/2

def solve_exact(rows, rhs, n):
    a=[list(r)+[v] for r,v in zip(rows,rhs)]; piv=[]; rr=0
    for col in range(n):
        k=next((k for k in range(rr,len(a)) if a[k][col]),None)
        if k is None: continue
        a[rr],a[k]=a[k],a[rr]; d=a[rr][col]; a[rr]=[x/d for x in a[rr]]
        for k in range(len(a)):
            if k!=rr and a[k][col]:
                d=a[k][col]; a[k]=[u-d*v for u,v in zip(a[k],a[rr])]
        piv.append(col); rr+=1
    if any(not any(r[:-1]) and r[-1] for r in a): raise ValueError('inconsistent rational basis')
    if len(piv)!=n: raise ValueError('nonunique rational basis')
    out=[F(0)]*n
    for i,c in enumerate(piv): out[c]=a[i][-1]
    return out

def lower_proposal(q,b,p,child,m):
    beta,a,r,d,ell=p['beta'],p['a'],p['r'],p['d'],p['ell']
    grid=[F(i,m) for i in range(m+1)]; off=[len(grid)]
    for ch in child: off.append(off[-1]+len(ch['anchors']))
    n=off[-1]+1; ab=n-1
    c=[F(0)]*n
    for i,x in enumerate(grid): c[i]=-(r*x-d*x*x/2)
    for j,ch in enumerate(child):
        for i,an in enumerate(ch['anchors']): c[off[j]+i]=-beta*p['P'][j]*an['value']
    c[ab]=ell
    rows=[]; rhs=[]
    def row(): return [F(0)]*n
    v=row(); v[:len(grid)]=[F(1)]*len(grid); rows.append(v); rhs.append(F(1))
    for j,ch in enumerate(child):
        v=row()
        for i in range(len(ch['anchors'])): v[off[j]+i]=F(1)
        rows.append(v); rhs.append(F(1))
        v=row(); v[:len(grid)]=[-x for x in grid]
        for i,an in enumerate(ch['anchors']): v[off[j]+i]=an['q']
        rows.append(v); rhs.append(F(0))
    v=row(); v[:len(grid)]=[a*x for x in grid]
    for j,ch in enumerate(child):
        for i,an in enumerate(ch['anchors']): v[off[j]+i]=beta*p['P'][j]*an['b']
    rows.append(v); rhs.append(b)
    u1=row(); u1[:len(grid)]=grid; u1[ab]=-1
    u2=row(); u2[:len(grid)]=[-x for x in grid]; u2[ab]=-1
    ub=[u1,u2]; bh=[q,-q]
    res=linprog(np.array(c,float),A_ub=np.array(ub,float),b_ub=np.array(bh,float),A_eq=np.array(rows,float),b_eq=np.array(rhs,float),bounds=[(0,None)]*n,method='highs')
    if not res.success: raise RuntimeError(res.message)
    supp=[i for i,x in enumerate(res.x) if x>1e-9]
    erows=[[r0[i] for i in supp] for r0 in rows]; erhs=list(rhs)
    for ur,bb in zip(ub,bh):
        if abs(float(np.dot(np.array(ur,float),res.x))-float(bb))<1e-7:
            erows.append([ur[i] for i in supp]); erhs.append(bb)
    xx=solve_exact(erows,erhs,len(supp)); v=[F(0)]*n
    for i,x in zip(supp,xx): v[i]=x
    if min(v)<0 or any(sum(x*y for x,y in zip(rr,v))!=h for rr,h in zip(rows,rhs)): raise ValueError('rational primal equality')
    if any(sum(x*y for x,y in zip(rr,v))>h for rr,h in zip(ub,bh)): raise ValueError('rational primal inequality')
    x=sum(v[i]*g for i,g in enumerate(grid))
    mixes=[]; future=F(0)
    for j,ch in enumerate(child):
        mix=[[i,v[off[j]+i]] for i in range(len(ch['anchors'])) if v[off[j]+i]]
        mixes.append(mix)
        future+=beta*p['P'][j]*sum(w*ch['anchors'][i]['value'] for i,w in mix)
    value=r*x-d*x*x/2-ell*abs(x-q)+future
    return {'q':q,'b':b,'x':x,'children':mixes,'value':down(value)}

def upper_proposal(q,b,p,child,m):
    beta,a,r,d,ell=p['beta'],p['a'],p['r'],p['d'],p['ell']
    # variables: x, absolute difference, stage hypograph, child budgets, child hypographs
    S=len(child); n=3+2*S; c=np.zeros(n); c[1]=float(ell); c[2]=-1
    for j in range(S): c[3+S+j]=-float(beta*p['P'][j])
    rows=[]; rhs=[]
    v=np.zeros(n);v[0]=1;v[1]=-1;rows.append(v);rhs.append(float(q))
    v=np.zeros(n);v[0]=-1;v[1]=-1;rows.append(v);rhs.append(float(-q))
    for i in range(m+1):
        h=F(i,m);v=np.zeros(n);v[2]=1;v[0]=-float(r-d*h);rows.append(v);rhs.append(float(d*h*h/2))
    starts=[]
    for j,ch in enumerate(child):
        starts.append(len(rows))
        for h in ch['planes']:
            v=np.zeros(n);v[3+S+j]=1;v[0]=-float(h['A']);v[3+j]=-float(h['B']);rows.append(v);rhs.append(float(h['C']))
    eq=np.zeros(n);eq[0]=float(a)
    for j in range(S):eq[3+j]=float(beta*p['P'][j])
    bounds=[(0,1),(0,None),(None,None)]+[(float(ch['L']),float(ch['U'])) for ch in child]+[(None,None)]*S
    res=linprog(c,A_ub=np.array(rows),b_ub=rhs,A_eq=[eq],b_eq=[float(b)],bounds=bounds,method='highs')
    if not res.success:raise RuntimeError(res.message)
    eta=F(float(-res.eqlin.marginals[0])).limit_denominator(10**7)
    s=clip(F(float(res.ineqlin.marginals[1]-res.ineqlin.marginals[0])).limit_denominator(10**7),-ell,ell)
    mixtures=[]; av=[]
    for j,ch in enumerate(child):
        weights=[max(F(0),F(float(-res.ineqlin.marginals[starts[j]+k])).limit_denominator(10**7)) for k in range(len(ch['planes']))]
        sm=sum(weights)
        if sm==0: weights[0]=F(1);sm=F(1)
        weights=[w/sm for w in weights]
        mix=[[i,w] for i,w in enumerate(weights) if w];mixtures.append(mix)
        av.append({key:sum(w*ch['planes'][i][key] for i,w in mix) for key in ('A','B','C')})
    v=r-s-a*eta+beta*sum(p['P'][j]*av[j]['A'] for j in range(S))
    C=support_quadratic(v,d)+beta*sum(p['P'][j]*(av[j]['C']+max((av[j]['B']-eta)*child[j]['L'],(av[j]['B']-eta)*child[j]['U'])) for j in range(S))
    return {'A':s,'B':eta,'C':up(C),'children':mixtures}

def certificate_width(node,m):
    # Every cell is split into two triangles. A single global plane per triangle
    # gives an outward bound, not an assertion that corner gaps alone suffice.
    worst=F(0)
    for i in range(m):
        for j in range(m):
            v00=i*(m+1)+j;v01=v00+1;v10=(i+1)*(m+1)+j;v11=v10+1
            for inds in ((v00,v01,v11),(v00,v10,v11)):
                gap=min(max(h['A']*node['anchors'][k]['q']+h['B']*node['anchors'][k]['b']+h['C']-node['anchors'][k]['value'] for k in inds) for h in node['planes'])
                worst=max(worst,gap)
    return worst

def make_model(T,beta):
    out=[]
    for t in range(T):
        horizon=sum(beta**i for i in range(T-t))
        out.append([{'beta':beta,'P':[F(3,4),F(1,4)] if z==0 else [F(1,4),F(3,4)],'a':F(1),'r':F(2+2*z,3)+F(t%3,10),'d':F(1),'ell':F(1+z,8),'cap':F(3+z,5)*horizon} for z in range(2)])
    return out

def run(T,m,beta):
    model=make_model(T,beta);terminal={'L':F(0),'U':F(0),'anchors':[{'q':F(0),'b':F(0),'value':F(0)},{'q':F(1),'b':F(0),'value':F(0)}],'planes':[{'A':F(0),'B':F(0),'C':F(0)}]}
    levels=[[terminal,terminal]];widths=[];start=time.perf_counter()
    for t in reversed(range(T)):
        layer=[]
        for z in range(2):
            p=model[t][z];child=levels[0];L=F(0);U=min(p['cap'],p['a']+beta*sum(pr*ch['U'] for pr,ch in zip(p['P'],child)))
            node={'L':L,'U':U,'anchors':[],'planes':[]}
            for i in range(m+1):
                for j in range(m+1):
                    q=F(i,m);b=U*F(j,m)
                    node['anchors'].append(lower_proposal(q,b,p,child,m))
                    h=upper_proposal(q,b,p,child,m)
                    # Distinct certificate witnesses may yield the same plane; retain one.
                    if not any(all(h[k]==v[k] for k in ('A','B','C')) for v in node['planes']):node['planes'].append(h)
            node['width']=certificate_width(node,m);layer.append(node)
        levels.insert(0,layer)
        print(f'T={T} m={m} t={t}: widths {[round(float(n["width"]),6) for n in layer]}',flush=True)
    count=sum(len(n['anchors']) for lev in levels[:-1] for n in lev)
    return {'schema':'ndu-r26-continuous-envelopes-v1','T':T,'m':m,'beta':beta,'model':model,'levels':levels,'summary':{'anchors':count,'planes':sum(len(n['planes']) for lev in levels[:-1] for n in lev),'max_root_width':max(n['width'] for n in levels[0]),'full_binary_tree_nodes':2**T-1,'proposal_seconds':time.perf_counter()-start}}

def strings(obj):
    if isinstance(obj,F):return str(obj)
    if isinstance(obj,dict):return {k:strings(v) for k,v in obj.items()}
    if isinstance(obj,list):return [strings(v) for v in obj]
    return obj

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--horizon',type=int,default=4);ap.add_argument('--grid',type=int,default=4);ap.add_argument('--beta',default='3/4');args=ap.parse_args()
    if args.horizon<1 or args.grid<1:raise ValueError('positive horizon and grid required')
    ans=run(args.horizon,args.grid,F(args.beta));out=R/'results'/f'envelopes_T{args.horizon}_m{args.grid}.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(strings(ans),separators=(',',':'))+'\n');print(json.dumps(strings(ans['summary']),indent=2))
