#!/usr/bin/env python3
"""Exact continuous accepted information hierarchy, all arithmetic rational.
Stock is eliminated only AFTER proving the fill/cost supporting-line lemma.
Randomized protocols are convexified ex ante; Jensen derandomizes continuous tiers.
"""
from fractions import Fraction as F
from pathlib import Path
import json,sys
import sympy as sp
sys.set_int_max_str_digits(0)
OUT=Path(__file__).resolve().parent/'results';OUT.mkdir(exist_ok=True)
T=8;beta=F(97,100);m=F(3,2);lam=F(3,5);q0=F(1,2)
P=[[F(x,20) for x in row] for row in [[14,5,1],[3,14,3],[1,5,14]]]
a=[F(9,25)+F(7,5)*z for z in range(3)]
C=[F(103,100)+F(3,10)*z for z in range(3)]
fill=[F(3,2)+z for z in range(3)]
dist=[[F(0),F(1),F(0)]]
for t in range(T-1):dist.append([sum(dist[-1][z]*P[z][k] for z in range(3)) for k in range(3)])
w=[[beta**t*x for x in d] for t,d in enumerate(dist)]
Htot=sum(map(sum,w));Atot=sum(w[t][z]*a[z] for t in range(T) for z in range(3))
physical=sum(w[t][z]*C[z] for t in range(T) for z in range(3))
Ftot=sum(w[t][z]*fill[z] for t in range(T) for z in range(3))
th=(Atot+2*lam*q0)/(2*(m*Htot+lam));cap=Atot*th

def rational(x):return F(int(x.p),int(x.q)) if isinstance(x,sp.Rational) else F(x)
def pack(x):return {'fraction':str(x),'decimal':float(x)}
def pin_stock():
    gaps=[]
    for z in range(3):
      for si in range(13):
        S=F(si,2);lo=sum(F(p,10)*max(z+k-S,0) for k,p in enumerate([1,3,4,2]));over=sum(F(p,10)*max(S-z-k,0) for k,p in enumerate([1,3,4,2]))
        cost=F(3,10)*S+F(3,5)*over+F(13,20)*lo
        f=F(17,10)+z-lo
        gap=cost-C[z]-(f-fill[z]) # supporting price gamma=1
        assert gap>=0 and ((gap==0)==(si==2*(z+2)))
        if gap>0:gaps.append(gap)
    return min(gaps)

def restricted(kind):
    keys=([0] if kind=='static' else list(range(T)) if kind=='time' else [(t,z) for t in range(T) for z in range(3) if dist[t][z]])
    index={k:i for i,k in enumerate(keys)};n=len(keys)
    def ix(t,z):return index[0 if kind=='static' else t if kind=='time' else (t,z)]
    Q=sp.zeros(n);b=sp.zeros(n,1);c=sp.zeros(n,1)
    for t in range(T):
      for z in range(3):
        if not dist[t][z]:continue
        i=ix(t,z);wt=w[t][z];Q[i,i]+=m*wt;b[i]+=a[z]*wt;c[i]+=a[z]*wt
        if t==0:Q[i,i]+=lam*wt;b[i]+=2*lam*q0*wt
        else:
          for zp in range(3):
            if not dist[t-1][zp]:continue
            j=ix(t-1,zp);e=lam*beta**t*dist[t-1][zp]*P[zp][z]
            Q[i,i]+=e;Q[j,j]+=e;Q[i,j]-=e;Q[j,i]-=e
    x0=Q.inv()*b/2;xc=Q.inv()*c/2
    eta=max(F(0),rational(((c.T*x0)[0]-cap)/(c.T*xc)[0]))
    x=x0-eta*xc
    assert all(0<v<1 for v in x)
    assert Q*x*2-b+eta*c==sp.zeros(n,1)
    assert rational((c.T*x)[0])<=cap and eta*(cap-rational((c.T*x)[0]))==0
    value=rational(-(x.T*Q*x)[0]+(b.T*x)[0])-physical-lam*q0*q0
    return {'class':kind,'value':pack(value),'eta':pack(eta),'customer':pack(2*Ftot-rational((c.T*x)[0])), 'filled':pack(Ftot),'physical':pack(physical),'randomization_needed':False,'policy':{str(k):str(rational(x[i])) for i,k in enumerate(keys)},'kkt_exact':True}

def coefficients(eta):
    A=[F(0)]*(T+1);B=[[F(0)]*3 for _ in range(T+1)];vel=[]
    for t in reversed(range(T)):
        K=m+lam+beta*A[t+1]
        L=[(1-eta)*a[z]+beta*sum(P[z][j]*B[t+1][j] for j in range(3)) for z in range(3)]
        A[t]=lam-lam*lam/K;B[t]=[lam*x/K for x in L]
        vel.append((lam/K,[x/(2*K) for x in L]))
    return vel[::-1]

def evaluate(pol):
    p=[F(0),F(1),F(0)];mean=[F(0),q0,F(0)];sq=[F(0),q0*q0,F(0)]
    rew=F(0);pay=F(0);maint=F(0);adj=F(0)
    for t,(k,b) in enumerate(pol):
        mt=[k*mean[z]+b[z]*p[z] for z in range(3)]
        st=[k*k*sq[z]+2*k*b[z]*mean[z]+b[z]*b[z]*p[z] for z in range(3)]
        dd=[(k-1)**2*sq[z]+2*(k-1)*b[z]*mean[z]+b[z]**2*p[z] for z in range(3)]
        pay+=beta**t*sum(a[z]*mt[z] for z in range(3));maint+=beta**t*m*sum(st);adj+=beta**t*lam*sum(dd)
        p=[sum(p[z]*P[z][j] for z in range(3)) for j in range(3)]
        mean=[sum(mt[z]*P[z][j] for z in range(3)) for j in range(3)]
        sq=[sum(st[z]*P[z][j] for z in range(3)) for j in range(3)]
    return pay-physical-maint-adj,pay,maint,adj

def full():
    _,p0,_,_=evaluate(coefficients(F(0)));_,p1,_,_=evaluate(coefficients(F(1)))
    eta=(p0-cap)/(p0-p1);assert 0<eta<1
    pol=coefficients(eta);val,pay,maint,adj=evaluate(pol)
    assert pay==cap
    assert all(0<b[z] and k+b[z]<1 for k,b in pol for z in range(3))
    return {'class':'full','value':pack(val),'eta':pack(eta),'customer':pack(2*Ftot-pay),'filled':pack(Ftot),'physical':pack(physical),'maintenance':pack(maint),'adjustment':pack(adj),'randomization_needed':False,'policy':[{'q_slope':str(k),'intercepts':[str(x) for x in b]} for k,b in pol], 'interior_on_entire_state_domain':True,'kkt_exact':True}

def main():
    gap=pin_stock();rows=[restricted(k) for k in ['static','time','regime']]+[full()]
    out={'scope':'continuous tiers; original complete stock menu; canonical accepted constraints; exact rational KKT/Riccati certificate', 'stock_supporting_price':'1','minimum_nonzero_stock_support_gap':str(gap),'theta_static':str(th),'rows':rows,'increments':{rows[i]['class']:pack(F(rows[i]['value']['fraction'])-F(rows[i-1]['value']['fraction'])) for i in range(1,4)}}
    (OUT/'accepted_continuous_exact.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PIN',gap,'STATIC THETA',float(th))
    for r in rows:print(r['class'],r['value']['decimal'],'eta',r['eta']['decimal'])
    print('INCREMENTS', {k:v['decimal'] for k,v in out['increments'].items()})
if __name__=='__main__':main()
