"""Final reader allocation: article-specific proofs and evidence stay together.

No text is shortened to balance the readers. Broader inherited theory stays
in the electronic companion. New bounded-overrun and computational methods
sections move intact to article appendices; their measurement tables follow
the article references, together with the other current evidence tables.
"""
from pathlib import Path
import json
from prepare import ROOT, R, REL, bibliography, response_reader


def apply():
    modules = [REL+'/bounded_overrun.tex', REL+'/methodology.tex']
    measurement_tables = REL+'/generated/companion_tables.tex'
    main_path, ec_path = ROOT/'main.tex', ROOT/'electronic_companion.tex'
    main, ec = main_path.read_text(), ec_path.read_text()
    anchor = '\\clearpage\\phantomsection\\label{r37-refs-start}'
    insertion = '\\appendix\n'+'\n'.join('\\input{'+p+'}' for p in modules)+'\n'
    assert anchor in main and '\\appendix' not in main
    main = main.replace(anchor, insertion+anchor, 1)
    for path in modules+[measurement_tables]:
        marker = '\\input{'+path+'}\n'
        assert ec.count(marker) == 1
        ec = ec.replace(marker, '')
    main = main.replace('\\end{document}', '\\clearpage\n\\input{'+measurement_tables+'}\n\\end{document}')
    main_path.write_text(main)
    ec_path.write_text(ec)
    p = R/'companion_guide.tex'
    p.write_text(p.read_text().replace(
        'It also gives the bounded-overrun proofs and current computational methods.',
        'Paper-specific bounded-overrun proofs and current computational methods appear in the article appendices, with their measurement tables after the article references.'))
    p = R/'evidence.tex'
    text = p.read_text()
    for old in ('The companion gives the measurements and definitions.',
                'The article appendices give the definitions; the companion supplies the detailed memory and profile tables.'):
        text = text.replace(old, 'All current measurements and their definitions are reported in the article and its appendices.')
    p.write_text(text)
    p = R/'RESPONSE_TO_REFEREES.md'
    p.write_text(p.read_text().replace(
        'For any fixed codebook, the companion proves the exact branch rule.',
        'For any fixed codebook, the article appendix proves the exact branch rule.'))
    record = json.loads((R/'PRESERVATION_MAP.json').read_text())
    record['current_main_inputs'] += modules+[measurement_tables]
    record['current_companion_inputs'] = [p for p in record['current_companion_inputs'] if p not in modules+[measurement_tables]]
    record['reader_allocation'] = 'New paper-specific bounded-overrun proofs and computational methods appear intact in main-article appendices; all current measurement tables follow the article references. Broader inherited theory remains in the companion. No content removed to balance reader lengths.'
    (R/'PRESERVATION_MAP.json').write_text(json.dumps(record, indent=2)+'\n')
    p = R/'PRESERVATION_MAP.md'
    p.write_text(p.read_text()+'\n## Current article appendices and tables\n\nThe new bounded-overrun proofs and current computational methods appear intact in the main article appendices. Their memory and profile tables follow the main article references. These sections and tables are not deleted or relegated to a missing supplement. The broader inherited theory remains in the electronic companion.\n')
    bibliography(record['current_main_inputs'], REL+'/generated/main_references.tex')
    bibliography(record['current_companion_inputs'], REL+'/generated/companion_references.tex')
    response_reader()


if __name__ == '__main__':
    apply()
