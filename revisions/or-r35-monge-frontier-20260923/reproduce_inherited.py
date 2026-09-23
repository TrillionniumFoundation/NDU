"""Re-run unmodified R33 and R34 suites in isolation, preserving their records."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parent
record={'status':'PASS','base_commit':'fbfdf24b370201c810425f633f5fc06048282b5c','suites':{}}
for version,folder,names in [
 ('R33','or-r33-piecewise-randomized-20260923',('exact_compiler.py','verify.py')),
 ('R34','or-r34-global-randomized-frontier-20260923',('randomized_frontier.py','verify.py'))]:
 with tempfile.TemporaryDirectory(prefix='ndu-r35-inherited-') as tmp:
  dest=Path(tmp);hashes={}
  for name in names:
   source=R.parent/folder/name
   hashes[name]=hashlib.sha256(source.read_bytes()).hexdigest()
   shutil.copy2(source,dest/name)
  p=subprocess.run([sys.executable,str(dest/'verify.py')],text=True,capture_output=True)
  if p.returncode:
   print(p.stdout);print(p.stderr);raise RuntimeError(f'{version} inherited suite failed')
  result=json.loads((dest/'verification.json').read_text());assert result['status']=='PASS'
  record['suites'][version]={'status':'PASS','unchanged_script_sha256':hashes,'rerun':result}
  print(version,'PASS')
record['note']='Both suites executed without modifying inherited scripts or result files. These are inherited regression tests, not new independent evidence.'
(R/'inherited_verification.json').write_text(json.dumps(record,indent=2)+'\n')
