"""Generate manuscript tables from executed R23 records, without editing values."""
import gzip,json,statistics
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parent;O=R/'results'
s=json.loads((O/'summary.json').read_text());p=json.loads((O/'primitives.json').read_text());gg=json.loads((O/'geometries.json').read_text())
D={};acc=len(p['Aacc'])*2
with gzip.open(O/'certificates.jsonl.gz','rt') as f:
 for line in f:
  it=json.loads(line);r=it['r'];g=gg[f'{r}-robust'];A=g['A_num'];
  for name,rec in it['nominal_diagnostics'].items():
   x=list(map(int,rec['x_num']));d=int(rec['x_den']);vv=[]
   for row in A[:acc]:
    norm=sum(abs(a) for a in row)
    if norm:vv.append(max(F(0),F(sum(a*xx for a,xx in zip(row,x)),d*norm)))
   D.setdefault((r,name),[]).append(float(max(vv,default=F(0))))
metrics=[{'r':r,'method':name,'median_max_continuation_violation_tier':statistics.median(v),'maximum_continuation_violation_tier':max(v)} for (r,name),v in D.items()]
(O/'violation_magnitudes.json').write_text(json.dumps(metrics,indent=2)+'\n')
rows=s['summary'];f=[]
f.append(r'\begin{table}[tbp]\centering\small')
f.append(r'\caption{Certified gains under joint coefficient misspecification.}\label{tab:r23-robust}')
f.append(r'\begin{tabular}{lrrrrr}\toprule')
f.append(r'Radius & Tanh mean & RBF mean & Classical mean & Lowest bound & Unsafe nominal (\%)\\\midrule')
for r in (0,1,2,4):
 rr=[x for x in rows if x['r']==r];a,b,c=rr;lo=min(x['min_robust_gain_lower'] for x in rr)
 unsafe=100*a['nominal_unsafe_fraction']
 f.append(f'{100*r/16:g}\\% & {a["mean_robust_gain_lower"]:.6f} & {b["mean_robust_gain_lower"]:.6f} & {c["mean_robust_gain_lower"]:.6f} & {lo:.6f} & {unsafe:.2f}'+r'\\')
f += [r'\bottomrule\end{tabular}',r'\par\smallskip\begin{minipage}{.98\textwidth}\small Each radius uses the same 96 fresh contexts. Means average pointwise lower certificates against the true, model-specific optimized time-only comparator; they are not lower confidence bounds. \emph{Lowest bound} is the minimum across all three methods and contexts. The classical rule solves the robust maximin certificate problem. Both nominal learned rules have the displayed unsafe fraction before robust response and repair; none of these unsafe diagnostics is deployed. All 1,152 protected implementations are exactly feasible throughout the specified uncertainty cube.\end{minipage}',r'\end{table}']
(R/'tables/robust.tex').write_text('\n'.join(f)+'\n')
v25=[x for x in metrics if x['r']==4]
a,b,c=[x for x in rows if x['r']==4]
t=r'''\subsection{Joint misspecification rather than covariate shift}
Theorem~\ref{thm:r23-robust} is evaluated on the full 63-node model with simultaneous reward, friction, continuation-coefficient, and capacity-budget error. We freeze the original eight-model ensembles, declare four uncertainty radii before final execution, and use 96 new contexts without retraining. An ordinary robust maximin quadratic program provides a nonlearned comparator. Every reported gain uses eight independently certified upper bounds for a common outer time-only class, and therefore refers to the restricted optimum at the actual hidden coefficients, not merely the robust restricted optimum.

Table~\ref{tab:r23-robust} reports 1,152 implemented policies and 3,072 vertex comparator certificates. All new pointwise gain lower bounds are positive in this study; no numerical solve fails. At 25\% radius, the mean lower bounds are %.6f, %.6f, and %.6f for protected tanh-gradient, protected RBF-direct, and classical maximin, respectively. Their minima are %.6f, %.6f, and %.6f. These are descriptive averages of uniformly valid, per-context certificates, not a new population confidence statement.

In contrast, both nominal learned responses violate at least one uncertain continuation or capacity restriction on every recorded positive-radius context. At 25\%% radius the median maximum continuation violations, normalized by each row's coefficient sum, are %.6f and %.6f tier units for tanh and RBF. Robust response plus exact repair eliminates these violations for the declared coefficient cube. The result establishes a concrete operational use of the accepted geometry beyond surrogate regression: the same frozen prices can propose a decision while the constraint and comparator certificates protect against specified coefficient error. Classical maximin remains the strongest measured rule; no neural speed or accuracy superiority is inferred. The uncertainty set is designed rather than estimated, so these results do not establish field calibration or arbitrary-model robustness.
'''
# Avoid percent formatting ambiguity in the LaTeX prose.
t=t.replace('25\\% radius','25 percent radius',1)
t=t % (a['mean_robust_gain_lower'],b['mean_robust_gain_lower'],c['mean_robust_gain_lower'],a['min_robust_gain_lower'],b['min_robust_gain_lower'],c['min_robust_gain_lower'],v25[0]['median_max_continuation_violation_tier'],v25[1]['median_max_continuation_violation_tier'])
(R/'sections/robust_findings.tex').write_text(t+'\n'+(R/'tables/robust.tex').read_text())
print(json.dumps(v25,indent=2))
