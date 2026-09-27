"""Nonmutating verification of actual manuscript contents, preservation and evidence."""
import hashlib,json,re,sys
from pathlib import Path
import fitz
R=Path(__file__).resolve().parent;ROOT=R.parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda n:json.loads((R/n).read_text())
def run(check=False):
 main=(ROOT/'main.tex').read_text();ec=(ROOT/'electronic_companion.tex').read_text();combined=main+'\n'+ec
 for t in (main,ec):
  assert '\\documentclass[11pt,letterpaper]{article}' in t and '\\onehalfspacing' in t
  assert '\\usepackage[margin=1in]{geometry}' in t and 'Revision R23' in t
  assert '\\usepackage[tablesonly,nomarkers,nolists,noheads]{endfloat}' in t
  assert '\\input{' not in t and '\\footnote{' not in t
 ab=main.split('\\textbf{Abstract.}')[1].split('\\par\\vspace')[0]
 words=len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*",ab));assert words<=200
 intro=main.split('\\section{Introduction}')[1].split('\\section{')[0]
 assert '$' not in intro and '\\begin{equation}' not in intro
 preserved=0
 for name in ('main.tex','electronic_companion.tex'):
  for m in re.finditer(r'\\begin\{(theorem|proposition|lemma|corollary|definition|assumption|proof)\}.*?\\end\{\1\}',(R/'predecessor'/name).read_text(),re.S):
   assert m.group() in combined,('Deleted original mathematical block',name,m.group()[:100]);preserved+=1
 for name,h in load('PREDECESSOR_SHA256.json').items():assert sha(R/'predecessor'/name)==h
 md=fitz.open(ROOT/'main.pdf');ed=fitz.open(ROOT/'electronic_companion.pdf')
 assert 'Revision R23' in md[0].get_text() and 'Revision R23' in ed[0].get_text()
 aux=(R/'results/tex-main.aux').read_text()
 def page(label):return int(re.search(r'\\newlabel\{'+label+r'\}\{\{[^}]*\}\{(\d+)\}',aux).group(1))
 refs=page('r19-reference-end')-page('r19-reference-start')+1
 assert len(md)-refs<=40,(len(md),refs)
 assert len(ed)<=len(md),(len(ed),len(md))
 for d in (md,ed):
  assert all(p.rect.width==612 and p.rect.height==792 for p in d)
  assert not any('\ufffd' in p.get_text() for p in d)
 for name in ('main','electronic_companion'):
  log=(R/f'results/tex-{name}.log').read_text(errors='replace')
  for bad in ('undefined references','multiply defined','Overfull \\hbox','referenced but does not exist'):assert bad not in log,(name,bad)
  assert not re.search(r'Citation .* undefined',log)
 rep=load('results/replay.json');assert rep['status']=='PASS' and rep['policy_records']==1152 and rep['vertex_comparator_certificates']==3072
 assert rep['negative_controls_rejected']==6 and rep['nominal_diagnostic_records']==768
 summary=load('results/summary.json');assert summary['status']=='EXECUTED' and not summary['pilot']
 assert len(summary['summary'])==12 and all(x['n']==96 for x in summary['summary'])
 assert len(load('results/failures.json'))==summary['failed_solves']
 for name in ('RESPONSE_TO_REFEREE.md','PRESERVATION_MAP.md','LITERATURE_MAP.md','CLAIM_EVIDENCE.md','DESIGN.json','PROVENANCE.json'):assert (R/name).is_file()
 for key in ('thm:r23-robust','ec:r23-robust','ec:r23-preserved-global-proof','tab:r23-robust'):assert '\\label{'+key+'}' in combined
 answer={'status':'PASS','revision':'R23','main_pdf_pages':len(md),'main_reference_pages':refs,'main_pages_excluding_references':len(md)-refs,'companion_pdf_pages':len(ed),'abstract_words':words,'preserved_mathematical_blocks':preserved,'predecessor_hashes_verified':len(load('PREDECESSOR_SHA256.json')),'ordinary_complete_tex':True,'all_references_resolved':True,'no_overfull_text_lines':True,'robust_policy_replays':rep['policy_records'],'vertex_comparator_certificates':rep['vertex_comparator_certificates'],'nominal_diagnostics':rep['nominal_diagnostic_records'],'negative_controls_rejected':6,'main_pdf_sha256':sha(ROOT/'main.pdf'),'companion_pdf_sha256':sha(ROOT/'electronic_companion.pdf')}
 if check:
  assert load('results/package_check.json')==answer
  for name,h in load('MANIFEST.json')['sha256'].items():assert sha(ROOT/name)==h,('Manifest',name)
 else:(R/'results/package_check.json').write_text(json.dumps(answer,indent=2)+'\n')
 print(json.dumps(answer,indent=2))
if __name__=='__main__':run('--verify-manifest' in sys.argv)
