"""Block 7 charts (operating note rule 9: no project jargon in titles/axes/legends; two footnotes).
  hydroacoustics-injection-recovery-run-j-pd  : detection probability against received level per receiver and detector
  hydroacoustics-injection-recovery-run-j-eta : coupling efficiency at which detection becomes even odds, by latitude band
Usage: python charts.py <run_dir> <eta_dir> <inputs.json> <results_dir>
"""
from __future__ import annotations
import json, sys, textwrap
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import prereg as R

NAMES = {"3376": "Perth Canyon logger 3376", "3315": "Perth Canyon logger 3315", "3274": "Portland logger 3274", "3275": "Portland logger 3275",
         "H01W": "Cape Leeuwin (H01W), proxy noise", "H08S": "Diego Garcia South (H08S), proxy noise"}
MLAB = {"M1b_mf_envelope": "envelope matched filter", "M0a_stalta": "STA/LTA ratio", "M0b_bandenergy": "band energy"}
COL = {"M1b_mf_envelope": "#1f4e9c", "M0a_stalta": "#c87d2a", "M0b_bandenergy": "#7a7a7a"}


def foot(fig, plain, tech):
    fig.text(0.01, 0.055, "\n".join(textwrap.wrap("(i) " + plain, 190)), fontsize=6.5, va="bottom", ha="left", color="#333")
    fig.text(0.01, 0.005, "\n".join(textwrap.wrap("(ii) " + tech, 190)), fontsize=6.0, va="bottom", ha="left", color="#555")


def chart_pd(run_dir, out, inp):
    PD = pd.read_csv(run_dir / "pd_vs_level.csv", dtype={"receiver": str}); S = json.load(open(run_dir / "summary.json"))
    taus = S["taus"]; tau_mid = taus[1]
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 8.6), sharex=True, sharey=True)
    for ax, rx in zip(axes.ravel(), R.RECEIVERS):
        g = PD[(PD.receiver == rx) & np.isclose(PD.tau_s, tau_mid) & np.isclose(PD.alpha, R.ALPHA_PRIMARY)]
        for name in R.METHODS:
            h = g[g.method == name].sort_values("level_re_noise_db")
            ax.fill_between(h.level_re_noise_db, h.ci_lo, h.ci_hi, color=COL[name], alpha=0.12, lw=0)
            ax.plot(h.level_re_noise_db, h.pd, "-o", ms=3, lw=1.4 if name == R.PRIMARY_METHOD else 1.0, color=COL[name], label=MLAB[name])
        # tau spread for the primary method
        for t, ls in zip((taus[0], taus[2]), (":", "--")):
            h = g0 = PD[(PD.receiver == rx) & np.isclose(PD.tau_s, t) & np.isclose(PD.alpha, R.ALPHA_PRIMARY) & (PD.method == R.PRIMARY_METHOD)].sort_values("level_re_noise_db")
            ax.plot(h.level_re_noise_db, h.pd, ls, lw=0.9, color=COL[R.PRIMARY_METHOD], alpha=0.8, label=f"matched filter, source duration {t:.2g} s" if rx == R.RECEIVERS[0] else None)
        ax.axhline(0.5, color="#999", lw=0.6, ls="-"); ax.axvline(0, color="#999", lw=0.6)
        nw = S["n_null_windows"][rx]; bg = S["background"][rx]
        ax.set_title(f"{NAMES[rx]}\n{nw:,} background windows ({'own recordings' if bg.startswith('own') else 'shaped IMOS proxy'})", fontsize=9, loc="left")
        ax.set_ylim(-0.03, 1.03); ax.set_xlim(-21, 31); ax.margins(0.04)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes[1]:
        ax.set_xlabel("Received peak level relative to the background median (dB)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Probability of detection")
    axes[0, 0].legend(frameon=False, fontsize=7, loc="upper left")
    fig.suptitle(f"How loud an impact signal must be to be detected on each recorder, at a false-alarm rate of 1 in 100 per minute (source duration {tau_mid:.2g} s)", fontsize=11, x=0.01, ha="left")
    foot(fig, "Each curve shows the share of synthetic impact signals that a detector found when the signal was added to real recorded background noise at the "
              "level on the horizontal axis. 0 dB means the signal peak is as loud as the usual background. The band is the 95 % confidence interval. The Cape Leeuwin and "
              "Diego Garcia panels use a stand-in background made from Perth Canyon recordings, because the real recordings are not held. Estimates only.",
         f"Block 7 injection-recovery, prereg e816313 (prepare/injection_recovery_run_j). Source posterior = end of flight run J (74 seeds + supplement not used here); "
         f"tau quantiles 5/50/95 % under 00:19 Held Out (D0'), p = 0.5: {taus[0]:.2f}/{taus[1]:.2f}/{taus[2]:.2f} s; dispersion = KRAKEN broadband on the representative "
         f"deep-water profile at the run J 5/50/95 % ranges per receiver (bank of 9 templates). Level = peak 1 s 5-40 Hz band level minus the background median 1 s level. "
         f"alpha = 0.01 per 60 s window; thresholds from the null of window maxima; N = {R.N_INJ['3376']} injections per cell at 3376, 60 elsewhere; Wilson 95 % CI. "
         f"Backgrounds: 3376/3274 IMOS 14-day set; 3315/3275 own 8 March recordings outside the request window; H01W/H08S = IMOS 3376 shaped to Blackman (2004) App. B "
         f"2003 median PSD (DIGITISED), single hydrophone, no triad gain. Caveats C1 (propagation slope misfit +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling "
         f"efficiency not calibrated; eta swept over four decades, F-35A upper anchor). PREDICTIVE, NOT CALIBRATED.")
    fig.tight_layout(rect=(0, 0.10, 1, 0.95))
    for ext in ("png", "pdf"):
        fig.savefig(out / f"hydroacoustics-injection-recovery-run-j-pd.{ext}", dpi=200)
    plt.close(fig)


def chart_eta(eta_dir, out, inp):
    E = json.load(open(eta_dir / "eta_map.json")); lb = pd.read_csv(eta_dir / "eta50_by_lat_band.csv")
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12.0, 5.2), gridspec_kw=dict(width_ratios=[1.3, 1]))
    mid = (lb.lat_lo + lb.lat_hi) / 2
    ok = lb.eta50.notna()
    ax.plot(mid[ok], lb.eta50[ok], "o-", color="#1f4e9c", ms=4, lw=1.3, label="coupling efficiency at which detection is even odds")
    ax.axhline(R.ETA_ANCHOR, color="#c87d2a", lw=1.0, ls="--", label="F-35A crash value (upper anchor)")
    miss = lb[~ok & (lb.n > 0)]
    if len(miss):
        ax.plot((miss.lat_lo + miss.lat_hi) / 2, np.full(len(miss), R.ETA_BOUNDS[1]), "v", color="#999", ms=5, label="not reached below 10⁻²")
    ax.set_yscale("log"); ax.set_ylim(5e-9, 2e-2); ax.set_xlim(-41.5, -19.5)
    ax.set_yticks([1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]); ax.set_yticklabels(["10⁻⁸", "10⁻⁷", "10⁻⁶", "10⁻⁵", "10⁻⁴", "10⁻³", "10⁻²"])
    ax.set_xlabel("Impact latitude (°, negative = south)"); ax.set_ylabel("Coupling efficiency (fraction of impact energy radiated as sound)")
    ax.set_title("Impacts near 37 °S need the least coupling to be detected; the north needs more", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=7.5, loc="upper left"); ax.spines[["top", "right"]].set_visible(False)
    ax1b = ax.twinx(); ax1b.bar(mid, lb.share, width=0.9, color="#dddddd", zorder=0, alpha=0.7); ax1b.set_ylim(0, lb.share.max() * 4 if lb.share.max() > 0 else 1)
    ax1b.set_ylabel("Share of impact probability in the latitude band", color="#777"); ax1b.tick_params(axis="y", colors="#777"); ax1b.spines[["top"]].set_visible(False)
    ax.set_zorder(ax1b.get_zorder() + 1); ax.patch.set_visible(False)
    # right: P_D(any) vs eta decade per option (D0', D2, D3, D4 at p 0.5), primary alpha, with calibration error
    dec = [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    labels = {"D0": "00:19 data held out", "D2": "R600 BTO + BFO", "D3": "both BFOs as recorded", "D4": "both BFOs, shared start-up offset"}
    for o, c in zip(R.OPTIONS, ["#1f4e9c", "#c87d2a", "#2a9d8f", "#7a7a7a"]):
        k = f"{o}/p0.5|alpha{R.ALPHA_PRIMARY}|cal"
        v = [E["pd_any_by_decade"][k][f"{d:.0e}"] for d in dec]
        ax2.plot(dec, v, "o-", ms=3.5, lw=1.2, color=c, label=labels[o])
    ax2.axvline(R.ETA_ANCHOR, color="#c87d2a", lw=1.0, ls="--"); ax2.axhline(0.5, color="#999", lw=0.6)
    ax2.set_xscale("log"); ax2.set_xticks(dec); ax2.set_xticklabels(["10⁻⁸", "10⁻⁷", "10⁻⁶", "10⁻⁵", "10⁻⁴", "10⁻³", "10⁻²"])
    ax2.set_xlabel("Coupling efficiency"); ax2.set_ylabel("Probability that at least one recorder detects the impact"); ax2.set_ylim(-0.03, 1.03)
    ax2.set_title("Detection by any recorder against coupling, per 00:19 data option", fontsize=10, loc="left")
    ax2.legend(frameon=False, fontsize=7.5, loc="upper left"); ax2.spines[["top", "right"]].set_visible(False)
    e50 = E["eta50"][f"D0/p0.5|alpha{R.ALPHA_PRIMARY}|cal"]["eta50"]
    foot(fig, "Left: for impacts in each one-degree latitude band, the fraction of the impact's energy that would have to become sound for there to be a 50 % chance that "
              "at least one recorder detects it (lower = easier to detect). Grey bars show where the flight model puts the impact. Right: the chance of a detection by any recorder "
              "as the coupling fraction is varied, for the four ways of using the last satellite data. The dashed line is the one measured aircraft crash. Estimates only; the "
              "sound loss along each path is provisional and the coupling of a 777 impact has never been measured.",
         f"Block 7 eta mapping (eta_map.py). Source posterior = run J, 1-in-4 thin of a 74-seed chunk subsample ({E['n_rows']:,} rows), p = 0.5 (left) and per option at p = 0.5 "
         f"(right); weights = EoF total q = 1/3 cell with survival factor, p_core pooling. SPL = 10 log10(eta E rho c / 2 pi sum_b S_b(tau) 10^(-TL_b/10) / T_eff / 1e-12), E = contact "
         f"KE, one-pole source (f^-2 above 1/tau), tau = tau90 (method 1), T_eff from this block's templates; TL = block 2 grid pass A (PROVISIONAL, on-arc sources, source 10 m) "
         f"+ RAM-KRAKEN band deltas for the IMOS loggers; calibration error L ~ N(0, 10 dB) per row; H01W/H08S +4.8 dB triad gain (labelled); P_D from this block's M1b logistic "
         f"fits at alpha 0.01 per 60 s window; P_D(any) = 1 - prod(1 - P_D_r) over 3376, 3274, 3315, 3275, H01W, H08S; H08N blocked, 3250 no-information. eta_50 (D0', p 0.5, "
         f"with cal error) = {e50 if e50 is None else f'{e50:.2e}'}. Rows north of 20 S: TL pending (grid). Caveats C1, C2. PREDICTIVE, NOT CALIBRATED.")
    fig.tight_layout(rect=(0, 0.14, 1, 0.97))
    for ext in ("png", "pdf"):
        fig.savefig(out / f"hydroacoustics-injection-recovery-run-j-eta.{ext}", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    run_dir, eta_dir, inputs_json, results = map(Path, sys.argv[1:5]); results.mkdir(parents=True, exist_ok=True)
    inp = json.load(open(inputs_json))
    chart_pd(run_dir, results, inp); chart_eta(eta_dir, results, inp); print("charts done")
