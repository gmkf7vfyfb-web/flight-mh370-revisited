"""Build the end-of-flight Results candidate graphics (8 Nov 2026) from the files in ../data only.

Usage:  python make_figures.py            (writes ../figures and ../results)
Each figure is written in Journal of Navigation (JON) form and in working form:
  <name>-word.png  600 dpi, no title, no notes (for Word)      <name>.pdf  vector
  <name>-proof.png the JON graphic with the caption beneath    <name>-caption.txt
  <name>-working.png the graphic with a title above and the technical footnote below
Default route model: Davey model with the fuel model ('df').
"""
import os, sys, textwrap, json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Times New Roman', 'mathtext.it': 'Times New Roman:italic'})
import matplotlib.patheffects as pe
from matplotlib.patches import Patch, Rectangle, PathPatch
from matplotlib.lines import Line2D
from scipy.ndimage import gaussian_filter
from scipy import ndimage as ndi
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eofmaps as E

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "figures"); RES = os.path.join(HERE, "..", "results")
os.makedirs(OUT, exist_ok=True); os.makedirs(RES, exist_ok=True)

# ------------------------------------------------------------------ data
Z = E.load("df")
FR = E.arc_frame(Z["latitude_deg"], Z["longitude_deg"])
CODES = ["D13", "D0", "D7", "D8", "D9", "D10", "D14", "D11", "D12"]
W = {D: E.weights(Z, D) for D in CODES}
P = {D: E.density(Z, W[D], FR) for D in CODES}
BIAS = ["D10", "D14", "D11", "D12"]          # treatments with a start-up bias, all with >= 1,000 effective samples
KE = Z["kinetic_energy_j"] / 1e9
PP = Z["peak_power_w"] / 1e9
TMIN = Z["impact_s_after_001929"] / 60.0
TREAT = pd.read_csv(os.path.join(E.DATA, "eof-treatments.csv"))
TDF = TREAT[TREAT["route family"] == "Davey model + fuel"].set_index("code")
EXT = (85.5, 104.0, -41.0, -24.0)            # overview map: lon0, lon1, lat0, lat1
ZEXT = (87.4, 93.4, -39.2, -34.6)            # close view of the highest-probability area

# searched area outline for display: fill holes and remove islands < 30 cells (0.01 deg), close and open with 3 x 3 cells
_m = E.SA_COV >= 0.5
_h = ndi.binary_fill_holes(_m) & ~_m; _l, _n = ndi.label(_h); _s = ndi.sum(_h, _l, range(1, _n + 1))
_m |= np.isin(_l, np.where(_s < 30)[0] + 1)
_l, _n = ndi.label(_m); _s = ndi.sum(_m, _l, range(1, _n + 1)); _m &= ~np.isin(_l, np.where(_s < 30)[0] + 1)
_m = ndi.binary_closing(_m, np.ones((3, 3))); _m = ndi.binary_opening(_m, np.ones((3, 3))); _m = ndi.binary_closing(_m, np.ones((3, 3)))
_f, _a = plt.subplots(); SA_PATH = _a.contourf(E.SA_LON, E.SA_Y, gaussian_filter(_m.astype(float), 0.8), levels=[0.5, 5]).get_paths()[0]; plt.close(_f)
HATCH = "\\\\\\\\\\"

# ------------------------------------------------------------------ drawing helpers
def arcs(a, lw7=0.8):
    a.plot(E.LO7, E.merc(E.LA7), color="k", lw=lw7, zorder=6)
    a.plot(E.LO6, E.merc(E.LA6), color="0.3", lw=0.5, ls=(0, (6, 1.5, 1, 1.5)), zorder=6)


def searched(a, z=3.2):
    a.add_patch(PathPatch(SA_PATH, fc="none", ec="0.3", lw=0, hatch=HATCH, zorder=z))


def sa_patch():
    return Patch(fc="white", ec="0.3", lw=0, hatch=HATCH, label="Previously searched area")


ARC_H = [Line2D([], [], color="k", lw=0.8, label="7th arc (00:19:29, sea level)"),
         Line2D([], [], color="0.3", lw=0.5, ls=(0, (6, 1.5, 1, 1.5)), label="6th arc (00:10:59, 35,000 ft)")]
HALO = [pe.withStroke(linewidth=2.2, foreground="white")]


def box(a, ext, lw=0.5):
    lo0, lo1, la0, la1 = ext
    a.add_patch(Rectangle((lo0, E.merc(la0)), lo1 - lo0, E.merc(la1) - E.merc(la0), fill=False, lw=lw, ec="k", zorder=10))


def tag(a, s, x=0.05, y=0.975, ha="left", va="top", bg=True):
    a.text(x, y, f"({s})", transform=a.transAxes, ha=ha, va=va, fontsize=8, zorder=30,
           bbox=dict(fc="white", ec="none", pad=0.5) if bg else None)


def hw(ext):
    return (E.merc(ext[3]) - E.merc(ext[2])) / (ext[1] - ext[0])


def sysres(w, n, seed=11):
    c = np.cumsum(w); u = (np.random.default_rng(seed).random() + np.arange(n)) / n
    return np.searchsorted(c / c[-1], u)


def pct(s):
    return f"{int(round(s * 100))} %"


# ------------------------------------------------------------------ 1. overlay map (develops Pete's example 2)
def fig_overlay(searched_on=False, r600=False, shares=(0.5, 0.95)):
    E.rc(); Wd = E.WID; axw = 0.86; mh = Wd * axw * hw(EXT); top, bot = 0.08, 0.27; H = mh + top + bot
    fig = plt.figure(figsize=(Wd, H)); ax = fig.add_axes([0.095, bot / H, axw, mh / H]); E.graticule(ax, EXT, 2, 0.5)
    env = E.union_region([P[D] for D in BIAS], shares[-1])

    def layers(a):
        E.fill_regions(a, P["D7"], shares, greys=("0.55", "0.84"), edge="0.35")
        if searched_on: searched(a)
        E.line_field(a, env, lw=0.8, ls=(0, (4, 1.6)))
        E.line_regions(a, P["D10"], shares, lws=(1.25, 0.65))
        if r600: E.line_regions(a, P["D8"], (shares[-1],), lws=(0.8,), ls=(0, (1, 1.3)))
        arcs(a)
    layers(ax)
    E.label_on_arc(ax, -32.6, "7th arc", 7, offset=(0.75, -0.75), va="top")
    E.label_on_arc(ax, -29.0, "6th arc", 6, offset=(-0.35, 0.3), va="bottom")
    E.scale_bar(ax, 95.4, -40.55, 100)
    tag(ax, "a", x=0.985, ha="right", bg=False)
    ix = fig.add_axes([0.095 + axw * 0.085, bot / H + mh / H * 0.505, axw * 0.44, mh / H * 0.47])
    E.graticule(ix, ZEXT, 1, 0.25); layers(ix); ix.tick_params(pad=1)
    tag(ix, "b", x=0.975, y=0.03, ha="right", va="bottom")
    box(ax, ZEXT, 0.6)
    q = [pct(s) for s in shares]
    h = [Patch(fc="0.55", ec="0.35", lw=0.3, label=f"BTO only, {q[0]}"), Patch(fc="0.84", ec="0.35", lw=0.3, label=f"BTO only, {q[1]}"),
         Line2D([], [], color="k", lw=1.25, label=f"Holland transient bias added, {q[0]}"),
         Line2D([], [], color="k", lw=0.65, label=f"Holland transient bias added, {q[1]}"),
         Line2D([], [], color="k", lw=0.8, ls=(0, (4, 1.6)), label=f"Outer limit of the bias treatments, {q[1]}")]
    if r600: h.append(Line2D([], [], color="k", lw=0.8, ls=(0, (1, 1.3)), label=f"00:19:29 BFO only, as observed, {q[1]}"))
    if searched_on: h.append(sa_patch())
    if shares[-1] < 0.98:
        ax.legend(handles=h, loc="lower right", bbox_to_anchor=(1.0, 0.065), fontsize=8, handlelength=2.2, borderaxespad=0.3)
    else:   # the 99 % region fills the south-east corner: legend below the map
        add = 0.30; Wf, Hf = fig.get_size_inches(); fig.set_size_inches(Wf, Hf + add)
        for a_ in fig.axes:
            b_ = a_.get_position(); a_.set_position([b_.x0, (b_.y0 * Hf + add) / (Hf + add), b_.width, b_.height * Hf / (Hf + add)])
        fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.02, 0.0), ncol=2, fontsize=8, handlelength=2.2, columnspacing=1.2)
    return fig


# ------------------------------------------------------------------ 2. small multiples (develops Pete's example 3)
def fig_multiples(cols=("D7", "D8", "D10"), searched_on=True, shares=(0.5, 0.95), greys=("0.5", "0.84")):
    E.rc(); Wd = E.WID; n = len(cols); L0 = 0.075; gap = 0.014; pw = (0.99 - L0 - gap * (n - 1)) / n
    h1 = Wd * pw * hw(EXT); h2 = Wd * pw * hw(ZEXT); bot = 0.85 if len(shares) == 2 else 0.95; mid = 0.2; H = h1 + h2 + mid + bot + 0.06
    fig = plt.figure(figsize=(Wd, H)); envf = E.union_region([P[x] for x in BIAS], shares[-1])

    def layer(a, D):
        E.fill_regions(a, P[D], shares, greys=greys, edge="0.2")
        if searched_on: searched(a)
        if D == "D10": E.line_field(a, envf, lw=0.7, ls=(0, (4, 1.6)))
        arcs(a, 0.7)
    lets = "abcdefgh"
    for k, D in enumerate(cols):
        x0 = L0 + k * (pw + gap)
        a = fig.add_axes([x0, (bot + h2 + mid) / H, pw, h1 / H]); E.graticule(a, EXT, 4, 1, ylabels=(k == 0)); layer(a, D)
        xt = [90, 98] if n > 2 else [88, 92, 96, 100]; a.set_xticks(xt); a.set_xticklabels([f"{x}°E" for x in xt])
        tag(a, lets[k], bg=False); box(a, ZEXT)
        b = fig.add_axes([x0, bot / H, pw, h2 / H]); E.graticule(b, ZEXT, 2 if n > 2 else 1, 0.5 if n > 2 else 0.25, ylabels=(k == 0)); layer(b, D)
        xt = [88, 90, 92] if n > 2 else [88, 89, 90, 91, 92, 93]; b.set_xticks(xt); b.set_xticklabels([f"{x}°E" for x in xt])
        tag(b, lets[k + n])
    h = [Patch(fc=g, ec="0.2", lw=0.3, label=f"{pct(s)} of probability") for s, g in zip(shares, greys)] + ARC_H
    if "D10" in cols: h.append(Line2D([], [], color="k", lw=0.7, ls=(0, (4, 1.6)), label=f"Outer limit of the bias treatments, {pct(shares[-1])}"))
    if searched_on: h.append(sa_patch())
    fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=2, fontsize=8, handlelength=2.0, columnspacing=1.2)
    return fig


# ------------------------------------------------------------------ 3. energy and peak power (develops Pete's examples 5 and 6)
CSTY = {"D7": dict(color="0.55", lw=1.0), "D8": dict(color="k", lw=0.8, ls=(0, (1, 1.2))), "D10": dict(color="k", lw=1.3)}


def contour_halo(a, p, shares=(0.5, 0.95), lws=(1.0, 0.6)):
    for l, w in zip(E.hpd_levels(p, shares), lws):
        cs = a.contour(E.gxc, E.YC, p, levels=[l], colors="k", linewidths=w, zorder=7); cs.set_path_effects(HALO)


def dots(a, D, val, edges, greys, sizes, n=3000):
    idx = sysres(W[D], n); v = val[idx]; x = Z["longitude_deg"][idx]; y = E.merc(Z["latitude_deg"][idx])
    for k in range(len(greys)):
        m = (v >= edges[k]) & (v < edges[k + 1]); a.scatter(x[m], y[m], s=sizes[k], c=greys[k], lw=0, zorder=3 + k * 0.1, rasterized=True)


def cdf(a, val, Ds, xl, xt, xlab, band=None):
    for D in Ds:
        o = np.argsort(val); c = np.cumsum(W[D][o]); a.plot(val[o], c / c[-1], **CSTY[D])
    if band: a.axvspan(*band, fc="none", ec="0.45", hatch="/////", lw=0, zorder=0)
    a.set_xscale("log"); a.set_xlim(*xl); a.set_xticks(xt); a.set_xticklabels([f"{t:g}" for t in xt]); a.xaxis.set_minor_formatter(plt.NullFormatter())
    a.set_ylim(0, 1); a.set_yticks([0, 0.5, 1]); a.set_xlabel(xlab); a.set_ylabel("Cumulative probability", labelpad=1)
    for s in ("top", "right"): a.spines[s].set_visible(False)


def fig_energy_maps(quantity="energy"):
    E.rc(); Wd = E.WID
    if quantity == "energy":
        val = KE; edges = [0, 1, 4, 1e9]; labs = ["Under 1 GJ", "1 to 4 GJ", "4 GJ or more"]; ttl = "Impact kinetic energy"
    else:
        val = PP; q = E.wquantile(PP, W["D7"], [0.5, 0.9]); edges = [0, q[0], q[1], 1e9]
        labs = [f"Under {q[0]:.1f} GW (lower half)", f"{q[0]:.1f} to {q[1]:.0f} GW", f"{q[1]:.0f} GW or more (top tenth)"]
        ttl = "Peak impact power (classes set on BTO only)"
    greys = ["0.72", "0.42", "0.0"]; sizes = [0.9, 1.1, 1.5]
    L0 = 0.075; gap = 0.012; pw = 0.262; h1 = Wd * pw * hw(EXT); h2 = Wd * pw * hw(ZEXT); bot = 1.1; mid = 0.2; H = h1 + h2 + mid + bot + 0.06
    fig = plt.figure(figsize=(Wd, H))
    for k, D in enumerate(["D7", "D10"]):
        x0 = L0 + k * (pw + gap)
        a = fig.add_axes([x0, (bot + h2 + mid) / H, pw, h1 / H]); E.graticule(a, EXT, 4, 1, ylabels=(k == 0)); a.set_xticks([90, 98]); a.set_xticklabels(["90°E", "98°E"])
        dots(a, D, val, edges, greys, [s * 0.7 for s in sizes]); contour_halo(a, P[D], (0.5, 0.95), (0.8, 0.5)); arcs(a, 0.6); box(a, ZEXT)
        tag(a, "ab"[k], bg=False)
        b = fig.add_axes([x0, bot / H, pw, h2 / H]); E.graticule(b, ZEXT, 2, 0.5, ylabels=(k == 0)); b.set_xticks([88, 90, 92]); b.set_xticklabels(["88°E", "90°E", "92°E"])
        dots(b, D, val, edges, greys, [s * 1.6 for s in sizes]); contour_halo(b, P[D]); arcs(b, 0.7); tag(b, "de"[k])
    xc0 = L0 + 2 * (pw + gap) + 0.075; cw = 0.99 - xc0
    c1 = fig.add_axes([xc0, (bot + h2 + mid + 0.05) / H, cw, (h1 - 0.05) / H]); c2 = fig.add_axes([xc0, bot / H, cw, (h2 - 0.22) / H])
    cdf(c1, KE, ["D7", "D8", "D10"], (0.2, 15), [0.3, 1, 3, 10], "Impact kinetic energy (GJ)", band=(6.4, 9.0))
    cdf(c2, PP, ["D7", "D8", "D10"], (0.05, 300), [0.1, 1, 10, 100], "Peak impact power (GW)")
    tag(c1, "c", x=0.03, y=1.0, bg=False); tag(c2, "f", x=0.03, y=1.0, bg=False)
    h = [Line2D([], [], marker="o", ls="none", ms=s, mfc=g, mec="none", label=l) for g, s, l in zip(greys, [2.2, 2.6, 3.0], labs)]
    h += [Line2D([], [], color="k", lw=0.9, label="50 % and 95 % of probability")]
    h2 = [Line2D([], [], label="BTO only", **CSTY["D7"]), Line2D([], [], label="00:19:29 BFO only, as observed", **CSTY["D8"]),
          Line2D([], [], label="Holland transient bias added", **CSTY["D10"]), Patch(fc="none", ec="0.45", hatch="/////", lw=0, label="Boeing 777 simulations, energy range (c)")]
    fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.01, 0.0), fontsize=8, handlelength=1.5, title=ttl, title_fontsize=8, alignment="left")
    fig.legend(handles=h2, loc="lower left", bbox_to_anchor=(0.50, 0.0), fontsize=8, handlelength=2.0, title="Graphs (c) and (f)", title_fontsize=8, alignment="left")
    return fig


def share_field(D, thr=4.0):
    wh = W[D] * (KE >= thr); num = E.density(Z, wh, FR) * wh.sum()
    return np.where(P[D] > 0, num / np.maximum(P[D], 1e-300), np.nan)


def region_shares(D, thr=4.0):
    p = P[D]; lv = E.hpd_levels(p, (0.5, 0.95))
    i = np.clip(((Z["latitude_deg"] - E.GLAT0) / E.GD).astype(int), 0, len(E.gyc) - 1)
    j = np.clip(((Z["longitude_deg"] - E.GLON0) / E.GD).astype(int), 0, len(E.gxc) - 1)
    v = p[i, j]; rg = np.where(v >= lv[0], 0, np.where(v >= lv[1], 1, 2)); w = W[D]
    return [float((w[rg == r] * (KE[rg == r] >= thr)).sum() / w[rg == r].sum()) for r in (0, 1, 2)]


SHC = [0, 0.25, 0.5, 0.75, 1.0001]; SHG = ["0.93", "0.78", "0.58", "0.32"]


def fig_energy_share():
    E.rc(); Wd = E.WID; L0 = 0.075; gap = 0.012; pw = 0.262; h1 = Wd * pw * hw(EXT); h2 = Wd * pw * hw(ZEXT); bot = 1.1; mid = 0.2; H = h1 + h2 + mid + bot + 0.06
    fig = plt.figure(figsize=(Wd, H))
    for k, D in enumerate(["D7", "D10"]):
        p = P[D]; l99 = E.hpd_levels(p, (0.99,))[0]; shm = np.where(p >= l99, share_field(D), np.nan); x0 = L0 + k * (pw + gap)
        for row, (ext, maj, mn, yy, hh, lets) in enumerate([(EXT, 4, 1, bot + h2 + mid, h1, "ab"), (ZEXT, 2, 0.5, bot, h2, "de")]):
            a = fig.add_axes([x0, yy / H, pw, hh / H]); E.graticule(a, ext, maj, mn, ylabels=(k == 0))
            xt = [90, 98] if row == 0 else [88, 90, 92]; a.set_xticks(xt); a.set_xticklabels([f"{x}°E" for x in xt])
            a.contourf(E.gxc, E.YC, shm, levels=SHC, colors=SHG, zorder=1)
            E.line_regions(a, p, (0.5, 0.95), lws=(1.0, 0.55) if row else (0.8, 0.45), z=5)
            a.contour(E.gxc, E.YC, p, levels=[l99], colors="k", linewidths=0.7, linestyles=[(0, (1, 1.2))], zorder=5)
            arcs(a, 0.6)
            if row == 0: box(a, ZEXT)
            tag(a, lets[k])
    xc0 = L0 + 2 * (pw + gap) + 0.04; c = fig.add_axes([xc0, (bot + 0.05) / H, 0.93 - xc0, (h1 + h2 + mid - 0.12) / H])
    mk = ["o", "s", "^"]; fills = ["k", "0.5", "white"]; names = ["BTO only", "00:19:29 BFO only, as observed", "Holland transient bias added"]
    for i, D in enumerate(["D7", "D8", "D10"]):
        s = region_shares(D)
        c.plot([min(s) * 100, max(s) * 100], [i, i], color="0.6", lw=0.6, zorder=1)
        for r in range(3): c.plot(s[r] * 100, i + (r - 1) * 0.18, marker=mk[r], ms=4.5, mfc=fills[r], mec="k", mew=0.7, ls="none", zorder=3)
        c.text(1, i - 0.36, names[i], ha="left", va="bottom", fontsize=8)
    c.set_yticks([]); c.set_ylim(2.45, -0.75); c.set_xlim(0, 104); c.set_xticks([0, 25, 50, 75, 100]); c.set_xlabel("Share of impacts at\n4 GJ or more (%)", labelpad=2)
    for s in ("top", "right", "left"): c.spines[s].set_visible(False)
    tag(c, "c", x=0.0, y=0.995, bg=False)
    h = [Patch(fc=g, ec="0.4", lw=0.3, label=l) for g, l in zip(SHG, ["Under 25 %", "25 to 50 %", "50 to 75 %", "75 % or more"])]
    h2 = [Line2D([], [], color="k", lw=1.0, label="50 % of probability"), Line2D([], [], color="k", lw=0.55, label="95 % of probability"),
          Line2D([], [], color="k", lw=0.7, ls=(0, (1, 1.2)), label="99 % of probability")]
    h3 = [Line2D([], [], marker=m_, ls="none", ms=4.5, mfc=fl, mec="k", mew=0.7, label=l) for m_, fl, l in zip(mk, fills, ["Inside the 50 % region", "Between 50 % and 95 %", "Outside the 95 % region"])]
    fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.01, 0.0), fontsize=8, title="Share of impacts at 4 GJ or more", title_fontsize=8, alignment="left", handlelength=1.5)
    fig.legend(handles=h2, loc="lower left", bbox_to_anchor=(0.36, 0.0), fontsize=8, handlelength=2.0, title="Probability regions", title_fontsize=8, alignment="left")
    fig.legend(handles=h3, loc="lower left", bbox_to_anchor=(0.64, 0.0), fontsize=8, title="Graph (c): impacts", title_fontsize=8, alignment="left", handlelength=1.2)
    return fig


# ------------------------------------------------------------------ 4. new concept: map with marginal distributions
MSTY = {"D7": dict(color="0.55", lw=1.1), "D8": dict(color="k", lw=0.8, ls=(0, (1, 1.2))), "D10": dict(color="k", lw=1.2)}


def fig_joint(searched_on=True):
    E.rc(); Wd = E.WID; Lm = 0.43; mw = 3.50; mh = mw * hw(EXT); gap = 0.07; bw = Wd - Lm - mw - gap - 0.1; bot = 1.25; H = bot + mh + 0.06
    fig = plt.figure(figsize=(Wd, H)); fx = lambda x: x / Wd; fy = lambda y: y / H
    ax = fig.add_axes([fx(Lm), fy(bot), fx(mw), fy(mh)]); E.graticule(ax, EXT, 4, 1)
    ax.set_xticks([88, 92, 96, 100]); ax.set_xticklabels(["88°E", "92°E", "96°E", "100°E"])
    E.fill_regions(ax, P["D7"], (0.5, 0.95), greys=("0.55", "0.84"), edge="0.35")
    if searched_on: searched(ax)
    E.line_regions(ax, P["D10"], (0.5, 0.95), lws=(1.2, 0.6)); arcs(ax)
    E.label_on_arc(ax, -32.8, "7th arc", 7, offset=(0.8, -0.8), va="top"); E.label_on_arc(ax, -29.3, "6th arc", 6, offset=(-0.4, 0.35))
    tag(ax, "a", x=0.985, ha="right", bg=False)
    m = fig.add_axes([fx(Lm + mw + gap), fy(bot), fx(bw), fy(mh)]); m.set_ylim(ax.get_ylim())
    lb = np.arange(-41, -23.99, 0.1); yy = E.merc(0.5 * (lb[1:] + lb[:-1]))
    for D in ["D7", "D8", "D10"]:
        h, _ = np.histogram(Z["latitude_deg"], lb, weights=W[D]); m.plot(gaussian_filter(h / 0.1, 1.0), yy, **MSTY[D])
    m.set_yticks(ax.get_yticks()); m.tick_params(labelleft=False, length=2.5)
    for y in ax.get_yticks(): m.axhline(y, color="0.85", lw=0.35, zorder=0)
    m.set_xlim(0, 0.45); m.set_xticks([0, 0.2, 0.4]); m.set_xticklabels(["0", "0.2", "0.4"]); m.set_xlabel("Probability\nper degree", fontsize=8)
    for s in ("top", "right"): m.spines[s].set_visible(False)
    tag(m, "b", x=0.95, ha="right", bg=False)
    d = fig.add_axes([fx(Lm + 0.42), fy(bot + mh * 0.66), fx(1.55), fy(mh * 0.27)]); d.patch.set_facecolor("white"); d.set_zorder(20)
    db = np.arange(-60, 121, 2.0); dc = 0.5 * (db[1:] + db[:-1])
    for D in ["D7", "D8", "D10"]:
        h, _ = np.histogram(Z["arc_distance_nm_signed"], db, weights=W[D]); d.plot(dc, gaussian_filter(h / 2.0, 1.0) * 100, **MSTY[D])
    d.axvline(0, color="k", lw=0.4); d.axvspan(-25, 25, color="0.9", lw=0, zorder=0)
    d.set_xlim(-60, 120); d.set_xticks([-50, 0, 50, 100]); d.set_xlabel("Distance from the 7th arc (NM)", fontsize=8, labelpad=1)
    d.set_ylabel("% per NM", fontsize=8, labelpad=1); d.set_ylim(0, 6); d.set_yticks([0, 3, 6]); d.tick_params(length=2, pad=1)
    for s in ("top", "right"): d.spines[s].set_visible(False)
    tag(d, "c", x=0.97, y=0.97, ha="right", bg=False)
    h = [Patch(fc="0.55", ec="0.35", lw=0.3, label="BTO only, 50 %"), Patch(fc="0.84", ec="0.35", lw=0.3, label="BTO only, 95 %"),
         Line2D([], [], color="k", lw=1.2, label="Holland transient bias added, 50 %"), Line2D([], [], color="k", lw=0.6, label="Holland transient bias added, 95 %")]
    if searched_on: h.append(sa_patch())
    h2 = [Line2D([], [], label="BTO only", **MSTY["D7"]), Line2D([], [], label="00:19:29 BFO only, as observed", **MSTY["D8"]), Line2D([], [], label="Holland transient bias added", **MSTY["D10"])]
    fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.01, 0.0), fontsize=8, handlelength=1.8, title="Map (a)", title_fontsize=8, alignment="left")
    fig.legend(handles=h2, loc="lower left", bbox_to_anchor=(0.53, 0.0), fontsize=8, handlelength=2.0, title="Graphs (b) and (c)", title_fontsize=8, alignment="left")
    return fig


# ------------------------------------------------------------------ 5. new concept: corner plot of the impact posterior
VARS = [("Latitude (°S)", -Z["latitude_deg"], (24, 41), False, [25, 30, 35, 40]),
        ("Distance from the\n7th arc (NM)", Z["arc_distance_nm_signed"], (-80, 160), False, [-50, 0, 50, 100, 150]),
        ("Time from 00:19:29\nto impact (min)", np.clip(TMIN, 0.31, 60), (0.3, 40), True, [1, 3, 10, 30]),
        ("Impact kinetic\nenergy (GJ)", KE, (0.25, 14), True, [0.3, 1, 3, 10])]


def fig_corner():
    E.rc(); n = len(VARS); Wd = E.WID; fig, axs = plt.subplots(n, n, figsize=(Wd, Wd)); nb = 60
    T = lambda v, lg: np.log10(v) if lg else v
    k = 0
    for i in range(n):
        for j in range(n):
            a = axs[i, j]
            if j > i: a.axis("off"); continue
            li, vi, lim_i, lg_i, tk_i = VARS[i]; lj, vj, lim_j, lg_j, tk_j = VARS[j]
            if i == j:
                e = np.linspace(T(lim_i[0], lg_i), T(lim_i[1], lg_i), nb + 1); c = 0.5 * (e[1:] + e[:-1])
                for D in ("D7", "D10"):
                    h, _ = np.histogram(T(vi, lg_i), e, weights=W[D]); h = gaussian_filter(h, 1.0); h /= h.max()
                    if D == "D7": a.fill_between(c, 0, h, color="0.82", lw=0); a.plot(c, h, color="0.45", lw=0.6)
                    else: a.plot(c, h, color="k", lw=1.1)
                a.set_ylim(0, 1.08); a.set_yticks([])
                for s in ("top", "right", "left"): a.spines[s].set_visible(False)
            else:
                ex = np.linspace(T(lim_j[0], lg_j), T(lim_j[1], lg_j), nb + 1); ey = np.linspace(T(lim_i[0], lg_i), T(lim_i[1], lg_i), nb + 1)
                cx, cy = 0.5 * (ex[1:] + ex[:-1]), 0.5 * (ey[1:] + ey[:-1])
                for D in ("D7", "D10"):
                    h, _, _ = np.histogram2d(T(vj, lg_j), T(vi, lg_i), bins=[ex, ey], weights=W[D]); h = gaussian_filter(h.T, 1.2); h /= h.sum()
                    lv = E.hpd_levels(h, (0.5, 0.95))
                    if D == "D7": a.contourf(cx, cy, h, levels=[lv[1], lv[0], h.max() * 1.01], colors=["0.84", "0.6"])
                    else: a.contour(cx, cy, h, levels=sorted(lv), colors="k", linewidths=[0.6, 1.1])
                a.set_ylim(T(lim_i[0], lg_i), T(lim_i[1], lg_i)); a.set_yticks([T(t, lg_i) for t in tk_i])
                a.set_yticklabels([f"{t:g}" for t in tk_i] if j == 0 else [])
                for s in ("top", "right"): a.spines[s].set_visible(False)
            a.set_xlim(T(lim_j[0], lg_j), T(lim_j[1], lg_j)); a.set_xticks([T(t, lg_j) for t in tk_j])
            a.set_xticklabels([f"{t:g}" for t in tk_j] if i == n - 1 else [])
            if i == n - 1: a.set_xlabel(lj, fontsize=8)
            if j == 0 and i > 0: a.set_ylabel(li, fontsize=8)
            a.tick_params(length=2.5, pad=1.5)
            a.text(0.0, 1.02, f"({'abcdefghij'[k]})", transform=a.transAxes, ha="left", va="bottom", fontsize=8); k += 1
    h = [Patch(fc="0.6", label="BTO only, 50 %"), Patch(fc="0.84", label="BTO only, 95 %"),
         Line2D([], [], color="k", lw=1.1, label="Holland transient bias added, 50 %"), Line2D([], [], color="k", lw=0.6, label="Holland transient bias added, 95 %")]
    fig.legend(handles=h, loc="upper right", bbox_to_anchor=(0.99, 0.97), fontsize=8, handlelength=1.8)
    fig.subplots_adjust(left=0.13, right=0.99, bottom=0.1, top=0.97, wspace=0.14, hspace=0.24)
    return fig


# ------------------------------------------------------------------ saving (JON set + working version)
def _compose(png, top, bottom, out, dpi, botsize=8, bold=False):
    im = Image.open(png).convert("L"); w, h = im.size; wi, hi = w / 600, h / 600; Wd = max(wi, E.WID) + 0.1
    cw = lambda fs: int((Wd - 0.15) * 72 / (0.50 * fs))
    tl = textwrap.wrap(top, cw(9) - 6) if top else []; bl = textwrap.wrap(bottom, cw(botsize)) if bottom else []
    ht = (0.17 * len(tl) + 0.12) if tl else 0.0; hb = (botsize / 72 * 1.25 * len(bl) + 0.2) if bl else 0.05; Ht = hi + ht + hb
    pf = plt.figure(figsize=(Wd, Ht)); ax = pf.add_axes([0.05 / Wd, hb / Ht, wi / Wd, hi / Ht]); ax.imshow(im, cmap="gray", vmin=0, vmax=255); ax.axis("off")
    if tl: pf.text(0.05 / Wd, 1 - 0.05 / Ht, "\n".join(tl), va="top", ha="left", fontsize=9, family="serif", weight="bold" if bold else "normal")
    if bl: pf.text(0.05 / Wd, (hb - 0.08) / Ht, "\n".join(bl).replace("x_Impact", r"$x_{\mathrm{Impact}}$"), va="top", ha="left", fontsize=botsize, family="serif")
    pf.savefig(out, dpi=dpi); plt.close(pf)


def save_set(build, name, caption, title, footnote):
    fig = build(); fig.savefig(f"{OUT}/{name}-word.png", dpi=600, bbox_inches="tight", pad_inches=0.03)
    fig.savefig(f"{OUT}/{name}.pdf", bbox_inches="tight", pad_inches=0.03); plt.close(fig)
    open(f"{OUT}/{name}-caption.txt", "w").write(caption.strip() + "\n")
    _compose(f"{OUT}/{name}-word.png", None, caption, f"{OUT}/{name}-proof.png", 250)
    _compose(f"{OUT}/{name}-word.png", title, footnote, f"{OUT}/{name}-working.png", 200, botsize=6, bold=True)


# ------------------------------------------------------------------ captions and footnotes
ESS = {D: float(TDF.loc[D, "ess"]) for D in CODES}
COMMON = ("Source: final end-of-flight run, 7 November 2026 (data/eof-handoff-davey-fuel.npz, 501,102 weighted impact rows, 16 seeds); Davey model with the fuel model, "
          "conditional on engine power at 00:11. Each treatment of the 00:19 data re-weights the same simulated paths by the likelihood of the data it uses. "
          "BTO: both 00:19 BTOs (00:19:29 R600 18,400 µs, sd 63 µs; 00:19:37 R1200 18,380 µs with the empirical offset applied, sd 43 µs). "
          "BFO: 182 Hz (00:19:29, R600) and −2 Hz (00:19:37, R1200), sd 4.32 Hz. Holland transient bias added: 17–136 Hz on 00:19:29 and 17–130 Hz on 00:19:37. "
          "Outer limit of the bias treatments: union of the 95 % regions of Holland's bias (17 Hz floor and zero floor) and of the bias on the 00:19:37 BFO only (17 Hz floor and zero floor). "
          "BTO and both BFOs as observed is not mapped: 508 effective samples, below the 1,000 needed for a map. "
          f"Effective samples: BTO only {ESS['D7']:,.0f}; 00:19:29 BFO only {ESS['D8']:,.0f}; Holland {ESS['D10']:,.0f}. Log-on cause prior 0.75 fuel exhaustion. ")
REGION = ("Probability regions: smallest regions holding the stated share; weighted histogram in a frame aligned with the 7th arc (5 NM along, 2 NM across), smoothed with a Gaussian kernel "
          "of 12 NM along and 3 NM across the arc, sampled to a 0.025° grid. Mercator projection. ")
SEARCH = ("Previously searched area: union of the ATSB Phase 2, Ocean Infinity 2018 and Ocean Infinity 2025–26 coverage (OI 2025–26 inferred from vessel tracks), drawn at half coverage; "
          "gaps and strips narrower than about 3 km are not drawn. Coverage only, with no detection probability. ")
ENERGY = ("Impact kinetic energy = 1/2 m (ground speed² + vertical speed²), mass = zero-fuel mass 174,196 kg plus fuel left. Energy is a sensitivity result: the no-pilot dives reach about "
          "Mach 1.0, and the median under both BFOs (about 9.2 GJ) is at or above the top of the Boeing 777 simulation range (6.4–9.0 GJ). ")
POWER = ("Peak impact power: peak rate at which kinetic energy is transferred to the water (ocean-settling method 1, file data/settling-energy-transfer-davey-fuel.npz, 8 Nov 2026, not yet "
         "independently checked); a mechanical rate, not radiated acoustic power. The October charts called this quantity 'peak radiated power'. ")

CAP = {}
CAP["ov"] = ("Impact position x_Impact, Davey model with the fuel model, for two treatments of the 00:19 satellite data: (a) whole region; (b) the area of highest probability (box in a). "
             "Light and dark grey: smallest regions holding {q1} and {q0} of the probability with the BTO values only. Thin and heavy black lines: the same regions with both BFOs and "
             "Holland's transient bias added. Dashed line: outer limit of the {q1} regions of all treatments that add a start-up bias to the BFO.{r6} Solid curve: 7th arc at sea level; "
             "dash-dot curve: 6th arc at 35,000 ft.{sa} Mercator projection.")
CAP["mu"] = ("Impact position x_Impact, Davey model with the fuel model, for three treatments of the 00:19 satellite data: (a, d) BTO values only; (b, e) BTO values and the 00:19:29 BFO as "
             "observed; (c, f) BTO values and both BFOs with Holland's transient bias added. The upper row shows the whole region; the lower row shows the box marked above. "
             "Shading: smallest regions holding {levels} of the probability. Dashed line in (c, f): outer limit of the {q1} regions of all treatments that add a start-up bias. "
             "Solid curve: 7th arc at sea level; dash-dot curve: 6th arc at 35,000 ft.{sa}")
CAP["mu2"] = ("Impact position x_Impact, Davey model with the fuel model: (a, c) BTO values only; (b, d) BTO values and both BFOs with Holland's transient bias added. The upper row shows "
              "the whole region; the lower row shows the box marked above. Shading: smallest regions holding 50 % and 95 % of the probability. Dashed line in (b, d): outer limit of the "
              "95 % regions of all treatments that add a start-up bias. Solid curve: 7th arc; dash-dot curve: 6th arc.{sa}")
CAP["en"] = ("Simulated impacts by kinetic energy, Davey model with the fuel model: (a, d) BTO values only; (b, e) BTO values and both BFOs with Holland's transient bias added; (d, e) show "
             "the box marked in (a, b). Each dot is one of 3,000 impacts drawn in proportion to probability: light grey under 1 GJ, mid-grey 1 to 4 GJ, black 4 GJ or more. Black lines "
             "with a white edge enclose 50 % and 95 % of the probability. (c) Cumulative distribution of impact kinetic energy; the hatched band is the range of the Boeing 777 "
             "simulations. (f) Cumulative distribution of peak impact power. In (c, f): grey line, BTO only; dotted line, 00:19:29 BFO only, as observed; heavy line, Holland's bias.")
CAP["pw"] = ("Simulated impacts by peak impact power, Davey model with the fuel model: (a, d) BTO values only; (b, e) BTO values and both BFOs with Holland's transient bias added; (d, e) show "
             "the box marked in (a, b). Each dot is one of 3,000 impacts drawn in proportion to probability. Classes are set on the BTO-only distribution: light grey, lower half; "
             "mid-grey, 50th to 90th percentile; black, top tenth. Black lines with a white edge enclose 50 % and 95 % of the probability. (c) and (f) as in the energy figure.")
CAP["sh"] = ("Where the high-energy impacts lie, Davey model with the fuel model: (a, d) BTO values only; (b, e) BTO values and both BFOs with Holland's transient bias added; (d, e) show the "
             "box marked in (a, b). Shading gives the share of impacts with a kinetic energy of 4 GJ or more at each place, inside the 99 % probability region. Heavy, thin and dotted "
             "lines enclose 50 %, 95 % and 99 % of the probability. (c) Share of impacts at 4 GJ or more inside the 50 % region (circles), between 50 % and 95 % (squares) and outside "
             "the 95 % region (triangles); the grey line joins the three shares of each treatment.")
CAP["jo"] = ("Impact position x_Impact and its distributions, Davey model with the fuel model. (a) Map: light and dark grey, regions holding 95 % and 50 % of the probability with the BTO "
             "values only; thin and heavy lines, the same regions with both BFOs and Holland's transient bias added; solid curve, 7th arc; dash-dot curve, 6th arc.{sa} (b) Probability "
             "per degree of latitude, on the latitude scale of (a). (c) Probability per nautical mile of distance from the 7th arc (positive to the south-east); the shaded band is within "
             "25 NM. In (b) and (c): grey line, BTO only; dotted line, 00:19:29 BFO only, as observed; heavy line, Holland's bias.")
CAP["co"] = ("Joint distributions of four impact quantities, Davey model with the fuel model: latitude, distance from the 7th arc (positive to the south-east), time from 00:19:29 to impact, "
             "and impact kinetic energy. Panels (a), (c), (f) and (j) show each quantity alone, scaled to its peak; the other panels show pairs. Grey shading: regions holding 95 % "
             "and 50 % of the probability with the BTO values only. Black lines: the same regions with both BFOs and Holland's transient bias added. Time and energy use logarithmic scales.")


def _sa(on): return " Hatching: previously searched area (ATSB Phase 2, Ocean Infinity 2018 and 2025–26)." if on else ""


def figure_list():
    L = []
    for nm, sa, r6, sh in [("eofn-01-overlay-searched", True, False, (0.5, 0.95)), ("eofn-02-overlay", False, False, (0.5, 0.95)),
                           ("eofn-03-overlay-searched-r600", True, True, (0.5, 0.95)), ("eofn-04-overlay-50-99", False, False, (0.5, 0.99))]:
        q0, q1 = pct(sh[0]), pct(sh[1])
        cap = CAP["ov"].format(q0=q0, q1=q1, sa=_sa(sa), r6=(f" Dotted line: the {q1} region with the 00:19:29 BFO only, as observed." if r6 else ""))
        L.append((nm, (lambda sa=sa, r6=r6, sh=sh: fig_overlay(sa, r6, sh)), cap,
                  f"Impact position: BTO only against Holland's transient bias, {q0} and {q1} regions" + (", with the previously searched area" if sa else ""),
                  COMMON.replace("union of the 95 % regions", f"union of the {q1} regions") + REGION + (SEARCH if sa else "")))
    L.append(("eofn-05-multiples-searched", lambda: fig_multiples(("D7", "D8", "D10"), True, (0.5, 0.95), ("0.5", "0.84")),
              CAP["mu"].format(levels="50 % and 95 %", q1="95 %", sa=_sa(True)), "Impact position: three treatments of the 00:19 data, whole region and close view",
              COMMON + REGION + SEARCH))
    L.append(("eofn-06-multiples-50-90-99", lambda: fig_multiples(("D7", "D8", "D10"), False, (0.5, 0.9, 0.99), ("0.4", "0.65", "0.87")),
              CAP["mu"].format(levels="50 %, 90 % and 99 %", q1="99 %", sa=""), "Impact position: three treatments, 50/90/99 % regions, no search overlay",
              COMMON.replace("union of the 95 % regions", "union of the 99 % regions") + REGION))
    L.append(("eofn-07-multiples-two", lambda: fig_multiples(("D7", "D10"), True, (0.5, 0.95), ("0.5", "0.84")),
              CAP["mu2"].format(sa=_sa(True)), "Impact position: widest and narrowest case, whole region and close view", COMMON + REGION + SEARCH))
    L.append(("eofn-08-energy-dots", lambda: fig_energy_maps("energy"), CAP["en"], "Impact kinetic energy: high-energy impacts fill the 50 % region next to the arc",
              COMMON + REGION + ENERGY + POWER + "Dots: systematic resample of 3,000 rows per treatment from the hand-off weights."))
    L.append(("eofn-09-power-dots", lambda: fig_energy_maps("power"), CAP["pw"], "Peak impact power: the top tenth concentrates in the 50 % region next to the arc",
              COMMON + REGION + ENERGY + POWER + "Classes: weighted 50th and 90th percentiles of peak impact power under BTO only."))
    L.append(("eofn-10-energy-share", fig_energy_share, CAP["sh"], "Share of high-energy impacts by place and by probability region",
              COMMON + REGION + ENERGY + "Share field: probability-weighted share of rows with energy ≥ 4 GJ, both smoothed with the same arc-aligned kernel."))
    L.append(("eofn-11-map-marginals", lambda: fig_joint(True), CAP["jo"].format(sa=_sa(True)), "Impact position with its latitude and distance-from-arc distributions",
              COMMON + REGION + SEARCH + "Graphs (b) and (c): weighted histograms (0.1 deg; 2 NM) smoothed with a one-bin Gaussian kernel."))
    L.append(("eofn-12-corner", fig_corner, CAP["co"], "Joint distributions of impact latitude, distance from the arc, time to impact and energy",
              COMMON + ENERGY + "Pair panels: weighted 60 × 60 histograms smoothed with a 1.2-bin Gaussian kernel; time below 0.3 min is placed at 0.3 min (2.7 % of the probability with Holland's bias)."))
    return L


# ------------------------------------------------------------------ summary metrics
def metrics():
    rows = []
    A_s = None
    for D in CODES:
        w = W[D]; p = P[D]; ad = np.abs(Z["arc_distance_nm_signed"]); la = Z["latitude_deg"]
        rows.append({"code": D, "treatment": E.TREATMENTS[D], "effective_samples_run": ESS[D],
                     "ln_B_vs_both_BFOs_as_observed": TDF.loc[D, "ln Z relative to first treatment of the same group"],
                     "latitude_q05": E.wquantile(la, w, 0.05), "latitude_q50": E.wquantile(la, w, 0.5), "latitude_q95": E.wquantile(la, w, 0.95),
                     "area50_km2": E.hpd_area_km2(p, 0.5), "area90_km2": E.hpd_area_km2(p, 0.9), "area95_km2": E.hpd_area_km2(p, 0.95), "area99_km2": E.hpd_area_km2(p, 0.99),
                     "abs_distance_q50_nm": E.wquantile(ad, w, 0.5), "abs_distance_q95_nm": E.wquantile(ad, w, 0.95), "within_25nm": float(w[ad <= 25].sum()),
                     "inside_previously_searched_area": float((w * E.coverage_at(la, Z["longitude_deg"])).sum()),
                     "minutes_to_impact_q50": E.wquantile(TMIN, w, 0.5), "energy_gj_q05": E.wquantile(KE, w, 0.05), "energy_gj_q50": E.wquantile(KE, w, 0.5),
                     "energy_gj_q95": E.wquantile(KE, w, 0.95), "share_energy_ge_4gj": float(w[KE >= 4].sum()),
                     "peak_power_gw_q50": E.wquantile(PP, w, 0.5), "no_pilot_share": float(w[Z["family_code"] == 1].sum())})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    only = sys.argv[1:]
    for name, build, cap, title, foot in figure_list():
        if only and not any(o in name for o in only): continue
        save_set(build, name, cap, title, foot); print("saved", name, flush=True)
    if not only:
        M = metrics(); M.to_csv(f"{RES}/eof-results-metrics-davey-fuel.csv", index=False)
        sh = {D: region_shares(D) for D in ["D7", "D8", "D10"]}
        json.dump(sh, open(f"{RES}/eof-high-energy-share-by-region.json", "w"), indent=1)
        print(M[["code", "area90_km2", "within_25nm", "inside_previously_searched_area"]].round(3).to_string())
