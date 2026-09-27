"""Replay R44 recovery/strict-gap regression in an isolated source hierarchy."""
from pathlib import Path
import tempfile,shutil,subprocess,sys,json,hashlib
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
versions=['or-r33-piecewise-randomized-20260923','or-r34-global-randomized-frontier-20260923',
'or-r35-monge-frontier-20260923','or-r36-linear-frontier-20260924','or-r37-integrated-frontier-20260924',
'or-r38-contractual-quantization-20260924','or-r39-robust-quantizer-20260924',
'or-r42-certified-joint-design-20260924','or-r43-prefix-decomposition-20260924',
'or-r44-resource-augmentation-20260924']
with tempfile.TemporaryDirectory(prefix='ndu-r45-inherited-') as tmp:
    dst=Path(tmp)/'revisions';dst.mkdir()
    for v in versions:
        shutil.copytree(ROOT/'revisions'/v,dst/v,ignore=shutil.ignore_patterns('*.pdf','__pycache__','transport','predecessor'))
    old=dst/versions[-1]
    ans=subprocess.run([sys.executable,str(old/'code/tests.py')],capture_output=True,text=True,timeout=900)
    (R/'results/inherited-r44.log').write_text(ans.stdout+'\n'+ans.stderr)
    if ans.returncode:raise RuntimeError(ans.stderr[-4000:])
    record=json.loads((old/'results/verification.json').read_text())
    assert record['status']=='PASS' and record['exhaustive_comparisons']==144
    out=dict(status='PASS',scope='new execution of R44 exact recovery and strict-gap regression only; older suites retain their archived execution records',record=record,
        source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for v in versions for p in (ROOT/'revisions'/v).rglob('*.py') if '__pycache__' not in str(p)})
    (R/'results/inherited.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Isolated R44 regression PASS; all original paths untouched.')
