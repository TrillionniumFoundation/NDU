#!/usr/bin/env python3
"""Check the actual manuscripts, scientific artifacts, and immutable snapshots."""
import sys,json,re,hashlib
from pathlib import Path
import fitz
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(p):
    b=p.read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def run():
    main=(ROOT/'main.tex').read_text();ec=(ROOT/'electronic_companion.tex').read_text()
    assert '\\documentclass[11pt,letterpaper]{article}' in main and '\\onehalfspacing' in main
    assert '\\usepackage[margin=1in]{geometry}' in main
    for text in [main,ec]:
        assert '\\footnote{' not in text
        assert '\\usepackage[tablesonly,nomarkers,nolists,noheads]{endfloat}' in text
    abstract=main.split('\\textbf{Abstract.}',1)[1].split('\\par\\vspace',1)[0]
    words=len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*",abstract));assert words<=200,words
    introduction=main.split('\\section{Introduction}',1)[1].split('\\section{',1)[0]
    assert '$' not in introduction and '\\begin{equation}' not in introduction
    md=fitz.open(ROOT/'main.pdf');ed=fitz.open(ROOT/'electronic_companion.pdf');aux=(R/'results/tex-main.aux').read_text()
    def page(label):return int(re.search(r'\\newlabel\{'+label+r'\}\{\{[^}]*\}\{(\d+)\}',aux).group(1))
    refpages=page('r19-reference-end')-page('r19-reference-start')+1
    nonrefs=len(md)-refpages
    assert nonrefs<=40,(len(md),nonrefs)
    assert len(ed)<=len(md),(len(ed),len(md))
    assert all(p.rect.width==612 and p.rect.height==792 for p in list(md)+list(ed))
    for name in ['main','electronic_companion']:
        log=(R/'results'/('tex-'+name+'.log')).read_text(errors='replace')
        for bad in ['undefined references','multiply defined','Overfull \\hbox','referenced but does not exist']:
            assert bad not in log,(name,bad)
        assert not re.search(r'Citation .* undefined',log)
    expected={'main.tex':'e70021eee301b9752fc109d6867bb126209223e8','main.pdf':'f6a82badb3a4652e6d85245096327fa361d45981','electronic_companion.tex':'8d43f4142c7fa5bc14c9d6216531a1401bb80da4','electronic_companion.pdf':'d2fb15004ced8a01b67e3888dc7f13f942ad08de'}
    for name,b in expected.items():assert blob(R/'predecessor'/name)==b,(name,blob(R/'predecessor'/name))
    replay=json.loads((R/'results/replay.json').read_text());assert replay['total_independent_policy_replays']==16640
    for name in ['replay','reanalysis','matched_cost','boundary_checks','nonquadratic_checks']:
        assert json.loads((R/'results'/f'{name}.json').read_text())['status']=='PASS',name
    cost=json.loads((R/'results/matched_cost.json').read_text());assert cost['observations']==4608
    rows=json.loads((R/'results/matched_cost_rows.json').read_text());assert len(rows)==4608
    assert all(r['final_gap']<=r['tol'] for r in rows)
    for name in ['RESPONSE_TO_REFEREE.md','PRESERVATION_MAP.md','REVISION_PLAN.json']:assert (R/name).is_file()
    result={'status':'PASS','revision':'R19','main_pdf_pages':len(md),'main_reference_pages':refpages,'main_pages_excluding_references':nonrefs,'companion_pdf_pages':len(ed),'abstract_words':words,'all_references_resolved':True,'no_overfull_text_lines':True,'ordinary_complete_tex':True,'exact_predecessor_blobs_preserved':expected,'independent_policy_replays':16640,'quartic_exact_cases':64,'new_boundary_instances':64,'matched_cost_pipelines':4608,'main_pdf_sha256':sha(ROOT/'main.pdf'),'companion_pdf_sha256':sha(ROOT/'electronic_companion.pdf')}
    if '--verify-manifest' in sys.argv:
        manifest=json.loads((R/'MANIFEST.json').read_text())
        for name,h in manifest['sha256'].items():assert sha(ROOT/name)==h,name
        assert json.loads((R/'results/package_check.json').read_text())==result
    else:(R/'results/package_check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':run()
