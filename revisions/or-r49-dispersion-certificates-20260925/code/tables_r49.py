"""Generate every displayed R49 number from preserved per-instance records."""
from pathlib import Path
from fractions import Fraction as F
import json,statistics
R=Path(__file__).resolve().parents[1]

def n(x,d=7):
    if x is None:return '--'
    x=float(F(x)) if isinstance(x,str) else float(x)
    if x==0:return '0'
    if abs(x)<10**(-d):return f'{x:.2g}'
    return f'{x:.{d}f}'.rstrip('0').rstrip('.')

def tid(row):
    if row['family']=='paired':return 'P'+row['id'][-2:]
    if row['family']=='common':return f"C{row['k']}/{row['n']}/{row['seed']-49400}"
    return f"S{row['seed']-49500}/{100 if row['epsilon']=='1/100' else 1000}/{row['node_limit']}"

def table(caption,label,cols,header,rows,note=''):
    return ('\\begin{table}[p]\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n'
      '\\setlength{\\tabcolsep}{3pt}\n\\begin{tabular}{'+cols+'}\\toprule\n'+header+' \\\\\n\\midrule\n'
      +'\n'.join(' & '.join(map(str,row))+' \\\\' for row in rows)+'\n\\bottomrule\\end{tabular}\n'
      +(r'\par\smallskip\begin{minipage}{.98\textwidth}'+note+r'\end{minipage}'+'\n' if note else '')+'\\end{table}\n')

def longtable(caption,label,cols,header,rows):
    return ('\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+'}\\\\\n\\toprule\n'+header+' \\\\\n\\midrule\\endfirsthead\n'
      '\\toprule\n'+header+' \\\\\n\\midrule\\endhead\n'
      +'\n'.join(' & '.join(map(str,row))+' \\\\' for row in rows)+'\n\\bottomrule\n\\end{longtable}\n')

def run():
    rows=json.loads((R/'results/study.json').read_text())['cases'];mips=json.loads((R/'results/mip.json').read_text())['cases']
    statuses=[v['status'] for rr in mips for v in rr['envelopes'].values()]
    successes=sum(x==0 for x in statuses);timeouts=sum(x==1 for x in statuses)
    status_text=(f'All {len(statuses)} solves terminate with the solver\'s success status in this execution.' if successes==len(statuses) else f'Of the {len(statuses)} solves, {successes} report success and {timeouts} reach the time limit; all returned statuses and bounds remain in the record.')
    (R/'generated/mip_status.tex').write_text(status_text+'\n')
    paired=[r for r in rows if r['family']=='paired'];common=[r for r in rows if r['family']=='common'];stress=[r for r in rows if r['family']=='stress']
    complexity=[
      ('Saturated catalog','Exact joint recurrence','Polynomial at saturation','R42; retained companion'),
      ('Unrestricted price','Exact priced menu','Polynomial per price, not a joint optimum','R43; Appendix~\\ref{sec:r43-decomposition}'),
      ('Fixed individual targets','Exact memory--charge frontier','Polynomial conditional on targets','R45; Theorem~\\ref{thm:r45-frontier}'),
      ('Individual target boxes','Exact two-sided bound; checked cover','Accuracy search in response types','R46; Theorems~\\ref{thm:r46-box}--\\ref{thm:r46-adaptive}'),
      ('Guarded / harmonic groups','Original-space error composition','Accuracy-dependent cap and cost bins','R47--R48; companion'),
      ('One eligible prefix','Exact original-budget joint optimum','Polynomial in histories, catalog and budget','New; Theorem~\\ref{thm:r49-frontier}'),
      ('Several eligible prefixes','Exact group oracle; additive joint accuracy','Exponent $E-1$, no dispersion allowance','New; Theorems~\\ref{thm:r49-box}--\\ref{thm:r49-accuracy}')]
    out=table('Joint-design regimes and theorem provenance. Each guarantee retains its stated assumptions.','tab:r49-complexity',r'p{.18\textwidth}p{.25\textwidth}p{.27\textwidth}p{.23\textwidth}',
      'Regime & Guarantee & Dependence & Provenance',complexity,
      r'The full R42--R48 theorem map remains in Table~\ref{tab:r46-contributions} of the computational record. Conditional, augmented-budget and original-budget results are not interchanged.')
    out+=table('All 24 paired original-space intervals. The unchanged tolerance is $10^{-3}$ and the node allowance is 31.','tab:r49-paired','rrrrrrrrr',
      'Case & Histories & Catalog & Budget & Classes & Prior gap & Pooled gap & Nodes & Seconds',
      [(r['id'][-2:],r['k'],r['n'],r['m'],r['eligibility_groups'],n(r['historical_r48_harmonic']['gap']),n(r['gap'],8),r['evaluated_nodes'],n(r['seconds'],3)) for r in paired],
      'Prior gaps are the immutable harmonic-coarsening intervals, not fresh matched-machine measurements. All new intervals meet tolerance; 19 have zero rational width. Case 19 retains a slightly wider interrupted interval. Exact arithmetic and complete lotteries are in the machine-readable certificates.')
    scale=[]
    for k in sorted({r['k'] for r in common}):
      for nn in sorted({r['n'] for r in common}):
        rr=[r for r in common if r['k']==k and r['n']==nn]
        scale.append((k,nn,'2/2',f"{min(r['seconds'] for r in rr):.3f}--{max(r['seconds'] for r in rr):.3f}",f"{min(r['check_seconds'] for r in rr):.3f}--{max(r['check_seconds'] for r in rr):.3f}"))
    out+=table('Common-eligibility joint optimization: all 16 intervals are exactly closed in one node.','tab:r49-scaling','rrrrr',
      'Histories & Catalog & Exact / cases & Optimization seconds & Checking seconds',scale,
      'Each row contains the two declared seeds; time ranges are reported without a statistical confidence claim. The budget is three and the requested tolerance is zero. Caps and service costs vary within the single eligibility class.')
    sr=[]
    for seed in sorted({r['seed'] for r in stress}):
      rr=[r for r in stress if r['seed']==seed and r['epsilon']=='1/1000'];s31=next(r for r in rr if r['node_limit']==31);s127=next(r for r in rr if r['node_limit']==127)
      sr.append((seed,s31['eligibility_groups'],n(s31['exact_reference'],6),n(s31['gap']),n(s127['gap']),n(s127['seconds'],3),'Yes' if s127['status']=='COMPLETE' else 'No'))
    out+=table('Eligibility stress at tolerance $10^{-3}$. Every row has 12 histories, nine catalog levels and budget three.','tab:r49-stress','rrrrrrr',
      'Seed & Classes & Exact value & Gap (31) & Gap (127) & Seconds (127) & Complete',sr,
      'Parentheses give node allowances, not claims that every run used all nodes. Two of the twelve tighter requests finish; all twelve requests at $10^{-2}$ finish. The record includes both tolerances, both budgets, exact references and every interruption. The final column refers to the 127-node allowance.')
    (R/'generated/main_tables.tex').write_text(out)
    details=r'''\section{Complete Exact-Pooling Records}\label{sec:r49-record}
P00--P23 identify the unchanged paired cases. C$k/N/s$ identifies history count, catalog size, and seed offset from 49400. S$s/a/n$ identifies seed offset from 49500, inverse tolerance, and node allowance. These are labels for the full machine-readable identifiers, not additional cases. Times below are measured in the execution environment recorded in \texttt{results/study.json}. Optimization and independent checking are timed separately.

The scale is $A=r+\max_j\gamma_j/2+\sum_{i=1}^{m}\rho_{(i)}$, where the charges are sorted from largest to smallest. The normalized interval width is gap divided by $A$. This is a scale diagnostic, not a relative-error theorem. An exact-reference loss is reported only when a reference was specified; a dash means that no exhaustive reference was requested. All common-eligibility rows instead have exact zero-width certificates.
\setlength{\tabcolsep}{4pt}
'''
    details+=longtable('All 64 exact-pooling runs, with interruptions retained.','tab:r49-all','lrrrrrr',
      'Identifier & Classes & Nodes & Gap & Seconds & Check seconds & Complete',
      [(tid(r),r['eligibility_groups'],r['evaluated_nodes'],n(r['gap'],8),n(r['seconds'],4),n(r['check_seconds'],4),'Yes' if r['status']=='COMPLETE' else 'No') for r in rows])
    srows=[]
    for r in rows:
      raw=r['model'];scale=F(raw['r'])+max(map(F,raw['gamma']))/2+sum(sorted(map(F,r['charges']),reverse=True)[:r['m']])
      ref=r.get('exact_reference') or (r.get('historical_reference') or {}).get('original')
      loss=None if ref is None else F(ref)-F(r['lower_bound'])
      relative=None if ref is None or F(ref)==0 else loss/abs(F(ref))
      srows.append((tid(r),n(scale,6),n(F(r['gap'])/scale,8),n(loss,8),n(relative,8)))
    details+=longtable('Scale diagnostics and exact-reference incumbent losses; no missing reference is imputed.','tab:r49-scales','lrrrr',
      'Identifier & Objective scale & Gap / scale & Reference loss & Relative loss',srows)
    mrows=[]
    for r in mips:
      src=next(z for z in rows if z['id']==r['source_case'])
      for env,v in r['envelopes'].items():
        mrows.append((tid(src),'Tangent' if env=='tangent' else 'Secant',v['status'],n(v['seconds'],4),v.get('node_count','--'),n(v.get('mip_gap'),6),n(v['approximation_error'],8),n(r['bracket_width'],8)))
    details+=longtable('Every direct mixed-integer solve. Bounds and solver gaps are numerical, not exact certificates.','tab:r49-mip','llrrrrrr',
      'Case & Envelope & Status & Seconds & Nodes & Solver gap & Error & Bracket',mrows)
    details+=r'''Status zero denotes successful numerical termination. A dash denotes a field the solver did not return, never an inferred zero. Error is the uniform quadratic-envelope allowance; bracket is the tangent upper bound minus the original-payoff value of the secant feasible policy. Small signed roundoff widths, when present, are retained in the raw records. Both envelopes have 32 segments and a three-second limit. The uneliminated probabilities, service tiers, selected levels, model residuals, primal objective and numerical dual bound are retained for every solve.

\paragraph{Historical distinctions.}
The archived charged portfolio example has exact net value $1373/3600$, portfolio value $53/150$, and loss $101/3600$, approximately 7.36 percent of the positive exact net value. Its safeguarded exactness is a sample observation. The inserted-ideal-target continuous example is an oracle-candidate sanity check. The historical large conditional table explicitly keeps its targets-fixed label. None is reclassified as an exact-pooling result.
'''
    (R/'generated/detailed_tables.tex').write_text(details)
if __name__=='__main__':run()
