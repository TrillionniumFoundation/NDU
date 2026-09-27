"""Run preceding exact suites without changing any historical repository output."""
from pathlib import Path
import tempfile, shutil, subprocess, sys, json, hashlib
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]
versions=['or-r33-piecewise-randomized-20260923','or-r34-global-randomized-frontier-20260923',
          'or-r35-monge-frontier-20260923','or-r36-linear-frontier-20260924',
          'or-r37-integrated-frontier-20260924']
with tempfile.TemporaryDirectory(prefix='ndu-r38-regression-') as temp:
    dest=Path(temp)/'revisions'; dest.mkdir()
    for v in versions:
        shutil.copytree(ROOT/'revisions'/v,dest/v,ignore=shutil.ignore_patterns('__pycache__','*.pdf'))
    script=dest/versions[-1]/'code/test_revision.py'
    run=subprocess.run([sys.executable,str(script)],capture_output=True,text=True,timeout=600)
    (R/'results/inherited.log').write_text(run.stdout+'\n'+run.stderr)
    if run.returncode: raise RuntimeError('Inherited suite failed: '+run.stderr[-2000:])
    result=json.loads((dest/versions[-1]/'results/verification.json').read_text())
    assert result['status']=='PASS'
    record=dict(status='PASS',suite='R37 plus its unchanged R33--R36 subprocess regressions',
                result=result,source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for v in versions for p in (ROOT/'revisions'/v).rglob('*.py') if '__pycache__' not in str(p)})
    (R/'results/inherited.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Inherited R33--R37 suites PASS')
