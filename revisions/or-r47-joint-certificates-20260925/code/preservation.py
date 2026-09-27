"""Full inherited-tree preservation, not just a count of theorem labels."""
from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
BASE='9f260e0d6c4e06cf4227f96865a88f4dab67e58e'
REPLACED=('main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    baseline=json.loads((R/'BASELINE_SHA256.json').read_text());errors=[];unchanged=0;predecessor={}
    for name,h in baseline.items():
        p=ROOT/name
        if name in REPLACED:
            old=R/'predecessor'/name
            if not old.exists() or sha(old)!=h:errors.append('Predecessor mismatch: '+name)
            else:predecessor[name]=h
        elif not p.exists() or sha(p)!=h:errors.append('Inherited change: '+name)
        else:unchanged+=1
    out=dict(status='PASS' if not errors else 'FAIL',baseline_commit=BASE,inherited_files=len(baseline),
      unchanged_inherited_files=unchanged,authorized_current_readers_and_indexes=list(REPLACED),
      exact_predecessor_sha256=predecessor,errors=errors,
      scope='All inherited paths outside the six explicit current readers/indexes are byte-identical; all six original versions are preserved. No historical derivation is deleted.')
    (R/'PRESERVATION_MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
    if errors:raise RuntimeError(errors)
if __name__=='__main__':run()
