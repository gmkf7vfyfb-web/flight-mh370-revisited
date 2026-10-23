cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
python - <<'EOF'
s=open('charts.py').read()
s=s.replace('"Candidate rows at every receiver, at about the rate chance predicts on other days; none is a detection"','"Candidate rows at every receiver, at one third to 1.5 times the rate chance gives on other days; none is a detection"')
s=s.replace('The counts of dots match what chance gives on other days; no dot is a detection.','The counts of dots are within a factor of about 1.5 of what chance gives on other days (fewer at Perth Canyon and Cape Leeuwin, more at Scott Reef and Portland); no dot is a detection.')
open('charts.py','w').write(s)
EOF
python charts.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches "$PWD/../../../../../../../repo/Claude Science Project Sep 29/results" 2>&1 | tail -1
cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches
python - <<'EOF'
import pandas as pd
pd.set_option('display.width',250)
T=pd.read_csv('named/table1_verdicts.csv'); print(T[['time_utc','bearing_deg','in_H01W_99pct_D0','in_H01W_99pct_D3','implied_impact_utc','implied_time_band_D0','implied_time_band_D4','log10_BF_demonstrated_t3_3p3','log10_BF_claimed_gauss_0p4','bearing_verdict','panel_best']].to_string(index=False))
A=pd.read_csv('named/royer_arrivals.csv'); print(A.to_string(index=False))
P=pd.read_csv('coincidence/pairs.csv'); p=P[(P.rx_a=='H01W')&(P.rx_b=='H08S')&(P.family=='primary_M1b')]; print(p[['t_a','p_a','t_b','p_b','lag_s','max_p','kadri_a']].to_string(index=False))
EOF
du -sh /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches; df -k /System/Volumes/Data | tail -1