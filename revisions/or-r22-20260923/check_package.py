"""Validate actual R22 manuscripts and evidence; frozen verification never mutates."""
from pathlib import Path
import hashlib,json,re,sys
import fitz
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((R/name).read_text())
def run():
    main=(ROOT/'main.tex').read_text();ec=(ROOT/'electronic_companion.tex').read_text();combined=main+'\n'+ec
    for text in [main,ec]:
        assert '\\documentclass[11pt,letterpaper]{article}' in text
        assert '\\onehalfspacing' in text and '\\usepackage[margin=1in]{geometry}' in text
        assert '\\usepackage[tablesonly,nomarkers,nolists,noheads]{endfloat}' in text
        assert '\\footnote{' not in text and '\\input{' not in text
        assert 'Revision R22' in text
    abstract=main.split('\\textbf{Abstract.}',1)[1].split('\\par\\vspace',1)[0]
    words=len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*",abstract));assert words<=200,words
    intro=main.split('\\section{Introduction}',1)[1].split('\\section{',1)[0]
    assert '$' not in intro and '\\begin{equation}' not in intro
    preserved=0
    for name in ['main.tex','electronic_companion.tex']:
        text=(R/'predecessor'/name).read_text()
        for m in re.finditer(r'\\begin\{(theorem|proposition|lemma|corollary|definition|assumption|proof)\}.*?\\end\{\1\}',text,re.S):
            assert m.group() in combined,('Missing original mathematical block',name,m.group()[:150]);preserved+=1
    expected=read('PREDECESSOR_SHA256.json')
    for name,h in expected.items():assert sha(R/'predecessor'/name)==h,('Predecessor hash',name)
    md=fitz.open(ROOT/'main.pdf');ed=fitz.open(ROOT/'electronic_companion.pdf')
    aux=(R/'results/tex-main.aux').read_text()
    def page(label):return int(re.search(r'\\newlabel\{'+label+r'\}\{\{[^}]*\}\{(\d+)\}',aux).group(1))
    refpages=page('r19-reference-end')-page('r19-reference-start')+1
    assert len(md)-refpages<=40,('Lengthy limit',len(md),refpages)
    assert len(ed)<=len(md),('Companion exceeds main',len(ed),len(md))
    assert all(p.rect.width==612 and p.rect.height==792 for p in list(md)+list(ed))
    assert 'Revision R22' in md[0].get_text() and 'Revision R22' in ed[0].get_text()
    for name in ['main','electronic_companion']:
        log=(R/'results'/('tex-'+name+'.log')).read_text(errors='replace')
        for bad in ['undefined references','multiply defined','Overfull \\hbox','referenced but does not exist']:
            assert bad not in log,(name,bad)
        assert not re.search(r'Citation .* undefined',log),name
    for name in ['matched_summary','validation_summary','theory_checks','complete_dual_checks','replay','analysis']:
        assert read('results/'+name+'.json')['status']=='PASS',name
    cost=read('results/matched_rows.json');assert len(cost)==5120 and all(x['final_gap']<=x['tol'] for x in cost)
    val=read('results/validation_summary.json');assert val['observations']==5120 and len(val['summary'])==4
    scale=read('results/scaling_summary.json');assert scale['observations']==800 and scale['label_records']==640
    assert scale['status'] in ['PASS','FAILURES_RETAINED']
    replay=read('results/replay.json');assert replay['groups']['matched']==15360 and replay['groups']['validation']==15616
    assert replay['negative_controls_rejected']==4 and replay['component_identities']==320
    complete=read('results/complete_dual_checks.json')
    assert complete['exact_optimum_and_attainment_cases']==225
    assert complete['lower_dimensional_no_strict_feasibility_cases']==45
    assert complete['exact_projected_gradient_steps']==3600
    assert complete['new_context_certificate_transports']==450
    for name in ['RESPONSE_TO_REFEREE.md','PRESERVATION_MAP.md','DESIGN.json','LITERATURE_MAP.md','CLAIM_EVIDENCE.md']:
        assert (R/name).is_file(),name
    out={'status':'PASS','revision':'R22','main_pdf_pages':len(md),'main_reference_pages':refpages,
        'main_pages_excluding_references':len(md)-refpages,'companion_pdf_pages':len(ed),'abstract_words':words,
        'preserved_mathematical_blocks':preserved,'ordinary_complete_tex':True,'all_references_resolved':True,
        'no_overfull_text_lines':True,'predecessor_hashes_verified':len(expected),'new_policy_replays':replay['independent_policy_replays'],
        'complete_dual_exact_cases':225,'complete_dual_exact_steps':3600,'certificate_transports':450,
        'component_identities':320,'negative_controls_rejected':4,'matched_pipelines':5120,'deterministic_validation_observations':5120,
        'scaling_attempts':800,'scaling_labels':640,'scaling_failures_retained':replay['scaling_target_failures_retained'],
        'main_pdf_sha256':sha(ROOT/'main.pdf'),'companion_pdf_sha256':sha(ROOT/'electronic_companion.pdf')}
    if '--verify-manifest' in sys.argv:
        for name,h in read('MANIFEST.json')['sha256'].items():assert sha(ROOT/name)==h,('Manifest',name)
        assert read('results/package_check.json')==out
    else:(R/'results/package_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':run()
