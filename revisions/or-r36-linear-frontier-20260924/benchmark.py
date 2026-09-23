"""Same-input complete frontier comparisons: quadratic, monotone, and SMAWK."""
from fractions import Fraction as F
from pathlib import Path
from dataclasses import asdict
import csv, hashlib, importlib.util, json, platform, time
import linear_frontier as fast
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"or-r35-monge-frontier-20260923"))
R=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_r35_benchmark',R.parent/'or-r35-monge-frontier-20260923'/'benchmark.py')
reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)

def main():
    rows=[];frontiers=[]
    for k in (16,32,64,128,256,512,1024,2048):
        p=reference.instance(k);m=8
        t=time.perf_counter();ran,rw=fast.randomized_frontiers(p,m);sec=time.perf_counter()-t
        t=time.perf_counter();det,dw=fast.deterministic_frontiers(p,m);dsec=time.perf_counter()-t
        t=time.perf_counter();middle,mw=fast.previous.randomized_frontiers(p,m);midsec=time.perf_counter()-t
        t=time.perf_counter();middet,mdw=fast.previous.deterministic_frontiers(p,m);middsec=time.perf_counter()-t
        assert [s.loss for s in ran]==[s.loss for s in middle]
        assert [s.loss for s in det]==[s.loss for s in middet]
        for budget,(a,d) in enumerate(zip(ran,det),1):
            fast.old.audit(p,a,budget)
            assert 0<=a.loss<=d.loss
            assert d.loss==sum(w*(p.reward(b)-p.reward(max(z for z in d.codebook if z<=b))
                +g*(b-max(z for z in d.codebook if z<=b))**2/2)
                for b,w,g in zip(p.caps,p.probabilities,p.gamma))
        if k<=256:
            slow,slowsec,sw=reference.baseline(p,m)
            assert [s.loss for s in ran]==[s.loss for s in slow]
            slowcalls=sw['tail']+sw['edge'];slowequal='PASS'
        else:slowsec=slowcalls=slowequal='NOT_RUN'
        calls=rw.tail_evaluations+rw.edge_evaluations
        assert rw.comparisons<=32*m*k and dw.comparisons<=32*m*k
        assert calls<=66*m*k and dw.cell_evaluations<=66*m*k
        row=dict(branches=k,budgets=m,r36_randomized_calls=calls,
          r35_randomized_calls=mw.tail_evaluations+mw.edge_evaluations,r34_randomized_calls=slowcalls,
          r36_randomized_seconds=sec,r35_randomized_seconds=midsec,r34_randomized_seconds=slowsec,
          exact_r35_equality='PASS',exact_r34_equality=slowequal,
          r36_pathwise_calls=dw.cell_evaluations,r35_pathwise_calls=mdw.cell_evaluations,
          r36_pathwise_seconds=dsec,r35_pathwise_seconds=middsec,
          r36_randomized_comparisons=rw.comparisons,r36_pathwise_comparisons=dw.comparisons,
          randomized_loss_m8=str(ran[-1].loss),pathwise_loss_m8=str(det[-1].loss),
          max_output_bits=max(max(x.numerator.bit_length(),x.denominator.bit_length()) for s in ran for x in (s.loss,*s.codebook)))
        rows.append(row)
        frontiers.append(dict(branches=k,randomized=[dict(loss=str(s.loss),codebook=list(map(str,s.codebook))) for s in ran],
          pathwise=[dict(loss=str(s.loss),codebook=list(map(str,s.codebook))) for s in det],
          r36_randomized_work=asdict(rw),r36_pathwise_work=asdict(dw)))
        print(json.dumps(row),flush=True)
    with (R/'scaling.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    out=dict(status='PASS',python=platform.python_version(),platform=platform.platform(),rows=rows,
      complete_frontiers=frontiers,source_sha256={str(p.relative_to(R.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in (R/'benchmark.py',R/'linear_frontier.py',reference.R/'benchmark.py',reference.R/'monge_frontier.py',
            reference.R.parent/'or-r34-global-randomized-frontier-20260923'/'randomized_frontier.py')},
      scope='Synthetic, single-run measurements on identical exact problems. R35 both frontiers are compared through 2048 branches; R34 randomized baseline through 256. NOT_RUN means unexecuted, not timeout. All budgets replayed. Moment oracle and reduction are shared. Oracle calls are not bit-operation counts. No claim of comparison to external published parametric-flow software.')
    (R/'benchmark.json').write_text(json.dumps(out,indent=2)+'\n')
    lines=[r'\begin{table}[htbp]\centering',
      r'\caption{Complete expected-participation frontiers on identical inputs. All budgets one through eight are computed. Counts include repeated economic oracle evaluations, but not ordinal padding comparisons.}\label{tab:r36-scale}',
      r'\begin{tabular}{rrrrr}\toprule',
      r'Branches & Monotone calls & Linear calls & Monotone seconds & Linear seconds\\\midrule']
    for row in rows:
        lines.append(f"{row['branches']:,} & {row['r35_randomized_calls']:,} & {row['r36_randomized_calls']:,} & {row['r35_randomized_seconds']:.3f} & {row['r36_randomized_seconds']:.3f}"+r'\\')
    lines.extend([r'\bottomrule\end{tabular}',
       r'\par\smallskip\begin{minipage}{.97\textwidth}\small Monotone denotes the preceding divide-and-conquer implementation; linear denotes the implemented SMAWK search with symbolic staircase completion. Every row has exact equality for both expected and pathwise frontiers and direct controller replay. The quadratic randomized baseline agrees through 256 branches; larger quadratic runs are not executed. Timing is machine-dependent. Inputs are synthetic.\end{minipage}',r'\end{table}'])
    (R/'evidence_table.tex').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
