S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches; cd $S; python - <<'E'
import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_columns',40); pd.set_option('display.max_colwidth',40)
t=pd.read_csv('named/table1_verdicts.csv'); print(t.columns.tolist()); print(t[['event_id','time_utc','bearing_deg','note','arc_crossing_lat','arc_crossing_lon','line_to_arc_km','implied_impact_utc','implied_time_band_D0','bearing_verdict','panel_rows_within_10s','panel_min_p','panel_best']].to_string())
p=pd.read_csv('coincidence/pairs.csv'); print(len(p))
q=p[(p.rx_a=='H01W')&(p.rx_b=='H08S')]
print(q.family.value_counts())
for ta in ['00:52:0','00:54:2','00:54:3']:
  print(q[q.t_a.str.startswith(ta)][['family','t_a','det_a','p_a','lab_a','t_b','det_b','p_b','lab_b','lag_s','max_p','kadri_a']].sort_values('max_p').head(8).to_string())
c=pd.read_csv('panels/panel_candidates.csv'); print(c.columns.tolist()); print(c[['receiver','panel','time_utc','detector','band_hz','statistic','p','p_A','p_B','label','kadri_label','eta_needed']].to_string())
E