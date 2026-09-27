"""Independent root-price support check using original one-history functions."""
from rational import F
from check_price import model, price_bound, require

def verify_root(spec, records):
    w,b,g,t,r,q,a,charges,B,m=model(spec);cache={}
    for row in records:
        book=tuple(map(F,row['book']));lam=F(row['price']);lo=hi=value=F(0)
        require(book and len(book)<=m and all(x in a for x in book),'Bad diagnostic book')
        for j in range(len(w)):
            eligible=[x for x in book if x<=t[j]];first=book[0];last=eligible[-1]
            knots={first,b[j]}|{x for x in eligible if x<=b[j]}
            if g[j] and lam<=0:knots.add(min(b[j],max(first,last-lam/g[j])))
            vals=[]
            for z in knots:
                mu=min(z,last)
                if mu in eligible:reward=r[j]*mu-q[j]*mu*mu/2
                else:
                    u=max(x for x in eligible if x<mu);v=min(x for x in eligible if x>mu)
                    reward=((v-mu)*(r[j]*u-q[j]*u*u/2)+(mu-u)*(r[j]*v-q[j]*v*v/2))/(v-u)
                vals.append((reward-g[j]*max(F(0),z-last)**2/2-lam*z,z))
            high=max(v for v,z in vals);zs=[z for v,z in vals if v==high]
            lo+=w[j]*min(zs);hi+=w[j]*max(zs);value+=w[j]*high
        value+=lam*B-sum(charges[a.index(x)] for x in book)
        global_upper=price_bound(spec,lam,set(),set(),cache)
        require(value==global_upper==F(row['upper']),'Book is not globally price-active')
        distance=max(lo-B,B-hi,F(0))
        require([str(lo),str(hi)]==[str(F(row['support_low'])),str(F(row['support_high']))],'Wrong support interval')
        require(distance==F(row['distance']) and row['supports_promise']==(distance==0),'Wrong support diagnostic')
    return dict(status='PASS',checked_root_candidates=len(records))
