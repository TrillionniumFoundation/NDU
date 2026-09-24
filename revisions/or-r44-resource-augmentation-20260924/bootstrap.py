"""Assemble R44 readers from an immutable predecessor; never edit its sources."""
from pathlib import Path
import subprocess,re,json,hashlib
R=Path(__file__).resolve().parent; ROOT=R.parents[1]
OLD=ROOT/'revisions/or-r43-prefix-decomposition-20260924'
BASE='55313f79ad7d6b09c2edf1ceeafe254898a2bcbe'
BRANCH='revision/ndu-operations-research-r44-resource-augmentation-20260924'
for d in ['generated','results/certificates','predecessor']: (R/d).mkdir(parents=True,exist_ok=True)
if (ROOT/'.git').exists():
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    if branch!=BRANCH: raise RuntimeError('Refusing to assemble on another branch')
    for n in ['main.tex','electronic_companion.tex','main.pdf','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']:
        raw=subprocess.check_output(['git','show',BASE+':'+n],cwd=ROOT)
        p=R/'predecessor'/n
        if p.exists() and p.read_bytes()!=raw: raise RuntimeError('Predecessor mismatch: '+n)
        p.write_bytes(raw)

def replace(s,a,b):
    if a not in s: raise ValueError('Missing predecessor anchor: '+a[:100])
    return s.replace(a,b)

abstract=(R/'ABSTRACT.txt').read_text().strip()
assert len(abstract.split())==189
s=(OLD/'introduction.tex').read_text()
s=replace(s,'Our principal algorithmic result uses this contractual structure rather than enumerating all its possible local decisions.','Our algorithmic results use this contractual structure rather than enumerating all its possible local decisions.')
paragraph='''
The new recovery result makes this price oracle constructive even when the original price gap is positive. Two priced solutions determine a single installed union alphabet and exact branch targets; canonical union lotteries preserve the pre-draw service rule and every realization ceiling. With zero opening charges, allowing at most twice as many execution levels gives any prescribed additive accuracy relative to the original-budget catalog optimum, in polynomial computation with variable branch count and alphabet budget. Nonnegative opening charges enter through an explicit excess-charge term. This is a quantified resource tradeoff, not randomization of the installed interface or a claim that extra symbols are free. An exact example exhibits a strictly positive original price gap and its removal by the fixed union construction.
'''
s=replace(s,'\nThe method is part',paragraph+'\nThe method is part')
s=replace(s,'The result does not require catalog optimization to finish, and it does not claim an efficient approximation scheme for unrestricted alphabet budgets.','The bound applies before catalog search finishes. Combined with the new recovery theorem, it also gives a polynomial continuous-design comparison with an expanded alphabet; the unexpanded fixed-budget enumeration guarantee remains a separate result.')
s=replace(s,'HandlerZang1980}','HandlerZang1980,Lemarechal2001}')
(R/'introduction.tex').write_text(s)
s=(OLD/'conclusion.tex').read_text()
s=replace(s,'The new polynomial subproblem and verified completion bounds are not claims of polynomial global optimization or an FPTAS.','The price subproblem and verified completion bounds do not assert polynomial global optimization at the original budget. The two-price recovery theorem adds a distinct polynomial guarantee: a fixed union alphabet of at most twice the size achieves any prescribed additive accuracy when charges vanish, and an explicitly computed excess-charge penalty when they do not. Promise and realization feasibility remain exact. Feasible mesh transport extends this resource tradeoff to continuous design; it is not an FPTAS at unchanged memory.')
(R/'conclusion.tex').write_text(s)
s=(OLD/'data_statement.tex').read_text()
s=replace(s,'The accompanying repository provides',r'The current revision additionally supplies exact two-price recovery, independent fixed-union policy verification, all new certificates, and the expanded-alphabet study under \nolinkurl{revisions/or-r44-resource-augmentation-20260924}. The accompanying repository retains')
(R/'data_statement.tex').write_text(s)
s=(OLD/'generated/references.tex').read_text()
ref=r'''\bibitem[Lemar\'echal(2001)]{Lemarechal2001}
Lemar\'echal C (2001) Lagrangian relaxation. J\"unger M, Naddef D, eds. \emph{Computational Combinatorial Optimization}, Lecture Notes in Computer Science 2241 (Springer), 112--156. doi:10.1007/3-540-45586-8\_4.

'''
pos=s.index('\\bibitem[Pag'); s=s[:pos]+ref+s[pos:]
(R/'generated/references.tex').write_text(s)
main_old=(R/'predecessor/main.tex').read_text(); ec_old=(R/'predecessor/electronic_companion.tex').read_text()
s=main_old.replace('Exact Quadratic Design and Prefix Decomposition','Exact Quadratic Design and Resource Augmentation').replace('r43-ec-labels','r44-ec-labels')
start=s.index('\\textbf{Abstract.}')+len('\\textbf{Abstract.}'); end=s.index('\\par\\vspace{.15in}',start)
s=s[:start]+' '+abstract+'\n'+s[end:]
for name in ['introduction','conclusion','data_statement']:
    s=replace(s,'or-r43-prefix-decomposition-20260924/'+name,'or-r44-resource-augmentation-20260924/'+name)
s=replace(s,'or-r43-prefix-decomposition-20260924/generated/references','or-r44-resource-augmentation-20260924/generated/references')
for anchor,new in [('grid_certificate','augmentation'),('study','study')]:
    needle='\\input{revisions/or-r43-prefix-decomposition-20260924/'+anchor+'.tex}'
    s=replace(s,needle,needle+'\n\\input{revisions/or-r44-resource-augmentation-20260924/'+new+'.tex}')
s=replace(s,'\\end{document}','\\input{revisions/or-r44-resource-augmentation-20260924/generated/main_table.tex}\n\\end{document}')
(ROOT/'main.tex').write_text(s)
s=ec_old.replace('Exact Quadratic Design and Prefix Decomposition','Exact Quadratic Design and Resource Augmentation').replace('r43-main-labels','r44-main-labels')
s=replace(s,'\\input{revisions/or-r43-prefix-decomposition-20260924/generated/references.tex}','\\input{revisions/or-r44-resource-augmentation-20260924/generated/references.tex}')
needle='\\input{revisions/or-r42-certified-joint-design-20260924/study.tex}'
s=replace(s,needle,needle+'\n\\input{revisions/or-r44-resource-augmentation-20260924/augmentation_companion.tex}\n\\input{revisions/or-r44-resource-augmentation-20260924/protocol.tex}')
s=replace(s,'\\end{document}','\\clearpage\n\\input{revisions/or-r44-resource-augmentation-20260924/generated/companion_tables.tex}\n\\end{document}')
(ROOT/'electronic_companion.tex').write_text(s)
# Keep every inherited scientific reader input; only exposition and references are updated.
inputs=lambda text:set(re.findall(r'\\input\{([^}]+)\}',text))
prior=inputs(main_old+ec_old); current=inputs((ROOT/'main.tex').read_text()+s)
updated={'revisions/or-r43-prefix-decomposition-20260924/'+x+'.tex' for x in ['introduction','conclusion','data_statement','generated/references']}
missing=prior-current-updated
assert not missing,missing
(R/'CONTENT_PRESERVATION.json').write_text(json.dumps(dict(base=BASE,prior_direct_inputs=len(prior),unchanged_scientific_inputs=sorted(prior-updated),updated_exposition_inputs=sorted(updated),missing_scientific_inputs=[]),indent=2)+'\n')
# Reuse the tested reader builder, changing only identities and required R44 checks.
s=(OLD/'code/build.py').read_text()
s=s.replace('or-r43-prefix-decomposition-20260924','or-r44-resource-augmentation-20260924').replace('ndu-operations-research-r43-prefix-decomposition-20260924','ndu-operations-research-r44-resource-augmentation-20260924')
s=replace(s,"BASE='a0d1f4e3dfc3f7639f806cab01f1faae877d5361'","BASE='"+BASE+"'")
s=replace(s,'REVIEW=BASE',"REVIEW='a0d1f4e3dfc3f7639f806cab01f1faae877d5361'")
s=s.replace('ndu-r43','ndu-r44').replace('r43-main-labels','r44-main-labels').replace('r43-ec-labels','r44-ec-labels')
oldcheck="    if (ROOT/'.git').exists():\n        summary=json.loads((R/'results/study_summary.json').read_text())\n        assert summary['independent_nonlinear_runs']==6\n        assert summary['independent_comparisons_passed']==6"
newcheck="    verification=json.loads((R/'results/verification.json').read_text())\n    assert verification['exhaustive_comparisons']==144\n    assert len(verification['corruption_rejections'])==14\n    scaling=json.loads((R/'results/scaling.json').read_text())\n    assert len(scaling['rows'])==12 and all(x['independent_check'] for x in scaling['rows'])"
s=replace(s,oldcheck,newcheck)
(R/'code/build.py').write_text(s)
print('R44 reader inputs assembled; all inherited scientific inputs retained.')
