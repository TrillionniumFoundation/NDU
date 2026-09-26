"""Derive every new table and scalar from retained immutable run records."""
from pathlib import Path
import csv,json,statistics,gzip,collections
from rational import F,write,bits
R=Path(__file__).resolve().parents[1];OUT=R/'results';GEN=R/'generated'

def f(x,d=3):return f'{x:.{d}f}'
def sci(x):return f'{float(x):.3g}'
def med(rows,key):return statistics.median(row[key] for row in rows)
def main():
    cases=json.loads((OUT/'CASES.json').read_text())+json.loads((OUT/'EXTENDED_CASES.json').read_text());C={x['id']:x for x in cases}
    rows=[json.loads(p.read_text()) for p in (OUT/'runs').glob('*.json') if '.phase.' not in p.name]
    rows.sort(key=lambda z:(z['id'],z['method']));lookup={(x['id'],x['method']):x for x in rows}
    replay={x['run_id']:x for x in json.loads((OUT/'VERIFY_REPLAY.json').read_text())};mechanics={x['id']:x for x in json.loads((OUT/'MECHANICS_REPLAY.json').read_text())}
    reference={}
    for x in rows:
        if x['status']=='EXACT' and x.get('verification_status')=='PASS':
            val=F(x['lower']);old=reference.get(x['instance_sha256'])
            if old is not None and old!=val:raise ValueError('Exact references disagree')
            reference[x['instance_sha256']]=val
    diag=[]
    for x in rows:
        if x['method']!='price':continue
        case=C[x['id']];m=x.get('mechanics',{});ev=m.get('evaluations',[]);root_trace=[z for z in x.get('trace',[]) if z['nodes']==1]
        initial=F(ev[0]['upper'])-F(ev[0]['lower']) if ev else None
        root=F(m['root_gap']) if m.get('root_gap') is not None else F(root_trace[-1]['upper'])-F(root_trace[-1]['lower']) if root_trace else None
        cert=json.loads(gzip.decompress((OUT/x['certificate']).read_bytes()))
        row=dict(id=x['id'],instance_sha256=x['instance_sha256'],epsilon=x['epsilon'],k=case['k'],N=case['n'],m=case['m'],evaluated_nodes=x.get('nodes'),created_nodes=x.get('created_tree_nodes'),oracle_calls=x.get('oracle_calls'),initial_gross_gap=initial,root_gap=root,root_fraction_closed=None if initial in (None,0) or root is None else 1-root/initial,live_leaves=x.get('live_leaves'),maximum_depth=x.get('max_depth'),incumbent_updates=m.get('incumbent_updates'),bound_prunes=m.get('bound_prunes'),infeasible_prunes=m.get('infeasible_prunes'),fixed_book_closures=m.get('fixed_book_closures'),standalone_forced_command_fixings=0,mandatory_set_mean=statistics.mean(e['required'] for e in ev) if ev else 0,mandatory_set_max=max((e['required'] for e in ev),default=0),incumbent_book_size=len(cert['policy']['book']),lower=x['lower'],upper=x['upper'],gap=x['gap'],reference_exact=reference.get(x['instance_sha256']),algorithm_seconds=x['algorithm_seconds'],checker_seconds=x.get('verification_seconds'),raw_proof_bytes=x['proof_bytes'],gzip_proof_bytes=x['compressed_proof_bytes'],price_numerator_bits=x.get('price_bits',{}).get('numerator_bits'),price_denominator_bits=x.get('price_bits',{}).get('denominator_bits'))
        diag.append(row)
    with (OUT/'SEARCH_MECHANICS.csv').open('w',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=list(diag[0]));writer.writeheader();writer.writerows(diag)
    diagmap={x['id']:x for x in diag};screen=[]
    for x in rows:
        if x['method']!='screen':continue
        direct=lookup[x['id'],'price'];case=C[x['id']];cats=collections.Counter(x.get('removal_categories',{}).values())
        screen.append(dict(id=x['id'],k=case['k'],N=case['n'],charge=x['id'].split('-c')[1].rsplit('-',1)[0],seed=case['seed'],removed=x.get('commands_removed',0),anchors=cats['possible_anchor'],wholly_ineligible=cats['wholly_ineligible'],ordinary=cats['ordinary'],direct_algorithm=direct['algorithm_seconds'],screen_algorithm=x['algorithm_seconds'],screen_stage=x.get('screen_seconds'),reduced_stage=x.get('reduced_seconds'),direct_total=direct['total_measured_seconds'],screen_total=x['total_measured_seconds'],total_ratio=x['total_measured_seconds']/direct['total_measured_seconds'],direct_nodes=direct.get('nodes'),reduced_nodes=x.get('downstream_nodes'),before_width=F(direct['gap']),after_width=F(x['gap']),direct_proof_bytes=direct['proof_bytes'],screen_proof_bytes=x['proof_bytes']))
    with (OUT/'SCREENING_END_TO_END.csv').open('w',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=list(screen[0]));writer.writeheader();writer.writerows(screen)
    summary=dict(timed_records=len(rows),primary_records=186,extension_records=39,status_counts=dict(collections.Counter(x['status'] for x in rows)),certificates=sum('certificate' in x for x in rows),primary_verification_timeouts=sum(x.get('verification_status')=='TIME_LIMIT' for x in rows),replay_passes=sum(x['replay_status']=='PASS' for x in replay.values()),completed_certificate_checks=sum(x.get('verification_status')=='PASS' for x in rows)+sum(x['replay_status']=='PASS' for x in replay.values()),screen_pairs=len(screen),screen_total_time_wins=sum(x['total_ratio']<1 for x in screen),median_screen_total_ratio=statistics.median(x['total_ratio'] for x in screen),maximum_price_denominator_bits=max(x.get('price_denominator_bits') or 0 for x in diag),maximum_price_numerator_bits=max(x.get('price_numerator_bits') or 0 for x in diag),maximum_tree_depth=max(x['maximum_depth'] or 0 for x in diag),maximum_oracle_calls=max(x['oracle_calls'] or 0 for x in diag),exact_reference_instances=len(reference))
    deficits=[x for x in rows if x['method']=='deficit' and x['status']=='TOLERANCE'];summary['deficit_completed']=len(deficits);summary['deficit_total']=30
    regret=[reference[x['instance_sha256']]-F(x['lower']) for x in deficits if x['instance_sha256'] in reference]
    summary['deficit_with_exact_reference']=len(regret);summary['deficit_max_actual_regret']=max(regret,default=F(0));summary['deficit_median_actual_regret']=statistics.median(regret) if regret else None
    exact_price=[x for x in rows if x['method']=='price' and x['family']=='exact_extension'];summary['exact_extension_price_success']=sum(x['status']=='EXACT' for x in exact_price);summary['exact_extension_price_runs']=len(exact_price)
    summary['maximum_verification_replay_seconds']=max((x['seconds'] for x in replay.values()),default=0);write(OUT/'SUMMARY.json',summary)
    tables=[]
    def start(cap,label,cols):
        tables.extend(['\\begin{table}[p]\\centering\\small',f'\\caption{{{cap}}}\\label{{{label}}}',f'\\begin{{tabular}}{{@{{}}{cols}@{{}}}}\\toprule'])
    def end(note):tables.extend(['\\bottomrule\\end{tabular}',f'\\par\\smallskip\\begin{{minipage}}{{\\textwidth}}\\footnotesize {note}\\end{{minipage}}','\\end{table}\\clearpage'])
    start('Matched positive-tolerance runs: median optimization seconds and successes out of three seeds.','tab:primary56','lrrcccc')
    tables.append('Family & $k,N,m$ & Limit & Price & Deficit & Enumeration & MIP \\\\ \\midrule')
    for family,dim in [('common-small','6,7,3'),('heterogeneous-small','8,9,3'),('heterogeneous-medium','24,17,4'),('heterogeneous-large','96,25,4')]:
        for limit in [.5,2.]:
            cells=[]
            for method in ['price','deficit','enumeration','direct-mip']:
                rr=[x for x in rows if x['family']==family and x['method']==method and C[x['id']]['seconds']==limit]
                good=sum(x['status'] in (['NUMERICAL'] if method=='direct-mip' else ['EXACT','TOLERANCE']) for x in rr)
                cells.append(f"{med(rr,'algorithm_seconds'):.3f} [{good}]")
            label={'common-small':'Common','heterogeneous-small':'Heterogeneous S','heterogeneous-medium':'Heterogeneous M','heterogeneous-large':'Heterogeneous L'}[family]
            tables.append(f'{label} & ${dim}$ & {limit:g} & '+' & '.join(cells)+r' \\')
    end('All price and deficit targets are $1/20$; enumeration requests exact completion. MIP entries count returned numerical results, not rational certificates. Limits are optimization seconds per fresh process. Setup, serialization and independent checking are measured separately. Verification timeouts and subsequent checks of unchanged certificate bytes are reported separately in the generated execution summary.')
    start('Exact-target extension: all nine models at the two-second optimization limit.','tab:exact56','rrrcrrrrr')
    tables.append('$k,N,m$ & Seed & Root gap & Nodes/calls & Depth & Books & Enum. $L$ & Price $V^*$ & Seconds \\\\ \\midrule')
    for case in cases:
        if case['family']!='exact_extension' or case['seconds']!=2:continue
        x=lookup[case['id'],'price'];d=diagmap[x['id']];mech=mechanics[x['id']]
        tables.append(f"${case['k']},{case['n']},{case['m']}$ & {case['seed']} & {sci(d['root_gap'])} & {x['nodes']}/{x['oracle_calls']} & {x['max_depth']} & {mech['unique_fixed_books']} & {float(F(mech['matched_enumeration_value'])):.4f} & {float(F(x['lower'])):.4f} & {x['algorithm_seconds']:.3f}"+r' \\')
    end('Root gap is the remaining rational gap after the root price attempts, before any split. Nodes are evaluated search nodes; calls are completed priced-path oracles. Books count distinct original fixed books in the untimed mechanical replay. Enumeration $L$ is the feasible value of lexicographic enumeration stopped at that same book count, not an equal-work or equal-time comparison. Every price result in this panel has zero rational final width and passes independent verification. The half-second counterparts and complete traces remain in the raw records.')
    start('Screening economics: medians over three seeds at the same two-second total optimization allowance.','tab:screen56','rrrccrrr')
    tables.append('$k,N$ & Charge & Removed & A/I/O & Direct total & Screen total & Ratio & Width change \\\\ \\midrule')
    for k,n in [(8,9),(24,17)]:
        for charge in ['0','1_100','1_10']:
            rr=[x for x in screen if x['k']==k and x['charge']==charge];cats='/'.join(str(sum(x[key] for x in rr)) for key in ['anchors','wholly_ineligible','ordinary'])
            tables.append(f"${k},{n}$ & {charge.replace('_','/')} & {med(rr,'removed'):g} & {cats} & {med(rr,'direct_total'):.3f} & {med(rr,'screen_total'):.3f} & {med(rr,'total_ratio'):.2f} & {sci(statistics.median(x['before_width'] for x in rr))}$\\to${sci(statistics.median(x['after_width'] for x in rr))}"+r' \\')
    end('Totals include optimization, serialization and independent checking, but not process setup. The screening allowance includes seed construction, forced bounds and reduced-catalog search; it is not added to a fresh full solve allowance. A/I/O are total removals across the three seeds: possible anchors, wholly ineligible commands, and ordinary nonanchors. Ratios are medians of paired total-time ratios. The number of actual paired time improvements is reported in the generated execution summary; a stronger bound is not itself a time saving.')
    start('Exact lattice results and explicit encoding limits.','tab:lattice56','rrrcrrr')
    tables.append('Cap-grid $H$ & Budget & Seeds & Exact & Median $Q$ & DP seconds & Enum. seconds \\\\ \\midrule')
    for H in [8,16,32]:
        for m in [2,4]:
            rr=[x for x in rows if x['method']=='lattice' and x['id'].startswith(f'lattice-H{H}-m{m}-')]
            ee=[lookup[x['id'],'enumeration'] for x in rr]
            tables.append(f"{H} & {m} & 3 & {sum(x['status']=='EXACT' for x in rr)}/3 & {med(rr,'grid_points'):g} & {med(rr,'algorithm_seconds'):.4f} & {med(ee,'algorithm_seconds'):.4f}"+r' \\')
    tables.append(r'\midrule \multicolumn{7}{l}{Post-inspection encoding stress: six histories, seven commands, budget two.} \\')
    for bit in [8,16,32]:
        x=lookup[f'encoding-H2power{bit}','lattice']
        tables.append(f"$2^{{{bit}}}$ & 2 & 1 & \\multicolumn{{2}}{{c}}{{{x['status'].replace('_',' ')}}} & {x['algorithm_seconds']:.4f} & ---"+r' \\')
    end('All lattice runs request exactly zero width; their comparator is exact book enumeration. $H$ describes the cap grid, while the implementation computes a common denominator for both cap and command components. The two larger stress grids exceeded the declared 600,000 Bellman-state allowance and return no optimality interval. Successful hexadecimal serialization does not remove this numerical-size barrier.')
    (GEN/'main_tables.tex').write_text('\n'.join(tables)+'\n')
    # A compact companion proof-cost table; every case remains in CSV/JSON.
    ec=['\\begin{table}[p]\\centering\\small\\caption{Exact-target certificate economics at the two-second limit.}\\label{tab:proof56}',r'\begin{tabular}{@{}rrrrrrr@{}}\toprule',r'$k,N$ & Seed & Check seconds & Raw bytes & Gzip bytes & Price bits & Final book \\ \midrule']
    for c in cases:
        if c['family']!='exact_extension' or c['seconds']!=2:continue
        x=lookup[c['id'],'price'];d=diagmap[x['id']]
        ec.append(f"${c['k']},{c['n']}$ & {c['seed']} & {x['verification_seconds']:.4f} & {x['proof_bytes']} & {x['compressed_proof_bytes']} & {d['price_numerator_bits']}/{d['price_denominator_bits']} & {d['incumbent_book_size']}"+r' \\')
    ec.extend([r'\bottomrule\end{tabular}',r'\par\smallskip\begin{minipage}{\textwidth}\footnotesize Both byte counts include the original input model, policy and full proof tree. Gzip uses deterministic zero timestamp; price bits report maxima of absolute numerator and positive denominator over retained leaf prices. Tested-price and distinct-book information is separately available in the mechanical replay.\end{minipage}',r'\end{table}\clearpage'])
    ec.extend([r'\begin{figure}[p]\centering',r'\includegraphics[width=\textwidth]{revisions/or-r58-structural-referee-20260926/generated/exact_trajectories.pdf}',r'\caption{Complete recorded exact-target price trajectories for the two eight-history instances requiring branching. Every recorded epoch is retained. The final circles denote zero rational width; elapsed times are those of the published two-second-limit runs, not the later mechanical replay.}\label{fig:trajectory56}',r'\end{figure}\clearpage'])
    (GEN/'ec_tables.tex').write_text('\n'.join(ec)+'\n')
    # Machine-readable statement numbers are collected after TeX compilation.
    print(json.dumps(encode_for_print(summary),indent=2))

def encode_for_print(z):
    from rational import encode
    return encode(z)
if __name__=='__main__':main()
