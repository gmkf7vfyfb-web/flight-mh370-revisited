"""Run J waypoints reference statistics per seed (Mac, numpy): final.npy summary (as final_stats.py) and the m0011 hand-off
corrected means, for the supplement's prior-recovery and re-allocation checks."""
import numpy as np, json, pathlib, sys
X = pathlib.Path("/Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/bto-bfo")
def final_stats(p):
    a = np.load(p, mmap_mode="r"); w = np.asarray(a[:, 0], float); lat = np.asarray(a[:, 1], float); lon = np.asarray(a[:, 2], float); st = np.asarray(a[:, 12]).astype(int)
    W = w.sum(); o = np.argsort(lat, kind="stable"); c = np.cumsum(w[o]) / W
    q = {k: float(lat[o][np.searchsorted(c, k)]) for k in (0.025, 0.5, 0.975)}
    return {"mean_lat": float((w * lat).sum() / W), "mean_lon": float((w * lon).sum() / W), "north_of_33S": float(w[lat > -33].sum() / W),
            "north_of_30S": float(w[lat > -30].sum() / W), "shoulder_34p5_36p5": float(w[(lat >= -36.5) & (lat <= -34.5)].sum() / W),
            "lat_q025": q[0.025], "lat_median": q[0.5], "lat_q975": q[0.975], "stratum_mass": [float(w[st == m].sum() / W) for m in range(5)]}
def handoff_stats(H):
    w = H[:, 0] * np.exp(H[:, 13]); W = w.sum(); lat = H[:, 1]
    f = {"lat": lat, "lon": H[:, 2], "alt_ft": H[:, 3], "mach": H[:, 4], "bfo_bias_hz": H[:, 8], "north_33": (lat > -33) * 1.0, "north_30": (lat > -30) * 1.0,
         "north_25": (lat > -25) * 1.0}
    out = {k: float((w * v).sum() / W) for k, v in f.items()}
    for m in range(5): out[f"mode{m}"] = float(w[H[:, 6] == m].sum() / W)
    return out
if __name__ == "__main__":
    R = {}
    for sd in sorted(X.glob("seed-*"), key=lambda p: int(p.name[5:])):
        d = json.load(open(sd / "diagnostics.json"))
        R[sd.name] = {"final": final_stats(sd / "final.npy"), "handoff_m0011": handoff_stats(np.load(sd / "handoff-m0011" / "handoff.npy")),
                      "log_evidence": d["log_evidence"], "lnZ_by_mode": [m["log_evidence"] for m in d["modes"]],
                      "m0011_mode_probability": d["handoffs"][1]["mode_probability"] if len(d["handoffs"]) > 1 else None}
        print(sd.name, flush=True)
    json.dump(R, open("runj_ref_stats.json", "w"), indent=1)
