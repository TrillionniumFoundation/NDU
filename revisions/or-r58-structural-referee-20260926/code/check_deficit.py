"""Independent original-instance and Bellman-inequality verifier.

This module imports neither deficit.py nor price_path.py. It reconstructs
terminal components, solves service water levels independently, and checks
all finite predecessor transitions explicitly rather than monotone search.
The implementation is deliberately quadratic in the grid size.
"""
from rational import F,qstr,digest
from check_price import model,check_policy,require
import time,json,gzip,sys


def kernel(spec,i,j,x):
    w,b,g,t,r,q,a,rho,B,m=model(spec);u=a[i];v=a[j] if j<len(a) else None
    segments=[];services=[]
    for h in range(len(b)):
        if v is not None and v<=t[h]:
            z=max(F(0),min(b[h],v)-u)
            if z:segments.append((r[h]-q[h]*(u+v)/2,w[h]*z))
        if u<=t[h] and (v is None or t[h]<v):
            z=max(F(0),b[h]-u)
            if z:services.append((w[h],g[h],z))
    T=sum((cap for slope,cap in segments),F(0));C=T+sum((p*c for p,gg,c in services),F(0))
    require(0<=x<=C,'Kernel capacity violated')
    remain=min(x,T);score=F(0)
    for slope,cap in sorted(segments,reverse=True):
        take=min(remain,cap);score+=slope*take;remain-=take
    y=max(F(0),x-T);free=sum((p*c for p,gg,c in services if not gg),F(0))
    if y>free:
        target=y-free;active=[(p,gg,c) for p,gg,c in services if gg]
        # Independently test each saturation threshold interval.
        breaks=[F(0)]+sorted({gg*c for p,gg,c in active})
        found=False
        for lo,hi in zip(breaks,breaks[1:]):
            saturated=[(p,gg,c) for p,gg,c in active if gg*c<=lo]
            unsat=[(p,gg,c) for p,gg,c in active if gg*c>lo]
            filled=sum((p*c for p,gg,c in saturated),F(0));den=sum((p/gg for p,gg,c in unsat),F(0))
            alpha=(target-filled)/den
            if lo<=alpha<=hi:
                score-=sum((p*gg*min(c,alpha/gg)**2/2 for p,gg,c in active),F(0));found=True;break
        require(found,'No service supporting interval')
    return score


def verify(cert,expected_sha256=None,max_states=600000):
    started=time.perf_counter();require(cert.get('schema')=='NDU-deficit-v1-hex','Unknown deficit schema')
    spec=cert['spec'];actual=digest(spec)
    require(actual==cert['instance_sha256'],'Instance binding failed')
    require(expected_sha256 is None or actual==expected_sha256,'Unexpected instance')
    w,b,g,t,r,q,a,rho,B,m=model(spec);n=len(a);R=sum(p*c for p,c in zip(w,b))-B
    eta,center,error,eps=map(F,(cert['eta'],cert['center'],cert['error'],cert['epsilon']))
    require(eta>0 and eps>=0,'Invalid accuracy encoding')
    K=(max(r)+max(g))/2;require(center==(max(r)-max(g))/2,'Invalid centering')
    if cert['mode']=='lattice':
        require(all(gg==0 for gg in g),'Lattice theorem does not cover nonzero service')
        D=int(cert['D'],16);require(D>0 and eta==F(1,D),'Invalid lattice')
        require((B*D).denominator==1,'Promise off lattice')
        require(all((p*c*D).denominator==1 and all((p*u*D).denominator==1 for u in a) for p,c in zip(w,b)),'Component off lattice')
        require(error==0,'Exact lattice has no approximation error');Q=int(R*D)+1;accepted=[Q-1]
    elif cert['mode']=='additive':
        if R==0:require(error==0,'Zero-deficit error');Q=1;accepted=[0]
        else:
            require(eps>0 and eta==eps/(2*K*m) and error==K*m*eta,'Invalid grid error')
            Q=int(R//eta)+1;accepted=[z for z in range(Q) if R-m*eta<=z*eta<=R]
    else:raise ValueError('Unknown deficit mode')
    require(m*n*Q<=max_states,'Verifier state allowance exceeded')
    values=cert['states'];require(len(values)==m and all(len(l)==n and all(len(row)==Q for row in l) for l in values),'Wrong potential dimensions')
    values=[[[None if z is None else F(z) for z in row] for row in layer] for layer in values]
    potential=[sum(p*min(c,u) for p,c in zip(w,b)) for u in a]+[sum(p*c for p,c in zip(w,b))]
    grids={}
    for i in range(n):
        for j in list(range(i+1,n))+[n]:
            C=potential[j]-potential[i];L=min(Q-1,int(C//eta))
            grids[i,j]=[kernel(spec,i,j,C-h*eta)+center*h*eta for h in range(L+1)]
    transitions=0
    for i,u in enumerate(a):
        init=sum(p*(rr*u-qq*u*u/2) for p,rr,qq in zip(w,r,q))-rho[i]
        if u<=min(B,min(b)):require(values[0][i][0] is not None and values[0][i][0]>=init,'Missing anchor potential')
    for ell in range(1,m):
        for i in range(n):
            for j in range(i+1,n):
                for z,prev in enumerate(values[ell-1][i]):
                    if prev is None:continue
                    for h,v in enumerate(grids[i,j][:Q-z]):
                        transitions+=1;out=values[ell][j][z+h]
                        require(out is not None and out>=prev+v-rho[j],'Invalid Bellman upper potential')
    upper_grid=None
    for layer in values:
        for i in range(n):
            for s in accepted:
                for h,v in enumerate(grids[i,n][:s+1]):
                    prev=layer[i][s-h]
                    if prev is not None:
                        val=prev+v
                        if upper_grid is None or val>upper_grid:upper_grid=val
    require(upper_grid is not None and F(cert['best'])==upper_grid,'Incorrect terminal bound')
    U=F(cert['upper']);L=check_policy(spec,cert['policy'])
    require(U==upper_grid-center*R+error and L==F(cert['lower']) and L<=U,'Invalid global interval')
    ids=cert['book_indices'];require(ids==sorted(set(ids)) and 1<=len(ids)<=m and all(type(i)==int and 0<=i<n for i in ids),'Invalid chosen path')
    require(a[ids[0]]<=min(B,min(b)),'Invalid chosen anchor')
    deficits=list(map(F,cert['rounded_deficits']));repaired=list(map(F,cert['repaired_deficits']))
    path=list(zip(ids,ids[1:]))+[(ids[-1],n)]
    require(len(deficits)==len(repaired)==len(path),'Deficit witness dimensions')
    z=sum(deficits);require(z/eta in accepted,'Rounded terminal target not accepted')
    path_value=sum(p*(rr*a[ids[0]]-qq*a[ids[0]]**2/2) for p,rr,qq in zip(w,r,q))-rho[ids[0]]
    for (i,j),d,dr in zip(path,deficits,repaired):
        C=potential[j]-potential[i]
        require(0<=d<=dr<=C and (d/eta).denominator==1,'Invalid grid/repair witness')
        path_value+=kernel(spec,i,j,C-d)+center*d-(rho[j] if j<n else 0)
    require(path_value==upper_grid,'Chosen path does not attain grid optimum')
    require(sum(repaired)==R and tuple(a[i] for i in ids)==tuple(map(F,cert['policy']['book'])),'Policy/repair mismatch')
    require(L>=upper_grid-center*R-error and U-L<=2*error,'Claimed repair guarantee failed')
    return {'status':'PASS','lower':qstr(L),'upper':qstr(U),'gap':qstr(U-L),'tolerance_met':U-L<=eps,'seconds':time.perf_counter()-started,'bellman_inequalities':transitions,'grid_points':Q,'instance_sha256':actual}

if __name__=='__main__':
    from pathlib import Path
    p=Path(sys.argv[1]);raw=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
    print(json.dumps(verify(json.loads(raw),sys.argv[2] if len(sys.argv)>2 else None),indent=2))
