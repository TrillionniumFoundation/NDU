"""Exact rational verification of benchmark-relative transfer identities.
The proof is in the manuscript. These tests audit identities and the example;
they are not numerical evidence standing in for a proof.
"""
import json,random
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parent

def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def check():
    rng=random.Random(2406401);checks=0;negative=0;binding=0
    for n in (3,7,15,31):
      for rep in range(16):
        c=[F(rng.randint(1,9),4) for _ in range(n)]
        z=[F(rng.randint(1,7),8) for _ in range(n)]
        y=[F(rng.randint(-8,8),100) for _ in range(n-1)]
        B=[[F(0)]*(n-1) for _ in range(n)]
        for j in range(1,n):B[j][j-1]=-1;B[(j-1)//2][j-1]=c[j]/c[(j-1)//2]
        by=[dot(row,y) for row in B];x=[zz+dx for zz,dx in zip(z,by)]
        assert dot(c,by)==0
        desc=[]
        for j in range(n):
            stack=[j];dd=[]
            while stack:
                a=stack.pop();dd.append(a)
                if 2*a+1<n:stack.append(2*a+1)
                if 2*a+2<n:stack.append(2*a+2)
            desc.append(dd)
        for j in range(1,n):
            actual=sum((c[i]*(x[i]-z[i]) for i in desc[j]),F(0))
            assert actual==-c[j]*y[j-1]
            slack=max(F(0),-c[j]*y[j-1])+F(rng.randint(0,2),20)
            budget=sum((c[i]*z[i] for i in desc[j]),F(0))+slack
            assert (sum((c[i]*x[i] for i in desc[j]),F(0))<=budget)==(y[j-1]>=-slack/c[j])
            negative+=y[j-1]<0;binding+=slack==-c[j]*y[j-1]
        q=[F(rng.randint(1,8),4) for _ in range(n)];p=[F(rng.randint(-4,8),3) for _ in range(n)]
        D=[[F(0)]*n for _ in range(n)]
        for j in range(n):
            D[j][j]=1
            if j:D[j][(j-1)//2]=-1
        h=[F(rng.randint(-2,2),10) for _ in range(n)]
        k=[F(rng.randint(1,5),4) for _ in range(n)];lam=F(rng.randint(0,5),4)
        def val(xx):return dot(p,xx)-sum((qq*a*a/2 for qq,a in zip(q,xx)),F(0))-lam*sum((kk*abs(dot(row,xx)-hh) for kk,row,hh in zip(k,D,h)),F(0))
        inc=dot([pp-qq*zz for pp,qq,zz in zip(p,q,z)],by)-sum((qq*d*d/2 for qq,d in zip(q,by)),F(0))
        inc-=lam*sum((kk*(abs(dot(row,z)+dot(row,by)-hh)-abs(dot(row,z)-hh)) for kk,row,hh in zip(k,D,h)),F(0))
        assert inc==val(x)-val(z);checks+=1
    z=[F(1,6),F(2,3),F(2,3)];x=[F(3,8),F(3,4),F(3,8)]
    def w(a):return a[1]-dot(a,a)/2
    assert w(z)==F(5,24) and w(x)==F(21,64) and w(x)-w(z)==F(23,192)
    # Exact KKT witnesses, positive semidefinite quadratic Hessian.
    gz=[-z[0],1-z[1],-z[2]];gx=[-x[0],1-x[1],-x[2]]
    assert gz==[F(-1,6),F(-1,6)+F(1,2),F(-1,6)-F(1,2)]
    assert gx==[F(-3,8),F(-3,8)+F(5,8),F(-3,8)]
    y=[z[1]-x[1],z[2]-x[2]]
    assert y==[F(-1,12),F(7,24)] and x[0]==z[0]+sum(y)
    bad=[F(1,6),F(2,3)+F(1,100),F(2,3)]
    rejected=0
    try:assert sum(bad)==F(3,2)
    except AssertionError:rejected+=1
    try:assert y[0]>=0
    except AssertionError:rejected+=1
    result={'status':'PASS','rational_tree_instances':checks,'node_counts':[3,7,15,31],
      'negative_relative_flows_tested':negative,'binding_relative_lower_bounds':binding,
      'exact_example_restricted':'5/24','exact_example_full':'21/64','exact_expansion':'23/192',
      'example_flow':['-1/12','7/24'],'negative_controls_rejected':rejected}
    (R/'results/transfer_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':check()
