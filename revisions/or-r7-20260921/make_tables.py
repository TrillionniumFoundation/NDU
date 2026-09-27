#!/usr/bin/env python3
from pathlib import Path
import json,os
import numpy as np
from scipy.stats import t
H=Path(__file__).resolve().parent;O=H/'results';D=Path(os.environ.get('NDU_TABLE_OUTPUT',str(H/'tables')));D.mkdir(parents=True,exist_ok=True)
def load(n):return json.loads((O/n).read_text())
def table(name,caption,label,cols,header,rows,note=''):
 s='\\begin{table}[!ht]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\\toprule\n'+header+'\\\\\n\\midrule\n'+'\n'.join(r+'\\\\' for r in rows)+'\n\\bottomrule\\end{tabular}\n'
 if note:s+='\\par\\smallskip\\begin{minipage}{.98\\textwidth}\\small '+note+'\\end{minipage}\n'
 s+='\\end{table}\n';(D/name).write_text(s)
h=load('accepted_continuous_exact.json');labels=['Static','Time','Time--regime','Full state'];rows=[]
for i,r in enumerate(h['rows']):
 inc='---' if i==0 else f"{r['value']['decimal']-h['rows'][i-1]['value']['decimal']:.9f}"
 rows.append(f"{labels[i]} & {r['value']['decimal']:.9f} & {inc} & {r['eta']['decimal']:.9f}")
table('accepted_hierarchy.tex','Accepted continuous-tier information values','tab:accepted-hierarchy','lrrr','Information & Provider reward & Increment & Payment price',rows,'All four classes have the same filled demand 18.021386714, customer utility 28.657506145, and physical cost 9.587377732. All policies are deterministic. Decimals round exact rational values; stock is optimized over the full interval through Lemma~\\ref{lem:stock-pin}.')
r=load('fine_menus.json')
table('fine_menus.tex','Accepted fine-menu optima and deterministic incumbents','tab:fine-menu','rrrr','Tier intervals & Randomized optimum & Deterministic incumbent & Incumbent gap', [f"{x['intervals']} & {x['randomized_value']:.9f} & {x['deterministic_value']:.9f} & {x['deterministic_to_upper']:.9f}" for x in r], 'Same customer, fill, and cost reservations as Table~\\ref{tab:accepted-hierarchy}. Only the first randomized row also has an independent rational R6 certificate. Other menu bounds are floating-point Lagrangian bounds. Deterministic entries are feasible incumbents, not claimed deterministic optima; their nonmonotone gaps reflect extraction, not nonnested feasible sets. The exact continuous optimum is $-5.233445701435\\ldots$.')
methods={'value_gradient':'Learned value--gradient','value_only_equal_oracle':'Learned value only','chebyshev_degree12':'Analytic Chebyshev','cg_rtol1e-4':'Conjugate gradient','sparse_direct':'Sparse direct','dense_cholesky':'Dense Cholesky'}
s=load('portfolio_summary.json');r=[x for key in methods for x in s if x['d']==1024 and x['method']==key]
table('portfolio.tex','Accepted coupled portfolios: 1,024 persistent tier coordinates','tab:portfolio','lrrr','Method & Mean loss/service & Max. bound/service & Time (ms)',[f"{methods[x['method']]} & {x['mean_loss_per_service']:.2e} & {x['max_bound_per_service']:.2e} & {1000*x['median_seconds']:.3f}" for x in r], 'All deployed policies satisfy customer acceptance exactly. Learned rows aggregate ten predeclared training seeds on four fixed test graphs; other rows use those same four graphs. Loss is against the sparse-direct value. Bounds certify the rounded actions in rational arithmetic. Time is the median recorded two-right-hand-side solve plus acceptance calibration, excluding offline training and rational audit. Small direct-method loss is rounded to zero, not asserted identically zero against the unknown real-arithmetic optimum.')
raw=load('portfolio_deployments.json');unc=[]
for d in [64,256,1024]:
 diff=[]
 for seed in range(101,111):
  v=np.mean([x['numerical_loss_per_service'] for x in raw if x['d']==d and x['seed']==seed and x['method']=='value_only_equal_oracle'])
  g=np.mean([x['numerical_loss_per_service'] for x in raw if x['d']==d and x['seed']==seed and x['method']=='value_gradient']);diff.append(v-g)
 mean=float(np.mean(diff));se=float(np.std(diff,ddof=1)/np.sqrt(10));ci=[mean-t.ppf(.975,9)*se,mean+t.ppf(.975,9)*se]
 unc.append({'d':d,'unit':'one training seed, averaged over four fixed test graphs','paired_seed_differences':diff,'mean_improvement':mean,'student_interval_95':ci,'improved_seeds':int(sum(x>0 for x in diff)),'n_seeds':10})
(O/'paired_seed_uncertainty.json').write_text(json.dumps(unc,indent=2)+'\n')
table('seed_uncertainty.tex','Equal-information paired training-seed comparison','tab:seed-uncertainty','rrrrr','$d$ & Mean improvement & Lower 95\\% & Upper 95\\% & Favorable seeds',[f"{x['d']} & {x['mean_improvement']:.2e} & {x['student_interval_95'][0]:.2e} & {x['student_interval_95'][1]:.2e} & {x['improved_seeds']}/10" for x in unc], 'Improvement is value-only loss minus value--gradient loss per service. The Student intervals summarize variation across ten independent training seeds conditional on the four selected test graphs; they are not population guarantees across arbitrary operations networks. The unit is a training seed, not forty independent replications. Every interval includes zero.')
rob=load('accepted_robustness.json');lines=[]
for x in rob:
 a=x['accepted'];nm=x['case'].replace('_',' ').replace('=',' = ')
 if not a['feasible']:lines.append(f"{nm} & infeasible & --- & --- & ---");continue
 gain=a.get('gain_over_accepted_static',a.get('gain'));star='' if x['reference_meets_changed_reservation'] or 'gain_over_accepted_static' in a else r'$^\dagger$'
 active=''.join(k for k,v in zip(['F','U','C'],a['slacks']) if abs(v)<1e-7) or 'none'
 h=x.get('continuous_hierarchy');mem='---' if not h else f"{h[3]['value']-h[2]['value']:.6f}"
 lines.append(f"{nm} & {gain:.6f}{star} & {active} & {a['randomized_reachable_states']} & {mem}")
s='\\begin{longtable}{p{.36\\textwidth}rrrr}\n\\caption{Full accepted-problem robustness design}\\label{tab:robust-all}\\\\\n\\toprule Perturbation & Grid gain & Active & Lottery & Memory gain\\\\\\midrule\\endfirsthead\n\\toprule Perturbation & Grid gain & Active & Lottery & Memory gain\\\\\\midrule\\endhead\n'+ '\n'.join(l+'\\\\' for l in lines)+'\n\\bottomrule\\end{longtable}\n'
s+='Grid gain uses the $0.1$ accepted menu and the reoptimized continuous static comparator under the same reservations. For increased customer reservations the accepted static tier is reoptimized again. The full JSON records original-static feasibility separately. Active constraints are filled demand ($F$), customer utility ($U$), and physical cost ($C$), using a numerical tolerance of $10^{-7}$. Lottery counts are reachable states randomized by the returned LP policy; a positive count does not prove that every optimizer randomizes. Memory gain is the continuous full-state minus time--regime value, computed only when stock identification and the interior quadratic reduction are verified. Dashes do not assert zero. All robustness diagnostics are floating-point, not interval certificates.\n'
(D/'robustness_all.tex').write_text(s)
sel=['canonical','lam=0.1','lam=4.0','power=1.5','power=3.0','persistence=0.6','dispersion=1.2','utility_delta=0.2','fill_delta=0.015','zero_regime_premium']
idx=[i for i,x in enumerate(rob) if x['case'] in sel]
table('robustness.tex','Accepted-problem sensitivity: selected cases','tab:robustness','lrrrr','Case & Grid gain & Active & Lottery & Memory gain',[lines[i] for i in idx],'Definitions and all 31 cases appear in EC Table~\\ref{tab:robust-all}. Reservations and static tiers are recomputed within each perturbed problem. The higher-fill case is infeasible under its stated physical-cost cap. The zero-slope case has no accepted gain.')
table('portfolio_all.tex','All coupled portfolio sizes','tab:portfolio-all','rlrrr','$d$ & Method & Mean loss/service & Max. bound/service & Time (ms)',[f"{x['d']} & {methods[x['method']]} & {x['mean_loss_per_service']:.2e} & {x['max_bound_per_service']:.2e} & {1000*x['median_seconds']:.3f}" for x in load('portfolio_summary.json')],'Same definitions and protocol as main Table~\\ref{tab:portfolio}. No favorable-seed selection is used.')
print(json.dumps(unc,indent=2))
