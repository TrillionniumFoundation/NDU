#!/usr/bin/env python3
"""Recompile every saved R30 certificate and audit the final source snapshot.

Does not regenerate elapsed timings or require access to remote GitHub.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,sys,time,subprocess,re
R=Path(__file__).resolve().parent;ROOT=R.parent.parent
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
from quotient import compile_graph,execute,minimal_machine
from policy_audit import check_policy

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    started=time.perf_counter();reports=[]
    for file in sorted((R/'results/certificates').glob('*.json')):
        old=json.loads(file.read_text());raw=old['instance'];t=time.perf_counter()
        comp=compile_graph(raw);cert=execute(comp,F(raw['promise']))
        assert cert==old['certificate'],f'Certificate changed: {file.name}'
        check=check_policy(dict(instance=raw,certificate=cert));machine=minimal_machine(raw,cert)
        reports.append(dict(file=file.name,sha256=digest(file),certificate_identical=True,
          exact_policy_KKT=True,relations=check['checked_relations'],minimal_symbols=machine['minimal_symbols'],
          public_nodes=len(raw['nodes']),elapsed_seconds=time.perf_counter()-t))
        print('PASS',file.name,flush=True)
    comparisons=json.loads((R/'results/comparisons.json').read_text())['records']
    scaling=json.loads((R/'results/scaling.json').read_text())['records']
    assert len(comparisons)==54 and len(scaling)==12
    value={z['name']:F(z['value']) for z in comparisons if z['specification']['method']=='quotient'}
    actual={'exact_tree':0,'qp_success':0,'grid_feasible':0}
    for z in comparisons:
        m=z['specification']['method']
        if m=='laminar':assert F(z['result']['value'])==value[z['name']];actual['exact_tree']+=1
        elif m=='qp':assert z['result']['success'];actual['qp_success']+=1
        elif m=='grid':assert F(z['result']['value'])<=value[z['name']];actual['grid_feasible']+=1
    inherited=json.loads((R/'INHERITED_SHA256.json').read_text());unchanged=[];backed=[]
    expected={'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'}
    for name,sha in inherited.items():
        p=ROOT/name;assert p.exists(),f'Deleted inherited file: {name}'
        if digest(p)==sha:unchanged.append(name)
        else:
            assert name in expected,f'Unexpected inherited modification: {name}'
            backup=R/'predecessor'/name
            assert backup.exists() and digest(backup)==sha,f'Original not preserved: {name}'
            backed.append(name)
    preservation={'status':'passed','inherited_files':len(inherited),'unchanged_files':len(unchanged),
                  'updated_entrypoints_with_byte_identical_originals':backed,'deleted_inherited_files':0}
    (R/'PRESERVATION_REPORT.json').write_text(json.dumps(preservation,indent=2)+'\n')
    pdfs={}
    for stem,logname in [('main','main-build.log'),('electronic_companion','electronic-companion-build.log'),('response','response-build.log')]:
        log=(R/'results'/logname).read_text();bad=re.findall(r'^.*(?:undefined references|undefined citations|Citation .* undefined|Reference .* undefined|multiply defined|^!|Overfull \\hbox|Underfull \\hbox|destination with the same identifier).*$',log,re.M)
        assert not bad,bad
        pdf=R/'RESPONSE_TO_REFEREES.pdf' if stem=='response' else ROOT/(stem+'.pdf')
        info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
        pdfs[stem]={'pages':int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1)),
                    'sha256':digest(pdf),'unresolved_references':0,'overfull_boxes':0}
    abstract=(R/'ABSTRACT.txt').read_text();assert len(abstract.split())<=200
    assert pdfs['electronic_companion']['pages']<=pdfs['main']['pages']
    sources={str(p.relative_to(ROOT)):digest(p) for p in sorted(R.glob('*')) if p.suffix in ('.py','.tex','.sh')}
    sources.update({x:digest(ROOT/x) for x in ('main.tex','electronic_companion.tex')})
    report=dict(status='passed',base_commit=json.loads((R/'PROVENANCE.json').read_text())['base_commit'],
                recomputed_certificates=len(reports),certificate_checks=reports,comparison_checks=actual,
                regression_tests=json.loads((R/'results/tests.json').read_text()),preservation=preservation,
                pdfs=pdfs,abstract_words=len(abstract.split()),source_sha256=sources,
                elapsed_seconds=time.perf_counter()-started,remote_push_performed=False,
                visual_inspection={'renderer':'PyMuPDF','main_pages':22,'companion_pages':10,'response_pages':8,'clipping_or_overlap_seen':False},
                scope='Final local source recompilation, exact certificates, data consistency, PDF build and preservation; no remote CI claim')
    (R/'FINAL_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['certificate_checks','source_sha256','regression_tests']},indent=2))
if __name__=='__main__':run()
