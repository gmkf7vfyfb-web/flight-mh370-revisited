"""Composer pass 1 (run C) figures, from report_c.py outputs. Footnotes per Pete's rule: two versions (STE100, technical) together in
at most the bottom 25 % of the image; titles, axes and legends without project codes.
Usage: python figures_c.py <work dir> <out dir>
"""
import json, math, pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "repo/Claude Science Project Sep 29/results/composer-pass0"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import summarise_stratum as S
import report as R0
import report_c as RC

plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 6.5, "xtick.labelsize": 6.5,
                     "ytick.labelsize": 6.5, "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans"})
COL = {"P1": "#8c8c8c", "D": "#6aa0d8", "G": "#1f5fa8", "Ga": "#1f5fa8", "H": "#c2571a", "Ha": "#c2571a", "Hn": "#e39a6a", "Hr5": "#7a3b8f"}
NAMES = {"P1": "Flight and end of flight only", "D": "Add debris drift (no underwater sound)", "G": "Add debris drift and underwater sound",
         "Ga": "... then the seabed searches", "H": "Also add the Pléiades objects (if aircraft debris)", "Ha": "... then the seabed searches"}
OPT_TITLE = {"r600-bto": "00:19 R600 BTO Only (primary)", "heldout": "00:19 Held Out", "r600-bfo": "00:19 R600 BTO + Raw BFO"}


def common_tech(R):
    sp = R["strata_present"]["r600-bto+unpowered"]
    return ("Source: core run C (prior track 289.7 deg, 00:11 hand-off), strata " + ", ".join(RC.SNAME[s] for s in sp) + " x 8 seeds, ~3.2 M impact rows per seed; "
            "core split-half mean 0.850-0.918 against floor 0.924: NOT CONVERGED. End of flight run C (binary 15ba1098; dive class (b); descents <= 6,500 ft/min; "
            "no structural limit, G13; residual roll P(left) 0.8 PROVISIONAL); log-on cause 'other', constraint +unpowered. Drift: GLORYS12V1 + ERA5 only, current 367 nodes, "
            "50 km bandwidth, 9 finds; GlobCurrent excluded (F1); not-computed rows carried. Hydroacoustics: stand-in L_hyd scenario A with audit F8 (Blackman App. B noise), "
            "PREDICTIVE, NOT CALIBRATED (C6). Pléiades v2: rating 5, equal clusters, GLORYS12, given H. Searches: Phase 2 + Bluefin-21, rho 0.05. "
            "Strata mixed by core P(family) re-weighted by the 00:19 evidence. Holland H1/H2 not estimable, not shown.")


def footer(fig, ste, tech, frac=0.24):
    fig.add_artist(matplotlib.lines.Line2D([0.01, 0.99], [frac, frac], color="#999999", lw=0.5))
    fig.text(0.01, frac - 0.008, "NOT CONVERGED (core run C). " + ste, fontsize=6.0, va="top", ha="left", wrap=True)
    fig.text(0.01, frac * 0.68, "Technical: " + tech, fontsize=5.3, va="top", ha="left", wrap=True, color="#333333")


def fig_latitude(D, R, out, T):
    fig, axes = plt.subplots(2, 3, figsize=(8.6, 6.4), sharey="row", sharex=True)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.86, bottom=0.31, wspace=0.06, hspace=0.34)
    for j, base in enumerate(("r600-bto", "heldout", "r600-bfo")):
        for i, ver in enumerate(("", "-v212")):
            ax = axes[i, j]; t = f"{base}+unpowered{ver}"
            if t not in R["options"]:
                ax.text(0.5, 0.5, "not available", transform=ax.transAxes, ha="center"); continue
            for key, ls in (("P1", "-"), ("D", ":"), ("G", "-"), ("Ga", "--"), ("H", "-"), ("Ha", "--")):
                h, _ = RC.mixture(D, t, key, "reweighted-0019"); d = R0.smooth_to_density(h)
                ax.plot(R0.GRID, d, ls, color=COL[key], lw=1.5 if key in ("G", "H") else 1.0, label=NAMES[key])
            ax.set_xlim(-44, -22); ax.set_xticks(range(-44, -21, 4))
            ax.set_title(OPT_TITLE[base] + ("\nall impacts" if not ver else "\nimpacts at 212 m/s or slower only"), loc="left", fontsize=7.2)
        axes[1, j].set_xlabel("Impact latitude (degrees; south is negative)")
    for i in range(2):
        axes[i, 0].set_ylabel("Probability density (per degree)")
    hl = axes[0, 0].get_legend_handles_labels()
    fig.legend(*hl, frameon=False, loc="upper left", bbox_to_anchor=(0.06, 0.965), ncol=3, fontsize=6.3)
    fig.suptitle("Where the aircraft hit the water, as each set of evidence is added", x=0.01, y=0.995, ha="left", fontsize=9)
    footer(fig, "Each curve adds more evidence. The orange curves are correct only if the Pléiades objects are aircraft debris. The lower row "
                "removes impacts faster than 212 m/s, because the model has no limit on structural speed. The sample did not settle, so the curves can change in a new run. Do not use them as a result.",
           common_tech(R) + " Curves: summary.rs latitude grid (0.05 deg, 0.1 deg Gaussian), summary.rs pooling(). Lower row: rows with contact speed > 212 m/s (1.25 VMO) "
           "given zero likelihood (ruling 8dbefed2), normaliser unchanged.", 0.25)
    fig.savefig(out / "fig1-impact-latitude.png", dpi=200); fig.savefig(out / "fig1-impact-latitude.pdf"); plt.close(fig)


def fig_maps(D, R, out, cells):
    t = "r600-bto+unpowered"; O = R["options"][t]
    fig, axes = plt.subplots(2, 2, figsize=(6.6, 8.2), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.10, right=0.99, top=0.885, bottom=0.26, wspace=0.04, hspace=0.17)
    for ax, key in zip(axes.flat, ("G", "Ga", "H", "Ha")):
        p = cells[f"{t}|{key}"]
        m50, m90 = R0.hdr_mask(p, 0.5).reshape(S.NY, S.NX), R0.hdr_mask(p, 0.9).reshape(S.NY, S.NX)
        lvl = np.where(m50, 2, np.where(m90, 1, 0)).astype(float); lvl[lvl == 0] = np.nan
        ax.pcolormesh(R0.LON_EDGES, R0.LAT_EDGES, lvl, cmap=matplotlib.colors.ListedColormap(["#c9d7ea" if key[0] == "G" else "#f1d1bd", COL[key]]), vmin=0.5, vmax=2.5, shading="flat")
        if key[0] == "H":
            g90 = R0.hdr_mask(cells[f"{t}|{'G' if key == 'H' else 'Ga'}"], 0.9).reshape(S.NY, S.NX).astype(float)
            ax.contour(np.repeat(R0.LON_C[None, :], S.NY, 0), np.repeat(R0.LAT_C[:, None], S.NX, 1), g90, levels=[0.5], colors=["#1f5fa8"], linewidths=0.6)
        e = O["products"][key]["reweighted-0019"]
        ax.plot(e["smoothed_map_mode_lat_lon"][1], e["smoothed_map_mode_lat_lon"][0], "k+", ms=7)
        ax.set_title({"G": "Drift and sound added", "Ga": "... after the seabed searches", "H": "Pléiades objects also added", "Ha": "... after the seabed searches"}[key]
                     + f"\n90 % region {e['hdr90_area_km2'] / 1e3:,.0f}k km²; 50 % region {e['hdr50_area_km2'] / 1e3:,.0f}k km²", loc="left", fontsize=7.2)
        ax.set_xlim(82, 108); ax.set_ylim(-44, -20); ax.set_aspect(1 / math.cos(math.radians(33)))
    for ax in axes[1]:
        ax.set_xlabel("Longitude (degrees east)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Latitude (degrees)")
    fig.suptitle("Most probable impact regions, primary case (00:19 R600 BTO Only)", x=0.01, y=0.985, ha="left", fontsize=9)
    fig.text(0.01, 0.952, "Dark: 50 % region.  Light: 90 % region.  +: highest density.  Blue outline on the lower maps: the 90 % region above.", fontsize=6.6)
    footer(fig, "The dark area holds half the probability, and the dark and light areas together hold 90 %. The lower maps are correct only if the "
                "Pléiades objects are aircraft debris. The sample did not settle. Do not use these maps for a search.",
           common_tech(R) + " Regions: highest-density cells of the patch-B equal-area grid (0.25 deg lon x equal authalic-latitude steps, 769.3 km² cells), unsmoothed; "
           "peak from the map smoothed by 1 cell. All impacts (no speed filter).", 0.20)
    fig.savefig(out / "fig2-impact-regions.png", dpi=200); fig.savefig(out / "fig2-impact-regions.pdf"); plt.close(fig)


def fig_tension(D, R, out):
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.4))
    fig.subplots_adjust(left=0.17, right=0.99, top=0.79, bottom=0.36, wspace=0.62)
    ax = axes[0]; cols = {"r600-bto": "#1f5fa8", "heldout": "#8c8c8c", "r600-bfo": "#2a9d55"}
    labels = []
    for j, base in enumerate(("r600-bto", "heldout", "r600-bfo")):
        t = f"{base}+unpowered"
        if t not in R["options"]:
            continue
        T = R["options"][t]["tension"]["before searches"]; ss = R["strata_present"][t]
        for i, st in enumerate(ss):
            v = T["per_stratum"][RC.SNAME[st]]; y = i + 0.22 * (j - 1)
            ax.plot(list(v["ln_R_per_seed"].values()), [y] * len(v["ln_R_per_seed"]), "o", ms=2.2, color=cols[base], alpha=0.5)
            ax.plot(v["ln_R"], y, "D", ms=4.5, color=cols[base], label=OPT_TITLE[base] if i == 0 else None)
        y = len(ss) + 0.22 * (j - 1)
        ax.plot(T["ln_R"], y, "D", ms=6, color=cols[base], mec="k")
        for pair, mk in (("without hydro", "x"), ("rho 0.5 (P + COSMO, correlated)", "^")):
            if pair in R["options"][t]["tension"]:
                ax.plot(R["options"][t]["tension"][pair]["ln_R"], y, mk, ms=5, color=cols[base])
        labels = [RC.SNAME[s] for s in ss] + ["mixture"]
    ax.plot([], [], "kx", ms=5, label="mixture, without underwater sound"); ax.plot([], [], "k^", ms=5, label="mixture, Pléiades with satellite contacts, correlated errors")
    ax.axvline(0, color="k", lw=0.6)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels); ax.invert_yaxis()
    ax.set_xlabel("ln R (above zero: drift and sound favour the Pléiades area)")
    ax.set_title("Agreement of drift and sound with the Pléiades area", loc="left")
    fig.legend(*ax.get_legend_handles_labels(), frameon=False, loc="upper left", bbox_to_anchor=(0.01, 0.955), ncol=2, fontsize=5.8)
    ax = axes[1]; t = "r600-bto+unpowered"
    keys = ["P1", "D", "Y", "S", "G", "Ga", "PE", "H", "Ha"]
    lab = ["flight + end of flight", "+ drift alone", "+ sound alone", "+ searches alone", "+ drift + sound", "  then searches", "+ Pléiades alone", "+ drift, sound, Pléiades", "  then searches"]
    for i, k in enumerate(keys):
        for st, mk in zip(RC.STRATA, "os^v"):
            if st in D and t in D[st]:
                e = min(x[1] for x in D[st][t]["products"][k]["ess_rows_parents"])
                ax.plot(e, i, mk, ms=3.5, color="#1f5fa8", alpha=0.85, label=RC.SNAME[st] if i == 0 else None)
    ax.axvline(1000, color="#b00020", lw=0.8, ls=":"); ax.text(1100, 8.45, "floor 1,000", fontsize=6, color="#b00020", va="center")
    ax.set_xscale("log"); ax.set_yticks(range(len(keys))); ax.set_yticklabels(lab); ax.invert_yaxis(); ax.set_xlim(300, 2e5)
    ax.set_xlabel("Effective parents, smallest seed (log scale)"); ax.set_title("Effective sample size, primary case", loc="left")
    ax.legend(frameon=False, fontsize=5.8, loc="lower left", bbox_to_anchor=(0.0, 0.02), title="stratum", title_fontsize=5.8)
    fig.suptitle("Pléiades agreement test and sample adequacy", x=0.01, y=0.995, ha="left", fontsize=9)
    footer(fig, "Left: a value above zero shows that the drift and sound evidence moves the probability towards the Pléiades area. Small dots are the "
                "eight seeds. Right: the number of independent samples that each step keeps. The sample did not settle.",
           common_tech(R) + " ln R = ln E[L_P | flight+EoF+drift+hydro] - ln E[L_P | flight+EoF] (Pléiades A_scene cancels); mixture over 00:19-re-weighted strata. "
           "Triangle: P + four COSMO contacts with correlated transport errors, rho 0.5 (joint-surface-rho0.5). ESS: composer Ess.parents.", 0.25)
    fig.savefig(out / "fig3-tension-and-ess.png", dpi=200); fig.savefig(out / "fig3-tension-and-ess.pdf"); plt.close(fig)


def fig_families(D, R, out):
    fig, ax = plt.subplots(figsize=(7.6, 4.6)); fig.subplots_adjust(left=0.34, right=0.97, top=0.86, bottom=0.33)
    fams = ["A1", "A2", "B", "B, approach to ditching (code 3)", "B, control lost en route (code 5)"]
    names = {"A1": "A1: fuel exhaustion, no controlled phase", "A2": "A2: fuel exhaustion, controlled phase", "B": "B: planned descent before exhaustion",
             "B, approach to ditching (code 3)": "   B with an approach to ditching", "B, control lost en route (code 5)": "   B with control lost on the way down"}
    for t, mk, off in (("r600-bto+unpowered", "o", 0.0), ("r600-bto+unpowered-v212", "s", 0.11)):
        if t not in R["options"]:
            continue
        for j, key in enumerate(("P1", "G", "H")):
            e = R["options"][t]["products"][key]["reweighted-0019"]
            for i, f in enumerate(fams):
                s = e["family_stats"].get(f)
                if not s:
                    continue
                y = i + (j - 1) * 0.26 + off
                ax.plot([s["q025"], s["q975"]], [y, y], color=COL[key], lw=1.0, alpha=1.0 if off == 0 else 0.5)
                ax.plot(s["median"], y, mk, color=COL[key], ms=3.6, mfc=COL[key] if off == 0 else "white", label=(NAMES[key] if off == 0 else NAMES[key] + ", 212 m/s or slower") if i == 0 else None)
                pr = e["family_probability"].get(f, e["B_split"].get(f))
                if off == 0:
                    ax.text(-20.8, y, f"P = {pr:.2f}", fontsize=5.6, va="center", color=COL[key])
    ax.set_yticks(range(len(fams))); ax.set_yticklabels([names[f] for f in fams]); ax.invert_yaxis(); ax.set_xlim(-45, -19)
    ax.set_xlabel("Impact latitude, median and 95 % interval (degrees)")
    fig.legend(*ax.get_legend_handles_labels(), frameon=False, fontsize=5.6, loc="upper left", ncol=3, bbox_to_anchor=(0.01, 0.995))
    ax.set_title("Impact latitude for each type of end of flight, primary case (00:19 R600 BTO Only)", loc="left")
    footer(fig, "Each line shows the impact latitude for one type of end of flight. P is the probability of that type. The data after 00:11 do not "
                "much change these probabilities, so they come mostly from the prior. Type B is only partly modelled. Open markers: impacts faster than 212 m/s removed.",
           common_tech(R) + " Families: EoF family4_code (ruling 6 as amended: code 4 split by recovery_attempted); B split by family_code 3 / 5; code 6 (outside B) "
           "holds < 0.1 % and is not drawn. P from the composed weights per product.", 0.25)
    fig.savefig(out / "fig4-families.png", dpi=200); fig.savefig(out / "fig4-families.pdf"); plt.close(fig)


def main(work, out):
    work, out = pathlib.Path(work), pathlib.Path(out)
    D = RC.load(work); R = json.loads((out / "pass1-results.json").read_text()); cells = dict(np.load(work / "cells.npz"))
    fig_latitude(D, R, out, None); fig_maps(D, R, out, cells); fig_tension(D, R, out); fig_families(D, R, out)
    print("figures ok")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
