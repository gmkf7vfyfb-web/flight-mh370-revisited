#!/usr/bin/env python3
"""Score run J settled outcomes with the per-cell detection model (work order searched-areas-spatial-detection-2026-10-18).

    python hypotheses/seabed-search/spatial/score_spatial_run_j.py <settling stratum dir> --fields <fields.npz>
        --published <searched-areas/run-j-settled/<stratum>> --eof <end-of-flight/run-j/<stratum>> --out <dir>

Same outcomes, same 'mean' field treatment and same per-row averaging as score_settled_run_j.py (alternative settling draws
are alternative OUTCOMES: the row likelihood is the MEAN of P(no find) over its draws). Per outcome the mass-weighted means of
the settled pieces are taken of: c_k on the module's 0.01 deg rasters (bilinear on cell centres, as `mh370 evaluate`), and on
the 0.005 deg fields: Phase 2 coverage c, c*f_lpd, the rho terrain weight w, and the Ocean Infinity density fields.
Then, per variant,
    d_P2 = q_hi * mean(c (1 - f)) + q_lpd * mean(c f);  d_BF = 0.9 c_BF;  d_OI = q_OI * c_OI
    rho  = mean(min(rho0 * w, 0.95))                     (w = 1 for 'flat')
    P(no find) = rho + (1 - rho) * prod_k (1 - d_k)
V0 is the published base exactly (Phase 2 q 0.945 flat on the 0.01 deg raster, OI uniform fractions 0.889 / 0.7808 with q 0.9,
rho 0.05 flat) and must reproduce the published run-j-settled rows to float32 precision.
"""
import argparse, hashlib, json, os, pathlib, sys, time
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
MOD = HERE.parent
sys.path.insert(0, str(HERE))
from build_fields import read_cov  # noqa: E402

STRIDE = 2 ** 20
F_OI = {"oi2018": 0.889, "oi2025": 0.7808}
RHO_CAP = 0.95
# id: (P2 grid, q_hi, q_lpd, f field, rho0, rho shape, OI mode, q_OI)
VARIANTS = {
    "V0_scalar":          ("cov01", 0.945, 0.945, None,  0.05, "flat",    "uniform", 0.9),
    "V0_scalar_500m":     ("g5",    0.945, 0.945, None,  0.05, "flat",    "uniform", 0.9),
    "V1_central":         ("g5",    0.95,  0.70,  "fig", 0.05, "terrain", "density", 0.9),
    "V1_rho0":            ("g5",    0.95,  0.70,  "fig", 0.0,  "terrain", "density", 0.9),
    "V1_rho0.25":         ("g5",    0.95,  0.70,  "fig", 0.25, "terrain", "density", 0.9),
    "V1_rho0.5":          ("g5",    0.95,  0.70,  "fig", 0.5,  "terrain", "density", 0.9),
    "V1_rho_flat":        ("g5",    0.95,  0.70,  "fig", 0.05, "flat",    "density", 0.9),
    "V1_lpd_terrain":     ("g5",    0.95,  0.70,  "ter", 0.05, "terrain", "density", 0.9),
    "V1_oi_uniform":      ("g5",    0.95,  0.70,  "fig", 0.05, "terrain", "uniform", 0.9),
    "V1_without_oi":      ("g5",    0.95,  0.70,  "fig", 0.05, "terrain", "none",    0.9),
    "V2_pessimistic":     ("g5",    0.90,  0.50,  "fig", 0.25, "terrain", "density", 0.63),
    "V3_optimistic":      ("g5",    0.99,  0.90,  "fig", 0.02, "terrain", "density", 0.95),
}
RHO0S = sorted({v[4] for v in VARIANTS.values()} - {0.0})


def bilin(a, s, w, st, lat, lon):
    r, c = a.shape
    y = (lat - s) / st - 0.5; x = (lon - w) / st - 0.5
    i0 = np.floor(y).astype(np.int64); j0 = np.floor(x).astype(np.int64); fy = y - i0; fx = x - j0
    def at(i, j):
        ok = (i >= 0) & (i < r) & (j >= 0) & (j < c); v = np.zeros(len(i)); v[ok] = a[i[ok], j[ok]]; return v
    return at(i0, j0) * (1 - fy) * (1 - fx) + at(i0 + 1, j0) * fy * (1 - fx) + at(i0, j0 + 1) * (1 - fy) * fx + at(i0 + 1, j0 + 1) * fy * fx


class Lookup:
    def __init__(self, fields):
        Fz = np.load(fields)
        self.g = (float(Fz["south"]), float(Fz["west"]), float(Fz["step"]))
        p2 = Fz["p2"].astype(np.float64)
        self.g5 = {"p2": p2, "p2f_fig": p2 * Fz["f_fig"], "p2f_ter": p2 * Fz["f_ter"], "w": Fz["w_rho"].astype(np.float64),
                   "oi2018": Fz["oi2018"].astype(np.float64), "oi2025": Fz["oi2025"].astype(np.float64)}
        self.cov = {k: read_cov(MOD / "coverage" / f"{f}.cov") for k, f in
                    (("p2", "phase2"), ("bf", "bluefin-2014"), ("oi2018", "ocean-infinity-2018"), ("oi2025", "ocean-infinity-2025"))}
        self.names = [f"c01_{k}" for k in self.cov] + [f"g5_{k}" for k in self.g5] + [f"wcap_{r}" for r in RHO0S]

    def __call__(self, lat, lon):
        out = [bilin(a, g[0], g[1], g[2], lat, lon) for a, g in self.cov.values()]
        s, w, st = self.g
        g5 = {k: bilin(a, s, w, st, lat, lon) for k, a in self.g5.items()}
        out += list(g5.values())
        # rho cap is applied per piece: mean(min(rho0 w, cap)) = rho0 * mean(min(w, cap / rho0))
        out += [np.minimum(g5["w"], RHO_CAP / r) for r in RHO0S]
        return np.column_stack(out)


def variant_P(S, v):
    """S: dict of per-outcome mass-weighted means. Returns P(no find) and the searched fraction (before evidence)."""
    grid, qh, ql, ff, r0, shape, oim, qoi = VARIANTS[v]
    c = S["c01_p2"] if grid == "cov01" else S["g5_p2"]
    cf = 0.0 if ff is None else S[f"g5_p2f_{ff}"]
    d = [qh * (c - cf) + ql * cf, 0.9 * S["c01_bf"]]
    srch = [c, S["c01_bf"]]
    if oim == "uniform":
        for k in ("oi2018", "oi2025"):
            d.append(qoi * F_OI[k] * S[f"c01_{k}"]); srch.append(F_OI[k] * S[f"c01_{k}"])
    elif oim == "density":
        for k in ("oi2018", "oi2025"):
            d.append(qoi * S[f"g5_{k}"]); srch.append(S[f"g5_{k}"])
    m = np.ones_like(c)
    for x in d:
        m = m * (1.0 - x)
    rho = 0.0 if r0 == 0 else (r0 if shape == "flat" else r0 * S[f"wcap_{r0}"])
    sf = 1.0 - np.prod([1.0 - x for x in srch], axis=0)
    return rho + (1.0 - rho) * m, sf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stratum_dir", type=pathlib.Path)
    ap.add_argument("--fields", required=True, type=pathlib.Path)
    ap.add_argument("--published", required=True, type=pathlib.Path)
    ap.add_argument("--eof", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--chunk", type=int, default=4_000_000)
    a = ap.parse_args()
    t0 = time.time()
    sd, st = a.stratum_dir, a.stratum_dir.name
    tag = next(sd.glob("*_impacts.f64")).name[:-len("_impacts.f64")]
    info = json.loads((sd / f"{tag}_info.json").read_text())
    imp = np.memmap(sd / f"{tag}_impacts.f64", dtype="<f8", mode="r").reshape(-1, 14)
    el = np.memmap(sd / f"{tag}_elements.f64", dtype="<f8", mode="r").reshape(-1, 8)
    src = np.load(sd / f"{tag}_source.npy"); dr = np.load(sd / f"{tag}_draws.npz")
    n_rows = imp.shape[0]
    L = Lookup(a.fields)
    checks = {"stratum": st, "table_rows": int(n_rows), "elements": int(el.shape[0])}

    key = el[:, 0].astype(np.int64) * STRIDE + el[:, 1].astype(np.int64)
    if np.any(np.diff(key) < 0):
        sys.exit("element table not in (row, draw) order")
    newblk = np.r_[True, key[1:] != key[:-1]]
    okey = key[newblk]; oidx = np.cumsum(newblk) - 1; del newblk
    n_out = len(okey); orow = okey // STRIDE
    checks["outcomes"] = int(n_out)

    # impact-position values (for carried outcomes)
    lat_i, lon_i = np.asarray(imp[:, 1]), np.asarray(imp[:, 2])
    V_row = L(lat_i, lon_i)
    nv = V_row.shape[1]
    msum = np.zeros(n_out); acc = np.zeros((n_out, nv))
    fate = el[:, 4]
    sel = np.where(fate == 0.0)[0]
    for s in range(0, len(sel), a.chunk):
        ee = sel[s:s + a.chunk]
        V = L(np.asarray(el[ee, 5]), np.asarray(el[ee, 6])); o = oidx[ee]; m = np.asarray(el[ee, 7])
        msum += np.bincount(o, weights=m, minlength=n_out)
        for j in range(nv):
            acc[:, j] += np.bincount(o, weights=m * V[:, j], minlength=n_out)
    carried = msum <= 0
    S_arr = np.where(carried[:, None], V_row[orow], acc / np.maximum(msum, 1e-300)[:, None])
    S = {n: S_arr[:, j] for j, n in enumerate(L.names)}
    checks["carried_outcomes"] = int(carried.sum())

    # V0 reproduction against the published settled columns
    pub = np.load(a.published / "outcomes.npz")
    pc = pub["c_mean"].astype(np.float64)
    if len(pc) != n_out or not np.array_equal(pub["row"], orow.astype(np.int32)):
        sys.exit("published outcomes not aligned")
    for j, k in enumerate(("p2", "bf", "oi2018", "oi2025")):
        checks[f"V0_c_mean_{k}_max_abs_vs_published"] = float(np.abs(S[f"c01_{k}"] - pc[:, j]).max())
    nd = np.bincount(orow, minlength=n_rows)
    P0, _ = variant_P(S, "V0_scalar")
    ln0 = np.log(np.bincount(orow, weights=P0, minlength=n_rows) / np.maximum(nd, 1))
    pr = np.load(a.published / "rows.npz")
    checks["V0_row_lnL_max_abs_vs_published"] = float(np.abs(ln0 - pr["lnL_settled_base_rho0.05"]).max())
    if checks["V0_row_lnL_max_abs_vs_published"] > 1e-5:
        sys.exit(f"V0 does not reproduce the published settled column: {checks}")
    # tests from the brief
    o1 = int(np.where(~carried)[0][0])
    Pv, _ = variant_P({k: v[[o1]] for k, v in S.items()}, "V1_central")
    Pv2, _ = variant_P({k: v[[o1, o1]] for k, v in S.items()}, "V1_central")
    checks["averaging_test_two_identical_draws_equal_one"] = bool(abs(Pv[0] - Pv2.mean()) < 1e-15)
    offg = np.ones(n_out, bool)
    for k in ("c01_p2", "c01_bf", "c01_oi2018", "c01_oi2025", "g5_p2", "g5_oi2018", "g5_oi2025"):
        offg &= S[k] == 0
    checks["off_ground_outcomes"] = int(offg.sum())
    checks["off_ground_lnL_exactly_zero_all_variants"] = bool(all(np.all(np.log(variant_P({k: v[offg] for k, v in S.items()}, vv)[0]) == 0.0)
                                                                  for vv in VARIANTS)) if offg.any() else None

    # row columns
    rows_out = {"n_draws": nd.astype(np.int32)}
    Pvar, SFvar = {}, {}
    for v in VARIANTS:
        P, sf = variant_P(S, v); Pvar[v], SFvar[v] = P, sf
        rows_out[f"lnL_{v}"] = np.log(np.bincount(orow, weights=P, minlength=n_rows) / np.maximum(nd, 1))
        if not np.isfinite(rows_out[f"lnL_{v}"]).all():
            sys.exit(f"non-finite {v}")

    # impact attributes for the split table
    arc = np.zeros(n_rows)
    for k in np.unique(src[:, 1]):
        rk = np.where(src[:, 1] == k)[0]
        I32 = np.load(a.eof / f"seed-{int(k)}" / "impacts32.npy", mmap_mode="r")
        arc[rk] = np.asarray(I32[src[rk, 2], 9], np.float64)
        if np.max(np.abs(np.asarray(I32[src[rk[:1000], 2], 7]) - lat_i[rk[:1000]])) > 1e-3:
            sys.exit("source.npy does not map to end-of-flight latitude")
    north25 = lat_i > -25.0; glide = np.abs(arc) > 25.0

    prods = []
    for j, p in enumerate(info["products"]):
        r, d = dr[f"rows_{j}"].astype(np.int64), dr[f"draws_{j}"].astype(np.int64)
        o = np.searchsorted(okey, r * STRIDE + d)
        if not np.array_equal(okey[np.clip(o, 0, n_out - 1)], r * STRIDE + d):
            sys.exit(f"product {j}: outcome missing")
        N = len(o)
        rec = {k: p[k] for k in ("option", "D", "cell", "subset", "N", "row_ess_kish", "share_of_option")}
        n25, gl = north25[r], glide[r]
        base = Pvar["V0_scalar"][o]
        for v in VARIANTS:
            P, sf = Pvar[v][o], SFvar[v][o]
            rest = 1.0 - sf
            cats = {"searched": sf, "north_of_25S": rest * n25, "beyond_25NM": rest * (~n25) * gl, "near_arc_unsearched": rest * (~n25) * (~gl)}
            dd = P - base
            rec[v] = {"Z": float(P.mean()), "Z_se": float(P.std(ddof=1) / np.sqrt(N)),
                      "dZ_vs_V0": float(dd.mean()), "dZ_vs_V0_se": float(dd.std(ddof=1) / np.sqrt(N)),
                      "before": {c_: float(x.mean()) for c_, x in cats.items()},
                      "after": {c_: float((P * x).sum() / P.sum()) for c_, x in cats.items()},
                      "outcome_ess_after": float(P.sum() ** 2 / (P * P).sum())}
        prods.append(rec)

    a.out.mkdir(parents=True, exist_ok=True)
    tmp = a.out / "rows.part.npz"
    np.savez(tmp, **{k: (v if k == "n_draws" else v.astype(np.float32)) for k, v in rows_out.items()}); os.replace(tmp, a.out / "rows.npz")
    checks["wall_s"] = time.time() - t0
    (a.out / "summary.json").write_text(json.dumps({"stratum": st, "variants": VARIANTS, "checks": checks, "products": prods}, indent=1))
    (a.out / "SHA256SUMS").write_text("".join(f"{hashlib.sha256((a.out / f).read_bytes()).hexdigest()}  {f}\n" for f in ("rows.npz", "summary.json")))
    print(json.dumps(checks), flush=True)


if __name__ == "__main__":
    main()
