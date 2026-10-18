"""Pléiades close-ups (colour + seabed, the module's house styles) on core run J, for every 00:19 data treatment D0'-D5 under the
primary log-on cause (competing-causes total q = 1/3, C2 silent; survival factor), BEFORE any seabed search. Flight-only maps:
aggregate_runj.py's pooled cell masses (end of flight's own row weights, strata by core P x own evidence, D3/D4 waypoints from the
both-burst set). L_H on the wide grid (rho 0.25 two models GlobCurrent product-relative = headline; GLORYS12 only, rho 0 / 0.5
beside). Draw code: runi_closeups.draw with run J labels and no search applied.

    python runj_closeups.py <maps dir> <pleiades exchange run-j> <geom dir> <gebco json> <out dir> <pleiades-runj-table.json>
"""
import json
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "end-of-flight" / "smoke"))
sys.path.append(str(HERE))
from runi_closeups import DS, NLAT, NLON, CAUSE  # noqa: E402
TITLE = {"D0": "00:19 data held out, transmission imposed (D0\u2032)", "D1": "00:19 R600 BTO", "D2": "00:19 R600 BTO + R600 BFO",
         "D3": "00:19 R600 BTO + both BFOs (Holland H2 data)", "D4": "00:19 R600 BTO + both BFOs, Holland transient bias (H1 data)",
         "D5": "00:19 R600 BTO + R600 BFO + R1200 BFO with start-up offset"}


def draw(maps_dir, pl_root, geom, gebco, out, ess_json):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, Polygon
    from matplotlib.colors import LinearSegmentedColormap
    import closeup_figure as cf
    import closeup_styles as cs
    import headline_rho_standin as h
    import branch_eof289 as b
    from branch_figure import hdr_level
    from headline_splithalf import rho_L
    matplotlib.rcParams.update({"font.size": 6, "axes.titlesize": 6.5, "axes.labelsize": 6, "xtick.labelsize": 5.5, "ytick.labelsize": 5.5})
    out = Path(out); out.mkdir(parents=True, exist_ok=True); maps_dir = Path(maps_dir)
    geo = json.loads((Path(geom) / "search_footprints.geojson").read_text())
    M = HERE.parent
    T5 = pd.read_csv(M / "data/targets-3km.csv").query("arm == 'rating5'"); Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    surf = Path(pl_root) / "surfaces"
    lat = -44.975 + 0.05 * np.arange(NLAT); lon = 78.025 + 0.05 * np.arange(NLON)
    area = b.area_km2(np.meshgrid(lat, lon, indexing="ij")[0])
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    V = {"proposed": ("ρ = 0.25\ntwo models\n(drawn)", "#08306b", "-", rho_L(surf, 0.25, "mean", "-gcrel"), "drift-error correlation 0.25, two ocean models"),
         "g12": ("ρ = 0.25\nGLORYS12\nonly", "#e6550d", (0, (6, 2, 1, 2)), rho_L(surf, 0.25, 0, ""), "drift-error correlation 0.25, GLORYS12 only"),
         "rho0": ("ρ = 0\ntwo models", "#2ca25f", (0, (4, 2)), rho_L(surf, 0.0, "mean", "-gcrel"), "drift-error correlation 0, two ocean models"),
         "rho05": ("ρ = 0.5\ntwo models", "#984ea3", (0, (1, 1.2)), rho_L(surf, 0.5, "mean", "-gcrel"), "drift-error correlation 0.5, two ocean models")}
    masks = {"nw": cf.mask_of(cf.polygons(geo, "oi2024_proposed_inboard_northwest"), LON, LAT),
             "past": cf.mask_of(cf.polygons(geo, "atsb_phase2_2014_2017"), LON, LAT)
             | cf.mask_of(cf.polygons(geo, "bluefin21_2014_1"), LON, LAT) | cf.mask_of(cf.polygons(geo, "bluefin21_2014_2"), LON, LAT)}
    cmap = LinearSegmentedColormap.from_list("dens", [(1, 1, 1, 0), (0.776, 0.859, 0.937, 0.75), "#6baed6", "#2171b5", "#08306b"])
    v = "base"
    rows = []
    E = json.loads(Path(ess_json).read_text())["variants"]["head"]
    cs.SEARCH_SHORT["base"] = "before any seabed search"
    cs.BG_TEXT["points"] = cs.BG_TEXT["points"].replace(", after the same searches", ", before any seabed search")
    STE = ("STE100: This map shows where the aircraft possibly went into the sea, if the objects in the Pléiades satellite images are from "
           "9M-MRO. {c} The drawn result uses two ocean models with equal weight and a correlation of 0.25 between the drift errors of the "
           "two satellite data sets{l}. No seabed search is applied. The flight calculation is core run J; its sampling is accepted as converged by project "
           "ruling. The result is conditional on this assumption only.")
    for d in DS:
        Z = np.load(maps_dir / f"map-{d}.npz")
        base = dict(lat=lat, lon=lon, area=area, pre=Z["pre"], post=Z["post"])
        MP = {k: {v: {**base, "L_P+C4": V[k][3]}} for k in V}
        st = {k: h.row(MP[k], masks, v=v) for k in V}
        for k in V:
            rows.append(dict(treatment=d, cause=CAUSE, setting=k, **{kk: vv for kk, vv in st[k].items() if "search_retains" not in kk}))
        tech = ("Technical: core run J (waypoints 24, free 18, descent-climb 16, repro-radar 16 seeds; strata by core P x own evidence; D3 and D4 waypoints "
                "from the both-burst supplementary set, 8 seeds); split-half accepted as a pass by project ruling, 16 Oct 2026. End-of-flight physics PROVISIONAL "
                "(piloted-turn model, INTERIM pitch-down, push-over and Boeing sequence; end of flight's run J labels). "
                f"{TITLE[d]}; log-on cause: competing-causes total, q = 1/3, C2 silent (primary); survival factor applied; end of flight's own "
                "row weights (option_table_0019.seed_terms). Search: none applied (outlines drawn only). Under H: 12 "
                "rating-5 Pléiades objects (6 clusters, 3 km, equal weight) x all four COSMO-SkyMed contacts, one debris field; bivariate-normal "
                "transport errors, ρ = 0.25 (measured 0.07-0.41), ρ = 0 / 0.5 beside; GLORYS12 + ERA5 and GlobCurrent daily + ERA5, equal weight, "
                "GlobCurrent windage product-relative (drift audit F1). Headline (brief v2); GLORYS12 only beside. Maps from per-impact "
                "columns on the wide 0.05 deg grid (prepare/runj_closeups.py). Conditional on H; no identity likelihood, no Bayes factor or "
                "P(H | data).")
        ess = E[f"{d} x {CAUSE}"]["gcrel-0.25"]["eff_impacts"]; ess0 = E[f"{d} x {CAUSE}"]["none (without H)"]["eff_impacts"]
        a1 = E[f"{d} x {CAUSE}"]["gcrel-0.25"]["families"]["A1"]["eff_impacts"]
        gap = ess < 1000
        cov = (f"Coverage: effective impacts {ess:,.0f} under H ({ess0:,.0f} without H); A1 under H {a1:,.0f}. "
               + ("NOT ESTIMABLE: below the 1,000 gate. The speckled regions, the small areas and the tension are sampling artefacts of too few "
                  "effective impacts, not a measured result." if gap else "Gate (1,000) met." + (" A1 under H is below the gate." if a1 < 1000 else "")))
        warn = " — NOT ESTIMABLE (too few samples under H)" if gap else ""
        # ---------------- colour
        fig = plt.figure(figsize=(7.1, 5.5))
        ax = fig.add_axes([0.07, 0.265, 0.52, 0.65]); side = fig.add_axes([0.62, 0.265, 0.37, 0.65]); side.axis("off")
        for fid, col, al, lab in cs.SEARCH_FILL:
            for p in cf.polygons(geo, fid):
                ax.add_patch(Polygon(p[:, :2], closed=True, fc=col, ec=col, alpha=al if "oi20" not in fid else al * 0.45, lw=0.8, zorder=1))
        hb = cs.flight_background(ax, MP["proposed"], v, "points", "#222222", zorder=2)
        m = cs.panel_mass(MP["proposed"], v, "P+C4"); dn = m / area
        ax.pcolormesh(lon, lat, dn / dn.max(), cmap=cmap, vmin=0, vmax=1, shading="auto", rasterized=True, zorder=3)
        nw = cf.polygons(geo, "oi2024_proposed_inboard_northwest")[0]; ax.plot(nw[:, 0], nw[:, 1], color="#1e8449", lw=1.4, ls=(0, (3, 2)), zorder=4)
        arc = cf.polygons(geo, "seventh_arc_fl400")[0]; ax.plot(arc[:, 0], arc[:, 1], color="#333333", lw=0.7, ls=":", zorder=4)
        ax.contour(lon, lat, dn, levels=[hdr_level(dn, m, q) for q in (0.9, 0.5)], colors=["#08306b"] * 2, linewidths=[0.7, 1.4], zorder=6)
        hv = []
        for k in ("g12", "rho0", "rho05"):
            mm = cs.panel_mass(MP[k], v, "P+C4"); dd = mm / area
            ax.contour(lon, lat, dd, levels=[hdr_level(dd, mm, 0.9)], colors=[V[k][1]], linewidths=[0.75], linestyles=[V[k][2]], zorder=5)
            hv.append(plt.Line2D([], [], color=V[k][1], lw=0.9, ls=V[k][2], label="90 % region, " + V[k][4]))
        ax.plot(T5.lon, T5.lat, "x", ms=3.5, color="#d62728", mew=0.9, zorder=7)
        ax.plot(Cc.longitude, Cc.latitude, "o", ms=3.5, mfc="white", mec="#e6550d", mew=0.9, zorder=7)
        ax.set_xlim(88, 96); ax.set_ylim(-38, -32); ax.set_aspect(1 / np.cos(np.radians(35)))
        ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)")
        ax.set_title("before any seabed search; search outlines drawn only", loc="left", fontsize=6.3)
        rl = ["50 % region, km²", "90 % region, km²", "mean position", "outside official\nsearch outlines",
              "tension ln S (p)", "mean shift from\nPDF without H", "PDF without H\ninside 90 % region"]
        cols = []
        for k in V:
            r = st[k]; p = "n/e" if r["tension_p"] != r["tension_p"] else f"{r['tension_p']:.2f}"
            cols.append([f"{r['hdr50_km2']:,.0f}", f"{r['hdr90_km2']:,.0f}", f"{abs(r['mean_lat']):.2f} S\n{r['mean_lon']:.2f} E",
                         f"{100 * r['share_outside_past_searches']:.1f} %", f"{r['ln_S']:+.2f} ({p})",
                         f"{r['mean_shift_nm']:.0f} NM", f"{100 * r['uncond_in_cond_hdr90']:.0f} %"])
        t = side.table(cellText=[[lab] + [c[i] for c in cols] for i, lab in enumerate(rl)], colLabels=[""] + [V[k][0] for k in V],
                       loc="upper left", cellLoc="left", edges="horizontal", colWidths=[0.32, 0.17, 0.17, 0.17, 0.17], bbox=[0.0, 0.44, 1.0, 0.56])
        t.auto_set_font_size(False); t.set_fontsize(4.6)
        for (r_, c_), ce in t.get_celld().items():
            ce.PAD = 0.03
            if r_ == 0 and c_ == 1:
                ce.get_text().set_fontweight("bold")
        hh = [Patch(fc="#2171b5", label="probability density if the objects are debris (relative)"),
              plt.Line2D([], [], color="#08306b", lw=1.4, label="50 % region (drawn setting)"),
              plt.Line2D([], [], color="#08306b", lw=0.7, label="90 % region (drawn setting)")] + hv + hb
        hh += [Patch(fc=c, alpha=a if "Ocean" not in l and "OI" not in l else a * 0.45, ec=c, label=l + (" — drawn only, not applied" if ("Ocean" in l or "OI" in l) else ""))
               for _, c, a, l in cs.SEARCH_FILL if l]
        hh += [plt.Line2D([], [], color="#1e8449", lw=1.4, ls=(0, (3, 2)), label="OI north-west band (not searched; grade C)"),
               plt.Line2D([], [], color="#333333", lw=0.7, ls=":", label="7th arc, FL400"),
               plt.Line2D([], [], ls="", marker="x", color="#d62728", label="Pléiades rating-5 objects"),
               plt.Line2D([], [], ls="", marker="o", mfc="white", mec="#e6550d", label="COSMO-SkyMed radar contacts (all four)")]
        side.legend(handles=hh, loc="upper left", bbox_to_anchor=(0.0, 0.42), frameon=False, fontsize=4.7, ncol=1)
        fig.suptitle(f"If the imaged objects are from 9M-MRO: where the debris entered the sea — {TITLE[d]}\n"
                     "core run J, drift-error correlation 0.25, two ocean models (headline)" + warn, x=0.01, ha="left", y=0.995, fontsize=7)
        ste = STE.format(c="The blue colour shows the probability with this assumption. The grey points show the probability without this assumption.",
                         l="; the thin lines show the 90 % region for other settings")
        txt = textwrap.fill(ste, 205) + "\n" + textwrap.fill(tech + " " + cov + " Background: 6,000 points from the impact PDF without H, before any seabed search.", 205)
        fig.text(0.01, 0.212, txt, ha="left", va="top", fontsize=4.5, color="#333333")
        fig.add_artist(plt.Line2D([0.01, 0.99], [0.218, 0.218], color="#999999", lw=0.4))
        fig.savefig(out / f"closeup-runj-{d}-colour.png", dpi=300); fig.savefig(out / f"closeup-runj-{d}-colour.pdf"); plt.close(fig)
        # ---------------- seabed
        r = st["proposed"]; g = st["g12"]; p = "n/e" if r["tension_p"] != r["tension_p"] else f"{r['tension_p']:.2f}"
        res = (f"Result, before any seabed search: 90 % region {r['hdr90_km2']:,.0f} km², mean {abs(r['mean_lat']):.2f} S {r['mean_lon']:.2f} E; "
               f"tension ln S {r['ln_S']:+.2f} (p {p}), mean shift {r['mean_shift_nm']:.0f} NM; PDF without H inside the 90 % region "
               f"{100 * r['uncond_in_cond_hdr90']:.0f} %. Beside it, GLORYS12 only at ρ = 0.25: {g['hdr90_km2']:,.0f} km², "
               f"{abs(g['mean_lat']):.2f} S {g['mean_lon']:.2f} E, ln S {g['ln_S']:+.2f}.")
        ste_b = STE.format(c="The red bands show the 50, 90 and 99 % regions with this assumption. The points show the probability without this assumption.", l="")
        cs.style_b(MP["proposed"], geo, T5, Cc, d, [ste_b, tech, cov, res], out, plt, gebco, stem=f"closeup-runj-{d}-seabed", bg="points",
                   v=v, title_opt=TITLE[d] + " — core run J" + warn)
        print(d, flush=True)
    pd.DataFrame(rows).to_csv(out / "closeup-runj-stats.csv", index=False)


if __name__ == "__main__":
    draw(*sys.argv[1:7])
