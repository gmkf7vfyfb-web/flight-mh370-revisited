"""Figures for the IMOS full-deployment noise statistics (call after apply_figure_style())."""
from __future__ import annotations

import textwrap

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyse import SITES

FOCAL = "#c0392b"      # 8 March 2014
BAND = "#2c6e9b"       # distribution shading / medians
MARCH = "#e08e0b"
GREY = "#8a8a8a"
W1 = (pd.Timestamp("2014-03-08T00:00Z"), pd.Timestamp("2014-03-08T08:00Z"))


def footnotes(fig, plain, tech, y0=0.0, width=190):
    t = "Note: " + plain
    s = "Technical note: " + tech
    txt = "\n".join(textwrap.wrap(t, width)) + "\n" + "\n".join(textwrap.wrap(s, width))
    fig.text(0.01, y0, txt, ha="left", va="top", fontsize=6, color="#333333")


def monthly_spectra(spec, lg, plain, tech):
    f = spec["f_hz"]
    groups = list(spec["groups"])
    pcts = list(spec["pcts"])
    ip = {p: pcts.index(p) for p in (5, 25, 50, 75, 95)}
    months = [g for g in groups if g[:2] == "20" and spec["n_rec"][groups.index(g)] > 0]
    dep = spec["rec_pct"][groups.index("deployment")][ip[50]]
    ncol = 4
    nrow = int(np.ceil(len(months) / ncol))
    fig, axs = plt.subplots(nrow, ncol, figsize=(7.2, 1.55 * nrow + 0.4), sharex=True, sharey=True,
                            gridspec_kw=dict(hspace=0.12, wspace=0.06))
    axs = np.atleast_2d(axs)
    lo = np.nanmin(spec["rec_pct"][[groups.index(m) for m in months], ip[5]]) - 3
    hi = np.nanmax(spec["rec_pct"][[groups.index(m) for m in months], ip[95]]) + 3
    for k, ax in enumerate(axs.flat):
        if k >= len(months):
            ax.set_visible(False)
            continue
        m = months[k]
        gi = groups.index(m)
        P = spec["rec_pct"][gi]
        ax.axvspan(2, 8, color="#eeeeee", lw=0, zorder=0)
        ax.fill_between(f, P[ip[5]], P[ip[95]], color=BAND, alpha=0.18, lw=0, label="5th-95th percentile")
        ax.fill_between(f, P[ip[25]], P[ip[75]], color=BAND, alpha=0.38, lw=0, label="25th-75th percentile")
        ax.plot(f, P[ip[50]], color=BAND, lw=0.9, label="median")
        ax.plot(f, dep, color="k", lw=0.6, ls="--", label="deployment median")
        if m == "2014-03":
            ax.plot(f, spec["win_median"], color=FOCAL, lw=0.9, label="8 Mar 2014 00:00-08:00 UTC, median")
        ax.set_xscale("log")
        ax.set_xlim(2, 1000)
        ax.set_ylim(lo, hi)
        ax.text(0.97, 0.94, f"{pd.Timestamp(m + '-01').strftime('%b %Y')}  n={spec['n_rec'][gi]}",
                transform=ax.transAxes, ha="right", va="top", fontsize=6)
        ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
        if k % ncol == 0:
            ax.set_ylabel("PSD (dB re 1 µPa²/Hz)")
        if k >= len(months) - ncol:
            ax.set_xlabel("Frequency (Hz)")
            ax.tick_params(labelbottom=True)
    h, l = [], []
    for ax in axs.flat:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in l:
                h.append(hh)
                l.append(ll)
    H = fig.get_figheight()
    top = max(a.get_position().y1 for a in axs.flat if a.get_visible())
    bot = min(a.get_position().y0 for a in axs.flat if a.get_visible())
    fig.legend(h, l, loc="lower center", ncol=5, frameon=False, fontsize=6, bbox_to_anchor=(0.5, top + 0.08 / H))
    fig.suptitle(f"{SITES[lg]['name']} seabed recorder: noise spectrum percentiles for each month of the deployment",
                 x=0.01, ha="left", y=top + 0.38 / H, fontsize=8)
    footnotes(fig, plain, tech, y0=bot - 0.55 / H)
    return fig


def timeseries(R, ranks, plain, tech, st="SPL_5_40", ylabel="5-40 Hz band level (dB re 1 µPa)"):
    lgs = ["3376", "3274", "3250"]
    fig = plt.figure(figsize=(7.6, 6.6))
    gs = fig.add_gridspec(3, 2, width_ratios=[5, 1], wspace=0.03, hspace=0.48)
    for i, lg in enumerate(lgs):
        D = R[(R.logger == lg) & R.qc_pass].sort_values("t_utc")
        ax = fig.add_subplot(gs[i, 0])
        axh = fig.add_subplot(gs[i, 1], sharey=ax)
        t = D.t_utc.dt.tz_convert(None)
        ax.scatter(t, D[st], s=0.4, color=GREY, alpha=0.35, lw=0, rasterized=True, label="one 307 s record")
        dmed = D.set_index(t)[st].resample("D").median()
        ax.plot(dmed.index, dmed.values, color=BAND, lw=0.7, label="daily median")
        w = D[(D.t_utc >= W1[0]) & (D.t_utc < W1[1])]
        ax.axvline(pd.Timestamp("2014-03-08"), color=FOCAL, lw=0.6, alpha=0.6)
        ax.scatter(w.t_utc.dt.tz_convert(None), w[st], s=5, color=FOCAL, lw=0, zorder=5,
                   label="8 Mar 2014 00:00-08:00 UTC records")
        ax.set_ylabel(ylabel if i == 1 else "")
        ax.set_title(f"{SITES[lg]['name']}", loc="left", fontsize=8)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
        ax.margins(x=0.01)
        lo, hi = np.percentile(D[st], [0.05, 99.95])
        ax.set_ylim(lo - 2, hi + 2)
        axh.hist(D[st], bins=np.arange(lo - 2, hi + 2, 0.5), orientation="horizontal", color=GREY, alpha=0.6)
        rk = ranks[(ranks.logger == lg) & (ranks.statistic == st) & ranks.window.str.startswith("W1")].iloc[0]
        axh.axhline(rk.window_median, color=FOCAL, lw=0.9)
        axh.text(1.02, 0.98, f"8 Mar window\nmedian {rk.window_median:.1f} dB\n"
                 f"rank {rk.day_window_rank_deployment:.0f} % of\n{rk.n_days_deployment} days\n"
                 f"rank {rk.day_window_rank_march:.0f} % of\n{rk.n_days_march} March days",
                 transform=axh.transAxes, ha="left", va="top", fontsize=5.5, color=FOCAL)
        axh.tick_params(labelleft=False)
        axh.set_xticks([])
        for s in ("top", "right"):
            axh.spines[s].set_visible(False)
        if i == 0:
            ax.legend(loc="upper left", frameon=False, fontsize=6, markerscale=2, ncol=3)
    fig.suptitle("5-40 Hz noise level through each full deployment, with 8 March 2014 marked", x=0.01, ha="left",
                 y=0.95, fontsize=8)
    footnotes(fig, plain, tech, y0=0.05)
    return fig


def diel_fig(Dl, R, plain, tech, st="SPL_5_40"):
    lgs = ["3376", "3274", "3250"]
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.6), sharey=False, gridspec_kw=dict(wspace=0.28))
    for ax, lg in zip(axs, lgs):
        for scope, col, lab in (("deployment", BAND, "deployment"), ("2014-03", MARCH, "March 2014")):
            d = Dl[(Dl.logger == lg) & (Dl.scope == scope)].sort_values("local_solar_hour")
            x = d.local_solar_hour + 0.5
            ax.fill_between(x, d.p25, d.p75, color=col, alpha=0.25, lw=0, step="mid")
            ax.plot(x, d.p50, color=col, lw=1.0, drawstyle="steps-mid", label=f"{lab}: median and 25th-75th percentile")
        e = R[(R.logger == lg) & R.qc_pass & (R.t_utc >= pd.Timestamp("2014-03-08T00:00Z")) &
              (R.t_utc < pd.Timestamp("2014-03-09T00:00Z"))]
        ax.scatter(e.local_solar_hour, e[st], s=4, color=FOCAL, zorder=5, lw=0, label="8 Mar 2014 (UTC day) records")
        ax.set_xlim(0, 24)
        ax.set_xticks([0, 6, 12, 18, 24])
        ax.set_xlabel("Local mean solar time (h)")
        ax.set_title(SITES[lg]["name"], loc="left", fontsize=8)
        ax.margins(y=0.05)
    axs[0].set_ylabel("5-40 Hz band level (dB re 1 µPa)")
    axs[0].legend(loc="upper center", bbox_to_anchor=(1.75, 1.30), ncol=3, frameon=False, fontsize=6)
    fig.suptitle("Daily cycle of 5-40 Hz noise at each recorder", x=0.01, ha="left", y=1.17, fontsize=8)
    footnotes(fig, plain, tech, y0=-0.10)
    return fig
