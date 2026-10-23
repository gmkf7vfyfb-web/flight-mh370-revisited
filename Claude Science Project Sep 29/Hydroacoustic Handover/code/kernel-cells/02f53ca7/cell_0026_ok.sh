cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; cat >> tl_recal_block9.py <<'EOF'
# Usage:
#   python tl_recal_block9.py sections <audit_scripts_dir> <shared_products_dir> <sections_out>
#   python tl_recal_block9.py tl <sections_dir> <at_bin> <scratch> <out> [nproc]        (air9 shared+builder, air8, air7 offsets)
#   python tl_recal_block9.py route1 <audit_residuals.csv> <ew0112_results_dir> <out>
#   python tl_recal_block9.py air8 <out>
#   python tl_recal_block9.py air7 <out> <nx2d_corridor.csv> <airgun_sites_confirm_dir>
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Geod

sys.path.insert(0, str(Path(__file__).resolve().parent))
import air9_tl_validation as A  # noqa: E402
import kraken_tl as K  # noqa: E402
from air9_ew0112 import score as ew_score  # noqa: E402  (C1 grading: level/slope/shape, same thresholds)

G = Geod(ellps="WGS84")
C_REF = 1500.0
STATIONS = {"H01W": ((-34.890303, 114.142637), 1055.0), "H08S": ((-7.639380, 72.483828), 1376.0)}
SITES = {  # shot-count weighted mean positions (data/blackman/blackman_shot_lines.csv; air9 = EW0112 p. 5 midpoint)
    "air9": dict(pos=(-27.5612, 98.8821), heading=111.2),
    "air8": dict(segs=[((-23.416667, 88.188333), (-23.426667, 88.221667), 11), ((-23.426667, 88.225), (-23.428333, 88.231667), 7)]),
    "air7": dict(segs=[((-22.925, 87.046667), (-22.91, 87.011667), 16), ((-22.91, 87.011667), (-22.905, 87.0), 14)]),
}
ALL_BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0, 80.0]
AIR7_BANDS = [16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0]
AIR8_BANDS = [16.0, 20.0, 25.0, 31.5, 40.0, 50.0]
OFFSETS_KM = [-20.0, -10.0, -5.0, 0.0, 5.0, 10.0, 20.0]
ZS = [9.0, 10.0, 12.0]


def site_pos_heading(site):
    s = SITES[site]
    if "pos" in s:
        return s["pos"], s["heading"]
    w = np.array([n for _, _, n in s["segs"]], float)
    mids = np.array([((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b, _ in s["segs"]])
    az = np.array([G.inv(a[1], a[0], b[1], b[0])[0] % 360 for a, b, _ in s["segs"]])
    return tuple((mids * w[:, None]).sum(0) / w.sum()), float((az * w).sum() / w.sum())


# ----------------------------------------------------------------------------------------------- sections
def offset_section(src, rcv, d_max_km, ds_km=0.5):
    """Bathymetry along the geodesic displaced laterally by d(s) = d_max sin(pi s / R) (positive = right of azimuth)."""
    import nx2d as N
    az12, _, R = G.inv(src[1], src[0], rcv[1], rcv[0])
    n = int(R / 1000.0 / ds_km) + 1
    s = np.linspace(0.0, R, n)
    lon, lat, _ = G.fwd(np.full(n, src[1]), np.full(n, src[0]), np.full(n, az12), s)
    az_loc = np.array(G.inv(lon[:-1], lat[:-1], lon[1:], lat[1:])[0]); az_loc = np.append(az_loc, az_loc[-1])
    d = d_max_km * 1000.0 * np.sin(np.pi * s / R)
    lo2, la2, _ = G.fwd(lon, lat, az_loc + 90.0, d)
    return pd.DataFrame(dict(range_km=s / 1000.0, lat=la2, lon=lo2, elevation_m=N.elevation(la2, lo2), offset_m=d,
                             tid=np.nan, corridor_max_elevation_m=np.nan)), R / 1000.0


def cmd_sections(audit_scripts, shared_products, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, audit_scripts); import paths as AP  # audit path builder (GEBCO 3x3 median, WOA23 95A4)
    import shared_paths as SP
    log = {}
    for st in STATIONS:
        log[f"shared_air9_{st}"] = SP.convert(Path(shared_products), out / "shared", f"air9-{st}") if (out / "shared").mkdir(parents=True, exist_ok=True) is None else None
    for site in ("air9", "air8", "air7"):
        pos, hd = site_pos_heading(site)
        log[f"{site}_pos_heading"] = (pos, hd)
        for st, (rpos, _) in STATIONS.items():
            if site == "air7" and st != "H01W":
                continue
            L, sh = AP.build(f"{site}_{st}", pos, rpos, "95A4", 10, out / "builder")
            log[f"builder_{site}_{st}"] = dict(range_km=L, shallowest_m=sh)
    pos, _ = site_pos_heading("air7")
    for d in OFFSETS_KM:
        b, R = offset_section(pos, STATIONS["H01W"][0], d)
        b.to_csv(out / "builder" / f"bathy_air7off{d:+.0f}_H01W.csv", index=False)
        log[f"air7_offset_{d:+.0f}"] = dict(range_km=R, shallowest_m=float(b.elevation_m.max()),
                                           crest_lat=float(b.lat[b.elevation_m.idxmax()]), crest_lon=float(b.lon[b.elevation_m.idxmax()]))
    json.dump(log, open(out / "sections.json", "w"), indent=1, default=str)
    print(json.dumps(log, indent=1, default=str))


# ----------------------------------------------------------------------------------------------- TL jobs
def tl_job(a):
    tag, bathy_csv, ssp_csv, fc, zs, rd, work, at = a
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    bathy = pd.read_csv(bathy_csv); ssp = pd.read_csv(ssp_csv)
    rprof, profiles = A.build_profiles(bathy, ssp)
    L = float(rprof[-1]); root = f"{tag}_f{fc:g}".replace(".", "p")
    t0 = time.time()
    try:
        K.tl_path(work, root, fc, profiles, rprof, np.array([L]), zs, [rd], A.BOTTOMS["hard"], at, fg=A.FG)
        s = K.read_shd(Path(work) / f"{root}.shd"); x = L / 6371.0; sph = 10 * np.log10(x / np.sin(x))
        import re
        nm = [int(v) for v in re.findall(r"Number of modes\s*=\s*(\d+)", (Path(work) / f"{root}.prt").read_text(errors="replace"))]
        rows = [dict(tag=tag, fc_hz=fc, src_depth_m=float(z), rcv_depth_m=rd, range_km=L, tl_db=float(-20 * np.log10(np.abs(s["p"][0, j, 0, -1])) + sph),
                     blocked=False, n_modes_min=min(nm) if nm else -1, min_profile_depth_m=float(min(p[0] for p in profiles)), wall_s=time.time() - t0) for j, z in enumerate(s["sz"])]
    except RuntimeError as e:
        why = "no modes" if "No modes" in str(e) else str(e).splitlines()[0][:80]
        rows = [dict(tag=tag, fc_hz=fc, src_depth_m=float(z), rcv_depth_m=rd, range_km=L, tl_db=np.inf, blocked=True, n_modes_min=0,
                     min_profile_depth_m=float(min(p[0] for p in profiles)), wall_s=time.time() - t0, reason=why) for z in zs]
    for p in Path(work).glob(f"{root}.*"):
        if p.suffix in (".shd", ".mod"):
            p.unlink()
    return rows


def cmd_tl(sections, at, scratch, out, nproc=4):
    sec = Path(sections); out = Path(out); out.mkdir(parents=True, exist_ok=True); Path(scratch).mkdir(parents=True, exist_ok=True)
    jobs = []
    for st, (_, rd) in STATIONS.items():
        for fc in ALL_BANDS:   # route 1: shared sections, 3 source depths
            jobs.append((f"shared_air9_{st}", sec / "shared" / f"bathy_air9_{st}.csv", sec / "shared" / f"ssp_air9_{st}.csv", fc, ZS, rd, scratch, at))
        for fc in sorted(set(AIR8_BANDS) | {12.5}):   # step b: builder sections, both sites, 10 m (+ 12.5 Hz pipeline check)
            for site in ("air9", "air8"):
                jobs.append((f"builder_{site}_{st}", sec / "builder" / f"bathy_{site}_{st}.csv", sec / "builder" / f"ssp_{site}_{st}.csv", fc, [10.0], rd, scratch, at))
    rd = STATIONS["H01W"][1]
    for d in OFFSETS_KM:   # step d2: air7 offset paths (d = 0 is the geodesic), 10 m
        for fc in AIR7_BANDS:
            jobs.append((f"air7off{d:+.0f}_H01W", sec / "builder" / f"bathy_air7off{d:+.0f}_H01W.csv", sec / "builder" / f"ssp_air7_H01W.csv", fc, [10.0], rd, scratch, at))
    for fc in AIR7_BANDS:   # air9 -> H01W on the builder at the air7 bands (for the difference), 10 m
        jobs.append((f"builder_air9_H01W_a7b", sec / "builder" / "bathy_air9_H01W.csv", sec / "builder" / "ssp_air9_H01W.csv", fc, [10.0], rd, scratch, at))
    t0 = time.time(); rows = []
    with Pool(int(nproc)) as P:
        for i, r in enumerate(P.imap_unordered(tl_job, jobs)):
            rows += r
            if i % 20 == 0:
                print(f"{i + 1}/{len(jobs)} {time.time() - t0:.0f} s", flush=True)
    T = pd.DataFrame(rows); T.to_csv(out / "tl_runs.csv", index=False)
    json.dump(dict(n_jobs=len(jobs), wall_s=time.time() - t0, nproc=int(nproc)), open(out / "wall_tl.json", "w"), indent=1)
    print(T.groupby("tag").agg(n=("fc_hz", "size"), blocked=("blocked", "sum"), wall=("wall_s", "sum")).to_string())


# ----------------------------------------------------------------------------------------------- route 1
def array_layout(csv):
    L = pd.read_csv(csv)
    return L.ahead_m.values, L.across_m.values, L.vol.values.astype(float)


def dref_array(fc, zs, xh, zh, R1m, xg, yg, w):
    f = np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 200); k = 2 * np.pi * f / C_REF
    p = 0
    for ax, ay, wg in zip(xg, yg, w):
        r1 = np.sqrt((xh - ax) ** 2 + ay ** 2 + (zh - zs) ** 2); r2 = np.sqrt((xh - ax) ** 2 + ay ** 2 + (zh + zs) ** 2)
        p = p + wg * (np.exp(1j * k * r1) / r1 - np.exp(1j * k * r2) / r2)
    return 10 * np.log10(np.mean(np.abs(p / w.sum()) ** 2) * R1m ** 2)


def array_factor(fc, phi_deg, xg, yg, w, sign=1):
    f = np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 200); k = 2 * np.pi * f / C_REF
    phi = np.radians(phi_deg); u = (np.cos(phi), sign * np.sin(phi))
    af = np.abs(sum(wg * np.exp(-1j * k * (u[0] * ax + u[1] * ay)) for ax, ay, wg in zip(xg, yg, w))) ** 2 / w.sum() ** 2
    return 10 * np.log10(np.mean(af))


def ols(fc, r):
    x = np.log2(fc); Am = np.vstack([x, np.ones_like(x)]).T; c, res, _, _ = np.linalg.lstsq(Am, r, rcond=None); e = r - Am @ c
    se = np.sqrt(e @ e / max(len(r) - 2, 1) / ((x - x.mean()) ** 2).sum()) if len(r) > 2 else np.nan
    return float(c[0]), float(se), e


def cmd_route1(resid_csv, ew_dir, out):
    out = Path(out); ew = Path(ew_dir)
    T = pd.read_csv(out / "tl_runs.csv")
    Rr = pd.read_csv(resid_csv); M1 = Rr[Rr.model == "M1"]
    ball = pd.read_csv(ew / "ew0112_fig2_ball_spectra_bands_DIGITISED.csv")
    R1m = float(json.load(open(ew / "ew0112_fig2_scaling.json"))["R1m_mean_m"])
    xg, yg, vol = array_layout(ew / "ewing_20gun_layout_ofr95228.csv")
    weights = {"V^(1/3)": vol ** (1 / 3), "equal": np.ones_like(vol)}
    readable = ball.groupby("fc_hz").readable.all()
    lvl = ball.pivot(index="fc_hz", columns="shot", values="level_db_re_1upa2_hz_at_receiver")
    ball_sets = {"both": lvl.mean(axis=1), **{f"shot {c}": lvl[c] for c in lvl.columns}}
    pos9, hd9 = site_pos_heading("air9")
    # pipeline check: shared 10 m against the audit M1 model TL
    chk = []
    for st in STATIONS:
        m = T[(T.tag == f"shared_air9_{st}") & (T.src_depth_m == 10.0)].set_index("fc_hz").tl_db
        a = M1[(M1.station == st) & (M1.src_depth_m == 10.0)].set_index("fc_hz").model_tl_db
        d = (m.reindex(a.index) - a); chk.append(dict(station=st, max_abs_diff_db=float(d.abs().max()), bands=len(a)))
    model_tl = T[T.tag.str.startswith("shared_air9")].copy(); model_tl["station"] = model_tl.tag.str[-4:]
    model_tl.to_csv(out / "route1_tl_model.csv", index=False)
    rows, grades = [], []
    for st, (rpos, _) in STATIONS.items():
        bearing = G.inv(pos9[1], pos9[0], rpos[1], rpos[0])[0] % 360; phi = bearing - hd9
        obs = M1[(M1.station == st) & (M1.src_depth_m == 10.0)].set_index("fc_hz").obs_tl_db
        fcs = np.array([f for f in obs.index if readable.get(f, False)])
        for zs in ZS:
            tl = T[(T.tag == f"shared_air9_{st}") & (T.src_depth_m == zs)].set_index("fc_hz").tl_db.reindex(fcs).values
            for wname, w in weights.items():
                for sign in (1, -1):
                    af = np.array([array_factor(f, phi, xg, yg, w, sign) for f in fcs])
                    for xh in (20, 30, 40):
                        for zh in (5, 10, 15, 20, 30):
                            dref = np.array([dref_array(f, zs, xh, zh, R1m, xg, yg, w) for f in fcs])
                            for bname, bs in ball_sets.items():
                                S0 = bs.reindex(fcs).values + 20 * np.log10(R1m) - dref
                                rl_pred = S0 + af - tl
                                for slb in (230.0, 235.0, 240.0):
                                    rl_obs = slb - obs.reindex(fcs).values; r = rl_obs - rl_pred
                                    nominal = (zs == 10.0 and wname == "V^(1/3)" and sign == 1 and xh == 30 and zh == 15 and bname == "both" and slb == 235.0)
                                    for f_, o_, p_, r_, s0_, af_, d_ in zip(fcs, rl_obs, rl_pred, r, S0, af, dref):
                                        rows.append(dict(station=st, zs=zs, weights=wname, sign=sign, xh=xh, zh=zh, ball=bname, SL_B=slb, fc_hz=f_,
                                                         rl_obs_db=o_, rl_pred_db=p_, r_db=r_, S0_db=s0_, af_db=af_, dref_db=d_, nominal=nominal))
                                    sc = ew_score(r, fcs); sl, se, _ = ols(fcs, r)
                                    grades.append(dict(station=st, zs=zs, weights=wname, sign=sign, xh=xh, zh=zh, ball=bname, SL_B=slb, nominal=nominal, slope_se=se, **sc))
    Rw = pd.DataFrame(rows); Gd = pd.DataFrame(grades)
    # common-mode removal on shared bands (every configuration)
    keys = ["zs", "weights", "sign", "xh", "zh", "ball", "SL_B"]
    cm_rows, cm_grades = [], []
    for kv, g in Rw.groupby(keys):
        pv = g.pivot(index="fc_hz", columns="station", values="r_db").dropna()
        c = pv.mean(axis=1); fcs = pv.index.values
        for st in pv.columns:
            rt = (pv[st] - c).values
            cm_grades.append(dict(**dict(zip(keys, kv)), station=st, view="common-mode removed", **ew_score(rt, fcs), slope_se=ols(fcs, rt)[1]))
            for f_, v_ in zip(fcs, rt):
                cm_rows.append(dict(**dict(zip(keys, kv)), station=st, fc_hz=f_, r_tilde_db=v_, common_mode_db=float(c[f_])))
        cm_grades.append(dict(**dict(zip(keys, kv)), station="both", view="common mode c_b", **ew_score(c.values, fcs), slope_se=ols(fcs, c.values)[1]))
    CM = pd.DataFrame(cm_grades); CMr = pd.DataFrame(cm_rows)
    Rw.to_csv(out / "route1_residuals.csv", index=False); Gd.to_csv(out / "route1_grades.csv", index=False)
    CMr.to_csv(out / "route1_common_mode_residuals.csv", index=False); CM.to_csv(out / "route1_common_mode_grades.csv", index=False)
    # decision rule
    nom = Gd[Gd.nominal].set_index("station")
    both_slope = all(nom.loc[s, "g_slope"] != "FAIL" for s in STATIONS)
    both_shape = all(nom.loc[s, "g_shape"] != "FAIL" for s in STATIONS)
    base = Gd[(Gd.weights == "V^(1/3)") & (Gd.sign == 1) & (Gd.ball == "both")]
    level_ok = all(((base[(base.station == s) & (base.zs == 10.0) & (base.xh == 30) & (base.zh == 15)].g_level != "FAIL").any()) for s in STATIONS)
    grid = base[base.SL_B == 235.0].groupby(["zs", "xh", "zh"]).g_slope.apply(lambda s: (s != "FAIL").all())
    frac = float(grid.mean())
    one_only = (sum(nom.loc[s, "g_slope"] != "FAIL" for s in STATIONS) == 1) and all(abs(nom.loc[s, "slope"]) <= 4.5 for s in STATIONS)
    if both_slope and both_shape and level_ok and frac >= 2 / 3:
        verdict = "EXPLAINED"
    elif (both_slope and both_shape and level_ok) or one_only:
        verdict = "PARTLY EXPLAINED"
    else:
        verdict = "NOT EXPLAINED"
    V = dict(verdict=verdict, nominal={s: {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in nom.loc[s].items() if k in ("n", "level", "slope", "slope_se", "shape", "g_level", "g_slope", "g_shape")} for s in STATIONS},
             grid_fraction_slope_both_ok=frac, n_grid=int(len(grid)), level_not_fail_some_SLB=level_ok, pipeline_check=chk,
             common_mode_nominal=CM[(CM.zs == 10.0) & (CM.weights == "V^(1/3)") & (CM.sign == 1) & (CM.xh == 30) & (CM.zh == 15) & (CM.ball == "both") & (CM.SL_B == 235.0)][["station", "view", "n", "level", "slope", "slope_se", "shape", "g_level", "g_slope", "g_shape"]].to_dict("records"),
             R1m_m=R1m, bands={s: [float(f) for f in Rw[(Rw.station == s) & Rw.nominal].fc_hz] for s in STATIONS})
    json.dump(V, open(out / "route1_verdict.json", "w"), indent=1, default=float)
    print(json.dumps(V, indent=1, default=float))


# ----------------------------------------------------------------------------------------------- step b
def cmd_air8(out, ew_dir):
    out = Path(out); T = pd.read_csv(out / "tl_runs.csv"); ew = Path(ew_dir)
    xg, yg, vol = array_layout(ew / "ewing_20gun_layout_ofr95228.csv"); w = vol ** (1 / 3)
    rows = []
    for st, (rpos, _) in STATIONS.items():
        d = {}
        for site in ("air9", "air8"):
            pos, hd = site_pos_heading(site); phi = (G.inv(pos[1], pos[0], rpos[1], rpos[0])[0] % 360) - hd
            tl = T[(T.tag == f"builder_{site}_{st}") & (T.src_depth_m == 10.0)].set_index("fc_hz").tl_db
            d[site] = dict(tl=tl, af={f: array_factor(f, phi, xg, yg, w) for f in AIR8_BANDS}, phi=phi, heading=hd)
        for f in AIR8_BANDS:
            D = (d["air8"]["af"][f] - d["air8"]["tl"][f]) - (d["air9"]["af"][f] - d["air9"]["tl"][f])
            rows.append(dict(station=st, fc_hz=f, tl_air9_db=d["air9"]["tl"][f], tl_air8_db=d["air8"]["tl"][f], af_air9_db=d["air9"]["af"][f], af_air8_db=d["air8"]["af"][f],
                             rl_diff_air8_minus_air9_db=D, tl_diff_only_db=-(d["air8"]["tl"][f] - d["air9"]["tl"][f]), heading_air8=d["air8"]["heading"], heading_air9=d["air9"]["heading"]))
    R = pd.DataFrame(rows); R.to_csv(out / "air8_recal.csv", index=False)
    med = R.groupby("station").rl_diff_air8_minus_air9_db.median()
    h01 = "FOLLOWS" if med["H01W"] <= -10 else ("DOES NOT" if med["H01W"] >= -3 else "INCONCLUSIVE")
    h08 = "CONSISTENT" if abs(med["H08S"]) <= 5 else "INCONSISTENT"
    V = dict(median_rl_diff_db=med.to_dict(), H01W=h01, H08S=h08, still_holds=(h01 == "FOLLOWS" and h08 == "CONSISTENT"),
             median_tl_diff_only_db=(-R.groupby("station").tl_diff_only_db.median()).to_dict(), headings=dict(air8=float(R.heading_air8.iloc[0]), air9=float(R.heading_air9.iloc[0])))
    json.dump(V, open(out / "air8_recal_verdict.json", "w"), indent=1, default=float); print(json.dumps(V, indent=1, default=float))


# ----------------------------------------------------------------------------------------------- step d
def cmd_air7(out, corridor_csv, confirm_dir):
    out = Path(out); T = pd.read_csv(out / "tl_runs.csv"); cf = Path(confirm_dir)
    o7 = pd.read_csv(cf / "fig23_CL_air7_bands_DIGITISED.csv").set_index("fc_hz").tl_obs_db
    o9 = pd.read_csv(cf / "fig23_CL_air9_bands_DIGITISED.csv").set_index("fc_hz").tl_obs_db
    a9 = T[(T.tag == "builder_air9_H01W_a7b")].set_index("fc_hz").tl_db
    off = T[T.tag.str.startswith("air7off")].copy(); off["d_km"] = off.tag.str.extract(r"air7off([+-]\d+)_")[0].astype(float)
    pv = off.pivot(index="fc_hz", columns="d_km", values="tl_db")
    cor = pd.read_csv(corridor_csv) if corridor_csv and Path(corridor_csv).exists() else None
    rows = []
    for f in AIR7_BANDS:
        least = float(pv.loc[f].min()); dmin = float(pv.loc[f].idxmin())
        r = dict(fc_hz=f, tl_geo_db=float(pv.loc[f, 0.0]), tl_least_loss_db=least, d_least_km=dmin, tl_air9_H01W_db=float(a9[f]),
                 dtl_obs_db=float(o7.get(f, np.nan) - o9.get(f, np.nan)), tl_obs_air7_db=float(o7.get(f, np.nan)))
        for d in OFFSETS_KM:
            r[f"tl_off{d:+.0f}_db"] = float(pv.loc[f, d])
        if cor is not None and (cor.fc_hz == f).any():
            c = cor[(cor.fc_hz == f) & (cor.src_depth_m == 10.0)].iloc[0]
            r.update(tl_nx2d_db=float(c.tl_nx2d_db), open_weight=float(c.open_weight))
        rows.append(r)
    R = pd.DataFrame(rows)
    for col in ("tl_geo_db", "tl_least_loss_db", "tl_nx2d_db"):
        if col in R:
            R["dmodel_" + col] = R[col] - R.tl_air9_H01W_db
            R["excess_" + col] = R["dmodel_" + col] - R.dtl_obs_db
    R.to_csv(out / "air7_corridor.csv", index=False)
    prim = R[R.fc_hz.isin([31.5, 40.0, 50.0, 63.0])]
    med = {c: float(prim["excess_" + c].median()) for c in ("tl_geo_db", "tl_least_loss_db", "tl_nx2d_db") if "excess_" + c in prim}
    if "tl_nx2d_db" in med and abs(med["tl_nx2d_db"]) <= 10:
        verdict = "REPRODUCED"
    elif abs(med["tl_least_loss_db"]) <= 10:
        verdict = "REPRODUCED AS AN UPPER BOUND"
    else:
        verdict = "NOT REPRODUCED"
    V = dict(verdict=verdict, median_excess_db_31p5_to_63=med, bands_primary=[31.5, 40.0, 50.0, 63.0],
             least_loss_offsets_km=prim.set_index("fc_hz").d_least_km.to_dict())
    json.dump(V, open(out / "air7_verdict.json", "w"), indent=1, default=float); print(R.round(1).to_string()); print(json.dumps(V, indent=1, default=float))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sections":
        cmd_sections(*sys.argv[2:5])
    elif cmd == "tl":
        cmd_tl(*sys.argv[2:6], *(sys.argv[6:7] or ["4"]))
    elif cmd == "route1":
        cmd_route1(*sys.argv[2:5])
    elif cmd == "air8":
        cmd_air8(*sys.argv[2:4])
    elif cmd == "air7":
        cmd_air7(*sys.argv[2:5])
EOF
python -c "import ast; ast.parse(open('tl_recal_block9.py').read()); print('syntax ok')"