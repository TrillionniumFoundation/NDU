"""Independent R27 rational verifier; Python standard library only.

No imports from any optimizer, historical verifier, proposal script, or fitted
model. Rebuilds every coefficient, checks all primal constraints, recomputes
Fenchel certificates, and deploys a cache with no query optimizer information.
"""
from __future__ import annotations
import copy,gzip,hashlib,json,math,sys
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parent;B=R.parent.parent;O=R/'results'
OLD=R.parent/'or-r25-20260923/results'

def require(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text())
def records(p):
    with gzip.open(p,'rt') as f:return [json.loads(l) for l in f]
def dot(a,b):
    require(len(a)==len(b),'dot dimensions')
    return sum((x*y for x,y in zip(a,b) if x and y),F(0))
def matvec(a,x):return [dot(row,x) for row in a]
def transpose_product(a,v,n):
    require(len(a)==len(v),'transpose dimensions')
    out=[F(0)]*n
    for row,mul in zip(a,v):
        require(len(row)==n,'matrix dimensions')
        if mul:
            for i,q in enumerate(row):
                if q:out[i]+=q*mul
    return out
def fraction_matrix(a):return [list(map(F,row)) for row in a]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clip(v,lo,hi):return min(hi,max(lo,v))
def strings(a):return {k:[str(x) for x in v] for k,v in a.items()}

def system(p,context,rho,theta,kind='true'):
    """Independent reconstruction of the explicitly recorded R25/R27 family."""
    rho=F(rho);theta=[F(int(x),8) for x in theta]
    require(len(theta)==3 and all(abs(x)<1 for x in theta),'coefficient direction')
    require(0<=rho<=F(1,4),'designed radius')
    n=len(p['qnum']);rank=p['rank'];sv=p['services']
    require(len(context)==rank+1,'reward context')
    lo=[F(-int(x),32) for x in p['znum']];hi=[F(32-int(x),32) for x in p['znum']]
    diagonal=[F(int(x),16) for x in p['qnum']]
    rr=[[F(int(x),32) for x in row] for row in p['Unum']]
    dd=fraction_matrix(p['B']);hh=[F(-int(x),32) for x in p['vnum']]
    kappa=[F(int(x),8) for x in p['knum']]
    lam=(1+rho*theta[1])*F(int(context[-1]),64)
    base=[F(int(p['bnum'][i]),32)+sum((F(int(p['Unum'][j][i])*int(context[j]),512) for j in range(rank)),F(0)) for i in range(n)]
    reward=[(1+rho*theta[0])*q+rho*theta[2]*F(1 if i%2==0 else -1,8) for i,q in enumerate(base)]
    aa=[];bb=[]
    for row in p['Aacc']:
        if kind=='outer':
            aa.append(list(map(F,row)))
            bb.append(rho*sum((abs(int(a))*max(abs(l),abs(u)) for a,l,u in zip(row,lo,hi)),F(0)))
        else:
            aa.append([F(int(a))*(1+rho*theta[2]*(1 if (i//sv)%2==0 else -1)) for i,a in enumerate(row)])
            bb.append(F(0))
    for row,cap in zip(p['C'],p['capnum']):
        aa.append(list(map(F,row)));bb.append((1+rho*(1 if kind=='outer' else theta[1]))*F(int(cap),8))
    ff=fraction_matrix(p['E'])
    if kind!='full':
        for j in range(p['nodes']):
            depth=(j+1).bit_length()-1;rep=(1<<depth)-1
            if j==rep:continue
            for a in range(sv):
                row=[F(0)]*n;row[j*sv+a]=F(1);row[rep*sv+a]=F(-1);ff.append(row)
    out={'lo':lo,'hi':hi,'H':diagonal,'R':rr,'D':dd,'h':hh,'kappa':kappa,'lam':lam,
         'p':reward,'A':aa,'b':bb,'F':ff,'f':[F(0)]*len(ff),'constant':lam*dot(kappa,list(map(abs,hh)))}
    validate_system(out);return out

def validate_system(m):
    n=len(m['H']);require(n>0 and len(m['p'])==n,'system dimension')
    require(len(m['lo'])==len(m['hi'])==n and all(l<u for l,u in zip(m['lo'],m['hi'])),'tier box')
    require(all(q>0 for q in m['H']) and m['lam']>=0,'curvature/friction')
    require(len(m['h'])==len(m['kappa'])==len(m['D']) and all(k>0 for k in m['kappa']),'switch shape')
    for key in ('R','D','A','F'):require(all(len(row)==n for row in m[key]),'matrix shape '+key)
    require(len(m['A'])==len(m['b']) and len(m['F'])==len(m['f']),'constraint shape')

def verify_model(m,stored):
    aliases={'p':'b','lam':'lam','A':'A','b':'rhs','F':'E'}
    for key,oldkey in aliases.items():
        v=stored[oldkey]
        actual=fraction_matrix(v) if key in ('A','F') else list(map(F,v)) if isinstance(v,list) else F(v)
        require(actual==m[key],'model coefficient mismatch '+oldkey)

def policy(record,n):
    den=int(record['x_den']);require(den>0,'primal denominator')
    x=[F(int(v),den) for v in record['x_num']];require(len(x)==n,'primal dimension');return x

def feasibility(m,x):
    require(len(x)==len(m['H']),'primal dimension')
    require(all(l<=v<=u for l,v,u in zip(m['lo'],x,m['hi'])),'primal box')
    require(all(dot(a,x)<=b for a,b in zip(m['A'],m['b'])),'primal inequality')
    require(all(dot(a,x)==b for a,b in zip(m['F'],m['f'])),'primal equality')

def normalized(m,record):
    den=int(record['den']);require(den>0,'dual denominator')
    a={key:[F(int(v),den) for v in record[old]] for key,old in [('alpha','p'),('mu','mu'),('nu','nu'),('tau','s')]}
    if m['lam']:
        a['tau']=[v/m['lam'] for v in a['tau']]
    else:
        require(all(v==0 for v in a['tau']),'zero-friction tension');a['tau']=[F(0)]*len(a['tau'])
    validate_price(m,a);return a

def validate_price(m,a):
    for key,target in [('alpha','R'),('mu','A'),('nu','F'),('tau','D')]:
        require(len(a[key])==len(m[target]),'price dimension '+key)
    require(all(x>=0 for x in a['mu']),'negative participation price')
    require(all(abs(x)<=k for x,k in zip(a['tau'],m['kappa'])),'normalized tension capacity')

def value(m,x):
    rx=matvec(m['R'],x);switch=[v-h for v,h in zip(matvec(m['D'],x),m['h'])]
    return m['constant']+dot(m['p'],x)-sum((h*v*v/2 for h,v in zip(m['H'],x)),F(0))-dot(rx,rx)/2-m['lam']*dot(m['kappa'],list(map(abs,switch)))

def upper(m,a,detail=False):
    """Only exact query coefficients and stored normalized prices are used."""
    validate_system(m);validate_price(m,a);n=len(m['H'])
    residual=list(m['p'])
    for key,price in [('R',a['alpha']),('A',a['mu']),('F',a['nu']),('D',[m['lam']*t for t in a['tau']])]:
        term=transpose_product(m[key],price,n);residual=[x-y for x,y in zip(residual,term)]
    modes=[clip(r/h,l,u) for r,h,l,u in zip(residual,m['H'],m['lo'],m['hi'])]
    conjugates=[r*x-h*x*x/2 for r,h,x in zip(residual,m['H'],modes)]
    total=m['constant']+dot(a['alpha'],a['alpha'])/2+dot(a['mu'],m['b'])+dot(a['nu'],m['f'])+m['lam']*dot(a['tau'],m['h'])+sum(conjugates,F(0))
    return (total,residual,conjugates) if detail else total

def decomposition(m,x,a):
    feasibility(m,x);up,res,conj=upper(m,a,True);lo=value(m,x)
    err=[v-w for v,w in zip(a['alpha'],matvec(m['R'],x))]
    comp={'resource':dot(err,err)/2,
          'box':sum((q-r*y+h*y*y/2 for q,r,h,y in zip(conj,res,m['H'],x)),F(0)),
          'participation':sum((mu*(b-dot(row,x)) for mu,row,b in zip(a['mu'],m['A'],m['b'])),F(0))}
    sw=[v-h for v,h in zip(matvec(m['D'],x),m['h'])]
    comp['switch']=m['lam']*sum((k*abs(v)-t*v for k,t,v in zip(m['kappa'],a['tau'],sw)),F(0))
    require(all(v>=0 for v in comp.values()),'negative Fenchel component')
    require(sum(comp.values(),F(0))==up-lo,'exact gap decomposition')
    return lo,up,comp

def audit(m,record):
    verify_model(m,record['model']);x=policy(record['policy'],len(m['H']));a=normalized(m,record['dual'])
    lo,up,_=decomposition(m,x,a)
    require(lo==F(record['lower']) and up==F(record['upper']),'stored certificate mismatch')
    require(up>=lo,'weak duality');return x,a,lo,up

def cache_upper(m,cache):
    vals=[upper(m,{k:list(map(F,v)) for k,v in item['price'].items()}) for item in cache]
    best=min(range(len(vals)),key=vals.__getitem__)
    return vals[best],best,vals

def simple_system(theta):
    t=F(theta)
    return {'lo':[F(0)],'hi':[F(1)],'H':[F(1)],'R':[],'D':[[F(1)]],'h':[F(0)],'kappa':[F(1)],'lam':F(1,2)+t/4,
            'p':[2+2*t],'A':[[1+t]],'b':[F(1,2)+t/8],'F':[],'f':[],'constant':F(0)}

def examples():
    a={'alpha':[],'mu':[F(1)],'nu':[],'tau':[F(1)]};moving=[]
    for t in [F(k,32) for k in range(-8,9)]:
        m=simple_system(t);z=(F(1,2)+t/8)/(1+t)
        # KKT: the actual upper cap binds, with nonnegative actual multiplier.
        actual_mu=(m['p'][0]-m['lam']-z)/(1+t);require(actual_mu>=0,'exact optimizer multiplier')
        opt={**a,'mu':[actual_mu]};lo,up,_=decomposition(m,[z],opt);require(lo==up,'exact moving optimum')
        cached=upper(m,a);err=t*(F(9,8)+F(3,4)*t)/(1+t)
        require(cached-lo==err*err/2,'moving geometry square identity')
        moving.append({'theta':str(t),'optimizer':str(z),'value':str(lo),'cache':str(cached),'gap':str(cached-lo)})
    degenerate=[]
    for t in [F(k,32) for k in range(-8,9)]:
        m={'lo':[F(-1,2)],'hi':[F(1,2)],'H':[F(1)],'R':[],'D':[],'h':[],'kappa':[],'lam':F(0),'p':[F(1)],'A':[[F(1)],[F(1)]],'b':[t,-t],'F':[],'f':[],'constant':F(0)}
        z=-abs(t);K=z-z*z/2;cached=upper(m,{'alpha':[],'mu':[F(1),F(0)],'nu':[],'tau':[]})
        require(cached-K==t+abs(t)+t*t/2,'degenerate first-order loss')
        degenerate.append({'theta':str(t),'optimizer':str(z),'value':str(K),'cache':str(cached),'gap':str(cached-K)})
    def robust(t):
        m=simple_system(t);m['b']=[F(3,4)+t/8];m['F']=[[F(1)]];m['f']=[F(1,2)];return m
    prices=[]
    for t in (-F(1,4),F(0),F(1,4)):
        m=robust(t);price={'alpha':[],'mu':[F(0)],'nu':[m['p'][0]-m['lam']-F(1,2)],'tau':[F(1)]}
        require(upper(m,price)==value(m,[F(1,2)]),'exact uniform anchor');prices.append(price)
    cell_records=[];previous=None
    for count in (1,2,4,8,16):
        cells=[]
        for i in range(count):
            ends=[-F(1,4)+F(i,2*count),-F(1,4)+F(i+1,2*count)]
            for t in ends:
                m=robust(t);full={**m,'F':[],'f':[]};feasibility(full,[F(3,5)]);feasibility(m,[F(1,2)])
                require(value(m,[F(3,5)])-value(m,[F(1,2)])==F(19,200)+F(7,40)*t,'exact uniform gain')
            lower=max(min(value(robust(t),[F(3,5)])-upper(robust(t),a) for t in ends) for a in prices)
            cells.append({'ends':[str(t) for t in ends],'lower':str(lower)})
        lower=min(F(c['lower']) for c in cells);require(lower<=F(41,800),'uniform gain upper violation')
        require(previous is None or lower>=previous,'subdivision monotonicity');previous=lower
        cell_records.append({'cell_count':count,'uniform_gain_lower':str(lower),'cells':cells})
    require([F(c['uniform_gain_lower']) for c in cell_records]==[F(-569,12800),F(-9,12800)]+[F(2519,51200)]*3,'uniform example arithmetic')
    def crossing(t):
        return {'lo':[F(0)],'hi':[F(1)],'H':[F(1)],'R':[],'D':[],'h':[],'kappa':[],'lam':F(0),'p':[F(1)],'A':[[F(1)],[F(1)]],'b':[1+t,1-t],'F':[],'f':[],'constant':F(0)}
    aa=[{'alpha':[],'mu':[F(1),F(0)],'nu':[],'tau':[]},{'alpha':[],'mu':[F(0),F(1)],'nu':[],'tau':[]}]
    unsafe=max(min(upper(crossing(t),a) for a in aa) for t in (F(-1),F(1)))
    center=value(crossing(F(0)),[F(1)]);require(unsafe==0 and center==F(1,2),'vertex minmax example')
    return {'moving_geometry':moving,'degenerate_face':degenerate,'uniform_cell_certificates':cell_records,
            'unsafe_vertex_anchor_interchange':{'false_uniform_upper':str(unsafe),'true_center_value':str(center)}}

def rejected(call):
    try:call()
    except (ValueError,AssertionError,KeyError,TypeError):return True
    return False

def negative_controls(m,r,a,example_results):
    failures=[]
    def check(name,fn):require(rejected(fn),'negative control accepted '+name);failures.append(name)
    b=copy.deepcopy(a);b['mu'][0]=F(-1);check('negative continuation price',lambda:upper(m,b))
    b=copy.deepcopy(a);b['tau'][0]=m['kappa'][0]+1;check('normalized switching capacity',lambda:upper(m,b))
    sm=simple_system(F(-1,4));stale={'alpha':[],'mu':[F(1)],'nu':[],'tau':[F(1,2)/sm['lam']]}
    check('unscaled stale switching tension',lambda:upper(sm,stale))
    b=copy.deepcopy(a);b['nu']=b['nu'][:-1];check('missing equality price',lambda:upper(m,b))
    b=copy.deepcopy(m);b['lam']=F(-1);check('negative friction parameter',lambda:upper(b,a))
    b=copy.deepcopy(m);b['H'][0]=0;check('nonpositive diagonal curvature',lambda:upper(b,a))
    sr=copy.deepcopy(r['model']);sr['A'][0][0]=str(F(sr['A'][0][0])+1);check('broken coefficient correlation',lambda:verify_model(m,sr))
    sr=copy.deepcopy(r['model']);sr['rhs'][-1]=str(F(sr['rhs'][-1])+1);check('changed continuation budget',lambda:verify_model(m,sr))
    sr=copy.deepcopy(r['model']);sr['E'].pop();check('removed information restriction',lambda:verify_model(m,sr))
    x=policy(r['policy'],len(m['H']));x[0]+=F(1,10000);check('broken root promise',lambda:feasibility(m,x))
    x=policy(r['policy'],len(m['H']));x[0]=m['hi'][0]+1;check('infeasible tier',lambda:feasibility(m,x))
    sr=copy.deepcopy(r);sr['upper']=str(F(sr['upper'])-F(1,1000));check('tampered dual endpoint',lambda:audit(m,sr))
    e=next(x for x in example_results['degenerate_face'] if x['theta']=='1/32')
    check('unconditional quadratic reuse claim',lambda:require(F(e['gap'])<=F(e['theta'])**2/2,'priced face changed'))
    trap=example_results['unsafe_vertex_anchor_interchange']
    check('invalid vertex-anchor interchange',lambda:require(F(trap['false_uniform_upper'])>=F(trap['true_center_value']),'unsafe uniform bound'))
    return failures

def round_up(q,d=10**8):return F(-((-q.numerator*d)//q.denominator),d)
def rounded(q):
    x=round_up(F(q));return f'{float(x):.8f}'
def mean(v):return sum(v,F(0))/len(v)

def run():
    p=read(OLD/'radius_primitives.json');old=records(OLD/'radius_certificates.jsonl.gz');new=records(O/'new_proposals.jsonl.gz')
    contexts=list(dict.fromkeys(tuple(r['context']) for r in old));require(len(contexts)==8,'context count')
    caches=[[] for _ in contexts];audited={};max_gap=F(0);audit_count=0
    for r in old:
        i=contexts.index(tuple(r['context']));rho=F(r['rho'])
        for kind in ('true','outer'):
            m=system(p,r['context'],rho,r['theta'],kind);out=audit(m,r[kind]);audited[(i,str(rho),kind)]=(m,out)
            max_gap=max(max_gap,out[3]-out[2]);audit_count+=1
        if rho in (0,F(1,16),F(1,4)):
            caches[i].append({'context_id':i,'rho':str(rho),'theta':r['theta'],'price':strings(audited[(i,str(rho),'true')][1][1]),'inherited_anchor_solver_seconds':r['true']['solver_seconds']})
    for c in caches:c.sort(key=lambda a:F(a['rho']))
    require(all(len(c)==3 for c in caches),'anchor count')
    outputs=[]
    def query(r,study,oracle):
        i=contexts.index(tuple(r['context']));rho=F(r['rho']);m=oracle['true'][0];x,_,lo,up=oracle['true'][1]
        cached,best,vals=cache_upper(m,caches[i]);outer=oracle['outer'][1][3]
        a={k:list(map(F,v)) for k,v in caches[i][best]['price'].items()}
        _,check,parts=decomposition(m,x,a);require(check==cached and cached>=lo,'cache audit')
        out={'study':study,'context_id':i,'rho':str(rho),'theta':r['theta'],'selected_anchor_rho':caches[i][best]['rho'],
             'restricted_lower':str(lo),'restricted_upper':str(up),'outer_upper':str(outer),
             'nominal_cache_upper':str(vals[0]),'cache_upper':str(cached),'all_cache_upper':[str(x) for x in vals],
             'cache_slack_interval':[str(max(F(0),cached-up)),str(cached-lo)],
             'outer_slack_interval':[str(max(F(0),outer-up)),str(outer-lo)],'decomposition_at_offline_restricted_witness':{k:str(v) for k,v in parts.items()}}
        if 'full' in oracle:
            full=oracle['full'][1]
            out.update({'implemented_full_value':str(full[2]),'full_optimum_upper':str(full[3]),
                        'implemented_gain_lower_cached':str(full[2]-cached),'implemented_gain_lower_outer':str(full[2]-outer),
                        'implemented_gain_interval':[str(full[2]-up),str(full[2]-lo)]})
        outputs.append(out)
    for r in old:
        if F(r['rho']) in (0,F(1,16),F(1,4)):continue
        i=contexts.index(tuple(r['context']));query(r,'inherited ray holdout',{k:audited[(i,str(F(r['rho'])),k)] for k in ('true','outer')})
    require(len(outputs)==56,'historical heldouts')
    design=read(R/'DESIGN.json')['new_queries'];require(len(new)==len(design)==24,'new query count')
    for r,d in zip(new,design):
        require(all(r[k]==d[k] for k in d),'new design mismatch')
        i=d['context_id'];direction=caches[i][1]['theta'];v=d['theta']
        require(any(direction[a]*v[b]!=direction[b]*v[a] for a in range(3) for b in range(a+1,3)),'new direction not off ray')
        oracle={}
        for kind in ('true','outer','full'):
            m=system(p,r['context'],r['rho'],r['theta'],kind);out=audit(m,r[kind]);oracle[kind]=(m,out)
            max_gap=max(max_gap,out[3]-out[2]);audit_count+=1
        query(r,'new off-ray query',oracle)
    ex=examples();r=new[0]['true'];m=system(p,new[0]['context'],new[0]['rho'],new[0]['theta']);a=normalized(m,r['dual'])
    controls=negative_controls(m,r,a,ex)
    tables=[]
    for family in ('inherited ray holdout','new off-ray query'):
        rows=[r for r in outputs if r['study']==family]
        for rho in sorted(set(r['rho'] for r in rows),key=F):
            rr=[r for r in rows if r['rho']==rho]
            vals={k:mean([F(r[k])-F(r['restricted_lower']) for r in rr]) for k in ('outer_upper','nominal_cache_upper','cache_upper')}
            tables.append({'study':family,'rho':rho,'queries':len(rr),'mean_slack_upper':{k:str(v) for k,v in vals.items()},'display_outward_8dp':{k:rounded(v) for k,v in vals.items()}})
    fresh=[r for r in outputs if r['study']=='new off-ray query']
    summary={'status':'PASS','independence':'standard-library verifier; no historical verifier or optimizer imported',
             'inherited_optimization_records_audited':160,'new_optimization_records_audited':72,'total_optimization_records_audited':audit_count,
             'cached_anchors':24,'inherited_ray_holdouts':56,'new_off_ray_queries':24,'cached_price_evaluations':3*len(outputs),
             'online_restricted_optimization_calls':0,'exact_gap_decompositions':audit_count+len(outputs),
             'exact_moving_geometry_checks':17,'exact_degenerate_face_checks':17,'uniform_cell_certificates':5,'negative_controls_rejected':controls,
             'largest_optimization_bracket':str(max_gap),'new_positive_gain_certificates':sum(F(r['implemented_gain_lower_cached'])>0 for r in fresh),
             'new_cache_tighter_than_outer':sum(F(r['cache_upper'])<F(r['outer_upper']) for r in fresh),
             'new_min_cached_gain_lower':str(min(F(r['implemented_gain_lower_cached']) for r in fresh)),
             'new_mean_cache_slack_upper':str(mean([F(r['cache_upper'])-F(r['restricted_lower']) for r in fresh])),
             'new_mean_outer_slack_upper':str(mean([F(r['outer_upper'])-F(r['restricted_lower']) for r in fresh])),
             'new_mean_gain_certificate_improvement':str(mean([F(r['outer_upper'])-F(r['cache_upper']) for r in fresh])),
             'inherited_anchor_solver_seconds_sum':sum(a['inherited_anchor_solver_seconds'] for c in caches for a in c),
             'new_proposal_solver_seconds_sum':sum(r[k]['solver_seconds'] for r in new for k in ('true','outer','full')),
             'cost_interpretation':'Recorded solver proposals exclude independent audits and do not establish matched-time speedup. All query solves are offline evaluation, not part of the deployed cache function.',
             'tables':tables}
    files={'deployment_cache.json':{'scientific_base':'38f99a5b46d8cfe4f1197fc869735d5f798c499a','contexts':[list(c) for c in contexts],'primitive_sha256':digest(OLD/'radius_primitives.json'),'prices_by_context':caches},
           'query_certificates.json':outputs,'exact_examples.json':ex,'replay.json':summary}
    return files

if __name__=='__main__':
    result=run()
    for name,data in result.items():
        if '--check' in sys.argv:require(read(O/name)==data,'replay file changed '+name)
        else:(O/name).write_text(json.dumps(data,indent=2)+'\n')
    s=result['replay.json'];print(json.dumps({k:v for k,v in s.items() if k!='tables' and not (isinstance(v,str) and len(v)>300)},indent=2))
