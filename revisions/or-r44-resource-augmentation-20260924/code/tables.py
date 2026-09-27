"""Generate new tables solely from executed JSON evidence."""
from pathlib import Path
from fractions import Fraction as F
import json
R=Path(__file__).resolve().parents[1]
rows=json.loads((R/'results/scaling.json').read_text())['rows']
def dec(x,n=5):
    v=float(F(x))
    return '0' if not v else (f'{v:.2e}' if abs(v)<10**(-n+1) else f'{v:.{n}f}')
main=r'''\begin{table}[p]\centering
\caption{Two-price recovery on the declared synthetic family. The original-budget interval $[L_m,U_m]$ and augmented payoff $J_U$ concern different memory budgets. All promise and positive risk residuals are exactly zero.}\label{tab:r44-scaling}
\small\begin{tabular}{rrrrrrrr}\toprule
$k$ & $N$ & $m$ & $|c^U|$ & Calls & $U_m-L_m$ & $J_U-U_m$ & $\Omega$\\\midrule
'''
for x in rows:
    main+=' & '.join([str(x[k]) for k in ['k','N','m','union_size','oracle_calls']]+[dec(x['original_interval_width']),dec(F(x['augmented_value'])-F(x['original_upper'])),dec(x['charge_excess'])])+r'\\'+'\n'
main+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{.97\textwidth}\footnotesize
Rows follow the complete parameter order in Table~\ref{tab:r44-work}. The first seven use zero charges; the next two use affine charges, and the last three form an accuracy path. A negative $J_U-U_m$ is permitted and is bounded below by $-e-\Omega$. The table does not assert that the original-budget interval closes as price accuracy increases.
\end{minipage}\end{table}
'''
(R/'generated').mkdir(exist_ok=True)
(R/'generated/main_table.tex').write_text(main)
comp=r'''\begin{table}[p]\centering
\caption{Complete recovery work and accuracy records. Wall times and peak traced memory are single instrumented observations, not repeated performance averages. Checker time is measured separately.}\label{tab:r44-work}
\small\begin{tabular}{rrrrrrrrr}\toprule
Case & $\delta$ & Charge slope & $\varepsilon$ & Time (s) & Check (s) & Peak (MB) & Bits & $e$\\\midrule
'''
for x in rows:
    comp+=' & '.join([str(x['case']),dec(x['delta'],3),dec(x['charge_slope'],2),f"{float(F(x['epsilon'])):.0e}",f"{x['seconds']:.3f}",f"{x['checker_seconds']:.3f}",f"{x['peak_bytes']/1e6:.3f}",str(x['max_dp_bits']),f"{float(F(x['price_error'])):.2e}"])+r'\\'+'\n'
comp+=r'''\bottomrule\end{tabular}
\end{table}
\begin{table}[p]\centering
\caption{Original-budget and continuous-comparison terms. The mesh column equals $K_mh$, not an optimization error.}\label{tab:r44-values}
\small\begin{tabular}{rrrrrr}\toprule
Case & $L_m$ & $U_m$ & $J_U$ & $K_mh$ & $e+\Omega$\\\midrule
'''
for x in rows:
    comp+=' & '.join([str(x['case'])]+[dec(x[k]) for k in ['original_lower','original_upper','augmented_value','mesh_error']]+[dec(F(x['price_error'])+F(x['charge_excess']))])+r'\\'+'\n'
comp+=r'\bottomrule\end{tabular}\end{table}'+'\n'
(R/'generated/companion_tables.tex').write_text(comp)
