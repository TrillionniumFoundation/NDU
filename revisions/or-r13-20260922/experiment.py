#!/usr/bin/env python3
"""Frozen face-aware neural routing, exact audits, independent validation.
Validation cannot expand the library or change features, tolerance or rules.
"""
from nonsmooth import *
import gzip,argparse

def draw(rng,n):
    return np.column_stack((rng.integers(-1000,1001,(n,2))/1000,rng.integers(10,201,n)/1000))
def serial(c):return {k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in c.items()}
def compress(path,obj):
    with open(path,'wb') as fp:
        with gzip.GzipFile(fileobj=fp,mode='wb',mtime=0) as gz:gz.write(json.dumps(obj,separators=(',',':')).encode())
def readzip(path):
    with gzip.open(path,'rt') as f:return json.load(f)

def train_model(n):
    tr=Tree(5);train=draw(np.random.default_rng(13031),n);cells=[];lookup={};labels=[];fail=[];start=time.perf_counter()
    for i,th in enumerate(train):
        u,secs,it,status=tr.solve(th)
        try:cell=tr.cell(th,u)
        except RuntimeError as e:fail.append({'index':i,'theta':th.tolist(),'reason':str(e)});labels.append(-1);continue
        if cell['key'] not in lookup:lookup[cell['key']]=len(cells);cells.append(cell)
        labels.append(lookup[cell['key']])
    library_seconds=time.perf_counter()-start;labels=np.array(labels);mask=labels>=0
    rng=np.random.default_rng(13032);hidden=192;A=rng.normal(size=(3,hidden));bias=rng.uniform(-1,1,hidden)
    def feats(x):
        xx=x*np.array([1.,1.,10.]);return np.column_stack((np.ones(len(x)),xx,np.maximum(xx@A+bias,0)))
    st=time.perf_counter();Phi=feats(train[mask]);Y=np.eye(len(cells))[labels[mask]]
    coef=np.linalg.solve(Phi.T@Phi+.01*np.eye(Phi.shape[1]),Phi.T@Y);fit_seconds=time.perf_counter()-st
    model={'architecture':'random-feature ReLU hidden layer; fitted least-squares multiclass readout',
           'hidden':hidden,'A':A.tolist(),'bias':bias.tolist(),'readout':coef.tolist(),'training_seed':13031,'feature_seed':13032,
           'depth':5,'tree_seed':1301,'train_n':n,'training_failures':fail,'labels':labels.tolist(),'training':train.tolist(),
           'cells':[serial(c) for c in cells],'pipelines':['neural-top1-static','neural-top3-static','nearest-anchor-static'],
           'validation_distribution':'independent uniform integers [-1000,1000]/1000 twice and [10,200]/1000 for friction',
           'validation_seed':13033,'delta':.05,'certificate_tolerance':1e-7,'frozen_before_validation':True,
           'library_seconds':library_seconds,'fit_seconds':fit_seconds}
    compress(HERE/'results/frozen_model.json.gz',model)
    print('frozen cells',len(cells),'training failures',len(fail),'offline seconds',library_seconds+fit_seconds,flush=True)

def load():
    model=readzip(HERE/'results/frozen_model.json.gz');tr=Tree(model['depth'],model['tree_seed'])
    cells=[{k:np.array(v) if isinstance(v,list) else v for k,v in c.items()} for c in model['cells']]
    A=np.array(model['A']);bias=np.array(model['bias']);coef=np.array(model['readout']);X=np.array(model['training']);Y=np.array(model['labels']);mask=Y>=0;X=X[mask];Y=Y[mask]
    def order(th):
        x=th*np.array([1.,1.,10.]);f=np.r_[1.,x,np.maximum(x@A+bias,0)];return np.argsort(-(f@coef))
    def nearest(th):return int(Y[np.argmin(np.sum(((X-th)*np.array([1,1,10]))**2,axis=1))])
    def pick(th,ids):
        for j in ids:
            if contains(cells[int(j)],th):return int(j)
        return -1
    def cert(th,j):
        if j<0:return tr.audit(th,np.zeros(tr.m),np.zeros(len(tr.L)),np.zeros(tr.N))
        return tr.audit(th,*eval_cell(cells[j],th))
    return model,tr,cells,order,nearest,pick,cert

def validate(n,start,count):
    model,tr,cells,order,nearest,pick,cert=load();out=HERE/'results'
    frozen_hash=hashlib.sha256((out/'frozen_model.json.gz').read_bytes()).hexdigest()
    val=draw(np.random.default_rng(13033),n);records=[];rows=[]
    for i in range(start,min(start+count,n)):
        th=val[i];ids=order(th);chosen=[pick(th,ids[:1]),pick(th,ids[:3]),pick(th,[nearest(th)])];cache={};refs=[]
        for j in chosen:
            if j not in cache:
                audit=cert(th,j);j_actual=j
                if audit['gain']<0:audit=cert(th,-1);j_actual=-1
                audit.update({'sample':i,'cell':j_actual});cache[j]=len(records);records.append(audit)
            refs.append(cache[j])
        rows.append({'sample':i,'theta':th.tolist(),'records':refs})
    assert hashlib.sha256((out/'frozen_model.json.gz').read_bytes()).hexdigest()==frozen_hash
    compress(out/f'validation-{start:05d}.json.gz',{'depth':5,'tree_seed':1301,'n':n,'records':records,'samples':rows,'frozen_sha256':frozen_hash})
    print('validated',start,len(rows),'exact records',len(records),flush=True)

def report():
    model,tr,cells,order,nearest,pick,cert=load();out=HERE/'results'
    Bq=max(sum(((tr.gq[0][i]+a*tr.gq[1][i]+b*tr.gq[2][i])**2/(4*tr.wq[i]) for i in range(tr.N)),F(0))/sum(tr.wq) for a in (-1,1) for b in (-1,1))
    sums=np.zeros(3);gains=np.zeros(3);hits=np.zeros(3,dtype=int);indices=[];hashes=set();numrecords=0
    for file in sorted(out.glob('validation-*.json.gz')):
        part=readzip(file);hashes.add(part['frozen_sha256']);numrecords+=len(part['records'])
        for row in part['samples']:
            indices.append(row['sample'])
            for k,rid in enumerate(row['records']):
                r=part['records'][rid];sums[k]+=min(r['bound'],float(Bq));gains[k]+=r['gain'];hits[k]+=int(r['cell']>=0)
    assert sorted(indices)==list(range(part['n'])) and len(hashes)==1
    n=len(indices);means=sums/n;rad=float(Bq)*np.sqrt(np.log(3/.05)/(2*n));selected=int(np.argmin(means))
    validation={'M':3,'n':n,'delta':.05,'B_fraction':str(Bq),'B':float(Bq),'radius':rad,
                'empirical_certificate_means':means.tolist(),'expected_regret_upper_bounds':(means+rad).tolist(),
                'empirical_gains':(gains/n).tolist(),'certified_cell_rates':(hits/n).tolist(),'selected_pipeline':selected,
                'model_sha256_before_and_after':next(iter(hashes)),'sampling_seed':13033,'no_validation_refitting':True,'record_count':numrecords}
    dump(out/'validation.json',validation)
    matched=[];test=draw(np.random.default_rng(13034),48)
    for i,th in enumerate(test):
        st=time.perf_counter();u,rawsec,nit,ok=tr.solve(th);ce=tr.cell(th,u);reference=tr.audit(th,*eval_cell(ce,th));coldsec=time.perf_counter()-st
        if reference['bound']>1e-7:raise RuntimeError('Cold final tolerance not attained')
        methods={}
        for method in ('neural-top3','nearest-anchor','sequential-cells'):
            st=time.perf_counter()
            ids=order(th)[:3] if method=='neural-top3' else ([nearest(th)] if method=='nearest-anchor' else range(len(cells)))
            jj=pick(th,ids);initial=cert(th,jj);refined=False;iterations=0;final=initial
            if final['bound']>1e-7:
                uu,ss,iterations,success=tr.solve(th);cc=tr.cell(th,uu);final=tr.audit(th,*eval_cell(cc,th));refined=True
            elapsed=time.perf_counter()-st
            if final['bound']>1e-7:raise RuntimeError('Deployment tolerance not attained')
            # Diagnostics run AFTER the timed complete pipeline, never hidden refinement.
            first=int(order(th)[0]) if method=='neural-top3' else (nearest(th) if method=='nearest-anchor' else 0)
            pu,pm,ps=eval_cell(cells[first],th);distance=float(np.linalg.norm(tr.B@(pu-u)))
            predicted=(np.abs(tr.h-tr.L@pu)<1e-6);truth=(np.abs(tr.h-tr.L@u)<1e-6)
            face_equal=bool(np.array_equal(predicted,truth) and np.array_equal(np.sign(np.round(tr.K@pu,6)),np.sign(np.round(tr.K@u,6))))
            methods[method]={'seconds':elapsed,'initial_cell':jj,'immediate':not refined,'static_before_refinement':jj<0,
                              'refinement_iterations':iterations,'refined':refined,'warm_distance':distance,
                              'first_face_correct':face_equal,'candidate':initial,'final':final}
        matched.append({'sample':i,'theta':th.tolist(),'cold_seconds':coldsec,'cold_iterations':nit,'cold_solver_success':ok,'reference':reference,'methods':methods})
    compress(out/'matched_records.json.gz',{'depth':5,'tree_seed':1301,'records':matched})
    times={'cold':float(np.median([r['cold_seconds'] for r in matched]))}
    for method in matched[0]['methods']:times[method]=float(np.median([r['methods'][method]['seconds'] for r in matched]))
    compatible=[]
    for th in test:
        j=pick(th,range(len(cells)))
        if j<0:continue
        ce=cells[j];uu,mm,ss=eval_cell(ce,th)
        def val(t):
            u,_,_=eval_cell(ce,t);a,lam=tr.pars(t);return a@u-.5*u@tr.Qf@u-lam*tr.k@np.abs(tr.K@u)
        eps=1e-6
        if all(contains(ce,th+eps*np.eye(3)[j]) and contains(ce,th-eps*np.eye(3)[j]) for j in range(3)):
            target=np.r_[tr.G[:,1:].T@(tr.B@uu),-tr.k@np.abs(tr.K@uu)]
            fd=np.array([(val(th+eps*np.eye(3)[j])-val(th-eps*np.eye(3)[j]))/(2*eps) for j in range(3)])
            compatible.append(float(np.max(np.abs(fd-target))))
    saved=np.mean([r['cold_seconds']-r['methods']['neural-top3']['seconds'] for r in matched]);cost=model['library_seconds']+model['fit_seconds']
    summary={'nodes':tr.N,'cells':len(cells),'training_failures':len(model['training_failures']),'library_seconds':model['library_seconds'],'fit_seconds':model['fit_seconds'],
             'matched_n':len(matched),'median_seconds':times,'observed_break_even_vs_cold':int(np.ceil(cost/saved)) if saved>0 else None,
             'maximum_final_certificate':max(r['methods'][m]['final']['bound'] for r in matched for m in r['methods']),
             'compatible_gradient_checks':len(compatible),'compatible_gradient_max_error':max(compatible,default=None),'validation':validation,
             'environment':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform()},
             'methods':{m:{'immediate_fraction':float(np.mean([r['methods'][m]['immediate'] for r in matched])),
                            'refinement_fraction':float(np.mean([r['methods'][m]['refined'] for r in matched])),
                            'first_face_accuracy':float(np.mean([r['methods'][m]['first_face_correct'] for r in matched])),
                            'mean_warm_distance':float(np.mean([r['methods'][m]['warm_distance'] for r in matched])),
                            'mean_added_iterations':float(np.mean([r['methods'][m]['refinement_iterations']-r['cold_iterations'] for r in matched]))}
                         for m in matched[0]['methods']}}
    dump(out/'summary.json',summary);print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['train','validate','report']);p.add_argument('--n',type=int,default=4096);p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=1024);a=p.parse_args()
    (HERE/'results').mkdir(exist_ok=True)
    if a.stage=='train':train_model(a.n)
    elif a.stage=='validate':validate(a.n,a.start,a.count)
    else:report()
