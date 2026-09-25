"""Fresh isolated publication execution, with local semantic comparison."""
from pathlib import Path
import subprocess,sys,json,hashlib,datetime,os
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
def run(name):
    subprocess.run([sys.executable,str(R/'code'/name)],cwd=ROOT,check=True)
def main():
    (R/'results/certificates').mkdir(parents=True,exist_ok=True)
    if (R/'results/study.json').exists():
        raise RuntimeError('Fresh publication requires a clean R51 results directory; do not overwrite measured evidence')
    run('tests.py');run('study.py');run('additional_checks.py')
    expected=json.loads((R/'SEMANTIC_EXPECTATIONS.json').read_text())
    now=json.loads((R/'results/study.json').read_text())
    assert now['protocol_sha256']==expected['protocol_sha256']
    byid={x['id']:x for x in now['cases']}
    assert set(byid)=={x['id'] for x in expected['cases']}
    for prior in expected['cases']:
        current=byid[prior['id']]
        fields={k:current[k] for k in ['model','catalog','charges','promise','m']}
        assert hashlib.sha256(json.dumps(fields,sort_keys=True,separators=(',',':')).encode()).hexdigest()==prior['input_sha256']
        for key in expected['fields']:
            assert prior[key]==current[key],(prior['id'],key,prior[key],current[key])
    record={'status':'PASS','cases':len(byid),'fields':expected['fields'],'inputs':'exact canonical input hashes match','timings':'local and publication measurements are distinct and are not required to match','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'github_run_id':os.getenv('GITHUB_RUN_ID'),'github_sha':os.getenv('GITHUB_SHA')}
    (R/'results/LOCAL_PUBLICATION_COMPARISON.json').write_text(json.dumps(record,indent=2)+'\n')
    run('tables.py');print(json.dumps(record),flush=True)
if __name__=='__main__':main()
