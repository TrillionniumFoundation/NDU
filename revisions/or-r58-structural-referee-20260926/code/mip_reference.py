"""R46 uneliminated formulation, extended only to history-specific rewards."""
import time
def direct_milp(data, catalog, charges, promise, budget, segments=32,
                envelope='tangent', time_limit=20):
    import numpy as np
    from scipy.optimize import milp, Bounds, LinearConstraint
    from scipy.sparse import coo_array
    k, n = len(data.caps), len(catalog)
    # open[n], support[k*n], probability[k*n], intermediate[k], epigraph[k]
    use = n; prob = n+k*n; ybase = n+2*k*n; hbase = ybase+k; nv = hbase+k
    c = np.zeros(nv); lb = np.zeros(nv); ub = np.full(nv, np.inf)
    integer = np.zeros(nv, dtype=int); integer[:prob] = 1; ub[:ybase] = 1
    c[:n] = list(map(float, charges))
    rows, cols, vals, lo, hi = [], [], [], [], []
    def add(entries, lower=-np.inf, upper=np.inf):
        z = len(lo); lo.append(lower); hi.append(upper)
        for col, value in entries.items():
            if value: rows.append(z); cols.append(col); vals.append(float(value))
    add({l:1 for l in range(n)}, upper=budget)
    aggregate = {}
    for j in range(k):
        b, w, gamma, tau = map(float, (data.caps[j], data.weights[j], data.gamma[j], data.ceilings[j]))
        y, h = ybase+j, hbase+j; ub[y] = b; c[h] = w
        psum, total = {}, {y:1}; aggregate[y] = w
        for l, aa in enumerate(catalog):
            a = float(aa); z = use+j*n+l; p = prob+j*n+l
            psum[p] = 1; total[p] = a; aggregate[p] = w*a
            c[p] = -w*(float(data.reward_r[j])*a-float(data.reward_q[j])*a*a/2)
            add({p:1,z:-1}, upper=0); add({z:1,l:-1}, upper=0)
            if aa > data.ceilings[j]: ub[p] = ub[z] = 0
            M = max(0.0, b+a-tau)
            add({y:1,z:M}, upper=tau-a+M)
        add(psum,1,1); add(total,upper=b)
        nodes = np.linspace(0,b,segments+1)
        if envelope == 'tangent':
            for x in nodes: add({h:1,y:-gamma*x}, lower=-gamma*x*x/2)
        elif envelope == 'secant':
            for a, d in zip(nodes,nodes[1:]):
                add({h:1,y:-gamma*(a+d)/2}, lower=-gamma*a*d/2)
        else: raise ValueError('Unknown quadratic envelope.')
    add(aggregate,float(promise),float(promise))
    mat = coo_array((np.array(vals),(np.array(rows,dtype=np.int32),np.array(cols,dtype=np.int32))),shape=(len(lo),nv)).tocsc()
    started=time.perf_counter()
    result=milp(c,integrality=integer,bounds=Bounds(lb,ub),
                constraints=LinearConstraint(mat,np.array(lo),np.array(hi)),
                options={'mip_rel_gap':1e-9,'time_limit':float(time_limit)})
    out=dict(status=int(result.status),message=result.message,seconds=time.perf_counter()-started,
             formulation='direct support-indicator probability/service MILP',envelope=envelope,
             segments=segments,variables=nv,binaries=int(integer.sum()),constraints=len(lo),
             approximation_error=sum(float(w*g*b*b)/(8*segments*segments)
                 for w,g,b in zip(data.weights,data.gamma,data.caps)),
             bound_scope='floating-point HiGHS global solver bound, not a rational proof')
    dual=getattr(result,'mip_dual_bound',None)
    out['numerical_upper']=None if dual is None else -float(dual)
    out['node_count']=int(getattr(result,'mip_node_count',0) or 0)
    out['mip_gap']=None if getattr(result,'mip_gap',None) is None else float(result.mip_gap)
    if result.x is not None:
        x=result.x; actual=0.0
        for j,w in enumerate(data.weights):
            actual+=float(w)*(sum(x[prob+j*n+l]*(float(data.reward_r[j])*float(a)-float(data.reward_q[j])*float(a)**2/2)
                for l,a in enumerate(catalog))-float(data.gamma[j])*x[ybase+j]**2/2)
        actual-=sum(float(rho)*round(x[l]) for l,rho in enumerate(charges))
        v=mat@x
        residual=max(float(np.max(np.maximum(np.array(lo)-v,0))),float(np.max(np.maximum(v-np.array(hi),0))),
                     float(np.max(np.abs(x[:prob]-np.rint(x[:prob])))))
        out.update(value=actual,objective=-float(result.fun),max_model_residual=residual,
                   installed=[str(a) for l,a in enumerate(catalog) if x[l]>.5],
                   probabilities=x[prob:ybase].reshape(k,n).tolist(),intermediate=x[ybase:hbase].tolist())
    return out
