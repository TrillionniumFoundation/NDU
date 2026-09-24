"""Final reader allocation: article-specific proofs in article appendices.

No text is shortened to balance the readers. The broader inherited theory
stays in the electronic companion; new bounded-overrun and computational
methods sections move intact to appendices of the current main article.
"""
from pathlib import Path
import json
import re
from prepare import ROOT, R, REL, bibliography, response_reader


def apply():
    modules = [REL+'/bounded_overrun.tex', REL+'/methodology.tex']
    main_path, ec_path = ROOT/'main.tex', ROOT/'electronic_companion.tex'
    main, ec = main_path.read_text(), ec_path.read_text()
    anchor = '\\clearpage\\phantomsection\\label{r37-refs-start}'
    insertion = '\\appendix\n'+'\n'.join('\\input{'+p+'}' for p in modules)+'\n'
    assert anchor in main and '\\appendix' not in main
    main = main.replace(anchor, insertion+anchor, 1)
    for path in modules:
        marker = '\\input{'+path+'}\n'
        assert ec.count(marker) == 1
        ec = ec.replace(marker, '')
    main_path.write_text(main)
    ec_path.write_text(ec)
    p = R/'companion_guide.tex'
    text = p.read_text().replace(
        'It also gives the bounded-overrun proofs and current computational methods.',
        'The paper-specific bounded-overrun proofs and current computational methods are in the article appendices; detailed memory and profile tables remain here.')
    p.write_text(text)
    p = R/'evidence.tex'
    p.write_text(p.read_text().replace(
        'The companion gives the measurements and definitions.',
        'The article appendices give the definitions; the companion supplies the detailed memory and profile tables.'))
    p = R/'RESPONSE_TO_REFEREES.md'
    p.write_text(p.read_text().replace(
        'For any fixed codebook, the companion proves the exact branch rule.',
        'For any fixed codebook, the article appendix proves the exact branch rule.'))
    record = json.loads((R/'PRESERVATION_MAP.json').read_text())
    record['current_main_inputs'] += modules
    record['current_companion_inputs'] = [p for p in record['current_companion_inputs'] if p not in modules]
    record['reader_allocation'] = 'New paper-specific bounded-overrun proofs and computational methods appear intact in main-article appendices; broader inherited theory remains in the companion. No content removed to balance reader lengths.'
    (R/'PRESERVATION_MAP.json').write_text(json.dumps(record, indent=2)+'\n')
    p = R/'PRESERVATION_MAP.md'
    p.write_text(p.read_text()+'\n## Current article appendices\n\nThe new bounded-overrun proofs and current computational methods appear intact in the main article appendices. They are not deleted or relegated to a missing supplement. The broader inherited theory remains in the electronic companion.\n')
    bibliography(record['current_main_inputs'], REL+'/generated/main_references.tex')
    bibliography(record['current_companion_inputs'], REL+'/generated/companion_references.tex')
    response_reader()


if __name__ == '__main__':
    apply()
