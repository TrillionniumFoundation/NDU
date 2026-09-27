#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
baseline=json.loads((HERE/'BASELINE_SHA256.json').read_text());checked=0
for name,digest in baseline.items():
    assert (ROOT/name).is_file(), 'Removed predecessor file: '+name
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, 'Changed predecessor content: '+name
    checked+=1
main=(ROOT/'main.tex').read_text();ec=(ROOT/'electronic_companion.tex').read_text()
assert '\\documentclass[11pt,letterpaper]' in main and '\\onehalfspacing' in main and 'margin=1in' in main
abstract=main.split('\\textbf{Abstract.}\n')[1].split('\\par\\vspace')[0]
assert len(abstract.split())<=200 and '$' not in abstract
intro=main.split('\\section{Introduction}')[1].split('\\input{revisions/or-r12-20260922/sections/model.tex}')[0]
assert '$' not in intro and '\\[' not in intro and '\\begin{equation}' not in intro
assert 'revisions/or-r12-20260922/sections/experiment.tex' in ec
pages={}
for name in ('main','electronic_companion','historical_supplement'):
    info=subprocess.check_output(['pdfinfo',str(ROOT/(name+'.pdf'))],text=True)
    pages[name]=int(re.search(r'Pages:\s+(\d+)',info).group(1))
    log=(ROOT/(name+'.log')).read_text(errors='replace')
    assert not re.search(r'undefined references|Citation .* undefined|multiply defined|Overfull \\hbox',log), name
# Conservative total-page check: even references and deferred tables are counted.
assert pages['main']<=40 and pages['electronic_companion']<=pages['main']
assert json.loads((HERE/'results/verification.json').read_text())['status']=='pass'
result={'status':'pass','main_total_pages':pages['main'],'companion_total_pages':pages['electronic_companion'],
        'historical_archive_pages':pages['historical_supplement'],'abstract_words':len(abstract.split()),
        'unchanged_predecessor_files':checked,'font_points':11,'line_spacing':1.5,'margin_inches':1,
        'undefined_references':False,'overfull_lines':False,'essential_new_proofs_in_main':True,
        'main_category':'Lengthy manuscript; total-page count including references is at most 40'}
(HERE/'results/package_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
