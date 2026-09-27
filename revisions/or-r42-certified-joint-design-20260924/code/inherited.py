"""Replay predecessor verification in a disposable hierarchy only."""
from pathlib import Path
import tempfile, shutil, subprocess, sys, json, hashlib
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]
versions=['or-r33-piecewise-randomized-20260923','or-r34-global-randomized-frontier-20260923','or-r35-monge-frontier-20260923','or-r36-linear-frontier-20260924','or-r37-integrated-frontier-20260924','or-r38-contractual-quantization-20260924','or-r39-robust-quantizer-20260924']
with tempfile.TemporaryDirectory(prefix='ndu-r42-regression-') as temp:
    dest=Path(temp)/'revisions'; dest.mkdir()
    for v in versions:
        shutil.copytree(ROOT/'revisions'/v,dest/v,ignore=shutil.ignore_patterns('__pycache__','*.pdf'))
    old=dest/versions[-1]
    for name in ('verify.py','verify_allocation.py','inherited.py'):
        result=subprocess.run([sys.executable,str(old/'code'/name)],capture_output=True,text=True,timeout=900)
        (R/'results'/('inherited-'+name+'.log')).write_text(result.stdout+'\n'+result.stderr)
        if result.returncode:raise RuntimeError(name+': '+result.stderr[-2000:])
    records={name:json.loads((old/'results'/name).read_text()) for name in ('verification.json','allocation_validation.json','inherited.json')}
    assert all(v['status']=='PASS' for v in records.values())
    out={'status':'PASS','suites':'R39 exact catalog and allocation plus isolated R33--R37 regressions','records':records,'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for v in versions for p in (ROOT/'revisions'/v).rglob('*.py') if '__pycache__' not in str(p)}}
    (R/'results/inherited.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Inherited R39 and R33--R37 exact suites PASS',flush=True)
