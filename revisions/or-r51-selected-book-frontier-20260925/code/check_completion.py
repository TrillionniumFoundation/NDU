"""Standalone exact certificate checker. Python standard library only.

No allocation, path optimizer, numerical solver, or study generator is imported.
Scalar supports are checked directly at endpoints, knots, and stationary points;
path tables satisfy Bellman inequalities; binary decisions reconstruct coverage.
"""
from fractions import Fraction as F
from types import SimpleNamespace
from pathlib import Path
import json,gzip,hashlib,sys


def need(ok,message):
    if not ok:raise ValueError(message)


def read_model(raw):
    fields=('caps','weights','gamma','ceilings')
    d=SimpleNamespace(**{x:tuple(F(v) for v in raw[x]) for x in fields},r=F(raw['r']),curvature=F(raw['curvature']))
    k=len(d.caps);need(k>0 and all(len(getattr(d,x))==k for x in fields),'Model dimensions')
    need(all(0<=b<=1 for b in d.caps) and all(w>0 for w in d.weights) and sum(d.weights)==1,'Caps/weights')
    need(all(g>=0 for g in d.gamma) and all(t>=b for t,b in zip(d.ceilings,d.caps)),'Costs/ceilings')
    need(0<=d.curvature<=d.r and d.r>0,'Reward shape')
    return d


def reward(d,x):return d.r*x-d.curvature*x*x/2


def value(d,j,book,t):
    eligible=tuple(x for x in book if x<=d.ceilings[j]);last=eligible[-1]
    if t>=last:return reward(d,last)-d.gamma[j]*(t-last)**2/2
    for u,v in zip(eligible,eligible[1:]):
        if u<=t<=v:return reward(d,u)+(t-u)*(reward(d,v)-reward(d,u))/(v-u)
    raise ValueError('Target below anchor')


def scalar(d,j,book,price):
    lo,hi=book[0],d.caps[j];eligible=tuple(x for x in book if x<=d.ceilings[j])
    need(bool(eligible) and lo<=hi,'Infeasible scalar support')
    points={lo,hi}|{x for x in eligible if lo<=x<=hi}
    if d.gamma[j]>0 and hi>=eligible[-1]:
        points.add(min(hi,max(lo,eligible[-1],eligible[-1]-price/d.gamma[j])))
    return max(value(d,j,book,t)-price*t for t in points)


def check_policy(d,a,rho,B,m,p):
    c=tuple(map(F,p['book']));t=tuple(map(F,p['targets']));y=tuple(map(F,p['intermediate']))
    laws=tuple(tuple((F(x),F(q)) for x,q in law) for law in p['lotteries'])
    need(bool(c) and len(c)<=m and all(x<z for x,z in zip(c,c[1:])) and all(x in a for x in c),'Book')
    need(len(t)==len(y)==len(laws)==len(d.caps),'Policy dimensions')
    gross=F(0)
    for j,(mean,service,law) in enumerate(zip(t,y,laws)):
        need(service>=0 and bool(law) and sum(q for x,q in law)==1,'Probability/service')
        need(all(x in c and q>=0 for x,q in law),'Lottery support')
        need(service+sum(x*q for x,q in law)==mean<=d.caps[j],'Mean/cap')
        need(all(service+x<=d.ceilings[j] for x,q in law if q>0),'Realization ceiling')
        gross+=d.weights[j]*(sum(q*reward(d,x) for x,q in law)-d.gamma[j]*service*service/2)
    need(sum(w*x for w,x in zip(d.weights,t))==B,'Root equality')
    charge=sum(rho[a.index(x)] for x in c)
    need(gross==F(p['gross']) and charge==F(p['charge']) and gross-charge==F(p['value']),'Objective')
    return gross-charge


def path_bound(d,a,rho,B,m,p,witness):
    """Check upper potentials, not equality to a rerun of the path solver."""
    lam=F(witness['price']);n=len(a);m=min(m,n)
    A=[[None if x is None else F(x) for x in row] for row in witness['alpha']]
    need(len(A)==m and all(len(row)==n for row in A),'Prefix potential dimensions')
    score=[reward(d,x)-lam*x for x in a]
    def edge_allowed(i,v):return i>=p-1 or v==i+1
    def stop(i):return i>=p-1
    def service(j,u):
        cap=d.caps[j]-u;points=[F(0),cap]
        if d.gamma[j]>0:points.append(min(cap,max(F(0),-lam/d.gamma[j])))
        return max(-d.gamma[j]*z*z/2-lam*z for z in points)
    def edge(i,v,rising):
        u,z=a[i],a[v];s=(score[v]-score[i])/(z-u);total=F(0)
        for j,weight in enumerate(d.weights):
            t=d.caps[j] if rising else F(0)
            if not u<=t<z:continue
            if z<=d.ceilings[j]:pay=score[i]+s*(t-u)
            elif rising:pay=score[i]+service(j,u)
            else:pay=score[i]-d.gamma[j]*(t-u)**2/2-lam*(t-u)
            total+=weight*pay
        return total
    feasible=[i for i,x in enumerate(a) if x<=min(d.caps) and x<=B and (p==0 or i==0)]
    for i in feasible:need(A[0][i] is not None and A[0][i]>=-rho[i],'Anchor bound')
    for r in range(1,m):
        for v in range(n):
            for i in range(v):
                if A[r-1][i] is not None and edge_allowed(i,v) and score[i]<=score[v]:
                    need(A[r][v] is not None and A[r][v]>=A[r-1][i]+edge(i,v,True)-rho[v],'Rising Bellman bound')
    options=[]
    if lam<=0:
        need(witness['beta'] is None,'Unexpected suffix table')
        tails=[sum((w*(score[i]+service(j,u)) for j,w in enumerate(d.weights) if d.caps[j]>=u),F(0)) for i,u in enumerate(a)]
        options=[A[r][i]+tails[i] for r in range(m) for i in range(n) if A[r][i] is not None and stop(i)]
    else:
        D=[[None if x is None else F(x) for x in row] for row in witness['beta']]
        need(len(D)==m and all(len(row)==n for row in D),'Suffix potential dimensions')
        tails=[sum((w*(score[i]-d.gamma[j]*u*u/2+lam*u) for j,w in enumerate(d.weights) if F(0)>=u),F(0)) for i,u in enumerate(a)]
        for s in range(m):
            for i in range(n):
                if stop(i):need(D[s][i] is not None and D[s][i]>=tails[i],'Suffix stopping bound')
                if s:
                    for v in range(i+1,n):
                        if edge_allowed(i,v) and score[v]<=score[i] and D[s-1][v] is not None:
                            need(D[s][i] is not None and D[s][i]>=edge(i,v,False)-rho[v]+D[s-1][v],'Falling Bellman bound')
        middle=[sum((w*score[i] for w,b in zip(d.weights,d.caps) if 0<u<=b),F(0)) for i,u in enumerate(a)]
        options=[A[r][i]+middle[i]+D[m-r-1][i] for r in range(m) for i in range(n) if A[r][i] is not None and D[m-r-1][i] is not None]
    need(bool(options),'No feasible final price bound')
    out=lam*B+max(options);need(F(witness['upper'])>=out,'Final price bound')
    return F(witness['upper'])


def check(cert):
    need(cert['schema']=='ndu-r51-selected-prefix-v1','Certificate schema')
    d=read_model(cert['model']);a=tuple(map(F,cert['catalog']));rho=tuple(map(F,cert['charges']));B=F(cert['promise']);m=cert['budget']
    need(bool(a) and len(a)==len(rho) and 0<=a[0]<=a[-1]<=1 and all(x<y for x,y in zip(a,a[1:])),'Catalog')
    need(all(x>=0 for x in rho) and isinstance(m,int) and not isinstance(m,bool) and 1<=m<=len(a),'Charges/budget')
    need(a[0]<=min(d.caps) and a[0]<=B<=sum(w*b for w,b in zip(d.weights,d.caps)),'Root feasibility')
    lower=check_policy(d,a,rho,B,m,cert['policy']);need(lower==F(cert['lower_bound']),'Lower endpoint')
    screen=cert['screening'];lam=F(screen['price']);G=lam*B+sum(w*scalar(d,j,a,lam) for j,w in enumerate(d.weights))
    need(F(screen['gross_upper'])>=G and F(screen['lower'])<=lower,'Screening support')
    removed=screen['removed'];need(len(removed)==len(set(removed)) and all(isinstance(i,int) and 0<=i<len(a) for i in removed),'Removed indices')
    need(all(F(screen['gross_upper'])-rho[i]<F(screen['lower']) for i in removed),'Unsafe catalog deletion')
    active=[i for i in range(len(a)) if i not in removed];need(active==cert['active'] and bool(active),'Active catalog')
    ac=tuple(a[i] for i in active);rc=tuple(rho[i] for i in active);n=len(ac)
    nodes=cert['nodes'];need(bool(nodes),'Missing binary cover');seen=set();stack=[(0,0,())];open_upper=[];prices=0
    while stack:
        nid,cursor,chosen=stack.pop();need(isinstance(nid,int) and 0<=nid<len(nodes) and nid not in seen,'Broken/cyclic cover');seen.add(nid)
        z=nodes[nid];kind=z['state'];terminal=cursor==n or len(chosen)==m
        ids=chosen if terminal else chosen+tuple(range(cursor,n))
        infeasible=not ids or ac[ids[0]]>min(d.caps) or ac[ids[0]]>B
        if infeasible:
            need(kind=='INFEASIBLE' and 'children' not in z and 'bound' not in z,'Unjustified infeasible leaf');continue
        need(kind!='INFEASIBLE','False infeasible leaf')
        book=tuple(ac[i] for i in ids);witness=z['bound'];committed=sum(rc[i] for i in chosen)
        if witness['kind']=='free':
            lam=F(witness['price']);upper=lam*B+sum(w*scalar(d,j,book,lam) for j,w in enumerate(d.weights))-committed
            need(F(witness['upper'])>=upper,'Free-completion support');upper=F(witness['upper'])
        else:
            need(witness['kind']=='price' and not terminal,'Unexpected bound kind')
            upper=path_bound(d,book,tuple(rho[a.index(x)] for x in book),B,m,len(chosen),witness);prices+=1
        if kind=='SPLIT':
            need(not terminal and len(z['children'])==2,'Invalid binary split')
            l,r=z['children'];stack.extend([(l,cursor+1,chosen),(r,cursor+1,chosen+(cursor,))])
        else:
            need('children' not in z,'Extraneous children')
            if kind=='CLOSED':need(upper<=lower,'Invalid pruning')
            else:need(kind=='OPEN','Leaf state');open_upper.append(upper)
    need(len(seen)==len(nodes),'Unreachable certificate records')
    upper=max([lower]+open_upper);need(F(cert['upper_bound'])==upper and F(cert['gap'])==upper-lower,'Global interval')
    need(cert['status']==('EXACT' if upper==lower else 'OPEN'),'Completion status')
    need(cert['evaluated_nodes']==len(nodes),'Node count')
    problem={k:cert[k] for k in ['model','catalog','charges','promise','budget']}
    return dict(status='PASS',nodes=len(nodes),path_witnesses=prices,removed=len(removed),exact=upper==lower,
                problem_sha256=hashlib.sha256(json.dumps(problem,sort_keys=True,separators=(',',':')).encode()).hexdigest())


if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: check_completion.py certificate.json[.gz]')
    p=Path(sys.argv[1]);data=p.read_bytes();raw=gzip.decompress(data) if p.suffix=='.gz' else data
    print(json.dumps(check(json.loads(raw)),indent=2))
