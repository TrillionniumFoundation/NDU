"""Independent external-input binding and proof verification.

A certificate's self-declared digest is not an external-input receipt. Historical
producers may re-encode the same rational using decimal fractions or hexadecimal
fractions. This adapter proves fieldwise exact equality first, records both byte
digests, and only then calls the independent mathematical checker. No optimizer
is imported. The original requested budget is preserved, not truncated.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json
from pathlib import Path
from rational import F, qstr, digest
from check_price import model, check_policy, require
TOP = {'model', 'catalog', 'charges', 'promise', 'budget'}
MODEL = {'caps', 'weights', 'gamma', 'ceilings', 'reward_r', 'reward_q'}
SCHEMAS = {'NDU-price-path-v2-hex': 'check_price',
           'NDU-R60-tariff-frontier-v1': 'check_tariff60',
           'NDU-R61-robust-tariff-v1': 'check_robust61',
           'NDU-deficit-v1-hex': 'check_deficit',
           'NDU-enumeration-v1-hex': 'check_enumeration'}

def canonical_spec(spec: dict) -> dict:
    require(type(spec) is dict and set(spec) == TOP, 'Unrecognized input fields')
    require(type(spec['model']) is dict and set(spec['model']) == MODEL,
            'Unrecognized model fields')
    model(spec)  # Independent validation of the original constraints.
    vector = lambda xs: [qstr(F(x)) for x in xs]
    return {'model': {k: vector(spec['model'][k]) for k in sorted(MODEL)},
            'catalog': vector(spec['catalog']), 'charges': vector(spec['charges']),
            'promise': qstr(F(spec['promise'])), 'budget': spec['budget']}

def verify_bound(cert: dict, expected: dict) -> dict:
    import importlib
    actual = cert.get('spec', cert.get('instance'))
    require(actual is not None, 'Missing certificate input')
    left, right = canonical_spec(expected), canonical_spec(actual)
    require(left == right, 'Certificate differs from the externally requested model')
    schema = cert['schema']
    if schema == 'NDU-R59-SCIP-numerical-v1':
        out = {'status': 'PASS_LOWER_ONLY', 'lower': qstr(check_policy(expected, cert['policy']))}
    else:
        require(schema in SCHEMAS, 'Unsupported certificate schema')
        out = importlib.import_module(SCHEMAS[schema]).verify(cert, digest(actual))
        # Independently check the final policy against the EXTERNAL input too.
        require(F(out['lower']) == check_policy(expected, cert['policy']),
                'Lower policy disagrees with requested instance')
    if schema == 'NDU-price-path-v2-hex':
        from diagnostics61 import verify_root
        out['root_diagnostics'] = verify_root(expected, cert.get('root_diagnostics', []))
    if 'hybrid_probe_certificate' in cert:
        out['hybrid_probe'] = verify_bound(cert['hybrid_probe_certificate'], expected)
    out['binding'] = {'schema': 'NDU-external-rational-binding-v1',
                      'requested_byte_sha256': digest(expected),
                      'certificate_input_byte_sha256': digest(actual),
                      'canonical_rational_sha256': digest(left),
                      'byte_identical': expected == actual,
                      'exact_fieldwise_equal': True}
    return out

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('certificate', type=Path)
    p.add_argument('external_input', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    raw = a.certificate.read_bytes()
    cert = json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)
    inp = json.loads(a.external_input.read_text()); inp = inp.get('spec', inp)
    ans = verify_bound(cert, inp)
    ans['certificate_file_sha256'] = hashlib.sha256(raw).hexdigest()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(ans, indent=2, sort_keys=True)+'\n')
    print(ans['status'], ans['binding']['canonical_rational_sha256'])
