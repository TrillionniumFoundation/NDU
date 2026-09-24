"""Generate every new displayed number from committed execution records."""
from pathlib import Path
from fractions import Fraction as F
import json,statistics,collections
R=Path(__file__).resolve().parents[1];O=R.parent/'or-r45-budgeted-compression-20260924'
def f(x,d=5):return f'{float(F(x)):.{d}f}'
def run():
    rows=json.loads((R/'results/joint.json').read_text());grid=json.loads((R/'results/grid.json').read_text());cmp=json.loads((R/'results/comparators.json').read_text());prefix=json.loads((R/'results/priced_prefix.json').read_text());test=json.loads((R/'results/tests.json').read_text())
    P={x['id']:x for x in prefix}; groups=collections.defaultdict(list)
    for x in rows:groups[(x['raw_k'],x['n'])].append(x)
    contrib=r'''\begin{table}[p]\centering
\caption{Theorem-level contribution map. Prior labels and proofs are retained.}\label{tab:r46-contributions}
\begin{tabular}{p{.28\textwidth}p{.39\textwidth}p{.23\textwidth}}\toprule
Component & Scope & Provenance \\\midrule
Canonical allocation and continuous design & Exact response; continuous and saturated Monge results & Inherited, Theorems~\ref{thm:eligible} and~\ref{thm:r37-linear} \\
Saturated charged path & Globally exact because targets are forced & R42 antecedent; Corollary~\ref{cor:r45-saturated} \\
Unrestricted price path and prefix search & Polynomial price oracle; finite joint search & R43, Theorems~\ref{thm:r43-price}--\ref{thm:r43-search} \\
Conditional compression and complete target net & Fixed targets; fixed-branch additive joint scheme & R45, Theorems~\ref{thm:r45-frontier} and~\ref{thm:r45-net} \\
Catalog-response type reduction & Exact aggregation with prefix-equivalent ceilings & Proposition~\ref{prop:r46-types}; extends homogeneous aggregation \\
Two-sided box-price path & Exact support on arbitrary target boxes, original budget and charges & New, Theorem~\ref{thm:r46-box} \\
Adaptive joint interval & Complete box cover; local tightness; positive-accuracy termination & New, Theorem~\ref{thm:r46-adaptive} \\
Independent certificate checker & Original policy, Bellman inequalities and whole target cover & New implemented verifier \\
\bottomrule\end{tabular}\end{table}
'''
    out=[contrib,r'''\begin{table}[p]\centering
\caption{Joint design at absolute tolerance $0.001$. Counts include every frozen holdout case. Both methods optimize targets and books; neither column is conditional optimization.}\label{tab:r46-joint}
\begin{tabular}{rrrrrrr}\toprule
Branches & Catalog & Cases & Box completed & Prefix completed & Box seconds & Box max gap \\\midrule
''']
    for (k,n),z in groups.items():
        out.append(f"{k} & {n} & {len(z)} & {sum(x['status']=='COMPLETE' for x in z)} & {sum(F(P[x['id']]['gap'])<=F(1,1000) for x in z)} & {statistics.median(x['runtime'] for x in z):.3f} & {max(float(F(x['gap'])) for x in z):.5f} \\\\\n")
    out.append(r'''\bottomrule\end{tabular}
\par\smallskip\raggedright Seconds are medians for box optimization, excluding independent verification. The price-prefix baseline uses the inherited R43 completion bound, not merely an unpriced catalog relaxation. The 128- and 256-branch rows use exactly repeated types; the 128-branch row contains both four- and eight-type cases. Node and time limits, and all individual outcomes, are reported in the companion and machine-readable records.
\end{table}
''')
    out.append(r'''\begin{table}[p]\centering
\caption{Completed and interrupted target grids versus adaptive joint design on identical finite catalogs. All have $N=5$ and $m=2$. A dash means that the grid does not certify the requested accuracy.}\label{tab:r46-grid}
\begin{tabular}{rrrrrrr}\toprule
Branches & Tolerance & Grid profiles & Grid seconds & Grid certified & Box nodes & Box gap \\\midrule
''')
    for z in grid:
        out.append(f"{z['k']} & {f(z['eps'],3)} & {z['net_profiles']} & {z['net_seconds']:.3f} & {('Yes' if z['net_status']=='COMPLETE' else '--')} & {z['adaptive_nodes']} & {f(z['adaptive_gap'],5)} \\\\\n")
    out.append(r'''\bottomrule\end{tabular}\par\smallskip\raggedright The grid has a declared cap of 1,000 evaluated profiles; these are profile-limited comparisons, not claims of time-matched speedup. Adaptive runs use at most 1,001 nodes and an eight-second soft limit. Exact values, objective scales, losses, and runtimes for both algorithms appear in the archived records.\end{table}
''')
    (R/'generated/main_tables.tex').write_text(''.join(out))
    ec=[r'''\begin{longtable}{lrrrrrr}
\caption{Individual joint certificates. The first column is the reproducible instance identifier.}\label{tab:r46-all}\\
\toprule Instance & Types & Nodes & Seconds & Lower & Upper & Gap/scale \\\midrule\endfirsthead
\toprule Instance & Types & Nodes & Seconds & Lower & Upper & Gap/scale \\\midrule\endhead
''']
    for z in rows:ec.append(f"{z['id']} & {z['types']} & {z['evaluated_nodes']} & {z['runtime']:.3f} & {f(z['lower'])} & {f(z['upper'])} & {float(F(z['gap'])/F(z['objective_scale'])):.5f} \\\\\n")
    ec.append('\\bottomrule\\end{longtable}\n')
    ec.append(r'''\begin{longtable}{lrrrrrr}
\caption{Independent numerical MIP comparisons for all 24 primary holdout cases. Times and node counts are tangent/secant pairs. Widths are numerical, not rational certificates.}\label{tab:r46-mip}\\
\toprule Instance & Seconds & Nodes & Max MIP gap & Envelope & Width & Prefix seconds \\\midrule\endfirsthead
\toprule Instance & Seconds & Nodes & Max MIP gap & Envelope & Width & Prefix seconds \\\midrule\endhead
''')
    for z in cmp:
        a,b=z['tangent'],z['secant'];pair=f"{a['seconds']:.2f}/{b['seconds']:.2f}";nodes=f"{a['node_count']}/{b['node_count']}"
        mg=max(a['mip_gap'] or 0,b['mip_gap'] or 0);wid=z['numerical_display_width']
        ec.append(f"{z['id']} & {pair} & {nodes} & {mg:.1e} & {a['approximation_error']:.1e} & {wid:.1e} & {P[z['id']]['seconds']:.3f} \\\\\n")
    ec.append(r'''\bottomrule\end{longtable}
Each envelope solve has a four-second limit and 64 shortfall segments. All 48 solves returned optimal status in this execution; hence no timeout is hidden. Maximum mixed-integer primal--dual gaps and the per-case shortfall-envelope errors are reported above. Signed raw widths, including negative values at floating roundoff scale, solver messages, residuals, solutions, and separate node counts are retained in \texttt{comparators.json}. Display widths truncate only negative floating residuals to zero; this is not a rational exactness assertion. The companion also retains the separate eight-case initial MIP execution, which is not pooled into the 24-case comparison.
''')
    (R/'generated/companion_tables.tex').write_text(''.join(ec))
    n=len(rows);complete=sum(x['status']=='COMPLETE' for x in rows);prefixcomplete=sum(F(x['gap'])<=F(1,1000) for x in prefix)
    jensens=[float(F(x['jensen_upper'])-F(x['lower'])) for x in rows];finals=[float(F(x['gap'])) for x in rows]
    faster=sum(x['runtime']<P[x['id']]['seconds'] for x in rows)
    study=r'''\section{Computational Evidence for Joint Design}\label{sec:r46-study}
The primary protocol fixes 24 independent-seed synthetic cases with two, four, or eight input branches; nine or seventeen catalog points; two or three installed commands; and zero or nonnegative heterogeneous charges. Eight additional cases vary the raw history count and response-type count using a 33-point catalog. Levels lie in $[0,1]$, the reward has $r=2$ and $q=1$, and shortfall curvatures are drawn from $\{1,2,4,8\}$. Participation caps, weights, and eligibility ceilings vary independently within the declared rational generator. The protocol was frozen before these runs, not externally preregistered. Every generated case is retained. Larger comparator extensions were added after the primary run and cover the entire declared comparison set, not selected successes.

The proposed method uses eight root price-bisection steps, retains price zero, and uses the same budget and charges in every incumbent and bound. Primary box runs have a 301-node and eight-second soft limit; repeated-type scaling runs have a 101-node limit. Time is checked after completing a node, so some recorded times exceed eight seconds. The only initial incumbent is a fixed-target conditional book at the capped ideal targets, followed by exact allocation for that book. It is not a global certificate. The baseline price-prefix search reimplements the inherited R43 exact completion bound, uses the same price budget, and stops at the same absolute tolerance. A weaker full-catalog prefix relaxation is reported separately, not substituted for this stronger baseline.

'''
    study+=f"Table~\\ref{{tab:r46-joint}} reports {complete} of {n} box runs attaining absolute gap $0.001$, versus {prefixcomplete} of {n} for the priced-prefix baseline. The box method has lower measured optimization time in {faster} cases, but it is not uniformly faster or more accurate. Median times are {statistics.median(x['runtime'] for x in rows):.3f} seconds for boxes and {statistics.median(x['seconds'] for x in prefix):.3f} seconds for priced prefixes. Four box runs retain unresolved gaps between {min(float(F(x['gap'])) for x in rows if x['status']!='COMPLETE'):.5f} and {max(finals):.5f}. These are valid intervals, not achieved-tolerance claims. The median Jensen-minus-incumbent interval is {statistics.median(jensens):.5f}; the median final box interval is {statistics.median(finals):.5f}. Every box interval passes the independent structural checker.\n\n"
    study+=r'''The eight smallest holdout cases also have independent all-book joint references. Their incumbent losses are zero in this sample, but the priced bounds need not be exact. This observation is not a guarantee for the initial target choice or any heuristic portfolio. Repeated-type cases with 128 and 256 histories reduce exactly to four or eight response types; their certificates are lifted and checked on the original history space. The sixteen-type cases have no such large reduction. These rows demonstrate full joint intervals after a stated exact aggregation, not merely the runtime of conditional target compression.

Table~\ref{tab:r46-grid} tests the complete-grid reference at successively smaller tolerances and with two through five branches. Only the three two-branch grid runs complete within the 1,000-profile limit. The adaptive method completes eleven of twelve corresponding requests; its four-branch, $0.001$ run remains interrupted. Exact-reference losses, normalized objective scales, and all counts are provided rather than inferring accuracy from sampled objective agreement. This comparison tests the new coverage mechanism, not a claim that generic spatial partitioning is novel.

The independent mixed-integer formulation retains installation binaries, branch support indicators, probabilities, pre-draw service, the root equality, and every realization implication. Its tangent and secant models are solved on all 24 primary cases with 64 cost segments and separate four-second limits. All 48 solves return optimal numerical status. Table~\ref{tab:r46-mip} gives each case's runtimes, search nodes, primal--dual gaps, envelope error and bracket width. Negative signed widths at floating roundoff scale are retained in the raw records and are not called exact certificates. The results show that generic MIP and inherited prefix search remain competitive on these catalogs. The methodological claim for the box oracle is exact lower-bound-aware decomposition and independently checkable adaptive joint certificates, not universal computational superiority.

Regression includes 600 exact all-book price comparisons on heterogeneous target boxes, 24 further joint interval comparisons, 2,793 independent finite-lattice checks of constructive net coverage, genuine below-anchor and above-cap clipping, the one-branch one-call case, and eleven rejected certificate mutations. The three-target descending-side example in Section~\ref{sec:r46-box} is an exact counterexample to reusing a rising-only oracle on a target box. The coverage checker is structurally independent of the search routine. These are verification tests, not statistical evidence about an operational population.

The complete historical numerical study remains in Section~\ref{sec:r45-study}. Its thirty-five-of-thirty-six portfolio result and safeguarded sample exactness are not used as the present global-algorithm headline. Its inserted-ideal-target continuous example is an oracle candidate-pool sanity check, and its large conditional table is explicitly labeled ``targets fixed.'' No customer records, estimated installation charges, field calibration, or deployment outcomes are asserted.
'''
    (R/'study.tex').write_text(study)
    # Preserve the archival datasets and every table row, but repair ambiguous headings in reader copies.
    old=(O/'generated/main_tables.tex').read_text().replace('Safe exact','Safeguarded exact in sample').replace('Conditional frontier scaling with heterogeneous realization ceilings','Conditional frontier scaling (targets fixed) with heterogeneous realization ceilings').replace('Safeguarded exact in sample',r'\shortstack{Safeguarded exact\\in sample}').replace('Charges & Used & Seconds & Gap','Charges & Selected & Seconds & Gap').replace('target-adaptive & 4','oracle pool & 4').replace('Candidate-pool size is not installed memory.','The interior oracle pool explicitly inserts ideal targets and is a sanity check. Candidate-pool size is not installed memory.')
    (R/'generated/historical_main_tables.tex').write_text(old)
    (R/'historical_study.tex').write_text((O/'study.tex').read_text().replace('\\section{Comparative Computation}', '\\section{Retained Historical Comparative Computation}'))
    print('New tables generated from',len(rows),'joint records and',len(cmp),'MIP comparisons.')
if __name__=='__main__':run()
