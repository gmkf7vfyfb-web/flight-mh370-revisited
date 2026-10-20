#!/usr/bin/env python3
"""Per-cell detection fields for the seabed searches (work order searched-areas-spatial-detection-2026-10-18).

    python hypotheses/seabed-search/spatial/build_fields.py --bathy <GA Phase 1 150 m zip> --out <dir>

Grid G5: 0.005 deg (about 500 m), lat -40.2..-24.5, lon 85..103. Writes <out>/fields.npz and <out>/fields.json.

Fields
  p2      ATSB Phase 2 covered fraction (valid 5 m pixels, union of the four sensors). Gaps are therefore already OUT of c.
  sub     Figure 73 sub-area of each covered cell: 1 red (main area), 2 orange, 3 yellow, 4 purple (outer band).
  f_fig   lower-confidence (LPD) fraction of the covered part of the cell, from the green overlay of ATSB 2017 Figure 73
          (printed p. 96), smoothed (Gaussian sigma 5 cells, about 2.8 km N-S) and scaled in each sub-area so that its
          coverage-weighted mean equals the printed share: lower / (high + lower).                    PRIMARY
  f_ter   the same, from a logistic terrain model fitted to the figure's green pixels (slope, max slope, roughness). SENSITIVITY
  w_rho   terrain weight for rho: the terrain model's propensity / its coverage-weighted mean over Phase 2 (mean 1);
          1 where the Phase 1 bathymetry has no data.
  oi2018, oi2025   Ocean Infinity coverage density (grade C): slow AIS fixes (< 4 kn, MH370-CAPTION hourly tracks),
          Gaussian kernel sigma 15 km (AUV working radius), times the module's traced layer fraction, scaled so the total
          equals the searched area Ocean Infinity / Malaysia report (112,000 and 7,571 km2), capped at the layer value.
"""
import argparse, json, pathlib, re, struct, sys
import numpy as np
from scipy import ndimage as ndi
from scipy.optimize import minimize

HERE = pathlib.Path(__file__).resolve().parent
MOD = HERE.parent
PROJ = MOD.parents[2]                                   # 'Claude Science Project Sep 29'
REPO = PROJ.parent
sys.path.insert(0, str(MOD / "prepare"))
import build_coverage as BC  # noqa: E402

G5 = dict(south=-40.2, west=85.0, step=0.005, rows=3140, cols=3600)
R_KM = 6371.0072
SNAP = REPO / "ISO Sept 28 Status" / "inputs" / "search-coverage"
PRINTED = {"red": (98.7, 1.1, 0.2), "orange": (91.5, 7.8, 0.7), "yellow": (97.8, 1.1, 1.1), "purple": (97.9, 1.5, 0.6)}
SUBCODE = {"red": 1, "orange": 2, "yellow": 3, "purple": 4}
# Figure 73 render (1191 x 1684 px). Box corners read by hand from zoomed crops (render pixels):
RED_BOX = [(241, 877), (610, 613), (653, 665), (279, 938)]     # NW-SW, NW-NE, SE-NE, SE-SW
ORANGE_NE_EDGE = [(748, 497), (762, 511)]
FRAME = (175, 1111, 227, 1083)                                  # x0, x1, y0, y1 of the map frame
OI_TARGET = {"oi2018": 112000.0, "oi2025": 7571.0}


def read_cov(p):
    b = p.read_bytes(); assert b[:8] == b"MH370COV"
    _, s, w, st, r, c, n = struct.unpack("<IdddIII", b[8:48])
    rec = np.frombuffer(b[48:48 + 3 * n], dtype=[("v", "u1"), ("n", "<u2")])
    return np.repeat(rec["v"], rec["n"]).reshape(r, c) / 255.0, (s, w, st, r, c)


def lat5(): return G5["south"] + (np.arange(G5["rows"]) + 0.5) * G5["step"]
def lon5(): return G5["west"] + (np.arange(G5["cols"]) + 0.5) * G5["step"]


def cell_km2():
    la = lat5()
    return (R_KM ** 2 * np.radians(G5["step"]) * (np.sin(np.radians(la + G5["step"] / 2)) - np.sin(np.radians(la - G5["step"] / 2))))[:, None] * np.ones((1, G5["cols"]))


def fine_to_g5(fine, grid):
    s, w, r, c = grid
    a = fine.reshape(r * 2, 5, c * 2, 5).sum(axis=(1, 3), dtype=np.uint32) / (25 * 255.0)
    return place(a, s, w)


def place(a, s, w):
    out = np.zeros((G5["rows"], G5["cols"]))
    r0 = round((s - G5["south"]) / G5["step"]); c0 = round((w - G5["west"]) / G5["step"])
    rr = slice(max(r0, 0), min(r0 + a.shape[0], G5["rows"])); cc = slice(max(c0, 0), min(c0 + a.shape[1], G5["cols"]))
    out[rr, cc] = a[rr.start - r0:rr.stop - r0, cc.start - c0:cc.stop - c0]
    return out


def cov_to_g5(a, g):
    s, w, st, r, c = g
    assert abs(st - 0.01) < 1e-12
    return place(np.repeat(np.repeat(a, 2, 0), 2, 1), s, w)


def terrain(bathy_zip):
    import rasterio
    Rm = 6378137.0
    ds = rasterio.open(f"/vsizip/{bathy_zip}/Southern_Indian_Ocean__MH370__Bathymetry_2017_150m_MSL_cog.tif")
    T = ds.transform
    my = lambda lat: Rm * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))
    x0 = np.radians(G5["west"]) * Rm; x1 = np.radians(G5["west"] + G5["cols"] * G5["step"]) * Rm
    y0 = my(G5["south"]); y1 = my(G5["south"] + G5["rows"] * G5["step"])
    c0 = int((x0 - T.c) / T.a) - 2; c1 = int((x1 - T.c) / T.a) + 2; r0 = int((T.f - y1) / (-T.e)) - 2; r1 = int((T.f - y0) / (-T.e)) + 2
    Z = ds.read(1, window=rasterio.windows.Window(c0, r0, c1 - c0, r1 - r0)).astype(np.float32)
    Z[Z < -1e30] = np.nan
    ys = T.f + T.e * (r0 + np.arange(Z.shape[0]) + 0.5); lat = np.degrees(2 * np.arctan(np.exp(ys / Rm)) - np.pi / 2)
    xs = T.c + T.a * (c0 + np.arange(Z.shape[1]) + 0.5); lon = np.degrees(xs / Rm)
    k = np.cos(np.radians(lat))[:, None]
    gy, gx = np.gradient(Z)
    slope = np.degrees(np.arctan(np.hypot(gx / (150 * k), gy / (150 * k)))).astype(np.float32)
    del gx, gy
    m = ndi.uniform_filter(np.nan_to_num(Z), 3); m2 = ndi.uniform_filter(np.nan_to_num(Z) ** 2, 3)
    rough = np.sqrt(np.clip(m2 - m * m, 0, None)).astype(np.float32); rough[np.isnan(Z)] = np.nan
    del m, m2
    ri = np.floor((lat - G5["south"]) / G5["step"]).astype(int); ci = np.floor((lon - G5["west"]) / G5["step"]).astype(int)
    okr = (ri >= 0) & (ri < G5["rows"]); okc = (ci >= 0) & (ci < G5["cols"])
    valid = okr[:, None] & okc[None, :] & np.isfinite(slope)
    idx = (ri[:, None] * G5["cols"] + ci[None, :])[valid]; N = G5["rows"] * G5["cols"]
    cnt = np.bincount(idx, minlength=N)
    agg = lambda a: (np.bincount(idx, weights=a[valid].astype(np.float64), minlength=N) / np.maximum(cnt, 1)).reshape(G5["rows"], G5["cols"])
    out = {"slope_mean": agg(slope), "rough": agg(rough), "depth": agg(np.nan_to_num(Z))}
    smax = np.zeros(N); np.maximum.at(smax, idx, slope[valid]); out["slope_max"] = smax.reshape(G5["rows"], G5["cols"])
    have = (cnt > 0).reshape(G5["rows"], G5["cols"])
    for v in out.values():
        v[~have] = np.nan
    return out, have


def merc(lat): return np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))


def georeference(A, p2cov):
    """Mercator model x = X0 + K lon, y = Y0 - K (180/pi) merc(lat); start from the printed graticule labels and refine by
    maximising overlap of the figure's coverage colours with the module's Phase 2 raster."""
    H, W, _ = A.shape
    s = 1191 / 1100
    kx = (973 - 265) / 12 * s; X0 = 265 * s - 86 * kx; Y0 = 885 * s + kx * 180 / np.pi * merc(-40)
    fx0, fx1, fy0, fy1 = FRAME
    F = A[fy0:fy1, fx0:fx1]; r, g, b = F[..., 0], F[..., 1], F[..., 2]
    gray = (abs(r - g) < 12) & (abs(g - b) < 12) & (r < 120)
    over = ((g > 150) & (r < 150) & (b < 120) & (g - r > 50)) | ((b > 150) & (r < 90) & (b - g > 30)) | ((r > 200) & (g > 200) & (b < 90))
    covimg = np.zeros((H, W), bool); covimg[fy0:fy1, fx0:fx1] = gray | over
    a, (s2, w2, _, rr, cc) = p2cov
    LAT = s2 + (np.arange(rr) + 0.5) * 0.01; LON = w2 + (np.arange(cc) + 0.5) * 0.01
    ii, jj = np.nonzero(a > 0.5); plat, plon = LAT[ii], LON[jj]

    def score(x0, y0, k):
        x = (x0 + k * plon).astype(int); y = (y0 - k * 180 / np.pi * merc(plat)).astype(int)
        ok = (x >= fx0) & (x < fx1) & (y >= fy0) & (y < fy1)
        return covimg[y[ok], x[ok]].mean()
    best = (score(X0, Y0, kx), X0, Y0, kx)
    for it in range(3):
        b0 = best
        for dk in np.linspace(-0.03, 0.03, 13):
            for dx in range(-12, 13, 2):
                for dy in range(-12, 13, 2):
                    sc = score(b0[1] + dx / (it + 1), b0[2] + dy / (it + 1), b0[3] * (1 + dk / (it + 1)))
                    if sc > best[0]:
                        best = (sc, b0[1] + dx / (it + 1), b0[2] + dy / (it + 1), b0[3] * (1 + dk / (it + 1)))
    return best


def side(p, a, b): return (b[0] - a[0]) * (p[:, 1] - a[1]) - (b[1] - a[1]) * (p[:, 0] - a[0])


def logistic_fit(X, y, lam=1e-3):
    Xa = np.c_[np.ones(len(X)), X]
    f = lambda w: (np.logaddexp(0, Xa @ w) - y * (Xa @ w)).sum() + 0.5 * lam * (w[1:] ** 2).sum()
    g = lambda w: Xa.T @ (1 / (1 + np.exp(-Xa @ w)) - y) + np.r_[0, lam * w[1:]]
    return minimize(f, np.zeros(Xa.shape[1]), jac=g, method="L-BFGS-B").x


def auc(score, y):
    o = np.argsort(score); rk = np.empty(len(o)); rk[o] = np.arange(1, len(o) + 1); n1 = y.sum(); n0 = len(y) - n1
    return float((rk[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def ais_fixes(paths, since=None):
    dec = json.JSONDecoder(); out = []
    for p in paths:
        t = p.read_text(); j, _ = dec.raw_decode(t[t.index("(") + 1:])
        for _, rows in j["data"].items():
            for r in rows:
                try:
                    sp = float(r[4])
                except (TypeError, ValueError, IndexError):
                    continue
                if sp < 4 and (since is None or r[0] >= since):
                    out.append((float(r[1]), float(r[2])))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bathy", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    a = ap.parse_args()
    from PIL import Image
    diag = {"grid": G5}
    km2 = cell_km2()
    covs = {f.stem: read_cov(f) for f in (MOD / "coverage").glob("*.cov")}
    fine = {s: np.load(SNAP / f"phase2-{s}.npz")["fraction"] for s in BC.SENSORS}
    union = np.maximum.reduce(list(fine.values()))
    g2 = BC.GRIDS["phase2"]
    diag["check_union_reproduces_phase2_cov_max_abs"] = float(np.abs(np.round(BC.coarse(union) * 255) / 255 - covs["phase2"][0]).max())
    p2 = fine_to_g5(union, g2)
    on = p2 > 0
    diag["phase2_km2_g5"] = float((p2 * km2).sum()); diag["phase2_km2_fine"] = BC.area_km2(union, g2, 255)
    diag["deep_tow_km2_fine"] = BC.area_km2(fine["deep-tow"], g2, 255)

    T, have = terrain(a.bathy)
    diag["phase2_km2_with_bathymetry"] = float((p2 * km2 * have).sum())

    A = np.asarray(Image.open(HERE / "inputs" / "atsb2017_p96_figure73_render.png").convert("RGB")).astype(int)
    H, W, _ = A.shape
    sc, X0, Y0, K = georeference(A, covs["phase2"]); KP = K * 180 / np.pi
    diag["georef"] = {"overlap": float(sc), "X0": X0, "Y0": Y0, "K_px_per_deg": K,
                      "check_lon_at_label_86E": float((265 * 1191 / 1100 - X0) / K),
                      "check_lat_at_label_40S": float(np.degrees(2 * np.arctan(np.exp((Y0 - 885 * 1191 / 1100) / KP)) - np.pi / 2))}
    la5, lo5 = lat5(), lon5()
    ri, ci = np.nonzero(on)
    fxp = (X0 + K * lo5)[ci]; fyp = (Y0 - KP * merc(la5))[ri]; P = np.c_[fxp, fyp]
    cen = np.array([[np.mean([p[0] for p in RED_BOX]), np.mean([p[1] for p in RED_BOX])]])
    sg = lambda a_, b_: np.sign(side(cen, a_, b_))[0]
    nw, ne, se, sw = (RED_BOX[0], RED_BOX[1]), (RED_BOX[1], RED_BOX[2]), (RED_BOX[3], RED_BOX[2]), (RED_BOX[0], RED_BOX[3])
    in_span = np.sign(side(P, *ne)) == sg(*ne)
    in_red = in_span & (np.sign(side(P, *nw)) == sg(*nw)) & (np.sign(side(P, *se)) == sg(*se))
    beyond = np.sign(side(P, *ORANGE_NE_EDGE)) != sg(*ORANGE_NE_EDGE)
    code = np.where(in_red, 1, np.where(in_span, 4, np.where(beyond, 3, 2)))
    sub = np.zeros(on.shape, np.uint8); sub[ri, ci] = code
    names = {v: k for k, v in SUBCODE.items()}
    diag["subareas"] = {}
    for c_, n_ in names.items():
        m = sub == c_
        diag["subareas"][n_] = {"covered_km2": float((p2 * km2 * m).sum()), "gap_share_in_c": float(1 - p2[m].mean()),
                                "printed": PRINTED[n_], "lat_range": [float(la5[np.nonzero(m)[0]].min()), float(la5[np.nonzero(m)[0]].max())]}

    # figure pixel classes
    fx0, fx1, fy0, fy1 = FRAME
    Fp = A[fy0:fy1, fx0:fx1]; r_, g_, b_ = Fp[..., 0], Fp[..., 1], Fp[..., 2]
    isgreen = (g_ > 150) & (r_ < 160) & (b_ < 130) & (g_ - r_ > 40)
    isgrey = (abs(r_ - g_) < 14) & (abs(g_ - b_) < 14) & (r_ > 60) & (r_ < 170)
    cls_img = np.full((H, W), np.nan)
    blk = cls_img[fy0:fy1, fx0:fx1]; blk[isgrey & ~isgreen] = 0.0; blk[isgreen] = 1.0
    IX = np.clip((X0 + K * lo5).astype(int), 0, W - 1); IY = np.clip((Y0 - KP * merc(la5)).astype(int), 0, H - 1)
    cls5 = cls_img[IY[:, None], IX[None, :]]; cls5[~on] = np.nan

    def nsmooth(v, sig):
        w = np.isfinite(v).astype(float)
        return ndi.gaussian_filter(np.nan_to_num(v), sig) / np.maximum(ndi.gaussian_filter(w, sig), 1e-9)
    raw_fig = nsmooth(cls5, 5.0)

    # terrain model fitted on figure pixels over covered ground
    def sm(x):
        v = np.where(np.isfinite(x), x, 0); w = np.isfinite(x).astype(float)
        return ndi.uniform_filter(v, 3) / np.maximum(ndi.uniform_filter(w, 3), 1e-9)
    feats = ["slope_mean", "slope_max", "rough"]
    TS = {k: sm(T[k]) for k in feats + ["depth"]}
    yy, xx = np.mgrid[fy0:fy1, fx0:fx1]
    plon = (xx + 0.5 - X0) / K; plat = np.degrees(2 * np.arctan(np.exp((Y0 - (yy + 0.5)) / KP)) - np.pi / 2)
    gr = np.floor((plat - G5["south"]) / G5["step"]).astype(int); gc = np.floor((plon - G5["west"]) / G5["step"]).astype(int)
    okg = (gr >= 0) & (gr < G5["rows"]) & (gc >= 0) & (gc < G5["cols"])
    grc = np.clip(gr, 0, G5["rows"] - 1); gcc = np.clip(gc, 0, G5["cols"] - 1)
    use = okg & (p2[grc, gcc] > 0.5) & (isgreen | isgrey)
    y = isgreen[use].astype(float)
    X = np.column_stack([TS[k][grc[use], gcc[use]] for k in feats + ["depth"]])
    ok = np.isfinite(X).all(1); X, y = X[ok], y[ok]
    MU, SD = X.mean(0), X.std(0); Xs = (X - MU) / SD
    folds = np.digitize(plon[use][ok], np.quantile(plon[use][ok], [0.2, 0.4, 0.6, 0.8]))
    cv = {}
    for cols, nm in (([0], "slope_mean"), ([2], "roughness"), ([0, 1, 2], "slope_mean+slope_max+roughness"), ([0, 1, 2, 3], "with depth")):
        s_ = np.zeros(len(y))
        for f_ in range(5):
            tr = folds != f_; w_ = logistic_fit(Xs[tr][:, cols], y[tr]); s_[~tr] = np.c_[np.ones((~tr).sum()), Xs[~tr][:, cols]] @ w_
        cv[nm] = auc(s_, y)
    wfull = logistic_fit(Xs[:, :3], y)
    subp = sub[grc[use], gcc[use]][ok]
    diag["figure_pixels"] = {"used": int(len(y)), "green_share": float(y.mean()),
                             "green_share_by_subarea": {n_: float(y[subp == c_].mean()) for c_, n_ in names.items()}}
    diag["terrain_model"] = {"features": feats, "coef_std_units": wfull.tolist(), "mu": MU[:3].tolist(), "sd": SD[:3].tolist(),
                             "blocked_cv_auc": cv}
    Xg = np.stack([TS[k] for k in feats], -1)
    p_ter = 1 / (1 + np.exp(-(wfull[0] + ((Xg - MU[:3]) / SD[:3]) @ wfull[1:])))

    def scale_to_printed(raw):
        f = np.zeros_like(p2)
        for c_, n_ in names.items():
            hi, lo, _ = PRINTED[n_]; m = sub == c_; tgt = lo / (hi + lo)
            r = raw[m].copy(); r[~np.isfinite(r)] = np.nanmean(r); wts = p2[m] * km2[m]; a_, b_ = 0.0, 1e4
            for _ in range(100):
                k = (a_ + b_) / 2; val = (np.minimum(1, k * r) * wts).sum() / wts.sum()
                a_, b_ = (k, b_) if val < tgt else (a_, k)
            f[m] = np.minimum(1, k * r)
        return f
    f_fig = scale_to_printed(raw_fig); f_ter = scale_to_printed(p_ter)
    wP = p2 * km2
    pm = np.nansum(p_ter * wP) / np.sum(wP * np.isfinite(p_ter))
    w_rho = np.where(np.isfinite(p_ter), p_ter / pm, 1.0)
    diag["f_lpd_check"] = {n_: {"target": PRINTED[n_][1] / (PRINTED[n_][0] + PRINTED[n_][1]),
                                "f_fig_mean": float((f_fig * wP)[sub == c_].sum() / wP[sub == c_].sum()),
                                "f_ter_mean": float((f_ter * wP)[sub == c_].sum() / wP[sub == c_].sum()),
                                "f_fig_max": float(f_fig[sub == c_].max()),
                                "corr_fig_ter": float(np.corrcoef(f_fig[sub == c_], np.nan_to_num(f_ter[sub == c_]))[0, 1])}
                           for c_, n_ in names.items()}
    diag["w_rho"] = {"mean_on_phase2": float((w_rho * wP).sum() / wP.sum()),
                     "p5_p50_p95_max_on_phase2": np.percentile(w_rho[on], [5, 50, 95, 100]).tolist()}

    # Ocean Infinity density
    lay = {"oi2018": cov_to_g5(*covs["ocean-infinity-2018"]), "oi2025": cov_to_g5(*covs["ocean-infinity-2025"])}
    fixes = {"oi2018": ais_fixes([HERE / "inputs" / f"caption_trk_sc{i}.js" for i in (1, 2, 3, 4)]),
             "oi2025": ais_fixes([HERE / "inputs" / f"caption_trk_phase{i}.js" for i in (1, 2, 3)], since="2025-03-01")}
    oi = {}
    diag["ocean_infinity"] = {}
    for k in ("oi2018", "oi2025"):
        la, lo = fixes[k][:, 0], fixes[k][:, 1]
        rr_ = np.floor((la - G5["south"]) / G5["step"]).astype(int); cc_ = np.floor((lo - G5["west"]) / G5["step"]).astype(int)
        okk = (rr_ >= 0) & (rr_ < G5["rows"]) & (cc_ >= 0) & (cc_ < G5["cols"])
        Hh = np.zeros(p2.shape); np.add.at(Hh, (rr_[okk], cc_[okk]), 1.0)
        sy = 15.0 / (111.2 * G5["step"]); D = ndi.gaussian_filter(Hh, (sy, sy / np.cos(np.radians(-33))))
        D /= D.max(); L = lay[k]; a_, b_ = 0.0, 1e9
        for _ in range(200):
            kap = (a_ + b_) / 2; c = L * np.minimum(1, kap * D)
            a_, b_ = (kap, b_) if (c * km2).sum() < OI_TARGET[k] else (a_, kap)
        oi[k] = L * np.minimum(1, kap * D)
        near = ndi.binary_dilation(L > 0, iterations=2)
        rc, ccl = np.clip(rr_, 0, G5["rows"] - 1), np.clip(cc_, 0, G5["cols"] - 1)
        diag["ocean_infinity"][k] = {"slow_fixes": int(len(la)), "share_in_or_next_to_layer": float((near[rc, ccl] & okk).mean()),
                                     "share_over_phase2": float(((p2[rc, ccl] > 0) & okk).mean()), "layer_km2": float((L * km2).sum()),
                                     "field_km2": float((oi[k] * km2).sum()), "target_km2": OI_TARGET[k],
                                     "layer_cells_at_cap": float((oi[k][L > 0] >= L[L > 0] - 1e-9).mean())}
    a.out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out / "fields.npz", p2=p2.astype(np.float32), sub=sub, f_fig=f_fig.astype(np.float32),
                        f_ter=f_ter.astype(np.float32), w_rho=w_rho.astype(np.float32), oi2018=oi["oi2018"].astype(np.float32),
                        oi2025=oi["oi2025"].astype(np.float32), south=G5["south"], west=G5["west"], step=G5["step"])
    (a.out / "fields.json").write_text(json.dumps(diag, indent=1))
    print(json.dumps(diag, indent=1))


if __name__ == "__main__":
    main()
