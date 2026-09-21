#!/usr/bin/env python3
"""Revision integration, content-preservation, and build audit."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess
ROOT=Path(__file__).resolve().parents[2];BASE=Path(__file__).resolve().parent
ENTRY=['main.tex','electronic_companion.tex','historical_supplement.tex']

def inputs(name,seen=None):
    seen=set() if seen is None else seen
    if name in seen:return seen
    seen.add(name);path=ROOT/name;assert path.is_file(),f'Missing input {name}'
    for target in re.findall(r'\\input\{([^}]+)\}',path.read_text()):
        inputs(target if target.endswith('.tex') else target+'.tex',seen)
    return seen

def run(pdf=False):
    current=set()
    for name in ENTRY:current.update(inputs(name))
    old=set()
    for p in ['predecessor_main.tex','predecessor_electronic_companion.tex']:
        old.update(re.findall(r'\\input\{([^}]+)\}',(BASE/p).read_text()))
    refs='revisions/or-r7-20260921/sections/references.tex'
    missing=old-current-{refs};assert not missing,f'Unpreserved predecessor content: {missing}'
    oldkeys=set(re.findall(r'\\bibitem(?:\[[^]]*\])?\{([^}]+)\}',(ROOT/refs).read_text()))
    newkeys=set(re.findall(r'\\bibitem(?:\[[^]]*\])?\{([^}]+)\}',(BASE/'sections/references.tex').read_text()))
    assert oldkeys<=newkeys
    main=(ROOT/'main.tex').read_text()
    abstract=main.split('\\textbf{Abstract.}',1)[1].split('\\par\\vspace{.16in}',1)[0]
    assert len(abstract.split())<=200 and 'Revision R10' in main
    assert 'general_theory.tex' in main and 'certified_multistage.tex' in main
    assert 'R10' in (ROOT/'README.md').read_text()
    out={'status':'PASS','abstract_words':len(abstract.split()),'predecessor_inputs':len(old),
         'preserved_input_paths':sorted(old-{refs}),'replacement_bibliography_preserves_all_keys':True,
         'integrated_source_files':len(current),'pdfs':{}}
    if pdf:
        for name in ENTRY:
            path=ROOT/name.replace('.tex','.pdf');assert path.is_file()
            info=subprocess.check_output(['pdfinfo',str(path)],text=True)
            pages=int(re.search(r'Pages:\s+(\d+)',info).group(1))
            out['pdfs'][path.name]={'pages':pages,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            log=path.with_suffix('.log').read_text(errors='replace')
            for bad in ['undefined references','multiply defined','Overfull \\hbox']:
                assert bad not in log,(name,bad)
        assert out['pdfs']['electronic_companion.pdf']['pages']<=out['pdfs']['main.pdf']['pages']
    (BASE/'results/package_validation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--pdf',action='store_true');run(ap.parse_args().pdf)
