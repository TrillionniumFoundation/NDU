"""Final proof precision; numerical experiments and their source stay unchanged."""
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'sections/complete_dual.tex';s=p.read_text()
old='Its generalized Hessians have the form $M_I D_I^{-1}M_I^\\top+P$, where $I$ indexes unclipped coordinates and $P$ is the identity on resource prices and zero on the other prices. Their norm is at most $L_Q$; integration along line segments gives global Lipschitz continuity.'
new='Away from clipping breakpoints its Hessian is $M_I D_I^{-1}M_I^\\top+P$, where $I$ indexes unclipped coordinates and $P$ is the identity on resource prices and zero elsewhere. At breakpoints the generalized Hessians lie in the convex hull of such limiting matrices. All have norm at most $L_Q$; integration along line segments gives global Lipschitz continuity.'
assert old in s or new in s
p.write_text(s.replace(old,new))
p=R/'complete_dual_checks.py';s=p.read_text()
old='tb=t.copy();tb[1]=clip(tb[1],-newlam,newlam);bn=[newb1,b[1]]'
new='tb=t.copy();tb[1]=clip(tb[1],-newlam,newlam);bn=[newb1,b[1]+newb1-b1]  # reward shift follows U.T*h'
assert old in s or new in s
p.write_text(s.replace(old,new))
print('Clarke-Hessian convex hull and exact resource-coordinate transport made explicit.')
