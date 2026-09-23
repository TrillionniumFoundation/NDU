"""Same-input, exact complete-frontier benchmark against the unchanged R34 DP."""
from fractions import Fraction as F
from pathlib import Path
from dataclasses import asdict
import csv, hashlib, json, math, platform, time
import monge_frontier as fast
R=Path(__file__).resolve().parent

def instance(k):
    return fast.Problem.make([F(j,k+1) for j in range(1,k+1)],
      [F(2*j,k*(k+1)) for j in range(1,k+1)], [F(j%5,3) for j in range(1,k+1)])

def baseline(p,m):
    original=fast.old.Moments
    counts={'tail':0,'edge':0}
    class Counted(original):
        def edge(self,i,j):
            counts['edge']+=1
            return super().edge(i,j)
        def tail_polynomial(self,i,ell):
            counts['tail']+=1
            return super().tail_polynomial(i,ell)
    fast.old.Moments=Counted
    try:
        start=time.perf_counter(); result=fast.old.randomized_frontiers(p,m)
        seconds=time.perf_counter()-start
    finally:
        fast.old.Moments=original
    return result, seconds, counts

def main():
    rows=[]
    for k in (16,32,64,128,256,512,1024):
        p=instance(k);m=8
        t=time.perf_counter();ran,rw=fast.randomized_frontiers(p,m); sec=time.perf_counter()-t
        t=time.perf_counter();det,dw=fast.deterministic_frontiers(p,m);dsec=time.perf_counter()-t
        for budget,(a,d) in enumerate(zip(ran,det),1):
            fast.old.audit(p,a,budget)
            assert 0<=a.loss<=d.loss
        if k<=256:
            ref,slowsec,c=baseline(p,m)
            assert [s.loss for s in ran]==[s.loss for s in ref]
            equal='PASS'; slowcalls=c['tail']+c['edge']
        else:
            slowsec=slowcalls='NOT_RUN';equal='NOT_RUN'
        calls=rw.tail_evaluations+rw.edge_evaluations
        bound=16*m*k*(math.ceil(math.log2(k+1))+1)
        assert calls<=bound and dw.cell_evaluations<=bound
        row={'branches':k,'budgets':m,'accelerated_randomized_seconds':sec,
             'r34_randomized_seconds':slowsec,'exact_r34_equality':equal,
             'accelerated_randomized_oracle_calls':calls,
             'r34_randomized_oracle_calls':slowcalls,
             'accelerated_pathwise_seconds':dsec,'accelerated_pathwise_cell_calls':dw.cell_evaluations,
             'randomized_loss_m8':str(ran[-1].loss),'pathwise_loss_m8':str(det[-1].loss),
             'max_output_bits':max(max(x.numerator.bit_length(),x.denominator.bit_length()) for s in ran for x in (s.loss,*s.codebook))}
        rows.append(row)
        print(json.dumps(row),flush=True)
    with (R/'scaling.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    record={'status':'PASS','python':platform.python_version(),'platform':platform.platform(),
            'rows':rows,'source_sha256':hashlib.sha256((R/'benchmark.py').read_bytes()).hexdigest(),
            'scope':'Single-run synthetic same-input comparison. R34 baseline evaluated only through 256 branches. Larger rows are replay and operation-bound checks, not baseline comparisons. Timing is machine-dependent; oracle counts are not bit-operation counts.'}
    (R/'benchmark.json').write_text(json.dumps(record,indent=2)+'\n')
    lines=[r'\begin{table}[htbp]\centering',r'\caption{Exact complete-frontier comparison on identical renewal inputs. All budgets one through eight are computed. Counts are tail-interval and prefix-edge oracle calls, not bit operations.}\label{tab:r35-scale}',r'\begin{tabular}{rrrrr}\toprule',r'Branches & R34 calls & Accelerated calls & R34 seconds & Accelerated seconds\\\midrule']
    for row in rows:
        slow='---' if row['r34_randomized_seconds']=='NOT_RUN' else f"{row['r34_randomized_seconds']:.3f}"
        count='---' if row['r34_randomized_oracle_calls']=='NOT_RUN' else f"{row['r34_randomized_oracle_calls']:,}"
        lines.append(f"{row['branches']:,} & {count} & {row['accelerated_randomized_oracle_calls']:,} & {slow} & {row['accelerated_randomized_seconds']:.3f}"+r'\\')
    lines.extend([r'\bottomrule\end{tabular}',r'\par\smallskip\begin{minipage}{.97\textwidth}\small The first five rows have exact equality with the unchanged R34 complete-frontier algorithm. Dashes mark unexecuted baseline runs, not timeouts or estimated results. Larger rows pass exact controller replay. All instances are synthetic.\end{minipage}',r'\end{table}'])
    (R/'evidence_table.tex').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
