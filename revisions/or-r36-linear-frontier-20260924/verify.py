"""Exact tests for ordinal staircase completion and implemented SMAWK.

Proofs supply validity on the continuum. Enumeration uses the inherited
cap-anchor theorem; direct nonanchor grids are falsification only. No test
claims a new proof of that theorem or a published-specialist benchmark.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from dataclasses import asdict
import hashlib, importlib.util, json, platform, random, sys, time
import linear_frontier as fast
R = Path(__file__).resolve().parent
P35 = R.parent / 'or-r35-monge-frontier-20260923'
sys.path.insert(0, str(P35))
spec = importlib.util.spec_from_file_location('_r35_direct_reference', P35/'verify.py')
ref = importlib.util.module_from_spec(spec); spec.loader.exec_module(ref)
COUNT = dict(frontier_equalities=0, controller_replays=0, exhaustive_equalities=0,
             total_monotonicity_implications=0, exact_submatrix_argmins=0,
             direct_interval_equalities=0, nonanchor_grid_checks=0,
             linear_work_checks=0, invalid_inputs_rejected=0,
             padding_regression_checks=0, primitive_monge_checks=0)

def test_matrix(rows, cols, key, all_submatrices=False):
    # Independent enumeration uses every entry, not the production search.
    table = {(i,j):key(i,j) for i in rows for j in cols}
    for a,b in combinations(rows,2):
        for c,d in combinations(cols,2):
            if table[a,d] < table[a,c]:
                assert table[b,d] < table[b,c], (a,b,c,d,table)
                COUNT['total_monotonicity_implications'] += 1
    rsets = [rows]; csets = [cols]
    if all_submatrices:
        rsets=[s for n in range(1,len(rows)+1) for s in combinations(rows,n)]
        csets=[s for n in range(1,len(cols)+1) for s in combinations(cols,n)]
    for rr in rsets:
        for cc in csets:
            w=fast.Work()
            answer=fast.smawk_minima(rr,cc,lambda i,j:table[i,j],w)
            assert w.comparisons <= 16*(len(rr)+len(cc))
            COUNT['linear_work_checks'] += 1
            for i in rr:
                expected=min(cc,key=lambda j:table[i,j])
                assert answer[i]==expected,(rr,cc,i,answer[i],expected)
                COUNT['exact_submatrix_argmins'] += 1

def structural(p, submatrices=False):
    k=len(p.caps); direct={(i,e):ref.direct_interval(p,i,e) for i in range(k) for e in range(i,k)}
    oracle=fast.previous.Oracle(p,fast.Work())
    for pair,expected in direct.items():
        assert oracle.interval(*pair)==expected
        COUNT['direct_interval_equalities']+=1
    w=fast.Work(); bounds=lambda i:(i,k-1)
    test_matrix(list(range(k)),list(range(k)),
      lambda i,j:fast.staircase_key(i,j,bounds,lambda a,b:direct[a,b][0],w),submatrices)
    # Finite ties, arbitrary column potentials, and the opposite staircase.
    # Potentials preserve the Monge property; they are deliberately not a
    # value-function copy from the implementation under test.
    potential=[F((i*17)%11-5,7) for i in range(k)]
    for kind in ('edge','cell'):
        def cost(j,i):
            value=(fast.Moments(p).edge(i,j-1) if kind=='edge' else ref.direct_cell(p,i,j-1))
            return potential[i]+value
        test_matrix(list(range(1,k+1)),list(range(k)),
          lambda j,i:fast.staircase_key(j,i,lambda t:(0,t-1),cost,w),submatrices)
    # Boundary-inclusive finite Monge assertions for the tail matrix.
    for a,b in combinations(range(k),2):
        for c,d in combinations(range(b,k),2):
            assert direct[a,c][0]+direct[b,d][0] <= direct[a,d][0]+direct[b,c][0]
            COUNT['primitive_monge_checks']+=1

def compare(p, exhaustive=False, structure=False, submatrices=False):
    k=len(p.caps); ran,rw=fast.randomized_frontiers(p,k+2); det,dw=fast.deterministic_frontiers(p,k+2)
    oldran=fast.old.randomized_frontiers(p,k+2); olddet=fast.old.deterministic_frontiers(p,k+2)
    midran,_=fast.previous.randomized_frontiers(p,k+2); middet,_=fast.previous.deterministic_frontiers(p,k+2)
    for b,(a,c,x,y,u,v) in enumerate(zip(ran,det,oldran,olddet,midran,middet),1):
        assert a.loss==x.loss==u.loss and c.loss==y.loss==v.loss
        assert 0<=a.loss<=c.loss
        fast.old.audit(p,a,b)
        assert len(c.codebook)<=b
        observed=sum(w*(p.reward(cap)-p.reward(max(z for z in c.codebook if z<=cap))
             +g*(cap-max(z for z in c.codebook if z<=cap))**2/2)
             for cap,w,g in zip(p.caps,p.probabilities,p.gamma))
        assert observed==c.loss
        COUNT['frontier_equalities']+=4;COUNT['controller_replays']+=2
    assert ran[k-1].loss==det[k-1].loss==0
    assert ran[k:]==[ran[k-1]]*2 and det[k:]==[det[k-1]]*2
    for work in (rw,dw):
        # Both key and economic-oracle work, including winner re-queries.
        assert work.comparisons<=32*k*k
        assert work.tail_evaluations+work.edge_evaluations+work.cell_evaluations<=66*k*k
        COUNT['linear_work_checks']+=2
    if exhaustive:
        er,ed=ref.reference.exhaustive(p)
        for j in range(k):
            assert ran[j].loss==er[j].loss and det[j].loss==ed[j].loss
            COUNT['exhaustive_equalities']+=2
    if structure:structural(p,submatrices)
    return dict(caps=list(map(str,p.caps)),probabilities=list(map(str,p.probabilities)),
      gamma=list(map(str,p.gamma)),r=str(p.r),q=str(p.q),
      randomized=[str(x.loss) for x in ran[:k]],pathwise=[str(x.loss) for x in det[:k]],
      randomized_work=asdict(rw),pathwise_work=asdict(dw))

def main():
    start=time.perf_counter();rng=random.Random(360924);make=fast.Problem.make;records=[]
    off=make(['1/4','1/2','3/4'],['7/20','3/5','1/20'],[1]*3)
    fixed=[off,make(['1/4','1/2','3/4'],['1/3']*3,[1]*3),
           make(['2/5'],[1],[0],1,1),
           make(['1/1000000','1/2','999999/1000000'],['1/1000000','499999/500000','1/1000000'],[0,1000,0],1,1)]
    for p in fixed:records.append(compare(p,True,True,True))
    for k in range(2,17):
        for repetition in range(6):
            caps=sorted(rng.sample(range(1,128),k));weights=[rng.randrange(1,100) for _ in caps]
            q=F(rng.randrange(1,11),rng.randrange(1,11))
            p=make([F(x,128) for x in caps],[F(w,sum(weights)) for w in weights],
                [F(rng.randrange(31),rng.randrange(1,9)) for _ in caps],
                q+F(rng.randrange(11),rng.randrange(1,9)),q)
            records.append(compare(p,k<=7 and repetition<2,k<=7 and repetition<2,k<=5 and repetition==0))
    for k in (2,3,4,5,8,16):
        p=make([F(i,k+1) for i in range(1,k+1)],[F(1,k)]*k,[0]*k,1,1)
        records.append(compare(p,k<=5,k<=8,k<=5))
    for side in ('left','right'):
        n=6;w=fast.Work();bounds=(lambda i:(i,n-1)) if side=='left' else (lambda i:(0,i))
        test_matrix(list(range(n)),list(range(n)),
          lambda i,j:fast.staircase_key(i,j,bounds,lambda a,b:F(0),w),True)
    # The all-invalid prefix submatrix must favor its rightmost column.
    w=fast.Work();key=lambda i,j:fast.staircase_key(i,j,lambda r:(r,3),lambda a,b:F(0),w)
    assert fast.smawk_minima([2,3],[0,1],key)=={2:1,3:1}
    # Constant infinities with ordinary left ties fail total monotonicity:
    # row 1 prefers column 1; row 2's entirely invalid prefix prefers 0.
    wrong=lambda i,j:((0,F(0),j) if j>=i else (1,F(0),j))
    assert wrong(1,1)<wrong(1,0) and not wrong(2,1)<wrong(2,0)
    COUNT['padding_regression_checks']+=2
    assert fast.smawk_minima([],[],lambda i,j:None)=={}
    rr,_=fast.randomized_frontiers(off,3)
    assert rr[1].loss==F(23,1280) and rr[1].codebook==(F(1,4),F(5,8))
    for p in fixed[:2]:
        result,_=fast.randomized_frontiers(p,3)
        grid=sorted(set([F(j,8) for j in range(9)]+list(p.caps)))
        for m in (1,2,3):
            for c in combinations(grid,m):
                if c[0]<=p.caps[0]:
                    assert fast.old.codebook_loss(p,c)>=result[m-1].loss
                    COUNT['nonanchor_grid_checks']+=1
    bad=[lambda:fast.smawk_minima([1,1],[0],lambda i,j:(0,F(0),j)),
         lambda:fast.smawk_minima([0],[1,0],lambda i,j:(0,F(0),j)),
         lambda:fast.smawk_minima([0],[],lambda i,j:(0,F(0),j)),
         lambda:make([0.5],[1],[1]),lambda:make(['1/2','1/2'],['1/2']*2,[1]*2),
         lambda:make(['1/2'],['9/10'],[1]),lambda:make(['1/2'],[1],[-1])]
    for fn in (fast.randomized_frontiers,fast.deterministic_frontiers):
        for b in (0,-1,1.5,True,'2'):
            bad.append(lambda fn=fn,b=b:fn(off,b))
    for fn in bad:
        try:fn()
        except (TypeError,ValueError):COUNT['invalid_inputs_rejected']+=1
        else:raise AssertionError('Invalid input accepted')
    out=dict(status='PASS',seed=360924,cases=len(records),counts=COUNT,
      independent_exhaustive_candidates=ref.reference.COUNTS['exhaustive_codebook_candidates'],
      elapsed_seconds=time.perf_counter()-start,python=platform.python_version(),platform=platform.platform(),
      case_records=records,source_sha256={str(p.relative_to(R.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (R/'linear_frontier.py',R/'verify.py',P35/'monge_frontier.py',P35/'verify.py',
                  ref.OLD/'randomized_frontier.py',ref.OLD/'verify.py')},
      scope='Exact rational tests, not a replacement for proofs. R35/R34 share the inherited economic interface and moment oracle. Exhaustive anchored prefixes use direct branch sums and three-point continuous quadratics, not production DP or moments. Submatrix enumeration includes entirely padded rows. Synthetic inputs only.')
    (R/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','cases','counts','independent_exhaustive_candidates','elapsed_seconds')},indent=2))
if __name__=='__main__':main()
