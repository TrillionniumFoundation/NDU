"""Place the proof table after references and embed the trajectory by its discussion."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'generated/ec_tables.tex').read_text();i=s.index(r'\begin{figure}')
(R/'generated/proof_table56.tex').write_text(s[:i])
(R/'generated/trajectory56.tex').write_text(s[i:].replace(r'\begin{figure}[p]',r'\begin{figure}[htbp]').replace(r'\end{figure}\clearpage',r'\end{figure}'))
