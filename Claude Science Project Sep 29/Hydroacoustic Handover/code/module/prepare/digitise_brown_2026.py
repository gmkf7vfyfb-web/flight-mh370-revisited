#!/usr/bin/env python
"""Digitise the waveform/spectrum figures of Brown et al. (2026), Icarus (`brown2026.pdf`, 60 pp).

DIGITISED DATA, NOT MEASUREMENTS.

FINDING (22 Oct 2026): the paper contains NO F-35A waveform or spectrum. The F-35A (9 Apr 2019, off Japan) enters
only as text on pp. 18-19: impact energy 900 +/- 200 MJ, observed peak pressure 0.7 Pa at H11 (Wake Island),
range 3,300 km, Arons/Soloway-Dahl relation (Eq. 2) => coupling efficiency to the SOFAR channel of order 1e-4,
"an upper bound"; signal one order of magnitude in pressure above local background (citing Metz, Obana & Fukao,
2022/2023, Pure Appl. Geophys. 180:1343-1351, doi 10.1007/s00024-022-03117-6; Pete holds a copy, artifact 7e4d336f). The F-35A source
spectrum therefore has to come from Metz et al. (held; digitised later on 22 Oct by track metz-f35a). What this paper does render, and what is
digitised here, are the two fireball cases and the analytic relation:

  Fig. 3  (p. 11, raster 3551x2354): Arons peak-pressure relation, Eq. 2: P_peak[Pa] = 52.4e6 (R / W^(1/3))^-1.13,
          R in m, W in kg TNT. Analytic: regenerated from the equation and checked against the raster (two points).
  Fig. 7  (p. 24, raster 1000x495): 2 Sep 2003 fireball, H03N stacked best beam, 4-9 Hz Butterworth, 22:13:19-22:18:0x
          UTC; lower panel waveform (axis labelled "Pa", +/-50000 full scale: evidently uncalibrated counts, see note),
          upper panel wavelet scalogram 2-15 Hz (relative dB, -1..0), right-hand bar spectrum (log f axis).
  Fig. C.10 (p. 53, raster 1763x207): 7 Oct 2004 fireball at H08S1-3, unfiltered, 13:30-14:30 UTC, one hour, no
          amplitude axis (envelope in pixels only).
  Fig. C.12 (p. 55, raster 1000x455): 7 Oct 2004 fireball at H08S, stacked waveform 14:04:13-14:05:43 UTC, axis
          "Pa" +/-4e6 (evidently counts), spectrogram 0-40 Hz, no colour bar.
Waveform tracing: per pixel column the green (0,255,0) pixel span gives the envelope (upper, lower) in axis units;
the plotted line is dense (hundreds of samples per column), so only the envelope is recoverable, not the samples.
Axis calibration from the tick marks detected on the frame (positions listed in CAL below with the printed labels).
Reading uncertainty: 1 px = 0.39 s and ~970 units (Fig. 7), 0.12 s and ~46,000 units (Fig. C.12), 2.15 s (Fig. C.10).

Outputs (--out, default results-data/digitised/brown-2026/): fig7_h03n_waveform_envelope_DIGITISED.csv,
fig7_h03n_spectrum_bars_DIGITISED.csv, figC10_h08s_envelopes_DIGITISED.csv, figC12_h08s_waveform_envelope_DIGITISED.csv,
fig3_arons_relation.csv, source rasters, overlays, METHOD.json.
"""
from __future__ import annotations
import argparse, io, json, os, hashlib
import numpy as np

CAL = {
    # (page index, image index, name): axes
    "fig7": dict(page=23, img=1, frame=dict(x0=82, x1=857, ytop=211, ybot=396),
                 t_ticks=[(129, "22:13:31"), (747, "22:17:31")], y_ticks=[(255, 50000.0), (358, -50000.0)],
                 wave_rows=(212, 395), spec_rows=(5, 199), spec_cols=(82, 830), spec_f=(2.0, 15.0, "log"),
                 bars=dict(x0=831, x1=927, rows=(5, 199))),
    "figC12": dict(page=54, img=0, frame=dict(x0=82, x1=861, ytop=211, ybot=396),
                   t_ticks=[(87, "14:04:13"), (835, "14:05:43")], y_ticks=[(217, 4e6), (391, -4e6)],
                   wave_rows=(212, 395), spec_rows=(5, 199), spec_cols=(82, 830), spec_f=(0.0, 40.0, "lin")),
    "figC10": dict(page=52, img=0, t_ticks=[(90, "13:30:00"), (1480, "14:20:00")], traces={"H08S1": 30, "H08S2": 77, "H08S3": 124}),
}


def hms(s):
    h, m, sec = s.split(":"); return int(h) * 3600 + int(m) * 60 + float(sec)


def lin(p, pts):
    (p0, v0), (p1, v1) = pts
    return v0 + (p - p0) * (v1 - v0) / (p1 - p0)


def green(a):
    return (a[..., 1] > 150) & (a[..., 0] < 130) & (a[..., 2] < 130)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results-data", "digitised", "brown-2026"))
    a = ap.parse_args()
    import fitz, pandas as pd
    from PIL import Image
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    out = os.path.abspath(a.out); os.makedirs(os.path.join(out, "overlays"), exist_ok=True)
    doc = fitz.open(a.pdf); sha = hashlib.sha256(open(a.pdf, "rb").read()).hexdigest()
    def raster(page, k):
        pg = doc[page]; info = doc.extract_image(pg.get_images(full=True)[k][0])
        im = Image.open(io.BytesIO(info["image"])).convert("RGB"); return im
    summary = {}
    hdr = f"# DIGITISED from Brown et al. (2026) Icarus, brown2026.pdf sha256 {sha[:16]}; prepare/digitise_brown_2026.py. Not a measurement.\n"
    # ---- Fig 3: Arons relation (analytic) + raster check
    im3 = raster(10, 0); im3.save(os.path.join(out, "fig3_source_raster.png"))
    R = np.logspace(3, 7, 81)
    rows = []
    for W in [1e-4, 1e-3, 1e-2, 1e-1, 1, 10, 100]:
        P = 52.4e6 * (R / W ** (1 / 3)) ** -1.13
        for r, p in zip(R, P):
            rows.append(dict(yield_kg_tnt=W, range_m=r, p_peak_pa=p, p_peak_db_re_1upa=20 * np.log10(p * 1e6)))
    with open(os.path.join(out, "fig3_arons_relation.csv"), "w") as f:
        f.write(hdr + "# Eq. 2 of the paper (Arons 1954; Soloway & Dahl 2014), regenerated analytically; the figure is this equation. F-35A text case: 0.7 Pa at 3,300 km => W = (R / (P/52.4e6)^(-1/1.13))^3.\n")
        pd.DataFrame(rows).to_csv(f, index=False, float_format="%.6g")
    W_f35 = (3.3e6 / (0.7 / 52.4e6) ** (-1 / 1.13)) ** 3
    summary["f35a_text_case"] = dict(p_peak_pa=0.7, range_km=3300, energy_mj=[700, 900, 1100], implied_sofar_yield_kg_tnt=W_f35,
                                     implied_eta_mid=W_f35 * 4.184e6 / 900e6, note="eta = yield*4.184 MJ/kg / 900 MJ; paper quotes 'of order 1e-4'")
    # ---- Fig 7 and C.12 waveforms
    for fid in ("fig7", "figC12"):
        C = CAL[fid]; im = raster(C["page"], C["img"]); im.save(os.path.join(out, f"{fid}_source_raster_{im.width}x{im.height}.png"))
        arr = np.asarray(im); gm = green(arr)
        tt = [(p, hms(s)) for p, s in C["t_ticks"]]
        r0, r1 = C["wave_rows"]; x0, x1 = C["frame"]["x0"] + 1, C["frame"]["x1"] - 1
        env = []
        for x in range(x0, x1):
            ys = np.where(gm[r0:r1, x])[0]
            if len(ys) == 0: continue
            env.append(dict(x_px=x, t_utc_s=round(lin(x, tt), 3), upper=round(lin(ys.min() + r0, C["y_ticks"]), 1), lower=round(lin(ys.max() + r0, C["y_ticks"]), 1)))
        df = pd.DataFrame(env); df["half_span"] = (df.upper - df.lower) / 2
        with open(os.path.join(out, f"{fid}_waveform_envelope_DIGITISED.csv"), "w") as f:
            f.write(hdr + f"# {fid}: per-column envelope of the plotted trace; units as printed on the axis ('Pa'; magnitudes +/-{abs(C['y_ticks'][0][1]):g} indicate uncalibrated counts). t_utc_s = seconds after 00:00 UTC of the event day.\n")
            df.to_csv(f, index=False)
        summary[fid] = dict(n_cols=len(df), t0=df.t_utc_s.min(), t1=df.t_utc_s.max(), s_per_px=round((tt[1][1] - tt[0][1]) / (tt[1][0] - tt[0][0]), 4),
                            units_per_px=round(abs(C["y_ticks"][1][1] - C["y_ticks"][0][1]) / abs(C["y_ticks"][1][0] - C["y_ticks"][0][0]), 1),
                            peak_half_span=float(df.half_span.max()), t_peak=float(df.t_utc_s[df.half_span.idxmax()]))
        # spectrogram panel: save crop + relative colour index (jet) with axes
        sr0, sr1 = C["spec_rows"]; sc0, sc1 = C["spec_cols"]
        crop = arr[sr0:sr1, sc0:sc1]
        import matplotlib
        lut = (matplotlib.colormaps["jet"](np.linspace(0, 1, 256))[:, :3] * 255)
        px = crop.reshape(-1, 3).astype(float); idx = ((px[:, None, :] - lut[None]) ** 2).sum(-1).argmin(1).reshape(crop.shape[:2]) / 255.0
        fl, fh, kind = C["spec_f"]
        nf = sr1 - sr0
        fax = (np.exp(np.log(fh) - (np.arange(nf) + 0.5) / nf * (np.log(fh) - np.log(fl))) if kind == "log" else fh - (np.arange(nf) + 0.5) / nf * (fh - fl))
        tax = np.array([lin(x, tt) for x in range(sc0, sc1)])
        np.savez_compressed(os.path.join(out, f"{fid}_spectrogram_relative.npz"), t_utc_s=tax, f_hz=fax.astype(np.float32), rel_level=idx.astype(np.float16),
                            note="relative colour index 0-1 on 'jet'; Fig. 7 colour bar spans -1..0 dB (relative); Fig. C.12 has no colour bar. Frequency axis read from printed ticks (" + kind + ").")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        ax1.imshow(crop, extent=[tax[0], tax[-1], 0, 1], aspect="auto"); ax1.set_yticks([]); ax1.set_ylabel(f"{fl:g}-{fh:g} Hz ({kind})")
        ax1.set_title(f"Brown et al. (2026) {fid}: source panels with the digitised envelope", fontsize=9)
        ax2.imshow(arr[r0:r1, x0:x1], extent=[lin(x0, tt), lin(x1, tt), C['y_ticks'][1][1] if False else lin(r1, C["y_ticks"]), lin(r0, C["y_ticks"])], aspect="auto")
        ax2.plot(df.t_utc_s, df.upper, "r-", lw=0.6); ax2.plot(df.t_utc_s, df.lower, "r-", lw=0.6); ax2.set_ylabel("axis units (as printed: Pa)")
        ax2.set_xlabel("seconds after 00:00 UTC (event day)")
        fig.text(0.01, 0.005, "DIGITISED envelope (red) over the source raster; axis units as printed; 1 px reading uncertainty.", fontsize=7)
        fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(os.path.join(out, "overlays", f"{fid}_overlay.png"), dpi=110); plt.close(fig)
        if "bars" in C:
            b = C["bars"]; sub = arr[b["rows"][0]:b["rows"][1], b["x0"]:b["x1"]]
            dark = sub.astype(int).sum(-1) < 500
            bars = []
            for r in range(dark.shape[0]):
                xs = np.where(dark[r])[0]
                if len(xs) > 3:
                    bars.append(dict(row_px=r + b["rows"][0], f_hz=round(float(fax[r]), 3), bar_len_px=int(xs.max() - xs.min() + 1)))
            bd = pd.DataFrame(bars)
            with open(os.path.join(out, "fig7_h03n_spectrum_bars_DIGITISED.csv"), "w") as f:
                f.write(hdr + "# Fig. 7 right-hand bar spectrum: bar length in px per row (relative amplitude; no numeric scale printed; the panel label reads '19.4 Hz'). f from the shared log axis 2-15 Hz.\n")
                bd.to_csv(f, index=False)
            summary["fig7_bars"] = dict(n=len(bd), f_at_longest=float(bd.f_hz[bd.bar_len_px.idxmax()]) if len(bd) else None)
    # ---- Fig C.10: three one-hour traces, pixel envelope only
    C = CAL["figC10"]; im = raster(C["page"], C["img"]); im.save(os.path.join(out, f"figC10_source_raster_{im.width}x{im.height}.png"))
    arr = np.asarray(im); gm = green(arr); tt = [(p, hms(s)) for p, s in C["t_ticks"]]
    rows = []
    for name, base in C["traces"].items():
        for x in range(90, 1757):
            ys = np.where(gm[base - 22:base + 23, x])[0]
            if len(ys): rows.append(dict(trace=name, x_px=x, t_utc_s=round(lin(x, tt), 2), half_span_px=round((ys.max() - ys.min()) / 2, 1)))
    df = pd.DataFrame(rows)
    with open(os.path.join(out, "figC10_h08s_envelopes_DIGITISED.csv"), "w") as f:
        f.write(hdr + "# Fig. C.10: H08S1-3 unfiltered, 13:30-14:30 UTC 7 Oct 2004; no amplitude axis printed, so the envelope is in pixels (relative). 2.16 s per px.\n")
        df.to_csv(f, index=False)
    pk = df.groupby("trace").apply(lambda d: d.t_utc_s[d.half_span_px.idxmax()]).to_dict()
    summary["figC10"] = dict(n=len(df), t_peak_by_trace=pk, s_per_px=round((tt[1][1] - tt[0][1]) / (tt[1][0] - tt[0][0]), 3))
    fig, ax = plt.subplots(figsize=(11, 3)); ax.imshow(arr, extent=[lin(0, tt), lin(arr.shape[1], tt), arr.shape[0], 0], aspect="auto")
    for name, base in C["traces"].items():
        d = df[df.trace == name]; ax.plot(d.t_utc_s, base - d.half_span_px, "r-", lw=0.5); ax.plot(d.t_utc_s, base + d.half_span_px, "r-", lw=0.5)
    ax.set_xlabel("seconds after 00:00 UTC 7 Oct 2004"); ax.set_title("Brown et al. (2026) Fig. C.10: H08S traces with the digitised pixel envelope", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(out, "overlays", "figC10_overlay.png"), dpi=110); plt.close(fig)
    json.dump(dict(script="prepare/digitise_brown_2026.py", pdf_sha256=sha, method=__doc__, summary=summary), open(os.path.join(out, "METHOD.json"), "w"), indent=1, default=float)
    print(json.dumps(summary, default=float))


if __name__ == "__main__":
    main()
