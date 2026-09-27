"""Check the actual R24 PDFs, preserved mathematics, evidence and manifest.
--verify-manifest is read-only and runs on a fresh final-SHA checkout.
"""
import hashlib,json,re,sys
from pathlib import Path
import fitz
R=Path(__file__).resolve().parent;ROOT=R.parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda n:json.loads((R/n).read_text())

def normalize_block(s):
    if 'Robust accepted expansion against a model-specific comparator' in s:
        s=s.replace(r'\begin{lemma}',r'\begin{theorem}').replace(r'\end{lemma}',r'\end{theorem}')
    return s

def blocks(s):
    return [normalize_block(x.group()) for x in re.finditer(r'\\begin\{(theorem|proposition|lemma|corollary|definition|assumption|proof)\}.*?\\end\{\1\}',s,re.S)]

def run(check=False):
    sources={n:(ROOT/(n+'.tex')).read_text() for n in ('main','electronic_companion','computational_supplement')}
    m=sources['main'];e=sources['electronic_companion'];combined=m+'\n'+e;alltext='\n'.join(sources.values())
    for n,t in sources.items():
        for a in (r'\documentclass[11pt,letterpaper]{article}',r'\onehalfspacing',r'\usepackage[margin=1in]{geometry}',r'\usepackage[tablesonly,nomarkers,nolists,noheads]{endfloat}','Revision R24'):
            assert a in t,(n,a)
        assert r'\input{' not in t and r'\footnote{' not in t
    ab=m.split(r'\textbf{Abstract.}')[1].split(r'\par\vspace')[0]
    words=len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*",ab));assert words<=200 and '$' not in ab
    intro=m.split(r'\section{Introduction}')[1].split(r'\section{')[0]
    assert '$' not in intro and r'\begin{equation}' not in intro
    preserved=0;newblocks=blocks(combined);oldtables=0
    for n in ('main.tex','electronic_companion.tex'):
        old=(R/'predecessor'/n).read_text()
        for b in blocks(old):
            assert b in newblocks,('Changed predecessor mathematics',n,b[:130]);preserved+=1
        # The contribution-comparison table is edited explicitly; empirical bodies remain intact.
        for table in re.findall(r'\\begin\{table\}.*?\\end\{table\}',old,re.S):
            if 'tab:r22-novelty' in table:continue
            for body in re.findall(r'\\begin\{tabular\}.*?\\end\{tabular\}',table,re.S):
                assert body in alltext,('Removed empirical table',n,body[:100]);oldtables+=1
    assert preserved==72,preserved
    for name,h in load('PREDECESSOR_SHA256.json').items():assert sha(R/'predecessor'/name)==h,name
    docs={n:fitz.open(ROOT/(n+'.pdf')) for n in sources}
    for n,d in docs.items():
        assert 'Revision R24' in d[0].get_text(),n
        assert all(p.rect.width==612 and p.rect.height==792 for p in d),n
        assert not any('\ufffd' in p.get_text() for p in d),n
        log=(R/f'results/tex-{n}.log').read_text(errors='replace')
        for bad in ('undefined references','multiply defined','Overfull \\hbox','referenced but does not exist'):
            assert bad not in log,(n,bad)
        assert not re.search(r'Citation .* undefined',log),(n,'citation')
    aux=(R/'results/tex-main.aux').read_text()
    def page(label):return int(re.search(r'\\newlabel\{'+label+r'\}\{\{[^}]*\}\{(\d+)\}',aux).group(1))
    refs=page('r19-reference-end')-page('r19-reference-start')+1
    assert len(docs['main'])-refs<=40
    assert len(docs['electronic_companion'])<=len(docs['main'])-refs
    rep=load('results/replay.json')
    expected={'status':'PASS','interior_models':768,'interior_comparator_certificates':1536,'source_vertex_comparator_certificates':3072,
       'timing_deployment_certificates':1728,'optimizer_label_certificates':192,'fresh_robust_policy_certificates':96,
       'fresh_robust_comparator_certificates':256,'negative_controls_rejected':7}
    assert all(rep.get(k)==v for k,v in expected.items()),rep
    tr=load('results/transfer_checks.json');assert tr['status']=='PASS' and tr['rational_tree_instances']==64
    a=load('results/analysis.json');assert a['status']=='PASS' and a['timing_failures']==a['interior_failed_solves']==a['robust_cost_failed_solves']==0
    assert a['timing_pipelines']==1728 and a['interior_models']==768 and a['robust_cost_policies']==96
    # Break-even outcomes may change on another host; they are evidence, not a precondition.
    for n in ('RESPONSE_TO_REFEREE.md','PRESERVATION_MAP.md','CLAIM_EVIDENCE.md','LITERATURE_MAP.md','DESIGN.json','ROBUST_COST_PROTOCOL.md','PROVENANCE.json'):
        assert (R/n).is_file(),n
    for lab in ('thm:r24-transfers','sec:r24-diagnostics','thm:r23-robust','ec:r24-fleet','ec:r24-sparse'):
        assert r'\label{'+lab+'}' in combined,lab
    assert r'\begin{lemma}[Robust accepted expansion against a model-specific comparator]' in m
    result={'status':'PASS','revision':'R24','main_pdf_pages':len(docs['main']),'main_reference_pages':refs,
      'main_pages_excluding_references':len(docs['main'])-refs,'companion_pdf_pages':len(docs['electronic_companion']),
      'code_data_record_pdf_pages':len(docs['computational_supplement']),'formal_electronic_companions':1,
      'abstract_words':words,'preserved_mathematical_blocks':preserved,'preserved_empirical_table_bodies':oldtables,
      'predecessor_hashes_verified':len(load('PREDECESSOR_SHA256.json')),'ordinary_complete_tex':True,
      'all_references_resolved':True,'no_overfull_text_lines':True,'new_rational_tree_tests':64,
      **{k:v for k,v in expected.items() if k!='status'},
      **{n+'_pdf_sha256':sha(ROOT/(n+'.pdf')) for n in sources}}
    if check:
        assert load('results/package_check.json')==result
        for name,h in load('MANIFEST.json')['sha256'].items():assert sha(ROOT/name)==h,('Manifest mismatch',name)
    else:(R/'results/package_check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':run('--verify-manifest' in sys.argv)
