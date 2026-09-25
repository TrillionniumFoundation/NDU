"""Fresh, deterministic remote reproduction; local measurements remain separate."""
from pathlib import Path
import subprocess,sys,json,os,datetime
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
def run(name):subprocess.run([sys.executable,str(R/'code'/name)],cwd=ROOT,check=True)
def main():
    os.environ['R49_EXECUTION_SCOPE']='R49 GitHub Actions publication execution'
    (R/'results').mkdir(exist_ok=True)
    run('tests.py')
    old=ROOT/'revisions/or-r48-harmonic-coarsening-20260925/code/tests.py'
    result=subprocess.run([sys.executable,str(old)],cwd=ROOT,text=True,capture_output=True,check=True)
    (R/'results/ANCESTOR_REGRESSION.txt').write_text(result.stdout+result.stderr)
    run('study_r49.py');run('verify_r49.py')
    local=json.loads((R/'LOCAL_EXECUTION.json').read_text())
    now=json.loads((R/'results/study.json').read_text())
    indexed={x['id']:x for x in now['cases']}
    for prior in local['cases']:
        current=indexed[prior['id']]
        for key in ['lower_bound','upper_bound','gap','status','evaluated_nodes','oracle_calls']:
            assert prior[key]==current[key],(prior['id'],key)
    (R/'results/LOCAL_PUBLICATION_COMPARISON.json').write_text(json.dumps(dict(status='PASS',
        fields=['lower_bound','upper_bound','gap','status','evaluated_nodes','oracle_calls'],cases=64,
        timings='Measured separately and not required to match',utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
    run('tables_r49.py');run('assemble_r49.py');run('response_r49.py');run('metadata_r49.py')
if __name__=='__main__':main()
