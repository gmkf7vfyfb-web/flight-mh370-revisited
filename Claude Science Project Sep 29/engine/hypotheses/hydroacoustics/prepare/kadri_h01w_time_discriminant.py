"""PRE-REGISTRATION and implementation — run J Task 1, amendment A1 (Pete, 13 Oct, during the run).
Committed BEFORE any statistic in this file was computed.

QUESTION. Can Kadri's own main signal be SEEN in the digitised Cape Leeuwin (H01W) trace, and does that
resolve which of his two times is the detection? His text gives 00:52:03 and calls it the figure 9c peak
(p. 9); his caption gives 00:54:30 (p. 14). Figure 9 panel c starts at 00:47:00 and runs 600 s, so it
CONTAINS BOTH TIMES. This is a two-point comparison between times fixed by his paper, not a search.

WHY IT MATTERS HERE. The two times imply source times 00:34:55 and 00:37:22 and therefore different
arrival windows at every other receiver. Task 1 tests both. If the digitised panel settles which time
carries the signal, the other option stops consuming look-elsewhere trials, and the question put to
Kadri in the collaboration package becomes a confirmation rather than an open ask.

DATA. kadri-2024-figure9-panel-c-H01W.csv, 8,716 vertices, start 00:47:00, pressure axis +/-1 Pa.
  Panels a (00:27) and b (00:37) are the same station and night and are used as background only.
  CLIPPING: the panel axis is +/-1 Pa and Kadri's level at his time was previously recorded as CLIPPED
  at that limit, so every amplitude statistic here is a LOWER BOUND. The fraction of samples at the rail
  within each test window is computed and reported, and a statistic whose window is clipped is labelled.

STATISTICS, at each of the two candidate times, in a window of +/- 3 s (the digitisation's indicative
half-linewidth in time is 0.508 s, so +/-3 s is about six times that):
  S1 envelope_peak_pa   peak of the 2-40 Hz analytic envelope
  S2 rms_pm1s_pa        RMS over +/- 1 s, 2-40 Hz  (the convention already used for Kadri's H01W level)
  S3 stalta_max         max of STA/LTA, STA 2 s over the preceding LTA 30 s, 2-40 Hz
  S4 matched_filter     max normalised cross-correlation against the committed real transient T_C2
All four are 'larger is more signal'.

NULL. All positions of the same +/- 3 s window across panel c, step one sample (primary), and across
  panels a, b and c pooled (secondary). p = #{positions at least as extreme} / n_positions, so the floor
  is 1/n_positions and is reported per row. No new background read.

PANEL MAXIMUM. The single most direct observable: the time of the panel-c maximum of the 2-40 Hz
  envelope, reported with its distance from each candidate time. The text claims 00:52:03 IS the plotted
  peak, so this is a direct check of the text against the figure it cites.

DECISION RULE, fixed before computing:
  - 'text time confirmed' if the panel-c envelope maximum lies within +/- 5 s of 00:52:03 AND the text
    time ranks higher than the caption time on at least three of S1-S4.
  - 'caption time confirmed' on the mirror condition.
  - 'not discriminated' otherwise, including when neither time reaches the 0.3 screen tier against the
    panel-c null — in which case the honest reading is that the digitised panel cannot separate them and
    the question stays with Kadri.
  A confirmation here is a statement about WHICH TIME HIS FIGURE SHOWS. It is not a detection of an
  impact signal and does not bear on the MH370 hypothesis either way.

ALSO IN THIS FILE: the two H08S trace plots required by the work order's acceptance - the predicted
  window 01:16:20-01:17:10 and the four flagged outliers 01:11:30-01:14:10. Plots are not statistics.

OUTPUTS: kadri_northern/h01w_time_discriminant.csv, h01w_time_discriminant.json,
  kadri-northern-h08s-trace-predicted-window.png, kadri-northern-h08s-trace-flagged-outliers.png,
  kadri-northern-h01w-panel-c.png
Usage: python kadri_h01w_time_discriminant.py <kadri data dir> <out dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from numpy.lib.stride_tricks import sliding_window_view  # noqa: E402
from scipy import signal  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
import h08s_shot_outliers as H  # noqa: E402
import kadri_northern_conditional as KN  # noqa: E402
import kadri_table1_test as KT  # noqa: E402

FS = 40.0
HALF = 3.0
CAND = {"text": "00:52:03", "caption": "00:54:30"}
PANEL_START = {"a": "00:27:00", "b": "00:37:00", "c": "00:47:00"}
RAIL_PA = 1.0
FLAGGED = [("01:11:39", -4.17), ("01:12:49", 4.11), ("01:13:09", -4.91), ("01:13:59", -3.16)]


def load_h01w(kd, pnl):
    f = Path(kd) / "kadri-figure-extraction" / "figure9-vector-traces" / f"kadri-2024-figure9-panel-{pnl}-H01W.csv"
    tr = pd.read_csv(f)
    t = (pd.to_datetime(tr.utc) - KT.DAY0).dt.total_seconds().values
    o = np.argsort(t)
    t, p = t[o], tr.pressure_pa.values[o]
    tg = np.arange(t[0], t[-1], 1 / FS)
    return tg, np.interp(tg, t, p)


def band(x):
    return signal.sosfiltfilt(signal.butter(4, [2, 19.9], btype="bandpass", fs=FS, output="sos"), x)


def stats_series(tg, p, tmpl):
    """Four statistic series on a common time base."""
    y = band(p)
    env = np.abs(signal.hilbert(y))
    n = int(round(2 * HALF * FS))
    out = {"envelope_peak_pa": sliding_window_view(env, n).max(1),
           "rms_pm1s_pa": np.sqrt(sliding_window_view(y ** 2, int(2 * FS)).mean(1))}
    y2 = y ** 2
    cs = np.concatenate([[0], np.cumsum(y2)])
    sta, lta = int(2 * FS), int(30 * FS)
    i = np.arange(lta, len(y) - sta + 1)
    sl = ((cs[i + sta] - cs[i]) / sta) / np.maximum((cs[i] - cs[i - lta]) / lta, 1e-30)
    out["stalta_max"] = sliding_window_view(sl, min(n, len(sl))).max(1)
    out["stalta_t0"] = tg[lta + sta // 2]
    k = tmpl / np.linalg.norm(tmpl)
    num = signal.correlate(y, k, mode="valid")
    e = np.sqrt(np.maximum(signal.correlate(y2, np.ones(len(k)), mode="valid"), 1e-30))
    mf = np.abs(num) / e
    out["matched_filter"] = sliding_window_view(mf, min(n, len(mf))).max(1)
    out["_env"], out["_y"] = env, y
    return out


def at_time(tg, ser, key, t):
    """Value of a sliding-window statistic for the window centred on t."""
    v = ser[key]
    if key == "stalta_max":
        t0 = ser["stalta_t0"]
        j = int(round((t - HALF - t0) * FS))
    else:
        j = int(round((t - HALF - tg[0]) * FS))
    j = max(0, min(j, len(v) - 1))
    return float(v[j])


def main(kd, out_dir):
    kd, out = Path(kd), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmpl = signal.resample_poly(KN.t_c2_500(), int(FS), 500)
    S, series = {}, {}
    for pnl in "abc":
        tg, p = load_h01w(kd, pnl)
        series[pnl] = (tg, p)
        S[pnl] = stats_series(tg, p, tmpl)
    tg, p = series["c"]
    envc = S["c"]["_env"]
    jmax = int(np.argmax(envc))
    panel_max = dict(t_utc=KN.utc(tg[jmax]), t_s=float(tg[jmax]), envelope_pa=float(envc[jmax]),
                     dt_from_text_s=float(tg[jmax] - KN.secs(CAND["text"])),
                     dt_from_caption_s=float(tg[jmax] - KN.secs(CAND["caption"])))
    rows = []
    for opt, hms in CAND.items():
        tc = KN.secs(hms)
        m = (tg >= tc - HALF) & (tg <= tc + HALF)
        clip = float(np.mean(np.abs(p[m]) >= RAIL_PA * 0.999)) if m.any() else np.nan
        for key in ("envelope_peak_pa", "rms_pm1s_pa", "stalta_max", "matched_filter"):
            obs = at_time(tg, S["c"], key, tc)
            r = dict(option=opt, kadri_time_utc=hms, statistic=key, observed=obs,
                     clipped_fraction_in_window=clip)
            for tag, pnls in (("panelc", "c"), ("pooled", "abc")):
                nl = np.concatenate([S[q][key] for q in pnls])
                hit = int((nl >= obs).sum())
                r[f"p_{tag}"] = float(hit / len(nl))
                r[f"n_null_{tag}"] = int(len(nl))
                r[f"floor_{tag}"] = float(1.0 / len(nl))
                r[f"rank_{tag}"] = hit
            rows.append(r)
    R = pd.DataFrame(rows)
    piv = R.pivot(index="statistic", columns="option", values="observed")
    piv["ratio_text_over_caption"] = piv["text"] / piv["caption"]
    wins_text = int((piv["text"] > piv["caption"]).sum())
    screened = R[R.p_panelc <= KN.TIERS["screen"]]
    near_text = abs(panel_max["dt_from_text_s"]) <= 5.0
    near_cap = abs(panel_max["dt_from_caption_s"]) <= 5.0
    if near_text and wins_text >= 3:
        verdict = "text time confirmed as the plotted figure 9c peak"
    elif near_cap and wins_text <= 1:
        verdict = "caption time confirmed as the plotted peak"
    else:
        verdict = "not discriminated by the digitised panel"
    summ = dict(panel_max=panel_max, ratio=piv.to_dict(), n_statistics_favouring_text=wins_text,
                n_screened_at_0p3=int(len(screened)), verdict=verdict,
                caveat="A confirmation here says which time his FIGURE shows. It is not a detection of "
                       "an impact signal and does not bear on the MH370 hypothesis either way. Panel c "
                       "is clipped at +/-1 Pa, so every amplitude statistic is a lower bound.")
    R.to_csv(out / "h01w_time_discriminant.csv", index=False)
    (out / "h01w_time_discriminant.json").write_text(json.dumps(summ, indent=1, default=str))

    # ---- panel c figure
    fig, ax = plt.subplots(figsize=(9, 3.2), dpi=300)
    ax.plot(tg, p, lw=0.35, color="0.35")
    for opt, hms in CAND.items():
        ax.axvline(KN.secs(hms), color="#b2182b" if opt == "text" else "#2166ac", lw=1.2,
                   label=f"Kadri {opt} time {hms}")
    ax.axvline(tg[jmax], color="#1a9850", lw=1.0, ls="--", label=f"panel maximum {panel_max['t_utc']}")
    ax.set_xlim(tg[0], tg[-1])
    ax.set_xticks(np.arange(KN.secs("00:47:00"), KN.secs("00:57:01"), 60))
    ax.set_xticklabels([KN.utc(v)[:5] for v in np.arange(KN.secs("00:47:00"), KN.secs("00:57:01"), 60)])
    ax.set_xlabel("time, UTC on 8 March 2014")
    ax.set_ylabel("pressure, Pa")
    ax.set_title("Cape Leeuwin (H01W), digitised figure 9 panel c")
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(out / "kadri-northern-h01w-panel-c.png")
    plt.close(fig)

    # ---- the two H08S trace plots required by the work order
    shots, h08s_series, _ = KN.h08s_shot_table(kd)
    for name, a, b, marks in [("predicted-window", "01:16:20", "01:17:10", [("01:16:19", "01:17:33")]),
                              ("flagged-outliers", "01:11:30", "01:14:10", [])]:
        tge, pe = h08s_series["e"]
        m = (tge >= KN.secs(a)) & (tge <= KN.secs(b))
        fig, ax = plt.subplots(figsize=(9, 3.2), dpi=300)
        ax.plot(tge[m], pe[m], lw=0.5, color="0.3")
        if name == "predicted-window":
            for wa, wb in marks:
                ax.axvspan(KN.secs(wa), KN.secs(wb), color="#fdae61", alpha=0.35,
                           label="predicted 95 per cent window, text option")
            ax.axvline(KN.secs("01:16:47"), color="#4575b4", lw=1.0, ls=":",
                       label="gap-power excursion, pre-registered target")
        else:
            for hms, z in FLAGGED:
                ax.axvline(KN.secs(hms), color="#b2182b", lw=1.0)
                ax.annotate(f"{hms}\nz = {z:+.2f}", (KN.secs(hms), ax.get_ylim()[1]), fontsize=6,
                            ha="center", va="top")
        for t in shots[(shots.t >= KN.secs(a)) & (shots.t <= KN.secs(b))].t.values:
            ax.plot([t], [0], marker="|", ms=8, color="#1a9850")
        ax.set_xlim(KN.secs(a), KN.secs(b))
        tick = np.arange(KN.secs(a), KN.secs(b) + 1, 10 if name == "predicted-window" else 20)
        ax.set_xticks(tick)
        ax.set_xticklabels([KN.utc(v) for v in tick], fontsize=6, rotation=45, ha="right")
        ax.set_xlabel("time, UTC on 8 March 2014")
        ax.set_ylabel("pressure, Pa")
        ax.set_title(f"Diego Garcia South (H08S), digitised figure 9 panel e, {a} to {b}")
        ax.legend(frameon=False, fontsize=7, loc="upper left")
        fig.tight_layout()
        fig.savefig(out / f"kadri-northern-h08s-trace-{name}.png")
        plt.close(fig)
    print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
