"""Produce journal tables from the executed rational-certificate summaries."""
import json
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'results';T=R/'tables';T.mkdir(exist_ok=True)
def load(p):return json.loads(p.read_text())
def table(name,caption,label,cols,lines,note):
 s='\\begin{table}[htbp]\n\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+'\n'.join(lines)+'\n\\bottomrule\n\\end{tabular}\n\\par\\smallskip\n\\begin{minipage}{.98\\textwidth}\\footnotesize '+note+'\\end{minipage}\n\\end{table}\n'
 (T/(name+'.tex')).write_text(s)
h=load(O/'hierarchy_summary.json')['summary'];a,b=h
steps=['Fixed to time-only','Time-only to regime','Regime to two-period memory','Two-period memory to full history']
lines=[r'& \multicolumn{2}{c}{Legacy amendments} & \multicolumn{2}{c}{Markov service tiers} \\',r'Expansion & Mean gain & Share (\%) & Mean gain & Share (\%) \\ \midrule']
for i,n in enumerate(steps):lines.append(f"{n} & {a['increment_means'][i]:.6f} & {100*a['shares_of_mean_total'][i]:.2f} & {b['increment_means'][i]:.6f} & {100*b['shares_of_mean_total'][i]:.2f} \\\\")
lines +=[r'\midrule',f"Total & {a['mean_total']:.6f} & 100.00 & {b['mean_total']:.6f} & 100.00 \\\\"]
table('hierarchy','Value of progressively richer optimized contracts','tab:hierarchy','lrrrr',lines,
 f"There are 24 common instances per family and five optimized classes per instance. Means use certified lower endpoints; the complete enclosing increment intervals are in the data. Maximum optimization-bracket widths are {a['max_gap']:.2e} and {b['max_gap']:.2e}, respectively. Shares divide each mean increment by the within-family total. Raw value units differ between families. Current regime omits inherited tier and remaining promise.")
r=load(O/'radius_summary.json');lines=[r'Uncertainty radius & Mean upper bound on outer-set slack \\ \midrule']
for a in r['summary']:lines.append(f"${a['rho']}$ & {a['mean_outer_slack_upper']:.9f} \\\\")
table('radius','The common outer comparator becomes locally tight','tab:radius','lr',lines,
 f"Eight fixed contexts and ten radii, with a directly optimized true and outer comparator at each pair (160 certificates). Entries average the outer certified upper value minus the true certified lower value. At zero the true outer-set slack is exactly zero; the displayed residual is the optimization bracket. Maximum individual bracket width is {r['max_gap']:.2e}. This isolates outer-set loss and is not a calibrated uncertainty experiment.")
c=load(O/'cache_summary.json');print('Cache summary',c)
lines=[r'Quantity & Value \\ \midrule',r'Certified anchors & 4 \\',r'Nearby reward queries & 32 \\',r'Restricted optimizations in deployed query evaluation & 0 \\',r'Query optimizations used only for offline validation & 32 \\']
for key,label in [('L_trace_bound','Curvature trace bound'),('mean_slack_upper','Mean envelope slack upper bound'),('max_slack_upper','Maximum envelope slack upper bound')]:
 if key in c:lines.append(f"{label} & {float(c[key]):.9f} \\\\")
# Exact schema validation prevents omission of metrics after a record change.
if not any('Maximum envelope' in x for x in lines):
 for key,label in [('L','Curvature trace bound'),('mean_cache_slack_upper','Mean envelope slack upper bound'),('max_cache_slack_upper','Maximum envelope slack upper bound')]:
  if key in c:lines.append(f"{label} & {float(c[key]):.9f} \\\\")
assert any('Maximum envelope' in x for x in lines),c
table('cache','Restricted-comparator reuse with fixed geometry','tab:cache','lr',lines,
 'A common time-only feasible set and switching coefficient are held fixed. Each query evaluates all four analytical anchor envelopes and takes their minimum. The slack is cached upper value minus independently certified query lower value; it therefore encloses the actual upper-bound loss. Anchor construction, policy acceptance checks, storage, and offline validation are separate costs. No end-to-end timing advantage is inferred.')
s=load(R.parent/'or-r24-20260923/results/timing_analysis.json')['summary'];methods=['lifted-price-continuation','tanh-gradient','rbf-direct'];lines=[r'Nodes & Lifted (ms) & Tanh (ms) & RBF (ms) \\ \midrule'];pres=[]
for nodes in (63,127,255):
 rows=[next(x for x in s if x['spec'][0]==nodes and x['tol']==1e-5 and x['method']==m) for m in methods]
 for x in rows[1:]:
  assert x['fallback_fraction']==1 and x['observed_crossing_queries'] is None
  assert x['paired_savings_ms']['percentile95'][1]<0
 lines.append(str(nodes)+' & '+' & '.join(f"{x['total_ms']['mean']:.2f}" for x in rows)+r' \\');pres.extend(rows)
table('historical','Preserved strict-target end-to-end timing comparisons','tab:historical','rrrr',lines,
 r'Historical R24 measurements, unchanged. Target $10^{-5}$; 32 held-out contexts and three repetitions per method and size. Both learned routes have 100\% fallback at each size. Their paired saving intervals versus lifted continuation are entirely negative. Offline label/fitting costs are retained separately and cannot turn negative online savings into amortization. These are not newly timed R25 measurements.')
(O/'analysis.json').write_text(json.dumps({'status':'ANALYZED','tables':4,'historical_source':'revisions/or-r24-20260923/results/timing_analysis.json','historical_strict_rows':pres},indent=2)+'\n')
