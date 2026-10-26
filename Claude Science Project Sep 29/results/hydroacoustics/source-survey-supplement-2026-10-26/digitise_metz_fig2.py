"""Independent re-digitisation of Metz, Obana & Fukao (2023) Fig. 2 (near-field F-35A records, 9 April 2019).
E-H: 1-s RMS envelopes (4-40 Hz), PDF vector polylines; axes from the vector frame and tick strokes.
A-D: spectrograms (1-40 Hz band-pass PSD, colour 90-110 dB re 1 uPa^2/Hz), embedded raster (xref 42, 1652 x 251 px)
inverted through the colour bar sampled from the same raster.
Output: out/metz-fig2-digitised-<station>.csv (envelope, 0.02 s grid as in Metz' 98 % overlap of 1-s windows),
        out/metz-fig2-spectrogram-<station>.npz, out/digitise_fig2_checks.json.
Usage: python digitise_metz_fig2.py <metz_pdf> <out_dir>
"""
import sys, json, io, pathlib
import numpy as np, pandas as pd, fitz
from PIL import Image

pdf, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
doc = fitz.open(pdf); pg = doc[3]; dr = pg.get_drawings()
STA = ["DSOH", "KSP1", "KSP2", "KSP3"]
TICK0 = {"DSOH": "10:28:25", "KSP1": "10:28:30", "KSP2": "10:29:15", "KSP3": "10:29:20"}   # first labelled tick (render)
hms = lambda s: sum(float(v) * m for v, m in zip(s.split(":"), (3600, 60, 1)))
utc = lambda x: f"{int(x//3600):02d}:{int(x%3600//60):02d}:{x%60:06.3f}"
chk = {"pdf_page_index": 3}

# ---------------- E-H vectors
frames = []
for d in dr:
    for it in d["items"]:
        if it[0] == "re" and it[1].width > 70 and 500 < it[1].y0 < 520:
            frames.append(it[1])
frames = sorted(frames, key=lambda r: r.x0); assert len(frames) == 4, frames
segs = [(it[1], it[2], d.get("width")) for d in dr for it in d["items"] if it[0] == "l"]
curves = [d for d in dr if len(d["items"]) > 300 and d.get("color") and d["rect"].y0 > 500 and d["rect"].y1 < 570]
curves = sorted(curves, key=lambda d: d["rect"].x0); assert len(curves) == 4
for st, fr, cv in zip(STA, frames, curves):
    xt = sorted({round(a.x, 3) for a, b, w in segs if w and abs(a.x - b.x) < 1e-3 and abs(a.y - fr.y1) < 0.05 and fr.x0 + 1 < a.x < fr.x1 - 1})
    yt = sorted({round(a.y, 3) for a, b, w in segs if w and abs(a.y - b.y) < 1e-3 and abs(a.x - fr.x0) < 0.05 and abs(b.x - a.x) < 5 and fr.y0 + 1 < a.y < fr.y1 - 1})
    sp = np.diff(xt); spp = 10.0 / sp.mean()                      # s per pt (ticks 10 s apart)
    t_of = lambda x: hms(TICK0[st]) + (x - xt[0]) * spp
    # y: frame bottom 90 dB, top 130 dB; ticks every 10 dB in between
    db_of = lambda y: 90.0 + (fr.y1 - y) / (fr.y1 - fr.y0) * 40.0
    P = []
    for it in cv["items"]:
        if it[0] == "l":
            P += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == "c":
            p0, c1, c2, p3 = it[1:5]
            for u in np.linspace(0, 1, 9):
                b = [(1-u)**3, 3*u*(1-u)**2, 3*u**2*(1-u), u**3]
                P.append((b[0]*p0.x+b[1]*c1.x+b[2]*c2.x+b[3]*p3.x, b[0]*p0.y+b[1]*c1.y+b[2]*c2.y+b[3]*p3.y))
    P = np.array(P); P = P[np.argsort(P[:, 0], kind="stable")]
    t = t_of(P[:, 0]); L = db_of(P[:, 1])
    tg = np.arange(np.ceil(t.min() / 0.02) * 0.02, t.max(), 0.02)
    _, iu = np.unique(t, return_index=True); Lg = np.interp(tg, t[iu], L[iu])
    pd.DataFrame(dict(station=st, utc_s_of_day=tg, utc=[utc(v) for v in tg], rms_db_re_1uPa=Lg,
                      label="DIGITISED Metz 2023 Fig. 2E-H (vector), 1-s RMS, 4-40 Hz")).to_csv(out / f"metz-fig2-digitised-{st}.csv", index=False)
    pd.DataFrame(dict(station=st, pdf_x_pt=P[:, 0], pdf_y_pt=P[:, 1], utc_s_of_day=t, rms_db_re_1uPa=L)).to_csv(out / f"vertices_{st}.csv", index=False)
    ytick_db = [db_of(y) for y in yt]
    chk[st] = dict(frame_pt=[fr.x0, fr.y0, fr.x1, fr.y1], x_ticks_pt=xt, x_tick_spacing_pt=list(map(float, sp)), s_per_pt=spp,
                   frame_span_s=(fr.x1 - fr.x0) * spp, frame_start_utc=utc(t_of(fr.x0)), y_ticks_pt=yt, y_ticks_db=ytick_db,
                   y_tick_residual_db=[v - round(v / 10) * 10 for v in ytick_db], n_vertices=int(len(P)),
                   curve_t_span=[utc(t.min()), utc(t.max())], peak_db=float(L.max()), peak_utc=utc(t[np.argmax(L)]))

# ---------------- A-D raster
xref = [i[0] for i in pg.get_images(full=True)][0]
im = np.array(Image.open(io.BytesIO(doc.extract_image(xref)["image"])).convert("RGB")).astype(float)
H, W, _ = im.shape; chk["raster"] = dict(xref=xref, shape=[H, W], rect_pt=list(pg.get_image_rects(xref)[0]))
dark = im.sum(2) < 200
# frame columns: columns that are dark over most of the height
colfrac = dark.mean(0); cols = np.where(colfrac > 0.8)[0]
groups = np.split(cols, np.where(np.diff(cols) > 2)[0] + 1); xs = [(g[0], g[-1]) for g in groups]
rowfrac = dark.mean(1); rows = np.where(rowfrac > 0.5)[0]; rg = np.split(rows, np.where(np.diff(rows) > 2)[0] + 1); ys = [(g[0], g[-1]) for g in rg]
chk["raster"]["frame_cols"] = [list(map(int, x)) for x in xs]; chk["raster"]["frame_rows"] = [list(map(int, y)) for y in ys]
y_in0, y_in1 = ys[0][1] + 1, ys[-1][0] - 1                      # inner rows (top = 40 Hz, bottom = 0 Hz)
pan = [(xs[2*i][1] + 1, xs[2*i+1][0] - 1) for i in range(4)]; cb = (xs[8][1] + 1, xs[9][0] - 1)
chk["raster"]["panels_inner_cols"] = [list(map(int, p)) for p in pan]; chk["raster"]["colourbar_inner_cols"] = list(map(int, cb))
n_in = y_in1 - y_in0 + 1; rr = np.arange(y_in0 + 2, y_in1 - 1)    # trim 2 rows each end (frame stroke bleeds in)
cbar = im[rr, cb[0] + 2:cb[1] - 1].mean(1)                       # rows top (110) -> bottom (90)
cdb = 110.0 - (rr - y_in0 + 0.5) / n_in * 20.0
chk["raster"]["colourbar_rgb_at"] = {f"{v:g}": cbar[np.argmin(abs(cdb - v))].round(0).tolist() for v in (110, 105, 100, 95, 91)}
for st, (x0, x1) in zip(STA, pan):
    sub = im[y_in0:y_in1 + 1, x0:x1 + 1]
    d2 = ((sub[:, :, None, :] - cbar[None, None, :, :]) ** 2).sum(-1)
    k = d2.argmin(2); dist = np.sqrt(d2.min(2))
    psd = cdb[k].astype(np.float32)
    white = sub.min(2) > 245
    bad = (dist > 30.0) & ~white                                    # frame strokes, tick marks, anti-aliased greys
    nf, nt = psd.shape
    lin = np.where(white, 10 ** 8.95, 10 ** (psd / 10.0))         # floor filled at 89.5 dB for the fill step only
    for r in range(nf):                                             # fill masked pixels along time in each row
        b = bad[r]
        if b.any() and (~b).sum() > 2:
            lin[r, b] = np.interp(np.where(b)[0], np.where(~b)[0], lin[r, ~b])
    psd = (10 * np.log10(lin)).astype(np.float32); white2 = psd < 90.0
    psd[white2] = np.nan
    freq = 40.0 * (1 - (np.arange(nf) + 0.5) / nf)                  # row centre -> Hz (top row ~40 Hz)
    fr = frames[STA.index(st)]; i = STA.index(st)
    # time: panel inner width = frame width of E-H counterpart (same 30 s window, same tick labels)
    t0 = hms(chk[st]["frame_start_utc"]); tt = t0 + (np.arange(nt) + 0.5) / nt * chk[st]["frame_span_s"]
    np.savez_compressed(out / f"metz-fig2-spectrogram-{st}.npz", psd_db_re_1uPa2_Hz=psd, freq_hz=freq, utc_s_of_day=tt,
                        colour_distance=dist.astype(np.float32), masked=bad, floor_db=90.0, saturation_db=110.0,
                        label="DIGITISED Metz 2023 Fig. 2A-D raster; NaN = white (<= 90 dB floor)")
    chk[st]["spectrogram"] = dict(n_freq=int(nf), n_time=int(nt), df_hz=40.0 / nf, dt_s=chk[st]["frame_span_s"] / nt,
                                  frac_white=float(white.mean()), frac_masked=float(bad.mean()), frac_saturated=float((psd >= 109.5).mean()),
                                  colour_dist_p95_unmasked=float(np.percentile(dist[~white & ~bad], 95)))
json.dump(chk, open(out / "digitise_fig2_checks.json", "w"), indent=1, default=float)
print(json.dumps({s: {k: chk[s][k] for k in ("frame_start_utc", "frame_span_s", "x_tick_spacing_pt", "y_ticks_db", "peak_db", "peak_utc", "n_vertices")} for s in STA}, indent=0, default=float))
print(json.dumps(chk["raster"], default=float)); print({s: chk[s]["spectrogram"] for s in STA})
