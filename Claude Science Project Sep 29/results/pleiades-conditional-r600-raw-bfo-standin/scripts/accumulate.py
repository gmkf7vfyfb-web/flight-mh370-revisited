"""Stand-in (architecture, for Pléiades + searched areas), 10 Oct 2026: one streaming pass per stratum-seed over end of
flight's core (b) next-run impacts, accumulating everything the Pléiades-conditional note needs.

    python accumulate.py <stratum> <seed> <out.npz>

Inputs (read-only):
  impacts      mh370-exchange/end-of-flight/next-run/<stratum>/seed-<k>/impacts.npy (+ run.json)
  Pléiades     mh370-exchange/pleiades/hydro-test/next-run-b/<stratum>/seed-<k>/pleiades-lnL.npy (row-aligned; adopted
               by the module, results/pleiades/hydro-test/module-review.md)
  search       eval/<stratum>/seed-<k>/cov.npy: searched areas' own `mh370 evaluate` columns covered_fraction_<campaign>
               (Phase 2, Bluefin-21, OI 2018, OI 2025-26) from run.toml + the union of its two OI overrides.
Weights: end of flight's own functions (displacement_hist.derived_logliks, constraint_log_factor), arms
  raw  = r600/no-offset + alive (00:19 R600 BTO + Raw BFO), log-on cause other;
  bto  = r600-bto + alive (00:19 R600 BTO Only), log-on cause other.
Pléiades likelihood per impact: L = mean over the two ocean models of exp(lnL_both_<model>) (P + all four COSMO contacts,
  rating-5 equal weights); a model not computed counts as zero likelihood - the module's build_branch convention.
Search likelihood: P(no find) = rho + (1 - rho) prod_k (1 - q_k f_k c_k) (lib.rs, shared misses, point target); the
  variants are searched areas' report.py scenarios that are pure arithmetic on the covered fractions.
"""
import json
import sys
import zlib
from pathlib import Path

import numpy as np

WS = Path(__file__).resolve().parents[1]
ENGINE = WS / "repo" / "Claude Science Project Sep 29" / "engine"
sys.path.insert(0, str(ENGINE / "hypotheses" / "end-of-flight" / "smoke"))
import displacement_hist as dh  # noqa: E402

X = Path("/Users/pete/Downloads/mh370-exchange")
SURF = ENGINE / "runs" / "pleiades"
STEP = 0.05
OPTIONS = {"raw": "r600/no-offset", "bto": "r600-bto"}
RHOS = [0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]
VARIANTS = [f"rho{r:g}" for r in RHOS] + ["q0.90", "q0.98", "independent", "oi2018", "oi2018-0.952", "oi2025", "oi2018+2025"]
MAPPED = ("rho0.05", "oi2018+2025")
CAT = {"family": 24, "latent:profile_shape": 6, "latent:debris_class": 4, "latent:spiral_divergent": 3,
       "latent:onset_mechanism": 6, "latent:engines_thrusting_at_onset": 4, "latent:control_realised": 6, "latent:timed_out": 3}
CONT = {"latent:last_burst_latitude_deg": (-48.0, -18.0, 3000), "latitude_deg": (-48.0, -18.0, 3000),
        "t_impact_min": (0.0, 180.0, 3600), "t_takeover_min": (-30.0, 180.0, 4200),
        "latent:time_descending_s": (0.0, 7200.0, 1440), "latent:max_descent_rate_fpm": (0.0, 60000.0, 600),
        "arc_distance_nm": (-300.0, 300.0, 600)}
T0 = 1394236800.0  # 2014-03-08 00:00:00 UTC
K_DRAW = 80


def grid():
    m = {}
    for line in (SURF / "likelihood-surface.toml").read_text().splitlines():
        k, v = line.split(" = ", 1)
        m[k] = json.loads(v) if v.startswith("[") else (v.strip('"') if v.startswith('"') else float(v))
    elon = m["lon0"] - STEP / 2 + STEP * np.arange(int(m["nlon"]) + 1)
    elat = m["lat0"] - STEP / 2 + STEP * np.arange(int(m["nlat"]) + 1)
    return elat, elon


def search_likelihoods(c):
    c1, c2, c3, c4 = (c[:, i].astype(float) for i in range(4))
    m = lambda q1=0.945: (1 - q1 * c1) * (1 - 0.9 * c2)
    sh = lambda rho, mm: rho + (1 - rho) * mm
    out = {f"rho{r:g}": sh(r, m()) for r in RHOS}
    out["q0.90"], out["q0.98"] = sh(0.05, m(0.90)), sh(0.05, m(0.98))
    out["independent"] = (0.05 + 0.95 * (1 - 0.945 * c1)) * (0.05 + 0.95 * (1 - 0.9 * c2))
    out["oi2018"] = sh(0.05, m() * (1 - 0.9 * 0.889 * c3))
    out["oi2018-0.952"] = sh(0.05, m() * (1 - 0.9 * 0.952 * c3))
    out["oi2025"] = sh(0.05, m() * (1 - 0.9 * 0.7808 * c4))
    out["oi2018+2025"] = sh(0.05, m() * (1 - 0.9 * 0.889 * c3) * (1 - 0.9 * 0.7808 * c4))
    return out


def main(stratum, seed, out):
    sd = X / "end-of-flight" / "next-run" / stratum / f"seed-{seed}"
    meta = json.loads((sd / "run.json").read_text())
    cols = meta["impact_columns"]
    ci = {c: i for i, c in enumerate(cols)}
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    present = [c[len("loglik:"):] for c in cols if c.startswith("loglik:")]
    A = np.load(sd / "impacts.npy", mmap_mode="r")
    PL = np.load(X / "pleiades" / "hydro-test" / "next-run-b" / stratum / f"seed-{seed}" / "pleiades-lnL.npy", mmap_mode="r")
    C = np.load(WS / "eval" / stratum / f"seed-{seed}" / "cov.npy", mmap_mode="r")
    n = A.shape[0]
    assert PL.shape[0] == n and C.shape[0] == n, (A.shape, PL.shape, C.shape)
    elat, elon = grid()
    npar = int(np.nanmax(A[:, ci["parent"]])) + 1
    acc = {}

    def add(k, v):
        acc[k] = acc.get(k, 0) + v
    rng = np.random.default_rng([seed, zlib.crc32(stratum.encode())])
    draws = {}
    CH = 400_000
    for a in range(0, n, CH):
        b = min(n, a + CH)
        Z = np.asarray(A[a:b], float)
        g = lambda k: Z[:, ci[k]]
        pl = PL[a:b]
        assert np.array_equal(pl["row"], np.arange(a, b)) and np.array_equal(pl["parent"], g("parent").astype(np.int64))
        e = np.stack([np.exp(np.asarray(pl["lnL_both_glorys12"], float)), np.exp(np.asarray(pl["lnL_both_globcurrent"], float))])
        L = np.nan_to_num(e, nan=0.0).mean(axis=0)
        lat, lon = g("latitude_deg"), g("longitude_deg")
        ingrid = (lat >= elat[0]) & (lat < elat[-1]) & (lon >= elon[0]) & (lon < elon[-1])
        S = search_likelihoods(np.asarray(C[a:b]))
        der = dh.derived_logliks(meta, g, present)
        con = dh.constraint_log_factor(g, logon, "other", "alive")
        par = g("parent").astype(np.int64)
        derived_vals = {"t_impact_min": (g("unix_s") - T0) / 60.0, "t_takeover_min": (g("takeover_unix_s") - T0) / 60.0}
        for o, arm in OPTIONS.items():
            base = der[arm] if arm in der else g("loglik:" + arm)
            ll = np.where(np.isfinite(base), base, -np.inf) + con
            w = g("weight") * np.exp(ll)
            w = np.where(np.isfinite(w), w, 0.0)
            wH = w * L
            add(f"{o}:sum_w", w.sum()); add(f"{o}:sum_w2", (w ** 2).sum())
            add(f"{o}:sum_wH", wH.sum()); add(f"{o}:sum_wH2", (wH ** 2).sum())
            add(f"{o}:sum_w_ingrid", w[ingrid].sum())
            add(f"{o}:par_w", np.bincount(par, w, minlength=npar)); add(f"{o}:par_wH", np.bincount(par, wH, minlength=npar))
            add(f"{o}:h_pre", np.histogram2d(lat, lon, bins=[elat, elon], weights=w)[0])
            add(f"{o}:h_preH", np.histogram2d(lat, lon, bins=[elat, elon], weights=wH)[0])
            for v in VARIANTS:
                s = S[v]
                add(f"{o}:sum_w_s:{v}", (w * s).sum()); add(f"{o}:sum_wH_s:{v}", (wH * s).sum())
                if v in MAPPED:
                    add(f"{o}:h_post:{v}", np.histogram2d(lat, lon, bins=[elat, elon], weights=w * s)[0])
                    add(f"{o}:h_postH:{v}", np.histogram2d(lat, lon, bins=[elat, elon], weights=wH * s)[0])
                    add(f"{o}:sum_wH_s2:{v}", ((wH * s) ** 2).sum()); add(f"{o}:sum_w_s2:{v}", ((w * s) ** 2).sum())
            for k, m in CAT.items():
                x = g(k)
                xi = np.where(np.isfinite(x), np.clip(x, 0, m - 2), m - 1).astype(int)
                add(f"{o}:cat0:{k}", np.bincount(xi, w, minlength=m)); add(f"{o}:catH:{k}", np.bincount(xi, wH, minlength=m))
                add(f"{o}:cat0sq:{k}", np.bincount(xi, w ** 2, minlength=m)); add(f"{o}:catHsq:{k}", np.bincount(xi, wH ** 2, minlength=m))
            for k, (lo, hi, nb) in CONT.items():
                x = derived_vals[k] if k in derived_vals else g(k)
                ok = np.isfinite(x)
                add(f"{o}:cont0:{k}", np.histogram(np.clip(x[ok], lo, hi - 1e-9), nb, (lo, hi), weights=w[ok])[0])
                add(f"{o}:contH:{k}", np.histogram(np.clip(x[ok], lo, hi - 1e-9), nb, (lo, hi), weights=wH[ok])[0])
                add(f"{o}:nan0:{k}", w[~ok].sum()); add(f"{o}:nanH:{k}", wH[~ok].sum())
            # weighted reservoir draws without replacement (Efraimidis-Spirakis), for the trajectory map
            for tag, ww in (("0", w), ("H", wH)):
                pos = ww > 0
                if not pos.any():
                    continue
                key = np.full(len(ww), -np.inf)
                key[pos] = np.log(rng.random(pos.sum())) / ww[pos]
                top = np.argsort(key)[-K_DRAW:]
                top = top[np.isfinite(key[top])]
                rec = np.stack([key[top], a + top, par[top], lat[top], lon[top], g("takeover_latitude_deg")[top],
                                g("takeover_longitude_deg")[top], g("latent:last_burst_latitude_deg")[top],
                                g("latent:last_burst_longitude_deg")[top], g("family")[top], ww[top]], 1)
                prev = draws.get(f"{o}:{tag}")
                allr = rec if prev is None else np.concatenate([prev, rec])
                draws[f"{o}:{tag}"] = allr[np.argsort(allr[:, 0])[-K_DRAW:]]
        print(f"{stratum} seed-{seed}: {b:,}/{n:,}", flush=True)
    for k, v in draws.items():
        acc["draws:" + k] = v
    acc["n_rows"] = n
    acc["elat"], acc["elon"] = elat, elon
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, **{k: (np.asarray(v, np.float32) if ":h_" in k else np.asarray(v)) for k, v in acc.items()})


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
