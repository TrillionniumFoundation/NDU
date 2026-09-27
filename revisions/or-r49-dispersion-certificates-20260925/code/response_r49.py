"""Typeset the complete response without requiring pandoc or a network."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
def esc(s):
    return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in s)
def inline(s):
    # Preserve readable monospace without creating unbreakable catalog paths.
    out='';parts=re.split(r'(`[^`]*`|\*\*[^*]*\*\*)',s)
    for p in parts:
        if p.startswith('`'):out+=r'\nolinkurl{'+p[1:-1]+'}'
        elif p.startswith('**'):out+=r'\textbf{'+esc(p[2:-2])+'}'
        else:out+=esc(p)
    return out
text=R.joinpath('RESPONSE_TO_REFEREES.md').read_text().replace('−','-')
tex=r'''\documentclass[11pt,letterpaper]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}\usepackage{newtxtext}\usepackage{setspace}
\usepackage{xurl}\usepackage[hidelinks]{hyperref}
\onehalfspacing\setlength{\emergencystretch}{3em}
\begin{document}
'''
for line in text.splitlines():
    if line.startswith('# '):tex+=r'\begin{center}\Large\bfseries '+inline(line[2:])+r'\end{center}'+'\n'
    elif line.startswith('## '):tex+=r'\section*{'+inline(line[3:])+'}\n'
    else:tex+=inline(line.strip())+'\n\n'
tex+=r'\end{document}'+'\n'
# Insert discretionary path breaks for this long metadata filename.
tex=tex.replace(esc('operation_research_referee_report_r45_independent_harsh_2026-09-25.md'),r'\nolinkurl{operation_research_referee_report_r45_independent_harsh_2026-09-25.md}')
R.joinpath('RESPONSE_TO_REFEREES.tex').write_text(tex)
