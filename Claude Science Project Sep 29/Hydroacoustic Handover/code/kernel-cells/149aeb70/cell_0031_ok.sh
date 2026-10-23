cat > /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i/subsample.py <<'EOF'
import numpy as np, json, glob, os
R = "/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i"
cols = json.load(open(f"{R}/next-i-free/seed-1/run.json"))["impact_columns"]
ix = {c: i for i, c in enumerate(cols)}
OPTS = [c for c in cols if c.startswith("loglik:")]
KEEP = ["weight","t_impact_s","latitude_deg","longitude_deg","velocity_east_mps","velocity_north_mps",
        "velocity_up_mps","flight_path_angle_deg","mass_kg","t_onset_s","t_realised_flameout_s",
        "latent:state_m0019a_vertical_speed_fpm","latent:state_m0019b_vertical_speed_fpm",
        "latent:state_m0019b_altitude_ft","latent:max_descent_rate_fpm","latent:time_descending_s",
        "latent:impact_heading_deg","latent:impact_bank_deg","family_code","onset_code","control_code"]
SIDE = ["tau90_s","peak_rate_w","energy_transferred_j","decel_g","l_eff_m","w_steep","t05_s","t95_s"]
K = 20000
rng = np.random.default_rng(7)
names = ["baseline"] + [o.replace("loglik:", "") for o in OPTS]
best = {n: {"key": np.full(K, -np.inf), "rows": np.zeros((K, len(KEEP)+len(SIDE)+1), np.float64)} for n in names}
strata = sorted(os.path.basename(p) for p in glob.glob(f"{R}/next-i-*"))
for s_i, s in enumerate(strata):
    for sd in sorted(glob.glob(f"{R}/{s}/seed-*/impacts32.npy")):
        a = np.load(sd, mmap_mode="r"); n = a.shape[0]
        z = np.load(sd.replace("impacts32.npy", "tau90_v1.npz"))
        for i in range(0, n, 400_000):
            b = np.asarray(a[i:i+400_000]); m = b.shape[0]
            feat = np.column_stack([b[:, ix[c]].astype(np.float64) for c in KEEP]
                                   + [z[k][i:i+m].astype(np.float64) for k in SIDE]
                                   + [np.full(m, s_i, np.float64)])
            w0 = b[:, ix["weight"]].astype(np.float64)
            u = rng.random(m)
            for nm in names:
                if nm == "baseline":
                    w = w0
                else:
                    lw = b[:, ix["loglik:" + nm]].astype(np.float64)
                    w = w0 * np.exp(np.where(np.isfinite(lw), lw, -np.inf))
                key = np.where(w > 0, np.log(u) / np.maximum(w, 1e-300), -np.inf)
                st = best[nm]
                cat_k = np.concatenate([st["key"], key])
                cat_r = np.concatenate([st["rows"], feat])
                top = np.argpartition(cat_k, -K)[-K:]
                st["key"] = cat_k[top]; st["rows"] = cat_r[top]
    print("done", s, flush=True)
np.savez_compressed(f"{R}/run-i-subsample.npz",
                    columns=np.array(KEEP + SIDE + ["stratum"]),
                    strata=np.array(strata),
                    **{nm: best[nm]["rows"] for nm in names})
print("saved", {nm: best[nm]["rows"].shape for nm in names[:2]})
EOF
cd /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i && nohup python3 subsample.py > subsample.log 2>&1 &
echo launched