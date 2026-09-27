"""Standalone semantic checker; imports neither optimizer nor antecedent code.

Service values are reconstructed from marginal-price intervals. All Bellman
rows are checked using SMAWK, distinct from the optimizer's divide-and-conquer
convolution. Rational model and original lottery constraints are also checked.
"""
from __future__ import annotations
from fractions import Fraction as F
import json,gzip,time,sys
if sys.flags.optimize:raise RuntimeError("Certificate verification requires assertions enabled")


def smawk(rows,columns,value):
    """Leftmost row maximizers of a totally monotone finite matrix."""
    if not rows:return {}
    reduced=[]
    for col in columns:
        while reduced and value(rows[len(reduced)-1],col)>value(rows[len(reduced)-1],reduced[-1]):reduced.pop()
        if len(reduced)<len(rows):reduced.append(col)
    answer=smawk(rows[1::2],reduced,value)
    positions={c:i for i,c in enumerate(reduced)}
    start=0
    for index in range(0,len(rows),2):
        row=rows[index]
        stop=positions[answer[rows[index+1]]] if index+1<len(rows) else len(reduced)-1
        best=reduced[start]
        for col in reduced[start+1:stop+1]:
            if value(row,col)>value(row,best):best=col
        answer[row]=best
        if index+1<len(rows):start=positions[answer[rows[index+1]]]
    return answer


def convolution(previous,kernel,limit):
    R,C=len(previous)-1,len(kernel)-1
    last=min(limit,R+C)
    # Concave linear continuation, steep enough never to win outside support.
    bound=max(map(abs,previous),default=0)+max(map(abs,kernel),default=0)
    slope=4*bound+1
    def entry(row,col):
        q=row-col
        z=kernel[0]+slope*q if q<0 else kernel[-1]-slope*(q-C) if q>C else kernel[q]
        return previous[col]+z
    arg=smawk(list(range(last+1)),list(range(R+1)),entry)
    assert all(0<=row-col<=C for row,col in arg.items())
    return [entry(row,arg[row]) for row in range(last+1)]


def service_segments(weights,gamma,caps):
    free=sum((w*c for w,g,c in zip(weights,gamma,caps) if g==0),F(0))
    total=sum((w*c for w,c in zip(weights,caps)),F(0))
    thresholds=sorted({F(0)}|{g*c for g,c in zip(gamma,caps) if g>0 and c>0})
    pieces=[]
    for low,high in zip(thresholds,thresholds[1:]):
        saturated=[i for i,(g,c) in enumerate(zip(gamma,caps)) if g>0 and g*c<=low]
        active=[i for i,(g,c) in enumerate(zip(gamma,caps)) if g>0 and g*c>low]
        base=free+sum((weights[i]*caps[i] for i in saturated),F(0))
        reciprocal=sum((weights[i]/gamma[i] for i in active),F(0))
        cost=sum((weights[i]*gamma[i]*caps[i]**2/2 for i in saturated),F(0))
        pieces.append((base+reciprocal*high,base,reciprocal,cost,low,high))
    return free,total,pieces


def kernels_from_model(model,a,eta,Q,den):
    w,b,g,tau=[tuple(map(F,model[key])) for key in ('weights','caps','gamma','ceilings')]
    r,c=F(model['r']),F(model['curvature'])
    reward=lambda x:r*x-c*x*x/2
    kernels={}
    for i,u in enumerate(a):
        for v in list(range(i+1,len(a)))+[len(a)]:
            ids=[j for j in range(len(b)) if tau[j]>=u and (v==len(a) or tau[j]<a[v])]
            caps=[max(F(0),b[j]-u) for j in ids]
            T=F(0) if v==len(a) else sum((w[j]*max(F(0),min(b[j],a[v])-u) for j in range(len(b)) if tau[j]>=a[v]),F(0))
            slope=F(0) if v==len(a) else (reward(a[v])-reward(u))/(a[v]-u)
            free,total,pieces=service_segments([w[j] for j in ids],[g[j] for j in ids],caps)
            out=[];piece=0
            for q in range(min(Q,int((T+total)//eta))+1):
                x=q*eta;y=max(F(0),x-T)
                if y<=free:cost=F(0)
                else:
                    while y>pieces[piece][0]:piece+=1
                    _,base,reciprocal,saturated_cost,low,high=pieces[piece]
                    alpha=(y-base)/reciprocal
                    assert low<=alpha<=high
                    cost=saturated_cost+reciprocal*alpha*alpha/2
                z=(slope*min(T,x)-cost)*den
                assert z.denominator==1,'Invalid payoff common denominator'
                out.append(z.numerator)
            assert all(out[q+1]-out[q]>=out[q+2]-out[q+1] for q in range(len(out)-2))
            kernels[i,v]=out
    return kernels


def original_policy(cert):
    model=cert['model'];w,b,g,tau=[tuple(map(F,model[key])) for key in ('weights','caps','gamma','ceilings')]
    r,c=F(model['r']),F(model['curvature']);reward=lambda x:r*x-c*x*x/2
    a=list(map(F,cert['catalog']));rho=list(map(F,cert['charges']));B=F(cert['promise']);m=cert['budget']
    p=cert['policy'];book=list(map(F,p['book']));ys=list(map(F,p['intermediate']));targets=list(map(F,p['targets']))
    assert 1<=len(book)<=m and book==sorted(set(book)) and all(x in a for x in book)
    assert len(ys)==len(b)==len(targets)==len(p['lotteries'])
    gross=F(0);promise=F(0)
    for j,law in enumerate(p['lotteries']):
        law=[(F(z),F(prob)) for z,prob in law]
        assert ys[j]>=0 and all(z in book and prob>=0 for z,prob in law) and sum(prob for z,prob in law)==1
        assert all(ys[j]+z<=tau[j] for z,prob in law if prob>0)
        t=ys[j]+sum(z*prob for z,prob in law)
        assert t==targets[j] and t<=b[j]
        gross+=w[j]*(sum(prob*reward(z) for z,prob in law)-g[j]*ys[j]**2/2)
        promise+=w[j]*t
    assert promise==B
    lower=gross-sum(rho[a.index(z)] for z in book)
    assert lower==F(cert['lower'])==F(p['value'])
    return lower


def verify(cert):
    begin=time.perf_counter()
    assert cert['schema']=='NDU-resource-path-v1'
    model=cert['model'];w,b,g,tau=[tuple(map(F,model[key])) for key in ('weights','caps','gamma','ceilings')]
    k=len(b);assert k and len(w)==len(g)==len(tau)==k
    assert all(wj>0 for wj in w) and sum(w)==1
    assert all(0<=bj<=1 and tj>=bj and gj>=0 for bj,tj,gj in zip(b,tau,g))
    r,c=F(model['r']),F(model['curvature']);assert r>0 and 0<=c<=r
    a=tuple(map(F,cert['catalog']));rho=tuple(map(F,cert['charges']));assert a and 0<=a[0]<=a[-1]<=1 and all(u<v for u,v in zip(a,a[1:]))
    assert len(a)==len(rho) and all(z>=0 for z in rho)
    B=F(cert['promise']);assert 0<=B<=sum(wj*bj for wj,bj in zip(w,b))
    m=cert['budget'];assert type(m)==int and 1<=m<=len(a)
    eta=F(cert['step']);eps=F(cert['epsilon']);L=max(r,max(g));assert eta>0 and eps>0 and F(cert['lipschitz'])==L
    anchors=[i for i,u in enumerate(a) if u<=min(B,min(b))];assert anchors
    assert set(cert['tables'])==set(map(str,anchors)),'Incomplete anchor cover'
    den=int(cert['denominator']);assert den>0
    Q=max(int((B-a[h])//eta) for h in anchors)
    kernels=kernels_from_model(model,a,eta,Q,den)
    scaled=[]
    for cost in rho:
        x=cost*den;assert x.denominator==1;scaled.append(x.numerator)
    score=None;states=0
    for anchor in anchors:
        tables={tuple(map(int,key.split(','))):list(map(int,row)) for key,row in cert['tables'][str(anchor)].items()}
        expected={(1,anchor)}|{(ell,v) for ell in range(2,m+1) for v in range(anchor+ell-1,len(a))}
        assert set(tables)==expected,'Incomplete Bellman state cover'
        initial=(r*a[anchor]-c*a[anchor]**2/2-rho[anchor])*den
        assert initial.denominator==1 and tables[1,anchor]==[initial.numerator]
        qmax=int((B-a[anchor])//eta);qmin=max(0,-int(-(B-a[anchor]-m*eta)//eta))
        for ell in range(2,m+1):
            for v in range(anchor+ell-1,len(a)):
                result=[]
                for u in range(anchor,v):
                    if (ell-1,u) not in tables:continue
                    z=convolution(tables[ell-1,u],kernels[u,v],qmax)
                    while len(result)<len(z):result.append(None)
                    for s,val in enumerate(z):
                        val-=scaled[v]
                        if result[s] is None or val>result[s]:result[s]=val
                assert tables[ell,v]==result,'Bellman equality failed'
        for (ell,u),row in tables.items():
            z=convolution(row,kernels[u,len(a)],qmax)
            if qmin<len(z):score=max(score,max(z[qmin:])) if score is not None else max(z[qmin:])
        states+=sum(map(len,tables.values()))
    assert F(score,den)==F(cert['grid_score'])
    upper=F(score,den)+L*m*eta;lower=original_policy(cert)
    assert upper==F(cert['upper']) and 0<=upper-lower<=2*L*m*eta
    assert upper-lower<=eps,'Requested tolerance not certified'
    return dict(status='PASS',lower=str(lower),upper=str(upper),gap=str(upper-lower),states=states,
                anchors=len(anchors),seconds=time.perf_counter()-begin)

if __name__=='__main__':
    opener=gzip.open if sys.argv[1].endswith('.gz') else open
    with opener(sys.argv[1],'rt') as f:certificate=json.load(f)
    print(json.dumps(verify(certificate),indent=2))
