"""R24 rational audit for interior-model restricted comparators.
Only Python's standard library is needed. No stored objective, optimizer
termination status, or floating-point residual is accepted as a certificate.
"""
from fractions import Fraction as F
from math import lcm
from functools import reduce


def fdot(a, b):
    return sum((F(x)*F(y) for x, y in zip(a, b)), F(0))


def make_model(p, context, radius, theta_num, outer=False):
    """theta_num/8 is strictly inside the R23 three-dimensional cube."""
    theta = [F(int(t), 8) for t in theta_num]
    assert len(theta) == 3 and all(-1 < t < 1 for t in theta)
    rho = F(int(radius), 16)
    n, rank = len(p['qnum']), p['rank']
    b0 = [F(int(p['bnum'][i]), 32) + sum(
        (F(int(p['Unum'][j][i])*int(context[j]), 512) for j in range(rank)), F(0))
        for i in range(n)]
    b = [(1+rho*theta[0])*bi + rho*theta[2]*F(1 if i % 2 == 0 else -1, 8)
         for i, bi in enumerate(b0)]
    lam = (1+rho*theta[1])*F(int(context[-1]), 64)
    A, rhs = [], []
    for row in p['Aacc']:
        if outer:
            A.append(list(map(F, row)))
            rhs.append(rho*sum((abs(int(a))*F(max(int(z),32-int(z)),32)
                                for a,z in zip(row,p['znum'])),F(0)))
        else:
            A.append([F(int(a))*(1+rho*theta[2]*(1 if (i//p['services'])%2 == 0 else -1))
                      for i,a in enumerate(row)])
            rhs.append(F(0))
    for row, cap in zip(p['C'],p['capnum']):
        A.append(list(map(F,row)))
        rhs.append((1+rho*(1 if outer else theta[1]))*F(int(cap),8))
    E = [list(map(F,row)) for row in p['E']]
    for j in range(p['nodes']):
        depth = (j+1).bit_length()-1
        rep = (1 << depth)-1
        if j == rep:
            continue
        for a in range(p['services']):
            row = [F(0)]*n
            row[j*p['services']+a] = F(1)
            row[rep*p['services']+a] = F(-1)
            E.append(row)
    return dict(b=b, lam=lam, A=A, rhs=rhs, E=E)


def cache(p, m):
    if '_B' not in p:
        p['_B'] = [[(i,F(int(a))) for i,a in enumerate(row) if a] for row in p['B']]
        p['_Bc'] = [[(j,F(int(row[i]))) for j,row in enumerate(p['B']) if row[i]]
                    for i in range(len(p['qnum']))]
    if '_A' not in m:
        m['_A'] = [[(i,a) for i,a in enumerate(row) if a] for row in m['A']]
        m['_E'] = [[(i,a) for i,a in enumerate(row) if a] for row in m['E']]
        n = len(p['qnum'])
        m['_Ac'] = [[(j,row[i]) for j,row in enumerate(m['A']) if row[i]] for i in range(n)]
        m['_Ec'] = [[(j,row[i]) for j,row in enumerate(m['E']) if row[i]] for i in range(n)]


def unpack(record):
    den = int(record['x_den'])
    assert den > 0
    return [F(int(a),den) for a in record['x_num']]


def vector_record(x):
    den = reduce(lcm,(a.denominator for a in x),1)
    return {'x_num':[str(int(a*den)) for a in x],'x_den':str(den)}


def feasible(p,m,rec):
    cache(p,m)
    x = unpack(rec)
    assert len(x) == len(p['qnum'])
    assert all(-F(int(z),32) <= a <= F(32-int(z),32) for a,z in zip(x,p['znum'])), 'box'
    assert all(sum((a*x[i] for i,a in row),F(0)) <= rhs
               for row,rhs in zip(m['_A'],m['rhs'])), 'participation/capacity'
    assert all(sum((a*x[i] for i,a in row),F(0)) == 0 for row in m['_E']), 'root/time equality'
    return True


def objective(p,m,rec):
    cache(p,m)
    x = unpack(rec)
    ans = fdot(m['b'],x) - sum((F(int(q),32)*a*a for q,a in zip(p['qnum'],x)),F(0))
    ux = [sum((F(int(a),32)*xx for a,xx in zip(row,x)),F(0)) for row in p['Unum']]
    ans -= sum((u*u/2 for u in ux),F(0))
    for row,k,v in zip(p['_B'],p['knum'],p['vnum']):
        vv=F(int(v),32)
        bx=sum((a*x[i] for i,a in row),F(0))
        ans -= m['lam']*F(int(k),8)*(abs(bx+vv)-abs(vv))
    return ans


def upper(p,m,dual):
    cache(p,m)
    den = int(dual['den'])
    assert den>0
    pp,ss,mu,nu = [[F(int(a),den) for a in dual[k]] for k in ('p','s','mu','nu')]
    n = len(p['qnum'])
    assert len(pp)==p['rank'] and len(ss)==n and len(mu)==len(m['A']) and len(nu)==len(m['E'])
    assert all(a>=0 for a in mu), 'negative inequality multiplier'
    assert all(abs(s)<=m['lam']*F(int(k),8) for s,k in zip(ss,p['knum'])), 'switch tension'
    ans = sum((a*a/2 for a in pp),F(0)) - fdot(ss,[F(int(v),32) for v in p['vnum']]) + fdot(mu,m['rhs'])
    ans += m['lam']*sum((F(int(k),8)*abs(F(int(v),32)) for k,v in zip(p['knum'],p['vnum'])),F(0))
    for i,(b,q,z) in enumerate(zip(m['b'],p['qnum'],p['znum'])):
        residual = b-sum((F(int(row[i]),32)*pp[j] for j,row in enumerate(p['Unum'])),F(0))
        residual -= sum((a*ss[j] for j,a in p['_Bc'][i]),F(0))
        residual -= sum((a*mu[j] for j,a in m['_Ac'][i]),F(0))
        residual -= sum((a*nu[j] for j,a in m['_Ec'][i]),F(0))
        d = F(int(q),16)
        xx = min(F(32-int(z),32),max(-F(int(z),32),residual/d))
        ans += residual*xx-d*xx*xx/2
    return ans


def repair_time(p,m,raw):
    """Round date/service amplitudes, reconstruct root, mix within that subspace."""
    cache(p,m)
    sv = p['services']; nodes = p['nodes']; n=nodes*sv
    groups = [((j+1).bit_length()-1)*sv+a for j in range(nodes) for a in range(sv)]
    ng=max(groups)+1
    amp=[F(0)]*ng
    anc=[F(0)]*sv+[F(-1)]*(ng-sv)
    for depth in range(1,ng//sv):
        rep=(1<<depth)-1
        for a in range(sv):
            amp[depth*sv+a] = F(int(round(float(raw[rep*sv+a])*10**10)),10**10)
    for a in range(sv):
        root = F(int(p['E'][a][a]))
        amp[a] = -sum((F(int(p['E'][a][i]))*amp[groups[i]] for i in range(sv,n)),F(0))/root
        anc[a] = -sum((F(int(p['E'][a][i]))*anc[groups[i]] for i in range(sv,n)),F(0))/root
    x=[amp[g] for g in groups]; anchor=[anc[g] for g in groups]
    scale=F(1)
    for xx,z in zip(anchor,p['znum']):
        if xx>0: scale=min(scale,F(32-int(z),64)/xx)
        if xx<0: scale=min(scale,-F(int(z),64)/xx)
    for row,rhs in zip(m['_A'],m['rhs']):
        v=sum((a*anchor[i] for i,a in row),F(0))
        if v>0:scale=min(scale,rhs/(2*v))
    assert scale>0
    anchor=[scale*a for a in anchor]
    rows=list(zip(m['_A'],m['rhs']))
    rows += [([(i,F(1))],F(32-int(z),32)) for i,z in enumerate(p['znum'])]
    rows += [([(i,F(-1))],F(int(z),32)) for i,z in enumerate(p['znum'])]
    alpha=F(0)
    for row,rhs in rows:
        xx=sum((a*x[i] for i,a in row),F(0)); zz=sum((a*anchor[i] for i,a in row),F(0))
        assert zz<rhs, 'strict reduced-coordinate anchor'
        if xx>rhs:alpha=max(alpha,(xx-rhs)/(xx-zz))
    assert 0<=alpha<1
    x=[(1-alpha)*xx+alpha*zz for xx,zz in zip(x,anchor)]
    rec=vector_record(x); rec['repair_fraction']=str(alpha)
    feasible(p,m,rec)
    return rec


def mixture_weights(theta_num):
    from itertools import product
    theta=[F(int(t),8) for t in theta_num]
    return [reduce(lambda a,b:a*b,((1+v*t)/2 for v,t in zip(vertex,theta)),F(1))
            for vertex in product((-1,1),repeat=3)]
