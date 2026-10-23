#!/usr/bin/env python
"""Extract the tabulated ground-truth material (event geometry, times, bearings, tables) and the embedded figure
rasters from three open-access papers used as calibration cases:

  Kadri (2017) Sci. Rep. 7:13949, doi 10.1038/s41598-017-14177-3 (unpaywall PDF, 12 pp):
     EQ1/EQ2 validation earthquakes, the 7 Mar 2014 20:30 UTC "impact" at 6150 km, E1/E2 candidate events at HA01,
     HA01 channel positions/depths, Table 1 (numerical validation). Figures 1, 3b, 7, 8 are embedded rasters
     (1000 px wide) saved at native resolution; Fig. 3a (distance pdfs) is vector and traced from the PDF paths.
  Nielsen et al. (2021) Pure Appl. Geophys. 178:2557-2577, doi 10.1007/s00024-020-02445-9 (CTBTO, ARA San Juan):
     Table 1 (locations, error ellipses, origin times), arrival times from the text, figure rasters (1870 px).
  Vergoz et al. (2021) Pure Appl. Geophys. 178:2527-2556, doi 10.1007/s00024-020-02625-7 (CEA, ARA San Juan):
     Table 1 (reflectors), Table 2 (cepstral delays), origin times and path speeds from the text, figure rasters.

Everything here is DIGITISED (text-layer tables) or a RASTER COPY of a published figure; nothing is a measurement.
Waveform tracing of these rasters (Nielsen Figs 3-5, Vergoz Figs 2-3) is NOT done here: they are 1870-px screen
renders of PMCC/waveform panels with printed axes and can be traced later with the module's raster method if the
weak-signal trials need them (recorded as a next step).

Outputs (--out, default results-data/digitised/ground-truth-cases/): kadri2017_events.csv, kadri2017_table1.csv,
kadri2017_ha01_channels.csv, kadri2017_fig3a_distance_pdfs_DIGITISED.csv, nielsen2021_table1_locations.csv,
nielsen2021_text_times.csv, vergoz2021_table1_reflectors.csv, vergoz2021_table2_cepstral_delays.csv,
vergoz2021_text_values.csv, figures/<paper>_p<page>_<w>x<h>.<ext>, METHOD.json.
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, re
import numpy as np


def save_rasters(doc, tag, outdir, min_w=600):
    saved = []
    for i, pg in enumerate(doc):
        for im in pg.get_images(full=True):
            info = doc.extract_image(im[0])
            if info["width"] >= min_w:
                fn = os.path.join(outdir, f"{tag}_p{i + 1:02d}_{info['width']}x{info['height']}.{info['ext']}")
                open(fn, "wb").write(info["image"]); saved.append(os.path.basename(fn))
    return saved


def kadri2017(doc, out, figdir):
    import pandas as pd
    txt = "\n".join(pg.get_text() for pg in doc)
    ev = [
        dict(event="impact_2014-03-07", kind="unknown impact (meteorite?)", date="2014-03-07", time_utc="20:30", arrival_ha01_utc="21:31:24", lat=-65.5445, lon=32.4730,
             range_km_triangulated=6145, range_km_inverse=6150, bearing_deg=None, bearing_err_deg=None, note="triangulated HA01+HA08; inverse method 6250 km in text p.3, 6150 km in Fig.3a text"),
        dict(event="EQ1", kind="earthquake M5.1 10 km", date="2017-01-13", time_utc="05:30", arrival_ha01_utc=None, lat=-6.762, lon=68.546, range_km_triangulated=2360, range_km_inverse=2500,
             bearing_deg=243.5, bearing_err_deg=0.3, note="standard bearing 243.1; 0.8 deg clockwise systematic correction applied (Li, Gavrilov & Duncan)"),
        dict(event="EQ2", kind="earthquake M5.1 10 km", date="2016-11-28", time_utc="08:07", arrival_ha01_utc=None, lat=-41.857, lon=88.545, range_km_triangulated=5600, range_km_inverse=5500,
             bearing_deg=292.8, bearing_err_deg=0.4, note="standard bearing 293.0"),
        dict(event="E1", kind="weak candidate (MH370 window)", date="2014-03-08", time_utc="01:11-01:16 (source)", arrival_ha01_utc="01:34:40", lat=-23.662, lon=96.676, range_km_triangulated=None, range_km_inverse=1900,
             bearing_deg=301.4, bearing_err_deg=0.4, note="range +/-200 km; cf. Duncan et al. 301.6 +/- 0.75"),
        dict(event="E2", kind="weak candidate (MH370 window)", date="2014-03-08", time_utc="00:25-00:31 (source)", arrival_ha01_utc="00:50:00", lat=-43.487, lon=94.469, range_km_triangulated=None, range_km_inverse=1940,
             bearing_deg=234.6, bearing_err_deg=0.4, note="range +/-200 km; >500 km from 7th arc"),
    ]
    pd.DataFrame(ev).to_csv(os.path.join(out, "kadri2017_events.csv"), index=False)
    m = re.findall(r"(\d+\.\d{3})\n(\d+\.\d{3})\n(\d+\.\d{4})", txt)
    t1 = [dict(distance_actual_km=float(a), distance_calculated_km=float(b), pct_error=float(c)) for a, b, c in m]
    pd.DataFrame(t1).to_csv(os.path.join(out, "kadri2017_table1.csv"), index=False)
    ch = re.findall(r"Channel (\d): latitude (−?-?\d+\.\d+), longitude (\d+\.\d+), depth (\d+)[\s\u2009]m", txt)
    pd.DataFrame([dict(channel=int(c), lat=float(la.replace("−", "-")), lon=float(lo), depth_m=int(d)) for c, la, lo, d in ch]).to_csv(os.path.join(out, "kadri2017_ha01_channels.csv"), index=False)
    # Fig 3a vector traces: page 4, filled grey polygons (three panels), axes 1000-8000 km
    pg = doc[3]; drw = pg.get_drawings()
    # the pdf outlines are black strokes (width 0.23 pt) closing along the panel baseline: 16/16/30 'l' items, x0 = 168.3
    fills = [d for d in drw if d.get("color") == (0.0, 0.0, 0.0) and 168 <= d["rect"].x0 <= 169 and d["rect"].width > 130 and len(d["items"]) in (16, 30)]
    td = pg.get_text("dict")
    spans = [(sp["text"].strip(), sp["bbox"]) for b in td["blocks"] if "lines" in b for l in b["lines"] for sp in l["spans"] if sp["text"].strip()]
    xt = sorted(set((round((bb[0] + bb[2]) / 2, 2), float(t)) for t, bb in spans if t.isdigit() and 1000 <= int(t) <= 8000 and bb[0] < 300))
    rows = []
    if len(xt) >= 2 and fills:
        px, vx = np.polyfit([p for p, _ in xt], [v for _, v in xt], 1), None
        fills.sort(key=lambda d: d["rect"].y0)
        names = ["EQ1", "EQ2", "Impact"]
        for name, d in zip(names, fills[:3]):
            pts = [pt for it in d["items"] if it[0] == "l" for pt in (it[1], it[2])]
            y0, y1 = d["rect"].y1, d["rect"].y0
            # y labels: numbers 0..4 (x1e-4) left of this panel
            yt = sorted(((bb[1] + bb[3]) / 2, float(t)) for t, bb in spans if t in ("0", "1", "2", "3", "4") and bb[2] < d["rect"].x0 and d["rect"].y0 - 8 <= (bb[1] + bb[3]) / 2 <= d["rect"].y1 + 8)
            py = np.polyfit([p for p, _ in yt], [v for _, v in yt], 1) if len(yt) >= 2 else None
            for p in pts:
                rows.append(dict(panel=name, pdf_x=round(p.x, 3), pdf_y=round(p.y, 3), distance_km=round(float(np.polyval(px, p.x)), 1),
                                 pdf_value_x1e_minus4=round(float(np.polyval(py, p.y)), 4) if py is not None else None))
    with open(os.path.join(out, "kadri2017_fig3a_distance_pdfs_DIGITISED.csv"), "w") as f:
        f.write("# DIGITISED from the PDF vector fills of Kadri (2017) Fig. 3a (distance pdfs for EQ1, EQ2, impact); polygon vertices, polygon outline incl. baseline vertices (pdf=0); x ticks 1000-8000 km, y ticks 0-4 (x1e-4). Not a measurement.\n")
        pd.DataFrame(rows).drop_duplicates().to_csv(f, index=False)
    return dict(n_events=len(ev), n_table1=len(t1), n_channels=len(ch), fig3a_vertices=len(rows), fig3a_xticks=xt)


def nielsen(doc, out):
    import pandas as pd
    txt = "\n".join(pg.get_text() for pg in doc).replace("\u0003", "")
    rows = [
        dict(event="2017-11-15 San Juan", solution="H10N+H04S", gt_lat=-45.9499, gt_lon=-59.7730, est_lat=-46.1180, est_lon=-59.6880, dist_km=19.8, bearing_deg=340, semi_major_km=487, semi_minor_km=22, strike_deg=98, origin_utc="13:51:00"),
        dict(event="2017-11-15 San Juan", solution="H10N+H04S+TRQA", gt_lat=-45.9499, gt_lon=-59.7730, est_lat=-46.1175, est_lon=-59.7257, dist_km=19.0, bearing_deg=348, semi_major_km=19, semi_minor_km=12, strike_deg=137, origin_utc="13:51:00"),
        dict(event="2017-12-01 depth charge", solution="H10N+H04S", gt_lat=-45.6667, gt_lon=-59.4150, est_lat=-45.6185, est_lon=-58.9208, dist_km=39, bearing_deg=262, semi_major_km=515, semi_minor_km=23, strike_deg=98, origin_utc="20:04:55"),
    ]
    pd.DataFrame(rows).to_csv(os.path.join(out, "nielsen2021_table1_locations.csv"), index=False)
    tv = [dict(quantity="arrival HA10 (approx)", value="14:58 UTC 2017-11-15", source="text p.5"), dict(quantity="arrival H04S (approx)", value="15:20 UTC 2017-11-15", source="text p.5"),
          dict(quantity="depth charge deployment", value="20:04 UTC 2017-12-01", source="text p.6"), dict(quantity="range to HA10", value="~6000 km (6050 km to H10N mooring)", source="text"),
          dict(quantity="range to HA04", value="~7700 km", source="text"), dict(quantity="coverage ellipse Nov15 hydro only", value="33,659 km2", source="text p.19"),
          dict(quantity="coverage ellipse Nov15 +TRQA", value="748 km2", source="text p.19"), dict(quantity="coverage ellipse Dec1", value="37,212 km2", source="text p.19"),
          dict(quantity="wreck depth / distance from anomaly", value="~900 m / <20 km", source="text p.19")]
    pd.DataFrame(tv).to_csv(os.path.join(out, "nielsen2021_text_times.csv"), index=False)
    return dict(n_rows=len(rows))


def vergoz(doc, out):
    import pandas as pd
    txt = "\n".join(pg.get_text() for pg in doc).replace("\u0003", "").replace("\ufb01", "fi").replace("\ufb02", "fl")
    # Table 1 reflectors: index, station, name (multi-line), lat, lon
    k0 = txt.index("List of identified reflectors"); k1 = txt.find("Table 2", k0); seg = txt[k0:k1 if k1 > 0 else None]
    toks = [t.strip() for t in seg.split("\n") if t.strip()]
    rows, i = [], 0
    while i < len(toks):
        if toks[i].isdigit() and i + 1 < len(toks) and toks[i + 1] in ("H10N", "H04S"):
            idx, st = int(toks[i]), toks[i + 1]; i += 2; name = []
            while i < len(toks) and not re.match(r"^-\s?\d+\.\d+$", toks[i]): name.append(toks[i]); i += 1
            if i + 1 < len(toks):
                lat, lon = float(toks[i].replace(" ", "")), float(toks[i + 1].replace(" ", "")); i += 2
                rows.append(dict(reflector_index=idx, station=st, reflector_name=" ".join(name), lat=lat, lon=lon))
        else:
            i += 1
    pd.DataFrame(rows).to_csv(os.path.join(out, "vergoz2021_table1_reflectors.csv"), index=False)
    seg2 = txt[txt.index("Table of delays measured"):]
    m = re.findall(r"\n(\d{1,2})\n(H10N|H04S)\n(\d+)\n(\d+|–)", seg2)
    t2 = [dict(arrival_index=int(a), station=b, emission_angle_deg=int(c), measured_delay_ms=None if d == "–" else int(d)) for a, b, c, d in m]
    pd.DataFrame(t2).to_csv(os.path.join(out, "vergoz2021_table2_cepstral_delays.csv"), index=False)
    tv = [dict(quantity="San Juan origin time (relocated)", value="2017-11-15 13:51:05 +/- 9 s", source="text"), dict(quantity="calibration grenade origin time", value="2017-12-01 20:04:30 +/- 14 s (announced 20:04:00)", source="text"),
          dict(quantity="velocity model H04S", value="1.460 km/s +/- 4 m/s", source="text"), dict(quantity="measured onset speed H10N / H04S", value="1.477 / 1.463 km/s", source="Fig. caption"),
          dict(quantity="direct arrival speeds", value="1.475-1.485 km/s H10N; 1.485-1.460 km/s H04S (group-speed spread of direct arrivals)", source="text"),
          dict(quantity="relocation accuracy", value="3.5 km from wreck; 95 % ellipse area reduced x100", source="abstract"), dict(quantity="secondary arrivals", value="13 within 15 min after direct arrival", source="abstract")]
    pd.DataFrame(tv).to_csv(os.path.join(out, "vergoz2021_text_values.csv"), index=False)
    return dict(n_reflectors=len(rows), n_table2=len(t2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kadri2017", required=True); ap.add_argument("--nielsen", required=True); ap.add_argument("--vergoz", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results-data", "digitised", "ground-truth-cases"))
    a = ap.parse_args()
    import fitz
    out = os.path.abspath(a.out); figdir = os.path.join(out, "figures"); os.makedirs(figdir, exist_ok=True)
    summary = {}
    for tag, path, fn in [("kadri2017", a.kadri2017, kadri2017), ("nielsen2021", a.nielsen, nielsen), ("vergoz2021", a.vergoz, vergoz)]:
        doc = fitz.open(path); sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
        res = fn(doc, out, figdir) if tag == "kadri2017" else fn(doc, out)
        res["rasters"] = save_rasters(doc, tag, figdir); res["sha256"] = sha
        summary[tag] = res
    json.dump(dict(script="prepare/digitise_ground_truth_cases.py", method=__doc__, summary=summary), open(os.path.join(out, "METHOD.json"), "w"), indent=1, default=str)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "rasters"} | {"n_rasters": len(v["rasters"])} for k, v in summary.items()}, default=str))


if __name__ == "__main__":
    main()
