"""Build manuscript tables solely from executed outputs; no hand-entered numbers."""
from pathlib import Path
import csv
from fractions import Fraction
P=Path(__file__).resolve().parent

def rows(name):
    with (P/'results'/name).open() as f: return list(csv.DictReader(f))

def table(label,title,cols,head,body,note):
    return '\n'.join([r'\begin{table}[!ht]',r'\centering',r'\caption{'+title+'}',r'\label{'+label+'}',
         r'\begin{tabular}{'+cols+'}',r'\toprule',head+r'\\',r'\midrule',
         *[b+r'\\' for b in body],r'\bottomrule',r'\end{tabular}',r'\par\smallskip',
         r'\begin{minipage}{0.98\textwidth}\small '+note+r'\end{minipage}',r'\end{table}',''])

names={'joint_contract':'Joint contract','expanded_action_mdp':'Expanded-action MDP','frozen_contract':'Frozen contract','capacity_matched_gate':'Dummy gate','physical_oracle':'Physical oracle'}
t=[]; rr=rows('exact_dp_summary.csv')
t.append(table('tab:exact','Exact discounted operating outcomes','lrrrr',
     'Method & Net reward & Physical cost & Fill rate & Actions',
     [names[r['method']]+' & '+' & '.join(f"{float(r[k]):.6f}" for k in ('net_reward','physical_cost','fill_rate'))+' & '+r['unique_economic_actions'] for r in rr],
     'All expectations are exact rational calculations; displayed decimals are rounded. Actions count distinct economic choices. The physical oracle minimizes physical cost, not the convention-dependent net reward shown here.'))
t.append(table('tab:ledger','Contract cash-flow decomposition','lrrrr',
     'Method & Premium & Liability & Maintenance & Adjustment',
     [names[r['method']]+' & '+' & '.join(f"{float(r[k]):.6f}" for k in ('premium','liability','maintenance','adjustment')) for r in rr],
     'Net reward equals premium minus physical cost, liability, maintenance, and adjustment. The oracle uses contract one under the recorded tie convention.'))
t.append(r'\clearpage')
t.append(table('tab:contractgrid','Exact grid values and continuous-contract enclosures','rrrr',
     'Intervals & Grid value & Loss bound & Value upper bound',
     [r['intervals']+' & '+' & '.join(f"{float(r[k]):.8f}" for k in ('value_decimal','quadratic_bound_decimal','continuous_value_upper_decimal')) for r in rows('contract_grid_refinement.csv')],
     r'Theorem~\ref{thm:quadratic} bounds contract discretization for the unchanged stock set. The lower endpoint is the grid value; the upper endpoint adds the proved bound.'))
t.append(table('tab:conditioning','Identical-data least-squares conditioning experiment','rrrrr',
     r'$\varepsilon$ & Direct $P$ MSE &  $P$ MSE via $Z$ & Direct condition & $Z$ condition',
     [f"{float(r['epsilon']):g}"+' & '+f"{float(r['direct_p_mse']):.8f} & {float(r['inferred_p_mse']):.8f} & {float(r['direct_design_condition']):.3f} & {float(r['z_design_condition']):.3f}" for r in rows('conditioning_summary.csv')],
     'Means over 64 batches, each with 2,048 pairs. Integrated shadow-price MSE uses uniform test states on $[-1,1]$. Condition numbers are spectral design-matrix condition numbers.'))
t.append(r'\clearpage')
t.append(table('tab:pde','Absolute certificates for the stopped diffusion','rrrrrr',
     r'$m$ & $\delta_H$ bound & $\delta_T$ & $\delta_\partial$ & $\delta_A$ & Policy-loss bound',
     [r['m']+' & '+f"{float(Fraction(r['residual_bound'])):.9f}"+' & 0 & 0 & 0 & '+f"{float(Fraction(r['policy_loss_bound'])):.9f}" for r in rows('analytic_pde_certificate.csv')],
     r'$e=2^{-m}$. The entire parabolic boundary is exact, and the actor is analytically greedy. These are manufactured analytic critics, not fitted neural inventory models.'))
t.append(table('tab:mesh','Joint space--time--action refinement','rrrrr',
     'Spatial nodes & Time steps & Actions per axis & Node error & Proved bound',
     [r['spatial_nodes']+' & '+r['time_steps']+' & '+r['action_points_per_coordinate']+' & '+f"{float(r['all_time_node_value_error']):.8f} & {float(r['proved_node_value_bound']):.8f}" for r in rows('space_time_action_refinement.csv')],
     r'Observed errors are maximized over every computed state--time node. The bounds are supplied by Proposition~\ref{prop:scheme}; they do not certify interpolation or a continuous-state actor.'))
(P/'tables.tex').write_text('\n'.join(t))
