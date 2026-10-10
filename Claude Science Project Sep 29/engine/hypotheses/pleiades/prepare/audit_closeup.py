"""Audit of the close-up conditional PDFs (Pete, 9 Oct 2026: "how confident are you that the estimation is
bug free, rigorous and defensible?").

    python audit_closeup.py <runs/pleiades> <module dir> <ocean-data root> <geometry dir> <out dir>

Six checks, each independent of the Rust code path it tests:
  1. integrator   - an independent RK4 (bilinear space, linear time, 1 h step) on the raw GLORYS12 / GlobCurrent
                    daily fields + c * ERA5 u10/v10, against the release tables from export.rs.
  2. surfaces     - an independent evaluation of ln L(s|H) (Pleiades) and ln L(s|C,H) (COSMO) from the tables,
                    against likelihood-surface.f32 and cosmo-surface.f32.
  3. spread       - the OU variance used by likelihood.rs against the GDP-replay empirical rms at every lead time.
  4. drift        - deterministic drift distance and endpoint miss distance inside the 50 / 90 % HDR.
  5. spread swap  - the prior work's spread (5 NM/day random walk + 10 km kernel ~ 30 km per component at 15 d),
                    its windages (0 / 1.25 / 3 %) and its 50:50 pool with 21 March COSMO, on OUR two ocean models.
  6. correlation  - Pleiades and COSMO transport errors correlated at rho = 0, 0.5, 0.8 (the hook assumes 0).
No advection is implemented for the likelihood; the RK4 here is a test oracle only (brief section 8).
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from branch_figure import footnote, hdr_level  # noqa: E402
import closeup_figure as cf  # noqa: E402

R_EARTH = 6371008.8
KM_DEG = 111.195
T_IMP = 1394238300.0                      # impact time used by the surfaces (00:25 UTC 8 Mar)
SCENE = {"PHR_4": 1395548640.0, "PHR_2": 1395548640.0, "PHR_1": 1395548880.0, "PHR_3": 1395548880.0}
FITS = [((0.1153, 0.1176), (6.13, 4.20)), ((0.1043, 0.0955), (16.02, 7.64))]   # run.toml products
MODELS = ["glorys12v1+era5-wind10", "globcurrent-my-p1d+era5-wind10"]
TABLES = ["release-grid", "release-grid-globcurrent-p1d"]


def load_table(run, name):
    m = json.loads((run / f"{name}.json").read_text())
    a = np.fromfile(run / f"{name}.f32", dtype="<f4").reshape(m["nlat"], m["nlon"], m["windage_n"], len(m["out_unix_s"]), 2)
    return m, a


def field(meta_path):
    m = json.loads(Path(meta_path).read_text())
    d = np.memmap(Path(meta_path).with_name(m["data_file"]), dtype="<f4", mode="r").reshape(len(m["time_unix_s"]), len(m["lat"]), len(m["lon"]), 2)
    return d, np.array(m["time_unix_s"]), np.array(m["lat"]), np.array(m["lon"])


def interp(F, t, y, x):
    d, tt, la, lo = F
    k = np.searchsorted(tt, t) - 1; ft = (t - tt[k]) / (tt[k + 1] - tt[k])
    i = np.searchsorted(la, y) - 1; fy = (y - la[i]) / (la[i + 1] - la[i])
    j = np.searchsorted(lo, x) - 1; fx = (x - lo[j]) / (lo[j + 1] - lo[j])
    out = 0.0
    for dk, wk in ((0, 1 - ft), (1, ft)):
        b = d[k + dk, i:i + 2, j:j + 2].astype(float)
        out = out + wk * ((1 - fy) * ((1 - fx) * b[0, 0] + fx * b[0, 1]) + fy * ((1 - fx) * b[1, 0] + fx * b[1, 1]))
    return out


def rk4(cur, wind, lon0, lat0, c, t0, t1, h=3600.0):
    def vel(t, p):
        v = interp(cur, t, p[1], p[0]) + c * interp(wind, t, p[1], p[0])
        return np.array([v[0] / (R_EARTH * np.cos(np.radians(p[1]))), v[1] / R_EARTH]) * 180 / np.pi
    p, t = np.array([lon0, lat0], float), t0
    while t < t1 - 1e-6:
        s = min(h, t1 - t)
        k1 = vel(t, p); k2 = vel(t + s / 2, p + s / 2 * k1); k3 = vel(t + s / 2, p + s / 2 * k2); k4 = vel(t + s, p + s * k3)
        p = p + s / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += s
    return p


def km(x0, y0, x1, y1):
    return np.hypot((x1 - x0) * KM_DEG * np.cos(np.radians((y0 + y1) / 2)), (y1 - y0) * KM_DEG)


def ou_var_km2(mi, dt):
    se, te = FITS[mi]
    return np.array([2 * s * s * (T * 86400) * (dt - T * 86400 * (1 - np.exp(-dt / (T * 86400)))) / 1e6 + 0.25 for s, T in zip(se, te)])


def endpoints_grid(a, ti, LON, LAT):
    x = (LON - 85) / 0.1; y = (LAT + 43) / 0.1
    i = np.floor(x).astype(int); j = np.floor(y).astype(int)
    ok = (i >= 0) & (j >= 0) & (i + 1 < a.shape[1]) & (j + 1 < a.shape[0])
    i = np.clip(i, 0, a.shape[1] - 2); j = np.clip(j, 0, a.shape[0] - 2); fx = x - i; fy = y - j
    out = np.zeros(LAT.shape + (a.shape[2], 2))
    for dj, wy in ((0, 1 - fy), (1, fy)):
        for di, wx in ((0, 1 - fx), (1, fx)):
            out += (wx * wy)[..., None, None] * a[j + dj, i + di, :, ti, :]
    out[~ok] = np.nan
    return out


def resid(X, y):
    de = (y[0] - X[..., 0]) * KM_DEG * np.cos(np.radians((y[1] + X[..., 1]) / 2)); dn = (y[1] - X[..., 1]) * KM_DEG
    return np.stack([de, dn], -1)


def wq(x, w, q):
    o = np.argsort(x); c = np.cumsum(w[o]) / w.sum()
    return [float(x[o][min(np.searchsorted(c, qq), len(c) - 1)]) for qq in q]


def main(runs, module_dir, ocean_root, geom_dir, out):
    runs, M, O, G, out = map(Path, (runs, module_dir, ocean_root, geom_dir, out))
    out.mkdir(parents=True, exist_ok=True)
    tabs = [load_table(runs, n) for n in TABLES]
    OUTS = tabs[0][0]["out_unix_s"]
    T5 = pd.read_csv(M / "data/targets-3km.csv").query("arm == 'rating5'")
    Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    wind = field(O / "era5/era5_u10_v10_3h_15-120E_50-0S_20140307-20141231.json")
    curs = [field(O / "glorys12/glorys12v1_uo_vo_surface_20140307-20140430.json"),
            field(O / "globcurrent/grid/globcurrent_my_p1d_uo_vo_0m-00.json")]
    summary = {}

    # 1. integrator
    rows = []
    for mi, (m, a) in enumerate(tabs):
        rng = np.random.default_rng(10 + mi)
        while sum(r["model"] == MODELS[mi] for r in rows) < 60:
            jj = int(rng.integers(35, 96)); ii = int(rng.integers(55, 106)); kw = int(rng.integers(0, 21)); ti = int(rng.integers(0, 4))
            tb = a[ii, jj, kw, ti]
            if not np.all(np.isfinite(tb)):
                continue
            lon0, lat0 = 85 + 0.1 * jj, -43 + 0.1 * ii
            p = rk4(curs[mi], wind, lon0, lat0, kw * m["windage_step"], m["release_unix_s"], OUTS[ti])
            rows.append(dict(model=MODELS[mi], lon0=lon0, lat0=lat0, windage=kw * m["windage_step"], out_unix_s=OUTS[ti],
                             table_lon=float(tb[0]), table_lat=float(tb[1]), rk4_lon=p[0], rk4_lat=p[1],
                             drift_km=km(lon0, lat0, tb[0], tb[1]), diff_km=km(p[0], p[1], tb[0], tb[1])))
    I = pd.DataFrame(rows); I.to_csv(out / "audit-integrator.csv", index=False)
    summary["integrator"] = I.groupby("model").agg(n=("diff_km", "size"), median_diff_km=("diff_km", "median"),
                                                   max_diff_km=("diff_km", "max"), median_drift_km=("drift_km", "median")).reset_index().to_dict("records")

    # grid
    Zb = np.load(runs / "branch-289/branch-maps.npz"); Zo = np.load(runs / "branch-289-oi2018-2025/branch-maps.npz")
    lat, lon, area = Zb["lat"], Zb["lon"], Zb["area"]
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    EP = {(mi, ti): endpoints_grid(tabs[mi][1], ti, LON, LAT) for mi in (0, 1) for ti in range(4)}

    # 2. surfaces (independent evaluation at random grid points)
    S = np.fromfile(runs / "likelihood-surface.f32", dtype="<f4").reshape(2, 4, 2, 360, 360)
    C = np.fromfile(runs / "cosmo-surface.f32", dtype="<f4").reshape(2, 2, 2, 360, 360)
    rng = np.random.default_rng(3); dP, dC = [], []
    for _ in range(300):
        j, i, mi = int(rng.integers(40, 320)), int(rng.integers(40, 320)), int(rng.integers(0, 2))
        tot = 0.0
        for _, r in T5.iterrows():
            ti = 2 if SCENE[r.scene] == OUTS[2] else 3; v = ou_var_km2(mi, SCENE[r.scene] - T_IMP)
            rr = resid(EP[(mi, ti)][j, i], (r.lon, r.lat))
            tot += r.w_equal * 500 * np.mean(np.exp(-0.5 * np.sum(rr ** 2 / v, -1)) / (2 * np.pi * np.sqrt(v.prod())))
        if np.isfinite(S[mi, 0, 0, j, i]) and tot > 0:
            dP.append(np.log(tot) - S[mi, 0, 0, j, i])
        cs, ps = int(rng.integers(0, 2)), int(rng.integers(0, 2)); v = ou_var_km2(mi, OUTS[ps] - T_IMP)
        rows_c = Cc.iloc[:3] if cs == 0 else Cc; tot = 0.0
        for _, r in rows_c.iterrows():
            rr = resid(EP[(mi, ps)][j, i], (r.longitude, r.latitude))
            tot += 500 / len(rows_c) * np.mean(np.exp(-0.5 * np.sum(rr ** 2 / v, -1)) / (2 * np.pi * np.sqrt(v.prod())))
        if np.isfinite(C[mi, cs, ps, j, i]) and tot > 0:
            dC.append(np.log(tot) - C[mi, cs, ps, j, i])
    summary["surfaces"] = dict(pleiades_n=len(dP), pleiades_max_abs_dlnL=float(np.max(np.abs(dP))),
                               cosmo_n=len(dC), cosmo_max_abs_dlnL=float(np.max(np.abs(dC))))

    # 3. spread vs GDP replay
    gdp = json.loads((M.parents[2] / "results/ocean-transport-error-gdp-replay.json").read_text())
    rows = []
    for mi, cfg in enumerate(("glorys12+0.01era5", "globcurrent-p1d+0.01era5")):
        e = gdp["configs"][cfg]["undrogued/box_MAM"]
        for r in e["rows"]:
            v = ou_var_km2(mi, r["lead_d"] * 86400) - 0.25
            rows.append(dict(model=MODELS[mi], lead_d=r["lead_d"], n=r["n"], rms_e_km=r["rms_e_km"], ou_e_km=float(np.sqrt(v[0])),
                             rms_n_km=r["rms_n_km"], ou_n_km=float(np.sqrt(v[1])), median_2d_km=r["median_km"], p90_2d_km=r["p90_km"]))
        summary.setdefault("gdp_boot95_rms_km_15d", {})[MODELS[mi]] = e["boot95_rms_km_15d"]
    SP = pd.DataFrame(rows); SP.to_csv(out / "audit-spread-vs-gdp.csv", index=False)
    # prior work: 5 NM/day rms random walk (per component) + 10 km kernel
    lead = np.array(gdp["lead_days"], float)
    prior_sd = np.sqrt((5 * 1.852) ** 2 * lead + 10.0 ** 2)

    # 4. drift / miss inside HDR (flight-conditioned P+C4 after full search; transport-only P+C4 before search)
    D = np.nanmean([np.nanmean(km(LON[..., None], LAT[..., None], EP[(mi, 2)][..., 0], EP[(mi, 2)][..., 1]), -1) for mi in (0, 1)], 0)
    miss = []
    for mi in (0, 1):
        per = []
        for ti, sc in ((2, ("PHR_4", "PHR_2")), (3, ("PHR_1", "PHR_3"))):
            X = EP[(mi, ti)]
            per.append(np.min([km(X[..., 0], X[..., 1], r.lon, r.lat) for _, r in T5.iterrows() if r.scene in sc], 0))
        miss.append(np.minimum(*per))
    Miss = np.nanmedian(np.minimum(*miss), -1)
    dnear = np.min([km(LON, LAT, r.lon, r.lat) for _, r in T5.iterrows()], 0)
    rows = []
    for lab, mass in (("flight-conditioned P+C4, after OI 2018 + 2025-26", Zo["post"] * np.nan_to_num(Zo["L_P+C4"])),
                      ("transport-only P+C4, before search", np.nan_to_num(Zb["L_P+C4"]) * area)):
        mm = mass / mass.sum(); dn = mm / area
        for q in (0.5, 0.9):
            sel = (dn >= hdr_level(dn, mm, q)) & np.isfinite(D) & np.isfinite(Miss); w = mm * sel
            rows.append(dict(case=lab, hdr=q, hdr_area_km2=float(area[dn >= hdr_level(dn, mm, q)].sum()),
                             **{f"model_drift_km_q{int(p*100)}": v for p, v in zip((.1, .5, .9), wq(D[sel], w[sel], (.1, .5, .9)))},
                             **{f"miss_km_q{int(p*100)}": v for p, v in zip((.1, .5, .9), wq(Miss[sel], w[sel], (.1, .5, .9)))},
                             **{f"origin_to_pleiades_km_q{int(p*100)}": v for p, v in zip((.1, .5, .9), wq(dnear[sel], w[sel], (.1, .5, .9)))},
                             share_drift_lt_30km=float(w[sel & (D < 30)].sum() / w[sel].sum())))
    pd.DataFrame(rows).to_csv(out / "audit-drift.csv", index=False)

    # common box for 5-6
    box = (LON >= 86) & (LON <= 98) & (LAT >= -40) & (LAT <= -30)
    bi = np.where(box.any(1))[0]; bj = np.where(box.any(0))[0]
    sl = (slice(bi[0], bi[-1] + 1), slice(bj[0], bj[-1] + 1))
    A, LA, LO = area[sl], LAT[sl], LON[sl]
    geo = json.loads((G / "search_footprints.geojson").read_text())
    masks = {"phase2": cf.mask_of(cf.polygons(geo, "atsb_phase2_2014_2017"), LO, LA),
             "oi2018_outline": cf.mask_of(cf.polygons(geo, "oi2018_total_outline_approx"), LO, LA),
             "oi_southeast_band": cf.mask_of(cf.polygons(geo, "oi2024_proposed_outboard_southeast"), LO, LA),
             "oi_northwest_band": cf.mask_of(cf.polygons(geo, "oi2024_proposed_inboard_northwest"), LO, LA)}
    masks["any_past_envelope"] = masks["phase2"] | masks["oi2018_outline"] | masks["oi_southeast_band"]
    Sg = cf.grid_search(runs, "oi2018-2025", LAT.shape)[sl]

    def summ(mass, **lab):
        mm = np.nan_to_num(mass); mm = mm / mm.sum(); dn = mm / A
        s = cf.stats(mm, A, LA, LO, masks)
        return dict(**lab, hdr50_km2=float(A[dn >= hdr_level(dn, mm, 0.5)].sum()), hdr90_km2=s["hdr90_km2"],
                    mode_lat=s["mode_lat"], mode_lon=s["mode_lon"], mean_lat=s["mean_lat"], mean_lon=s["mean_lon"],
                    nw_band=s["mass_in_oi_northwest_band"], outside_past=1 - s["mass_in_any_past_envelope"])

    def single(mi, v, ks, which, passes):
        tot = 0.0
        if which == "P":
            for _, r in T5.iterrows():
                ti = 2 if SCENE[r.scene] == OUTS[2] else 3
                rr = resid(EP[(mi, ti)][sl][..., ks, :], (r.lon, r.lat))
                tot = tot + r.w_equal * np.mean(np.exp(-0.5 * np.sum(rr ** 2 / v, -1)) / (2 * np.pi * np.sqrt(np.prod(v))), -1)
        else:
            for ps in passes:
                for _, r in Cc.iterrows():
                    rr = resid(EP[(mi, ps)][sl][..., ks, :], (r.longitude, r.latitude))
                    tot = tot + 0.25 / len(passes) * np.mean(np.exp(-0.5 * np.sum(rr ** 2 / v, -1)) / (2 * np.pi * np.sqrt(np.prod(v))), -1)
        return tot

    # 5. spread swap
    rows, maps = [], {}
    for sp in ("prior-work 30 km", "measured OU"):
        for wl, ks in (("0/1.25/3 %", [0, 5, 12]), ("0-5 %", list(range(21)))):
            LP, LC = [], []
            for mi in (0, 1):
                v = np.array([900.0, 900.0]) if sp.startswith("prior") else ou_var_km2(mi, OUTS[2] - T_IMP)
                LP.append(single(mi, v, ks, "P", None)); LC.append(single(mi, v, ks, "C", (1,)))
            LPa, LCa = np.mean(LP, 0), np.mean(LC, 0)
            pool = 0.5 * LPa / (LPa * A).sum() + 0.5 * LCa / (LCa * A).sum()
            prod = np.mean([p * c for p, c in zip(LP, LC)], 0)
            for comb, L in (("50:50 pool", pool), ("joint product", prod)):
                rows.append(summ(L * A, spread=sp, windage=wl, combination=comb, cosmo_pass="21 Mar (dusk)", search="none", prior="flat"))
                maps[(sp, wl, comb)] = L * A
    SW = pd.DataFrame(rows); SW.to_csv(out / "audit-spread-swap.csv", index=False)

    # 6. correlated P / C errors
    def joint(mi, rho):
        tot = 0.0
        for ps in (0, 1):
            vC = ou_var_km2(mi, OUTS[ps] - T_IMP)
            RC = [resid(EP[(mi, ps)][sl], (r.longitude, r.latitude)) for _, r in Cc.iterrows()]
            for _, r in T5.iterrows():
                ti = 2 if SCENE[r.scene] == OUTS[2] else 3; vP = ou_var_km2(mi, SCENE[r.scene] - T_IMP)
                rP = resid(EP[(mi, ti)][sl], (r.lon, r.lat))
                lpP = -0.5 * np.sum(rP ** 2 / vP, -1) - np.log(2 * np.pi * np.sqrt(vP.prod()))
                b = rho * np.sqrt(vC / vP); vc = vC * (1 - rho ** 2)
                for rC in RC:
                    dif = rC[..., None, :, :] - b * rP[..., :, None, :]
                    lpC = -0.5 * np.sum(dif ** 2 / vc, -1) - np.log(2 * np.pi * np.sqrt(vc.prod()))
                    tot = tot + r.w_equal * 0.25 * 0.5 * np.mean(np.exp(lpP[..., :, None] + lpC), axis=(-2, -1))
        return tot
    rows = []
    for rho in (0.0, 0.5, 0.8):
        t0 = time.time()
        J = 0.5 * (joint(0, rho) + joint(1, rho))
        if rho == 0.0:
            ref = np.nan_to_num(Zb["L_P+C4"])[sl]; ok = (ref > 0) & (J > 0)
            summary["rho0_vs_branch_lnratio_sd"] = float(np.std(np.log(J[ok]) - np.log(ref[ok])))
        for lab, mass in (("flight-conditioned, after OI 2018 + 2025-26", Zo["post"][sl] * J),
                          ("transport only, after OI 2018 + 2025-26", J * Sg * A), ("transport only, before search", J * A)):
            rows.append(summ(mass, rho=rho, case=lab))
        print(f"rho {rho}: {time.time() - t0:.0f} s", flush=True)
    pd.DataFrame(rows).to_csv(out / "audit-correlation.csv", index=False)
    (out / "audit-summary.json").write_text(json.dumps(summary, indent=1, default=float))
    np.savez_compressed(out / "audit-spread-maps.npz", lat=LA[:, 0], lon=LO[0], area=A,
                        prior_pool=maps[("prior-work 30 km", "0/1.25/3 %", "50:50 pool")],
                        measured_pool=maps[("measured OU", "0/1.25/3 %", "50:50 pool")],
                        prior_lead=lead, prior_sd=prior_sd)
    return summary


def figure(out, module_dir, geom_dir, plt, panel_letter=None):
    """Three panels: (a) GDP replay rms vs the OU kernel vs the prior work's assumed spread; (b) prior-work spread on
    our models (reproduces the prior work's map); (c) the measured spread, otherwise identical."""
    out, M, G = Path(out), Path(module_dir), Path(geom_dir)
    SP = pd.read_csv(out / "audit-spread-vs-gdp.csv"); Z = np.load(out / "audit-spread-maps.npz")
    SW = pd.read_csv(out / "audit-spread-swap.csv")
    geo = json.loads((G / "search_footprints.geojson").read_text())
    T5 = pd.read_csv(M / "data/targets-3km.csv").query("arm == 'rating5'"); Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    fig = plt.figure(figsize=(7.1, 3.0))
    gs = fig.add_gridspec(1, 3, width_ratios=[0.8, 1, 1], wspace=0.28)
    ax = fig.add_subplot(gs[0])
    for mdl, ls, lab in (("glorys12v1+era5-wind10", "-", "GLORYS12"), ("globcurrent-my-p1d+era5-wind10", "--", "GlobCurrent")):
        d = SP[SP.model == mdl]
        ax.plot(d.lead_d, np.sqrt((d.rms_e_km ** 2 + d.rms_n_km ** 2) / 2), "o", ms=2.5, color="black" if ls == "-" else "#777777",
                label=f"GDP replay, {lab}")
        ax.plot(d.lead_d, np.sqrt((d.ou_e_km ** 2 + d.ou_n_km ** 2) / 2), ls, lw=1.0, color="black" if ls == "-" else "#777777",
                label=f"OU kernel used, {lab}")
    ax.plot(Z["prior_lead"], Z["prior_sd"], color="#c0392b", lw=1.2, label="prior work (5 NM/day + 10 km)")
    ax.set_xlabel("Days since release"); ax.set_ylabel("Transport error, rms per component (km)")
    ax.set_xlim(0, 15.5); ax.set_ylim(0, 145); ax.legend(frameon=False, fontsize=5, loc="upper left")
    lat, lon, area = Z["lat"], Z["lon"], Z["area"]
    axs = [fig.add_subplot(gs[1]), fig.add_subplot(gs[2])]
    for a2, key, ttl, sp in ((axs[0], "prior_pool", "Prior-work spread, our models", "prior-work 30 km"),
                             (axs[1], "measured_pool", "Measured spread, our models", "measured OU")):
        m = Z[key] / Z[key].sum(); dn = m / area
        cf.hdr_bands(a2, lon, lat, dn, m); cf.draw_outlines(a2, geo)
        a2.plot(T5.lon, T5.lat, "x", ms=3, color="#b03030", mew=0.7)
        a2.plot(Cc.longitude, Cc.latitude, "o", ms=3, mfc="none", mec="#d35400", mew=0.7)
        r = SW[(SW.spread == sp) & (SW.windage == "0/1.25/3 %") & (SW.combination == "50:50 pool")].iloc[0]
        a2.plot(r.mode_lon, r.mode_lat, "*", ms=6, color="#f0b030", mec="#333333", mew=0.4)
        a2.text(0.02, 0.03, f"90 % area {r.hdr90_km2:,.0f} km²\nmode {abs(r.mode_lat):.2f} S {r.mode_lon:.2f} E",
                transform=a2.transAxes, fontsize=5.5, va="bottom", bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.0))
        a2.set_xlim(88, 96); a2.set_ylim(-38, -32); a2.set_title(ttl, loc="left", fontsize=6.5); a2.set_xlabel("Longitude (°E)")
        a2.set_xticks([88, 90, 92, 94, 96])
    axs[0].set_ylabel("Latitude (°)")
    if panel_letter:
        for a2, l in zip([ax] + axs, "abc"):
            panel_letter(a2, l)
    footnote(fig, [
        "a: GDP replay of 808 undrogued drifter segments (60 drifters), box 80-110 E 45-20 S, March-May starts, current + 1 % ERA5 "
        "(ocean transport, results/ocean-transport-error-gdp-replay.json); bootstrap 95 % at 15 d: 99-121 km east, 89-111 km north (GLORYS12). "
        "Lines: the OU variance likelihood.rs uses (run.toml). Red: the prior work's 5 NM/day random walk plus its 10 km kernel, read per component (an upper bound if 5 NM/day is the 2-D rms).",
        "b-c: transport only, flat prior, no search; Pleiades rating-5 (equal weights) and all four COSMO contacts, 21 March dusk pass, "
        "50:50 pool, windage 0 / 1.25 / 3 % - the prior work's settings - on GLORYS12 + ERA5 and GlobCurrent daily + ERA5 at equal weight. "
        "b uses 30 km per component, inside the 27-37 km the prior work's spread gives at 15 d under its two readings (90 % area 52,823-69,465 km², mode unchanged); c the measured OU spread. Prior work published: 90 % area 57,708 km², mode about 35.3 S 92.2 E.",
        "Shading: 50/90/99 % HDR with black contours of decreasing weight. Conditional on H; no Bayes factor or P(H | data). GlobCurrent daily label provisional (P4).",
    ], width=165, y=-0.02)
    fig.savefig(out / "spread-diagnostic.png", dpi=300, bbox_inches="tight")
    fig.savefig(out / "spread-diagnostic.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:6]), indent=1, default=float))
