"""Block 11 charts (prereg section 12): (1) latitude distributions core / combined / hydroacoustics alone per 00:19 option;
(2) probability of no detection against coupling efficiency per 5-degree band with the 95 % limits. PNG + PDF, two footnotes.
Usage: python charts.py <reduce_out_dir> <results_dir> <commit_tag>
"""
from __future__ import annotations
import json, sys, textwrap
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R

plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "figure.dpi": 200, "savefig.dpi": 200})
OPT = {"D0": "00:19 data held out", "D2": "00:19 BTO + BFO as recorded", "D3": "00:19 both BFOs as recorded (Holland H2)", "D4": "00:19 both BFOs, shared offset (Holland H1)"}
C_CORE, C_COMB, C_ALONE, C_IMS = "#9a9a9a", "#1f4e9c", "#c8701a", "#6aa0d8"


def footnotes(fig, plain, tech, y0=0.005, width=215):
    t2 = textwrap.fill("Technical note: " + tech, width); n2 = t2.count("\n") + 1
    h_in = fig.get_size_inches()[1]; line = 6 * 1.35 / 72 / h_in          # line height in figure fraction at 6 pt
    fig.text(0.01, y0, t2, fontsize=6, va="bottom", ha="left", color="#333333")
    fig.text(0.01, y0 + n2 * line + 0.012, textwrap.fill("Plain-language note: " + plain, width), fontsize=6, va="bottom", ha="left", color="#333333")


def check_overlaps(fig):
    fig.canvas.draw(); r = fig.canvas.get_renderer()
    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(matplotlib.text.Text) if t.get_text().strip() and t.get_visible()]
    bad = [(a.get_text()[:30], b.get_text()[:30]) for i, (a, ba) in enumerate(texts) for b, bb in texts[i + 1:] if ba.overlaps(bb)]
    return bad


def chart_evidence(out, res, tag):
    z = np.load(out / "latitude_distributions.npz"); ev = pd.read_csv(out / "evidence_three_ways.csv")
    fig, axes = plt.subplots(1, 4, figsize=(11.5, 4.9), sharey=True); fig.subplots_adjust(left=0.06, right=0.99, top=0.80, bottom=0.42, wspace=0.08)
    nd = json.load(open(out / "nd_alone_1deg.json"))
    for ax, o in zip(axes, R.OPTIONS):
        k = f"{o}/p0.5|a0.05|imos|"; mid = z[k + "mid"]; core = z[k + "core"]; comb = z[k + "combined"]; alone = z[k + "alone"]
        combi = z[f"{o}/p0.5|a0.05|ims|combined"]
        sel = (mid >= -41.5) & (mid <= -19.5)
        ax.fill_between(mid[sel], 0, core[sel], step="mid", color=C_CORE, alpha=0.55, lw=0, label="end-of-flight posterior alone")
        ax.step(mid[sel], comb[sel], where="mid", color=C_COMB, lw=1.4, label="with the four IMOS recorders (gate passed)")
        ax.step(mid[sel], combi[sel], where="mid", color=C_IMS, lw=0.9, ls=":", label="with IMOS + Cape Leeuwin / Diego Garcia stand-in noise (sensitivity)")
        ax.step(mid[sel], alone[sel], where="mid", color=C_ALONE, lw=1.1, ls="--", label="hydroacoustics alone, flat prior along the arc")
        xb = np.array(nd["band_mid"]); yb = np.array(nd[f"{o}/p0.5"]) / 2.0     # 1-degree bands scaled to the 0.5-degree bin height
        ax.step(xb, yb, where="mid", color="#7a4a10", lw=0.8, ls="-.", label="hydroacoustics alone, non-detections only (1° bands)")
        e = ev[(ev.option == o) & (ev.p == 0.5) & (ev.alpha == 0.05) & (ev.receivers == "IMOS gated")].iloc[0]
        ax.set_title(OPT[o] + f"\nmedian shift {e.shift_median_deg:+.2f}°; mass north of 33°S {e.mass_north_33S_core:.3f} → {e.mass_north_33S_combined:.3f}", loc="left", fontsize=6.5)
        ax.set_xlim(-41.5, -19.5); ax.set_xticks([-40, -35, -30, -25, -20]); ax.set_xticklabels(["40", "35", "30", "25", "20"]); ax.margins(y=0.05)
        ax.set_xlabel("Latitude of the impact on the 7th arc (°S)")
    axes[0].set_ylabel("Probability per 0.5° bin")
    h, l = axes[0].get_legend_handles_labels(); fig.legend(h, l, loc="upper left", bbox_to_anchor=(0.06, 0.945), ncol=3, fontsize=6.5)
    sh = [abs(ev[(ev.option == o) & (ev.p == 0.5) & (ev.alpha == 0.05) & (ev.receivers == "IMOS gated")].iloc[0].shift_median_deg) for o in R.OPTIONS]
    fig.suptitle(f"At dive probability 0.5, adding the hydroacoustic result moves the end-of-flight latitude distribution by {min(sh):.2f}–{max(sh):.2f}°;\nthe bumps near 33–36°S come from two time-matched Portland candidates that are too loud to be the aircraft (amplitude-blind matching)", x=0.01, ha="left", y=0.998, fontsize=8.5)
    e0 = ev[(ev.option == "D0") & (ev.p == 0.5) & (ev.alpha == 0.05) & (ev.receivers == "IMOS gated")].iloc[0]
    footnotes(fig,
              f"Grey: where the flight simulation (run J) puts the impact, by latitude. Blue: the same after multiplying by the chance that the four Australian sea-floor recorders would have heard, or not heard, each simulated impact at the times their recordings were running; the sound-coupling share is unknown and is averaged over 1e-6 to 1e-2. Orange: what the recorders say on their own if every latitude were equally likely beforehand. Dotted: adds the two deep-ocean stations with stand-in noise. The recorders were running about a third of the time, so most impacts could not have been heard at all. Dive probability 0.5. These are model predictions; no detection is claimed.",
              f"Source posterior run J (74 seeds + northern supplement, p_core strata mix, seeds pooled by evidence), p = 0.5, per 00:19 option; module likelihood per row L = prod_r [(1 - P_D,r) + P_D,r m_r/beta_r], M1b, alpha = 0.05 per 55 s window, P_D from block 7 injection-recovery fits on own IMOS backgrounds (3376, 3315, 3274, 3275), TL block 2 arc grid (41-20 S; IMOS: RAM along the grid, imos_tl_ram_arc.csv, amendment A4), E = contact KE, tau = tau90 (EoF method 1), calibration error N(0, 10 dB), eta marginalised log-uniform [1e-6, 1e-2]; 'alone' = bin mean of exp(lnL) over bins with mass; KL(core||combined) D0' = {e0.KL_core_vs_combined_nats:.4f} nats. IMS stand-in = IMOS 3376 shaped to Blackman 2003 (digitised), +4.8 dB triad gain. PREDICTIVE, NOT CALIBRATED; caveats C1 (propagation slope misfit +10.4/+7.4 dB/oct at H01W/H08S) and C2 (coupling efficiency not calibrated, F-35A upper anchor 2.1e-4). Block 11 prereg 90d7181 + A4 e13a32e; {tag}.")
    bad = check_overlaps(fig)
    for ext in ("png", "pdf"): fig.savefig(res / f"hydroacoustics-composition-run-j-evidence.{ext}")
    plt.close(fig); return bad


def chart_limits(out, res, tag):
    ul = pd.read_csv(out / "upper_limits.csv"); summ = json.load(open(out / "summary.json"))
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0), gridspec_kw=dict(width_ratios=[1.25, 1])); fig.subplots_adjust(left=0.06, right=0.99, top=0.86, bottom=0.40, wspace=0.30)
    ax = axes[0]; cols = plt.cm.viridis(np.linspace(0.1, 0.9, 5)); bands = [(-41, -36), (-36, -31), (-31, -26), (-26, -21)]
    # P(no detection | eta) per band from the streamed sums is not stored per eta in the csv: recompute from the merged subsample (declared: 1-in-125)
    for (lo, hi), c in zip(bands, cols):
        row = ul[(ul.option == "D0") & (ul.p == 0.5) & (ul.alpha == 0.05) & (ul.receivers == "IMOS gated") & (ul.lat_lo == lo) & (ul.lat_hi == hi)].iloc[0]
        xs = [1e-4, R.ETA_ANCHOR, 1e-3, 1e-2]; ys = [row["pnd_at_1e-4"], row["pnd_at_anchor"], row["pnd_at_1e-3"], row["pnd_at_1e-2"]]
        ax.plot(xs, ys, "-o", color=c, lw=1.3, ms=3.5, label=f"{-lo}–{-hi}°S (share {row['share']:.3f}, n_eff {row['ess']:.0f})")
    row = ul[(ul.option == "D0") & (ul.p == 0.5) & (ul.alpha == 0.05) & (ul.receivers == "IMOS gated") & (ul.lat_lo == -41) & (ul.lat_hi == -20)].iloc[0]
    ax.plot([1e-4, R.ETA_ANCHOR, 1e-3, 1e-2], [row["pnd_at_1e-4"], row["pnd_at_anchor"], row["pnd_at_1e-3"], row["pnd_at_1e-2"]], "-s", color="black", lw=1.6, ms=4, label="all latitudes 41–20°S")
    ax.axhline(0.05, color="#b03030", lw=0.8, ls="--"); ax.text(1.3e-2, 0.07, "95 % exclusion needs 0.05", fontsize=6, color="#b03030", ha="right")
    ax.axvline(R.ETA_ANCHOR, color="#777777", lw=0.8, ls=":"); ax.text(R.ETA_ANCHOR * 1.08, 0.98, "F-35A upper anchor", fontsize=6, color="#555555", va="top")
    ax.set_xscale("log"); ax.set_xlim(7e-5, 1.4e-2); ax.set_ylim(0, 1.02); ax.set_xlabel("Share of impact energy that becomes sound (coupling efficiency)")
    ax.set_ylabel("Probability that no recorder detects the impact")
    ax.set_title(f"a  Even at a coupling efficiency of 0.01 the recordings held\n    miss the impact about {100 * row['pnd_at_1e-2']:.0f} % of the time", loc="left", fontsize=7.5)
    ax.legend(loc="lower left", fontsize=6, bbox_to_anchor=(0.0, 0.08))
    ax = axes[1]
    sel = ul[(ul.p == 0.5) & (ul.alpha == 0.05) & (ul.receivers == "IMOS gated") & (ul.lat_lo == -41) & (ul.lat_hi == -20)]
    y = np.arange(len(sel)); ax.barh(y, 0, color="none")
    for i, (_, r) in enumerate(sel.iterrows()):
        ax.plot([r["eta95_bayes_nondetection_logu_1e-6_1e-2"]], [i], "o", color=C_COMB, ms=5)
        ax.plot([r["eta95_bayes_full_likelihood"]], [i], "s", color=C_ALONE, ms=4, mfc="none")
    ax.axvline(sel["eta95_prior_alone"].iloc[0], color="#777777", lw=0.9, ls="--"); ax.text(sel["eta95_prior_alone"].iloc[0] * 0.97, len(sel) - 0.55, "prior alone (log-uniform, 1e-6 to 1e-2): 6.3e-3", fontsize=6, ha="right", color="#555555")
    SHORT = {"D0": "00:19 held out", "D2": "BTO + BFO", "D3": "both BFOs (H2)", "D4": "both BFOs, offset (H1)"}
    ax.set_yticks(y); ax.set_yticklabels([SHORT[o] for o in sel.option]); ax.set_xscale("log"); ax.set_xlim(1e-3, 1.2e-2); ax.set_ylim(-0.6, len(sel) - 0.2)
    ax.set_xlabel("95 % upper limit on the coupling efficiency (posterior quantile)")
    ax.set_title("b  The 95 % upper limit sits near the prior's own:\n    the non-detection constrains little", loc="left", fontsize=7.5)
    ax.plot([], [], "o", color=C_COMB, label="from the non-detections only"); ax.plot([], [], "s", color=C_ALONE, mfc="none", label="full likelihood incl. time-matched candidates"); ax.legend(loc="lower left", fontsize=6)
    fig.suptitle("The Australian sea-floor recordings held cannot exclude any coupling efficiency in the swept range at 95 %", x=0.01, ha="left", y=0.995, fontsize=9)
    footnotes(fig,
              f"(a) For impacts in each latitude band of the flight simulation, the chance that all four recorders would have missed the sound, against the share of impact energy that becomes sound. The recorders ran for 5 minutes in every 15 and only two of them cover each arrival, so even a loud impact is missed about {100 * row['pnd_at_1e-2']:.0f} % of the time. (b) The upper limit on the coupling efficiency that the absence of a detection allows, with 95 % probability, for each treatment of the 00:19 satellite data; it is almost the same as the limit implied by the assumed range alone. Dive probability 0.5. No detection is claimed.",
              f"Run J, p = 0.5, alpha = 0.05 (M1b), P_D from block 7 injection-recovery on own backgrounds; P(no detection | eta) = weighted mean over impacts of prod_r (1 - P_D,r) with P_D,r = 0 outside the scored IMOS windows; (b) posterior 95 % quantile under the log-uniform prior on [1e-6, 1e-2] with the non-detection likelihood (filled) and the full likelihood including the amplitude-blind time matches at Portland 3275 (open; gap G11-1); classical 95 % exclusion not reached below 1e-2 in any band. Bands: 1-degree streamed sums over all 313.6 M rows + supplement. PREDICTIVE, NOT CALIBRATED; C1, C2; TL arc grid (IMOS: RAM along the grid, imos_tl_ram_arc.csv, amendment A4). Block 11 prereg 90d7181 + A4 e13a32e; {tag}.")
    bad = check_overlaps(fig)
    for ext in ("png", "pdf"): fig.savefig(res / f"hydroacoustics-composition-run-j-limits.{ext}")
    plt.close(fig); return bad


if __name__ == "__main__":
    out, res, tag = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    print("evidence overlaps:", chart_evidence(out, res, tag)); print("limits overlaps:", chart_limits(out, res, tag))
