"""Run unchanged R33--R35 exact suites without overwriting historical evidence."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parent
folders=['or-r33-piecewise-randomized-20260923','or-r34-global-randomized-frontier-20260923','or-r35-monge-frontier-20260923']
record={'status':'PASS','base_commit':'7e49851cd04f0f7e015c2561b43a4e7591574e67','suites':{}}
with tempfile.TemporaryDirectory(prefix='ndu-r36-inherited-') as tmp:
    dest=Path(tmp)/'revisions';dest.mkdir()
    for folder in folders:
        (dest/folder).mkdir()
        for source in (R.parent/folder).glob('*.py'):
            shutil.copy2(source,dest/folder/source.name)
    for version,folder in zip(('R33','R34','R35'),folders):
        hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R.parent/folder).glob('*.py')}
        p=subprocess.run([sys.executable,str(dest/folder/'verify.py')],text=True,capture_output=True,timeout=600)
        if p.returncode:
            print(p.stdout);print(p.stderr);raise RuntimeError(f'{version} suite failed')
        result=json.loads((dest/folder/'verification.json').read_text());assert result['status']=='PASS'
        record['suites'][version]={'status':'PASS','unchanged_script_sha256':hashes,'rerun':result}
        print(version,'PASS',flush=True)
record['note']='Unmodified inherited source suites executed in an isolated directory. Historical result files are unchanged. These are inherited regression checks, not newly independent evidence.'
(R/'inherited_verification.json').write_text(json.dumps(record,indent=2)+'\n')
