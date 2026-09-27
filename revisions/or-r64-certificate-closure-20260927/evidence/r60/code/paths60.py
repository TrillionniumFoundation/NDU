"""Capacity recognition, length-aware lifting and exact scalar repair.

The public functions use exact Fractions; path witnesses are explicit vertex
sequences. The lifted DAG is topologically ordered by elapsed edge count.
"""
from fractions import Fraction as F
from collections import deque


def recognize(vertices, edges, sources, sink):
    vertices=list(vertices);adj={v:[] for v in vertices};rev={v:[] for v in vertices}
    for u,v,c in edges:
        if u not in adj or v not in adj or F(c)<0:raise ValueError('Invalid edge')
        adj[u].append((v,F(c)));rev[v].append(u)
    if sink not in adj or any(s not in adj for s in sources):raise ValueError('Unknown source/sink')
    reachable=set(sources);parent={s:None for s in sources};queue=deque(sources)
    while queue:
        u=queue.popleft()
        for v,c in adj[u]:
            if v not in reachable:reachable.add(v);parent[v]=u;queue.append(v)
    live={sink};queue=deque([sink])
    while queue:
        for v in rev[queue.popleft()]:
            if v not in live:live.add(v);queue.append(v)
    keep=reachable&live
    if not keep:return dict(accepted=True,potential={},sources=[],empty=True)
    indeg={v:sum(u in keep for u in rev[v]) for v in keep};queue=deque(v for v in vertices if v in keep and indeg[v]==0);order=[]
    while queue:
        u=queue.popleft();order.append(u)
        for v,c in adj[u]:
            if v in keep:
                indeg[v]-=1
                if indeg[v]==0:queue.append(v)
    if len(order)!=len(keep):raise ValueError('Graph is not acyclic')
    H={sink:F(0)};next_vertex={sink:None}
    def suffix(v):
        out=[v]
        while next_vertex[v] is not None:
            v=next_vertex[v];out.append(v)
        return out
    def prefix(v):
        out=[v]
        while parent[v] is not None:
            v=parent[v];out.append(v)
        return list(reversed(out))
    for u in reversed(order):
        if u==sink:continue
        choices=[(c+H[v],v) for v,c in adj[u] if v in keep]
        if not choices:raise ArithmeticError('Retained vertex without suffix')
        H[u],next_vertex[u]=choices[0]
        for val,v in choices[1:]:
            if val!=H[u]:
                return dict(accepted=False,witness=[prefix(u)[:-1]+suffix(u),prefix(u)+suffix(v)])
    return dict(accepted=True,potential=H,sources=[s for s in sources if s in keep],empty=False)


def bounded_recognize(vertices,edges,sources,sink,h):
    if type(h)!=int or h<0:raise ValueError('Nonnegative integer edge bound required')
    terminal=('terminal',)
    nodes=[(v,l) for l in range(h+1) for v in vertices]+[terminal]
    arcs=[((u,l),(v,l+1),F(c)) for l in range(h) for u,v,c in edges if u!=sink]
    arcs += [((sink,l),terminal,F(0)) for l in range(h+1)]
    ans=recognize(nodes,arcs,[(s,0) for s in sources],terminal)
    if not ans['accepted']:
        ans['witness']=[[v[0] for v in path if v!=terminal] for path in ans['witness']]
    else:
        ans['source_capacity']={s:ans['potential'][s,0] for s in sources if (s,0) in ans['potential']}
    return ans


def repair(capacities,rounded,R):
    caps=list(map(F,capacities));w=list(map(F,rounded));R=F(R)
    if len(caps)!=len(w) or any(c<0 or not 0<=x<=c for c,x in zip(caps,w)) or not sum(w)<=R<=sum(caps):raise ValueError('Repair preconditions fail')
    need=R-sum(w)
    for i,c in enumerate(caps):
        delta=min(need,c-w[i]);w[i]+=delta;need-=delta
    if need or sum(w)!=R:raise ArithmeticError('Repair failed')
    return w
