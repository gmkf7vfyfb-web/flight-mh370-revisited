cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
python - <<'EOF'
s=open('charts.py').read()
s=s.replace('''    ax.text(x1 - 60, -0.55, "rows per receiver: upper = matched filter, middle = energy ratio, lower = band energy", fontsize=6, color="0.3", va="bottom", ha="right")\n''','')
s=s.replace('''"The counts of dots match what chance gives on other days; no dot is a detection.",''','''"Within each receiver's row the upper dots are the matched filter, the middle the energy ratio, the lower the band energy. The counts of dots match what chance gives on other days; no dot is a detection.",''')
open('charts.py','w').write(s)
EOF
python charts.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches "$PWD/../../../../../../../repo/Claude Science Project Sep 29/results" 2>&1 | tail -1
cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches
python - <<'EOF'
import pandas as pd, numpy as np, json
pd.set_option('display.width',250)
W=pd.concat([pd.read_csv('imos/imos_windows.csv'),pd.read_csv('panels/panel_windows.csv')],ignore_index=True); W['receiver']=W.receiver.astype(str)
rows=[]
for rx,g in W.groupby('receiver', sort=False):
    n=len(g); rows.append(dict(receiver=rx,n_windows=n,screen=int((g.p<0.3).sum()),exp_screen=round(0.3*n,1),mark=int((g.p<0.1).sum()),exp_mark=round(0.1*n,1),report=int((g.p<0.05).sum()),exp_report=round(0.05*n,2)))
A=pd.DataFrame(rows); print(A.to_string(index=False)); A.to_csv('counts_vs_chance_by_receiver.csv',index=False)
rows=[]
for (rx,det),g in W.groupby(['receiver','detector'], sort=False):
    n=len(g); rows.append(dict(receiver=rx,detector=det,n_windows=n,screen=int((g.p<0.3).sum()),exp_screen=round(0.3*n,1),mark=int((g.p<0.1).sum()),exp_mark=round(0.1*n,1),report=int((g.p<0.05).sum()),exp_report=round(0.05*n,2)))
B=pd.DataFrame(rows); print(B.to_string(index=False)); B.to_csv('counts_vs_chance_by_detector.csv',index=False)
# M1b rows only, all receivers
M=W[W.detector.isin(['M1b','M1b_res'])&(W.p<0.3)].sort_values('p')
print(M[['receiver','time_utc','detector','statistic','p','label','in_window_sofar','kadri_label','eta_needed','tl_note']].head(25).to_string(index=False))
# H08S residual rows
print(W[(W.receiver=='H08S')&W.detector.isin(['M1b_res','Z_res'])].sort_values('p').head(6)[['time_utc','detector','statistic','p','p_B','label']].to_string(index=False))
# H01W rows all
print(W[(W.receiver=='H01W')&(W.p<0.3)][['time_utc','detector','band_hz','statistic','p','p_A','p_B','label','kadri_label','eta_needed']].to_string(index=False))
C=pd.read_csv('coincidence/coincidence_summary.csv'); print(C[C.family=='primary_M1b'][['rx_a','rx_b','n_pairs_obs','expected_by_chance','p_perm','strongest_pair_max_p']].to_string(index=False))
EOF