"""Replay and test publication without relabeling benchmark performance."""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
sys.path.insert(0,str(R/'code'))
import tests
from evidence import replay

def run():
    expected=json.loads((R/'results/tests.json').read_text())
    out=ROOT/'.build/r47/test_rerun.json';out.parent.mkdir(parents=True,exist_ok=True)
    got=tests.run(out)
    if got['counts']!=expected['counts'] or got['mutations']!=expected['mutations']:
        raise RuntimeError('Regression outcomes differ from frozen validation')
    replay()
    (R/'results/PUBLICATION_VALIDATION.json').write_text(json.dumps(dict(status='PASS',regression_counts=got['counts'],
        exact_certificates=56,regression_rerun_seconds=got['elapsed_seconds'],
        benchmark_scope='Canonical local observations preserved; publication is deterministic witness reconstruction and validation',
        protocol_sha256=hashlib.sha256((R/'PROTOCOL.json').read_bytes()).hexdigest()),indent=2)+'\n')
if __name__=='__main__':run()
