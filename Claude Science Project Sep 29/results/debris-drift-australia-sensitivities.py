"""Australian non-recovery term: the pre-registered sensitivities (A, C, off, searcher) against the
pre-registered primary (B), on the completed REACH-LIMITED interim pilot of 12-13 Oct 2026.

No transport is run. The pilot scored every option as a level column in one pass, so this script only
reads the committed node table and reports what the work order of 15 Oct 2026 (section 2, item 9) asks for:
the drift-only median and 90 per cent interval per option, the share of floating debris reaching
Australian coasts by source latitude, and the change in log evidence.

Base surface: run A GLORYS12 node log-likelihoods from results/debris-drift-two-model-nodes.csv (367 of the
710 run A nodes; the other 343 are not on disk), with the per-node change carried from the pilot nodes by
inverse-distance weighting of the 6 nearest, as in prepare/pilot/australia_pilot_analysis.py. A cross-check
repeats everything on the 175 pilot nodes alone, with no carry.

Usage: python debris-drift-australia-sensitivities.py <results dir> <out stem>
"""
import sys, json
import numpy as np, pandas as pd

res_dir, stem = sys.argv[1:3]
p = pd.read_csv(f"{res_dir}/debris-drift-australia-pilot-nodes.csv")
tm = pd.read_csv(f"{res_dir}/debris-drift-two-model-nodes.csv")

OPT = {"off": "ln_l_lev_off", "B (primary)": "ln_l", "A": "ln_l_lev_A", "C": "ln_l_lev_C",
       "searcher": "ln_l_lev_searcher"}
DELTA = {"B (primary)": "d_B (primary)", "A": "d_A", "C": "d_C", "searcher": "d_searcher"}
q = p[p[list(OPT.values())].notna().all(axis=1)].copy()

def km(la1, lo1, la2, lo2):
    return 111.195 * np.hypot(la1 - la2, (lo1 - lo2) * np.cos(np.radians(0.5 * (la1 + la2))))

def lat_stats(lnl, lat, qs=(0.025, 0.05, 0.25, 0.5, 0.75, 0.95, 0.975)):
    w = np.exp(lnl - lnl.max()) * np.cos(np.radians(lat)); w /= w.sum()
    o = np.argsort(lat); c = np.cumsum(w[o]); la = lat[o]
    return {x: float(np.interp(x, c, la)) for x in qs}

def mean_lat(lnl, lat):
    w = np.exp(lnl - lnl.max()) * np.cos(np.radians(lat)); w /= w.sum()
    return float(np.sum(w * lat))

def ln_z(lnl, lat):
    w = np.cos(np.radians(lat)); w /= w.sum(); m = lnl.max()
    return float(m + np.log(np.sum(w * np.exp(lnl - m))))

# --- carry the per-node change to the recoverable run A nodes (IDW, 6 nearest, inverse square of km)
A = tm[tm.ln_l_glorys12.notna()].copy()
for name, dcol in DELTA.items():
    v = np.empty(len(A))
    for i, (la, lo) in enumerate(zip(A.lat_deg.values, A.lon_deg.values)):
        d = km(la, lo, q.lat_deg.values, q.lon_deg.values)
        k = np.argsort(d)[:6]; w = 1 / np.maximum(d[k], 1.0) ** 2
        v[i] = np.sum(w * q[dcol].values[k]) / w.sum()
    A["carried_" + name] = v

latA, latP = A.lat_deg.values, q.lat_deg.values
both = q[[c + s for c in OPT.values() for s in ("_half_a", "_half_b")]].notna().all(axis=1)
qb = q[both]; latB = qb.lat_deg.values

summary = {}
for name in OPT:
    lnlA = A.ln_l_glorys12.values if name == "off" else A.ln_l_glorys12.values + A["carried_" + name].values
    sA, sP = lat_stats(lnlA, latA), lat_stats(q[OPT[name]].values, latP)
    e = {"median": sA[0.5], "p5": sA[0.05], "p95": sA[0.95], "p2.5": sA[0.025], "p97.5": sA[0.975],
         "mean_latitude": mean_lat(lnlA, latA),
         "cross_check_pilot_nodes_only": {"median": sP[0.5], "p5": sP[0.05], "p95": sP[0.95]}}
    if name != "off":
        sh = [mean_lat(qb[OPT[name] + h].values, latB) - mean_lat(qb[OPT["off"] + h].values, latB)
              for h in ("_half_a", "_half_b")]
        dz = [ln_z(qb[OPT[name] + h].values, latB) - ln_z(qb[OPT["off"] + h].values, latB)
              for h in ("_half_a", "_half_b")]
        e.update({
            "median_shift_north": sA[0.5] - lat_stats(A.ln_l_glorys12.values, latA)[0.5],
            "mean_latitude_shift_north": mean_lat(lnlA, latA) - mean_lat(A.ln_l_glorys12.values, latA),
            "mean_latitude_shift_split_half_noise": abs(sh[0] - sh[1]) / 2,
            "delta_ln_evidence": ln_z(lnlA, latA) - ln_z(A.ln_l_glorys12.values, latA),
            "delta_ln_evidence_pilot_nodes_only": ln_z(q[OPT[name]].values, latP) - ln_z(q[OPT["off"]].values, latP),
            "delta_ln_evidence_split_half_noise": abs(dz[0] - dz[1]) / 2,
            "mean_per_node_change_in_ln_l": float((q[OPT[name]] - q[OPT["off"]]).mean())})
    summary[name] = e

# --- arrival shares by source latitude (physics; the same under every option)
CLS = ["flaperon", "low_exposure_exterior", "high_windage_interior"]
GRP = {"find coasts S1-S6": range(0, 6), "Australia city and inner regional": [6, 7, 8],
       "Australia outer regional": [9, 10, 11], "Australia remote and very remote": [12, 13, 14, 15],
       "Australia Western Australia": [8, 11, 15], "Australia south (SA-Vic-Tas)": [7, 10, 14],
       "Australia north-east (NT-Qld-NSW)": [6, 9, 13], "Australia Indian Ocean territories": [12]}
sh = pd.DataFrame({"lat_deg": latP})
for g, idx in GRP.items():
    sh[g] = np.mean([q[[f"p_{c}_{i}" for i in idx]].sum(axis=1).values for c in CLS], axis=0)
sh["Australia, all coasts"] = sh[["Australia city and inner regional", "Australia outer regional",
                                  "Australia remote and very remote"]].sum(axis=1)
sh["beached anywhere"] = np.mean([q[f"p_{c}_any_beach"].values for c in CLS], axis=0)
sh["left the model domain"] = q.left_domain_fraction.values
sh["band"] = pd.cut(sh.lat_deg, [-42, -37, -34, -31, -28, -25, -20])
cols = ["Australia, all coasts", "Australia Western Australia", "Australia south (SA-Vic-Tas)",
        "Australia north-east (NT-Qld-NSW)", "Australia Indian Ocean territories",
        "Australia city and inner regional", "Australia outer regional", "Australia remote and very remote",
        "find coasts S1-S6", "beached anywhere", "left the model domain"]
shares = (100 * sh.groupby("band", observed=True)[cols].mean()).round(2)
counts = sh.groupby("band", observed=True).size()

out = {"source": "completed interim pilot 12-13 Oct 2026, GLORYS12 + ERA5, no new transport run",
       "nodes_scored_in_all_options": int(len(q)),
       "base_surface": "run A GLORYS12, 367 of 710 nodes recoverable; change carried by IDW from the pilot nodes",
       "drift_only_latitude_by_option_deg": summary,
       "arrival_share_percent_by_source_latitude_band": shares.reset_index().astype({"band": str}).to_dict("records"),
       "nodes_per_band": {str(k): int(v) for k, v in counts.items()},
       "labels": ["PILOT", "REACH-LIMITED 15-120 E", "GLORYS12 only", "interim, not evidence",
                  "run I not converged", "not composed"]}
json.dump(out, open(stem + ".json", "w"), indent=1)
shares.to_csv(stem + "-shares.csv")
print(pd.DataFrame(summary).T.to_string())
print(shares.to_string())
