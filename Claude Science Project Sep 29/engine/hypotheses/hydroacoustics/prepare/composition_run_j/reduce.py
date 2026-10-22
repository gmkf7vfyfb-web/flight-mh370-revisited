"""Block 11 reduction (prereg.py sections 9-11): merge the per-seed streamed accumulators (strata mixed by p_core / K, seeds pooled
by evidence, supplement mixed by share s_D), then the 95 % upper limits on eta (two ways), the evidence three ways, the family
and Holland-type Bayes factors, the conditional-hypothesis Bayes factors (Kadri 306.18 at both times, Royer B/D1/D2, poster
boxes), and the two-site coincidence summary. Writes CSV/JSON to <out_dir>. Usage: python reduce.py <columns_dir> <out_dir>
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R
from common import Machinery
from worker import KEYS, NB1, NBH, FAM_CODES
import os
STATS_ONLY = os.environ.get("B11_STATS_ONLY") == "1"     # amendment A4: RAM-grid IMOS TL + amplitude-weighted variant present in the accumulators

FAM_NAMES = {1: "A1", 2: "A2", 3: "B", 6: "outside B"}
OPTION_NAMES = {"D0": "00:19 Held Out (D0')", "D2": "R600 BTO + BFO (D2)", "D3": "both BFOs as recorded (D3)", "D4": "both BFOs, shared start-up offset (D4)"}
BANDS5 = [(-41, -36), (-36, -31), (-31, -26), (-26, -21), (-21, -20), (-41, -20)]
ETA = R.ETA_GRID; LETA = np.log10(ETA); NG = len(ETA)
ALPHA_TAGS = {a: f"a{a:g}" for a in R.ALPHAS}


def load_parts(cols_dir):
    cols_dir = Path(cols_dir)
    pc = json.load(open(R.RUN_J / "summary" / "family-evidence-run-j.json"))["p_core"]
    acc = {}; sub = []; meta = {}
    def addto(A, z, c):
        for k in z.files:
            if k == "meta": continue
            A[k] = A.get(k, 0) + z[k] * c
    for s in R.STRATA:
        seeds = sorted([p for p in (cols_dir / s).glob("seed-*") if (p / "acc.npz").exists()], key=lambda p: int(p.name.split("-")[1]))
        K = len(seeds); meta[s] = K
        for sd in seeds:
            z = np.load(sd / "acc.npz"); c = pc[s] / K
            addto(acc, z, c)
            # sum_w2 and fam_w2 scale with c^2: correct them (they were added with c)
            acc["sum_w2"] += z["sum_w2"] * (c * c - c); acc["fam_w2"] += z["fam_w2"] * (c * c - c)
            ss = np.load(sd / "subsample.npz"); d = {k: ss[k] for k in ss.files if k not in ("stratum", "seed")}
            d["W"] = d["W"] * c * R.SUBSAMPLE_EVERY; d["src"] = np.full(len(d["lat"]), s); sub.append(d)
    supp = None; supp_sub = None; share = None
    if (cols_dir / "supplement" / "acc.npz").exists():
        z = np.load(cols_dir / "supplement" / "acc.npz"); supp = {k: z[k] for k in z.files if k != "meta"}
        ss = np.load(cols_dir / "supplement" / "subsample.npz"); supp_sub = {k: ss[k] for k in ss.files if k not in ("stratum", "seed")}
        supp_sub["W"] = supp_sub["W"] * 2.0; supp_sub["src"] = np.full(len(supp_sub["lat"]), "supplement")
        share = json.load(open(cols_dir / "_parts" / "supplement.json"))["share"]
    return acc, supp, share, sub, supp_sub, meta


def mix(acc, supp, share):
    """Per option/p: strata totals normalised to (1 - s_D), supplement to s_D (windows note pooling). Returns dict of mixed arrays
    with the same keys, plus the normalising constants."""
    out = {}; norm = {}
    for j, key in enumerate(KEYS):
        o = key.split("/")[0]; sD = share[o]["supplement"] / share[o]["total"] if (supp is not None and share) else 0.0
        Zs = acc["sum_w"][j].sum(); Zp = supp["sum_w"][j].sum() if supp is not None else 0.0
        a = (1 - sD) / Zs if Zs > 0 else 0.0; b = sD / Zp if Zp > 0 else 0.0
        norm[key] = dict(a=a, b=b, sD=sD, Zs=Zs, Zsup=Zp)
        for k in acc:
            if k.endswith("hist_edges"): out[k] = acc[k]; continue
            sq = k in ("sum_w2", "fam_w2")
            v = acc[k][j] * (a * a if sq else a)
            if supp is not None: v = v + supp[k][j] * (b * b if sq else b)
            out.setdefault(k, np.zeros((12,) + np.shape(v)))[j] = v
    return out, norm


def band_sum(arr1deg, lo, hi):
    """Sum of the 1-degree-band axis over [lo, hi): bins 1..21 are 41..20 S; 0 = south of 41, 22 = north of 20."""
    e = R.LAT_BAND_EDGES_1DEG; i0 = int(np.searchsorted(e, lo + 1e-9, "right")); i1 = int(np.searchsorted(e, hi - 1e-9, "right"))
    return arr1deg[i0:i1 + 1].sum(0)      # band axis is the first axis ([band] or [band, eta])


def upper_limits(mx, norm):
    rows = []
    for j, key in enumerate(KEYS):
        for a in R.ALPHAS:
            t = ALPHA_TAGS[a]
            variants = [(False, "IMOS gated"), (True, "IMS proxy + IMOS")] + ([("A", "IMOS gated (amplitude-weighted)")] if STATS_ONLY else [])
            for ims, label in variants:
                wP = mx[f"wPnd{'_ims' if ims is True else ''}_{t}"][j]; wL = mx[f"wL_A_{t}" if ims == "A" else f"wL{'_ims' if ims else ''}_{t}"][j]; sw = mx["sum_w"][j]; sw2 = mx["sum_w2"][j]
                for lo, hi in BANDS5:
                    W = band_sum(sw, lo, hi); W2 = band_sum(sw2, lo, hi)
                    if W <= 0: rows.append(dict(option=key.split("/")[0], p=float(key.split("/p")[1]), alpha=a, receivers=label, lat_lo=lo, lat_hi=hi, share=0.0, ess=0.0)); continue
                    P = band_sum(wP, lo, hi)[:NG] / W; L = band_sum(wL, lo, hi)[:NG] / W
                    # Bayesian 95 % upper limit under the log-uniform prior: posterior on the grid proportional to L (equal prior weights)
                    post = L / L.sum(); cdf = np.cumsum(post)
                    i = int(np.searchsorted(cdf, 0.95)); eta95 = 10 ** (LETA[i] - 0.05 + 0.1 * (0.95 - (cdf[i - 1] if i > 0 else 0.0)) / post[i]) if i < NG else ETA[-1]
                    postN = P / P.sum(); cdfN = np.cumsum(postN); iN = int(np.searchsorted(cdfN, 0.95))
                    eta95_nd = 10 ** (LETA[iN] - 0.05 + 0.1 * (0.95 - (cdfN[iN - 1] if iN > 0 else 0.0)) / postN[iN]) if iN < NG else ETA[-1]
                    # classical exclusion: weighted probability of no detection = 0.05
                    if P[-1] > 0.05: excl = None
                    else:
                        k = int(np.argmax(P <= 0.05)); excl = float(10 ** np.interp(0.05, [P[k], P[k - 1]], [LETA[k], LETA[k - 1]])) if k > 0 else float(ETA[0])
                    rows.append({"option": key.split("/")[0], "p": float(key.split("/p")[1]), "alpha": a, "receivers": label, "lat_lo": lo, "lat_hi": hi,
                                 "share": float(W), "ess": float(W * W / W2) if W2 > 0 else 0.0, "eta95_bayes_nondetection_logu_1e-6_1e-2": float(eta95_nd), "eta95_bayes_full_likelihood": float(eta95), "eta95_prior_alone": float(10 ** (-6 + 0.95 * 4)),
                                 "eta_excl95_classical": excl, "pnd_at_1e-2": float(P[-1]), "pnd_at_1e-3": float(P[np.argmin(abs(LETA + 3))]),
                                 "pnd_at_anchor": float(np.interp(np.log10(R.ETA_ANCHOR), LETA, P)), "pnd_at_1e-4": float(P[np.argmin(abs(LETA + 4))]),
                                 "L_at_1e-2": float(L[-1]), "L_at_anchor": float(np.interp(np.log10(R.ETA_ANCHOR), LETA, L)), "L_marg": float(L.mean()),
                                 "posterior_median_eta": float(10 ** np.interp(0.5, cdf, LETA))})
    return pd.DataFrame(rows)


def evidence_three_ways(mx):
    e = R.LAT_BIN_EDGES_HALF; mid = 0.5 * (e[:-1] + e[1:]); rows = []; dists = {}
    for j, key in enumerate(KEYS):
        core = mx["half_w"][j]; Zc = core.sum()
        for a in R.ALPHAS:
            for ims, label in [(False, "IMOS gated"), (True, "IMS proxy + IMOS")] + ([("A", "IMOS gated (amplitude-weighted)")] if STATS_ONLY else []):
                wL = mx[f"half_wLA_{ALPHA_TAGS[a]}" if ims == "A" else f"half_wL{'ims' if ims else ''}_{ALPHA_TAGS[a]}"][j]
                comb = wL / wL.sum() if wL.sum() > 0 else wL
                corep = core / Zc
                # hydroacoustics alone on a prior uniform along the arc: bin mean of exp(lnL_marg), over bins 41-20 S with mass
                sel = (mid > -41) & (mid < -20) & (core > 1e-9 * Zc)
                alone = np.zeros(NBH); alone[sel] = wL[sel] / core[sel]; alone = alone / alone.sum() if alone.sum() > 0 else alone
                with np.errstate(divide="ignore", invalid="ignore"):
                    kl = float(np.nansum(np.where(corep > 0, corep * np.log(corep / np.where(comb > 0, comb, np.nan)), 0.0)))
                med = lambda d: float(np.interp(0.5, np.cumsum(d), e[1:]))
                n33 = lambda d: float(d[mid > -33].sum())
                dists[(key, a, ims)] = dict(mid=mid, core=corep, combined=comb, alone=alone)
                rows.append(dict(option=key.split("/")[0], p=float(key.split("/p")[1]), alpha=a, receivers=label,
                                 lnZ_hydro=float(np.log(wL.sum() / Zc)), median_lat_core=med(corep), median_lat_combined=med(comb), median_lat_alone=med(alone),
                                 shift_median_deg=med(comb) - med(corep), mass_north_33S_core=n33(corep), mass_north_33S_combined=n33(comb), mass_north_33S_alone=n33(alone),
                                 shift_mass_north_33S=n33(comb) - n33(corep), KL_core_vs_combined_nats=kl, bins_alone=int(sel.sum())))
    return pd.DataFrame(rows), dists


def families_and_holland(mx, norm):
    rows = []; hol = []
    for j, key in enumerate(KEYS):
        o, p = key.split("/")[0], float(key.split("/p")[1]); Z = mx["sum_w"][j].sum()
        for k, c in enumerate(FAM_CODES):
            w, w2, wL, wLi = mx["fam_w"][j, k], mx["fam_w2"][j, k], mx["fam_wL"][j, k], mx["fam_wLims"][j, k]
            wLA = mx["fam_wLA"][j, k] if STATS_ONLY else np.nan
            rows.append(dict(option=o, p=p, family=FAM_NAMES[c], share=float(w / Z) if Z > 0 else 0.0, ess=float(w * w / w2) if w2 > 0 else 0.0,
                             lnZ_hydro_imos=float(np.log(wL / w)) if w > 0 and wL > 0 else None, lnZ_hydro_ims_proxy=float(np.log(wLi / w)) if w > 0 and wLi > 0 else None,
                             lnZ_hydro_imos_ampweighted=float(np.log(wLA / w)) if (STATS_ONLY and w > 0 and wLA > 0) else None))
    for o in R.OPTIONS:
        z = {}
        for p in R.PS:
            j = KEYS.index(f"{o}/p{p:g}"); Z = mx["sum_w"][j].sum()
            z[p] = {a: dict(imos=mx[f"wLmarg_{ALPHA_TAGS[a]}"][j] / Z, ims=mx[f"wLmarg_ims_{ALPHA_TAGS[a]}"][j] / Z, amp=(mx[f"wLmarg_A_{ALPHA_TAGS[a]}"][j] / Z) if STATS_ONLY else np.nan,
                            nd_imos=mx[f"wPnd_{ALPHA_TAGS[a]}"][j].sum(0)[:NG].mean() / Z) for a in R.ALPHAS}
        for a in R.ALPHAS:
            hol.append(dict(option=o, alpha=a, lnBF_p1_vs_p0_imos=float(np.log(z[1.0][a]["imos"] / z[0.0][a]["imos"])), lnBF_p1_vs_p0_ims_proxy=float(np.log(z[1.0][a]["ims"] / z[0.0][a]["ims"])),
                            lnBF_p1_vs_p0_nondetection_only=float(np.log(z[1.0][a]["nd_imos"] / z[0.0][a]["nd_imos"])),
                            lnBF_p1_vs_p0_ampweighted=float(np.log(z[1.0][a]["amp"] / z[0.0][a]["amp"])) if STATS_ONLY else None,
                            lnBF_p05_vs_p0_imos=float(np.log(z[0.5][a]["imos"] / z[0.0][a]["imos"])), lnZ_p0=float(np.log(z[0.0][a]["imos"])), lnZ_p1=float(np.log(z[1.0][a]["imos"]))))
    return pd.DataFrame(rows), pd.DataFrame(hol)


def concat_sub(sub, supp_sub):
    allp = sub + ([supp_sub] if supp_sub is not None else [])
    keys = [k for k in allp[0] if k != "W"]
    out = {k: np.concatenate([d[k] for d in allp]) for k in keys}; out["W"] = np.concatenate([d["W"] for d in allp], axis=1)
    return out


def source_hypothesis(M, S, lat, lon, t_imp, rng, label):
    """Fixed-source likelihood marginalised over eta: E and tau resampled from run J rows within +/-1 deg of lat (D0' p 0.5 weights)."""
    j = KEYS.index("D0/p0.5"); m = (np.abs(S["lat"] - lat) <= 1.0) & (S["W"][j] > 0)
    if m.sum() < 50: m = (np.abs(S["lat"] - lat) <= 3.0) & (S["W"][j] > 0)
    w = S["W"][j][m]; w = w / w.sum(); pick = rng.choice(np.where(m)[0], R.N_DRAWS_BF, p=w)
    E, tau = S["E"][pick], S["tau"][pick]; Lcal = rng.normal(0, R.CAL_L_SD_DB, R.N_DRAWS_BF)
    n = R.N_DRAWS_BF; PP = M.prep(np.full(n, t_imp), np.full(n, lat), np.full(n, lon), E, tau)
    out = dict(hypothesis=label, lat=lat, lon=lon, t_impact_utc=hms(t_imp), n_rows_for_E_tau=int(m.sum()))
    for a in R.ALPHAS:
        lg, pg, nsc, la_ = M.lnL_grid(PP, Lcal, a, R.RECEIVERS_GATED, amp=True); li, pi, nsci = M.lnL_grid(PP, Lcal, a, R.RECEIVERS_PROXY)
        out[f"L_imos_a{a:g}"] = float(np.exp(M.marg(lg)).mean()); out[f"L_ims_a{a:g}"] = float(np.exp(M.marg(lg + li)).mean()); out[f"L_imos_amp_a{a:g}"] = float(np.exp(M.marg(la_)).mean())
        out[f"Pnd_imos_marg_a{a:g}"] = float(np.exp(pg[:, :NG]).mean())
        if a == R.ALPHA_PRIMARY:
            out["scored_receivers"] = ",".join(rx for rx in R.RECEIVERS if PP["sc"][rx].any())
            out["L_imos_at_anchor"] = float(np.exp(M.fixed(lg, "eta2.1e-4")).mean()); out["L_imos_at_1e-3"] = float(np.exp(M.fixed(lg, "eta1e-3")).mean())
    return out


def hms(ts):
    s = ts - R.T0; return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"


def conditionals(M, S, Zrun, out_dir):
    rng = np.random.default_rng([R.SEED, R.BLOCK, 77]); rows = []
    tp = json.load(open(R.RD / "tl_grid_run_j" / "table_points.json")); arc = {v["lat"]: v["lon"] for k, v in tp.items() if v["offset_nm"] == 0}
    d_H01W = lambda la, lo: M.distances_km(np.array([la]), np.array([lo]))["H01W"][0]
    j = KEYS.index("D0/p0.5")
    def prior_mass(lat, lon, km=100.0):
        from pyproj import Geod
        _, _, d = Geod(ellps="WGS84").inv(S["lon"], S["lat"], np.full_like(S["lon"], lon), np.full_like(S["lat"], lat)); w = S["W"][j]
        return float(w[d / 1000 <= km].sum() / w.sum())
    for name, t_h in R.KADRI_TIMES.items():
        la, lo = R.KADRI_LOCUS; t_imp = t_h - d_H01W(la, lo) / R.C_SOFAR
        r = source_hypothesis(M, S, la, lo, t_imp, rng, f"Kadri 306.18 deg row, {name}, locus 25.8 S 101.4 E")
        r.update(prior_D0_mass_within_100km=prior_mass(la, lo), implied_impact_vs_0019=("after" if t_imp > R.T_0019_LOGON else "BEFORE 00:19:29"),
                 note="H01W factor CIRCULAR (hypothesis built from the 00:52:04 candidate); IMOS term is the non-circular test"); rows.append(r)
    for ev, (la, lo, t_imp) in R.ROYER.items():
        r = source_hypothesis(M, S, la, lo, t_imp, rng, f"Royer OHASISBIO event {ev} as source"); r.update(prior_D0_mass_within_100km=prior_mass(la, lo),
            implied_impact_vs_0019="after" if t_imp > R.T_0019_LOGON else "BEFORE 00:19:29", note="origin and time from Royer (digitised report)"); rows.append(r)
    la0, dk = R.H01W_CLOSEST_ARC; lo0 = arc[la0]
    for name, (a_, b_) in R.POSTER_BOXES.items():
        t_imp = 0.5 * (a_ + b_) - dk / R.C_SOFAR
        r = source_hypothesis(M, S, la0, lo0, t_imp, rng, f"{name}: 'source before 00:19:29 or off the arc' row, nearest arc locus 28.0 S")
        r.update(prior_D0_mass_within_100km=prior_mass(la0, lo0), implied_impact_vs_0019="after" if t_imp > R.T_0019_LOGON else "BEFORE 00:19:29 (prior 0 under the 00:19 log-on; what-if only)",
                 note="declared row; not a run J hypothesis"); rows.append(r)
    df = pd.DataFrame(rows)
    for a in R.ALPHAS:
        df[f"lnBF_imos_a{a:g}"] = np.log(df[f"L_imos_a{a:g}"] / Zrun[a]["imos"]); df[f"lnBF_ims_proxy_a{a:g}"] = np.log(df[f"L_ims_a{a:g}"] / Zrun[a]["ims"])
        if "amp" in Zrun[a]: df[f"lnBF_imos_amp_a{a:g}"] = np.log(df[f"L_imos_amp_a{a:g}"] / Zrun[a]["amp"])
    df["lnZ_runJ_imos_a0.05"] = np.log(Zrun[R.ALPHA_PRIMARY]["imos"]); df["lnZ_runJ_ims_a0.05"] = np.log(Zrun[R.ALPHA_PRIMARY]["ims"])
    df.to_csv(Path(out_dir) / "bayes_factors_conditionals.csv", index=False)
    return df


def coincidence(M, S, out_dir):
    tp = json.load(open(R.RD / "tl_grid_run_j" / "table_points.json")); pts = sorted([(v["lat"], v["lon"]) for v in tp.values() if v["offset_nm"] == 0])
    la = np.array([p[0] for p in pts]); lo = np.array([p[1] for p in pts]); d = M.distances_km(la, lo)
    lag = (d["H08S"] - d["H01W"]) / R.C_SOFAR; target = R.PAIR["lag_s"]
    # locus: latitude where the lag equals the observed lag (the lag is monotone enough along the arc for a root; take all crossings)
    cross = np.where(np.diff(np.sign(lag - target)) != 0)[0]; loci = [float(np.interp(target, [lag[i], lag[i + 1]], [la[i], la[i + 1]])) if lag[i + 1] != lag[i] else la[i] for i in cross]
    rows = []
    j = KEYS.index("D0/p0.5")
    for L_ in loci:
        lon_ = float(np.interp(L_, la, lo)); dd = M.distances_km(np.array([L_]), np.array([lon_])); t_imp = R.PAIR["H01W"] - dd["H01W"][0] / R.C_SOFAR
        m = (np.abs(S["lat"] - L_) <= 1.0) & (S["W"][j] > 0); w = S["W"][j][m]
        if m.sum() < 20: continue
        Emed = float(np.interp(0.5, np.cumsum(w[np.argsort(S["E"][m])]) / w.sum(), np.sort(S["E"][m]))); tmed = float(np.interp(0.5, np.cumsum(w[np.argsort(S["tau"][m])]) / w.sum(), np.sort(S["tau"][m])))
        base, ti = M.level_base(np.array([L_]), np.array([Emed]), np.array([tmed]))
        res = dict(locus_lat=L_, locus_lon=lon_, implied_impact_utc=hms(t_imp), implied_impact_vs_0019="after" if t_imp > R.T_0019_LOGON else "BEFORE 00:19:29",
                   E_median_GJ=Emed / 1e9, tau_median_s=tmed, prior_D0_mass_within_1deg=float(w.sum() / S["W"][j].sum()))
        for a in R.ALPHAS:
            lg = np.log10(np.logspace(-6, 0, 601)); pdp = {}
            for rx in R.RECEIVERS_PROXY:
                snr = base[rx][0] + 10 * lg[None, :]; pdp[rx] = M.pd(rx, a, snr, ti)[0]
            both = pdp["H01W"] * pdp["H08S"]
            for thr in (0.5, 0.05):
                k = np.argmax(both >= thr) if (both >= thr).any() else None
                res[f"eta_both_pd_{thr}_a{a:g}"] = float(10 ** lg[k]) if k is not None else None
            for rx in R.RECEIVERS_PROXY:
                res[f"pd_{rx}_at_anchor_a{a:g}"] = float(np.interp(np.log10(R.ETA_ANCHOR), lg, pdp[rx]))
            res[f"pd_both_at_anchor_a{a:g}"] = float(np.interp(np.log10(R.ETA_ANCHOR), lg, both))
        rows.append(res)
    df = pd.DataFrame(rows); df.to_csv(Path(out_dir) / "coincidence_locus.csv", index=False)
    summ = dict(pair="H01W 00:52:04 (M1b p 0.043, text time box) x H08S 01:12:49 (M1b p 0.039, p_B 0.30; raw panel, airgun-dominated: G-S9 variant)",
                lag_s=target, n_pairs_obs=R.PAIR["n_obs"], expected_by_chance=R.PAIR["expected"], p_perm=R.PAIR["p_perm"], n_pair_tests=R.PAIR["n_pair_tests"],
                expected_min_p_over_tests=1 - (1 - R.PAIR["p_perm"]) ** R.PAIR["n_pair_tests"], eta_needed_searches=dict(H01W=0.026, H08S=1.5), loci=rows)
    json.dump(summ, open(Path(out_dir) / "coincidence_summary.json", "w"), indent=1)
    return summ


def main(cols_dir, out_dir):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    acc, supp, share, sub, supp_sub, meta = load_parts(cols_dir)
    mx, norm = mix(acc, supp, share)
    ul = upper_limits(mx, norm); ul.to_csv(out / "upper_limits.csv", index=False)
    ev, dists = evidence_three_ways(mx); ev.to_csv(out / "evidence_three_ways.csv", index=False)
    np.savez_compressed(out / "latitude_distributions.npz", **{f"{k[0]}|a{k[1]:g}|{'amp' if k[2] == 'A' else ('ims' if k[2] else 'imos')}|{n}": v for k, d in dists.items() for n, v in d.items()})
    nd = {"band_mid": (R.LAT_BAND_EDGES_1DEG[:-1] + 0.5).tolist()}
    for j, key in enumerate(KEYS):
        P = mx[f"wPnd_{ALPHA_TAGS[R.ALPHA_PRIMARY]}"][j][1:22, :NG].mean(1); w = mx["sum_w"][j][1:22]
        with np.errstate(invalid="ignore", divide="ignore"):
            v = np.where(w > 1e-9 * w.sum(), P / w, 0.0)
        nd[key] = (v / v.sum()).tolist() if v.sum() > 0 else v.tolist()
    json.dump(nd, open(out / "nd_alone_1deg.json", "w"), indent=0)
    # non-detection-only combined distribution at 1-degree resolution (removes the amplitude-blind matches, gap G11-1)
    e1 = R.LAT_BAND_EDGES_1DEG; rows_nd = []
    for j, key in enumerate(KEYS):
        for ims in (False, True):
            wP = mx[f"wPnd{'_ims' if ims else ''}_{ALPHA_TAGS[R.ALPHA_PRIMARY]}"][j][1:22, :NG].mean(1); w = mx["sum_w"][j][1:22]
            core = w / w.sum(); comb = wP / wP.sum()
            med = lambda d: float(np.interp(0.5, np.cumsum(d), e1[1:])); n33 = lambda d: float(d[e1[:-1] >= -33].sum())
            with np.errstate(divide="ignore", invalid="ignore"):
                kl = float(np.nansum(np.where(core > 0, core * np.log(core / np.where(comb > 0, comb, np.nan)), 0.0)))
            rows_nd.append(dict(option=key.split("/")[0], p=float(key.split("/p")[1]), receivers="IMS proxy + IMOS" if ims else "IMOS gated", lnZ_nd=float(np.log(wP.sum() / w.sum())),
                                median_lat_core_1deg=med(core), median_lat_combined_nd=med(comb), shift_median_deg=med(comb) - med(core),
                                mass_north_33S_core=n33(core), mass_north_33S_combined_nd=n33(comb), KL_nats=kl))
    pd.DataFrame(rows_nd).to_csv(out / "evidence_nd_only_1deg.csv", index=False)
    fam, hol = families_and_holland(mx, norm); fam.to_csv(out / "families.csv", index=False); hol.to_csv(out / "holland_p1_vs_p0.csv", index=False)
    S = concat_sub(sub, supp_sub); M = Machinery(imos_ramgrid=STATS_ONLY)
    j = KEYS.index("D0/p0.5"); Z = mx["sum_w"][j].sum()
    Zrun = {a: dict(imos=mx[f"wLmarg_{ALPHA_TAGS[a]}"][j] / Z, ims=mx[f"wLmarg_ims_{ALPHA_TAGS[a]}"][j] / Z, **({"amp": mx[f"wLmarg_A_{ALPHA_TAGS[a]}"][j] / Z} if STATS_ONLY else {})) for a in R.ALPHAS}
    bf = conditionals(M, S, Zrun, out); co = coincidence(M, S, out)
    # ESS check: streamed vs subsample (D0' p 0.5), and the eta-grid posterior for the headline
    ess_stream = {k: float(mx["sum_w"][i].sum() ** 2 / mx["sum_w2"][i].sum()) for i, k in enumerate(KEYS)}
    ess_sub = {k: float(S["W"][i].sum() ** 2 / (S["W"][i] ** 2).sum()) for i, k in enumerate(KEYS)}
    hist = {k: mx["lnL_hist"][i].tolist() for i, k in enumerate(KEYS)}
    summary = dict(prereg="90d7181" + (" + A4 e13a32e (RAM-grid IMOS TL, statistics only)" if STATS_ONLY else ""), imos_tl="imos_tl_ram_arc.csv" if STATS_ONLY else "imos_tl_ramcorr_arc.csv", ramgrid_covered_share=M.ramgrid_covered_share, seeds=meta, supplement_share={o: share[o]["supplement"] / share[o]["total"] for o in R.OPTIONS} if share else None,
                   ess_streamed=ess_stream, ess_subsample=ess_sub, n_subsample=int(len(S["lat"])), Zrun_D0_p05={f"a{a:g}": v for a, v in Zrun.items()},
                   lnL_hist_edges=mx["lnL_hist_edges"].tolist(), lnL_hist_D0_p05=hist["D0/p0.5"], norm=norm, pd_missing=M.pd_missing,
                   candidates={f"{rx}|{a}": M.cands[(rx, a)].to_dict("records") for rx in R.RECEIVERS for a in R.ALPHAS},
                   scored_windows={rx: int(len(v)) for rx, v in M.windows.items()})
    json.dump(summary, open(out / "summary.json", "w"), indent=1, default=float)
    # merged subsample not saved (1.1 GB duplicate of the per-seed files; disk cap)
    print(json.dumps(dict(ess=ess_stream, Z=Zrun[R.ALPHA_PRIMARY]), indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
