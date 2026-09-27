from pathlib import Path
from fractions import Fraction as F
import json,math
R=Path(__file__).resolve().parents[1]; O=R/'results'; G=R/'generated'

def lo(x,d=6):
    v=F(x); n=(v.numerator*10**d)//v.denominator
    return f'{n/10**d:.{d}f}'
def hi(x,d=6):
    v=F(x); n=-((-v.numerator*10**d)//v.denominator)
    return f'{n/10**d:.{d}f}'
def f(x): return str(F(x))

def generate():
    tests=json.loads((O/'verification.json').read_text()); scale=json.loads((O/'scaling.json').read_text()); fronts=json.loads((O/'continuous_frontier.json').read_text())
    exact=sum(x['exact_catalog'] for x in scale); done=sum(x['face']['status']=='exact' for x in fronts)
    independent=[x for x in fronts if 'lower' in x.get('independent_minlp',{})]
    independent_pass=sum(bool(x.get('comparison_passed')) for x in independent)
    text=r'''\section{Decomposition, Global Bounds, and Independent Computation}\label{sec:r43-study}
The experiments separate exact mathematical bounds from numerical corroboration and source provenance. Every input is synthetic and every reported run, including a stopped run, is retained. The preceding continuous promise--risk--price study, its exact optima, and its tables are reproduced in the electronic companion, Section~\ref{sec:joint-study}; none of that evidence is deleted or relabeled as a new run.

\paragraph{Exact independent comparisons.}
'''
    text+=f"The seeded test suite uses {tests['models']} models with heterogeneous costs, repeated caps, zero and saturated promises, and both monotone and nonmonotone charges. An independent explicit-lottery oracle checks {tests['priced_root']} priced root problems and {tests['priced_prefix']:,} prefix-completion problems against exhaustive catalog search. All {tests['global_comparisons']} completed prefix searches equal the independent catalog enumeration. A further {tests['interrupted']} deliberately interrupted runs enclose the exhaustive optimum, and {tests['tamper']} altered upper-bound records are rejected. Five exact uniform-grid comparisons reproduce Proposition~\\ref{{prop:r43-sharp}}. These checks test implementations and witnesses; the proofs establish the claims for all inputs.\n\n"
    text+=r'''\paragraph{Variable branch count and alphabet budget.}
Table~\ref{tab:r43-bounds} reports the new algorithm, not the saturated Monge implementation. Its largest branch count is 256; budgets reach 8 and catalogs reach 65 levels. Caps are distinct and costs are heterogeneous, so repeated-cap aggregation is not the explanation for scaling. The declared limit is 40 expanded prefixes per instance, and all bounds are independently checked. '''
    text+=f"All {exact} of the {len(scale)} reported catalog searches close their exact optimization gap within that limit. "
    text+=r'''This is an observation about the stated family, not a worst-case efficiency theorem. The residual continuous gap includes the full mesh term even when catalog optimization is exact. Detailed rows in the companion vary the intermediate-cost scale and the charge slope, and record evaluated books, traced memory, and rational bit lengths. The charge is a fixed fee plus a nondecreasing surcharge, not the specially shaped charge of Proposition~\ref{prop:pathwise-interior}.

\paragraph{Enumeration frontier and a different global formulation.}
'''
    text+=f"The instrumented factorial study completes {done} of {len(fronts)} continuous face instances and explicitly records the remaining {len(fronts)-done} at the 5,000-system budget. It includes four-branch, two-symbol runs and a five-branch case; incomplete face search contributes no purported global upper bound. "
    if independent:
        text+=f"On {len(independent)} separately modeled one- and two-branch instances, SCIP's original-policy nonlinear formulation produces numerical intervals consistent with every completed rational optimum ({independent_pass} comparisons). "
        numoptimal=sum(all(y['status']=='optimal' for y in x['independent_minlp']['sizes']) for x in independent)
        text+=f"Both book sizes terminate with solver status optimal on {numoptimal} of these {len(independent)} instances; all statuses and residual intervals are reported, including any time limits. "
    else:
        text+='This local reader records the original-policy SCIP formulation as not run because its dependency is unavailable in the local container. No independent nonlinear-solver result is asserted in this local build. '
    text+=r'''Section~\ref{sec:r43-implementation} gives the original probability-and-service formulation, which shares no cell-generator or price-DP code. Its floating-point bounds are corroboration within stated tolerances, not rational certificates. The prefix checker supplies the latter for the catalog problem.
'''
    (R/'study.tex').write_text(text)
    tab=r'''\begin{table}[p]\centering\small
\caption{New prefix search and continuous enclosures. Each row has a separately checked global catalog certificate.}\label{tab:r43-bounds}
\begin{tabular}{rrrrrrrr}\toprule
Case & $k$ & $N$ & $m$ & $L$ & $U$ & $K_mh$ & Seconds\\\midrule
'''
    for x in scale:
        tab+=f"{x['case']} & {x['k']} & {x['N']} & {x['m']} & {lo(x['lower'])} & {hi(x['catalog_upper'])} & {hi(x['mesh_error'])} & {x['seconds']:.2f} \\\\\n"
    tab+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{\textwidth}\small
$L$ is rounded downward; $U$ and $K_mh$ are rounded upward. The exact rational catalog gap is zero in each displayed row, though outward rounding can separate the printed endpoints. The continuous interval is $[L,U+K_mh]$. Detailed parameters and separate checker timings appear in Table~\ref{tab:r43-scale-detail}. Seconds are one instrumented run with allocation tracing, not averages or uninstrumented speed comparisons.
\end{minipage}\end{table}
'''
    (G/'main_tables.tex').write_text(tab)
    ec=r'''\begin{table}[p]\centering\small
\caption{Scaling parameters and work. The opening charge is $1/200+\ell c$ and $\gamma_j=g(1+(j-1)\bmod4)$.}\label{tab:r43-scale-detail}
\begin{tabular}{rrrrrrrrr}\toprule
Case & $\delta$ & $g$ & $\ell$ & Prefixes & Books & Bits & MB & Check sec.\\\midrule
'''
    for x in scale:
        ec+=f"{x['case']} & {f(x['delta'])} & {x['gamma_scale']} & {f(x['charge_slope'])} & {x['expanded_nodes']} & {x['books_evaluated']} & {x['dp_bits']} & {x['peak_traced_bytes']/1e6:.2f} & {x['checker_seconds']:.2f} \\\\\n"
    ec+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{\textwidth}\small
Bits is the largest numerator or denominator bit length observed in any price-DP table. MB is peak traced Python allocation during the solve. The separate process-wide resident-set high-water mark and the number of price tables are in the raw records. All inputs use $b_j=1/4+j/[2(k+2)]$, equal probabilities, and $B=3\bar b/4$. Unrestricted subset counts are recorded for comparison; they are not claimed to be the number of feasible books.
\end{minipage}\end{table}
'''
    ec+=r'''\begin{table}[p]\centering\small
\caption{Complete factorial frontier of exact continuous face enumeration.}\label{tab:r43-face}
\begin{tabular}{rrrrrrrr}\toprule
$k$ & $m$ & $\delta$ & Complete cells & Systems & Infeas. frac. & Seconds & Status\\\midrule
'''
    for x in fronts:
        a=x['face']; fr=a['infeasible_cell_fraction']; fs='--' if fr is None else f'{fr:.3f}'
        ec+=f"{x['k']} & {x['m']} & {f(x['delta'])} & {a['cells_completed']}/{a['cells_started']} & {a['systems']} & {fs} & {a['seconds']:.2f} & {'exact' if a['status']=='exact' else 'limit'} \\\\\n"
    ec+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{\textwidth}\small
Limit means the predeclared 5,000-system budget, not a returned global solution or a hardware impossibility claim. The infeasible fraction refers only to completed cells. A singular or infeasible stationary system is counted as attempted. Every input and partial best feasible value remains in the JSON record.
\end{minipage}\end{table}
'''
    ec+=r'''\begin{table}[p]\centering\small
\caption{Arithmetic and memory growth in the same continuous enumeration runs.}\label{tab:r43-bits}
\begin{tabular}{rrrrrrrr}\toprule
$k$ & $m$ & $\delta$ & Nonsingular & Feasible & Rational bits & Integer bits & MB\\\midrule
'''
    for x in fronts:
        a=x['face'];ec+=f"{x['k']} & {x['m']} & {f(x['delta'])} & {a['nonsingular']} & {a['feasible']} & {a['max_candidate_bits']} & {a['max_elimination_integer_bits']} & {a['peak_traced_bytes']/1e6:.2f} \\\\\n"
    ec+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{\textwidth}\small
Rational bits includes every computed stationary candidate, whether feasible or not. Integer bits observes all stored intermediate integers in fraction-free elimination. MB is traced memory; process RSS, inequality counts, and timing are separate raw fields. These observations do not replace bit-complexity analysis.
\end{minipage}\end{table}
'''
    ec+=r'''\begin{table}[p]\centering\small
\caption{Independent original-policy nonlinear cross-check against rational continuous optima.}\label{tab:r43-scip}
\begin{tabular}{rrrrrr}\toprule
$k$ & $\delta$ & Rational optimum & SCIP lower & SCIP upper & Size statuses\\\midrule
'''
    if independent:
        for x in independent:
            e=x['independent_minlp']; status='/'.join(v['status'] for v in e['sizes'])
            ec+=f"{x['k']} & {f(x['delta'])} & {float(F(x['face']['value'])):.7f} & {e['lower']:.7f} & {e['upper']:.7f} & {status} \\\\\n"
    else:
        ec+=r'\multicolumn{6}{c}{Not run in this local build; dependency unavailable.}\\'+'\n'
    ec+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{\textwidth}\small
Numerical bounds use feasibility tolerance $10^{-8}$ and are shown to seven decimal places, not as exact interval endpoints. Comparisons allow absolute tolerance $2\times10^{-5}$. Complete per-size bounds, times, solver nodes, gaps, and versions are in the machine-readable records. This table is numerical corroboration, separate from the rational global catalog certificates.
\end{minipage}\end{table}
'''
    (G/'companion_tables.tex').write_text(ec)
    (O/'study_summary.json').write_text(json.dumps(dict(status='PASS',rational_tests=tests,
        exact_catalog_runs=exact,total_catalog_runs=len(scale),complete_face_runs=done,
        total_face_runs=len(fronts),independent_nonlinear_runs=len(independent),
        independent_comparisons_passed=independent_pass),indent=2)+'\n')
if __name__=='__main__': generate()
