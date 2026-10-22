"""DIGITISATION of waveform rasters held by the module (gap G8, correction track 22 Oct 2026): ARA San Juan explosion and
calibration-charge traces (Kadri 2024 Figs 7-8; Nielsen et al. 2021 Fig. 3; Vergoz et al. 2021 Fig. 2), AF447 (Kadri 2024
Fig. 5a) and CMST 2014-30 Figs 1-2 (the 01:33:44 Perth Canyon logger signal and the HA01 spectrograms).

Everything written here is DIGITISED publication data, not a measurement. PMC copies of Kadri 2024 (669-799 px wide) are
the highest resolution the module holds (the publisher PDF, Drive id 1ZxR_3Y6Ryn-OXyRJ0tjOPSjassZn8ioW, 16.2 MB, is NOT
RETRIEVED - ask Pete: over the Drive connector's 10 MB limit, direct host not on the allowlist).

METHOD (fixed before tracing). Axis box: grey/black low-chroma lines spanning > 90 % of the panel (raster_trace.box_lines);
x calibration from the box edges = printed axis limits, checked against the inward tick marks (raster_trace.ticks_bottom);
y calibration from the box edges = printed limits where the extreme tick labels sit on the box (Kadri Figs 7-8, CMST
Fig. 1), else from the tick-mark rows (Kadri Fig. 7 H04S: ticks +/-5e6 uPa at 427/467.5 px) or from the module's interim
scale (Kadri Fig. 5a: 0.0247 Pa/px, results-data/calibration_events/kadri_peaks.csv). Where the y axis carries no pressure
scale (Nielsen Fig. 3 node offsets, Vergoz Fig. 2 strips) the amplitude is NORMALISED (1 = panel maximum) and only times
and shapes are used. Trace = pixels of the trace colour inside the box; per column the extreme rows give the upper and
lower envelope. Zero line = median of the column mid-points (the trace's own baseline). Noise = 99th percentile of
|envelope| outside the event window; onset = first column after which |envelope| stays > 2 x noise for >= 1 s; peak = max
|envelope|; SNR = peak / noise. Resolution = 1 px (reported per panel in units). Spectrogram panels (CMST Fig. 2): the
jet colour map is inverted to dB on the printed colour bar (-40..0 dB re panel maximum) and averaged over 5-40 Hz rows.
Usage: python digitise_waveform_rasters.py <kadri_pmc_dir> <ground_truth_fig_dir> <cmst_fig_dir> <out_dir>
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import raster_trace as R  # noqa: E402

def m_blue(s):   return (s[..., 2] > 150) & (s[..., 0] < 120) & (s[..., 2] - s[..., 0] > 60)
def m_orange(s): return (s[..., 0] > 180) & (s[..., 2] < 110) & (s[..., 0] - s[..., 2] > 100)
def m_black(s):  return s.max(-1) < 110
def m_yellow(s): return (s[..., 0] > 150) & (s[..., 1] > 150) & (s[..., 2] < 140)
def m_cmst(s):   return (s[..., 2] > 180) & (s[..., 0] < 90) & (s[..., 1] < 90)
MASKS = dict(blue=m_blue, orange=m_orange, black=m_black, yellow=m_yellow, cmst=m_cmst)

# name, image, box (l, t, r, b) px, x-limits (s), t0 UTC, y-limits (Pa) or None, mask, event window (s) for noise exclusion
PANELS = [
 ("kadri2024_fig8_grenade_H03S", "K/41598_2024_60529_Fig8_HTML.jpg", (70, 159, 660, 209.5), (0, 300), "2017-12-01T20:14:00Z", (20, -20), "blue", (90, 240)),
 ("kadri2024_fig8_grenade_H04S", "K/41598_2024_60529_Fig8_HTML.jpg", (70, 428.5, 660, 477.5), (0, 300), "2017-12-01T21:31:00Z", (2, -2), "blue", (90, 180)),
 ("kadri2024_fig8_grenade_H10N", "K/41598_2024_60529_Fig8_HTML.jpg", (70, 694.5, 660, 744.5), (0, 300), "2017-12-01T21:10:00Z", (4, -4), "blue", (110, 230)),
 ("kadri2024_fig7_sanjuan_H03S", "K/41598_2024_60529_Fig7_HTML.jpg", (63.5, 155.5, 649, 205.5), (0, 300), "2017-11-15T14:01:00Z", (1, -1), "blue", (85, 160)),
 ("kadri2024_fig7_sanjuan_H04S", "K/41598_2024_60529_Fig7_HTML.jpg", (63.5, 422.5, 649.5, 471.5), (0, 300), "2017-11-15T15:17:00Z", (5 * 24.5 / 20.25, -5 * 24.5 / 20.25), "blue", (140, 200)),
 ("kadri2024_fig7_sanjuan_H10N", "K/41598_2024_60529_Fig7_HTML.jpg", (63.5, 686.5, 649, 735.5), (0, 300), "2017-11-15T14:57:00Z", (10, -10), "blue", (125, 290)),
 ("kadri2024_fig5a_af447_H10S", "K/41598_2024_60529_Fig5_HTML.jpg", (406, 17, 659, 108), (0, 600), "2009-06-01T02:41:00Z", "scale:0.0247", "orange", (239, 328)),
 ("cmst2014_fig1_perth_canyon", "C/cmst2014_p07_561x420.png", (73, 32.5, 507.5, 175), (100, 400), "2014-03-08T01:30:00Z", (2, -2), "cmst", (205, 245)),
]
NIELSEN = [  # Fig. 3: 3 nodes per panel, y = node number (no pressure scale): NORMALISED
 ("nielsen2021_fig3_sanjuan_H10N", (71, 31, 573, 632), "2017-11-15T14:50:00Z", (540, 700)),
 ("nielsen2021_fig3_sanjuan_H10S", (712, 31, 1213, 632), "2017-11-15T14:50:00Z", (460, 620)),
 ("nielsen2021_fig3_sanjuan_H04S", (1347, 31, 1849, 632), "2017-11-15T15:11:00Z", (480, 640)),
 ("nielsen2021_fig3_charge_H10N", (71, 811, 573, 1413), "2017-12-01T21:02:55Z", (500, 700)),
 ("nielsen2021_fig3_charge_H10S", (712, 811, 1213, 1413), "2017-12-01T21:02:55Z", (420, 600)),
 ("nielsen2021_fig3_charge_H04S", (1347, 811, 1849, 1413), "2017-12-01T21:23:55Z", (500, 640)),
]
VERGOZ = [   # Fig. 2 strips: x 00:00:00-00:05:00 after the station reference time; no amplitude scale: NORMALISED
 ("vergoz2021_fig2_sanjuan_H10N", (269, 278, 1291, 398), "2017-11-15T14:57:06Z", (110, 160)),
 ("vergoz2021_fig2_sanjuan_H04S", (269, 655, 1291, 776), "2017-11-15T15:17:24Z", (110, 200)),
 ("vergoz2021_fig2_charge_H10N", (269, 1110, 1291, 1229), "2017-12-01T21:09:55Z", (110, 160)),
 ("vergoz2021_fig2_charge_H04S", (269, 1488, 1291, 1607), "2017-12-01T21:30:43Z", (110, 200)),
]

def arrivals(t, a, noise, sep=20.0, k=4.0):
    """Times of local maxima of |envelope| above k x noise, at least sep seconds apart (strongest first)."""
    idx = [i for i in np.argsort(a)[::-1] if a[i] > k * noise]; keep = []
    for i in idx:
        if all(abs(t[i] - t[j]) >= sep for j in keep): keep.append(i)
        if len(keep) >= 6: break
    return ";".join(f"{t[i]:.1f}s:{a[i] / a.max():.2f}" for i in sorted(keep))

def summarise(t, env, win, dt_px, floor=0.0):
    out = ~((t >= win[0]) & (t <= win[1])); noise = float(np.percentile(np.abs(env[out]), 99)) if out.any() else np.nan
    noise = max(noise, floor)
    a = np.abs(env); ipk = int(np.argmax(a)); k = max(1, int(round(1.0 / dt_px)))
    on = None
    for i in range(len(a) - k):
        if t[i] >= win[0] - 30 and np.all(a[i:i + k] > 2 * noise):
            on = float(t[i]); break
    return dict(peak=float(a[ipk]), t_peak_s=float(t[ipk]), t_onset_s=on, noise_p99=noise, snr=float(a[ipk] / noise) if noise else None,
                arrivals_t_s_rel=arrivals(t, a, noise))

def trace(img, box, xl, yl, mask):
    a = R.load(img); l, t_, r, b = box
    cols, up, lo = R.envelope(a, (int(np.ceil(l)) + 1, int(np.ceil(t_)) + 1, int(np.floor(r)) - 1, int(np.floor(b)) - 1), MASKS[mask])
    x = R.cal(cols, l, r, xl[0], xl[1]); mid = 0.5 * (up + lo); z0 = float(np.median(mid))
    if isinstance(yl, str):
        s = float(yl.split(":")[1]); u, d = (z0 - up) * s, (z0 - lo) * s; px = s
    elif yl is None:
        u, d = z0 - up, z0 - lo; m = max(np.abs(u).max(), np.abs(d).max()); u, d = u / m, d / m; px = 1 / m
    else:
        u = R.cal(up, t_, b, yl[0], yl[1]) - R.cal(z0, t_, b, yl[0], yl[1]); d = R.cal(lo, t_, b, yl[0], yl[1]) - R.cal(z0, t_, b, yl[0], yl[1])
        px = abs(yl[0] - yl[1]) / (b - t_)
    env = np.where(np.abs(u) > np.abs(d), u, d)
    return a, cols, up, lo, x, u, d, env, px, (x[1] - x[0]) if len(x) > 1 else np.nan

def overlay(a, box, cols, up, lo, path):
    l, t_, r, b = [int(round(v)) for v in box]; im = Image.fromarray(a.astype(np.uint8)).crop((l - 5, t_ - 5, r + 5, b + 5)).convert("RGB")
    im = im.resize((im.width * 2, im.height * 2)); d = ImageDraw.Draw(im)
    for c, u, w in zip(cols, up, lo):
        d.point([(2 * (c - l + 5), 2 * (u - t_ + 5)), (2 * (c - l + 5), 2 * (w - t_ + 5))], fill=(255, 0, 255))
    im.save(path)

def main(kdir, gdir, cdir, out):
    out = Path(out); (out / "overlays").mkdir(parents=True, exist_ok=True); rows = []
    base = {"K": Path(kdir), "C": Path(cdir), "G": Path(gdir)}
    for name, img, box, xl, t0, yl, mask, win in PANELS:
        p = base[img[0]] / img[2:]
        a, cols, up, lo, x, u, d, env, px, dt = trace(p, box, xl, yl, mask)
        T0 = pd.Timestamp(t0); unit = "normalised" if yl is None else "Pa"
        pd.DataFrame(dict(t_s=x, utc=[str(T0 + pd.Timedelta(seconds=float(v))) for v in x], upper=u, lower=d)).to_csv(out / f"{name}_DIGITISED.csv", index=False)
        s = summarise(x, env, win, dt, floor=px); s.update(name=name, source=img[2:], unit=unit, t0_utc=t0, px_y=px, px_t_s=dt,
            t_peak_utc=str(T0 + pd.Timedelta(seconds=s["t_peak_s"])), t_onset_utc=None if s["t_onset_s"] is None else str(T0 + pd.Timedelta(seconds=s["t_onset_s"])))
        rows.append(s); overlay(a, box, cols, up, lo, out / "overlays" / f"{name}.png")
    for name, box, t0, win in NIELSEN:
        a = R.load(Path(gdir) / "nielsen2021_p06_1870x1491.png"); l, t_, r, b = box; T0 = pd.Timestamp(t0)
        cols, up, lo = R.envelope(a, (l + 2, t_ + 2, r - 2, b - 2), m_black)
        h = (b - t_) / 3.0
        for k, node in enumerate((3, 2, 1)):
            bt = (int(t_ + k * h + (12 if k == 0 else 3)), int(t_ + (k + 1) * h - (12 if k == 2 else 3)))   # skip tick marks at the box edges
            c2, u2, l2 = R.envelope(a, (l + 2, bt[0], r - 2, bt[1]), m_black)
            if len(c2) < 50 or (np.median(l2 - u2) < 1 and np.ptp(u2) < 2):
                rows.append(dict(name=f"{name}_node{node}", source="nielsen2021_p06", unit="normalised", note="dead channel (flat line)")); continue
            x = R.cal(c2, l, r, 0, 1440); z0 = float(np.median(0.5 * (u2 + l2))); uu, dd = z0 - u2, z0 - l2
            m = max(np.abs(uu).max(), np.abs(dd).max()); uu, dd = uu / m, dd / m; env = np.where(np.abs(uu) > np.abs(dd), uu, dd)
            pd.DataFrame(dict(t_s=x, utc=[str(T0 + pd.Timedelta(seconds=float(v))) for v in x], upper=uu, lower=dd)).to_csv(out / f"{name}_node{node}_DIGITISED.csv", index=False)
            s = summarise(x, env, win, x[1] - x[0]); s.update(name=f"{name}_node{node}", source="nielsen2021_p06", unit="normalised", t0_utc=t0, px_y=1 / m, px_t_s=float(x[1] - x[0]),
                t_peak_utc=str(T0 + pd.Timedelta(seconds=s["t_peak_s"])), t_onset_utc=None if s["t_onset_s"] is None else str(T0 + pd.Timedelta(seconds=s["t_onset_s"])))
            rows.append(s); overlay(a, (l, bt[0], r, bt[1]), c2, u2, l2, out / "overlays" / f"{name}_node{node}.png")
    for name, box, t0, win in VERGOZ:
        p = Path(gdir) / "vergoz2021_p05_1598x1694.jpeg"
        a, cols, up, lo, x, u, d, env, px, dt = trace(p, box, (0, 300), None, "yellow"); T0 = pd.Timestamp(t0)
        pd.DataFrame(dict(t_s=x, utc=[str(T0 + pd.Timedelta(seconds=float(v))) for v in x], upper=u, lower=d)).to_csv(out / f"{name}_DIGITISED.csv", index=False)
        s = summarise(x, env, win, dt); s.update(name=name, source="vergoz2021_p05", unit="normalised", t0_utc=t0, px_y=px, px_t_s=dt,
            t_peak_utc=str(T0 + pd.Timedelta(seconds=s["t_peak_s"])), t_onset_utc=None if s["t_onset_s"] is None else str(T0 + pd.Timedelta(seconds=s["t_onset_s"])))
        rows.append(s); overlay(a, box, cols, up, lo, out / "overlays" / f"{name}.png")
    # CMST Fig. 2: three HA01 spectrograms, jet colour map -> dB re panel maximum, mean over 5-40 Hz
    rows += cmst_fig2(Path(cdir) / "cmst2014_p08_561x420.png", out)
    pd.DataFrame(rows).to_csv(out / "waveform_raster_summary.csv", index=False)
    return pd.DataFrame(rows)

def jet_lut(n=256):
    import matplotlib; cm = matplotlib.colormaps["jet"]; return (np.array([cm(i / (n - 1))[:3] for i in range(n)]) * 255)

def cmst_fig2(path, out):
    a = R.load(path); lut = jet_lut(); res = []
    # spectrogram boxes found from the saturated (non-white, non-grey) area of each panel
    sat = (a.max(2) - a.min(2)) > 60
    colsat = sat[:, :445].mean(0); x0 = int(np.argmax(colsat > 0.3)); x1 = 440 - int(np.argmax(colsat[:440][::-1] > 0.3))
    rr = R.runs([y for y in range(a.shape[0]) if sat[y, x0 + 5:x1 - 5].mean() > 0.9])
    rr = [q for q in rr if q[1] - q[0] > 40][:3]
    for k, (t_, b) in enumerate(rr):
        sub = a[t_:b + 1, x0:x1 + 1].reshape(-1, 3).astype(float)
        d2 = ((sub[:, None, :] - lut[None, :, :]) ** 2).sum(-1); idx = d2.argmin(1)
        db = (-40 + 40 * idx / 255.0).reshape(b - t_ + 1, x1 - x0 + 1)
        f = 125 - 125 * (np.arange(b - t_ + 1)) / (b - t_)            # 0-125 Hz printed axis (fs 250 Hz)
        sel = (f >= 5) & (f <= 40); band = 10 * np.log10(np.mean(10 ** (db[sel] / 10), axis=0))
        ts = 100 + 250 * np.arange(x1 - x0 + 1) / (x1 - x0)            # printed x axis 100-350 s after 01:30:00 (spans the box)
        pd.DataFrame(dict(t_s=ts, utc=[str(pd.Timestamp("2014-03-08T01:30:00Z") + pd.Timedelta(seconds=float(v))) for v in ts],
                          band_5_40Hz_db_re_panel_max=band)).to_csv(out / f"cmst2014_fig2_ha01_h{k + 1}_band_DIGITISED.csv", index=False)
        i = int(np.argmax(band)); bg = float(np.median(band))
        res.append(dict(name=f"cmst2014_fig2_ha01_h{k + 1}", source="cmst2014_p08", unit="dB re panel max (5-40 Hz mean)", t0_utc="2014-03-08T01:30:00Z",
                        peak=float(band[i]), t_peak_s=float(ts[i]), t_peak_utc=str(pd.Timestamp("2014-03-08T01:30:00Z") + pd.Timedelta(seconds=float(ts[i]))),
                        noise_p99=bg, snr=float(band[i] - bg), note=f"box x {x0}-{x1}, y {t_}-{b}; SNR here = peak minus median, dB"))
    return res

if __name__ == "__main__":
    print(main(*sys.argv[1:5]).to_string())
