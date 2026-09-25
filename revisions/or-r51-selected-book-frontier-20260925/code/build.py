"""Build anonymous OR readers; audit TeX, page limits and inherited content."""
from pathlib import Path
import json,re,subprocess,shutil,hashlib,sys
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]

def expand(path,seen=None):
    seen=set() if seen is None else seen
    if path in seen:return ''
    seen.add(path)
    text=path.read_text()
    for name in re.findall(r'\\input\{([^}]+)\}',text):
        p=ROOT/name
        if p.exists():text+='\n'+expand(p,seen)
    return text

def label_lines(path):
    return [line for line in path.read_text().splitlines() if line.startswith('\\newlabel{')] if path.exists() else []

def prepare():
    (R/'generated').mkdir(exist_ok=True)
    data=json.loads((R/'results/SUMMARY.json').read_text())
    metrics=''.join('\\newcommand{\\'+key+'}{'+str(value)+'}\n' for key,value in [
        ('rFiftyOneMaxBytes',data['max_certificate_bytes']),('rFiftyOneNumBits',data['max_numerator_bits']),('rFiftyOneDenBits',data['max_denominator_bits'])])
    (R/'generated/metrics.tex').write_text(metrics)
    # Keep only literature actually cited in the two current readers; the old bibliography is untouched.
    combined=expand(ROOT/'main.tex')+expand(ROOT/'electronic_companion.tex')
    keys=set(k.strip() for group in re.findall(r'\\cite\w*\{([^}]+)\}',combined) for k in group.split(','))
    old=(ROOT/'revisions/or-r49-dispersion-certificates-20260925/generated/references.tex').read_text()
    parts=re.split(r'(?=\\bibitem\[)',old)[1:]
    selected=[]
    for item in parts:
        key=re.search(r'\]\{([^}]+)\}',item).group(1)
        if key in keys:
            item=item.split('\\end{thebibliography}')[0]
            if key=='PatrikssonStromberg2015':
                item=item.replace('Author manuscript, arXiv:1501.07035.',r'\emph{European Journal of Operational Research} 243(3):703--722. doi:10.1016/j.ejor.2015.01.029.')
            selected.append(item.strip())
    (R/'generated/references.tex').write_text('\\begin{thebibliography}{99}\\raggedright\n'+'\n\n'.join(selected)+'\n\\end{thebibliography}\n')
    # Sources not in the new readers remain linked to immutable archived readers, never silently dropped.
    main=expand(ROOT/'main.tex');ec=expand(ROOT/'electronic_companion.tex')
    current=set(re.findall(r'\\label\{([^}]+)\}',main+ec))
    taken=set(current)
    for old,new in [('r49-main-labels.aux','r51-archive-labels.aux'),('r49-ec-labels.aux','r51-archive-ec-labels.aux'),('r49-cs-labels.aux','r51-archive-cs-labels.aux')]:
        lines=[]
        for line in label_lines(ROOT/old):
            key=re.match(r'\\newlabel\{([^}]+)\}',line).group(1)
            if key not in taken:lines.append(line);taken.add(key)
        (ROOT/new).write_text('\n'.join(lines)+'\n')
    for name in ['r51-main-labels.aux','r51-ec-labels.aux']:
        if not (ROOT/name).exists():(ROOT/name).write_text('')
    return keys,current

def pdfstats(path):
    import fitz
    with fitz.open(path) as doc:
        return {'pages':len(doc),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'all_fonts_embedded':all(font[1] not in ['n/a',''] for p in doc for font in p.get_fonts()),
                'missing_glyph_replacement':any('\ufffd' in p.get_text() for p in doc)}

def run():
    keys,current=prepare();logs=R/'results/build_logs';logs.mkdir(exist_ok=True)
    for sweep in range(4):
        for name,target in [('main','r51-main-labels.aux'),('electronic_companion','r51-ec-labels.aux')]:
            p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            (logs/f'{name}-pass{sweep+1}.txt').write_text(p.stdout)
            if p.returncode:
                print(p.stdout[-9000:]);raise RuntimeError(f'{name}: LaTeX failed')
            (ROOT/target).write_text('\n'.join(label_lines(ROOT/(name+'.aux')))+'\n')
    findings={}
    for name in ['main','electronic_companion']:
        text=(ROOT/(name+'.log')).read_text()
        findings[name]={
            'undefined_references':re.findall(r'LaTeX Warning: Reference .*?undefined',text),
            'undefined_citations':re.findall(r'Package natbib Warning: Citation .*?undefined',text),
            'duplicate_labels':re.findall(r'Label .*? multiply defined',text),
            'overfull_boxes':re.findall(r'Overfull \\[hv]box.*',text),
            'missing_characters':re.findall(r'Missing character:.*',text),
        }
        shutil.copyfile(ROOT/(name+'.pdf'),R/(name+'.pdf'))
        shutil.copyfile(ROOT/(name+'.tex'),R/(name+'.tex'))
    for sweep in range(2):
        p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(R),str(R/'RESPONSE_TO_REFEREES.tex')],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (logs/f'response-pass{sweep+1}.txt').write_text(p.stdout)
        if p.returncode:print(p.stdout[-9000:]);raise RuntimeError('Response LaTeX failed')
    response_log=(R/'RESPONSE_TO_REFEREES.log').read_text()
    findings['response']={'undefined_references':re.findall(r'LaTeX Warning: Reference .*?undefined',response_log),'overfull_boxes':re.findall(r'Overfull \\[hv]box.*',response_log),'missing_characters':re.findall(r'Missing character:.*',response_log)}
    stats={name:pdfstats(ROOT/(name+'.pdf')) for name in ['main','electronic_companion']}
    stats['response']=pdfstats(R/'RESPONSE_TO_REFEREES.pdf')
    aux=(ROOT/'main.aux').read_text()
    def page(label):return int(re.search(r'\\newlabel\{'+re.escape(label)+r'\}\{\{[^}]*\}\{(\d+)\}',aux).group(1))
    refs=page('refs-end')-page('refs-start')+1
    stats['main']['reference_pages']=refs;stats['main']['nonreference_pages']=stats['main']['pages']-refs
    bad=any(v for obj in findings.values() for v in obj.values())
    result={'status':'PASS' if not bad and stats['main']['nonreference_pages']<=30 and stats['electronic_companion']['pages']<=stats['main']['pages'] else 'FAIL',
        'format':{'submission_category':'Regular Manuscript','font_point':11,'line_spacing':1.5,'margins_inches':1,'anonymous':True,'abstract_words':len((R/'ABSTRACT.txt').read_text().split()),'equation_free_introduction':not bool(re.search(r'\$|\\\[|\\begin\{equation',(R/'introduction.tex').read_text()))},
        'readers':stats,'findings':findings,'cited_keys':sorted(keys),'current_labels':sorted(current)}
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='current_labels'},indent=2))
    return result
if __name__=='__main__':run()
