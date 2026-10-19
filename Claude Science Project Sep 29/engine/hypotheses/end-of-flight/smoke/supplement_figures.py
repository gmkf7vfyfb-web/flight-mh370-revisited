"""Figures for the run J northern supplement pass (overnight order A, 19 Oct 2026). Run in a kernel where the figure-style
helpers are loaded (apply_figure_style, panel_letter), or standalone with matplotlib defaults.

    exec(open("supplement_figures.py").read()); make_all(FINAL_JSON, PASS1_JSON, DAVEY_CSV, OUT_PREFIX)
"""
import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

TREAT = ["D0", "D1", "D2", "D3", "D4", "D5"]
TLAB = {"D0": "00:19 data\nnot used", "D1": "first burst:\ntiming", "D2": "first burst:\ntiming and\nfrequency",
        "D3": "both bursts:\nfrequencies\nas recorded", "D4": "both bursts:\nHolland transient\nbias added", "D5": "both bursts:\nsecond frequency\nwith start-up offset"}
GREY, FOCAL, DARK, REF = "#8c8c8c", "#2b7bba", "#0b3d66", "#222222"
# P5 (core DESIGN.md, posted before the run): predicted ESS ranges on impacts, 64 descents per parent, all supplement rows.
P5 = {("D2", "35-30 S"): (1000, None), ("D2", "30-25 S"): (1000, None), ("D2", "25-20 S"): (1000, None),
      ("D4", "30-25 S"): (800, 2500), ("D4", "35-30 S"): (600, 1500), ("D3", "35-30 S"): (500, 1500), ("D3", "30-25 S"): (500, 1500)}

FOOT_STE = ("Simple words: This chart uses the satellite data to 00:11 and our model of the last part of the flight. "
            "It adds a second set of flight paths that goes more to the north. We add the two sets by a fixed rule. "
            "The rule does not change the answer; it only makes the north less noisy. The physics of the last part of the flight is not yet calibrated.")


def foot_tech(extra=""):
    return ("Technical: source posterior = core run J, waypoints stratum (24 seeds) + run-J northern supplement (16 seeds, every 2nd row, "
            "multiple importance sampling by the balance heuristic with r(00:11 latitude) from r_hat.csv); prior track = run J waypoint route "
            "sampler; 00:19 data option as labelled, log-on cause q = 1/3 with 'other cause' silent, survival factor applied; provisional "
            "physics: round-3 descent laws, bank limit U[52, 90] deg, interim pitch-down, uncontrolled arm uncalibrated (Boeing gate failed); "
            "no search, ocean-drift or other evidence applied (impact level); waypoints stratum only (core prior share 0.998). " + extra)


def style():
    try:
        apply_figure_style(sizes=(8, 7, 6))   # noqa: F821 (figure-style kernel helper)
    except NameError:
        mpl.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})


def footnotes(fig, extra=""):
    """Two footnotes (STE100, technical), wrapped and stacked from the bottom; returns the figure fraction they use."""
    import textwrap
    h_pt = fig.get_figheight() * 72; lh = 6 * 1.3 / h_pt
    tech = textwrap.fill(foot_tech(extra), 175); ste = textwrap.fill(FOOT_STE, 175)
    nt, ns = tech.count("\n") + 1, ste.count("\n") + 1
    fig.text(0.01, 0.01, tech, fontsize=6, va="bottom", ha="left", linespacing=1.3)
    fig.text(0.01, 0.01 + nt * lh + 0.012, ste, fontsize=6, va="bottom", ha="left", linespacing=1.3)
    return 0.01 + (nt + ns) * lh + 0.03


def fig_pdf(F, davey, out):
    style(); lat = np.array(F["fine_lat"]); x = lat[:-1] + 0.05
    a = np.array(F["cells"]["D0"]["alone"]["imp"]["pdf_per_deg"]); c = np.array(F["cells"]["D0"]["comb"]["imp"]["pdf_per_deg"])
    dv = np.loadtxt(davey, delimiter=",", skiprows=1)
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 4.0), gridspec_kw={"width_ratios": [1, 1], "wspace": 0.28})
    for ax, logy in zip(axs, (False, True)):
        dd = dv[dv[:, 0] <= -33.0]
        ax.plot(dd[:, 0], dd[:, 1], color=REF, lw=1.0, ls="--", label="Davey et al. (2016), Fig. 10.3")
        ax.plot(x, a, color=GREY, lw=1.2, label="standard flight-path sample (24 replicates)")
        ax.plot(x, c, color=FOCAL, lw=1.2, label="standard + north-weighted sample (40 replicates)")
        ax.set_xlabel("impact latitude (deg; negative = south)")
        if logy:
            ax.set_yscale("log"); ax.set_xlim(-36, -20); ax.set_ylim(1e-4, 1.5); ax.set_title("Northern tail, log scale", loc="left")
        else:
            ax.set_xlim(-42, -20); ax.set_title("Impact latitude, 00:19 data not used", loc="left"); ax.set_ylabel("probability density (per deg)")
            ax.legend(frameon=False, loc="upper right", fontsize=6)
    for ax, l in zip(axs, "ab"):
        try: panel_letter(ax, l)   # noqa: F821
        except NameError: pass
    fb = footnotes(fig, "Davey curve recovered from the PDF vector paths, drawn to 33.0 S (north of that the recovered path is the flat plot baseline, 0.0002 per deg). 0.1 deg bins.")
    fig.subplots_adjust(bottom=fb + 0.13, top=0.92, left=0.08, right=0.98)
    for e in ("png", "pdf"): fig.savefig(f"{out}.{e}", dpi=300)
    plt.close(fig)


def fig_ess(F, P1, out, measure="states", name="imp"):
    style(); bands = ["35-30 S", "30-25 S", "25-20 S"]
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 4.6), sharey=True, gridspec_kw={"wspace": 0.06})
    xs = np.arange(len(TREAT))
    for ax, b in zip(axs, bands):
        def get(S, w):
            return np.array([next(r for r in S["cells"][d][w][name]["bands"] if r["band"] == b)["all"][measure] for d in TREAT])
        for i, d in enumerate(TREAT):
            lo_hi = P5.get((d, b))
            if lo_hi: ax.add_patch(mpl.patches.Rectangle((i - 0.32, lo_hi[0]), 0.64, (lo_hi[1] or 3e5) - lo_hi[0], color="#d9d9d9", lw=0, zorder=0))
        ax.axhline(1000, color=REF, lw=0.7, ls=":", zorder=1)
        ax.plot(xs - 0.18, get(F, "alone"), "o", color=GREY, ms=4, label="standard sample")
        ax.plot(xs, get(P1, "comb"), "s", color=FOCAL, ms=4, label="+ north-weighted sample, 64 descents per path")
        if F is not P1:
            v = get(F, "comb"); ax.plot(xs[2:] + 0.18, v[2:], "D", color=DARK, ms=4, label="+ 256 more descents per path (both-burst options)")
        ax.set_yscale("log"); ax.set_ylim(5, 3e5); ax.set_xticks(xs); ax.set_xticklabels([TLAB[d] for d in TREAT], fontsize=5.5, rotation=90)
        ax.set_title(f"impact {b}", loc="left"); ax.margins(x=0.06)
    axs[0].set_ylabel("effective distinct 00:11 states" if measure == "states" else f"effective sample size ({measure})")
    axs[0].text(-0.4, 1150, "1,000 target", fontsize=6, ha="left", va="bottom")
    hh, ll = axs[0].get_legend_handles_labels(); fig.legend(hh, ll, frameon=False, loc="upper center", ncol=3, fontsize=6, bbox_to_anchor=(0.55, 1.0))
    for ax, l in zip(axs, "abc"):
        try: panel_letter(ax, l)   # noqa: F821
        except NameError: pass
    fb = footnotes(fig, "ESS = Kish effective sample size over distinct 00:11 states (identical resampled copies merged). Grey bars: core's "
                   "predicted ranges posted before the run (P5); a bar without a top is a lower bound only; they apply to the 64-descent set. Extra descents: 256 more per 00:11 path north of 35.5 S, "
                   "pooled with the first 64 per path by count, for the both-burst options only. The last option is scored with a 4.3177 Hz frequency error, as run J.")
    fig.subplots_adjust(bottom=fb + 0.25, top=0.88, left=0.09, right=0.99)
    for e in ("png", "pdf"): fig.savefig(f"{out}.{e}", dpi=300)
    plt.close(fig)


def fig_mass(F, out):
    style(); bands = ["35-30 S", "30-25 S", "25-20 S"]
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 4.6), gridspec_kw={"wspace": 0.32})
    xs = np.arange(len(TREAT))
    for ax, b in zip(axs, bands):
        for off, w, col, mk, lab in ((-0.12, "alone", GREY, "o", "standard sample"), (0.12, "comb", FOCAL, "s", "standard + north-weighted sample")):
            v = np.array([next(r for r in F["cells"][d][w]["imp"]["bands"] if r["band"] == b)["mass"] for d in TREAT])
            bt = [F["cells"][d][f"boot_{w}"][b] for d in TREAT]
            ax.errorbar(xs + off, v, yerr=[v - np.array([q["q025"] for q in bt]), np.array([q["q975"] for q in bt]) - v], fmt=mk, color=col, ms=4, lw=0.9, capsize=0, label=lab)
        ax.set_xticks(xs); ax.set_xticklabels([TLAB[d] for d in TREAT], fontsize=5.5, rotation=90); ax.set_title(f"impact {b}", loc="left")
        ax.set_ylim(bottom=0); ax.margins(x=0.06)
    axs[0].set_ylabel("posterior probability in band")
    hh, ll = axs[0].get_legend_handles_labels(); fig.legend(hh, ll, frameon=False, loc="upper center", ncol=2, fontsize=6, bbox_to_anchor=(0.55, 1.0))
    for ax, l in zip(axs, "abc"):
        try: panel_letter(ax, l)   # noqa: F821
        except NameError: pass
    fb = footnotes(fig, "Error bars: 95 % seed-bootstrap intervals (2,000 draws; the 24 run J and the 16 supplement replicates resampled separately).")
    fig.subplots_adjust(bottom=fb + 0.25, top=0.88, left=0.09, right=0.99)
    for e in ("png", "pdf"): fig.savefig(f"{out}.{e}", dpi=300)
    plt.close(fig)


def make_all(final_json, pass1_json, davey, prefix):
    F = json.load(open(final_json)); P1 = json.load(open(pass1_json))
    fig_pdf(F, davey, prefix + "-latitude-pdf"); fig_ess(F, P1, prefix + "-band-ess"); fig_mass(F, prefix + "-band-mass")
