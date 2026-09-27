#!/usr/bin/env python3
"""Exhaustive retrospective R16 summaries plus separately identified R19 tests."""
import json,math,hashlib
from pathlib import Path
from fractions import Fraction as F
from statistics import mean,median
ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent/'or-r16-20260922'/'results';OUT=ROOT/'results';TAB=ROOT/'tables'
LABEL={'tanh-value':'Tanh: value','tanh-gradient':'Tanh: value + gradient','tanh-direct':'Tanh: price','quadratic-value':'Quadratic: value','quadratic-gradient':'Quadratic: value + gradient','quadratic-direct':'Quadratic: price','rbf-direct':'RBF: price','cubic-value':'Cubic: value','classical-cold':'Classical: cold','classical-previous':'Classical: previous'}
def load(p):return json.loads(p.read_text())
def table(name,caption,label,cols,header,rows,note=''):
    text='\\begin{table}[p]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n\\setlength{\\tabcolsep}{4pt}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+header+' \\\\\n\\midrule\n'
    text+='\n'.join(' & '.join(map(str,row))+' \\\\' for row in rows)+'\n\\bottomrule\n\\end{tabular}\n'
    if note:text+='\n\\par\\medskip\\begin{minipage}{\\textwidth}'+note+'\\end{minipage}\n'
    text+='\\end{table}\n';(TAB/name).write_text(text)
def run():
    OUT.mkdir(exist_ok=True);TAB.mkdir(exist_ok=True);s=load(OLD/'summary.json');co=load(OLD/'cohorts.json');dep=load(OLD/'deployment.json');p=load(OLD/'primitives.json')
    names=list(s['methods']);assert len(co)==8 and all(len(x['contexts'])==256 for x in dep)
    bound=sum((F((abs(int(p['bnum'][i]))+sum(abs(int(row[i])) for row in p['Unum']))**2,128*int(p['qnum'][i])) for i in range(len(p['qnum']))),F(0))
    bound+=F(sum(int(k)*abs(int(v)) for k,v in zip(p['knum'],p['vnum'])),512)
    B=(bound.numerator+bound.denominator-1)//bound.denominator;assert B==25
    penalty=B*math.sqrt(math.log(7/.05)/(2*2048));fleet=[]
    for name in names:
        gains=[r['gain'] for c in dep for r in c['methods'][name]];reg=[r['regret_upper'] for c in dep for r in c['methods'][name]]
        assert abs(mean(gains)-s['methods'][name]['gain'])<1e-12
        assert abs(mean(reg)-s['methods'][name]['regret_upper'])<1e-12
        fleet.append({'method':name,'mean_gain':mean(gains),'lower_bound':max(0,mean(gains)-penalty)})
    oldtim=[];raw=load(OLD/'timings.json')
    for m in ['cached-full-cold','cached-full-previous']+names:
        for tol in ([None] if m.startswith('cached') else [1e-3,1e-5]):
            rr=[r for r in raw if r['method']==m and r['tol']==tol]
            oldtim.append({'method':m,'tol':tol,'n':len(rr),'mean_total':mean(r['total'] for r in rr),'median_total':median(r['total'] for r in rr),'fallback':mean(r['fallback'] for r in rr)})
    star=load(OLD/'star_rows.json');strat=[]
    bins={
      'absolute_friction_distance':lambda r:'<0.001' if abs(r['friction_distance'])<.001 else '0.001--0.01' if abs(r['friction_distance'])<.01 else '>=0.01',
      'capacity_binding':lambda r:str(bool(r['capacity_binding'])),
      'active_leaves':lambda r:'0' if r['active_leaves']==0 else '1--63' if r['active_leaves']<64 else '>=64',
      'saturated_leaves':lambda r:'0' if r['saturated_leaves']==0 else '1--63' if r['saturated_leaves']<64 else '>=64',
      'breakpoint_distance':lambda r:'<0.0001' if r['breakpoint_distance']<.0001 else '0.0001--0.01' if r['breakpoint_distance']<.01 else '>=0.01',
      'optimal_gain_lower':lambda r:'<0.00001' if r['optimal_gain_lower']<1e-5 else '0.00001--0.001' if r['optimal_gain_lower']<.001 else '>=0.001'}
    for dimension,fn in bins.items():
        groups={}
        for r in star:groups.setdefault((r['method'],fn(r)),[]).append(r)
        for (method,binname),rr in sorted(groups.items()):strat.append({'dimension':dimension,'method':method,'bin':binname,'n':len(rr),**{k:mean(r[k] for r in rr) for k in ['regret_upper','gap','gate','root_repair','pass_1e-7','pass_1e-3']}})
    inputs={str(x.relative_to(ROOT.parents[1])):hashlib.sha256(x.read_bytes()).hexdigest() for x in [OLD/'summary.json',OLD/'cohorts.json',OLD/'deployment.json',OLD/'timings.json',OLD/'star_rows.json',OLD/'primitives.json']}
    result={'status':'PASS','classification':'Retrospective analysis of all R16 observations; not new deployments or preregistration','fleet':{'policies_per_method':8,'cohorts_per_policy':1,'contexts_per_cohort':256,'methods':7,'delta':.05,'exact_range_bound':str(bound),'integer_range_upper':B,'penalty':penalty,'bounds':fleet,'target':'uniform independent randomization over the eight fixed policies, conditional on all fitted models'},'individual_policy_bounds':s['frozen_bounds'],'paired_training_comparison':s['paired_neural_regret_difference'],'original_timing_reanalysis':oldtim,'star_stratification':strat,'input_sha256':inputs}
    (OUT/'reanalysis.json').write_text(json.dumps(result,indent=2)+'\n')
    table('quality.tex','Unrefined multistage decisions and conditional frozen-fleet gains','tab:r19-quality','lrrrr','Method & Regret upper & Mean gap & Pass (\\%) & Fleet lower',[[LABEL[m],f"{s['methods'][m]['regret_upper']:.6f}",f"{s['methods'][m]['gap']:.6f}",f"{100*s['methods'][m]['pass_1e-3']:.2f}",f"{fleet[i]['lower_bound']:.6f}"] for i,m in enumerate(names)],'All 2,048 independent deployment contexts per method are included. Pass means the immediate exact full-objective gap is at most $10^{-3}$. No method passes at $10^{-5}$ before refinement. Fleet bounds apply to the explicitly randomized eight-model deployment, not each model or arbitrary retraining.')
    bc=load(OUT/'boundary_checks.json');rr=bc['rows'];geo=[]
    for st in ['heterogeneous','binding-capacity','tier-boundary','switching-kinks']:
        a=[r for r in rr if r['stratum']==st];geo.append([st.replace('-',' '),len(a),sum(r['binding_capacities']>0 for r in a),sum(r['boundary_tiers']>0 for r in a),sum(r['near_kinks']>0 for r in a),f"{max(r.get('gradient_fd_error',0) for r in a):.2e}"])
    table('geometry.tex','Deliberate multistage geometry checks','tab:r19-geometry','lrrrrr','Stratum & Cases & Capacity & Tier boundary & Kinks & Gradient error',geo,'Capacity, tier boundary, and kinks count instances with at least one such event; diagnostics use $10^{-5}$. Each of 128 implemented reference/proposal certificates is independently replayed. The gradient column is the maximum finite-difference error among the four checked contexts in that stratum.')
    cost=load(OUT/'matched_cost.json');cs={(r['method'],r['tol']):r for r in cost['summary']};ordered=['classical-cold','classical-previous']+names
    table('matched_cost.tex','Accuracy-targeted complete-pipeline cost','tab:r19-cost','lrrrr','Method & \\shortstack{Mean ms\\\\$10^{-3}$} & \\shortstack{Mean ms\\\\$10^{-5}$} & \\shortstack{Fall back\\\\(\\%)} & \\shortstack{Fall back\\\\(\\%)}',[[LABEL[m],f"{1000*cs[m,1e-3]['mean']:.3f}",f"{1000*cs[m,1e-5]['mean']:.3f}",f"{100*cs[m,1e-3]['fallback_rate']:.2f}",f"{100*cs[m,1e-5]['fallback_rate']:.2f}"] for m in ordered],'The last two columns correspond to $10^{-3}$ and $10^{-5}$, respectively. All methods start with numerical tolerance $10^{-5}$, then refine and re-audit when the independent full-objective gap fails the requested target. Each mean uses 256 records. No prediction, response, repair, audit, or actual refinement cost is omitted.')
    c0=min((cs[m,1e-3] for m in ['classical-cold','classical-previous']),key=lambda r:r['mean'])
    c1=min((cs[m,1e-5] for m in ['classical-cold','classical-previous']),key=lambda r:r['mean'])
    rb=cs['rbf-direct',1e-3];rb1=cs['rbf-direct',1e-5]
    findings=(f"At the coarse target, the lower-mean classical baseline costs {1000*c0['mean']:.3f} ms, compared with {1000*rb['mean']:.3f} ms for radial-basis direct-price deployment. "
      + (f"Its observed full-pipeline saving has a conservative offline break-even count of {rb['break_even_queries']:,} queries. " if rb['break_even_queries'] is not None else "There is no positive observed saving and therefore no finite break-even count. ")
      + f"At the strict target, the corresponding classical cost is {1000*c1['mean']:.3f} ms and the radial-basis cost is {1000*rb1['mean']:.3f} ms. "
      + "These are separately measured follow-up results, not the original fixed-solver-tolerance timings.\n")
    (TAB/'matched_findings.tex').write_text(findings)
    rows=[]
    for m in ordered:
        for t in [1e-3,1e-5]:
            a=cs[m,t];lo,hi=a['mean_difference_interval95'];rows.append([LABEL[m],'$10^{-3}$' if t==1e-3 else '$10^{-5}$',f"{1000*a['median']:.2f}",f"{1000*a['p95']:.2f}",str(a['break_even_queries']) if a['break_even_queries'] is not None else '--'])
    table('matched_details.tex','Timing dispersion and conservative offline break-even','tab:r19-cost-details','llrrr','Method & Target & \\shortstack{Median\\\\ms} & \\shortstack{95th percentile\\\\ms} & Break-even',rows,'A dash means no positive observed saving (or a classical method), not unmeasured overhead. All same-host label-generation and seven-model fitting cost is charged to each surrogate. Raw rows, component costs, and approximate eight-cohort timing-difference intervals are supplied in the results file.')
    stsum=load(OLD/'star_summary.json');rows=[]
    for st in ['original','critical-friction','capacity-activation','primitive-perturbation']:
        a={r['method']:r for r in stsum if r['stratum']==st}
        for m in ['tanh-value','tanh-gradient','tanh-direct','quadratic-direct','rbf-direct']:
            if m in a:rows.append([st,LABEL[m],f"{a[m]['regret_upper']:.2e}",f"{100*a[m]['root_repair']:.1f}"])
    table('star_strata.tex','Retained star stress strata: selected columns, complete records supplied','tab:r19-star','llrr','Stratum & Method & Regret upper & Root repair (\\%)',rows,'All eight methods, all four seeds, every stratum, and all geometry bins are retained in the machine-readable results; the table displays five methods for readability. Every method in the capacity-activation stratum has the same regret bracket to numerical precision. These are existing R16 observations, not newly generated R19 evidence.')
    print('reanalysis and tables PASS')
if __name__=='__main__':run()
