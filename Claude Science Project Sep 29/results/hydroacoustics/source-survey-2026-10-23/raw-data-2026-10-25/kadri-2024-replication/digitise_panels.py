"""Digitise Kadri (2024) Figs. 4-6 pressure panels (right-hand column) from the publisher's full-resolution PNGs
(media.springernature.com .../41598_2024_60529_FigN_HTML.png, CC BY 4.0).

Per panel: axes frame (dark lines), x calibration 0..10 min at the frame edges (MATLAB xlim [0 10]), y calibration by
least squares on the detected left-axis tick marks against the printed tick labels (TICKS below, read by eye from the
figure; units Pa = 1e6 uPa as printed 'x10^6'), orange trace mask -> per pixel column upper and lower envelope (Pa),
black box -> left/right edges (min after panel start). Raster digitisation: 1 px ~ 0.78 s; trace clipped at the frame.
"""
import numpy as np
from PIL import Image

# panel: (fig, title, station, panel start UTC, y_top, y_bottom, x_left, x_right, tick labels top->bottom in Pa)
PANELS = {
 "F35A_H11N":  (4, "F-35a (H11N)", "H11N", "2019-04-09T10:58:00", 47, 319, 1196, 1968, [1, .5, 0, -.5, -1]),
 "F35A_H11S":  (4, "F-35a (H11S)", "H11S", "2019-04-09T10:59:00", 473, 745, 1197, 1968, [1, .5, 0, -.5, -1]),
 "SJ182_H08S": (4, "Sriwijaya Air Flight 182 (H08S)", "H08S", "2021-01-09T08:06:00", 1803, 2078, 1199, 1968, [1, .5, 0, -.5, -1]),
 "TA810_H11N": (5, "Transair Flight 810 (H11N)", "H11N", "2021-07-02T12:28:00", 470, 740, 1217, 1979, [1, .5, 0, -.5, -1]),
 "TA810_H11S": (5, "Transair Flight 810 (H11S)", "H11S", "2021-07-02T12:27:00", 909, 1182, 1217, 1979, [1, .5, 0, -.5, -1]),
 "AB1103_H08S": (6, "AB Aviation Y61103 (H08S)", "H08S", "2022-02-26T09:36:00", 49, 323, 1222, 1983, [1, .5, 0, -.5, -1]),
 "QZ8501_H01W": (6, "Air Asia Flight 8501 (H01W)", "H01W", "2014-12-27T23:51:00", 513, 787, 1222, 1983, [1, .5, 0, -.5, -1]),
}

def load(fig):
    return np.array(Image.open(f"kadri/src/hires/Fig{fig}.png").convert("RGB")).astype(int)

def orange_mask(a):
    """Wide orange mask: includes the lighter anti-aliased tint of thin spikes (e.g. 237,148,116). The strict mask
    (r>170, 40<g<140, b<90, r-g>90) misses printed spikes (F-35A H11N peak 0.86 vs 1.03 Pa) and is kept as a check."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > 150) & (r - b > 70) & (r - g > 40) & (g < 200)

def orange_mask_strict(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > 170) & (g > 40) & (g < 140) & (b < 90) & (r - g > 90)

def dark_mask(a, thr=110):
    return a.max(axis=2) < thr

def refine_frame(a, y0, y1, x0, x1):
    d = dark_mask(a, 150)
    # left frame column: the column near x0 with most dark pixels between y0..y1
    cols = range(x0 - 6, x0 + 7); xl = max(cols, key=lambda x: d[y0:y1, x].sum())
    cols = range(x1 - 6, x1 + 7); xr = max(cols, key=lambda x: d[y0:y1, x].sum())
    rows = range(y0 - 6, y0 + 7); yt = max(rows, key=lambda y: d[y, xl:xr].sum())
    rows = range(y1 - 6, y1 + 7); yb = max(rows, key=lambda y: d[y, xl:xr].sum())
    return yt, yb, xl, xr

def ticks_left(a, yt, yb, xl):
    """y centres of the printed tick LABELS left of the frame (x = xl-75 .. xl-4): dark-text row clusters >= 15 px tall.
    (Tick marks themselves are hidden under the trace.) Text centre ~ tick position, +/- 1-2 px (~0.01 Pa)."""
    d = dark_mask(a, 140)[yt - 18:yb + 18, xl - 75:xl - 4]
    rows = np.where(d.sum(1) >= 1)[0] + yt - 18
    grp = []
    for y in rows:
        if grp and y - grp[-1][-1] <= 2: grp[-1].append(y)
        else: grp.append([y])
    return [float((g[0] + g[-1]) / 2) for g in grp if len(g) >= 15]

def box_edges(a, yt, yb, xl, xr):
    d = dark_mask(a, 110)
    h = yb - yt
    col = d[yt + 3:yb - 3, xl + 12:xr - 12].sum(0)
    xs = np.where(col > 0.35 * h)[0] + xl + 12
    grp = []
    for x in xs:
        if grp and x - grp[-1][-1] <= 2: grp[-1].append(x)
        else: grp.append([x])
    return [float(np.mean(g)) for g in grp]

def digitise(key):
    fig, title, sta, t0, y0, y1, x0, x1, labels = PANELS[key]
    a = load(fig)
    yt, yb, xl, xr = refine_frame(a, y0, y1, x0, x1)
    tk = ticks_left(a, yt, yb, xl)
    # match ticks to labels: take the len(labels) ticks best spaced (equal spacing)
    tk = np.array(tk)
    best = None
    from itertools import combinations
    for comb in combinations(range(len(tk)), len(labels)):
        yy = tk[list(comb)]; sp = np.diff(yy)
        if np.all(sp > 10):
            sc = np.std(sp)
            if best is None or sc < best[0]: best = (sc, yy)
    yy = best[1]
    fit = np.polyfit(yy, labels, 1)               # Pa per px (negative slope) and offset
    m = orange_mask(a)[yt + 1:yb, xl + 1:xr]
    ncol = m.shape[1]
    t_min = (np.arange(ncol) + 0.5) / ncol * 10.0
    up = np.full(ncol, np.nan); lo = np.full(ncol, np.nan)
    for j in range(ncol):
        r = np.where(m[:, j])[0]
        if len(r):
            up[j] = np.polyval(fit, r.min() + yt + 1); lo[j] = np.polyval(fit, r.max() + yt + 1)
    bx = box_edges(a, yt, yb, xl, xr)
    bx_min = [(x - xl) / (xr - xl) * 10.0 for x in bx]
    return dict(key=key, title=title, station=sta, t0=t0, frame=(yt, yb, xl, xr), ticks_px=list(map(float, yy)),
                pa_per_px=float(fit[0]), y_zero_px=float(-fit[1] / fit[0]), t_min=t_min, upper_pa=up, lower_pa=lo,
                box_px=bx, box_min=bx_min, s_per_px=600.0 / (xr - xl),
                ylim_pa=(float(np.polyval(fit, yb)), float(np.polyval(fit, yt))))
