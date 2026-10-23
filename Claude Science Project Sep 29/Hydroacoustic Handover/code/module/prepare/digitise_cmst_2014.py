#!/usr/bin/env python
"""Extract the automatic-detection scatter plots of the CMST report 2014-30 (Duncan, Gavrilov et al., Curtin
University, "MH370 passive acoustics", 33 pp) from the PDF vector paths, and save the embedded figure rasters.

DIGITISED PUBLICATION OBJECTS, NOT DETECTOR OUTPUT. Each detection is drawn as a cross: a horizontal 'l' item
(5 pt wide) and a vertical 'l' item (5 pt tall) centred on the data point, blue for the first detector iteration and
red for the second. The centres are recovered from the horizontal strokes (one per cross), de-duplicated against the
vertical strokes within 0.3 pt, and converted with the tick labels read from the PDF text layer.

  Fig. 5  (p. 14): HA01, all automatic detections 00:00:10-08:00:00 UTC 8 Mar 2014; x = hours after 00:00 UTC (ticks
          0-8), y = arrival bearing deg (ticks 0-350); the orange arrow marks the 01:34:50 arrival at ~301.6 deg.
  Fig. 7  (p. 21): HA08S, 00:00-03:00 UTC; x = hours (ticks 0.5-2.5), y = bearing deg (0-350); black dotted line =
          expected bearing at HA08S vs arrival time for the HA01 01:34:50 signal (saved as a separate series).
  Fig. 10 (p. 24): HA08S detections attributed to the TGS Huzzas 3D seismic survey; x = time (s, ticks 1000-7000,
          origin per caption), y = bearing deg (112-114); magenta = bearing from TGS navigation (saved as a series).
  Fig. 13 (p. 29): bathymetry along 301.61 deg from HA01 and +/-0.75 deg (blue/red/green polylines, x = range km
          0-9000, y = depth m -6000..0); lower panels = transmission-loss style curves 80-180 (saved raw).
Reading uncertainty: the cross centre is exact to the PDF precision (0.01 pt); the axis mapping is a linear fit of
the tick labels, so about 0.005 h (18 s) and 0.3 deg for Figs 5/7, 5 s and 0.003 deg for Fig. 10.
Verification: the cross count against the caption ("blue crosses first iteration, red second"); the orange-arrow
detection (Fig. 5) must sit at 1.58 h, ~301.6 deg; Fig. 7 Table 4 (HA08S detections) is parsed from the text too.

Outputs (--out, default results-data/digitised/cmst-2014/): cmst2014_fig5_ha01_detections_DIGITISED.csv,
cmst2014_fig7_ha08s_detections_DIGITISED.csv, cmst2014_fig7_expected_bearing_line_DIGITISED.csv,
cmst2014_fig10_ha08s_tgs_detections_DIGITISED.csv, cmst2014_fig10_tgs_navigation_bearing_DIGITISED.csv,
cmst2014_fig13_bathymetry_DIGITISED.csv, cmst2014_table4_ha08s.csv, figures/, overlays/, METHOD.json.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re
import numpy as np

T0 = 1394236800  # 00:00 UTC 8 Mar 2014


def num(s):
    try:
        return float(s.replace("\u2212", "-"))
    except ValueError:
        return None


def spans(pg):
    return [(sp["text"].strip(), sp["bbox"]) for b in pg.get_text("dict")["blocks"] if "lines" in b for l in b["lines"] for sp in l["spans"] if sp["text"].strip()]


def axis_fit(sp, frame, which):
    """Linear fit tick-label value vs pdf coordinate. x labels: centred below the frame; y labels: right-aligned left of it."""
    x0, y0, x1, y1 = frame
    if which == "x":
        pts = [(((bb[0] + bb[2]) / 2), num(t)) for t, bb in sp if num(t) is not None and y1 - 1 < bb[1] < y1 + 16 and x0 - 10 <= (bb[0] + bb[2]) / 2 <= x1 + 10 and bb[2] - bb[0] < 40]
    else:
        pts = [(((bb[1] + bb[3]) / 2), num(t)) for t, bb in sp if num(t) is not None and x0 - 30 <= bb[2] <= x0 + 1 and y0 - 8 <= (bb[1] + bb[3]) / 2 <= y1 + 8]
    pts = sorted(set(pts))
    assert len(pts) >= 3, (which, pts)
    p = np.polyfit([a for a, _ in pts], [b for _, b in pts], 1)
    return p, pts


def frame_of(drw, colour=(0.0, 0.0, 0.0), min_w=250):
    """Outer axes frame: the widest black horizontal strokes give y0/y1; the matching verticals give x0/x1."""
    hs = [d["rect"] for d in drw if d.get("color") == colour and d["rect"].width > min_w and d["rect"].height < 0.5]
    vs = [d["rect"] for d in drw if d.get("color") == colour and d["rect"].height > 100 and d["rect"].width < 0.5]
    y0, y1 = min(r.y0 for r in hs), max(r.y0 for r in hs)
    x0, x1 = min(r.x0 for r in vs), max(r.x0 for r in vs)
    return (x0, y0, x1, y1)


def crosses(drw, colour):
    hs, vs = [], []
    for d in drw:
        if d.get("color") != colour or d["type"] != "s":
            continue
        for it in d["items"]:
            if it[0] != "l":
                continue
            a, b = it[1], it[2]
            if abs(a.y - b.y) < 1e-3 and 3 < abs(a.x - b.x) < 8:
                hs.append(((a.x + b.x) / 2, a.y))
            elif abs(a.x - b.x) < 1e-3 and 3 < abs(a.y - b.y) < 8:
                vs.append((a.x, (a.y + b.y) / 2))
    hs = np.array(hs); vs = np.array(vs)
    confirmed = []
    if len(hs) and len(vs):
        for x, y in hs:
            d2 = ((vs[:, 0] - x) ** 2 + (vs[:, 1] - y) ** 2)
            confirmed.append(bool(d2.min() < 0.3 ** 2))
    return hs, np.array(confirmed, bool)


def polylines(drw, colour, min_items=20):
    out = []
    for d in drw:
        if d.get("color") == colour and d["type"] == "s" and len(d["items"]) >= min_items:
            out.append([(it[1].x, it[1].y) for it in d["items"] if it[0] == "l"] + [(d["items"][-1][2].x, d["items"][-1][2].y)])
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results-data", "digitised", "cmst-2014"))
    a = ap.parse_args()
    import fitz, pandas as pd
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from PIL import Image
    out = os.path.abspath(a.out); os.makedirs(os.path.join(out, "figures"), exist_ok=True); os.makedirs(os.path.join(out, "overlays"), exist_ok=True)
    doc = fitz.open(a.pdf); sha = hashlib.sha256(open(a.pdf, "rb").read()).hexdigest()
    hdr = f"# DIGITISED from CMST report 2014-30 (Curtin University) PDF vector paths, sha256 {sha[:16]}; prepare/digitise_cmst_2014.py. Not detector output.\n"
    summary = {}
    # rasters
    for i, pg in enumerate(doc):
        for im in pg.get_images(full=True):
            info = doc.extract_image(im[0])
            if info["width"] >= 500:
                open(os.path.join(out, "figures", f"cmst2014_p{i + 1:02d}_{info['width']}x{info['height']}.{info['ext']}"), "wb").write(info["image"])

    def overlay(pg, frame, series, name, xlabel, ylabel, px, py):
        clip = fitz.Rect(frame[0] - 30, frame[1] - 10, frame[2] + 10, frame[3] + 25); pix = pg.get_pixmap(dpi=200, clip=clip)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.imshow(im, extent=[np.polyval(px, clip.x0), np.polyval(px, clip.x1), np.polyval(py, clip.y1), np.polyval(py, clip.y0)], aspect="auto")
        for lab, (xs, ys, st) in series.items():
            ax.plot(xs, ys, st, ms=4, mfc="none", lw=0.8, label=lab)
        ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.legend(fontsize=7); ax.set_title(f"CMST (2014) {name}: extracted points over the page render", fontsize=9)
        fig.text(0.01, 0.005, "DIGITISED from PDF vector paths; markers = recovered cross centres.", fontsize=7)
        fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(os.path.join(out, "overlays", f"{name}.png"), dpi=110); plt.close(fig)

    # ---- Fig 5 (p.14) and Fig 7 (p.21): detections, bearing vs hours
    for pno, name, station in [(13, "fig5", "HA01"), (20, "fig7", "HA08S")]:
        pg = doc[pno]; drw = pg.get_drawings(); sp = spans(pg)
        frame = frame_of(drw)
        px, xt = axis_fit(sp, frame, "x"); py, yt = axis_fit(sp, frame, "y")
        rows = []
        for colour, it_ in [((0.0, 0.0, 1.0), 1), ((1.0, 0.0, 0.0), 2)]:
            hs, ok = crosses(drw, colour)
            for (x, y), c in zip(hs, ok):
                hours = float(np.polyval(px, x)); brg = float(np.polyval(py, y))
                s = hours * 3600
                rows.append(dict(station=station, iteration=it_, hours_after_0000utc=round(hours, 4), t_utc=f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d}",
                                 t_utc_s=round(s, 1), epoch_s=round(T0 + s, 1), bearing_deg=round(brg, 2), cross_confirmed=int(c), pdf_x=round(x, 3), pdf_y=round(y, 3)))
        df = pd.DataFrame(rows).sort_values("t_utc_s")
        with open(os.path.join(out, f"cmst2014_{name}_{station.lower()}_detections_DIGITISED.csv"), "w") as f:
            f.write(hdr + f"# {name}: automatic detections at {station} on 8 Mar 2014 (x = hours after 00:00 UTC, y = arrival bearing deg); iteration 1 = blue, 2 = red crosses; cross_confirmed = both strokes found.\n")
            df.to_csv(f, index=False)
        summary[name] = dict(station=station, n_iter1=int((df.iteration == 1).sum()), n_iter2=int((df.iteration == 2).sum()), frac_confirmed=float(df.cross_confirmed.mean()),
                             x_ticks=[v for _, v in xt], y_ticks=[v for _, v in yt], hours_range=[float(df.hours_after_0000utc.min()), float(df.hours_after_0000utc.max())])
        series = {"iteration 1": (df[df.iteration == 1].hours_after_0000utc, df[df.iteration == 1].bearing_deg, "o"), "iteration 2": (df[df.iteration == 2].hours_after_0000utc, df[df.iteration == 2].bearing_deg, "s")}
        if name == "fig5":
            near = df[(df.hours_after_0000utc.between(1.5, 1.7)) & (df.bearing_deg.between(290, 315))]
            summary[name]["orange_arrow_candidates"] = near[["t_utc", "bearing_deg", "iteration"]].to_dict("records")
        if name == "fig7":
            # black dotted expected-bearing line: short black strokes/fills inside the frame, not on the axes
            pts = []
            for d in drw:
                if d.get("color") == (0.0, 0.0, 0.0) or d.get("fill") == (0.0, 0.0, 0.0):
                    r = d["rect"]
                    if frame[0] + 2 < r.x0 < frame[2] - 2 and frame[1] + 2 < r.y0 < frame[3] - 2 and r.width < 6 and r.height < 6:
                        pts.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))
            ln = pd.DataFrame([dict(hours_after_0000utc=round(float(np.polyval(px, x)), 4), expected_bearing_deg=round(float(np.polyval(py, y)), 2)) for x, y in pts]).sort_values("hours_after_0000utc")
            with open(os.path.join(out, "cmst2014_fig7_expected_bearing_line_DIGITISED.csv"), "w") as f:
                f.write(hdr + "# Fig. 7 black dotted line: expected arrival bearing at HA08S vs arrival time for the HA01 01:34:50 UTC signal (CMST's own calculation).\n"); ln.to_csv(f, index=False)
            summary[name]["expected_line_points"] = len(ln)
            series["expected bearing (HA01 01:34:50 source)"] = (ln.hours_after_0000utc, ln.expected_bearing_deg, "k.")
        overlay(pg, frame, series, name, "hours after 00:00 UTC, 8 Mar 2014", "arrival bearing (deg)", px, py)
    # ---- Fig 10 (p.24): TGS survey detections, bearing 112-114 vs time (s)
    pg = doc[23]; drw = pg.get_drawings(); sp = spans(pg); frame = frame_of(drw)
    px, xt = axis_fit(sp, frame, "x"); py, yt = axis_fit(sp, frame, "y")
    rows = []
    for colour, it_ in [((0.0, 0.0, 1.0), 1), ((1.0, 0.0, 0.0), 2)]:
        hs, ok = crosses(drw, colour)
        for (x, y), c in zip(hs, ok):
            rows.append(dict(iteration=it_, time_s_axis=round(float(np.polyval(px, x)), 1), bearing_deg=round(float(np.polyval(py, y)), 3), cross_confirmed=int(c)))
    df10 = pd.DataFrame(rows).sort_values("time_s_axis")
    cap = re.sub(r"\s+", " ", pg.get_text())
    with open(os.path.join(out, "cmst2014_fig10_ha08s_tgs_detections_DIGITISED.csv"), "w") as f:
        f.write(hdr + "# Fig. 10: HA08S detections attributed to the TGS Huzzas 3D survey; x axis in seconds as printed (origin: see caption text in METHOD.json), y = bearing deg.\n"); df10.to_csv(f, index=False)
    mag = [((d["rect"].x0 + d["rect"].x1) / 2, (d["rect"].y0 + d["rect"].y1) / 2) for d in drw if d.get("fill") == (1.0, 0.0, 1.0)]
    nav = pd.DataFrame([dict(time_s_axis=round(float(np.polyval(px, x)), 1), bearing_deg=round(float(np.polyval(py, y)), 3)) for x, y in mag]).sort_values("time_s_axis")
    with open(os.path.join(out, "cmst2014_fig10_tgs_navigation_bearing_DIGITISED.csv"), "w") as f:
        f.write(hdr + "# Fig. 10 magenta line: bearing from HA08S to the TGS survey vessel from its navigation data.\n"); nav.to_csv(f, index=False)
    summary["fig10"] = dict(n_detections=len(df10), n_nav_points=len(nav), x_ticks=[v for _, v in xt], y_ticks=[v for _, v in yt], caption=cap[cap.find("Figure 10"):cap.find("Figure 10") + 260])
    overlay(pg, frame, {"detections": (df10.time_s_axis, df10.bearing_deg, "o"), "TGS navigation": (nav.time_s_axis, nav.bearing_deg, "m.")}, "fig10", "time (s, axis as printed)", "bearing (deg)", px, py)
    # ---- Fig 13 (p.29): bathymetry polylines (top panel)
    pg = doc[28]; drw = pg.get_drawings(); sp = spans(pg)
    # three stacked panels; the top one holds the bathymetry (y 142-266 pt): take the first group of horizontal grid lines
    hs = sorted([d["rect"] for d in drw if d.get("color") == (0.0, 0.0, 0.0) and d["rect"].width > 250 and d["rect"].height < 0.5], key=lambda r: r.y0)
    ys = [r.y0 for r in hs]; brk = [i for i in range(1, len(ys)) if ys[i] - ys[i - 1] > 25]
    top_ys = ys[:brk[0]] if brk else ys
    vs = [d["rect"] for d in drw if d.get("color") == (0.0, 0.0, 0.0) and d["rect"].height > 80 and d["rect"].width < 0.5 and abs(d["rect"].y0 - top_ys[0]) < 2]
    top_frame = (min(r.x0 for r in vs), top_ys[0], max(r.x0 for r in vs), top_ys[-1])
    px, xt = axis_fit(sp, top_frame, "x"); py, yt = axis_fit(sp, top_frame, "y")
    rows = []
    for colour, lab in [((0.0, 0.0, 1.0), "301.61"), ((1.0, 0.0, 0.0), "300.86"), ((0.0, 1.0, 0.0), "302.36")]:
        for pl in polylines(drw, colour):
            for x, y in pl:
                if top_frame[1] - 1 <= y <= top_frame[3] + 1:
                    rows.append(dict(bearing_from_ha01_deg=lab, range_km=round(float(np.polyval(px, x)), 1), depth_m=round(float(np.polyval(py, y)), 1)))
    df13 = pd.DataFrame(rows).drop_duplicates().sort_values(["bearing_from_ha01_deg", "range_km"])
    with open(os.path.join(out, "cmst2014_fig13_bathymetry_DIGITISED.csv"), "w") as f:
        f.write(hdr + "# Fig. 13 top panel: bathymetry along 301.61 deg from HA01 (blue) and +/-0.75 deg (red 300.86, green 302.36); colour->bearing assignment per caption order, UNVERIFIED for red/green.\n"); df13.to_csv(f, index=False)
    summary["fig13"] = dict(n_points=len(df13), x_ticks=[v for _, v in xt], y_ticks=[v for _, v in yt])
    # ---- Table 4 (p.21) text
    t21 = doc[20].get_text()
    summary["table4_text"] = re.sub(r"\s+", " ", t21[t21.find("Table 4"):t21.find("Table 4") + 1200])
    json.dump(dict(script="prepare/digitise_cmst_2014.py", pdf_sha256=sha, method=__doc__, summary=summary), open(os.path.join(out, "METHOD.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in summary.items() if k != "table4_text"}, default=str)[:1500])


if __name__ == "__main__":
    main()
