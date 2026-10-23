cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
python - <<'EOF'
import numpy as np
z=np.load('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz')
tech=z['technique']; sel=tech>=1
E=z['latent:impact_energy_transferred_j'].astype(np.float32)
w_all=np.exp(z['lnw:comb/D0'].astype(np.float64)); print('nan lnw', np.isnan(z['lnw:comb/D0']).sum(), 'inf w', np.isinf(w_all).sum())
w_all[~np.isfinite(w_all)]=0
w=np.where(sel & np.isfinite(E), w_all, 0.0); print(np.isnan(w).sum(), w.sum(), np.isnan(E).sum(), (E<=0).sum())
print(np.isnan(z['latitude_deg']).sum(), np.isnan(z['t_impact_s']).sum())
EOF