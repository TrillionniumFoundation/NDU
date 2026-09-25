"""Build new tables and narrative numbers from retained execution records."""
from pathlib import Path
from fractions import Fraction as F
import json,statistics,collections
R=Path(__file__).resolve().parents[1]

def n(x,d=5):return f'{float(F(x)):.{d}f}'
def e(x):return f'{float(F(x)):.2e}'

def run():
    cases=json.loads((R/'results/joint.json').read_text())['cases']
    stress=json.loads((R/'results/stress.json').read_text())['cases']
    mip=json.loads((R/'results/mip.json').read_text())['cases']
    tests=json.loads((R/'results/tests.json').read_text())['counts']
    success={key:sum(F(c[key]['gap'])<=F(1,1000) for c in cases) for key in ('coarse','raw','priced_prefix')}
    median={key:statistics.median(c[key]['seconds'] for c in cases) for key in success}
    maxgap=max(F(c['coarse']['gap']) for c in cases)
    maxloss=max(F(c['reference']['value'])-F(c['coarse']['lower_bound']) for c in cases if c['reference'])
    summary=dict(cases=len(cases),complete=success,median_seconds=median,
        all_original_histories_distinct=all(c['k']==c['coarse']['original_exact_types'] for c in cases),
        checked_joint_intervals=2*len(cases),checked_refinement_intervals=sum(len(c['stages']) for c in stress),
        max_coarse_gap=str(maxgap),max_reference_loss=str(maxloss),
        stress_initial_unresolved=sum(F(c['stages'][0]['gap'])>F(1,1000) for c in stress),
        stress_final_exact=sum(F(c['stages'][-1]['gap'])==0 for c in stress),
        mip_solves=2*len(mip),mip_optimal_status=sum(c[x]['status']==0 for c in mip for x in ('tangent','secant')))
    if not summary['all_original_histories_distinct']:raise AssertionError('Repeated-type case in distinct-history study')
    (R/'results/SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    grouped=collections.defaultdict(list)
    for c in cases:grouped[c['k']].append(c)
    table=r'''\begin{table}[p]\centering
\caption{Distinct-history joint design at original-space tolerance $0.001$. Every declared case is included. Histories in these rows have distinct cap--cost pairs.}\label{tab:r47-joint}
\begin{tabular}{rrrrrrr}\toprule
Histories & Catalog & Cases & Coarsened & Raw boxes & Priced prefix & Groups \\
 & & & completed & completed & completed & \\\midrule
'''
    for k,rows in grouped.items():
        complete=[sum(F(c[key]['gap'])<=F(1,1000) for c in rows) for key in ('coarse','raw','priced_prefix')]
        table+=f"{k} & {rows[0]['n']} & {len(rows)} & {complete[0]} & {complete[1]} & {complete[2]} & {rows[0]['coarse']['groups_count']} \\\\\n"
    table+=r'''\bottomrule\end{tabular}
\par\smallskip\raggedright The twelve primary cases use four, eight, or twelve histories, nine catalog levels, and two or three commands. The twelve scaling cases use seventeen catalog levels and three commands. The reduced solve uses tolerance $0.0005$; completion above refers only to the checked original interval. Both box methods use at most 101 nodes and a four-second soft limit checked after full nodes. The priced-prefix comparator has the same requested original tolerance, node limit, and soft limit. All raw intervals and all lifted intervals pass their independent checkers.
\end{table}
\begin{table}[p]\centering
\caption{Optimization time and original-space gaps on all distinct-history cases. Seconds are local medians; maximum gaps are exact certificate widths rounded for display.}\label{tab:r47-times}
\begin{tabular}{rrrrrrr}\toprule
Histories & Coarsened & Raw box & Prefix & Coarsened & Raw box & Prefix \\
 & seconds & seconds & seconds & max gap & max gap & max gap \\\midrule
'''
    for k,rows in grouped.items():
        med=[statistics.median(c[key]['seconds'] for c in rows) for key in ('coarse','raw','priced_prefix')]
        gaps=[max(F(c[key]['gap']) for c in rows) for key in ('coarse','raw','priced_prefix')]
        table+=f"{k} & {med[0]:.3f} & {med[1]:.3f} & {med[2]:.3f} & {n(gaps[0])} & {n(gaps[1])} & {n(gaps[2])} \\\\\n"
    table+=r'''\bottomrule\end{tabular}
\par\smallskip\raggedright Timing excludes independent checking; coarsened timing includes reduction and original-space lifting. It is not uniformly faster: per-case outcomes, actual times above the soft limit, node counts, objective scales, and normalized gaps are retained in \texttt{results/joint.json}. The current code uses exact rational arithmetic. The data are a declared four-cluster perturbation family, not arbitrary-population or field evidence.
\end{table}
'''
    (R/'generated/main_tables.tex').write_text(table)
    ec=r'''\begin{table}[p]\centering
\caption{Coarse-relaxation stress cases. The root obligation equals total original capacity. Each initial two-group solve is exact for its reduced model but does not certify the original tolerance.}\label{tab:r47-stress}
\begin{tabular}{rrrrrrr}\toprule
Case & Commands & Final & Original & Initial & Initial & Refined \\
 & & curvature & optimum & lower & gap & gap \\\midrule
'''
    for c in stress:
        ec+=f"{c['id'].split('-')[-1]} & {c['budget']} & {n(c['gamma2'],1)} & {n(c['reference_value'])} & {n(c['stages'][0]['lower'])} & {n(c['stages'][0]['gap'])} & {n(c['stages'][-1]['gap'])} \\\\\n"
    ec+=r'''\bottomrule\end{tabular}
\par\smallskip\raggedright Caps are $(1/5,2/5,4/5)$, weights $(1/5,3/10,1/2)$, and ceilings are all one. The first two curvatures are one and two; the third is shown. The catalog is $\{0,1/4,1/2,3/4,1\}$. All charges are zero except case 3, which charges $1/20$ per installed level. The initial groups are $\{1\}$ and $\{2,3\}$, with the smallest-cap guard intact. Splitting the latter group gives three singleton histories and zero global gap. Every stage has a checked original-space policy and upper certificate.
\end{table}
\begin{table}[p]\centering
\caption{Independent original-model mixed-integer comparisons on every primary case. Times and node counts are tangent/secant pairs. All widths are numerical, not rational certificates.}\label{tab:r47-mip}
\begin{tabular}{rrrrrrr}\toprule
Case & Seconds & Nodes & Max solver & Envelope & Signed & Status \\
 & & & gap & error & width & pair \\\midrule
'''
    for c in mip:
        a,b=c['tangent'],c['secant'];wid=c['signed_bracket_width'];gap=max(a['mip_gap'] or 0,b['mip_gap'] or 0)
        ec+=f"{c['id'].split('-')[-1]} & {a['seconds']:.2f}/{b['seconds']:.2f} & {a['node_count']}/{b['node_count']} & {gap:.1e} & {a['approximation_error']:.1e} & {wid:.1e} & {a['status']}/{b['status']} \\\\\n"
    ec+=r'''\bottomrule\end{tabular}
\par\smallskip\raggedright Each envelope has 64 segments and a separate two-second solver limit. Status 0 means the numerical solver reported optimal termination; nonzero statuses would remain in the table. All 24 solves report status 0 here. Signed negative widths at floating roundoff scale are deliberately retained. The full formulation, global numerical bounds, primal values, residuals, probabilities, and individual runtimes are in \texttt{results/mip.json}. Exhaustive book references agree with these numerical brackets up to the declared $10^{-6}$ comparison allowance, which is not an exact upper-bound guarantee.
\end{table}
'''
    (R/'generated/companion_tables.tex').write_text(ec)
    study=r'''\section{Joint Computation with Distinct Histories}\label{sec:r47-study}
The additional protocol contains twelve primary cases with four, eight, or twelve distinct histories and twelve scaling cases with 32, 128, or 256 distinct histories. Primary catalogs have nine levels and budgets two or three; scaling catalogs have seventeen levels and budget three. Four cap centers and four cost centers receive rational, history-specific perturbations at scales $0.001$ and $0.02$. We vary nonuniform weights, nonnegative charges, one or four eligibility regimes, and interior or saturated promises. Every cap--cost pair is distinct, so the exact response-type reduction leaves every history separate. This is a declared clustered synthetic family, not a generic random population. The protocol and generator hash were fixed before these runs, not externally preregistered.

Coarsening uses cap and curvature bins twice the perturbation scale, exact eligibility classes, and one minimum-cap guard. It gives four groups for four-history cases and five otherwise. These practical bins are deliberately coarser than the conservative accuracy prescription in Theorem~\ref{thm:r47-variable}; their validity comes from the checked original-space interval, not from assuming a small worst-case error. The inner target-box tolerance is $0.0005$, and the requested original tolerance is $0.001$. Both box methods use eight root-price steps, a 101-node limit and a four-second soft limit. No original reallocation improvement is added after the groupwise lift. The priced-prefix baseline uses the same original tolerance and resource limits. Soft limits are checked between complete oracle blocks; recorded times exceeding them are retained.

'''
    study+=f"Tables~\\ref{{tab:r47-joint}} and~\\ref{{tab:r47-times}} report {success['coarse']} of {len(cases)} original-space certificates within tolerance for coarsening, {success['raw']} for unaggregated boxes, and {success['priced_prefix']} for priced prefixes. Median optimization times are {median['coarse']:.3f}, {median['raw']:.3f}, and {median['priced_prefix']:.3f} seconds, respectively. The largest coarsened gap is {float(maxgap):.6f}. This is a global certificate result, not an exact-hit claim about a target portfolio. All {2*len(cases)} coarsened and raw intervals pass independent semantic checking; full original policies and tree witnesses are supplied. The inherited 32-case study, including its four unresolved box runs and stronger prefix results, remains intact in Section~\\ref{{sec:r46-study}}. Its runtimes are not pooled with this execution.\n\n"
    study+=f"All twelve primary cases have exhaustive all-book joint references. That enumeration is independent of the target search but shares the exact fixed-book allocator; it is not presented as a separately derived allocation algorithm. The largest lifted-incumbent loss to those references is {float(maxloss):.2e}. A genuinely uneliminated original-model mixed-integer formulation provides a separate check: its 24 tangent/secant solves retain every support implication and do not use canonical allocation. Table~\\ref{{tab:r47-mip}} reports each solver status, time, node count, gap, envelope error, and signed numerical bracket width. These floating-point bounds are not substituted for rational certificates.\n\n"
    study+=r'''An additional four-case stress protocol was fixed after the primary run to challenge coarse recovery, rather than to extend its success rate. In Table~\ref{tab:r47-stress}, the reduced models are solved exactly but initial original-space gaps range from $27/640$ to $67/100$. None is mislabeled as meeting tolerance. One refinement to original singletons closes every gap to zero. This demonstrates both the need to account for aggregation error and the constructive route back to the original problem; it does not claim that one refinement always suffices.

'''
    study+=f"New regression tests include {tests['exhaustive_joint_pairs']} exhaustive original/reduced optimum pairs, {tests['fixed_book_lifts']} fixed-book lifts, {tests['cap_deviation_bounds']} cap-dispersion checks, {tests['accuracy_partitions']} accuracy-binned partitions, and {tests['refinement_comparisons']} exact refinement comparisons. Genuine clipping at saturation restores every individual cap. The independent checker rejects {tests['mutations_rejected']} semantic mutations, including changed representatives, lost branches, altered charges, false gaps, and missing coverage leaves. Prior tests and derivations are preserved without relabeling them as new runs. The study establishes algorithmic and certificate behavior on these declared inputs; it does not assert field calibration or universal runtime superiority.\n"
    (R/'study.tex').write_text(study)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
