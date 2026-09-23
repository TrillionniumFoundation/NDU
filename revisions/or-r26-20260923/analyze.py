"""Write the table with outward rounding from independently checked certificates."""
from pathlib import Path
from fractions import Fraction as F
import json
R=Path(__file__).resolve().parent
rep=json.loads((R/'results/replay.json').read_text());rows=[]
for c in sorted(rep['cases'],key=lambda c:(c['horizon'],c['grid_subdivisions'])):
    ub=F((F(c['uniform_root_gap'])*10**6).__ceil__(),10**6)
    rows.append(f"{c['horizon']} & {c['grid_subdivisions']} & {c['anchors']:,} & {c['dual_planes']:,} & {float(ub):.6f} & {c['not_materialized_history_nodes']:,} \\\\")
tab=r'''\begin{table}[p]\centering
\caption{Continuous promised-state certificates on designed Markov models}\label{tab:r26-envelopes}
\small\begin{tabular}{rrrrrr}\toprule
Dates & Subdivisions & Lower anchors & Upper planes & Uniform gap & Tree nodes\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\begin{minipage}{.97\textwidth}\footnotesize Lower anchors and upper planes are totals over all dates and both regimes. The uniform gap is the largest certified root loss over both regimes, all inherited tiers, and all feasible promises, rounded upward to six decimals. Tree nodes give the hypothetical full binary history tree, which is not constructed. These rows are not timing comparisons.\end{minipage}
\end{table}
'''
(R/'tables').mkdir(exist_ok=True);(R/'tables/envelopes.tex').write_text(tab)
