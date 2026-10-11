"""Run H routes carried to impact (architecture 21:30Z 11 Oct): per route (conditional on the route) and pooled, per 00:19
option, constraint `unpowered`, PRIMARY with the survival factor (sensitivity without): ln Z, effective impacts (and parents),
P(A1/A2/B), P(in-flight breakup), impact latitude q05 / q50 / q95 (the 90% region), and core's own 00:19 latitude per route.
Seeds pooled by their evidence (row mass w_i L_i / sum w over the seed / K). Route of a row = route_index.csv[parent].
Usage: python run_h_summary.py OUT_STRATUM_DIR CORE_RUN_H_DIR CORE_PER_ROUTE_CSV OUT_JSON
"""
import json, sys, pathlib, csv
import numpy as np
from scipy.special import logsumexp, gammaln
from compact_impacts import load, family_labels
from displacement_hist import derived_logliks, constraint_log_factor
from smoke_compare import CORE

NAMES = {43: "MEKAR-SAMAK-ISBIX", 19: "NILAM-SAMAK-ISBIX", 3: "NILAM-IGOGU-ISBIX", 11: "NILAM-ANOKO-ISBIX", 10: "NILAM-ANOKO-BULVA", 2: "NILAM-IGOGU-BULVA"}


def wq(x, p, qs=(0.05, 0.5, 0.95)):
    o = np.argsort(x); c = np.cumsum(p[o]); c /= c[-1]
    return [float(x[o][min(np.searchsorted(c, q), len(c) - 1)]) for q in qs]


def main(outdir, coredir, core_csv, outp):
    seeds = sorted(p for p in pathlib.Path(outdir).glob("seed-*") if p.is_dir()); K = len(seeds)
    rows = {}
    for sd in seeds:
        k = sd.name.split("-")[1]
        route = np.array([int(r["route_index"]) for r in csv.DictReader(open(pathlib.Path(coredir) / f"seed-{k}" / "route_index.csv"))])
        meta, g = load(sd); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
        w = g("weight"); lw = np.log(w) - np.log(w.sum()) - np.log(K); par = g("parent").astype(np.int64)
        present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]; der = derived_logliks(meta, g, present)
        lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
        with np.errstate(divide="ignore", invalid="ignore"):
            lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
        f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
        pb19 = np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1); pb = np.clip(g("latent:inflight_p_breakup"), 0, 1)
        for name, o, cause in CORE:
            base = der[o] if o in der else g("loglik:" + o)
            ll = np.where(np.isfinite(base), base, -np.inf) + (lfe if cause == "fuel-exhaustion" else 0.0) + constraint_log_factor(g, logon, cause, "unpowered")
            for ver, extra in (("primary", None), ("without survival factor", 0.0)):
                with np.errstate(divide="ignore"):
                    a = lw + ll + (np.log1p(-pb19) if extra is None else 0.0)
                R = rows.setdefault((name, ver), {"a": [], "lat": [], "f4": [], "route": [], "pb": [], "par": []})
                keep = np.isfinite(a)
                R["a"].append(a[keep]); R["lat"].append(g("latitude_deg")[keep]); R["f4"].append(f4[keep]); R["route"].append(route[par[keep]])
                R["pb"].append(pb[keep]); R["par"].append(par[keep] + 10_000_000 * int(k))
    core = {int(r["route"]): r for r in csv.DictReader(open(core_csv))}
    res = {"seeds": K, "options": {}}
    for (name, ver), R in rows.items():
        a = np.concatenate(R["a"]); lat = np.concatenate(R["lat"]); f4 = np.concatenate(R["f4"]); route = np.concatenate(R["route"]); pb = np.concatenate(R["pb"]); par = np.concatenate(R["par"])
        out = {}
        for rk in ["pooled"] + sorted(set(route.tolist()), key=lambda r: -np.exp(logsumexp(a[route == r]))):
            m = np.ones(len(a), bool) if rk == "pooled" else route == rk
            if not m.any():
                continue
            lz = float(logsumexp(a[m])); p = np.exp(a[m] - lz)
            _, inv = np.unique(par[m], return_inverse=True); P = np.bincount(inv, weights=p)
            d = {"ln_Z": lz, "eff_impacts": float(1 / (p ** 2).sum()), "eff_parents": float(1 / (P ** 2).sum()),
                 "P_family": {n: float(p[f4[m] == c].sum()) for c, n in ((1, "A1"), (2, "A2"), (3, "B"))},
                 "P_inflight_breakup": float((p * pb[m]).sum()), "latitude_q05_q50_q95": wq(lat[m], p)}
            if rk != "pooled":
                d["route_name"] = NAMES.get(rk, str(rk)); c = core.get(rk, {})
                d["core_0019_latitude_q05_q50_q95"] = [float(c[x]) if c.get(x) else None for x in ("lat0019_q05", "lat0019_med", "lat0019_q95")]
            out["pooled" if rk == "pooled" else str(rk)] = d
        if "pooled" in out:
            tot = out["pooled"]["ln_Z"]
            for kk, d in out.items():
                d["route_share_posterior"] = float(np.exp(d["ln_Z"] - tot))
        res["options"].setdefault(name, {})[ver] = out
    json.dump(res, open(outp, "w"), indent=1)
    for name, v in res["options"].items():
        for ver, out in v.items():
            for rk, d in out.items():
                print(f"{name:26s} {ver[:7]:7s} {rk:6s} {d.get('route_name',''):18s} share {d['route_share_posterior']:.3f} lnZ {d['ln_Z']:8.2f} ESS {d['eff_impacts']:9.0f} par {d['eff_parents']:7.0f} A1/A2/B " + "/".join(f"{x:.2f}" for x in d['P_family'].values()) + f" brk {d['P_inflight_breakup']:.2f} lat " + "/".join(f"{x:.2f}" for x in d['latitude_q05_q50_q95']) + (f" core0019 {d['core_0019_latitude_q05_q50_q95']}" if 'core_0019_latitude_q05_q50_q95' in d else ""))


if __name__ == "__main__":
    main(*sys.argv[1:5])
