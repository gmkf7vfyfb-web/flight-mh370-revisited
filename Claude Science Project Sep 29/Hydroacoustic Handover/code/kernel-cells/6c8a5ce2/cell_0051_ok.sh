cd .tmp/standin; python - <<'EOF'
import pandas as pd, numpy as np, json
g=pd.read_csv("q1/af447_q1_grid.csv")
pk=pd.read_csv("../hy/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/calibration_events/kadri_peaks.csv").set_index("panel")
pe=0.914; n99=float(pk.loc["AF447 H10S","noise_p99"])
for conv,h in g.groupby("convention"):
    pp=pe/10**(h.delta_ratio_mean_db/20)
    need=20*np.log10(2*n99/pp)
    print(conv, "pred peak at F-35A coupling Pa: median %.3f range %.3f-%.3f"%(pp.median(),pp.min(),pp.max()), "| dB above F-35A coupling for SNR 2: median %.1f range %.1f-%.1f"%(need.median(),need.min(),need.max()))
    for z,hh in h.groupby("src_depth_m"):
        print("  z",z,"G_F/G_e dB median %.1f"%(10*np.log10(0.5*(hh.G_F_H11N+hh.G_F_H11S)/hh.G_event)).median(), "tau of max delta", hh.loc[hh.delta_ratio_mean_db.idxmax(),"tau_s"].round(3), "min", hh.loc[hh.delta_ratio_mean_db.idxmin(),"tau_s"].round(3))
print("noise p99", n99)
EOF