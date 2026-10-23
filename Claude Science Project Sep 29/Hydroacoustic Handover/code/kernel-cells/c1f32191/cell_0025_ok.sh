cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF' 2>&1 | grep -v Warn
import numpy as np, sys; sys.path.insert(0,'..'); import prereg as R, run_j_windows as W
sd=R.RUN_J/"run-j-waypoints"/"seed-1"; g,meta,n=W.load_seed(sd); idx=np.arange(0,n,n//2000)[:2000]
for k in ["unix_s","latitude_deg","longitude_deg","latent:impact_energy_transferred_j","mass_kg","velocity_up_mps","weight","family4_code"]:
    v=g(k)[idx]; print(k, np.isfinite(v).mean(), np.nanquantile(v,[.05,.5,.95]) if np.isfinite(v).any() else None)
z=np.load(sd/"tau90_v1.npz"); print(z.files, {k: (z[k].shape, np.isfinite(z[k]).mean() if z[k].dtype.kind=='f' else z[k]) for k in z.files})
EOF