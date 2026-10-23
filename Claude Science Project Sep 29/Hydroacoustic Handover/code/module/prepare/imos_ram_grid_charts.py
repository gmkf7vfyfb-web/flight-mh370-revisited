"""One comparison figure for the G-TL1 closure (imos_ram_grid.py): old (constant per-logger RAM correction) against new
(RAM along the grid) transmission loss by latitude per IMOS logger, and old against new detectable shares.
Chart rule of 10 Oct: no project jargon in titles, axes or legends; two footnotes, (i) plain, (ii) technical.
Usage: python imos_ram_grid_charts.py <tables_dir_old> <tables_dir_new> <detectable_old.csv> <detectable_new.csv> <out_png> [--commit X]
"""
from __future__ import annotations

import argparse
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

NAMES = {"3315": "Perth Canyon logger 3315", "3376": "Perth Canyon logger 3376", "3274": "Portland logger 3274", "3275": "Portland logger 3275", "3250": "Scott Reef logger 3250"}
BANDS = [10.0, 20.0, 40.0]
CLIP_DB = 230.0   # values above (blocked paths, 250-630 dB) are drawn at the top edge
COL = {10.0: "#1b6ca8", 20.0: "#c46a10", 40.0: "#3a7d44"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("old_dir"); ap.add_argument("new_dir"); ap.add_argument("det_old"); ap.add_argument("det_new"); ap.add_argument("out"); ap.add_argument("--commit", default="")
    a = ap.parse_args()
    old = pd.read_csv(pathlib.Path(a.old_dir) / "imos_tl_ramcorr_arc.csv", dtype={"logger": str}); new = pd.read_csv(pathlib.Path(a.new_dir) / "imos_tl_ram_arc.csv", dtype={"logger": str})
    do = pd.read_csv(a.det_old, dtype={"receiver": str}); dn = pd.read_csv(a.det_new, dtype={"receiver": str})
    do = do[(do.key == "D0/p0.5")]; dn = dn[(dn.key == "D0/p0.5")]
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5})
    fig, axes = plt.subplots(2, 5, figsize=(13.5, 7.6), gridspec_kw=dict(height_ratios=[1.25, 1.0], hspace=0.55, wspace=0.28))
    for j, lg in enumerate(NAMES):
        ax = axes[0, j]
        for fc in BANDS:
            for tab, ls, lab in ((old, "--", "constant correction (old)"), (new, "-", "RAM along the grid (new)")):
                g = tab[(tab.logger == lg) & (tab.fc_hz == fc) & np.isclose(tab.src_depth_m, 10.0) & (tab.offset_nm == 0)].sort_values("lat")
                ax.plot(-g.lat, np.minimum(g.tl_db, CLIP_DB), ls, color=COL[fc], lw=1.3 if ls == "-" else 1.0, alpha=1.0 if ls == "-" else 0.75,
                        label=f"{fc:g} Hz, {lab}" if j == 0 else None)
        g = new[(new.logger == lg) & (new.fc_hz == 20.0) & np.isclose(new.src_depth_m, 10.0) & (new.offset_nm == 0)]
        nc = g[~g.ram_grid_covered & g.status.isin(["ok", "ram_fill"])]
        if len(nc): ax.scatter(-nc.lat, np.minimum(nc.tl_db, CLIP_DB), marker="x", s=12, color="0.3", zorder=5, label="row not covered by the new run (old value kept)" if j == 0 else None)
        ax.set_title(NAMES[lg], loc="left"); ax.set_xlim(41.5, 19.5); ax.set_ylim(105, CLIP_DB + 8); ax.grid(alpha=0.25)
        ax.axhline(CLIP_DB, color="0.6", lw=0.6, ls=":"); 
        if j == 0: ax.set_ylabel("Transmission loss, 10 m source (dB)"); ax.text(41, CLIP_DB - 2.5, "at the dotted line: path blocked (up to 630 dB)", fontsize=5.8, color="0.4", va="top")
        if j == 2: ax.set_xlabel("Latitude of the impact on the 7th arc (°S)")
    h, l = axes[0, 0].get_legend_handles_labels(); fig.legend(h, l, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.965))
    # detectable shares
    for j, lg in enumerate(NAMES):
        ax = axes[1, j]; xs = np.arange(4); w = 0.36
        vals_o, vals_n, labs = [], [], []
        for eta in (0.00021, 0.001):
            for thr in ("matched_filter", "baseline"):
                ro = do[(do.receiver == lg) & np.isclose(do.eta, eta)]; rn = dn[(dn.receiver == lg) & np.isclose(dn.eta, eta)]
                vals_o.append(float(ro[f"frac_{thr}"].iloc[0]) if len(ro) and f"frac_{thr}" in ro else np.nan)
                vals_n.append(float(rn[f"frac_{thr}"].iloc[0]) if len(rn) and f"frac_{thr}" in rn else np.nan)
                labs.append(f"{'MF' if thr == 'matched_filter' else 'energy'}\nη={eta:g}")
        ax.bar(xs - w / 2, np.nan_to_num(vals_o) * 100, w, color="0.75", label="constant correction (old)" if j == 0 else None)
        ax.bar(xs + w / 2, np.nan_to_num(vals_n) * 100, w, color="#7b3294", label="RAM along the grid (new)" if j == 0 else None)
        for x, vo, vn in zip(xs, vals_o, vals_n):
            ax.text(x - w / 2, vo * 100 + 0.8, f"{vo * 100:.1f}", ha="center", va="bottom", fontsize=6, color="0.35")
            ax.text(x + w / 2, vn * 100 + 0.8, f"{vn * 100:.1f}", ha="center", va="bottom", fontsize=6, color="#7b3294")
        ax.set_xticks(xs); ax.set_xticklabels(labs); ax.set_ylim(0, max(5, np.nanmax(np.r_[vals_o, vals_n]) * 100 * 1.25)); ax.grid(axis="y", alpha=0.25)
        if j == 0: ax.set_ylabel("Share of simulated impacts detectable (%)")
        ax.set_title(NAMES[lg], loc="left")
    h, l = axes[1, 0].get_legend_handles_labels(); axes[1, 0].legend(h, l, frameon=False, loc="upper left", fontsize=6.5)
    fig.suptitle("Transmission loss to the five Australian seabed recorders, recomputed path by path with a coupled-mode model, and the resulting share of detectable impacts", x=0.01, ha="left", y=0.998, fontsize=9.5)
    fn1 = ("Plain-language note: Top row: how much the sound weakens on its way from an impact at each latitude on the 7th arc to each seabed recorder, in three frequency bands. The dashed lines are the old "
           "tables, which applied one fixed correction per recorder; the solid lines are the new tables, computed path by path with a model that handles sloping seabeds. Bottom row: the share of simulated "
           "impacts that would be detectable at each recorder (MF = matched-filter detector, 7 dB; energy = conventional energy detector, 15 dB) for two assumed values of the share of impact energy that "
           "becomes sound, before (grey) and after (purple) the new tables. Model predictions, not detections; the sound-loss model is not calibrated against a real event at these recorders.")
    fn2 = ("Technical note: source posterior = run J (D0′ 00:19 held out, p = 0.5, 2 M weighted draws, prereg c360db5); old = imos_tl_ramcorr_arc.csv (rule 2 constant Δ from imp500 paths); new = imos_tl_ram_arc.csv "
           "= raw adiabatic KRAKEN − Δ_noabs(lat, offset, f), Δ from pyram split-step Padé (dr 2λ, dz λ/20, 9 freqs per third octave, hard bottom cp 1650 / ρ 1.9 / 0.5 dB/λ, no absorption in either model) at 1.0° × "
           "offset 0 nodes, 5/8/10/20/40 Hz (addendum of 22 Oct: 5 and 8 Hz added; 31.5 Hz interpolated in log f), 10 m source, receiver on its own bathymetry at seabed − 2 m; rows marked × keep the old value. η ∈ {2.1e-4 (F-35A anchor), 1e-3}; "
           f"thresholds from the weak-signal track. PREDICTIVE, NOT CALIBRATED; caveats C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not calibrated). Module commit {a.commit}.")
    import textwrap
    fig.text(0.01, 0.118, textwrap.fill(fn1, 235), fontsize=6.2, va="top"); fig.text(0.01, 0.058, textwrap.fill(fn2, 235), fontsize=6.2, va="top")
    fig.subplots_adjust(left=0.05, right=0.99, top=0.89, bottom=0.2)
    out = pathlib.Path(a.out); fig.savefig(out, dpi=200); fig.savefig(out.with_suffix(".pdf")); print("wrote", out)


if __name__ == "__main__":
    main()
