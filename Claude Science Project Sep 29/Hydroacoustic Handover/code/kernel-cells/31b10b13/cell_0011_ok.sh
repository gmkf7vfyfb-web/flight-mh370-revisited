cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches
python - <<'EOF'
import pandas as pd
ic=pd.read_csv('imos/imos_candidates.csv',dtype={'receiver':str}); pc=pd.read_csv('panels/panel_candidates.csv')
print(ic.groupby(['receiver','detector']).size().to_string())
print(pc.groupby(['receiver','panel','detector']).size().to_string())
print(ic.band_hz.unique(), pc.band_hz.unique(), ic.label.unique())
pr=pd.read_csv('coincidence/pairs.csv',dtype={'rx_a':str,'rx_b':str}); print(pr.groupby(['rx_a','rx_b','family']).size().to_string())
k=['rx_a','t_a','det_a','band_a','rx_b','t_b','det_b','band_b']; print(len(pr), len(pr.drop_duplicates(k)))
t=pd.read_csv('named/table1_verdicts.csv'); print(t[['event_id','time_utc','bearing_deg','note','bearing_verdict','implied_impact_utc']].to_string())
print(pc[pc.receiver=='H01W'][['time_utc','detector','band_hz','p','p_B','label','kadri_label','eta_needed']].to_string())
EOF