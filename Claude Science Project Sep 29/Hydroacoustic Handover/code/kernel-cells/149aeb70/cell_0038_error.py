import numpy as np
S = np.load("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i/run-i-subsample.npz", allow_pickle=True)
cols = list(S["columns"]); ci = {c:i for i,c in enumerate(cols)}
names = [k for k in S.files if k not in ("columns","strata")]
print(len(cols), names)
b = S["baseline"]
print("shape", b.shape)
for c in ["t_impact_s","latitude_deg","longitude_deg","velocity_up_mps","flight_path_angle_deg",
          "latent:state_m0019b_vertical_speed_fpm","latent:state_m0019b_altitude_ft","tau90_s","peak_rate_w","energy_transferred_j","l_eff_m","decel_g"]:
    v = b[:,ci[c]]; v=v[np.isfinite(v)]
    print(f"{c:42s} n={v.size:6d} p5={np.percentile(v,5):12.4g} med={np.median(v):12.4g} p95={np.percentile(v,95):12.4g}")
