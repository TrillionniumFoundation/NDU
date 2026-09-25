"""Generate the full screening table from measured records, without hand edits."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def run():
    rows=json.loads((R/'results/CONTROLLED.json').read_text())
    text=r'''\begin{table}[p]\centering
\caption{Certified catalog refinement. All optima equal $15/64$; all reduced catalogs have three commands and one eligibility class.}\label{tab:screen53}
\small\setlength{\tabcolsep}{3pt}
\begin{tabular}{rrrrrrrrrr}
\toprule
$k$ & Added & $E$ & Removed & States & Screen & Full & Reduced & Check & Bytes\\
 & & & & full/reduced & ms & ms & ms & ms & full/transfer\\
\midrule
'''
    for d in rows:
        text+=f"{d['histories']} & {d['insertions']} & {d['full_classes']} & {d['screened']} & {d['full_states']}/{d['screened_states']} & {1000*d['screening_seconds']:.2f} & {1000*d['full_seconds']:.2f} & {1000*d['reduced_seconds']:.2f} & {1000*d['transfer_check_seconds']:.2f} & {d['full_certificate']['compressed_bytes']}/{d['transfer_certificate']['compressed_bytes']} "+r'\\'+'\n'
    text+=r'''\bottomrule
\end{tabular}
\par\smallskip\begin{minipage}{0.98\textwidth}\small
Notes. Screen is the new exclusion calculation; Full and Reduced include resource-grid construction and policy recovery but not serialization. Check verifies both the exclusion chain and the reduced global certificate. Bytes are compressed certificate sizes. The transferred certificate retains the original instance and can exceed the full certificate on small cases. Removed includes the unused, zero-charge endpoint one. The gross incumbent bound excludes none of the added positive-charge commands. These are controlled tests at absolute tolerance $1/10$, not replacements for the earlier fine-accuracy study.\end{minipage}
\end{table}
'''
    (R/'generated').mkdir(exist_ok=True);(R/'generated/main_table.tex').write_text(text)
if __name__=='__main__':run()
