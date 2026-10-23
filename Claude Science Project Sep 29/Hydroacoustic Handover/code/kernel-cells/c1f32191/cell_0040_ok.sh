cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF' 2>&1 | grep -v Warn
import numpy as np, sys; sys.path.insert(0,'.'); sys.path.insert(0,'..'); import prereg as R, run_j_windows as W
for s,k in [("run-j-waypoints",1),("run-j-free",1),("run-j-descent-climb",1)]:
    sd=R.RUN_J/s/f"seed-{k}"; g,meta,n=W.load_seed(sd); z=np.load(sd/"tau90_v1.npz")
    E=z["energy_transferred_j"].astype(float); KE=0.5*g("mass_kg")*(g("velocity_east_mps")**2+g("velocity_north_mps")**2+g("velocity_up_mps")**2)
    r=E/KE; print(s, "ratio E_sidecar/KE quantiles", np.round(np.nanquantile(r,[0,.001,.5,.999,1]),4), "max|rel diff|", float(np.nanmax(np.abs(r-1))), "nan E", int(np.isnan(E).sum()))
EOF