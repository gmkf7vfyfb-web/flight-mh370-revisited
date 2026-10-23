
import matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
from scipy import signal as SG
COL_WIN = "#f4a261"; COL_EXP = "#5e3c99"; COL_PICK = "#1b7f7a"; COL_OBS = "#111111"; COL_TR = "#3a3a3a"
THR_STYLE = {0.3: dict(color="#bbbbbb", ls=(0,(2,2)), lw=0.8), 0.1: dict(color="#888888", ls=(0,(4,2)), lw=0.8), 0.05: dict(color="#333333", ls=(0,(6,2)), lw=0.9)}
def fmt_hms(x, pos=None):
    x = round(x); return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d}"
def setx(ax, s0, s1, show):
    ax.set_xlim(s0 - T0, s1 - T0); ax.xaxis.set_major_formatter(FuncFormatter(fmt_hms)); ax.xaxis.set_major_locator(MaxNLocator(4))
    if not show: ax.tick_params(labelbottom=False)
def shade(ax, d):
    ax.axvspan(d["w0"] - T0, d["w1"] - T0, color=COL_WIN, alpha=0.28, lw=0, zorder=0)
def obs_lines(ax, c, rx):
    for r_, t_ in zip(c["rx"], c["t_obs"]):
        if r_ == rx: ax.axvline(t_ - T0, color=COL_OBS, lw=0.9, zorder=5)
def pick_marks(ax, d):
    for t, kd, l, off in d.get("marks", []):
        ax.plot([t - T0], [0.0], marker="^", color=COL_PICK, ms=4.5, mfc="white", transform=ax.get_xaxis_transform(), clip_on=False, zorder=6)
    for t, s, l, e in d["picks"]:
        ax.axvline(t - T0, color=COL_PICK, lw=0.8, ls=(0,(1,1)), zorder=4)
        ax.plot([t - T0], [1.0], marker="v", color=COL_PICK, ms=4, transform=ax.get_xaxis_transform(), clip_on=False, zorder=6)
def spec_imos(x500, t0):
    f, tt, Sxx = SG.spectrogram(x500 * 1e6, fs=500, nperseg=500, noverlap=250, scaling="density")
    m = f <= 60; return f[m], t0 + tt, 10 * np.log10(np.maximum(Sxx[m], 1e-12))
def spec_panel(x20, t0):
    f, tt, Sxx = SG.spectrogram(x20 * 1e6, fs=20, nperseg=40, noverlap=30, scaling="density")
    return f, t0 + tt, 10 * np.log10(np.maximum(Sxx, 1e-12))
def level_panel(x20, t0):
    xb = SG.sosfiltfilt(D.SOS_P, np.asarray(x20, float)); t1, lev = D.band_levels_1s(xb * 1e6, 20, [(1.0, 9.0)])
    return t0 + t1, lev[(1.0, 9.0)]

def draw_candidate(c, rows, fname, title, subtitle, foot1, foot2):
    n = len(rows); H = sum(1.15 if d["held"] else 0.45 for d in rows) + 3.0
    fig = plt.figure(figsize=(17, H))
    top = 1 - 1.45 / H; bot = 2.0 / H
    gs = fig.add_gridspec(n, 4, left=0.13, right=0.985, top=top, bottom=bot, hspace=0.55, wspace=0.22, width_ratios=[1.15, 1.0, 1.0, 1.0], height_ratios=[1.0 if d["held"] else 0.38 for d in rows])
    fig.text(0.01, 1 - 0.28 / H, title, ha="left", va="top", fontsize=9.5)
    fig.text(0.01, 1 - 0.58 / H, "\n".join(textwrap.fill(s_, 250) for s_ in subtitle.split("\n")), ha="left", va="top", fontsize=7.5, color="#222222")
    col_titles = ["Sound pressure (5-40 Hz band; Kadri plots 1-9 Hz)", "Spectrogram (dB re 1 uPa^2/Hz)", "Matched-filter statistic and null thresholds", "Level above background median (dB) and expected level"]
    last_held = max([i for i, d in enumerate(rows) if d["held"]] + [0])
    for i, d in enumerate(rows):
        rx, kind = d["rx"], d["kind"]; label = ROW_LABEL[(rx, kind)]
        if not d["held"]:
            ax = fig.add_subplot(gs[i, :]); ax.set_facecolor("#f2f2f2")
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values(): s.set_visible(False)
            ax.text(0.5, 0.5, f"No recording held. Predicted arrival {fmt_hms(d['w0']-T0)} to {fmt_hms(d['w1']-T0)} UTC.  {d['reason']}.",
                    ha="center", va="center", transform=ax.transAxes, fontsize=7.5, color="#444444")
            ax.text(-0.012, 0.5, label.replace("\n", ", "), transform=ax.transAxes, ha="right", va="center", fontsize=7.5)
            continue
        axs = [fig.add_subplot(gs[i, j]) for j in range(4)]
        show = True
        for ax in axs: shade(ax, d)
        # ---------- column A, B
        if kind == "imos":
            allx = []
            for o in d["segs"]:
                t = o["t0"] + np.arange(len(o["x100_pa"])) / 100.0; m = (t >= d["s0"]) & (t <= d["s1"])
                axs[0].plot(t[m] - T0, o["x100_pa"][m], color=COL_TR, lw=0.3, rasterized=True); allx.append(o["x100_pa"][m])
                f, tt, S = spec_imos(o["x500"], o["t0"]); mm = (tt >= d["s0"]) & (tt <= d["s1"])
                if mm.any(): axs[1].pcolormesh(tt[mm] - T0, f, S[:, mm], shading="nearest", cmap="magma", vmin=55, vmax=95, rasterized=True)
                tl = o["t0"] + o["lev_t"]; ml = (tl >= d["s0"]) & (tl <= d["s1"])
                axs[3].plot(tl[ml] - T0, o["lev"][ml] - d["bmed"], color=COL_TR, lw=0.6)
                tm = o["t0"] + o["m1b_t"]; mm2 = (tm >= d["s0"]) & (tm <= d["s1"])
                axs[2].plot(tm[mm2] - T0, o["m1b"][mm2], color=COL_TR, lw=0.6)
            if allx:
                a = np.concatenate(allx); lim = np.percentile(np.abs(a), 99.9) * 1.2 if len(a) else 1
                axs[0].set_ylim(-lim, lim)
            axs[1].set_ylim(0, 60)
        elif kind == "kadri":
            for o in d["segs"]:
                t = o["t0"] + o["t"]; m = (t >= d["s0"]) & (t <= d["s1"])
                axs[0].plot(t[m] - T0, o["x"][m], color=COL_TR, lw=0.3, rasterized=True)
                f, tt, S = spec_panel(o["x"], o["t0"]); mm = (tt >= d["s0"]) & (tt <= d["s1"])
                if mm.any(): axs[1].pcolormesh(tt[mm] - T0, f, S[:, mm], shading="nearest", cmap="magma", vmin=np.percentile(S, 5), vmax=np.percentile(S, 99.5), rasterized=True)
                tl, lv = level_panel(o["x"], o["t0"]); ml = (tl >= d["s0"]) & (tl <= d["s1"])
                axs[3].plot(tl[ml] - T0, lv[ml] - np.median(lv), color=COL_TR, lw=0.6)
                tm = o["t0"] + o["m1b_t"]; mm2 = (tm >= d["s0"]) & (tm <= d["s1"])
                axs[2].plot(tm[mm2] - T0, o["m1b"][mm2], color=COL_TR, lw=0.6, label="raw plot" if o is d["segs"][0] else None)
                if o.get("res") is not None:
                    tr = o["t0"] + o["res_t"]; mr = (tr >= d["s0"]) & (tr <= d["s1"])
                    axs[2].plot(tr[mr] - T0, o["res"][mr], color="#7a7a7a", lw=0.6, ls=(0,(3,1)), label="airgun shots removed" if o is d["segs"][0] else None)
            axs[1].set_ylim(0, 10)
            if rx == "H08S": axs[2].legend(loc="upper left", frameon=False, fontsize=6, handlelength=1.6)
        elif kind == "royer":
            for o in d["segs"]:
                bt = o["band"].t_utc_s.values + T0; bv = o["band"].psd_db_5_40.values; m = (bt >= d["s0"]) & (bt <= d["s1"])
                axs[0].plot(bt[m] - T0, bv[m], color=COL_TR, lw=0.7)
                axs[3].plot(bt[m] - T0, bv[m] - np.nanmedian(bv), color=COL_TR, lw=0.7)
                tt = o["t"]; mm = (tt >= d["s0"]) & (tt <= d["s1"])
                if mm.any(): axs[1].pcolormesh(tt[mm] - T0, o["f"], o["psd"][:, mm], shading="nearest", cmap="magma", vmin=70, vmax=100, rasterized=True)
            axs[1].set_ylim(0, 60)
            axs[2].text(0.5, 0.5, "No waveform held: only the published\nspectrogram, so no matched filter", transform=axs[2].transAxes, ha="center", va="center", fontsize=7, color="#555555")
            axs[2].set_yticks([])
            for ax in (axs[0], axs[3]): pick_marks(ax, d)
        if kind in ("imos", "kadri"):
            for a_, st_ in THR_STYLE.items(): axs[2].axhline(d["thr"][a_], **st_)
            if "stat" in d:
                axs[2].plot([d["stat_t"] - T0], [d["stat"]], marker="o", ms=3.5, mfc="white", mec=COL_TR, zorder=6)
                axs[2].text(0.99, 0.95, f"max in window {d['stat']:.2f}, p {d['p']:.2g}", transform=axs[2].transAxes, ha="right", va="top", fontsize=6.5)
            axs[2].set_ylim(min(-0.1, axs[2].get_ylim()[0]), max(1.0, d["thr"][0.05] * 1.15))
            if d["picks"] or d.get("marks"):
                for ax in (axs[0], axs[3]): pick_marks(ax, d)
        # ---------- expected level (col D)
        if rx in c.get("snr", {}) and np.isfinite(c["snr"][rx]):
            e = c["snr"][rx]; axs[3].axhline(e, color=COL_EXP, lw=1.3); axs[3].axhline(c["L50"][rx], color=COL_EXP, lw=0.8, ls=(0,(1,1.5)))
            yl = axs[3].get_ylim(); axs[3].set_ylim(min(yl[0], e - 3, c["L50"][rx] - 3), max(yl[1], e + 4, c["L50"][rx] + 4))
            axs[3].text(0.99, 0.95, f"expected {e:+.0f} dB, detection probability {c['pd'][rx]:.2f}" + (" (proxy noise)" if rx in ("H01W","H08S") else ""),
                        transform=axs[3].transAxes, ha="right", va="top", fontsize=6.5, color=COL_EXP)
        elif rx in c.get("snr", {}):
            axs[3].text(0.99, 0.95, "expected level: none (sound path blocked)", transform=axs[3].transAxes, ha="right", va="top", fontsize=6.5, color=COL_EXP)
        else:
            axs[3].text(0.99, 0.95, ("expected level: none (no flight-model source)" if not c.get("snr") else "expected level: not modelled at this site" if rx not in ("3250",) else "expected level: none (sound path blocked)"),
                        transform=axs[3].transAxes, ha="right", va="top", fontsize=6.5, color=COL_EXP)
        for ax in axs:
            obs_lines(ax, c, rx); setx(ax, d["s0"], d["s1"], show)
            ax.tick_params(labelsize=6)
        if d["cover_frac"] < 0.999:
            axs[0].text(0.01, 0.05, f"held for {100*d['cover_frac']:.0f} % of the window", transform=axs[0].transAxes, fontsize=6.5, color="#444444")
        axs[0].text(-0.2, 0.62, label, transform=axs[0].transAxes, ha="right", va="center", fontsize=7.5)
        axs[0].text(-0.2, 0.12, "\n".join(textwrap.wrap(verdict(c, d)[1], 34)), transform=axs[0].transAxes, ha="right", va="center", fontsize=6.5, color=VCOL[verdict(c, d)[0]])
        axs[1].set_ylabel("Hz", fontsize=6.5, labelpad=1)
        if i == 0 or not any(r_["held"] for r_ in rows[:i]):
            for j, ax in enumerate(axs): ax.set_title(col_titles[j], loc="left", fontsize=7.5)
    for j in range(4):
        pass
    fig.text(0.13, bot - 0.42 / H, "Time (UTC, 8 March 2014). Orange band: predicted arrival window (95 %). Black line: the signal that defines the candidate. "
             "Purple line: expected level of the candidate if it were the impact; dotted purple: level for detection probability 0.5.\n"
             "Grey dashed lines: matched-filter thresholds for p = 0.3, 0.1, 0.05 (light to dark). Teal: Royer's picked arrivals (filled triangle and dotted line: his Table 5; open triangle: the arrival marks on his figures).",
             ha="left", va="top", fontsize=6.8)
    fig.text(0.01, bot - 0.80 / H, foot1, ha="left", va="top", fontsize=6.5, wrap=True)
    fig.text(0.01, bot - 1.25 / H, foot2, ha="left", va="top", fontsize=6.0, color="#333333", wrap=True)
    fig.savefig(fname + ".png", dpi=200); fig.savefig(fname + ".pdf"); plt.close(fig)
