cat > leg/analyse_L.py <<'EOF'
"""Run J rows in the locality L: weights (headline 'D{d} total q=0.333 (C2 silent)'), per-branch arrival likelihood at H01W
(pre-registration Q2 formula, as a CROSS-CHECK only), predicted received level / SNR / P_D at every station across the
coupling sweep, and the H01W level-consistency test (Q4).  Usage: python leg/analyse_L.py SCAN_DIR OUT_DIR"""
import sys, glob, json, pathlib; sys.path.insert(0, "leg"); import numpy as np, pandas as pd
from scipy.special import logsumexp
from pyproj import Geod; Gp = Geod(ellps="WGS84")
import levels as LV; from geometry_windows import ST, R7, AZ
SCAN, OUT = sys.argv[1], pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
DAY0 = 1394236800.0; T_OBS = {"T": 52 * 60 + 3, "C": 54 * 60 + 30}; C = 1.48
files = sorted(glob.glob(f"{SCAN}/*.npz")); Z = [np.load(f, allow_pickle=False) for f in files]
names = [pathlib.Path(f).stem for f in files]
DS = ["D0", "D1", "D2", "D3", "D4", "D5"]
logZ = {d: float(logsumexp([float(z["c_stratum"]) + json.loads(str(z["norms_json"]))[d] for z in Z])) for d in DS}
cat = lambda k: np.concatenate([np.asarray(z[k], float) for z in Z])
seed_id = np.concatenate([np.full(len(z["row"]), i) for i, z in enumerate(Z)])
lat, lon, az, dist = cat("lat"), cat("lon"), cat("az"), cat("dist_km"); dx, dh = cat("dx_km"), cat("dh_km")
t_imp = cat("t_impact") - DAY0; e_tr, tau, ke = cat("e_tr"), cat("tau90"), cat("ke"); fam = cat("fam4"); parent = cat("parent")
cst = np.concatenate([np.full(len(z["row"]), float(z["c_stratum"])) for z in Z]); base = cat("base")
mix = np.logaddexp(np.log(0.75) + cat("C1"), np.log(0.25) + cat("C2s"))
LW = {d: cst + base + cat("ld_" + d) + mix - logZ[d] for d in DS}          # log of globally normalised weight
strip = (np.abs(((az - AZ + 180) % 360) - 180) <= 1.0) & (dist >= R7["bto"] - 60) & (dist <= R7["bto"] + 250)
regions = {"strip": strip}
for r in (50, 100, 200, 400): regions[f"disc{r}_crossing"] = dx <= r; regions[f"disc{r}_haixun"] = dh <= r
def wq(x, w, qs=(0.05, 0.5, 0.95)):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]; return [float(x[o][min(np.searchsorted(c, q), len(x) - 1)]) for q in qs]
reg = {}
for d in DS:
    w_all = np.exp(LW[d])
    for rn, m in regions.items():
        w = w_all[m]; s = w.sum()
        if s <= 0 or not m.any(): reg[f"{d}|{rn}"] = dict(mass=0.0, ess=0.0, n_rows=int(m.sum())); continue
        wn = w / s; key = seed_id[m] * 10 ** 7 + parent[m]; up = pd.Series(wn).groupby(key).sum()
        ok = np.isfinite(e_tr[m]) & (e_tr[m] > 0)
        reg[f"{d}|{rn}"] = dict(mass=float(s), ess=float(1 / (wn ** 2).sum()), n_rows=int(m.sum()), eff_parents=float(1 / (up.values ** 2).sum()),
                                family_share={str(int(f)): float(wn[fam[m] == f].sum()) for f in np.unique(fam[m])},
                                t_impact_q=[f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d}" for x in wq(t_imp[m], wn)],
                                e_tr_q=wq(e_tr[m][ok], wn[ok]) if ok.any() else None, tau90_q=wq(tau[m][ok], wn[ok]) if ok.any() else None)
json.dump(dict(logZ=logZ, files=names, regions=reg), open(OUT / "L_regions.json", "w"), indent=1)
# Q2 cross-check (lower bound: rows with |bearing - 306.18| > 1.5 deg or range outside 1,400-1,950 km were not scanned)
bdev = ((az - AZ + 180) % 360) - 180; s_t = np.sqrt((dist * 0.015 / C ** 2) ** 2 + 25.0); L_bg = 1.0 / (1260.0 * 140.0)
q2 = {}; LI = {}
for br in ("T", "C"):
    tp = t_imp + dist / C
    for sbn, sb in (("core", 0.5), ("wide", 1.0)):
        li = np.exp(-0.5 * ((T_OBS[br] - tp) / s_t) ** 2) / (np.sqrt(2 * np.pi) * s_t) * np.exp(-0.5 * (bdev / sb) ** 2) / (np.sqrt(2 * np.pi) * sb)
        LI[(br, sbn)] = li
        for d in DS:
            w = np.exp(LW[d]); num = float((w * li).sum()); wl = w * li
            q2[f"{br}|{sbn}|{d}"] = dict(B_lower_bound=num / L_bg, log10_B=float(np.log10(num / L_bg)) if num > 0 else None,
                                         ess_wL=float(wl.sum() ** 2 / (wl ** 2).sum()) if num > 0 else 0.0,
                                         impact_q=[f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d}" for x in wq(t_imp, wl)] if num > 0 else None,
                                         lat_q=wq(lat, wl) if num > 0 else None, lon_q=wq(lon, wl) if num > 0 else None)
json.dump(q2, open(OUT / "q2_crosscheck.json", "w"), indent=1)
# received levels: rows in the strip (branch-independent) and rows weighted by L_i (branch-specific, core bearing sigma)
T = LV.tl_tables(); N = LV.noise(); CV = LV.pd_curves(); ok = strip & np.isfinite(e_tr) & (e_tr > 0) & np.isfinite(tau)
STN = ["H01W", "PerthCanyon_3376", "PerthCanyon_3315", "H08S", "OHAS_SSEIR", "OHAS_SWAMS3", "OHAS_MAD", "OHAS_WKER", "OHAS_NCRO"]
pos = {k: (v[0], v[1]) for k, v in ST.items()}; pos["H01W"] = (-34.8903, 114.1426)
rows = []; keepH = {}
for d in ("D2", "D5", "D0"):
    for subset in ("strip", "T", "C"):
        w = np.exp(LW[d]) * (1.0 if subset == "strip" else LI[(subset, "core")]); m = ok & (w > 0)
        if not m.any(): continue
        wn = w[m] / w[m].sum(); ess = float(1 / (wn ** 2).sum())
        for stn in STN:
            la, lo = pos[stn]; _, _, r = Gp.inv(np.full(m.sum(), lo), np.full(m.sum(), la), lon[m], lat[m]); r = r / 1e3
            lev = LV.station_levels(e_tr[m], tau[m], r, stn, T, N, CV)
            for eta, v in lev.items():
                rec = dict(D=d, subset=subset, station=stn, eta=eta, ess=ess, n_rows=int(m.sum()), range_km_q50=wq(r, wn)[1],
                           snr_db_q=wq(v["snr"], wn), ppk_pa_q=wq(v["ppk"], wn), se_q=wq(v["se"], wn),
                           pd05_mean=float((wn * v["pd05"]).sum()), pd005_mean=float((wn * v["pd005"]).sum()),
                           share_pd05_ge_0p5=float(wn[v["pd05"] >= 0.5].sum()))
                if stn == "H08S": rec.update(snr_shot_q=wq(v["snr_shot"], wn), pd_shot_mean=float((wn * v["pd_shot"]).sum()))
                rows.append(rec)
            if stn == "H01W": keepH[(d, subset)] = (wn, lev, r)
pd.DataFrame(rows).to_json(OUT / "levels.json", orient="records", indent=1)
# Q4: H01W level consistency. Observed excess envelope amplitude over the panel's median 6 s maximum (digitised Fig 9c, 2-20 Hz)
OBS = {"T": 1.018, "C": 0.668}; rng = np.random.default_rng(20261018); q4 = {}
for d in ("D2", "D5", "D0"):
    for subset in ("strip", "T", "C"):
        if (d, subset) not in keepH: continue
        wn, lev, r = keepH[(d, subset)]; p1 = lev[1e-3]["ppk"]
        for br in ("T", "C"):
            eta_req = 1e-3 * (OBS[br] / p1) ** 2
            # prior-predictive tail: eta log-uniform 1e-4..1e-1, TL error N(0, 7.9 dB), 64 draws per row (row drawn by weight)
            idx = rng.choice(len(wn), size=200000, p=wn); le = rng.uniform(-4, -1, idx.size); dtl = rng.normal(0, 7.9, idx.size)
            ppk = p1[idx] * np.sqrt(10 ** le / 1e-3) * 10 ** (-dtl / 20)
            q4[f"{d}|{subset}|obs{br}"] = dict(observed_excess_pa=OBS[br], ppk_eta_f35_q=[float(x) * np.sqrt(LV.ETA_F35 / 1e-3) for x in wq(p1, wn)],
                                               eta_required_q=wq(eta_req, wn), eta_required_q_tl_minus2sd=wq(eta_req * 10 ** (-15.8 / 10), wn),
                                               share_eta_req_le_0p1=float(wn[eta_req <= 0.1].sum()), share_eta_req_le_f35=float(wn[eta_req <= LV.ETA_F35].sum()),
                                               prior_predictive_P_ppk_ge_obs=float((ppk >= OBS[br]).mean()))
json.dump(q4, open(OUT / "q4_h01w_level.json", "w"), indent=1)
print(json.dumps({k: reg[k] for k in reg if k.startswith("D2|strip") or k.startswith("D2|disc50")}, indent=0)[:1500])
print(json.dumps({k: (v["log10_B"], round(v["ess_wL"], 1)) for k, v in q2.items()}))
print(json.dumps(q4, indent=0)[:2500])
EOF
python leg/analyse_L.py leg/scan_dev leg/out_dev 2>&1 | grep -v -i -E 'proj|ca_bundle'