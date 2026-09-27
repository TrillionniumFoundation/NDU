#!/usr/bin/env python3
"""Preservation, source integrity, journal layout, and cross-reference checks."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
base=json.loads((HERE/'BASELINE_SHA256.json').read_text())
allowed={'README.md','NDU_OR_submission_checklist.md','main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','historical_supplement.pdf'}
unchanged=[];preserved=[]
for path,digest in base.items():
    p=ROOT/path
    if path in allowed:
        q=HERE/'predecessor'/path
        assert q.exists(),f'Missing predecessor snapshot: {path}'
        assert hashlib.sha256(q.read_bytes()).hexdigest()==digest,path
        preserved.append(path)
    else:
        assert p.exists(),f'Missing predecessor file: {path}'
        assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,f'Historical mutation: {path}'
        unchanged.append(path)
for doc in ['main','electronic_companion','historical_supplement']:
    log=(ROOT/(doc+'.log')).read_text()
    for bad in ['undefined references','multiply defined','Overfull \\hbox']:
        assert bad not in log,(doc,bad)
    assert not re.search(r'Citation .* undefined',log),doc
    text=subprocess.check_output(['pdftotext','-layout',str(ROOT/(doc+'.pdf')),'-'],text=True)
    assert '\ufffd' not in text,doc
main=(ROOT/'main.tex').read_text();abstract=main.split('\\textbf{Abstract.}')[1].split('\\par\\vspace')[0]
words=len(abstract.split());assert words<=200,words
intro=main.split('\\section{Introduction}')[1].split('\\input{revisions/or-r14-20260922/sections/model.tex}')[0]
assert '$' not in intro and '\\[' not in intro
assert '\\documentclass[11pt,letterpaper]{article}' in main and '\\usepackage[margin=1in]{geometry}' in main and '\\onehalfspacing' in main
for key in ['model','general_theory','network_structure']:
    assert (HERE/f'sections/{key}.tex').exists()
# PDF page counts from poppler, no extra PDF parsing dependency required.
def pages(doc):
    info=subprocess.check_output(['pdfinfo',str(ROOT/(doc+'.pdf'))],text=True)
    return int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
text=subprocess.check_output(['pdftotext','-layout',str(ROOT/'main.pdf'),'-'],text=True).split('\f')
ref_start=next(i for i,t in enumerate(text) if re.search(r'^\s*References\s*$',t,re.M))
first_table=next(i for i,t in enumerate(text[ref_start+1:],ref_start+1) if re.search(r'^\s*Table\s+1\b',t,re.M))
refs=first_table-ref_start
np=pages('main');ep=pages('electronic_companion');hp=pages('historical_supplement')
assert np-refs<=40,(np,refs)
assert ep<=np,(ep,np)
# The entire optional scalar precursor is input into the companion, unchanged.
assert '\\input{revisions/or-r10-20260921/sections/tree_structure.tex}' in (ROOT/'electronic_companion.tex').read_text()
result={'status':'PASS','base_commit':'808b8f0353051581134d3b8b5a7424422d4e48a8',
        'unchanged_predecessor_files':len(unchanged),'exact_root_snapshots':len(preserved),
        'main_pages':np,'reference_pages':refs,'main_pages_excluding_references':np-refs,
        'electronic_companion_pages':ep,'historical_archive_pages':hp,'abstract_words':words,
        'font_points':11,'line_spacing':1.5,'margin_inches':1,
        'undefined_references':False,'overfull_hboxes':False,'source_preservation':'PASS'}
(HERE/'results/package_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
