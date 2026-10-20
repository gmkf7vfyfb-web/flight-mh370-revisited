"""Pléiades module (11 Oct 2026): statistics and close-ups (colour + seabed) for the PROPOSED run C headline after drift audit F1:
both ocean models (equal weight), GlobCurrent windage product-relative (joint-surface-rho*-gcrel), drift-error correlation ρ = 0.25.
Beside it: GLORYS12 + ERA5 only at ρ = 0.25 (the headline in force under architecture ruling 2 of 11 Oct 02:15 -0600), and both
models product-relative at ρ = 0 and 0.5. Module version of the adopted stand-in (headline_rho_standin.py / headline_rho_figure_standin.py);
the statistics use the same functions (headline_rho_standin.row -> closeup_figure.stats, rerun_reference.tension).

    python headline_figure.py <branch root> <surface dir> <family-evidence json> <geom dir> <gebco json> <splithalf csv> <out dir>
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
import headline_rho_standin as h  # noqa: E402
from branch_figure import hdr_level  # noqa: E402
from headline_splithalf import VARIANTS, rho_L  # noqa: E402
from option_closeups import load_mixture  # noqa: E402

DRAWN = "rho0.25 both models, GlobCurrent product-relative"
COLS = {DRAWN: ("ρ = 0.25\ntwo models\n(drawn)", "#08306b", "-"),
        "rho0.25 GLORYS12": ("ρ = 0.25\nGLORYS12\nonly", "#e6550d", (0, (6, 2, 1, 2))),
        "rho0 both models, GlobCurrent product-relative": ("ρ = 0\ntwo models", "#2ca25f", (0, (4, 2))),
        "rho0.5 both models, GlobCurrent product-relative": ("ρ = 0.5\ntwo models", "#984ea3", (0, (1, 1.2)))}
LEG = {DRAWN: "drift-error correlation 0.25, two ocean models",
       "rho0.25 GLORYS12": "drift-error correlation 0.25, GLORYS12 only",
       "rho0 both models, GlobCurrent product-relative": "drift-error correlation 0, two ocean models",
       "rho0.5 both models, GlobCurrent product-relative": "drift-error correlation 0.5, two ocean models"}

STE = ("STE100: This map shows where the aircraft possibly went into the sea, if the objects in the Pléiades satellite images are from "
       "9M-MRO. {colour} The drawn result uses two ocean models with equal weight and a correlation of 0.25 between the drift errors of "
       "the two satellite data sets. {lines} This is a proposed headline; the architecture session must accept it. The flight calculation "
       "(core run C) is not converged. Use these results with caution.")


def tech(opt, key, pf, sh_note):
    return ("Technical: core run C (4 strata x 8 seeds) split-half NOT CONVERGED (floor 0.924: free 0.918, Davey dynamics + radar 0.910, "
            "descent-climb 0.892, routes 0.850); end-of-flight physics PROVISIONAL (descents > 6,500 ft/min and unloading not reachable; "
            f"no structural limit, G13). {cs.describe_option(opt, short=True)}, existence constraint 'unpowered'; strata re-weighted by the "
            f"00:19 evidence (family-evidence-run-c.json, key '{key}': " + ", ".join(f"{k} {v:.3f}" for k, v in pf.items()) + "). "
            "After Phase 2 + Bluefin-21 (official) + OI 2018 + OI 2025-26 SE band (grade C; NW band drawn only). Under H: 12 rating-5 "
            "Pléiades objects (6 clusters, 3 km, equal weight) x all four COSMO-SkyMed contacts, one debris field; bivariate-normal "
            "transport errors per component (prepare/rho_surface.py), ρ = 0.25 (ocean transport measured 0.07-0.41), ρ = 0 / 0.5 beside. "
            "GLORYS12 + ERA5 and GlobCurrent daily + ERA5, equal weight; GlobCurrent windage product-relative (drift audit F1: weights of "
            "c - dc, dc uniform 0.60-0.75 % U10 by 3-point quadrature, mass below 0 clamped to node 0; surfaces joint-surface-rho*-gcrel). "
            "PROPOSED headline (module, 11 Oct 18:19 UTC); in force until accepted: GLORYS12 only (ruling 2, 11 Oct 02:15 -0600), shown "
            f"beside. {sh_note} Conditional on H; no identity likelihood, no Bayes factor or P(H | data). Holland H1/H2 not estimable.")


def stats(root, surf, fam, geom, out):
    h.VARIANTS = [(k, r, (m, t)) for k, r, m, t in VARIANTS] + [("rho0 GLORYS12", 0.0, (0, ""))]   # needed by the hook check
    h.rho_L = lambda s, r, mt: rho_L(s, r, *mt) if isinstance(mt, tuple) else rho_L(s, r, mt)   # hook rows pass a bare model
    T, C = h.main(root, surf, fam, geom, out)
    for a, b in (("headline-rho025-stats.csv", "headline-gcrel-stats.csv"), ("headline-rho025-checks.csv", "headline-gcrel-checks.csv")):
        (Path(out) / a).replace(Path(out) / b)
    return T


def sigma(SH, opt, k):
    if SH is None:
        return None
    q = SH[(SH.option == opt) & (SH.variant == k)]
    return float(q.iloc[0].hdr90_km2_splithalf_sd) if len(q) else None


def main(root, surf, fam, geom, gebco, sh_csv, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, Polygon
    from matplotlib.colors import LinearSegmentedColormap
    matplotlib.rcParams.update({"font.size": 6, "axes.titlesize": 6.5, "axes.labelsize": 6, "xtick.labelsize": 5.5, "ytick.labelsize": 5.5})
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    S = stats(root, surf, fam, geom, out)
    geo = json.loads((Path(geom) / "search_footprints.geojson").read_text())
    M = HERE.parent
    T5 = pd.read_csv(M / "data/targets-3km.csv").query("arm == 'rating5'"); Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    SH = pd.read_csv(sh_csv) if sh_csv and Path(sh_csv).exists() else None
    sh_note = ("± = split-half σ of the 90 % region (rms over three 4 + 4 seed partitions, headline_splithalf.py)." if SH is not None else
               "Split-half σ for these settings is queued on the heavy-compute lock and is not shown yet.")
    Ls = {k: rho_L(surf, r, m, t) for k, r, m, t in VARIANTS}
    cmap = LinearSegmentedColormap.from_list("dens", [(1, 1, 1, 0), (0.776, 0.859, 0.937, 0.75), "#6baed6", "#2171b5", "#08306b"])
    v = "oi2018-2025"
    for opt in h.OPTS:
        pf = cs.reweighted_pfam(fam, opt); key = cs.eof_family_key(opt, json.loads(Path(fam).read_text())["mixtures"])
        maps = {vv: load_mixture(root, opt, vv, pf) for vv in ("base", v)}
        lat, lon, area = maps[v]["lat"], maps[v]["lon"], maps[v]["area"]
        head = h.with_L(maps, Ls[DRAWN])
        safe = opt.replace("/", "-")
        others = [k for k in COLS if k != DRAWN]
        # ---------------- colour close-up (house style: search fills, faint points without H, density under H)
        fig = plt.figure(figsize=(7.1, 5.5))
        ax = fig.add_axes([0.07, 0.265, 0.52, 0.65])
        side = fig.add_axes([0.62, 0.265, 0.37, 0.65]); side.axis("off")
        for fid, col, al, _ in cs.SEARCH_FILL:
            for p in cf.polygons(geo, fid):
                ax.add_patch(Polygon(p[:, :2], closed=True, fc=col, ec=col, alpha=al, lw=0.8, zorder=1))
        hb = cs.flight_background(ax, maps, v, "points", "#222222", zorder=2)
        m = cs.panel_mass(head, v, "P+C4"); dn = m / area
        ax.pcolormesh(lon, lat, dn / dn.max(), cmap=cmap, vmin=0, vmax=1, shading="auto", rasterized=True, zorder=3)
        nw = cf.polygons(geo, "oi2024_proposed_inboard_northwest")[0]
        ax.plot(nw[:, 0], nw[:, 1], color="#1e8449", lw=1.4, ls=(0, (3, 2)), zorder=4)
        arc = cf.polygons(geo, "seventh_arc_fl400")[0]
        ax.plot(arc[:, 0], arc[:, 1], color="#333333", lw=0.7, ls=":", zorder=4)
        ax.contour(lon, lat, dn, levels=[hdr_level(dn, m, q) for q in (0.9, 0.5)], colors=["#08306b"] * 2, linewidths=[0.7, 1.4], zorder=6)
        hv = []
        for k in others:
            mm = cs.panel_mass(h.with_L(maps, Ls[k]), v, "P+C4"); dd = mm / area
            ax.contour(lon, lat, dd, levels=[hdr_level(dd, mm, 0.9)], colors=[COLS[k][1]], linewidths=[0.75], linestyles=[COLS[k][2]], zorder=5)
            hv.append(plt.Line2D([], [], color=COLS[k][1], lw=0.9, ls=COLS[k][2], label="90 % region, " + LEG[k]))
        ax.plot(T5.lon, T5.lat, "x", ms=3.5, color="#d62728", mew=0.9, zorder=7)
        ax.plot(Cc.longitude, Cc.latitude, "o", ms=3.5, mfc="white", mec="#e6550d", mew=0.9, zorder=7)
        ax.set_xlim(88, 96); ax.set_ylim(-38, -32); ax.set_aspect(1 / np.cos(np.radians(35)))
        ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)")
        ax.set_title("after all past seabed searches", loc="left", fontsize=6.3)
        rows_lab = ["50 % region, km²", "90 % region, km²", "mean position", "outside past searches", "share left by searches",
                    "tension ln S (p)", "mean shift from\nPDF without H", "PDF without H\ninside 90 % region"]
        cols = []
        for k in COLS:
            r = S[(S.option == opt) & (S.variant == k)].iloc[0]
            sd = sigma(SH, opt, k)
            sd = f"\n± {sd:,.0f}" if sd is not None else "\nσ pending"
            cols.append([f"{r.hdr50_km2:,.0f}", f"{r.hdr90_km2:,.0f}{sd}", f"{abs(r.mean_lat):.2f} S\n{r.mean_lon:.2f} E",
                         f"{100 * r.share_outside_past_searches:.1f} %", f"{r.search_retains_under_H:.3f}",
                         f"{r.ln_S:+.2f} ({r.tension_p:.2f})", f"{r.mean_shift_nm:.0f} NM", f"{100 * r.uncond_in_cond_hdr90:.0f} %"])
        cell = [[lab] + [c[i] for c in cols] for i, lab in enumerate(rows_lab)]
        t = side.table(cellText=cell, colLabels=[""] + [COLS[k][0] for k in COLS], loc="upper left", cellLoc="left", edges="horizontal",
                       colWidths=[0.32, 0.17, 0.17, 0.17, 0.17], bbox=[0.0, 0.42, 1.0, 0.58])
        t.auto_set_font_size(False); t.set_fontsize(4.6)
        for (r_, c_), ce in t.get_celld().items():
            ce.PAD = 0.03
            if r_ == 0 and c_ == 1:
                ce.get_text().set_fontweight("bold")
        hh = [Patch(fc="#2171b5", label="probability density if the objects are debris (relative)"),
              plt.Line2D([], [], color="#08306b", lw=1.4, label="50 % region (drawn setting)"),
              plt.Line2D([], [], color="#08306b", lw=0.7, label="90 % region (drawn setting)")] + hv + hb
        hh += [Patch(fc=c, alpha=a, ec=c, label=l) for _, c, a, l in cs.SEARCH_FILL if l]
        hh += [plt.Line2D([], [], color="#1e8449", lw=1.4, ls=(0, (3, 2)), label="OI north-west band (not searched; grade C)"),
               plt.Line2D([], [], color="#333333", lw=0.7, ls=":", label="7th arc, FL400"),
               plt.Line2D([], [], ls="", marker="x", color="#d62728", label="Pléiades rating-5 objects"),
               plt.Line2D([], [], ls="", marker="o", mfc="white", mec="#e6550d", label="COSMO-SkyMed radar contacts (all four)")]
        side.legend(handles=hh, loc="upper left", bbox_to_anchor=(0.0, 0.40), frameon=False, fontsize=4.9, ncol=1)
        fig.suptitle(f"If the imaged objects are from 9M-MRO: where the debris entered the sea — {cs.describe_option(opt, short=True)}\n"
                     "drift-error correlation 0.25, two ocean models (proposed headline) — core run C NOT CONVERGED",
                     x=0.01, ha="left", y=0.995, fontsize=7)
        ste = STE.format(colour="The blue colour shows the probability with this assumption. The grey points show the probability without "
                                "this assumption.", lines="The thin lines show the 90 % region for other settings.")
        txt = textwrap.fill(ste, 205) + "\n" + textwrap.fill(tech(opt, key, pf, sh_note) + " Background: 6,000 points from the impact PDF "
                                                             "without H after the same searches.", 205)
        fig.text(0.01, 0.212, txt, ha="left", va="top", fontsize=4.55, color="#333333")
        fig.add_artist(plt.Line2D([0.01, 0.99], [0.218, 0.218], color="#999999", lw=0.4))
        fig.savefig(out / f"closeup-{safe}-headline-colour.png", dpi=300)
        fig.savefig(out / f"closeup-{safe}-headline-colour.pdf")
        plt.close(fig)
        # ---------------- seabed close-up (house style B), same drawn setting
        r = S[(S.option == opt) & (S.variant == DRAWN)].iloc[0]
        g = S[(S.option == opt) & (S.variant == "rho0.25 GLORYS12")].iloc[0]
        sd = sigma(SH, opt, DRAWN)
        ste_b = STE.format(colour="The red bands show the 50, 90 and 99 % regions with this assumption. The points show the probability "
                                  "without this assumption.", lines="")
        res = (f"Result, after all searches: 90 % region {r.hdr90_km2:,.0f} km²" + (f" ± {sd:,.0f} (split-half σ)" if sd is not None else "")
               + f", mean {abs(r.mean_lat):.2f} S {r.mean_lon:.2f} E; tension ln S {r.ln_S:+.2f} (p {r.tension_p:.2f}), mean shift "
               f"{r.mean_shift_nm:.0f} NM, PDF without H inside the 90 % region {100 * r.uncond_in_cond_hdr90:.0f} %. Beside it, GLORYS12 "
               f"only at ρ = 0.25: {g.hdr90_km2:,.0f} km², {abs(g.mean_lat):.2f} S {g.mean_lon:.2f} E, ln S {g.ln_S:+.2f}.")
        cs.style_b(head, geo, T5, Cc, opt, [" ".join(ste_b.split()), tech(opt, key, pf, sh_note), res], out, plt, gebco,
                   stem=f"closeup-{safe}-headline-seabed", bg="points")
        print(opt, flush=True)
    return S


if __name__ == "__main__":
    S = main(*sys.argv[1:8])
    pd.set_option("display.width", 250)
    print(S[["option_name", "variant", "hdr50_km2", "hdr90_km2", "mean_lat", "mean_lon", "share_outside_past_searches",
             "search_retains_under_H", "ln_S", "tension_p", "mean_shift_nm", "uncond_in_cond_hdr90"]].round(4).to_string(index=False))
