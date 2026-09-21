#!/usr/bin/env python3
from pathlib import Path
import csv,json
H=Path(__file__).resolve().parent;O=H/'results';T=H/'tables';T.mkdir(exist_ok=True)
def load(n):return list(csv.DictReader((O/n).open()))
def table(name,caption,label,header,rows,align,note=''):
 s='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n\\small\n\\begin{tabular}{'+align+'}\n\\toprule\n'+' & '.join(header)+r' \\'+'\n\\midrule\n'
 s+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
 s+='\n\\bottomrule\n\\end{tabular}\n'
 if note:s+='\\par\\smallskip\\begin{minipage}{0.96\\textwidth}\\footnotesize '+note+'\\end{minipage}\n'
 s+='\\end{table}\n';(T/name).write_text(s)
def f(x):return f'{float(x):.6f}'
def main():
 a=load('adaptivity.csv');sx=json.loads((O/'static_exact.json').read_text());rg=json.loads((O/'restriction_regime.json').read_text())
 rows=[['Frozen $0.5$',f(a[0]['reward']),'--'],['Best continuous static',f(sx['value']),'0.076947'],['Best grid static / time / inherited-only',f(a[1]['reward']),'--'],['Time and regime',f(rg['reward']),'0.820860'],['Full $(t,z,q)$',f(a[3]['reward']),'0.050593']]
 table('adaptivity.tex','Optimized contract classes and successive information increments','tab:r6adapt',['Contract rule','Reward','Increment'],rows,'lrr','The first increment improves the frozen tier; the last two follow the nested grid-class chain. Continuous and grid static values are reported separately. Stock uses observed regime in every row.')
 labels={'unconstrained':'Provider relaxation','service_90':'Fill $0.90$','service_92':'Fill $0.92$','same_service':'Static fill','same_service_customer':'Static fill and utility','same_service_customer_cost':'Static fill, utility, cost','service_95_customer':'Fill $0.95$ and utility','service_98_customer':'Fill $0.98$ and utility'}
 rows=[[labels[r['policy']],f(r['reward']),f(r['physical']),f(r['customer']),f(r['fill_rate'])] for r in load('service_frontier.csv')]
 ref=json.loads((O/'static_service_reference.json').read_text());rows.insert(0,['Continuous static reference',f(ref['reward']),f(ref['physical']),f(ref['customer']),f(ref['fill_rate'])])
 table('frontier.tex','Provider reward, physical cost, customer utility, and discounted fill','tab:r6frontier',['Protocol / requirement','$W$','$C$','$U$','Fill'],rows,'lrrrr','The last column is expected discounted filled demand divided by expected discounted demand. Incremental utilities exclude a common retainer. At a 0.95 or 0.98 floor the displayed operating solutions need a larger retainer to satisfy a zero provider outside option.')
 rows=[[f(r['level']),f(r['reward']),f(r['static_best']),f(r['adaptive_gain']),f(r['movement'])] for r in load('comparative_statics.csv') if r['parameter']=='lam']
 table('sensitivity.tex','Adjustment cost, adaptive value, and squared movement','tab:r6sensitivity',['$\\lambda$','Full reward','Best static grid','Gain','Movement'],rows,'rrrrr','Each static comparator is reoptimized at its own coefficient. Movement is the expected discounted sum of squared tier changes, without multiplying by the coefficient.')
 rows=[[r['seed'],'Value' if r['mode']=='value_only' else 'Value + gradient',f(r['initial_policy_loss']),f(r['value_rmse']),f(r['finite_chain_policy_bound'])] for r in load('learned_critics.csv')]
 table('learning.tex','Actual learned-critic deployment on the operational evaluation chain','tab:r6learning',['Seed','Training targets','Policy loss','Value RMSE','Residual budget'],rows,'rlrrr','Both methods use 2,048 identical sample locations and 6,000 matched optimization steps per seed. Derivative training receives additional numerical derivative labels. The budget is the floating evaluation of the full finite-chain formula, not a continuum certificate; it is intentionally not replaced by the observed initial policy loss.')
if __name__=='__main__':main()
