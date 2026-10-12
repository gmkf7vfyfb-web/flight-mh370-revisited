"""Drift-only source-location PDF (uniform prior over the computed grid), equal-weight mixture of GLORYS12 and GlobCurrent
(product-relative windage), run A surfaces (710 nodes). Interpolated in likelihood exactly as interpolate.rs (score_impacts.lookup).
Greyscale 50/90/99 % HPD regions with black contour lines (Pete's convention), 6th and 7th arcs from core run D run.json."""
import sys, json, textwrap
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator
WS = "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/f90cad13-a26e-40d1-9a16-691b3817aa7b/"
R = WS + "repo/Claude Science Project Sep 29/engine/runs/"
sys.path.insert(0, WS + "repo/Claude Science Project Sep 29/engine/hypotheses/debris-drift/prepare/pilot")
from score_impacts import lookup, surface_arrays
G = surface_arrays(R + "debris-drift-runA-glorys12-combined/merged", "ln_l")
C = surface_arrays(R + "debris-drift-runA-globcurrent/merged", "ln_l")
d = 0.02
lat = np.arange(-42.5, -19.0, d) + d / 2; lon = np.arange(83.0, 108.0, d) + d / 2
LA, LO = np.meshgrid(lat, lon, indexing="ij")
fg, lg = lookup(*G, LA.ravel(), LO.ravel()); fc, lc = lookup(*C, LA.ravel(), LO.ravel())
both = (fg == 1) & (fc == 1)
area = np.cos(np.radians(LA.ravel()))  # cell area on a degree grid
def dens(ll, ok):
    p = np.zeros(ll.size); m = np.nanmax(ll[ok]); p[ok] = np.exp(ll[ok] - m); p *= area; return (p / p.sum()).reshape(LA.shape)
Pg, Pc = dens(lg, both), dens(lc, both)
Pm = 0.5 * Pg + 0.5 * Pc  # equal prior weight per model, each normalised over the same support (mixture of model posteriors)
# posterior model weights under equal prior: ratio of each model's evidence over the support
lw = {}
for k, ll in (("GLORYS12", lg), ("GlobCurrent", lc)):
    m = ll[both].max(); lw[k] = m + np.log(np.sum(np.exp(ll[both] - m) * area[both]))
mx = max(lw.values()); pw = {k: np.exp(v - mx) for k, v in lw.items()}; s = sum(pw.values()); pw = {k: v / s for k, v in pw.items()}
Pe = (pw["GLORYS12"] * Pg + pw["GlobCurrent"] * Pc)  # evidence-weighted mixture (posterior model weights)
LEV = [0.99, 0.90, 0.50]
def hpd(P):
    v = np.sort(P.ravel())[::-1]; c = np.cumsum(v); return [float(v[np.searchsorted(c, f)]) for f in LEV]
SH = ["#f3f3f3", "#e1e1e1", "#cdcdcd"]; LW = [0.6, 0.9, 1.3]
arcs = {x["epoch"]: np.asarray(x["lat_lon"], float) for x in json.load(open("/Users/pete/Downloads/mh370-exchange/core/next-run-d/next-d-free/run.json"))["reference_arcs"]}
AR = {"m0011": dict(lw=1.1, color="#b16286", label="6th arc, 00:11 UTC"), "m0019a": dict(lw=1.0, color="#4a6fa5", ls="--", label="7th arc, 00:19 UTC")}
def stats(P):
    pl = P.sum(1); c = np.cumsum(pl); med = float(np.interp(0.5, c, lat)); lo, hi = float(np.interp(0.025, c, lat)), float(np.interp(0.975, c, lat))
    lv = hpd(P); km2 = (111.195 * d) ** 2 * np.cos(np.radians(LA))
    return med, lo, hi, [float(km2[P >= l].sum() / 1e3) for l in lv]
panels = [("Mixture of both ocean models, equal weights", Pm), ("GLORYS12 + ERA5", Pg), ("GlobCurrent + ERA5, wind effect corrected", Pc)]
fig, axs = plt.subplots(1, 3, figsize=(10.2, 6.6), sharey=True, gridspec_kw=dict(wspace=0.05))
fmt = FuncFormatter(lambda v, _: f"{abs(v):.0f}°S" if v < 0 else f"{v:.0f}°")
out = {"posterior_model_weights_equal_prior": pw}
for ax, (t, P) in zip(axs, panels):
    lv = hpd(P)
    ax.set_axisbelow(True); ax.grid(True, color="#ececec", lw=0.5)
    ax.contourf(lon, lat, P, levels=lv + [P.max() * 1.0001], colors=SH, antialiased=True)
    ax.contour(lon, lat, P, levels=lv, colors="k", linewidths=LW)
    ax.contour(lon, lat, both.reshape(LA.shape).astype(float), levels=[0.5], colors="#8c8c8c", linewidths=0.5, linestyles=":")
    for e, st in AR.items(): ax.plot(arcs[e][:, 1], arcs[e][:, 0], **st)
    ax.set_xlim(83.5, 107.5); ax.set_ylim(-42.5, -19.5); ax.set_aspect(1 / np.cos(np.radians(31)))
    ax.xaxis.set_major_locator(MultipleLocator(5)); ax.yaxis.set_major_locator(MultipleLocator(5)); ax.yaxis.set_major_formatter(fmt)
    ax.set_xlabel("Longitude (°E)", fontsize=8); ax.tick_params(labelsize=7); ax.set_title(t, fontsize=8.5, loc="left")
    med, lo, hi, ar = stats(P)
    ax.text(0.97, 0.03, f"median {abs(med):.1f}°S (95 %: {abs(hi):.1f}–{abs(lo):.1f}°S)\n50 / 90 / 99 % area {ar[2]:.0f} / {ar[1]:.0f} / {ar[0]:.0f} thousand km²",
            transform=ax.transAxes, fontsize=6.3, ha="right", va="bottom", color="#333333")
    out[t] = dict(median_lat=med, lat_2p5=lo, lat_97p5=hi, area_kkm2_99_90_50=ar)
med, lo, hi, ar = stats(Pe); out["evidence-weighted mixture"] = dict(median_lat=med, lat_2p5=lo, lat_97p5=hi, area_kkm2_99_90_50=ar)
axs[0].set_ylabel("Latitude", fontsize=8)
hs = [Patch(facecolor=s, edgecolor="k", lw=w, label=f"{int(f*100)} % of probability") for s, f, w in zip(SH[::-1], LEV[::-1], LW[::-1])]
hs += [plt.Line2D([], [], **st) for st in AR.values()] + [plt.Line2D([], [], color="#8c8c8c", lw=0.5, ls=":", label="edge of computed grid")]
fig.legend(handles=hs, loc="lower center", ncol=6, frameon=False, fontsize=7, bbox_to_anchor=(0.5, 0.255))
fig.suptitle("Impact location from the recovered debris alone: posterior PDF, 50 / 90 / 99 % regions", x=0.02, ha="left", fontsize=10, y=0.985)
ste = ("What the chart shows. Each map shows where the aircraft hit the sea, using only the drift of the nine identified debris items. "
       "The darker the grey, the more probable the area. The left map averages the two ocean models with equal weight. The other maps show each model alone. "
       "The maps do not use the satellite data or the flight path, except that the calculation is limited to the grid (dotted line), which is placed where the flight model puts impacts. "
       "Values in the far south are noisy. The results are interim and are not evidence of the impact location.")
tec = (f"Technical. Debris-drift log-likelihood, nine stringent finds, recovery bandwidth 50 km; run A surfaces on 710 nodes at 30 NM (GLORYS12V1 0.494 m: production 367 + extension 343; "
       f"GlobCurrent my-p1d 0 m, windage product-relative, c_wind offset U(-0.75 %, -0.60 %) of U10, audit F1), each + ERA5 10 m wind; bilinear interpolation in likelihood (interpolate.rs) on a 0.02° grid; "
       f"uniform prior per unit area over the support scored by both models (6 GLORYS12 and 1 GlobCurrent nodes unresolved at 41.2-39.2°S, not computed). "
       f"Mixture = 0.5 p_GLORYS12 + 0.5 p_GlobCurrent (equal prior model weight, Pete 03:10Z). Posterior model weights from the debris evidence over this support: "
       f"GLORYS12 {pw['GLORYS12']:.2f}, GlobCurrent {pw['GlobCurrent']:.2f}; evidence-weighted mixture median {abs(med):.1f}°S. Split-half Monte Carlo noise per node 1.61 (GLORYS12), 1.17 (GlobCurrent) log-likelihood units; NOT CONVERGED in the south. "
       f"HPD levels on the unsmoothed density. Arcs: core run D reference_arcs (m0011, m0019a). Not combined with core/end-of-flight posteriors, searches, hydroacoustics or Pléiades.")
fig.text(0.02, 0.215, "\n".join(textwrap.wrap(ste, 190)), fontsize=6.4, va="top")
fig.text(0.02, 0.135, "\n".join(textwrap.wrap(tec, 190)), fontsize=6.4, va="top")
fig.subplots_adjust(left=0.06, right=0.99, top=0.935, bottom=0.33)
fig.savefig(WS + "debris-drift-source-pdf-mixture.pdf"); fig.savefig(WS + "debris-drift-source-pdf-mixture.png", dpi=220)
json.dump(out, open(WS + "debris-drift-source-pdf-mixture.json", "w"), indent=1); print(json.dumps(out, indent=1))
