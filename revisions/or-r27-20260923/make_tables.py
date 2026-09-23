"""Render only audited rational endpoints; upper slack decimals round outward."""
import json,sys
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parent
s=json.loads((R/'results/replay.json').read_text())
rows=[]
for family,title in [('inherited ray holdout','Inherited ray holdouts; no query price reused'),('new off-ray query','New off-ray queries; same frozen cache')]:
    rows.append(r'\multicolumn{5}{l}{\textit{'+title+r'}}\\')
    for rec in s['tables']:
        if rec['study']!=family:continue
        q=rec['rho'];rho='$'+q+'$'
        vals=rec['display_outward_8dp']
        for k in vals:
            true=F(rec['mean_slack_upper'][k]);require=F(vals[k])>=true and F(vals[k])-true<F(1,10**8)
            assert require,(k,vals[k],true)
        rows.append(f"{rho} & {rec['queries']} & {vals['outer_upper']} & {vals['nominal_cache_upper']} & {vals['cache_upper']} "+r'\\')
    rows.append(r'\addlinespace')
table=r'''\begin{table}[htbp]
\centering
\caption{Certified comparator upper slack under correlated parameter changes}
\label{tab:r27-cache}
\begin{tabular}{lrrrr}
\toprule
Radius & Queries & Outer & One price & Three prices\\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule
\end{tabular}
\par\smallskip
\begin{minipage}{\textwidth}
Entries are means of $U-L_K$, where $L_K$ is an independently checked restricted feasible value. Each decimal is rounded upward. The one-price cache uses the nominal anchor; the three-price cache also uses the inherited radii $1/16$ and $1/4$. No anchor query is included in the first panel. Off-ray queries change coefficient directions, not merely radii. Initial prices and the offline validation optimizations are charged separately; these are certificate-quality comparisons, not matched timings.
\end{minipage}
\end{table}
'''
(R/'tables').mkdir(exist_ok=True)
p=R/'tables/correlated_cache.tex'
if '--check' in sys.argv:assert p.read_text()==table,'table not generated from current audit'
else:p.write_text(table)
print('PASS: all 30 table endpoints rounded outward from exact audit means')
