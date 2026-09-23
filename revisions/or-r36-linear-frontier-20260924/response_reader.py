"""Generate the response TeX from its authoritative Markdown text."""
from pathlib import Path
import re
R=Path(__file__).resolve().parent

def escape(s):
    for a,b in [('–','--'),('—','---'),('≤',r'$\leq$'),('²',r'$^2$'),('³',r'$^3$')]:s=s.replace(a,b)
    # Protect the three generated mathematical tokens before escaping prose.
    tokens={r'$\leq$':'ZZMATHLEZZ',r'$^2$':'ZZMATHTWOZZ',r'$^3$':'ZZMATHTHREEZZ'}
    for a,b in tokens.items():s=s.replace(a,b)
    s=''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in s)
    for a,b in tokens.items():s=s.replace(b,a)
    return s

def inline(s):
    # Long paths and hashes use xurl's line breaking, not a nonbreakable typewriter box.
    parts=re.split(r'(`[^`]+`|\*\*[^*]+\*\*)',s)
    out=[]
    for p in parts:
        if p.startswith('`'):out.append(r'\nolinkurl{'+p[1:-1]+'}')
        elif p.startswith('**'):out.append(r'\textbf{'+escape(p[2:-2])+'}')
        else:out.append(escape(p))
    return ''.join(out)

header=r'''\documentclass[11pt,letterpaper]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{newtxtext,newtxmath,setspace,xurl}
\usepackage[hidelinks]{hyperref}
\onehalfspacing\setlength{\emergencystretch}{3em}
\begin{document}
'''
body=[]
for paragraph in (R/'RESPONSE_TO_REFEREES.md').read_text().split('\n\n'):
    if paragraph.startswith('# '):body.append(r'\begin{center}\Large\bfseries '+inline(paragraph[2:])+r'\end{center}')
    elif paragraph.startswith('## '):body.append(r'\section*{'+inline(paragraph[3:])+'}')
    else:body.append(inline(paragraph.replace('  \n', '\n')).replace('\n',r'\par '+'\n')+'\n')
(R/'RESPONSE_TO_REFEREES.tex').write_text(header+'\n\n'.join(body)+r'\end{document}'+'\n')
