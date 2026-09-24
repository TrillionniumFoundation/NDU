"""Independent exact stress test of the R43 general-cost price theorem.

Run with ordinary Python (not python -O). This script does not import any
paper solver. It compares literal cap-crossing recurrences with exhaustive
books and explicit piecewise-linear branch supports, including nonidentical
eligibility thresholds. Its recorded output is a supplementary local audit,
not one of the twelve main scaling runs or six independent SCIP comparisons.
"""
from fractions import Fraction as Q
from itertools import combinations
from random import Random
import json,time,sys,platform,hashlib,os
from pathlib import Path
rng=Random(430924)
a=tuple(Q(i,6) for i in range(7))
def f(x):
    return 3*min(x,Q(1,3))+2*max(Q(0),min(x,Q(2,3))-Q(1,3))+max(Q(0),x-Q(2,3))
def h(y,pars):
    s,t,k=pars
    return s*min(y,k)+t*max(Q(0),y-k)
def phi(z,lam,pars):
    return max(-h(y,pars)-lam*y for y in {Q(0),z,min(z,pars[2])})
def support(book,b,tau,lam,pars):
    lev=[c for c in book if c<=tau]; d=lev[-1]
    knots={b}|{c for c in lev if c<=b}|{min(b,d+pars[2])}
    vals=[]
    for t in knots:
        if not lev[0]<=t<=b:continue
        if t>=d:v=f(d)-h(t-d,pars)
        else:
            v=next(( (v-t)*f(u)+(t-u)*f(v) )/(v-u) for u,v in zip(lev,lev[1:]) if u<=t<=v)
        vals.append(v-lam*t)
    return max(vals)
start=time.perf_counter(); roots=prefixes=0
for trial in range(100):
    k=rng.randrange(1,6);m=rng.randrange(1,4)
    caps=[Q(rng.randrange(2,7),6) for _ in range(k)]
    taus=[min(Q(1),b+Q(rng.randrange(4),6)) for b in caps]
    costs=[(Q(rng.randrange(3)),Q(rng.randrange(3,7)),Q(rng.randrange(1,5),6)) for _ in caps]
    w=[rng.randrange(1,5) for _ in caps];p=[Q(v,sum(w)) for v in w]
    B=Q(rng.randrange(1,5),5)*sum(pi*b for pi,b in zip(p,caps));astar=min(B,min(caps))
    fees=[Q(rng.randrange(5),20) for _ in a]
    books=[s for n in range(1,m+1) for s in combinations(range(len(a)),n) if a[s[0]]<=astar]
    for lam in (Q(-3),Q(-1,2),Q(0),Q(5,4),Q(3),Q(7)):
        g=[f(x)-lam*x for x in a]
        tail=[sum(pi*(g[i]+phi(b-u,lam,hp)) for pi,b,hp in zip(p,caps,costs) if b>=u) for i,u in enumerate(a)]
        edges={(i,j):sum(pi*(g[i]+(b-u)/(v-u)*(g[j]-g[i]) if v<=tau else g[i]+phi(b-u,lam,hp)) for pi,b,tau,hp in zip(p,caps,taus,costs) if u<=b<v) for i,u in enumerate(a) for j,v in enumerate(a) if i<j and g[j]>=g[i]}
        W={1:tail}
        for r in range(2,m+1):W[r]=[max([tail[i]]+[ed-fees[j]+W[r-1][j] for (h0,j),ed in edges.items() if h0==i]) for i in range(len(a))]
        val={bk:lam*B+sum(pi*support([a[i] for i in bk],b,tau,lam,hp) for pi,b,tau,hp in zip(p,caps,taus,costs))-sum(fees[i] for i in bk) for bk in books}
        dp=lam*B+max(W[m][i]-fees[i] for i,x in enumerate(a) if x<=astar)
        assert dp==max(val.values()),('root',trial,lam);roots+=1
        for pref in books:
            if any(g[j]<g[i] for i,j in zip(pref,pref[1:])):bound=val[pref]
            else:bound=lam*B+sum(edges[i,j] for i,j in zip(pref,pref[1:]))-sum(fees[i] for i in pref)+W[m-len(pref)+1][pref[-1]]
            truth=max(v for bk,v in val.items() if bk[:len(pref)]==pref)
            assert bound==truth,('prefix',trial,lam,pref,bound,truth);prefixes+=1
out={'status':'PASS','scope':'Separate local audit of branch-specific eligibility thresholds and nonquadratic piecewise-linear concave rewards and convex shortfall costs','models':100,'root_price_equalities':roots,'prefix_price_equalities':prefixes,'seconds':time.perf_counter()-start,'seed':430924}
out.update(python=sys.version,platform=platform.platform(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),execution=os.environ.get('R43_AUDIT_CONTEXT','Local supplementary audit; independent of publication CI'))
Path(os.environ.get('R43_AUDIT_OUTPUT',str(Path(__file__).with_name('general_class_result.json')))).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
