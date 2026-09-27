"""Deterministic aggregation of recorded R24 evidence and dated reanalyses."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;O=R/'results';T=R/'tables';T.mkdir(exist_ok=True)
NAMES=['lifted-price-continuation','tanh-gradient','rbf-direct']
SHORT={'lifted-price-continuation':'Lifted continuation','tanh-gradient':'Tanh gradient','rbf-direct':'RBF direct',
       'dense-cold':'Dense cold','dense-previous':'Dense previous','protected-tanh-gradient':'Protected tanh',
       'protected-rbf-direct':'Protected RBF','classical-robust-maximin':'Robust maximin'}
PHASES=['prediction','initial_solve','first_audit','polishing','fallback_setup','fallback_solve','fallback_audit']

def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def stats(x):
    a=np.array(x,float)
    return {'mean':float(np.mean(a)),'median':float(np.median(a)),
            'q25':float(np.quantile(a,.25)),'q75':float(np.quantile(a,.75)),
            'p95':float(np.quantile(a,.95)),'max':float(np.max(a))}

def intervals(values,seed):
    a=np.array(values,float);rng=np.random.default_rng(seed);n=len(a)
    ordinary=np.mean(a[rng.integers(0,n,size=(10000,n))],axis=1)
    # Additional serial-dependence sensitivity; this is exploratory, not a
    # distribution-free coverage theorem. Classical continuation carries state.
    block=min(4,n); starts=rng.integers(0,n,size=(10000,math.ceil(n/block)))
    indices=((starts[:,:,None]+np.arange(block))%n).reshape(10000,-1)[:,:n]
    blocked=np.mean(a[indices],axis=1)
    return {'mean':float(a.mean()),'percentile95':np.quantile(ordinary,[.025,.975]).tolist(),
            'moving_block4_percentile95':np.quantile(blocked,[.025,.975]).tolist(),
            'pairs':n,'scope':'Descriptive fixed-fit paired resampling; no retraining guarantee or distribution-free coverage claim.'}

def f(x,d=2):return f'{x:.{d}f}'
def sci(x):
    if x==0:return '0'
    exponent=math.floor(math.log10(abs(x)));a=x/10**exponent
    return r'\ensuremath{'+f'{a:.2f}'+r'\times10^{'+str(exponent)+'}}'

def table(caption,label,headers,rows,widths=None):
    cols='l'+'r'*(len(headers)-1)
    out=r'\begin{table}[tbp]\centering\scriptsize'+'\n'+r'\caption{'+caption+'}\n'+r'\label{'+label+'}\n'
    out+=r'\begin{tabular}{'+cols+'}\n'+r'\toprule'+'\n'+' & '.join(headers)+r'\\'+'\n'+r'\midrule'+'\n'
    out+='\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)+'\n'+r'\bottomrule'+'\n'+r'\end{tabular}'+'\n'+r'\end{table}'+'\n\n'
    return out

def run():
    rows=read(O/'timing_rows.json');setups=read(O/'timing_setup.json');summ=[]
    for ix,setup in enumerate(setups):
      for ti,tol in enumerate([1e-3,1e-5]):
        base=[r for r in rows if r['instance']==ix and r['tol']==tol and r['method']==NAMES[0]]
        baseline={j:np.mean([r['total'] for r in base if r['context_id']==j]) for j in sorted(set(r['context_id'] for r in base))}
        for mi,method in enumerate(NAMES):
            rr=[r for r in rows if r['instance']==ix and r['tol']==tol and r['method']==method]
            item={'instance':ix,'spec':setup['spec'],'tol':tol,'method':method,'attempts':len(rr),
                  'failures':sum(r['status']!='PASS' for r in rr),'total_ms':stats([r['total']*1000 for r in rr])}
            valid=[r for r in rr if r['status']=='PASS']
            item['fallback_fraction']=float(np.mean([r['fallback'] for r in valid])) if valid else None
            item['phase_mean_ms']={k:float(np.mean([r.get(k,0)*1000 for r in rr])) for k in PHASES}
            fb=[r for r in valid if r['fallback']]
            item['fallback_conditional_mean_ms']=float(np.mean([sum(r[k] for k in ('fallback_setup','fallback_solve','fallback_audit'))*1000 for r in fb])) if fb else None
            item['fallback_conditional_mean_iterations']=float(np.mean([r['fallback_iterations'] for r in fb])) if fb else None
            pairs=[1000*(baseline[j]-np.mean([r['total'] for r in rr if r['context_id']==j])) for j in baseline]
            item['paired_savings_ms']=intervals(pairs,2405401+100*ix+10*ti+mi)
            if method!=NAMES[0]:
                ss=[a for a in setup['workspace_setup_repetitions'] if a['tol']==tol]
                setup_delta=float(np.mean([a['response']-a['lifted'] for a in ss]))
                offline=setup['label_seconds']+setup['fit_seconds'][method]+setup_delta
                delta=item['paired_savings_ms']['mean']/1000
                item['incremental_setup_seconds']=setup_delta;item['offline_seconds']=offline
                item['observed_crossing_queries']=math.ceil(offline/delta) if delta>0 else None
                ci=item['paired_savings_ms']['percentile95']
                item['resampling_savings_lower_positive']=ci[0]>0
                item['cost_difference_seconds_at_query_volume']={str(q):offline-q*delta for q in (1,100,1000,10000,100000,1000000)}
            summ.append(item)
    dump(O/'timing_analysis.json',{'status':'ANALYZED','summary':summ,
       'resampling_note':'Repetitions averaged within context. Main intervals are descriptive paired percentile intervals; moving-block length four sensitivity is also retained because continuation creates serial dependence. Neither is a retraining-level or distribution-free confidence guarantee.'})
    # Retrospective scaling: preserve all old rows and their original machine times.
    old=R.parent/'or-r22-20260923/results';oldrows=read(old/'scaling_rows.json');oldsum=[]
    for ix in sorted(set(r['instance'] for r in oldrows)):
      for ti,tol in enumerate([1e-3,1e-5]):
        base={r['context']:r['total'] for r in oldrows if r['instance']==ix and r['tol']==tol and r['method']==NAMES[0]}
        for mi,method in enumerate(['dense-cold','dense-previous',*NAMES]):
            rr=[r for r in oldrows if r['instance']==ix and r['tol']==tol and r['method']==method]
            pairs=[1000*(base[r['context']]-r['total']) for r in rr]
            oldsum.append({'instance':ix,'spec':rr[0]['spec'],'tol':tol,'method':method,'attempts':len(rr),
              'failures':sum(r['status']!='PASS' for r in rr),'total_ms':stats([r['total']*1000 for r in rr]),
              'paired_savings_ms':intervals(pairs,2408401+ix*100+ti*10+mi),
              'fallback_fraction':float(np.mean([r.get('fallback',True) for r in rr]))})
    dump(O/'r22_scaling_reanalysis.json',{'status':'RETROSPECTIVE','source_rows':len(oldrows),'summary':oldsum,
       'scope':'Eight historical contexts per configuration; no new run, retraining or accuracy claim.'})
    oldrob=read(R.parent/'or-r23-20260923/results/rows.json');arch=[]
    for radius in [0,1,2,4]:
      for method in ['protected-tanh-gradient','protected-rbf-direct','classical-robust-maximin']:
        rr=[a for a in oldrob if a['r']==radius and a['method']==method]
        arch.append({'r':radius,'method':method,'n':len(rr),'own_ms':stats([r['own_seconds']*1000 for r in rr]),
           'comparator_ms':stats([r['shared_comparator_seconds']*1000 for r in rr]),
           'recorded_sum_ms':stats([(r['own_seconds']+r['shared_comparator_seconds'])*1000 for r in rr])})
    dump(O/'r23_robust_cost_reanalysis.json',{'status':'RETROSPECTIVE','summary':arch,
       'scope':'Own plus eight-comparator batch on original host. Original learned timers omit prediction, so these are not complete learned-pipeline times.'})
    interior=read(O/'interior_summary.json');cost=read(O/'robust_cost_summary.json');execution=read(O/'timing_execution.json')
    r4=next(x for x in interior['summary'] if x['r']==4)
    maxgap=max(max(a['true_gap']['max'],a['outer_gap']['max']) for a in interior['summary'])
    metrics={'RTwentyFourInteriorGap':sci(maxgap),'RTwentyFourSlackTotal':f(r4['total_slack_upper']['mean'],6),
      'RTwentyFourSlackOuter':f(r4['outer_set_slack_upper']['mean'],6),'RTwentyFourSlackInterpolation':f(r4['interpolation_slack_upper']['mean'],6),
      'RTwentyFourTimingRows':f"{execution['rows']:,}",'RTwentyFourTimingFailures':str(execution['failures'])}
    for suffix,method in [('Tanh','protected-tanh-gradient'),('RBF','protected-rbf-direct'),('Classical','classical-robust-maximin')]:
        cr=next(a for a in cost['summary'] if a['r']==4 and a['method']==method)
        metrics['RTwentyFourRobust'+suffix]=f(cr['total_seconds']['mean']*1000,2)
    (T/'metrics.tex').write_text('% Generated only from recorded R24 observations.\n'+'\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in metrics.items())+'\n')
    mainrows=[]
    for a in interior['summary']:
        mainrows.append([f(a['rho'],4),f(a['outer_set_slack_upper']['mean'],6),f(a['interpolation_slack_upper']['mean'],6),
                        f(a['total_slack_upper']['mean'],6),f(a['total_slack_upper']['median'],6),f(a['total_slack_upper']['p95'],6)])
    maintex=table('Interior-model certificate conservatism. Each radius has 192 models; entries use certified upper endpoints of slack brackets.','tab:r24-tightness',
       [r'Radius',r'Outer mean',r'Interpolation mean',r'Total mean',r'Total median',r'Total 95th'],mainrows)
    trows=[]
    for a in summ:
        if a['tol']!=1e-5:continue
        v=a['total_ms'];pair=a['paired_savings_ms'];ci=pair['percentile95']
        saving='---' if a['method']==NAMES[0] else f(pair['mean'])+' ['+f(ci[0])+', '+f(ci[1])+']'
        trows.append([str(a['spec'][0]),{'lifted-price-continuation':'Lifted','tanh-gradient':'Tanh','rbf-direct':'RBF'}[a['method']],f(v['mean']),f(v['median']),
                      '['+f(v['q25'])+', '+f(v['q75'])+']',f(100*a['fallback_fraction'],1)+r'\%',saving])
    maintex+=table('Strict-target matched timing in milliseconds. Thirty-two contexts and three repetitions per fixed fit. Positive paired savings favor the predictor; bracketed savings intervals are descriptive percentile resampling intervals.','tab:r24-timing',
        ['Nodes','Method','Mean','Median','Quartiles','Fallback','Savings [interval]'],trows)
    (T/'main_tables.tex').write_text(maintex.replace(r'\centering\scriptsize',r'\centering\small\setlength{\tabcolsep}{4pt}'))
    cstex=''
    offrows=[]
    for a in setups:
        for name in ['tanh-gradient','rbf-direct']:
            mem=a['memory_predictors'][name]
            offrows.append([str(a['spec'][0]),SHORT[name],f(a['label_seconds'],3),f(a['fit_seconds'][name],5),
                            str(mem['serialized_bytes']),str(mem['reachable_array_bytes'])])
    cstex+=table('Separate offline information and predictor storage costs. Label time is the full cost for a standalone deployment of either method. Reachable array bytes are not a peak-memory measure.','tab:r24-offline',
        ['Nodes','Method','Labels (s)','Fit (s)','Serialized bytes','Array bytes'],offrows)
    memoryrows=[]
    for a in setups:
        memoryrows.append([str(a['spec'][0]),str(a['response_sparse_matrix_bytes']),str(a['lifted_sparse_matrix_bytes']),str(a['peak_process_rss_kib_to_this_point'])])
    cstex+=table('Matrix-input storage and whole-process peak memory. Sparse input bytes exclude solver factorization; peak RSS is a process high-water mark across methods, not an attributed method cost.','tab:r24-memory',
        ['Nodes','Response input bytes','Lifted input bytes','Process peak KiB'],memoryrows)
    for tol in [1e-3,1e-5]:
        rr=[]
        for a in summ:
            if a['tol']!=tol:continue
            ph=a['phase_mean_ms']
            rr.append([str(a['spec'][0]),SHORT[a['method']],f(ph['prediction']),f(ph['initial_solve']),
                       f(ph['first_audit']+ph['polishing']),f(ph['fallback_setup']),f(ph['fallback_solve']),f(ph['fallback_audit'])])
        cstex+=table('Mean timing components in milliseconds at target '+('$10^{-3}$' if tol==1e-3 else '$10^{-5}$')+'. Fallback columns are unconditional means; conditional means and iterations are in the machine-readable record.','tab:r24-components-'+str(tol),
            ['Nodes','Method','Predict','Initial','Audit/polish','FB setup','FB solve','FB audit'],rr)
    rr=[]
    for a in cost['summary']:
        rr.append([f(a['rho'],2),SHORT[a['method']],f(a['prediction_seconds']['mean']*1000),
                   f(a['own_seconds']['mean']*1000),f(a['comparator_seconds']['mean']*1000),f(a['total_seconds']['mean']*1000),f(a['min_gain_lower'],6)])
    cstex+=table('Fresh-host robust pointwise certification costs in milliseconds, including ensemble prediction. Sixteen contexts per radius. The entire comparator batch is charged once per independently certified method; its actual reuse in the experiment is disclosed.','tab:r24-robust-cost',
        ['Radius','Method','Prediction','Own total','Comparators','Complete total','Minimum gain'],rr)
    # Retain all entries instead of selecting favorable scales or methods.
    for group in range(4):
        rr=[]
        for a in oldsum[group*25:(group+1)*25]:
            v=a['total_ms'];pair=a['paired_savings_ms'];ci=pair['percentile95'];spec='/'.join(map(str,a['spec']))
            rr.append([spec,'C' if a['tol']==1e-3 else 'S',SHORT[a['method']],f(v['median']),
              '['+f(v['q25'])+', '+f(v['q75'])+']',f(pair['mean']), '['+f(ci[0])+', '+f(ci[1])+']'])
        cstex+=table('Retrospective full R22 scaling variability, part '+str(group+1)+'. Specification is nodes/services/resources/capacities/curvature; C and S denote coarse and strict targets. Times and paired savings are milliseconds; each entry has only eight historical contexts.','tab:r24-old-scaling-'+str(group+1),
          ['Specification','Target','Method','Median','Quartiles','Savings','Resampling interval'],rr)
    (T/'computational_tables.tex').write_text(cstex)
    dump(O/'analysis.json',{'status':'PASS','timing_pipelines':len(rows),'timing_failures':execution['failures'],
      'interior_models':interior['models'],'interior_failed_solves':len(interior['failures']),
      'robust_cost_policies':cost['policy_records'],'robust_cost_failed_solves':len(cost['failed_solves']),
      'old_scaling_rows':len(oldrows),'old_robust_rows':len(oldrob),
      'finite_observed_break_even_cases':sum(a.get('observed_crossing_queries') is not None for a in summ),
      'max_interior_comparator_bracket':maxgap})
    print(json.dumps(read(O/'analysis.json')))
if __name__=='__main__':run()
