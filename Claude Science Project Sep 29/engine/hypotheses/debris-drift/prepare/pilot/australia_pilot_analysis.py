"""Australian non-recovery pilot: per-node change in ln L from the Australian term (option - off), by option, with split-half noise,
and its effect on the drift-only latitude distribution. The pilot nodes are every 4th run A node, so the change is carried to all 710
run A GLORYS12 nodes by inverse-distance weighting of the 6 nearest pilot nodes (declared approximation) and added to the run A surface.
Usage: python australia_pilot_analysis.py <pilot merged dir> <run A glorys12 merged dir> <out stem>"""
import sys, json
import numpy as np, pandas as pd
pilot, runa, stem = sys.argv[1:4]
p = pd.read_csv(f"{pilot}/nodes.csv"); a = pd.read_csv(f"{runa}/nodes.csv")
opts = {"B (primary)": "ln_l", "A": "ln_l_lev_A", "C": "ln_l_lev_C", "searcher": "ln_l_lev_searcher"}
off = "ln_l_lev_off"
res = {}
ok = p[[off] + list(opts.values())].notna().all(axis=1); q = p[ok].copy()
for name, c in opts.items():
    d = q[c] - q[off]
    dh = (q[c + "_half_a"] - q[off + "_half_a"]) - (q[c + "_half_b"] - q[off + "_half_b"]) if c != "ln_l" else (q["ln_l_half_a"] - q[off + "_half_a"]) - (q["ln_l_half_b"] - q[off + "_half_b"])
    q["d_" + name] = d
    res[name] = {"mean": float(d.mean()), "min": float(d.min()), "max": float(d.max()), "split_half_noise_of_delta": float(dh.std() / 2)}
bands = [-42, -37, -34, -31, -28, -25, -20]
q["band"] = pd.cut(q.lat_deg, bands)
tab = q.groupby("band", observed=True)[[c for c in q.columns if c.startswith("d_")]].mean().round(3)
# carry Delta(B) to the run A nodes (IDW, 6 nearest pilot nodes, distance in km)
def km(la1, lo1, la2, lo2):
    return 111.195 * np.hypot(la1 - la2, (lo1 - lo2) * np.cos(np.radians(0.5 * (la1 + la2))))
A = a[a.ln_l.notna()].copy()
for name in opts:
    vals = np.empty(len(A))
    for i, (la, lo) in enumerate(zip(A.lat_deg.values, A.lon_deg.values)):
        dd = km(la, lo, q.lat_deg.values, q.lon_deg.values); k = np.argsort(dd)[:6]; w = 1 / np.maximum(dd[k], 1.0) ** 2
        vals[i] = np.sum(w * q["d_" + name].values[k]) / w.sum()
    A["d_" + name] = vals
def lat_stats(lnl):
    w = np.exp(lnl - lnl.max()) * np.cos(np.radians(A.lat_deg.values)); w /= w.sum(); o = np.argsort(A.lat_deg.values); c = np.cumsum(w[o]); la = A.lat_deg.values[o]
    return {q_: float(np.interp(q_, c, la)) for q_ in (0.025, 0.25, 0.5, 0.75, 0.975)}
out = {"pilot_nodes_scored_all_options": int(ok.sum()), "delta_by_option": res, "band_means": tab.reset_index().astype({"band": str}).to_dict("records"),
       "drift_only_latitude_quantiles": {"off (run A surface)": lat_stats(A.ln_l.values), **{n: lat_stats(A.ln_l.values + A["d_" + n].values) for n in opts}},
       "note": "drift-only, uniform prior over the 710-node grid, GLORYS12 only; Delta carried by IDW from 178 pilot nodes; REACH-LIMITED (120 E)"}
json.dump(out, open(stem + ".json", "w"), indent=1); q.drop(columns=["band"]).to_csv(stem + "-nodes.csv", index=False)
print(json.dumps({k: out[k] for k in ("pilot_nodes_scored_all_options", "delta_by_option")}, indent=1)); print(tab.to_string())
print(json.dumps(out["drift_only_latitude_quantiles"], indent=1))
