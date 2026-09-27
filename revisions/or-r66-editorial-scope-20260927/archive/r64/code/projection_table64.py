"""Projection quality from immutable study records; never invokes an optimizer.

Exact comparator values may be integrity-checked after the study. Their original
checking/deadline status is retained separately; no target is reclassified.
"""
from pathlib import Path
import csv, gzip, hashlib, json
from rational import F
from binding63 import verify_bound
R=Path(__file__).resolve().parents[1]
S=R/'evidence/r61/results'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read_certificate(record):
    p=S/record['certificate']; raw=p.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==record['certificate_sha256']
    return json.loads(gzip.decompress(raw)),sha(p)

def generate():
    freeze=json.loads((S/'STUDY_FREEZE.json').read_text())
    cases={x['id']:x for x in freeze['cases']}
    allrows=list(csv.DictReader((S/'ALL_RUNS.csv').open()))
    selected=[x for x in allrows if x['family']=='adversarial' and x['method']=='robust']
    assert len(selected)==12
    out=[]
    for r in selected:
        name=r['id']; case=cases[name]; p=S/'records'/f'{name}--robust.json'
        rec=json.loads(p.read_text())
        row=dict(id=name,case='A'+name.split('-')[1]+'.'+name.split('-')[2],
            N=len(case['spec']['catalog']),epsilon=str(F(case['epsilon'])),
            original_status=rec['status'],original_timed_target=rec['rational_target_met'],
            original_verification_status=rec.get('verification_status'),
            optimization_seconds=rec.get('optimization_seconds'),
            original_check_seconds=rec.get('verification_seconds'),
            proof_bytes=rec.get('proof_bytes'),compressed_proof_bytes=rec.get('compressed_proof_bytes'),
            record_sha256=sha(p),projection=None,regret=None)
        if rec.get('certificate'):
            c,cs=read_certificate(rec);ans=verify_bound(c,case['spec'])
            assert ans['status']=='PASS'
            row['certificate_sha256']=cs
            row['projection']={k:ans[k] for k in ('selected_exception_budget','projected_exceptions',
                'tariff_exceptions','projection_standard_fee','tariff_standard_fee','projection_l1',
                'previous_projection_l1','minimum_allowance_certified')}
            row.update(E_plus=str(F(c['error_budget']['positive_budget'])),
                E_minus=str(F(c['error_budget']['negative_budget'])),
                lower=str(F(ans['lower'])),upper=str(F(ans['upper'])),
                interval_width=str(F(ans['upper'])-F(ans['lower'])))
            bestlo=F(ans['lower']);besthi=F(ans['upper']);comparators=[]
            for method in ('tariff','price','hybrid','enumeration'):
                q=S/'records'/f'{name}--{method}.json';other=json.loads(q.read_text())
                if not other.get('certificate'):continue
                cert,h=read_certificate(other);proof=verify_bound(cert,case['spec'])
                assert proof['status']=='PASS'
                bestlo=max(bestlo,F(proof['lower']));besthi=min(besthi,F(proof['upper']))
                comparators.append(dict(method=method,record_sha256=sha(q),certificate_sha256=h,
                    lower=str(F(proof['lower'])),upper=str(F(proof['upper'])),
                    original_status=other['status'],original_verification_status=other.get('verification_status'),
                    original_timed_target=other['rational_target_met']))
            assert bestlo<=besthi
            row['regret']={'lower':str(max(F(0),bestlo-F(ans['lower']))),
                'upper':str(besthi-F(ans['lower'])),'exact':bestlo==besthi,
                'comparators':comparators,'scope':'Post-study rational comparison, not original target attainment'}
        out.append(row)
    target=R/'results/r64';target.mkdir(parents=True,exist_ok=True)
    result={'schema':'NDU-R64-frozen-projection-table-v1','status':'PASS',
        'source_freeze_sha256':sha(S/'STUDY_FREEZE.json'),'source_csv_sha256':sha(S/'ALL_RUNS.csv'),
        'source_requests':405,'rows':out,'new_optimization_runs':0,
        'accounting':'All times, outcomes, and proof sizes are ORIGINAL recorded values; current checking is an integrity audit only.'}
    (target/'PROJECTION_QUALITY64.json').write_text(json.dumps(result,indent=2)+'\n')
    fields=['case','N','epsilon','allowance','projected_exceptions','tariff_exceptions','E_plus','E_minus',
        'interval_width','regret_lower','regret_upper','regret_exact','original_status','original_timed_target',
        'optimization_seconds','original_check_seconds','proof_bytes','compressed_proof_bytes']
    with (target/'PROJECTION_QUALITY64.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in out:
            x={k:r.get(k) for k in fields};p=r['projection'];g=r['regret']
            if p:x.update(allowance=p['selected_exception_budget'],projected_exceptions=p['projected_exceptions'],tariff_exceptions=p['tariff_exceptions'])
            if g:x.update(regret_lower=g['lower'],regret_upper=g['upper'],regret_exact=g['exact'])
            w.writerow(x)
    # Monetary columns below are exact integers in units of 10^{-5}.
    def scaled(v):
        q=F(v)*100000;assert q.denominator==1;return str(q.numerator)
    lines=[r'\begin{table}[p]\centering',
        r'\caption{Near-standard projection quality and original timed checking, all frozen adversarial requests}\label{tab:projection64}',
        r'\begin{singlespace}\small',r'\textbf{Panel A: fee distortion and original-policy value}\par\smallskip',
        r'\begin{tabular}{lrrrrrrrr}\toprule',
        r'Case & $N$ & $d_{\rm allow}$ & $d_{\rm proj}$ & $d_{\rm tariff}$ & $E_+$ & $E_-$ & Width & Regret\\\midrule']
    for r in out:
        p=r['projection'];g=r['regret']
        if p:
            regret=scaled(g['lower']) if g['exact'] else '$['+scaled(g['lower'])+','+scaled(g['upper'])+']$'
            values=[r['case'],str(r['N']),str(p['selected_exception_budget']),str(p['projected_exceptions']),str(p['tariff_exceptions']),scaled(r['E_plus']),scaled(r['E_minus']),scaled(r['interval_width']),regret]
            lines.append(' & '.join(values)+r' \\')
        else:
            label='Inapplicable' if r['original_status']=='MATHEMATICALLY_INAPPLICABLE' else 'Engineering guard'
            lines.append(f"{r['case']} & {r['N']} & \\multicolumn{{7}}{{l}}{{{label}; no interval or policy certificate}}"+r' \\')
    lines += [r'\bottomrule\end{tabular}\par\medskip',r'\textbf{Panel B: original execution and proof costs}\par\smallskip',
        r'\begin{tabular}{llrrrrr}\toprule',r'Case & Original outcome & Target & Optimize (s) & Check (s) & Bytes & Gzip bytes\\\midrule']
    for r in out:
        status={'MATHEMATICALLY_INAPPLICABLE':'Inapplicable','ENGINEERING_GUARD':'Guard','EXACT':'Exact','TOLERANCE':'Tolerance'}[r['original_status']]
        vals=[r['case'],status,'Yes' if r['original_timed_target'] else 'No',f"{r['optimization_seconds']:.4f}",
            '--' if r['original_check_seconds'] is None else f"{r['original_check_seconds']:.4f}",
            '--' if r['proof_bytes'] is None else f"{r['proof_bytes']:,}",
            '--' if r['compressed_proof_bytes'] is None else f"{r['compressed_proof_bytes']:,}"]
        lines.append(' & '.join(vals)+r' \\')
    lines += [r'\bottomrule\end{tabular}\par\smallskip',r'\begin{minipage}{\textwidth}\footnotesize',
        r'All requests use tolerance $\varepsilon=1/500$ and a six-second total allowance. Monetary entries in Panel A are in units of $10^{-5}$. Width is the original-fee upper bound minus the returned policy value; a regret interval is not an exact regret. Exact comparator proofs close the five reported zero regrets; the two bracketed entries remain bounds. The three exception counts have the meanings in Section~\ref{sec:robust-fees}. Cases A0--A5 respectively perturb fees, reduce the promise, introduce small dispersed deviations, combine curvature with service costs (two variants), and alternate fees; the suffix selects catalog size. All 12 requests, including four inapplicable requests and one guard, remain in the denominator.',
        r'Panel B reports original optimization/checking times and proof bytes, not later replay costs. Target attainment requires the original end-to-end deadline and original checker outcome. R63 external-input binding and R64 semantic checks are later integrity audits and do not promote a late or failed request. Exact comparators used only to identify regret retain their original timing outcomes in the machine-readable table. Dashes mean that no check or certificate was produced, not zero cost.',
        r'\end{minipage}\end{singlespace}\end{table}']
    (R/'generated/projection_quality64.tex').write_text('\n'.join(lines)+'\n')
    tails={key:max((int(r[key]) for r in allrows if r.get(key)),default=0) for key in ('proof_bytes','compressed_proof_bytes')}
    result_summary={'rows':len(out),'intervals':sum(x['projection'] is not None for x in out),
        'exact_regrets':sum(x['regret'] is not None and x['regret']['exact'] for x in out),
        'proof_size_maxima_across_405':tails}
    (target/'PROJECTION_SUMMARY64.json').write_text(json.dumps(result_summary,indent=2)+'\n');print(result_summary)
    return result
if __name__=='__main__':generate()
