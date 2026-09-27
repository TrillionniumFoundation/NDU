#!/usr/bin/env python3
"""Independent standard-library rational verifier. Does not import the generator."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import copy, hashlib, json, re, sys
R=Path(__file__).resolve().parent

def decode(x):
    if isinstance(x,str) and re.fullmatch(r'-?\d+(?:/\d+)?',x): return Q(x)
    if isinstance(x,list): return [decode(t) for t in x]
    if isinstance(x,dict): return {k:decode(v) for k,v in x.items()}
    return x

def dot(a,b): return sum((x*y for x,y in zip(a,b)),Q(0))
def clamp(x,l=Q(0),u=Q(1)): return min(u,max(l,x))
def conjugate(d,h):
    candidates=[Q(0),Q(1)]
    if 0<=d/h<=1: candidates.append(d/h)
    return max(d*x-h*x*x/2 for x in candidates)
def linear(matrix,rhs):
    a=[list(map(Q,row))+[Q(b)] for row,b in zip(matrix,rhs)]; n=len(a)
    assert all(len(row)==n+1 for row in a)
    for c in range(n):
        pivot=next((i for i in range(c,n) if a[i][c]),None)
        assert pivot is not None, 'singular basis'
        a[c],a[pivot]=a[pivot],a[c]; scale=a[c][c]; a[c]=[v/scale for v in a[c]]
        for i in range(n):
            if i!=c:
                z=a[i][c]; a[i]=[v-z*w for v,w in zip(a[i],a[c])]
    return [a[i][-1] for i in range(n)]

def tree_value(x): return x[0]-x[0]*x[0]/2+x[2]-(x[1]*x[1]+x[2]*x[2])/4

def tree_opt(delta):
    H=[Q(1),Q(1,2),Q(1,2)]; p=[Q(1),Q(0),Q(1)]
    A=[[-1,0,0],[0,-1,0],[0,0,-1],[1,0,0],[0,1,0],[0,0,1],[0,-1,1],[0,1,-1]]
    b=[Q(0)]*3+[Q(1),Q(2,5),Q(4,5),2*delta,2*delta]
    sols=[]
    for k in range(3):
        for active in combinations(range(8),k):
            B=[[Q(1),Q(1,2),Q(1,2)]]+[list(map(Q,A[i])) for i in active]
            c=[Q(1)]+[b[i] for i in active]; n=3+len(B)
            mat=[[Q(0)]*n for _ in range(n)]
            for i in range(3):
                mat[i][i]=H[i]
                for j in range(len(B)): mat[i][3+j]=mat[3+j][i]=B[j][i]
            try: solution=linear(mat,p+c)
            except AssertionError: continue
            x=solution[:3]
            if any(dot(row,x)>v for row,v in zip(A,b)) or any(m<0 for m in solution[4:]): continue
            sols.append((tree_value(x),x))
    assert sols and len({tuple(x) for _,x in sols})==1
    return sols[0]

def check_bridge(record):
    d=record['delta']; x=record['x']; value,z=tree_opt(d)
    assert x==z and record['value']==value
    u=record['table']; assert u[0]==x[0] and abs(x[1]-u[1])<=d and abs(x[2]-u[1])<=d
    assert x[0]+(x[1]+x[2])/2==1
    eta,t=record['eta'],record['t']; ml,mh=record['mu']
    assert t>=0 and ml>=0 and mh>=0
    assert t*(2*d-x[2]+x[1])==0 and ml*(Q(2,5)-x[1])==0 and mh*(Q(4,5)-x[2])==0
    expected=[]
    for reward,cap,mu,rp,rm,tier in [(Q(0),Q(2,5),ml,Q(0),2*t,x[1]),(Q(2),Q(4,5),mh,2*t,Q(0),x[2])]:
        chi=2*mu; etach=eta+chi; dd=reward-etach-rp+rm
        assert conjugate(dd,Q(1))==dd*tier-tier*tier/2
        expected.append(dict(chi=chi,eta=etach,B=etach-chi,gamma=rp-rm,k=rp+rm,C=conjugate(dd,Q(1))+chi*cap,d=dd))
    assert expected==record['children']
    assert conjugate(1-eta,Q(1))==(1-eta)*x[0]-x[0]*x[0]/2
    plane=dict(B=eta,gamma=(expected[0]['gamma']+expected[1]['gamma'])/2,k=2*t,C=conjugate(1-eta,Q(1))+(expected[0]['C']+expected[1]['C'])/2)
    assert plane==record['plane'] and plane['gamma']==0
    assert value==plane['B']+plane['C']+plane['k']*d==record['upper']

def primitive(q,bid,unstable):
    d=len(q)
    z=dot([Q(((bid+1)*(j+2))%7-3,3) for j in range(d)],q)/d
    z2=dot([Q(((bid+4)*(j+5))%9-4,4) for j in range(d)],q)/d
    return {'p0':1+z/8,'rl':Q(1,5)+z2/4,'rh':Q(9,5)+z/2,'al':1+z/8,'ah':1-z/10,'bl':Q(1,2)+q[0]/5+z2/20 if unstable else Q(7,20)+z2/30,'bh':Q(1,2)-q[0]/5-z2/20 if unstable else Q(7,10)-z2/30}

def objective(m,x):
    return dot([m['p0'],m['rl']/2,m['rh']/2],x)-dot([Q(1),Q(1,2),Q(1,2)],[v*v for v in x])/2

def feasible(m,x,pool=False):
    assert len(x)==3 and all(0<=v<=1 for v in x)
    assert dot([Q(1),Q(1,2),Q(1,2)],x)==1
    assert m['al']*x[1]<=m['bl'] and m['ah']*x[2]<=m['bh']
    if pool: assert x[1]==x[2]

def dual(m,a,z):
    assert a['ml']>=0 and a['mh']>=0
    dd=[m['p0']-a['nu'],m['rl']/2-a['nu']/2-a['xi']-m['al']*a['ml'],m['rh']/2-a['nu']/2+a['xi']-m['ah']*a['mh']]
    hs=[Q(1),Q(1,2),Q(1,2)]
    coordinate=[conjugate(v,h)-v*x+h*x*x/2 for v,h,x in zip(dd,hs,z)]
    participation=[a['ml']*(m['bl']-m['al']*z[1]),a['mh']*(m['bh']-m['ah']*z[2])]
    assert all(v>=0 for v in coordinate+participation)
    u=a['nu']+a['ml']*m['bl']+a['mh']*m['bh']+sum((conjugate(v,h) for v,h in zip(dd,hs)),Q(0))
    assert u-objective(m,z)==sum(coordinate+participation,Q(0))
    return u

def exact_restricted(m):
    v0=(1-m['p0']+(m['rl']+m['rh'])/2)/2
    cl,ch=m['bl']/m['al'],m['bh']/m['ah']; v=clamp(v0,Q(0),min(cl,ch)); assert 0<v<1
    x=[1-v,v,v]; feasible(m,x,True)
    nu=m['p0']-x[0]; price=2*(v0-v)
    ml=price/m['al'] if cl<=ch else Q(0); mh=price/m['ah'] if cl>ch else Q(0)
    xi=m['rl']/2-nu/2-v/2-m['al']*ml
    a=dict(nu=nu,xi=xi,ml=ml,mh=mh)
    assert dual(m,a,x)==objective(m,x)
    return x,a,'interior' if price==0 else ('low' if cl<=ch else 'high')

def full_kkt(m,x):
    feasible(m,x); assert 0<x[0]<1
    eta=m['p0']-x[0]
    for reward,tier,cap in [(m['rl'],x[1],m['bl']/m['al']),(m['rh'],x[2],m['bh']/m['ah'])]:
        assert tier==clamp(reward-eta,Q(0),cap)

COUNTS={'initial_block_anchors':0,'query_block_policies':0,'cached_block_evaluations':0,'refresh_queries':0,'queries':0}
def check_scaling(case):
    cfg=case['config']; blocks=cfg['cycles']*cfg['services']; assert blocks==case['blocks'] and case['n']==3*blocks
    assert case['tolerance']==Q(blocks,1000)
    cache=copy.deepcopy(case['initial_cache']); assert len(cache)==cfg['cache']; previous=None
    for c in cache:
        assert len(c['x'])==len(c['prices'])==blocks
        for j in range(blocks):
            m=primitive(c['theta'],j,cfg['unstable']); feasible(m,c['x'][j],True)
            assert dual(m,c['prices'][j],c['x'][j])==objective(m,c['x'][j]); COUNTS['initial_block_anchors']+=1
    for r in case['records']:
        assert r['theta']==[Q(((r['index']+3)*(j*7+5)+j*j*3)%19-9,9) for j in range(cfg['d'])]
        ms=[primitive(r['theta'],j,cfg['unstable']) for j in range(blocks)]
        opt=[exact_restricted(m) for m in ms]; kval=sum((objective(m,a[0]) for m,a in zip(ms,opt)),Q(0))
        assert kval==r['reference']; faces=[x[2] for x in opt]; assert faces==r['faces']
        assert r['face_changes']==(0 if previous is None else sum(x!=y for x,y in zip(faces,previous))); previous=faces
        vals=[]
        for c in cache:
            vals.append(sum((dual(m,a,o[0]) for m,a,o in zip(ms,c['prices'],opt)),Q(0)))
            COUNTS['cached_block_evaluations']+=blocks
        best=min(range(len(vals)),key=vals.__getitem__); u=vals[best]
        assert u==r['pre_upper'] and best==r['best_anchor']
        witness=[]
        for m,x in zip(ms,cache[best]['x']):
            v=min(x[1],m['bl']/m['al'],m['bh']/m['ah']); y=[1-v,v,v]; feasible(m,y,True); witness.append(y)
        low=sum((objective(m,x) for m,x in zip(ms,witness)),Q(0)); assert low==r['witness_lower']
        trigger=u-low>case['tolerance']; assert trigger==r['refresh']
        for m,x in zip(ms,r['candidate']): full_kkt(m,x); COUNTS['query_block_policies']+=1
        assert len(r['candidate'])==blocks and sum((objective(m,x) for m,x in zip(ms,r['candidate'])),Q(0))==r['full_value']>=kval
        if trigger:
            cache.append(dict(theta=r['theta'],x=[x[0] for x in opt],prices=[x[1] for x in opt])); cache=cache[-cfg['cache']:]
            assert r['used_upper']==kval and r['refresh_ns']>=r['fresh_ns']; COUNTS['refresh_queries']+=1
        else: assert r['used_upper']==u and r['refresh_ns']==0
        assert 0<=r['used_upper']-kval<=case['tolerance']
        assert all(isinstance(r[k],int) and r[k]>=0 for k in ['coeff_ns','candidate_ns','audit_ns','cache_ns','witness_ns','fresh_ns','refresh_ns'])
        COUNTS['queries']+=1

NEG=[]
def reject(name,fn):
    try: fn()
    except AssertionError: NEG.append(name); return
    raise AssertionError('negative control was not rejected: '+name)
def require(x): assert x

def supplemental_tests():
    # Two nonconstant table planes: exact root LP at u=1/2, not branchwise table choice.
    p1=lambda u:u-Q(1,8); p2=lambda u:Q(7,8)-u
    roots=[Q(0),Q(1),Q(1,2)]; assert max(min(p1(u),p2(u)) for u in roots)==Q(3,8)
    # Uniform nonconstant policy: feasibility and objective are recomputed from primitives.
    vs=[Q(1,8),Q(3,8)]; pol=lambda t:[Q(1,2)+3*t/4,Q(1,2)-3*t/4]
    A=lambda t:[1+t,1-t]; b=lambda t:1+t
    coeff=[b(vs[0])-dot(A(vs[0]),pol(vs[0])),(b(vs[0])+b(vs[1])-dot(A(vs[0]),pol(vs[1]))-dot(A(vs[1]),pol(vs[0])))/2,b(vs[1])-dot(A(vs[1]),pol(vs[1]))]
    assert min(coeff)>=0
    def W(t):
        x=pol(t); assert sum(x)==1 and all(0<=a<=1 for a in x)
        return dot([1+t,1-t],x)-dot(x,x)/2-t*abs(x[0]-x[1])/4
    nu,xi=Q(1,2),Q(3,32)
    def U(t): return nu+conjugate(1+t-nu-xi-t/4,Q(1))+conjugate(1-t-nu+xi+t/4,Q(1))
    def chord(t): return ((vs[1]-t)*U(vs[0])+(t-vs[0])*U(vs[1]))/(vs[1]-vs[0])
    f=lambda t:W(t)-chord(t)
    mid=sum(vs)/2; gains=[f(vs[0]),2*f(mid)-(f(vs[0])+f(vs[1]))/2,f(vs[1])]
    assert gains==[Q(9,1024),Q(9,1024),Q(45,1024)]
    assert tree_opt(Q(1,15))[0]-Q(1,15)==Q(56,75)
    assert Q(56,75)-Q(37,50)==Q(1,150)
    # Exact active-face KKT check and transition rejection.
    H=[Q(1),Q(1,2),Q(1,2)]; B=[[Q(1),Q(1,2),Q(1,2)],[Q(0),Q(1),Q(-1)],[Q(0),Q(1),Q(0)]]
    mat=[[Q(0)]*6 for _ in range(6)]
    for i in range(3):
        mat[i][i]=H[i]
        for j in range(3): mat[i][3+j]=mat[3+j][i]=B[j][i]
    good=linear(mat,[1,0,1,1,0,Q(1,3)])
    assert good[:3]==[Q(2,3),Q(1,3),Q(1,3)] and good[-1]>=0
    bad=linear(mat,[1,0,1,1,0,Q(2,3)])
    reject('retained low-cap face violates changed high cap',lambda:require(bad[2]<=Q(1,3)))
    reject('singular dependent active basis',lambda:linear([[1,1],[1,1]],[1,1]))
    reject('endpoint-only adaptive feasibility',lambda:require(Q(-1,2)>=0))
    reject('adaptive midpoint violation hidden by vertices',lambda:require(Q(1,2)*(1-Q(1,2))<=0))
    reject('independent child tables mislabeled as common table',lambda:require(Q(0)==Q(4,5)))
    reject('false pooled value from childwise reoptimization',lambda:require(tree_opt(Q(0))[0]==Q(53,50)))
    reject('incorrect release factor one instead of two',lambda:require(Q(1,5)<=Q(1,10)))
    reject('unpriced continuation cap overstates accepted witness',lambda:require(Q(1,2)<=Q(2,5)))
    return dict(adaptive_gain=str(min(gains)),adaptive_bernstein=[str(x) for x in gains],design_release='1/15',design_net_value='56/75',shared_table_value='37/50',unrestricted_value='53/50',master_lp_value='3/8',face_tests=3)

def main():
    raw=(R/'results/evidence.json').read_bytes(); data=decode(json.loads(raw)); assert data['schema']=='ndu-or-r28-exact-v1'
    for row in data['bridge']: check_bridge(row)
    for a in data['bridge']:
        for b in data['bridge']:
            p=a['plane']; assert p['B']+p['C']+p['k']*b['delta']>=b['value']
    for case in data['scaling']:
        check_scaling(case)
        print('verified scaling n=',case['n'],'cache=',case['config']['cache'],file=sys.stderr,flush=True)
    extra=supplemental_tests()
    broken=copy.deepcopy(data['bridge'][1]); broken['plane']['k']+=1
    reject('corrupt recursive release coefficient',lambda:check_bridge(broken))
    broken2=copy.deepcopy(data['bridge'][1]); broken2['children'][0]['chi']*=2
    reject('incorrect conditional price normalization',lambda:check_bridge(broken2))
    m=primitive([Q(0)],0,False); x,a,_=exact_restricted(m)
    aa=dict(a); aa['ml']=Q(-1)
    reject('negative cached continuation price',lambda:dual(m,aa,x))
    xx=x.copy();xx[0]+=Q(1,100)
    reject('broken root promise witness',lambda:feasible(m,xx,True))
    xx=x.copy();xx[1]=Q(1)
    reject('infeasible continuation witness',lambda:feasible(m,xx,True))
    reject('unverified tolerance claim',lambda:require(Q(1,10)<=Q(1,1000)))
    summary=dict(status='PASS',evidence_sha256=hashlib.sha256(raw).hexdigest(),bridge_exact_records=len(data['bridge']),cross_release_support_tests=len(data['bridge'])**2,scaling_configurations=len(data['scaling']),negative_controls=len(NEG),rejected_controls=NEG,counts=COUNTS,exact_results=extra,limitations=['Synthetic block-separable stress design; not a dense-QP speed comparison.','Timing observations are not replayed as performance claims.','The verifier checks finite fixtures and certificate arithmetic, not mathematical novelty or all possible models.'])
    path=R/'results/replay.json'; text=json.dumps(summary,indent=2,sort_keys=True)+'\n'
    if '--check' in sys.argv: assert json.loads(path.read_text())==summary
    else: path.write_text(text)
    print(text)
if __name__=='__main__': main()
