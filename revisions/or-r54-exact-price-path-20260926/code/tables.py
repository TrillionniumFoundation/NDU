"""Generate every displayed R54 number from the retained execution records."""
from pathlib import Path
from fractions import Fraction as F
from statistics import median
from collections import Counter
import json
R=Path(__file__).resolve().parents[1];OUT=R/'results';G=R/'generated';G.mkdir(exist_ok=True)
def read(name):return json.loads((OUT/name).read_text())
def num(x,digits=3):
    if x is None:return '--'
    x=float(F(str(x)))
    if x==0:return '0'
    if abs(x)<1e-3:return f'{x:.1e}'
    return f'{x:.{digits}f}'
def gap(r):return num(r.get('gap'),5)
def begin(title,label,columns,headers):
    return '\\begin{table}[p]\\centering\\small\\setlength{\\tabcolsep}{3pt}\n'+f'\\caption{{{title}}}\\label{{{label}}}\n\\begin{{tabular}}{{{columns}}}\\toprule\n'+headers+r'\\\midrule'+'\n'
def end(note):return r'\bottomrule\end{tabular}'+'\n'+r'\par\smallskip\begin{minipage}{0.98\textwidth}\small '+note+r'\end{minipage}\end{table}\clearpage'+'\n'
def row(items):return ' & '.join(map(str,items))+r'\\'+'\n'
def short(c):
    x=c['id']
    if x.startswith('histories-'):return 'Histories '+x.split('-')[-1]
    if x.startswith('catalog-'):return 'Catalog '+x.split('-')[-1]
    if x.startswith('budget-'):return 'Budget '+x.split('-')[-1]
    if x.startswith('accuracy-'):return 'Accuracy '+x[9:].replace('_','/')
    if x.startswith('charge-'):return 'Charges '+x[7:].replace('_','/')
    return 'Different rewards'
def run():
    cases=read('CASES.json');study=read('STUDY.json')['records'];rr={(x['id'],x['method']):x for x in study}
    prices=[rr[c['id'],'price'] for c in cases];counts=Counter(x['status'] for x in prices)
    screen=read('SCREENING.json');anytime=read('ANYTIME.json');hard=read('HARDNESS_REGRESSION.json');challenge=read('CHALLENGE.json');tests=read('REGRESSION.json')
    metrics=dict(PriceExact=counts['EXACT'],PriceTolerance=counts['TOLERANCE'],PriceLimited=sum(counts[x] for x in ['TIME_LIMIT','NODE_LIMIT','MEMORY_LIMIT','PROCESS_LIMIT']),PriceChecked=sum(x.get('verification_status')=='PASS' for x in prices),
                 PriceMinBytes=min(x['certificate_bytes'] for x in prices),PriceMaxBytes=max(x['certificate_bytes'] for x in prices),
                 AnytimeExact=sum(x['status']=='EXACT' for x in anytime['records']),ForcedAnchors=screen['forced_anchor_removals'],
                 HardnessSubsets=hard['optional_subsets'],HardnessBooks=hard['full_catalog_books'])
    (G/'metrics.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+str(v)+'}' for k,v in metrics.items())+'\n')
    main=begin('Arbitrary-eligibility scaling under the common four-second algorithm budget.','tab:scale54','lrrrrrrrrr',r'Case & $k$ & $N$ & $m$ & $E$ & Seconds & Width & Bytes & Check (ms) & Memory')
    for c in cases:
        if c['family']=='historical':continue
        x=rr[c['id'],'price'];time=num(x.get('algorithm_seconds'))+('$^{*}$' if x['status'] not in ['EXACT','TOLERANCE'] else '')
        main+=row([short(c),c['k'],c['n'],c['m'],c['E'],time,gap(x),x.get('certificate_bytes','--'),num(1000*x['verification_seconds'],2) if 'verification_seconds' in x else '--',num(x.get('algorithm_peak_rss_kib',0)/1024,1)])
    main+=end(r'Widths and bytes refer to independently checked rational certificates. Zero width denotes exact closure. An asterisk marks a time or node limit; it does not invalidate the interval. Memory is peak resident process memory in MiB under a common 2-GiB address-space cap. Check is additional verification time. Except in the named accuracy sweep, requested width is $10^{-3}$. Charges and accuracy vary on the same base model; these repeated anchors of the one-factor sweeps are not independent samples. Heterogeneous rows correspond to $(k,N)=(12,9),(12,17),(24,9),(24,17)$.')
    main+=begin('Paired reruns of the six historical fine-accuracy cases.','tab:fine54','rrrrrrr',r'Seed & Price seconds & Price width & Enumeration & Uniform grid & Class boxes & Mixed integer')
    for c in cases:
        if c['family']!='historical':continue
        p=rr[c['id'],'price'];cells=[c['id'].split('-')[-1],num(p.get('algorithm_seconds')),gap(p)]
        for method in ['enumeration','uniform','classbox','mip']:
            x=rr[c['id'],method];txt=num(x.get('algorithm_seconds'))
            if x['status'] in ['TIME_LIMIT','PROCESS_LIMIT','MEMORY_LIMIT','NODE_LIMIT']:txt+=' limit'
            cells.append(txt)
        main+=row(cells)
    main+=end(r'Times are measured seconds under the same four-second algorithm allowance and 2-GiB address-space cap. The mixed-integer column includes construction and both envelopes, each with a two-second solver limit; it is not an envelope-error allowance. Numerical mixed-integer bounds are not rational certificates. Complete primal/dual values, solver nodes, model sizes, residuals, envelope errors, and actual per-envelope solver times appear in the companion and raw records. Interrupted old solvers retain only their separately valid fallback interval, not an uncertified intermediate result.')
    main+=begin('All matched-limit outcomes, including unsuccessful runs.','tab:outcomes54','lrrrrr',r'Method & Runs & Exact & Tolerance & Numerical & Resource limit')
    for method,label in [('price','Price paths'),('uniform','Uniform grid'),('enumeration','Book enumeration'),('classbox','Class boxes'),('mip','Mixed integer')]:
        rows=[x for x in study if x['method']==method];cc=Counter(x['status'] for x in rows)
        main+=row([label,len(rows),cc['EXACT'],cc['TOLERANCE']+cc['COMPLETE'],cc['NUMERICAL'],sum(cc[s] for s in ['TIME_LIMIT','PROCESS_LIMIT','MEMORY_LIMIT','NODE_LIMIT'])])
    main+=r'\bottomrule\end{tabular}\par\medskip'+ '\n'
    main+=r'\begin{tabular}{rrrrrrr}\toprule Histories & Commands & Price & Uniform & Enumeration & Class boxes & Mixed integer\\\midrule'+'\n'
    for c in challenge['cases']:
        cells=[c['histories'],c['catalog_size']]
        for method in ['price','uniform','enumeration','classbox','mip']:
            x=next(z for z in challenge['runs'] if z['id']==c['id'] and z['method']==method)
            cells.append({'EXACT':'Exact','NUMERICAL':'Numerical','TIME_LIMIT':'Time limit','NODE_LIMIT':'Node limit','PROCESS_LIMIT':'Process limit','TOLERANCE':'Tolerance','COMPLETE':'Tolerance'}.get(x['status'],x['status']))
        main+=row(cells)
    main+=end(r'Top panel: the original 30-case study, 142 method runs. The inherited grid and class-box implementations do not accept heterogeneous rewards, so each has 26 applicable cases. Bottom panel: all four separately preregistered SUBSET SUM reduction challenges, not an operational sample. Price and enumeration request exact closure; grid and class-box width is $1/(8K)$. Constructed-case integer subset-sum dynamic programming provides exact reference values independently of these methods. Resource limits remain outcomes, not discarded cases. A numerical outcome only means that both numerical envelope calls returned; individual solver statuses and widths remain reported.')
    main+=begin('Time-to-gap records for the separately requested zero-width runs.','tab:anytime54','lrrrrrr',r'Case & Width at 0.1 s & Width at 0.5 s & Width at 1 s & Width at 4 s & Final width & Seconds')
    for x in anytime['records']:
        vals=[]
        for t in [.1,.5,1.,4.]:
            trace=[p for p in x.get('trace',[]) if p['seconds']<=t]
            vals.append(num(F(trace[-1]['upper'])-F(trace[-1]['lower']),5) if trace else '--')
        main+=row([x['id'].replace('anytime-',''),*vals,gap(x),num(x.get('algorithm_seconds'))])
    main+=end(r'Each entry uses the latest completed price or node calculation at or before the indicated time. A dash means that no completed price calculation had yet been recorded; the initialized universal bound still exists. Final bounds are independently checked. Once a run terminates its final trace continues to describe the incumbent interval. These zero-width reruns are separate from the fixed-tolerance study and use the same resource caps. Full per-oracle traces, not just these checkpoints, are retained.')
    main+=begin('Screening rates and costs on all 24 near-threshold, mixed-catalog cases.','tab:screen54','lrrrrrr',r'Rule & Minimum & Lower quartile & Median & Upper quartile & Maximum & Anchors')
    for key,label,anchor in [('envelope_rate','Target-box envelope',0),('forced_rate','Forced price paths',screen['forced_anchor_removals'])]:
        z=screen[key];main+=row([label,*[num(z[t],3) for t in ['minimum','q25','median','q75','maximum']],anchor])
    main+=r'\bottomrule\end{tabular}\par\medskip'+'\n'
    main+=r'\begin{tabular}{lrrrr}\toprule Calculation & Median seconds & Minimum seconds & Maximum seconds & Description\\\midrule'+'\n'
    for key,label,desc in [('envelope_seconds','Envelope','Bound evaluation'),('incumbent_seconds','Incumbent','Price search'),('forced_test_and_check_seconds','Forced paths','Bounds and checks'),('enumeration_seconds','Exact reference','All feasible books')]:
        vs=[x[key] for x in screen['rows']];main+=row([label,num(median(vs),4),num(min(vs),4),num(max(vs),4),desc])
    main+=end(r'Rates are fractions of eight catalog commands removed. Anchor counts aggregate all cases, not distinct physical commands. Forced tests include all possible anchors and use feasible-incumbent price information, not an exact-reference value supplied for free. The exact reference is only used for evaluation. A stronger forced test costs more and can miss truly irrelevant commands; it is not advertised as universally preferable preprocessing. The companion reports wholly ineligible removals, charge slacks, missed exclusions, all target-command triples, and sharpness neighbors in which the same command is useful, tied, or excluded.')
    (G/'main_tables.tex').write_text(main)
    ec=begin('Complete numerical mixed-integer diagnostics on the historical cases.','tab:mip54','rlrrrrrrr',r'Seed & Envelope & Variables & Binary & Nodes & Solver s & Limit s & Error & Width')
    for c in cases:
        if c['family']!='historical':continue
        x=rr[c['id'],'mip']
        for kind,e in x.get('envelopes',{}).items():
            ec+=row([c['id'].split('-')[-1],kind,e.get('variables','--'),e.get('binaries','--'),e.get('node_count','--'),num(e.get('seconds'),4),2,num(e.get('approximation_error'),6),num(x.get('gap'),6)])
    ec+=end(r'Solver seconds are actual per-envelope calls; each solver limit is two seconds, within the total four-second algorithm alarm. Error is the analytical service-envelope approximation allowance, not a time allowance. Width is the signed floating-point difference of the two returned numerical values; tiny negative values are roundoff and are not recast as exact certificates. All raw primal/dual values, status codes, relative solver gaps and residuals are retained in the machine-readable records.')
    ec+=begin('Target-command threshold slacks and exact relevance in every screening case.','tab:threshold54','rrrrrrrr',r'Family & Ratio & $z$ & $G(z)$ & Charge & Slack & Envelope & Forced')
    for x in screen['rows']:
        z=next(e for e in x['entries'] if e['command']==x['target']);ec+=row([x['family'],x['multiplier'],num(z['command'],2),num(z['gain_bound'],4),num(z['charge'],4),num(z['slack'],4),int(z['envelope_screen']),int(z['forced_screen'])])
    ec+=end(r'Each family uses the same nonuniform caps, promise and mixed catalog at charge ratios $0.9,1,1.1$. The full command records additionally give $G$, charge, slack, forced upper bound and exact inclusion/exclusion value for every candidate, not just this target. A below-envelope charge does not by itself prove usefulness. The separate sharpness examples below demonstrate that usefulness can change across the equality threshold.')
    sharp=read('SHARP_SCREENING.json')['rows'];prod=read('PRODUCTION.json')
    ec+=begin('Exact sharpness neighbors and a distinct divisible-production example.','tab:production54','rrrrrr',r'Charge ratio & Envelope & Charge & Singleton & Pair & Pair needed')
    for x in sharp:ec+=row([x['multiplier'],num(x['G'],6),num(x['charge'],6),num(x['singleton'],6),num(x['pair'],6),int(x['target_necessary'])])
    ec+=r'\bottomrule\end{tabular}\par\medskip'+'\n'+r'\begin{tabular}{rrrrl}\toprule Module budget & Order & Exact value & Supporting price & Selected vertices\\\midrule'+'\n'
    for x in prod['cases']:
        z=x['optimum'];ec+=row([x['budget'],x['order'],z['value'],z['price'],','.join(map(str,z['vertices']))])
    ec+=end(r'The sharpness configuration has $B=\bar b$, nonuniform caps and a feasible two-command budget; equality allows both books. Production uses vertices of capacities $0,2,5,9$ and six independently specified compatible modules, with parallel divisible order assignment. Exact allocations and every alternative configuration are recorded. This is a numerical mathematical example, not an industrial calibration or a renamed history/lottery instance.')
    (G/'ec_tables.tex').write_text(ec)
    detail=[]
    for x in screen['rows']:
        for key in ['envelope_screen','forced_screen']:
            selected=[z for z in x['entries'] if z[key]]
            irrelevant=[z for z in x['entries'] if z['exact_inclusion_value'] is None or F(z['exact_inclusion_value'])<F(x['exact_value'])]
            detail.append(dict(case=x['id'],rule=key,total_removed=len(selected),ineligible_removed=sum(z['wholly_ineligible'] for z in selected),strictly_irrelevant=len(irrelevant),missed_strictly_irrelevant=sum(not z[key] for z in irrelevant)))
    (OUT/'DISPLAY_METRICS.json').write_text(json.dumps(dict(macros=metrics,screening_diagnostics=detail),indent=2)+'\n')
if __name__=='__main__':run()
