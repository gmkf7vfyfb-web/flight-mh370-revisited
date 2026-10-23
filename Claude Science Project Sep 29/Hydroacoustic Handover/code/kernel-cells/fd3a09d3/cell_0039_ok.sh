cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
head -3 results-data/imos1d/noise_bands.csv; python -c "
import pandas as pd, json; d=pd.read_csv('results-data/imos1d/noise_bands.csv'); print(d.columns.tolist()); print(d.head(8).to_string())
s=json.load(open('results-data/imos1d/noise_summary.json')); print(str(s)[:800])
p=pd.read_csv('results-data/blackman_noise/blackman_noise_panels.csv'); print(p.columns.tolist()); print(p.head(5).to_string())
import numpy as np; z=np.load('results-data/blackman_noise/blackman_noise_curves.npz'); print({k:z[k].shape for k in z.files})
print(json.load(open('results-data/blackman_noise/blackman_noise_summary.json')).keys())
"
sed -n 28,70p prepare/imos_stageB_map.py