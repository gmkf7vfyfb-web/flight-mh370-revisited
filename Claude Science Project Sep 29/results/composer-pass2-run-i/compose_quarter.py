"""Composer pass 2 on core run I (architecture stand-in for the composer): per-row composition of one stratum x one seed-quarter.

For every row of end of flight's run I impacts, build the 00:19 two-factor row mass exactly as end of flight's
smoke/option_table_0019.py seed_terms (hand-off weight / sum x survival factor x L(D) x L(cause)), then multiply the module
factors read in place from the exchange (row-aligned, asserted):
  drift      debris-drift/run-i  lnL_glorys12_h50, lnL_globcurrent_h50 (state 1 = scored; else carried at the seed's mean
             likelihood ratio under the base cell weights, finding R1 / ruling 1; exclusion = labelled sensitivity "x")
  searches   searched-areas/run-i  seabed-lnL.npy (rho 0.05, point target)
  Pleiades   pleiades/run-i  reader.load_rho(sd, 0.25, m, "-gcrel") for m = 0 GLORYS12, 1 GlobCurrent (product-relative windage);
             the A_scene^2 constant (12.43 nat) is not in the surface and is added back only in the reported evidence increment
  hydro      hydroacoustics/run-i  lnL_gated (= 0, the module likelihood, predictive) ; lnL_soft = labelled sensitivity "+hyd"
Ocean model: per row, L_M = 0.5 (L_G + L_C) where L_m = drift_m x Pleiades_m (Bayesian model averaging over a global model choice
at equal prior: the marginal posterior is the prior times the mean likelihood); the posterior model weights come from Z_G, Z_C.
Seeds within a stratum are pooled by evidence (as option_table_0019 / settling). Output per job: per-product 2D histograms
(0.1 deg grid, all rows and per EoF family), per-seed latitude histograms (pass-0 grid, 0.05 deg) and scalar sums.
Usage: python compose_quarter.py <stratum> <seed,seed> <out.npz> [repo project dir]
"""
import csv, json, math, pathlib, sys, time
import numpy as np
from scipy.special import gammaln

EX = pathlib.Path("/Users/pete/Downloads/mh370-exchange")
HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path(sys.argv[4]) if len(sys.argv) > 4 else HERE.parents[1] / "scratch/repo/Claude Science Project Sep 29"
sys.path.insert(0, str(REPO / "engine/hypotheses/end-of-flight/smoke")); sys.path.insert(0, str(EX / "pleiades/run-i"))
from compact_impacts import load, family_labels                    # noqa: E402
from displacement_hist import derived_logliks, constraint_log_factor, SATCOM_CSV   # noqa: E402
import reader as PLE                                                # noqa: E402
import option_table_0019 as OT                                      # noqa: E402  (d5_loglik, W_S used unchanged)

DS = ["D0", "D1", "D2", "D3", "D4", "D5"]
CS = ["T", "C1", "C2s", "T1"]          # total q=1/3 (C2 silent) PRIMARY; C1; C2 silent; total q=1 (C2 silent)
LAYERS = ["Dr", "DrS", "H", "HS"]
FAMS = {"A1": (1,), "A2": (2,), "B": (3, 6)}
G2 = 0.1; LAT2 = (-46.0, -18.0); LON2 = (82.0, 110.0)
NY2 = int(round((LAT2[1] - LAT2[0]) / G2)); NX2 = int(round((LON2[1] - LON2[0]) / G2))
GMIN, GSTEP = -50.0, 0.05; NPTS = int(round(100.0 / GSTEP)) + 1


def products():
    P = []
    for d in DS:
        for c in CS:
            P.append((d, c, "P1", "-", ""))
            for L in LAYERS:
                P.append((d, c, L, "M", ""))
        for L in LAYERS:
            P += [(d, "T", L, "G", ""), (d, "T", L, "C", ""), (d, "T", L, "M", "+hyd")]
        P += [(d, "T", "Dr", "M", "x"), (d, "T", "H", "M", "x")]
    return P


def pid(p):
    return f"{p[0]}|{p[1]}|{p[2]}|{p[3]}|{p[4]}"


def seed_rows(st, k):
    sd = EX / "end-of-flight/run-i" / st / f"seed-{k}"
    meta, g = load(sd); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    obs = {r["epoch_id"]: r for r in csv.DictReader(open(SATCOM_CSV))}
    w = g("weight"); lw = np.log(w) - np.log(w.sum())
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]; der = derived_logliks(meta, g, present)
    par = g("parent").astype(np.int64)
    V = np.asarray(np.load(EX / "core/run-i" / st / "bto-bfo" / f"seed-{k}" / "handoff-m0011" / "handoff.npy", mmap_mode="r")[:, 9])[par]
    col = lambda kk: np.where(np.isfinite(g("loglik:" + kk)), g("loglik:" + kk), -np.inf)
    D = {"D0": np.zeros(len(w)), "D1": der["r600-bto"], "D2": col("r600/no-offset"), "D3": col("both/no-offset"),
         "D4": col("both/startup-offset"), "D5": OT.d5_loglik(g, V, obs)}
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    C1 = lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered")
    C2 = -np.log(OT.W_S) + constraint_log_factor(g, logon, "other", "silent")
    Cc = {"C1": C1, "C2s": C2, "T": np.logaddexp(np.log(0.75) + C1, np.log(0.25) + C2), "T1": np.logaddexp(np.log(0.5) + C1, np.log(0.5) + C2)}
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    lat, lon = g("latitude_deg"), g("longitude_deg")
    spd = np.sqrt(g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2)
    n = len(w); row = np.arange(n)
    dr = np.load(EX / "debris-drift/run-i" / st / f"seed-{k}" / "drift-lnL.npy", mmap_mode="r")
    assert len(dr) == n and np.array_equal(np.asarray(dr["row"], np.int64), row) and np.array_equal(np.asarray(dr["parent"], np.int64), par), "drift align"
    dG = np.where(np.asarray(dr["state_glorys12_h50"]) == 1, np.asarray(dr["lnL_glorys12_h50"], float), np.nan)
    dC = np.where(np.asarray(dr["state_globcurrent_h50"]) == 1, np.asarray(dr["lnL_globcurrent_h50"], float), np.nan)
    ssd = EX / "searched-areas/run-i" / f"i-{st}" / f"seed-{k}"
    S = np.asarray(np.load(ssd / "seabed-lnL.npy", mmap_mode="r"), float); assert len(S) == n and np.isfinite(S).all(), "search"
    psd = EX / "pleiades/run-i" / st / f"seed-{k}"
    pr = np.load(psd / "pleiades-lnL.npy", mmap_mode="r")
    assert np.array_equal(np.asarray(pr["row"], np.int64), row) and np.array_equal(np.asarray(pr["parent"], np.int64), par), "pleiades align"
    pG = PLE.load_rho(psd, 0.25, 0, "-gcrel"); pC = PLE.load_rho(psd, 0.25, 1, "-gcrel")
    hy = np.load(EX / "hydroacoustics/run-i" / st / f"seed-{k}" / "hydro-lnL.npy", mmap_mode="r")
    assert np.array_equal(np.asarray(hy["row"], np.int64), row) and np.array_equal(np.asarray(hy["parent"], np.int64), par), "hydro align"
    assert np.all(np.asarray(hy["lnL_gated"]) == 0.0), "hydro gated not zero"
    Y = np.asarray(hy["lnL_soft"], float); ync = int((~np.isfinite(Y)).sum()); Y = np.where(np.isfinite(Y), Y, 0.0)
    return dict(lw=lw, surv=surv, D=D, C=Cc, f4=f4, lat=lat, lon=lon, spd=spd, dG=dG, dC=dC, S=S, pG=pG, pC=pC, Y=Y, n=n, hy_nc=ync)


def carry(x, a):
    """NaN entries of x -> ln(sum_ok e^a e^x / sum_ok e^a): the mean likelihood ratio under base weights e^a (R1 / ruling 1).
    Returns (carried x, base-weight share of the NaN rows)."""
    ok = np.isfinite(x) & np.isfinite(a); fa = np.isfinite(a)
    if np.isfinite(x[fa]).all():
        return x, 0.0
    sa = a[fa].max(); wa = np.where(fa, np.exp(np.where(fa, a, 0.0) - sa), 0.0)
    xm = x[ok].max(); m = np.log(np.sum(wa[ok] * np.exp(x[ok] - xm))) + xm - np.log(wa[ok].sum())
    share = float(wa[~np.isfinite(x)].sum() / wa.sum())
    return np.where(np.isfinite(x), x, m), share


def main(st, seeds, outp):
    t0 = time.time(); PRODS = products(); out = {}; scal = {}
    for k in seeds:
        R = seed_rows(st, k)
        lat, lon = R["lat"], R["lon"]
        iy = np.floor((lat - LAT2[0]) / G2).astype(np.int64); ix = np.floor((lon - LON2[0]) / G2).astype(np.int64)
        in2 = (iy >= 0) & (iy < NY2) & (ix >= 0) & (ix < NX2); cell = np.where(in2, iy * NX2 + ix, 0)
        lb = np.clip(np.floor((lat - GMIN + GSTEP / 2) / GSTEP).astype(np.int64), 0, NPTS - 1)
        fidx = {f: np.isin(R["f4"], v) for f, v in FAMS.items()}
        fast = R["spd"] > 212.0
        cache = {}
        for p in PRODS:
            d, c, L, oc, var = p
            a0 = R["lw"] + R["surv"] + R["D"][d] + R["C"][c]
            if (d, c) not in cache:
                dG, nG = carry(R["dG"], a0); dC, nC = carry(R["dC"], a0)
                pG, _ = carry(R["pG"], a0); pC, _ = carry(R["pC"], a0)
                cache = {(d, c): (dG, dC, pG, pC, nG, nC)}
            dG, dC, pG, pC, nG, nC = cache[(d, c)]
            if L == "P1":
                a = a0
            else:
                withP = L.startswith("H")
                lG = dG + (pG if withP else 0.0); lC = dC + (pC if withP else 0.0)
                if oc == "G":
                    a = a0 + lG
                elif oc == "C":
                    a = a0 + lC
                else:
                    a = a0 + np.logaddexp(lG, lC) - math.log(2.0)
                if var == "x":
                    a = np.where(np.isfinite(R["dG"]) & np.isfinite(R["dC"]), a, -np.inf)
                if L.endswith("S"):
                    a = a + R["S"]
                if var == "+hyd":
                    a = a + R["Y"]
            fin = np.isfinite(a)
            s = float(a[fin].max()); w = np.where(fin, np.exp(np.where(fin, a, 0.0) - s), 0.0)
            P = pid(p); E = scal.setdefault(P, {})
            m = w.sum(); E.setdefault("lnM", []).append(float(np.log(m) + s)); E.setdefault("lnM2", []).append(float(np.log((w * w).sum()) + 2 * s))
            E.setdefault("fam_lnM", {}); E.setdefault("fam_lnM2", {})
            for f, ix_ in fidx.items():
                wf = w[ix_]; mf = wf.sum()
                E["fam_lnM"].setdefault(f, []).append(float(np.log(mf) + s) if mf > 0 else -1e300)
                E["fam_lnM2"].setdefault(f, []).append(float(np.log((wf * wf).sum()) + 2 * s) if mf > 0 else -1e300)
            E.setdefault("mean_lat", []).append(float((w * lat).sum() / m)); E.setdefault("mean_lon", []).append(float((w * lon).sum() / m))
            E.setdefault("fast_share", []).append(float(w[fast].sum() / m)); E.setdefault("out2d_share", []).append(float(w[~in2].sum() / m))
            E.setdefault("drift_nc_share_G", []).append(nG); E.setdefault("drift_nc_share_C", []).append(nC)
            wn = w / m
            out.setdefault(P + "|2d", []).append((float(np.log(m) + s), np.bincount(cell[in2], weights=wn[in2], minlength=NY2 * NX2)))
            out[P + f"|lat|s{k}"] = np.bincount(lb, weights=wn, minlength=NPTS).astype(np.float32)
            for f, ix_ in fidx.items():
                sel = in2 & ix_
                out.setdefault(P + f"|2d|{f}", []).append((float(np.log(m) + s), np.bincount(cell[sel], weights=wn[sel], minlength=NY2 * NX2)))
                out[P + f"|lat|{f}|s{k}"] = np.bincount(lb[ix_], weights=wn[ix_], minlength=NPTS).astype(np.float32)
        scal.setdefault("_meta", {}).setdefault("rows", []).append(R["n"]); scal["_meta"].setdefault("hydro_soft_nonfinite", []).append(R["hy_nc"])
        scal["_meta"].setdefault("pleiades_nan_rows_G_C", []).append([int((~np.isfinite(R["pG"])).sum()), int((~np.isfinite(R["pC"])).sum())])
        scal["_meta"].setdefault("drift_nan_rows_G_C", []).append([int((~np.isfinite(R["dG"])).sum()), int((~np.isfinite(R["dC"])).sum())])
        print(st, k, f"{time.time() - t0:.0f}s", flush=True)
    arrays = {}
    for key, v in out.items():
        if isinstance(v, list):          # 2D: quarter sum on a common scale; mass histogram = arrays[key] * exp(arrays[key|lnscale])
            lm = np.array([x for x, _ in v]); mx = lm.max(); h = sum(hh * np.exp(x - mx) for x, hh in v)
            arrays[key] = h.astype(np.float32); arrays[key + "|lnscale"] = np.array([mx])
        else:
            arrays[key] = v
    np.savez_compressed(outp, **arrays)
    pathlib.Path(str(outp).replace(".npz", ".json")).write_text(json.dumps({"stratum": st, "seeds": seeds, "scalars": scal}))
    print("done", st, seeds, f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], [int(x) for x in sys.argv[2].split(",")], sys.argv[3])
