#!/usr/bin/env python3
"""Check typeset package, ordinary source closure, and preservation records."""
from pathlib import Path
import re,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent

def text(path):return subprocess.check_output(['pdftotext','-layout',str(path),'-'],text=True)

def pages(path):
    info=subprocess.check_output(['pdfinfo',str(path)],text=True)
    return int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))

def closure(path,seen):
    key=str(path.relative_to(ROOT))
    if key in seen:return
    assert path.is_file(),f'Missing ordinary input: {path}'
    seen.add(key);data=path.read_text()
    for m in re.finditer(r'\\input\{([^}]+)\}',data):
        target=ROOT/m.group(1)
        if not target.suffix:target=target.with_suffix('.tex')
        closure(target,seen)

def run():
    content=(ROOT/'main.tex').read_text()
    abstract=content.split(r'\textbf{Abstract.}',1)[1].split(r'\par\vspace',1)[0]
    words=len(abstract.split());assert words<=200
    intro=content.split(r'\section{Introduction}',1)[1].split(r'\input{',1)[0]
    assert not any(s in intro for s in ('$','\\[','\\(','\\begin{equation}'))
    counts={p:pages(ROOT/(p+'.pdf')) for p in ('main','electronic_companion','historical_supplement')}
    pp=text(ROOT/'main.pdf').split('\f');pp=[p for p in pp if p.strip()]
    refstart=next(i for i,p in enumerate(pp) if re.search(r'^\s*References\s*$',p,re.M))
    tabstart=next(i for i,p in enumerate(pp) if i>refstart and re.search(r'^\s*Table\s+1[.:]',p,re.M))
    refpages=tabstart-refstart;exrefs=counts['main']-refpages
    assert exrefs<=30,(counts,exrefs)
    assert counts['electronic_companion']<=counts['main'],counts
    seen=set()
    for name in ('main','electronic_companion','historical_supplement'):
        data=(ROOT/(name+'.tex')).read_text()
        assert '[11pt,letterpaper]' in data and r'\onehalfspacing' in data and 'margin=1in' in data
        closure(ROOT/(name+'.tex'),seen)
        log=(ROOT/(name+'.log')).read_text()
        assert not re.search(r'undefined references|Citation .* undefined|multiply defined|Overfull \\hbox',log)
        assert '??' not in text(ROOT/(name+'.pdf'))
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(seen)}
    # Ordinary copies of generated R7 sources; no generation prerequisite remains.
    for name in ('accepted','extensions','constructive_critics','legacy_study','model_structure'):
        assert (HERE/f'retained/{name}.tex').is_file()
    out={'pdf_pages':counts,'main_reference_pages':refpages,'main_pages_excluding_references':exrefs,
         'abstract_words':words,'ordinary_input_files':len(seen),'input_sha256':hashes,
         'format':'11-point, one-and-a-half spacing, one-inch margins, anonymous title page',
         'archive_status':'historical_supplement.pdf is a preserved archive, not part of the current journal EC',
         'unresolved_references':0,'overfull_hboxes':0}
    (HERE/'results/package_checks.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='input_sha256'},indent=2))
if __name__=='__main__':run()
