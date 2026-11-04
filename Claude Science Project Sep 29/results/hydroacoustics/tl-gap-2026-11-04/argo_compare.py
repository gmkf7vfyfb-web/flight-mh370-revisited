"""Argo profiles near the source regions (addendum, 5 Nov 2026), from the Copernicus Marine in-situ product CORA
(cmems_obs-ins_glo_phy-temp-sal_my_cora_irr, version 202511, daily *_PR_PF.nc files, 'global' region).
Selection: within 300 km of the first 400 km of any of the 5 paths, within +/-10 days of the event day (8 Mar 2014 for the
arc paths, 9 Apr 2019 for the Wake paths). Levels: *_ADJUSTED where present, else raw; QC flags 1 or 2 only.
Sound speed: TEOS-10 (SA from SP, CT from in-situ T). Each profile is compared with GLORYS12 (same day if the local file
holds it, else the nearest held day; flagged) and with WOA23 (chain convention) at the same position.
Usage: python argo_compare.py <cora_root> <sec_dir> <out_dir>"""
import glob, os, pickle, sys
import numpy as np, pandas as pd, netCDF4 as nc, gsw
sys.path.insert(0, os.environ["TLCHAIN_DIR"]); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tlchain import paths as P                                  # noqa: E402
import make_jobs_glorys as MG                                   # noqa: E402
ROOT, SEC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
EV = {"arc": pd.Timestamp("2014-03-08"), "wake": pd.Timestamp("2019-04-09")}
WOA = {"arc": ("A5B4", 3), "wake": ("B5C2", 4)}
HELD = {"arc": pd.date_range("2014-03-07", "2014-03-14"), "wake": pd.date_range("2019-03-30", "2019-04-19")}
PATHS = {"arc39.0S-H01W": "arc", "arc35.5S-H01W": "arc", "arc30.0S-H01W": "arc", "f35a-H11N": "wake", "f35a-H11S": "wake"}
pts = {}
for nm, reg in PATHS.items():
    s = pickle.load(open(f"{SEC}/{nm}.pkl", "rb")); k = s["range_km"] <= 400.0
    pts[nm] = (s["lat"][k][::100], s["lon"][k][::100], reg)       # every 25 km
G = P.G
rows, levels = [], []
for f in sorted(glob.glob(f"{ROOT}/**/global/*/CO_*_PR_PF.nc", recursive=True)):
    d = nc.Dataset(f)
    lat = d.variables["LATITUDE"][:].astype(float); lon = d.variables["LONGITUDE"][:].astype(float)
    t = pd.to_datetime(d.variables["TIME"][:].astype(float), unit="D", origin="1950-01-01")
    plat = ["".join(x.astype(str)).strip() for x in nc.chartostring(d.variables["PLATFORM_NUMBER"][:]).reshape(-1, 1)] if False else \
        [str(x).strip() for x in nc.chartostring(d.variables["PLATFORM_NUMBER"][:])]
    for i in range(len(lat)):
        if not (np.isfinite(lat[i]) and np.isfinite(lon[i])):
            continue
        best = None
        for nm, (pla, plo, reg) in pts.items():
            if abs((t[i] - EV[reg]).days) > 10 or (reg == "arc") != (lat[i] < 0):
                continue
            _, _, dist = G.inv(np.full(len(pla), lon[i]), np.full(len(pla), lat[i]), plo, pla)
            dm = float(np.min(dist)) / 1e3
            if dm <= 300.0 and (best is None or dm < best[1]):
                best = (nm, dm, reg)
        if best is None:
            continue
        def get(v):
            a = d.variables[v + "_ADJUSTED"][i]; q = d.variables[v + "_ADJUSTED_QC"][i]
            a = np.ma.filled(a.astype(float), np.nan)
            if not np.isfinite(a).any():
                a = np.ma.filled(d.variables[v][i].astype(float), np.nan); q = d.variables[v + "_QC"][i]
            q = np.ma.filled(q, b" ").astype(str) if q.dtype.kind in "SU" else np.ma.filled(q.astype(float), 9).astype(int).astype(str)
            return np.where(np.isin(q, ["1", "2"]), a, np.nan)
        pr, te, ps = get("PRES"), get("TEMP"), get("PSAL")
        ok = np.isfinite(pr) & np.isfinite(te) & np.isfinite(ps)
        if ok.sum() < 10 or np.nanmin(pr[ok]) > 20:
            continue
        pr, te, ps = pr[ok], te[ok], ps[ok]; o = np.argsort(pr); pr, te, ps = pr[o], te[o], ps[o]
        sa = gsw.SA_from_SP(ps, pr, lon[i], lat[i]); ct = gsw.CT_from_t(sa, te, pr); c = gsw.sound_speed(sa, ct, pr); z = -gsw.z_from_p(pr, lat[i])
        nm, dm, reg = best
        # GLORYS (same or nearest held day) and WOA23 at the profile position
        day = pd.Timestamp(t[i].date()); held = HELD[reg]; dg = held[np.argmin(np.abs((held - day).days))]
        g = MG.glorys_profile(reg, dg.strftime("%Y-%m-%d"), float(lat[i]), float(lon[i]))
        zw, cw = P.sound_speed_profile(float(lat[i]), float(lon[i]), *WOA[reg])
        zz = np.arange(10.0, min(1500.0, z.max()) + 1, 10.0)
        ca = np.interp(zz, z, c); cwi = np.interp(zz, zw, cw); cgi = np.interp(zz, g[0], g[1]) if g is not None else np.full(len(zz), np.nan)
        rows.append(dict(region=reg, nearest_path=nm, dist_km=dm, platform=plat[i], time=str(t[i]), dt_days=(t[i] - EV[reg]).total_seconds() / 86400,
                         lat=float(lat[i]), lon=float(lon[i]), max_depth_m=float(z.max()), n_levels=int(len(z)), file=os.path.basename(f),
                         glorys_day=dg.strftime("%Y-%m-%d") if g is not None else "", glorys_day_offset=int((dg - day).days) if g is not None else np.nan,
                         c_surf_argo=float(np.interp(10, z, c)), c_surf_woa=float(np.interp(10, zw, cw)), c_surf_glorys=float(np.interp(10, *g)) if g is not None else np.nan,
                         rms_argo_minus_woa_0_1500=float(np.sqrt(np.nanmean((ca - cwi) ** 2))), rms_argo_minus_glorys_0_1500=float(np.sqrt(np.nanmean((ca - cgi) ** 2))) if g is not None else np.nan,
                         mean_argo_minus_woa_0_300=float(np.nanmean((ca - cwi)[zz <= 300])), mean_argo_minus_glorys_0_300=float(np.nanmean((ca - cgi)[zz <= 300])) if g is not None else np.nan))
        levels += [dict(platform=plat[i], time=str(t[i]), depth_m=a, c_argo=b, c_woa=e, c_glorys=h) for a, b, e, h in zip(zz, ca, cwi, cgi)]
R = pd.DataFrame(rows).drop_duplicates(["platform", "time"]); R.to_csv(f"{OUT}/argo-profiles-near-sources.csv", index=False)
pd.DataFrame(levels).drop_duplicates(["platform", "time", "depth_m"]).to_csv(f"{OUT}/argo-profile-levels.csv.gz", index=False)
print(len(R), "profiles"); print(R.groupby("region")[["rms_argo_minus_woa_0_1500", "rms_argo_minus_glorys_0_1500", "mean_argo_minus_woa_0_300", "mean_argo_minus_glorys_0_300"]].median().round(2).to_string())
print(R.groupby(["region", "nearest_path"]).size().to_string())
