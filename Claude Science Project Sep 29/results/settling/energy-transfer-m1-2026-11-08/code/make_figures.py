"""Figures for the settling energy-transfer run (working and Journal of Navigation forms).

Usage: python make_figures.py HANDOFF_DIR SIDECAR_DIR NACA_CSV OUT_DIR
Figure 1 (settling-tau90-cdf): weighted cumulative distribution of tau90, D7, D9, D10, both route models, headline band
  10-30 deg (black) and band-edge sensitivity 5-45 deg (grey).
Figure 2 (settling-abar-source-check): average longitudinal deceleration of model ditchings (NACA Report 1347 transport
  tables; NACA RM SL9H05a) against the method-1 range.
JON form: greyscale, 127 mm, no title, no notes on the image, letter-only panel labels, 9/8 pt text; caption in a text file
and set beneath the image in a proof PNG. Working form: the same plot with a title and footnotes.
"""
import sys, textwrap
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullFormatter
from PIL import Image, ImageDraw, ImageFont
import settling_energy_transfer_m1 as m1

MM = 1 / 25.4
STY = {"D7": "-", "D9": "--", "D10": ":"}
TREAT_LABEL = {"D7": "Both 00:19 timings", "D9": "Timings and frequencies as recorded", "D10": "Timings and frequencies, Holland offset"}
ROUTE_LABEL = {"df": "Davey model with fuel", "wp": "Waypoint routes"}


def style():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.labelsize": 9, "xtick.labelsize": 8,
                         "ytick.labelsize": 8, "legend.fontsize": 8, "axes.edgecolor": "black", "axes.linewidth": 0.8,
                         "xtick.color": "black", "ytick.color": "black", "text.color": "black", "axes.labelcolor": "black",
                         "xtick.direction": "out", "ytick.direction": "out", "legend.frameon": False, "pdf.fonttype": 42,
                         "axes.spines.top": False, "axes.spines.right": False})


def wcdf(x, w, grid):
    k = np.isfinite(x) & (w > 0); x, w = x[k], w[k]
    o = np.argsort(x); x, w = x[o], np.cumsum(w[o]); w /= w[-1]
    return np.interp(grid, x, w, left=0.0, right=1.0)


def fig1(hdir, sdir):
    grid = np.logspace(np.log10(0.05), np.log10(40), 400)
    fig, axs = plt.subplots(1, 2, figsize=(127 * MM, 68 * MM), sharey=True)
    for ax, route, let in zip(axs, ("df", "wp"), "ab"):
        h = np.load(f"{hdir}/eof-final-handoff-{route}.npz"); s = np.load(f"{sdir}/settling-energy-transfer-m1-{route}.npz")
        for t in ("D7", "D9", "D10"):
            lw = h[f"log_weight_{t}"].astype(float); w = np.exp(lw - lw.max()); w /= w.sum()
            ax.plot(grid, wcdf(s["energy_transfer_tau90_s_band5_45"].astype(float), w, grid), STY[t], color="0.6", lw=1.0)
            ax.plot(grid, wcdf(s["energy_transfer_tau90_s"].astype(float), w, grid), STY[t], color="black", lw=1.3,
                    label=TREAT_LABEL[t])
        ax.set_xscale("log"); ax.set_xlim(0.05, 40); ax.set_ylim(0, 1.0)
        ax.xaxis.set_major_locator(FixedLocator([0.1, 1, 10])); ax.set_xticklabels(["0.1", "1", "10"])
        ax.xaxis.set_minor_locator(FixedLocator([0.05, 0.2, 0.5, 2, 5, 20, 40])); ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_xlabel("Energy-transfer duration $\\tau_{90}$ (s)")
        ax.text(-0.02, 1.06, let, transform=ax.transAxes, fontsize=9, fontweight="bold", ha="right", va="bottom")
    axs[0].set_ylabel("Cumulative probability")
    from matplotlib.lines import Line2D
    hl = [Line2D([], [], ls=STY[t], color="black", lw=1.3) for t in ("D7", "D9", "D10")]
    hl += [Line2D([], [], ls="-", color="black", lw=1.3), Line2D([], [], ls="-", color="0.6", lw=1.0)]
    lab = [TREAT_LABEL[t] for t in ("D7", "D9", "D10")] + ["Blend band 10-30°", "Blend band 5-45°"]
    fig.legend(hl, lab, loc="lower center", ncol=2, bbox_to_anchor=(0.54, 0.0), handlelength=2.6, columnspacing=1.2)
    fig.subplots_adjust(left=0.11, right=0.98, top=0.92, bottom=0.40, wspace=0.10)
    return fig


def fig2(naca_csv):
    d = pd.read_csv(naca_csv)
    groups = [("Constellation with Speedpak\n(NACA RM SL9H05a)", d.source == "NACA RM SL9H05a", "s", "0.0", "black"),
              ("Transports, ditching aids", (d.source == "NACA Report 1347") & (d.configuration != "standard"), "^", "none", "black"),
              ("Transports, damaged model", (d.source == "NACA Report 1347") & (d.configuration == "standard") & (d.damaged == 1), "o", "black", "black"),
              ("Transports, undamaged model", (d.source == "NACA Report 1347") & (d.configuration == "standard") & (d.damaged == 0), "o", "none", "black")]
    fig, ax = plt.subplots(figsize=(127 * MM, 62 * MM))
    ax.axvspan(0.75, 3.0, color="0.85", lw=0, zorder=0)
    ax.axvline(0.45, color="black", ls="--", lw=0.9, zorder=1)
    rng = np.random.default_rng(1)
    for i, (lab, sel, mk, fc, ec) in enumerate(groups):
        x = d.loc[sel, "recomputed_average_g"].values
        y = i + rng.uniform(-0.18, 0.18, len(x))
        ax.scatter(x, y, marker=mk, s=16, facecolors=fc, edgecolors=ec, linewidths=0.8, zorder=3)
    ax.set_yticks(range(len(groups))); ax.set_yticklabels([g[0] for g in groups])
    ax.set_xlim(0, 3.2); ax.set_ylim(-0.6, len(groups) - 0.1)
    ax.set_xlabel("Average longitudinal deceleration, $v^2/(2s)$ (g)")
    ax.text(1.875, len(groups) - 0.42, "Range used, 0.75-3.0 g", ha="center", va="bottom", fontsize=8)
    ax.text(0.47, -0.55, "0.45 g", ha="left", va="bottom", fontsize=8)
    fig.subplots_adjust(left=0.40, right=0.97, top=0.90, bottom=0.20)
    return fig


CAP1 = ("Weighted cumulative distribution of the mechanical energy-transfer duration at water entry, τ90 (time between 5 % "
        "and 95 % of cumulative energy transfer), for (a) the Davey route model with fuel and (b) the waypoint route model. "
        "Line style gives the treatment of the 00:19 satellite data: solid, both log-on timings; dashed, timings and both "
        "frequencies as recorded; dotted, timings and both frequencies with the Holland start-up offset (17 Hz floor). Black lines "
        "use the blend band of 10-30 degrees of flight-path angle between the shallow-entry and steep-entry regimes; grey lines "
        "use 5-45 degrees. First-order water-entry model: constant mean deceleration of 0.75-3.0 g for shallow entry, "
        "progressive crushing over 0.5-1.0 of the airframe length for steep entry. Weights are those of the end-of-flight stage.")
CAP2 = ("Average longitudinal deceleration of calm-water model ditchings, from landing speed v and length of run s. "
        "Circles: twelve transport aeroplanes of NACA Report 1347 (Tables 26-37), open for undamaged models and filled for models "
        "with scale-strength bottoms; triangles: the same with ditching aids (cargo container, hydro-ski, hydroflap); squares: "
        "Lockheed Constellation with Speedpak, NACA RM SL9H05a. Landing speeds 29-84 m/s. The shaded band is the range of "
        "mean deceleration used for shallow water entry (0.75-3.0 g); the dashed line marks the lower edge of the sensitivity case (0.45 g). "
        "Points are spread vertically within each group for legibility.")

FOOT1 = ("Source: final end-of-flight hand-off of 7 Nov 2026 (status UNCHECKED), 501,102 rows (Davey model + fuel, 16 seeds) and "
         "500,198 rows (waypoints, 24 seeds). Treatments D7, D9, D10; weights exp(log_weight), normalised per route model. "
         "Method impact_tau_method = 1 (note of 11 Oct 2026, ported unchanged): a_bar ~ U[0.75, 3.0] g, L_eff ~ U[0.5, 1.0] x 63.7 m, "
         "log-linear blend in flight-path angle. Contact speed from kinetic energy, ground-relative, wind included, current not subtracted. "
         "Energy transferred = contact kinetic energy (upper bound); single pulse. Break-up not applied. Provisional cells: D9 no-pilot ESS 156 (Davey) "
         "and 261 (waypoints). Shallow entries above about 90 m/s extrapolate the ditching-test basis. Result status UNCHECKED.")
FOOT2 = ("Values recomputed by this module as v^2/(2s) from the printed tables; printed averages (rounded to 1/2 g) agree for 103 of 104 rows "
         "(Transport F, damaged, 12 deg: printed 1 g, recomputed 0.73 g). Model tests, calm water, Langley tank no. 2, 1948-1958. "
         "NACA RM SL55K08 (Boeing 707): not retrieved — ask Pete. The 0.45 g edge is a sensitivity, not a change of the method-1 range.")


def save_jon(fig, base, caption, odir):
    fig.savefig(f"{odir}/{base}-word.png", dpi=600)
    fig.savefig(f"{odir}/{base}.pdf")
    open(f"{odir}/{base}-caption.txt", "w").write(caption + "\n")
    im = Image.open(f"{odir}/{base}-word.png").convert("L")
    W = im.width
    try:
        font = ImageFont.truetype(matplotlib.get_data_path() + "/fonts/ttf/DejaVuSans.ttf", int(9 / 72 * 600))
    except Exception:
        font = ImageFont.load_default()
    chars = int(W / (font.getlength("x") * 1.02))
    lines = textwrap.wrap(f"Figure X. {caption}", chars)
    lh = int(9 / 72 * 600 * 1.3)
    out = Image.new("L", (W, im.height + lh * (len(lines) + 1)), 255); out.paste(im, (0, 0))
    dr = ImageDraw.Draw(out)
    for i, l in enumerate(lines):
        dr.text((0, im.height + lh // 2 + i * lh), l, fill=0, font=font)
    out.save(f"{odir}/{base}-proof.png", dpi=(600, 600))


def save_working(fig, base, title, foot, odir):
    w, h = fig.get_size_inches(); top, bot = 0.45, 1.0
    H = h + top + bot
    fig.set_size_inches(w, H)
    for a in fig.axes:
        p = a.get_position(); a.set_position([p.x0, (p.y0 * h + bot) / H, p.width, p.height * h / H])
    for lg in fig.legends:
        x, y = 0.54, 0.0
        lg.set_bbox_to_anchor((x, bot / H))
    fig.text(0.01, 1 - 0.08 / H, "\n".join(textwrap.wrap(title, 78)), fontsize=8, va="top", ha="left")
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(foot, 118)), fontsize=5.5, va="bottom", ha="left", color="0.2")
    fig.savefig(f"{odir}/{base}-working.png", dpi=200)


def main(hdir, sdir, naca_csv, odir):
    style()
    f = fig1(hdir, sdir); save_jon(f, "settling-tau90-cdf", CAP1, odir)
    save_working(f, "settling-tau90-cdf", "Energy-transfer duration at water entry, method 1: weighted distribution by 00:19 treatment", FOOT1, odir)
    plt.close(f)
    f = fig2(naca_csv); save_jon(f, "settling-abar-source-check", CAP2, odir)
    save_working(f, "settling-abar-source-check", "Source check of the shallow-entry mean deceleration range against NACA model ditchings", FOOT2, odir)
    plt.close(f)


if __name__ == "__main__":
    main(*sys.argv[1:5])
