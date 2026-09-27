"""Render executed evidence into manuscript tables; never fill missing runs."""
from pathlib import Path
import json

R = Path(__file__).resolve().parents[1]
G = R/'generated'
G.mkdir(exist_ok=True)
SEARCH = {'divide': 'Divide-conquer', 'linear': 'SMAWK', 'pads': 'PADS'}
INST = {'expected': 'Expected', 'pathwise': 'Pathwise'}


def load(name):
    value = json.loads((R/'results'/name).read_text())
    if value['status'] not in ('PASS', 'PASS_WITH_RECORDED_LIMITS'):
        raise RuntimeError('Evidence is not validated: '+name)
    return value


def seconds(t):
    if t is None:
        return 'Not completed'
    return r'$<0.0001$' if 0 < t < .0001 else f'{t:.4f}'


def longtable(caption, label, layout, headings, rows, note=''):
    head = ' & '.join(headings)+r' \\'+'\n'
    text = ('\\begin{longtable}{'+layout+'}\n\\caption{'+caption+'}\\label{'+label+r'}\\'+'\n'
            +r'\toprule'+'\n'+head+r'\midrule'+'\n'+r'\endfirsthead'+'\n'
            +r'\toprule'+'\n'+head+r'\midrule'+'\n'+r'\endhead'+'\n'
            +r'\bottomrule'+'\n'+r'\endfoot'+'\n')
    text += '\n'.join(' & '.join(map(str, row))+r' \\' for row in rows)
    text += '\n'+r'\end{longtable}'+'\n'
    if note:
        text += '\\noindent '+note+'\n\n'
    return text


def generate():
    verification, study, external = (load('verification.json'), load('study.json'), load('external_solver.json'))
    counts = verification['counts']
    paragraph = (f"The executed suite checks {counts['completed_matrices']:,} completed matrices and "
                 f"{counts['all_selected_submatrix_row_minima']:,} selected-submatrix row minima, including "
                 f"{counts['padded_selected_rows']:,} wholly padded selected rows. It records "
                 f"{counts['frontier_equalities']:,} exact frontier equalities and direct controller replays, "
                 f"{counts['bounded_all_pairs_equalities']:,} bounded-overrun all-pairs equalities, and "
                 f"{counts['risk_frontier_equalities']:,} evaluations of the solved tolerance frontier. "
                 "The unchanged R33--R36 suites also pass in isolated directories. "
                 f"All {len(external['records'])} independently assembled HiGHS cases yield an exactly certified "
                 "reduced-network optimum and a matching controller.\n")
    (G/'verification_summary.tex').write_text(paragraph)
    timed = [r for r in study['records'] if r['mode'] == 'time']
    perf = []
    comparisons = []
    for institution in ('expected', 'pathwise'):
        common = []
        for k in sorted({r['k'] for r in timed}):
            group = {r['engine']: r for r in timed if r['k'] == k and r['institution'] == institution and r['status'] == 'PASS'}
            if 'linear' in group and 'divide' in group:
                common.append((k, group['linear'], group['divide']))
                comparisons.append(group['linear']['frontier_seconds'] > group['divide']['frontier_seconds'])
        if common:
            k, a, b = common[-1]
            ratio = a['frontier_seconds']/b['frontier_seconds']
            perf.append(f"At the largest completed common size for {institution} participation, "
                        f"{k:,} branches, the retained SMAWK implementation takes {a['frontier_seconds']:.3f} seconds "
                        f"against {b['frontier_seconds']:.3f} for divide-and-conquer, a time ratio of {ratio:.3f}. ")
    if comparisons:
        perf.append(f"Across the {len(comparisons)} completed same-size comparisons, SMAWK is slower in "
                    f"{sum(comparisons)}. These are observations on one runner and one input family, "
                    "not a uniform speedup claim. ")
    limits = sum(r['status'] == 'TIME_LIMIT' for r in study['records'])
    perf.append((f"The study records {limits} process-limit observations; they remain visible in the data."
                 if limits else "No configured study case exceeded the stated process limit.")+"\n")
    (G/'performance_summary.tex').write_text(''.join(perf))
    rows = []
    for r in timed:
        done = r['status'] == 'PASS'
        rows.append([INST[r['institution']], f"{r['k']:,}", SEARCH[r['engine']],
                     seconds(r.get('frontier_seconds')) if done else 'Limit',
                     f"{r['economic_queries']:,}" if done else '--',
                     f"{r['max_resident_kib_before_validation']/1024:.1f}" if done else '--'])
    tables = longtable('Same-input unprofiled frontier measurements; budgets one through eight.',
                       'tab:r37-scale', '@{}lrlrrr@{}',
                       ['Institution', 'Branches', 'Search', 'Seconds', 'Requests', 'Resident MiB'], rows,
                       'Requests count finite economic-oracle evaluations, including reevaluations. Resident memory is the process peak before validation and includes its baseline. A limit denotes the 120-second whole-process limit, not a measured frontier time.')
    rows = []
    for r in external['records']:
        if r['budget'] != 8:
            continue
        rows.append([INST[r['institution']], r['k'], f"{r['arcs']:,}",
                     seconds(r['construction_seconds']), seconds(r['highs_seconds']),
                     seconds(r['exact_reprice_replay_and_frontier_seconds'])])
    tables += '\n\\clearpage\n'+longtable('External compiled solver on independently assembled reduced networks; eight-symbol budget.',
                       'tab:r37-solver', '@{}lrrrrr@{}',
                       ['Institution', 'Branches', 'Arcs', 'Construction', 'Solver', 'Certification'], rows,
                       'All times are seconds. Certification includes exact repricing, rational shortest-path potentials, controller replay, and comparison with the exact frontier. The machine-readable record also includes budgets two and four. Solver time excludes network construction and certification.')
    (G/'main_tables.tex').write_text(tables)
    memory = []
    for r in study['records']:
        if r['mode'] != 'memory':
            continue
        done = r['status'] == 'PASS'
        memory.append([INST[r['institution']], SEARCH[r['engine']],
                       f"{r['python_heap_current_bytes']/1048576:.2f}" if done else '--',
                       f"{r['python_heap_peak_bytes']/1048576:.2f}" if done else '--',
                       f"{r['max_resident_kib_before_validation']/1024:.1f}" if done else '--'])
    ec = longtable('Separate memory runs at 1,024 branches and budgets one through eight; mebibytes.',
                   'tab:r37-memory', '@{}llrrr@{}',
                   ['Institution', 'Search', 'Current heap', 'Peak heap', 'Resident peak'], memory,
                   'Tracing starts before input creation and stops before validation. Heap fields are Python-tracked allocations; resident peaks include the process baseline and native allocations. Traced runtimes are not used as the unprofiled comparison.')
    profile = []
    keys = ['rational_arithmetic', 'moment_and_economic_oracle_own_work',
            'matrix_search_and_key_bookkeeping_own_work', 'frontier_scans_and_reconstruction_combined', 'other']
    for r in study['records']:
        if r['mode'] != 'profile':
            continue
        if r['status'] != 'PASS':
            profile.append([INST[r['institution']], SEARCH[r['engine']], *(['--']*5)])
            continue
        groups = r['profile_exclusive_categories']
        total = sum(groups.values())
        profile.append([INST[r['institution']], SEARCH[r['engine']],
                        *[f'{100*groups.get(key, 0)/total:.1f}' for key in keys]])
    ec += '\n\\clearpage\n'+longtable('Exclusive-time decomposition in separate 512-branch profile runs; percentages.',
                   'tab:r37-profile', '@{}llrrrrr@{}',
                   ['Institution', 'Search', 'Arithmetic', 'Oracle', 'Search', 'Outer', 'Other'], profile,
                   'Arithmetic includes reduced-fraction operations and gcd. Oracle and search columns count their own exclusive work, not child arithmetic again. Outer combines frontier scans and reconstruction. Percentages use exclusive profile time and are not percentages of unprofiled wall time; rounding can prevent an exact sum of 100.')
    (G/'companion_tables.tex').write_text(ec)
    report = ('\\section*{Executed evidence}\n'+paragraph+'\n\n'+''.join(perf)
              +'\nThe machine-readable evidence is in the current results directory. The current build manifest records the exact scientific source commit, PDF hashes, page counts, and base-tree preservation audit.\n')
    (G/'response_results.tex').write_text(report)
    summary = {'verification_counts': counts, 'external_solver_cases': len(external['records']),
               'study_status': study['status'], 'process_limit_observations': limits,
               'completed_timing_comparisons': len(comparisons), 'linear_slower_cases': sum(comparisons)}
    (G/'EVIDENCE_SUMMARY.json').write_text(json.dumps(summary, indent=2)+'\n')


if __name__ == '__main__':
    generate()
