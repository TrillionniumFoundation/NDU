"""Assemble new readers while preserving exact scientific-parent entry points."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
OLD=ROOT/'revisions/or-r52-resource-path-20260925'
PARENT='7bdfda8f84b84f491e80b50a86089c37ea4c7f3a'
PREFIX=str(R.relative_to(ROOT))

def parent_bytes(name):
    if (ROOT/'.git').exists():
        return subprocess.check_output(['git','show',f'{PARENT}:{name}'],cwd=ROOT)
    saved=R/'predecessor'/name
    if saved.exists():return saved.read_bytes()
    raise RuntimeError('Assembly needs the Git parent or exact predecessor copies')

def run():
    (R/'predecessor').mkdir(exist_ok=True)
    names=['main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']
    originals={name:parent_bytes(name) for name in names}
    for name,data in originals.items():(R/'predecessor'/name).write_bytes(data)
    paragraph='A uniform deletion envelope further separates harmful refinement from irrelevant candidate proliferation. It bounds the payoff contribution of a non-anchor command in every possible selected neighboring context by a single minimum-command expression. A command whose opening charge covers this envelope can be removed without changing any individual target or the optimal value. All certified removals can be made together, and the bounds do not depend on other non-anchor candidates. A checked global interval on the reduced catalog then transfers to the original catalog through a separately verified exclusion record. This is an optimization guarantee, not a conclusion drawn from observing an unchanged incumbent.\n\n'
    intro=(OLD/'introduction.tex').read_text().replace('Our analysis uses classical tools with specific roles.',paragraph+'Our analysis uses classical tools with specific roles.')
    (R/'introduction.tex').write_text(intro)
    con=(OLD/'conclusion.tex').read_text().replace('The theory and the synthetic evidence answer different questions.','The capacity potential shows that eligibility changes returns but not the conserved resource capacity. Anchor-envelope screening then removes certified non-anchor alternatives at their original targets and transfers global intervals across otherwise irrelevant refinements. Its equality case preserves an optimal decision without asserting that all optimal decisions are identical.\n\nThe theory and the synthetic evidence answer different questions.')
    (R/'conclusion.tex').write_text(con)
    main=originals['main.tex'].decode();abstract=(R/'ABSTRACT.txt').read_text().strip()
    start=main.index('A renewal provider');end=main.index('\n\\par\\vspace',start)
    main=main[:start]+abstract+main[end:]
    main=main.replace('September 25, 2026','September 26, 2026')
    main=main.replace('\\input{revisions/or-r52-resource-path-20260925/introduction.tex}',f'\\input{{{PREFIX}/introduction.tex}}')
    for name,addition in [('selected_boundaries','capacity_potential'),('common_and_robustness','safe_catalog')]:
        oldinput=f'\\input{{revisions/or-r52-resource-path-20260925/{name}.tex}}'
        main=main.replace(oldinput,oldinput+f'\n\\input{{{PREFIX}/{addition}.tex}}')
    main=main.replace('\\input{revisions/or-r52-resource-path-20260925/conclusion.tex}',f'\\input{{{PREFIX}/study53.tex}}\n\\input{{{PREFIX}/conclusion.tex}}')
    main=main.replace('\\clearpage\\end{document}',f'\\clearpage\\input{{{PREFIX}/generated/main_table.tex}}\n\\clearpage\\end{{document}}')
    ec=originals['electronic_companion.tex'].decode().replace('.build/r52/main','.build/r53/main')
    ec=ec.replace('\\clearpage\\input{revisions/or-r52-resource-path-20260925/references.tex}',f'\\input{{{PREFIX}/catalog_ec.tex}}\n\\clearpage\\input{{revisions/or-r52-resource-path-20260925/references.tex}}')
    for name,content in [('main.tex',main),('electronic_companion.tex',ec)]:
        (R/name).write_text(content);(ROOT/name).write_text(content)
    response=(OLD/'RESPONSE_TO_REFEREES.tex').read_text().replace('.build/r52/main','.build/r53/main')
    response=response.replace('\\input{revisions/or-r52-resource-path-20260925/response_body.tex}',f'\\input{{{PREFIX}/response_body.tex}}')
    (R/'RESPONSE_TO_REFEREES.tex').write_text(response)
    (ROOT/'README.md').write_bytes((R/'README.md').read_bytes())
    checklist='# Operations Research R53 reader checks\n\nAnonymous readers, a 182-word text-only abstract, equation-free introduction, 11-point text, one-inch margins, one-and-one-half spacing, author-year references, and numbered tables after references. The code/data statement follows the body. BUILD_VALIDATION.json supplies measured page counts and layout diagnostics; PRESERVATION_MANIFEST.json supplies the full inherited-blob audit. Synthetic inputs, comparison scope, and certificate costs are stated explicitly. No editorial acceptance or field calibration is inferred from compilation.\n\nGuideline source checked September 26, 2026: https://pubsonline.informs.org/page/opre/submission-guidelines\n'
    (R/'NDU_OR_submission_checklist.md').write_text(checklist);(ROOT/'NDU_OR_submission_checklist.md').write_text(checklist)
if __name__=='__main__':run()
