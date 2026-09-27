"""Render the new study tables solely from executed rational JSON records."""
from pathlib import Path
from fractions import Fraction as F
import json
R=Path(__file__).resolve().parents[1]
def frac(s):
    v=F(s)
    return str(v.numerator) if v.denominator==1 else r'\frac{'+str(v.numerator)+'}{'+str(v.denominator)+'}'
def math(s):return '$'+frac(s)+'$'
def book(xs):return '$('+','.join(frac(x) for x in xs)+')$'
def make():
    out=[]
    def begin(caption,label,cols,heads):
        out.extend([r'\begin{table}[p]\centering\small',r'\caption{'+caption+r'}\label{'+label+'}',r'\begin{tabular}{'+cols+r'}\toprule',heads+r'\\\midrule'])
    def end(note=''):
        out.append(r'\bottomrule\end{tabular}')
        if note:out.append(r'\par\smallskip\begin{minipage}{.96\textwidth}\footnotesize '+note+r'\end{minipage}')
        out.append(r'\end{table}\clearpage')
    load=lambda n:json.loads((R/'results'/f'{n}.json').read_text())
    begin('Continuous institutional gaps at eight root promises.','tab:r42-gap','rrrr',r'$B$ & $V_2^E-V_2^P$ & Transport lower bound & $V_2^P-V_2^D$')
    for x in load('promise_gap'):
        out.append(' & '.join(math(x[k]) for k in ('B','expected_pathwise_gap','transport_sufficient_lower','pathwise_deterministic_gap'))+r'\\[3pt]')
    end('Equal branch probabilities; zero selected-level charges. These are globally optimized continuous books. A zero sampled gap does not establish equality at every intermediate promise.')
    begin('Joint continuous books with endogenous promises, risk ceilings, and charges.','tab:r42-joint','rrlrr',r'$B$ & $\delta$ & Charge & Optimal book & Net payoff')
    for x in load('joint_paths'):
        if x['B'] not in ('2/5','17/40'):continue
        fee='$0$' if x['beta']=='0' else '$c/50+1/200$'
        out.append(' & '.join((math(x['B']),math(x['delta']),fee,book(x['codebook']),math(x['net'])))+r'\\[3pt]')
    end('Caps $(1/4,1/2,3/4)$, probabilities $(7/20,3/5,1/20)$, and two available symbols. The full 32-case archive also records targets, intermediate tiers, and lotteries.')
    begin('Exact grid values compared with the continuous optimum $7169/10400$.','tab:r42-mesh','rrrrr',r'$N$ & Grid book & Actual gap & Certified gap $K_2h$ & Seconds')
    for x in load('mesh_convergence'):
        out.append(' & '.join((str(x['N']),book(x['codebook']),math(x['actual_gap']),math(x['certified_gap']),f"{x['seconds']:.3f}"))+r'\\[3pt]')
    end(r'Interior promise $B=2/5$, tolerance $\delta=1/16$, and charge $c/50+1/200$. Every policy meets its promise and ceiling without slack. Timings are single reference-implementation solves, not averaged performance estimates.')
    begin('Separate scaling of all-promise charged catalog enumeration.','tab:r42-scaling','rrrrr',r'Branches $k$ & Catalog $N$ & Budget $m$ & Feasible books checked & Seconds')
    for x in load('new_algorithm_scaling'):
        out.append(' & '.join((str(x['k']),str(x['N']),str(x['m']),str(x['books']),f"{x['seconds']:.3f}"))+r'\\')
    end('Each row solves the new nonsaturated problem with a realization ceiling and actual codeword charges. These measurements do not reuse the inherited saturated-frontier timings and do not measure the exponential continuous face search.')
    (R/'generated'/'tables.tex').write_text('\n'.join(out)+'\n')
if __name__=='__main__':make()
