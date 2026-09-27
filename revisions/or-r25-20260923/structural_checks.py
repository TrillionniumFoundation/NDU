"""Exact theorem examples and random rational active-cell certificates.
Only the random matrix calculation needs SymPy; example replay is independent.
"""
from fractions import Fraction as F
from pathlib import Path
import json,random,itertools
R=Path(__file__).resolve().parent;OUT=R/'results';OUT.mkdir(exist_ok=True)
def dot(x,y):return sum((a*b for a,b in zip(x,y)),F(0))
def W(x):return x[1]-dot(x,x)/2

def examples():
    z=[F(1,6),F(2,3),F(2,3)];rows=[]
    for k in range(49):
        t=F(k,64)
        if t<=F(1,6):
            x=[F(1,6),F(2,3)+t/2,F(2,3)-t/2];value=t/2-t*t/4;nu=F(1,2)-t/2;mu=F(0)
        elif t<=F(3,8):
            x=[t,F(3,4),F(3,4)-t];value=-F(1,48)+3*t/4-t*t;nu=F(3,4)-2*t;mu=3*t-F(1,2)
        else:
            x=[F(3,8),F(3,4),F(3,8)];value=F(23,192);nu=F(0);mu=F(5,8)
        assert sum(x)==F(3,2) and all(0<=v<=1 for v in x) and x[1]<=F(3,4) and x[2]<=F(3,4)
        assert abs(x[1]-x[2])<=t and mu>=0 and nu>=0
        grad=[-x[0],1-x[1],-x[2]];root=-x[0]
        assert grad==[root,root+mu+nu,root-nu]
        assert mu*(x[1]-F(3,4))==0 and nu*(x[1]-x[2]-t)==0 and W(x)-W(z)==value
        rows.append({'t':str(t),'x':list(map(str,x)),'gain':str(value),'release_price':str(nu),'cap_price':str(mu)})
    u=[]
    for k in range(1,41):
        b=F(1,4)+F(k,96)
        if b>F(2,3):continue
        x=[(F(3,2)-b)/2,b,(F(3,2)-b)/2];y=[F(3,2)-2*b,b,b]
        mux=F(7,4)-3*b/2;muy=4-6*b
        assert mux>=0 and muy>=0 and all(0<=a<=1 for a in x+y)
        assert W(x)-W(y)==9*(2*b-1)**2/16
        # Both optimized values are supported by feasible KKT prices.
        gradx=[-x[0],1-x[1],-x[2]]; grady=[-y[0],1-y[1],-y[2]]
        assert gradx==[-x[0],-x[0]+mux,-x[0]]
        eta=y[0]-b
        assert grady==[-y[0],-y[0]+muy-eta,-y[0]+eta]
        assert mux-muy==9*(2*b-1)/4
        u.append({'cap':str(b),'full':list(map(str,x)),'restricted':list(map(str,y)),
        'gain':str(W(x)-W(y)),'rent_difference':str(mux-muy)})
    return rows,u

def random_cells():
    import sympy as s
    rng=random.Random(250925);records=[]
    for n in (3,5,7):
      for rep in range(8):
        k=min(2,n-1);Q=s.diag(*[s.Rational(rng.randint(1,7),2) for _ in range(n)])
        Rr=s.ones(1,n);M=s.zeros(k,n)
        for j in range(k):M[j,j+1]=1;M[j,0]=-1
        Z=s.Matrix.hstack(*Rr.nullspace());H=Z.T*Q*Z;S=((M*Z)*H.inv()*(M*Z).T).inv()
        P=Z*H.inv()*(M*Z).T*S;z=s.ones(n,1)/2
        nu=s.Matrix([s.Rational(rng.choice((-1,1))*rng.randint(2,6),3) for _ in range(k)])
        beta=s.Matrix([s.Rational(rng.randint(1,4),4) for _ in range(k)]);v=s.Matrix([beta[i]*s.sign(nu[i]) for i in range(k)])
        p=Q*z+M.T*nu;direction=P*v
        A=s.Matrix([[rng.randint(-2,4) for _ in range(n)] for _ in range(3)])
        slack=s.Matrix([s.Rational(rng.randint(1,5),24) for _ in range(3)]);rhs=A*z+slack
        stops=[]
        for i in range(3):
            a=(A*direction)[i]
            if a>0:stops.append((slack[i]/a,'capacity',i))
        for i in range(n):
            if direction[i]>0:stops.append(((1-z[i])/direction[i],'upper box',i))
            if direction[i]<0:stops.append((-z[i]/direction[i],'lower box',i))
        for i in range(k):
            d=(S*v)[i]*s.sign(nu[i])
            if d>0:stops.append((abs(nu[i])/d,'release price',i))
        stop=min(stops,key=lambda x:x[0]);t=stop[0]/2;x=z+t*direction
        assert M*(x-z)==t*v and Rr*(x-z)==s.zeros(1,1)
        assert all(a<=b for a,b in zip(A*x,rhs)) and all(0<=a<=1 for a in x)
        updated=nu-t*S*v;res=p-Q*x-M.T*updated
        assert all(s.simplify(a-res[0])==0 for a in res)
        gain=(p.T*(x-z))[0]-((x.T*Q*x)[0]-(z.T*Q*z)[0])/2
        formula=t*sum(beta[i]*abs(nu[i]) for i in range(k))-t*t*(v.T*S*v)[0]/2
        assert s.simplify(gain-formula)==0
        records.append({'n':n,'rep':rep,'step':str(t),'first_break':str(stop[0]),'event':stop[1],
            'Q':[[str(a) for a in row] for row in Q.tolist()],'M':[[str(a) for a in row] for row in M.tolist()],
            'P':[[str(a) for a in row] for row in P.tolist()],'S':[[str(a) for a in row] for row in S.tolist()],
            'A':[[str(a) for a in row] for row in A.tolist()],'rhs':[str(a) for a in rhs],
            'nu':[str(a) for a in nu],'omega':[str(a) for a in beta],'p':[str(a) for a in p],
            'gain':str(gain),'formula':str(formula),'all_positive_release_prices':all(updated[i]*s.sign(nu[i])>0 for i in range(k))})
    return records

if __name__=='__main__':
    a,b=examples();r=random_cells();friction=[]
    for j in range(65):
        lam=F(j,64);p=[F(1,2),F(3,4),F(1,4)];x=[F(1,2),F(3,4)-min(lam,F(1,4)),F(1,4)+min(lam,F(1,4))]
        def obj(y):return dot(p,y)-dot(y,y)/2-lam*(abs(y[1]-y[0])+abs(y[2]-y[0]))
        gain=obj(x)-obj(p);expected=lam*lam if lam<=F(1,4) else lam/2-F(1,16)
        assert gain==expected
        tension=min(lam,F(1,4));assert [pp-xx for pp,xx in zip(p,x)]==[F(0),tension,-tension]
        friction.append({'lambda':str(lam),'gain':str(gain),'full':list(map(str,x))})
    (OUT/'structural_certificates.json').write_text(json.dumps({'release':a,'capacity':b,'random_cells':r,'friction':friction},indent=2)+'\n')
    print(json.dumps({'status':'PASS','release_witnesses':len(a),'capacity_witnesses':len(b),'rational_cells':len(r),'friction_witnesses':len(friction)}))
