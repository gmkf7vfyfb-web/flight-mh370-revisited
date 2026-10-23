cd leg; python - <<'E'
import json, pandas as pd, sys
sys.path.insert(0,'.'); from geometry_windows import ST, dist, T_RX
P=pd.read_json('out/conditional_on_h01w_level.json')
x=P[(P.D=='D2')&(P.subset=='strip')]
for _,r in x.iterrows(): print(r.branch, r.anchor, r.station, [round(v,2) for v in r.cond_ppk_pa_q], [round(v,1) for v in r.cond_snr_db_q], [f"{v:.3g}" for v in r.eta_req_q])
rc=json.load(open('out/royer_recombination.json'))
for k,v in rc['inversions'].items():
    p=(v['best_lat'],v['best_lon']); t0=v['origin_utc']; s=lambda x: sum(float(a)*m for a,m in zip(x.split(':'),(3600,60,1)))
    for stn in ['PerthCanyon_3376','H08S','OHAS_SWAMS3','OHAS_NCRO','OHAS_WKER']:
        t=s(t0)+dist(p,ST[stn][:2])/1.48; print(k[:3], stn, f"{int(t//3600):02d}:{int(t%3600//60):02d}:{t%60:04.1f}")
E