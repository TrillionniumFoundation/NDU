"""Reproduce the frozen protocol, not a selected subset, on the publication host."""
from pathlib import Path
import subprocess,sys,json,hashlib,platform,os
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
if sys.flags.optimize:raise RuntimeError('Verification requires Python assertions enabled')
def run():
    for script,args in [('tests.py',[]),('study.py',['--phase','all']),('readers.py',[])]:
        subprocess.run([sys.executable,str(R/'code'/script),*args],cwd=ROOT,check=True)
    old=ROOT/'revisions/or-r49-dispersion-certificates-20260925/code/tests.py'
    target=old.parents[1]/'results/TESTS.json';before=target.read_bytes()
    z=subprocess.run([sys.executable,str(old)],cwd=ROOT,capture_output=True,text=True)
    (R/'results/antecedent_regression.log.txt').write_text(z.stdout+z.stderr)
    # The inherited test writes a deterministic record; preserve the old blob regardless.
    result=json.loads(target.read_text());target.write_bytes(before)
    if z.returncode:raise RuntimeError('Antecedent regression failed')
    (R/'results/ANTECEDENT_REGRESSION.json').write_text(json.dumps(dict(status='PASS',counts=result),indent=2)+'\n')
    env=dict(python=sys.version,platform=platform.platform(),source_files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'code').glob('*.py')},protocol_sha256=hashlib.sha256((R/'PROTOCOL.json').read_bytes()).hexdigest())
    (R/'results/ENVIRONMENT.json').write_text(json.dumps(env,indent=2)+'\n')
if __name__=='__main__':run()
