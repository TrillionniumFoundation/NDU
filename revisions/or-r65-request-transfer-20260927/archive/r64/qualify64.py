"""Execute validation without replacing any historical study observation."""
from pathlib import Path
import hashlib,json,os,platform,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parent
O=R/'results/r64';O.mkdir(parents=True,exist_ok=True)
records=[]
def run(name,args,cwd=R):
    start=time.perf_counter();p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,errors='replace')
    log=O/(name+'.log');log.write_text(p.stdout+p.stderr)
    records.append({'name':name,'command':args,'exit_code':p.returncode,'seconds':time.perf_counter()-start,
        'log':str(log.relative_to(R)),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
    if p.returncode:raise RuntimeError(name+'\n'+p.stdout[-2000:]+p.stderr[-2000:])
    print(name,'PASS',flush=True)

def qualify():
    run('frozen_projection_table',[sys.executable,'code/projection_table64.py'])
    run('reader_revision',[sys.executable,'revise64.py'])
    sources=list((R/'code').glob('*.py'))+list(R.glob('*64.py'))+list((R/'sections/r64').glob('*.tex'))
    sources += [R/x for x in ('main.tex','electronic_companion.tex','RESPONSE_TO_REFEREES.tex','requirements.txt','generated/projection_quality64.tex')]
    freeze={'schema':'NDU-R64-source-freeze-v1','source_hashes':{p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(sources))},
        'scope':'Current sources before validation; frozen R63/R61 sources and timings remain separate'}
    (O/'SOURCE_FREEZE64.json').write_text(json.dumps(freeze,indent=2)+'\n')
    run('semantic_regressions',[sys.executable,'code/tests64.py'])
    with tempfile.TemporaryDirectory(prefix='ndu-r64-structural-') as td:
        t=Path(td);shutil.copytree(R/'code',t/'code',ignore=shutil.ignore_patterns('__pycache__'));(t/'results').mkdir()
        run('structural60',[sys.executable,'code/tests60.py','--output',str(O/'STRUCTURAL60_REPLAY.json')],t)
        run('structural61',[sys.executable,'code/tests61.py','--output',str(O/'STRUCTURAL61_REPLAY.json')],t)
        run('binding_regressions',[sys.executable,'code/tests63.py'],t)
        shutil.copy2(t/'results/BINDING_TESTS63.json',O/'BINDING_TESTS63.json')
        shutil.copy2(t/'results/DECISION_FRONTIERS.json',O/'DECISION_FRONTIERS_REPLAY.json')
    run('compile',[sys.executable,'compile64.py'])
    run('full_replay',[sys.executable,'code/replay63.py','evidence/r61','results/r64/replay'])
    from verify64 import verify
    start=time.perf_counter();check=verify(manifest=False)
    result={'schema':'NDU-R64-executed-qualification-v1','status':'PASS','python':sys.version,
        'platform':platform.platform(),'commands':records,'read_only_check':check,
        'read_only_check_seconds':time.perf_counter()-start,
        'source_freeze_sha256':hashlib.sha256((O/'SOURCE_FREEZE64.json').read_bytes()).hexdigest(),
        'scope':'Executed current-source checks; historical study source, records, failures and timing classifications unchanged'}
    (O/'QUALIFICATION64.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':qualify()
