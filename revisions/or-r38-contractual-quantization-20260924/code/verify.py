"""Independent exact finite checks, not proof by testing."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json, random, time
from catalog import Model, solve, replay, branch_rule, clipped
R = Path(__file__).resolve().parents[1]
OUT = R/'results'
OUT.mkdir(exist_ok=True)
counts = dict(catalog_frontier_equalities=0, direct_support_book_checks=0,
              promise_scaling_lift_checks=0, clipped_kkt_checks=0,
              fixed_book_concavity_checks=0, repeated_cap_checks=0,
              invalid_input_rejections=0, quantizer_comparisons=0)


def direct_branch(p, j, book, delta):
    """Enumerate every one/two-point support, not just adjacent levels.
    The best mean of a given support is min(b,v), since its chord reward
    increases and its intermediate cost decreases. Feasibility requires
    mu >= v-delta. This oracle does not use the DP edge-cost implementation.
    """
    b, g = p.caps[j], p.gamma[j]
    feasible = [p.reward(c)-g*(b-c)**2/2 for c in book if c <= b]
    for u, v in combinations(book, 2):
        mu = min(b, v)
        if u <= mu and v-mu <= delta:
            feasible.append(((v-mu)*p.reward(u)+(mu-u)*p.reward(v))/(v-u)-g*(b-mu)**2/2)
    assert feasible
    return p.reward(b)-max(feasible)


def exhaustive(p, catalog, charges, m, delta):
    exact = [None]*m
    for s in range(1, min(m, len(catalog))+1):
        for ids in combinations(range(len(catalog)), s):
            book = tuple(catalog[i] for i in ids)
            if book[0] > p.caps[0]: continue
            service = sum(w*direct_branch(p,j,book,delta) for j,w in enumerate(p.probabilities))
            assert service == replay(p,book,delta)
            counts['direct_support_book_checks'] += 1
            cost = service+sum(charges[i] for i in ids)
            for cap in range(s,m+1):
                if exact[cap-1] is None or cost < exact[cap-1]: exact[cap-1]=cost
    return exact


def catalog_tests():
    rng = random.Random(380924)
    for trial in range(48):
        k=2+trial%6
        caps=sorted(F(rng.randrange(1,16),16) for _ in range(k))
        weights=[rng.randrange(1,8) for _ in caps]
        p=Model.make(caps,[F(w,sum(weights)) for w in weights],
                     [F(rng.randrange(8),3) for _ in caps],r=3,q=2)
        a=tuple(sorted({F(0),F(1),*caps,*[F(rng.randrange(1,16),16) for _ in range(3)]}))
        charge=tuple(F(rng.randrange(4),640) for _ in a)
        m=min(4,len(a))
        for delta in (F(0),F(1,16),F(1,4),F(1)):
            got=solve(p,a,charge,m,delta)
            assert [x.total for x in got]==exhaustive(p,a,charge,m,delta)
            counts['catalog_frontier_equalities']+=m
    p=Model.make(['1/4','1/2','3/4'],['7/20','3/5','1/20'],[1,1,1])
    a=tuple(map(F,['1/4','1/2','5/8','3/4']))
    old=solve(p,a,[0]*4,2,1)[1]
    new=solve(p,a,[0,0,F(1,640),0],2,1)[1]
    assert old.codebook==(F(1,4),F(5,8)) and old.total==F(23,1280)
    assert new.total==F(24,1280) and F(5,8) not in new.codebook
    return dict(uncharged_book=old.codebook,uncharged_loss=old.total,
                charged_book=new.codebook,charged_optimum=new.total,
                old_book_charged_cost=F(25,1280))


def promise_tests():
    rng=random.Random(38924)
    for trial in range(60):
        k=2+trial%5
        b=sorted(F(rng.randrange(1,16),16) for _ in range(k))
        raw=[rng.randrange(1,8) for _ in b]
        p=Model.make(b,[F(w,sum(raw)) for w in raw],
                     [F(rng.randrange(9),4) for _ in b],r=3,q=2)
        bar=sum(w*x for w,x in zip(p.probabilities,b))
        for step in range(11):
            B=bar*F(step,10); c=clipped(p,B)
            assert sum(w*x for w,x in zip(p.probabilities,c))==B
            free=[x for x,bj in zip(c,b) if x<bj]
            assert len(set(free))<=1
            if free: assert all(x==min(bj,free[0]) for x,bj in zip(c,b))
            assert all(0<=x<=bj for x,bj in zip(c,b))
            counts['clipped_kkt_checks']+=1
        book=tuple(sorted({F(0),b[0],b[-1]*F(3,4)}))
        for delta in (F(0),F(1)):
            saturated=[branch_rule(p,j,book,delta) for j in range(k)]
            V=sum(w*(sum(pr*p.reward(c) for c,pr in draw)-g*y*y/2)
                  for w,g,(y,draw) in zip(p.probabilities,p.gamma,saturated))
            H=max(g*bj for g,bj in zip(p.gamma,b))
            for alpha in (F(0),F(1,7),F(1,2),F(6,7),F(1)):
                eps=(1-alpha)*bar
                scaled=[(alpha*y,tuple((alpha*c,pr) for c,pr in draws)) for y,draws in saturated]
                val=sum(w*(sum(pr*p.reward(c) for c,pr in draw)-g*y*y/2)
                        for w,g,(y,draw) in zip(p.probabilities,p.gamma,scaled))
                assert val>=V-p.r*eps
                if delta==1:
                    lift=sum(w*(sum(pr*p.reward(c) for c,pr in draw)
                                    -g*(bj-sum(pr*c for c,pr in draw))**2/2)
                             for bj,w,g,(y,draw) in zip(b,p.probabilities,p.gamma,scaled))
                else:
                    lift=sum(w*sum(pr*(p.reward(c)-g*(bj-c)**2/2) for c,pr in draw)
                             for bj,w,g,(y,draw) in zip(b,p.probabilities,p.gamma,scaled))
                assert lift>=val-H*eps
                counts['promise_scaling_lift_checks']+=1
    assert F(11,96)/(F(2)+F(3,4))==F(1,24)
    for g in [F(0),F(1),F(7,3)]:
        p=Model.make(['3/4'],[1],[g]); book=(F(1,8),F(3,8),F(5,8))
        def response(t):
            if t>=book[-1]: return p.reward(book[-1])-g*(t-book[-1])**2/2
            i=max(i for i,a in enumerate(book) if a<=t)
            if t==book[i]: return p.reward(t)
            u,v=book[i:i+2]
            return ((v-t)*p.reward(u)+(t-u)*p.reward(v))/(v-u)
        ts=[F(i,64) for i in range(8,49)]
        for t1,t2 in combinations(ts,2):
            assert response((t1+t2)/2)>=(response(t1)+response(t2))/2
            counts['fixed_book_concavity_checks']+=1
    return dict(saturated_gap=F(11,96),L_f=2,H=F(3,4),
                strict_interval_left_open=F(11,24),strict_interval_right_closed=F(1,2))


def repeated_tests():
    p=Model.make(['1/4','1/2','1/2','3/4'],['1/8','1/4','3/8','1/4'],[0,1,3,2])
    grouped=Model.make(['1/4','1/2','3/4'],['1/8','5/8','1/4'],[0,F(11,5),2])
    a=tuple(F(i,8) for i in range(9))
    for ids in combinations(range(9),3):
        book=tuple(a[i] for i in ids)
        if book[0]>F(1,4):continue
        for delta in (F(0),F(1)):
            assert replay(p,book,delta)==replay(grouped,book,delta)
            counts['repeated_cap_checks']+=1


def invalid_tests():
    p=Model.make(['1/4','1/2'],['1/2','1/2'],[1,1])
    cases=[lambda:solve(p,[0,0],[0,0],1),lambda:solve(p,[0,1],[0,-1],1),
           lambda:solve(p,[0,1],[0,0],0),lambda:solve(p,[0,1],[0,0],1,-1),
           lambda:solve(p,[0.0,1],[0,0],1),lambda:solve(p,['1/2',1],[0,0],1),
           lambda:clipped(p,1),lambda:Model.make([F(1,2)],[F(1,2)],[1])]
    for fn in cases:
        try:fn()
        except (TypeError,ValueError):counts['invalid_input_rejections']+=1
        else:raise AssertionError('Invalid input accepted')


def quantizer_comparison():
    b=(F(1,4),F(1,2),F(3,4)); w=(F(1,3),)*3; result=[]
    for cut in (1,2):
        cells=(list(range(cut)),list(range(cut,3)))
        centers=tuple(sum(w[j]*b[j] for j in cell)/sum(w[j] for j in cell) for cell in cells)
        mse=sum(w[j]*(b[j]-center)**2 for cell,center in zip(cells,centers) for j in cell)
        feasible=all(center<=b[j] for cell,center in zip(cells,centers) for j in cell)
        assert not feasible
        result.append(dict(cut=cut,mse_centers=centers,mse_objective=mse,
                           pathwise_feasible=feasible))
        counts['quantizer_comparisons']+=1
    return result


if __name__=='__main__':
    start=time.perf_counter()
    switched=catalog_tests(); interval=promise_tests(); repeated_tests(); invalid_tests()
    data=dict(status='PASS',seed=380924,counts=counts,charge_switch=switched,
              promise_certificate=interval,mse_comparison=quantizer_comparison(),
              elapsed_seconds=time.perf_counter()-start,
              scope='Exact finite regression and independent support/subset enumeration; not proof by testing.')
    (OUT/'verification.json').write_text(json.dumps(data,indent=2,default=str)+'\n')
    print(json.dumps(data,indent=2,default=str))
