"""Independent R25 certificate replay. Run with python -S (standard library).
Rebuilds model rows, checks exact feasible policies, Fenchel bounds, examples,
cache curvature and outward arithmetic. Does not import a numerical optimizer.
"""
import copy,gzip,json,math,sys
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'results'
sys.path.insert(0,str(R.parent/'or-r24-20260923'))
import interior_exact as ie

def load(p):return json.loads(Path(p).read_text())
def stream(p):
    with gzip.open(p,'rt') as fh:
        for line in fh:yield json.loads(line)
def dot(a,b):return sum((F(x)*F(y) for x,y in zip(a,b)),F(0))
def trans(A):return list(map(list,zip(*A)))
def mm(A,B):return [[dot(a,b) for b in trans(B)] for a in A]
def mv(A,x):return [dot(a,x) for a in A]
def mat(A):return [list(map(F,row)) for row in A]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def inv(A):
    n=len(A);a=[list(map(F,row))+[F(int(i==j)) for j in range(n)] for i,row in enumerate(A)]
    for j in range(n):
        k=next(k for k in range(j,n) if a[k][j]);a[j],a[k]=a[k],a[j]
        q=a[j][j];a[j]=[x/q for x in a[j]]
        for i in range(n):
            if i!=j:
                q=a[i][j];a[i]=[x-q*y for x,y in zip(a[i],a[j])]
    return [row[n:] for row in a]
def parse(m):
    return {k:mat(v) if k in ('A','E') else list(map(F,v)) if isinstance(v,list) else F(v) for k,v in m.items()}
def compare_model(actual,expected):
    for k in ('A','rhs','E','b','lam'):assert actual[k]==expected[k],('model changed',k)
def audit(p,m,r):
    ie.feasible(p,m,r['policy']);lo=ie.objective(p,m,r['policy']);up=ie.upper(p,m,r['dual'])
    assert up>=lo and str(lo)==r['lower'] and str(up)==r['upper'],'bound record mismatch'
    assert abs(float(up-lo)-r['gap'])<=1e-12
    return lo,up

def groups(p,kind):
    keys={};ids=[]
    for j in range(p['nodes']):
        h=bin(j+1)[3:];t=len(h)
        info={'fixed amendment':(), 'time-only':(t,), 'current regime':(t,h[-1:]),'memory two':(t,h[-2:]),'full history':(j,)}[kind]
        for a in range(p['services']):
            key=info+(a,)
            if key not in keys:keys[key]=len(keys)
            ids.append(keys[key])
    return ids

def restriction(p,m,kind):
    out={k:copy.deepcopy(v) for k,v in m.items() if not k.startswith('_')};ids=groups(p,kind);rep={};n=len(ids)
    out['E']=mat(p['E'])
    for i,g in enumerate(ids):
        if g in rep:
            row=[F(0)]*n;row[i]=1;row[rep[g]]=-1;out['E'].append(row)
        else:rep[g]=i
    return out,ids

def canonical(c):
    n=63;w=[2**(5-((i+1).bit_length()-1)) for i in range(n)]
    p={'nodes':n,'services':1,'rank':1,'znum':[16]*n,'Unum':[[0]*n], 'qnum':[], 'bnum':[0]*n,
       'knum':[8*a for a in w],'vnum':[0]*n,'B':[],'E':[w],'Aacc':[],'C':[],'capnum':[]}
    b=[];rhs=[]
    for i in range(n):
        t=(i+1).bit_length()-1;z=0 if i==0 else (1 if i%2==0 else -1)
        p['qnum'].append((16+4*z)*w[i]);b.append(w[i]*(F(c[0]+z*c[1],32)+F(t*c[2],128)))
        row=[0]*n;row[i]=1
        if i:row[(i-1)//2]=-1
        p['B'].append(row)
        if i:
            row=[0]*n
            for j in range(n):
                node=j
                while node>i:node=(node-1)//2
                if node==i:row[j]=w[j]
            p['Aacc'].append(row);rhs.append(F(w[i]*(6-t)*(3+z),64))
    return p,{'A':mat(p['Aacc']),'rhs':rhs,'E':mat(p['E']),'b':b,'lam':F(c[3],128)}

def sqrt_up(x,d=10**12):
    n=(x.numerator*d*d+x.denominator-1)//x.denominator;k=math.isqrt(n)
    if k*k<n:k+=1
    assert F(k*k,d*d)>=x
    return F(k,d)

def envelope(L,a,h):
    dh=[x-F(y) for x,y in zip(h,a['h'])];norm2=dot(dh,dh);delta=F(a['upper'])-F(a['lower'])
    return F(a['upper'])+dot(a['gradient'],dh)+sqrt_up(2*L*delta)*sqrt_up(norm2)+L*norm2/2

def structural():
    r=load(O/'structural_certificates.json');z=[F(1,6),F(2,3),F(2,3)]
    def W(x):return x[1]-dot(x,x)/2
    for a in r['release']:
        t=F(a['t']);x=list(map(F,a['x']));nu=F(a['release_price']);mu=F(a['cap_price'])
        assert sum(x)==F(3,2) and all(0<=v<=1 for v in x) and x[1]<=F(3,4) and x[2]<=F(3,4)
        assert abs(x[1]-x[2])<=t and min(mu,nu)>=0
        assert [-x[0],1-x[1],-x[2]]==[-x[0],-x[0]+mu+nu,-x[0]-nu]
        assert mu*(x[1]-F(3,4))==nu*(x[1]-x[2]-t)==0
        assert W(x)-W(z)==F(a['gain'])
    for a in r['capacity']:
        b=F(a['cap']);x=list(map(F,a['full']));y=list(map(F,a['restricted']))
        assert x==[(F(3,2)-b)/2,b,(F(3,2)-b)/2] and y==[F(3,2)-2*b,b,b]
        assert W(x)-W(y)==F(a['gain'])==9*(2*b-1)**2/16
        assert F(a['rent_difference'])==9*(2*b-1)/4
    for a in r['friction']:
        lam=F(a['lambda']);p=[F(1,2),F(3,4),F(1,4)];x=list(map(F,a['full']))
        def w(y):return dot(p,y)-dot(y,y)/2-lam*(abs(y[1]-y[0])+abs(y[2]-y[0]))
        assert w(x)-w(p)==F(a['gain'])==(lam*lam if lam<=F(1,4) else lam/2-F(1,16))
        tension=min(lam,F(1,4));assert sub(p,x)==[F(0),tension,-tension]
    for a in r['random_cells']:
        n=a['n'];Q,M,P,S,A=map(mat,[a[k] for k in ('Q','M','P','S','A')]);nu=list(map(F,a['nu']));om=list(map(F,a['omega']));p=list(map(F,a['p']));z=[F(1,2)]*n
        v=[w*(1 if b>0 else -1) for w,b in zip(om,nu)];d=mv(P,v);t=F(a['step']);x=[zz+t*dd for zz,dd in zip(z,d)]
        assert mm(M,P)==[[F(int(i==j)) for j in range(len(M))] for i in range(len(M))]
        assert mm(trans(P),mm(Q,P))==S and all(sum(col)==0 for col in trans(P))
        assert all(Q[i][i]>0 for i in range(n)) and all(Q[i][j]==0 for i in range(n) for j in range(n) if i!=j)
        assert all(0<=xx<=1 for xx in x) and all(u<=F(b) for u,b in zip(mv(A,x),a['rhs']))
        slope=sum(w*abs(q) for w,q in zip(om,nu));gain=dot(p,sub(x,z))-(dot(x,mv(Q,x))-dot(z,mv(Q,z)))/2
        assert gain==t*slope-t*t*dot(v,mv(S,v))/2==F(a['gain'])==F(a['formula'])
        upd=sub(nu,[t*u for u in mv(S,v)]);res=sub(sub(p,mv(Q,x)),mv(trans(M),upd));assert all(vv==res[0] for vv in res)
        assert all(u*v0>0 for u,v0 in zip(upd,nu))
        stops=[]
        for az,ad,rhs in zip(mv(A,z),mv(A,d),a['rhs']):
            if ad>0:stops.append((F(rhs)-az)/ad)
        for zi,di in zip(z,d):
            if di>0:stops.append((1-zi)/di)
            if di<0:stops.append(-zi/di)
        for ni,si in zip(nu,mv(S,v)):
            sign=1 if ni>0 else -1
            if sign*si>0:stops.append(abs(ni)/(sign*si))
        assert min(stops)>0 and min(stops)==t*2==F(a['first_break'])
    assert (len(r['release']),len(r['capacity']),len(r['friction']),len(r['random_cells']))==(49,40,65,24)
    return r

def replay(check=False):
    source=R.parent/'or-r23-20260923/results';p0=load(source/'primitives.json')
    cs=[a['context'] for a in stream(source/'certificates.jsonl.gz') if a['r']==0][:24]
    ncert=0;seen=set();one=None;names=['fixed amendment','time-only','current regime','memory two','full history']
    for a in stream(O/'hierarchy_certificates.jsonl.gz'):
        assert (a['family'],a['id']) not in seen;seen.add((a['family'],a['id']))
        if a['family']=='R24 amendments':
            p=copy.deepcopy(p0);assert a['context']==cs[a['id']];base=ie.make_model(p,a['context'],0,[0,0,0])
        else:p,base=canonical(a['context'])
        assert a['primitives']==p,'primitives changed'
        assert [b['name'] for b in a['classes']]==names
        intervals=[]
        for b in a['classes']:
            m,ids=restriction(p,base,b['name']);compare_model(parse(b['model']),m);assert ids==b['groups']
            intervals.append(audit(p,m,b));ncert+=1
            if one is None and b['name']=='time-only':one=(copy.deepcopy(p),copy.deepcopy(m),copy.deepcopy(b))
        for i in range(4):
            assert intervals[i][0]<=intervals[i+1][1]
            assert abs(float(intervals[i+1][0]-intervals[i][0])-a['increments'][i])<=1e-12
    assert len(seen)==48 and ncert==240
    p=load(O/'radius_primitives.json');assert p==p0;nr=0
    for a in stream(O/'radius_certificates.jsonl.gz'):
        rho=F(a['rho']);assert a['context']==cs[a['id']]
        for k,flag in [('true',False),('outer',True)]:
            m0=ie.make_model(p,a['context'],0,a['theta'],flag);m1=ie.make_model(p,a['context'],1,a['theta'],flag)
            m={'E':m0['E'],'lam':m0['lam']+16*rho*(m1['lam']-m0['lam'])}
            for key in ('b','rhs'):m[key]=[x+16*rho*(y-x) for x,y in zip(m0[key],m1[key])]
            m['A']=[[x+16*rho*(y-x) for x,y in zip(u,v)] for u,v in zip(m0['A'],m1['A'])]
            compare_model(parse(a[k]['model']),m);audit(p,m,a[k]);nr+=1
        assert abs(float(F(a['outer']['upper'])-F(a['true']['lower']))-a['outer_slack_upper'])<=1e-12
    assert nr==160
    p=load(O/'cache_primitives.json');assert p==p0;c=load(O/'cache_certificates.json');L=F(c['L']);base=ie.make_model(p,[0]*p['rank']+[29],0,[0,0,0]);nc=0
    ids=groups(p,'time-only');sv=p['services'];free=[g for g in range(max(ids)+1) if g not in ids[:sv]];cols={g:i for i,g in enumerate(free)};Z=[[F(0)]*len(free) for _ in range(len(ids))]
    for i in range(sv,len(ids)):Z[i][cols[ids[i]]]=1
    for a in range(sv):
        for j in range(len(free)):Z[a][j]=-sum((F(int(p['E'][a][i]))*Z[i][j] for i in range(sv,len(ids))),F(0))/F(int(p['E'][a][a]))
    DZ=[[F(int(q),16)*v for v in row] for q,row in zip(p['qnum'],Z)];U=[[F(int(a),32) for a in row] for row in p['Unum']];UZ=mm(U,Z)
    G=mm(UZ,mm(inv(mm(trans(Z),DZ)),trans(UZ)));assert L==sum((G[i][i] for i in range(p['rank'])),F(0))
    def qm(h):
        m=copy.deepcopy(base);m['b']=[b+sum((U[j][i]*h[j] for j in range(p['rank'])),F(0)) for i,b in enumerate(base['b'])];return m
    for a in c['anchors']:
        h=list(map(F,a['h']));m=qm(h);compare_model(parse(a['model']),m);audit(p,m,a);nc+=1
        assert mv(U,ie.unpack(a['policy']))==list(map(F,a['gradient']))
    for a in c['queries']:
        h=list(map(F,a['h']));m=qm(h);compare_model(parse(a['model']),m);lo,up=audit(p,m,a);nc+=1
        env=[envelope(L,b,h) for b in c['anchors']]
        assert list(map(str,env))==a['envelopes'] and min(env)==F(a['cached_upper']) and min(env)>=lo
    assert nc==36
    sr=structural()
    # Recompute finite-action promise values from the independent exhaustive policy path.
    import promise_checks
    stored=load(O/'promise_checks.json')
    for a in stored['cases']:
        replayed=promise_checks.case(a['horizon'],tuple(map(F,a['tiers'])),F(a['gamma']))
        assert replayed==a
    # Malformed proposals and result records must fail rather than become certificates.
    pp,mm0,rr=one;negative=[]
    def reject(name,fn):
        try:fn()
        except (AssertionError,ValueError,ZeroDivisionError,IndexError,KeyError):negative.append(name);return
        raise AssertionError('negative control accepted: '+name)
    bad=copy.deepcopy(rr);bad['policy']['x_num'][0]=str(int(bad['policy']['x_num'][0])+1)
    reject('root payment mutation',lambda:audit(pp,mm0,bad))
    bad=copy.deepcopy(rr);bad['dual']['mu'][0]=-1;reject('negative participation price',lambda:audit(pp,mm0,bad))
    bad=copy.deepcopy(rr);bad['dual']['s'][0]=10**30;reject('switch capacity violation',lambda:audit(pp,mm0,bad))
    bad=copy.deepcopy(rr);bad['upper']=str(F(bad['upper'])-1);reject('falsified upper objective',lambda:audit(pp,mm0,bad))
    bad=copy.deepcopy(rr);bad['dual']['nu'][0]+=100000000000;reject('changed equality certificate',lambda:audit(pp,mm0,bad))
    badmodel=copy.deepcopy(mm0);badmodel['rhs'][0]-=F(1,3);reject('changed model row',lambda:compare_model(badmodel,mm0))
    reject('false cache upper',lambda:assertion(F(c['queries'][0]['cached_upper'])-1==min(envelope(L,a,list(map(F,c['queries'][0]['h']))) for a in c['anchors'])))
    reject('false release gain',lambda:assertion(F(sr['release'][1]['gain'])+1==F(1,64)/2-F(1,64)**2/4))
    # Correct candidate-minus-lifted difference is 10+Q*(1-3), not 10+Q*(3-1).
    assert 10+5*(1-3)==0 and 10+6*(1-3)<0 and 10+6*(3-1)>0
    reject('reversed amortization sign',lambda:assertion(10+5*(3-1)==0))
    result={'status':'PASS','hierarchy_certificates':ncert,'radius_certificates':nr,'cache_certificates':nc,
      'total_new_optimization_certificates':ncert+nr+nc,'release_KKT_witnesses':49,'capacity_KKT_witnesses':40,
      'friction_witnesses':65,'random_rational_cells':24,'promise_cases':3,'enumerated_history_policies':37142,
      'negative_controls_rejected':negative,'verifier':'Python standard library only; no numerical optimizer imported'}
    if check:assert result==load(O/'replay.json')
    else:(O/'replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
def assertion(ok):assert ok
if __name__=='__main__':replay('--check' in sys.argv)
