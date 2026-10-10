"""Three alternative designs for the close-up of the conditional PDF under H (Pete, 10 Oct 2026: "try three very
different approaches"). Same data as option_closeups.py; only the presentation differs.

  A  colour      2 x 2 small multiples; perceptual colour density with HDR contours; searched areas as translucent
                 fills; statistics in a table under the maps instead of inside the axes.
  B  seabed      one large map of the headline panel on GEBCO 2026 shaded relief, HDR as coloured bands, plus a
                 latitude-PDF strip comparing the four variants.
  C  arc frame   the PDF re-projected into distance along the 7th arc and distance north-west of it (NM), so search
                 widths and "how far inside the arc" read directly; across-arc marginal on the right.

    python closeup_styles.py <branch root> <impacts root> <geometry dir> <gebco grid json> <out dir> <option>
                             [--pfamily ...] [--labels ...]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import closeup_figure as cf  # noqa: E402
from branch_figure import footnote, hdr_level, run_provenance  # noqa: E402
from describe import describe_option, describe_field, SEARCH_SHORT  # noqa: E402
from option_closeups import load_mixture  # noqa: E402
from rerun_reference import tension  # noqa: E402


def mix_tension(mp, v, f="P+C4"):
    """Tension of H against the flight posterior on this map (brief: the conditional and the tension go TOGETHER):
    the module's own measure (rerun_reference.tension: ln S, Handley-Lemos p, mean shift)."""
    lat, lon, area = mp[v]["lat"], mp[v]["lon"], mp[v]["area"]
    z = np.zeros_like(area, dtype=bool)
    return tension(mp[v]["post"], np.nan_to_num(mp[v][f"L_{f}"]), area, lat, lon, z, z, z)

NM = 1.852
PANELS = [("base", "P+C3"), ("base", "P+C4"), ("oi2018-2025", "P+C3"), ("oi2018-2025", "P+C4")]
SEARCH_FILL = [("atsb_phase2_2014_2017", "#7f7f7f", 0.30, "ATSB Phase 2 2014-17 (official)"),
               ("bluefin21_2014_1", "#7f7f7f", 0.30, None), ("bluefin21_2014_2", "#7f7f7f", 0.30, None),
               ("oi2018_total_outline_approx", "#6a3d9a", 0.18, "Ocean Infinity 2018 (grade C)"),
               ("oi2024_proposed_outboard_southeast", "#c0392b", 0.28, "OI 2025-26 south-east band (grade C)")]


def eof_family_key(opt):
    """end of flight's key in family-evidence-*.json for a module option string."""
    base = opt.split("@")[0]
    opt0, _, con = base.partition("+")
    name = describe_option(opt0, short=True).replace(" (unconstrained)", "")
    # end of flight publishes `+alive` keys only. For `unpowered` (ruling ~19:10 B (b)) the family weights use the `+alive` key and the
    # not-powered-at-01:15:56 factor acts within each stratum only (as ocean settling does; it removes <= 0.3 % of weight). Others: fixed.
    if con == "unpowered":
        con = "alive"
    return name + (f" +{con}" if con else "")


def reweighted_pfam(fam_json, opt):
    """Ruling C (architecture, 10 Oct 2026): P(family) re-weighted by the 00:19 evidence, from end of flight's own file.
    Returns None where end of flight gives no re-weighting (Holland H1/H2: not yet estimable)."""
    if not fam_json:
        return None
    d = json.loads(Path(fam_json).read_text())["mixtures"]
    k = eof_family_key(opt)
    if k not in d or "Holland" in k:
        return None
    return {s: float(v) for s, v in d[k]["p_family_reweighted"].items()}


def notes_for(opt, src, pfam, labels, pfam_rw=None, fam_json=None):
    if pfam and pfam_rw:
        mix = (f"Strata mixed by P(family) re-weighted by the 00:19 evidence (ruling C; end of flight's "
               f"{Path(fam_json).name}, key '{eof_family_key(opt)}': {', '.join(f'{k} {pfam_rw[k]:.4f}' for k in pfam)}"
               + ("; the not-powered-at-01:15:56 factor acts within each stratum, not in these weights" if "+unpowered" in opt else "")
               + "); the core's fixed P(family) "
               f"({', '.join(f'{k} {v:.4f}' for k, v in pfam.items())}) is shown beside it. The search then re-weights strata by their own evidence.")
    elif pfam:
        mix = (f"Strata mixed by core's P(family), held fixed ({', '.join(f'{k} {v:.4f}' for k, v in pfam.items())}); the search "
               f"re-weights strata by their own evidence, the 00:19 data do not.")
    else:
        mix = "Single impact set."
    return [src, "What was run: " + describe_option(opt) + ". " + mix, "Labels: " + (labels or "none") + ".",
            "Search: the searched-areas module's own per-impact likelihood (point target, rho = 0.05, shared). Phase 2 (q 0.945), "
            "Bluefin-21 (q 0.9) official; OI 2018 (q 0.9, coverage 0.889) and OI 2025-26 south-east band (q 0.9, coverage 0.7808) are "
            "community tracings, grade C; the north-west band is drawn only, never negative evidence.",
            "Under H: 12 rating-5 Pléiades objects in 6 clusters (3 km), equal weights; COSMO-SkyMed contacts equally weighted, dawn "
            "20 / dusk 21 Mar passes equal (unverified source, time, footprint); 'one debris field' = likelihoods multiplied per ocean "
            "model; GLORYS12 + ERA5 and GlobCurrent daily + ERA5 equal weight; measured transport error (~100-110 km per component at "
            "15 d); windage 0-5 %; Pléiades and COSMO errors independent (rho = 0).",
            "Conditional on H (the objects are debris from 9M-MRO); no Bayes factor or P(H | data)."]


def panel_mass(maps, v, f):
    m = maps[v]["post"] * np.nan_to_num(maps[v][f"L_{f}"])
    return m / m.sum()


# ---------------------------------------------------------------- A: colour small multiples + table
PANELS_A = [("base", "P+C4"), ("oi2018-2025", "P+C4")]


def style_a(maps, geo, T5, Cc, opt, notes, out, plt, stem="style-A-colour"):
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Patch, Polygon
    cmap = LinearSegmentedColormap.from_list("dens", ["#ffffff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"])
    lat, lon, area = maps["base"]["lat"], maps["base"]["lon"], maps["base"]["area"]
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    fig = plt.figure(figsize=(7.1, 4.9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.36], hspace=0.30, wspace=0.06)
    axs = [fig.add_subplot(gs[0, i]) for i in range(2)]
    rows = []
    for ax, (v, f), let in zip(axs, PANELS_A, "ab"):
        m = panel_mass(maps, v, f); dn = m / area
        ax.pcolormesh(lon, lat, dn / dn.max(), cmap=cmap, vmin=0, vmax=1, shading="auto", rasterized=True, zorder=0)
        for fid, col, al, _ in SEARCH_FILL:
            for p in cf.polygons(geo, fid):
                ax.add_patch(Polygon(p[:, :2], closed=True, fc=col, ec=col, alpha=al, lw=0.8, zorder=2))
        nw = cf.polygons(geo, "oi2024_proposed_inboard_northwest")[0]
        ax.plot(nw[:, 0], nw[:, 1], color="#1e8449", lw=1.4, ls=(0, (3, 2)), zorder=3)
        arc = cf.polygons(geo, "seventh_arc_fl400")[0]
        ax.plot(arc[:, 0], arc[:, 1], color="#333333", lw=0.7, ls=":", zorder=3)
        lv = [hdr_level(dn, m, q) for q in (0.9, 0.5)]
        ax.contour(lon, lat, dn, levels=lv, colors=["#08306b", "#08306b"], linewidths=[0.7, 1.4], zorder=4)
        ax.plot(T5.lon, T5.lat, "x", ms=3.5, color="#d62728", mew=0.9, zorder=5)
        ax.plot(Cc.longitude, Cc.latitude, "o", ms=3.5, mfc="white", mec="#e6550d", mew=0.9, zorder=5)
        ax.set_xlim(88, 96); ax.set_ylim(-38, -32); ax.set_aspect(1 / np.cos(np.radians(35)))
        ax.set_title(f"{let}  {SEARCH_SHORT[v]}", loc="left", fontsize=6)
        ax.tick_params(labelsize=5.5)
        if let == "b":
            ax.set_yticklabels([])
        s = cf.stats(m, area, LAT, LON, {})
        rows.append([let, f"{area[dn >= lv[1]].sum():,.0f}", f"{s['hdr90_km2']:,.0f}", f"{abs(s['mean_lat']):.2f} S {s['mean_lon']:.2f} E"])
    axs[0].set_ylabel("Latitude (°)", fontsize=6)
    for ax in axs:
        ax.set_xlabel("Longitude (°E)", fontsize=6)
    tab = fig.add_subplot(gs[1, 0]); tab.axis("off")
    t = tab.table(cellText=rows, colLabels=["panel", "50 % area km²", "90 % area km²", "mean"], loc="upper left",
                  colLoc="left", cellLoc="left", edges="horizontal", colWidths=[0.12, 0.27, 0.27, 0.34])
    t.auto_set_font_size(False); t.set_fontsize(5.8); t.scale(1, 1.15)
    lg = fig.add_subplot(gs[1, 1]); lg.axis("off")
    h = [Patch(fc="#2171b5", label="probability density (relative)"),
         plt.Line2D([], [], color="#08306b", lw=1.4, label="50 % region"), plt.Line2D([], [], color="#08306b", lw=0.7, label="90 % region")]
    h += [Patch(fc=c, alpha=a, ec=c, label=l) for _, c, a, l in SEARCH_FILL if l]
    h += [plt.Line2D([], [], color="#1e8449", lw=1.4, ls=(0, (3, 2)), label="OI north-west band (not searched; grade C)"),
          plt.Line2D([], [], color="#333333", lw=0.7, ls=":", label="7th arc, FL400"),
          plt.Line2D([], [], ls="", marker="x", color="#d62728", label="Pléiades rating-5 objects"),
          plt.Line2D([], [], ls="", marker="o", mfc="white", mec="#e6550d", label="COSMO-SkyMed radar contacts (all four)")]
    lg.legend(handles=h, loc="upper left", frameon=False, fontsize=5.6, ncol=2)
    fig.suptitle(f"If the imaged objects are from 9M-MRO: where the debris entered the sea — {describe_option(opt, short=True)}\n"
                 f"Pléiades objects + all four COSMO-SkyMed contacts, one debris field", x=0.01, ha="left", y=1.0, fontsize=7)
    footnote(fig, notes, width=165, y=0.10)
    fig.savefig(out / f"{stem}.png", dpi=300, bbox_inches="tight"); fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)



# ---------------------------------------------------------------- flight-posterior background (Pete, 10 Oct 2026)
BG_TEXT = {
    None: "",
    "contours": "Background: the impact PDF without H (flight posterior alone, after the same searches), as its 50 % and 90 % "
                "regions (dashed lines). Its regions are computed over the whole grid, 85-103 E, 43-25 S.",
    "points": "Background: the impact PDF without H (flight posterior alone, after the same searches), as 6,000 points drawn "
              "in proportion to its probability from 0.05 deg grid cells and jittered within each cell.",
    "shade": "Background: the impact PDF without H (flight posterior alone, after the same searches), as shading of its "
             "density, scaled to its 99th percentile inside this frame.",
}


def flight_background(ax, maps, v, mode, colour, zorder=1, cmap=None):
    """Draw the flight posterior alone (after the same searches) behind the conditional. Returns legend handles."""
    if not mode:
        return []
    lat, lon, area = maps[v]["lat"], maps[v]["lon"], maps[v]["area"]
    m = maps[v]["post"] / maps[v]["post"].sum(); dn = m / area
    import matplotlib.pyplot as plt
    if mode == "contours":
        lv = [hdr_level(dn, m, q) for q in (0.9, 0.5)]
        ax.contour(lon, lat, dn, levels=lv, colors=[colour, colour], linewidths=[0.7, 1.1], linestyles=[(0, (4, 2)), (0, (4, 2))], zorder=zorder)
        return [plt.Line2D([], [], color=colour, lw=0.9, ls=(0, (4, 2)), label="impact PDF without H: 50 % / 90 % regions")]
    if mode == "points":
        rng = np.random.default_rng(0)
        k = rng.choice(m.size, size=6000, p=m.ravel())
        i, j = np.unravel_index(k, m.shape)
        step = float(lat[1] - lat[0])
        y = lat[i] + rng.uniform(-step / 2, step / 2, len(k)); x = lon[j] + rng.uniform(-step / 2, step / 2, len(k))
        ax.scatter(x, y, s=1.2, c=colour, alpha=0.55, linewidths=0, zorder=zorder, rasterized=True)
        return [plt.Line2D([], [], ls="", marker="o", ms=1.5, color=colour, alpha=0.6, label="impact PDF without H (sampled points)")]
    if mode == "shade":
        from matplotlib.colors import LinearSegmentedColormap
        cm = cmap or LinearSegmentedColormap.from_list("bg", [(1, 1, 1, 0), colour])
        la_ = (lat >= -38) & (lat <= -32); lo_ = (lon >= 88) & (lon <= 96)
        ref = np.quantile(dn[np.ix_(la_, lo_)], 0.99) or dn.max()
        ax.pcolormesh(lon, lat, np.clip(dn / ref, 0, 1), cmap=cm, vmin=0, vmax=1, alpha=0.6, shading="auto", rasterized=True, zorder=zorder)
        from matplotlib.patches import Patch
        return [Patch(fc=colour, alpha=0.35, label="impact PDF without H (shading)")]
    raise ValueError(mode)


def frame_share(maps, v):
    lat, lon = maps[v]["lat"], maps[v]["lon"]
    m = maps[v]["post"] / maps[v]["post"].sum()
    la = (lat >= -38) & (lat <= -32); lo = (lon >= 88) & (lon <= 96)
    return float(m[np.ix_(la, lo)].sum())


# ---------------------------------------------------------------- colour, one panel (the old panel b), with table
def colour_single(maps, geo, T5, Cc, opt, notes, out, plt, stem, bg=None, v="oi2018-2025", f="P+C4", cmp=None):
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Patch, Polygon
    cmap = LinearSegmentedColormap.from_list("dens", [(1, 1, 1, 0), (0.776, 0.859, 0.937, 0.75), "#6baed6", "#2171b5", "#08306b"])
    lat, lon, area = maps[v]["lat"], maps[v]["lon"], maps[v]["area"]
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    fig = plt.figure(figsize=(7.1, 4.6))
    ax = fig.add_axes([0.07, 0.12, 0.56, 0.80])
    side = fig.add_axes([0.66, 0.12, 0.33, 0.80]); side.axis("off")
    for fid, col, al, _ in SEARCH_FILL:
        for p in cf.polygons(geo, fid):
            ax.add_patch(Polygon(p[:, :2], closed=True, fc=col, ec=col, alpha=al, lw=0.8, zorder=1))
    hb = flight_background(ax, maps, v, bg, "#222222", zorder=2)
    m = panel_mass(maps, v, f); dn = m / area
    ax.pcolormesh(lon, lat, dn / dn.max(), cmap=cmap, vmin=0, vmax=1, shading="auto", rasterized=True, zorder=3)
    nw = cf.polygons(geo, "oi2024_proposed_inboard_northwest")[0]
    ax.plot(nw[:, 0], nw[:, 1], color="#1e8449", lw=1.4, ls=(0, (3, 2)), zorder=4)
    arc = cf.polygons(geo, "seventh_arc_fl400")[0]
    ax.plot(arc[:, 0], arc[:, 1], color="#333333", lw=0.7, ls=":", zorder=4)
    lv = [hdr_level(dn, m, q) for q in (0.9, 0.5)]
    ax.contour(lon, lat, dn, levels=lv, colors=["#08306b", "#08306b"], linewidths=[0.7, 1.4], zorder=5)
    ax.plot(T5.lon, T5.lat, "x", ms=3.5, color="#d62728", mew=0.9, zorder=6)
    ax.plot(Cc.longitude, Cc.latitude, "o", ms=3.5, mfc="white", mec="#e6550d", mew=0.9, zorder=6)
    ax.set_xlim(88, 96); ax.set_ylim(-38, -32); ax.set_aspect(1 / np.cos(np.radians(35)))
    ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)")
    ax.set_title(SEARCH_SHORT[v], loc="left", fontsize=6.3)
    geo_masks = {"nw": cf.mask_of(cf.polygons(geo, "oi2024_proposed_inboard_northwest"), LON, LAT),
                 "past": cf.mask_of(cf.polygons(geo, "atsb_phase2_2014_2017"), LON, LAT)
                 | cf.mask_of(cf.polygons(geo, "oi2018_total_outline_approx"), LON, LAT)
                 | cf.mask_of(cf.polygons(geo, "oi2024_proposed_outboard_southeast"), LON, LAT)}
    def col(mp):
        mm = panel_mass(mp, v, f); dd = mm / area; ss = cf.stats(mm, area, LAT, LON, geo_masks)
        Lf = np.nan_to_num(mp[v][f"L_{f}"]); ret = float((mp[v]["post"] * Lf).sum() / (mp[v]["pre"] * Lf).sum())
        tt = mix_tension(mp, v, f)
        return [f"{area[dd >= hdr_level(dd, mm, 0.5)].sum():,.0f} km²", f"{ss['hdr90_km2']:,.0f} km²",
                f"{abs(ss['mean_lat']):.2f} S {ss['mean_lon']:.2f} E", f"{100 * (1 - ss['mass_in_past']):.1f} %",
                f"{100 * ss['mass_in_nw']:.1f} %", f"{ret:.3f}", f"{tt['ln_S']:+.2f} (p {tt['tension_p']:.2f})",
                f"{tt['mean_shift_nm']:.0f} NM"]
    lab = ["50 % region", "90 % region", "mean", "outside past searches", "in OI north-west band", "searches leave, under H",
           "tension, ln S (p)", "mean shift from flight PDF"]
    if cmp is None:
        rows = [[a, b] for a, b in zip(lab, col(maps))]
        t = side.table(cellText=rows, loc="upper left", cellLoc="left", edges="horizontal", colWidths=[0.64, 0.36], bbox=[0.0, 0.56, 1.0, 0.44])
    else:
        rows = [[a, b, c] for a, b, c in zip(lab, col(maps), col(cmp))]
        t = side.table(cellText=rows, colLabels=["strata weights", "re-weighted\n(drawn)", "fixed"], loc="upper left", cellLoc="left",
                       edges="horizontal", colWidths=[0.40, 0.30, 0.30], bbox=[0.0, 0.54, 1.0, 0.46])
    if cmp is not None:
        t.auto_set_font_size(False); t.set_fontsize(5.1)
        for (r_, c_), cell in t.get_celld().items():
            cell.PAD = 0.03
    if cmp is None:
        t.auto_set_font_size(False); t.set_fontsize(5.8)
    h = [Patch(fc="#2171b5", label="probability density under H (relative)"),
         plt.Line2D([], [], color="#08306b", lw=1.4, label="50 % region under H"), plt.Line2D([], [], color="#08306b", lw=0.7, label="90 % region under H")]
    h += hb
    h += [Patch(fc=c, alpha=a, ec=c, label=l) for _, c, a, l in SEARCH_FILL if l]
    h += [plt.Line2D([], [], color="#1e8449", lw=1.4, ls=(0, (3, 2)), label="OI north-west band (not searched; grade C)"),
          plt.Line2D([], [], color="#333333", lw=0.7, ls=":", label="7th arc, FL400"),
          plt.Line2D([], [], ls="", marker="x", color="#d62728", label="Pléiades rating-5 objects"),
          plt.Line2D([], [], ls="", marker="o", mfc="white", mec="#e6550d", label="COSMO-SkyMed radar contacts (all four)")]
    side.legend(handles=h, loc="upper left", bbox_to_anchor=(0.0, 0.52), frameon=False, fontsize=5.4)
    fig.suptitle(f"If the imaged objects are from 9M-MRO: where the debris entered the sea — {describe_option(opt, short=True)}\n"
                 f"Pléiades objects + all four COSMO-SkyMed contacts, one debris field", x=0.01, ha="left", y=1.0, fontsize=7)
    extra = [BG_TEXT[bg] + (f" {100 * frame_share(maps, v):.0f} % of it lies inside this frame." if bg else "")] if bg else []
    footnote(fig, notes + extra, width=165, y=0.02)
    fig.savefig(out / f"{stem}.png", dpi=300, bbox_inches="tight"); fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- B: one map on shaded relief + latitude strip
def gebco_subset(meta_path, lon_rng=(88, 96), lat_rng=(-38, -32), stride=6):
    m = json.loads(Path(meta_path).read_text())
    E = np.memmap(Path(meta_path).with_name(m["elevation_file"]), dtype="<i2", mode="r").reshape(m["nlat"], m["nlon"])
    j0 = int((lon_rng[0] - m["lon0"]) / m["step_deg"]); j1 = int((lon_rng[1] - m["lon0"]) / m["step_deg"])
    i0 = int((lat_rng[0] - m["lat0"]) / m["step_deg"]); i1 = int((lat_rng[1] - m["lat0"]) / m["step_deg"])
    z = np.asarray(E[i0:i1:stride, j0:j1:stride], float)
    lo = m["lon0"] + m["step_deg"] * np.arange(j0, j1, stride); la = m["lat0"] + m["step_deg"] * np.arange(i0, i1, stride)
    return lo, la, z


def style_b(maps, geo, T5, Cc, opt, notes, out, plt, gebco, stem="style-B-seabed", bg=None):
    from matplotlib.colors import LightSource
    from matplotlib.patches import Patch
    lat, lon, area = maps["base"]["lat"], maps["base"]["lon"], maps["base"]["area"]
    lo, la, z = gebco_subset(gebco)
    fig = plt.figure(figsize=(7.1, 5.2))
    # map on the left; the latitude strip is placed after the map's aspect is applied, at exactly the map's height,
    # with its own latitude labels on its right (Pete, 10 Oct 2026: the shared axis did not line up)
    ax = fig.add_axes([0.07, 0.10, 0.66, 0.80])
    ax2 = fig.add_axes([0.80, 0.10, 0.15, 0.80])
    ls = LightSource(azdeg=315, altdeg=35)
    shade = ls.hillshade(z, vert_exag=0.02, dx=1, dy=1)
    ax.imshow(shade, extent=[lo[0], lo[-1], la[0], la[-1]], origin="lower", cmap="Greys_r", vmin=0.0, vmax=1.6, alpha=0.55,
              aspect=1 / np.cos(np.radians(35)), zorder=0, interpolation="bilinear")
    cs = ax.contour(lo, la, z, levels=[-5000, -4000, -3000, -2000], colors="#9a9a9a", linewidths=0.3, zorder=1)
    ax.clabel(cs, fmt=lambda x: f"{-x/1000:.0f} km", fontsize=4.5, inline=True)
    v, f = "oi2018-2025", "P+C4"
    hb = flight_background(ax, maps, v, bg, "#00525a" if bg == "points" else "#00727a", zorder=2)
    m = panel_mass(maps, v, f); dn = m / area
    lv = [hdr_level(dn, m, q) for q in (0.99, 0.9, 0.5)]
    ax.contourf(lon, lat, dn, levels=lv + [dn.max() * 1.0001], colors=["#fee8c8", "#fdbb84", "#e34a33"], alpha=0.55, zorder=2)
    ax.contour(lon, lat, dn, levels=lv, colors=["#b30000"] * 3, linewidths=[0.4, 0.8, 1.3], zorder=3)
    for fid, col, lw, lsty in (("atsb_phase2_2014_2017", "#222222", 1.0, "-"), ("bluefin21_2014_1", "#222222", 0.9, "-"),
                               ("bluefin21_2014_2", "#222222", 0.9, "-"), ("oi2018_total_outline_approx", "#4a1486", 1.3, (0, (5, 3))),
                               ("oi2024_proposed_outboard_southeast", "#1f4e9e", 1.5, "-"), ("oi2024_proposed_inboard_northwest", "#006d2c", 1.5, (0, (3, 2)))):
        for p in cf.polygons(geo, fid):
            ax.plot(p[:, 0], p[:, 1], color=col, lw=lw, ls=lsty, zorder=4)
    arc = cf.polygons(geo, "seventh_arc_fl400")[0]
    ax.plot(arc[:, 0], arc[:, 1], color="white", lw=1.2, zorder=4); ax.plot(arc[:, 0], arc[:, 1], color="black", lw=0.5, ls=(0, (2, 2)), zorder=4)
    ax.plot(T5.lon, T5.lat, "x", ms=4, color="black", mew=1.0, zorder=5)
    ax.plot(Cc.longitude, Cc.latitude, "o", ms=4, mfc="white", mec="black", mew=0.8, zorder=5)
    ax.set_xlim(88, 96); ax.set_ylim(-38, -32)
    ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)")
    ax.set_title(f"{describe_field(f, short=True)}, one debris field\n{SEARCH_SHORT[v]}", loc="left", fontsize=6.5)
    # latitude strip: probability per degree for the four variants
    mm = panel_mass(maps, v, f)
    ax2.plot(mm.sum(axis=1) / (lat[1] - lat[0]), lat, color="#b30000", lw=1.2, label="under H")
    if bg:
        fm = maps[v]["post"] / maps[v]["post"].sum()
        ax2.plot(fm.sum(axis=1) / (lat[1] - lat[0]), lat, color="#00727a", lw=1.0, ls=(0, (4, 2)), label="without H")
    ax2.set_xlabel("Probability per\ndegree of latitude")
    ax2.set_ylim(-38, -32); ax2.set_yticks(range(-38, -31))
    ax2.yaxis.tick_right(); ax2.yaxis.set_label_position("right"); ax2.set_ylabel("Latitude (°)")
    ax2.grid(axis="y", color="#dddddd", lw=0.4)
    fig.canvas.draw()
    b = ax.get_position()                      # the map's box after its fixed aspect is applied
    ax2.set_position([b.x1 + 0.025, b.y0, 0.15, b.height])
    ax2.legend(frameon=False, fontsize=4.6, loc="upper right")
    for s in ("top", "left"):
        ax2.spines[s].set_visible(False)
    h = [Patch(fc="#e34a33", alpha=0.55, label="50 %"), Patch(fc="#fdbb84", alpha=0.55, label="90 %"), Patch(fc="#fee8c8", alpha=0.55, label="99 %"),
         plt.Line2D([], [], color="#222222", lw=1.0, label="Phase 2 + Bluefin-21"), plt.Line2D([], [], color="#4a1486", lw=1.3, ls=(0, (5, 3)), label="OI 2018"),
         plt.Line2D([], [], color="#1f4e9e", lw=1.5, label="OI 2025-26 SE band"), plt.Line2D([], [], color="#006d2c", lw=1.5, ls=(0, (3, 2)), label="OI NW band (not searched)"),
         plt.Line2D([], [], color="black", lw=0.6, ls=(0, (2, 2)), label="7th arc"),
         plt.Line2D([], [], ls="", marker="x", color="black", label="Pléiades objects"), plt.Line2D([], [], ls="", marker="o", mfc="white", mec="black", label="COSMO-SkyMed contacts")]
    ax.legend(handles=h + hb, loc="lower left", fontsize=4.8, frameon=True, framealpha=0.85, ncol=2)
    fig.suptitle(f"If the imaged objects are from 9M-MRO: where the debris entered the sea, on GEBCO 2026 relief — {describe_option(opt, short=True)}",
                 x=0.01, ha="left", y=0.99, fontsize=7)
    footnote(fig, notes + ["Relief: GEBCO 2026 15-arcsecond grid (doi:10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa), shown at 0.025 deg; "
                           "contours every 1 km depth. Right: probability per degree of latitude over 85-103 E, after all searches."]
             + ([BG_TEXT[bg] + f" {100 * frame_share(maps, v):.0f} % of it lies inside this frame."] if bg else []), width=165, y=0.0)
    fig.savefig(out / f"{stem}.png", dpi=300, bbox_inches="tight"); fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- C: arc-relative frame
class ArcFrame:
    def __init__(self, arc, lat_ref=-35.0):
        self.lon0, self.lat0 = 92.0, -35.0
        self.k = np.cos(np.radians(self.lat0))
        P = self.xy(arc[:, 0], arc[:, 1])
        self.A, self.B = P[:-1], P[1:]
        seg = self.B - self.A; self.L = np.hypot(seg[:, 0], seg[:, 1]); self.U = seg / self.L[:, None]
        self.cum = np.r_[0, np.cumsum(self.L)][:-1]
        self.s0 = 0.0
        s, _ = self.project(np.interp(lat_ref, arc[:, 1], arc[:, 0]) if arc[0, 1] < arc[-1, 1] else np.interp(lat_ref, arc[::-1, 1], arc[::-1, 0]), lat_ref)
        self.s0 = float(np.atleast_1d(s)[0]) * NM

    def xy(self, lon, lat):
        return np.stack([(np.asarray(lon) - self.lon0) * 111.195 * self.k, (np.asarray(lat) - self.lat0) * 111.195], -1)

    def project(self, lon, lat):
        p = self.xy(np.atleast_1d(lon).ravel(), np.atleast_1d(lat).ravel())
        best_d = np.full(len(p), np.inf); s = np.zeros(len(p)); d = np.zeros(len(p))
        for a, u, Lk, c in zip(self.A, self.U, self.L, self.cum):
            r = p - a; t = np.clip(r @ u, 0, Lk); q = a + t[:, None] * u
            dist = np.hypot(*(p - q).T)
            better = dist < best_d
            cross = u[0] * r[:, 1] - u[1] * r[:, 0]
            best_d[better] = dist[better]; s[better] = c + t[better]; d[better] = np.sign(cross[better]) * dist[better]
        return (s - self.s0) / NM, d / NM


def densify(p, step=0.02):
    out = [p[0]]
    for a, b in zip(p[:-1], p[1:]):
        n = max(1, int(np.hypot(*(b - a)[:2]) / step))
        out += [a + (b - a) * t for t in np.linspace(0, 1, n + 1)[1:]]
    return np.asarray(out)


def style_c(maps, geo, T5, Cc, opt, notes, out, plt):
    from matplotlib.patches import Patch
    lat, lon, area = maps["base"]["lat"], maps["base"]["lon"], maps["base"]["area"]
    arc = cf.polygons(geo, "seventh_arc_fl400")[0][:, :2]
    if arc[0, 1] > arc[-1, 1]:
        arc = arc[::-1]                      # run SW -> NE so that "left" is north-west
    fr = ArcFrame(arc)
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    S, D = fr.project(LON, LAT)
    se = np.arange(-300, 300.1, 5.0); de = np.arange(-120, 160.1, 4.0)
    fig = plt.figure(figsize=(7.1, 5.6))
    gs = fig.add_gridspec(2, 2, width_ratios=[4, 1], hspace=0.28, wspace=0.04)
    for r, (v, f) in enumerate([("base", "P+C4"), ("oi2018-2025", "P+C4")]):
        ax = fig.add_subplot(gs[r, 0]); axm = fig.add_subplot(gs[r, 1], sharey=ax)
        m = panel_mass(maps, v, f)
        H, _, _ = np.histogram2d(D.ravel(), S.ravel(), bins=[de, se], weights=m.ravel())
        Hd = H / H.sum()
        lv = [hdr_level(Hd, Hd, q) for q in (0.99, 0.9, 0.5)]
        sc, dc = 0.5 * (se[1:] + se[:-1]), 0.5 * (de[1:] + de[:-1])
        ax.contourf(sc, dc, Hd, levels=lv + [Hd.max() * 1.0001], colors=cf.BAND_FILL, zorder=0)
        ax.contour(sc, dc, Hd, levels=lv, colors="black", linewidths=cf.BAND_LW, zorder=1)
        for fid, col, lw, lsty in (("atsb_phase2_2014_2017", "#3c3c3c", 1.2, "-"), ("oi2018_total_outline_approx", "#6a3d9a", 1.4, (0, (5, 3))),
                                   ("oi2024_proposed_outboard_southeast", "#c0392b", 1.6, "-"), ("oi2024_proposed_inboard_northwest", "#1e8449", 1.6, (0, (3, 2)))):
            for p in cf.polygons(geo, fid):
                q = densify(p[:, :2])
                ps, pd_ = fr.project(q[:, 0], q[:, 1])
                ax.plot(ps, pd_, color=col, lw=lw, ls=lsty, zorder=2)
        ax.axhline(0, color="#555555", lw=0.8, ls=":", zorder=2)
        ts, td = fr.project(T5.lon.values, T5.lat.values); ax.plot(ts, td, "x", ms=4, color="#b03030", mew=0.9, zorder=3)
        cs_, cd_ = fr.project(Cc.longitude.values, Cc.latitude.values); ax.plot(cs_, cd_, "o", ms=3.5, mfc="none", mec="#d35400", mew=0.8, zorder=3)
        for latmark in (-37, -36, -35, -34, -33):
            ls_, _ = fr.project(np.interp(latmark, arc[:, 1], arc[:, 0]), latmark)
            ax.annotate(f"{abs(latmark)}°S", (ls_[0], -118), fontsize=5, ha="center", color="#555555")
        ax.set_xlim(-250, 250); ax.set_ylim(-120, 150)
        ax.set_ylabel("NM north-west of the 7th arc\n(negative = south-east, outside)")
        ax.set_title(f"{describe_field(f, short=True)}, one debris field — {SEARCH_SHORT[v]}", loc="left", fontsize=6.5)
        if r == 1:
            ax.set_xlabel("NM along the 7th arc from its 35°S crossing (positive = north-east)")
        pdm = Hd.sum(axis=1) / (de[1] - de[0])
        axm.fill_betweenx(dc, 0, pdm, color="#c4c4c4"); axm.plot(pdm, dc, color="black", lw=0.8)
        axm.axhline(0, color="#555555", lw=0.8, ls=":")
        axm.tick_params(labelleft=False); axm.set_xlabel("per NM" if r == 1 else "")
        for s_ in ("top", "right"):
            axm.spines[s_].set_visible(False)
        inside = Hd[dc > 0].sum()
        axm.text(0.95, 0.97, f"{100 * inside:.0f} % NW\nof the arc", transform=axm.transAxes, ha="right", va="top", fontsize=5.5)
    h = [Patch(fc=cf.BAND_FILL[2], ec="black", lw=cf.BAND_LW[2], label="50 %"), Patch(fc=cf.BAND_FILL[1], ec="black", lw=cf.BAND_LW[1], label="90 %"),
         Patch(fc=cf.BAND_FILL[0], ec="black", lw=cf.BAND_LW[0], label="99 %"),
         plt.Line2D([], [], color="#3c3c3c", lw=1.2, label="Phase 2 + Bluefin-21"), plt.Line2D([], [], color="#6a3d9a", lw=1.4, ls=(0, (5, 3)), label="OI 2018 (C)"),
         plt.Line2D([], [], color="#c0392b", lw=1.6, label="OI 2025-26 SE (C)"), plt.Line2D([], [], color="#1e8449", lw=1.6, ls=(0, (3, 2)), label="OI NW band, not searched (C)"),
         plt.Line2D([], [], ls="", marker="x", color="#b03030", label="Pléiades"), plt.Line2D([], [], ls="", marker="o", mfc="none", mec="#d35400", label="COSMO F1-F4")]
    fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.08, -0.04), ncol=5, frameon=False, fontsize=5.3)
    fig.suptitle(f"C. Relative to the 7th arc: {describe_option(opt, short=True)}", x=0.01, ha="left", y=0.995, fontsize=7)
    footnote(fig, notes + ["Frame: each 0.05 deg cell projected to its nearest point on the 7th-arc FL400 polyline (local tangent plane at "
                           "35 S 92 E; distortion < 1 % over the frame); bins 5 NM along x 4 NM across. Latitude ticks mark where the arc crosses them."],
             width=165, y=-0.06)
    fig.savefig(out / "style-C-arc-frame.png", dpi=300, bbox_inches="tight"); fig.savefig(out / "style-C-arc-frame.pdf", bbox_inches="tight")
    plt.close(fig)


def standard(root, impacts_root, geom, gebco, out, plt, pfam=None, options=(), labels="", bg="points", suffix="", fam_json=None):
    # Pete, 10 Oct 2026: faint points of the impact PDF without H are the default background ("feint points was best")
    """The standard close-ups (Pete, 10 Oct 2026): colour (A) and seabed (B) for every option, all four COSMO-SkyMed
    contacts only. Writes closeup-<option>-colour.{png,pdf}, closeup-<option>-seabed.{png,pdf} and closeup-stats.csv."""
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    geo = json.loads((Path(geom) / "search_footprints.geojson").read_text())
    M = HERE.parent
    T5 = pd.read_csv(M / "data/targets-3km.csv").query("arm == 'rating5'"); Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    prov = Path(impacts_root) / next(iter(pfam)) if pfam else Path(impacts_root)
    src = run_provenance(prov) or f"Source: {impacts_root}"
    if pfam:
        src = src.replace(f"impacts {prov.name}", f"impacts {Path(impacts_root).name} (strata {', '.join(pfam)}; provenance read from {prov.name})")
    rows = []
    for opt in options:
        # ruling C: draw the 00:19-re-weighted mixture; the fixed-weight mixture is shown beside it
        pfam_rw = reweighted_pfam(fam_json, opt) if pfam else None
        fixed = {v: load_mixture(root, opt, v, pfam) for v in ("base", "oi2018-2025")}
        maps = {v: load_mixture(root, opt, v, pfam_rw) for v in ("base", "oi2018-2025")} if pfam_rw else fixed
        notes = notes_for(opt, src, pfam, labels, pfam_rw, fam_json)
        safe = opt.replace("/", "-")
        # Pete, 10 Oct 2026: only the after-all-searches panel (old panel b); panel a added little
        colour_single(maps, geo, T5, Cc, opt, notes, out, plt, stem=f"closeup-{safe}-colour{suffix}", bg=bg,
                      cmp=fixed if pfam_rw else None)
        nb = notes
        if pfam_rw:
            T_ = []
            for nm, mp in (("re-weighted", maps), ("fixed", fixed)):
                mm = panel_mass(mp, "oi2018-2025", "P+C4"); a_ = mp["base"]["area"]
                LA, LO = np.meshgrid(mp["base"]["lat"], mp["base"]["lon"], indexing="ij")
                ss = cf.stats(mm, a_, LA, LO, {})
                T_.append(f"{nm} {ss['hdr90_km2']:,.0f} km², mean {abs(ss['mean_lat']):.2f} S {ss['mean_lon']:.2f} E")
            nb = notes + ["Strata weights, after all searches, 90 % region under H: " + "; ".join(T_) + " (drawn: re-weighted)."]
        tt = mix_tension(maps, "oi2018-2025")
        nb = nb + [f"Tension of H against the flight PDF, after all searches (the module's measure; reported with the conditional): ln S "
                   f"{tt['ln_S']:+.2f}, p {tt['tension_p']:.2f} (Handley-Lemos), mean shift {tt['mean_shift_nm']:.0f} NM; flight PDF mass "
                   f"inside the 90 % region under H {100 * tt['uncond_in_cond_hdr90']:.0f} %."]
        style_b(maps, geo, T5, Cc, opt, nb, out, plt, gebco, stem=f"closeup-{safe}-seabed{suffix}", bg=bg)
        lat, lon, area = maps["base"]["lat"], maps["base"]["lon"], maps["base"]["area"]
        LAT, LON = np.meshgrid(lat, lon, indexing="ij")
        masks = {"oi_northwest_band": cf.mask_of(cf.polygons(geo, "oi2024_proposed_inboard_northwest"), LON, LAT),
                 "past": cf.mask_of(cf.polygons(geo, "atsb_phase2_2014_2017"), LON, LAT)
                 | cf.mask_of(cf.polygons(geo, "oi2018_total_outline_approx"), LON, LAT)
                 | cf.mask_of(cf.polygons(geo, "oi2024_proposed_outboard_southeast"), LON, LAT)}
        for wname, MP in ((("reweighted-0019", maps), ("fixed", fixed)) if pfam_rw else (("fixed" if pfam else "single", maps),)):
          for v in ("base", "oi2018-2025"):
            m = panel_mass(MP, v, "P+C4"); dn = m / area; s_ = cf.stats(m, area, LAT, LON, masks)
            Lf = np.nan_to_num(MP[v]["L_P+C4"])
            rows.append(dict(option=opt, strata_weights=wname, option_name=describe_option(opt, short=True), option_described=describe_option(opt),
                             field="Pléiades + all four COSMO-SkyMed contacts, one debris field", search=SEARCH_SHORT[v],
                             hdr50_km2=round(float(area[dn >= hdr_level(dn, m, 0.5)].sum())), hdr90_km2=round(s_["hdr90_km2"]),
                             mean_lat=round(s_["mean_lat"], 3), mean_lon=round(s_["mean_lon"], 3),
                             share_in_nw_band=round(s_["mass_in_oi_northwest_band"], 4), share_outside_past_searches=round(1 - s_["mass_in_past"], 4),
                             search_retains_under_H=round(float((MP[v]["post"] * Lf).sum() / (MP[v]["pre"] * Lf).sum()), 3),
                             search_retains_flight_only=round(float(MP[v]["post"].sum() / MP[v]["pre"].sum()), 3),
                             **{k_: round(float(t_[k_]), 4) for t_ in [mix_tension(MP, v)] for k_ in
                                ("ln_S", "tension_p", "d_shared", "mean_shift_nm", "uncond_in_cond_hdr90", "cond_in_uncond_hdr90")}))
    T = pd.DataFrame(rows); T.to_csv(out / f"closeup-stats{suffix}.csv", index=False)
    return T


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for a_ in ("root", "impacts_root", "geom", "gebco", "out", "option"):
        ap.add_argument(a_)
    ap.add_argument("--pfamily", default=""); ap.add_argument("--labels", default="")
    a = ap.parse_args()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update({"font.size": 6, "axes.titlesize": 6.5, "axes.labelsize": 6, "xtick.labelsize": 5.5, "ytick.labelsize": 5.5})
    pf = {k: float(v) for k, v in (x.split("=") for x in a.pfamily.split(",") if x)} or None
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    maps = {v: load_mixture(a.root, a.option, v, pf) for v in ("base", "oi2018-2025")}
    geo = json.loads((Path(a.geom) / "search_footprints.geojson").read_text())
    M = HERE.parent
    T5 = pd.read_csv(M / "data/targets-3km.csv").query("arm == 'rating5'"); Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    prov = Path(a.impacts_root) / next(iter(pf)) if pf else Path(a.impacts_root)
    src = run_provenance(prov) or f"Source: {a.impacts_root}"
    if pf:
        src = src.replace(f"impacts {prov.name}", f"impacts {Path(a.impacts_root).name} (strata {', '.join(pf)}; provenance read from {prov.name})")
    notes = notes_for(a.option, src, pf, a.labels)
    style_a(maps, geo, T5, Cc, a.option, notes, out, plt)
    style_b(maps, geo, T5, Cc, a.option, notes, out, plt, a.gebco)
    style_c(maps, geo, T5, Cc, a.option, notes, out, plt)
    print("ok")
