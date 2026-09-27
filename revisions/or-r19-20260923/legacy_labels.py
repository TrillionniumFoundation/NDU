#!/usr/bin/env python3
"""Keep links to displaced material directed at immutable predecessor PDFs."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2];R=Path(__file__).resolve().parent
seenfiles=set();labels=set()
def visit(p):
    p=p.resolve()
    if p in seenfiles:return
    seenfiles.add(p);s=p.read_text()
    labels.update(re.findall(r'\\label\{([^}]+)\}',s))
    for x in re.findall(r'\\input\{([^}]+)\}',s):
        f=ROOT/x
        if not f.suffix:f=f.with_suffix('.tex')
        if not f.exists():raise FileNotFoundError(f)
        visit(f)
for name in ['main.tex','electronic_companion.tex']:visit(ROOT/name)
for kind,target in [('main','legacy-main-labels.aux'),('ec','legacy-ec-labels.aux'),('history','history-labels.aux')]:
    src=R/'predecessor'/('original-'+kind+'-labels.aux');out=[]
    for line in src.read_text().splitlines():
        m=re.match(r'\\newlabel\{([^}]+)\}',line)
        if m and m.group(1) not in labels:out.append(line);labels.add(m.group(1))
    (ROOT/target).write_text('\n'.join(out)+'\n')
