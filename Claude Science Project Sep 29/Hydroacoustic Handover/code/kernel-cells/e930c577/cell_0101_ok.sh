cd leg; python - <<'E'
import pandas as pd, json
P=pd.read_json('out/conditional_on_h01w_level.json')
x=P[(P.station=='PerthCanyon_3376')&(P.anchor=='energy')]
print(x[['D','branch','subset','ess','eta_req_q','LR_amp_sd7.9','LR_amp_sd11.2']].to_string(index=False))
y=P[(P.station=='H08S')]; print(y[['D','branch','subset','anchor','H08S_shot_snr_q_sd7.9','LR_nondet_sd7.9','LR_nondet_sd11.2']].to_string(index=False))
t=json.load(open('out/timing_consistent_rows.json')); print(json.dumps({k:{kk:(vv if not isinstance(vv,list) else [round(z,3) if isinstance(z,float) else z for z in vv]) for kk,vv in v.items()} for k,v in t.items() if k.startswith('D2') or k.startswith('D5')}, indent=0)[:2500])
E