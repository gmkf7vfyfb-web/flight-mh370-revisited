"""PRE-REGISTRATION and implementation: N x 2D transmission loss in a Fresnel corridor (architecture ruling 6, 11 Oct
2026 00:50 -0600: "module-built N x 2D ... start with Yemenia -> H08S/N"; audit F11). Committed before any corridor TL
was computed. Changes after the first result are amendments with their own commits.

WHY. The module's TL is adiabatic normal modes on ONE 2-D section along the source-receiver geodesic. A bank or rise
crossed by that one line either blocks everything (Saya de Malha Bank on Yemenia 626 -> H08S: 19-75 m) or nothing,
while sound actually reaches the receiver through a band of width set by the Fresnel zone. Paths beside the geodesic
may be open where the geodesic is blocked (or shallower where it is open).

METHOD (fixed now).
  1. Path family. For each third-octave band b (5-40 Hz, as the module) and lateral parameter u_j in
     {-2.0, -1.75, ..., +2.0} (17 values), a curve that leaves the geodesic by d_j(s) = u_j F_b(s) at along-track
     distance s, with F_b(s) = sqrt(lambda_b s (R - s) / R), lambda_b = 1500 / f_b (the first Fresnel-zone half-width),
     offset perpendicular to the local geodesic azimuth (WGS84, pyproj). u = 0 is the geodesic.
  2. Sections. Bathymetry along each curve every 0.5 km from the shared GEBCO_2026 layers (3 x 3 median, the same rule
     as ocean transport's sections; layers: gebco_2026 (40-180 E), gebco_2026_satl (62-12 W)). Sound speed from the
     geodesic's own section (ocean transport / shared exporter), DECLARED: lateral offsets are <= 2 F <= 31 km, well
     inside one WOA23 1-degree cell.
  3. TL per member. The module's KRAKEN wrapper unchanged (kraken_tl.tl_path + air9_tl_validation.build_profiles:
     5-km profiles, hard bottom, Francois-Garrison, incoherent mode sum, adiabatic, spherical correction), at the
     path end, for z_s in {2, 10, 30} m (+33 m for the San Juan charge). A member for which KRAKEN finds no
     propagating mode on some profile (fatal "No modes") is BLOCKED: its contribution is zero.
  4. Corridor TL. TL_nx2d,b = -10 log10[ sum_j w_j 10^(-TL_j,b / 10) / sum_j w_j ], w_j = exp(-u_j^2). Reported with
     the geodesic TL (u = 0) and the open weight fraction sum_{open} w_j / sum w_j. If every member is blocked the band
     is BLOCKED (no finite TL; reported, never imputed).
  DECLARED LIMITS: no horizontal refraction or diffraction beyond the Fresnel corridor (|u| <= 2); members are
  combined incoherently; the curve length differs from R by < 0.1 % and the geodesic range R is used.
CHECKS (fixed now).
  K1 (control, unobstructed path): AF447 -> H10S has no feature shallower than 1,000 m (ocean transport). PASS if
     |TL_nx2d - TL_geodesic(ocean transport's section)| <= 1.5 dB in every band at z_s = 10 m.
  K2 (sampling consistency): the u = 0 member, built here from the GEBCO layer, against the same KRAKEN run on ocean
     transport's section of the same geodesic: PASS if <= 1.0 dB in every band at z_s = 10 m (AF447 -> H10S).
  If K1 or K2 fails, results are reported labelled CHECK-FAILED and are not used for any calibration statement.
APPLICATIONS (in this order, ruling 6): Yemenia 626 (11.3715 S 43.2250 E, calibration_events amendment 2) -> H08S and
  H08N; then the ARA San Juan charge (45.666 S 59.240 W, z_s 33 m) -> H10N on ocean transport's section.
OUTPUTS: <out>/<name>/members.csv (band, u, z_s, TL or blocked, n_modes_min), <out>/<name>/corridor.csv (band, z_s,
  TL_geo, TL_nx2d, open_weight), <out>/checks.json.
AMENDMENT 1 (11 Oct 2026, after the first results at 29e21362; committed BEFORE either run below). Audit F11 names
  the test case for N x 2D: Blackman (2004) shot A11sus (site A11, -13.197967 S 104.694350 E, June 2003, z_s 915 m)
  -> H08S crosses the Cocos (Keeling) Islands, so the single-path model gives no field, yet the shot WAS recorded at
  H08S (App. B Fig. B11). The same logic sets Chagos blocking for H08N under MH370.
  K3 (blocked-but-detected case). Corridor TL for A11 -> H08S (2002 triad centroid, rd 1376 m) and A11 -> H01W (H01W1,
     -34.892899 114.153900, rd 1063 m), bands 5-63 Hz (adds 50 and 63 Hz with --bands; the audit's band set), z_s 915 m,
     sound speed from the audit's own path builder (results/hydroacoustics-audit/scripts/paths.py, WOA23 95A4 June).
     Scored with the audit's C2 station difference d_b = r_b(H01W) - r_b(H08S) observed minus predicted, over the bands
     where the audit's sus_bands.csv gives a noise-subtracted signal (SNR >= 3 dB) at BOTH stations, with C2's grades
     (level |median| <= 3 / 6 dB, slope <= 1.5 / 3 dB/oct, shape RMS <= 3.5 / 5 dB).
     Outcomes, fixed now: (i) if the H08S corridor is BLOCKED (open weight 0) in any shared band, K3 FAILS for reach:
     N x 2D within +/-2 Fresnel widths cannot explain the detection, gap G-N1 stays open and NO H08N non-detection may be
     used; (ii) if open, C2 grades are reported as they fall, with n bands stated; fewer than 3 shared bands = NOT
     TESTABLE. No parameter is tuned to Fig. B11.
  K4 (application, only after K3): MH370 -> H08N corridor for one representative impact (the run C posterior-weighted
     median impact, all four strata pooled, as written in the composer pass-1 note) at z_s 2, 10, 30 m, bands 5-40 Hz.
     Reported as open weight per band; labelled with K3's outcome.
Usage: python nx2d.py <at_dir> <out_dir> <name> <src_lat> <src_lon> <rcv_lat> <rcv_lon> <rcv_depth_m> <ssp_csv>
                      [--src-depths 2 10 30] [--geo-tl <csv>] [--bands 5 ... 63]  (amendment 1)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Geod

sys.path.insert(0, str(Path(__file__).parent))
import air9_tl_validation as A  # noqa: E402
import kraken_tl as K  # noqa: E402

BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
U = np.round(np.arange(-2.0, 2.0001, 0.25), 2)
C_REF = 1500.0
DS_KM = 0.5
GRIDS = [Path("/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026.json"),
         Path("/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026_satl.json")]
G = Geod(ellps="WGS84")
_MM = {}


def _grid(p):
    if p not in _MM:
        g = json.loads(p.read_text())
        el = np.memmap(p.parent / g["elevation_file"], dtype=np.int16, mode="r", shape=(g["nlat"], g["nlon"]))
        _MM[p] = (g, el)
    return _MM[p]


def elevation(lat, lon):
    """3 x 3 median GEBCO_2026 elevation (m, positive up) from whichever shared layer contains each point."""
    lat = np.asarray(lat, float); lon = np.asarray(lon, float); out = np.full(lat.shape, np.nan)
    for p in GRIDS:
        g, el = _grid(p)
        i = np.rint((lat - g["lat0"]) / g["step_deg"]).astype(int); j = np.rint((lon - g["lon0"]) / g["step_deg"]).astype(int)
        m = np.isnan(out) & (i >= 1) & (i < g["nlat"] - 1) & (j >= 1) & (j < g["nlon"] - 1)
        if m.any():
            st = np.stack([el[i[m] + di, j[m] + dj] for di in (-1, 0, 1) for dj in (-1, 0, 1)]).astype(float)
            out[m] = np.median(st, axis=0)
    assert np.isfinite(out).all(), "path point outside every shared GEBCO layer"
    return out


def member_section(src, rcv, u, f):
    """Bathymetry (range_km, elevation_m) along the curve offset by u * F_f(s) from the geodesic."""
    az12, _, R = G.inv(src[1], src[0], rcv[1], rcv[0])
    n = int(R / 1000.0 / DS_KM) + 1
    s = np.linspace(0.0, R, n)
    lon, lat, az = G.fwd(np.full(n, src[1]), np.full(n, src[0]), np.full(n, az12), s)
    # local forward azimuth along the geodesic at each point
    az_loc = np.array(G.inv(lon[:-1], lat[:-1], lon[1:], lat[1:])[0]); az_loc = np.append(az_loc, az_loc[-1])
    lam = C_REF / f
    d = u * np.sqrt(np.maximum(lam * s * (R - s) / R, 0.0))
    lo2, la2, _ = G.fwd(lon, lat, az_loc + 90.0, d)
    return pd.DataFrame(dict(range_km=s / 1000.0, lat=la2, lon=lo2, elevation_m=elevation(la2, lo2), offset_m=d)), R / 1000.0


def run(at, out, name, src, rcv, rd, ssp_csv, zs, geo_tl=None):
    out = Path(out) / name; out.mkdir(parents=True, exist_ok=True)
    ssp = pd.read_csv(ssp_csv); rows = []
    t0 = time.time()
    for f in BANDS:
        for u in U:
            bathy, Rk = member_section(src, rcv, float(u), f)
            rprof, profiles = A.build_profiles(bathy, ssp)
            tag = f"f{f:g}_u{u:+.2f}".replace(".", "p").replace("+", "P").replace("-", "M")
            minD = float(min(p[0] for p in profiles))
            try:
                K.tl_path(out / "work", tag, f, profiles, rprof, np.array([rprof[-1]]), zs, [rd], A.BOTTOMS["hard"], at, fg=A.FG)
                s = K.read_shd(out / "work" / f"{tag}.shd"); x = s["rr_m"] / 1000.0 / 6371.0; sph = 10 * np.log10(x / np.sin(x))
                prt = (out / "work" / f"{tag}.prt").read_text(errors="replace")
                import re
                nm = [int(v) for v in re.findall(r"Number of modes\s*=\s*(\d+)", prt)]
                for js, z in enumerate(s["sz"]):
                    rows.append(dict(fc_hz=f, u=float(u), src_depth_m=float(z), tl_db=float(-20 * np.log10(np.abs(s["p"][0, js, 0, -1])) + sph[-1]),
                                     blocked=False, n_modes_min=min(nm) if nm else -1, min_profile_depth_m=minD, range_km=Rk))
            except RuntimeError as e:
                why = "no modes" if "No modes" in str(e) else str(e).splitlines()[0][:80]
                for z in zs:
                    rows.append(dict(fc_hz=f, u=float(u), src_depth_m=float(z), tl_db=np.inf, blocked=True, n_modes_min=0,
                                     min_profile_depth_m=minD, range_km=Rk, reason=why))
            for p in (out / "work").glob(f"{tag}.*"):
                if p.suffix in (".shd", ".mod"):
                    p.unlink()      # this run's own KRAKEN scratch files (large), written above
        print(name, f, f"{time.time() - t0:.0f} s", flush=True)
    M = pd.DataFrame(rows); M.to_csv(out / "members.csv", index=False)
    w = np.exp(-M.u ** 2); M["w"] = w
    cor = []
    for (f, z), g in M.groupby(["fc_hz", "src_depth_m"]):
        lin = (g.w * np.where(g.blocked, 0.0, 10 ** (-g.tl_db.where(~g.blocked, 0) / 10))).sum() / g.w.sum()
        geo = g[g.u == 0].iloc[0]
        cor.append(dict(fc_hz=f, src_depth_m=z, tl_geo_db=float(geo.tl_db), geo_blocked=bool(geo.blocked),
                        tl_nx2d_db=float(-10 * np.log10(lin)) if lin > 0 else np.inf,
                        open_weight=float(g.w[~g.blocked].sum() / g.w.sum())))
    C = pd.DataFrame(cor)
    if geo_tl is not None:
        gt = pd.read_csv(geo_tl)
        C = C.merge(gt[["fc_hz", "src_depth_m", "tl_db"]].rename(columns={"tl_db": "tl_geo_section_db"}), on=["fc_hz", "src_depth_m"], how="left")
    C.to_csv(out / "corridor.csv", index=False)
    return M, C


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for k in ("at", "out", "name"):
        ap.add_argument(k)
    for k in ("src_lat", "src_lon", "rcv_lat", "rcv_lon", "rcv_depth"):
        ap.add_argument(k, type=float)
    ap.add_argument("ssp_csv"); ap.add_argument("--src-depths", nargs="+", type=float, default=[2.0, 10.0, 30.0])
    ap.add_argument("--geo-tl")
    ap.add_argument("--bands", nargs="+", type=float, default=None)   # amendment 1
    a = ap.parse_args()
    if a.bands:
        BANDS[:] = a.bands
    M, C = run(a.at, a.out, a.name, (a.src_lat, a.src_lon), (a.rcv_lat, a.rcv_lon), a.rcv_depth, a.ssp_csv, a.src_depths, a.geo_tl)
    print(C.round(2).to_string(index=False))
