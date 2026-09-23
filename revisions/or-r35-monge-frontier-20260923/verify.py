"""Exact falsification, independent enumeration, and baseline comparisons.

No matrix property is inferred from a timing experiment. The analytical
proof supplies global validity. Exhaustive comparisons use the established
cap-anchor reduction; additional direct nonanchor grids are falsification.
"""
from __future__ import annotations
from dataclasses import asdict
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import csv, hashlib, importlib.util, json, math, platform, random, sys, time
import monge_frontier as fast
R = Path(__file__).resolve().parent
OLD = R.parent / 'or-r34-global-randomized-frontier-20260923'
# Reuse the independently coded, unchanged exhaustive R34 comparator.
sys.path.insert(0, str(OLD))
spec = importlib.util.spec_from_file_location('_r34_verify_reference', OLD / 'verify.py')
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)
COUNTS = dict(frontier_equalities=0, independent_exhaustive_equalities=0,
              controller_replays=0, edge_monge_inequalities=0,
              tail_monge_inequalities=0, deterministic_monge_inequalities=0,
              direct_interval_checks=0, tail_argmin_checks=0,
              invalid_inputs_rejected=0, nonanchor_grid_checks=0,
              recursion_work_bound_checks=0)


def direct_tail(p, i, z):
    """Original branchwise loss from last anchor onward, without moments."""
    u = p.caps[i]
    return sum(w*(p.q*(b-u)*(z-b)/2 if b <= z else
                   p.reward(b)-p.reward(z)+g*(b-z)**2/2)
               for b,w,g in zip(p.caps[i+1:],p.probabilities[i+1:],p.gamma[i+1:]))


def direct_interval(p, i, ell):
    lo, hi = p.caps[ell], p.caps[min(ell+1,len(p.caps)-1)]
    if lo == hi:
        return direct_tail(p,i,lo),lo
    mid, step = (lo+hi)/2, (hi-lo)/2
    f0, fm, f1 = [direct_tail(p,i,z) for z in (lo,mid,hi)]
    A = (f0+f1-2*fm)/(2*step*step)
    B = (f1-f0)/(2*step)-2*A*mid
    assert A > 0
    z = max(lo,min(hi,-B/(2*A)))
    return direct_tail(p,i,z),z


def direct_cell(p,i,j):
    u=p.caps[i]
    return sum(w*(p.reward(b)-p.reward(u)+g*(b-u)**2/2)
               for b,w,g in zip(p.caps[i:j+1],p.probabilities[i:j+1],p.gamma[i:j+1]))


def compare(p, structural=True, exhaustive=False):
    k=len(p.caps); ran,rw=fast.randomized_frontiers(p,k+2)
    det,dw=fast.deterministic_frontiers(p,k+2)
    rr=fast.old.randomized_frontiers(p,k+2)
    rd=fast.old.deterministic_frontiers(p,k+2)
    for budget,(a,b,c,d) in enumerate(zip(ran,rr,det,rd),1):
        assert a.loss==b.loss and c.loss==d.loss
        assert 0<=a.loss<=c.loss
        fast.old.audit(p,a,budget)
        assert sum(w*(p.reward(cap)-p.reward(max(z for z in c.codebook if z<=cap))
                      +g*(cap-max(z for z in c.codebook if z<=cap))**2/2)
                   for cap,w,g in zip(p.caps,p.probabilities,p.gamma))==c.loss
        COUNTS['frontier_equalities']+=2
        COUNTS['controller_replays']+=2
    assert ran[k-1].loss==det[k-1].loss==0
    assert ran[k:]==[ran[k-1]]*2 and det[k:]==[det[k-1]]*2
    # A deliberately conservative oracle-count consequence of the proof.
    bound=16*k*k*(math.ceil(math.log2(k+1))+1)
    assert rw.tail_evaluations+rw.edge_evaluations<=bound
    assert dw.cell_evaluations<=bound
    COUNTS['recursion_work_bound_checks']+=2
    if exhaustive:
        er,ed=reference.exhaustive(p)
        for i in range(k):
            assert er[i].loss==ran[i].loss and ed[i].loss==det[i].loss
            COUNTS['independent_exhaustive_equalities']+=2
    if structural:
        oracle=fast.Oracle(p,fast.Work()); mm=fast.Moments(p)
        Q={}
        for i in range(k):
            for ell in range(i,k):
                direct=direct_interval(p,i,ell)
                assert oracle.interval(i,ell)==direct
                Q[i,ell]=direct[0]
                COUNTS['direct_interval_checks']+=1
        tails,_=fast.terminal_minima(p)
        expected=[min((Q[i,e],e) for e in range(i,k)) for i in range(k)]
        assert [e for _,e in expected]==sorted(e for _,e in expected)
        for i,(val,ell) in enumerate(expected):
            assert tails[i][0]==val and tails[i][2]==ell
            COUNTS['tail_argmin_checks']+=1
        for a,b,c,d in combinations(range(k),4):
            assert mm.edge(a,c)+mm.edge(b,d)<=mm.edge(a,d)+mm.edge(b,c)
            assert direct_cell(p,a,c)+direct_cell(p,b,d)<=direct_cell(p,a,d)+direct_cell(p,b,c)
            COUNTS['edge_monge_inequalities']+=1
            COUNTS['deterministic_monge_inequalities']+=1
        # Include adjoining/overlapping boundary cases in the triangular tail.
        for a,b in combinations(range(k),2):
            for c,d in combinations(range(b,k),2):
                assert Q[a,c]+Q[b,d]<=Q[a,d]+Q[b,c]
                COUNTS['tail_monge_inequalities']+=1
    return {'caps':list(map(str,p.caps)), 'probabilities':list(map(str,p.probabilities)),
            'gamma':list(map(str,p.gamma)), 'r':str(p.r), 'q':str(p.q),
            'randomized':[str(s.loss) for s in ran[:k]],
            'deterministic_pathwise':[str(s.loss) for s in det[:k]],
            'randomized_work':asdict(rw),'deterministic_work':asdict(dw)}


def main():
    start=time.perf_counter(); cases=[]; rng=random.Random(350923)
    make=fast.Problem.make
    uni=make(['1/4','1/2','3/4'],['1/3']*3,[1]*3)
    off=make(['1/4','1/2','3/4'],['7/20','3/5','1/20'],[1]*3)
    fixed=[uni,off,make(['2/5'],[1],[0],1,1),
           make(['1/1000','1/2','999/1000'],['1/1000','998/1000','1/1000'],[0,50,0],1,1)]
    for p in fixed:
        cases.append(compare(p,exhaustive=True))
    for k in range(2,13):
        for rep in range(8):
            cap=sorted(rng.sample(range(1,101),k)); weight=[rng.randint(1,30) for _ in cap]
            q=F(rng.randint(1,7),rng.randint(1,7))
            p=make([F(c,101) for c in cap],[F(w,sum(weight)) for w in weight],
                   [F(rng.randint(0,30),rng.randint(1,7)) for _ in cap],
                   q+F(rng.randint(0,7),rng.randint(1,7)),q)
            cases.append(compare(p,structural=k<=9,exhaustive=k<=7 and rep<2))
    # Symmetries, zero intermediate costs and r=q generate useful boundary ties.
    for k in (2,3,4,5,8,12):
        p=make([F(j,k+1) for j in range(1,k+1)],[F(1,k)]*k,[0]*k,1,1)
        cases.append(compare(p,structural=k<=8,exhaustive=k<=5))
    for p in (uni,off):
        fr,_=fast.randomized_frontiers(p,3)
        grid=sorted(set([F(j,8) for j in range(9)]+list(p.caps)))
        for m in (1,2,3):
            for levels in combinations(grid,m):
                if levels[0]<=p.caps[0]:
                    assert fast.old.codebook_loss(p,levels)>=fr[m-1].loss
                    COUNTS['nonanchor_grid_checks']+=1
    # Directly check leftmost tie behavior of the generic monotone search.
    ties=fast.monotone_minima(0,7,0,7,lambda i:(i,7),lambda i,j:F(0),fast.Work())
    assert all(ties[i][1]==i for i in range(8))
    for function in (fast.randomized_frontiers,fast.deterministic_frontiers):
        for bad in (0,-1,1.5,True,'2'):
            try:function(uni,bad)
            except (TypeError,ValueError):COUNTS['invalid_inputs_rejected']+=1
            else:raise AssertionError('Invalid budget accepted')
    for call in (lambda:make([0.5],[1],[1]),lambda:make(['1/2','1/2'],['1/2']*2,[1,1]),
                 lambda:make(['1/2'],['9/10'],[1]),lambda:make(['1/2'],[1],[-1])):
        try:call()
        except (TypeError,ValueError):COUNTS['invalid_inputs_rejected']+=1
        else:raise AssertionError('Invalid primitive accepted')
    out={'status':'PASS','seed':350923,'cases':len(cases),'counts':COUNTS,
         'independent_exhaustive_candidates':reference.COUNTS['exhaustive_codebook_candidates'],
         'python':platform.python_version(),'platform':platform.platform(),
         'elapsed_seconds':time.perf_counter()-start,'case_records':cases,
         'source_sha256':{str(p.relative_to(R.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (R/'monge_frontier.py',R/'verify.py',OLD/'randomized_frontier.py',OLD/'verify.py')},
         'scope':'Exact arithmetic; theorem-reduced exhaustive candidates, not enumeration of the continuum. R34 comparators and primitive moment oracles are shared/inherited and explicitly identified. No external published solver benchmark.'}
    (R/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','cases','counts','independent_exhaustive_candidates','elapsed_seconds')},indent=2))
if __name__=='__main__':main()
