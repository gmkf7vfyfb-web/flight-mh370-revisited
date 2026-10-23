cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/tables
python - <<'EOF'
import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',40)
d=pd.read_csv('detectable.csv',dtype={'receiver':str})
k=d[d.key=='D0/p0.5']
print("D0'/p0.5 — median SNR and detectable fractions")
for eta in [2.1e-4,1e-3]:
    s=k[np.isclose(k.eta,eta)][['receiver','snr_q10','snr_q50','snr_q90','frac_matched_filter','frac_baseline','blocked_mass']].round(3)
    print('eta',eta); print(s.to_string(index=False))
print(k[np.isclose(k.eta,2.1e-4)&(k.receiver=='H01W')][['frac_matched_filter_kadri_noise','frac_baseline_kadri_noise']])
e=pd.read_csv('eta_50.csv',dtype={'receiver':str}); print(e[e.key=='D0/p0.5'].pivot(index='receiver',columns='threshold',values='eta_50').map(lambda v: f"{v:.2e}"))
b=pd.read_csv('best_receiver.csv'); print(b[b.p==0.5][['option','eta','snr_best_q50','frac_matched_filter','frac_baseline']+[c for c in b.columns if c.startswith('share_best')]].round(3).to_string(index=False))
c=pd.read_csv('coverage.csv'); print(c[['key','kish_ess_subsample','share_A1','share_A2','share_B','share_wings_level_by_assumption','lat_q99','share_lat_outside_grid','share_arc_abs_gt_60nm','E_q50_gj','tau90_q50_s','tau_clamped_share']].round(4).to_string(index=False))
EOF