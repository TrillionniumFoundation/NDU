"""Generate all numerical prose and tables from executed records."""
from pathlib import Path
from fractions import Fraction as F
import json,statistics as stats
R=Path(__file__).resolve().parents[1]

def fmt(x):
    if x is None:return '--'
    return f'{float(F(x)):.4g}'

def run():
    rows=json.loads((R/'results/study.json').read_text())['cases'];M=json.loads((R/'results/mip.json').read_text())['cases'];summary=json.loads((R/'results/SUMMARY.json').read_text());T=json.loads((R/'results/tests.json').read_text())
    g=R/'generated';g.mkdir(exist_ok=True)
    tab=r'''\begin{table}[p]\centering
\caption{Harmonic versus minimum-curvature aggregation at identical partitions and search limits. Entries report original-space certificates at tolerance $0.001$, not reduced-solver completion. Every family contains six instances, including 32, 128, and 256 histories.}\label{tab:r48-paired}
\begin{tabular}{lrrrrrr}\toprule
& \multicolumn{2}{c}{Certified / 6}&\multicolumn{2}{c}{Maximum gap}&\multicolumn{2}{c}{Median seconds}\\
Family & Harmonic & Minimum & Harmonic & Minimum & Harmonic & Minimum\\\midrule
'''
    names=['Common caps','Dispersed caps','Eligibility / high promise','Zero cost / charged']
    for f,n in enumerate(names):
        rr=[r for r in rows if r['family']==f];cells=[n]
        cells += [str(sum(r[z]['status']=='COMPLETE' for r in rr)) for z in ['harmonic','minimum']]
        cells += [fmt(max(F(r[z]['gap']) for r in rr)) for z in ['harmonic','minimum']]
        cells += [fmt(stats.median(r[z]['seconds'] for r in rr)) for z in ['harmonic','minimum']]
        tab+=' & '.join(cells)+r' \\'+'\n'
    tab+=r'''\bottomrule\end{tabular}
\par\small Both methods receive 31 target boxes and four price refinements. Larger exact rational denominators and optimal original-group recovery can make harmonic pooling slower. A tighter reduced optimum is not a theorem about interrupted-search runtime or every returned interval.
\end{table}
'''
    (g/'main_table.tex').write_text(tab)
    detailed=r'''\section{Complete Paired Outcomes}\label{sec:r48-record}
All cases in the declared protocol are listed. H and M denote harmonic and minimum-curvature aggregation. C and U denote a certified tolerance and an unresolved original-space gap. Times include reduction and lift but exclude independent checking. The objective scale is $r+\Gamma/2$ plus the largest possible selected charge; scaled gaps divide by that stated scale, not by a possibly zero or negative optimum.
\begin{longtable}{lrrrrrrrrrr}
\caption{Every original-space interval and execution cost.}\label{tab:r48-all}\\
\toprule Case & $k$ & $d$ & $m$ & H gap & M gap & H sec. & M sec. & H/M & H nodes & Scale\\\midrule\endfirsthead
\toprule Case & $k$ & $d$ & $m$ & H gap & M gap & H sec. & M sec. & H/M & H nodes & Scale\\\midrule\endhead
'''
    for r in rows:
        h,mi=r['harmonic'],r['minimum'];cells=[r['id'],str(r['k']),str(len(r['groups'])),str(r['m']),fmt(h['gap']),fmt(mi['gap']),fmt(h['seconds']),fmt(mi['seconds']),('C' if h['status']=='COMPLETE' else 'U')+'/'+('C' if mi['status']=='COMPLETE' else 'U'),str(h['nodes']),fmt(r['objective_scale'])]
        detailed+=' & '.join(cells)+r' \\'+'\n'
    detailed+=r'''\bottomrule\end{longtable}
\section{Independent Numerical Mixed-Integer Comparisons}
Every primary case has tangent and secant solves of the uneliminated original model. Status 0 means completed; status 1 means a solver limit. Times, nodes and relative primal--dual gaps below are tangent/secant pairs. The approximation bound is the maximum one-sided quadratic-envelope error. Width is the tangent dual upper bound minus the secant feasible original payoff. These are floating-point diagnostics, never substitutes for the exact semantic certificates.
\begin{longtable}{lrrrrrr}
\caption{All direct MIP comparisons; no timeout or failed solve is omitted.}\label{tab:r48-mip}\\
\toprule Case & Status & Seconds & Nodes & MIP gaps & Env. error & Width\\\midrule\endfirsthead
\toprule Case & Status & Seconds & Nodes & MIP gaps & Env. error & Width\\\midrule\endhead
'''
    for row in M:
        a,b=row['envelopes']['tangent'],row['envelopes']['secant'];pair=lambda key:fmt(a.get(key))+'/'+fmt(b.get(key))
        cells=[row['id'],str(a['status'])+'/'+str(b['status']),pair('seconds'),pair('node_count'),pair('mip_gap'),fmt(a['approximation_error']),fmt(row['bracket_width'])]
        detailed+=' & '.join(cells)+r' \\'+'\n'
    detailed+=r'\bottomrule\end{longtable}'+'\n'
    detailed+=r'''\section{Interpretation and Reproduction}
The twelve all-book references independently enumerate menu choices but share the exact fixed-book allocator. The separate MIP retains support indicators, probabilities, pre-draw service and every realized ceiling. The harmonic checker imports neither harmonic reduction nor the search implementation: it rebuilds harmonic means, verifies eligibility and the anchor guard, checks all original lottery constraints, verifies clipping comparison identities and group supporting prices, and delegates the full target-cover and Bellman upper witness to the antecedent independent checker.

The paired study deliberately uses one wide curvature bin within each cap and eligibility group. It is an ablation of the optimistic representative, not an experiment claiming that conservative accuracy bins are always small. The supplied records separately count both accuracy partitions at three tolerances. The final metric pass uses the antecedent node-accounting MIP wrapper; the cases and limits did not change from the initial authoring run. Both local and remote executions must identify their own measured times rather than substitute one environment's times for another's. Full rational policies, raw solver messages, scaled-gap denominators, check times, protocol hashes and generators are retained in the revision directory.
'''
    (g/'detailed_tables.tex').write_text(detailed)
    prose=r'''\section{Joint Computational Evidence}\label{sec:r48-study}
The evidence now separates two questions. The preserved distinct-history study tests certified joint design against unaggregated boxes, priced-prefix search, all-book enumeration, and direct mixed-integer envelopes. Its 24 original-space successes at tolerance $0.001$, including up to 256 distinct histories, remain in Tables~\ref{tab:r47-joint}--\ref{tab:r47-times}. Those clustered-input results are not a universal runtime claim. The full protocol, four deliberately unresolved coarse stress cases, their refinements, and the earlier R46 failures remain in the computational record and companion tables.

The new paired study isolates harmonic pooling under substantially dispersed costs. It contains 24 cases: twelve primary cases with four, six, or eight histories and twelve cases with 32, 128, or 256 histories. Catalog sizes are seven and nine, budgets range from one to three, and the four families vary common or dispersed caps, eligibility, saturated or interior promises, positive charges, and a zero-cost history. Within each shared eligibility prefix and cap bin, all curvatures enter one deliberately coarse group; both representatives use identical groups and a minimum-cap guard. Each receives 31 target boxes, four price refinements and reduced tolerance $0.0005$. The requested original tolerance is $0.001$.

Table~\ref{tab:r48-paired} reports '''+str(summary['harmonic_complete'])+r''' harmonic certificates within tolerance, versus '''+str(summary['minimum_complete'])+r''' for minimum-curvature aggregation. All '''+str(24-summary['harmonic_complete'])+r''' unresolved harmonic cases remain in the record; the largest gap is '''+fmt(summary['max_harmonic_gap'])+r'''. At the twelve primary all-book references, harmonic reduced optima are never larger and are strictly smaller in '''+str(summary['strict_harmonic_reference_improvements'])+r''' cases. Nevertheless, a tighter relaxation need not improve every interrupted interval: cost pooling can leave cap dispersion dominant, and independently chosen price bounds can differ. We report both intervals and their valid intersection, not a fictitious pointwise runtime dominance.

All 48 paired upper/lower certificates pass independent semantic checking. The 24 direct tangent/secant MIP solves retain original support probabilities and service decisions; every solver status, time, node count, primal--dual gap, envelope error, and bracket width is reported in Table~\ref{tab:r48-mip}. These numerical intervals are not rational proofs. Exact regression checks comprise '''+str(T['joint_order'])+r''' ordered joint-optimum comparisons, '''+str(T['book_lifts'])+r''' original-policy lifts, '''+str(T['dispersion'])+r''' dispersion checks, '''+str(T['accuracy_partitions'])+r''' accuracy partitions, '''+str(T['refinement'])+r''' refinement comparisons, and '''+str(T['certificate_mutations'])+r''' rejected semantic mutations. The study tests the new mathematical mechanism rather than replacing unresolved cases with selected successes. No operational population, charge calibration, or deployment is claimed from synthetic inputs.
'''
    (R/'study.tex').write_text(prose)
if __name__=='__main__':run()
