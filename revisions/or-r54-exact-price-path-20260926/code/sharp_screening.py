"""Post-derivation sharp-envelope neighbors; not part of the 24-case benchmark."""
from fractions import Fraction as F
from pathlib import Path
import json,sys
from price_path import Model,spec_for,allocate,solve,encode
from check_price import verify
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/or-r53-catalog-safe-certificates-20260926/code'))
from screening import context_gain,Instance
R=Path(__file__).resolve().parents[1]
def run():
    b=[F(1,5),F(2,5),F(3,5)];w=[F(1,3)]*3;g=[F(0),F(1),F(2)];tau=[F(3,5),F(13,20),F(7,10)]
    d=Model.make(b,w,g,tau);old=Instance.make(b,w,g,tau);a=(F(0),F(1,2));B=d.cap_total;G=context_gain(old,*a)
    rows=[]
    for ratio in [F(9,10),F(1),F(11,10)]:
        rho=(F(0),ratio*G);cost=dict(zip(a,rho));one=allocate(d,(a[0],),B,cost)['value'];pair=allocate(d,a,B,cost)['value']
        assert pair-one==(1-ratio)*G
        ans=solve(spec_for(d,a,rho,B,2));verify(ans['certificate']);assert ans['lower']==ans['upper']==max(one,pair)
        rows.append(dict(multiplier=str(ratio),G=str(G),charge=str(rho[1]),slack=str(rho[1]-G),singleton=str(one),pair=str(pair),
                         target_necessary=pair>one,target_tied=pair==one,target_excluded=pair<one,certificate=ans['certificate']))
    out=dict(status='PASS',scope='Three explicit neighbors at the proven sharpness configuration; separate from the 24-case screening-rate benchmark.',rows=rows)
    (R/'results/SHARP_SCREENING.json').write_text(json.dumps(encode(out),indent=2)+'\n')
if __name__=='__main__':run()
