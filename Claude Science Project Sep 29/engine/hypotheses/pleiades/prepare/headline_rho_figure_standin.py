"""STAND-IN (11 Oct 2026): close-ups of the run C headline under the rulings of 11 Oct 02:15 -0600, in the module's colour house style
(closeup_styles.colour_single: search fills, faint points for the impact PDF without H, density under H with 50 / 90 % regions).
Drawn: ρ = 0.25, GLORYS12 + ERA5 only. Beside it (90 % outlines and table columns): ρ = 0 and 0.5 (GLORYS12 only) and ρ = 0.25 with
both ocean models (GlobCurrent windage double-counted, drift audit F1). Two-part footnote (STE100 + technical) in the bottom 25 %.

    python headline_rho_figure_standin.py <branch root> <surface dir> <family-evidence json> <geom dir> <stats csv> <splithalf csv> <out dir>
"""
import json
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import closeup_figure as cf  # noqa: E402
import closeup_styles as cs  # noqa: E402
from branch_figure import hdr_level  # noqa: E402
from option_closeups import load_mixture  # noqa: E402
from headline_rho_standin import OPTS, VARIANTS, rho_L, with_L  # noqa: E402

COLS = {"rho0.25 GLORYS12": ("ρ = 0.25\nGLORYS12\n(drawn)", "#08306b", "-"),
        "rho0 GLORYS12": ("ρ = 0\nGLORYS12", "#2ca25f", (0, (4, 2))),
        "rho0.5 GLORYS12": ("ρ = 0.5\nGLORYS12", "#984ea3", (0, (1, 1.2))),
        "rho0.25 both models": ("ρ = 0.25\ntwo ocean\nmodels*", "#e6550d", (0, (6, 2, 1, 2)))}

STE = ("STE100: This map shows where the aircraft possibly went into the sea, if the objects in the Pléiades satellite images are "
       "from 9M-MRO. The blue colour shows the probability with this assumption. The grey points show the probability without this "
       "assumption. The drawn result uses one ocean model (GLORYS12) and a correlation of 0.25 between the drift errors of the two "
       "satellite data sets. The thin lines show the 90 % region for other settings. *The two-model result counts the wind drift of "
       "the GlobCurrent model two times, thus it is shown only for comparison. The flight calculation (core run C) is not converged. "
       "Use these results with caution.")


def tech(opt, key, pf, sh_ok):
    return ("Technical: core run C (4 strata x 8 seeds) split-half NOT CONVERGED (floor 0.924: free 0.918, Davey dynamics + radar 0.910, "
            "descent-climb 0.892, routes 0.850); end-of-flight physics PROVISIONAL (descents > 6,500 ft/min and unloading not reachable; "
            f"no structural limit, G13). {cs.describe_option(opt, short=True)}, existence constraint 'unpowered'; strata re-weighted by the "
            f"00:19 evidence (family-evidence-run-c.json, key '{key}': " + ", ".join(f"{k} {v:.3f}" for k, v in pf.items()) + "). "
            "After Phase 2 + Bluefin-21 (official) + OI 2018 + OI 2025-26 SE band (grade C; NW band drawn only). Under H: 12 rating-5 "
            "Pléiades objects (6 clusters, 3 km, equal weight) x all four COSMO-SkyMed contacts, one debris field; bivariate-normal "
            "transport errors per component (prepare/rho_surface.py), ρ = 0.25 headline (ocean transport measured 0.07-0.41, GLORYS12), "
            "ρ = 0 / 0.5 beside; GLORYS12 + ERA5 only (architecture ruling 2, 11 Oct 02:15 -0600); *both models equal weight, GlobCurrent "
            "windage double-counted (drift audit F1). " + ("± = split-half σ (rms over three 4 + 4 seed partitions), from the module's splithalf.csv; measured for ρ = 0 GLORYS12 only. The "
               "σ for the other three settings was not run (the heavy-compute lock was held by other work). " if sh_ok else "")
            + "Conditional on H; no Bayes factor or P(H | data). Holland H1/H2 not estimable. Background: 6,000 points from the impact "
            "PDF without H after the same searches. Stand-in redraw (module scripts, inputs changed only); module review pending.")


def main(root, surf, fam, geom, stats_csv, sh_csv, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, Polygon
    from matplotlib.colors import LinearSegmentedColormap
    matplotlib.rcParams.update({"font.size": 6, "axes.titlesize": 6.5, "axes.labelsize": 6, "xtick.labelsize": 5.5, "ytick.labelsize": 5.5})
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    geo = json.loads((Path(geom) / "search_footprints.geojson").read_text())
    M = HERE.parent
    T5 = pd.read_csv(M / "data/targets-3km.csv").query("arm == 'rating5'"); Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    S = pd.read_csv(stats_csv)
    SH = pd.read_csv(sh_csv) if sh_csv and Path(sh_csv).exists() else None
    if SH is not None and "variant" not in SH.columns:   # the module's own splithalf.csv (rho = 0): only its GLORYS12-only rows match a variant
        SH = SH[SH.ocean_models == "GLORYS12 only"].assign(variant="rho0 GLORYS12")
    Ls = {k: rho_L(surf, r, mo) for k, r, mo in VARIANTS}
    cmap = LinearSegmentedColormap.from_list("dens", [(1, 1, 1, 0), (0.776, 0.859, 0.937, 0.75), "#6baed6", "#2171b5", "#08306b"])
    v = "oi2018-2025"
    for opt in OPTS:
        pf = cs.reweighted_pfam(fam, opt); key = cs.eof_family_key(opt, json.loads(Path(fam).read_text())["mixtures"])
        maps = {vv: load_mixture(root, opt, vv, pf) for vv in ("base", v)}
        lat, lon, area = maps[v]["lat"], maps[v]["lon"], maps[v]["area"]
        fig = plt.figure(figsize=(7.1, 5.5))
        ax = fig.add_axes([0.07, 0.265, 0.52, 0.65])
        side = fig.add_axes([0.62, 0.265, 0.37, 0.65]); side.axis("off")
        for fid, col, al, _ in cs.SEARCH_FILL:
            for p in cf.polygons(geo, fid):
                ax.add_patch(Polygon(p[:, :2], closed=True, fc=col, ec=col, alpha=al, lw=0.8, zorder=1))
        hb = cs.flight_background(ax, maps, v, "points", "#222222", zorder=2)
        head = with_L(maps, Ls["rho0.25 GLORYS12"])
        m = cs.panel_mass(head, v, "P+C4"); dn = m / area
        ax.pcolormesh(lon, lat, dn / dn.max(), cmap=cmap, vmin=0, vmax=1, shading="auto", rasterized=True, zorder=3)
        nw = cf.polygons(geo, "oi2024_proposed_inboard_northwest")[0]
        ax.plot(nw[:, 0], nw[:, 1], color="#1e8449", lw=1.4, ls=(0, (3, 2)), zorder=4)
        arc = cf.polygons(geo, "seventh_arc_fl400")[0]
        ax.plot(arc[:, 0], arc[:, 1], color="#333333", lw=0.7, ls=":", zorder=4)
        ax.contour(lon, lat, dn, levels=[hdr_level(dn, m, q) for q in (0.9, 0.5)], colors=["#08306b"] * 2, linewidths=[0.7, 1.4], zorder=6)
        hv = []
        for k in ("rho0 GLORYS12", "rho0.5 GLORYS12", "rho0.25 both models"):
            mm = cs.panel_mass(with_L(maps, Ls[k]), v, "P+C4"); dd = mm / area
            ax.contour(lon, lat, dd, levels=[hdr_level(dd, mm, 0.9)], colors=[COLS[k][1]], linewidths=[0.75], linestyles=[COLS[k][2]], zorder=5)
            hv.append(plt.Line2D([], [], color=COLS[k][1], lw=0.9, ls=COLS[k][2], label="90 % region, " + COLS[k][0].replace("\n", " ").replace("ρ =", "drift-error correlation").replace(" GLORYS12", ", GLORYS12").replace(" two ocean", ", two ocean")))
        ax.plot(T5.lon, T5.lat, "x", ms=3.5, color="#d62728", mew=0.9, zorder=7)
        ax.plot(Cc.longitude, Cc.latitude, "o", ms=3.5, mfc="white", mec="#e6550d", mew=0.9, zorder=7)
        ax.set_xlim(88, 96); ax.set_ylim(-38, -32); ax.set_aspect(1 / np.cos(np.radians(35)))
        ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)")
        ax.set_title("after all past seabed searches", loc="left", fontsize=6.3)
        # table: 4 variants
        rows_lab = ["50 % region, km²", "90 % region, km²", "mean position", "outside past searches", "share left by searches",
                    "tension ln S (p)", "mean shift from\nPDF without H", "PDF without H\ninside 90 % region"]
        cols = []
        for k in COLS:
            r = S[(S.option == opt) & (S.variant == k)].iloc[0]
            sd = ""
            if SH is not None:
                q = SH[(SH.option == opt) & (SH.variant == k)]
                sd = f"\n± {q.iloc[0].hdr90_km2_splithalf_sd:,.0f}" if len(q) else "\nσ not run"
            cols.append([f"{r.hdr50_km2:,.0f}", f"{r.hdr90_km2:,.0f}{sd}", f"{abs(r.mean_lat):.2f} S\n{r.mean_lon:.2f} E",
                         f"{100 * r.share_outside_past_searches:.1f} %", f"{r.search_retains_under_H:.3f}",
                         f"{r.ln_S:+.2f} ({r.tension_p:.2f})", f"{r.mean_shift_nm:.0f} NM", f"{100 * r.uncond_in_cond_hdr90:.0f} %"])
        cell = [[lab] + [c[i] for c in cols] for i, lab in enumerate(rows_lab)]
        t = side.table(cellText=cell, colLabels=[""] + [COLS[k][0] for k in COLS], loc="upper left", cellLoc="left", edges="horizontal",
                       colWidths=[0.32, 0.17, 0.17, 0.17, 0.17], bbox=[0.0, 0.44, 1.0, 0.56])
        t.auto_set_font_size(False); t.set_fontsize(4.6)
        for (r_, c_), ce in t.get_celld().items():
            ce.PAD = 0.03
            if r_ == 0 and c_ == 1:
                ce.get_text().set_fontweight("bold")
        h = [Patch(fc="#2171b5", label="probability density if the objects are debris (relative)"),
             plt.Line2D([], [], color="#08306b", lw=1.4, label="50 % region (drawn setting)"),
             plt.Line2D([], [], color="#08306b", lw=0.7, label="90 % region (drawn setting)")] + hv + hb
        h += [Patch(fc=c, alpha=a, ec=c, label=l) for _, c, a, l in cs.SEARCH_FILL if l]
        h += [plt.Line2D([], [], color="#1e8449", lw=1.4, ls=(0, (3, 2)), label="OI north-west band (not searched; grade C)"),
              plt.Line2D([], [], color="#333333", lw=0.7, ls=":", label="7th arc, FL400"),
              plt.Line2D([], [], ls="", marker="x", color="#d62728", label="Pléiades rating-5 objects"),
              plt.Line2D([], [], ls="", marker="o", mfc="white", mec="#e6550d", label="COSMO-SkyMed radar contacts (all four)")]
        side.legend(handles=h, loc="upper left", bbox_to_anchor=(0.0, 0.42), frameon=False, fontsize=4.9, ncol=1)
        fig.suptitle(f"If the imaged objects are from 9M-MRO: where the debris entered the sea — {cs.describe_option(opt, short=True)}\n"
                     "drift-error correlation 0.25, one ocean model (GLORYS12) — core run C NOT CONVERGED",
                     x=0.01, ha="left", y=0.995, fontsize=7)
        txt = textwrap.fill(STE, 205) + "\n" + textwrap.fill(tech(opt, key, pf, SH is not None), 205)
        fig.text(0.01, 0.212, txt, ha="left", va="top", fontsize=4.55, color="#333333")
        fig.add_artist(plt.Line2D([0.01, 0.99], [0.218, 0.218], color="#999999", lw=0.4))
        safe = opt.replace("/", "-")
        fig.savefig(out / f"closeup-{safe}-rho025-glorys12.png", dpi=300)
        fig.savefig(out / f"closeup-{safe}-rho025-glorys12.pdf")
        plt.close(fig)
        print(opt, flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:8])
