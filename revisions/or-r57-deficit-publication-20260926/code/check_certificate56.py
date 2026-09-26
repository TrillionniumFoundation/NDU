"""Verify one certificate against an independently supplied original model digest."""
from pathlib import Path
import argparse,gzip,json

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('certificate',type=Path)
    p.add_argument('--expected-sha256',required=True)
    a=p.parse_args();data=a.certificate.read_bytes()
    cert=json.loads(gzip.decompress(data) if a.certificate.suffix=='.gz' else data)
    schema=cert.get('schema')
    if schema=='NDU-deficit-v1-hex':
        from check_deficit import verify
    elif schema=='NDU-enumeration-v1-hex':
        from check_enumeration import verify
    elif schema=='NDU-screen-v1-hex':
        from check_screen import verify
    elif schema=='NDU-price-path-v2-hex':
        from check_price import verify
    else:raise ValueError('Unsupported certificate schema: '+str(schema))
    print(json.dumps(verify(cert,a.expected_sha256),indent=2))
if __name__=='__main__':main()
