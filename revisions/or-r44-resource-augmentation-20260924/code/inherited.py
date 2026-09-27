"""Replay inherited derivations without mutating their original files."""
from pathlib import Path
import tempfile,shutil,subprocess,sys,json,hashlib,os
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]
versions=['or-r33-piecewise-randomized-20260923','or-r34-global-randomized-frontier-20260923','or-r35-monge-frontier-20260923','or-r36-linear-frontier-20260924','or-r37-integrated-frontier-20260924','or-r38-contractual-quantization-20260924','or-r39-robust-quantizer-20260924','or-r42-certified-joint-design-20260924','or-r43-prefix-decomposition-20260924']
with tempfile.TemporaryDirectory(prefix='ndu-r44-regression-') as tmp:
    dest=Path(tmp)/'revisions'; dest.mkdir()
    for v in versions: shutil.copytree(ROOT/'revisions'/v,dest/v,ignore=shutil.ignore_patterns('*.pdf','__pycache__','transport','predecessor'))
    old=dest/versions[-1]; records={}
    for name in ('tests.py','inherited.py'):
        ans=subprocess.run([sys.executable,str(old/'code'/name)],capture_output=True,text=True,timeout=900)
        (R/'results'/('inherited-'+name+'.log')).write_text(ans.stdout+'\n'+ans.stderr)
        if ans.returncode: raise RuntimeError(name+': '+ans.stderr[-3000:])
    for name in ('verification.json','inherited.json'): records[name]=json.loads((old/'results'/name).read_text())
    script=old/'supplementary_audits/verify_general_class.py'
    if script.exists():
        env=dict(os.environ,R43_AUDIT_CONTEXT='R44 isolated replay',R43_AUDIT_OUTPUT=str(Path(tmp)/'general.json'))
        subprocess.run([sys.executable,str(script)],check=True,env=env,capture_output=True,text=True,timeout=600)
        records['general_class']=json.loads((Path(tmp)/'general.json').read_text())
    out=dict(status='PASS',executed='R43 + general-class audit + R42 + R39/R33-R37, disposable source hierarchy',records=records,source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for v in versions for p in (ROOT/'revisions'/v).rglob('*.py') if '__pycache__' not in str(p)})
    (R/'results/inherited.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Inherited R43 and R42 / R39 / R33--R37 replays PASS')
