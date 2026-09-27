"""Validate the actual R27 source/PDF/evidence package and ancestor preservation."""
from __future__ import annotations
import hashlib,json,re,sys
from fractions import Fraction as F
from pathlib import Path
import fitz
R=Path(__file__).resolve().parent;B=R.parent.parent;O=R/'results'
MUTABLE={'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'}
ROOTS=sorted(MUTABLE|{'main.bib','r27-main-labels.aux','r27-ec-labels.aux'})
def require(ok,msg):
    if not ok:raise ValueError(msg)
def load(p):return json.loads(Path(p).read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def blocks(text):
    return [m.group(0) for m in re.finditer(r'\\begin\{(theorem|proposition|lemma|corollary|assumption|remark|proof)\}.*?\\end\{\1\}',text,re.S)]
def expand(path):
    s=Path(path).read_text()
    def sub(match):
        p=B/match.group(1)
        if not p.suffix:p=p.with_suffix('.tex')
        require(p.is_file(),('missing input',str(p)));return expand(p)
    return re.sub(r'\\input\{([^}]+)\}',sub,s)

def check():
    inherited=load(R/'INHERITED_SHA256.json');unchanged=0
    for path,h in inherited.items():
        if path in MUTABLE:continue
        require((B/path).is_file() and digest(B/path)==h,('inherited file modified',path));unchanged+=1
    pre=load(R/'PREDECESSOR_SHA256.json')
    for path,h in pre['files'].items():require(digest(R/'predecessor'/path)==h,('predecessor copy changed',path))
    old_blocks=0
    for name in ('main.tex','electronic_companion.tex'):
        before=expand(R/'predecessor'/name);after=expand(B/name)
        for block in blocks(before):require(block in after,('removed mathematical statement/proof',name,block[:100]));old_blocks+=1
    text=(B/'main.tex').read_text();abstract=text.split('\\textbf{Abstract.}')[1].split('\\par\\vspace')[0].strip()
    wc=len(abstract.split());require(wc<=200 and '$' not in abstract,'abstract')
    intro=text.split('\\section{Introduction}')[1].split('\\section{')[0]
    require(not any(s in intro for s in ('$','\\[','\\begin{equation}')),'introduction equations')
    require('\\footnote{' not in expand(B/'main.tex'),'footnotes')
    require('Revision R27' in text and 'r27-ec-labels' in text,'wrong current revision')
    new=(R/'correlated_main.tex').read_text()
    require('(Dz-h)_a' not in new and r'\sum_j\left\{\kappa_j|(Dz-h)_j|' in new,'switch summation index mismatch')
    pages={};bad=[]
    for name in ('main','electronic_companion'):
        log=(O/(('main' if name=='main' else 'ec')+'-build.log')).read_text()
        for term in ('undefined','multiply defined','Overfull','! LaTeX Error'):require(term not in log,(name,term))
        doc=fitz.open(B/(name+'.pdf'));pages[name]=len(doc)
        require('??' not in ''.join(p.get_text() for p in doc),'unresolved PDF reference')
        for i,page in enumerate(doc):
            require(abs(page.rect.width-612)<1 and abs(page.rect.height-792)<1,'letter geometry')
            for b in page.get_text('blocks'):
                if b[0]<70 or b[2]>542:bad.append([name,i+1,list(b[:4])])
    require(not bad,('horizontal overflow',bad))
    require(pages['main']<=30 and pages['electronic_companion']<=pages['main'],'Regular paper/EC length')
    rep=load(O/'replay.json')
    for k,v in {'inherited_optimization_records_audited':160,'new_optimization_records_audited':72,'cached_anchors':24,'inherited_ray_holdouts':56,'new_off_ray_queries':24,'cached_price_evaluations':240,'online_restricted_optimization_calls':0,'exact_gap_decompositions':312,'uniform_cell_certificates':5,'new_positive_gain_certificates':24,'new_cache_tighter_than_outer':24}.items():require(rep[k]==v,('audit count',k))
    require(rep['status']=='PASS' and len(rep['negative_controls_rejected'])==14,'rational replay')
    require(F(rep['largest_optimization_bracket'])<F(6,10**8),'stated optimization tolerance')
    require(F(rep['new_mean_cache_slack_upper'])<=F('0.016632'),'stated cache mean')
    require(F(rep['new_mean_outer_slack_upper'])<=F('0.064069'),'stated outer mean')
    require(F(rep['new_min_cached_gain_lower'])>=F('0.762195'),'stated positive gain')
    for rev in (24,25,26):require(load(O/f'inherited_r{rev}_replay.json')['status']=='PASS',('inherited replay',rev))
    details={'status':'PASS','scientific_base':pre['scientific_base'],'pdf_pages_including_title_references_tables':pages,'abstract_words':wc,
             'inherited_files_pinned':len(inherited),'inherited_files_unchanged_at_original_paths':unchanged,'predecessor_root_copies':len(pre['files']),
             'preserved_expanded_mathematical_blocks':old_blocks,'new_optimizer_proposals_independently_audited':72,'new_queries':24,
             'cached_price_evaluations':240,'new_negative_controls_rejected':14,'inherited_r24_r25_r26_replays':'PASS',
             'references':'resolved','horizontal_overflow':0,'scope':'only six current root documents plus new R27 files and new label files; all earlier research files unchanged'}
    (O/'package_check.json').write_text(json.dumps(details,indent=2)+'\n')
    (R/'BUILD_REPORT.md').write_text('# R27 compiled package check\n\n```json\n'+json.dumps(details,indent=2)+'\n```\n\nThe separate final-SHA CI status validates the actual published commit, not only its source-generation commit.\n')
    return details

def inventory():
    paths=[B/f for f in ROOTS]
    for p in R.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts or p.name in {'MANIFEST.json','package_check.json'}:continue
        if p.suffix in {'.so','.log'} or p.name.endswith('_stdout.txt') or '-build-pass-' in p.name:continue
        paths.append(p)
    return {str(p.relative_to(B)):digest(p) for p in sorted(set(paths))}

if __name__=='__main__':
    if '--verify-manifest' in sys.argv:
        require(inventory()==load(R/'MANIFEST.json')['files'],'published manifest mismatch');print('PASS: published source, PDFs, evidence, and preservation manifest')
    else:
        print(json.dumps(check(),indent=2))
        if '--manifest' in sys.argv:
            (R/'MANIFEST.json').write_text(json.dumps({'schema':'ndu-r27-source-pdf-evidence-v1','scientific_base':'38f99a5b46d8cfe4f1197fc869735d5f798c499a','files':inventory()},indent=2)+'\n')
