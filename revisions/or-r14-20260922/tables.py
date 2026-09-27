#!/usr/bin/env python3
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parent;O=ROOT/'results';T=ROOT/'tables';T.mkdir(exist_ok=True)
s=json.loads((O/'summary.json').read_text());v=json.loads((O/'validation.json').read_text());c=json.loads((O/'structural_checks.json').read_text());a=json.loads((O/'verification.json').read_text());sc=json.loads((O/'scaling.json').read_text())
def sci(x):
    m,e=f'{x:.3e}'.split('e');return rf'{m}\times10^{{{int(e)}}}'
def num(x):return f'{x:.6f}'
metric={
'OptimalGain':num(s['mean_optimal_gain']),
'ValueRegret':'$'+sci(s['methods']['value']['mean_regret'])+'$',
'GradientRegret':'$'+sci(s['methods']['value-gradient']['mean_regret'])+'$',
'CapRate':f"{100*s['methods']['value']['cap_projection_fraction']:.2f}\\%",
'CILow':sci(s['paired_differences']['mean_regret']['lower']),
'CIHigh':sci(s['paired_differences']['mean_regret']['upper']),
'ImmediateValue':f"{100*s['methods']['value']['immediate_fraction']:.2f}\\%",
'ImmediateGradient':f"{100*s['methods']['value-gradient']['immediate_fraction']:.2f}\\%",
'ColdTime':f"{s['timing']['cold-newton']['median_total_ms']:.3f}",
'LearnedTime':f"{s['timing']['value-gradient']['median_total_ms']:.3f}",
'Range':f"{math.ceil(v['B']*1e6)/1e6:.6f}",'ValidationGain':num(v['methods']['value-gradient']['empirical_gain']),
'ValidationFloor':f"{math.floor(v['methods']['value-gradient']['simultaneous_gain_lower']*1e6)/1e6:.6f}",
'ValidationGap':'$'+sci(v['methods']['value-gradient']['mean_gap'])+'$',
'DenseError':'$'+sci(c['max_dense_value_error'])+'$',
'Certificates':f"{a['rational_certificates']:,}",'Checks':f"{a['exact_algebraic_checks']:,}",
'LabelTime':f"{s['total_training_label_seconds']:.3f}",
'ValueFit':f"{s['fit_seconds']['value']:.3f}",'GradientFit':f"{s['fit_seconds']['value-gradient']:.3f}"}
(T/'metrics.tex').write_text('% Generated from actual R14 execution records.\n'+''.join('\\newcommand{\\RFourteen'+k+'}{'+val+'}\n' for k,val in metric.items()))
q=r'''\begin{table}[t]
\centering
\caption{Unrefined accepted scalar-critic policies: eight paired training seeds, 128 shared independent contexts, and positive switching friction.}
\label{tab:r14-quality}
\begin{tabular}{lrr}
\toprule
Metric & Value only & Value gradient\\
\midrule
'''
for label,key,fmt in [('Mean normalized regret','mean_regret','sci'),('Mean exact normalized gap','mean_certificate','sci'),('Mean residual bound','mean_residual_bound','sci'),('Mean gradient bound','mean_gradient_bound','sci'),('Partial-gradient squared error','gradient_mse','sci'),('Immediately certified at $10^{-7}$','immediate_fraction','percent'),('Negative gain, static gate','static_gate_fraction','percent')]:
    vals=[s['methods'][name][key] for name in ['value','value-gradient']]
    q+=label+' & '+' & '.join('$'+sci(x)+'$' if fmt=='sci' else f'{x*100:.2f}\\%' for x in vals)+r'\\'+'\n'
q+=r'''\bottomrule
\end{tabular}
\par\smallskip
\begin{minipage}{0.94\linewidth}
All proposal losses and bounds precede full-objective refinement. The paired primary regret interval includes zero; lower mean error alone does not establish a derivative-training advantage. The exact gap includes rational repair, whereas the analytical bounds describe the exact feasible price response.
\end{minipage}
\end{table}
'''
(T/'quality.tex').write_text(q)
t=r'''\begin{table}[htbp]
\centering
\caption{Complete matched-accuracy deployment on 32 contexts, with three repetitions. All final normalized exact gaps are at most $10^{-7}$.}
\label{tab:r14-timing}
\begin{tabular}{lrrrr}
\toprule
Method & Total (ms) & Audit (ms) & Iterations & Refined (\%)\\
\midrule
'''
for name,label in [('cold-newton','Cold scalar Newton'),('Brent','Brent'),('breakpoints','Sorted breakpoints'),('value','Value only'),('value-gradient','Value gradient')]:
    r=s['timing'][name];t+=f"{label} & {r['median_total_ms']:.3f} & {r['median_audit_ms']:.3f} & {r['mean_iterations']:.2f} & {100*r['refinement_fraction']:.2f}"+r'\\'+'\n'
t+=r'''\bottomrule
\end{tabular}
\par\smallskip
\begin{minipage}{0.97\linewidth}
Times are medians including both audits when refinement occurs. Iterations are mean full-objective solver iterations, counting zero for an immediately certified learned response. The classical methods solve directly, so their refinement indicator is zero rather than a claim of zero computation. Breakpoint scan iterations count scanned intervals and are not comparable arithmetic units to Newton or Brent steps.
\end{minipage}
\end{table}
''';(T/'timing.tex').write_text(t)
t=r'''\begin{table}[htbp]
\centering
\caption{Structural calculation only: median milliseconds over five repetitions at fixed two-date depth. Rational deployment audit is excluded from this scaling table.}
\label{tab:r14-scaling}
\begin{tabular}{rrrrr}
\toprule
Leaves & Threshold & Scalar Newton & Brent & Breakpoints\\
\midrule
'''
for n in sorted(set(r['leaves'] for r in sc)):
    vals=[next(r['median_ms'] for r in sc if r['leaves']==n and r['method']==meth) for meth in ['critical','newton','brent','sort']]
    t+=f'{n:,} & '+' & '.join(f'{x:.3f}' for x in vals)+r'\\'+'\n'
t+=r'\bottomrule\end{tabular}\end{table}'+'\n';(T/'scaling.tex').write_text(t)
