"""Charts for the whole-arc TL grid note (block 2): (1) transmission loss against latitude per receiver, blocked bands
marked; (2) detectable fraction against latitude per receiver and coupling efficiency. Chart rule of 10 Oct: no project
jargon in titles, axes or legends; two footnotes (plain ASD-STE100, technical). PNG + PDF via fig.savefig.
Usage: python tl_grid_charts.py <table_dir> <evidence_dir> <out_dir> [--stamp "<provenance>"]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

NAMES = {"H01W": "Cape Leeuwin H01W (IMS triad)", "H08S": "Diego Garcia South H08S (IMS triad)", "H08N": "Diego Garcia North H08N (IMS triad)",
         "3315": "Perth Canyon logger 3315", "3376": "Perth Canyon logger 3376", "3250": "Scott Reef logger 3250",
         "3274": "Portland logger 3274", "3275": "Portland logger 3275"}
ORDER = ["H01W", "H08S", "H08N", "3315", "3376", "3250", "3274", "3275"]
SHOW_BANDS = [5.0, 10.0, 20.0, 40.0]
BAND_COL = {5.0: "#1b2a6b", 10.0: "#2f6fb6", 20.0: "#5aa5d6", 40.0: "#a3cde3"}
ETA_COL = {1e-2: "#4a1486", 1e-3: "#7a51a8", 1e-4: "#a98fc9", 1e-5: "#d4c6e6"}


def style():
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6,
                         "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "figure.dpi": 150})


def footnotes(fig, plain, tech, y0=0.005):
    t = textwrap.fill("Technical note: " + tech, 235); n = t.count("\n") + 1
    fig.text(0.01, y0, t, fontsize=6, va="bottom", color="#333333", linespacing=1.25)
    fig.text(0.01, y0 + 0.0115 * n + 0.012, textwrap.fill("Plain-language note: " + plain, 235), fontsize=6, va="bottom", color="#333333", linespacing=1.25)


def ridge_shade(ax, ims):
    r = ims[(ims.offset_nm == 0) & ims.ridge_source].lat.unique()
    for la in r:
        ax.axvspan(-la - 0.25, -la + 0.25, color="#fbe3c8", zorder=0, lw=0)


def chart_tl(table_dir, out, stamp):
    ims = pd.read_csv(table_dir / "ims_tl_kraken_arc.csv"); imo = pd.read_csv(table_dir / "imos_tl_ramcorr_arc.csv", dtype={"logger": str})
    rd = pd.read_csv(pathlib.Path(__file__).resolve().parent.parent / "results-data/near_limits/ims_ram_delta.csv")
    frames = []
    for st in ("H01W", "H08S", "H08N"):
        g = ims[ims.station == st].rename(columns={"station": "receiver"}).copy()
        if st != "H08N":
            dd = rd[(rd.path == f"imp500_{st}") & np.isclose(rd.src_depth_m, 10.0)].set_index("fc_hz").delta_db
            g["tl_db"] = g.tl_db - np.interp(np.log10(g.fc_hz), np.log10(dd.index.values), dd.values)
        frames.append(g)
    frames.append(imo.rename(columns={"logger": "receiver"}))
    d = pd.concat(frames, ignore_index=True); d = d[np.isclose(d.src_depth_m, 10.0)]
    offs = sorted(d.offset_nm.unique())
    fig, axes = plt.subplots(2, 4, figsize=(13, 8.2), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.87, bottom=0.24, wspace=0.08, hspace=0.3)
    for ax, rec in zip(axes.ravel(), ORDER):
        g = d[d.receiver == rec]; ridge_shade(ax, ims)
        for fc in SHOW_BANDS:
            for off in offs:
                h = g[(g.fc_hz == fc) & (g.offset_nm == off)].sort_values("lat")
                lw, al = (1.6, 1.0) if off == 0 else (0.7, 0.45)
                ax.plot(-h.lat, h.tl_db, color=BAND_COL[fc], lw=lw, alpha=al, label=f"{fc:g} Hz" if (off == 0 and rec == "H01W") else None)
                if off == 0:
                    bl = h[~np.isfinite(h.tl_db)]
                    if len(bl):
                        ax.plot(-bl.lat, np.full(len(bl), 262 - 4 * SHOW_BANDS.index(fc)), ls="none", marker="x", ms=3.5, mew=0.8, color=BAND_COL[fc])
        ax.set_title(NAMES[rec], loc="left")
        ax.set_xlim(41.5, 19.5); ax.set_ylim(100, 265); ax.grid(alpha=0.25, lw=0.5)
        ax.axhspan(246, 265, color="#f2f2f2", zorder=0)
        if rec == "H01W":
            ax.text(41.2, 263.5, "x = band blocked (no sound reaches the receiver)", fontsize=6, va="top", color="#444444")
            ax.text(41.2, 104, "orange band = source over Broken Ridge (< 2,000 m water)", fontsize=6, va="bottom", color="#8a5a1e")
    for ax in axes[1]:
        ax.set_xlabel("Latitude of the sound source on the 7th arc (°S)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Transmission loss (dB re 1 m)")
    h, l = axes[0, 0].get_legend_handles_labels()
    side = ", ".join(f"{int(abs(o))}" for o in sorted({abs(o) for o in offs if o != 0}))
    fig.legend(h, l, loc="upper right", ncol=4, bbox_to_anchor=(0.99, 0.945), title=f"Frequency band (third octave); thick line = on the arc, thin lines = {side} NM either side")
    fig.suptitle("Sound transmission loss from the 7th arc to each receiver, by source latitude: Diego Garcia North is blocked from almost everywhere, Scott Reef from south of 29.5°S",
                 x=0.01, ha="left", fontsize=9)
    footnotes(fig,
              "Each line shows how much the sound from an impact on the 7th arc is reduced on its way to one receiver, for sources from 41°S to 20°S. "
              "A higher value means a weaker arriving sound. A cross means the sea floor is too shallow somewhere on the path for that frequency, so the model "
              "sends no sound through. The thin lines are for sources 30 (and, where drawn, 60) nautical miles west and east of the arc. In the orange band the source sits over "
              "Broken Ridge in water less than 2,000 m deep; the model then lets more sound into the deep channel, and this part of the model is not validated. "
              "Values are estimates from a model of the ocean; they are not measurements, and the model is not yet calibrated.",
              "KRAKEN adiabatic incoherent modes along the WGS84 geodesic, GEBCO_2026 bathymetry (5 km profiles, median of 3x3 cells), WOA23 2005-2014 March "
              "sound speed, hard bottom (cp 1650, rho 1.9, 0.5 dB/lambda), Francois-Garrison absorption, spherical correction; source 10 m; receiver at the "
              "triad hydrophone depth (IMS) or 2 m above the seabed (IMOS). IMS values have the module's RAM delta subtracted (ims_ram_delta.csv, H01W/H08S "
              "only); IMOS values carry the module's RAM correction (ram_tl_check rule 2; none for 3250). Blocked = KRAKEN finds no propagating mode on a profile "
              "(or land on track, or zero field at the receiver); at Portland the 5 Hz line is the RAM reference value that rule 2 assigns to a no-mode band. ridge_source rows (orange) "
              "are flagged (reach gap G-N2/K5); at Portland their RAM-corrected value is floored at the reference RAM value (tl_grid_table.py). Arc = zero contour of the project's arc-distance field (searched-areas arc-grid.npz); offsets "
              "in that field. Caveats C1 (slope misfit +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling not calibrated). " + stamp)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"hydroacoustics-tl-grid-run-j-tl-vs-latitude.{ext}", dpi=200 if ext == "png" else None)
    plt.close(fig)


def chart_detect(ev_dir, out, stamp, a_table):
    d = pd.read_csv(ev_dir / "evidence_alone.csv", dtype={"receiver": str}); d = d[d.offset_nm == 0]
    nz = json.loads((ev_dir / "noise_levels.json").read_text())
    ims = pd.read_csv(pathlib.Path(a_table) / "ims_tl_kraken_arc.csv")
    fig, axes = plt.subplots(2, 4, figsize=(13, 8.2), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.87, bottom=0.24, wspace=0.08, hspace=0.3)
    for ax, rec in zip(axes.ravel(), ORDER):
        g = d[d.receiver == rec]; ridge_shade(ax, ims)
        for eta in sorted(g.eta.unique(), reverse=True):
            h = g[g.eta == eta].sort_values("lat")
            ax.plot(-h.lat, h.frac_pd, color=ETA_COL[eta], lw=1.6, label=f"{eta:g}" if rec == "H01W" else None)
            ax.plot(-h.lat, h.frac_above_noise_hi, color=ETA_COL[eta], lw=0.7, ls="--", alpha=0.8)
        ax.set_title(NAMES[rec], loc="left"); ax.set_xlim(41.5, 19.5); ax.set_ylim(-0.03, 1.03); ax.grid(alpha=0.25, lw=0.5)
    for ax in axes[1]:
        ax.set_xlabel("Latitude of the impact on the 7th arc (°S)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Share of simulated impacts detectable")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper right", ncol=4, bbox_to_anchor=(0.99, 0.945),
               title="Share of impact energy that becomes sound (coupling efficiency); solid = detection probability, dashed = level above the 90-95 % noise")
    fig.suptitle("Share of simulated impacts that would be detectable at each receiver: appreciable only for a coupling efficiency of 0.001 or more, and smaller north of 30°S",
                 x=0.01, ha="left", fontsize=9)
    footnotes(fig,
              "For an impact at each latitude on the 7th arc, the chart shows the share of simulated impacts whose sound would be strong enough to detect at the "
              "receiver, for four assumed values of the share of impact energy that becomes sound. The impact energies come from the project's end-of-flight "
              "simulation (run J). The dashed line uses a stricter rule: the sound must be above the loudest 5-10 % of the background noise. In the orange band the "
              "source sits over Broken Ridge (water less than 2,000 m deep), where the model is not validated. These are model predictions, not detections; the "
              "sound-loss model is not yet calibrated.",
              "Source posterior run J (one seed per stratum, equal stratum weights, prior weight = 00:19 held out, n = %d draws of E = contact kinetic energy and "
              "tau90; tau_ac = tau90 clamped 0.05-10 s, k = 1). Received 5-40 Hz peak 1 s SPL = sum_b eta E rho c/(2 pi) S_b(f_c, 1/tau) 10^(-TL_b/10) / T_eff, "
              "T_eff = %.2f s (T_C2), f^-2 spectrum, TL at 10 m source from the grid (IMS: KRAKEN - RAM delta; IMOS: RAM-corrected). Solid: mean stage-A logistic "
              "P_D(SNR) (3376 fit for Perth Canyon, 3274 fit for Portland, 3250 fit for Scott Reef; IMS BORROWED 3274 fit + 4.8 dB triad gain), SNR against the "
              "noise median (IMOS: imos2b background median; IMS: 3376 proxy + Blackman App. B offset, digitised 2003). Dashed: share of draws above the noise "
              "p95 (IMOS, imos1d 1 s percentiles) or p90 (IMS, Blackman panel spread). eta = 1e-2 and 1e-3 exceed the F-35A upper anchor 2.1e-4 and are shown "
              "as the swept range asked for. PREDICTIVE, NOT CALIBRATED; caveats C1, C2. " % (nz["n_draws"], nz["t_eff_s"]) + stamp)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"hydroacoustics-tl-grid-run-j-detectable-fraction.{ext}", dpi=200 if ext == "png" else None)
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("table_dir"); ap.add_argument("ev_dir"); ap.add_argument("out"); ap.add_argument("--stamp", default="")
    a = ap.parse_args(); style(); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    chart_tl(pathlib.Path(a.table_dir), out, a.stamp); chart_detect(pathlib.Path(a.ev_dir), out, a.stamp, a.table_dir)
