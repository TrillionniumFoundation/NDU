#!/usr/bin/env python3
"""Generate all manuscript numerical tables from saved worker receipts."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,sys
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
R=Path(__file__).resolve().parent

def sci(x):
    if abs(x)<1e-15:return '0'
    return f'{x:.2e}'
def fmt(x):return f'{x:.4f}'
def table(caption,label,cols,head,rows,note):
    return '\\begin{table}[htbp]\n\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+head+' \\\\\n\\midrule\n'+'\n'.join(' & '.join(map(str,row))+' \\\\' for row in rows)+'\n\\bottomrule\n\\end{tabular}\n\\par\\smallskip\\begin{minipage}{\\textwidth}\\footnotesize '+note+'\\end{minipage}\n\\end{table}\n'

def run():
    compare=json.loads((R/'results/comparisons.json').read_text())['records']
    scale=json.loads((R/'results/scaling.json').read_text())['records']
    assert len(compare)==54 and len(scale)==12
    d={}
    for z in compare:
        s=z['specification'];d[s['T'],s['seed'],s['method'],s.get('resolution',0)]=z
    rows=[];errors=[];residuals=[];ratios=[]
    for T in [4,6,8,10]:
        for seed in [13,29]:
            q=d[T,seed,'quotient',0];tree=d[T,seed,'laminar',0];qp=d[T,seed,'qp',0]
            assert F(q['value'])==F(tree['result']['value']);assert qp['result']['success']
            graph=sum(q[k]['median'] for k in ['construction_seconds','root_inversion_seconds','certificate_seconds'])
            error=abs(float(F(q['value']))-qp['result']['value']);errors.append(error);residuals.append(qp['result']['primal_residual'])
            ratios.append(tree['total_seconds']['median']/graph)
            rows.append([T,seed,q['public_nodes'],2**T-1,fmt(graph),fmt(tree['total_seconds']['median']),fmt(qp['total_seconds']['median']),sci(error)])
    out=table('Comparison on unfoldable instances','tab:comparison','rrrrrrrr',
        'Dates & Seed & Vertices & Occurrences & Quotient & Tree & Convex & Value error',rows,
        'Times are seconds. Quotient time is the sum of the separately measured phase medians for construction, root inversion, and certificate generation; the exact audit is excluded. Tree and convex times are end-to-end medians of three repetitions. Tree and quotient values agree as rational numbers. Value error is the absolute difference between the numerical convex-solver value and the exact optimum; its feasibility and stationarity residuals are retained separately. All methods use the same input, not an optimum supplied by another method.')
    gridrows=[];gaps=[]
    for T in [4,8,12]:
        for seed in [13,29]:
            value=F(d[T,seed,'quotient',0]['value']);row=[T,seed]
            for Q in [10,20,40,80]:
                g=d[T,seed,'grid',Q];gap=value-F(g['result']['value']);assert gap>=0
                row.append(sci(float(gap)))
                if Q==80:gaps.append(float(gap))
            z=d[T,seed,'grid',80];row += [fmt(z['total_seconds']['median']),z['result']['stored_primal_states']]
            gridrows.append(row)
    out+='\\clearpage\n'+table('Primal promise discretization on the public graph','tab:grid','rrrrrrrr',
        'Dates & Seed & $Q=10$ & $Q=20$ & $Q=40$ & $Q=80$ & Seconds & States',gridrows,
        'The four resolution columns report the exact feasible-policy value loss relative to the quotient optimum. Child promises are multiples of $1/Q$; local actions are continuous residuals and the root promise is not rounded. Seconds and stored states refer to $Q=80$. Times are medians of three repetitions. The grid is a public-graph dynamic program, not a scenario-tree baseline; exact rational replay checks its feasibility. A zero gap on a particular instance is not a uniform exactness claim for the grid.')
    labels={'markov':'Coupled','bounded':'Tight caps','late-renewal':'Late renewal','slack':'Dense knots'}
    rows=[]
    for z in scale:
        s=z['statistics'];family=z['specification']['family']
        rows.append([labels[family],s['public_nodes'],s['public_edges'],s['global_breakpoints'],s['stored_segments'],s['max_node_segments'],s['coefficient_max_bits']])
    out+='\\clearpage\n'+table('Response representation and rational coefficient growth','tab:representation','lrrrrrr',
        'Family & Vertices & Edges & Knots & Segments & Largest & Bits',rows,
        'Knots counts the distinct global union; segments counts the entire stored family. Bits is the largest numerator or denominator bit length among reduced affine coefficients. Late-renewal caps are heterogeneous and active only at the penultimate date; this family is deliberately distinct from the dense-knot stress family and from the broadly capped coupled family. It tests long rational horizons with a small knot universe, not worst-case quadratic storage.')
    rows=[]
    for z in scale:
        s=z['statistics'];family=z['specification']['family']
        rows.append([labels[family],s['public_nodes'],fmt(z['construction_seconds']['median']),
             f"{1e6*z['root_inversion_seconds']['median']:.1f}",fmt(z['certificate_seconds']['median']),
             fmt(z['audit_seconds']['median']),z['machine_symbols'],f"{z['peak_rss_kib']/1024:.1f}"])
    out+='\\clearpage\n'+table('Separate construction, execution, and audit costs','tab:phases','lrrrrrrr',
       'Family & Vertices & Build & Invert & Certificate & Audit & Symbols & Memory',rows,
       'Build, certificate, and audit are seconds; inversion is microseconds. Build and inversion use three repetitions. Certificate generation and the independent single-query policy audit are each measured once in this scale suite; they are diagnostic measurements, not repeated-time claims. Symbols is the exact minimized writable alphabet. Memory is the absolute fresh-worker process high-water mark in MiB, including common Python, NumPy, and SciPy imports; it is not incremental algorithm allocation. Whole-curve audits are reported separately from these single-query KKT/flow audits.')
    batch=[]
    for z in scale:
        if z['specification']['family']=='late-renewal':
            batch.append([z['public_nodes'],fmt(z['batch_101_inversions_seconds']['median']),fmt(z['machine_seconds']['median'])])
    (R/'tables.tex').write_text(out)
    ectab=table('Repeated-query and execution-machine measurements','tab:ec-batch','rrr',
        'Vertices & 101 root inversions & Machine minimization',batch,
        'Seconds, median of three repetitions. The 101 payments are equally spaced across the compiled feasible root interval. Only inversion is included; emitting and auditing 101 different policies is not included. Machine minimization is for the original single query.')
    (R/'companion_tables.tex').write_text(ectab)
    facts={'completed_comparison_workers':len(compare),'completed_scaling_workers':len(scale),
        'exact_tree_comparisons':8,'qp_max_absolute_value_error':max(errors),'qp_max_primal_residual':max(residuals),
        'tree_to_quotient_time_ratio_range':[min(ratios),max(ratios)],'grid80_max_loss':max(gaps),
        'max_public_vertices':max(z['public_nodes'] for z in scale),'max_stored_segments':max(z['statistics']['stored_segments'] for z in scale),
        'late_renewal_max_vertices':scale[7]['statistics'],'late_renewal_max_symbols':scale[7]['machine_symbols']}
    (R/'results/summary.json').write_text(json.dumps(facts,indent=2)+'\n')
    print(json.dumps(facts,indent=2))
if __name__=='__main__':run()
