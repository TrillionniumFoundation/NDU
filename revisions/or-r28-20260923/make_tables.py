#!/usr/bin/env python3
from pathlib import Path
from fractions import Fraction as F
import json,statistics,sys
R=Path(__file__).resolve().parent
D=json.loads((R/'results/evidence.json').read_text()); replay=json.loads((R/'results/replay.json').read_text())
med=lambda values:statistics.median(values)
rows=[]
for c in D['scaling']:
    rr=c['records']; cfg=c['config']; B=c['blocks']
    phase={k:med([r[k]/1e6 for r in rr]) for k in ['coeff_ns','candidate_ns','audit_ns','cache_ns','witness_ns','refresh_ns','fresh_ns']}
    total=med([(r['coeff_ns']+r['candidate_ns']+r['audit_ns']+r['cache_ns']+r['witness_ns']+r['refresh_ns'])/1e6 for r in rr])
    fresh=med([(r['coeff_ns']+r['candidate_ns']+r['audit_ns']+r['fresh_ns'])/1e6 for r in rr])
    row=dict(n=c['n'],services=cfg['services'],d=cfg['d'],cache=cfg['cache'],unstable=cfg['unstable'],refresh=sum(r['refresh'] for r in rr),face_change_rate=sum(r['face_changes'] for r in rr)/(11*B),max_pre_error_per_block=max(float(F(r['pre_upper'])-F(r['reference']))/B for r in rr),max_used_error_per_block=max(float(F(r['used_upper'])-F(r['reference']))/B for r in rr),total_ms=total,fresh_total_ms=fresh,phase_medians_ms=phase,initial_ms=c['initial_ns']/1e6,cache_kib=max(r['cache_bytes'] for r in rr)/1024,peak_rss_mib=c['peak_process_rss_kib']/1024)
    rows.append(row)
summary=dict(rows=rows,queries=replay['counts']['queries'],refreshes=replay['counts']['refresh_queries'],maximum_certified_error_per_block=max(x['max_used_error_per_block'] for x in rows),minimum_adaptive_example_gain='9/1024')
paths={}
paths[R/'results/scaling_summary.json']=json.dumps(summary,indent=2,sort_keys=True)+'\n'
head=r'''\begin{table}[t]\centering\small
\caption{New exact-arithmetic scaling and cache governance. Each row has 12 queries; the tolerance is $10^{-3}$ per independent block. ``Changes'' is the fraction of block active-cap labels changing between successive queries. Total costs include coefficients, the same full-policy generator and audit, witness repair, cache evaluation, and any refresh. Fresh uses an exact specialized restricted solve. Memory is isolated-process peak resident memory; these are synthetic block-separable models, not dense-QP speed comparisons.}\label{tab:r28-scaling}
\begin{tabular}{rrrrrrrrr}\toprule
$n$ & Services & $d$ & Cache & Changes & Refresh & Cached total & Fresh total & Memory\\
 & & & & (\%) & /12 & (ms) & (ms) & (MiB)\\\midrule
'''
for r in rows:
    head+=f"{r['n']} & {r['services']} & {r['d']} & {r['cache']} & {100*r['face_change_rate']:.1f} & {r['refresh']} & {r['total_ms']:.2f} & {r['fresh_total_ms']:.2f} & {r['peak_rss_mib']:.1f} \\\\\n"
head+=r'\bottomrule\end{tabular}'+'\n'+r'\end{table}'+'\n'
paths[R/'scaling_table.tex']=head
ph=r'''\begin{center}\small
\begin{tabular}{rrrrrrrrr}\toprule
$n$ & Cache & Coefficients & Policy & Audit & Cache & Witness & Refresh & Fresh solve\\\midrule
'''
for r in rows:
    p=r['phase_medians_ms'];ph+=f"{r['n']} & {r['cache']} & "+' & '.join(f"{p[k]:.2f}" for k in ['coeff_ns','candidate_ns','audit_ns','cache_ns','witness_ns','refresh_ns','fresh_ns'])+r' \\'+'\n'
ph+=r'\bottomrule\end{tabular}'+'\n'+r'\end{center}'+'\n'
ph+=r'''\begin{center}\small
\begin{tabular}{rrrrrr}\toprule
$n$ & Cache & Initial build (ms) & Serialized cache (KiB) & Max. stale loss/block & Max. used loss/block\\\midrule
'''
for r in rows:
    ph+=f"{r['n']} & {r['cache']} & {r['initial_ms']:.2f} & {r['cache_kib']:.1f} & {r['max_pre_error_per_block']:.5f} & {r['max_used_error_per_block']:.7f} \\\\\n"
ph+=r'\bottomrule\end{tabular}\end{center}'+'\n'
paths[R/'phase_tables.tex']=ph
paths[R/'evidence_main.tex']=r'''\subsection{Shared restrictions, adaptive certificates, and refresh costs}
The new exact two-period checks reconstruct the optimized release policy, its local box maxima, normalized participation prices, shared-table stationarity, and recursive root plane at nine rational releases, including active-cap transitions. Exhaustive rational KKT-basis enumeration independently recovers the tree optimum. All 81 anchor/query release pairs satisfy the supporting-plane inequality. A separate two-plane shared-table master has value $3/8$. The declared adaptive policy in Proposition~\ref{prop:adaptiveuniform} passes its full-cell feasibility test and has uniform gain certificate $9/1024$. Fourteen deliberately invalid witnesses or certificates are rejected; these finite checks supplement, rather than replace, the proofs.

Table~\ref{tab:r28-scaling} varies decision dimension, service count, parameter dimension, cache size, and active-cap instability. The family is an explicit direct sum of two-period accepted-service blocks with shared child tiers, not a claim that a deep nonrecombining tree has been compressed for free. All generated quantities and audits use rational arithmetic. The same exact full-policy generator and its audit are charged to both pipelines. The fresh comparator is a specialized exact solve and meets a stronger zero-gap criterion within the common target; it is not an artificially expensive generic solver.

The strict tolerance triggers refresh on 83 of 84 queries. All post-governance comparator errors are within the declared target, but the cache pipeline is not faster in these measurements. This is useful adverse evidence: global validity alone does not imply that a cached price is economically tight or computationally beneficial. The full phase accounting and isolated-process memory are reported in EC Section~\ref{ec:r28-evidence}. Historical continuous-state approximation, full-tree comparisons, and unfavorable learning results follow unchanged and are not relabeled as new experiments.
\input{revisions/or-r28-20260923/scaling_table.tex}
'''
for path,text in paths.items():
    if '--check' in sys.argv: assert path.read_text()==text,str(path)
    else: path.write_text(text)
print(json.dumps(summary,indent=2))
