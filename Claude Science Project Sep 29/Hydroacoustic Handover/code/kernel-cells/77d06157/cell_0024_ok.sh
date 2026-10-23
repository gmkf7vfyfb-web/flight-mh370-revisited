python - <<'E'
import numpy as np, json
z=np.load('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/panels/panel_series.npz',allow_pickle=True)
for k in z.files: print(k, z[k].shape, z[k].dtype)
print(json.dumps(json.load(open('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/panels/panel_summary.json')))[:1500])
E
cat /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/named/poster_boxes.csv | cut -d, -f1-3,9-14