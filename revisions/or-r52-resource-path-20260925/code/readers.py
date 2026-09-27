"""Generate every displayed number from the frozen, retained execution records."""
from pathlib import Path
from fractions import Fraction as F
import json, statistics, sys
R=Path(__file__).resolve().parents[1];G=R/'generated';G.mkdir(exist_ok=True)
a=json.loads((R/'results/study.json').read_text())['cases']; b=json.loads((R/'results/baselines.json').read_text())['cases']
assert len(a)==44 and len(b)==48
fine=[x for x in a if x['family']=='stress' and x['epsilon']=='1/1000']
base=[x for x in b if x['method']=='group']; strict=[x for x in a if x['family']=='strict-prefix']; sweep=[x for x in a if x['family']=='eligibility-sweep']; robust=[x for x in a if x['family']=='robustness']; mip=[x for x in b if x['method']=='mip']
def val(x):return float(F(str(x)))
def f(x,n=3):return f'{val(x):.{n}f}'
def sci(x):
    if x is None:return '--'
    x=val(x)
    if not x:return '0'
    mant,exp=f'{x:.2e}'.split('e');return '$'+mant+r'\,10^{'+str(int(exp))+'}$'
def table(caption,label,head,rows,note,cols=None):
    n=len(head);cols=cols or 'l'+'r'*(n-1)
    return '\n'.join([r'\begin{table}[p]\centering',r'\caption{'+caption+r'}\label{'+label+'}',r'\setlength{\tabcolsep}{4pt}',r'\begin{tabular}{'+cols+'}',r'\toprule',' & '.join(head)+r'\\',r'\midrule']+[' & '.join(map(str,row))+r'\\' for row in rows]+[r'\bottomrule\end{tabular}',r'\par\vspace{6pt}\begin{minipage}{\textwidth}'+note+r'\end{minipage}',r'\end{table}',''])
main=[]
main.append(table('Difficult instances: exact-resource intervals at tolerance 0.001','tab:stress52',['Seed','$E$','$E(c)$','Reference','Width','Relative','Seconds'],[[x['seed'],x['E'],x['selected_classes'],f(x['exact_reference'],6),f(x['gap'],6),f(100*F(x['relative_gap']),2)+r'\%',f(x['seconds'])] for x in fine],r'All instances have 12 histories, 9 candidates, and a command budget of 3. $E$ counts full-catalog classes and $E(c)$ counts classes on the returned book. Relative width is the interval width divided by the positive exhaustive reference. Every returned lower policy attains the exhaustive value, but its resource-path certificate has positive width.'))
rows=[]
for name,n,p in [('group',1,4),('group',7,4),('group',31,4),('group',127,4),('group',31,0),('group',31,8),('individual',31,4)]:
    z=[x for x in b if x['method']==name and x.get('node_limit')==n and x.get('price_steps')==p]
    rows.append([name.capitalize(),n,p,sum(F(x['gap'])<=F(1,1000) for x in z),f(statistics.median(val(x['gap']) for x in z),6),f(max(val(x['gap']) for x in z),6),f(statistics.median(x['seconds'] for x in z))])
main.append(table('Matched-machine subdivision and price sensitivity','tab:baseline52',['Method','Nodes','Steps','Complete','Median width','Largest width','Seconds'],rows,r'Each row contains all six seeds in Table~\ref{tab:stress52}. Complete means an interval width at most 0.001. Nodes are the allowed node count, not a common time or memory allowance. Steps is the inherited root-price refinement parameter; zero retains only zero price. Seconds is the median optimization time. With a finite adaptive cover, a changed price set may change the chosen subdivisions, so more steps need not dominate every earlier interval.'))
rows=[]
for k in [16,64,256,1024]:
    z=[x for x in strict if x['k']==k]
    rows.append([k]+[f(x['seconds']) for x in z]+[f(max(x['checker_to_optimization_ratio'] for x in z)),0])
main.append(table('Exact common eligibility with a strict interior prefix','tab:strict52',['Histories','Design 1','Design 2','Design 3','Check/solve','Width'],rows,r'Optimization times are in seconds. Designs 1--3 use, respectively, $(N,m,B/\bar b)=(13,2,0.5),(25,3,0.9),(25,5,1)$. Every ceiling differs across histories and lies strictly in the catalog gap immediately above $1/2$; a nonempty catalog suffix is ineligible. Caps, weights, costs, and charges are heterogeneous, including zero curvature. The ratio is the largest checker-to-solver ratio across the three designs. These are structural zero-width closures, not extrapolated results for arbitrary eligibility.'))
main.append(table('Controlled full-catalog eligibility sweep','tab:sweep52',['$E$','$E(c)$','Width','Width/$L$','States','Seconds'],[[x['E'],x['selected_classes'],f(x['gap'],6),f(x['normalized_gap'],6),f"{x['resource_states']:,}",f(x['seconds'])] for x in sweep],r'All six instances share 12 histories, 17 candidates, budget 3, promise fraction 0.85, caps, weights, costs, and charges. Only the ceiling grouping changes. The tolerance is 0.01. The generic resource method is used even at $E=1$ to isolate its scaling; the exact common-prefix algorithm remains available. Every interval contains its independent exhaustive reference. At two classes the returned lower value is below that reference by 83/143360; the other five returned values equal their references.'))
main.append(table('Resource certificate economics on the difficult instances','tab:cert52',['Seed','Packed','Plain','Entries','Bits','Check/solve'],[[x['seed'],f(x['compressed_bytes']/1e6),f(x['uncompressed_bytes']/1e6),f"{x['rational_entry_count']:,}",str(x['maximum_numerator_bits'])+'/'+str(x['maximum_denominator_bits']),f(x['checker_to_optimization_ratio'])] for x in fine],r'Packed and Plain are decimal megabytes of compressed and uncompressed JSON. Entries counts serialized rational or common-denominator integer values. Bits reports the maximum numerator length and maximum denominator length; Bellman numerators are measured before reducing their common denominator. Verification reconstructs all arc kernels and checks every anchor table. Storage and checking are part of the certification cost, not part of the command alphabet budget.'))
rows=[]
for x in mip:
    t=x['envelopes']['tangent'];s=x['envelopes']['secant']
    rows.append([x['seed'],f(t['value'],6),f(t['numerical_upper'],6),f(s['value'],6),sci(t['approximation_error']),f(t['seconds']+s['seconds']),sci(x['bracket_width'])])
main.append(table('Direct mixed-integer envelope diagnostics','tab:mip52',['Seed','Tangent value','Upper','Secant value','Allowance','Seconds','Width'],rows,r'Each formulation has 249 variables, including 117 binaries, and 746 constraints, with 32 service-envelope segments. All 12 solves return status zero and one branch-and-bound node. Their recorded relative solver gaps are below $10^{-12}$. The two solves share an allowance equal to the resource solver time, subject to a minimum of 0.1 seconds per solve. Allowance is the analytic envelope approximation allowance, not the runtime allowance. Width is the unrounded floating-point upper minus recovered secant value; a tiny negative width reflects numerical error and is not a rational zero-width proof. The full records retain both solver objectives, bounds, statuses, residuals, and allowances.'))
(G/'main_tables.tex').write_text(''.join(main))
# One compact record table for each experimental family in the companion.
ec=[]
rows=[]
for x in robust:
    cid=x['id'].replace('refinement-','').replace('within-gap-','gap-')
    rows.append([cid,x['E'],x['selected_classes'],f(x['exact_reference'],6),f(x['gap'],6),f(x['seconds'])])
ec.append(table('All catalog-refinement and perturbation requests','tab:robustec52',['Case','$E$','$E(c)$','Reference','Width','Seconds'],rows,r'All prescribed cases are shown. Dominated insertions have opening charge 3. Their full-catalog class count grows from one to five, while the optimal retained book and value remain unchanged. Free insertion improves the value at the first inserted command and then leaves it unchanged. The near-boundary pair splits classes but need not change the winning book; the main text gives a separate example with an actual value jump.'))
for p in [4,0,8]:
    z=[x for x in b if x['method']=='group' and x['price_steps']==p]
    if p==4:
        for n in [1,7,31,127]:
            q=[x for x in z if x['node_limit']==n]
            ec.append(table(f'Class-mean subdivision: node allowance {n}, price steps 4',f'tab:group{n}ec52',['Seed','Nodes used','Width','Relative','Seconds','Bytes'],[[x['seed'],x['nodes'],f(x['gap'],6),f(100*F(x['relative_gap']),2)+r'\%',f(x['seconds']),x['compressed_bytes']] for x in q],r'Every interval contains its exhaustive reference. The full JSON also gives oracle calls, rational sizes, normalized errors, and verification times.'))
    else:
        ec.append(table(f'Class-mean subdivision: node allowance 31, price steps {p}',f'tab:price{p}ec52',['Seed','Nodes used','Width','Relative','Seconds','Bytes'],[[x['seed'],x['nodes'],f(x['gap'],6),f(100*F(x['relative_gap']),2)+r'\%',f(x['seconds']),x['compressed_bytes']] for x in z],r'This is a root-price sensitivity experiment, not a node-local price-generation experiment.'))
# Combine certificate timings and exact enumeration references.
ec.append(table('Optimization, verification, and exhaustive-reference time','tab:timeec52',['Seed','Resource','Checking','Enumeration','States'],[[x['seed'],f(x['seconds']),f(x['checker_seconds']),f(x['exhaustive_seconds']),f"{x['resource_states']:,}"] for x in fine],r'Times are seconds. Optimization includes exact payoff preprocessing, dynamic programming, book recovery, and table construction. Checking is separately timed. JSON serialization and gzip compression are not in either timer; their byte counts are reported separately. These tiny references are enumerated over books using a separate original fixed-book allocator, not the resource-path code.'))
(G/'ec_tables.tex').write_text(''.join(ec))
# Dynamic facts used in text, so a remote run cannot leave stale timing claims.
def macro(name,value):return '\\newcommand{\\'+name+'}{'+str(value)+'}\n'
metrics={
 'FineMaxGap':f(max(F(x['gap']) for x in fine),6),
 'FineMinTime':f(min(x['seconds'] for x in fine)), 'FineMaxTime':f(max(x['seconds'] for x in fine)),
 'FineMaxRelative':f(max(100*F(x['relative_gap']) for x in fine),2)+r'\%',
 'FineMinPacked':f(min(x['compressed_bytes']/1e6 for x in fine)), 'FineMaxPacked':f(max(x['compressed_bytes']/1e6 for x in fine)),
 'FineMaxDenBits':max(x['maximum_denominator_bits'] for x in fine),
 'AllResourceExact':sum(F(x.get('attained_error','1'))==0 for x in a if x['family']!='strict-prefix'),
 'GroupNOneComplete':sum(F(x['gap'])<=F(1,1000) for x in base if x['node_limit']==127 and x['price_steps']==4),
 'MIPMaxSeconds':f(max(x['envelopes']['tangent']['seconds']+x['envelopes']['secant']['seconds'] for x in mip)),
 'MIPMaxGap':sci(max(abs(x['bracket_width'] or 0) for x in mip)),
}
(G/'metrics.tex').write_text(''.join(macro(k,v) for k,v in metrics.items()))
(G/'METRICS.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics,indent=2))
