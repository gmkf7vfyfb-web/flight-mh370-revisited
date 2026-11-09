"""Candidate Journal of Navigation figures: 00:19 descent-rate comparison (MH370 end of flight).

Self-contained: reads only the files in this package (see README.md) and writes, per candidate,
<name>-word.png (600 dpi), <name>.pdf, <name>-proof.png (caption beneath), <name>-caption.txt and
<name>-working.png (title + method footnote), plus plotted-numbers.csv and band-polygons.csv.

Usage:  python descent0019_charts.py [package_dir] [output_dir]
Requires: numpy, pandas, scipy, matplotlib, pillow.
"""
import os, sys, textwrap
import numpy as np, pandas as pd
from scipy.ndimage import uniform_filter1d, gaussian_filter
from scipy.signal import argrelextrema
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Patch, Polygon
from matplotlib.lines import Line2D
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from PIL import Image

PKG = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PKG, "figures")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------------------- constants
MM = 1 / 25.4
G_FT = 32.174                       # ft/s^2
TA = (4350.0, 14860.0)              # implied rates, 00:19 BFOs as observed (00:19:29, 00:19:37), ft/min
TH = (8590.0, 18830.0)              # implied rates, Holland transient bias added (published point)
WIN = (67.0, 198.0)                 # log-on window, s after power loss (5-95 % of first estimate)
SLOPE_HALF = 500.0                  # B1: first-instant window half-width, ft/min
LW_DATA, LW_THICK, LW_REF = 1.0, 1.2, 0.5
G15, G35 = "0.85", "0.65"           # tints 15 % and 35 %

def rc():
    matplotlib.rcdefaults()
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "Times", "STIXGeneral"], "mathtext.fontset": "stix",
        "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2.5,
        "ytick.major.size": 2.5, "xtick.minor.width": 0.4, "ytick.minor.width": 0.4, "xtick.minor.size": 1.5,
        "ytick.minor.size": 1.5, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "black",
        "text.color": "black", "axes.labelcolor": "black", "xtick.color": "black", "ytick.color": "black",
        "legend.frameon": False, "legend.handlelength": 1.8, "legend.handleheight": 0.9, "legend.labelspacing": 0.35,
        "legend.borderaxespad": 0.0, "legend.borderpad": 0.0, "legend.handletextpad": 0.5, "legend.columnspacing": 1.2,
        "hatch.linewidth": 0.5, "lines.solid_capstyle": "butt", "pdf.fonttype": 42, "savefig.dpi": 600,
        "axes.labelpad": 3.0})

NB = "\u00a0"
def nb(s): return s.replace(" ", NB)
def text_width_mm(s, size=8, bold=False):
    fp = FontProperties(family="serif", size=size, weight="bold" if bold else "normal")
    return max(TextPath((0, 0), ln, prop=fp).get_extents().width for ln in s.split("\n")) / 72 * 25.4

def wrap_mm(s, width_mm, size=8, bold=False):
    words, lines, cur = [w for w in s.replace("\n", " ").split(" ") if w], [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_width_mm(t, size, bold) <= width_mm: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return "\n".join(lines)

def ax_mm(fig, x, y, w, h):
    W, H = fig.get_size_inches() / MM
    return fig.add_axes([x / W, y / H, w / W, h / H])

def letter(ax, s, x=0.0, y=1.0, dx=-0.0, dy=0.0, **kw):
    ax.text(x, y, f"({s})", transform=ax.transAxes, ha="left", va="bottom", fontsize=8, **kw)

# ----------------------------------------------------------------------------- data
prof = pd.read_csv(f"{PKG}/descent-rate-profiles.csv")
PROF = {c: (g.time_s.values, g.descent_rate_fpm.values, g.group.iloc[0]) for c, g in prof.groupby("case", sort=False)}
steady = pd.read_csv(f"{PKG}/steady-descent-cases.csv")
ev = pd.read_csv(f"{PKG}/eof-0019-bfo-evidence.csv")
ess = pd.read_csv(f"{PKG}/eof-treatments-ess.csv")
Z = np.load(f"{PKG}/posterior-descent-pairs-davey-fuel.npz")
R29, R37 = Z["rate_001929_fpm"].astype(float), Z["rate_001937_fpm"].astype(float)
WT = {d: Z[f"w_{d}"] for d in ["D7", "D8", "D9", "D10", "D11"]}

GROUPS = {"P": ["EgyptAir 990", "Atlas Air 3591", "SilkAir 185"],
          "R": ["TWA 841", "Adam Air 574", "AirAsia 8501", "China Eastern 5735", "Lauda Air 004"],
          "A": [f"Boeing 777 simulation {r}" for r in (3, 4, 6, 10)],
          "N": [f"Boeing 777 simulation {r}" for r in (1, 2, 5, 7, 8, 9)]}

# ---- build-up limbs and 8-s pairs (same rules as the chosen chart, lineage 1ffdc3eb)
def limbs(tt, dd, min_gain=1500):
    g = np.arange(tt[0], tt[-1], 0.25); v = np.interp(g, tt, dd)
    k = 9; vs = np.convolve(np.pad(v, (k // 2, k // 2), mode="edge"), np.ones(k) / k, mode="valid")
    mins = list(argrelextrema(vs, np.less_equal, order=12)[0]); maxs = list(argrelextrema(vs, np.greater_equal, order=12)[0])
    out = []
    for m in sorted(set([0] + mins)):
        nxt = [x for x in maxs + [len(v) - 1] if x > m]
        if not nxt: continue
        nm = [x for x in mins if x > nxt[0]]; end = nm[0] if nm else len(v) - 1
        M_ = m + int(np.argmax(v[m:end + 1]))
        if v[M_] - v[m] >= min_gain and (not out or out[-1][1] <= m): out.append((m, M_))
    return [(g[a:b + 1], v[a:b + 1]) for a, b in out]
LIMB = {k: limbs(t, d) for k, (t, d, _) in PROF.items()}

def pairs(key):
    tt, dd, _ = PROF[key]; out = []
    for lt, lv in LIMB[key]:
        if lt[-1] - lt[0] < 8: continue
        t1 = np.arange(lt[0], lt[-1] - 8 + 1e-9, 0.25)
        v1 = np.interp(t1, tt, dd); v2 = np.interp(t1 + 8, tt, dd); m = v1 >= 0
        if m.sum() > 1: out.append((t1[m], v1[m], v2[m]))
    return out

def allpairs(keys, window=None):
    T, X, Y = [], [], []
    for k in keys:
        for t1, v1, v2 in pairs(k):
            m = np.ones(len(t1), bool) if window is None else ((t1 >= window[0]) & (t1 <= window[1])) if window else ~((t1 >= WIN[0]) & (t1 <= WIN[1]))
            T.append(t1[m]); X.append(v1[m]); Y.append(v2[m])
    return np.concatenate(T), np.concatenate(X), np.concatenate(Y)

def band(X, Y, dx=0.75, xmax=55):
    e = np.arange(0, xmax + dx, dx); c = (e[:-1] + e[1:]) / 2; lo = np.full(len(c), np.nan); hi = lo.copy()
    for i in range(len(c)):
        m = (X >= e[i]) & (X < e[i + 1])
        if m.sum(): lo[i], hi[i] = Y[m].min(), Y[m].max()
    idx = np.flatnonzero(np.isfinite(lo)); runs = np.split(idx, np.flatnonzero(np.diff(idx) > 2) + 1)
    return [(c[r], uniform_filter1d(lo[r], 3), uniform_filter1d(hi[r], 3)) for r in runs if len(r) >= 2]

acc_g = lambda v1, v2: (v2 - v1) / (8 * 60 * G_FT)
BANDS, ABANDS = {}, {}
for g, keys in GROUPS.items():
    _, X, Y = allpairs(keys); BANDS[g] = band(X / 1e3, Y / 1e3); ABANDS[g] = band(X / 1e3, acc_g(X, Y))
_, Xw, Yw = allpairs(GROUPS["A"] + GROUPS["N"], window=WIN)
BANDS["W"] = band(Xw / 1e3, Yw / 1e3); ABANDS["W"] = band(Xw / 1e3, acc_g(Xw, Yw))

def inside(g, v1k, v2k):
    res = np.zeros(np.shape(v1k), bool)
    for c_, lo_, hi_ in BANDS[g]:
        for j in range(len(c_)): res |= (np.abs(v1k - c_[j]) <= 0.375) & (v2k >= lo_[j]) & (v2k <= hi_[j])
    return res

# ---- posterior summaries (Davey model with fuel)
def wq(x, w, q):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]; return np.interp(q, c, x[o])
Q = {}
for d, w in WT.items():
    Q[d] = dict(r29=wq(R29, w, [.05, .5, .95]), r37=wq(R37, w, [.05, .5, .95]), acc=wq(acc_g(R29, R37), w, [.05, .5, .95]))
    k = w > w.max() * 1e-9; a, b, ww = R29[k] / 1e3, R37[k] / 1e3, w[k] / w[k].sum()
    Q[d]["in_real"] = float(ww[inside("P", a, b) | inside("R", a, b)].sum()); Q[d]["in_window"] = float(ww[inside("W", a, b)].sum())

def lnb(route, code):
    s = ev[(ev["route model"] == route) & (ev.code == code)]["ln Z relative to first treatment of the same group"].iloc[0]
    if s == "reference": return 0.0, 0.0, 0.0
    v = s.replace("(", "").replace(")", "").replace(" to ", " ").split(); return float(v[0]), float(v[1]), float(v[2])
PPROB = {r: ev[ev["route model"] == r].set_index("code")["posterior probability, equal prior over D9 D10 D11"] for r in ["Davey model + fuel", "waypoints"]}
ESS = {(r["route family"], r.code): (r.ess, bool(r["provisional (no-pilot ESS < 500)"])) for _, r in ess.iterrows()}

# ---- timings-only (D7) predicted density of descending paths (rate at 00:19:37 > 3,000 ft/min)
def hdr_grid(sig=5.0, dx=0.25):
    m = R37 > 3000; a, b, w = R29[m] / 1e3, R37[m] / 1e3, WT["D7"][m]
    xe = np.arange(0, 60 + dx, dx); ye = np.arange(-5, 35 + dx, dx)
    H, _, _ = np.histogram2d(b, a, bins=[xe, ye], weights=w); H = gaussian_filter(H / H.sum(), sig)
    f = np.sort(H.ravel())[::-1]; cs = np.cumsum(f)
    return (xe[:-1] + xe[1:]) / 2, (ye[:-1] + ye[1:]) / 2, H, {p: f[np.searchsorted(cs, p * cs[-1])] for p in (0.5, 0.9)}, float(w.sum())
HX, HY, HD, HLEV, D7_DESC = hdr_grid()

# ---- conditional cut: rate 8 s after the build-up passes a threshold
def after_cross(key, X):
    tt, dd, _ = PROF[key]; out = []
    for lt, lv in LIMB[key]:
        if lv[0] < X <= lv.max():
            j = np.flatnonzero(lv >= X)[0]
            tc = lt[j - 1] + (X - lv[j - 1]) * (lt[j] - lt[j - 1]) / (lv[j] - lv[j - 1]) if j > 0 else lt[0]
            out.append((tc, float(np.interp(tc + 8, tt, dd))))
    return out
CUT = pd.DataFrame([dict(threshold_fpm=X, case=k, group=PROF[k][2], crossing_time_s=round(tc, 2), rate_8s_later_fpm=round(v),
                         in_logon_window=(k.startswith("Boeing") and WIN[0] <= tc <= WIN[1]))
                    for X in (TA[0], TH[0]) for k in GROUPS["P"] + GROUPS["R"] + GROUPS["A"] + GROUPS["N"] for tc, v in after_cross(k, X)])

# ----------------------------------------------------------------------------- styles and labels
STY = {"A": dict(facecolor=G35, edgecolor="none", linewidth=0, hatch=None, z=1),
       "N": dict(facecolor=G15, edgecolor="0.45", linewidth=0, hatch="....", z=1.5),
       "P": dict(facecolor="none", edgecolor="k", linewidth=LW_DATA, hatch="////", linestyle="-", z=3),
       "R": dict(facecolor="none", edgecolor="0.3", linewidth=LW_DATA, hatch="\\\\\\\\", linestyle=(0, (3.5, 1.5)), z=3)}
GLAB = {"P": "Push-overs: " + ", ".join(nb(x) for x in ["EgyptAir 990", "Atlas Air 3591", "SilkAir 185"]),
        "R": "Roll-offs/upsets: " + ", ".join(nb(x) for x in ["TWA 841", "Adam Air 574", "AirAsia 8501", "China Eastern 5735", "Lauda Air 004"]),
        "A": "Boeing 777 simulations, alternate electrical configuration " + nb("(simulations 3, 4, 6, 10)"),
        "N": "Boeing 777 simulations, normal electrical configuration " + nb("(simulations 1, 2, 5, 7, 8, 9)"),
        "S": "Steady descents and stalls " + nb("(9 accident cases)"),
        "W": "Boeing 777 build-ups inside the log-on window"}
TLAB = {"o": "00:19 BFOs as observed",
        "s": "00:19 BFOs, Holland transient bias added",
        "^": "Holland transient bias added to the " + nb("00:19:37 BFO only"),
        "v": "00:19:29 BFO only, as observed " + nb("(R600)")}
TCODE = {"o": "D9", "s": "D10", "^": "D11", "v": "D8"}
def patch(g):
    s = {k: v for k, v in STY[g].items() if k != "z"}; return Patch(**s)
def mk_handle(m): return Line2D([], [], ls="none", marker=m, ms=4.5, mfc="white", mec="k", mew=0.8)
def steady_handle(): return Line2D([], [], color="0.35", lw=LW_THICK, marker="D", ms=3.2)
HALO = [pe.withStroke(linewidth=2.4, foreground="white")]

def draw_bands(ax, groups="ANPR"):
    for g in groups:
        s = STY[g]
        for c_, lo_, hi_ in BANDS[g]:
            ax.fill_betweenx(c_, lo_, hi_, **{k: v for k, v in s.items() if k != "z"}, zorder=s["z"])

def draw_steady(ax, accel=False):
    for _, r in steady.iterrows():
        lo, hi = r.steady_rate_low_fpm / 1e3, r.steady_rate_high_fpm / 1e3
        y = (0.0, 0.0) if accel else (lo, hi)
        if hi - lo > 0.05: ax.plot([lo, hi], y, color="0.35", lw=LW_THICK, solid_capstyle="round", zorder=2)
        ax.plot([lo] if hi - lo <= 0.05 else [], [y[0]] if hi - lo <= 0.05 else [], ls="none", marker="D", color="0.35", ms=3.2, zorder=2)

def rng(d):  # (x=00:19:37, y=00:19:29) centre, x-range, y-range in 1000 ft/min
    q = Q[d]; return q["r37"] / 1e3, q["r29"] / 1e3

def draw_treatments(ax, which="os^v"):
    for m in which:
        x, y = rng(TCODE[m])
        cx, cy = (TA[1] / 1e3, TA[0] / 1e3) if m == "o" else (TH[1] / 1e3, TH[0] / 1e3) if m == "s" else (x[1], y[1])
        ax.plot([x[0], x[2]], [cy, cy], color="k", lw=0.8, zorder=8); ax.plot([cx, cx], [y[0], y[2]], color="k", lw=0.8, zorder=8)
        ax.plot(cx, cy, ls="none", marker=m, ms=4.5, mfc="white", mec="k", mew=0.8, zorder=9)

def draw_main(ax, which="os^v"):
    draw_bands(ax); draw_steady(ax)
    ax.plot([0, 60], [0, 60], color="0.35", lw=LW_REF, ls=(0, (1, 1.5)), zorder=0.5)
    draw_treatments(ax, which)
    ax.set_xlim(0, 55); ax.set_ylim(0, 30); ax.set_xticks(range(0, 56, 10)); ax.set_yticks(range(0, 31, 5))
    ax.set_xlabel("Descent rate 8 s later (1000 ft/min)"); ax.set_ylabel("Descent rate at the first instant (1000 ft/min)")

def legend_block(fig, x_mm, y_mm, entries, width_mm, ncol=1, col_mm=None):
    """entries: list of (handle, label). Labels wrapped to the column width. Returns the legend."""
    W, H = fig.get_size_inches() / MM
    cw = col_mm or width_mm
    lab = [wrap_mm(l, cw - 7.5) for _, l in entries]
    return fig.legend([h for h, _ in entries], lab, loc="upper left", bbox_to_anchor=(x_mm / W, y_mm / H), ncol=ncol,
                      handlelength=1.8, columnspacing=1.0)

def groups_and_treatments_legend(fig, y_mm, which="os^v", extra=()):
    left = [(patch("P"), GLAB["P"]), (patch("R"), GLAB["R"]), (patch("A"), GLAB["A"]), (patch("N"), GLAB["N"]), (steady_handle(), GLAB["S"])]
    right = [(mk_handle(m), TLAB[m]) for m in which] + list(extra)
    legend_block(fig, 1.0, y_mm, left, 63)
    legend_block(fig, 66.0, y_mm, right, 60)

# ----------------------------------------------------------------------------- shared caption text
CAP_MAIN = ("(a) Descent rate at a first instant and 8 s later during dive build-ups; each area covers one group of dives, "
            "and the dotted line is a steady descent. ")
CAP_MK = ("Symbols mark the 00:19:29 and 00:19:37 rates implied by each 00:19 BFO treatment; bars are 5–95 % posterior ranges "
          "(Davey model with fuel), centred on the published point for Holland transient bias. ")
CAP_R = "R600 is the 600 bit/s channel of the 00:19:29 burst. "
WF = ("Source: final end-of-flight run, 7 November 2026, Davey model with fuel (waypoint routes only where marked). Treatments: 00:19 BFOs as observed (D9); "
      "Holland transient bias added to both, 17 Hz floor (D10); bias added to the 00:19:37 BFO only, 17 Hz floor (D11); 00:19:29 BFO only (D8); both 00:19 BTOs, no BFO (D7). "
      "Rule: ln Z is compared only among treatments with the same data (both 00:19 BTOs and both BFOs: D9, D10, D11); D8 and D7 are never compared by ln Z. "
      "All |ln B| < 0.5 nat: weak (Kass and Raftery: below 1 nat is not worth more than a bare mention). PROVISIONAL: D9 has 508 effective samples (156 no-pilot); "
      "D11 has 489 no-pilot. Areas: minimum-maximum envelopes of 8-s pairs taken every 0.25 s on rising limbs that gain at least 1,500 ft/min, in 750 ft/min bins, "
      "smoothed over three bins. Atlas Air 3591, SilkAir 185, TWA 841 and Lauda Air 004 are constant-acceleration estimates from report values (TWA 841 and Lauda Air 004 "
      "lower bounds). Boeing areas include build-ups at any time after power loss; log-on window 67–198 s after power loss (5–95 % of the first estimate). "
      "Posterior ranges are weighted 5–95 % quantiles of the final-run descent rates. Steady descents and stalls: Germanwings 9525, LAM 470, EgyptAir 804, "
      "Alaska Airlines 261, Helios 522, Air France 447, Pulkovo 612, West Caribbean 708, Turkish Airlines 981.")

NUMS = []
def num(fig, element, series, **kw): NUMS.append(dict(figure=fig, element=element, series=series, **kw))

# ----------------------------------------------------------------------------- A1: evidence dot plot
def build_A1():
    fig = plt.figure(figsize=(127 * MM, 122 * MM))
    axm = ax_mm(fig, 11, 50, 64, 70); draw_main(axm); letter(axm, "a", x=0.0, y=1.01)
    axb = ax_mm(fig, 84, 72, 41, 48)
    axb.axvspan(-1, 1, color=G15, lw=0, zorder=0); axb.axvline(0, color="k", lw=LW_REF, zorder=1)
    for y0, code, m in ((1.0, "D10", "s"), (0.0, "D11", "^")):
        for route, dy, fill in (("Davey model + fuel", 0.13, "k"), ("waypoints", -0.13, "white")):
            c, lo, hi = lnb(route, code); axb.plot([lo, hi], [y0 + dy] * 2, color="k", lw=LW_DATA, zorder=3)
            axb.plot(c, y0 + dy, ls="none", marker=m, ms=4.5, mfc=fill, mec="k", mew=0.8, zorder=4)
            num("A1", "ln B vs BFOs as observed (90 % seed interval)", f"{route} {code}", value=c, low=lo, high=hi)
    axb.set_xlim(-1.5, 1.5); axb.set_ylim(-0.6, 1.6); axb.set_yticks([]); axb.spines["left"].set_visible(False)
    axb.set_xticks([-1, 0, 1]); axb.set_xticklabels(["−1", "0", "+1"])
    axb.set_xlabel("ln B relative to\n00:19 BFOs as observed")
    letter(axb, "b", x=0.0, y=1.01)
    legend_block(fig, 84, 58, [(Line2D([], [], ls="none", marker="s", ms=4.5, mfc="k", mec="k"), "Davey model with fuel"),
                               (Line2D([], [], ls="none", marker="s", ms=4.5, mfc="white", mec="k", mew=0.8), "Waypoint routes")], 41)
    groups_and_treatments_legend(fig, 40)
    cap = (CAP_MAIN + CAP_MK + "(b) Log Bayes factor against the 00:19 BFOs as observed, for the same data; lines are 90 % intervals over seeds. "
           "The grey band (|ln B| < 1) is evidence not worth more than a bare mention (Kass and Raftery, 1995). " + CAP_R)
    return fig, cap, "The 00:19 BFO treatments differ by less than 0.5 nat: the evidence does not choose between them"

# ----------------------------------------------------------------------------- A2: prediction contours + probabilities
def draw_contours(ax):
    c9 = ax.contour(HX, HY, HD.T, levels=[HLEV[0.9]], colors="k", linewidths=0.8, linestyles=[(0, (5, 1.5, 1, 1.5))], zorder=6)
    c5 = ax.contour(HX, HY, HD.T, levels=[HLEV[0.5]], colors="k", linewidths=LW_THICK, zorder=6)
    for cs in (c9, c5): cs.set(path_effects=HALO)
    for p, cs in ((0.9, c9), (0.5, c5)):
        for seg in cs.allsegs[0]:
            for x_, y_ in seg[::4]: num("A2", f"BTO-only predicted region {int(p*100)} %", "descending paths", rate_8s_later_kfpm=round(x_, 3), rate_first_kfpm=round(y_, 3))

def build_A2():
    fig = plt.figure(figsize=(127 * MM, 128 * MM))
    axm = ax_mm(fig, 11, 56, 64, 70); draw_main(axm); draw_contours(axm); letter(axm, "a", x=0.0, y=1.01)
    axb = ax_mm(fig, 88, 84, 37, 42)
    for y0, code, m in ((2, "D9", "o"), (1, "D10", "s"), (0, "D11", "^")):
        p, pw = PPROB["Davey model + fuel"][code], PPROB["waypoints"][code]
        axb.barh(y0, p, height=0.42, color=G35, lw=0, zorder=2)
        axb.plot([pw, pw], [y0 - 0.3, y0 + 0.3], color="k", lw=LW_DATA, zorder=3)
        axb.plot(-0.07, y0, ls="none", marker=m, ms=4.5, mfc="white", mec="k", mew=0.8, clip_on=False)
        axb.text(max(p, pw) + 0.06, y0, f"{p:.2f}", va="center", ha="left", fontsize=8)
        num("A2", "posterior probability, equal prior", code, davey_fuel=p, waypoints=pw)
    axb.axvline(1 / 3, color="k", lw=LW_REF, ls=(0, (1, 1.5)), zorder=1)
    axb.set_xlim(0, 0.7); axb.set_ylim(-0.6, 2.6); axb.set_yticks([]); axb.spines["left"].set_visible(False)
    axb.set_xticks([0, 1 / 3, 0.5]); axb.set_xticklabels(["0", "1/3", "0.5"]); axb.set_xlabel("Posterior probability\n(equal prior)")
    letter(axb, "b", x=-0.12, y=1.01)
    legend_block(fig, 84, 70, [(Patch(facecolor=G35, lw=0), "Davey model with fuel"), (Line2D([], [], color="k", lw=LW_DATA, marker="|", ls="none", ms=8, mew=LW_DATA), "Waypoint routes")], 41)
    extra = [(Line2D([], [], color="k", lw=LW_THICK), "Prediction from the BTOs only, " + nb("50 % region")),
             (Line2D([], [], color="k", lw=0.8, ls=(0, (5, 1.5, 1, 1.5))), "Prediction from the BTOs only, " + nb("90 % region"))]
    groups_and_treatments_legend(fig, 46, extra=extra)
    cap = (CAP_MAIN + CAP_MK + f"Contours enclose 50 % and 90 % of the rates predicted from the 00:19 BTOs alone for descending paths "
           f"({D7_DESC*100:.0f} % of the predicted weight). (b) Posterior probability, with an equal prior (dotted line), of the three treatments that use both BFOs. " + CAP_R)
    return fig, cap, "Before the BFOs are used, the model predicts mostly steady descents; the BFO-implied pairs lie at or beyond the 90 % region"

# ----------------------------------------------------------------------------- A3: scorecard
def score_rows():
    sym = lambda f: "full" if f >= 0.9 else ("left" if f >= 0.1 else "none")
    ev_ = {"D9": "0", "D10": f"{lnb('Davey model + fuel','D10')[0]:+.2f}".replace("-", "−"), "D11": f"{lnb('Davey model + fuel','D11')[0]:+.2f}".replace("-", "−")}
    cols = ["D9", "D10", "D11", "D8", "D7"]
    rows = [("Evidence, ln B", [("t", ev_.get(c, "–")) for c in cols]),
            ("18:25 log-on, R600 BFO", [("s", "full"), ("s", "none"), ("s", "full"), ("s", "full"), ("t", "–")]),
            ("18:25 log-on, R1200 BFO", [("s", "none"), ("s", "left"), ("s", "left"), ("t", "–"), ("t", "–")]),
            ("Inside accident-dive areas", [("s", sym(Q[c]["in_real"])) for c in cols]),
            ("Inside Boeing build-ups in\nthe log-on window", [("s", sym(Q[c]["in_window"])) for c in cols])]
    for crit, vals in rows:
        for c, v in zip(cols, vals): num("A3", "scorecard cell", f"{crit} | {c}", cell=v[1])
    for c in cols: num("A3", "posterior weight inside areas", c, accident_dive=round(Q[c]["in_real"], 4), boeing_logon_window=round(Q[c]["in_window"], 4))
    return rows

def build_A3():
    fig = plt.figure(figsize=(127 * MM, 128 * MM))
    axm = ax_mm(fig, 11, 56, 64, 70); draw_main(axm); letter(axm, "a", x=0.0, y=1.01)
    axs = ax_mm(fig, 81, 62, 45, 64); axs.axis("off"); axs.set_xlim(0, 45); axs.set_ylim(0, 64)
    xs = [5.5 + 8.6 * j for j in range(5)]
    for j, m in enumerate(["o", "s", "^", "v"]): axs.plot(xs[j], 61.5, ls="none", marker=m, ms=4.5, mfc="white", mec="k", mew=0.8, clip_on=False)
    axs.text(xs[4], 61.5, "BTO\nonly", ha="center", va="center", fontsize=8, linespacing=0.95)
    y = 56.0
    for i, (crit, vals) in enumerate(score_rows()):
        lab = crit
        nl = lab.count("\n") + 1
        axs.plot([0, 45], [y + 1.4, y + 1.4], color="0.6", lw=LW_REF)
        axs.text(0, y, lab, ha="left", va="top", fontsize=8, linespacing=1.0)
        yv = y - 3.3 * nl - 2.6
        for j, v in enumerate(vals):
            if v[0] == "t": axs.text(xs[j], yv, v[1], ha="center", va="center", fontsize=8)
            else: axs.plot(xs[j], yv, ls="none", marker="o", ms=5.5, color="k", mec="k", mew=0.8, fillstyle=v[1], markerfacecoloralt="white")
        y = yv - 4.2
    axs.plot([0, 45], [y + 1.4, y + 1.4], color="0.6", lw=LW_REF)
    yk = y - 2.0
    for x0, fs, t in ((0.8, "full", "yes"), (12.0, "left", "partly"), (25.5, "none", "no")):
        axs.plot(x0, yk, ls="none", marker="o", ms=5.0, color="k", mew=0.8, fillstyle=fs, markerfacecoloralt="white", clip_on=False)
        axs.text(x0 + 2.4, yk, t, ha="left", va="center", fontsize=8)
    axs.text(0.2, yk - 4.6, "–", ha="left", va="center", fontsize=8); axs.text(3.2, yk - 4.6, "not applicable", ha="left", va="center", fontsize=8)
    letter(axs, "b", x=-0.02, y=1.0)
    groups_and_treatments_legend(fig, 46)
    cap = (CAP_MAIN + CAP_MK + "(b) Tests of each treatment: ln B against the BFOs as observed (only for treatments with both BFOs); fit when applied to the 18:25 log-on "
           "(half: fit only at the top of Holland's range, which was set from that log-on); posterior weight inside the areas (filled ≥ 90 %, half 10–90 %, open < 10 %). "
           "R600 and R1200 are the 600 and 1200 bit/s channels.")
    return fig, cap, "No 00:19 BFO treatment passes every test; the differences in evidence are weak"

# ----------------------------------------------------------------------------- A4: compact numeric table
def build_A4():
    fig = plt.figure(figsize=(127 * MM, 128 * MM))
    axm = ax_mm(fig, 11, 56, 58, 70); draw_main(axm); letter(axm, "a", x=0.0, y=1.01)
    axt = ax_mm(fig, 74, 82, 52, 44); axt.axis("off"); axt.set_xlim(0, 52); axt.set_ylim(0, 44)
    X = dict(sym=1.6, lnb=14.0, p=31.0, n=51.5)
    axt.plot([0, 52], [44, 44], color="k", lw=LW_REF)
    axt.text(X["lnb"], 43, "ln B\n(90 % interval)", ha="center", va="top", fontsize=8, linespacing=1.0)
    axt.text(X["p"], 43, "Posterior\nprobability", ha="center", va="top", fontsize=8, linespacing=1.0)
    axt.text(X["n"], 43, "Effective\nsamples", ha="right", va="top", fontsize=8, linespacing=1.0)
    axt.plot([0, 52], [35.5, 35.5], color="k", lw=LW_REF)
    y = 32.0
    for code, m in (("D9", "o"), ("D10", "s"), ("D11", "^"), ("D8", "v"), ("D7", None)):
        n_, prov = ESS[("Davey model + fuel", code)]
        if m: axt.plot(X["sym"], y - 1.8, ls="none", marker=m, ms=4.5, mfc="white", mec="k", mew=0.8)
        else: axt.text(0, y - 1.8, "BTO\nonly", ha="left", va="center", fontsize=8, linespacing=0.95)
        if code in ("D9", "D10", "D11"):
            c, lo, hi = lnb("Davey model + fuel", code); f = lambda v: f"{v:+.2f}".replace("-", "−")
            axt.text(X["lnb"], y, "0" if code == "D9" else f(c), ha="center", va="center", fontsize=8)
            axt.text(X["lnb"], y - 3.6, "(reference)" if code == "D9" else f"({f(lo)}, {f(hi)})", ha="center", va="center", fontsize=8)
            axt.text(X["p"], y - 1.8, f"{PPROB['Davey model + fuel'][code]:.2f}", ha="center", va="center", fontsize=8)
            num("A4", "table row", code, lnB=c, lnB_low=lo, lnB_high=hi, probability=PPROB['Davey model + fuel'][code], effective_samples=round(n_))
        else:
            axt.text(X["lnb"], y - 1.8, "–", ha="center", va="center", fontsize=8); axt.text(X["p"], y - 1.8, "–", ha="center", va="center", fontsize=8)
            num("A4", "table row", code, effective_samples=round(n_))
        axt.text(X["n"], y - 1.8, f"{n_:,.0f}" + ("*" if prov else ""), ha="right", va="center", fontsize=8)
        y -= 7.2
    axt.plot([0, 52], [y + 2.6, y + 2.6], color="k", lw=LW_REF)
    letter(axt, "b", x=-0.02, y=1.02)
    groups_and_treatments_legend(fig, 46)
    cap = (CAP_MAIN + CAP_MK + "(b) ln B against the BFOs as observed (90 % interval over seeds) and posterior probability with an equal prior, both only for treatments "
           "with both BFOs; effective sample size of the final run (* fewer than 500 in the no-pilot family). " + CAP_R)
    return fig, cap, "Numeric summary: evidence, probability and effective sample size of each 00:19 BFO treatment"

# ----------------------------------------------------------------------------- B1: slope bands at the two 00:19:29 rates
SL_GROUPS = [("P", "Push-overs"), ("R", "Roll-offs/upsets"), ("W", "Boeing build-ups inside the log-on window"), ("O", "Boeing build-ups at other times")]
def slope_envelope(keys, centre, window=None):
    T_, X_, Y_ = allpairs(keys, window=window)
    m = np.abs(X_ - centre) <= SLOPE_HALF
    if m.sum() < 2: return None
    s = np.linspace(0, 1, 41); seg = X_[m][:, None] + s[None, :] * (Y_[m] - X_[m])[:, None]
    return s, seg.min(0) / 1e3, seg.max(0) / 1e3, int(m.sum())

def build_B1():
    fig = plt.figure(figsize=(127 * MM, 104 * MM))
    st_ = {"P": dict(facecolor="none", edgecolor="k", hatch="////", linewidth=0.8, zorder=3),
           "R": dict(facecolor="none", edgecolor="0.3", hatch="\\\\\\\\", linewidth=0.8, linestyle=(0, (3.5, 1.5)), zorder=3),
           "W": dict(facecolor=G35, edgecolor="none", linewidth=0, zorder=1.5),
           "O": dict(facecolor=G15, edgecolor="none", linewidth=0, zorder=1)}
    panels = ((TA[0], "o", ("D9", "D11"), TLAB["o"]), (TH[0], "s", ("D10",), TLAB["s"]))
    for i, (centre, mk_main, codes, _) in enumerate(panels):
        ax = ax_mm(fig, 13 + i * 58, 44, 48, 56)
        for g in ("O", "W", "P", "R"):
            keys = GROUPS[g] if g in "PR" else GROUPS["A"] + GROUPS["N"]
            env = slope_envelope(keys, centre, window=(WIN if g == "W" else (False if g == "O" else None)))
            if env is None: continue
            s_, lo, hi, n = env; ax.fill_between(s_, lo, hi, **st_[g])
            num("B1", f"slope envelope, first instant {centre:.0f} +/- {SLOPE_HALF:.0f} ft/min", g, n_pairs=n, first_low=lo[0], first_high=hi[0], later_low=lo[-1], later_high=hi[-1])
        a, b = (TA if i == 0 else TH)
        ax.plot([0, 1], [a / 1e3, b / 1e3], color="k", lw=LW_THICK, ls="-" if i == 0 else (0, (4, 1.5)), zorder=6, path_effects=HALO)
        for code in codes:
            m = {"D9": "o", "D10": "s", "D11": "^"}[code]; q = Q[code]; on_line = code != "D11"
            for xe, rr, yl in ((0.0 if on_line else -0.09, q["r29"], a), (1.0 if on_line else 1.09, q["r37"], b)):
                cy = yl / 1e3 if on_line else rr[1] / 1e3
                ax.plot([xe, xe], [rr[0] / 1e3, rr[2] / 1e3], color="k", lw=0.8, zorder=7, clip_on=False)
                ax.plot(xe, cy, ls="none", marker=m, ms=4.5, mfc="white", mec="k", mew=0.8, zorder=8, clip_on=False)
        ax.set_xlim(-0.2, 1.2); ax.set_ylim(0, 30); ax.set_xticks([0, 1]); ax.set_xticklabels(["0", "8"])
        ax.set_yticks(range(0, 31, 5)); ax.spines["bottom"].set_bounds(0, 1)
        ax.set_xlabel("Time after the first instant (s)")
        if i == 0: ax.set_ylabel("Descent rate (1000 ft/min)")
        else: ax.set_yticklabels([])
        letter(ax, "ab"[i], x=0.0, y=1.01)
        num("B1", "implied segment", "D9" if i == 0 else "D10 published point", first_fpm=a, later_fpm=b)
    ent = [(Patch(**{k: v for k, v in st_["P"].items() if k != "zorder"}), "Push-overs " + nb("(3 accident cases)")),
           (Patch(**{k: v for k, v in st_["R"].items() if k != "zorder"}), "Roll-offs/upsets " + nb("(5 accident cases)")),
           (Patch(**{k: v for k, v in st_["W"].items() if k != "zorder"}), "Boeing 777 simulations, build-ups inside the log-on window"),
           (Patch(**{k: v for k, v in st_["O"].items() if k != "zorder"}), "Boeing 777 simulations, build-ups at other times")]
    ent2 = [(Line2D([], [], color="k", lw=LW_THICK, marker="o", ms=4.5, mfc="white", mec="k", mew=0.8), TLAB["o"]),
            (Line2D([], [], color="k", lw=LW_THICK, ls=(0, (4, 1.5)), marker="s", ms=4.5, mfc="white", mec="k", mew=0.8), TLAB["s"] + ", " + nb("published point")),
            (mk_handle("^"), TLAB["^"])]
    legend_block(fig, 1, 32, ent, 62); legend_block(fig, 66, 32, ent2, 60)
    cap = ("Change of descent rate over 8 s in every dive build-up whose first-instant rate lies within 500 ft/min of the 00:19:29 rate implied by (a) the "
           "00:19 BFOs as observed (4,350 ft/min) and (b) the BFOs with Holland transient bias added (8,590 ft/min, published point). Each area spans all such "
           "changes in one group. Heavy lines join the implied rates; bars are 5–95 % posterior ranges at each instant (Davey model with fuel), and triangles "
           "give the bias added to the 00:19:37 BFO only. The log-on window is 67–198 s after power loss.")
    return fig, cap, "From the 00:19:29 rate, accident dives gain as much in 8 s as the 00:19 BFOs imply; Boeing build-ups inside the log-on window do not"

# ----------------------------------------------------------------------------- B2: acceleration plane
def build_B2():
    fig = plt.figure(figsize=(127 * MM, 92 * MM))
    ax = ax_mm(fig, 12, 11, 70, 78)
    for g in "ANPR":
        s = STY[g]
        for c_, lo_, hi_ in ABANDS[g]: ax.fill_between(c_, lo_, hi_, **{k: v for k, v in s.items() if k != "z"}, zorder=s["z"])
    for c_, lo_, hi_ in ABANDS["W"]:
        ax.plot(np.r_[c_, c_[::-1], c_[0]], np.r_[hi_, lo_[::-1], hi_[0]], color="k", lw=LW_DATA, ls=(0, (1, 1.2)), zorder=6, path_effects=HALO)
    draw_steady(ax, accel=True)
    ax.axhline(0, color="0.35", lw=LW_REF, ls=(0, (1, 1.5)), zorder=0.5)
    for m in "os^":
        q = Q[TCODE[m]]; x, a_ = q["r29"] / 1e3, q["acc"]
        cx, cy = (TA[0] / 1e3, acc_g(*TA)) if m == "o" else (TH[0] / 1e3, acc_g(*TH)) if m == "s" else (x[1], a_[1])
        ax.plot([x[0], x[2]], [cy, cy], color="k", lw=0.8, zorder=8); ax.plot([cx, cx], [a_[0], a_[2]], color="k", lw=0.8, zorder=8)
        ax.plot(cx, cy, ls="none", marker=m, ms=4.5, mfc="white", mec="k", mew=0.8, zorder=9)
        num("B2", "treatment point and 5-95 % posterior range", TCODE[m], rate_first_kfpm=cx, accel_g=round(cy, 4), rate_low=x[0], rate_high=x[2], accel_low=a_[0], accel_high=a_[2])
    ax.set_xlim(0, 30); ax.set_ylim(-0.1, 1.6); ax.set_yticks([0, 0.5, 1.0, 1.5]); ax.set_yticklabels(["0", "0.5", "1.0", "1.5"])
    ax.set_yticks([0.25, 0.75, 1.25], minor=True)
    ax.set_xlabel("Descent rate at the first instant (1000 ft/min)"); ax.set_ylabel("Mean downward acceleration over the next 8 s (g)")
    ent = [(patch("P"), GLAB["P"]), (patch("R"), GLAB["R"]), (patch("A"), GLAB["A"]), (patch("N"), GLAB["N"]),
           (Line2D([], [], color="k", lw=LW_DATA, ls=(0, (1, 1.2))), "Boeing 777 build-ups inside the log-on window (outline)"),
           (steady_handle(), GLAB["S"])] + [(mk_handle(m), TLAB[m]) for m in "os^"]
    legend_block(fig, 86, 89, ent, 40)
    cap = ("Descent rate at a first instant and mean downward acceleration over the next 8 s (g = 32.174 ft/s²) during the build-up of dives; each area covers one "
           "group, and steady descents lie on the dotted zero line. The dotted outline encloses Boeing build-ups inside the log-on window (67–198 s after power loss). "
           f"Symbols are the values implied by the 00:19 BFO treatments ({acc_g(*TA):.2f} g as observed; {acc_g(*TH):.2f} g with Holland transient bias added, published point); "
           "bars give the 5–95 % posterior range (Davey model with fuel).")
    return fig, cap, "The 00:19 BFOs imply about 0.66–0.68 g: inside accident dives and above Boeing build-ups in the log-on window"

# ----------------------------------------------------------------------------- B3: conditional cut
def build_B3():
    order = [("Push-overs", GROUPS["P"]), ("Roll-offs/upsets", GROUPS["R"]),
             ("Boeing 777 simulations,\nalternate electrical configuration", GROUPS["A"]), ("Boeing 777 simulations,\nnormal electrical configuration", GROUPS["N"])]
    ys, heads, y = {}, [], 0.0
    for gname, keys in order:
        hy = y + (0.3 if "\n" in gname else 0.0); heads.append((gname, hy)); y += 1.6 if "\n" in gname else 1
        for k in keys: ys[k] = y; y += 1
        y += 0.35
    ymax = y
    fig = plt.figure(figsize=(127 * MM, 118 * MM))
    axs = [ax_mm(fig, 50, 30, 36, 86), ax_mm(fig, 90, 30, 36, 86)]
    for i, (ax, X, obs, code) in enumerate(zip(axs, (TA[0], TH[0]), (TA[1], TH[1]), ("D11", "D10"))):
        q = Q[code]["r37"] / 1e3
        ax.axvspan(q[0], q[2], color=G15, lw=0, zorder=0)
        ax.axvline(X / 1e3, color="0.35", lw=LW_REF, ls=(0, (1, 1.5)), zorder=1)
        ax.axvline(obs / 1e3, color="k", lw=LW_DATA, zorder=2)
        for k, yy in ys.items():
            d = CUT[(CUT.threshold_fpm == X) & (CUT.case == k)]
            if not len(d): continue
            v = d.rate_8s_later_fpm.values / 1e3
            if len(v) > 1: ax.plot([v.min(), v.max()], [yy, yy], color="0.55", lw=0.8, zorder=3)
            if k.startswith("Boeing"):
                w = d.in_logon_window.values.astype(bool)
                ax.plot(v[~w], [yy] * int((~w).sum()), ls="none", marker="o", mfc="white", mec="k", mew=0.7, ms=3.6, zorder=4)
                ax.plot(v[w], [yy] * int(w.sum()), ls="none", marker="o", color="k", ms=4.0, zorder=5)
            else: ax.plot(v, [yy] * len(v), ls="none", marker="D", color="k", ms=3.6, zorder=5)
        ax.set_xlim(0, 30); ax.set_ylim(ymax - 0.15, -0.85); ax.tick_params(left=False)
        ax.set_xlabel(f"Descent rate 8 s after passing\n{X:,.0f} ft/min (1000 ft/min)")
        ax.text(0.98, 1.0, f"({'ab'[i]})", transform=ax.transAxes, ha="right", va="bottom", fontsize=8)
        if i: ax.spines["left"].set_visible(False); ax.set_yticks([])
    axs[0].set_yticks(list(ys.values())); axs[0].set_yticklabels([k.replace("Boeing 777 simulation", "Simulation") for k in ys])
    tr = matplotlib.transforms.blended_transform_factory(fig.transFigure, axs[0].transData)
    for gname, yy in heads: fig.text(1.2 / 127, yy, gname, transform=tr, ha="left", va="center", fontsize=8, style="italic", linespacing=1.0)
    ent = [(Line2D([], [], ls="none", marker="D", color="k", ms=3.6), "Accident case"),
           (Line2D([], [], ls="none", marker="o", color="k", ms=4.0), "Boeing build-up inside the log-on window"),
           (Line2D([], [], ls="none", marker="o", mfc="white", mec="k", mew=0.7, ms=3.6), "Boeing build-up at other times"),
           (Line2D([], [], color="0.55", lw=0.8), "Range over repeated build-ups")]
    ent2 = [(Line2D([], [], color="k", lw=LW_DATA), "Rate at 00:19:37 implied by the BFOs"),
            (Line2D([], [], color="0.35", lw=LW_REF, ls=(0, (1, 1.5))), "Steady descent (no acceleration)"),
            (Patch(facecolor=G15, lw=0), "5–95 % posterior range of the 00:19:37 rate")]
    legend_block(fig, 1, 17, ent, 62); legend_block(fig, 66, 17, ent2, 60)
    for _, r in CUT.iterrows(): num("B3", "rate 8 s after passing threshold", r.case, threshold_fpm=r.threshold_fpm, crossing_time_s=r.crossing_time_s, rate_8s_later_fpm=r.rate_8s_later_fpm, in_logon_window=r.in_logon_window)
    cap = ("Descent rate 8 s after each dive passed the 00:19:29 rate implied by (a) the 00:19 BFOs as observed (4,350 ft/min) and (b) the BFOs with Holland "
           "transient bias added (8,590 ft/min, published point). Solid lines: implied 00:19:37 rates (14,860 and 18,830 ft/min). Grey bands: 5–95 % posterior range "
           "of the 00:19:37 rate with (a) the bias added to the 00:19:37 BFO only and (b) the bias added to both (Davey model with fuel). Filled circles are Boeing "
           "build-ups inside the log-on window (67–198 s after power loss); a row without a symbol never reaches that rate.")
    return fig, cap, "8 s after passing the 00:19:29 rate, accident dives reach about the 00:19:37 rate; no Boeing build-up in the log-on window does"

# ----------------------------------------------------------------------------- output
def compose(png, top, bottom, out, dpi, botsize=8):
    im = Image.open(png).convert("L"); w, h = im.size; wi, hi = w / 600, h / 600
    Wd = max(wi, 127 * MM) + 0.1; tw = (Wd - 0.14) * 25.4
    tl = wrap_mm(top, tw, 9, bold=True).split("\n") if top else []; bl = wrap_mm(bottom, tw, botsize).split("\n") if bottom else []
    ht = (9 / 72 * 1.3 * len(tl) + 0.12) if tl else 0.0; hb = (botsize / 72 * 1.25 * len(bl) + 0.2) if bl else 0.05
    Ht = hi + ht + hb; pf = plt.figure(figsize=(Wd, Ht))
    a = pf.add_axes([0.05 / Wd, hb / Ht, wi / Wd, hi / Ht]); a.imshow(im, cmap="gray", vmin=0, vmax=255); a.axis("off")
    if tl: pf.text(0.05 / Wd, 1 - 0.05 / Ht, "\n".join(tl), va="top", ha="left", fontsize=9, family="serif", weight="bold")
    if bl: pf.text(0.05 / Wd, (hb - 0.08) / Ht, "\n".join(bl), va="top", ha="left", fontsize=botsize, family="serif", linespacing=1.15)
    pf.savefig(out, dpi=dpi); plt.close(pf)

FIGS = {"A1": ("descent-0019-A1-evidence-dots", build_A1), "A2": ("descent-0019-A2-prediction-contours", build_A2),
        "A3": ("descent-0019-A3-scorecard", build_A3), "A4": ("descent-0019-A4-compact-table", build_A4),
        "B1": ("descent-0019-B1-slope-bands", build_B1), "B2": ("descent-0019-B2-acceleration-plane", build_B2),
        "B3": ("descent-0019-B3-conditional-cut", build_B3)}

def main(only=None):
    rc(); caps = {}
    for key, (name, fn) in FIGS.items():
        if only and key not in only: continue
        rc(); fig, cap, title = fn()
        fig.savefig(f"{OUT}/{name}-word.png", dpi=600, bbox_inches="tight", pad_inches=0.04)
        fig.savefig(f"{OUT}/{name}.pdf", bbox_inches="tight", pad_inches=0.04); plt.close(fig)
        open(f"{OUT}/{name}-caption.txt", "w").write(cap.strip() + "\n"); caps[key] = (name, cap, title)
        compose(f"{OUT}/{name}-word.png", None, cap, f"{OUT}/{name}-proof.png", 250)
        compose(f"{OUT}/{name}-word.png", title, WF, f"{OUT}/{name}-working.png", 200, botsize=6.5)
    for k, (t, d, g) in [("as observed", (TA[0], TA[1], None)), ("Holland published point", (TH[0], TH[1], None))]:
        num("all", "implied point", k, rate_001929_fpm=t, rate_001937_fpm=d, accel_g=round(acc_g(t, d), 4))
    for d_, q in Q.items():
        num("all", "posterior 5/50/95 % (Davey model with fuel)", d_, r29_q05=q["r29"][0], r29_q50=q["r29"][1], r29_q95=q["r29"][2],
            r37_q05=q["r37"][0], r37_q50=q["r37"][1], r37_q95=q["r37"][2], acc_q05=q["acc"][0], acc_q50=q["acc"][1], acc_q95=q["acc"][2])
    pd.DataFrame(NUMS).to_csv(f"{OUT}/plotted-numbers.csv", index=False)
    rows = []
    for plane, B in (("rate-rate", BANDS), ("rate-acceleration", ABANDS)):
        for g, segs in B.items():
            for si, (c_, lo_, hi_) in enumerate(segs):
                for cc, l_, h_ in zip(c_, lo_, hi_):
                    rows.append(dict(plane=plane, group=g, segment=si, first_instant_rate_kfpm=round(cc, 4), low=round(l_, 5), high=round(h_, 5)))
    pd.DataFrame(rows).to_csv(f"{OUT}/band-polygons.csv", index=False)
    return caps

if __name__ == "__main__":
    main()
