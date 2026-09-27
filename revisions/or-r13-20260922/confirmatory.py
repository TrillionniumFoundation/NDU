#!/usr/bin/env python3
"""Prospective confirmation; fixed policy model and deterministic corner range."""
from experiment import *

def run(start,count):
    plan=json.loads((HERE/'results/confirmatory_plan.json').read_text())
    model,tr,cells,order,nearest,pick,cert=load()
    assert hashlib.sha256((HERE/'results/frozen_model.json.gz').read_bytes()).hexdigest()==plan['model_sha256']
    ths=draw(np.random.default_rng(plan['seed']),plan['n']);records=[];rows=[]
    for i in range(start,min(start+count,plan['n'])):
        th=ths[i];ids=order(th);chosen=[pick(th,ids[:1]),pick(th,ids[:3]),pick(th,[nearest(th)])];cache={};refs=[]
        for j in chosen:
            if j not in cache:
                r=cert(th,j);actual=j
                if r['gain']<0:r=cert(th,-1);actual=-1
                r.update(sample=i,cell=actual);cache[j]=len(records);records.append(r)
            refs.append(cache[j])
        rows.append({'sample':i,'theta':th.tolist(),'records':refs})
    compress(HERE/f'results/confirmation-{start:05d}.json.gz',{'records':records,'samples':rows,'depth':5,'tree_seed':1301,
             'model_sha256':plan['model_sha256'],'plan_sha256':hashlib.sha256((HERE/'results/confirmatory_plan.json').read_bytes()).hexdigest()})
    print('confirmation',start,len(rows),flush=True)

def prepare():
    model,tr,*_=load();rs=[]
    for x in (-1.,1.):
        for y in (-1.,1.):
            th=np.array([x,y,.01]);u,*_=tr.solve(th);ce=tr.cell(th,u);rs.append(tr.audit(th,*eval_cell(ce,th)))
    B=max(F(r['gain_fraction'])+F(r['bound_fraction']) for r in rs)/sum(tr.wq)
    dump(HERE/'results/confirmatory_plan.json',{'model_sha256':hashlib.sha256((HERE/'results/frozen_model.json.gz').read_bytes()).hexdigest(),
         'M':3,'n':4096,'delta':.05,'seed':13035,'pipelines':model['pipelines'],'range_fraction':str(B),'corner_records':rs,
         'design_note':'Prospective second validation after broad-range first validation. Frozen policies unchanged; tighter range obtained solely from four deterministic parameter-box corners, not validation samples.'})

def summary():
    plan=json.loads((HERE/'results/confirmatory_plan.json').read_text());B=F(plan['range_fraction']);mass=sum(Tree(5).wq)
    cs=[F(0)]*3;gs=[F(0)]*3;hits=[0]*3;seen=[];record_count=0
    for p in sorted((HERE/'results').glob('confirmation-*.json.gz')):
        data=readzip(p);record_count+=len(data['records'])
        assert data['model_sha256']==plan['model_sha256']
        assert data['plan_sha256']==hashlib.sha256((HERE/'results/confirmatory_plan.json').read_bytes()).hexdigest()
        for row in data['samples']:
            seen.append(row['sample'])
            for j,ind in enumerate(row['records']):
                r=data['records'][ind];cs[j]+=min(B,F(r['bound_fraction'])/mass);gs[j]+=F(r['gain_fraction'])/mass;hits[j]+=r['cell']>=0
    assert sorted(seen)==list(range(plan['n']))
    n=plan['n'];radius=float(B)*np.sqrt(np.log(2*plan['M']/plan['delta'])/(2*n))
    out={'M':3,'n':n,'delta':.05,'B':float(B),'B_fraction':str(B),'radius':radius,'seed':13035,'model_sha256':plan['model_sha256'],
         'empirical_certificate_means':[float(c/n) for c in cs],'empirical_gains':[float(g/n) for g in gs],
         'expected_regret_upper_bounds':[float(c/n)+radius for c in cs],
         'expected_gain_lower_bounds':[max(0.,float(g/n)-radius) for g in gs],
         'certificate_sums_fraction':list(map(str,cs)),'gain_sums_fraction':list(map(str,gs)),
         'certified_cell_rates':[h/n for h in hits],'selected_pipeline':int(np.argmin(list(map(float,cs)))),
         'record_count':record_count,'simultaneous_gain_and_regret':True,'no_refitting':True}
    dump(HERE/'results/confirmation.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','run','summary']);p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=1024);a=p.parse_args()
    if a.stage=='prepare':prepare()
    elif a.stage=='run':run(a.start,a.count)
    else:summary()
