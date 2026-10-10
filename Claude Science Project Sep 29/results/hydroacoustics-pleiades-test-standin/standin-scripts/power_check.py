"""Power check for the hydroacoustic test of the Pleiades hypothesis (pre-registration section 6). Stand-in, not
module code. Uses lhyd.Model (pre-registered) for every per-row quantity; this file only (a) splits the station term
of lhyd.Model.station_terms into its per-candidate parts so synthetic event lists can be scored quickly, (b) draws the
synthetic data, and (c) computes arrival-window overlaps. Part (a) is checked against station_terms on the real event
lists (max |d ln L| must be < 1e-9).

Usage: python power_check.py <module_dir> <imos_events.json> <kadri.csv> <sources.npz> <out_dir>
"""
import json, pathlib, sys, time
import numpy as np
import lhyd

import os
N_SYN, K_REP, SEED = int(os.environ.get("N_SYN", 2000)), 8, 20261010
SCEN = ["A", "A-IMOS", "B", "C"]
DAY_LIMIT = (0.0, 4 * 3600.0)      # scenario B coverage restricted to 00:00-04:00 UTC (no arrival lies outside)


def columns(src):
    c = {n: i for i, n in enumerate(src["state_columns"])}
    S = src["state"]
    return S[:, c["unix_s"]], S[:, c["latitude_deg"]], S[:, c["longitude_deg"]], S[:, c["kinetic_energy_j"]]


def parts(m, t_imp, lat, lon, E, rng, scenario):
    """Per station: q, t_arr, sd_t, baz (or None), lam, coverage segments, background box. Mirrors station_terms."""
    n = len(lat); nu = m.nuisance(rng, n); t0 = t_imp - lhyd.DAY0_UNIX; C = nu["c_site"] + nu["c_rcv"]; out = {}
    base = "B" if scenario == "B" else ("C" if scenario == "C" else "A")
    for lg in m.B.LOGGERS:
        _, d = m.geometry(lat, lon, lg); t_arr = t0 + d / lhyd.C_MEAN
        sd = np.sqrt(lhyd.PICK_S ** 2 + (d * lhyd.C_SD / lhyd.C_MEAN ** 2) ** 2)
        segs = m.imos_recorded[lg] if base == "B" else m.imos_scored[lg]
        q = m._cov(t_arr, segs) * m._pd(m._snr0(lat, E, nu, m.tl_imos[lg], lg) + C, m.B.TARGET[lg])
        if base == "B":
            segs = np.array([[max(a, DAY_LIMIT[0]), min(b, DAY_LIMIT[1])] for a, b in segs if b > DAY_LIMIT[0] and a < DAY_LIMIT[1]])
        out[lg] = dict(q=q, t=t_arr, sd=sd, baz=None, lam=lhyd.ALPHA / lhyd.WIN_S, segs=segs, ev=m.imos_events[lg])
    Cs = nu["c_site"] + nu["c_ims"]
    snr_ims = {s: m._snr0(lat, E, nu, m.tl_ims[s], "3376") + Cs + lhyd.TRIAD_GAIN_DB for s in ("H01W", "H08S")}
    for stn in ("H01W", "H08S"):
        if stn == "H08S" and base != "C":
            continue
        baz, d = m.geometry(lat, lon, stn); t_arr = t0 + d / lhyd.C_MEAN
        sd = np.sqrt(lhyd.PICK_S ** 2 + (d * lhyd.C_SD / lhyd.C_MEAN ** 2) ** 2)
        pdv = m._pd(snr_ims[stn], "3274")
        if base == "C":
            lo, hi = lhyd.RAW_REQ[stn]; lam = lhyd.ALPHA / lhyd.WIN_S / 360.0; box = (lo, hi, 0.0, 360.0); ev = np.zeros((0, 2))
        else:
            lo, hi = lhyd.KADRI_SPAN; lam = lhyd.KADRI_LAMBDA; box = (38 * 60 + 29.0, 38 * 60 + 29.0 + 998.0, 234.67, 343.16); ev = m.kadri
        q = ((t_arr >= lo) & (t_arr <= hi)) * pdv
        out[stn] = dict(q=q, t=t_arr, sd=sd, baz=baz, lam=lam, segs=np.array([[lo, hi]]), box=box, ev=ev)
    if scenario == "A-IMOS":
        out.pop("H01W", None)
    return out


def lnL(m, P, events):
    tot = 0.0
    for s, p in P.items():
        et, eb = events[s]
        tot = tot + np.log(m._mix(p["q"], p["t"], p["sd"], et, p["lam"], p["baz"], eb if p["baz"] is not None else None))
    return tot


def draw_events(rng, truth, P):
    ev = {}
    for s, p in P.items():
        tq = truth[s]
        segs = p["segs"]; L = segs[:, 1] - segs[:, 0]
        if p["baz"] is None:
            nb = rng.poisson(p["lam"] * L.sum())
            k = rng.choice(len(L), nb, p=L / L.sum()) if nb else np.zeros(0, int)
            t = segs[k, 0] + rng.uniform(0, 1, nb) * L[k]; b = np.zeros(nb)
        else:
            t0, t1, b0, b1 = p["box"]; nb = rng.poisson(p["lam"] * (t1 - t0) * (b1 - b0))
            t = rng.uniform(t0, t1, nb); b = rng.uniform(b0, b1, nb)
        if rng.uniform() < tq["q"]:
            t = np.append(t, tq["t"] + rng.normal(0, tq["sd"]))
            if p["baz"] is not None:
                s3 = lhyd.SD_BEAR / np.sqrt(lhyd.NU_T / (lhyd.NU_T - 2))
                b = np.append(b, (tq["baz"] + s3 * rng.standard_t(lhyd.NU_T)) % 360.0)
            else:
                b = np.append(b, 0.0)
        ev[s] = (t, b)
    return ev


def main():
    mod, evj, kd, srcp, outd = sys.argv[1:6]
    out = pathlib.Path(outd); out.mkdir(parents=True, exist_ok=True)
    m = lhyd.Model(mod, evj, kd)
    src = np.load(srcp)
    t_imp, lat, lon, E = columns(src)
    n = len(lat); res = {"source_package": srcp, "n_rows": n, "option": str(src["option_name"]),
                         "ess": {k: float(src[k]) for k in ("ess_w_flight", "ess_w_H", "ess_w_flight_fixed", "ess_w_H_fixed")},
                         "not_computed": int(src["not_computed"].sum())}
    # ---- check: parts() + lnL() reproduces station_terms() on the real events ----
    for sc in ("A", "B"):
        st = m.station_terms(t_imp, lat, lon, E, np.random.default_rng(SEED), sc)["total"]
        P = parts(m, t_imp, lat, lon, E, np.random.default_rng(SEED), sc)
        mine = lnL(m, P, {s: (p["ev"][:, 0], p["ev"][:, 1]) if p["baz"] is not None else (p["ev"], None) for s, p in P.items()})
        res[f"check_max_abs_dlnL_{sc}"] = float(np.max(np.abs(mine - st)))
        assert res[f"check_max_abs_dlnL_{sc}"] < 1e-9, res
    # ---- candidates: K_REP nuisance replicas per source row ----
    rep = np.repeat(np.arange(n), K_REP)
    W = {}
    for lab, wk in (("reweighted", ("w_flight", "w_H")), ("fixed", ("w_flight_fixed", "w_H_fixed"))):
        W[lab] = (np.asarray(src[wk[0]], float)[rep], np.asarray(src[wk[1]], float)[rep])
    # ---- arrival windows (SOFAR), per station, H vs without H (re-weighted and fixed) ----
    pr = m.predict(t_imp, lat, lon, E, np.random.default_rng(SEED + 1))
    bins = np.arange(0, 4 * 3600 + 60, 60.0); win = {}
    for s in ("H01W", "H08S", "H08N", "3376", "3274"):
        rec = {}
        for lab in ("reweighted", "fixed"):
            w0, wH = np.asarray(src["w_flight" if lab == "reweighted" else "w_flight_fixed"], float), np.asarray(src["w_H" if lab == "reweighted" else "w_H_fixed"], float)
            h0, _ = np.histogram(pr[s]["t"], bins, weights=w0); hH, _ = np.histogram(pr[s]["t"], bins, weights=wH)
            h0 /= h0.sum(); hH /= hH.sum()
            def q(w, qq):
                o = np.argsort(pr[s]["t"]); c = np.cumsum(w[o]); c /= c[-1]
                return [float(pr[s]["t"][o][np.searchsorted(c, x)]) for x in qq]
            rec[lab] = dict(ovl=float(np.minimum(h0, hH).sum()), q_flight=q(w0, (0.01, 0.5, 0.99)), q_H=q(wH, (0.01, 0.5, 0.99)),
                            hist_flight=h0.tolist(), hist_H=hH.tolist(),
                            mean_pd_flight=float(np.average(pr[s]["pd"], weights=w0)) if "pd" in pr[s] else None,
                            mean_pd_H=float(np.average(pr[s]["pd"], weights=wH)) if "pd" in pr[s] else None,
                            baz_q_flight=[float(np.quantile(pr[s]["baz"], x)) for x in (0.05, 0.5, 0.95)])
        win[s] = rec
    res["windows"] = win; res["bins_s"] = bins.tolist()
    # ---- synthetic ln R ----
    syn = {}
    for sc in SCEN:
        t = time.time()
        P = parts(m, t_imp[rep], lat[rep], lon[rep], E[rep], np.random.default_rng([SEED, 7, SCEN.index(sc)]), sc)
        rng = np.random.default_rng([SEED, 11, SCEN.index(sc)])
        rec = {"H": {}, "noH": {}}
        for lab, (w0, wH) in W.items():
            for hyp in ("H", "noH"):
                key = ("w_H" if hyp == "H" else "w_flight") + ("" if lab == "reweighted" else "_fixed")
                wt = np.asarray(src[key], float); wt = wt / wt.sum()
                v, ndet, nsig = [], [], []
                for _ in range(N_SYN):
                    j = rng.choice(n, p=wt)
                    Tj = parts(m, t_imp[[j]], lat[[j]], lon[[j]], E[[j]], rng, sc)
                    truth = {s: {k: p[k][0] for k in ("q", "t", "sd")} | {"baz": None if p["baz"] is None else p["baz"][0]} for s, p in Tj.items()}
                    ev = draw_events(rng, truth, P)
                    ll = lnL(m, P, ev); keep = rep != j
                    Lr = np.exp(ll[keep] - ll[keep].max())
                    a = np.sum(wH[keep] * Lr) / np.sum(wH[keep]); b = np.sum(w0[keep] * Lr) / np.sum(w0[keep])
                    v.append(float(np.log(a) - np.log(b))); ndet.append(sum(len(ev[s][0]) for s in ev))
                    nsig.append(float(1 - np.prod([1 - truth[s]["q"] for s in truth])))
                v = np.array(v)
                rec[hyp][lab] = dict(mean=float(v.mean()), sd=float(v.std()), mc_se_mean=float(v.std() / np.sqrt(len(v))),
                                     q=[float(np.quantile(v, x)) for x in (0.025, 0.5, 0.975)],
                                     p_abs_ge_0p5=float(np.mean(np.abs(v) >= 0.5)), p_abs_ge_1=float(np.mean(np.abs(v) >= 1)),
                                     p_abs_ge_2p3=float(np.mean(np.abs(v) >= 2.3)), mean_events=float(np.mean(ndet)),
                                     mean_p_any_signal=float(np.mean(nsig)), values=v.tolist())
        syn[sc] = rec
        print(sc, f"{time.time() - t:.0f} s", {h: (round(rec[h]['reweighted']['mean'], 4), round(rec[h]['reweighted']['p_abs_ge_0p5'], 4)) for h in ("H", "noH")}, flush=True)
    res["synthetic"] = syn
    A = syn["A"]; ovl_ok = all(win[s]["reweighted"]["ovl"] >= 0.5 for s in win)
    near0 = all(abs(A[h]["reweighted"]["mean"]) < 0.1 and A[h]["reweighted"]["p_abs_ge_0p5"] < 0.05 for h in ("H", "noH"))
    res["stop_rule"] = dict(ovl_all_ge_0p5=ovl_ok, expected_lnR_near_zero=near0, not_informative=bool(ovl_ok and near0))
    (out / "power_check.json").write_text(json.dumps(res))
    print(json.dumps(res["stop_rule"]), res["ess"], res["not_computed"], res["check_max_abs_dlnL_A"], res["check_max_abs_dlnL_B"])


if __name__ == "__main__":
    main()
