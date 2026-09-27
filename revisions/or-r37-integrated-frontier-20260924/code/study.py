"""Same-input performance study with isolated processes and explicit limits.

Wall-time runs are unprofiled. Heap tracing and cProfile run separately.
Resident peaks are Linux ru_maxrss (KiB), including interpreter/input/output;
tracemalloc reports Python-tracked allocations, not native total memory.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from time import perf_counter
import argparse
import cProfile
import csv
import hashlib
import json
import os
import platform
import pstats
import resource
import subprocess
import sys
import tracemalloc
from frontier import instance, serial_solutions, solve, verify_solution

R = Path(__file__).resolve().parents[1]
OUT = R/'results'
OUT.mkdir(exist_ok=True)
ENGINES = ('divide', 'linear', 'pads')
INSTITUTIONS = ('expected', 'pathwise')
LIMIT = 120


def category(filename, function):
    if 'fractions.py' in filename or 'gcd' in function:
        return 'rational_arithmetic'
    if function in ('randomized_frontiers', 'deterministic_frontiers'):
        return 'frontier_scans_and_reconstruction_combined'
    if function in ('sums', 'edge', 'tail_polynomial', 'interval', 'cell', 'reward', 'value', '__init__'):
        return 'moment_and_economic_oracle_own_work'
    if ('linear_frontier.py' in filename or 'monge_frontier.py' in filename
            or 'pads_excerpt.py' in filename or function == 'pads_rows'):
        return 'matrix_search_and_key_bookkeeping_own_work'
    return 'other'


def worker(k, budget, institution, engine, mode, destination):
    if mode == 'memory':
        tracemalloc.start()
    begin = perf_counter()
    p = instance(k)
    input_seconds = perf_counter()-begin
    profiler = cProfile.Profile() if mode == 'profile' else None
    begin = perf_counter()
    if profiler:
        profiler.enable()
    ans, work = solve(p, budget, institution, engine)
    if profiler:
        profiler.disable()
    elapsed = perf_counter()-begin
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    current_heap = peak_heap = None
    if mode == 'memory':
        current_heap, peak_heap = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    # Capture performance/memory BEFORE validation and JSON serialization.
    for m, sol in enumerate(ans, 1):
        verify_solution(p, sol, m, institution)
    record = {'status': 'PASS', 'k': k, 'budget': budget,
              'institution': institution, 'engine': engine, 'mode': mode,
              'input_seconds': input_seconds, 'frontier_seconds': elapsed,
              'max_resident_kib_before_validation': rss,
              'python_heap_current_bytes': current_heap, 'python_heap_peak_bytes': peak_heap,
              'work': work, 'frontiers': serial_solutions(ans)}
    record['economic_queries'] = sum(work.get(name, 0) for name in
                                     ('tail_evaluations', 'edge_evaluations', 'cell_evaluations'))
    if profiler:
        stats = pstats.Stats(profiler)
        parts, functions = {}, []
        for (filename, line, function), (cc, nc, tt, ct, _) in stats.stats.items():
            group = category(filename, function)
            parts[group] = parts.get(group, 0.0)+tt
            functions.append({'file': Path(filename).name, 'line': line, 'function': function,
                              'primitive_calls': cc, 'total_calls': nc,
                              'exclusive_seconds': tt, 'inclusive_seconds': ct,
                              'category': group})
        record['profile_exclusive_categories'] = parts
        record['profile_functions'] = sorted(functions, key=lambda x: -x['exclusive_seconds'])
    destination.write_text(json.dumps(record, indent=2)+'\n')


def launch(k, institution, engine, mode):
    name = f'{mode}-{institution}-{engine}-{k}'
    destination = OUT/(name+'.json')
    command = [sys.executable, str(Path(__file__).resolve()), '--worker',
               '--k', str(k), '--institution', institution, '--engine', engine,
               '--mode', mode, '--output', str(destination)]
    begin = perf_counter()
    try:
        p = subprocess.run(command, text=True, capture_output=True, timeout=LIMIT,
                           env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    except subprocess.TimeoutExpired:
        record = {'status': 'TIME_LIMIT', 'k': k, 'budget': 8, 'institution': institution,
                  'engine': engine, 'mode': mode, 'process_limit_seconds': LIMIT,
                  'observed_process_seconds': perf_counter()-begin,
                  'frontier_seconds': None, 'frontiers': None}
        destination.write_text(json.dumps(record, indent=2)+'\n')
        print(name, 'TIME_LIMIT', flush=True)
        return record
    (OUT/(name+'.log')).write_text(p.stdout+'\n'+p.stderr)
    if p.returncode:
        raise RuntimeError(name+' failed, not a resource-limit observation; see log')
    record = json.loads(destination.read_text())
    record['process_seconds'] = perf_counter()-begin
    print(name, 'PASS', round(record['frontier_seconds'], 4), flush=True)
    return record


def study():
    records = []
    for k in (256, 4096, 16384):
        for institution in INSTITUTIONS:
            for engine in ENGINES:
                records.append(launch(k, institution, engine, 'time'))
    for institution in INSTITUTIONS:
        for engine in ENGINES:
            records.append(launch(1024, institution, engine, 'memory'))
            records.append(launch(512, institution, engine, 'profile'))
    checks = 0
    groups = {}
    for record in records:
        if record['status'] != 'PASS':
            continue
        key = (record['k'], record['institution'], record['mode'])
        losses = [s['loss'] for s in record['frontiers']]
        if key in groups:
            assert losses == groups[key]
            checks += len(losses)
        else:
            groups[key] = losses
    with (OUT/'scaling.csv').open('w', newline='') as handle:
        columns = ['k', 'institution', 'engine', 'status', 'frontier_seconds',
                   'economic_queries', 'max_resident_kib_before_validation']
        writer = csv.DictWriter(handle, columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(r for r in records if r['mode'] == 'time')
    data = {'status': 'PASS_WITH_RECORDED_LIMITS' if any(r['status'] == 'TIME_LIMIT' for r in records) else 'PASS',
            'platform': platform.platform(), 'python': sys.version,
            'same_input_exact_frontier_equalities': checks,
            'per_process_limit_seconds': LIMIT, 'records': records,
            'source_sha256': {str(p.relative_to(R)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (R/'code').rglob('*.py')},
            'interpretation': 'Unprofiled time includes rational frontier computation and all-budget reconstruction, excludes input construction and replay. RSS includes process baseline; Python heap is measured separately starting before input creation. Profiled runs are not timing comparisons. Scans and reconstruction are combined, not falsely isolated. Shared moment oracles limit algorithmic independence; PADS supplies independently authored search. No calibration or optimized native-search speed claim.'}
    (OUT/'study.json').write_text(json.dumps(data, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--k', type=int, default=256)
    parser.add_argument('--budget', type=int, default=8)
    parser.add_argument('--institution', choices=INSTITUTIONS, default='expected')
    parser.add_argument('--engine', choices=ENGINES, default='linear')
    parser.add_argument('--mode', choices=('time', 'memory', 'profile'), default='time')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        if args.output is None:
            parser.error('--worker requires --output')
        worker(args.k, args.budget, args.institution, args.engine, args.mode, args.output)
    else:
        study()
