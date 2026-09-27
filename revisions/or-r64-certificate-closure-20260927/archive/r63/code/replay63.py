"""Replay frozen historical evidence without changing any timing outcome."""
from pathlib import Path
import argparse, collections, gzip, hashlib, json, time, sys
from rational import digest, F
from binding63 import verify_bound

def replay(source: Path, output: Path):
    freeze = json.loads((source/'results/STUDY_FREEZE.json').read_text())
    for name, sha in freeze['source_hashes'].items():
        assert hashlib.sha256((source/'code'/name).read_bytes()).hexdigest()==sha, name
    cases={x['id']:x for x in freeze['cases']}
    files=sorted(p for p in (source/'results/records').glob('*.json') if not p.name.endswith('.check.json'))
    assert len(files)==freeze['declared_requests']
    output.mkdir(parents=True,exist_ok=True)
    counts=collections.Counter();seen=set();begin=time.perf_counter()
    with (output/'BINDING_RECEIPTS.jsonl').open('w') as stream:
        for i,p in enumerate(files):
            rec=json.loads(p.read_text());key=(rec['id'],rec['method']);assert key not in seen;seen.add(key)
            case=cases[rec['id']];spec=case['spec'];assert rec['instance_sha256']==digest(spec) and rec['parent_finished']
            counts['requests']+=1
            row={'id':rec['id'],'method':rec['method'],'historical_status':rec['status'],
                 'historical_verification_status':rec.get('verification_status'),
                 'historical_rational_target_met':rec['rational_target_met'],
                 'record_file_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            if rec.get('certificate'):
                raw=(source/'results'/rec['certificate']).read_bytes()
                assert hashlib.sha256(raw).hexdigest()==rec['certificate_sha256']
                cert=json.loads(gzip.decompress(raw));tick=time.perf_counter()
                ans=verify_bound(cert,spec)
                row.update(current_replay=ans,replay_seconds=time.perf_counter()-tick,
                           certificate_file_sha256=hashlib.sha256(raw).hexdigest())
                counts['certificates']+=1;counts[ans['status']]+=1
                counts['different_input_bytes']+=not ans['binding']['byte_identical']
                if rec.get('verification_status') not in ('PASS','PASS_LOWER_ONLY'):
                    counts['newly_replayed_not_reclassified']+=1
                if rec['rational_target_met']:
                    assert ans['status']=='PASS' and rec['within_total_budget']
                    assert F(rec['upper'])==F(ans['upper']) and F(rec['lower'])==F(ans['lower'])
                    assert F(ans['upper'])-F(ans['lower'])<=F(case['epsilon'])
            else: counts['no_certificate']+=1
            stream.write(json.dumps(row,sort_keys=True)+'\n');stream.flush()
            if i%25==0:print('REPLAY',i+1,len(files),dict(counts),flush=True)
    answer={'status':'PASS','source_freeze_sha256':hashlib.sha256((source/'results/STUDY_FREEZE.json').read_bytes()).hexdigest(),
            **dict(counts),'seconds':time.perf_counter()-begin,
            'scope':'Exact source hashes, external-input rational equivalence, independent mathematical checks; historical timing and failure classifications unchanged.'}
    (output/'BINDING_REPLAY.json').write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps(answer),flush=True)
    return answer
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();replay(a.source,a.output)
