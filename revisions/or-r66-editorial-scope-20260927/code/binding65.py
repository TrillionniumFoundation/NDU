"""Independent request-level certificate verification; no optimizer imports.

The request must come from the caller, not from the submitted proof. A wrapper
and its self-declared hash never supply this trust anchor. Legacy proofs can be
bound at replay, without rewriting the historical bytes or asserting that the
wrapper existed at the original execution time.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import argparse, gzip, hashlib, json
from rational import F, qstr, digest
from check_price import require
from binding63 import canonical_spec, verify_bound, SCHEMAS
REQUEST='NDU-R65-request-v1'
ENVELOPE='NDU-R65-request-bound-certificate-v1'
ROBUST='NDU-R61-robust-tariff-v1'
TARIFF='NDU-R60-tariff-frontier-v1'
NUMERICAL='NDU-R59-SCIP-numerical-v1'
FIELDS={'schema','spec','epsilon','certificate_class','configured_guard'}


def canonical_request(request: dict) -> dict:
    require(type(request) is dict and set(request)==FIELDS,'Request field mismatch')
    require(request['schema']==REQUEST,'Wrong request schema')
    cls=request['certificate_class']
    require(cls in set(SCHEMAS)|{NUMERICAL},'Unsupported requested certificate class')
    eps=request['epsilon']
    require(type(eps) in (str,int),'Request tolerance must have an exact rational encoding')
    eps=F(eps);require(eps>=0,'Negative requested tolerance')
    guard=request['configured_guard']
    if cls in (ROBUST,TARIFF):
        require(type(guard) is int and guard>=0,'Invalid requested exception guard')
    else:require(guard is None,'Exception guard is inapplicable to requested proof class')
    return dict(schema=REQUEST,spec=canonical_spec(request['spec']),epsilon=qstr(eps),
                certificate_class=cls,configured_guard=guard)


def make_request(spec, epsilon, certificate_class, configured_guard=None):
    return canonical_request(dict(schema=REQUEST,spec=spec,epsilon=qstr(F(epsilon)),
        certificate_class=certificate_class,configured_guard=configured_guard))


def bind_legacy(certificate: dict, external_request: dict) -> dict:
    """Packaging only, NOT verification or an assertion of past execution."""
    req=canonical_request(external_request)
    return dict(schema=ENVELOPE,request=req,request_sha256=digest(req),
                certificate=deepcopy(certificate))


def verify_request(envelope: dict, external_request: dict) -> dict:
    require(type(envelope) is dict and set(envelope)==
        {'schema','request','request_sha256','certificate'},'Envelope field mismatch')
    require(envelope['schema']==ENVELOPE,'Wrong envelope schema')
    expected=canonical_request(external_request)
    declared=canonical_request(envelope['request'])
    require(declared==expected,'Certificate differs from the externally requested contract')
    require(envelope['request_sha256']==digest(declared),'Wrong canonical request digest')
    cert=envelope['certificate'];cls=expected['certificate_class']
    require(cert['schema']==cls,'Certificate class differs from external request')
    if cls==ROBUST:
        require(F(cert['epsilon'])==F(expected['epsilon']),
                'Projection tolerance differs from external request')
    tariff=cert if cls==TARIFF else cert.get('surrogate_certificate') if cls==ROBUST else None
    if tariff is not None:
        require(type(tariff.get('configured_guard')) is int and
                tariff['configured_guard']==expected['configured_guard'],
                'Configured exception guard differs from external request')
    # Independent physical equality, all mathematical checks, and final-policy
    # validation against the caller's original model. Probes get the same model.
    out=verify_bound(cert,external_request['spec'])
    if 'hybrid_probe_certificate' in cert:
        probe=cert['hybrid_probe_certificate']
        require(probe['schema']=='NDU-price-path-v2-hex','Unexpected hybrid probe class')
    met=out['status']=='PASS' and F(out['upper'])-F(out['lower'])<=F(expected['epsilon'])
    out.update(request_bound=True,tolerance_met=met,
        request_binding=dict(schema=REQUEST,canonical_request_sha256=digest(expected),
            external_request_byte_sha256=digest(external_request),
            certificate_class=cls,requested_epsilon=expected['epsilon'],
            configured_guard=expected['configured_guard'],
            configured_guard_checked=tariff is not None,
            projection_tolerance_checked=cls==ROBUST,
            scope='Mathematical request agreement; not wall-clock execution attestation'))
    if cls==ROBUST:
        out['minimality_scope']='total absolute fee distortion at the EXTERNAL requested tolerance'
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('certificate',type=Path);p.add_argument('external_request',type=Path)
    p.add_argument('--legacy',action='store_true',help='Bind an unchanged legacy proof at replay time')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    raw=a.certificate.read_bytes();obj=json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
    req=json.loads(a.external_request.read_text())
    ans=verify_request(bind_legacy(obj,req) if a.legacy else obj,req)
    ans['source_certificate_file_sha256']=hashlib.sha256(raw).hexdigest()
    ans['legacy_bound_at_replay']=a.legacy
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(ans,indent=2,sort_keys=True)+'\n')
    print(ans['status'],ans['request_binding']['canonical_request_sha256'])
