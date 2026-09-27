"""Verify every committed new certificate without rerunning any optimizer."""
from pathlib import Path
import gzip,json,hashlib,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'or-r47-joint-certificates-20260925'/'code'))
from check_harmonic import check
from check_coarsening import check as check_old
R=Path(__file__).resolve().parents[1]
def run():
    rows=json.loads((R/'results/study.json').read_text())['cases'];checked=[]
    for row in rows:
        for name,checker in [('harmonic',check),('minimum',check_old)]:
            meta=row[name+'_certificate'];p=R/meta['path']
            if hashlib.sha256(p.read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('Certificate hash')
            val=checker(json.loads(gzip.decompress(p.read_bytes())))
            if val['status']!='PASS':raise ValueError('Certificate rejected')
            checked.append(dict(case=row['id'],method=name,sha256=meta['sha256'],gap=val['gap']))
    if len(rows)!=24 or len(checked)!=48:raise ValueError('Missing requested case')
    out=dict(status='PASS',certificates=checked)
    (R/'results/VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print('48 semantic certificates verified')
if __name__=='__main__':run()
