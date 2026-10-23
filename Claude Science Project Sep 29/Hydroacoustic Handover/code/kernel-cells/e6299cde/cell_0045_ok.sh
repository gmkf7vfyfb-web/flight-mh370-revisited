cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
cat > charts.py <<'EOF'
"""Charts for the run J searches note (preregistration.py section 10; chart rule of 10 Oct 2026: no project jargon in
titles, axes or legends; two footnotes). Usage: python charts.py <search_out_dir> <results_dir>"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
sys.path.insert(0, str(Path(__file__).resolve().parent))
import preregistration as R

plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150, "savefig.dpi": 300})
RX = ["H01W", "H08S", "3315", "3376", "3274", "3275", "3250"]
NAME = {"H01W": "Cape Leeuwin H01W\n(digitised plot)", "H08S": "Diego Garcia H08S\n(digitised plot)", "3315": "Perth Canyon 3315", "3376": "Perth Canyon 3376",
        "3274": "Portland 3274", "3275": "Portland 3275", "3250": "Scott Reef 3250\n(no-information row)"}
LEVEL_COL = {"screen": "#c6dbef", "mark": "#6baed6", "report": "#08519c"}
DET_OFF = {"M1b": 0.22, "M1b_res": 0.22, "D1": 0.0, "BE": -0.22, "Z_res": -0.22}
T0 = R.T0


def hm(x, _=None):
    s = x - T0; return f"{int(s // 3600):02d}:{int((s % 3600) // 60):02d}"


def foot(fig, plain, tech):
    fig.text(0.01, 0.045, plain, fontsize=6, ha="left", va="bottom", wrap=True, color="0.25")
    fig.text(0.01, 0.005, tech, fontsize=5.2, ha="left", va="bottom", wrap=True, color="0.35")


def timeline(sd, rd):
    W = pd.concat([pd.read_csv(sd / "imos" / "imos_windows.csv"), pd.read_csv(sd / "panels" / "panel_windows.csv")], ignore_index=True); W["receiver"] = W.receiver.astype(str)
    PW = pd.read_csv(R.RD / "searches_run_j" / "prereg_windows.csv"); PW["receiver"] = PW.receiver.astype(str)
    fig, ax = plt.subplots(figsize=(11, 7.4)); fig.subplots_adjust(left=0.13, right=0.99, top=0.9, bottom=0.2)
    x0, x1 = R.hms_to_unix("00:20:00"), R.hms_to_unix("01:45:00")
    for i, rx in enumerate(RX):
        y = len(RX) - 1 - i
        u = PW[(PW.receiver == rx) & (PW.branch == "SOFAR") & (PW.kind == "union")].iloc[0]
        ax.axhspan(y - 0.45, y + 0.45, xmin=(u.start_unix - x0) / (x1 - x0), xmax=(u.end_unix - x0) / (x1 - x0), color="#fff3cd", zorder=0)
        for o, lw in (("D0", 2.2), ("D2", 1.0), ("D3", 1.0), ("D4", 1.0)):
            r = PW[(PW.receiver == rx) & (PW.branch == "SOFAR") & (PW.kind == "option99") & (PW.option == o)].iloc[0]
            ax.plot([r.start_unix, r.end_unix], [y - 0.44, y - 0.44], color="#b8860b", lw=lw, solid_capstyle="butt", alpha=0.9 if o == "D0" else 0.5)
        # held data = searched windows
        g = W[W.receiver == rx]
        for ws in sorted(set(g.window_start_utc)):
            a = R.hms_to_unix(ws + ".0"); ax.plot([a, a + R.WINDOW_S], [y + 0.44, y + 0.44], color="0.45", lw=3, solid_capstyle="butt")
        c = g[g.p < R.SCREEN_P]
        for lev in ("screen", "mark", "report"):
            cc = c[c.label == lev]
            ax.scatter(cc.t_unix, y + cc.detector.map(DET_OFF).fillna(0.0), s=18 if lev != "report" else 30, color=LEVEL_COL[lev], edgecolor="k" if lev == "report" else "none", lw=0.4, zorder=3)
    for k, (nm, hms) in enumerate((("text time 00:52:03", "00:52:03"), ("caption time 00:54:30", "00:54:30"))):
        ax.axvline(R.hms_to_unix(hms), color="#d62728" if k == 0 else "#ff7f0e", lw=0.9, ls="--", zorder=2)
    yH = len(RX) - 1
    for nm, (a, b) in R.BOXES.items():
        if nm.startswith("poster"):
            ax.add_patch(plt.Rectangle((R.hms_to_unix(a), yH - 0.45), R.hms_to_unix(b) - R.hms_to_unix(a), 0.9, fill=False, hatch="////", edgecolor="#7f7f7f", lw=0.6, zorder=1))
    ax.set_xlim(x0, x1); ax.set_ylim(-0.6, len(RX) - 0.4)
    ax.set_yticks(range(len(RX))); ax.set_yticklabels([NAME[r] for r in RX[::-1]])
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(300)); ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(hm))
    ax.set_xlabel("Time at the receiver, UTC, 8 March 2014")
    ax.set_title("Candidate rows at every receiver sit inside the predicted arrival windows, at the rate chance predicts; none is a detection", loc="left")
    h = [Patch(color="#fff3cd", label="search window (99 % arrival window, union over options)"), Line2D([], [], color="#b8860b", lw=2.2, label="99 % window, 00:19 data held out (thin: other 00:19 options)"),
         Line2D([], [], color="0.45", lw=3, label="recording searched"), Line2D([], [], marker="o", ls="", color=LEVEL_COL["screen"], label="candidate row, p < 0.3 (screen)"),
         Line2D([], [], marker="o", ls="", color=LEVEL_COL["mark"], label="p < 0.1 (mark)"), Line2D([], [], marker="o", ls="", color=LEVEL_COL["report"], markeredgecolor="k", label="p < 0.05 (report)"),
         Line2D([], [], color="#d62728", ls="--", label="Kadri text time 00:52:03"), Line2D([], [], color="#ff7f0e", ls="--", label="Kadri caption time 00:54:30"),
         Patch(fill=False, hatch="////", edgecolor="#7f7f7f", label="poster panel (a) boxes 1-4")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=6.5)
    ax.text(x0 + 60, len(RX) - 0.5, "rows per receiver: upper = matched filter, middle = energy ratio, lower = band energy", fontsize=6, color="0.3", va="bottom")
    foot(fig, "(i) What the chart shows: for each receiver, the time span in which the sound of an impact on the 7th arc would arrive (yellow), the recordings we hold (grey bars), and every time at which a detector "
              "statistic was in the top 30 % of its background (dots; darker = rarer). The red and orange lines are the two times Kadri gives for his main signal. The hatched boxes are the weak signals marked on his poster. "
              "The counts of dots match what chance gives on other days; no dot is a detection.",
         "(ii) Source posterior run J (74 seeds + northern supplement), 00:19 options D0' (held out, thick), D2, D3, D4, p = 0.5; windows = [q0.5, q99.5] of impact time + geodesic/c, c ~ N(1.482, 0.006) km/s (SOFAR; union over p in {0, 0.5, 1}). "
              "Detectors: envelope matched filter (KRAKEN templates), STA/LTA 2/30 s, band energy 2-5/5-10/10-20/20-40/5-40 Hz; 55 s windows; p = (k+1)/(n+1) against ~6,500 background windows of the same logger on 1-7, 9-15 March "
              "(3315 <- 3376, 3275 <- 3274; panels: emulated 3376 plot). H01W/H08S = DIGITISED Kadri (2024) Fig. 9 panels, not recordings. H08S raw-panel rows are airgun-dominated. Caveats C1 (propagation slope misfit) and C2 (coupling not calibrated). "
              "Pre-registration a4cdab0; PREDICTIVE, NOT CALIBRATED.")
    for ext in ("png", "pdf"): fig.savefig(rd / f"hydroacoustics-searches-run-j-timeline.{ext}")
    plt.close(fig)


def table1(sd, rd):
    T = pd.read_csv(sd / "named" / "table1_verdicts.csv")
    PW = pd.read_csv(R.RD / "searches_run_j" / "prereg_windows.csv")
    bz = pd.read_csv(R.GEOM / "bearing_h01w.csv"); c = np.cumsum(bz.mass_D0) / bz.mass_D0.sum(); mid = (bz.baz_lo + bz.baz_hi) / 2
    q05, q50, q95 = (float(np.interp(q, c, mid)) for q in (0.05, 0.5, 0.95)); q005, q995 = (float(np.interp(q, c, mid)) for q in (0.005, 0.995))
    fig, ax = plt.subplots(figsize=(9, 5.6)); fig.subplots_adjust(left=0.1, right=0.98, top=0.88, bottom=0.25)
    x0, x1 = R.hms_to_unix("00:36:00"), R.hms_to_unix("01:16:00")
    for o, col, al in (("D0", "#fff3cd", 1.0), ("D3", "#ffe0b2", 0.6)):
        r = PW[(PW.receiver == "H01W") & (PW.branch == "SOFAR") & (PW.kind == "option99") & (PW.option == o)].iloc[0]
        ax.axvspan(r.start_unix, r.end_unix, color=col, alpha=al, zorder=0, lw=0)
    ax.axhspan(q005, q995, color="#d9e8f5", zorder=0, lw=0); ax.axhspan(q05, q95, color="#9ecae1", zorder=0, lw=0); ax.axhline(q50, color="#3182bd", lw=0.8)
    VC = {"favoured": "#1b9e77", "uninformative": "#7f7f7f", "disfavoured": "#d95f02"}
    for _, r in T.iterrows():
        tu = R.hms_to_unix(r.time_utc); ok = r.implied_time_band_D0 != "outside 99%"
        ax.scatter(tu, r.bearing_deg, s=46, color=VC[r.bearing_verdict], marker="o" if ok else "X", edgecolor="k", lw=0.5, zorder=3)
    for k, (hms, col) in enumerate((("00:52:03", "#d62728"), ("00:54:30", "#ff7f0e"))):
        ax.axvline(R.hms_to_unix(hms), color=col, lw=0.9, ls="--", zorder=2)
    ax.annotate("306.18°, caption time", (R.hms_to_unix("00:54:30"), 306.18), xytext=(20, 10), textcoords="offset points", fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.5))
    ax.annotate("306.18°, text time", (R.hms_to_unix("00:52:03"), 306.18), xytext=(-70, 14), textcoords="offset points", fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.5))
    ax.set_xlim(x0, x1); ax.set_ylim(225, 350)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(300)); ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(hm))
    ax.set_xlabel("Arrival time at Cape Leeuwin H01W, UTC, 8 March 2014"); ax.set_ylabel("Bearing from H01W to the source (degrees true)")
    ax.set_title("Kadri's Table 1: the rows that point at the core region arrive too early; the rows in the time window point north of it", loc="left")
    h = [Patch(color="#fff3cd", label="99 % arrival window, 00:19 data held out"), Patch(color="#ffe0b2", label="99 % arrival window, both 00:19 BFOs as recorded"),
         Patch(color="#9ecae1", label="predicted bearing, 5-95 % (light: 0.5-99.5 %)"), Line2D([], [], color="#3182bd", label="predicted bearing, median"),
         Line2D([], [], marker="o", ls="", color=VC["favoured"], markeredgecolor="k", label="bearing favours the posterior (BF ≥ 10)"),
         Line2D([], [], marker="o", ls="", color=VC["uninformative"], markeredgecolor="k", label="bearing uninformative"),
         Line2D([], [], marker="o", ls="", color=VC["disfavoured"], markeredgecolor="k", label="bearing disfavoured (BF ≤ 0.1)"),
         Line2D([], [], marker="X", ls="", color="w", markeredgecolor="k", label="X: implied impact time outside the 99 % band"),
         Line2D([], [], color="#d62728", ls="--", label="text time 00:52:03"), Line2D([], [], color="#ff7f0e", ls="--", label="caption time 00:54:30")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=6.3)
    foot(fig, "(i) What the chart shows: each dot is one of the 19 signals in Kadri's Table 1 (time and direction at Cape Leeuwin). The blue band is the direction in which the aircraft is predicted to lie. "
              "The yellow band is the time span in which its sound would arrive. A dot is credible only if it is inside both. The dots inside the blue band arrive too early for an impact after 00:19:29 (X); the dots in the time span point further north. "
              "The 306° row is uninformative on this impact set, not disfavoured as on the earlier stand-in.",
         "(ii) Source posterior run J (waypoints seeds 1-8 every 6th row + northern supplement at share 0.125), D0' p = 0.5; back-azimuth mass in 0.5° bins; Bayes factor = sum_k m_k f(bearing - baz_k) / (1/360), "
              "f = Student-t(3) with sd 3.3° (demonstrated error model; claimed Gaussian 0.4° in the table). Implied impact time = arrival - range/1.482 km/s with the range to the bearing line's arc crossing (block-2 arc fit). "
              "Table 1 EXTRACTED from Kadri (2024) Sci. Rep. 14:10102; bearings not reproducible from the published single channel. Caveats C1, C2; pre-registration a4cdab0; PREDICTIVE, NOT CALIBRATED.")
    for ext in ("png", "pdf"): fig.savefig(rd / f"hydroacoustics-searches-run-j-table1.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    sd, rd = Path(sys.argv[1]), Path(sys.argv[2]); rd.mkdir(parents=True, exist_ok=True)
    timeline(sd, rd); table1(sd, rd); print("charts done")
EOF
python charts.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches "$PWD/../../../../../../../repo/Claude Science Project Sep 29/results" 2>&1 | tail -3
ls -la "../../../../../../../repo/Claude Science Project Sep 29/results/" | grep searches-run-j