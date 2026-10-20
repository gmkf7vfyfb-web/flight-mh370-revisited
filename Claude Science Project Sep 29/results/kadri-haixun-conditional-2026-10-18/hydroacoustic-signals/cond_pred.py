"""CONDITIONAL prediction given the H01W amplitude (eta-free): if the Kadri 306 deg arrival is the impact, scale each row's
source so that its predicted H01W peak equals the observed excess (T 1.018 Pa, C 0.668 Pa; digitised Fig. 9c, 2-20 Hz);
the coupling efficiency then cancels and the other stations' levels follow from the TL difference only.
Amplitude likelihood term at Perth Canyon 3376: LR = P(arrival SNR <= observed window-maximum SNR | H_K) (the window max is an
upper bound on any arrival in it); relative TL error N(0, 7.9 dB) primary, N(0, 11.2 dB) sensitivity (independent paths).
H08S: airgun-shot criterion, LR_nondetection = (1 - P_D) / (1 - 0.0067) (module construction 13 Oct).
Also: trajectory character of the timing-consistent rows.  Usage: python leg/cond_pred.py SCAN OUT"""
import sys, glob, json, pathlib; sys.path.insert(0, "leg"); import numpy as np, pandas as pd
from scipy.special import logsumexp; from pyproj import Geod; Gp = Geod(ellps="WGS84")
import levels as LV; from geometry_windows import ST, R7, AZ
SCAN, OUT = sys.argv[1], pathlib.Path(sys.argv[2])
DAY0 = 1394236800.0; T_OBS = {"T": 52 * 60 + 3, "C": 54 * 60 + 30}; C = 1.48; OBS = {"T": 1.018, "C": 0.668}; OBS_MS = {"T": 0.1283, "C": 0.0689};   # peak excess (Pa) and max 1 s mean-square excess (Pa^2), digitised Fig 9c, 2-20 Hz
SNR_OBS_3376 = {"T": 4.797, "C": 8.733}
Z = [np.load(f) for f in sorted(glob.glob(f"{SCAN}/*.npz"))]; DS = ["D0", "D2", "D5"]
logZ = {d: float(logsumexp([float(z["c_stratum"]) + json.loads(str(z["norms_json"]))[d] for z in Z])) for d in DS}
cat = lambda k: np.concatenate([np.asarray(z[k], float) for z in Z])
lat, lon, az, dist = cat("lat"), cat("lon"), cat("az"), cat("dist_km"); t_imp = cat("t_impact"); e_tr, tau = cat("e_tr"), cat("tau90")
cst = np.concatenate([np.full(len(z["row"]), float(z["c_stratum"])) for z in Z]); base = cat("base"); mix = np.logaddexp(np.log(0.75) + cat("C1"), np.log(0.25) + cat("C2s"))
LW = {d: cst + base + cat("ld_" + d) + mix - logZ[d] for d in DS}
X = dict(fam=cat("fam4"), fpa=cat("fpa"), vup=cat("vup"), vh=cat("vh"), ke=cat("ke"), mass=cat("mass"), push=cat("pushover"), tfo=cat("t_flameout") - DAY0)
bdev = ((az - AZ + 180) % 360) - 180; s_t = np.sqrt((dist * 0.015 / C ** 2) ** 2 + 25.0)
strip = (np.abs(bdev) <= 1.0) & (dist >= R7["bto"] - 60) & (dist <= R7["bto"] + 250); ok = np.isfinite(e_tr) & (e_tr > 0) & np.isfinite(tau)
def wq(x, w, qs=(0.05, 0.5, 0.95)):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]; return [float(x[o][min(np.searchsorted(c, q), len(x) - 1)]) for q in qs]
T = LV.tl_tables(); N = LV.noise(); CV = LV.pd_curves(); rng = np.random.default_rng(20261018)
pos = {k: (v[0], v[1]) for k, v in ST.items()}; pos["H01W"] = (-34.8903, 114.1426)
STN = ["PerthCanyon_3376", "PerthCanyon_3315", "H08S", "OHAS_SSEIR", "OHAS_SWAMS3", "OHAS_MAD", "OHAS_WKER", "OHAS_NCRO"]
res, traj = [], {}
for d in DS:
    for br in ("T", "C"):
        li = np.exp(-0.5 * ((T_OBS[br] - (t_imp + dist / C)) / s_t) ** 2) / s_t * np.exp(-0.5 * (bdev / 0.5) ** 2)
        for subset, w in (("strip", np.exp(LW[d]) * strip), (f"timing-consistent {br}", np.exp(LW[d]) * li)):
            m = ok & (w > 0)
            if w[m].sum() <= 0: continue
            wn = w[m] / w[m].sum(); ess = float(1 / (wn ** 2).sum())
            if subset.startswith("timing"):
                traj[f"{d}|{br}"] = dict(ess=ess, impact_utc_q=[f"00:{int(x%3600//60):02d}:{int(x%60):02d}" for x in wq(t_imp[m], wn)], lat_q=wq(lat[m], wn), lon_q=wq(lon[m], wn),
                                         dist_from_h01w_km_q=wq(dist[m], wn), e_tr_j_q=wq(e_tr[m], wn), tau90_s_q=wq(tau[m], wn), fpa_deg_q=wq(X["fpa"][m], wn),
                                         vup_mps_q=wq(X["vup"][m], wn), vh_mps_q=wq(X["vh"][m], wn), minutes_after_flameout_q=wq((t_imp[m] - X["tfo"][m]) / 60, wn),
                                         family_share={str(int(f)): float(wn[X["fam"][m] == f].sum()) for f in np.unique(X["fam"][m])}, pushover_share=float(wn[X["push"][m] == 1].sum()))
            la, lo = pos["H01W"]; _, _, r = Gp.inv(np.full(m.sum(), lo), np.full(m.sum(), la), lon[m], lat[m])
            h = LV.station_levels(e_tr[m], tau[m], r / 1e3, "H01W", T, N, CV)[1e-3]
            S_h = h["se"] / np.maximum(np.clip(tau[m], 0.05, 10), 1.0)
            for anchor, eta_req in (("energy", 1e-3 * OBS_MS[br] / S_h), ("peak", 1e-3 * (OBS[br] / h["ppk"]) ** 2)):
             for stn in STN:
                 la, lo = pos[stn]; _, _, r = Gp.inv(np.full(m.sum(), lo), np.full(m.sum(), la), lon[m], lat[m])
                 v = LV.station_levels(e_tr[m], tau[m], r / 1e3, stn, T, N, CV)[1e-3]
                 s_lin = v["se"] * eta_req / 1e-3 / np.maximum(np.clip(tau[m], 0.05, 10), 1.0) / 1e-12 / 10 ** (N.get(stn, N["H08S"]) / 10)
                 snr = 10 * np.log10(1 + s_lin); ppk = v["ppk"] * np.sqrt(eta_req / 1e-3)
                 rec = dict(D=d, branch=br, subset=subset, anchor=anchor, station=stn, ess=ess, eta_req_q=wq(eta_req, wn), cond_ppk_pa_q=wq(ppk, wn), cond_snr_db_q=wq(snr, wn))
                 idx = rng.choice(len(wn), 100000, p=wn)
                 for sd in (7.9, 11.2):
                     sl = s_lin[idx] * 10 ** (rng.normal(0, sd, idx.size) / 10); sn = 10 * np.log10(1 + sl)
                     if stn == "PerthCanyon_3376": rec[f"LR_amp_sd{sd}"] = float((sn <= SNR_OBS_3376[br]).mean())
                     if stn == "H08S":
                         shot = 10 * np.log10(v["se"][idx] * eta_req[idx] / 1e-3 / LV.MED_SHOT) + rng.normal(0, sd, idx.size)
                         pdv = np.interp(shot, *CV["h08s_shot"]); rec[f"H08S_shot_snr_q_sd{sd}"] = [float(np.quantile(shot, q)) for q in (0.05, 0.5, 0.95)]
                         rec[f"LR_nondet_sd{sd}"] = float(np.mean((1 - pdv) / (1 - 0.0067)))
                 res.append(rec)
pd.DataFrame(res).to_json(OUT / "conditional_on_h01w_level.json", orient="records", indent=1); json.dump(traj, open(OUT / "timing_consistent_rows.json", "w"), indent=1)
P = pd.DataFrame(res); P["snr"] = P.cond_snr_db_q.map(lambda v: "/".join(f"{x:.1f}" for x in v)); P["ppk"] = P.cond_ppk_pa_q.map(lambda v: "/".join(f"{x:.2f}" for x in v))
cols = [c for c in ["D", "branch", "subset", "anchor", "station", "ess", "ppk", "snr", "LR_amp_sd7.9", "LR_amp_sd11.2", "LR_nondet_sd7.9", "LR_nondet_sd11.2"] if c in P]
print(P[P.station.isin(["PerthCanyon_3376", "H08S", "OHAS_SSEIR", "OHAS_MAD"])][cols].to_string(index=False)); print(json.dumps(traj, indent=0)[:3000])
