#!/usr/bin/env python
"""Digitise every separable curve of Blackman et al. (2004) UCRL-TR-207323 Fig. 23 (p. 21), plus Appendix A Table I.

DIGITISED DATA, NOT MEASUREMENTS.

Source resolution (checked 22 Oct 2026): the only public copies are OSTI purl 15011808 (byte-identical to the repo
copy `ISO Sept 28 Status/inputs/papers/hydroacoustics/ucrl-tr-207323.pdf`, sha256 34a735f7...), whose Fig. 23 is an
embedded 351 x 458 px raster drawn at 153 dpi, and OSTI purl 850576, a bilevel 200-dpi page scan in which Fig. 23
occupies about 190 x 270 px. Rendering the page at 600 dpi only upsamples the 351 x 458 raster. The limit is the
source: 2.875 px/Hz and 3.6 px/dB, i.e. one pixel is 0.35 Hz and 0.28 dB, but anti-aliased lines are 2-3 px wide and
the curves cross each other, so the reading uncertainty is set by line separation, not by pixel size.

Curves and legend swatches (grey level 0-255 at the swatch core, line weight):
  DGN (= H08N): air1 thin black (111, 1 px); air2 thick dark grey (153, 2 px core); air3 dotted (210/227, 46 % duty);
                air4 thick light grey (201, 3 px); air5 thin light grey (215, 2 px).
  DGS (= H08S): air7 thick light grey (201/215); air8 dotted (210/227); air9 thin black (163/210).
  CL  (= H01W): air7 light grey (201/215); air9 thin black (163/210).
Separability: air1 vs air2 (111 vs 153) and black vs light grey are separable where they do not cross; air4 vs air5
(201 vs 215) differ by one grey step and are separable only by line weight; dotted curves (air3, air8) are
separable by their duty cycle. Where two candidate clusters fall in the same grey window within the continuity
jump, the column is flagged `ambiguous=1` and the value is still recorded (nearest to the previous pick).

Method per curve: in each pixel column inside the panel frame (legend box and panel label masked) the dark clusters
are found; a cluster matches the curve if its minimum grey is within the curve's window and its thickness is within
the curve's weight band; the match nearest the previous pick (max jump 30 px) is taken. Dotted curves accept gaps.
Calibration as in digitise_blackman_fig23.py: 150 dB at the top tick row, 3.6 px/dB; 0 Hz at x = 51.5 px, 2.875 px/Hz
(tick-label centres). Reading uncertainty: +/-1 dB where a curve is isolated, +/-2 dB where curves of similar grey
run within 2 dB of each other (flagged), and the frequency axis +/-0.5 Hz.

Separability findings (22 Oct 2026 run): air1, air2 (where thick), air9, air7 (DGS, CL) trace cleanly. air3 (dotted) is
visible only at 5-18 Hz (its 140 dB peak at 14 Hz); elsewhere the dotted curve is hidden under solid ones and is NOT
SEPARABLE. air8 (DGS, dotted) lies on top of the thick light-grey air7 almost everywhere and is NOT SEPARABLE (one
isolated column survives). air4 and air5 (both light grey, 201 vs 215) differ by one grey step: the thick curve at
60-80 Hz (to 147 dB) is air4 by weight; below 20 Hz the single light-grey curve at 120-130 dB is assigned to both by
the tracer, but the report text says air4 is close to air1-air3 (130-135 dB) in the 5-8 Hz band, so that low curve
is air5 and the air4 points below 20 Hz are WEIGHT-AMBIGUOUS (see the SEPARABILITY column written into each CSV header).

Outputs (--out, default results-data/digitised/blackman-2004/): fig23_<panel>_<site>_DIGITISED.csv
(f_hz, tl_db, x_px, grey_min, thickness_px, ambiguous), one overlay PNG per curve, fig23_source_raster_351x458.png,
table1_shot_lines.csv (Appendix A Table I from the text layer), METHOD.json.
"""
from __future__ import annotations
import argparse, io, json, os, re, hashlib
import numpy as np

PANELS = {"DGN": dict(y0=10, y1=134, ytop=10.0, legend=(76, 133, 215, 340), label=(10, 34, 52, 118), station="H08N"),
          "DGS": dict(y0=149, y1=274, ytop=148.5, legend=(227, 263, 215, 340), label=(149, 173, 52, 118), station="H08S"),
          "CL": dict(y0=289, y1=414, ytop=288.5, legend=(378, 403, 215, 340), label=(289, 313, 52, 118), station="H01W")}
# grey window (lo, hi) on the cluster minimum, thickness band (min, max px), dotted flag
CURVES = {
    ("DGN", "air1"): dict(grey=(60, 135), thick=(1, 3), dotted=False),
    ("DGN", "air2"): dict(grey=(136, 180), thick=(2, 5), dotted=False),
    ("DGN", "air3"): dict(grey=(195, 232), thick=(1, 3), dotted=True),
    ("DGN", "air4"): dict(grey=(190, 212), thick=(3, 6), dotted=False),
    ("DGN", "air5"): dict(grey=(205, 232), thick=(1, 2), dotted=False, max_core=2),
    ("DGS", "air7"): dict(grey=(190, 222), thick=(2, 5), dotted=False),
    ("DGS", "air8"): dict(grey=(195, 232), thick=(1, 3), dotted=True),
    ("DGS", "air9"): dict(grey=(60, 185), thick=(1, 4), dotted=False),
    ("CL", "air7"): dict(grey=(190, 222), thick=(2, 5), dotted=False),
    ("CL", "air9"): dict(grey=(60, 185), thick=(1, 4), dotted=False),
}
X0, PX_PER_HZ, PX_PER_DB, JUMP = 51.5, 2.875, 3.6, 30
SEP = {("DGN", "air3"): "dotted curve visible only 5-18 Hz; elsewhere hidden under solid curves, NOT SEPARABLE",
       ("DGS", "air8"): "dotted curve lies on the thick light-grey air7 almost everywhere; NOT SEPARABLE (isolated columns only)",
       ("DGN", "air4"): "light grey, separable from air5 only by line weight; points below 20 Hz are WEIGHT-AMBIGUOUS (report text puts air4 at 130-135 dB in 5-8 Hz, i.e. with air1-air3, so the 120-130 dB curve there is air5)",
       ("DGN", "air5"): "thin light grey, separable from air4 only by line weight; points above 40 Hz coincide with the thick air4 curve and are WEIGHT-AMBIGUOUS",
       ("DGN", "air2"): "thick dark grey; separable from air1 only where the two diverge (sparse: ~20 columns)",
       ("DGS", "air9"): "thin black; 20 % of columns flagged where air7/air8 cross within 4 dB"}
XMIN, XMAX = 54, 337


def clusters(ys):
    out, s, p = [], ys[0], ys[0]
    for v in ys[1:]:
        if v > p + 1:
            out.append((s, p)); s = v
        p = v
    out.append((s, p))
    return out


def solid_run(sub, x, yc, lo_y, hi_y, tol=3, maxn=8):
    """Columns over which a line can be followed continuously from (x, yc): step one column at a time, each step
    allowed to move the row by up to `tol` px (the curves are steep in places); counts left+right, up to maxn each."""
    n = 0
    for d in (1, -1):
        xx, yy = x + d, int(round(yc))
        while 0 <= xx < sub.shape[1] and abs(xx - x) <= maxn:
            r0, r1 = max(lo_y, yy - tol), min(hi_y, yy + tol + 1)
            seg = sub[r0:r1, xx]
            if (seg < 235).any():
                yy = r0 + int(np.argmin(seg)); n += 1; xx += d
            else:
                break
    return n


def trace(g, P, C):
    sub = g.copy()
    for (a, b, c, d) in (P["legend"], P["label"]):
        sub[a:b, c:d] = 255
    pts, prev, gap = [], None, 0
    for x in range(XMIN, XMAX):
        col = sub[P["y0"] + 2:P["y1"] - 1, x]
        ys = np.where(col < 235)[0] + P["y0"] + 2
        if len(ys) == 0:
            gap += 1; continue
        cands = []
        for s, e in clusters(ys):
            seg = sub[s:e + 1, x]
            gmin = int(seg.min()); th = e - s + 1
            if C["grey"][0] <= gmin <= C["grey"][1] and C["thick"][0] <= th <= C["thick"][1]:
                yc = s + float(np.argmin(seg))  # darkest row = line core
                run = solid_run(sub, x, yc, P["y0"] + 2, P["y1"] - 1)
                if C["dotted"] and run > 6:
                    continue          # a continuous line: not the dotted curve
                if not C["dotted"] and run < 8:
                    continue          # an isolated dot: not a solid curve
                if "max_core" in C and int((seg <= gmin + 10).sum()) > C["max_core"]:
                    continue          # thin curve: core (near-minimum grey) must be <= max_core px
                cands.append((yc, gmin, th))
        if prev is not None:
            cands = [c for c in cands if abs(c[0] - prev) <= JUMP + (gap * 4 if C["dotted"] else 0)]
        if not cands:
            gap += 1
            if prev is not None and gap > (12 if C["dotted"] else 6):
                prev = None  # lost the curve: allow re-acquisition
            continue
        cands.sort(key=lambda c: abs(c[0] - prev) if prev is not None else 0)
        yc, gmin, th = cands[0]
        amb = int(len(cands) > 1 and abs(cands[1][0] - yc) < 2 * PX_PER_DB * 2)
        prev, gap = yc, 0
        pts.append(dict(x_px=x, f_hz=round((x - X0) / PX_PER_HZ, 3), tl_db=round(150 - (yc - P["ytop"]) / PX_PER_DB, 3),
                        grey_min=gmin, thickness_px=th, ambiguous=amb))
    return pts


def parse_table1(doc):
    txt = "\n".join(doc[i].get_text() for i in range(len(doc)) if "Airgun array shot lines" in doc[i].get_text())
    rows = []
    pat = re.compile(r"(\d{3})[: ]+(\d\d:\d\d)\s+(\d+)[°]?\s*(\d+\.\d)'?\s+(\d+)[°]?\s*(\d+\.\d)'?\s*\n(\d{4})")
    for m in pat.finditer(txt):
        jd, hm, latd, latm, lond, lonm, depth = m.groups()
        rows.append(dict(jd_2001=int(jd), hhmm_utc=hm, lat_deg=-(int(latd) + float(latm) / 60), lon_deg=int(lond) + float(lonm) / 60, seafloor_m=int(depth)))
    # site/interval/shot# assignments, in order of the 13 line segments (start/end pairs)
    meta = [("air1", 97, "1-9"), ("air1", 173, "11-14"), ("air2", 127, "22-35"), ("air3", 173, "36-46"), ("air4", 57, "49-59"),
            ("air4", 173, "61-68"), ("air5", 127, "69-83"), ("air6", 173, "86-96"), ("air7", 127, "99-114"), ("air7", 57, "115-128"),
            ("air8", 173, "129-139"), ("air8", 57, "140-146"), ("air9", 57, "147-170"), ("air9", 127, "171-178")]
    assert len(rows) == 28, len(rows)
    out = []
    for k in range(14):
        a, b = rows[2 * k], rows[2 * k + 1]
        site, interval, shots = meta[k]
        out.append(dict(site=site, shot_numbers=shots, interval_s=interval, jd_2001=a["jd_2001"], start_hhmm_utc=a["hhmm_utc"], end_hhmm_utc=b["hhmm_utc"],
                        start_lat_deg=round(a["lat_deg"], 4), start_lon_deg=round(a["lon_deg"], 4), end_lat_deg=round(b["lat_deg"], 4), end_lon_deg=round(b["lon_deg"], 4),
                        start_seafloor_m=a["seafloor_m"], end_seafloor_m=b["seafloor_m"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results-data", "digitised", "blackman-2004"))
    a = ap.parse_args()
    import fitz, pandas as pd
    from PIL import Image
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    out = os.path.abspath(a.out); os.makedirs(os.path.join(out, "overlays"), exist_ok=True)
    doc = fitz.open(a.pdf); sha = hashlib.sha256(open(a.pdf, "rb").read()).hexdigest()
    pg = doc[22]
    im = None
    for ref in pg.get_images(full=True):
        info = doc.extract_image(ref[0])
        if (info["width"], info["height"]) == (351, 458):
            im = Image.open(io.BytesIO(info["image"])).convert("L")
    assert im is not None, "Fig. 23 raster (351x458) not found on p. 23"
    im.save(os.path.join(out, "fig23_source_raster_351x458.png"))
    pg.get_pixmap(dpi=600, clip=fitz.Rect(85, 486, 251, 702)).save(os.path.join(out, "fig23_page_render_600dpi.png"))
    g = np.array(im).astype(int)
    summary = {}
    for (panel, site), C in CURVES.items():
        P = PANELS[panel]
        pts = trace(g, P, C)
        df = pd.DataFrame(pts)
        fn = os.path.join(out, f"fig23_{panel}_{site}_DIGITISED.csv")
        with open(fn, "w") as f:
            f.write(f"# DIGITISED from Blackman et al. (2004) UCRL-TR-207323 Fig. 23 (observed TL, median over shots, plotted only where SNR > 3 dB), panel {panel} (= {P['station']}), curve {site}.\n"
                    f"# Source raster 351x458 px (153 dpi; the public PDFs hold nothing finer), pdf sha256 {sha[:16]}. Script prepare/digitise_blackman_fig23_all.py.\n"
                    f"# Grey window {C['grey']}, thickness {C['thick']} px, dotted={C['dotted']}; ambiguous=1 where another cluster of the same grey lies within 4 dB. Reading +/-1 dB (isolated) to +/-2 dB (flagged), +/-0.5 Hz. Not a measurement.\n"
                    f"# SEPARABILITY: {SEP.get((panel, site), 'clean trace')}\n")
            df.to_csv(f, index=False)
        summary[f"{panel}_{site}"] = dict(n=len(df), f_min=float(df.f_hz.min()) if len(df) else None, f_max=float(df.f_hz.max()) if len(df) else None,
                                          ambiguous_frac=round(float(df.ambiguous.mean()), 3) if len(df) else None)
        fig, ax = plt.subplots(figsize=(7, 3.2))
        ax.imshow(g[P["y0"]:P["y1"], :], cmap="gray", vmin=0, vmax=255, extent=[(0 - X0) / PX_PER_HZ, (351 - X0) / PX_PER_HZ, 150 - (P["y1"] - P["ytop"]) / PX_PER_DB, 150 - (P["y0"] - P["ytop"]) / PX_PER_DB], aspect="auto")
        if len(df):
            ok = df.ambiguous == 0
            ax.plot(df.f_hz[ok], df.tl_db[ok], ".", ms=2.5, color="red", label=f"{site} trace")
            ax.plot(df.f_hz[~ok], df.tl_db[~ok], "x", ms=3, color="orange", label="ambiguous column")
        ax.set_xlim(0, 100); ax.set_ylim(118, 151); ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Transmission loss (dB)")
        ax.set_title(f"Blackman et al. (2004) Fig. 23 panel {panel} ({P['station']}): digitised {site} over the source raster", fontsize=9)
        ax.legend(fontsize=7, loc="lower right")
        fig.text(0.01, 0.01, "DIGITISED; source raster 351x458 px; red = traced curve, orange = another curve of the same grey within 4 dB.", fontsize=7)
        fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(os.path.join(out, "overlays", f"fig23_{panel}_{site}_overlay.png"), dpi=150); plt.close(fig)
    t1 = parse_table1(doc)
    pd.DataFrame(t1).to_csv(os.path.join(out, "table1_shot_lines.csv"), index=False)
    json.dump(dict(script="prepare/digitise_blackman_fig23_all.py", pdf_sha256=sha, method=__doc__, summary=summary), open(os.path.join(out, "METHOD.json"), "w"), indent=1)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
