#!/usr/bin/env python
"""Extract every quantitative object of Metz, Obana & Fukao (2023), 'Remote hydroacoustic detection of an airplane
crash', Pure Appl. Geophys. 180:1343-1351, doi 10.1007/s00024-022-03117-6 (the JASDF F-35A loss, 9 Apr 2019).

DIGITISED PUBLICATION OBJECTS, NOT CTBTO WAVEFORM SAMPLES. Source PDF: the copy Pete holds (artifact store,
'art:10.1007/s00024-022-03117-6.pdf'; also mh370-exchange/hydroacoustics/sources/). The 22 Oct overnight note
called this paper 'closed access, not held'; that was wrong (correction of 22 Oct, gap G4).

What the paper gives (text): last radar contact 10:26:30 UTC about 135 km east of Misawa (JASDF), ~300 m/s steep
descent; acoustic origin time 10:26:32 +/- 9 s; epicentre within 8 km of the 135 km circle; 90 % ellipse 844 km^2,
semi-axes 36.8 / 7.3 km; 3,341 km to H11S; H11 triplets 55 km NE (H11N) and 90 km S (H11S) of Wake, 2 km aperture,
250 Hz, moored 727 m (H11N) / 739 m (H11S), seafloor ~1430 / ~1170 m; detection from 11:03:00 (H11N) and 11:04:05
(H11S); 6-8 s transients; 4-64 Hz processing band; no energy above background near 20 Hz; local cabled observatory
(DSOH, KSP1-3, 100 Hz, flat 1-40 Hz, 2124-3428 m deep, 180-255 km) first arrivals 10:28:31-10:29:21, up to 20 dB
above ambient (peak 1 s RMS). The paper gives NO impact energy, NO source level and NO coupling efficiency: the
900 +/- 200 MJ and the 0.7 Pa are Brown et al. (2026), not Metz. The epicentre is shown only as a cross in Fig. 1E
(no coordinates, no graticule); its position is therefore not digitised.

Figures (method per object):
  Fig. 1      raster map (1870 x 1505) - raster copy only.
  Fig. 2A-D   local-station spectrograms, ONE raster (1652 x 251) incl. colour bar 90-110 dB re 1 uPa^2/Hz -> colour
              inverted against the colour bar to dB on a (time, frequency) pixel grid; floor (<= 90) and saturation
              (>= 110) flagged.
  Fig. 2E-H   local-station 1 s RMS amplitude (4-40 Hz), PDF vector polylines, axis 90-130 dB re 1 uPa, 30 s.
  Fig. 3A-B   H11N1 / H11S1 spectrograms (2-80 Hz band-passed), ONE raster (1679 x 227) incl. colour bar 80-100 dB
              re 1 uPa^2/Hz -> colour inverted as Fig. 2.
  Fig. 3C-D   H11N1-3 / H11S1-3 1 s RMS amplitude (98 % overlap, 4-64 Hz), PDF vector polylines, 80-120 dB re 1 uPa,
              30 s from 11:02:55 / 11:03:55 UTC.
  Fig. 3E-H   apparent velocity (1430-1530 m/s), closure (colour, -16..16 ms) and back azimuth (0-360 deg) of the 6 s
              windows that pass the detection rule: vector marker centres.
  Fig. 4      H11N / H11S sound-speed profiles (WOA09 annual mean, Dushaw et al.), PDF vector polylines.
Axis calibration: frames and tick marks from the PDF vector strokes (tick labels are glyph outlines, read from a
200 dpi render and checked against the tick spacing: 10 s / 10 dB per tick). Verification: an overlay PNG per vector
object over a 4x render of the page region; tick-spacing residuals in METHOD.json.

Outputs (--out, default results-data/digitised/metz2023/): see METHOD.json 'files'.
Usage: python digitise_metz_2023.py --pdf <Metz2023.pdf> [--out DIR]
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, io, json, os
import numpy as np

UTC0 = dt.datetime(2019, 4, 9)
C_STROKE = (0.141, 0.125, 0.118)
EL_COL = {"1": (0.10194552689790726, 0.26274511218070984, 0.45488670468330383),
          "2": (0.6274357438087463, 0.8274357318878174, 0.9293965101242065),
          "3": (0.35684749484062195, 0.5921568870544434, 0.807827889919281)}
# Fig. 3 (page index 4): frames from the vector strokes
F3 = dict(C=dict(sta="H11N", x0=71.0, x1=241.98, t0="11:02:55"), D=dict(sta="H11S", x0=284.91, x1=455.9, t0="11:03:55"))
F3_RMS_Y = (135.65, 189.22, 120.0, 80.0)            # y_top, y_bot, value_top, value_bot
F3_VEL_Y = (210.14, 264.07, 1530.0, 1430.0)
F3_BAZ_Y = (284.62, 338.56, 360.0, 0.0)
# Fig. 2 (page index 3)
F2 = [dict(sta="DSOH", x0=72.16, x1=149.86, tick=85.11, tick_t="10:28:25"),
      dict(sta="KSP1", x0=173.71, x1=251.41, tick=186.66, tick_t="10:28:30"),
      dict(sta="KSP2", x0=276.13, x1=352.95, tick=288.93, tick_t="10:29:15"),
      dict(sta="KSP3", x0=377.68, x1=455.38, tick=390.63, tick_t="10:29:20")]
F2_RMS_Y = (507.98, 566.26, 130.0, 90.0)
F4 = dict(x0=314.4, x1=489.55, v0=1480.0, v1=1550.0, y0=127.47, y1=447.79, d0=0.0, d1=2500.0)


def close(c, ref, tol=3e-3):
    return c is not None and all(abs(float(a) - float(b)) <= tol for a, b in zip(c, ref))


def hms(s):
    h, m, x = s.split(":"); return int(h) * 3600 + int(m) * 60 + float(x)


def utc(sec):
    return (UTC0 + dt.timedelta(seconds=float(sec))).strftime("%H:%M:%S.%f")[:-3]


def polylines(pg, min_items=50):
    out = []
    for d in pg.get_drawings():
        c = d.get("color")
        if c is None or len(d["items"]) < min_items:
            continue
        pts = []
        for it in d["items"]:
            if it[0] == "l":
                if not pts: pts.append((it[1].x, it[1].y))
                pts.append((it[2].x, it[2].y))
            elif it[0] == "c":                         # cubic Bezier: sampled at 8 points (chords would cut corners)
                p0, p1, p2, p3 = it[1], it[2], it[3], it[4]
                if not pts: pts.append((p0.x, p0.y))
                for u in np.linspace(0.125, 1.0, 8):
                    w = ((1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3)
                    pts.append((w[0] * p0.x + w[1] * p1.x + w[2] * p2.x + w[3] * p3.x, w[0] * p0.y + w[1] * p1.y + w[2] * p2.y + w[3] * p3.y))
        out.append((c, np.array(pts)))
    return out


def lin(v, a0, a1, b0, b1):
    return b0 + (np.asarray(v, float) - a0) / (a1 - a0) * (b1 - b0)


def colour_invert(img, bar_cols, top_val, bot_val, frame_rows=(3, 223)):
    """Map every RGB pixel to the colour-bar value by nearest colour (Lab-free RGB distance). Returns value, distance."""
    c0, c1 = bar_cols
    bar = img[frame_rows[0]:frame_rows[1], c0:c1].astype(float).mean(1)            # rows top->bottom
    vals = np.linspace(top_val, bot_val, len(bar))
    flat = img.reshape(-1, 3).astype(float)
    best = np.full(len(flat), np.inf); arg = np.zeros(len(flat), int)
    for k in range(len(bar)):
        d = ((flat - bar[k]) ** 2).sum(1); m = d < best; best[m] = d[m]; arg[m] = k
    return vals[arg].reshape(img.shape[:2]), np.sqrt(best).reshape(img.shape[:2])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results-data", "digitised", "metz2023"))
    a = ap.parse_args()
    import fitz, pandas as pd
    from PIL import Image
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    out = os.path.abspath(a.out); os.makedirs(os.path.join(out, "overlays"), exist_ok=True); os.makedirs(os.path.join(out, "rasters"), exist_ok=True)
    raw = open(a.pdf, "rb").read(); sha = hashlib.sha256(raw).hexdigest(); doc = fitz.open(a.pdf)
    meth = dict(source="Metz, Obana & Fukao (2023) Pure Appl. Geophys. 180:1343-1351, doi 10.1007/s00024-022-03117-6",
                pdf_sha256=sha, label="DIGITISED publication objects; not waveform samples", files=[], checks={})

    # ---------------------------------------------------------------- Fig. 3C/D RMS envelopes (vector)
    pg = doc[4]; rows = []; env = {}
    for c, pts in polylines(pg):
        el = [k for k, v in EL_COL.items() if close(c, v)]
        if not el or pts[:, 1].min() < 130 or pts[:, 1].max() > 195:
            continue
        pn = "C" if pts[:, 0].mean() < 260 else "D"; P = F3[pn]
        t = lin(pts[:, 0], P["x0"], P["x1"], 0.0, 30.0) + hms(P["t0"])
        L = lin(pts[:, 1], F3_RMS_Y[0], F3_RMS_Y[1], F3_RMS_Y[2], F3_RMS_Y[3])
        key = f"{P['sta']}{el[0]}"; env[key] = (t, L)
        for ti, Li, x, y in zip(t, L, pts[:, 0], pts[:, 1]):
            rows.append(dict(element=key, utc_s_of_day=ti, utc=utc(ti), rms_db_re_1uPa=Li, pdf_x_pt=x, pdf_y_pt=y))
    df = pd.DataFrame(rows); fn = "fig3CD_rms_envelopes_vertices_DIGITISED.csv"; df.to_csv(os.path.join(out, fn), index=False); meth["files"].append(fn)
    # uniform 0.05 s resampling (linear between vertices; the plotted line IS linear between vertices)
    grid = []
    for key, (t, L) in sorted(env.items()):
        o = np.argsort(t); t, L = t[o], L[o]
        tg = np.arange(np.ceil(t[0] * 20) / 20, t[-1], 0.05)
        grid.append(pd.DataFrame(dict(element=key, utc_s_of_day=tg, utc=[utc(v) for v in tg], rms_db_re_1uPa=np.interp(tg, t, L))))
    g = pd.concat(grid); fn = "fig3CD_rms_envelopes_0p05s_DIGITISED.csv"; g.to_csv(os.path.join(out, fn), index=False); meth["files"].append(fn)
    meth["checks"]["fig3CD"] = {k: dict(n_vertices=int(len(v[0])), t_span_s=[float(v[0].min() - hms(F3['C' if k.startswith('H11N') else 'D']['t0'])), float(v[0].max() - hms(F3['C' if k.startswith('H11N') else 'D']['t0']))],
                                       peak_db=float(v[1].max()), peak_utc=utc(v[0][np.argmax(v[1])])) for k, v in env.items()}
    # tick check: x ticks at 11:03:00/10/20 sit at 99.54/156.49/213.45 (C) -> residual of the linear map
    tc = lin(np.array([99.54, 156.49, 213.45]), F3["C"]["x0"], F3["C"]["x1"], 0, 30) - np.array([5.0, 15.0, 25.0])
    yc = lin(np.array([149.04, 162.44, 175.83]), F3_RMS_Y[0], F3_RMS_Y[1], 120, 80) - np.array([110.0, 100.0, 90.0])
    meth["checks"]["fig3_tick_residuals"] = dict(time_s=[float(v) for v in tc], level_db=[float(v) for v in yc])

    # ---------------------------------------------------------------- Fig. 3E-H markers (vector fills)
    mk = []
    for d in pg.get_drawings():
        f = d.get("fill"); r = d["rect"]
        if f is None or d.get("color") is not None or r.width > 4 or r.width < 1.0 or abs(r.width - r.height) > 0.3:
            continue
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        pn = "E" if cx < 260 else "F"; P = F3["C" if pn == "E" else "D"]
        if not (P["x0"] - 2 <= cx <= P["x1"] + 2):
            continue
        t = float(lin(cx, P["x0"], P["x1"], 0.0, 30.0) + hms(P["t0"]))
        if F3_VEL_Y[0] - 2 <= cy <= F3_VEL_Y[1] + 2:
            mk.append(dict(panel=pn, triplet=P["sta"], quantity="apparent_velocity_m_s", utc_s_of_day=t, utc=utc(t),
                           value=float(lin(cy, F3_VEL_Y[0], F3_VEL_Y[1], F3_VEL_Y[2], F3_VEL_Y[3])), fill_rgb="%.3f,%.3f,%.3f" % tuple(f)))
        elif F3_BAZ_Y[0] - 2 <= cy <= F3_BAZ_Y[1] + 2:
            mk.append(dict(panel="G" if pn == "E" else "H", triplet=P["sta"], quantity="back_azimuth_deg", utc_s_of_day=t, utc=utc(t),
                           value=float(lin(cy, F3_BAZ_Y[0], F3_BAZ_Y[1], F3_BAZ_Y[2], F3_BAZ_Y[3])), fill_rgb="%.3f,%.3f,%.3f" % tuple(f)))
    mkd = pd.DataFrame(mk).drop_duplicates(subset=["panel", "utc_s_of_day", "value"])
    fn = "fig3EH_detection_windows_DIGITISED.csv"; mkd.to_csv(os.path.join(out, fn), index=False); meth["files"].append(fn)
    meth["checks"]["fig3EH"] = {f"{p}|{q}": dict(n=int(len(x)), first_utc=utc(x.utc_s_of_day.min()), last_utc=utc(x.utc_s_of_day.max()),
                                                median=float(x.value.median()), q05=float(x.value.quantile(0.05)), q95=float(x.value.quantile(0.95)))
                                for (p, q), x in mkd.groupby(["triplet", "quantity"])}
    meth["checks"]["fig3EH_note"] = "marker centres; marker radius ~1.2 pt = 0.2 s, 2.2 m/s, 8 deg (axis-limited resolution of the back azimuth)"

    # ---------------------------------------------------------------- Fig. 2E-H local-station RMS (vector)
    pg2 = doc[3]; rows = []; env2 = {}
    for c, pts in polylines(pg2):
        if pts[:, 1].min() < 500:
            continue
        P = [p for p in F2 if p["x0"] - 2 <= pts[:, 0].mean() <= p["x1"] + 2][0]
        sec_per_pt = 10.0 / (25.9 if P["sta"] != "KSP2" else 25.61)
        t = hms(P["tick_t"]) + (pts[:, 0] - P["tick"]) * sec_per_pt
        L = lin(pts[:, 1], F2_RMS_Y[0], F2_RMS_Y[1], F2_RMS_Y[2], F2_RMS_Y[3]); env2[P["sta"]] = (t, L)
        for ti, Li, x, y in zip(t, L, pts[:, 0], pts[:, 1]):
            rows.append(dict(station=P["sta"], utc_s_of_day=ti, utc=utc(ti), rms_db_re_1uPa=Li, pdf_x_pt=x, pdf_y_pt=y))
    fn = "fig2EH_local_rms_envelopes_vertices_DIGITISED.csv"; pd.DataFrame(rows).to_csv(os.path.join(out, fn), index=False); meth["files"].append(fn)
    meth["checks"]["fig2EH"] = {k: dict(n_vertices=int(len(v[0])), start_utc=utc(v[0].min()), end_utc=utc(v[0].max()), peak_db=float(v[1].max()),
                                       peak_utc=utc(v[0][np.argmax(v[1])]), pre_event_median_db=float(np.median(v[1][v[0] < v[0].min() + 4.0])))
                               for k, v in env2.items()}

    # ---------------------------------------------------------------- Fig. 4 sound-speed profiles (vector)
    pg4 = doc[6]; ss = []
    for c, pts in polylines(pg4, min_items=30):
        if pts[:, 0].min() < F4["x0"] - 1 or pts[:, 1].min() < F4["y0"] - 1 or (pts[:, 1].max() - pts[:, 1].min()) < 200:
            continue
        name = "H11N" if close(c, (0.165, 0.286, 0.463), 3e-3) else ("H11S" if close(c, (0.451, 0.667, 0.82), 3e-3) else None)
        if name is None:
            continue
        v = lin(pts[:, 0], F4["x0"], F4["x1"], F4["v0"], F4["v1"]); z = lin(pts[:, 1], F4["y0"], F4["y1"], F4["d0"], F4["d1"])
        for vi, zi in zip(v, z):
            ss.append(dict(triplet=name, depth_m=zi, sound_speed_m_s=vi))
    ssd = pd.DataFrame(ss); fn = "fig4_h11_soundspeed_DIGITISED.csv"; ssd.to_csv(os.path.join(out, fn), index=False); meth["files"].append(fn)
    meth["checks"]["fig4"] = {k: dict(n=int(len(x)), axis_depth_m=float(x.depth_m.iloc[int(np.argmin(x.sound_speed_m_s))]), c_min=float(x.sound_speed_m_s.min()),
                                     c_surface=float(x.sound_speed_m_s.iloc[int(np.argmin(x.depth_m))])) for k, x in ssd.groupby("triplet")}

    # ---------------------------------------------------------------- spectrogram rasters (colour inversion)
    def raster(pno, idx_min_w=1000):
        p = doc[pno]
        for inf in p.get_image_info(xrefs=True):
            if inf["width"] >= idx_min_w:
                d = doc.extract_image(inf["xref"]); im = np.array(Image.open(io.BytesIO(d["image"])).convert("RGB"))
                return im, inf["bbox"], d
    spec_meta = {}
    for tag, pno, panels, bar, vr, fmax in (
            ("fig3AB", 4, [("H11N1", 0, 714, "11:02:55"), ("H11S1", 892, 1605, "11:03:55")], (1630, 1675), (100.0, 80.0), 80.0),
            ("fig2AD", 3, None, None, (110.0, 90.0), 40.0)):
        im, bb, d = raster(pno)
        Image.fromarray(im).save(os.path.join(out, "rasters", f"{tag}_source_raster_{im.shape[1]}x{im.shape[0]}.png"))
        dark = (im.sum(2) < 200)
        rows_f = np.where(dark.mean(1) > 0.3)[0]; r0, r1 = int(rows_f[rows_f < 10].max()) + 1, int(rows_f[rows_f > im.shape[0] - 10].min()) - 1
        cols_f = np.where(dark.mean(0) > 0.5)[0]
        # group frame columns into runs: [left, right] pairs per panel then the colour bar
        runs = np.split(cols_f, np.where(np.diff(cols_f) > 1)[0] + 1); edges = [(int(r[0]), int(r[-1])) for r in runs]
        if panels is None:
            names = [("DSOH", "10:28:20"), ("KSP1", "10:28:25"), ("KSP2", "10:29:10"), ("KSP3", "10:29:15")]
            panels = [(names[k][0], edges[2 * k][1] + 1, edges[2 * k + 1][0], names[k][1]) for k in range(4)]
            bar = (edges[8][1] + 2, edges[9][0] - 1)
        val, dist = colour_invert(im, bar, vr[0], vr[1], (r0 + 1, r1 - 1))
        white = im.min(2) > 245
        for name, c0, c1, t0 in panels:
            sub = val[r0:r1, c0:c1].copy(); wsub = white[r0:r1, c0:c1]; dsub = dist[r0:r1, c0:c1]
            sub[wsub] = np.nan                                   # at or below the colour-scale floor
            nT, nF = sub.shape[1], sub.shape[0]
            tt = hms(t0) + (np.arange(nT) + 0.5) / nT * 30.0
            ff = fmax * (1 - (np.arange(nF) + 0.5) / nF)
            np.savez_compressed(os.path.join(out, f"{tag}_spectrogram_{name}_DIGITISED.npz"), psd_db_re_1uPa2_Hz=sub.astype(np.float32),
                                utc_s_of_day=tt, freq_hz=ff, floor_db=vr[1], saturation_db=vr[0], colour_distance=dsub.astype(np.float32))
            meth["files"].append(f"{tag}_spectrogram_{name}_DIGITISED.npz")
            spec_meta[name] = dict(figure=tag, pixels=[int(nF), int(nT)], df_hz=fmax / nF, dt_s=30.0 / nT, floor_frac=float(wsub.mean()),
                                   sat_frac=float(np.mean(sub[np.isfinite(sub)] >= vr[0] - 0.25)), colour_dist_p95=float(np.quantile(dsub[~wsub], 0.95)) if (~wsub).any() else None)
    meth["checks"]["spectrograms"] = spec_meta
    # Fig. 1 raster copy
    im1, bb1, d1 = raster(1)
    Image.fromarray(im1).save(os.path.join(out, "rasters", f"fig1_map_source_raster_{im1.shape[1]}x{im1.shape[0]}.png"))

    # ---------------------------------------------------------------- text values
    tv = dict(
        last_radar_contact_utc="10:26:30 (JASDF; 'at or within a few seconds of', below 300 m)", acoustic_origin_time_utc="10:26:32 +/- 9 s",
        position_text="~135 km east of Misawa Air Base; acoustic epicentre within 8 km of the 135 km circle (Fig. 1E, no coordinates)",
        ellipse_90pct=dict(area_km2=844, semi_major_km=36.8, semi_minor_km=7.3), dist_to_H11S_km=3341,
        descent_speed_m_s="~300 (near-supersonic, steep; JASDF report)",
        H11=dict(H11N="55 km NE of Wake, mean depth 727 m, seafloor ~1430 m", H11S="90 km S of Wake, mean depth 739 m, seafloor ~1170 m",
                 aperture_km=2.0, fs_hz=250, band_hz=[4, 64], window_s=6, closure_ms=16, velocity_gate_m_s=[1430, 1530]),
        H11_first_detection_utc=dict(H11N="11:03:00", H11S="11:04:05"), duration_s="6-8 (transients); 'overture' and 'finale' at H11N",
        reading_error_s=dict(H11S1=1.4, KSP2=5.7), back_azimuth_scatter_2sigma_deg=dict(H11N=0.1, H11S=0.05),
        back_azimuth_std_err_used_deg=0.3, travel_time_model_error="1 s per 10 deg geodesic", local_speed_m_s=1475,
        spectral_note="absence of energy above background near 20 Hz, also at the cabled stations",
        local=dict(first_arrivals_utc="10:28:31 (DSOH) - 10:29:21 (KSP3)", ranges_km="180 (DSOH) - 255 (KSP3)", depths_m="2124 (KSP3) - 3428 (KSP2)",
                   fs_hz=100, flat_hz=[1, 40], peak_rms_above_ambient_db=20),
        not_in_paper="impact energy, source level, coupling efficiency, epicentre coordinates (Brown et al. 2026 supply 900 +/- 200 MJ and 0.7 Pa)")
    json.dump(tv, open(os.path.join(out, "text_values.json"), "w"), indent=1); meth["files"].append("text_values.json")

    # ---------------------------------------------------------------- overlays (vector extraction over a 4x render)
    for pno, clip, name, series in ((4, (60, 125, 465, 345), "fig3CDEH", "env"), (3, (60, 495, 465, 580), "fig2EH", "env2"), (6, (300, 120, 495, 455), "fig4", "ss")):
        pix = doc[pno].get_pixmap(matrix=fitz.Matrix(4, 4), clip=fitz.Rect(*clip)); img = Image.open(io.BytesIO(pix.tobytes("png")))
        fig, ax = plt.subplots(figsize=(10, 10 * img.size[1] / img.size[0])); ax.imshow(img, extent=(clip[0], clip[2], clip[3], clip[1]))
        if series == "env":
            for k, (t, L) in env.items():
                P = F3["C" if k.startswith("H11N") else "D"]
                ax.plot(lin(t - hms(P["t0"]), 0, 30, P["x0"], P["x1"]), lin(L, F3_RMS_Y[2], F3_RMS_Y[3], F3_RMS_Y[0], F3_RMS_Y[1]), "r-", lw=0.4)
            for _, r in mkd.iterrows():
                P = F3["C" if r.triplet == "H11N" else "D"]; Y = F3_VEL_Y if r.quantity.startswith("app") else F3_BAZ_Y
                ax.plot(lin(r.utc_s_of_day - hms(P["t0"]), 0, 30, P["x0"], P["x1"]), lin(r.value, Y[2], Y[3], Y[0], Y[1]), "r.", ms=0.6)
        elif series == "env2":
            for k, (t, L) in env2.items():
                P = [p for p in F2 if p["sta"] == k][0]; spp = 10.0 / (25.9 if k != "KSP2" else 25.61)
                ax.plot(P["tick"] + (t - hms(P["tick_t"])) / spp, lin(L, F2_RMS_Y[2], F2_RMS_Y[3], F2_RMS_Y[0], F2_RMS_Y[1]), "r-", lw=0.4)
        else:
            for k, x in ssd.groupby("triplet"):
                ax.plot(lin(x.sound_speed_m_s, F4["v0"], F4["v1"], F4["x0"], F4["x1"]), lin(x.depth_m, F4["d0"], F4["d1"], F4["y0"], F4["y1"]), "r-", lw=0.4)
        ax.set_axis_off(); fig.savefig(os.path.join(out, "overlays", f"{name}_overlay.png"), dpi=200, bbox_inches="tight"); plt.close(fig)
    json.dump(meth, open(os.path.join(out, "METHOD.json"), "w"), indent=1, default=str)
    print(json.dumps(meth["checks"], indent=0, default=str)[:6000])


if __name__ == "__main__":
    main()
