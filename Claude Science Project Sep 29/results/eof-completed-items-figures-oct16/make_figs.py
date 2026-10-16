# End-of-flight completed items, 15-16 Oct 2026: report figures.
import json, textwrap, numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
W = "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/370552c2-5cc9-44d0-86c9-507ea022948e"
B = W + "/repo/Claude Science Project Sep 29/results/"
OUT = W + "/figs/"
J = lambda f: json.load(open(B + f))

DLAB = {"D0": "00:19 values not used", "D1": "Timing only", "D2": "Timing + first frequency",
        "D3": "Timing + both frequencies", "D4": "Both frequencies, transient bias",
        "D5": "Both frequencies, offset on second"}
DSHORT = {"D0": "No 00:19\nvalues", "D1": "Timing\nonly", "D2": "Timing +\nfirst\nfrequency", "D3": "Timing +\nboth\nfrequencies",
          "D4": "Both\nfrequencies,\ntransient\nbias", "D5": "Both\nfrequencies,\nsecond\noffset"}
DCOL = {"D0": "#333333", "D1": "#56B4E9", "D2": "#0072B2", "D3": "#CC79A7", "D4": "#D55E00", "D5": "#009E73"}
FCOL = {"A1": "#E69F00", "A2": "#9a9a9a", "B": "#332288"}
BCOL = ["#c6dbef", "#6baed6", "#08519c"]
BLAB = ["below 10°", "10–45°", "above 45°"]
CAVEAT = ("The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all three rounds. "
          "Impact energy, attitude, flight-path angle and energy-transfer duration from this arm are a labelled "
          "sensitivity on uncalibrated dynamics, not a physical prediction.")

def foot(fig, plain, tech, y0=0.008, width=158):
    lines = textwrap.wrap("Plain words: " + plain, width) + textwrap.wrap("Technical: " + tech, width)
    fig.text(0.01, y0, "\n".join(lines), fontsize=6, va="bottom", ha="left", color="#333333", linespacing=1.25)

def letter(ax, s, dx=-0.13):
    ax.text(dx, 1.06, s, transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom")

def style():
    mpl.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 6.5,
                         "ytick.labelsize": 6.5, "legend.fontsize": 7, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.titlelocation": "left", "figure.dpi": 300,
                         "savefig.dpi": 300, "font.family": "DejaVu Sans"})

def check(fig, name):
    fig.savefig(OUT + name)
    r = fig.canvas.get_renderer()
    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
    fb = fig.bbox
    bad = [t.get_text()[:40] for t, b in texts if b.x0 < fb.x0 - 1 or b.x1 > fb.x1 + 1 or b.y0 < fb.y0 - 1 or b.y1 > fb.y1 + 1]
    ov = [(a.get_text()[:25], c.get_text()[:25]) for i, (a, ba) in enumerate(texts) for c, bc in texts[i + 1:] if ba.overlaps(bc)]
    print(name, "outside:", bad, "overlaps:", ov)

style()
COMMON_T = ("Core run I, end-of-flight set run-i-dive (32 seeds: 8 per stratum, strata pooled by core prior shares 0.9982/0.0011/0.0004/0.0002); "
            "log-on cause mixture q = 1/3, cause C2 silent; ")

def fig1():
    sw = J("eof-order-b-oct15/transmission-imposed.json")["sweep_p"]
    fig = plt.figure(figsize=(7.2, 3.9))
    a1 = fig.add_axes([0.08, 0.42, 0.30, 0.47]); a2 = fig.add_axes([0.57, 0.42, 0.30, 0.47])
    short = {"D0": "00:19 values\nnot used", "D2": "Timing + first\nfrequency", "D4": "Both frequencies,\ntransient bias"}
    for D in ["D0", "D2", "D4"]:
        rows = sorted([r for r in sw if r["option"] == D], key=lambda r: r["p"])
        p = [r["p"] for r in rows]; y1 = [r["band_10_45"] for r in rows]; y2 = [r["energy_GJ_q05_q50_q95"][1] for r in rows]
        a1.plot(p, y1, "-o", color=DCOL[D], ms=3.5, lw=1.4); a2.plot(p, y2, "-o", color=DCOL[D], ms=3.5, lw=1.4)
        off1 = {"D0": 0.06, "D2": -0.05, "D4": 0}[D]; off2 = {"D0": 0.78, "D2": 1.3, "D4": 1.0}[D]
        a1.text(1.05, y1[-1] + off1, short[D], color=DCOL[D], fontsize=7, va="center")
        a2.text(1.05, y2[-1] * off2, short[D], color=DCOL[D], fontsize=7, va="center")
    for a in (a1, a2):
        a.axvline(0.5, color="#888888", lw=0.8, ls=":"); a.set_xlim(-0.04, 1.04); a.set_xticks([0, 0.25, 0.5, 0.75, 1])
        a.set_xlabel("Probability p that a push-over\ncontinues to the sea")
    a1.text(0.52, 0.95, "headline\np = 0.5", fontsize=6.5, color="#666666", transform=a1.get_xaxis_transform(), va="top")
    a1.set_ylabel("Share of impacts at 10–45°\nflight-path angle"); a1.set_ylim(0, 0.92)
    a2.set_yscale("log"); a2.set_ylim(0.8, 14); a2.set_yticks([1, 2, 5, 10]); a2.set_yticklabels(["1", "2", "5", "10"])
    a2.minorticks_off(); a2.set_ylabel("Median impact energy (GJ)")
    a1.set_title("With both 00:19 frequencies, p sets the impact angle", pad=10)
    a2.set_title("…and the median impact energy", pad=10)
    letter(a1, "a", -0.25); letter(a2, "b", -0.25)
    foot(fig,
         "We changed one probability: after the nose goes down, does the aircraft continue down to the sea, or does it level off? "
         "When the 00:19 data are not used, this probability changes the impact angle a little. When both 00:19 frequency values are used "
         "with the transient bias, it changes the impact angle and energy very much. The latitude and the family shares do not change. "
         "Only aircraft that were still flying at 00:19:37 are counted.",
         COMMON_T + "transmission imposed (airborne at 00:19:37.443 x survival factor). Exact re-weighting by 2p or 2(1-p) on latent "
         "pushover_to_surface; p = 0.5 is the headline (Decision 4). 10–45° share under D4 0.036 to 0.865; held out 0.035 to 0.162. "
         "ESS (impacts) at p = 0.5: held out 9.78M, D2 245k, D4 55k. Production descent laws. " + CAVEAT)
    check(fig, "fig1-dive-probability.png"); return fig

def fig2():
    r = J("eof-item8-round3-oct15/round3-report.json")["rule11"]
    fs = J("eof-order-b-oct15/feasible-set-impact-conditions.json")
    fig = plt.figure(figsize=(7.2, 4.1))
    a1 = fig.add_axes([0.08, 0.44, 0.47, 0.45]); a2 = fig.add_axes([0.67, 0.72, 0.31, 0.17]); a3 = fig.add_axes([0.73, 0.44, 0.19, 0.12])
    Ds = ["D0", "D1", "D2", "D3", "D4", "D5"]
    for i, D in enumerate(Ds):
        v = r[f"{D} total q=0.333 (C2 silent)"]
        for dx, key, col in [(-0.15, "before", "#333333"), (0.15, "after", "#CC79A7")]:
            m = v[f"lat_median_{key}"]; lo, hi = v[f"lat_q05_q95_{key}"]
            a1.errorbar(i + dx, m, yerr=[[m - lo], [hi - m]], fmt="o", color=col, ms=3.5, lw=1.1, capsize=0)
        a2.plot([i, i], [0, v["d_ln_Z"]], color="#CC79A7", lw=1.2); a2.plot(i, v["d_ln_Z"], "o", color="#CC79A7", ms=3.5)
    a1.set_xticks(range(6)); a1.set_xticklabels([DSHORT[D] for D in Ds], fontsize=6)
    a1.set_ylabel("Impact latitude (°), median, 5–95 %"); a1.set_ylim(-39.0, -32.6); a1.set_xlim(-0.5, 5.5)
    a1.text(0.02, 0.98, "● production laws", color="#333333", fontsize=7, transform=a1.transAxes, va="top")
    a1.text(0.40, 0.98, "● round-3 laws", color="#CC79A7", fontsize=7, transform=a1.transAxes, va="top")
    a1.set_title("Round-3 descent laws: the latitude does not move")
    a2.axhline(0, color="#888888", lw=0.7); a2.set_xticks(range(6)); a2.set_xticklabels([]); a2.set_ylim(-0.3, 0.1)
    a2.set_ylabel("Change in\nln evidence"); a2.set_xlim(-0.5, 5.5)
    a2.set_title("Change in evidence (order as in a)")
    for j, (k, lab) in enumerate([("production (run-i-dive)", "production laws"), ("round-3, fixed 52.5", "round-3 laws")]):
        left = 0
        for b, c in zip(["band_lt10", "band_10_45", "band_gt45"], BCOL):
            w = fs[k][b]; a3.barh(j, w, left=left, color=c, height=0.62, edgecolor="white", lw=0.5)
            if w > 0.15: a3.text(left + w / 2, j, f"{w:.2f}", ha="center", va="center", fontsize=6, color="white" if c != BCOL[0] else "#222222")
            left += w
        a3.text(1.03, j, f"{fs[k]['band_gt45']:.3f}", va="center", fontsize=6, color=BCOL[2])
    a3.set_yticks([0, 1]); a3.set_yticklabels(["production laws", "round-3 laws"]); a3.set_xlim(0, 1); a3.invert_yaxis()
    a3.set_xlabel("Share of impacts by flight-path angle")
    for c, l, x in zip(BCOL[:2], BLAB[:2], [-0.30, 0.32]):
        a3.text(x, 1.12, "■ " + l, color=c if c != BCOL[0] else "#6b8fb5", fontsize=6.5, transform=a3.transAxes)
    a3.text(-0.62, 1.62, "…but steep impacts (above 45°) nearly stop", fontsize=8, transform=a3.transAxes)
    a3.text(1.03, 1.12, "above 45°", fontsize=6, color=BCOL[2], transform=a3.transAxes)
    letter(a1, "a", -0.17); letter(a2, "b", -0.17); a3.text(-0.70, 1.62, "c", transform=a3.transAxes, fontsize=9, fontweight="bold")
    foot(fig,
         "We replaced the descent laws with the round-3 fit to the Boeing simulator traces. The impact latitude and the evidence for each "
         "00:19 treatment almost do not change. The impact angles do change: steep impacts (above 45°) almost stop, because the round-3 "
         "bank limit (52.5°) stops the spiral before it becomes steep. Panel c uses only aircraft still flying at 00:19:37 and no 00:19 data.",
         COMMON_T + "full re-run, 4 strata x 8 seeds (item 8 Task B). Round-3 laws: spiral doubling 26.45 s, lift lag 3.52 s, gain 0.41, "
         "bank cap 52.53° (all-data fit; LOO 57.3–62.4°). Panels a–b two-factor totals; latitude shift ≤ 0.06°, Δ ln Z −0.20 to −0.02; "
         "ESS by treatment 4.7k (both raw) to 891k. Panel c on D0' (feasible set), ESS 317k / 295k. Boeing LOO gate stays failed. " + CAVEAT)
    check(fig, "fig2-round3-laws.png"); return fig

def fig3():
    ti = J("eof-order-b-oct15/transmission-imposed.json")
    fig = plt.figure(figsize=(7.2, 3.6))
    a1 = fig.add_axes([0.22, 0.44, 0.24, 0.30]); a2 = fig.add_axes([0.72, 0.44, 0.25, 0.42])
    rows = [("old_raw_D0", "before: all samples"), ("D0_transmission_imposed", "after: airborne at 00:19:37")]
    for j, (k, lab) in enumerate(rows):
        left = 0
        for b, c in zip(["band_lt10", "band_10_45", "band_gt45"], BCOL):
            w = ti[k][b]; a1.barh(j, w, left=left, color=c, height=0.6, edgecolor="white", lw=0.5)
            if w > 0.085: a1.text(left + w / 2, j, f"{w:.2f}", ha="center", va="center", fontsize=6, color="white" if c != BCOL[0] else "#222222")
            left += w
    a1.set_yticks([0, 1]); a1.set_yticklabels([r[1] for r in rows]); a1.invert_yaxis(); a1.set_xlim(0, 1)
    a1.set_xlabel("Share of impacts by flight-path angle\n(00:19 values not used)")
    for c, l, x in zip(BCOL, BLAB, [0.0, 0.36, 0.66]):
        a1.text(x, 1.06, "■ " + l, color=c if c != BCOL[0] else "#6b8fb5", fontsize=6.5, transform=a1.transAxes)
    a1.text(-0.75, 1.55, "13.0 % of the old weight was on the sea before\nthe last transmission; removing it lowers 10–45°",
            fontsize=8, transform=a1.transAxes)
    Ds = ["D0", "D1", "D2", "D3", "D4", "D5"]
    for i, D in enumerate(Ds):
        v = ti["loudness"]["data:" + D]["loud_decile_share"]
        a2.plot([0, v], [i, i], color=DCOL[D], lw=1.2); a2.plot(v, i, "o", color=DCOL[D], ms=4)
        a2.text(v + 0.008, i, f"{v:.3f}", va="center", fontsize=6.5, color=DCOL[D])
    a2.set_yticks(range(6)); a2.set_yticklabels([DLAB[D] for D in Ds], fontsize=6.5); a2.invert_yaxis(); a2.set_xlim(0, 0.30)
    a2.set_xlabel("Share of impacts in the loudest 10 %")
    a2.text(-1.0, 1.06, "00:19 data make loud impacts up to 2.4x more likely", fontsize=8, transform=a2.transAxes)
    a1.text(-0.85, 1.55 + 0.0, "", transform=a1.transAxes)
    a1.text(-0.78, 1.55, "a", transform=a1.transAxes, fontsize=9, fontweight="bold", ha="right")
    a2.text(-1.06, 1.06, "b", transform=a2.transAxes, fontsize=9, fontweight="bold", ha="right")
    foot(fig,
         "The aircraft sent its last signal at 00:19:37. Before this change, 13 per cent of the 'no 00:19 data' samples were already in "
         "the sea before that time. We removed them, and the samples that broke up in the air before that time. Panel b: the loudest 10 per cent "
         "of impacts are set from the 'no 00:19 data' case (so it is 0.100); each 00:19 treatment then makes loud impacts more likely.",
         COMMON_T + "D0' = 00:19 values held out x airborne at 00:19:37.443 x survival factor; p = 0.5. ESS D0' 9.78M impacts (raw 10.84M). "
         "Loud = acoustic power above 2.947e10 W, the 90th percentile of D0'. D4/D0' = 1.93; two-factor totals 0.137–0.256. "
         "D0' family shares A1 0.140, A2 0.341, B 0.518; median latitude −37.16° (raw −37.02°). " + CAVEAT)
    check(fig, "fig3-transmission-imposed.png"); return fig

def fig4():
    tw = J("eof-order-b-oct15/bank-cap-sampled-tail-weight.json")["by_bin"]
    S = J("eof-order-b-oct15/bank-cap-S-vs-fixed52.json")["rule11"]; F = J("eof-order-b-oct15/bank-cap-F90-vs-fixed52.json")["rule11"]
    fig = plt.figure(figsize=(7.2, 3.9))
    a1 = fig.add_axes([0.08, 0.42, 0.34, 0.45]); a2 = fig.add_axes([0.62, 0.60, 0.27, 0.15]); a3 = fig.add_axes([0.62, 0.42, 0.27, 0.11])
    bins = list(tw); lo = np.array([float(b.split("-")[0]) for b in bins]); hi = np.array([float(b.split("-")[1]) for b in bins])
    mid = (lo + hi) / 2; st = np.array([tw[b]["band_gt45"] for b in bins]); md = np.array([tw[b]["band_10_45"] for b in bins])
    a1.axvspan(52, 63, color="#eeeeee", zorder=0); a1.text(57.5, 0.33, "range from\nBoeing traces", ha="center", va="top", fontsize=6.5, color="#555555")
    a1.errorbar(mid, st, xerr=[mid - lo, hi - mid], fmt="o", color=BCOL[2], ms=4, lw=1.1, capsize=0)
    a1.errorbar(mid, md, xerr=[mid - lo, hi - mid], fmt="s", color=BCOL[1], ms=3.5, lw=1.1, capsize=0)
    a1.text(76, st[-1] + 0.005, "above 45°", color=BCOL[2], fontsize=7, ha="right"); a1.text(66, md[3] + 0.02, "10–45°", color=BCOL[1], fontsize=7)
    a1.set_xlim(50, 92); a1.set_ylim(-0.01, 0.34); a1.set_xlabel("Bank limit in the spiral (°)"); a1.set_ylabel("Share of impacts")
    a1.set_title("Steep impacts need a bank limit above 70°")
    arms = [("fixed 52.5°", None), ("sampled 52–90°", S), ("fixed 90°", F)]
    for ax, key, ttl in [(a2, "D4 total q=0.333 (C2 silent)", "Both frequencies, transient bias"), (a3, "D0 total q=0.333 (C2 silent)", "00:19 values not used")]:
        for j, (lab, R) in enumerate(arms):
            v = (S[key]["family_shares_before"] if R is None else R[key]["family_shares_after"])
            left = 0
            for fam in ["A1", "A2", "B"]:
                w = v[fam]; ax.barh(j, w, left=left, color=FCOL[fam], height=0.62, edgecolor="white", lw=0.5)
                if w > 0.08: ax.text(left + w / 2, j, f"{w:.2f}", ha="center", va="center", fontsize=6, color="white" if fam != "A2" else "#222222")
                left += w
            ax.text(1.03, j, "0 (ref.)" if R is None else f"{R[key]['d_ln_Z']:+.2f}", va="center", fontsize=6.5, color="#333333")
        ax.set_yticks(range(3)); ax.set_yticklabels([a[0] for a in arms], fontsize=6.5); ax.invert_yaxis(); ax.set_xlim(0, 1)
        ax.set_title(ttl, fontsize=7, pad=2)
        if ax is a2: ax.set_xticklabels([])
    a2.text(1.03, 1.14, "Δ ln evidence", transform=a2.transAxes, fontsize=6.5, color="#333333")
    a3.set_xlabel("Family share")
    for fam, (x, y) in zip(["A1", "A2", "B"], [(-0.30, 1.62), (0.45, 1.62), (-0.30, 1.30)]):
        a2.text(x, y, "■ " + {"A1": "Fuel ends, no input", "A2": "Fuel ends, controlled", "B": "Planned descent"}[fam],
                color=FCOL[fam], fontsize=6.5, transform=a2.transAxes)
    a2.text(-0.48, 2.0, "With both frequencies and transient bias,\nthe bank limit decides the family", transform=a2.transAxes, fontsize=8)
    letter(a1, "a", -0.17); a2.text(-0.52, 2.0, "b", transform=a2.transAxes, fontsize=9, fontweight="bold", ha="right")
    foot(fig,
         "In a spiral with no pilot input, the bank angle increases until it reaches a limit. The Boeing traces show limits of 53–60°, but "
         "the true limit is not known, so we let it go to 90°. Steep impacts need a limit above 70°. When the 00:19 frequency values are "
         "used with the transient bias, a 90° limit makes 'fuel ends, no pilot input' the most probable family.",
         COMMON_T + "transmission imposed, round-3 laws, full runs 4 strata x 8 seeds per arm. Sampled prior U[52,63] weight 0.8 + U[63,90] "
         "weight 0.2 (declared choice; exact re-weighting via latent spiral_bank_cap_deg). Panel a on D0' (feasible set), ESS per bin 14.6k–84.6k. "
         "D4 ESS: fixed 52.5 33.3k, sampled 18.8k, fixed 90 8.9k; D4 x C2 silent at 90°: Δ ln Z +1.03, A1 0.62. Overbank (above 90°) is "
         "outside the model. " + CAVEAT)
    check(fig, "fig4-bank-limit.png"); return fig

def fig5():
    fig = plt.figure(figsize=(7.2, 3.3))
    ax = fig.add_axes([0.08, 0.40, 0.60, 0.48])
    pri = [("fe_tied", "fuel-tied (headline)", "#332288", True), ("uniform_U1", "uniform in time (declared\nsensitivity)", "#44AA99", True),
           ("binned_coordination", "binned (not adopted:\nchanges the fuel state)", "#999999", False)]
    rng = np.random.default_rng(3)
    for i, D in enumerate(["D0", "D2", "D4"]):
        for j, (k, lab, col, filled) in enumerate(pri):
            v = np.array([J(f"eof-order-b-oct15/onset-uniform/seed-{s}.json")["cells"][D][k]["B"]["share"] for s in range(1, 9)])
            xc = i + (j - 1) * 0.24; x = xc + rng.uniform(-0.05, 0.05, 8)
            ax.plot(x, v, "o", ms=3.4, mfc=col if filled else "none", mec=col, mew=0.9, alpha=0.9)
            ax.plot([xc - 0.09, xc + 0.09], [np.median(v)] * 2, color=col, lw=2)
    ax.set_xticks(range(3)); ax.set_xticklabels([DLAB[D] for D in ["D0", "D2", "D4"]]); ax.set_xlim(-0.5, 2.5)
    ax.set_ylabel("Share of planned descent"); ax.set_ylim(0, 0.45)
    ax.set_title("A uniform start time does not raise the planned-descent share")
    for j, (k, lab, col, filled) in enumerate(pri):
        ax.text(1.03, 0.92 - j * 0.20, ("● " if filled else "○ ") + lab, color=col, fontsize=7, transform=ax.transAxes, va="top")
    ax.text(1.03, 0.25, "bar = median of 8 seeds\npoints = single seeds", fontsize=6.5, color="#555555", transform=ax.transAxes)
    foot(fig,
         "A planned descent can start at any time before the fuel ends. We compared two ways to spread the start time between 22:41 and "
         "00:11. If only the start time changes, the share of planned descent stays at about 0.10. It doubles only if the method also "
         "changes how much fuel the aircraft had, which the earlier stages already set from the evidence. Pete ruled for the first method.",
         "Core run I, joined V2 (onset split at 22:41:21 and 00:10:59), stratum next-i-waypoints, 8 seeds; two-factor totals, q = 1/3, C2 silent, "
         "transmission imposed. U1: onset uniform on [22:41, min(00:11, P)] per parent with fuel-tied pre-00:11 mass kept (exact; prior "
         "recovery 0.998–1.002). Medians (range): D0 0.108 (0.062–0.254) → 0.098 (0.056–0.223); D2 0.077 → 0.076; D4 0.044 → 0.044. "
         "Binned (0.197) shown for the record only (ruled not adopted 16 Oct 02:08Z). B ESS per seed 180–1,450; pre-00:11 B under D2/D4 not estimable.")
    check(fig, "fig5-onset-prior.png"); return fig

def fig6():
    d = J("eof-both-burst-oct16/both-burst-smoke-seed1.json")
    fig = plt.figure(figsize=(7.2, 3.3))
    ax = fig.add_axes([0.10, 0.40, 0.56, 0.48])
    cells = [("none", "00:19 values not used"), ("r600/no-offset", "Timing + first frequency"), ("both/no-offset", "Timing + both frequencies"),
             ("both/startup-offset", "Both frequencies, start-up offset")]
    arms = [("base", "production (32 descents\nper aircraft state)", "#333333"), ("aimed", "aimed selection\n(8x candidates)", "#CC79A7"),
            ("ch64", "more descents (256 per\naircraft state)", "#0072B2")]
    for i, (k, lab) in enumerate(cells):
        for j, (a, al, col) in enumerate(arms):
            ax.plot(i + (j - 1) * 0.22, d[a]["opts"][k]["eff_impacts"], "o", color=col, ms=4.5)
    ax.axhline(1000, color="#D55E00", lw=0.9, ls="--"); ax.text(3.45, 1250, "target 1,000", color="#D55E00", fontsize=6.5, ha="right")
    ax.set_yscale("log"); ax.set_ylim(15, 8e6); ax.set_yticks([1e2, 1e3, 1e4, 1e5, 1e6]); ax.set_yticklabels(["100", "1k", "10k", "100k", "1M"])
    ax.minorticks_off()
    ax.set_xticks(range(4)); ax.set_xticklabels([textwrap.fill(c[1], 16) for c in cells]); ax.set_xlim(-0.5, 3.5)
    ax.set_ylabel("Effective number of impacts")
    ax.set_title("Trial run, one seed: neither fix reaches 1,000 for the two-burst cases")
    for j, (a, al, col) in enumerate(arms):
        ax.text(1.03, 0.95 - j * 0.20, "● " + al, color=col, fontsize=7, transform=ax.transAxes, va="top")
    ax.text(1.03, 0.25, "TRIAL RUN: not evidence", color="#D55E00", fontsize=7, transform=ax.transAxes)
    foot(fig,
         "This is a small trial (one seed, one part of the sample). We tried two ways to get more useful samples for the cases that use "
         "both 00:19 frequency values. Both helped (3 to 25 times more) but did not reach the target. The aimed method also lost samples "
         "in the other cases.",
         "Core run I, stratum next-i-repro-radar, seed 1, 100k m0011 parents; run-i-dive recipe (c2-silent-aim + dive-branch), binary sha256 "
         "dc1f52f8...; unnormalised within-parent weights (request 9). Prior recovery, aimed vs base: max CDF difference 0.0105 (push-over "
         "rate) vs 0.0030 standard, base noise about 0.004: marginal. Seed-2 repeat not assessed (run-I hand-offs removed 16 Oct 02:00Z). " + CAVEAT)
    check(fig, "fig6-both-burst-trial.png"); return fig

if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6): f()
