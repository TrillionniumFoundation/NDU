#!/usr/bin/env python3
"""Publish ordinary complete TeX, preserving the text of every imported component.
Only input expansion and float delimiter line breaks are typesetting changes.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2];R=Path(__file__).resolve().parent
pat=re.compile(r'\\input\{([^}]+)\}')
def expand(s,stack=()):
    def sub(m):
        p=ROOT/m.group(1)
        if not p.suffix:p=p.with_suffix('.tex')
        if str(p) in stack:raise ValueError('cyclic TeX input')
        text=expand(p.read_text(),stack+(str(p),))
        return '\n% BEGIN preserved/input source: '+m.group(1)+'\n'+text+'\n% END input source: '+m.group(1)+'\n'
    return pat.sub(sub,s)
for source,target in [('main_draft.tex','main.tex'),('ec_draft.tex','electronic_companion.tex')]:
    s=expand((R/source).read_text())
    # endfloat scans literal float terminators at line boundaries.
    s=re.sub(r'\s*\\end\{table\}\s*',lambda m:'\n\\end{table}\n',s)
    s=re.sub(r'\s*\\end\{figure\}\s*',lambda m:'\n\\end{figure}\n',s)
    (ROOT/target).write_text(s)
