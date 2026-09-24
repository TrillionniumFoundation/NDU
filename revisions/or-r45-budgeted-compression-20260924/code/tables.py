"""Generate every R45 numerical table from executed JSON."""
from pathlib import Path
from fractions import Fraction as F
import json,statistics
R=Path(__file__).resolve().parents[1]
def load(n):return json.loads((R/'results'/f'{n}.json').read_text())
def x(v):return float(F(v))
def fmt(v):
    v=float(v)
    return f'{v:.6f}' if abs(v)>=1e-5 or v==0 else f'{v:.2e}'
def table(caption,label,columns,head,rows,note):
    return '\\begin{table}[p]\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+columns+'}\\toprule\n'+head+' \\\\\n\\midrule\n'+'\n'.join(' & '.join(map(str,r))+' \\\\' for r in rows)+'\n\\bottomrule\\end{tabular}\n\\par\\smallskip\\begin{minipage}{.98\\textwidth}\\footnotesize '+note+'\\end{minipage}\n\\end{table}\n'
def run():
    c=load('comparison');sc=load('scaling');cont=load('continuous');net=load('target_net')
    main=table('Original-budget comparison across six seeds','tab:r45-comparison','lrrrrrr',
        'Charges & Cases & Core exact & Safe exact & Core wins & Greedy wins & Max core loss',
        [[('None' if not g['charged'] else 'Nonuniform'),g['n'],g['zero_exact_gap'],g['safeguarded_zero_exact_gap'],g['new_wins'],g['greedy_wins'],fmt(g['max_exact_gap'])] for g in c['groups']],
        'Exact means equality with the exhaustive joint catalog reference. Core and greedy wins compare their same-budget values; ties are omitted. The safeguarded policy keeps the better feasible candidate. The charged exception remains in the data. These counts are observations, not global guarantees for a finite target portfolio.')
    rows=[]
    for k in [2,3]:
        rs=[r for r in net['rows'] if len(r['model']['caps'])==k]
        for eps in sorted({r['epsilon'] for r in rs},key=x,reverse=True):
            rr=[r for r in rs if r['epsilon']==eps]
            rows.append([k,eps,len(rr),sum(r['result']['evaluated_profiles'] for r in rr),fmt(max(x(r['actual_gap']) for r in rr))])
    main+=table('Completed same-budget target-net comparisons','tab:r45-net','rrrrr',
        'Branches & Tolerance & Cases & Profiles & Maximum actual loss',rows,
        'All completed nets meet the requested additive tolerance with the original two-symbol budget and nonuniform charges. Counts aggregate four seeds. An additional interrupted run withholds its global accuracy guarantee.')
    rows=[[r['seed'],r['k'],r['N'],r['m'],'Yes' if r['charged'] else 'No',len(r['frontier'][-1]['book']),f"{r['median_seconds']:.3f}",fmt(x(r['gaps'][-1]))] for r in sc['rows']]
    main+=table('Conditional frontier scaling with heterogeneous realization ceilings','tab:r45-scaling','rrrrlrrr',
        'Seed & Branches & Catalog & Budget & Charges & Used & Seconds & Gap',rows,
        'Seconds are medians of three repeated executions on the same input. Gap is the valid same-budget Jensen upper bound minus the ideal-target conditional policy value, not an observed error to an unknown global optimum. Full timing arrays, stored-entry bit lengths and cumulative process resident-memory records are archived.')
    selected=[r for r in cont['rows'] if (r['case']=='interior-ideal' and r['N'] in [4,9,65]) or
        (r['case']=='off-cap-top' and r['N'] in [5,6,9]) or
        (r['case'].startswith('saturated-') and r['N']==9)]
    rows=[[r['case'].replace('saturated-','Sat. '),r['grid'].replace('adaptive-midpoint','Adaptive'),r['N'],r['m'],fmt(x(r['gap']))] for r in selected]
    main+=table('Adaptive candidates at an unchanged installed-symbol budget','tab:r45-continuous','llrrr',
        'Case & Candidate pool & Candidates & Symbols & Exact-reference loss',rows,
        'Every row has an exact continuous reference in the stated Jensen-attaining or saturated expected-participation regime. Candidate-pool size is not installed memory. Adaptive midpoint selection is a heuristic; catalog optimization at the saturated target is exact. The complete 22-row path is in the companion and JSON.')
    (R/'generated/main_tables.tex').write_text(main)
    rows=[[r['case'].replace('saturated-','Sat. '),r['grid'].replace('adaptive-midpoint','Adaptive'),r['N'],fmt(x(r['gap']))] for r in cont['rows']]
    ec=table('Complete continuous-reference comparison path','tab:r45-cont-full','llrr',
        'Case & Candidate pool & Candidates & Exact-reference loss',rows,'All inputs, reference codebooks and returned rational policies are retained. The same installed budget is used along each path.')
    rows=[]
    for charged in [False,True]:
        rr=[r for r in c['rows'] if r['charged']==charged]
        rows.append(['None' if not charged else 'Nonuniform',len(rr),sum(r['nested'] for r in rr),max(r['actual_extra_levels'] for r in rr),
            fmt(statistics.median(r['overlap'] for r in rr)),fmt(max(x(r['union_gap_at_actual_budget']) for r in rr)),
            fmt(max(x(r['new_gap_at_union_budget']) for r in rr))])
    ec+=table('Union overlap and quality at the actual installed size','tab:r45-union','lrrrrrr',
        'Charges & Cases & Nested & Max extra & Median overlap & Union loss & Core loss',rows,
        'Loss columns give the maximum difference from the exact joint optimum at the union\textquotesingle s actual size, not the original-budget price bound. Max extra uses the nonnegative expansion beyond the original budget. Per-instance percentage expansion and gain per additional symbol are generated in the expanded JSON accounting.')
    (R/'generated/companion_tables.tex').write_text(ec)
    # Derived per-instance metrics remain machine readable even when not all fit a table.
    out=[]
    for r in c['rows']:
        extra=r['actual_extra_levels']; gain=x(r['r44']['augmented_policy']['value'])-x(r['r44']['original_lower'])
        out.append(dict(seed=r['seed'],family=r['family'],charged=r['charged'],budget=r['m'],actual_union_size=r['union_size'],
            expansion_percent=100*extra/r['m'],overlap=r['overlap'],nested=r['nested'],gain_over_original_incumbent=gain,
            gain_per_added_symbol=gain/extra if extra else None))
    (R/'results/memory_accounting.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':run()
