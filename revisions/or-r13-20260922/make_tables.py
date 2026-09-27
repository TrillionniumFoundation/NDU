#!/usr/bin/env python3
from experiment import *
S=json.loads((HERE/'results/summary.json').read_text());V=json.loads((HERE/'results/confirmation.json').read_text());A=json.loads((HERE/'results/verification.json').read_text())
P=readzip(HERE/'results/friction_paths.json.gz')['records'];R=readzip(HERE/'results/scaling.json.gz')['records'];out=HERE/'tables';out.mkdir(exist_ok=True)
mac={'RThirteenCells':str(S['cells']),'RThirteenOffline':f"{S['library_seconds']+S['fit_seconds']:.2f}",
     'RThirteenGainFloor':f"{V['expected_gain_lower_bounds'][1]:.6f}",'RThirteenGain':f"{V['empirical_gains'][1]:.6f}",
     'RThirteenRegret':f"{V['expected_regret_upper_bounds'][1]:.6f}",'RThirteenRange':f"{V['B']:.6f}",'RThirteenRadius':f"{V['radius']:.6f}",
     'RThirteenPolicies':f"{A['policies']:,}",'RThirteenChecks':f"{A['subtrees']:,}",
     'RThirteenGap':f"{S['maximum_final_certificate']:.2g}",'RThirteenBreakEven':str(S['observed_break_even_vs_cold'] or 'not attained')}
(out/'metrics.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in mac.items())+'\n')
def table(name,caption,label,columns,headers,rows,note):
    text='\\begin{table}[t]\n\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+columns+'}\\toprule\n'+headers+' \\\\\\midrule\n'
    text+='\n'.join(' & '.join(map(str,row))+' \\\\' for row in rows)
    text+='\n\\bottomrule\\end{tabular}\n\\par\\smallskip\\begin{minipage}{.96\\textwidth}\\footnotesize '+note+'\\end{minipage}\n\\end{table}\n';(out/name).write_text(text)
rows=[]
for r in P:
 if r['context']==[.2,-.4] and r['fraction'] in (0.,.5,1.,1.25):
  rows.append([r['nodes'],f"{r['fraction']:.2f}",f"{r['lambda']:.4f}",f"{r['audit']['gain']:.6f}",f"{r['switching_per_review']:.5f}",r['active_continuation'],r['fused_edges']])
table('friction.tex','Accepted decisions along nonzero switching-friction paths','tab:r13-friction','rrrrrrr','Nodes & $\\lambda/\\lambda_c$ & $\\lambda$ & Gain & Switching & Binding caps & Fused edges',rows,
      'Context $(0.2,-0.4)$; all 81 paths across three contexts are retained in the data. Gain and switching are per discounted review. Binding and fused masks use $10^{-6}$ for numerical diagnosis; exact rational policy gaps, rather than masks, determine validity. The zero-friction row is the control, not the learning experiment.')
rows=[]
for m,title in [('cold','Cold quadratic program'),('neural-top3','Neural, three cells'),('nearest-anchor','Nearest anchor'),('sequential-cells','Sequential cell check')]:
 d=S['methods'].get(m);rows.append([title,f"{1000*S['median_seconds'][m]:.2f}",f"{100*d['immediate_fraction']:.1f}" if d else '--',f"{100*d['refinement_fraction']:.1f}" if d else '--',f"{100*d['first_face_accuracy']:.1f}" if d else '--',f"{d['mean_added_iterations']:.2f}" if d else '--'])
table('matched.tex','Complete deployment at a common certified gap','tab:r13-matched','lrrrrr','Method & Milliseconds & Immediate (\\%) & Refine (\\%) & First face (\\%) & Added iterations',rows,
      'Forty-eight fresh 31-node problems. Time includes proposal generation, membership checking, exact rational audit, and any executed refinement. Refused cells use a cold classical refinement, not an unreported warm start. All final normalized gaps are at most $10^{-7}$. First-face masks are descriptive and use the tolerance stated in the data. Offline construction is reported separately; these timings are hardware-dependent observations, not population speed claims.')
rows=[]
for j,title in enumerate(['Neural, one cell','Neural, three cells','Nearest anchor']):
 rows.append([title,f"{100*V['certified_cell_rates'][j]:.2f}",f"{V['empirical_gains'][j]:.6f}",f"{V['expected_gain_lower_bounds'][j]:.6f}",f"{V['expected_regret_upper_bounds'][j]:.6f}"])
table('validation.tex','Independent validation of frozen, static-gated pipelines','tab:r13-validation','lrrrr','Pipeline & Cell accepted (\\%) & Mean gain & Expected gain floor & Expected regret ceiling',rows,
      'A separate sample of $n=4096$ contexts, three frozen pipelines, and $\\delta=0.05$. Both expectation bounds hold simultaneously under the declared deployment distribution. The model-derived range is $B=\\RThirteenRange$ and the deviation radius is $\\RThirteenRadius$. The gain floor compares with static, not with an optimized nonstatic policy. The regret ceilings are valid but not small enough to imply near-optimality.')
rows=[]
for r in R:
 if r['nodes'] in (31,127,1023):
  rows.append([r['topology'].title(),r['nodes'],f"{r['factored_nonzeros']:,}",f"{r['materialized_nonzeros']:,}",f"{1000*r['factored_lp_seconds']:.2f}",f"{1000*r['materialized_lp_seconds']:.2f}",f"{r['certificate']['upper']-r['certificate']['lower']:.5f}"])
table('scaling.tex','Factored critical-friction computation and independent brackets','tab:r13-scaling','lrrrrrr','Tree & Nodes & Factored entries & Expanded entries & Factored ms & Expanded ms & Bracket width',rows,
      'Both linear programs use HiGHS; expanded time includes materializing $DB$. The final column is the exact rational width from the separate accelerated projected-gradient algorithm, capped at 12,000 iterations and targeting $10^{-4}$. Widths above target are retained, not recorded as successful solves. Sparse arithmetic is not a claim that this first-order algorithm beats the linear-programming solver.')
