"""Request-bound producer for the exact/robust tariff certificate classes."""
from pathlib import Path
import argparse,json
from binding65 import canonical_request,bind_legacy,verify_request,TARIFF,ROBUST
from rational import write

def produce(request):
    req=canonical_request(request)
    if req['certificate_class']==TARIFF:
        from tariff60 import solve
        ans=solve(req['spec'],max_exceptions=req['configured_guard'])
    elif req['certificate_class']==ROBUST:
        from robust61 import solve
        ans=solve(req['spec'],req['epsilon'],max_exceptions=req['configured_guard'])
    else:raise ValueError('This producer supports tariff and robust-tariff requests only')
    envelope=bind_legacy(ans['certificate'],req)
    verify_request(envelope,request)
    return envelope

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('request',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();write(a.output,produce(json.loads(a.request.read_text())))
