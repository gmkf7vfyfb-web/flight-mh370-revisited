#!/usr/bin/env python
"""Extract the Figure S1 pressure traces of Kadri (2024, Sci. Rep. 14:10102) Supplementary Information S1 from the
PDF vector paths, with the same method as the archive's `extract_figure_vectors.py` used for Fig. 9.

DIGITISED PUBLICATION OBJECTS, NOT CTBTO WAVEFORM SAMPLES. The PDF holds the plotted polyline vertices (MATLAB
export): processing, filtering, decimation and array-element selection cannot be reconstructed.

Source: 41598_2024_60529_MOESM1_ESM.pdf (Europe PMC supplementary file for PMC11065988; nature.com is not on the
sandbox allowlist). Figure S1 is on p. 5: five panels, 7 March 2014 (the first-route window), spectrogram (raster,
left) and pressure time series (vector, orange (0.851, 0.325, 0.098), right):
  (a) H08S after 17:49 UTC, axis -2..2 x 1e6 uPa; (b) H08S after 18:44, -1..2; (c) H08S after 19:00, -2..2;
  (d) H11S after 19:35, -1..1; (e) H11S after 19:41, -1..1. Time axis 0-10 min on all panels.
Axis calibration: tick-label centres read from the PDF text layer (x labels 0..10 min; y labels left of each axes
box, the colour-bar labels and the 'x10^6' exponent excluded by x position). The vector vertices extend beyond the
visible axes (MATLAB exports the full data; the PDF clips it), so pressures outside the printed range are kept and
flagged `outside_axes=1` (also vertices before 0 min or after 10 min: the plotted series starts about 15 s before the axis).
Verification: the vertex count per panel, the fitted samples/s, the pressure RMS and the fraction outside the axes
are written to METHOD.json; an overlay PNG per panel draws the extracted trace over a 4x render of the page crop.

Outputs (--out, default results-data/digitised/kadri-2024/figS1-vector-traces/):
  kadri-2024-figureS1-panel-<a..e>-<station>.csv  (plotted_time_s, utc, pressure_pa, pdf_x_pt, pdf_y_pt, outside_axes)
  overlays/panel-<x>.png, METHOD.json
"""
from __future__ import annotations
import argparse, hashlib, json, os
from datetime import datetime, timedelta, timezone
import numpy as np

ORANGE = (0.8510000109672546, 0.32499998807907104, 0.09799999743700027)
START = {"17:49": "a", "18:44": "b", "19:00": "c", "19:35": "d", "19:41": "e"}
STATION = {"a": "H08S", "b": "H08S", "c": "H08S", "d": "H11S", "e": "H11S"}
PAGE = 4  # 0-based


def close(c, ref, tol=2e-3):
    return c is not None and all(abs(float(a) - float(b)) <= tol for a, b in zip(c, ref))


def num(s):
    try:
        return float(s.replace("\u2212", "-"))
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results-data", "digitised", "kadri-2024", "figS1-vector-traces"))
    a = ap.parse_args()
    import fitz, pandas as pd
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from PIL import Image
    out = os.path.abspath(a.out); os.makedirs(os.path.join(out, "overlays"), exist_ok=True)
    doc = fitz.open(a.pdf); sha = hashlib.sha256(open(a.pdf, "rb").read()).hexdigest()
    pg = doc[PAGE]; drw = pg.get_drawings()
    td = pg.get_text("dict")
    spans = [(sp["text"].strip(), sp["bbox"]) for b in td["blocks"] if "lines" in b for l in b["lines"] for sp in l["spans"] if sp["text"].strip()]
    # right-hand axes boxes: dark-grey stroked frames wider than 150 pt, x0 > 300
    boxes = sorted(set((round(d["rect"].x0, 2), round(d["rect"].y0, 2), round(d["rect"].x1, 2), round(d["rect"].y1, 2))
                       for d in drw if close(d.get("color"), (0.15, 0.15, 0.15)) and d["rect"].width > 150 and d["rect"].height > 40 and d["rect"].x0 > 300), key=lambda b: b[1])
    assert len(boxes) == 5, boxes
    panels = []
    for (x0, y0, x1, y1) in boxes:
        yt = sorted((((bb[1] + bb[3]) / 2), num(t)) for t, bb in spans if num(t) is not None and abs(num(t)) <= 4 and x0 - 4 < bb[2] <= x0 + 2 and y0 - 6 <= (bb[1] + bb[3]) / 2 <= y1 + 6)
        xt = sorted((((bb[0] + bb[2]) / 2), num(t)) for t, bb in spans if num(t) is not None and y1 < bb[1] <= y1 + 14 and x0 - 8 <= (bb[0] + bb[2]) / 2 <= x1 + 8)
        title = [t for t, bb in spans if "Time [min] after" in t and y1 < bb[1] < y1 + 30 and bb[0] > 300][0]
        start = title.split("after ")[1].split(" UTC")[0]
        py, vy = np.polyfit([p for p, _ in yt], [v for _, v in yt], 1), None
        px = np.polyfit([p for p, _ in xt], [v for _, v in xt], 1)
        panels.append(dict(panel=START[start], station=STATION[START[start]], start=start, box=(x0, y0, x1, y1), y_fit=py, x_fit=px,
                           y_ticks=yt, x_ticks=xt, pa_min=min(v for _, v in yt), pa_max=max(v for _, v in yt)))
    # orange paths -> panel by the median y of their vertices
    orange = [d for d in drw if close(d.get("color"), ORANGE)]
    summary = {}
    for P in panels:
        x0, y0, x1, y1 = P["box"]
        pts = []
        for d in orange:
            v = [pt for it in d["items"] if it[0] == "l" for pt in (it[1], it[2])]
            if not v: continue
            ymed = float(np.median([p.y for p in v]))
            if y0 - 1 <= ymed <= y1 + 1:
                for p in v: pts.append((float(p.x), float(p.y), d["seqno"]))
        # de-duplicate consecutive repeated vertices (segment end == next start)
        arr = np.array(pts); arr = arr[np.lexsort((arr[:, 1], arr[:, 0]))] if False else arr
        # keep drawing order (seqno then original order), then drop exact duplicates of the previous vertex
        keep = np.ones(len(arr), bool); keep[1:] = ~((arr[1:, 0] == arr[:-1, 0]) & (arr[1:, 1] == arr[:-1, 1]))
        arr = arr[keep]
        t_min = np.polyval(P["x_fit"], arr[:, 0]); pa = np.polyval(P["y_fit"], arr[:, 1])  # pressure in the printed unit (x1e6 uPa = Pa)
        t0 = datetime(2014, 3, 7, int(P["start"][:2]), int(P["start"][3:]), tzinfo=timezone.utc)
        order = np.argsort(t_min, kind="stable"); arr, t_min, pa = arr[order], t_min[order], pa[order]
        outside = ((pa < P["pa_min"]) | (pa > P["pa_max"]) | (t_min < 0) | (t_min > 10)).astype(int)
        df = pd.DataFrame(dict(plotted_time_s=np.round(t_min * 60, 6), utc=[(t0 + timedelta(seconds=float(s))).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" for s in t_min * 60],
                               pressure_pa=np.round(pa, 6), pdf_x_pt=np.round(arr[:, 0], 4), pdf_y_pt=np.round(arr[:, 1], 4), outside_axes=outside))
        fn = os.path.join(out, f"kadri-2024-figureS1-panel-{P['panel']}-{P['station']}.csv")
        with open(fn, "w") as f:
            f.write(f"# DIGITISED PDF vector vertices, Kadri (2024) Supplementary Figure S1 panel ({P['panel']}) {P['station']}, 7 Mar 2014 from {P['start']} UTC; S1 pdf sha256 {sha[:16]}; prepare/digitise_kadri_2024_s1.py. Not CTBTO samples.\n")
            df.to_csv(f, index=False)
        dt = np.diff(df.plotted_time_s.values); dt = dt[dt > 0]
        summary[P["panel"]] = dict(station=P["station"], start_utc=P["start"], n_vertices=int(len(df)), median_dt_s=float(np.median(dt)), samples_per_s=float(1 / np.median(dt)),
                                   rms_pa=float(np.sqrt(np.mean(pa ** 2))), frac_outside_axes=float(outside.mean()), axes_pa=[P["pa_min"], P["pa_max"]],
                                   y_fit_pa_per_pt=float(P["y_fit"][0]), x_fit_min_per_pt=float(P["x_fit"][0]))
        # overlay
        clip = fitz.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2); pix = pg.get_pixmap(dpi=288, clip=clip)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        fig, ax = plt.subplots(figsize=(9, 3.6))
        ax.imshow(im, extent=[np.polyval(P["x_fit"], clip.x0) * 60, np.polyval(P["x_fit"], clip.x1) * 60, np.polyval(P["y_fit"], clip.y1), np.polyval(P["y_fit"], clip.y0)], aspect="auto")
        vis = df[df.outside_axes == 0]
        ax.plot(vis.plotted_time_s, vis.pressure_pa, color="cyan", lw=0.3, alpha=0.8)
        ax.set_xlabel(f"seconds after {P['start']} UTC, 7 Mar 2014"); ax.set_ylabel("Pressure (Pa)")
        ax.set_title(f"Kadri (2024) Fig. S1 panel ({P['panel']}) {P['station']}: extracted vector trace (cyan) over the page render", fontsize=9)
        fig.text(0.01, 0.005, "DIGITISED from PDF vector paths; vertices outside the printed axes kept in the CSV (flagged) but not drawn here.", fontsize=7)
        fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(os.path.join(out, "overlays", f"panel-{P['panel']}.png"), dpi=110); plt.close(fig)
    # spectrogram rasters (left panels) saved as embedded images
    for k, im in enumerate(pg.get_images(full=True)):
        info = doc.extract_image(im[0])
        if info["width"] > 100:
            open(os.path.join(out, f"figS1_spectrogram_raster_{k}_{info['width']}x{info['height']}.{info['ext']}"), "wb").write(info["image"])
    json.dump(dict(script="prepare/digitise_kadri_2024_s1.py", pdf_sha256=sha, method=__doc__, summary=summary), open(os.path.join(out, "METHOD.json"), "w"), indent=1)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
