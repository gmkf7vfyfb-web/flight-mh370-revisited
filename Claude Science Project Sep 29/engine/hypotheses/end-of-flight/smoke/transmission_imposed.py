"""Order (b) item 2, 15 Oct 2026: D0 redefined as "00:19 values held out, transmission imposed".

Every treatment requires the aircraft to be airborne at 00:19:37.443 (the R1200 acknowledge, the last burst it sent) and
carries the adopted survival factor (no in-flight breakup before that burst, 1 - latent:inflight_p_breakup_to_m0019b).
The two-factor table (option_table_0019.py) already imposes both through its log-on constraint, so its D0 cells are
unchanged; what changes is every product that used the RAW stored weights as the "held out" baseline (the loud-tail
convention, the item 7 sweep, the item 8 distributions, family-share summaries).

Per stratum and seed, from the compact impacts and the tau90_v1 sidecar, this writes the inputs for:
  A. old raw D0 against D0' (shares, latitude, effective impacts, share on the sea before 00:19:37);
  B. loudest-decile shares, threshold = 90th percentile of peak radiated power under D0' (the feasible set);
  C. the dive-probability sweep (item 7) on the feasible set.
Usage: python transmission_imposed.py EOF_ROOT CORE_ROOT OUT_JSON
"""
import sys, json, csv, pathlib
import numpy as np
from scipy.special import gammaln
from compact_impacts import load
from displacement_hist import derived_logliks, constraint_log_factor, SATCOM_CSV, T_M0019B
from option_table_0019 import d5_loglik, W_S

STRATA = {"next-i-waypoints": 0.9982, "next-i-free": 0.0011, "next-i-repro-radar": 0.0004, "next-i-descent-climb": 0.0002}
DS = ["D0", "D1", "D2", "D3", "D4", "D5"]
FAMS = {1: "A1", 2: "A2", 3: "B controlled", 6: "B uncontrolled"}
PGRID = [0.0, 0.25, 0.5, 0.75, 1.0]


def seed_rows(sd, handoff):
    meta, g = load(sd); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    obs = {r["epoch_id"]: r for r in csv.DictReader(open(SATCOM_CSV))}
    w = g("weight"); lw = np.log(w) - np.log(w.sum())
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
    der = derived_logliks(meta, g, present)
    V = np.asarray(np.load(handoff, mmap_mode="r")[:, 9])[g("parent").astype(np.int64)]
    col = lambda k: np.where(np.isfinite(g("loglik:" + k)), g("loglik:" + k), -np.inf)
    D = {"D0": np.zeros(len(w)), "D1": der["r600-bto"], "D2": col("r600/no-offset"), "D3": col("both/no-offset"),
         "D4": col("both/startup-offset"), "D5": d5_loglik(g, V, obs)}
    t = g("unix_s")
    alive = np.where(t > T_M0019B, 0.0, -np.inf)
    with np.errstate(divide="ignore", invalid="ignore"):
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
        lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    c1 = lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered")
    c2 = -np.log(W_S) + constraint_log_factor(g, logon, "other", "silent")
    tot = np.logaddexp(np.log(0.75) + c1, np.log(0.25) + c2)
    z = np.load(pathlib.Path(sd) / "tau90_v1.npz")
    assert z["peak_rate_w"].shape[0] == len(w)
    rows = {"raw": lw.astype(np.float32)}
    for d in DS:
        rows["data:" + d] = (lw + alive + surv + D[d]).astype(np.float32)   # data treatment, transmission imposed
        rows["total:" + d] = (lw + surv + D[d] + tot).astype(np.float32)    # two-factor total, q = 1/3, C2 silent
    rows.update(t_rel=(t - T_M0019B).astype(np.float32), lat=g("latitude_deg").astype(np.float32),
                fpa=g("flight_path_angle_deg").astype(np.float32), peak=z["peak_rate_w"].astype(np.float32),
                energy=z["energy_transferred_j"].astype(np.float32), fam=g("family4_code").astype(np.int8),
                drawn=(g("latent:pushover_drawn") == 1), surf=(g("latent:pushover_to_surface") == 1))
    return rows


def wq(v, w, qs):
    o = np.argsort(v, kind="stable"); c = np.cumsum(w[o]); c /= c[-1]
    return [float(v[o][min(int(np.searchsorted(c, q)), len(c) - 1)]) for q in qs]


def main(eof_root, core_root, outp):
    parts = []
    for st, P in STRATA.items():
        seeds = sorted(p for p in (pathlib.Path(eof_root) / st).glob("seed-*") if p.is_dir())
        K = len(seeds)
        for sd in seeds:
            r = seed_rows(sd, pathlib.Path(core_root) / st / "bto-bfo" / sd.name / "handoff-m0011" / "handoff.npy")
            c = np.float32(np.log(P / K))
            for k in list(r):
                if k == "raw" or k.startswith(("data:", "total:")):
                    r[k] = r[k] + c
            parts.append(r); print(f"  {st} {sd.name} rows {len(r['lat'])}", flush=True)
    A = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    del parts

    def W(key, factor=None):
        a = A[key].astype(np.float64); s = np.max(a[np.isfinite(a)])
        w = np.exp(a - s); w[~np.isfinite(w)] = 0.0
        if factor is not None:
            w = w * factor
        return w, float(np.log(w.sum()) + s)

    def ess(w):
        return float(w.sum() ** 2 / np.square(w).sum()) if w.sum() > 0 else 0.0

    def summary(w):
        tot = w.sum()
        return {"eff_impacts": ess(w), "families": {n: float(w[A["fam"] == c].sum() / tot) for c, n in FAMS.items()},
                "latitude_q05_q50_q95": wq(A["lat"], w, [0.05, 0.5, 0.95]),
                "band_lt10": float(w[A["fpa"] < 10].sum() / tot), "band_10_45": float(w[(A["fpa"] >= 10) & (A["fpa"] <= 45)].sum() / tot),
                "band_gt45": float(w[A["fpa"] > 45].sum() / tot),
                "energy_GJ_q05_q50_q95": [x / 1e9 for x in wq(A["energy"], w, [0.05, 0.5, 0.95])]}

    res = {"definition": "D0' = 00:19 values held out, transmission imposed: airborne at 00:19:37.443 and survival factor applied",
           "n_impacts": int(len(A["lat"]))}
    w_raw, _ = W("raw")
    res["old_raw_D0"] = summary(w_raw)
    res["old_raw_D0"]["share_on_sea_before_001937"] = float(w_raw[A["t_rel"] <= 0].sum() / w_raw.sum())
    w0, lz0 = W("data:D0")
    res["D0_transmission_imposed"] = summary(w0); res["D0_transmission_imposed"]["ln_mass"] = lz0
    thr = wq(A["peak"], w0, [0.90])[0]
    res["loud_threshold_W_on_feasible_set"] = thr
    loud = A["peak"] > thr
    res["loudness"] = {}
    for kind in ("data", "total"):
        for d in DS:
            w, lz = W(f"{kind}:{d}")
            res["loudness"][f"{kind}:{d}"] = {"loud_decile_share": float(w[loud].sum() / w.sum()), "ln_mass": lz,
                                             "eff_impacts": ess(w), "eff_impacts_loud": ess(w * loud)}
    res["loudness"]["old_raw_D0_against_feasible_threshold"] = float(w_raw[loud].sum() / w_raw.sum())
    res["sweep_p"] = []
    for d in ("D0", "D2", "D4"):
        for kind in ("data",):
            for p in PGRID:
                f = np.ones(len(A["lat"]))
                f[A["drawn"] & A["surf"]] = 2 * p; f[A["drawn"] & ~A["surf"]] = 2 * (1 - p)
                w, lz = W(f"{kind}:{d}", f)
                s = summary(w); s.update(option=d, kind=kind, p=p, ln_mass=lz, loud_decile_share=float(w[loud].sum() / w.sum()))
                res["sweep_p"].append(s)
                print(f"  sweep {d} p={p:.2f} band10-45 {s['band_10_45']:.4f} loud {s['loud_decile_share']:.4f} ESS {s['eff_impacts']:,.0f}", flush=True)
    json.dump(res, open(outp, "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("old_raw_D0", "D0_transmission_imposed")}, indent=1))
    print("loud:", {k: round(v["loud_decile_share"], 4) for k, v in res["loudness"].items() if isinstance(v, dict)})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
