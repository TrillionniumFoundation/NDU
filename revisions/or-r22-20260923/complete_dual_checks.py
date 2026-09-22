"""Independent exact-arithmetic checks for complete-dual repair and transport.

No numerical optimizer, array package, or manuscript certificate helper is used.
The two-dimensional model has x2=0 and l<=x1<=u, including l=u=0
(no strict-feasibility point), quadratic D=diag(1,2), U=(1,1), B=(1,-1),
and both an upper and a lower participation/capacity row. A direct piecewise
one-dimensional optimization supplies a separately derived exact optimum.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json, sys
R=Path(__file__).resolve().parent

def clip(x,lo,hi): return min(hi,max(lo,x))
def squared(x): return sum((v*v for v in x),F(0))
def primal(x,b,v,lam):
    x1,x2=x
    return b[0]*x1+b[1]*x2-x1*x1/2-x2*x2-(x1+x2)**2/2-lam*(abs(x1-x2+v)-abs(v))
def dual(t,b,v,lam,lo,hi):
    p,s,mu,ml,nu=t
    assert abs(s)<=lam and mu>=0 and ml>=0
    r=[b[0]-p-s-mu+ml,b[1]-p+s-nu]
    z=[clip(r[0],F(-1),F(1)),clip(r[1]/2,F(-1),F(1))]
    q=sum((ri*zi-di*zi*zi/2 for ri,zi,di in zip(r,z,[F(1),F(2)])),F(0))
    value=q+p*p/2-s*v+mu*hi-ml*lo+lam*abs(v)
    grad=[p-z[0]-z[1],-z[0]+z[1]-v,hi-z[0],-lo+z[0],-z[1]]
    return value,grad

def run():
    intervals=[(F(-3,4),F(3,4)),(F(0),F(0)),(F(-1,2),F(0)),(F(0),F(1,2)),(F(-1),F(1))]
    cases=steps=transports=noslater=0
    for (lo,hi),lam,v,b1 in product(intervals,[F(0),F(1,4),F(1)],[F(-1,2),F(0),F(1,2)],[F(-2),F(-1,3),F(0),F(1,3),F(2)]):
        b=[b1,F(1,3)]
        candidates=[lo,hi,clip(-v,lo,hi)]
        # Both stationary candidates are harmless if they lie on the wrong
        # sign region: including additional feasible points cannot raise the
        # objective above its true maximum. The true maximizer is included.
        candidates += [clip((b1-lam)/2,lo,hi),clip((b1+lam)/2,lo,hi)]
        star=max(candidates,key=lambda x:primal([x,F(0)],b,v,lam))
        optimum=primal([star,F(0)],b,v,lam)
        sign=star+v
        s=lam if sign>0 else -lam if sign<0 else clip(b1-2*star,-lam,lam)
        residual=b1-2*star-s
        mu=max(residual,F(0));ml=max(-residual,F(0))
        assert mu*(hi-star)==0 and ml*(star-lo)==0
        optimal_t=[star,s,mu,ml,b[1]-star+s]
        qstar,_=dual(optimal_t,b,v,lam,lo,hi)
        assert qstar==optimum
        y=[(lo+hi)/2,F(0)]
        true_regret=optimum-primal(y,b,v,lam)
        assert true_regret>=0 and qstar-primal(y,b,v,lam)==true_regret
        t=[F(1,3),clip(F(-1,5),-lam,lam),F(1,4),F(1,6),F(-1,3)]
        q,g=dual(t,b,v,lam,lo,hi)
        distance=squared([a-c for a,c in zip(t,optimal_t)])
        # 1+||M D^{-1/2}||_F^2=13/2 is a valid rational Lipschitz bound.
        L=F(13,2)
        for k in range(1,17):
            u=[a-grad/L for a,grad in zip(t,g)]
            u[1]=clip(u[1],-lam,lam);u[2]=max(u[2],F(0));u[3]=max(u[3],F(0))
            qnew,gnew=dual(u,b,v,lam,lo,hi)
            assert optimum<=qnew<=q
            assert qnew-optimum<=L*distance/(2*k)
            assert qnew-optimum <= L*(squared([a-c for a,c in zip(t,optimal_t)])-squared([a-c for a,c in zip(u,optimal_t)]))/2
            t,q,g=u,qnew,gnew;steps+=1
        # A new reward and friction must use a fresh bound. Old feasibility
        # survives exactly; clipping only the changing tension box suffices.
        for newlam,newb1 in [(lam/2,b1+F(1,5)),(lam+F(1,3),b1-F(2,5))]:
            tb=t.copy();tb[1]=clip(tb[1],-newlam,newlam);bn=[newb1,b[1]+newb1-b1]  # reward shift follows U.T*h
            qn,_=dual(tb,bn,v,newlam,lo,hi)
            assert lo<=y[0]<=hi and y[1]==0
            cn=[lo,hi,clip(-v,lo,hi),clip((newb1-newlam)/2,lo,hi),clip((newb1+newlam)/2,lo,hi)]
            exactnew=max(primal([c,F(0)],bn,v,newlam) for c in cn)
            assert qn>=exactnew>=primal(y,bn,v,newlam)
            transports+=1
        cases+=1;noslater+=int(lo==hi)
    result={'status':'PASS','exact_optimum_and_attainment_cases':cases,'lower_dimensional_no_strict_feasibility_cases':noslater,
            'exact_projected_gradient_steps':steps,'new_context_certificate_transports':transports,
            'lipschitz_bound':'13/2','iterations_per_case':16,
            'scope':'Small exact tests of the full-dimensional dual theorem, not an acceleration benchmark or a replacement for its proof.'}
    out=R/'results/complete_dual_checks.json'
    if '--check' in sys.argv:
        assert json.loads(out.read_text())==result
    else:
        out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': run()
