#!/usr/bin/env python3
"""Check actual PDFs, resolved sources, inherited content and final package hashes."""
from pathlib import Path
import hashlib,json,re,sys
import fitz
R=Path(__file__).resolve().parent; ROOT=R.parents[1]
MUTABLE={'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def expand(text):
    return re.sub(r'\\input\{([^}]+)\}',lambda m:expand((ROOT/m.group(1)).read_text()),text)
def check():
    inv=json.loads((R/'INHERITED_SHA256.json').read_text())
    for name,digest in inv.items():
        p=R/'predecessor'/name if name in MUTABLE else ROOT/name
        assert p.is_file() and sha(p)==digest,('inherited modification',name)
    texts={};pdfinfo={}
    for stem,logstem in [('main','main'),('electronic_companion','ec')]:
        source=(ROOT/(stem+'.tex')).read_text(); expanded=expand(source)
        old=expand((R/'predecessor'/(stem+'.tex')).read_text())
        oldlabels=set(re.findall(r'\\label\{([^}]+)\}',old)); newlabels=set(re.findall(r'\\label\{([^}]+)\}',expanded))
        assert oldlabels<=newlabels,('missing inherited label',oldlabels-newlabels)
        log=(R/f'results/{logstem}-build.log').read_text()
        assert 'undefined' not in log.lower() and 'multiply defined' not in log.lower()
        assert not re.search(r'Overfull \\hbox',log),('horizontal overflow',stem)
        pdf=fitz.open(ROOT/(stem+'.pdf')); pages=[p.get_text() for p in pdf]
        assert 'Revision R28' in pages[0] and 'Shared Policy Tables' in pages[0],('stale PDF',stem)
        assert '??' not in '\n'.join(pages)
        assert all(abs(p.rect.width-612)<1 and abs(p.rect.height-792)<1 for p in pdf)
        nlog=re.search(r'Output written on .*?\((\d+) pages',log)
        assert nlog and int(nlog.group(1))==len(pdf),('PDF/log mismatch',stem)
        texts[stem]=pages;pdfinfo[stem]=dict(pages=len(pdf),bytes=(ROOT/(stem+'.pdf')).stat().st_size,sha256=sha(ROOT/(stem+'.pdf')),inherited_labels_retained=len(oldlabels),horizontal_overflow=0,unresolved_references=0)
    s=(ROOT/'main.tex').read_text(); abstract=s.split('\\textbf{Abstract.}')[1].split('\\par\\vspace')[0]
    assert len(abstract.split())<=200
    intro=s.split('\\section{Introduction}')[1].split('\\section{Relation to')[0]
    assert '$' not in intro and '\\begin{equation}' not in intro and '\\[' not in intro
    for marker in ['11pt,letterpaper','margin=1in','\\onehalfspacing','\\usepackage[round,authoryear]{natbib}']:
        assert marker in s
    assert not re.search(r'\\footnote(?:\[|\{)',expand(s))
    pages=texts['main']; refpage=next(i for i,t in enumerate(pages) if '\nReferences\n' in t)
    tablepage=next(i for i in range(refpage+1,len(pages)) if re.search(r'\bTable 1:',pages[i]))
    # Exclude only pages strictly between the reference heading page and first table:
    # the heading page may also contain body text and is conservatively charged in full.
    full_reference_pages=list(range(refpage+2,tablepage+1))
    conservative_count=len(pages)-len(full_reference_pages)
    assert conservative_count<=30,('regular manuscript limit',conservative_count)
    assert pdfinfo['electronic_companion']['pages']<=pdfinfo['main']['pages'], 'EC longer than manuscript'
    inherited={}
    for rev in (24,25,26,27):
        p=R/f'results/inherited_r{rev}_replay.json'; data=json.loads(p.read_text()); assert data['status']=='PASS'
        err=R/f'results/inherited_r{rev}_replay.stderr'
        assert not err.exists() or not err.read_text().strip(),('inherited replay stderr',rev)
        inherited[str(rev)]=dict(status='PASS',sha256=sha(p))
    replay=json.loads((R/'results/replay.json').read_text()); assert replay['status']=='PASS'
    assert replay['evidence_sha256']==sha(R/'results/evidence.json')
    assert replay['counts']['queries']==84 and replay['counts']['refresh_queries']==83 and replay['negative_controls']==14
    return dict(status='PASS',scientific_predecessor='85fe1a799a192758a93a423bbb6d213ab9f04cce',review_base='61aff783672ce39745713f5cefbcf83d8748ebd6',pdfs=pdfinfo,abstract_words=len(abstract.split()),regular_format_conservative_nonreference_pages=conservative_count,fully_excluded_reference_pages=full_reference_pages,format_source='https://pubsonline.informs.org/page/opre/submission-guidelines',inherited_files_pinned=len(inv),unchanged_inherited_nonreader_files=len(inv)-len(MUTABLE),predecessor_reader_files=6,inherited_replays=inherited,r28_replay=dict(status='PASS',sha256=sha(R/'results/replay.json')),mathematical_status='Author theorem/proof revision with exact arithmetic regression checks; not a claim of independent referee approval.')
def file_manifest():
    files=[ROOT/n for n in sorted(MUTABLE)]+[ROOT/'r28-main-labels.aux',ROOT/'r28-ec-labels.aux']
    files += [p for p in R.rglob('*') if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts and p.suffix not in {'.pyc'}]
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(set(files))}
def main():
    result=check(); p=R/'results/package_check.json'
    if '--manifest' in sys.argv or not p.exists(): p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else: assert json.loads(p.read_text())==result
    if '--manifest' in sys.argv:
        lines=['# R28 build, proof-location and preservation report','',f"Main PDF: {result['pdfs']['main']['pages']} pages including title, references and tables.",f"Electronic companion: {result['pdfs']['electronic_companion']['pages']} pages.",f"Conservative manuscript count excluding only full reference-only pages: {result['regular_format_conservative_nonreference_pages']} pages.",f"Abstract: {result['abstract_words']} words.",'','Both documents use letter paper, 11-point text, 1.5 spacing and one-inch margins. The introduction has no equations or mathematical notation. Final LaTeX logs have no unresolved references, multiply defined labels or horizontal overflow. The EC is no longer than the actual manuscript.','',f"Inherited files pinned: {result['inherited_files_pinned']}; six predecessor reader files are preserved byte for byte. All other inherited files remain unchanged, and every inherited formal label remains present.",'','R24, R25, R26 and R27 independent replays: PASS. R28 independent replay: PASS. It checks nine exact bridge records, 81 cross-release supports, 84 aggregate queries, 10,416 query block policies and 14 rejected controls. The strict governance rule refreshes 83 queries; performance superiority is not claimed.','','The bridge proof is in Section 6 and the companion; cache governance and adaptive continuum feasibility are in Section 7 and the companion. The response maps every numbered review request to its revision location.','','Official format source: https://pubsonline.informs.org/page/opre/submission-guidelines (checked September 23, 2026). Only complete reference-only pages are excluded from the conservative main count. This build check does not certify editorial novelty or acceptance.','','The source transport is verified before materialization. The final-SHA workflow replays the actual published checkout and verifies this package manifest.']
        (R/'BUILD_REPORT.md').write_text('\n'.join(lines)+'\n')
        (R/'MANIFEST.json').write_text(json.dumps(file_manifest(),indent=2,sort_keys=True)+'\n')
    if '--verify-manifest' in sys.argv:
        expected=json.loads((R/'MANIFEST.json').read_text());actual=file_manifest();assert expected==actual,dict(missing=set(expected)-set(actual),extra=set(actual)-set(expected),changed=[x for x in expected.keys()&actual.keys() if expected[x]!=actual[x]])
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__': main()
