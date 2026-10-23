X=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a; python - <<E
import json,pandas as pd
s=json.load(open("$X/step5/step5_summary.json"))
for st,v in s['triads'].items(): print(st, v['profile'], v['observed'], v['n_bad']); print(' tau5',{k:round(x,2) for k,x in v['model_at_tau5'].items()}); print(' fb',{k:round(x,2) for k,x in v['model_at_fallback'].items()}); print(' tmin',{k:round(x,2) for k,x in v['model_at_tau_min'].items()})
T=pd.read_csv("$X/step5/step5_tau_scan.csv"); print(T[T.tau_s.isin(T.tau_s.unique()[::3])].round(2).to_string())
E