"""Reproducible exact tests for the R34 global codebook algorithm.

The exhaustive comparator uses the proved cap-anchor reduction but neither
prefix moments nor the production DP. Direct continuous codebook grids are
additional falsification tests, not a proof of continuous global optimality.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import csv, hashlib, json, platform, random, time
from randomized_frontier import (Problem, Solution, codebook_loss,
                                 randomized_frontiers, deterministic_frontiers,
                                 audit, Moments)
R = Path(__file__).resolve().parent
COUNTS = {"exhaustive_codebook_candidates":0, "frontier_equalities":0,
          "controller_replays":0, "off_anchor_grid_comparisons":0,
          "direct_moment_equalities":0, "invalid_inputs_rejected":0}


def exhaustive(p: Problem) -> tuple[list[Solution], list[Solution]]:
    """Enumerate every anchored prefix, infer each final-cell quadratic
    from three direct evaluations, and minimize it exactly. No DP/moments."""
    k, b = len(p.caps), p.caps
    ran: list[Solution | None] = [None]*k
    det: list[Solution | None] = [None]*k
    def offer(store, budget, candidate):
        if store[budget-1] is None or candidate.loss < store[budget-1].loss:
            store[budget-1] = candidate
    for s in range(1, k+1):
        for rest in combinations(range(1, k), s-1):
            indices=(0,*rest); anchors=tuple(b[i] for i in indices)
            dloss=sum(w*(p.reward(cap)-p.reward(max(c for c in anchors if c<=cap))
                         +g*(cap-max(c for c in anchors if c<=cap))**2/2)
                      for cap,w,g in zip(b,p.probabilities,p.gamma))
            offer(det,s,Solution(dloss,anchors))
            # A codebook with no extra level is also feasible in expectation.
            offer(ran,s,Solution(codebook_loss(p,anchors),anchors))
            if s == k: continue
            for ell in range(indices[-1], k):
                lo,hi=b[ell],b[min(ell+1,k-1)]
                if lo == hi:
                    z=lo
                else:
                    mid=(lo+hi)/2; half=(hi-lo)/2
                    f0=codebook_loss(p,(*anchors,lo))
                    fm=codebook_loss(p,(*anchors,mid))
                    f1=codebook_loss(p,(*anchors,hi))
                    A=(f0+f1-2*fm)/(2*half*half)
                    B=(f1-f0)/(2*half)-2*A*mid
                    assert A>=0
                    z=max(lo,min(hi,-B/(2*A))) if A else (lo if B>=0 else hi)
                c=tuple(sorted(set((*anchors,z))))
                offer(ran,s+1,Solution(codebook_loss(p,c),c))
                COUNTS['exhaustive_codebook_candidates']+=1
    for store in (ran,det):
        for j in range(1,k):
            assert store[j] is not None and store[j-1] is not None
            if store[j-1].loss < store[j].loss: store[j]=store[j-1]
        assert all(x is not None for x in store)
    return ran,det


def compare(p: Problem) -> dict:
    k=len(p.caps)
    got=randomized_frontiers(p,k+2); dg=deterministic_frontiers(p,k+2)
    er,ed=exhaustive(p)
    for j in range(k):
        assert got[j].loss==er[j].loss and dg[j].loss==ed[j].loss
        assert 0<=got[j].loss<=dg[j].loss
        assert len(got[j].codebook)<=j+1
        assert all(c in p.caps for c in got[j].codebook[:-1])
        assert got[j].codebook[0]==p.caps[0]
        audit(p,got[j],j+1); COUNTS['controller_replays']+=1
        # Pathwise codebook controller uses the largest eligible level.
        c=dg[j].codebook
        realized_loss=F(0)
        for b,w,g in zip(p.caps,p.probabilities,p.gamma):
            level=max(x for x in c if x<=b); y=b-level
            assert 0<=y<=1 and y+level==b
            realized_loss+=w*(p.reward(b)-p.reward(level)+g*y*y/2)
        assert realized_loss==dg[j].loss
        COUNTS['frontier_equalities']+=2
        if j:
            assert got[j].loss<=got[j-1].loss and dg[j].loss<=dg[j-1].loss
    assert got[k-1].loss==dg[k-1].loss==0
    assert got[k:]==[got[k-1]]*2 and dg[k:]==[dg[k-1]]*2
    if k>1: assert got[k-2].loss>0
    mm=Moments(p)
    for i in range(k):
        for j in range(i,k):
            expected=sum(w*p.q*(cap-p.caps[i])*(p.caps[j]-cap)/2
                         for cap,w in zip(p.caps[i:j+1],p.probabilities[i:j+1]))
            assert mm.edge(i,j)==expected
            COUNTS['direct_moment_equalities']+=1
            if i==0:
                lo=p.caps[j];hi=p.caps[min(j+1,k-1)]
                A,B,C=mm.tail_polynomial(i,j)
                for z in (lo,(lo+hi)/2,hi):
                    assert A*z*z+B*z+C==codebook_loss(p,(p.caps[i],z))
                    COUNTS['direct_moment_equalities']+=1
    return {'caps':list(map(str,p.caps)), 'probabilities':list(map(str,p.probabilities)),
            'gamma':list(map(str,p.gamma)), 'r':str(p.r),'q':str(p.q),
            'randomized_losses':[str(x.loss) for x in got[:k]],
            'deterministic_pathwise_losses':[str(x.loss) for x in dg[:k]]}


def main():
    start=time.perf_counter();cases=[]
    uni=Problem.make(['1/4','1/2','3/4'],['1/3']*3,[1]*3)
    off=Problem.make(['1/4','1/2','3/4'],['7/20','3/5','1/20'],[1]*3)
    for p in (uni,off,Problem.make(['2/5'],[1],[0],1,1)):
        cases.append(compare(p))
    ur=randomized_frontiers(uni,3);ud=deterministic_frontiers(uni,3)
    rr=randomized_frontiers(off,3);dd=deterministic_frontiers(off,3)
    assert ur[1].loss==F(1,96) and ud[1].loss==F(1,8)
    assert rr[1]==Solution(F(23,1280),(F(1,4),F(5,8)))
    assert dd[1].loss==F(3,160)
    cap_only=min(codebook_loss(off,c) for n in (1,2) for c in combinations(off.caps,n)
                 if c[0]<=off.caps[0])
    assert cap_only==F(3,160)>rr[1].loss
    rng=random.Random(340923)
    gridcases=[]
    for k in range(2,8):
        for rep in range(8):
            caps=sorted(rng.sample(range(1,41),k)); weights=[rng.randint(1,20) for _ in caps]
            q=F(rng.randint(1,5),rng.randint(1,4))
            r=q+F(rng.randint(0,5),rng.randint(1,4))
            p=Problem.make([F(c,41) for c in caps],
                           [F(w,sum(weights)) for w in weights],
                           [F(rng.randint(0,6),rng.randint(1,4)) for _ in caps],r,q)
            cases.append(compare(p))
            if rep==0 and k<=5:gridcases.append(p)
    # Grids deliberately include levels not at caps, as well as extreme 0/1.
    for p in (uni,off,*gridcases):
        levels=sorted(set([F(i,8) for i in range(9)]+list(p.caps)))
        frontier=randomized_frontiers(p,3)
        for s in (1,2,3):
            for c in combinations(levels,s):
                if c[0]>p.caps[0]:continue
                assert codebook_loss(p,c)>=frontier[s-1].loss
                COUNTS['off_anchor_grid_comparisons']+=1
    bad=[lambda: Problem.make([0],[1],[1]),
         lambda: Problem.make(['1/2','1/2'],['1/2']*2,[1]*2),
         lambda: Problem.make(['1/2'],['9/10'],[1]),
         lambda: Problem.make(['1/2'],[1],[-1]),
         lambda: Problem.make(['1/2'],[1],[1],1,2),
         lambda: Problem.make([0.5],[1],[1]),
         lambda: Problem.make([],[],[]),
         lambda: randomized_frontiers(uni,0),
         lambda: randomized_frontiers(uni,1.5),
         lambda: deterministic_frontiers(uni,False)]
    for call in bad:
        try:call()
        except (TypeError,ValueError):COUNTS['invalid_inputs_rejected']+=1
        else:raise AssertionError('Invalid input was accepted')
    scale=[]
    for k in (16,32,64,128):
        p=Problem.make([F(j,k+1) for j in range(1,k+1)],
                       [F(2*j,k*(k+1)) for j in range(1,k+1)],
                       [F(j%5,3) for j in range(1,k+1)])
        t=time.perf_counter();sol=randomized_frontiers(p,8);ransec=time.perf_counter()-t
        t=time.perf_counter();det=deterministic_frontiers(p,8);detsec=time.perf_counter()-t
        for m,(a,d) in enumerate(zip(sol,det),1):
            audit(p,a,m);COUNTS['controller_replays']+=1
            assert 0<=a.loss<=d.loss
        height=max(max(x.numerator.bit_length(),x.denominator.bit_length())
                   for a in sol for x in (a.loss,*a.codebook))
        scale.append({'branches':k,'budgets':8,'randomized_seconds':ransec,
                      'deterministic_seconds':detsec,'max_output_bits':height,
                      'randomized_loss_m8':str(sol[-1].loss),
                      'deterministic_pathwise_loss_m8':str(det[-1].loss)})
    (R/'scaling.csv').write_text('')
    with (R/'scaling.csv').open('w',newline='') as fh:
        wr=csv.DictWriter(fh,fieldnames=list(scale[0]));wr.writeheader();wr.writerows(scale)
    out={'status':'PASS','seed':340923,'python':platform.python_version(),
         'platform':platform.platform(),'elapsed_seconds':time.perf_counter()-start,
         'cases':len(cases),'counts':COUNTS,'case_records':cases,'scaling':scale,
         'off_cap_regression':audit(off,rr[1],2),'uniform_regression':audit(uni,ur[1],2),
         'best_cap_only_off_cap_instance':str(cap_only),
         'source_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest()
                          for x in [R/'randomized_frontier.py',R/'verify.py']},
         'scope':'Exact comparator enumerates the theorem-reduced candidates. Grid checks are falsification, not global proofs. Timings are reproducibility data, not published-specialist benchmarks.'}
    (R/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','cases','counts','elapsed_seconds','scaling')},indent=2))
if __name__=='__main__':main()
