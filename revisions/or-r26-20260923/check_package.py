"""Check actual R26 sources/PDFs, preservation and optional complete manifest."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,re,sys
import fitz
R=Path(__file__).resolve().parent;B=R.parent.parent;O=R/'results'
ROOTS=['main.tex','main.pdf','main.bib','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md','r26-main-labels.aux','r26-ec-labels.aux']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def require(ok,msg):
    if not ok:raise ValueError(msg)
def mathblocks(s):
    pat=r'\\begin\{(theorem|proposition|lemma|corollary|assumption|remark|proof)\}.*?\\end\{\1\}'
    return [m.group(0) for m in re.finditer(pat,s,re.S)]
def inventory():
    paths=[B/f for f in ROOTS]
    for p in R.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts or p.name in {'MANIFEST.json','package_check.json','inherited_status.txt'}:continue
        if p.name.endswith(('.log','.txt')) and p.name!='requirements.txt':continue
        paths.append(p)
    review=B/'reviews/operation_research_referee_report_r24_independent_2026-09-23.md'
    if review.exists():paths.append(review)
    return {str(p.relative_to(B)):digest(p) for p in sorted(set(paths))}
def run():
    pre=load(R/'PREDECESSOR_SHA256.json')['files']
    for name,h in pre.items():require(digest(R/'predecessor'/name)==h,('predecessor changed',name))
    for name in ['computational_supplement.tex','computational_supplement.pdf','historical_supplement.tex','historical_supplement.pdf']:
        require(digest(B/name)==pre[name],('historical root changed',name))
    preserved=0
    for name in ('main.tex','electronic_companion.tex'):
        old=(R/'predecessor'/name).read_text();new=(B/name).read_text()
        for block in mathblocks(old):require(block in new,('mathematical block removed or changed',name,block[:120]));preserved+=1
    s=(B/'main.tex').read_text();abstract=s.split('\\textbf{Abstract.}')[1].split('\\par\\vspace')[0].strip()
    wc=len(abstract.split());require(wc<=200 and '$' not in abstract,('abstract',wc))
    intro=s.split('\\section{Introduction}')[1].split('\\section{')[0]
    require(not any(x in intro for x in ('$','\\[','\\begin{equation}')), 'introduction notation')
    require('\\footnote{' not in s,'footnotes')
    pages={};bad=[]
    for name in ('main','electronic_companion'):
        log=(O/(('main' if name=='main' else 'ec')+'-build.log')).read_text()
        for term in ('undefined','multiply defined','Overfull','! LaTeX Error'):require(term not in log,(name,term))
        doc=fitz.open(B/(name+'.pdf'));pages[name]=len(doc)
        require('??' not in ''.join(p.get_text() for p in doc),(name,'unresolved PDF reference'))
        for i,p in enumerate(doc):
            require(abs(p.rect.width-612)<1 and abs(p.rect.height-792)<1,'letter geometry')
            for block in p.get_text('blocks'):
                if block[0]<70 or block[2]>542:bad.append([name,i+1,list(block[:4])])
    require(not bad,('horizontal overflow',bad));require(pages['main']<=30 and pages['electronic_companion']<=pages['main'],'Regular manuscript length')
    rep=load(O/'replay.json');require(rep['status']=='PASS' and rep['total_primal_anchor_certificates']==4414,'new rational replay')
    require(rep['total_recursive_dual_planes']==1123 and len(rep['negative_controls_rejected'])==11,'new witness counts')
    for name in ('inherited_r25_replay.json','inherited_r24_replay.json'):
        require(load(O/name)['status']=='PASS',('inherited evidence failed',name))
    # Review content itself is imported by its existing Git blob, not rewritten.
    rfile=B/'reviews/operation_research_referee_report_r24_independent_2026-09-23.md'
    if rfile.exists():
        raw=rfile.read_bytes();gitsha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(gitsha=='4f45f76715936234d9f5738f798dd9e4f3b2dc4a','independent review changed')
    res={'status':'PASS','pdf_pages_including_title_references_tables':pages,'abstract_words':wc,'preserved_r25_mathematical_blocks':preserved,'preserved_predecessor_files':len(pre),'new_primal_anchors':4414,'new_recursive_upper_planes':1123,'negative_controls_rejected':11,'inherited_r25_and_r24_replays':'PASS','references':'resolved','horizontal_overflow':0,'independent_report_imported_in_runtime':rfile.exists()}
    (O/'package_check.json').write_text(json.dumps(res,indent=2)+'\n');return res
if __name__=='__main__':
    if '--verify-manifest' in sys.argv:
        expected=load(R/'MANIFEST.json');require(inventory()==expected['files'],'published manifest mismatch');print('PASS: actual published source/PDF/evidence hashes')
    else:
        print(json.dumps(run(),indent=2))
        if '--manifest' in sys.argv:(R/'MANIFEST.json').write_text(json.dumps({'schema':'ndu-r26-final-source-pdf-evidence-v1','scientific_base':'7f3f12c9d412b45a570725dc9b61203d64da5e41','files':inventory()},indent=2)+'\n')
