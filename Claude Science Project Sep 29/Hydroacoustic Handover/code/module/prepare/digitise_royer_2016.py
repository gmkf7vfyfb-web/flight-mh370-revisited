#!/usr/bin/env python
"""Digitise Royer (2016), OHASISBIO report LDO-201608 (18 pp).

Everything this script writes is DIGITISED data (text-layer OCR of the tables, embedded JPX rasters
of the figures with pixel->time/frequency calibration, and a colour->dB inversion of the spectrograms).

Inputs
  --pdf   path to royer-2016-LDO-201608.pdf (the public PDF; sha256 prefix 2e7190b96c7bb774).
Outputs (--out, default results-data/digitised/royer-2016/)
  royer_stations.csv      Table 1 (positions, site depth, hydrophone depth), decimal degrees.
  royer_sensitivity.csv   Table 3 (uV/count, dB re 1 uPa/V).
  royer_events.csv        Table 4 (20 solutions) joined with Table 2 labels: origin time, position, standard errors.
  royer_arrivals.csv      Table 5, long format: event index x station -> picked arrival (UTC), with the implied
                          path speed (geodesic / (arrival - origin)) as the verification check.
  royer_map_labels.csv    Arrival times printed on the Fig. 4-8 maps (read by eye) against Table 5.
  royer_figure_marks.csv  Author's arrows (appendix strips) and pick bars (Figs 4-8) converted to UTC, against the nearest Table 5 pick.
  figures/<id>.png        Embedded rasters at native resolution (JPX -> PNG, lossless re-encode).
  figures/<id>_calibration.json   Pixel frames and the time/frequency axis mapping of each spectrogram panel.
  spectrograms/<panel>.npz        dB grid (float16) per panel: t_utc_s (seconds after 00:00 UTC 8 Mar 2014), f_hz, psd_db.
  spectrograms/<panel>_band.csv   Mean dB over 5-40 Hz and 10-15 Hz against time (one row per pixel column).
  overlays/<panel>.png            Check image: panel crop with the calibrated tick grid and the band series under it.

Method notes (also written to METHOD.json)
  * Tables come from the PDF text layer (pdf has real text, not a scan), parsed by position in the token stream.
  * Panel frames are found as connected regions of saturated colour; the time axis is linear between the first
    and last printed tick label of each panel (read by eye once, stored in PANELS below). Reading uncertainty:
    +-1 px in frame edges = +-0.3 s for 3-min panels, +-4 s for the 45-min Fig. 2 panels. The appendix strips are
    NOT 30 min wide: they run about 33 min (the frame continues past the last label), so they are calibrated on
    the detected 5-min tick series (about 192 px per 5 min, 1.56 s per px); +-1.6 s.
  * Colour -> dB uses MATLAB/matplotlib 'jet' over 70-100 dB (the printed colour bar); nearest RGB after JPX
    compression. Expect +-1.5 dB per pixel and a bias where saturated pixels (>100 dB) are clipped at 100.
  * The 3-min panels in Figs 4-8 are about 0.28 s per pixel column; the spectrogram itself was computed with
    hann(256), 80 % overlap, at 240 Hz (OHASISBIO) or 250 Hz (H01W), i.e. about 0.21 s hop; so the raster is
    close to the native time resolution but the frequency axis (0-60 Hz over ~190 px) is coarser than the FFT bin.
"""
from __future__ import annotations
import argparse, json, os, re, sys, hashlib
import numpy as np

T0 = 1394236800  # 00:00 UTC 8 Mar 2014

# ---- panel definitions: (page, image-index, panel-order top->bottom, label, t_start, t_end, f_top, note)
PANELS = {
    "fig2_h01w2": dict(page=4, img=0, rotate=0, panels=[
        ("H01W-2", "00:15", "01:00", 125.0), ("H01W-2", "01:00", "01:45", 125.0)],
        note="Figure 2, p.4; S1 arrow at ~00:52, S2 at ~01:34; srate 250 so f_top = Nyquist 125 Hz (tick labels 0/50/100 only)."),
    "fig4_eventA": dict(page=8, img=0, rotate=0, panels=[
        ("MAD", "01:03", "01:06", 60.0), ("H01W-2", "00:51", "00:54", 60.0),
        ("WKER", "00:41", "00:44", 60.0), ("SWAMS-3", "00:36", "00:39", 60.0)],
        note="Figure 4, p.8, event A (iceberg). Black bars above each panel mark the author's pick window."),
    "fig5_eventB": dict(page=9, img=0, rotate=0, panels=[
        ("MAD", "01:06", "01:09", 60.0), ("SWAMS-2", "00:46", "00:49", 60.0),
        ("SWAMS-3", "00:46", "00:49", 60.0), ("H01W-2", "00:34", "00:37", 60.0)],
        note="Figure 5, p.9, event B. MAD/SWAMS bars carry a '?'. H01W-2 bar ~00:36:08-00:36:35."),
    "fig6_eventC1": dict(page=10, img=0, rotate=0, panels=[
        ("MAD", "01:07", "01:10", 60.0), ("SSEIR", "01:10", "01:13", 60.0),
        ("NCRO", "01:25", "01:28", 60.0), ("H01W-2", "01:33", "01:36", 60.0)],
        note="Figure 6, p.10, event C1 (Chagos Bank solution)."),
    "fig7_eventC2": dict(page=11, img=0, rotate=0, panels=[
        ("H01W-2", "01:33", "01:36", 60.0), ("SSEIR", "01:10", "01:13", 60.0),
        ("SWAMS-3", "01:18", "01:21", 60.0), ("NCRO", "01:30", "01:33", 60.0)],
        note="Figure 7, p.11, event C2 (west of 90E Ridge), same H01W event as Fig. 6."),
    "fig8_eventD2": dict(page=12, img=0, rotate=0, panels=[
        ("H01W-2", "01:29", "01:32", 125.0), ("SSEIR", "01:30", "01:33", 120.0),
        ("SWAMS-3", "01:32", "01:35", 120.0), ("MAD", "01:45", "01:48", 120.0)],
        note="Figure 8, p.12, event D2. Right-hand label of the MAD panel is printed '01:58' (typo for 01:48; tick spacing is 3 min). f axis 0-50-100; top = Nyquist."),
    "appendix_swams3": dict(page=16, img=0, rotate=-90, panels=[
        ("SWAMS-3", "00:00", "00:30", 60.0), ("SWAMS-3", "00:30", "01:00", 60.0),
        ("SWAMS-3", "01:00", "01:30", 60.0), ("SWAMS-3", "01:30", "02:00", 60.0)],
        note="Appendix p.16, SWAMS-3 00:00-02:00, four 30-min strips (page rotated)."),
    "appendix_sseir": dict(page=17, img=0, rotate=-90, panels=[
        ("SSEIR", "00:00", "00:30", 60.0), ("SSEIR", "00:30", "01:00", 60.0),
        ("SSEIR", "01:00", "01:30", 60.0), ("SSEIR", "01:30", "02:00", 60.0)],
        note="Appendix p.17, SSEIR 00:00-02:00, four 30-min strips (page rotated). Black arrows = author's picks."),
    "appendix_h01w2": dict(page=18, img=0, rotate=-90, panels=[
        ("H01W-2", "00:00", "00:30", 60.0), ("H01W-2", "00:30", "01:00", 60.0),
        ("H01W-2", "01:00", "01:30", 60.0), ("H01W-2", "01:30", "02:00", 60.0)],
        note="Appendix p.18, H01W-2 00:00-02:00, four 30-min strips (page rotated), srate 250. Black arrows = author's picks."),
}
# Maps (Figs 3-9) and the network map (Fig 1) are saved as rasters only.
RASTER_ONLY = {"fig1_network_map": (3, 0), "fig3_candidates_map": (5, 0),
               "fig4_mapA": (8, 1), "fig5_mapB": (9, 1), "fig6_mapC1": (10, 1), "fig7_mapC2": (11, 1),
               "fig8_mapD2": (12, 1), "fig9_all_events_map": (13, 0)}

# Arrival-time labels printed on the Fig 4-8 maps (read by eye from the 492x478 rasters; +-1 s reading).
MAP_LABELS = [
    ("A", 3, "MAD", "01:04:24"), ("A", 3, "WKER", "00:42:04"), ("A", 3, "SWAMS", "00:37:37"), ("A", 3, "H01W", "00:51:59"),
    ("B", 4, "MAD", "01:07:34"), ("B", 4, "SWAMS", "00:47:42"), ("B", 4, "H01W", "00:36:10"),
    ("C1", 7, "MAD", "01:07:40"), ("C1", 7, "NCRO", "01:26:24"), ("C1", 7, "SSEIR", "01:11:15"), ("C1", 7, "H01W", "01:34:47"),
    ("C2", 11, "SSEIR", "01:11:20"), ("C2", 11, "SWAMS", "01:19:01"), ("C2", 11, "NCRO", "01:31:35"), ("C2", 11, "H01W", "01:34:49"),
    ("D2", 15, "MAD", "01:45:23"), ("D2", 15, "SSEIR", "01:31:13"), ("D2", 15, "NCRO", "01:49:48"), ("D2", 15, "H01W", "01:29:56"),
]


def hms(s: str) -> float:
    s = s.strip().rstrip("(*)").strip()
    p = s.split(":")
    v = int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2]) if len(p) == 3 else int(p[0]) * 3600 + int(p[1]) * 60
    return v


def dm(tok: str) -> float:
    """'053°05.05’E' or '074˚36.30’E' -> decimal degrees (sign from hemisphere)."""
    m = re.match(r"(\d+)[°˚](\d+\.\d+)[’'](\w)", tok)
    d, mi, h = int(m.group(1)), float(m.group(2)), m.group(3)
    v = d + mi / 60
    return -v if h in "SW" else v


def parse_tables(doc):
    txt = [doc[i].get_text() for i in range(len(doc))]
    # Table 1 (page 3)
    p3 = txt[2]
    stations = []
    coords = re.findall(r"(\d{3}[°˚]\d+\.\d+[’']\w)\s+(\d{2}[°˚]\d+\.\d+[’']\w)", p3)
    names = ["NCRO", "WKER", "SWAMS1", "SWAMS2", "SWAMS3", "NEAMS", "SSEIR", "MAD"]
    sdep = [3310, 4530, 3450, 3460, 3450, 3850, 4180, 5220]
    hdep = [1050, 970, 1090, 1100, 1090, 1090, 1180, 1260]
    for n, (lo, la), sd, hd in zip(names, coords, sdep, hdep):
        lat = dm(la); lon = dm(lo); note = ""
        if n == "SWAMS1" and lat > 0:
            lat = -lat; note = "Table 1 prints 43˚02.62’E for the latitude (typo); taken as S"
        stations.append(dict(station=n, lat_deg=round(lat, 5), lon_deg=round(lon, 5), site_depth_m=sd, hydrophone_depth_m=hd,
                             network="OHASISBIO", status="lost on recovery, no data" if n == "NEAMS" else "recorded", note=note))
    dec = re.findall(r"(\d{3}\.\d{6})[°˚]E\s+(\d{2}\.\d{6})[°˚]S", p3)
    for (lo, la), n in zip(dec, ["H08S1", "H08S2", "H08S3", "H01W1", "H01W2", "H01W3"]):
        stations.append(dict(station=n, lat_deg=-float(la), lon_deg=float(lo), site_depth_m="", hydrophone_depth_m=800,
                             network="IMS-CTBTO", status="recorded", note="Table 1 gives 800 m hydrophone depth"))
    # Table 3 (page 13)
    sens = [dict(site=s, uV_per_count=u, sensitivity_dB_re_1uPa_per_V=d) for s, u, d in
            zip(["NCRO", "WKER", "SWAMS1-2-3", "SSEIR", "MAD", "H08S", "H01"],
                [0.298] * 5 + [0.848] * 2, [-164] * 5 + [-174] * 2)]
    # Table 2 (page 5) labels
    t2 = re.findall(r"\n(A|B|C1|C2|D1|D2)\s*\n(\d\d:\d\d:\d\d\.\d)\s*\n\s*(-?\d+\.\d+)\s*\n\s*(\d+\.\d+)\s*\n\s*(\d+\.\d+)\s*\n\s*(\d+\.\d+)\s*\n\s*(\d+\.\d+)\s*\n(\d)", txt[4])
    table2 = {r[0]: r for r in t2}
    # Table 4 (page 14)
    t4 = re.findall(r"\n(\d{1,2})\s*\n([^\n]+?)\s*\n(\d\d:\d\d:\d\d\.\d(?: \(\*\))?)\s*\n\s*(-?\d+\.\d+)\s*\n\s*(\d+\.\d+)\s*\n\s*(\d+\.\d+)\s*\n\s*(\d+\.\d+)\s*\n\s*(\d+\.\d+)\s*\n(\d)", txt[13])
    events = []
    for idx, typ, ot, la, lo, ela, elo, et, n in t4:
        label = typ.split()[0] if typ.split()[0] in ("A", "B", "C1", "C2", "C3", "C4", "D1", "D2") else ""
        cls = ("icequake" if "cequake" in typ else "earthquake" if "arthquake" in typ else "uncertain")
        day = "2014-03-07" if "(*)" in ot else "2014-03-08"
        ot_s = hms(ot) - (86400 if day == "2014-03-07" else 0)
        chk = ""
        if label in table2:
            r = table2[label]
            chk = "matches Table 2" if (r[1] == ot.split(" ")[0] and float(r[2]) == float(la) and float(r[3]) == float(lo)) else "DIFFERS from Table 2"
        events.append(dict(index=int(idx), label=label, event_class=cls, type_text=typ.strip(), origin_date=day,
                           origin_time_utc=ot.split(" ")[0], origin_s_after_T0=round(ot_s, 1), lat_deg=float(la), lon_deg=float(lo),
                           err_lat_deg=float(ela), err_lon_deg=float(elo), err_time_s=float(et), n_hydrophones=int(n), table2_check=chk))
    assert len(events) == 20, len(events)
    # Table 5 (page 15)
    toks = [t.strip() for t in txt[14].split("\n") if t.strip()]
    i = toks.index("H01W3") + 1
    cols = ["MAD", "NCRO", "WKER", "SSEIR", "SWAMS1", "SWAMS2", "SWAMS3", "H01W1", "H01W2", "H01W3"]
    arrivals = []
    while i < len(toks) and toks[i].isdigit():
        idx = int(toks[i]); i += 2  # skip type
        ot = toks[i]; i += 1
        vals = toks[i:i + 10]; i += 10
        for c, v in zip(cols, vals):
            arrivals.append(dict(index=idx, origin_time_utc=ot, station=c, arrival_utc=None if v == "X" else v))
    assert len(arrivals) == 200, len(arrivals)
    return stations, sens, events, arrivals


def geodesic_km(lat1, lon1, lat2, lon2):
    from pyproj import Geod
    g = Geod(ellps="WGS84")
    return g.inv(lon1, lat1, lon2, lat2)[2] / 1000.0



def detect_ticks(arr, frame, lo=150, hi=300):
    """Regularly spaced dark tick marks just inside the bottom edge of a frame. Returns (cols, spacing_px) or (None, None)."""
    r0, r1, c0, c1 = frame
    sub = arr[r1 - 12:r1 - 4, c0 + 3:c1 - 3].astype(int).sum(-1)
    cols = np.where((sub < 150).sum(0) >= 4)[0] + c0 + 3
    if len(cols) == 0:
        return None, None
    groups = np.split(cols, np.where(np.diff(cols) > 2)[0] + 1)
    cand = np.array([g.mean() for g in groups if len(g)])
    best = (0, None, None)
    for i in range(len(cand)):
        for j in range(i + 1, len(cand)):
            s = cand[j] - cand[i]
            if not (lo <= s <= hi):
                continue
            k = np.round((cand - cand[i]) / s)
            ok = np.abs(cand - (cand[i] + k * s)) < 2.5
            n = int(ok.sum())
            if n > best[0]:
                best = (n, cand[ok], s)
    if best[0] < 4 or len(cand) > 10:   # fewer than 4 regular ticks, or the strip is crossed by shot lines
        return None, None
    members = best[1]
    k = np.round((members - members[0]) / best[2])
    spacing = np.polyfit(k, members, 1)[0]
    return members, float(spacing)


def detect_arrows(arr, frame):
    """Columns (centre) of black arrow markers inside the upper 45 % of a frame."""
    from scipy import ndimage
    r0, r1, c0, c1 = frame
    top = arr[r0 + 2:r0 + int(0.45 * (r1 - r0)), c0 + 3:c1 - 3].astype(int).sum(-1) < 120
    lab, n = ndimage.label(top)
    out = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if h > 15 and w > 4:
            out.append(float((sl[1].start + sl[1].stop) / 2 + c0 + 3))
    return out


def detect_bars(arr, frame, prev_bottom):
    """Black (or white, on the Fig. 8 dark background) horizontal pick bars printed above a frame: list of (col_start, col_end)."""
    from scipy import ndimage
    r0, r1, c0, c1 = frame
    bars = []
    band = arr[max(prev_bottom + 2, r0 - 40):r0 - 1, c0:c1].astype(int)
    for mask in (band.sum(-1) < 120,):
        lab, n = ndimage.label(mask)
        for sl in ndimage.find_objects(lab):
            h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if w > 12 and h <= 8:
                bars.append((float(sl[1].start + c0), float(sl[1].stop - 1 + c0)))
    # white bars drawn inside the top of the frame (Fig. 8, dark background)
    top = arr[r0:r0 + int(0.12 * (r1 - r0)), c0 + 2:c1 - 2].astype(int)
    white = top.min(-1) > 225
    lab, n = ndimage.label(white)
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if w > 25 and 2 <= h <= 10:
            bars.append((float(sl[1].start + c0 + 2), float(sl[1].stop - 1 + c0 + 2)))
    return sorted(bars)


def frames_from_image(arr):
    """Bounding boxes of the spectrogram panels: connected regions of saturated colour wider than 40 % of the image."""
    from scipy import ndimage
    rgb = arr[..., :3].astype(float) / 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    mask = (sat > 0.45) & (mx > 0.35)
    mask = ndimage.binary_closing(mask, iterations=3)
    mask = ndimage.binary_opening(mask, iterations=2)
    lab, n = ndimage.label(mask)
    boxes = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if w > 0.4 * arr.shape[1] and h > 40:
            boxes.append((sl[0].start, sl[0].stop, sl[1].start, sl[1].stop))
    boxes.sort()
    return boxes


def jet_lut(n=256):
    import matplotlib
    cm = matplotlib.colormaps["jet"]
    return (cm(np.linspace(0, 1, n))[:, :3] * 255).astype(float)


def rgb_to_db(crop, lut, lo=70.0, hi=100.0):
    px = crop[..., :3].reshape(-1, 3).astype(float)
    # nearest colour in LUT (chunked)
    idx = np.empty(len(px), dtype=np.int32)
    for s in range(0, len(px), 200000):
        d = ((px[s:s + 200000, None, :] - lut[None, :, :]) ** 2).sum(-1)
        idx[s:s + 200000] = d.argmin(1)
    return (lo + (hi - lo) * idx / (len(lut) - 1)).reshape(crop.shape[:2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results-data", "digitised", "royer-2016"))
    a = ap.parse_args()
    import fitz, pandas as pd
    from PIL import Image
    import io
    out = os.path.abspath(a.out)
    for d in ("figures", "spectrograms", "overlays"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    doc = fitz.open(a.pdf)
    sha = hashlib.sha256(open(a.pdf, "rb").read()).hexdigest()
    stations, sens, events, arrivals = parse_tables(doc)
    st = pd.DataFrame(stations); st.to_csv(os.path.join(out, "royer_stations.csv"), index=False)
    pd.DataFrame(sens).to_csv(os.path.join(out, "royer_sensitivity.csv"), index=False)
    ev = pd.DataFrame(events); ev.to_csv(os.path.join(out, "royer_events.csv"), index=False)
    # arrivals + implied speed check
    pos = {r.station: (r.lat_deg, r.lon_deg) for r in st.itertuples()}
    evi = ev.set_index("index")
    rows = []
    for r in arrivals:
        e = evi.loc[r["index"]]
        d = dict(index=r["index"], label=e.label, event_class=e.event_class, origin_time_utc=e.origin_time_utc,
                 station=r["station"], arrival_utc=r["arrival_utc"], arrival_s_after_T0=None, range_km=None, travel_s=None, implied_speed_km_s=None)
        if r["arrival_utc"]:
            arr_s = hms(r["arrival_utc"])
            rng = geodesic_km(e.lat_deg, e.lon_deg, *pos[r["station"]])
            tr = arr_s - e.origin_s_after_T0
            d.update(arrival_s_after_T0=round(arr_s, 2), range_km=round(rng, 1), travel_s=round(tr, 2),
                     implied_speed_km_s=round(rng / tr, 4) if tr > 0 else None)
        rows.append(d)
    ar = pd.DataFrame(rows); ar.to_csv(os.path.join(out, "royer_arrivals.csv"), index=False)
    # map labels
    ml = []
    for lab, idx, stn, t in MAP_LABELS:
        col = {"SWAMS": "SWAMS1", "H01W": "H01W1"}.get(stn, stn)
        tab = ar[(ar["index"] == idx) & (ar.station == col)].arrival_utc.iloc[0]
        ml.append(dict(label=lab, index=idx, station=stn, map_label_utc=t, table5_station=col, table5_arrival_utc=tab,
                       map_minus_table5_s=round(hms(t) - hms(tab), 2) if tab else None))
    pd.DataFrame(ml).to_csv(os.path.join(out, "royer_map_labels.csv"), index=False)

    # rasters
    lut = jet_lut()
    calib_all = {}
    marks = []
    def get_img(page, k):
        pg = doc[page - 1]; im = pg.get_images(full=True)[k]
        info = doc.extract_image(im[0])
        return Image.open(io.BytesIO(info["image"])).convert("RGB"), info
    for fid, (page, k) in RASTER_ONLY.items():
        im, info = get_img(page, k)
        im.save(os.path.join(out, "figures", f"{fid}_p{page:02d}_{im.width}x{im.height}.png"))
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    for fid, spec in PANELS.items():
        im, info = get_img(spec["page"], spec["img"])
        if spec["rotate"]:
            im = im.rotate(spec["rotate"], expand=True)
        arr = np.asarray(im)
        im.save(os.path.join(out, "figures", f"{fid}_p{spec['page']:02d}_{im.width}x{im.height}.png"))
        boxes = frames_from_image(arr)
        # drop the colour bar (narrow) already by width; keep the first len(panels) tallest-by-order boxes
        if len(boxes) != len(spec["panels"]):
            print(f"WARNING {fid}: found {len(boxes)} frames, expected {len(spec['panels'])}: {boxes}", file=sys.stderr)
        cal = dict(source="Royer 2016 LDO-201608", sha256=sha, page=spec["page"], note=spec["note"], image_size=[im.width, im.height],
                   rotate_deg=spec["rotate"], panels=[])
        prev_bottom = 0
        for (stn, t0, t1, ftop), (r0, r1, c0, c1) in zip(spec["panels"], boxes):
            ts, te = hms(t0), hms(t1)
            crop = arr[r0:r1, c0:c1]
            db = rgb_to_db(crop, lut)
            nt, nf = c1 - c0, r1 - r0
            tick_cols, tick_sp = detect_ticks(arr, (r0, r1, c0, c1))
            axis_note = "frame = printed span (tick spacing verified)"
            if fid.startswith("appendix"):
                # Strips are NOT exactly 30 min: the printed labels are 5 min apart and the frame runs on past the
                # last label. Calibrate on the detected tick series: first regular tick = start label + 5 min.
                # Fixed geometry shared by all 12 strips: the start label sits at the frame's left edge and the printed
                # labels are 192.0 px apart (verified on 8 strips with clean tick detection: 191.9-192.0 px; the other
                # 4 strips are crossed by seismic-shot lines that defeat the tick detector, so the fixed value is used).
                if tick_cols is not None:
                    # clean tick series: calibrate on it (handles the two strips whose geometry differs: H01W-2 strip 1
                    # starts about 1 min late, SSEIR strip 4 has 258.7 px per 5 min and ends at 01:54:30)
                    s_per_px = 300.0 / tick_sp
                    ts = ts + 300.0 - (tick_cols[0] - c0) * s_per_px
                    te = ts + nt * s_per_px
                    axis_note = f"tick-calibrated: {len(tick_cols)} ticks, {tick_sp:.1f} px per 5 min; frame spans {ts:.0f}-{te:.0f} s"
                else:
                    s_per_px = 300.0 / 192.0
                    te = ts + nt * s_per_px
                    axis_note = f"fixed strip geometry 192 px per 5 min (1.5625 s/px; verified on the 8 clean strips), frame spans {ts:.0f}-{te:.0f} s; tick detector defeated by shot lines"
            t = ts + (np.arange(nt) + 0.5) * (te - ts) / nt
            for col in detect_arrows(arr, (r0, r1, c0, c1)):
                tt = ts + (col - c0) * (te - ts) / nt
                marks.append(dict(figure=fid, station=stn, kind="arrow", t_utc_s=round(tt, 1), t_utc=f"{int(tt // 3600):02d}:{int(tt % 3600 // 60):02d}:{tt % 60:05.2f}", col_px=col))
            for b0, b1 in detect_bars(arr, (r0, r1, c0, c1), prev_bottom):
                ta, tb = ts + (b0 - c0) * (te - ts) / nt, ts + (b1 - c0) * (te - ts) / nt
                marks.append(dict(figure=fid, station=stn, kind="pick_bar", t_utc_s=round(ta, 1), t_end_utc_s=round(tb, 1),
                                  t_utc=f"{int(ta // 3600):02d}:{int(ta % 3600 // 60):02d}:{ta % 60:05.2f}", t_end_utc=f"{int(tb // 3600):02d}:{int(tb % 3600 // 60):02d}:{tb % 60:05.2f}", col_px=b0))
            prev_bottom = r1
            f = ftop * (1 - (np.arange(nf) + 0.5) / nf)
            pid = f"{fid}_{stn.replace('-', '').lower()}_{t0.replace(':', '')}-{t1.replace(':', '')}"
            np.savez_compressed(os.path.join(out, "spectrograms", pid + ".npz"), t_utc_s=t.astype(np.float64), f_hz=f.astype(np.float32),
                                psd_db=db.astype(np.float16), station=stn, t_start=t0, t_end=t1, f_top_hz=ftop)
            band = lambda lo, hi: db[(f >= lo) & (f <= hi)].mean(0)
            bd = pd.DataFrame(dict(t_utc_s=np.round(t, 2), psd_db_5_40=np.round(band(5, 40), 2), psd_db_10_15=np.round(band(10, 15), 2),
                                   psd_db_2_60=np.round(band(2, min(60, ftop)), 2)))
            bd.to_csv(os.path.join(out, "spectrograms", pid + "_band.csv"), index=False)
            cal["panels"].append(dict(panel_id=pid, station=stn, t_start_utc=t0, t_end_utc=t1, t_start_s=round(ts, 1), t_end_s=round(te, 1), axis=axis_note, f_top_hz=ftop, f_bottom_hz=0.0,
                                      frame_px=dict(row0=int(r0), row1=int(r1), col0=int(c0), col1=int(c1)),
                                      s_per_px=round((te - ts) / nt, 4), hz_per_px=round(ftop / nf, 4),
                                      reading_uncertainty=dict(time_s=round((te - ts) / nt, 2), freq_hz=round(ftop / nf, 2), db=1.5)))
            # overlay
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True, gridspec_kw=dict(height_ratios=[3, 1.3]))
            ax1.imshow(crop, extent=[ts, te, 0, ftop], aspect="auto")
            step = 10 if te - ts <= 200 else (300 if te - ts <= 1800 else 300)
            for tk in np.arange(np.ceil(ts / step) * step, te + 1e-6, step):
                ax1.axvline(tk, color="w", lw=0.5, alpha=0.6)
            ax1.set_ylabel("Frequency (Hz)"); ax1.set_title(f"Royer (2016) {fid} {stn} {t0}-{t1} UTC: calibrated frame (white = tick grid)", fontsize=9)
            ax2.plot(t, band(5, 40), lw=0.6, label="5-40 Hz mean"); ax2.plot(t, band(10, 15), lw=0.6, label="10-15 Hz mean")
            ax2.set_ylabel("dB re 1 µPa²/Hz"); ax2.legend(fontsize=7, loc="upper right")
            ticks = np.arange(np.ceil(ts / step) * step, te + 1e-6, step)
            ax2.set_xticks(ticks); ax2.set_xticklabels([f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d}" for x in ticks], rotation=45, fontsize=7)
            ax2.set_xlabel("UTC, 8 Mar 2014")
            fig.text(0.01, 0.005, "DIGITISED from the embedded raster; colour->dB by nearest 'jet' colour over the printed 70-100 dB bar (±1.5 dB); frame edges ±1 px.", fontsize=7)
            fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(os.path.join(out, "overlays", pid + ".png"), dpi=110); plt.close(fig)
        json.dump(cal, open(os.path.join(out, "figures", f"{fid}_calibration.json"), "w"), indent=1)
        calib_all[fid] = cal
    # figure marks (arrows, pick bars) against the nearest Table 5 pick of the same station
    stmap = {"H01W-2": ["H01W1", "H01W2", "H01W3"], "SWAMS-3": ["SWAMS3"], "SWAMS-2": ["SWAMS2"], "SSEIR": ["SSEIR"], "MAD": ["MAD"], "WKER": ["WKER"], "NCRO": ["NCRO"]}
    for m in marks:
        sub = ar[ar.station.isin(stmap[m["station"]]) & ar.arrival_utc.notna()]
        if len(sub):
            k = (sub.arrival_s_after_T0 - m["t_utc_s"]).abs().idxmin()
            m["nearest_table5_index"] = int(ar.loc[k, "index"]); m["nearest_table5_label"] = ar.loc[k, "label"]
            m["nearest_table5_arrival_utc"] = ar.loc[k, "arrival_utc"]
            m["mark_minus_table5_s"] = round(m["t_utc_s"] - ar.loc[k, "arrival_s_after_T0"], 1)
    pd.DataFrame(marks).to_csv(os.path.join(out, "royer_figure_marks.csv"), index=False)
    json.dump(dict(script="prepare/digitise_royer_2016.py", pdf_sha256=sha, method=__doc__), open(os.path.join(out, "METHOD.json"), "w"), indent=1)
    print(json.dumps(dict(n_stations=len(st), n_events=len(ev), n_arrivals=int(ar.arrival_utc.notna().sum()),
                          speed_median=float(ar.implied_speed_km_s.median()), speed_min=float(ar.implied_speed_km_s.min()), speed_max=float(ar.implied_speed_km_s.max()),
                          panels={k: len(v["panels"]) for k, v in calib_all.items()})))


if __name__ == "__main__":
    main()
