"""Re-run the unchanged R33 exact tests without changing inherited records."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parent
OLD=R.parent/'or-r33-piecewise-randomized-20260923'
with tempfile.TemporaryDirectory(prefix='ndu-r34-inherited-') as tmp:
 t=Path(tmp)
 hashes={}
 for name in ('exact_compiler.py','verify.py'):
  source=OLD/name;hashes[name]=hashlib.sha256(source.read_bytes()).hexdigest()
  shutil.copy2(source,t/name)
 p=subprocess.run([sys.executable,str(t/'verify.py')],text=True,capture_output=True)
 if p.returncode:
  print(p.stdout);print(p.stderr);raise RuntimeError('Inherited verification failed')
 result=json.loads((t/'verification.json').read_text())
 assert result['status']=='PASS'
 record={'status':'PASS','base_commit':'38b3f264e371758054d94a9f94088ae17a816241',
         'unchanged_script_sha256':hashes,'rerun':result,
         'note':'Executed from a temporary directory; inherited evidence files were not overwritten.'}
 (R/'inherited_verification.json').write_text(json.dumps(record,indent=2)+'\n')
 print(p.stdout)
