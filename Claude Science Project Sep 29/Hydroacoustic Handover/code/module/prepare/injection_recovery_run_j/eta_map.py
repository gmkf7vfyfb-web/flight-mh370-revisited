"""Block 7 eta mapping (prereg.py 'ETA MAPPING'): received level -> P_D per receiver -> P_D(any unblocked receiver) per
run J row -> eta_50 per 00:19 option and p, P_D(any) at the F-35A anchor and per eta decade, eta_50 per latitude band.
TL: as pre-registered -- (i) IMOS loggers: the module's RAM-corrected table (ram_check/imos_tl_ramcorr.csv, five quantile
paths 38.46-31.64 S, source depth 10 m, per band, linear in impact latitude, CLAMPED beyond the span: rows north of 31.64 S
are 'TL extrapolated (clamped)' and their share is reported); (ii) H01W/H08S: block 2 grid pass A (on-arc sources 41-20 S,
source depth 10 m; PROVISIONAL until that track's note is published). A band with no modes / land carries no energy.
Rows north of 20 S are 'TL pending (grid)'.
Rows: 1-in-8 systematic thin of subsample.npz (declared; ESS per option reported).
Usage: python eta_map.py <inputs_dir> <run_out_dir> <out_dir>
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R
from imos_stageB_map import band_fraction

MODULE = HERE.parent.parent
QLAT = {"025": -38.45841, "250": -37.68136, "500": -37.2291, "750": -36.60999, "975": -31.63642}   # data/ocean_paths/request.json


def tl_tables():
    g = pd.read_csv(R.TL_GRID_PASSA); g = g[np.isclose(g.src_depth_m, R.TL_SRC_DEPTH_M)]
    g["receiver"] = g.receiver.astype(str)
    lats = np.array(sorted(g.src_lat.unique()))
    tab = {}
    for rx in R.RECEIVERS:
        T = np.full((len(lats), len(R.BANDS_HZ)), np.nan)
        for i, la in enumerate(lats):
            gi = g[(g.receiver == rx) & np.isclose(g.src_lat, la)]
            for j, fc in enumerate(R.BANDS_HZ):
                r = gi[np.isclose(gi.fc_hz, fc) & (gi.status == "ok")]
                if len(r):
                    T[i, j] = float(r.tl_db.median())
        tab[rx] = T
    # IMOS: the module's RAM-corrected TL at the five quantile paths (per band), by quantile-path latitude
    rc = pd.read_csv(MODULE / "results-data" / "ram_check" / "imos_tl_ramcorr.csv", dtype={"quantile": str, "logger": str})
    rc = rc[np.isclose(rc.src_depth_m, R.TL_SRC_DEPTH_M)]
    delta = {}
    for lg in ("3376", "3274", "3315", "3275"):
        ql = np.array([QLAT[q] for q in sorted(QLAT)]); D = np.full((len(ql), len(R.BANDS_HZ)), np.nan)
        for i, q in enumerate(sorted(QLAT)):
            for j, fc in enumerate(R.BANDS_HZ):
                r = rc[(rc.logger == lg) & (rc["quantile"] == q) & np.isclose(rc.fc_hz, fc)]
                if len(r) and np.isfinite(r.tl_db).any():
                    D[i, j] = float(r.tl_db.median())
        delta[lg] = (ql, D)
    return lats, tab, delta


def tl_for_rows(lat, rx, lats, tab, delta):
    """TL per band for impact latitudes. IMOS: RAM-corrected quantile-path table, linear in latitude, clamped (NaN band = no
    energy). IMS: grid pass A, linear in latitude on the grid; NaN where the nearest grid node is blocked."""
    if rx in delta:
        ql, D = delta[rx]; la = np.clip(lat, ql.min(), ql.max()); out = np.empty((len(lat), D.shape[1]))
        for j in range(D.shape[1]):
            col = D[:, j]; ok = np.isfinite(col)
            out[:, j] = np.interp(la, ql[ok], col[ok]) if ok.sum() >= 2 else np.nan
        return out
    T = tab[rx]; out = np.empty((len(lat), T.shape[1]))
    la = np.clip(lat, lats.min(), lats.max())
    for j in range(T.shape[1]):
        col = T[:, j]; ok = np.isfinite(col)
        v = np.interp(la, lats[ok], col[ok]) if ok.sum() >= 2 else np.full(len(la), np.nan)
        near = np.abs(la[:, None] - lats[None, :]).argmin(1)
        out[:, j] = np.where(ok[near], v, np.nan)
    return out


def main(inputs_dir, run_dir, out_dir):
    inputs_dir, run_dir, out = Path(inputs_dir), Path(run_dir), Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    S0 = np.load(inputs_dir / "subsample.npz"); inp = json.load(open(inputs_dir / "inputs.json"))
    THIN = 8   # declared: a further 1-in-8 systematic thin of the saved subsample for the bisection (run time); ESS reported per option
    S = {k: S0[k][::THIN] for k in S0.files}
    summ = json.load(open(run_dir / "summary.json")); fits = json.load(open(run_dir / "fits.json"))
    taus = [float(v) for v in summ["taus"]]
    lat = S["lat"].astype(float); E = S["E_j"].astype(float); tau = S["tau90_s"].astype(float)
    n = len(lat); rng = np.random.default_rng([R.SEED, R.BLOCK, 99]); calL = rng.normal(0, R.CAL_L_SD_DB, n)
    lats, tab, delta = tl_tables()
    # band fractions on a tau grid, interpolated per row
    tgrid = np.logspace(np.log10(0.02), np.log10(30), 60)
    SB = np.vstack([band_fraction(fc, 1.0 / tgrid, 2.0) for fc in R.BANDS_HZ]).T      # [tgrid, band]
    tau_c = np.clip(tau, tgrid[0], tgrid[-1]); lt = np.log10(tau_c)
    Sb = np.vstack([np.interp(lt, np.log10(tgrid), SB[:, j]) for j in range(len(R.BANDS_HZ))]).T   # [n, band]
    # per receiver: received-energy factor without eta: F_r = E * rho c / (2 pi) * sum_b Sb 10^(-TL/10) / T_eff   -> SPL = 10log10(eta F_r / 1e-12)
    F = {}; blocked = {}; teff = {}
    for rx in R.RECEIVERS:
        TL = tl_for_rows(lat, rx, lats, tab, delta)
        te = summ["t_eff_s"][rx]; teff[rx] = {t: float(np.mean([v for k, v in te.items() if abs(float(k.split("|")[1]) - t) < 1e-9])) for t in taus}
        ti = np.abs(np.log(tau_c)[:, None] - np.log(np.array(taus))[None, :]).argmin(1)
        te_row = np.array([teff[rx][taus[i]] for i in ti])
        tlin = np.nan_to_num(10 ** (-TL / 10), nan=0.0)
        F[rx] = E * R.RHO_C / (2 * np.pi) * (Sb * tlin).sum(1) / te_row
        blocked[rx] = ~np.isfinite(TL).any(1)
    north_pending = lat > -20.0
    # P_D(level) per receiver from this block's fits (primary method), tau cell nearest
    def pd_level(rx, lev, ti, alpha):
        p = np.zeros(len(lev))
        for i, t in enumerate(taus):
            f = fits.get(f"{rx}|{R.PRIMARY_METHOD}|{alpha}|{t}", {})
            m = ti == i
            if not f.get("resolvable", False) or f.get("L50_re_noise_db") is None:
                # unreached: use the fitted curve anyway if the fit exists, else zero
                l50, s = f.get("L50_re_noise_db"), f.get("slope_db")
                if l50 is None:
                    # fall back: logistic through the top-of-grid P_D (declared); zero if no fit
                    p[m] = 0.0; continue
            l50, s = f["L50_re_noise_db"], f["slope_db"]
            p[m] = 1 / (1 + np.exp(-(lev[m] - l50) / s))
        return p
    ti = np.abs(np.log(tau_c)[:, None] - np.log(np.array(taus))[None, :]).argmin(1)
    bmed = {rx: summ["bg_median_level_db"][rx] + summ["abs_offset_db"][rx] for rx in R.RECEIVERS}   # absolute: dB re 1 uPa, 5-40 Hz, 1 s
    def pd_any(eta, alpha, with_cal, receivers=R.RECEIVERS):
        q = np.ones(n)
        for rx in receivers:
            spl = 10 * np.log10(np.maximum(eta * F[rx], 1e-300) / 1e-12)
            if with_cal:
                spl = spl + calL
            if rx in ("H01W", "H08S"):
                spl = spl + R.TRIAD_GAIN_DB
            snr = spl - bmed[rx]
            p = pd_level(rx, snr, ti, alpha); p[blocked[rx]] = 0.0
            q *= (1 - p)
        return 1 - q
    def weights(o, p):
        w = np.exp(S[f"lnw_{o}"].astype(float)); f = np.ones(n); dr, ts = S["pf_drawn"], S["pf_surface"]
        f[dr & ts] = 2 * p; f[dr & ~ts] = 2 * (1 - p); w = w * f
        w[~np.isfinite(tau) | north_pending] = 0.0
        return w / w.sum()
    def eta50(w, alpha, with_cal, receivers=R.RECEIVERS):
        lo, hi = np.log10(R.ETA_BOUNDS[0]), np.log10(R.ETA_BOUNDS[1])
        f_lo = np.sum(w * pd_any(10 ** lo, alpha, with_cal, receivers)) - 0.5; f_hi = np.sum(w * pd_any(10 ** hi, alpha, with_cal, receivers)) - 0.5
        if f_hi < 0:
            return None, float(f_hi + 0.5)
        if f_lo > 0:
            return float(10 ** lo), float(f_lo + 0.5)
        for _ in range(28):
            mid = 0.5 * (lo + hi); fm = np.sum(w * pd_any(10 ** mid, alpha, with_cal, receivers)) - 0.5
            if fm > 0: hi = mid
            else: lo = mid
        return float(10 ** (0.5 * (lo + hi))), None
    res = {"method": R.PRIMARY_METHOD, "taus": taus, "n_rows": int(n), "thin": THIN, "ess": {}, "share_north_of_20S_pending": float(north_pending.mean()),
           "blocked_share": {rx: float(blocked[rx].mean()) for rx in R.RECEIVERS}, "t_eff_s": teff, "tl_source": "IMOS: module RAM-corrected quantile-path table (clamped beyond 38.46-31.64 S); H01W/H08S: block 2 grid pass A (provisional)", "share_tl_extrapolated_imos": float((lat > -31.63642).mean()),
           "bg_median_abs_db_re_uPa": None, "eta50": {}, "pd_any_at_anchor": {}, "pd_any_by_decade": {}, "eta50_by_lat_band": {}, "eta50_by_receiver": {}}
    res["bg_median_abs_db_re_uPa"] = bmed
    decades = [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    for o in R.OPTIONS:
        for p in R.PS:
            key = f"{o}/p{p:g}"; w = weights(o, p); res["ess"][key] = float(1.0 / np.sum(w ** 2))
            for alpha in (R.ALPHA_PRIMARY, 0.05, 0.001):
                for wc in (False, True):
                    tag = f"{key}|alpha{alpha}|{'cal' if wc else 'nocal'}"
                    e50, pdmax = eta50(w, alpha, wc)
                    res["eta50"][tag] = dict(eta50=e50, pd_any_max_at_1e_2=pdmax)
                    res["pd_any_at_anchor"][tag] = float(np.sum(w * pd_any(R.ETA_ANCHOR, alpha, wc)))
                    res["pd_any_by_decade"][tag] = {f"{d:.0e}": float(np.sum(w * pd_any(d, alpha, wc))) for d in decades}
            print("eta50", key, res["eta50"][f"{key}|alpha{R.ALPHA_PRIMARY}|nocal"], flush=True)
    # per receiver eta50 (D0' p 0.5, primary alpha, no cal)
    w = weights("D0", 0.5)
    for rx in R.RECEIVERS:
        e50, pdmax = eta50(w, R.ALPHA_PRIMARY, False, [rx]); res["eta50_by_receiver"][rx] = dict(eta50=e50, pd_max_at_1e_2=pdmax, pd_at_anchor=float(np.sum(w * pd_any(R.ETA_ANCHOR, R.ALPHA_PRIMARY, False, [rx]))))
    # per latitude band (D0', p 0.5): eta50 within the band, weights renormalised in the band
    edges = np.arange(-41.0, -19.99, 1.0); rows = []
    for a in edges:
        m = (lat >= a) & (lat < a + 1.0); wb = w * m
        if wb.sum() <= 0 or m.sum() < 200:
            rows.append(dict(lat_lo=a, lat_hi=a + 1, share=float(wb.sum()), n=int(m.sum()), eta50=None, pd_any_at_anchor=None)); continue
        wb = wb / wb.sum(); e50, pdmax = eta50(wb, R.ALPHA_PRIMARY, False)
        rows.append(dict(lat_lo=a, lat_hi=a + 1, share=float((w * m).sum()), n=int(m.sum()), eta50=e50, pd_any_max=pdmax, pd_any_at_anchor=float(np.sum(wb * pd_any(R.ETA_ANCHOR, R.ALPHA_PRIMARY, False)))))
    pd.DataFrame(rows).to_csv(out / "eta50_by_lat_band.csv", index=False)
    res["eta50_by_lat_band"] = rows
    json.dump(res, open(out / "eta_map.json", "w"), indent=1)
    print("done")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
