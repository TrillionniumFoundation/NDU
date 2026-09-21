#!/usr/bin/env python3
from pathlib import Path
from fractions import Fraction as Q
import json
import numpy as np
BASE=Path(__file__).resolve().parent;R=BASE/'results';T=BASE/'tables';T.mkdir(exist_ok=True)
ps={p['id']:p for p in json.loads((R/'nonlinear_problems.json').read_text())}
rs=json.loads((R/'nonlinear_records.json').read_text());ts=json.loads((R/'nonlinear_timing.json').read_text())
summary=json.loads((R/'nonlinear_summary.json').read_text())
label={'cycle':'Cycle','erdos':'Random edge','geometric':'Geometric','weighted_block':'Weighted block'}
methodlabel={'fresh':'Newton--direct','cached_pcg':'Newton--PCG','value':'Value only','gradient':'Value--gradient'}
quality=[];timings=[];gate=[]
for fam in label:
    for method in methodlabel:
        sub=[r for r in rs if ps[r['problem']]['family']==fam and r['method']==method]
        gains=[r['certificate']['gain_over_static']/ps[r['problem']]['mass'] for r in sub]
        upper=max(r['certificate']['gap_per_service_review'] for r in sub)
        rejected=sum(v<0 for v in gains)
        safe=float(np.mean([max(0,v) for v in gains]))
        quality.append(f"{label[fam]} & {methodlabel[method]} & {np.mean(gains):.6f} & {safe:.6f} & {upper:.3g} & {rejected}/{len(sub)} \\\\")
        if method in ('fresh','cached_pcg'):
            rr=[t for t in ts if ps[t['problem']]['family']==fam and t['method']==method]
        else:rr=[r for r in sub if r['seed']==0]
        median=1000*np.mean([r['median_end_to_end'] for r in rr]);q10=1000*np.mean([r['q10'] for r in rr]);q90=1000*np.mean([r['q90'] for r in rr])
        timings.append(f"{label[fam]} & {methodlabel[method]} & {median:.2f} & [{q10:.2f}, {q90:.2f}] \\\\")
for r in rs:
    c=r['certificate'];v=Q(c['value_fraction']);s=Q(c['static_fraction']);b=Q(c['bound_fraction'])
    lower=max(v,s);gap=v+b-lower;assert gap>=0
    gate.append({'problem':r['problem'],'method':r['method'],'seed':r['seed'],
        'selection':'proposal' if v>=s else 'static','value_fraction':str(lower),
        'gain_fraction':str(lower-s),'upper_gap_fraction':str(gap)})
(R/'safe_gate.json').write_text(json.dumps(gate,indent=2)+'\n')
(T/'nonlinear_quality.tex').write_text(r'''\begin{table}[p]
\centering\small
\caption{Nonlinear multistage control: mean normalized gain and exact audit. Gains divide total discounted reward by discounted service--reviews. Each learned row averages ten training seeds and two problem seeds; a classical row has two problems. The maximum certificate bound is not an estimated realized loss. ``Static gate'' selects the higher exact reward of the proposal and optimized static rule; no test is removed.}
\label{tab:r10-quality}
\begin{tabular}{llrrrr}\toprule
Family & Method & Raw gain & Static gate & Max. bound & Gate returns static\\\midrule
'''+ '\n'.join(quality)+r'''
\bottomrule\end{tabular}
\end{table}
''')
(T/'nonlinear_timing.tex').write_text(r'''\begin{table}[p]
\centering\small
\caption{Measured end-to-end candidate construction, feasibility repair, and rational audit, in milliseconds. Entries average the two problem-instance medians and their 10th--90th percentiles, each from 15 repetitions after one warmup. Learned timing uses the prespecified training seed zero, not the fastest seed. Factorization setup and training are separate. Methods do not have matched accuracy; this table is not a speedup-at-equal-quality claim.}
\label{tab:r10-timing}
\begin{tabular}{llrr}\toprule
Family & Method & Median & [10th, 90th]\\\midrule
'''+ '\n'.join(timings)+r'''
\bottomrule\end{tabular}
\end{table}
''')
# A compact transparent report; full timing arrays and policies remain archived.
statistics={'raw_negative_learned_decisions':sum(g['selection']=='static' for g in gate if g['method'] in ('value','gradient')),
    'learned_decisions':sum(g['method'] in ('value','gradient') for g in gate),
    'all_gated_gains_nonnegative':all(Q(g['gain_fraction'])>=0 for g in gate),
    'mean_training_seconds':float(np.mean([t['seconds'] for t in json.loads((R/'nonlinear_training.json').read_text())])),
    'min_cached_setup_seconds':min(t['setup_seconds'] for t in ts),
    'max_cached_setup_seconds':max(t['setup_seconds'] for t in ts)}
(R/'gate_summary.json').write_text(json.dumps(statistics,indent=2)+'\n')
print(json.dumps(statistics,indent=2))
verified=json.loads((R/'independent_verification.json').read_text())
lo,hi=summary['student_95_interval']
macros={'RtenMeanDifference':f"{summary['mean_improvement_per_service_review']:.6f}",
 'RtenIntervalLower':f'{lo:.6f}','RtenIntervalUpper':f'{hi:.6f}',
 'RtenTeacherGap':f"{verified['max_teacher_upper_gap']:.3e}",
 'RtenDirectionalBound':f"{verified['max_normalized_directional_error_bound']:.6f}"}
mantissa,exponent=macros['RtenTeacherGap'].split('e')
macros['RtenTeacherGap']=mantissa+r'\times10^{'+str(int(exponent))+'}'
(T/'metrics.tex').write_text('% Generated from the recorded run; do not hand-edit.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in macros.items()))
