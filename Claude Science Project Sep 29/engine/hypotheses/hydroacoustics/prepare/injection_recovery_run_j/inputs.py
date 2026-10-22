"""Run J inputs for block 7 (prereg.py 'SOURCE MODEL', 'ETA MAPPING'): tau90 quantiles, per-receiver geodesic range
quantiles, and a row subsample (latitude, longitude, contact kinetic energy, tau90, ln-weights per 00:19 option,
push-over flags, stratum) for the eta mapping. Systematic chunk subsample: CHUNKS_PER_SEED contiguous chunks of
CHUNK_ROWS rows, evenly spaced through each seed's impacts32.npy, all 74 seeds. Weights: run_j_windows.ln_weights
(EoF total q = 1/3 cell, survival factor) normalised within the subsample, pooled by p_core(stratum) / K(stratum).
Usage: python inputs.py <out_dir>
"""
from __future__ import annotations
import json, pathlib, sys, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R
import run_j_windows as W


def wq(x, w, qs):
    o = np.argsort(x); x, w = x[o], w[o]
    c = np.cumsum(w); c /= c[-1]
    return [float(np.interp(q, c, x)) for q in qs]


def main(out_dir):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    eof = pathlib.Path(R.RUN_J)
    fe = json.loads((eof / "summary" / "family-evidence-run-j.json").read_text()); p_core = fe["p_core"]
    rx = W.receivers()
    rows = {k: [] for k in ["lat", "lon", "E_j", "tau90_s", "pf_drawn", "pf_surface", "stratum", "seed"] + [f"lnw_{o}" for o in R.OPTIONS]}
    t0 = time.time(); nseeds = 0; seed_rows = {}
    for s in W.STRATA:
        seeds = sorted([q for q in (eof / s).glob("seed-*") if q.is_dir() and (q / "impacts32.npy").exists()], key=lambda p: int(p.name.split("-")[1]))
        K = len(seeds)
        for sd in seeds:
            g, meta, n = W.load_seed(sd)
            logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
            starts = np.linspace(0, n - R.CHUNK_ROWS, R.CHUNKS_PER_SEED).astype(int)
            idx = np.concatenate([np.arange(a, a + R.CHUNK_ROWS) for a in starts])
            cols = (sd / "COLUMNS.txt").read_text().split(); ci = {c: i for i, c in enumerate(cols)}
            X = np.load(sd / "impacts32.npy", mmap_mode="r")
            sub = np.asarray(X[idx], dtype=np.float64)  # 8 contiguous chunks
            cache = {}
            tmap = {"unix_s": "t_impact_s", "latent:realised_flameout_unix_s": "t_realised_flameout_s"}
            def gg(k):
                if k not in cache:
                    cache[k] = sub[:, ci[tmap[k]]] + W.T0 if k in tmap else sub[:, ci[k]]
                return cache[k]
            z = np.load(sd / "tau90_v1.npz"); assert int(z["method"]) == 1
            tau = np.asarray(z["tau90_s"], float)[idx]
            v = np.sqrt(gg("velocity_east_mps") ** 2 + gg("velocity_north_mps") ** 2 + gg("velocity_up_mps") ** 2)
            E = 0.5 * gg("mass_kg") * v ** 2
            rows["lat"].append(gg("latitude_deg")); rows["lon"].append(gg("longitude_deg")); rows["E_j"].append(E); rows["tau90_s"].append(tau)
            rows["pf_drawn"].append(gg("latent:pushover_drawn") == 1); rows["pf_surface"].append(gg("latent:pushover_to_surface") == 1)
            rows["stratum"].append(np.full(len(idx), W.STRATA.index(s), np.int8)); rows["seed"].append(np.full(len(idx), int(sd.name.split("-")[1]), np.int16))
            for o in R.OPTIONS:
                lnw = W.ln_weights(gg, logon, o)
                lnw = np.where(np.isfinite(lnw), lnw, -np.inf)
                # normalise within the subsample, pool by p_core / K
                m = np.max(lnw[np.isfinite(lnw)]) if np.isfinite(lnw).any() else 0.0
                lse = m + np.log(np.sum(np.exp(lnw - m)))
                rows[f"lnw_{o}"].append(lnw - lse + np.log(p_core[s] / K))
            nseeds += 1; seed_rows[f"{s}/{sd.name}"] = int(n)
            print(s, sd.name, n, round(time.time() - t0), flush=True)
    D = {k: np.concatenate(v) for k, v in rows.items()}
    # quantiles under D0' p = 0.5
    def weights(o, p):
        w = np.exp(D[f"lnw_{o}"]); f = np.ones(len(w)); dr, ts = D["pf_drawn"], D["pf_surface"]
        f[dr & ts] = 2 * p; f[dr & ~ts] = 2 * (1 - p)
        return w * f
    res = {"n_rows": int(len(D["lat"])), "n_seeds": nseeds, "seed_rows": seed_rows, "p_core": p_core,
           "chunks_per_seed": R.CHUNKS_PER_SEED, "chunk_rows": R.CHUNK_ROWS, "tau": {}, "range_km": {}, "E_j": {}, "ess": {}}
    # quantiles on a 1-in-4 systematic thin (the same rows saved for the eta mapping); distances once per receiver
    th = slice(0, None, 4)
    Dt = {k: v[th] for k, v in D.items()}
    dist = {r: W.geodesic_km(Dt["lat"], Dt["lon"], rlat, rlon) for r, (rlat, rlon) in rx.items()}
    o_tau = np.argsort(Dt["tau90_s"]); o_E = np.argsort(Dt["E_j"]); o_d = {r: np.argsort(dist[r]) for r in rx}
    def wq_sorted(xs, w_sorted, qs):
        c = np.cumsum(w_sorted); c /= c[-1]
        return [float(np.interp(q, c, xs)) for q in qs]
    for o in R.OPTIONS:
        for p in R.PS:
            w = np.exp(Dt[f"lnw_{o}"]); f = np.ones(len(w)); dr, ts = Dt["pf_drawn"], Dt["pf_surface"]
            f[dr & ts] = 2 * p; f[dr & ~ts] = 2 * (1 - p); w = w * f
            w = np.where(np.isfinite(Dt["tau90_s"]), w, 0.0)
            key = f"{o}/p{p:g}"
            res["ess"][key] = float(w.sum() ** 2 / (w ** 2).sum())
            res["tau"][key] = wq_sorted(Dt["tau90_s"][o_tau], w[o_tau], list(R.TAU_QS))
            res["E_j"][key] = wq_sorted(Dt["E_j"][o_E], w[o_E], [0.05, 0.25, 0.5, 0.75, 0.95])
            res["range_km"][key] = {r: wq_sorted(dist[r][o_d[r]], w[o_d[r]], list(R.RANGE_QS)) for r in rx}
            print("quantiles", key, round(time.time() - t0), flush=True)
    res["receivers"] = {r: list(v) for r, v in rx.items()}
    json.dump(res, open(out / "inputs.json", "w"), indent=1)
    np.savez_compressed(out / "subsample.npz", **{k: (v.astype(np.float32) if v.dtype == np.float64 else v) for k, v in Dt.items()}, **{f"dist_{r}": dist[r].astype(np.float32) for r in rx})
    print("done", res["n_rows"], round(time.time() - t0), "s; tau D0/p0.5", res["tau"]["D0/p0.5"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
