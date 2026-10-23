"""Charts 1, 2 (+ the other six stations and the overview): noise against the FULL distribution of run J received levels
per third-octave band, on the corrected IMOS transmission-loss table; and chart 3: loudness maps per 00:19 option."""
exec(open(str(WS_ROOT) + "/gfx/common.py").read())
import run_j_levels as RL
import run_j_levels_charts as RLC
from scipy.ndimage import gaussian_filter1d

ETAS3 = [1e-2, 2.26e-3, 2.1e-4, 1e-5]
H = np.load(GD / "band_hist_D0_p0.5.npz"); EDGES = H["edges"]; MID = 0.5 * (EDGES[1:] + EDGES[:-1])
DET = pd.read_csv(GD / "detectable_corrected.csv", dtype={"receiver": str})
DET_OLD = pd.read_csv(RD / "levels_run_j/detectable.csv", dtype={"receiver": str})
NOISE = RLC.load_noise(LEV)
YLO, YHI = 30.0, 130.0

NIGHT_H08S = (4.02 - 1.46, 8.93 - 1.46)
def share_shift(st, eta, dnoise, thr):
    """Weighted share with SNR >= thr when the noise median rises by dnoise dB (0.25 dB histogram of the 5-40 Hz total)."""
    h = H[f"{st}/total"]; tot = h.sum() + float(H[f"{st}/band{RL.BANDS[0]:g}_blocked"])
    r = DET[(DET.receiver == st) & (DET.key == "D0/p0.5")].iloc[0]
    s = MID + r.gain_db - r.noise_median_db + 10 * np.log10(eta) - dnoise
    return float(h[s >= thr].sum() / tot)



def wq(hist, qs):
    c = np.cumsum(hist); c = c / c[-1]
    return np.interp(qs, c, MID)


def violin(ax, x, hist, eta, col, half=0.10, ylo=YLO, yhi=YHI):
    """Full weighted distribution of the band level at this eta: mirrored density (area-normalised per band), 5-95 % line,
    25-75 % box, median tick. Mass below the axis floor is reported, not drawn."""
    tot = hist.sum()
    if tot <= 0: return None
    sh = 10 * np.log10(eta); y = MID + sh
    d = gaussian_filter1d(hist / tot, 2.0)          # 0.5 dB smoothing (2 bins of 0.25 dB)
    m = (y >= ylo) & (y <= yhi); dm = d[m]
    if dm.size and dm.max() > 0:
        wdt = half * dm / d.max()
        ax.fill_betweenx(y[m], x - wdt, x + wdt, color=col, alpha=0.85, lw=0, zorder=3)
    q = wq(hist, [0.05, 0.25, 0.5, 0.75, 0.95]) + sh
    ax.plot([x, x], [max(q[0], ylo), min(q[4], yhi)], color="#222222", lw=0.6, zorder=4)
    ax.add_patch(matplotlib.patches.Rectangle((x - 0.022, q[1]), 0.044, q[3] - q[1], fc="#222222", ec="none", zorder=4))
    if ylo <= q[2] <= yhi: ax.plot([x - 0.045, x + 0.045], [q[2], q[2]], color="white", lw=1.2, zorder=5)
    below = float(hist[y < ylo].sum() / tot)
    return dict(q05=q[0], q50=q[2], q95=q[4], below=below)


def station_panel(ax, st, show_xlabels=True, compact=False):
    nz = NOISE[st].set_index("fc")
    xs = list(range(len(RL.BANDS))); x25 = -1.25
    # noise: per-band median line segment and 10-90 % box
    for i, fc in enumerate(RL.BANDS):
        r = nz.loc[fc]
        ax.add_patch(matplotlib.patches.Rectangle((i - 0.45, r.p10), 0.9, r.p90 - r.p10, fc="#bdbdbd", ec="none", alpha=0.55, zorder=1))
        ax.plot([i - 0.45, i + 0.45], [r.p50, r.p50], color="#252525", lw=1.3, zorder=6)
    if 3.2 in nz.index:
        r = nz.loc[3.2]
        ax.add_patch(matplotlib.patches.Rectangle((x25 - 0.45, r.p10), 0.9, r.p90 - r.p10, fc="#bdbdbd", ec="none", alpha=0.55, zorder=1))
        ax.plot([x25 - 0.45, x25 + 0.45], [r.p50, r.p50], color="#252525", lw=1.3, zorder=6)
        ax.text(x25, YLO + 3, "noise\nonly", fontsize=5.5, ha="center", va="bottom", color="#555555")
    stats = {}
    for k, eta in enumerate(ETAS3):
        for i, fc in enumerate(RL.BANDS):
            s = violin(ax, i + (k - 1.5) * 0.22, H[f"{st}/band{fc:g}"], eta, ETA_COL[eta])
            if s: stats[(eta, fc)] = s
    ax.set_xlim(-1.85 if 3.2 in nz.index else -0.6, len(RL.BANDS) - 0.4); ax.set_ylim(YLO, YHI)
    ax.set_xticks(([x25] if 3.2 in nz.index else []) + xs)
    ax.set_xticklabels((["2–5"] if 3.2 in nz.index else []) + [f"{fc:g}" for fc in RL.BANDS] if show_xlabels else [])
    ax.yaxis.grid(True, alpha=0.25, lw=0.4)
    # detectable fractions (5-40 Hz total, corrected IMOS table)
    d = DET[(DET.receiver == st) & (DET.key == "D0/p0.5")]
    lines = ["coupling   matched filter   baseline"] if not compact else ["coupling: matched filter / baseline"]
    for eta in ETAS3:
        r = d[np.isclose(d.eta, eta)].iloc[0]
        lines.append(f"{eta:<9g}  {pct(r.frac_matched_filter):>12}   {pct(r.frac_baseline):>9}" if not compact else
                     f"{eta:g}: {pct(r.frac_matched_filter)} / {pct(r.frac_baseline)}")
    if st == "H08S" and not compact:
        for lab, dn in (("8 Mar 2014 between airgun shots", NIGHT_H08S[0]), ("8 Mar 2014 shots included", NIGHT_H08S[1])):
            lines.append(f"matched filter, {lab} (+{dn:.1f} dB):")
            lines.append("  " + ", ".join(f"{pct(share_shift(st, eta, dn, 7))} at {eta:g}" for eta in (1e-2, 2.26e-3)))
    bl = {fc: float(H[f"{st}/band{fc:g}_blocked"]) for fc in RL.BANDS}; fcb = max(bl, key=bl.get); blocked = bl[fcb]
    belowmax = max(s["below"] for (eta, fc), s in stats.items() if eta == 1e-2) if stats else 1.0
    if belowmax > 0.5: lines.append(f"most impacts: level below {YLO:.0f} dB in every band")
    if blocked > 0.005: lines.append(f"no sound path (blocked) for up to {pct(blocked, 0)}" + ("\n" if compact else " ") + f"of impacts ({fcb:g} Hz band); shapes = open paths")
    hdr = "Share of impacts detectable (5–40 Hz total)"
    ax.text(0.99, 0.985, hdr + "\n" + "\n".join(lines), transform=ax.transAxes, ha="right", va="top", fontsize=5.8 if compact else 6.3,
            family="DejaVu Sans Mono", bbox=dict(fc="white", ec="#cccccc", lw=0.5, alpha=0.92, pad=2.5), zorder=10)
    return stats


def legend_handles():
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color="#252525", lw=1.3), Patch(fc="#bdbdbd", alpha=0.55)]
    l = ["background noise, median", "background noise, 10–90 % range"]
    for eta in ETAS3:
        h.append(Patch(fc=ETA_COL[eta])); l.append(f"predicted level, coupling {eta:g}" + (" (our F-35A estimate from Metz et al. 2023 data; not adopted)" if eta == ETA_F35A else (" (Brown et al. 2026 preprint; other definition)" if eta == ETA_BROWN else "")))
    h.append(Line2D([], [], color="#222222", lw=3.0, solid_capstyle="butt")); l.append("box 25–75 %, line 5–95 %, tick = median")
    return h, l


PLAIN_L = ("The grey line is the median background noise at the station in each frequency band. The grey box holds 80 % of the noise "
           "levels. Each coloured shape shows all the simulated impacts: its width shows how many impacts give that sound level at the "
           "station. There is one shape for each of four assumed shares of impact energy that become sound. Where a shape is above the "
           "grey line, those impacts are louder than the noise in that band. The box at the top right gives the share of impacts that two "
           "detectors would find in the 5 to 40 Hz total. Below 5 Hz there is no prediction. These are estimates. They are not calibrated.")


def tech_L(st):
    src = NOISE[st].attrs["source"]
    t = (f"{PROV_J} Panel: 00:19 option D0′ (held out), p = 0.5; Kish ESS of the subsample 1.90 M (Kish ESS of the full run J "
         f"mixture for D0′ at p = 0.5: 1.34 M, run-j-windows/ess.json). E = contact kinetic energy (upper anchor), tau = tau90 clamped to 0.05–10 s, 10 m source, "
         f"one-pole spectrum flat to 1/tau and f^-2 above; level = 1 s-equivalent third-octave band SPL (T_eff 2.68 s), dB re 1 uPa; eta only "
         f"shifts the distribution by 10 log10 eta. Violins: weighted histograms of the 2 M draws (0.25 dB bins, 0.5 dB Gaussian smoothing), "
         f"width normalised per violin; mass below {YLO:.0f} dB is not drawn. TL: whole-arc KRAKEN grid (offset-0 line, latitude-only, clamped "
         f"41–20 S); {IMOS_CORR} RAM delta at H01W/H08S, none at H08N; 3250 uncorrected. Noise: {src}"
         f"{' (IMOS third-octave 1 s percentiles)' if st not in RL.IMS else ' (PSD x band width)'}. Detectable = SNR of the 5–40 Hz total "
         f">= 7 dB (envelope matched filter, P_D 0.5, alpha 0.01) or >= 15 dB (STA/LTA baseline), model-matched upper bounds from the weak-signal "
         f"trial on 3376 background; SNR against the module's 5–40 Hz noise medians (imos2b; IMS = 3376 proxy + Blackman offset, +4.8 dB triad gain). ")
    if st == "H01W": t += ("Noise is Blackman et al. 2004 (2003); 2014 cross-checks agree within about 1.5 dB (Royer 2016 spectrogram 101.7 dB after a raster-smoothing "
        "correction, Kadri 2024 trace 103.1 dB, against 101.7 dB). The earlier '2014 noise 6 dB quieter' case (Kadri spectrogram colours) is withdrawn. ")
    if st == "H08S": t += (f"8 March 2014 conditions: airgun shots every 9.98 s (Kadri 2024 Fig. 9d). Noise raised by +{NIGHT_H08S[0]:.1f} dB between shots and "
        f"+{NIGHT_H08S[1]:.1f} dB with shots included = measured excess on the Fig. 9d trace (+4.0 / +8.9 dB) minus the +1.5 dB by which the same figure's "
        "trace reads above Blackman at H01W; shares from the 5–40 Hz total-level histogram (0.25 dB bins). ")
    if st in ("3315", "3376", "3274", "3275"):
        o = DET_OLD[(DET_OLD.receiver == st) & (DET_OLD.key == "D0/p0.5") & np.isclose(DET_OLD.eta, 1e-3)].iloc[0]
        n = DET[(DET.receiver == st) & (DET.key == "D0/p0.5") & np.isclose(DET.eta, 1e-3)].iloc[0]
        t += f"Change from the earlier table at eta 1e-3: matched-filter share {pct(o.frac_matched_filter)} -> {pct(n.frac_matched_filter)}. "
    return t + CAV


def chart_station(st, fname):
    fig = plt.figure(figsize=(8.6, 7.4))
    tech = tech_L(st); b = need_bottom(fig, PLAIN_L, tech)
    ax = fig.add_axes([0.085, b + 0.075, 0.895, 0.865 - b - 0.075])
    station_panel(ax, st)
    ax.set_xlabel("Third-octave frequency band, centre frequency (Hz)"); ax.set_ylabel("Sound level in a 1 s window (dB re 1 µPa)")
    h, l = legend_handles(); fig.legend(h, l, loc="upper left", bbox_to_anchor=(0.06, 0.935), ncol=2, frameon=False, fontsize=6.0)
    fig.text(0.01, 0.975, f"{STN[st]}: background noise against the predicted sound level of all simulated impacts, by frequency band",
             fontsize=9, ha="left", va="top")
    footnotes(fig, PLAIN_L, tech)
    return save(fig, fname)


def chart_overview(fname):
    fig = plt.figure(figsize=(15, 9.6))
    tech = tech_L("3315").replace("Change from the earlier table", "Example change (3315) from the earlier table"); b = need_bottom(fig, PLAIN_L, tech)
    top = 0.87; gap = 0.07; hgt = (top - b - 0.06 - gap) / 2
    axs = []
    for r in range(2):
        for c in range(4):
            ax = fig.add_axes([0.05 + c * 0.2375, b + 0.05 + (1 - r) * (hgt + gap), 0.225, hgt]); axs.append(ax)
    for ax, st in zip(axs, RL.RECEIVERS):
        station_panel(ax, st, compact=True); ax.set_title(STN[st], fontsize=8)
    for ax in axs[4:]: ax.set_xlabel("Band centre (Hz)")
    for ax in (axs[0], axs[4]): ax.set_ylabel("Sound level, 1 s window (dB re 1 µPa)")
    for ax in axs:
        if ax not in (axs[0], axs[4]): ax.set_yticklabels([])
    h, l = legend_handles(); fig.legend(h, l, loc="upper left", bbox_to_anchor=(0.03, 0.945), ncol=3, frameon=False, fontsize=6.2)
    fig.text(0.01, 0.985, "Background noise against the predicted sound level of all simulated impacts, eight stations (00:19 data not used, dive probability 0.5)",
             fontsize=10, ha="left", va="top")
    footnotes(fig, PLAIN_L, tech)
    return save(fig, fname)


BEST = pd.read_csv(GD / "best_receiver_corrected.csv"); BEST_OLD = pd.read_csv(RD / "levels_run_j/best_receiver.csv")
POST_ESS = {"D0": 1336700, "D2": 107226, "D3": 5671, "D4": 25414}   # run-j-windows/ess.json, Kish ESS of the full run J mixture at p = 0.5


def chart_maps(fname, eta_map=1e-3):
    import matplotlib.colors as mcolors
    import run_j_windows as W
    rx = W.receivers()
    fig = plt.figure(figsize=(15, 9.0))
    plain = ("Each dot is one likely place where the aircraft hit the ocean, from the end-of-flight run. The colour shows how far the predicted "
             "sound at the best station is above or below the noise at that station. Panels a to d show four ways to use the last satellite data "
             "at 00:19. Panel e gives the share of impacts that a detector could find at the best station, before and after the correction of the "
             "sound loss to the IMOS loggers. Panel f shows which station would hear each impact best. The loudness is not calibrated.")
    tech = (f"{PROV_J} Maps: 40,000 of 150,000 draws taken with probability proportional to weight (so dot density = posterior density), drawn in "
            f"order of SNR (highest last); colour = max over the eight receivers of SNR at eta = {eta_map:g} (5–40 Hz 1 s-equivalent total + 4.8 dB triad "
            f"gain at IMS − station 5–40 Hz noise median; blocked paths excluded from the max). Shares in the panels and in e/f are weighted over the "
            f"full 2 M-draw subsample. Posterior ESS = Kish ESS of the full run J mixture at p = 0.5 (run-j-windows/ess.json): D0′ 1.34 M, D2 107 k, D3 5.7 k, D4 25 k; "
            f"Kish ESS of the 2 M-draw subsample 1.80–1.93 M. {IMOS_CORR} 'Before' = the overnight levels table (imos_tl_ramcorr_arc.csv). "
            f"Options D1 (R600 BTO only) and D5 (R1200 offset) are not in the run J levels design (run_j_windows OPTIONS = D0′, D2, D3, D4): coverage gap, "
            f"not estimable from these draws. Latitude span to 20 S (more northerly than the 99th-percentile contour, 27.5 S for D0′). "
            f"Detectable = SNR >= 7 dB (matched filter) / >= 15 dB (baseline). Replaces the 'peak radiated power at impact' six-panel figure (impacts "
            f"now shown by predicted SNR, not source loudness). " + CAV)
    b = need_bottom(fig, plain, tech)
    top = 0.90; mh = 0.25; wd = 0.2
    pos = [[0.05 + c * 0.222, top - mh, wd, mh] for c in range(4)]
    pos_e = [0.17, b + 0.085, 0.32, top - mh - 0.11 - b - 0.085]; pos_f = [0.64, b + 0.085, 0.31, pos_e[3]]
    norm = mcolors.Normalize(-30, 20); cmap = plt.get_cmap("viridis")
    north = {}
    for k, opt in enumerate(["D0", "D2", "D3", "D4"]):
        ax = fig.add_axes(pos[k]); z = np.load(GD / f"map_{opt}.npz")
        s = z["snr_best_eta1"] + 10 * np.log10(eta_map); sub = np.arange(0, len(s), len(s) // 40000)[:40000]
        o = sub[np.argsort(s[sub])]
        ax.scatter(z["lon"][o], z["lat"][o], c=s[o], s=3.0, cmap=cmap, norm=norm, lw=0, alpha=1.0, rasterized=True)
        north[opt] = float((z["lat"] > -20).mean())
        for r, lab in (("H01W", "Cape Leeuwin"), ("3315", "Perth Canyon")):
            ax.plot(rx[r][1], rx[r][0], marker="^", color="k", ms=4.5, zorder=5)
            ax.annotate(lab, (rx[r][1], rx[r][0]), xytext=(-4, -9 if r == "H01W" else 4), textcoords="offset points", fontsize=6, ha="right")
        bb = BEST[BEST.key == f"{opt}/p0.5"].set_index("eta")
        ax.text(0.03, 0.97, f"detectable at the best station\ncoupling 0.001: {pct(bb.loc[1e-3].frac_matched_filter)} matched filter, {pct(bb.loc[1e-3].frac_baseline)} baseline\n"
                f"coupling 0.00226: {pct(bb.loc[2.26e-3].frac_matched_filter)} matched filter, {pct(bb.loc[2.26e-3].frac_baseline)} baseline\nposterior ESS {POST_ESS[opt]:,}",
                transform=ax.transAxes, fontsize=6, va="top", bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))
        ax.set_xlim(82, 118); ax.set_ylim(-41, -20); ax.set_aspect("equal", adjustable="box"); ax.grid(alpha=0.2, lw=0.4)
        ax.set_title(f"{'abcd'[k]}  {OPT[opt]}", fontsize=8)
        ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude" if k == 0 else "")
        if k > 0: ax.set_yticklabels([])
        ax.set_yticks([-40, -35, -30, -25, -20]); ax.set_yticklabels(["40°S", "35°S", "30°S", "25°S", "20°S"] if k == 0 else [])
    cax = fig.add_axes([pos[3][0] + 0.02, pos[3][1] - 0.0, 0.012, 0.0]) if False else None
    # colour bar to the right of panel c
    cax = fig.add_axes([pos[3][0] + wd + 0.006, pos[3][1] + 0.05 * mh, 0.008, 0.9 * mh])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax); cb.set_label(f"Signal-to-noise ratio at the best station,\ncoupling efficiency {eta_map:g} (dB)", fontsize=7)
    for thr, lab in ((7, "matched\nfilter"), (15, "baseline")): cb.ax.axhline(thr, color="w", lw=1.2); cb.ax.text(-0.6, thr, lab, fontsize=5.5, ha="right", va="center", transform=cb.ax.get_yaxis_transform())
    # e: detectable share by option, corrected vs before
    ax = fig.add_axes(pos_e); opts = ["D0", "D2", "D3", "D4"]
    for j, opt in enumerate(opts):
        for eta, mk in ((1e-3, "o"), (2.26e-3, "s")):
            n = BEST[(BEST.key == f"{opt}/p0.5") & np.isclose(BEST.eta, eta)].iloc[0]; o_ = BEST_OLD[(BEST_OLD.key == f"{opt}/p0.5") & np.isclose(BEST_OLD.eta, eta)].iloc[0] if np.isclose(BEST_OLD.eta, eta).any() else None
            yy = j + (0.15 if eta == 1e-3 else -0.15)
            if o_ is not None:
                ax.plot([o_.frac_matched_filter, n.frac_matched_filter], [yy, yy], color="#999999", lw=0.8, zorder=1)
                ax.plot(o_.frac_matched_filter, yy, mk, mfc="white", mec=OPT_COL[opt], ms=5, zorder=2)
            ax.plot(n.frac_matched_filter, yy, mk, color=OPT_COL[opt], ms=5, zorder=3)
    ax.set_yticks(range(4)); ax.set_yticklabels([OPT[o].replace("both 00:19 frequencies, ", "both frequencies,\n").replace("both 00:19 frequencies as", "both frequencies as\n") for o in opts], fontsize=6.5)
    ax.set_xlim(-0.02, 0.7); ax.invert_yaxis(); ax.grid(axis="x", alpha=0.25, lw=0.4)
    ax.set_xlabel("Share of impacts detectable by the matched filter at the best station")
    from matplotlib.lines import Line2D
    ax.legend([Line2D([], [], marker="o", color="k", ls=""), Line2D([], [], marker="s", color="k", ls=""), Line2D([], [], marker="o", mfc="white", mec="k", ls="")],
              ["coupling 0.001, corrected IMOS loss", "coupling 0.00226 (our F-35A estimate, not adopted), corrected", "open marker: before the correction"], fontsize=6, frameon=False, loc="upper left")
    ax.set_title("e  Detectable share before and after the IMOS loss correction", fontsize=8)
    # f: best station share
    ax = fig.add_axes(pos_f)
    sc = {"H01W": "#1b9e77", "3376": "#7570b3", "3315": "#a6a1d6", "H08S": "#d95f02", "other": "#bbbbbb"}
    for j, opt in enumerate(opts):
        bb = BEST[(BEST.key == f"{opt}/p0.5") & np.isclose(BEST.eta, 1e-3)].iloc[0]; left = 0
        vals = {"H01W": bb.share_best_H01W, "3376": bb.share_best_3376, "3315": bb.share_best_3315, "H08S": bb.share_best_H08S}
        vals["other"] = max(0.0, 1 - sum(vals.values()))
        for k_, v in vals.items():
            ax.barh(j, v, left=left, color=sc[k_], height=0.6, label=k_ if j == 0 else None); left += v
        ax.text(1.01, j, f"{100 * vals['H01W']:.0f} %", va="center", fontsize=6)
    ax.set_yticks(range(4)); ax.set_yticklabels([OPT[o].replace("both 00:19 frequencies, ", "both frequencies,\n").replace("both 00:19 frequencies as", "both frequencies as\n") for o in opts], fontsize=6.5); ax.invert_yaxis(); ax.set_xlim(0, 1.12)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.set_xlabel("Share of impacts for which the station has the highest signal-to-noise ratio (coupling 0.001)")
    h_ = [matplotlib.patches.Patch(color=sc[k_]) for k_ in sc]; l_ = ["Cape Leeuwin", "Perth Canyon 3376", "Perth Canyon 3315", "Diego Garcia South", "all others"]
    ax.legend(h_, l_, fontsize=6, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=5)
    ax.set_title("f  Station with the highest predicted signal, same four uses of the 00:19 data", fontsize=8)
    fig.text(0.01, 0.985, "Where the simulated impacts would be heard best: predicted signal-to-noise ratio at the best station, for four uses of the 00:19 data (dive probability 0.5)",
             fontsize=10, ha="left", va="top")
    footnotes(fig, plain, tech)
    print("share north of 20S in map draws:", north)
    return save(fig, fname)
