"""End-of-flight impact maps for the Journal of Navigation paper (8 Nov 2026).

Reads only the files in ../data (this package). No other project code is needed.
Conventions
  * Positions: WGS-84 latitude/longitude in degrees (south negative).
  * Map projection: Mercator (y = asinh(tan(lat)) expressed in degrees so that the axes have equal scale).
  * Weights: each 00:19 treatment D has a column log_weight_<D> in the hand-off file; w = exp(lw - max), normalised.
  * Impact-position density: weighted histogram in a frame aligned with the 7th arc (along-arc distance s, NM;
    signed distance from the arc d, NM, positive to the south-east), smoothed with a Gaussian kernel of
    12 NM along the arc and 3 NM across it, then sampled onto a 0.025 deg latitude/longitude grid.
  * Probability regions: smallest regions holding the stated share of probability (highest-density regions).
"""
import os, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
MM = 1 / 25.4
WID = 127 * MM
NM_KM = 1.852

# ---------------------------------------------------------------- data
ROUTE_FILE = {"df": "davey-fuel", "wp": "waypoints"}
TREATMENTS = {  # code: wording used in the paper graphics (project wording rules)
    "D13": "No 00:19 data used",
    "D0": "Log-on event only",
    "D7": "BTO only",
    "D8": "BTO and 00:19:29 BFO (R600) as observed",
    "D9": "BTO and both BFOs as observed",
    "D10": "BTO and both BFOs, Holland transient bias added",
    "D14": "BTO and both BFOs, Holland transient bias added (zero floor)",
    "D11": "BTO and both BFOs, Holland transient bias added to the 00:19:37 BFO only",
    "D12": "As D11, zero floor",
}


def load(route="df"):
    z = dict(np.load(os.path.join(DATA, f"eof-handoff-{ROUTE_FILE[route]}.npz")))
    s = dict(np.load(os.path.join(DATA, f"settling-energy-transfer-{ROUTE_FILE[route]}.npz")))
    assert (s["row_index"] == np.arange(len(z["latitude_deg"]))).all()
    z["peak_power_w"] = s["energy_transfer_peak_rate_w"].astype(float)
    return z


def weights(z, code):
    lw = z["log_weight_" + code]
    w = np.zeros_like(lw)
    ok = np.isfinite(lw)
    w[ok] = np.exp(lw[ok] - lw[ok].max())
    return w / w.sum()


def wquantile(x, w, q):
    o = np.argsort(x)
    c = np.cumsum(w[o])
    return np.interp(q, c / c[-1], x[o])


# ---------------------------------------------------------------- arcs and arc frame
A7 = np.loadtxt(os.path.join(DATA, "arc7-001929-sea-level.csv"), delimiter=",", skiprows=1)
A6 = np.loadtxt(os.path.join(DATA, "arc6-001059-35000ft.csv"), delimiter=",", skiprows=1)
LA7, LO7 = A7[:, 0], A7[:, 1]
LA6, LO6 = A6[:, 0], A6[:, 1]


def _uv(lat, lon):
    p, l = np.radians(lat), np.radians(lon)
    return np.c_[np.cos(p) * np.cos(l), np.cos(p) * np.sin(l), np.sin(p)]


def gc_nm(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2)
    dl = np.radians(lo2 - lo1)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a)) / NM_KM


_TREE = cKDTree(_uv(LA7, LO7))
_S7 = np.r_[0, np.cumsum(gc_nm(LA7[:-1], LO7[:-1], LA7[1:], LO7[1:]))]
_S7 -= np.interp(-40.0, LA7, _S7)          # along-arc distance, 0 at 40 S, increasing northwards


def arc_frame(lat, lon):
    """Along-arc distance s (NM) of the nearest 7th-arc point and signed distance d (NM, + south-east)."""
    c, i = _TREE.query(_uv(lat, lon))
    d = 2 * np.arcsin(np.clip(c / 2, 0, 1)) * 6371.0 / NM_KM
    sgn = np.sign(lon - np.interp(lat, LA7, LO7))
    return _S7[i], sgn * d


# ---------------------------------------------------------------- density on the map grid
GD = 0.025
GLAT0, GLAT1, GLON0, GLON1 = -45.0, -20.0, 84.0, 108.0
gxe = np.arange(GLON0, GLON1 + 1e-9, GD); gye = np.arange(GLAT0, GLAT1 + 1e-9, GD)
gxc = 0.5 * (gxe[1:] + gxe[:-1]); gyc = 0.5 * (gye[1:] + gye[:-1])
_GX, _GY = np.meshgrid(gxc, gyc)
_GS, _GDIST = [a.reshape(_GX.shape) for a in arc_frame(_GY.ravel(), _GX.ravel())]
CELL_NM2 = (GD * 60) ** 2 * np.cos(np.radians(gyc))[:, None] * np.ones((1, len(gxc)))
CELL_KM2 = CELL_NM2 * NM_KM ** 2
SB = np.arange(-350, 1551, 5.0); DB = np.arange(-200, 200.01, 2.0)
SIG_ALONG_NM, SIG_ACROSS_NM = 12.0, 3.0


def density(z, w, frame=None):
    """Probability per map cell (sums to 1) for weights w."""
    s, d = frame if frame is not None else arc_frame(z["latitude_deg"], z["longitude_deg"])
    h, _, _ = np.histogram2d(d, s, bins=[DB, SB], weights=w)
    h = gaussian_filter(h, (SIG_ACROSS_NM / 2.0, SIG_ALONG_NM / 5.0)) / 10.0
    ri = (_GDIST - DB[0]) / 2.0 - 0.5
    ci = (_GS - SB[0]) / 5.0 - 0.5
    v = map_coordinates(h, [ri.ravel(), ci.ravel()], order=1, mode="constant", cval=0.0).reshape(_GX.shape)
    p = v * CELL_NM2
    return p / p.sum()


def hpd_levels(p, shares):
    s = np.sort(p.ravel())[::-1]
    c = np.cumsum(s)
    return [s[min(np.searchsorted(c, q), len(s) - 1)] for q in shares]


def hpd_area_km2(p, share):
    return float(CELL_KM2[p >= hpd_levels(p, [share])[0]].sum())


def union_region(ps, share=0.95, smooth=1.0):
    u = np.zeros_like(ps[0], bool)
    for p in ps:
        u |= p >= hpd_levels(p, [share])[0]
    return gaussian_filter(u.astype(float), smooth)


# ---------------------------------------------------------------- searched area
_C = np.load(os.path.join(DATA, "searched-area-coverage-0p01deg.npz"))
_cs = float(_C["step_deg"])
SA_LAT = float(_C["south_edge_deg"]) + (np.arange(_C["union_percent"].shape[0]) + 0.5) * _cs
SA_LON = float(_C["west_edge_deg"]) + (np.arange(_C["union_percent"].shape[1]) + 0.5) * _cs
SA_COV = gaussian_filter(_C["union_percent"].astype(float) / 100.0, 1.2)
_RAW = _C["union_percent"] / 100.0


def coverage_at(lat, lon):
    i = np.floor((lat - SA_LAT[0]) / _cs + 0.5).astype(int)
    j = np.floor((lon - SA_LON[0]) / _cs + 0.5).astype(int)
    ok = (i >= 0) & (i < len(SA_LAT)) & (j >= 0) & (j < len(SA_LON))
    out = np.zeros(len(lat))
    out[ok] = _RAW[i[ok], j[ok]]
    return out


# ---------------------------------------------------------------- plotting
def merc(lat):
    return np.degrees(np.arcsinh(np.tan(np.radians(lat))))


YC = merc(gyc)
SA_Y = merc(SA_LAT)


def rc():
    matplotlib.rcdefaults()
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "Times", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix", "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "legend.fontsize": 8, "axes.linewidth": 0.6, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
        "xtick.direction": "out", "ytick.direction": "out", "legend.frameon": False, "savefig.dpi": 600,
        "pdf.fonttype": 42, "hatch.linewidth": 0.35, "lines.solid_capstyle": "butt",
    })


def graticule(ax, ext, major=2.0, minor=0.5, xlabels=True, ylabels=True):
    lo0, lo1, la0, la1 = ext
    for x in np.arange(np.ceil(lo0 / minor) * minor, lo1 + 1e-9, minor):
        mj = abs(x / major - round(x / major)) < 1e-6
        ax.axvline(x, color="0.60" if mj else "0.82", lw=0.35 if mj else 0.2, zorder=0)
    for y in np.arange(np.ceil(la0 / minor) * minor, la1 + 1e-9, minor):
        mj = abs(y / major - round(y / major)) < 1e-6
        ax.axhline(merc(y), color="0.60" if mj else "0.82", lw=0.35 if mj else 0.2, zorder=0)
    xt = np.arange(np.ceil(lo0 / major) * major, lo1 + 1e-9, major)
    yt = np.arange(np.ceil(la0 / major) * major, la1 + 1e-9, major)
    ax.set_xticks(xt); ax.set_xticklabels([f"{x:g}°E" for x in xt] if xlabels else [])
    ax.set_yticks(merc(yt)); ax.set_yticklabels([f"{-y:g}°S" for y in yt] if ylabels else [])
    ax.set_xlim(lo0, lo1); ax.set_ylim(merc(la0), merc(la1)); ax.set_aspect(1)
    ax.tick_params(length=2.5, width=0.5, pad=1.5)


def draw_arcs(ax, six=True, lw7=0.8):
    ax.plot(LO7, merc(LA7), color="k", lw=lw7, zorder=6)
    if six:
        ax.plot(LO6, merc(LA6), color="k", lw=0.5, ls=(0, (4, 2)), zorder=6)


def label_on_arc(ax, lat, text, which=7, offset=(0.0, 0.0), va="bottom", fs=8, ha="left", step=20):
    la, lo = (LA7, LO7) if which == 7 else (LA6, LO6)
    i = int(np.argmin(abs(la - lat)))
    j = min(i + step, len(la) - 1)
    x0, y0, x1, y1 = lo[i], merc(la[i]), lo[j], merc(la[j])
    ang = np.degrees(np.arctan2(y1 - y0, x1 - x0))
    ax.text(x0 + offset[0], y0 + offset[1], text, rotation=ang, rotation_mode="anchor", ha=ha, va=va,
            fontsize=fs, zorder=9, transform_rotates_text=True)


def draw_searched(ax, hatch=True, edge=True, z=0.5):
    if hatch:
        cs = ax.contourf(SA_LON, SA_Y, SA_COV, levels=[0.5, 5], colors="none", hatches=["////////"], zorder=z)
        try:
            cs.set_edgecolor("0.55"); cs.set_linewidth(0.0)
        except Exception:
            for c in cs.collections:
                c.set_edgecolor("0.55"); c.set_linewidth(0.0)
    if edge:
        ax.contour(SA_LON, SA_Y, SA_COV, levels=[0.5], colors="0.25", linewidths=0.45, zorder=4.6)


def fill_regions(ax, p, shares=(0.5, 0.95), greys=("0.45", "0.82"), edge="0.2", z=1.0):
    lv = hpd_levels(p, shares)
    for k in np.argsort(lv):          # outer region first
        ax.contourf(gxc, YC, p, levels=[lv[k], p.max() * 1.01], colors=[greys[k]], zorder=z)
    if edge:
        ax.contour(gxc, YC, p, levels=sorted(lv), colors=edge, linewidths=0.3, zorder=z + 0.1)


def line_regions(ax, p, shares=(0.5, 0.95), lws=(1.2, 0.6), ls="-", color="k", z=5.0):
    for l, w in zip(hpd_levels(p, shares), lws):
        ax.contour(gxc, YC, p, levels=[l], colors=color, linewidths=w, linestyles=[ls], zorder=z)


def line_field(ax, f, level=0.5, lw=0.8, ls=(0, (5, 2)), color="k", z=5.0):
    ax.contour(gxc, YC, f, levels=[level], colors=color, linewidths=lw, linestyles=[ls], zorder=z)


def scale_bar(ax, lon0, lat0, nm=100, label=True):
    dlon = nm / 60 / np.cos(np.radians(lat0)); y = merc(lat0)
    ax.plot([lon0, lon0 + dlon], [y, y], color="k", lw=1.4, zorder=9)
    if label:
        ax.text(lon0 + dlon / 2, y + 0.12, f"{nm} NM", ha="center", va="bottom", fontsize=8, zorder=9)


def letter(ax, s, x=0.02, y=0.98, bg=True):
    ax.text(x, y, f"({s})", transform=ax.transAxes, ha="left", va="top", fontsize=8, zorder=20,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.6) if bg else None)
