#!/usr/bin/env python3
"""Generate every new reported number from recorded results, never from literals."""
from pathlib import Path
import json,statistics as st
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent;OUT=HERE/'results';TAB=HERE/'tables'
s=json.loads((OUT/'summary.json').read_text());v=json.loads((OUT/'verification.json').read_text())
old=json.loads((OUT/'old_diagnostics.json').read_text());fd=json.loads((OUT/'fd_sensitivity.json').read_text())
timing=json.loads((OUT/'repeated_timing.json').read_text());groups=s['groups']
family={'cycle':'Cycle','erdos':'Random-edge','geometric':'Geometric','weighted_block':'Weighted block'}
method={'cold_slsqp':'Cold SLSQP','value':'Value','gradient':'Value--gradient'}

def table(name,caption,label,headers,rows,align,note):
    # Stable plain TeX, in the OR table-at-end convention.
    text=r'\begin{table}[p]\centering'+'\n'+r'\caption{'+caption+r'}\label{'+label+'}\n'
    text+=r'\setlength{\tabcolsep}{3.5pt}\begin{tabular}{'+align+'}\n\\toprule\n'
    text+=' & '.join(headers)+r' \\'+'\n\\midrule\n'
    text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    text+='\n\\bottomrule\n\\end{tabular}\n\\begin{minipage}{.98\\textwidth}\\small\n'+note+'\n\\end{minipage}\n\\end{table}\n'
    (TAB/name).write_text(text)

rows=[]
for g in groups:
    rows.append([family[g['family']],method[g['method']],f"{g['1e-07']['met']}/{g['n']}",
                 f"{g['final_max_bound']:.1e}",f"{g['final_mean_gain']:.6f}",
                 f"{g['1e-05']['median_ms']:.2f}",f"{g['1e-07']['median_ms']:.2f}"])
table('matched_accuracy.tex','Certified refinement under noncentered forcing','tab:r12-matched',
      ['Family','Pipeline',r'\shortstack{Met\\tolerance}',r'\shortstack{Maximum\\final gap}',
       r'\shortstack{Mean\\final gain}',r'\shortstack{Time at\\$10^{-5}$}',r'\shortstack{Time at\\$10^{-7}$}'],rows,'llrrrrr',
      'Gaps and gains are per discounted service--review. Times are median milliseconds across the declared instances and, for learned pipelines, frozen training seeds. They include candidate generation, projection, rational audit, gating, and actual refinement; a cold pipeline starts at the same optimized static protocol. Common setup is recorded separately. These are not independent timing repetitions or a speedup claim. The last column compares the same certified error tolerance, not different solver stopping flags.')
rows=[]
for g in groups:
    if g['method']=='cold_slsqp':continue
    rows.append([family[g['family']],method[g['method']],f"{g['pre_repair_feasible']}/{g['n']}",f"{g['mean_radial_scale']:.3f}",f"{g['mean_before_gain']:.4f}",f"{g['mean_radial_gain']:.4f}",f"{g['mean_projection_gain']:.4f}",f"{g['mean_flow_gain']:.4f}"])
table('repair.tex','Raw actors and alternative acceptance repairs','tab:r12-repair',
      ['Family','Actor',r'\shortstack{Feasible\\before}',r'\shortstack{Mean\\scale}',r'\shortstack{Before\\gain}',
       r'\shortstack{Radial\\gain}',r'\shortstack{Projection\\gain}',r'\shortstack{Tree-flow\\gain}'],rows,'llrrrrrr',
      'Before denotes box clipping without continuation repair. Negative raw outcomes are retained. Projection minimizes weighted Euclidean actor distance, not economic loss. Tree-flow uses nonnegative child-to-parent payment transfers and a box-limited step. All reported repaired policies receive the same exact feasibility and value audit. All gains are relative to the reoptimized static protocol per discounted service--review; the comparison is not field-calibrated.')
rows=[]
for f in family:
    for m in ('value','gradient'):
        rr=[r for r in old if r['family']==f and r['method']==m]
        rows.append([family[f],method[m],f"{st.mean(x['radial']['gain'] for x in rr):.6f}",
                     f"{st.median(x['proposal_bound_gain_ratio'] for x in rr):.2f}",
                     f"{st.median(x['selected_bound_gain_ratio'] for x in rr):.2f}"])
table('gate_ratios.tex','Original nonlinear transfer: certificate size relative to available gain','tab:r12-ratios',
      ['Family','Actor',r'\shortstack{Mean raw\\gain}',r'\shortstack{Proposal gap /\\classical gain}',r'\shortstack{Selected gap /\\classical gain}'],rows,'llrrr',
      'Ratios are medians across the original two instances and ten training seeds, using the classical certified feasible gain as denominator. The selected gap uses both the proposal and static upper bounds, as in the main-paper gate equation. The weighted-block gate still has a large gap; a no-harm choice is not an accuracy certificate. All forty weighted-block pipelines were subsequently refined by the cached classical solver and independently audited.')
rows=[]
for f in family:
    for m in method:
        rr=[r for r in timing if r['family']==f and r['method']==m]
        times=[r['pipeline']['hits']['1e-07']['seconds']*1000 for r in rr]
        rows.append([family[f],method[m],len(times),f'{min(times):.2f}',f'{st.median(times):.2f}',f'{max(times):.2f}'])
table('timing_repetitions.tex','Timing variation separated from test-instance and training-seed variation','tab:r12-repeated',
      ['Family','Pipeline','Repetitions','Minimum','Median','Maximum'],rows,'llrrrr',
      'Milliseconds to the same $10^{-7}$ certified tolerance on the first new instance of each family, one frozen training seed, five repetitions after one warmup. Pipeline order is randomized within repetition. This separate experiment does not enlarge the economic test sample; every timing record and final policy is retained.')
rows=[]
for h in ('1/80','1/40','1/20'):
    for extra in (0.,1e-7,1e-5):
        rr=[r for r in fd if r['h']==h and r['extra_endpoint_gap_per_review']==extra]
        rows.append([f'${h}$',f'{extra:.0e}',f"{max(r['measured_directional_error'] for r in rr):.3g}",f"{max(r['bound'] for r in rr):.5f}"])
table('fd_sensitivity.tex','Directional targets: step size and certified oracle error','tab:r12-fd',
      ['Step size',r'\shortstack{Additional endpoint\\error allowance}',r'\shortstack{Maximum measured\\direction error}',r'\shortstack{Maximum certified\\target-error bound}'],rows,'rrrr',
      'Twelve independently generated training-sized problems. Endpoint values are re-solved and rationally certified at every step size. The extra error column is an explicit sensitivity allowance added to each endpoint certificate, not a claim that fresh noisy labels were simulated. Measured error compares with the separately solved central actor and is numerical; the displayed bound includes oracle gaps and the finite-difference bias bound.')
large=[r for r in old if 'refined' in r]
macros={'RtwInstances':s['instances'],'RtwDeployments':s['deployments'],'RtwBoundaryInstances':s['static_boundary_instances'],
        'RtwStaticGap':f"{s['static_max_bound']:.3g}",'RtwCertificates':v['verified_certificates'],
        'RtwSubtrees':v['exact_subtree_checks'],'RtwTiers':v['exact_tier_checks'],
        'RtwFinalGap':f"{max(g['final_max_bound'] for g in groups):.3g}",
        'RtwLargeGap':f"{max(r['refined']['bound'] for r in large):.3g}",
        'RtwPairedMean':f"{s['crossed_projection_difference']['mean']:.6f}",
        'RtwPairedLower':f"{s['crossed_projection_difference']['percentile95'][0]:.6f}",
        'RtwPairedUpper':f"{s['crossed_projection_difference']['percentile95'][1]:.6f}",
        'RtwRawNegative':sum(r['diagnosis']['projection']['gain']<0 for r in json.loads((OUT/'new_records.json').read_text()) if r['method']!='cold_slsqp'),
        'RtwLargeMedianMs':f"{1000*st.median(r['pipeline_seconds'] for r in large):.2f}"}
for key in ('RtwStaticGap','RtwFinalGap','RtwLargeGap'):
    mantissa,exponent=macros[key].split('e')
    macros[key]=r'\ensuremath{'+mantissa+r'\times10^{'+str(int(exponent))+'}}'
(TAB/'metrics.tex').write_text('\n'.join('\\providecommand{\\'+name+'}{'+str(val)+'}' for name,val in macros.items())+'\n')
print(json.dumps(macros,indent=2))
