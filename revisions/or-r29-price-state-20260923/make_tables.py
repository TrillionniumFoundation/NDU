#!/usr/bin/env python3
from pathlib import Path
from fractions import Fraction as F
import json,sys
R=Path(__file__).resolve().parent

def run():
    timing=json.loads((R/'results/timings.json').read_text())['measurements']
    selected=[x for x in timing if x['name'] in {
        'markov-T8-S2-seed111','markov-T16-S2-seed119','markov-T32-S2-seed135','markov-T64-S2-seed167',
        'markov-T16-S3-seed120','markov-T32-S3-seed136','markov-T64-S3-seed168',
        'markov-T32-S2-seed341-corridor','markov-T64-S2-seed373-corridor'}]
    lines=[r'\begin{table}[!htbp]\centering',
           r'\caption{Exact computation on coupled recombining graphs.}\label{tab:r29-scaling}',
           r'\begin{tabular}{lrrrrrr}\toprule',
           r'Design & Vertices & Knots & Segments & Price pairs & Solve (s) & Audit (s)\\\midrule']
    for x in selected:
        parts=x['name'].split('-');design=parts[1][1:]+' dates, '+parts[2][1:]+' states'
        if x['name'].endswith('corridor'):design+='*'
        lines.append(f"{design} & {x['public_nodes']} & {x['global_breakpoints']} & {x['stored_segments']} & {x['reachable_price_pairs']} & {x['solve_seconds']:.3f} & {x['verify_seconds']:.3f} \\\\")
    lines +=[r'\bottomrule\end{tabular}',r'\begin{minipage}{.97\linewidth}\small *Fixed shared time-only table with positive corridor release. Knots count the global union, segments count all stored response pieces, and price pairs count reached public/incoming-price states. Every value has an exact system-level rational primal--dual equality. Times are single-run platform observations, not replicated speed estimates; audit is independent of the generator.\end{minipage}',r'\end{table}']
    memory=json.loads((R/'results/memory.json').read_text())['families']
    m=next(x for x in memory if x['k']==8)
    lines+= [r'\begin{table}[!htbp]\centering',r'\caption{The exact memory frontier for eight renewal regimes.}\label{tab:r29-memory}',
             r'\begin{tabular}{rrrr}\toprule',r'Symbols & Writable bits & Optimal reward & Loss from full information\\\midrule']
    for x in m['frontier']:
        def tex(v):
            z=F(v);return '$'+str(z)+'$'
        lines.append(f"{x['symbols']} & {x['bits']} & {tex(x['value'])} & {tex(x['loss'])} \\\\")
    lines +=[r'\bottomrule\end{tabular}',r'\begin{minipage}{.9\linewidth}\small Caps are $b_j=j/9$ and the exact root promise is $1/2$. Bits count an index into a stored decision table, not the read-only table or numeric storage. Two bits permit four symbols; unused capacity is not required. No memory costs are calibrated.\end{minipage}',r'\end{table}']
    p=R/'tables.tex';s='\n'.join(lines)+'\n'
    chosen=next(x for x in timing if x['name']=='markov-T64-S3-seed168')
    tree=json.loads((R/'results/tree_comparison.json').read_text())['instances']
    err=max(x['absolute_value_difference'] for x in tree)
    mantissa,exponent=f'{err:.2e}'.split('e')
    metrics=(r'\newcommand{\PriceSolveSeconds}{'+f"{chosen['solve_seconds']:.2f}"+'}\n'+
             r'\newcommand{\PriceAuditSeconds}{'+f"{chosen['verify_seconds']:.2f}"+'}\n'+
             r'\newcommand{\TreeDiscrepancy}{'+mantissa+r'\times10^{'+str(int(exponent))+'}}\n')
    if '--check' in sys.argv: assert (R/'metrics.tex').read_text()==metrics
    else:(R/'metrics.tex').write_text(metrics)
    if '--check' in sys.argv:assert p.read_text()==s
    else:p.write_text(s)
if __name__=='__main__':run()
