cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
grep -n "^BANDS\|^SRC\|^def eta_cal_lookup\|^def receiver_depth\|TRIAD\|^ETA" f35a_eta_calibration.py | head
grep -n "T_eff\|t_eff\|teff" exploratory/pleiades_test/lhyd.py | head -5
grep -n "BN_OFF\|TRIAD_GAIN\|3376" per_impact_lnl.py | head -5
python - <<'EOF'
import numpy as np
EX='/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/'
for st in ['run-j-waypoints','run-j-free']:
    z=np.load(EX+st+'/seed-1/tau90_v1.npz'); E=z['energy_transferred_j'].astype(float); t=z['tau90_s'].astype(float)
    ok=np.isfinite(E)&np.isfinite(t)
    print(st, 'E q05/50/95 GJ', np.quantile(E[ok],[0.05,0.5,0.95])/1e9, 'tau q', np.quantile(t[ok],[0.05,0.5,0.95]), 'nan', (~ok).mean(), str(z['note'])[:200])
EOF