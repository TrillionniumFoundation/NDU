"""Execute the declared new evidence; compare deterministic outcomes to local run."""
from pathlib import Path
import subprocess,sys,json
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
def run():
    for name in ['tests','study','verify','response','tables','assemble']:
        subprocess.run([sys.executable,str(R/'code'/f'{name}.py')],cwd=ROOT,check=True)
    expected=json.loads((R/'EXPECTED_SUMMARY.json').read_text());actual=json.loads((R/'results/SUMMARY.json').read_text())
    keys=['cases','max_histories','certificates','harmonic_complete','minimum_complete','combined_complete','strict_harmonic_reference_improvements','reference_cases','mip_solves','max_harmonic_gap','max_combined_gap']
    if any(expected[k]!=actual[k] for k in keys):raise ValueError('Deterministic scientific outcomes differ from local validation')
    (R/'PUBLICATION_VALIDATION.json').write_text(json.dumps(dict(status='PASS',compared_fields=keys,
        timing_provenance='Current results contain actual publication measurements; LOCAL_EXECUTION.json retains separate local measurements',
        mip_status_provenance='Solver time-limit outcomes may differ and are retained, not forced to match'),indent=2)+'\n')
if __name__=='__main__':run()
