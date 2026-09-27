from pathlib import Path
import subprocess,os
root=Path(__file__).resolve().parent;out=root/'.build/r60';out.mkdir(parents=True,exist_ok=True)
for cycle in range(4):
    for name in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
        subprocess.run(['pdflatex','-halt-on-error','-interaction=nonstopmode','-output-directory='+str(out),name+'.tex'],cwd=root,check=True)
print('Rebuilt PDFs are in .build/r60; recorded PDFs remain unchanged.')
