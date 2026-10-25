"""Figures for the F-35A raw-record note. Reads out/*.csv from f35a_raw_analysis.py. Call from the kernel after
apply_figure_style() (figure-style skill) has been run; writes fig/*.png."""
import pathlib, textwrap, pickle
import numpy as np, pandas as pd, matplotlib.pyplot as plt
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "out"; FIG = ROOT / "fig"; FIG.mkdir(exist_ok=True)
ELS = ["H11N1", "H11N2", "H11N3", "H11S1", "H11S2", "H11S3"]
CN = {"H11N": "#1f5fa6", "H11S": "#c2571a"}
def foot(fig, plain, tech, y=0.0, width=170):
    t = "(i) " + plain + "\n(ii) " + tech
    fig.text(0.01, y, "\n".join(textwrap.fill(p, width) for p in t.split("\n")), ha="left", va="top", fontsize=6, color="#333333")

def fig_spectra():
    S = pd.read_csv(OUT / "f35a-raw-spectra.csv"); GD = pd.read_csv(OUT / "f35a-raw-gap-test.csv")
    import obspy
    inv = obspy.read_inventory(str(ROOT / "data/H11_resp_2019-04-09.xml")); r = inv.select(station="H11N1")[0][0][0].response
    fig, ax = plt.subplots(3, 1, figsize=(7.0, 8.2), gridspec_kw=dict(height_ratios=[3, 3, 1.3]), sharex=True)
    for el in ELS:
        g = S[S.element == el]; c = CN[el[:4]]; ls = {"1": "-", "2": "--", "3": ":"}[el[-1]]
        ax[0].plot(g.f_hz, g.arrival_psd_db, color=c, ls=ls, lw=1.0, label=f"{el} arrival")
        e = 10 * np.log10(np.clip(g.excess_esd_pa2s_hz, 1e-12, None) / 1e-12)
        ax[1].plot(g.f_hz, np.where(g.excess_esd_pa2s_hz > 0, e, np.nan), color=c, ls=ls, lw=1.0, label=el)
    g = S[S.element == "H11N1"]; h = S[S.element == "H11S1"]
    ax[0].fill_between(g.f_hz, g.bg_p05_psd_db, g.bg_p95_psd_db, color="#999999", alpha=0.25, lw=0, label="background same day, 5-95 % (H11N1)")
    ax[0].plot(g.f_hz, g.noise_pre_psd_db, color="#555555", lw=0.8, label="noise before arrival (H11N1)")
    ax[0].plot(h.f_hz, h.noise_pre_psd_db, color="#555555", lw=0.8, ls="--", label="noise before arrival (H11S1)")
    for a in ax[:2]: a.axvspan(18, 24, color="#e8d44d", alpha=0.25, lw=0)
    ax[0].set_ylabel("PSD (dB re 1 µPa²/Hz)"); ax[0].set_ylim(65, 112)
    ax[0].set_title("The arrival falls to the noise level near 20 Hz at all six hydrophones", loc="left")
    ax[0].legend(ncol=3, fontsize=6, frameon=False, loc="upper right")
    ax[1].set_ylabel("Energy spectral density above noise\n(dB re 1 µPa² s/Hz)"); ax[1].set_ylim(65, 118)
    ax[1].set_title("Received energy above noise: a 7-12 dB notch at 18-24 Hz; none is resolved at 60 Hz", loc="left")
    ax[1].legend(ncol=6, fontsize=6, frameon=False, loc="upper right")
    f = np.linspace(1.5, 118, 600); hr = np.abs(r.get_evalresp_response_for_frequencies(f, output="DEF")); h10 = np.abs(r.get_evalresp_response_for_frequencies([10.0], output="DEF"))[0]
    ax[2].plot(f, 20 * np.log10(hr / h10), color="k", lw=1.0); ax[2].set_ylim(-12, 4); ax[2].axvspan(18, 24, color="#e8d44d", alpha=0.25, lw=0)
    ax[2].set_ylabel("Instrument gain\nre 10 Hz (dB)"); ax[2].set_xlabel("Frequency (Hz)"); ax[2].set_title("The instrument response is smooth through 20 Hz (feature +0.1 dB)", loc="left")
    for a in ax: a.set_xscale("log"); a.set_xlim(1.8, 115); a.grid(True, which="both", alpha=0.25)
    ax[2].set_xticks([2, 5, 10, 20, 50, 100]); ax[2].set_xticklabels(["2", "5", "10", "20", "50", "100"])
    d20 = GD[GD.statistic == "D20"]
    foot(fig, "The graphs show the sound of the F-35A crash (9 April 2019) at the six Wake Island hydrophones. We took the records from the open archive and removed the instrument effect. Near 20 Hz the crash sound is not above the noise at all six hydrophones. The noise and the instrument have no feature at 20 Hz. Thus the gap is in the sound that arrived.",
         f"Raw IMS H11N1-3/H11S1-3 EDH (EarthScope FDSN), full StationXML response removed (pre-filt 0.5/1/110/120 Hz). Welch PSD, 1-s Hann, 50 % overlap, over the arrival window (envelope window +/-2 s, 10.3-14.0 s). Noise: 10:45-11:01 UTC; background: seven 30-min windows the same day. Excess ESD = (PSD_arrival - PSD_noise) x window. Gap depth 18-24 Hz vs mean of 12-17 and 26-34 Hz: {d20.gap_depth_excess_db.min():.1f} to {d20.gap_depth_excess_db.max():.1f} dB (bootstrap 95 % upper bounds all < -4.9 dB). Above ~45 Hz the excess is within noise scatter. Pre-registered test G1-G4 (artifact 493a290e).", y=0.0)
    fig.tight_layout(rect=(0, 0.01, 1, 1)); fig.savefig(FIG / "f35a-raw-spectra.png", dpi=300, bbox_inches="tight"); plt.close(fig)

def fig_ridge():
    RD0 = pd.read_csv(OUT / "f35a-raw-ridge.csv"); RD = RD0[(RD0.score_band_hz == "5-63") & (RD0.ram_delta != "own_new")]
    OWN = RD0[(RD0.score_band_hz == "5-63") & (RD0.ram_delta == "own_new") & (RD0.family == "F2")].sort_values("src_depth_m")
    fams = [("F2", "source falls as f⁻² (module form)", "#1f5fa6"), ("Ffit_c", "fitted slope (f⁻²·⁷ to f⁻³·⁵) with 5 Hz corner", "#2a9d5c"),
            ("Ffit", "fitted slope, no corner above 1 Hz", "#8e5bb5"), ("F4", "source falls as f⁻⁴, no corner above 1 Hz", "#c2571a")]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 4.4), sharey=True, gridspec_kw=dict(wspace=0.06))
    for ax, chn, ttl in ((axs[0], "KRAKEN_RAM", "Mode propagation with coupled-mode correction"), (axs[1], "KRAKEN_ONLY", "Mode propagation without correction")):
        for fam, lab, c in fams:
            g = RD[(RD.family == fam) & (RD.chain == chn)].sort_values("src_depth_m")
            ax.fill_between(g.src_depth_m, g.eta_low_68, g.eta_high_68, color=c, alpha=0.18, lw=0)
            ax.plot(g.src_depth_m, g.eta_pooled, "-o", color=c, ms=3, lw=1.2, label=lab)
        if chn == "KRAKEN_ONLY":
            ax.plot([2, 10, 30], [0.106, 4.43e-3, 6.79e-4], "s", mfc="white", mec="k", ms=5, label="near-field records, digitised (180-255 km)")
            ax.plot([2, 10, 30], [0.025, 1.05e-3, 1.62e-4], "x", color="k", ms=5, label="Wake records, digitised")
        else:
            ax.plot(OWN.src_depth_m, OWN.eta_pooled, "--", color="#1f5fa6", lw=1.0, label="f⁻², correction computed for each station")
            ax.plot([2, 10, 30], [0.054, 2.26e-3, 3.4e-4], "x", color="k", ms=5, label="Wake records, digitised")
        ax.axhline(1.0, color="#aa0000", lw=0.8, ls="--"); ax.text(1.05, 1.25, "all energy radiated (limit)", color="#aa0000", fontsize=6)
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xticks([1, 2, 5, 10, 20, 50]); ax.set_xticklabels(["1", "2", "5", "10", "20", "50"])
        ax.set_xlabel("Effective source depth (m)"); ax.set_title(ttl, loc="left"); ax.grid(True, which="both", alpha=0.25); ax.set_ylim(3e-5, 40)
    axs[0].set_ylabel("Coupling: radiated sound energy / impact energy")
    axs[0].legend(fontsize=6, frameon=False, loc="lower left"); axs[1].legend(fontsize=6, frameon=False, loc="lower left", handles=axs[1].get_legend_handles_labels()[0][-2:])
    fig.suptitle("The coupling needed falls by about 1,200-6,400 times as the source depth goes from 1 m to 50 m", x=0.01, ha="left", fontsize=8)
    foot(fig, "The lines show how much of the crash energy must become sound to give the recorded sound, for each source depth and source spectrum shape. A deeper source needs less. The shaded bands show the uncertainty from the crash energy, the hydrophones, the two stations and the crash position. The red line is the physical limit.",
         "D1 eta_rad = SE_obs(4-64 Hz) / [E rho c/(2 pi) sum_b W_b S_b 10^(-TL_b/10)], bands 5-63 Hz (W63 0.54), E 900 MJ (Brown et al. 2026), rho c 1025 x 1500. TL: module KRAKEN adiabatic chain (GEBCO_2026, WOA23 B5C2 April, hard bottom); left adds the module RAM-KRAKEN delta (H11S, 5-40 Hz, both triads); dashed: new pyram delta for each triad (H11N delta 0.4-2.4 dB vs H11S 1.2-3.9 dB). Source point 40.64 N 142.96 E. Families: one-pole n=2 and n=4 (tau 3.3 s, corner below 1 Hz); fitted n = 2.6-3.4 from the implied source ESD 5-40 Hz (no corner above 1 Hz); fitted corner 4.5-5.75 Hz with n 2.65-3.5 (post hoc). Bands: 68 % (energy +/-200 MJ, element, station N/S, location W vs Metz point P, in quadrature). Geometric mean of the two triads. Caveats: TL fails the 2001 airgun frequency-slope check (+10/+7 dB/octave); no detection statistic here.", y=0.0)
    fig.tight_layout(rect=(0, 0.01, 1, 0.96)); fig.savefig(FIG / "f35a-raw-ridge.png", dpi=300, bbox_inches="tight"); plt.close(fig)

def fig_envelopes():
    A = pickle.load(open(OUT / "analysis.pkl", "rb"))["OBS"]
    dig = pd.read_csv(ROOT / "H/results-data/digitised/metz2023/fig3CD_rms_envelopes_0p05s_DIGITISED.csv")
    fig, axs = plt.subplots(2, 3, figsize=(7.2, 4.4), sharey=True)
    for ax, el in zip(axs.ravel(), ELS):
        o = A[el]; g = dig[dig.element == el]; t0 = o["peak_t"]
        ax.plot(o["env_t"] - t0, o["env_L"], color=CN[el[:4]], lw=1.0, label="raw record")
        ax.plot(g.utc_s_of_day - t0, g.rms_db_re_1uPa, color="k", lw=0.8, ls="--", label="published figure, digitised")
        ax.axhline(o["noise_db"], color="#777777", lw=0.6, ls=":")
        ax.set_title(el, loc="left"); ax.grid(True, alpha=0.25); ax.set_xlim(-12, 20)
    for a in axs[1]: a.set_xlabel("Time from raw 1-s peak (s)")
    for a in axs[:, 0]: a.set_ylabel("1-s RMS level, 4-64 Hz\n(dB re 1 µPa)")
    axs[0, 0].legend(fontsize=6, frameon=False, loc="upper right")
    fig.suptitle("The raw envelopes match the digitised published envelopes to within 0.8 dB at the peak", x=0.01, ha="left", fontsize=8)
    foot(fig, "The graphs compare the sound level from the raw records with the level read from the published figure (Metz and others, 2023). The two agree. The raw peaks are 0.4-0.8 dB higher and the noise is 0.1-0.2 dB higher.",
         "Raw: full response removed, 4-pole zero-phase 4-64 Hz, 1-s boxcar mean square, 0.02-s step (Metz: 98 % overlap). Digitised: Metz et al. 2023 Fig. 3C/D vector traces resampled at 0.05 s (module results-data). Dotted line: module noise level (median outside peak +/-8 s in the Metz frame). Exposure differs by +0.22 to +0.29 dB (raw higher).", y=0.0)
    fig.tight_layout(rect=(0, 0.01, 1, 0.95)); fig.savefig(FIG / "f35a-raw-envelopes.png", dpi=300, bbox_inches="tight"); plt.close(fig)

def fig_source():
    SS = pd.read_csv(OUT / "f35a-raw-source-spectrum.csv"); FC = pd.read_csv(OUT / "f35a-raw-corner-fit.csv"); SL = pd.read_csv(OUT / "f35a-raw-source-slope.csv")
    import sys; sys.path.insert(0, str(ROOT / "H/prepare")); from imos_stageB_map import band_fraction
    z, chn = 10.0, "KRAKEN_RAM"; g = SS[(SS.src_depth_m == z) & (SS.chain == chn)]
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    for el in ELS:
        h = g[g.element == el]; c = CN[el[:4]]
        ax.plot(h[h.measured].fc_hz, h[h.measured].src_esd_db, "o", color=c, ms=3.5, alpha=0.8)
        ax.plot(h[~h.measured].fc_hz, h[~h.measured].src_esd_db, "o", mfc="none", mec=c, ms=3.5, alpha=0.6)
    pb = g[g.measured].groupby("fc_hz").src_esd_db.agg(["mean", "count"]); pb = pb[pb["count"] >= 2]
    ax.plot(pb.index, pb["mean"], "D", color="k", ms=4, label="mean of measured bands")
    f = np.array(sorted(g.fc_hz.unique())); bw = f * (2 ** (1 / 6) - 2 ** (-1 / 6))
    fcr = FC[(FC.chain == chn) & (FC.src_depth_m == z)].iloc[0]; n_fit = -SL[(SL.chain == chn) & (SL.src_depth_m == z) & (SL.band == "5-63") & (SL.who == "pooled")].src_esd_slope_db_oct.iloc[0] / (10 * np.log10(2))
    msk = np.isin(f, pb.index)
    for lab, fr, n, c in (("f⁻² (module form)", 1 / 3.2977, 2.0, "#1f5fa6"), (f"fitted f⁻{n_fit:.1f}, no corner above 1 Hz", 1 / 3.2977, n_fit, "#8e5bb5"),
                           (f"fitted f⁻{fcr.exponent_above_corner:.2f} with {fcr.corner_hz:g} Hz corner", fcr.corner_hz, fcr.exponent_above_corner, "#2a9d5c"), ("f⁻⁴", 1 / 3.2977, 4.0, "#c2571a")):
        s = 10 * np.log10(np.array([float(band_fraction(x, np.array([fr]), n)[0]) for x in f]) / bw)
        A = np.mean(pb["mean"].values - s[msk]); ax.plot(f, s + A, color=c, lw=1.1, label=lab)
    ax.set_xscale("log"); ax.set_xticks([2, 5, 10, 20, 50, 100]); ax.set_xticklabels(["2", "5", "10", "20", "50", "100"])
    ax.set_ylim(185, 250); ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Source energy spectral density at 1 m\n(dB re 1 µPa² s/Hz)")
    ax.set_title("Below 5 Hz the source energy stops rising; an f⁻⁴ form overstates it", loc="left"); ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=6, frameon=False, loc="upper right")
    foot(fig, "The points show the sound energy at the source, found from each hydrophone record and the sound loss model, for a source 10 m deep. Filled points are above the noise. The lines show four possible source shapes, each fitted to the mean points.",
         "Implied source ESD S_b = 10 log10(E_b / bw_b / 1e-12) + TL_b, z_eff 10 m, KRAKEN + module RAM delta, path from 40.64 N 142.96 E. E_b: noise-subtracted third-octave exposure (window = envelope window +/-2 s). Filled: E_b >= 2 sigma_b and window/noise >= 3 dB (blue H11N, orange H11S). Shapes: module band_fraction (flat to the corner, f^-n above, 1-500 Hz), vertical offset fitted to the mean of measured bands (n >= 2 elements). Corner fit 3.15-40 Hz is post hoc. Airgun frequency-slope caveat applies (TL slope error would bias n).", y=0.0, width=130)
    fig.tight_layout(rect=(0, 0.01, 1, 1)); fig.savefig(FIG / "f35a-raw-source-spectrum.png", dpi=300, bbox_inches="tight"); plt.close(fig)
