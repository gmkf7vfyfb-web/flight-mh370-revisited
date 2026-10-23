cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal
python - <<'EOF'
import numpy as np, json
j=json.load(open('template_build.json')); print(json.dumps(j)[:1200])
z=np.load('templates_raw.npz'); print('fs',z['fs'],'T',z['T'], 'ranges', z['ranges_km'][:5], z['ranges_km'][-3:])
h=z['h_2200.0']; print(h.shape, np.abs(h).max(), np.argmax(np.abs(h))/float(z['fs']))
import os; print(os.listdir('templates')[:10])
EOF
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels; tail -n 2 $OUT/logs/noise.log; python -c "
import pandas as pd; d=pd.read_csv('$OUT/noise/imos_thirdoctave_percentiles.csv'); print(d[d.band=='5-40'][['logger','set','n_files','n_1s','p10','p50','p90']].to_string())"
tail -n 3 $OUT/logs/levels.log