#!/usr/bin/env python3
"""Post-deployment face diagnostics. Never changes the frozen pipelines."""
from experiment import *
model,tr,cells,order,nearest,pick,cert=load();records=[]
for row in readzip(HERE/'results/matched_records.json.gz')['records']:
    th=np.array(row['theta']);ref=row['reference'];truth=np.array(list(map(float,map(F,ref['flows']))))
    for name,j in [('neural',int(order(th)[0])),('nearest',nearest(th))]:
        u,mu,s=eval_cell(cells[j],th);audit=tr.audit(th,u,mu,s)
        assert F(ref['gain_fraction'])-F(audit['gain_fraction'])<=F(audit['bound_fraction'])
        records.append({'sample':row['sample'],'method':name,'proposed_cell':j,'membership':contains(cells[j],th),
            'predicted_active':np.where(abs(tr.h-tr.L@u)<1e-6)[0].tolist(),'reference_active':np.where(abs(tr.h-tr.L@truth)<1e-6)[0].tolist(),
            'predicted_switch_signs':np.sign(np.round(tr.K@u,6)).astype(int).tolist(),
            'reference_switch_signs':np.sign(np.round(tr.K@truth,6)).astype(int).tolist(),
            'audit':audit,'reference_gain_fraction':ref['gain_fraction']})
compress(HERE/'results/face_diagnostics.json.gz',{'records':records,'mask_tolerance':1e-6,'diagnostics_not_used_in_timed_deployment':True})
print('raw-face diagnostics',len(records))
