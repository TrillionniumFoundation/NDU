"""Verify and unpack the R48 scientific sources, then preserve exact base readers."""
from pathlib import Path, PurePosixPath
import base64
import hashlib
import importlib.util
import json
import lzma
import subprocess

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
BRANCH = 'revision/ndu-operations-research-r48-harmonic-coarsening-20260925'
BASE = 'df1e192fd0846315ff0938e57d797efcd04109aa'
COMPRESSED_SHA256 = 'e4692a91595978e4f2e4b8d3a74863bad34e32afc8b951a4009d44e9216e6fd6'
PART_SHA256 = [
    '67579bdeaec6029b1118ed18f981bf6d11b6fb51f22e31647a1a90fb91620e4a',
    'a0776311a5ab43c50f9d23a538c7428248af28e955b307d93f14b641ee3ef64d',
    '4478e25b022bd8e00bd72c4cccab2463aa178f8521c40b636454a413e910f5bd',
    '9bd57e371a1f8dc71cf4260b43c2456e7f343353139371aba0c8913e24cd46f4',
    '9599d6d6f936fb0bde45a49d96a0c667f8b0cdc40b4d163a605b5e974155499f',
    '3b28d2ebcd091ac617e0cbf1ba5454728d1218ff3125d280b34909da035f5738',
]

def main() -> None:
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    if branch != BRANCH:
        raise RuntimeError('Refusing publication outside the isolated R48 branch')
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT, check=True)
    parts = []
    for i, expected in enumerate(PART_SHA256):
        raw = (R / 'transport' / f'part-{i:02d}.b64').read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f'Source transport checksum failure in part {i}')
        parts.append(raw.strip())
    compressed = base64.b64decode(b''.join(parts), validate=True)
    if hashlib.sha256(compressed).hexdigest() != COMPRESSED_SHA256:
        raise ValueError('Compressed source checksum failure')
    sources = json.loads(lzma.decompress(compressed))
    if not isinstance(sources, dict) or len(sources) != 19:
        raise ValueError('Unexpected source manifest')
    manifest = {}
    for name, text in sorted(sources.items()):
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or not isinstance(text, str):
            raise ValueError('Unsafe source path or content')
        destination = R / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = text.encode('utf-8')
        destination.write_bytes(data)
        manifest[name] = hashlib.sha256(data).hexdigest()
    (R / 'TRANSPORT_MANIFEST.json').write_text(json.dumps({
        'base': BASE, 'compressed_sha256': COMPRESSED_SHA256,
        'files': manifest, 'status': 'PASS'
    }, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('r48_preservation', R / 'code' / 'preservation.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.prepare()
    print('Verified 19 scientific source files and preserved all six exact predecessor readers/indexes.')

if __name__ == '__main__':
    main()
