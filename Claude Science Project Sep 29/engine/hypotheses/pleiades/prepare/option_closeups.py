"""Close-ups of the conditional PDF under H after the seabed search, one figure per 00:19 option (Pete, 10 Oct 2026:
"for the plots I need the close ups every time"). Strata are mixed by P(family) when the impacts come in strata.

    python option_closeups.py <branch root> <impacts root> <geometry dir> <out dir> [--pfamily a=0.69,b=0.15,...]
                              [--options none+alive,r600/no-offset,...] [--labels "..."]

<branch root>   holds branch-<option>-<variant>/branch-maps.npz from branch_eof289.py (variants base, oi2018-2025),
                either directly (one impact set) or under <stratum>/ (one per stratum, mixed with --pfamily).
<impacts root>  end of flight's impacts (run.json provenance for the footnote); with strata, <impacts root>/<stratum>.

Mixture (adopted from the architecture stand-in's combine_mixture.py, 10 Oct ~11:45 UTC, after review):
  pre_mix = sum_f P(f) pre_f,  post_mix = sum_f P(f) post_f,
where pre_f is stratum f's flight posterior on the grid, normalised to one, and post_f the same after the search,
normalised with the SAME constant (it sums to that stratum's search evidence Z_f). The search therefore re-weights the
strata by Z_f automatically. The 00:19 data do not: P(family) is core's, fixed before any 00:19 option is scored, as
in end of flight's and searched areas' mixtures (declared in every footnote). The conditional under H is then
pre/post_mix x L(field), L being identical in every stratum (one exported surface).

Panels per option: (a) Pléiades + COSMO F1-F3 and (b) Pléiades + COSMO F1-F4 after Phase 2 + Bluefin-21;
(c), (d) the same after + OI 2018 + 2025-26 south-east band. Shading: light 50/90/99 % HDR, black contours of
decreasing weight, heavier search outlines (Pete, 9 Oct).
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
from describe import describe_option, describe_field, SEARCH, SEARCH_SHORT  # noqa: E402

VARIANTS = ("base", "oi2018-2025")
PANELS = [("base", "P+C3"), ("base", "P+C4"), ("oi2018-2025", "P+C3"), ("oi2018-2025", "P+C4")]


def load_mixture(root, opt, variant, pfam):
    safe = opt.replace("/", "-")
    if not pfam:
        return dict(np.load(Path(root) / f"branch-{safe}-{variant}" / "branch-maps.npz"))
    out = None
    for s, pi in pfam.items():
        Z = dict(np.load(Path(root) / s / f"branch-{safe}-{variant}" / "branch-maps.npz"))
        if out is None:
            out = {k: v for k, v in Z.items()}
            out["pre"], out["post"] = pi * Z["pre"], pi * Z["post"]
        else:
            for k in ("L_P", "L_C3", "L_C4", "L_P+C3", "L_P+C4"):
                a, b = np.nan_to_num(out[k]), np.nan_to_num(Z[k])
                assert np.allclose(a, b, rtol=1e-6, atol=0), f"{k} differs between strata"
            out["pre"] = out["pre"] + pi * Z["pre"]
            out["post"] = out["post"] + pi * Z["post"]
    return out


def make(root, impacts_root, geom_dir, out, plt, pfam=None, options=None, labels="", panel_letter=None):
    root, out = Path(root), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    M = HERE.parent
    geo = json.loads((Path(geom_dir) / "search_footprints.geojson").read_text())
    T5 = pd.read_csv(M / "data/targets-3km.csv").query("arm == 'rating5'")
    Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    prov_root = Path(impacts_root) / next(iter(pfam)) if pfam else Path(impacts_root)
    src = run_provenance(prov_root) or f"Source: {impacts_root}"
    if pfam:
        src = src.replace(f"impacts {prov_root.name}", f"impacts {Path(impacts_root).name} (strata {', '.join(pfam)}; provenance read from {prov_root.name})")
    rows = []
    for opt in options:
        maps = {v: load_mixture(root, opt, v, pfam) for v in VARIANTS}
        lat, lon, area = maps["base"]["lat"], maps["base"]["lon"], maps["base"]["area"]
        LAT, LON = np.meshgrid(lat, lon, indexing="ij")
        masks = {"phase2": cf.mask_of(cf.polygons(geo, "atsb_phase2_2014_2017"), LON, LAT),
                 "oi2018_outline": cf.mask_of(cf.polygons(geo, "oi2018_total_outline_approx"), LON, LAT),
                 "oi_southeast_band": cf.mask_of(cf.polygons(geo, "oi2024_proposed_outboard_southeast"), LON, LAT),
                 "oi_northwest_band": cf.mask_of(cf.polygons(geo, "oi2024_proposed_inboard_northwest"), LON, LAT)}
        masks["any_past_envelope"] = masks["phase2"] | masks["oi2018_outline"] | masks["oi_southeast_band"]
        fig, axs = plt.subplots(2, 2, figsize=(7.1, 6.4), sharex=True, sharey=True, gridspec_kw=dict(wspace=0.05, hspace=0.16))
        for ax, (v, f) in zip(axs.ravel(), PANELS):
            m = maps[v]["post"] * np.nan_to_num(maps[v][f"L_{f}"])
            m = m / m.sum(); dn = m / area
            cf.hdr_bands(ax, lon, lat, dn, m)
            cf.draw_outlines(ax, geo)
            ax.plot(T5.lon, T5.lat, "x", ms=3, color="#b03030", mew=0.7)
            n = 3 if f == "P+C3" else 4
            ax.plot(Cc.longitude[:n], Cc.latitude[:n], "o", ms=3, mfc="none", mec="#d35400", mew=0.7)
            s = cf.stats(m, area, LAT, LON, masks)
            s50 = float(area[dn >= hdr_level(dn, m, 0.5)].sum())
            mo = maps[v]["post"] / maps[v]["post"].sum()
            pre = maps[v]["pre"]
            ret_h = float((maps[v]["post"] * np.nan_to_num(maps[v][f"L_{f}"])).sum() / (pre * np.nan_to_num(maps[v][f"L_{f}"])).sum())
            rows.append(dict(option=opt, option_described=describe_option(opt), field=f, field_described=describe_field(f),
                             search=SEARCH[v], hdr50_km2=round(s50), hdr90_km2=round(s["hdr90_km2"]),
                             mean_lat=round(s["mean_lat"], 3), mean_lon=round(s["mean_lon"], 3),
                             share_in_nw_band=round(s["mass_in_oi_northwest_band"], 4),
                             share_outside_past_searches=round(1 - s["mass_in_any_past_envelope"], 4),
                             search_retains_under_H=round(ret_h, 3), search_retains_unconditional=round(float(maps[v]["post"].sum() / pre.sum()), 3)))
            ax.text(0.02, 0.03, f"50 % area {s50:,.0f} km²; 90 % area {s['hdr90_km2']:,.0f} km²\n"
                    f"in NW band {100 * s['mass_in_oi_northwest_band']:.1f} %; outside past searches {100 * (1 - s['mass_in_any_past_envelope']):.1f} %",
                    transform=ax.transAxes, fontsize=5.5, va="bottom", bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.0))
            ax.set_title(f"{describe_field(f, short=True)}, one debris field\n{SEARCH_SHORT[v]}", loc="left", fontsize=6)
            ax.set_xlim(88, 96); ax.set_ylim(-38, -32)
        for ax in axs[:, 0]:
            ax.set_ylabel("Latitude (°)")
        for ax in axs[1, :]:
            ax.set_xlabel("Longitude (°E)")
        if panel_letter:
            for a, l in zip(axs.ravel(), "abcd"):
                panel_letter(a, l)
        fig.suptitle(f"Where the debris would have entered the sea if the imaged objects are from 9M-MRO — "
                     f"{describe_option(opt, short=True)}", x=0.01, ha="left", y=0.995, fontsize=7)
        from matplotlib.patches import Patch
        h = [Patch(fc=cf.BAND_FILL[2], ec="black", lw=cf.BAND_LW[2], label="50 % of probability"),
             Patch(fc=cf.BAND_FILL[1], ec="black", lw=cf.BAND_LW[1], label="90 % of probability"),
             Patch(fc=cf.BAND_FILL[0], ec="black", lw=cf.BAND_LW[0], label="99 % of probability"),
             plt.Line2D([], [], color="#3c3c3c", lw=1.3, label="ATSB Phase 2 2014-17 and Bluefin-21 (official footprints)"),
             plt.Line2D([], [], color="#6a3d9a", lw=1.5, ls=(0, (5, 3)), label="Ocean Infinity 2018 outline (community tracing, grade C)"),
             plt.Line2D([], [], color="#c0392b", lw=1.7, label="OI 2025-26 south-east band (likely searched; grade C)"),
             plt.Line2D([], [], color="#1e8449", lw=1.7, ls=(0, (3, 2)), label="OI inferred remaining north-west band (not searched; grade C)"),
             plt.Line2D([], [], color="#777777", lw=0.8, ls=":", label="7th arc, FL400 (official)"),
             plt.Line2D([], [], ls="", marker="x", color="#b03030", label="Pléiades rating-5 objects (23 Mar)"),
             plt.Line2D([], [], ls="", marker="o", mfc="none", mec="#d35400", label="COSMO-SkyMed radar contacts F1-F3 (F4 in b, d)")]
        fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.06, -0.07), ncol=2, frameon=False, fontsize=5.5)
        mix = (f"Strata mixed by core's P(family), held fixed ({', '.join(f'{k} {v:.4f}' for k, v in pfam.items())}); the search re-weights "
               f"strata by their own evidence, the 00:19 data do not.") if pfam else "Single impact set (no strata)."
        notes = [src,
                 "What was run: " + describe_option(opt) + ". " + mix,
                 "Labels: " + (labels or "none") + ".",
                 "Search: the searched-areas module's own per-impact likelihood (point target, undetectable probability rho = 0.05, shared between "
                 "campaigns). Phase 2 (q 0.945) and Bluefin-21 (q 0.9) official; OI 2018 (q 0.9, coverage 0.889) and OI 2025-26 south-east band "
                 "(q 0.9, coverage 0.7808) are inferred community tracings, grade C. The north-west band is drawn only and is never negative evidence.",
                 "Under H: the 12 rating-5 Pléiades objects merged into 6 clusters (3 km), equal weights; COSMO-SkyMed contacts equally weighted, dawn "
                 "20 Mar and dusk 21 Mar passes equally weighted (source, time and footprint unverified). 'One debris field' = both sets' likelihoods "
                 "multiplied, per ocean model. Ocean models GLORYS12 + ERA5 and GlobCurrent daily + ERA5, equal weight; measured transport error "
                 "(drifter replay, ~100-110 km per component at 15 d); windage 0-5 %; Pléiades and COSMO errors treated as independent (rho = 0; "
                 "0.5-0.8 widened the 90 % area 28-38 % on reference-289).",
                 "Every PDF is conditional on H (the objects are debris from 9M-MRO); no Bayes factor or P(H | data). Shading: highest-density "
                 "regions holding 50/90/99 % of each panel's PDF. Percentages are of the panel's PDF within 85-103 E, 43-25 S."]
        footnote(fig, notes, width=150, y=-0.11)
        safe = opt.replace("/", "-")
        fig.savefig(out / f"closeup-{safe}.png", dpi=300, bbox_inches="tight")
        fig.savefig(out / f"closeup-{safe}.pdf", bbox_inches="tight")
        plt.close(fig)
    T = pd.DataFrame(rows)
    T.to_csv(out / "closeup-stats-by-option.csv", index=False)
    return T


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root"); ap.add_argument("impacts_root"); ap.add_argument("geom"); ap.add_argument("out")
    ap.add_argument("--pfamily", default=""); ap.add_argument("--options", default="none+alive,none,r600/no-offset")
    ap.add_argument("--labels", default="")
    a = ap.parse_args()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update({"font.size": 6, "axes.titlesize": 6.5, "axes.labelsize": 6, "xtick.labelsize": 5.5, "ytick.labelsize": 5.5})
    pf = {k: float(v) for k, v in (x.split("=") for x in a.pfamily.split(",") if x)} or None
    print(make(a.root, a.impacts_root, a.geom, a.out, plt, pf, a.options.split(","), a.labels).to_string(index=False))
