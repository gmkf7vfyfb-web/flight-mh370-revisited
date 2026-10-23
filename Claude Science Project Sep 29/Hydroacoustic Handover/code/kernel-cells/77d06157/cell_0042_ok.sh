cat >> gfx/charts_levels.py <<'E'


BEST = pd.read_csv(GD / "best_receiver_corrected.csv"); BEST_OLD = pd.read_csv(RD / "levels_run_j/best_receiver.csv")
POST_ESS = {"D0": 110383, "D2": 6431, "D3": 403, "D4": 2031}   # geometry/lags.csv (run J mixture, p = 0.5)


def chart_maps(fname, eta_map=1e-3):
    import matplotlib.colors as mcolors
    import run_j_windows as W
    rx = W.receivers()
    fig = plt.figure(figsize=(13.5, 10.2))
    plain = ("Each dot is one likely place where the aircraft hit the ocean, from the end-of-flight run. The colour shows how far the predicted "
             "sound at the best station is above or below the noise at that station. Panels a to d show four ways to use the last satellite data "
             "at 00:19. Panel e gives the share of impacts that a detector could find at the best station, before and after the correction of the "
             "sound loss to the IMOS loggers. Panel f shows which station would hear each impact best. The loudness is not calibrated.")
    tech = (f"{PROV_J} Maps: 40,000 of 150,000 draws taken with probability proportional to weight (so dot density = posterior density), drawn in "
            f"order of SNR (highest last); colour = max over the eight receivers of SNR at eta = {eta_map:g} (5–40 Hz 1 s-equivalent total + 4.8 dB triad "
            f"gain at IMS − station 5–40 Hz noise median; blocked paths excluded from the max). Shares in the panels and in e/f are weighted over the "
            f"full 2 M-draw subsample. Posterior ESS of the run J mixture (geometry/lags.csv): D0′ 110 k, D2 6.4 k, D3 403, D4 2.0 k (D3 below 1,000: "
            f"read as provisional); subsample Kish ESS 1.80–1.93 M. {IMOS_CORR} 'Before' = the overnight levels table (imos_tl_ramcorr_arc.csv). "
            f"Options D1 (R600 BTO only) and D5 (R1200 offset) are not in the run J levels design (run_j_windows OPTIONS = D0′, D2, D3, D4): coverage gap, "
            f"not estimable from these draws. Latitude span to 20 S (more northerly than the 99th-percentile contour, 27.5 S for D0′). "
            f"Detectable = SNR >= 7 dB (matched filter) / >= 15 dB (baseline). Replaces the 'peak radiated power at impact' six-panel figure (impacts "
            f"now shown by predicted SNR, not source loudness). " + CAV)
    b = need_bottom(fig, plain, tech)
    top = 0.905; gap = 0.06; hgt = (top - b - 0.05 - gap) / 2; wd = 0.255
    pos = [[0.06 + c * 0.30, b + 0.045 + (1 - r) * (hgt + gap), wd, hgt] for r in range(2) for c in range(3)]
    norm = mcolors.Normalize(-30, 20); cmap = plt.get_cmap("viridis")
    north = {}
    for k, opt in enumerate(["D0", "D2", "D3", "D4"]):
        ax = fig.add_axes(pos[k]); z = np.load(GD / f"map_{opt}.npz")
        s = z["snr_best_eta1"] + 10 * np.log10(eta_map); sub = np.arange(0, len(s), len(s) // 40000)[:40000]
        o = sub[np.argsort(s[sub])]
        ax.scatter(z["lon"][o], z["lat"][o], c=s[o], s=2.2, cmap=cmap, norm=norm, lw=0, alpha=0.85, rasterized=True)
        north[opt] = float((z["lat"] > -20).mean())
        for r, lab in (("H01W", "Cape Leeuwin"), ("3315", "Perth Canyon")):
            ax.plot(rx[r][1], rx[r][0], marker="^", color="k", ms=4.5, zorder=5)
            ax.annotate(lab, (rx[r][1], rx[r][0]), xytext=(-4, -9 if r == "H01W" else 4), textcoords="offset points", fontsize=6, ha="right")
        bb = BEST[BEST.key == f"{opt}/p0.5"].set_index("eta")
        ax.text(0.03, 0.97, f"detectable at the best station\nη 0.001: {pct(bb.loc[1e-3].frac_matched_filter)} matched filter, {pct(bb.loc[1e-3].frac_baseline)} baseline\n"
                f"η 0.00021: {pct(bb.loc[2.1e-4].frac_matched_filter)} matched filter, {pct(bb.loc[2.1e-4].frac_baseline)} baseline\nposterior ESS {POST_ESS[opt]:,}",
                transform=ax.transAxes, fontsize=6, va="top", bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))
        ax.set_xlim(82, 118); ax.set_ylim(-41, -20); ax.set_aspect("equal", adjustable="box"); ax.grid(alpha=0.2, lw=0.4)
        ax.set_title(f"{'abcd'[k]}  {OPT[opt]}", fontsize=8)
        ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)" if k in (0, 3) else "")
        ax.set_yticks([-40, -35, -30, -25, -20]); ax.set_yticklabels(["40°S", "35°S", "30°S", "25°S", "20°S"])
    cax = fig.add_axes([pos[3][0] + 0.02, pos[3][1] - 0.0, 0.012, 0.0]) if False else None
    # colour bar to the right of panel c
    cax = fig.add_axes([pos[2][0] + wd + 0.008, pos[2][1] + 0.1 * hgt, 0.009, 0.8 * hgt])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax); cb.set_label(f"Signal-to-noise ratio at the best station, η = {eta_map:g} (dB)", fontsize=7)
    for thr, lab in ((7, "matched filter"), (15, "baseline")): cb.ax.axhline(thr, color="w", lw=1.2)
    # e: detectable share by option, corrected vs before
    ax = fig.add_axes([pos[4][0] + 0.03, pos[4][1], wd - 0.03, hgt]); opts = ["D0", "D2", "D3", "D4"]
    for j, opt in enumerate(opts):
        for eta, mk in ((1e-3, "o"), (2.1e-4, "s")):
            n = BEST[(BEST.key == f"{opt}/p0.5") & np.isclose(BEST.eta, eta)].iloc[0]; o_ = BEST_OLD[(BEST_OLD.key == f"{opt}/p0.5") & np.isclose(BEST_OLD.eta, eta)].iloc[0]
            yy = j + (0.15 if eta == 1e-3 else -0.15)
            ax.plot([o_.frac_matched_filter, n.frac_matched_filter], [yy, yy], color="#999999", lw=0.8, zorder=1)
            ax.plot(o_.frac_matched_filter, yy, mk, mfc="white", mec=OPT_COL[opt], ms=5, zorder=2)
            ax.plot(n.frac_matched_filter, yy, mk, color=OPT_COL[opt], ms=5, zorder=3)
    ax.set_yticks(range(4)); ax.set_yticklabels([OPT[o].replace("both 00:19 frequencies, ", "both frequencies,\n").replace("both 00:19 frequencies as", "both frequencies as\n") for o in opts], fontsize=6.5)
    ax.set_xlim(-0.02, 0.7); ax.invert_yaxis(); ax.grid(axis="x", alpha=0.25, lw=0.4)
    ax.set_xlabel("Share of impacts detectable by the matched filter at the best station")
    from matplotlib.lines import Line2D
    ax.legend([Line2D([], [], marker="o", color="k", ls=""), Line2D([], [], marker="s", color="k", ls=""), Line2D([], [], marker="o", mfc="white", mec="k", ls="")],
              ["η 0.001, corrected IMOS loss", "η 0.00021 (F-35A), corrected", "open marker: before the correction"], fontsize=6, frameon=False, loc="lower right")
    ax.set_title("e  Detectable share before and after the IMOS loss correction", fontsize=8)
    # f: best station share
    ax = fig.add_axes([pos[5][0] + 0.05, pos[5][1], wd - 0.05, hgt])
    sc = {"H01W": "#1b9e77", "3376": "#7570b3", "3315": "#a6a1d6", "H08S": "#d95f02", "other": "#bbbbbb"}
    for j, opt in enumerate(opts):
        bb = BEST[(BEST.key == f"{opt}/p0.5") & np.isclose(BEST.eta, 1e-3)].iloc[0]; left = 0
        vals = {"H01W": bb.share_best_H01W, "3376": bb.share_best_3376, "3315": bb.share_best_3315, "H08S": bb.share_best_H08S}
        vals["other"] = max(0.0, 1 - sum(vals.values()))
        for k_, v in vals.items():
            ax.barh(j, v, left=left, color=sc[k_], height=0.6, label=k_ if j == 0 else None); left += v
        ax.text(1.01, j, f"{100 * vals['H01W']:.0f} %", va="center", fontsize=6)
    ax.set_yticks(range(4)); ax.set_yticklabels(["D0′", "D2", "D3", "D4"]); ax.invert_yaxis(); ax.set_xlim(0, 1.12)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.set_xlabel("Share of impacts for which the station has the highest signal-to-noise ratio")
    h_ = [matplotlib.patches.Patch(color=sc[k_]) for k_ in sc]; l_ = ["Cape Leeuwin", "Perth Canyon 3376", "Perth Canyon 3315", "Diego Garcia South", "all others"]
    ax.legend(h_, l_, fontsize=6, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    ax.set_title("f  Station with the highest predicted signal (panel rows a–d)", fontsize=8)
    fig.text(0.01, 0.985, "Where the simulated impacts would be heard best: predicted signal-to-noise ratio at the best station, for four uses of the 00:19 data (dive probability 0.5)",
             fontsize=10, ha="left", va="top")
    footnotes(fig, plain, tech)
    print("share north of 20S in map draws:", north)
    return save(fig, fname)
E