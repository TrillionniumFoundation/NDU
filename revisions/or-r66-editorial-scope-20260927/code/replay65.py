"""Parallel integrity replay against frozen external requests, never retiming the study."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import argparse,collections,gzip,hashlib,json,time
from rational import digest,F
from binding65 import make_request,bind_legacy,verify_request,ROBUST,TARIFF


def check_one(job):
    source,name,case=job;source=Path(source);p=source/'results/records'/name
    rec=json.loads(p.read_text());spec=case['spec']
    assert rec['instance_sha256']==digest(spec) and rec['parent_finished']
    row=dict(id=rec['id'],method=rec['method'],historical_status=rec['status'],
        historical_verification_status=rec.get('verification_status'),
        historical_rational_target_met=rec['rational_target_met'],
        record_file_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    if not rec.get('certificate'):return row
    raw=(source/'results'/rec['certificate']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==rec['certificate_sha256']
    cert=json.loads(gzip.decompress(raw));cls=rec['certificate_schema']
    # Class comes from the immutable execution record, tolerance/model from its
    # frozen case. Hybrid's robust guard is fixed by the frozen worker protocol.
    guard=None
    if cls in (ROBUST,TARIFF):
        if rec['method']=='hybrid':
            assert cls==ROBUST and rec['selected_route']=='robust_tariff_d_le_4'
            guard=4;guard_source='frozen hybrid protocol, worker61.py: max_exceptions=4'
        else:guard=case.get('guard',12);guard_source='frozen case guard (default 12)'
    else:guard_source='not applicable to this mathematical certificate class'
    request=make_request(spec,case['epsilon'],cls,guard)
    request['spec']=spec  # Retain the frozen request's raw rational notation.
    tick=time.perf_counter();answer=verify_request(bind_legacy(cert,request),request)
    row.update(current_replay=answer,replay_seconds=time.perf_counter()-tick,
        certificate_file_sha256=hashlib.sha256(raw).hexdigest(),external_request=request,
        external_request_sha256=digest(request),guard_source=guard_source,
        wrapper_created_at_replay=True)
    if cls==ROBUST:
        assert answer['transfer_formula_certified'] and answer['equal_gross_certified']
        assert answer['request_binding']['projection_tolerance_checked']
    if rec['rational_target_met']:
        assert answer['status']=='PASS' and rec['within_total_budget'] and answer['tolerance_met']
        assert F(rec['upper'])==F(answer['upper']) and F(rec['lower'])==F(answer['lower'])
    return row


def replay(source,output,workers=4):
    source=source.resolve();output=output.resolve()
    freeze=json.loads((source/'results/STUDY_FREEZE.json').read_text())
    for name,sha in freeze['source_hashes'].items():
        assert hashlib.sha256((source/'code'/name).read_bytes()).hexdigest()==sha,name
    cases={x['id']:x for x in freeze['cases']}
    files=sorted(p for p in (source/'results/records').glob('*.json') if not p.name.endswith('.check.json'))
    assert len(files)==freeze['declared_requests']==405
    jobs=[(str(source),p.name,cases[json.loads(p.read_text())['id']]) for p in files]
    output.mkdir(parents=True,exist_ok=True);counts=collections.Counter();seen=set();start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as pool, (output/'REQUEST_RECEIPTS65.jsonl').open('w') as stream:
        for i,row in enumerate(pool.map(check_one,jobs)):
            key=(row['id'],row['method']);assert key not in seen;seen.add(key);counts['requests']+=1
            if 'current_replay' not in row:counts['no_certificate']+=1
            else:
                ans=row['current_replay'];counts['certificates']+=1;counts[ans['status']]+=1
                counts['different_input_bytes']+=not ans['binding']['byte_identical']
                counts['request_bound_certificates']+=bool(ans['request_bound'])
                if ans['request_binding']['certificate_class']==ROBUST:counts['robust_transfer_and_request_bound']+=1
                if row['historical_verification_status'] not in ('PASS','PASS_LOWER_ONLY'):counts['newly_replayed_not_reclassified']+=1
            stream.write(json.dumps(row,sort_keys=True)+'\n');stream.flush()
            if i%25==0:print('REQUEST REPLAY',i+1,len(files),dict(counts),flush=True)
    result=dict(status='PASS',source_freeze_sha256=hashlib.sha256((source/'results/STUDY_FREEZE.json').read_bytes()).hexdigest(),
        **dict(counts),workers=workers,seconds=time.perf_counter()-start,
        scope='Post-study parallel integrity check against frozen requests; no original timing, failure, or target classification changed.')
    (output/'REQUEST_REPLAY65.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    replay(a.source,a.output,a.workers)
