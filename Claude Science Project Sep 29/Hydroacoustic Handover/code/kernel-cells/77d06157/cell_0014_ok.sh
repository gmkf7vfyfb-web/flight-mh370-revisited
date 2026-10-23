M="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"; head -5 "$M/composition_run_j/v2/coincidence_locus.csv"; wc -l "$M/composition_run_j/v2/coincidence_locus.csv"; cat "$M/composition_run_j/v2/coincidence_summary.json" | head -c 2500; echo; python - <<E
import pandas as pd
w=pd.read_csv('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/panels/panel_windows.csv')
for r,t in [('H08S','01:10:0'),('H08S','01:09:5'),('H01W','00:54:2'),('H01W','00:52:0'),('H01W','00:49:5'),('H01W','00:53:3'),('H01W','00:52:5')]:
  print(r,t); print(w[(w.receiver==r)&(w.time_utc.str.startswith(t))][['panel','window_start_utc','time_utc','detector','band_hz','p_A','p_B','label','kadri_label']].to_string())
print(w.groupby(['receiver','panel']).window_start_utc.agg(['min','max','count']))
E