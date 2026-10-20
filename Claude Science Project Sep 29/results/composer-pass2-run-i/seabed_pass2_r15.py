"""Composer pass 2b (ruling 15 Oct 2026): seabed_pass2.py with the drift/Pleiades carry taken per core seed (replicate)
within the stratum (mode) instead of pooled over all seeds; not-computed outcome share recorded. Nothing else changed.
Composer pass 2 (run I), seabed PDF: settling's run I wreckage samples re-weighted by the composed impact-level factors (gap G12).

Settling's run I products (settling/run-i/<stratum>/, products P00-P35 = D0-D5 x {total, A1, A2, B, C1, C2 silent}) are systematic
resamples of the flight + EoF 00:19 row mass, each outcome weight 1/N. The module factors are functions of the impact row alone, so
the composed seabed distribution is the same outcomes re-weighted by exp(sum of module log-likelihoods at the outcome's source row)
(importance re-weighting; ESS reported per product). Drift not-computed rows: carried at the mean likelihood ratio over the product's
own outcomes (R1). Ocean model: equal-prior mixture of GLORYS12 and GlobCurrent (product-relative windage), per row (as the impact
step). Seabed density = settled elements, each sharing its outcome's weight in proportion to settled mass (afloat pieces excluded),
as results/composer-pass1-run-c/seabed_c.py. Grid as compose_quarter.py (0.1 deg); halves by core seed (1-4 against 5-8).
Usage: python seabed_pass2.py <stratum> <out.npz>
"""
import json, math, pathlib, sys, time
import numpy as np

EX = pathlib.Path("/Users/pete/Downloads/mh370-exchange")
sys.path.insert(0, str(EX / "pleiades/run-i")); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reader as PLE                                      # noqa: E402
from compose_quarter import G2, LAT2, LON2, NY2, NX2      # noqa: E402

TAG = {"next-i-waypoints": "waypoints", "next-i-free": "free", "next-i-descent-climb": "descentclimb", "next-i-repro-radar": "reproradar"}
LAYERS = ["P1", "Dr", "DrS", "H", "HS"]


def main(st, outp):
    t0 = time.time(); d = EX / "settling/run-i" / st; t = TAG[st]
    info = json.loads((d / f"ri_{t}_info.json").read_text()); z = np.load(d / f"ri_{t}_draws.npz")
    src = np.load(d / f"ri_{t}_source.npy"); T = np.fromfile(d / f"ri_{t}_impacts.f64", "<f8").reshape(-1, 14)
    assert len(src) == len(T)
    nT = len(T); dG = np.full(nT, np.nan); dC = np.full(nT, np.nan); S = np.full(nT, np.nan); pG = np.full(nT, np.nan); pC = np.full(nT, np.nan)
    for k in range(1, 9):
        sel = np.where(src[:, 1] == k)[0]; r = src[sel, 2]
        if len(sel) == 0:
            continue
        dr = np.load(EX / "debris-drift/run-i" / st / f"seed-{k}" / "drift-lnL.npy", mmap_mode="r")[r]
        dG[sel] = np.where(dr["state_glorys12_h50"] == 1, dr["lnL_glorys12_h50"], np.nan)
        dC[sel] = np.where(dr["state_globcurrent_h50"] == 1, dr["lnL_globcurrent_h50"], np.nan)
        S[sel] = np.load(EX / "searched-areas/run-i" / f"i-{st}" / f"seed-{k}" / "seabed-lnL.npy", mmap_mode="r")[r]
        psd = EX / "pleiades/run-i" / st / f"seed-{k}"
        pG[sel] = PLE.load_rho(psd, 0.25, 0, "-gcrel")[r]; pC[sel] = PLE.load_rho(psd, 0.25, 1, "-gcrel")[r]
        imp = np.load(EX / "end-of-flight/run-i" / st / f"seed-{k}" / "impacts32.npy", mmap_mode="r")
        assert np.allclose(imp[r, 7], T[sel, 1], atol=1e-4) and np.allclose(imp[r, 8], T[sel, 2], atol=1e-4), "source row mismatch"
    assert np.isfinite(S).all()
    # settled elements -> per outcome key, share of the outcome's settled mass
    EL = np.memmap(d / f"ri_{t}_elements.f64", dtype="<f8", mode="r").reshape(-1, 8)
    fate = np.asarray(EL[:, 4]); st0 = fate == 0
    key = (np.asarray(EL[:, 0])[st0].astype(np.int64) << 20) + np.asarray(EL[:, 1])[st0].astype(np.int64)
    o = np.argsort(key, kind="stable"); key = key[o]
    lat = np.asarray(EL[:, 5])[st0][o]; lon = np.asarray(EL[:, 6])[st0][o]; mass = np.asarray(EL[:, 7])[st0][o]
    afloat_mass_share = float(np.asarray(EL[:, 7])[fate == 1].sum() / np.asarray(EL[:, 7])[fate >= 0].sum())
    del o
    uk, start, cnt = np.unique(key, return_index=True, return_counts=True)
    share = mass / np.repeat(np.add.reduceat(mass, start), cnt); elem_uk = np.repeat(np.arange(len(uk)), cnt)
    iy = np.floor((lat - LAT2[0]) / G2).astype(np.int64); ix = np.floor((lon - LON2[0]) / G2).astype(np.int64)
    ine = (iy >= 0) & (iy < NY2) & (ix >= 0) & (ix < NX2); ecell = np.where(ine, iy * NX2 + ix, 0)
    print(st, "elements", len(key), f"{time.time() - t0:.0f}s", flush=True)
    arrays, meta = {}, {"stratum": st, "afloat_mass_share": afloat_mass_share, "products": []}
    for j, p in enumerate(info["products"]):
        rows, draws, seeds = z[f"rows_{j}"].astype(np.int64), z[f"draws_{j}"].astype(np.int64), z[f"seed_{j}"]
        want = (rows << 20) + draws; pos = np.minimum(np.searchsorted(uk, want), len(uk) - 1); ok = uk[pos] == want
        cg, cc = dG[rows], dC[rows]
        lpg, lpc = pG[rows], pC[rows]
        nc_out = {}
        for nm, x in (("dG", cg), ("dC", cc), ("pG", lpg), ("pC", lpc)):   # ruling 15 Oct: carry at the (replicate, mode) mean
            nc_out[nm] = float((~np.isfinite(x)).mean())                 # ratio, i.e. per core seed within this stratum (was:
            for k in np.unique(seeds):                                   # pooled over the product's outcomes of all seeds)
                sk = seeds == k; f = np.isfinite(x) & sk
                if f.sum() < sk.sum():
                    x[sk & ~f] = np.log(np.mean(np.exp(x[f] - x[f].max()))) + x[f].max()
        lf = {"P1": np.zeros(len(rows)), "Dr": np.logaddexp(cg, cc) - math.log(2), "H": np.logaddexp(cg + lpg, cc + lpc) - math.log(2)}
        lf["DrS"] = lf["Dr"] + S[rows]; lf["HS"] = lf["H"] + S[rows]
        ip = np.floor((T[rows, 1] - LAT2[0]) / G2).astype(np.int64) * NX2 + np.floor((T[rows, 2] - LON2[0]) / G2).astype(np.int64)
        e = {"j": j, "D": p["D"], "cell": p["cell"], "subset": p["subset"], "N": int(len(rows)), "outcomes_without_settled_mass": int((~ok).sum()), "nc_outcome_share": nc_out, "layers": {}}
        for L in LAYERS:
            a = lf[L]; v = np.exp(a - a.max()); v[~ok] = 0.0
            ess = float(v.sum() ** 2 / (v * v).sum()); lnmean = float(np.log(np.mean(np.exp(a - a.max()))) + a.max())
            e["layers"][L] = {"ess_outcomes": ess, "ln_mean_factor": lnmean, "distinct_rows_weight90": int(np.searchsorted(np.cumsum(np.sort(v)[::-1]) / v.sum(), 0.9) + 1)}
            for hname, m in (("all", np.ones(len(rows), bool)), ("h0", seeds <= 4), ("h1", seeds >= 5)):
                vv = np.where(m, v, 0.0)
                if vv.sum() == 0:
                    continue
                Wuk = np.bincount(pos[ok], weights=vv[ok] / vv.sum(), minlength=len(uk))
                we = share * Wuk[elem_uk]
                arrays[f"{j}|{L}|seabed|{hname}"] = np.bincount(ecell[ine], weights=we[ine], minlength=NY2 * NX2).astype(np.float32)
                if hname == "all":
                    okp = (ip >= 0) & (ip < NY2 * NX2)
                    arrays[f"{j}|{L}|impact|all"] = np.bincount(ip[okp], weights=(vv / vv.sum())[okp], minlength=NY2 * NX2).astype(np.float32)
                    e["layers"][L]["seabed_mean_lat_lon"] = [float((we * lat).sum() / we.sum()), float((we * lon).sum() / we.sum())]
        meta["products"].append(e)
    np.savez_compressed(outp, **arrays); pathlib.Path(str(outp).replace(".npz", ".json")).write_text(json.dumps(meta))
    print("done", st, f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
