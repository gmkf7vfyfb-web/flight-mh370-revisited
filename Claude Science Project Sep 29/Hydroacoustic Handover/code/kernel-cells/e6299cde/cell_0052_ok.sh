cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches
python -c "
import pandas as pd; W=pd.read_csv('imos/imos_windows.csv')
for lg in (3315,3376,3274): r=W[W.receiver==lg].sort_values('p').iloc[0]; print(lg, r.time_utc, r.detector, r.band_hz, round(r.p,3), r.in_window_sofar, r.eta_needed)"