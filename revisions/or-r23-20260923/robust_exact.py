"""R23 independent rational certificate verifier; Python standard library only.
No numerical optimizer, inverse, floating-point feasibility tolerance, or stored
objective is trusted. Matrices use documented fixed integer denominators.
"""
from fractions import Fraction as F
from math import lcm
from functools import reduce
from itertools import product

VERTICES=list(product((-1,1),repeat=3))
def dot(a,b):return sum(int(x)*int(y) for x,y in zip(a,b))
def ceildiv(a,b):return -((-a)//b)
def sparse_rows(rows):return [[(i,int(a)) for i,a in enumerate(row) if a] for row in rows]
def cache(p,g):
    if '_B' not in p:p['_B']=sparse_rows(p['B'])
    if '_A' not in g:
        g['_A']=sparse_rows(g['A_num']);g['_E']=sparse_rows(g['E'])
        n=len(p['qnum'])
        g['_Ac']=[[(j,int(row[i])) for j,row in enumerate(g['A_num']) if row[i]] for i in range(n)]
        g['_Ec']=[[(j,int(row[i])) for j,row in enumerate(g['E']) if row[i]] for i in range(n)]
    if '_Bc' not in p:
        n=len(p['qnum']);p['_Bc']=[[(j,int(row[i])) for j,row in enumerate(p['B']) if row[i]] for i in range(n)]
def coefficients(p,c,r,v):
    n=len(p['qnum']);rank=p['rank']
    cn=[16*int(p['bnum'][i])+sum(int(p['Unum'][j][i])*int(c[j]) for j in range(rank)) for i in range(n)]
    bn=[(16+r*v[0])*a+64*r*v[2]*(1 if i%2==0 else -1) for i,a in enumerate(cn)]
    return bn,(16+r*v[1])*int(c[-1])
def feasible(p,g,xn,xd):
    cache(p,g);xn=list(map(int,xn));xd=int(xd)
    assert xd>0 and len(xn)==len(p['qnum'])
    assert all(-int(z)*xd<=32*x<=(32-int(z))*xd for x,z in zip(xn,p['znum'])),'box violation'
    assert all(32*sum(a*xn[i] for i,a in row)<=int(b)*xd for row,b in zip(g['_A'],g['budget_num'])),'uncertain participation/capacity violation'
    assert all(sum(a*xn[i] for i,a in row)==0 for row in g['_E']),'exact equality violation'
    return True

def value(p,c,r,v,xn,xd):
    xn=list(map(int,xn));xd=int(xd);bn,ln=coefficients(p,c,r,v)
    if '_B' not in p:p['_B']=sparse_rows(p['B'])
    bx=[sum(a*xn[i] for i,a in row) for row in p['_B']]
    ux=[dot(row,xn) for row in p['Unum']]
    ans=F(dot(bn,xn),8192*xd)-F(sum(int(q)*x*x for q,x in zip(p['qnum'],xn)),32*xd*xd)-F(sum(u*u for u in ux),2048*xd*xd)
    ans-=F(ln*sum(int(k)*abs(32*b+int(vv)*xd) for k,b,vv in zip(p['knum'],bx,p['vnum'])),262144*xd)
    ans+=F(ln*sum(int(k)*abs(int(vv)) for k,vv in zip(p['knum'],p['vnum'])),262144)
    return ans

def upper(p,g,c,r,v,d):
    cache(p,g);bn,ln=coefficients(p,c,r,v);den=int(d['den'])
    pp=list(map(int,d['p']));ss=list(map(int,d['s']));mu=list(map(int,d['mu']));nu=list(map(int,d['nu']))
    assert den>0 and len(pp)==p['rank'] and len(ss)==len(p['qnum'])
    assert len(mu)==len(g['A_num']) and len(nu)==len(g['E'])
    assert all(m>=0 for m in mu),'negative inequality price'
    assert all(8192*abs(s)<=den*ln*int(k) for s,k in zip(ss,p['knum'])),'invalid switching tension'
    rd=8192*den;scale=10**12;out=0
    for i,(b,q,z) in enumerate(zip(bn,p['qnum'],p['znum'])):
        q=int(q);z=int(z)
        rr=b*den-256*sum(int(row[i])*pp[j] for j,row in enumerate(p['Unum']))
        rr-=8192*sum(a*ss[j] for j,a in p['_Bc'][i])
        rr-=512*sum(a*mu[j] for j,a in g['_Ac'][i])+8192*sum(a*nu[j] for j,a in g['_Ec'][i])
        if 512*rr<rd*q*(-z):zz=-z
        elif 512*rr>rd*q*(32-z):zz=32-z
        else:out+=ceildiv(8*rr*rr*scale,rd*rd*q);continue
        out+=ceildiv((1024*rr*zz-q*zz*zz*rd)*scale,32768*rd)
    out=F(out,scale)+F(dot(pp,pp),2*den*den)-F(dot(ss,p['vnum']),32*den)
    out+=F(dot(mu,g['budget_num']),512*den)
    out+=F(ln*sum(int(k)*abs(int(vv)) for k,vv in zip(p['knum'],p['vnum'])),262144)
    assert out>=0,'zero policy must belong to outer comparator'
    return out

def vector_record(x):
    den=reduce(lcm,(a.denominator for a in x),1)
    return {'x_num':[str(int(a*den)) for a in x],'x_den':str(den)}

def repair(p,g,raw,anchor):
    """Round nonroots, reconstruct exact root equalities, mix with robust anchor.
    Return the *implemented* rational vector and the exact minimal ray fraction.
    """
    sv=p['services'];n=len(p['qnum'])
    x=[F(0)]*sv+[F(int(round(float(raw[i])*10**10)),10**10) for i in range(sv,n)]
    for a in range(sv):
        x[a]=-sum((int(p['E'][a][i])*x[i] for i in range(sv,n)),F(0))/int(p['E'][a][a])
    cache(p,g);alpha=F(0)
    rows=[([(i,1)],F(32-int(z),32)) for i,z in enumerate(p['znum'])]
    rows += [([(i,-1)],F(int(z),32)) for i,z in enumerate(p['znum'])]
    rows += [(row,F(int(b),32)) for row,b in zip(g['_A'],g['budget_num'])]
    for row,b in rows:
        xx=sum((a*x[i] for i,a in row),F(0));zz=sum((a*anchor[i] for i,a in row),F(0))
        assert zz<b,'anchor is not strictly robust feasible'
        if xx>b:alpha=max(alpha,(xx-b)/(xx-zz))
    assert 0<=alpha<1
    xx=[(1-alpha)*a+alpha*z for a,z in zip(x,anchor)]
    rec=vector_record(xx);feasible(p,g,rec['x_num'],rec['x_den'])
    rec['repair_fraction']=str(alpha)
    return rec

def verify_outer(p,g,r):
    """Reconstruct the analytical outer class, not a sampled containment test."""
    expectedA=[[16*int(a) for a in row] for row in p['Aacc']+p['C']]
    expectedb=[r*sum(int(a)*max(int(z),32-int(z)) for a,z in zip(row,p['znum'])) for row in p['Aacc']]
    expectedb += [(16+r)*int(c)*4 for c in p['capnum']]
    assert g['A_num']==expectedA and g['budget_num']==expectedb,'outer-class containment formula changed'
    expectedE=[list(map(int,row)) for row in p['E']]
    for j in range(p['nodes']):
        dep=(j+1).bit_length()-1;rep=(1<<dep)-1
        if rep==j:continue
        for a in range(p['services']):
            row=[0]*len(p['qnum']);row[j*p['services']+a]=1;row[rep*p['services']+a]=-1;expectedE.append(row)
    assert g['E']==expectedE,'time-only class changed'
    return True

def verify_robust(p,g,r):
    signs=[1 if (i//p['services'])%2==0 else -1 for i in range(len(p['qnum']))]
    aa=[[int(a)*(16+r*v*signs[i]) for i,a in enumerate(row)] for v in (-1,1) for row in p['Aacc']]
    aa += [[16*int(a) for a in row] for row in p['C']]
    bb=[0]*(2*len(p['Aacc']))+[(16-r)*int(c)*4 for c in p['capnum']]
    assert g['A_num']==aa and g['budget_num']==bb and g['E']==p['E'],'robust vertex system changed'
    return True
