"""Independent integer/rational Fenchel verifier. Standard library only."""
from fractions import Fraction as F

def prepare(p):
    if '_Bcols' in p:return
    n=len(p['qnum'])
    for name,rows in [('B',p['B']),('A',p['Aacc']+p['C']),('E',p['E'])]:
        p['_'+name+'cols']=[[(j,int(row[i])) for j,row in enumerate(rows) if row[i]] for i in range(n)]
    p['_Brows']=[[(i,int(a)) for i,a in enumerate(row) if a] for row in p['B']]

def ceildiv(n,d):return -((-int(n))//int(d))
def audit_exact(p,context,xn,xd,pn,sn,mu,nu,den):
    """Pure-Python integer/Fraction audit. No numerical solver or inverse needed."""
    n=len(xn);sv=p['services'];nodes=p['nodes'];r=p['rank'];xn=list(map(int,xn));xd=int(xd)
    def dot(a,b):return sum(int(u)*int(v) for u,v in zip(a,b))
    # Feasibility is recomputed from the implemented x, not trusted from its repair.
    for x,z in zip(xn,p['znum']):
        assert -int(z)*xd<=32*x<=(32-int(z))*xd,'box violation'
    sub=[[int(p['c'][j*sv+a])*xn[j*sv+a] for a in range(sv)] for j in range(nodes)]
    for j in range(nodes-1,0,-1):
        assert all(v<=0 for v in sub[j]),'continuation violation'
        for a in range(sv):sub[p['parent'][j]][a]+=sub[j][a]
    assert all(v==0 for v in sub[0]),'root equality violation'
    for row in p['E']: assert dot(row,xn)==0,'additional equality violation'
    for row,cap in zip(p['C'],p['capnum']):assert 8*dot(row,xn)<=int(cap)*xd,'capacity violation'
    lam=int(context[-1]);h=list(map(int,context[:r]));qnum=p['qnum'];Un=p['Unum'];B=p['B'];v=p['vnum'];kn=p['knum']
    cn=[16*int(p['bnum'][i])+sum(int(Un[j][i])*h[j] for j in range(r)) for i in range(n)]
    prepare(p);ux=[dot(row,xn) for row in Un];bx=[sum(a*xn[j] for j,a in row) for row in p['_Brows']]
    gain=F(dot(cn,xn),512*xd)-F(sum(int(q)*x*x for q,x in zip(qnum,xn)),32*xd*xd)-F(sum(vv*vv for vv in ux),2048*xd*xd)
    gain-=F(lam*sum(int(k)*abs(32*b+int(vv)*xd) for k,b,vv in zip(kn,bx,v)),16384*xd)
    gain+=F(lam*sum(int(k)*abs(int(vv)) for k,vv in zip(kn,v)),16384)
    assert all(u>=0 for u in mu),'negative inequality price'
    assert all(512*abs(int(s))<=den*lam*int(k) for s,k in zip(sn,kn)),'invalid switching tension'
    prepare(p);rd=512*den;scale=10**12
    rn=[]
    for i in range(n):
        rn.append(den*cn[i]-16*sum(int(Un[j][i])*int(pn[j]) for j in range(r))-512*(sum(a*int(sn[j]) for j,a in p['_Bcols'][i])+sum(a*int(mu[j]) for j,a in p['_Acols'][i])+sum(a*int(nu[j]) for j,a in p['_Ecols'][i])))
    conj=0
    for ri,qi,zi in zip(rn,qnum,p['znum']):
        qi=int(qi);lo=-int(zi);hi=32-int(zi)
        if 512*ri<rd*qi*lo:b=lo
        elif 512*ri>rd*qi*hi:b=hi
        else:
            conj+=ceildiv(8*ri*ri*scale,rd*rd*qi);continue
        conj+=ceildiv((1024*ri*b-qi*b*b*rd)*scale,32768*rd)
    upper=F(conj,scale)+F(dot(pn,pn),2*den*den)-F(dot(sn,v),32*den)+F(dot(mu[-len(p['capnum']):],p['capnum']),8*den)+F(lam*sum(int(k)*abs(int(vv)) for k,vv in zip(kn,v)),16384)
    assert upper>=gain,'invalid Fenchel certificate'
    # Gate is improvement over this exact outside protocol only.
    accepted_gain=max(F(0),gain);gap=upper-accepted_gain
    assert gap>=0,'outside comparator is feasible and its gain is zero'
    return {'gain':float(accepted_gain),'raw_gain':float(gain),'raw_gain_exact':str(gain),'gap':float(gap),'gate':bool(gain<0),'gain_exact':str(accepted_gain),'upper_exact':str(upper),'feasible':True,'positive_switches':sum(32*b+int(vv)*xd>0 for b,vv in zip(bx,v)),'negative_switches':sum(32*b+int(vv)*xd<0 for b,vv in zip(bx,v)),'near_kinks':sum(abs(float(F(32*b+int(vv)*xd,32*xd)))<1e-5 for b,vv in zip(bx,v))}


def decompose(p,rec):
    """Exact four-term identity plus the explicit outward-rounding remainder."""
    prepare(p)
    n=len(p['qnum']); r=p['rank']; den=rec['dual_den']
    x=[F(int(v),int(rec['x_den'])) for v in rec['x_num']]
    price=[F(v,den) for v in rec['price_num']]
    sw=[F(v,den) for v in rec['switch_num']]
    mu=[F(v,den) for v in rec['ineq_num']]
    nu=[F(v,den) for v in rec['equality_num']]
    h=rec['context'][:r]; lam=F(rec['context'][-1],64)
    dot=lambda a,b:sum((aa*bb for aa,bb in zip(a,b)),F(0))
    U=[[F(int(v),32) for v in row] for row in p['Unum']]
    ux=[dot(row,x) for row in U]
    b=[F(16*int(p['bnum'][i])+sum(int(p['Unum'][j][i])*h[j] for j in range(r)),512) for i in range(n)]
    rr=[b[i]-sum(U[j][i]*price[j] for j in range(r))-sum(a*sw[j] for j,a in p['_Bcols'][i])-sum(a*mu[j] for j,a in p['_Acols'][i])-sum(a*nu[j] for j,a in p['_Ecols'][i]) for i in range(n)]
    box=F(0)
    for i in range(n):
        d=F(int(p['qnum'][i]),16); lo=F(-int(p['znum'][i]),32); hi=lo+1
        z=min(hi,max(lo,rr[i]/d))
        box+=d*x[i]*x[i]/2+rr[i]*z-d*z*z/2-rr[i]*x[i]
    resource=sum(((a-b)**2/2 for a,b in zip(price,ux)),F(0))
    v=[sum(a*x[i] for i,a in row)+F(int(v),32) for row,v in zip(p['_Brows'],p['vnum'])]
    switching=sum((lam*F(int(k),8)*abs(vv)-ss*vv for k,vv,ss in zip(p['knum'],v,sw)),F(0))
    budgets=[F(0)]*len(p['Aacc'])+[F(int(v),8) for v in p['capnum']]
    acceptance=sum((m*(bb-dot(row,x)) for m,bb,row in zip(mu,budgets,p['Aacc']+p['C'])),F(0))
    aa=audit_exact(p,rec['context'],rec['x_num'],rec['x_den'],rec['price_num'],rec['switch_num'],rec['ineq_num'],rec['equality_num'],den)
    rounding=F(aa['upper_exact'])-F(aa['raw_gain_exact'])-box-resource-switching-acceptance
    out={'box':box,'resource':resource,'switching':switching,'acceptance':acceptance,'outward_rounding':rounding}
    assert all(v>=0 for v in out.values()),out
    assert sum(out.values())==F(aa['upper_exact'])-F(aa['raw_gain_exact'])
    return {k:str(v) for k,v in out.items()}
