cd leg/out; python - <<'E'
import json, pandas as pd
m=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/table-0019-mixture.json'))['cells']
print({d: (round(m[f'{d} total q=0.333 (C2 silent)']['ln_Z'],6)) for d in ['D0','D1','D2','D3','D4','D5']})
L=pd.read_json('levels.json'); pd.set_option('display.width',250)
f=lambda v:'/'.join(f"{x:.1f}" for x in v)
L['snr']=L.snr_db_q.map(f); L['ppk']=L.ppk_pa_q.map(lambda v:'/'.join(f"{x:.3g}" for x in v))
for sub in ['strip','T','C']:
    print('==',sub); x=L[(L.D=='D2')&(L.subset==sub)]; print(x[['station','eta','ess','n_rows','range_km_q50','snr','ppk','pd05_mean','share_pd05_ge_0p5']].to_string(index=False,float_format=lambda v:f"{v:.3g}"))
h=L[(L.station=='H08S')&(L.D=='D2')][['subset','eta','snr_shot_q','pd_shot_mean']]; print(h.to_string())
print(L[(L.D=='D5')&(L.subset=='strip')&(L.station.isin(['H01W','PerthCanyon_3376','H08S','OHAS_SSEIR']))][['station','eta','ess','snr','pd05_mean']].to_string(index=False))
q=json.load(open('q4_h01w_level.json'))
for k,v in q.items(): print(k, [f"{x:.3g}" for x in v['ppk_eta_f35_q']], [f"{x:.3g}" for x in v['eta_required_q']], [f"{x:.3g}" for x in v['eta_required_q_tl_minus2sd']], round(v['share_eta_req_le_0p1'],3), round(v['share_eta_req_le_f35'],4), v['prior_predictive_P_ppk_ge_obs'])
E