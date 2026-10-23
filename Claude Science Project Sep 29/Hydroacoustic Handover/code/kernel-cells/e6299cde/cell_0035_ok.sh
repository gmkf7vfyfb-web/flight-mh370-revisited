cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python imos_search.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/imos 2>&1 | tail -8
cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/imos
python - <<'EOF'
import pandas as pd, json
W=pd.read_csv('imos_windows.csv'); C=pd.read_csv('imos_candidates.csv')
print(W.groupby(['receiver','detector']).size().unstack())
print(C.groupby(['receiver','label']).size().unstack(fill_value=0))
print(C[C.detector=='M1b'].head(12)[['receiver','time_utc','band_hz','statistic','p','label','in_window_sofar','kadri_label','eta_needed','tl_note']].to_string())
s=json.load(open('imos_summary.json')); print(s['coupling']); print({k:v for k,v in s.items() if k in ('3376','3250')})
EOF