#!/usr/bin/env python3
"""Independent, standard-library rational replay; no optimizer is imported.
Checks the recursive proof witnesses, not merely reported solver statuses.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse, copy, hashlib, json
R=Path(__file__).resolve().parent
SCALE=10**12

def require(ok,msg):
    if not ok:raise ValueError(msg)
def cv(obj):
    if isinstance(obj,str):
        try:return F(obj)
        except ValueError:return obj
    if isinstance(obj,list):return [cv(x) for x in obj]
    if isinstance(obj,dict):return {k:cv(v) for k,v in obj.items()}
    return obj

def simplex(mix,n):
    require(bool(mix),'empty mixture')
    require(len({i for i,w in mix})==len(mix),'duplicate mixture index')
    require(all(isinstance(i,int) and 0<=i<n and w>=0 for i,w in mix),'mixture index or sign')
    require(sum(w for i,w in mix)==1,'mixture normalization')

def qsupport(v,d):
    require(d>0,'positive curvature')
    x=max(F(0),min(F(1),v/d))
    return v*x-d*x*x/2

def width(node,m):
    result=F(0)
    for i in range(m):
        for j in range(m):
            a=i*(m+1)+j;b=a+1;c=(i+1)*(m+1)+j;d=c+1
            for inds in ((a,b,d),(a,c,d)):
                ub=min(max(h['A']*node['anchors'][k]['q']+h['B']*node['anchors'][k]['b']+h['C']-node['anchors'][k]['value'] for k in inds) for h in node['planes'])
                require(ub>=0,'negative global bracket')
                result=max(result,ub)
    return result

def verify(data,full_crosscheck=True):
    d=cv(data);T=d['T'];m=d['m'];levels=d['levels'];model=d['model'];beta=d['beta']
    require(0<beta<=1 and len(levels)==T+1 and len(model)==T,'dimensions or discount')
    count=planes=0
    for terminal in levels[-1]:
        require(terminal['L']==terminal['U']==0,'terminal domain')
        require(terminal['anchors']==[{'q':F(0),'b':F(0),'value':F(0)},{'q':F(1),'b':F(0),'value':F(0)}],'terminal anchors')
        require(terminal['planes']==[{'A':F(0),'B':F(0),'C':F(0)}],'terminal plane')
    for t in reversed(range(T)):
        for z,node in enumerate(levels[t]):
            p=model[t][z];child=levels[t+1];pr=p['P'];a=p['a'];r=p['r'];cur=p['d'];ell=p['ell']
            require(p['beta']==beta and a>0 and cur>0 and ell>=0,'model sign or discount')
            require(len(pr)==len(child) and all(v>0 for v in pr) and sum(pr)==1,'transition row')
            L=beta*sum(w*ch['L'] for w,ch in zip(pr,child));U=min(p['cap'],a+beta*sum(w*ch['U'] for w,ch in zip(pr,child)))
            require(node['L']==L==0 and node['U']==U and U>0,'exact promise interval')
            require(len(node['anchors'])==(m+1)**2 and bool(node['planes']),'grid coverage')
            for k,an in enumerate(node['anchors']):
                i,j=divmod(k,m+1);q=an['q'];b=an['b'];x=an['x']
                require(q==F(i,m) and b==U*F(j,m),'grid coordinates')
                require(0<=x<=1 and L<=b<=U,'primal domain')
                require(len(an['children'])==len(child),'child count')
                pay=a*x;reward=r*x-cur*x*x/2-ell*abs(x-q)
                for jj,(ch,mix) in enumerate(zip(child,an['children'])):
                    simplex(mix,len(ch['anchors']))
                    require(sum(w*ch['anchors'][idx]['q'] for idx,w in mix)==x,'inherited-tier consistency')
                    bj=sum(w*ch['anchors'][idx]['b'] for idx,w in mix)
                    require(ch['L']<=bj<=ch['U'],'child participation cap')
                    pay+=beta*pr[jj]*bj
                    reward+=beta*pr[jj]*sum(w*ch['anchors'][idx]['value'] for idx,w in mix)
                require(pay==b,'exact promise equation')
                require(an['value']==F((reward*SCALE).__floor__(),SCALE),'lower rounding or value')
                count+=1
            for h in node['planes']:
                s,eta=h['A'],h['B'];require(-ell<=s<=ell,'switching-price capacity')
                require(len(h['children'])==len(child),'dual child count')
                av=[]
                for ch,mix in zip(child,h['children']):
                    simplex(mix,len(ch['planes']))
                    av.append({k:sum(w*ch['planes'][idx][k] for idx,w in mix) for k in ('A','B','C')})
                v=r-s-a*eta+beta*sum(w*h0['A'] for w,h0 in zip(pr,av))
                cc=qsupport(v,cur)+beta*sum(w*(h0['C']+max((h0['B']-eta)*ch['L'],(h0['B']-eta)*ch['U'])) for w,h0,ch in zip(pr,av,child))
                require(h['C']==F((cc*SCALE).__ceil__(),SCALE),'global conjugate bound or outward rounding')
                if full_crosscheck:
                    require(all(h['A']*an['q']+h['B']*an['b']+h['C']>=an['value'] for an in node['anchors']),'cross-envelope bracket')
                planes+=1
            require(node['width']==width(node,m),'triangle certificate')
    su=d['summary'];root=max(node['width'] for node in levels[0])
    require(su['anchors']==count and su['planes']==planes and su['max_root_width']==root and su['full_binary_tree_nodes']==2**T-1,'reported summary')
    return {'horizon':T,'grid_subdivisions':m,'anchors':count,'dual_planes':planes,'uniform_root_gap':str(root),'uniform_root_gap_decimal':float(root),'not_materialized_history_nodes':2**T-1}

def exact_information():
    # Promise-state omission: all probabilities, caps, and optimizers are exact.
    x=[F(1),F(1,2),F(1,2),F(1,4),F(3,4)]
    z=[F(1),F(1,4),F(3,4),F(1,2),F(1,2)];w=[F(1)]+[F(1,2)]*4
    def W(v):return (v[1]-v[2])/8-sum(a*b*b for a,b in zip(w,v))/2
    for v in (x,z):
        require(all(0<=a<=1 for a in v),'example box')
        require(v[0]+(v[1]+v[2]+v[3]+v[4])/2==2,'example root')
        require(v[1]+v[3]==F(3,4) and v[2]+v[4]==F(5,4),'example continuation budgets')
    # Branch budgets are forced; equality of marginal rewards solves each pair.
    require(F(1,4)-x[1]==-x[3] and -F(1,4)-x[2]==-x[4],'full marginal equality')
    require(x[1]==x[2]==F(1,2),'same inherited tier at terminal histories')
    require(z[3]==z[4]==F(1,2),'restricted pooling')
    # Restricted value is -35/32+c-c^2 on c in [1/4,3/4].
    require(W(z)==-F(35,32)+F(1,2)-F(1,4),'restricted quadratic optimum')
    gain=W(x)-W(z);require(gain==F(1,16),'promise gain')
    dispersion=sum(F(1,2)*(v-F(1,2))**2 for v in (x[3],x[4]));require(dispersion/2==F(1,32),'dispersion lower bound')
    # Inherited-tier omission: exact one-dimensional convex objective and kinks.
    def cost(q,v):return (v*v+(1-v)**2)/2+F(3,2)*abs(v-q)+F(1,2)*abs(1-2*v)
    for q,v in ((F(0),F(1,4)),(F(1),F(3,4))):
        require(cost(q,v)==F(15,16),'tier-aware value')
        # Piecewise quadratic minima occur at these stationary points or kinks.
        candidates=[F(0),F(1,4),F(1,2),F(3,4),F(1)]
        require(all(cost(q,v)<=cost(q,c) for c in candidates),'tier optimality cells')
    require((cost(F(0),F(1,2))+cost(F(1),F(1,2)))/2==1,'tier-blind optimum')
    # A positive certificate despite a deliberately inexact full policy.
    eps=F(1,128);v=F(1,16)
    require(v>2*eps,'strict inexact-policy dispersion margin')
    return {'promise_aware_value':str(W(x)),'regime_only_value':str(W(z)),'promise_omission_gain':'1/16','curvature_lower_bound':'1/32','tier_aware_value':'-15/16','tier_blind_value':'-1','tier_omission_gain':'1/16','finite_action_mixing_counterexample':'{0,1} has no feasible action at exact one-period promise 1/2'}

def negative_controls(raw):
    tests=[]
    def reject(name,edit):
        d=copy.deepcopy(raw);edit(d)
        try:verify(d,False)
        except (ValueError,IndexError,KeyError,ZeroDivisionError):tests.append(name);return
        raise AssertionError('negative control accepted: '+name)
    reject('wrong_discount',lambda d:d.update(beta='1'))
    reject('lost_root_cap',lambda d:d['model'][0][0].update(cap='0'))
    reject('negative_primal_mixture',lambda d:d['levels'][0][0]['anchors'][0]['children'][0][0].__setitem__(1,'-1'))
    reject('altered_exact_promise',lambda d:d['levels'][0][0]['anchors'][0].update(b='1/100'))
    reject('inflated_primal_reward',lambda d:d['levels'][0][0]['anchors'][0].update(value='100'))
    reject('exceeded_switching_price',lambda d:d['levels'][0][0]['planes'][0].update(A='100'))
    reject('understated_upper_constant',lambda d:d['levels'][0][0]['planes'][0].update(C='-100'))
    reject('unnormalized_dual_mixture',lambda d:d['levels'][0][0]['planes'][0]['children'][0][0].__setitem__(1,'2'))
    reject('false_terminal_domain',lambda d:d['levels'][-1][0].update(U='1'))
    reject('understated_triangle_gap',lambda d:d['levels'][0][0].update(width='0'))
    # Convex interpolation cannot be exported to indivisible tiers.
    require(not any(F(a)==F(1,2) for a in (0,1)),'discrete-action counterexample')
    tests.append('discrete_action_interpolation_rejected')
    return tests

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    paths=sorted((R/'results').glob('envelopes_T*_m*.json'));require(len(paths)>=6,'missing evidence files')
    cases=[]
    for p in paths: cases.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),**verify(json.loads(p.read_text()))})
    result={'status':'PASS','cases':cases,'total_primal_anchor_certificates':sum(c['anchors'] for c in cases),'total_recursive_dual_planes':sum(c['dual_planes'] for c in cases),'information_examples':exact_information(),'negative_controls_rejected':negative_controls(json.loads(paths[-1].read_text())),'scope':'Exact rational induction certificates for continuous-tier envelopes of the stored synthetic models. No universal convergence rate, field validation, or learned speedup is asserted.'}
    out=R/'results'/'replay.json'
    if args.check:require(json.loads(out.read_text())==result,'replay output mismatch')
    else:out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
