cd .tmp/standin; P="$(cd ..; pwd)/hy/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; cat > q1_af447.py <<'EOF'
"""Stand-in: Q1 arithmetic for AF447 -> H10S exactly as written in calibration_events.py (prereg 23add102, amendment 1(i)
primary same-figure ratio; secondary eta_cal comparison). The module file has the formula but no implementation of the
inversion; this file implements only the pre-registered formula. Usage: python q1_af447.py <module_dir> <event_tl.csv> <out_dir>"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
M = Path(sys.argv[1]); sys.path.insert(0, str(M / "prepare"))
import calibration_events as CE  # noqa: E402
F, B = CE.F, CE.B
out = Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
tl = pd.read_csv(sys.argv[2]); tl = tl[tl.path == "af447-H10S"]
ftl = pd.read_csv(M / "results-data/f35a_cal/f35a_tl.csv")
pk = pd.read_csv(M / "results-data/calibration_events/kadri_peaks.csv").set_index("panel")
cal = pd.read_csv(M / "results-data/f35a_cal/eta_cal.csv")
TAUS, ZS, R, E_F = F.TAUS, [2.0, 10.0, 30.0], 3.013, CE.E_F35
_, _, (Et, _), (Ev, _) = CE.EVENTS["AF447"]
p_e = float(pk.loc["AF447 H10S", "peak_Pa"]); pF = {"H11N": float(pk.loc["F-35A H11N", "peak_Pa"]), "H11S": float(pk.loc["F-35A H11S", "peak_Pa"])}
def Gof(t):
    o = {}
    for z in ZS:
        s = t[np.isclose(t.src_depth_m, z)].set_index("fc_hz").tl_db
        o[z] = np.array([sum(B.band_fraction(fc, np.array([1 / tau]), 2)[0] * 10 ** (-s[fc] / 10) for fc in F.BANDS) for tau in TAUS])
    return o
Ge = Gof(tl); GF = {st: Gof(ftl[ftl.station == st]) for st in pF}
rows = []
for conv, Ee in (("total KE", Et), ("vertical KE", Ev)):
    for z in ZS:
        for i, tau in enumerate(TAUS):
            d = {st: 10 * np.log10((p_e / pF[st]) ** 2 * (E_F / Ee) * GF[st][z][i] / Ge[z][i]) for st in pF}
            g = cal[(cal.slope == 2) & (cal.template == "T_C2") & (cal.E_case == "mid") & np.isclose(cal.src_depth_m, z) & np.isclose(cal.tau_s, tau)]
            eta_cal = 10 ** np.log10(g.eta_cal).mean()
            eta_e = p_e ** 2 / (R * Ee * B.RHO_C / (2 * np.pi) * Ge[z][i])
            rows.append(dict(convention=conv, E_event_J=Ee, src_depth_m=z, tau_s=tau, G_event=Ge[z][i], G_F_H11N=GF["H11N"][z][i], G_F_H11S=GF["H11S"][z][i],
                             delta_ratio_H11N_db=d["H11N"], delta_ratio_H11S_db=d["H11S"], delta_ratio_mean_db=0.5 * (d["H11N"] + d["H11S"]),
                             eta_event_upper=eta_e, eta_cal=eta_cal, delta_secondary_db=10 * np.log10(eta_e / eta_cal)))
df = pd.DataFrame(rows); df.to_csv(out / "af447_q1_grid.csv", index=False)
summ = {}
for conv, g in df.groupby("convention"):
    summ[conv] = {k: dict(median=float(g[k].median()), min=float(g[k].min()), max=float(g[k].max())) for k in ("delta_ratio_mean_db", "delta_ratio_H11N_db", "delta_ratio_H11S_db", "delta_secondary_db")}
    summ[conv]["by_src_depth_ratio_mean"] = {str(z): dict(median=float(h.delta_ratio_mean_db.median()), min=float(h.delta_ratio_mean_db.min()), max=float(h.delta_ratio_mean_db.max())) for z, h in g.groupby("src_depth_m")}
summ["inputs"] = dict(p_event_Pa_upper=p_e, snr=float(pk.loc["AF447 H10S", "snr"]), p_F_Pa=pF, E_F_J=E_F, E_total_J=Et, E_vertical_J=Ev, R_per_s=R, slope=2,
                      note="AF447 peak is an UPPER LIMIT (SNR < 2): every Delta here is an upper bound on Delta.")
json.dump(summ, open(out / "af447_q1_summary.json", "w"), indent=1)
print(json.dumps({k: v for k, v in summ.items() if k != "inputs"}, indent=0)[:2500])
EOF
python q1_af447.py "$P" tl/event_tl.csv q1