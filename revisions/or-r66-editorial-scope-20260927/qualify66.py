"""Execute R66 editorial and retained mathematical qualification without retiming the study."""
from pathlib import Path
import hashlib,json,platform,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parent;O=R/'results/r66';O.mkdir(parents=True,exist_ok=True);records=[]
def run(name,args,cwd=R):
    start=time.perf_counter();p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,errors='replace')
    log=O/(name+'.log');log.write_text(p.stdout+p.stderr)
    records.append(dict(name=name,command=args,exit_code=p.returncode,seconds=time.perf_counter()-start,
        log=log.relative_to(R).as_posix(),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
    if p.returncode:raise RuntimeError(name+'\n'+p.stdout[-3000:]+p.stderr[-3000:])
    print(name,'PASS',flush=True)
def qualify():
    from verify66 import invariants,verify
    invariants()
    sources=list((R/'code').glob('*.py'))+list(R.glob('*66.py'))+[R/x for x in
        ('main.tex','electronic_companion.tex','RESPONSE_TO_REFEREES.tex','requirements.txt','README.md',
         'CONTENT_MAP.md','PROVENANCE66.json','EDITORIAL_SCOPE66.md','EDITORIAL_DIFF66.patch',
         'REQUEST_CONTRACT65.md','GOVERNING_REFEREE_REPORT_R65.md')]
    freeze=dict(schema='NDU-R66-source-freeze-v1',source_hashes={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(sources))},
        scope='Current editorial readers and executed sources; accepted code and all original evidence unchanged')
    (O/'SOURCE_FREEZE66.json').write_text(json.dumps(freeze,indent=2)+'\n')
    run('receipt_scope',[sys.executable,'tests66.py'])
    run('request_transfer',[sys.executable,'code/tests65.py','--output',str(O/'request')])
    run('retained_semantics',[sys.executable,'code/tests64.py','--output',str(O/'semantic')])
    with tempfile.TemporaryDirectory(prefix='ndu-r66-regressions-') as td:
        t=Path(td);shutil.copytree(R/'code',t/'code',ignore=shutil.ignore_patterns('__pycache__'));(t/'results').mkdir()
        run('structural60',[sys.executable,'code/tests60.py','--output',str(O/'STRUCTURAL60_REPLAY.json')],t)
        run('structural61',[sys.executable,'code/tests61.py','--output',str(O/'STRUCTURAL61_REPLAY.json')],t)
        run('physical_binding',[sys.executable,'code/tests63.py'],t)
        shutil.copy2(t/'results/BINDING_TESTS63.json',O/'BINDING_TESTS63.json')
        shutil.copy2(t/'results/DECISION_FRONTIERS.json',O/'DECISION_FRONTIERS_REPLAY.json')
    run('compile',[sys.executable,'compile66.py'])
    run('frozen_request_replay',[sys.executable,'code/replay65.py','evidence/r61',str(O/'replay')])
    check=verify(manifest=False)
    out=dict(schema='NDU-R66-executed-qualification-v1',status='PASS',python=sys.version,platform=platform.platform(),commands=records,
        read_only_check=check,source_freeze_sha256=hashlib.sha256((O/'SOURCE_FREEZE66.json').read_bytes()).hexdigest(),
        scope='Executed editorial, receipt-scope, retained regressions, PDF builds and integrity replay; no new optimization study or historical reclassification')
    (O/'QUALIFICATION66.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':qualify()
