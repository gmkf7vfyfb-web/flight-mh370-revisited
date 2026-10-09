"""Close-up of the conditional branch after the seabed search, with every search outline drawn, the Ocean
Infinity layers applied as labelled variants, and a like-for-like comparison with the prior work's
transport-only "residual origin density".

    python closeup_figure.py <runs/pleiades> <module dir> <geometry dir> <out dir>

Inputs (all produced by this module or read in place):
  branch-289/, branch-289-oi2018/, branch-289-oi2018-2025/   branch_eof289.py with the searched-areas column
      (base: Phase 2 + Bluefin-21; + OI 2018; + OI 2018 + OI 2025-26 south-east band), 00:19 option none
  eval-oi/grid-<variant>/evaluate.csv   the searched-areas module's ln P(no find) at every grid centre
  <geometry dir>/search_footprints.geojson   ATSB Phase 2, Bluefin-21, OI 2018 outline, OI 2024 proposed
      bands (south-east, north-west), 7th arc FL400 (community / official tracings, grades as recorded)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.path import Path as MPath

sys.path.insert(0, str(Path(__file__).parent))
from branch_figure import footnote, hdr_level  # noqa: E402

VARIANTS = [("base", "branch-289", "Phase 2 + Bluefin-21"),
            ("oi2018", "branch-289-oi2018", "+ Ocean Infinity 2018"),
            ("oi2018-2025", "branch-289-oi2018-2025", "+ OI 2018 + OI 2025-26 south-east band")]


def polygons(geo, fid):
    for f in geo["features"]:
        if f["properties"].get("id") == fid:
            g = f["geometry"]
            if g["type"] == "Polygon":
                return [np.asarray(g["coordinates"][0])]
            if g["type"] == "MultiPolygon":
                return [np.asarray(p[0]) for p in g["coordinates"]]
            if g["type"] == "LineString":
                return [np.asarray(g["coordinates"])]
    raise KeyError(fid)


def mask_of(polys, LON, LAT):
    pts = np.c_[LON.ravel(), LAT.ravel()]
    m = np.zeros(len(pts), bool)
    for p in polys:
        m |= MPath(p[:, :2]).contains_points(pts)
    return m.reshape(LON.shape)


def grid_search(runs, v, shape):
    d = pd.read_csv(Path(runs) / "eval-oi" / f"grid-{v}" / "evaluate.csv")
    return np.exp(d["seabed-search:loglik"].to_numpy()).reshape(shape)


def stats(m, area, LAT, LON, masks):
    m = m / m.sum()
    dn = m / area
    lvl = hdr_level(dn, m)
    i = np.unravel_index(np.argmax(dn), dn.shape)
    out = dict(hdr90_km2=float(area[dn >= lvl].sum()), mode_lat=float(LAT[i]), mode_lon=float(LON[i]),
               mean_lat=float((m * LAT).sum()), mean_lon=float((m * LON).sum()))
    for k, mk in masks.items():
        out[f"mass_in_{k}"] = float(m[mk].sum())
    return out


BAND_FILL = ["#f3f3f3", "#e0e0e0", "#c4c4c4"]   # 99 / 90 / 50 % (light, so outlines stay legible)
BAND_LW = [0.45, 0.9, 1.5]                        # black contour weights, 99 / 90 / 50 %


def hdr_bands(ax, lon, lat, dn, m):
    """Light greyscale HDR bands (99/90/50 %) with black contours of increasing weight."""
    lv = [hdr_level(dn, m, q) for q in (0.99, 0.9, 0.5)]
    ax.contourf(lon, lat, dn, levels=lv + [dn.max() * 1.0001], colors=BAND_FILL, zorder=0)
    ax.contour(lon, lat, dn, levels=lv, colors="black", linewidths=BAND_LW, zorder=1)
    ax.set_aspect(1 / np.cos(np.radians(35)))


def draw_outlines(ax, geo):
    for p in polygons(geo, "atsb_phase2_2014_2017"):
        ax.plot(p[:, 0], p[:, 1], color="#3c3c3c", lw=1.3, zorder=2)
    for fid in ("bluefin21_2014_1", "bluefin21_2014_2"):
        for p in polygons(geo, fid):
            ax.plot(p[:, 0], p[:, 1], color="#3c3c3c", lw=1.1, zorder=2)
    p = polygons(geo, "oi2018_total_outline_approx")[0]
    ax.plot(p[:, 0], p[:, 1], color="#6a3d9a", lw=1.5, ls=(0, (5, 3)), zorder=2)
    p = polygons(geo, "oi2024_proposed_outboard_southeast")[0]
    ax.plot(p[:, 0], p[:, 1], color="#c0392b", lw=1.7, zorder=2)
    p = polygons(geo, "oi2024_proposed_inboard_northwest")[0]
    ax.plot(p[:, 0], p[:, 1], color="#1e8449", lw=1.7, ls=(0, (3, 2)), zorder=2)
    a = polygons(geo, "seventh_arc_fl400")[0]
    ax.plot(a[:, 0], a[:, 1], color="#777777", lw=0.8, ls=":", zorder=2)


def make(runs, module_dir, geom_dir, out, plt, panel_letter=None):
    runs, M, G, out = Path(runs), Path(module_dir), Path(geom_dir), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    geo = json.loads((G / "search_footprints.geojson").read_text())
    Z = {v: np.load(runs / d / "branch-maps.npz") for v, d, _ in VARIANTS}
    lat, lon, area = Z["base"]["lat"], Z["base"]["lon"], Z["base"]["area"]
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    masks = {
        "phase2": mask_of(polygons(geo, "atsb_phase2_2014_2017"), LON, LAT),
        "oi2018_outline": mask_of(polygons(geo, "oi2018_total_outline_approx"), LON, LAT),
        "oi_southeast_band": mask_of(polygons(geo, "oi2024_proposed_outboard_southeast"), LON, LAT),
        "oi_northwest_band": mask_of(polygons(geo, "oi2024_proposed_inboard_northwest"), LON, LAT),
    }
    masks["any_past_envelope"] = masks["phase2"] | masks["oi2018_outline"] | masks["oi_southeast_band"]
    T = pd.read_csv(M / "data/targets-3km.csv")
    T5 = T[T.arm == "rating5"]
    Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    rows = []
    # flight-conditioned: pre = flight posterior histogram; post = x search (per impact), per variant
    for v, d, lab in VARIANTS:
        for f in ("P+C3", "P+C4", "P", "C4"):
            L = np.nan_to_num(Z[v][f"L_{f}"])
            for stage, pc in (("before search", Z[v]["pre"]), ("after search", Z[v]["post"])):
                if stage == "before search" and v != "base":
                    continue
                r = stats(pc * L, area, LAT, LON, masks)
                r.update(prior="flight posterior (reference-289, 00:19 none)", field=f, search=lab if stage == "after search" else "none", stage=stage)
                rows.append(r)
    # transport-only (flat prior over the grid), as in the prior work's 'residual origin density'
    S = {v: grid_search(runs, v, LAT.shape) for v, _, _ in VARIANTS}
    LP, LC4 = np.nan_to_num(Z["base"]["L_P"]), np.nan_to_num(Z["base"]["L_C4"])
    pool = 0.5 * LP / (LP * area).sum() + 0.5 * LC4 / (LC4 * area).sum()  # prior work's 50:50 sensor pool
    for name, L in (("P+C4 joint (product)", np.nan_to_num(Z["base"]["L_P+C4"])), ("P | C4 50:50 pool", pool)):
        rows.append(dict(stats(L * area, area, LAT, LON, masks), prior="flat (transport only)", field=name, search="none", stage="before search"))
        for v, _, lab in VARIANTS:
            rows.append(dict(stats(L * S[v] * area, area, LAT, LON, masks), prior="flat (transport only)", field=name, search=lab, stage="after search"))
    tab = pd.DataFrame(rows)
    tab.to_csv(out / "closeup-stats.csv", index=False)

    # ---- figure 1: close-up of 'Both, after search', across search variants ----
    panels = [("base", "P+C3", "Both (P+C3), after search: Phase 2 + Bluefin-21"),
              ("base", "P+C4", "Both (P+C4), after search: Phase 2 + Bluefin-21"),
              ("oi2018", "P+C4", "P+C4, after search: + Ocean Infinity 2018"),
              ("oi2018-2025", "P+C4", "P+C4, after search: + OI 2018 + OI 2025-26 SE band")]
    fig, axs = plt.subplots(2, 2, figsize=(7.1, 6.4), sharex=True, sharey=True, gridspec_kw=dict(wspace=0.05, hspace=0.12))
    ext = [lon[0] - 0.025, lon[-1] + 0.025, lat[0] - 0.025, lat[-1] + 0.025]
    for ax, (v, f, ttl) in zip(axs.ravel(), panels):
        m = Z[v]["post"] * np.nan_to_num(Z[v][f"L_{f}"])
        m = m / m.sum()
        dn = m / area
        hdr_bands(ax, lon, lat, dn, m)
        draw_outlines(ax, geo)
        ax.plot(T5.lon, T5.lat, "x", ms=3, color="#b03030", mew=0.7)
        n = 3 if f == "P+C3" else 4
        ax.plot(Cc.longitude[:n], Cc.latitude[:n], "o", ms=3, mfc="none", mec="#d35400", mew=0.7)
        r = tab[(tab.prior.str.startswith("flight")) & (tab.field == f) & (tab.stage == "after search") & (tab.search == dict((a, c) for a, _, c in VARIANTS)[v])].iloc[0]
        ax.plot(r.mode_lon, r.mode_lat, "*", ms=6, color="#f0b030", mec="#333333", mew=0.4)
        ax.text(0.02, 0.03, f"90 % area {r.hdr90_km2:,.0f} km²\nin NW band {100 * r.mass_in_oi_northwest_band:.1f} %;"
                f" outside past envelopes {100 * (1 - r.mass_in_any_past_envelope):.1f} %",
                transform=ax.transAxes, fontsize=5.5, va="bottom",
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.0))
        ax.set_title(ttl, loc="left", fontsize=6.5)
        ax.set_xlim(88, 96)
        ax.set_ylim(-38, -32)
    for ax in axs[:, 0]:
        ax.set_ylabel("Latitude (°)")
    for ax in axs[1, :]:
        ax.set_xlabel("Longitude (°E)")
    if panel_letter:
        for a, l in zip(axs.ravel(), "abcd"):
            panel_letter(a, l)
    from matplotlib.patches import Patch
    h = [Patch(fc=BAND_FILL[2], ec="black", lw=BAND_LW[2], label="50 % of probability"),
         Patch(fc=BAND_FILL[1], ec="black", lw=BAND_LW[1], label="90 % of probability"),
         Patch(fc=BAND_FILL[0], ec="black", lw=BAND_LW[0], label="99 % of probability"),
         plt.Line2D([], [], color="#3c3c3c", lw=1.3, label="ATSB Phase 2 2014-17 and Bluefin-21 (official footprints)"),
         plt.Line2D([], [], color="#6a3d9a", lw=1.5, ls=(0, (5, 3)), label="Ocean Infinity 2018 outline (community tracing, grade C)"),
         plt.Line2D([], [], color="#c0392b", lw=1.7, label="OI 2025-26 south-east band (likely searched; grade C)"),
         plt.Line2D([], [], color="#1e8449", lw=1.7, ls=(0, (3, 2)), label="OI inferred remaining north-west band (not searched; grade C)"),
         plt.Line2D([], [], color="#777777", lw=0.8, ls=":", label="7th arc, FL400 (official)"),
         plt.Line2D([], [], ls="", marker="x", color="#b03030", label="Pléiades rating-5 objects"),
         plt.Line2D([], [], ls="", marker="o", mfc="none", mec="#d35400", label="COSMO-SkyMed contacts F1-F3 (F4 in b-d)"),
         plt.Line2D([], [], ls="", marker="*", color="#f0b030", mec="#333333", label="grid-cell mode")]
    fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.06, -0.06), ncol=2, frameon=False, fontsize=5.5)
    notes = [
        "Prior: end of flight's reference-289 impacts (run eof-289-full; core reference-289, prior track 289.7 deg sd 1.0 at 18:01:49 UTC; base config "
        "davey2016 + no-exhaustion-prior + reference-snapshots + early-families/overnight/reference-289 + end-of-flight full/reference-289); 4 seeds x "
        "100,000 parents x 8 children x 4 descents = 12,799,968 impacts; 7 Hz BFO sigma baseline. 00:19 option 'none' (both 00:19 messages held out), "
        "log-on cause 'other'. End-of-flight dive class (b) and Boeing-calibrated glide: PROVISIONAL. The core run is tempered "
        "(temper_epochs m1839-m0011, 16 stages) and so is affected by filter-audit F1 (tempered-move ancestry defect): PROVISIONAL until re-run.",
        "Search: the searched-areas module's per-impact likelihood, point target, rho = 0.05. Phase 2 (q 0.945) and Bluefin-21 (q 0.9) official; "
        "OI 2018 (q 0.9, coverage fraction 0.889) and OI 2025-26 south-east band (q 0.9, coverage fraction 0.7808) are inferred community tracings "
        "(MH370-CAPTION, grade C), used as Pete ruled with this footnote. The north-west band is drawn only: it is not searched and is never negative evidence.",
        "Under H: Pléiades rating-5 clusters (3 km), equal weights; COSMO pass dawn-20 / dusk-21 Mar equally weighted; P+C = both sets debris (product), "
        "formed per ocean model; GLORYS12 + ERA5 and GlobCurrent daily + ERA5 at equal weight; measured transport error (GDP-replay OU fit: ~100-110 km rms per component at 15 d), windage 0-5 %; Pleiades and COSMO "
        "transport errors treated as independent (rho = 0; rho 0.5-0.8 widens the 90 % area by 28-38 %, see closeup-289.md).",
        "Conditional on H; no Bayes factor or P(H | data). Shading: highest-density regions holding 50/90/99 % of each panel's PDF. Percentages are of the panel's PDF within the 0.05 deg grid.",
    ]
    footnote(fig, notes, width=150, y=-0.10)
    fig.savefig(out / "closeup-both-after-search.png", dpi=300, bbox_inches="tight")
    fig.savefig(out / "closeup-both-after-search.pdf", bbox_inches="tight")
    plt.close(fig)

    # ---- figure 2: like-for-like with the prior work (transport only, flat prior) ----
    fig, axs = plt.subplots(1, 3, figsize=(7.1, 2.45), sharey=True, gridspec_kw=dict(wspace=0.05))
    L = np.nan_to_num(Z["base"]["L_P+C4"])
    for ax, (ttl, w) in zip(axs, [("Transport only, before search", np.ones_like(L)),
                                  ("After Phase 2 + Bluefin-21", S["base"]),
                                  ("After + OI 2018 + OI 2025-26 SE band", S["oi2018-2025"])]):
        m = L * w * area
        m = m / m.sum()
        dn = m / area
        hdr_bands(ax, lon, lat, dn, m)
        draw_outlines(ax, geo)
        ax.plot(T5.lon, T5.lat, "x", ms=3, color="#b03030", mew=0.7)
        ax.plot(Cc.longitude, Cc.latitude, "o", ms=3, mfc="none", mec="#d35400", mew=0.7)
        st = stats(m, area, LAT, LON, masks)
        ax.plot(st["mode_lon"], st["mode_lat"], "*", ms=6, color="#f0b030", mec="#333333", mew=0.4)
        ax.text(0.02, 0.03, f"90 % area {st['hdr90_km2']:,.0f} km²\noutside past envelopes {100 * (1 - st['mass_in_any_past_envelope']):.1f} %",
                transform=ax.transAxes, fontsize=5.5, va="bottom",
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.0))
        ax.set_title(ttl, loc="left", fontsize=6.5)
        ax.set_xlim(88, 96)
        ax.set_ylim(-38, -32)
        ax.set_xlabel("Longitude (°E)")
        ax.set_xticks([88, 90, 92, 94, 96] if ax is axs[-1] else [88, 90, 92, 94])
    axs[0].set_ylabel("Latitude (°)")
    if panel_letter:
        for a, l in zip(axs, "abc"):
            panel_letter(a, l)
    footnote(fig, [
        "Like-for-like with the prior work's 'residual origin density': flat prior over 85-103 E, 43-25 S (no flight posterior), Pléiades x all four "
        "COSMO contacts (joint product, not the prior work's 50:50 pool; the pool is in closeup-stats.csv). Search factor: the searched-areas "
        "module's ln P(no find) evaluated at every grid centre (point target, rho = 0.05; shared miss dependence as in its run.toml).",
        "Ocean models GLORYS12 + ERA5 and GlobCurrent daily + ERA5 at equal weight (the prior work: BRAN2016, OSCAR v2, GLORYS12 + WAVERYS); measured "
        "transport error; COSMO passes dawn-20 / dusk-21 Mar equally weighted (the prior work: 21 March). Outlines and grades as in the close-up figure.",
        "No flight posterior, so no 00:19 option applies here. GlobCurrent daily label provisional (P4). Conditional on H; no Bayes factor or "
        "P(H | data). The grid-cell mode sits on a broad plateau (L_P and L_C4 within 5 % of their local maximum over ~0.15 deg), so read the HDR, not the star. Shading and line weights as in the close-up figure (50/90/99 % HDR).",
    ], width=150, y=0.0)
    fig.savefig(out / "transport-only-vs-prior-work.png", dpi=300, bbox_inches="tight")
    fig.savefig(out / "transport-only-vs-prior-work.pdf", bbox_inches="tight")
    plt.close(fig)
    return tab


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    make(*sys.argv[1:5], plt=plt)
