"""Canonical, bounded-decoding hexadecimal rational wire format.

No process-global integer-string security setting is changed.  Only arithmetic
and serialization are shared by producer and checker, not optimization logic.
"""
from fractions import Fraction
import hashlib, json

def F(x=0, denominator=None):
    if denominator is not None:
        return Fraction(x, denominator)
    if isinstance(x, str) and x.startswith('hex:'):
        a, sep, b = x[4:].partition('/')
        if not sep or len(a)+len(b)>4000000:
            raise ValueError('Invalid or oversized rational encoding')
        d = int(b, 16)
        if d<=0:
            raise ValueError('Nonpositive denominator')
        return Fraction(int(a,16),d)
    return Fraction(x)

def qstr(x):
    z=F(x)
    return 'hex:'+format(z.numerator,'x')+'/'+format(z.denominator,'x')

def encode(x):
    if isinstance(x,Fraction): return qstr(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v) for v in x]
    return x

def canonical(x):return json.dumps(encode(x),sort_keys=True,separators=(',',':')).encode()
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()
def write(path,x):path.write_text(json.dumps(encode(x),indent=2)+'\n')

def bits(x):
    out={'numerator_bits':0,'denominator_bits':0,'rational_count':0}
    def visit(z):
        if isinstance(z,Fraction) or isinstance(z,str) and z.startswith('hex:'):
            a=F(z);out['numerator_bits']=max(out['numerator_bits'],abs(a.numerator).bit_length())
            out['denominator_bits']=max(out['denominator_bits'],a.denominator.bit_length());out['rational_count']+=1
        elif isinstance(z,dict):
            for v in z.values():visit(v)
        elif isinstance(z,(list,tuple)):
            for v in z:visit(v)
    visit(x);return out
