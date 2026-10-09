"""Engine validation (brief section 3, amended sequence item 1): KRAKEN adiabatic-mode transmission loss
for the Blackman air9 airgun site against Blackman et al. (2004) Fig. 23, at H01W and H08S, 5-60 Hz.

PROVISIONAL: the ocean environment is the WOA23 + GEBCO_2026 path stub (data/stub/, ruling item 5).

OBSERVED. Fig. 23 plots, per source-receiver pair, the MEDIAN over shots of observed transmission
loss, only where signal exceeded noise by 3 dB. The air9 curves are DIGITISED here from the page image
(artifact p23_img0.png, version 99b55187-e5c8-4c37-abff-0482499b5a7f) by tracing the darkest thin
curve per pixel column with continuity: threshold 140 of 255, a maximum jump of 30 px, legend and
panel labels masked. Axis calibration is from the tick-label centres: 3.6 px/dB, 2.875 px/Hz, 0 Hz at
x = 51.5 px. Resolution is 0.28 dB and 0.35 Hz per pixel. Chart-reading uncertainty is taken as
+/-2 dB. In the DGS panel the dotted air8 curve can capture the trace where the two cross;
continuity limits this but does not exclude it. Observed values are averaged in dB within
third-octave bands.

MODEL.
- Source: air9 line midpoint (-27.5612, 98.8821). Depth 10 m, with 9 and 12 m as the stated range.
- Receivers: FDSN triad centroid depths, H01W 1,055 m and H08S 1,376 m.
- Range profiles every 5 km. Depth is the median GEBCO_2026 within +/-2.5 km of the profile.
- c(z): from WOA23 95A4 season 16 at 25 km nodes, linear in range on common levels. Below the
  deepest valid WOA level, c is extended by holding SA and CT and increasing pressure (gsw).
- Bottom: acoustic half-space, two DECLARED alternatives:
    hard   cp 1650 m/s, rho 1.9, 0.5 dB/wavelength
    soft   cp 1560 m/s, rho 1.5, 1.0 dB/wavelength
- Volume attenuation: Francois-Garrison (T 4 C, S 34.7, pH 8.0, z_bar 1000 m).
- Incoherent adiabatic mode sum (FIELD 'RAOI'), then the spherical-spreading correction.
- Third-octave centres 5 to 63 Hz; model TL at the band centre.

UNRESOLVED, stated: whether Blackman's 230-240 dB source level "adjusted to 1 m" already contains
the surface ghost. The model's point source at 10 m includes the ghost in propagation. If the
quoted level is a far-field vertical level that already includes the ghost, the model should be
compared with observed TL corrected by about -20 log10 |2 sin(k zs)|. That is +7.5 dB at 5 Hz and
-5.6 dB at 30 Hz for zs = 10 m, and it is reported as a sensitivity row, not applied.

PRE-REGISTERED CRITERION (fixed before the first run; do not edit after looking). Per station, over the
third-octave bands where Fig. 23 has data within 5-63 Hz:
    residual = model TL - observed TL (dB)
    VALIDATED          |median residual| <= 3 dB and RMS residual <= 5 dB, for at least one declared
                       bottom alternative at the nominal 10 m source depth;
    PARTLY VALIDATED   |median residual| <= 6 dB (an offset), RMS <= 8 dB;
    NOT VALIDATED      otherwise.
The verdict is reported per station and per bottom alternative, with wall time.

Run: python prepare/air9_tl_validation.py <stub_dir> <at_bin_dir> <fig23_trace.csv> <out_dir>
"""

import json
import pathlib
import sys
import time

import gsw
import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import kraken_tl as K  # noqa: E402

SRC_DEPTHS = [9.0, 10.0, 12.0]
RCV = {"H01W": 1055.0, "H08S": 1376.0}
BOTTOMS = {"hard": dict(cp=1650.0, rho=1.9, ap=0.5), "soft": dict(cp=1560.0, rho=1.5, ap=1.0)}
FG = dict(T=4.0, S=34.7, pH=8.0, z_bar=1000.0)
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0]
DR_KM = 5.0
EXT_LEVELS = np.arange(5600.0, 7001.0, 100.0)


def node_profiles(ssp):
    """Full-depth c(z) per node on WOA levels plus extension levels."""
    out = {}
    for node, g in ssp.groupby("node"):
        g = g.sort_values("depth_m")
        v = g.dropna(subset=["c_m_s"])
        lat, lon = float(g.lat.iloc[0]), float(g.lon.iloc[0])
        z_all = np.concatenate([g.depth_m.values, EXT_LEVELS])
        c_all = np.full(len(z_all), np.nan)
        c_all[: len(g)] = g.c_m_s.values
        last = v.iloc[-1]
        p_last = gsw.p_from_z(-last.depth_m, lat)
        sa = gsw.SA_from_SP(last.sp_psu, p_last, lon, lat)
        ct = gsw.CT_from_t(sa, last.t_insitu_c, p_last)
        deep = z_all > last.depth_m
        c_all[deep] = gsw.sound_speed(sa, ct, gsw.p_from_z(-z_all[deep], lat))
        out[node] = (float(g.range_km.iloc[0]), z_all, c_all)
    return out


def build_profiles(bathy, ssp):
    nodes = node_profiles(ssp)
    keys = sorted(nodes)
    nr = np.array([nodes[k][0] for k in keys])
    z = nodes[keys[0]][1]
    C = np.vstack([nodes[k][2] for k in keys])
    L = float(bathy.range_km.iloc[-1])
    rprof = np.append(np.arange(0.0, L, DR_KM), L)
    profiles = []
    for r in rprof:
        w = bathy[(bathy.range_km >= r - 2.5) & (bathy.range_km <= r + 2.5)]
        D = float(np.median(-w.elevation_m.values))
        c = np.array([np.interp(r, nr, C[:, j]) for j in range(len(z))])
        keep = z < D
        zz = np.append(z[keep], D)
        cc = np.append(c[keep], np.interp(D, z, c))
        profiles.append((D, zz, cc))
    return rprof, profiles


def observed_bands(tr, f_lo, f_hi):
    rows = []
    for fc in BANDS:
        a, b = fc / 2 ** (1 / 6), fc * 2 ** (1 / 6)
        v = tr[(tr.f_hz >= a) & (tr.f_hz < b)].tl_db
        rows.append((fc, float(v.mean()) if len(v) >= 3 else np.nan, int(len(v))))
    return pd.DataFrame(rows, columns=["fc_hz", "obs_tl_db", "n_obs_px"])


def verdict(res):
    r = res.dropna()
    if len(r) == 0:
        return "not assessed", np.nan, np.nan
    med, rms = float(np.median(r)), float(np.sqrt(np.mean(r ** 2)))
    if abs(med) <= 3 and rms <= 5:
        v = "VALIDATED"
    elif abs(med) <= 6 and rms <= 8:
        v = "PARTLY VALIDATED"
    else:
        v = "NOT VALIDATED"
    return v, med, rms


def main(stub, at_bin, trace_csv, out_dir):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    stub = pathlib.Path(stub)
    traces = pd.read_csv(trace_csv, comment="#")
    rows, curves, summary = [], [], {}
    t_start = time.time()
    for st, rd in RCV.items():
        bathy = pd.read_csv(stub / f"bathy_air9_{st}.csv")
        ssp = pd.read_csv(stub / f"ssp_air9_{st}.csv")
        rprof, profiles = build_profiles(bathy, ssp)
        L = rprof[-1]
        rr = np.append(np.arange(DR_KM, L, DR_KM), L)
        obs = observed_bands(traces[traces.station == st], 5, 63)
        for bname, bot in BOTTOMS.items():
            t0 = time.time()
            for fc in BANDS:
                r, tl, nm, dt = K.tl_path(out / "work" / f"{st}_{bname}", f"f{fc:g}".replace(".", "p"), fc,
                                          profiles, rprof, rr, SRC_DEPTHS, [rd], bot, at_bin, fg=FG)
                s = K.read_shd(out / "work" / f"{st}_{bname}" / (f"f{fc:g}".replace(".", "p") + ".shd"))
                R = 6371.0
                x = s["rr_m"] / 1000.0 / R
                sph = 10 * np.log10(x / np.sin(x))
                for js, zs in enumerate(s["sz"]):
                    tlz = -20 * np.log10(np.abs(s["p"][0, js, 0])) + sph
                    rows.append(dict(station=st, bottom=bname, fc_hz=fc, src_depth_m=float(zs), rcv_depth_m=rd,
                                     range_km=float(L), tl_db=float(tlz[-1]), n_modes_first=nm[0] if nm else -1,
                                     n_modes_min=min(nm) if nm else -1))
                    if zs == 10.0:
                        curves.append(pd.DataFrame(dict(station=st, bottom=bname, fc_hz=fc, range_km=s["rr_m"] / 1000.0,
                                                        tl_db=tlz)))
            summary[f"{st}_{bname}_wall_s"] = round(time.time() - t0, 1)
            print(st, bname, "done", summary[f"{st}_{bname}_wall_s"], "s", flush=True)
        summary[f"{st}_profiles"] = len(rprof)
        summary[f"{st}_min_profile_depth_m"] = float(min(p[0] for p in profiles))
        obs.to_csv(out / f"observed_bands_{st}.csv", index=False)
    model = pd.DataFrame(rows)
    model.to_csv(out / "air9_tl_model.csv", index=False)
    pd.concat(curves).to_csv(out / "air9_tl_vs_range.csv", index=False)
    verdicts = []
    for st in RCV:
        obs = pd.read_csv(out / f"observed_bands_{st}.csv")
        for bname in BOTTOMS:
            for zs in SRC_DEPTHS:
                m = model[(model.station == st) & (model.bottom == bname) & (model.src_depth_m == zs)].set_index("fc_hz").tl_db
                res = m.reindex(obs.fc_hz).values - obs.obs_tl_db.values
                v, med, rms = verdict(pd.Series(res))
                ghost = 20 * np.log10(np.abs(2 * np.sin(2 * np.pi * obs.fc_hz.values / 1500.0 * zs)))
                vg, medg, rmsg = verdict(pd.Series(res + ghost))
                verdicts.append(dict(station=st, bottom=bname, src_depth_m=zs, n_bands=int(np.isfinite(res).sum()),
                                     median_residual_db=med, rms_residual_db=rms, verdict=v,
                                     ghost_sensitivity_median_db=medg, ghost_sensitivity_rms_db=rmsg,
                                     ghost_sensitivity_verdict=vg, nominal=(zs == 10.0)))
    vd = pd.DataFrame(verdicts)
    vd.to_csv(out / "air9_tl_verdicts.csv", index=False)
    summary["total_wall_s"] = round(time.time() - t_start, 1)
    json.dump(summary, open(out / "air9_tl_summary.json", "w"), indent=1)
    print(vd.to_string(index=False, float_format="%.2f"))
    print(json.dumps(summary))


if __name__ == "__main__":
    main(*sys.argv[1:5])
