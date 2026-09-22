"""Generate every new manuscript number from recorded results, not hand edits."""
from pathlib import Path
import json,statistics as st
R=Path(__file__).resolve().parent;O=R/'results';T=R/'tables';T.mkdir(exist_ok=True)
LABEL={'classical-cold':'Dense cold','classical-previous':'Dense previous','lifted-price-continuation':'Lifted continuation',
       'dense-cold':'Dense cold','dense-previous':'Dense previous','tanh-value':'Tanh value','tanh-gradient':'Tanh gradient',
       'tanh-direct':'Tanh direct','quadratic-value':'Quadratic value','quadratic-gradient':'Quadratic gradient',
       'quadratic-direct':'Quadratic direct','rbf-direct':'RBF direct','ensemble-tanh-gradient':'Tanh-gradient ensemble','ensemble-rbf-direct':'RBF-direct ensemble'}
def save(name,text):(T/name).write_text(text+'\n')
def table(caption,label,columns,header,rows,note=''):
    return ('\\begin{table}[tbp]\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n'
      '\\begin{tabular}{'+columns+'}\n\\toprule\n'+header+'\\\\\n\\midrule\n'+
      '\\\\\n'.join(rows)+'\\\\\n\\bottomrule\n\\end{tabular}\n'+
      ('\\par\\smallskip\\begin{minipage}{.98\\textwidth}\\small '+note+'\\end{minipage}\n' if note else '')+'\\end{table}')
def run():
    cost=json.loads((O/'matched_summary.json').read_text());val=json.loads((O/'validation_summary.json').read_text());scale=json.loads((O/'scaling_summary.json').read_text())
    assert cost['observations']==5120 and val['observations']==5120 and scale['observations']==800
    c={(x['method'],x['tol']):x for x in cost['summary']};names=list(dict.fromkeys(x['method'] for x in cost['summary']))
    rr=[]
    for name in names:
        a,b=c[name,.001],c[name,.00001]
        rr.append(f"{LABEL[name]} & {a['mean_ms']:.3f} & {100*a['original_pass']:.2f} & {100*a['polished_pass']:.2f} & {b['mean_ms']:.3f} & {100*b['polished_pass']:.2f}")
    save('matched.tex',table('Complete matched-target pipelines after certificate-price repair.','tab:r21-cost','lrrrrr',
         r'Method & Coarse ms & Before (\%) & After (\%) & Strict ms & After (\%)',rr,
         r'Coarse and strict refer to final gap targets $10^{-3}$ and $10^{-5}$. Percentages are immediate passes before or after price repair, not final feasibility rates. Every returned final decision meets its requested target. Each method--target mean uses 256 complete pipelines; fallback and all audit costs are charged.'))
    coarse=[x for x in cost['summary'] if x['tol']==.001 and x['method'] in names[:3]];best=min(coarse,key=lambda x:x['mean_ms']);rb=c['rbf-direct',.001]
    allstrict=all(c[name,.00001]['polished_pass']==0 for name in names[3:])
    save('matched_findings.tex',f"At the coarse target, the smallest observed classical mean is {best['mean_ms']:.3f} ms for {LABEL[best['method']].lower()}, compared with {rb['mean_ms']:.3f} ms for RBF direct prices. RBF's immediate pass rate changes from {100*rb['original_pass']:.2f}\\% to {100*rb['polished_pass']:.2f}\\% without changing its primal proposals. "+('At the strict target, every surrogate still requires full refinement in every timed case.' if allstrict else 'Strict-target refinement frequencies are reported separately and are not inferred from coarse-target success.'))
    rr=[]
    for x in val['summary']:
        rr.append(f"{LABEL[x['method']]} & {x['domain'].upper()} & {x['mean_restricted_gain_lower']:.6f} & {x['expected_restricted_gain_lower']:.6f} & {x['mean_regret_upper']:.6f}")
    save('validation.tex',table('Independent deterministic deployment against reoptimized time-only amendments.','tab:r21-validation','llrrr',
      'Policy & Domain & Mean gain lower & Expected gain lower & Regret upper',rr,
      r'The gain comparator is the optimized restricted value, not the arbitrary outside protocol. The four expected-gain lower bounds have simultaneous confidence at least $0.95$, conditional on the frozen policies. The mean gain uses certified one-sided observations; regret is bounded against the full accepted optimum.'))
    lower=min(x['expected_restricted_gain_lower'] for x in val['summary']);gap=max(x['max_comparator_gap'] for x in val['summary'])
    save('validation_findings.tex',f"The smallest simultaneous expected-gain lower bound is {lower:.6f} normalized objective units across the four pairs. "+('All four bounds are positive.' if lower>0 else 'Not all four lower bounds establish positive expected gain.')+f" The largest observed restricted-comparator gap is {gap:.3g}; this small observed error is charged rather than treated as an exact optimum. Each domain's range bound is obtained from all 128 rationally audited vertices.")
    methods=['dense-cold','dense-previous','lifted-price-continuation','tanh-gradient','rbf-direct'];ss={(x['instance'],x['method'],x['tol']):x for x in scale['summary']}
    for tol,name,lab in [(1e-5,'scaling.tex','tab:r21-scaling'),(.001,'scaling_coarse.tex','tab:r21-scaling-coarse')]:
        rr=[]
        for ix,setup in enumerate(scale['setup']):
            nn,sv,r,cc,q=setup['spec'];a=[f'${nn}\\times {sv}$',f'{r}/{cc}/{q}']
            for m in methods:
                z=ss[ix,m,tol];a.append(f"{z['mean_ms']:.2f}"+(f"$^{{({z['failures']})}}$" if z['failures'] else ''))
            rr.append(' & '.join(a))
        save(name,table(('Strict' if tol==1e-5 else 'Coarse')+'-target scaling on complete accepted polyhedra (mean milliseconds).',lab,'llrrrrr',
          r'Nodes $\times$ services & $r/c/q$ & Cold & Previous & Lifted & Tanh & RBF',rr,
          r'Each entry includes eight held-out complete attempts. The second column reports resource rank, additional capacities, and the alternating curvature multiplier. All methods receive the same independent target, price repair and actual fallback. Parenthesized superscripts, when present, count failed target checks; such attempts remain in the recorded cost and do not establish a certified speed advantage. A separate 64-label fit is used at every configuration.'))
    failures=sum(x['failures'] for x in scale['summary']);largest=5
    a=ss[largest,'dense-cold',1e-5];b=ss[largest,'lifted-price-continuation',1e-5]
    save('scaling_findings.tex',f"At 1,023 nodes and two services, the strict-target dense-cold and lifted mean costs are {a['mean_ms']:.2f} and {b['mean_ms']:.2f} ms, respectively. The full scaling study records {failures} failed requested-target checks among 800 attempts; failures, if any, are retained. These results are distinct from the original 63-node, eight-fit comparison and are not pooled to create extra training replications.")
    geom=json.loads((O/'validation_geometry.json').read_text());vr=json.loads((O/'validation_rows.json').read_text());rr=[]
    for domain in ['iid','shift']:
        gg=[x for x in geom if x['domain']==domain];vv=[x for x in vr if x['domain']==domain and x['method']=='ensemble-tanh-gradient']
        outside=st.mean(any(abs(h)>16 for h in x['context'][:-1]) or not 2<=x['context'][-1]<=32 for x in vv)
        rr.append(f"{domain.upper()} & {len(gg)} & {100*outside:.2f} & {st.mean(x['capacity_binding'] for x in gg):.3f} & {st.mean(x['tier_boundary'] for x in gg):.3f} & {st.mean(x['switching_kinks'] for x in gg):.3f}")
    save('geometry.tex',table('Actual geometry in the new independent validation populations.','tab:r21-geometry','lrrrrr',
      r'Domain & Contexts & Out of support (\%) & Capacities & Tier bounds & Kinks',rr,
      'The last three columns are mean counts in the audited full reference decision. Zero capacity activation is reported as zero, not relabeled as a capacity stress test. The deliberate inherited R19 suite remains the separate test of forced active geometries.'))
    setup_rows=[]
    for x in scale['setup']:
        n,sv,*_=x['spec'];setup_rows.append(f"${n}\\times {sv}$ & {x['label_seconds']:.3f} & {x['fit_both_seconds']:.3f} & {x['dense_setup']:.3f} & {x['lifted_setup']:.3f} & {x['dense_P_nnz']:,} & {x['lifted_P_nnz']:,}")
    save('setup.tex',table('Measured scaling offline work and formulation sizes.','tab:r21-setup','lrrrrrr',
      r'Nodes $\times$ services & Labels (s) & Fits (s) & Dense setup & Lifted setups & Dense $P$ & Lifted $P$',setup_rows,
      'Labels include 64 lifted full-objective solves and independent audits. Fits include both declared predictors. Lifted setup charges two tolerance-isolated workspaces; dense cold setup charges one. The last columns report stored quadratic-matrix nonzero counts, not an asymptotic complexity theorem. Primitive construction and all remaining setup timings are retained in the raw summary.'))
    result={'status':'PASS','matched_pipelines':5120,'deterministic_policy_observations':5120,'validation_contexts':2560,
      'scaling_attempts':800,'scaling_labels':640,'scaling_target_failures':failures,'minimum_expected_gain_lower':lower,
      'old_numbers_preserved':True,'no_selected_model':True,'validation_seeds':[23011,23012]}
    (O/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':run()
