"""Seabed wreckage-field PDF under several impact PDFs, in the project map convention.

Standard-set renderer (10 Oct 2026, rulings ~16:30 and ~19:10 UTC): plain option names, STE100 title, two-version
footnote (FOOT_STE, FOOT_TECH) in at most the bottom quarter, grid sized to the impacts (no mass dropped off the map),
STAMP for options below ESS_MIN. Inputs (set before exec): KEYS, TITLES_W, TITLE, SUBTITLE, FOOT_STE, FOOT_TECH, STAMP, GRID_EXTENT, full (key -> list of per-seed (lat, lon, p)),
SRC (key -> (impacts table, input rows, draw indices, elements from settling::tests::wreckage_field)), ESS (key -> pooled
impact ESS), ESS_MIN (below it a panel is stamped NOT ESTIMABLE), ARCS_JSON (core run.json with reference_arcs), OUTSTEM, SMOOTH.

Wreckage density: each resampled impact carries one settling draw; the draw's SETTLED elements share the impact's
probability in proportion to element mass (multiplicity x piece mass). Impact density for the faint reference
contours: every impact at its option-posterior weight, seeds pooled with equal weight. Both on a 0.02 deg grid,
Gaussian-smoothed at SMOOTH deg; HPD levels from the smoothed density (end of flight's hpd_levels).
"""
import numpy as np, matplotlib.pyplot as plt, json, pathlib
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MultipleLocator
from scipy.ndimage import gaussian_filter
from displacement_greyscale import hpd_levels, LEVELS, SHADES, EDGE, EDGE_W

GRID = 0.02
R_AUTH = 6371.0072
REF = dict(color="#d9822b", lw=0.6, alpha=0.9)
ARCSTY = {"m0011": dict(lw=1.2, color="#b16286", label="6th arc, 00:11 UTC"),
          "m0019a": dict(lw=1.0, color="#4a6fa5", ls="--", label="7th arc, 00:19 UTC")}

arcs = {x["epoch"]: np.asarray(x["lat_lon"], float) for x in json.loads(pathlib.Path(ARCS_JSON).read_text())["reference_arcs"]}
le = np.arange(GRID_EXTENT[2], GRID_EXTENT[3] + GRID / 2, GRID); oe = np.arange(GRID_EXTENT[0], GRID_EXTENT[1] + GRID / 2, GRID)
lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1])
cell_km2 = (R_AUTH ** 2) * np.radians(GRID) * np.abs(np.sin(np.radians(le[1:])) - np.sin(np.radians(le[:-1])))[:, None] * np.ones(len(oc))[None, :]


def smooth(H):
    d = gaussian_filter(H, SMOOTH / GRID, mode="constant"); return d / d.sum()


def hpd_area(d, lv):
    return [float(cell_km2[d >= l].sum()) for l in lv]  # 99, 90, 50


def seabed_density(T, rows, draws, el):
    """Mass-weighted seabed density of the settled elements of each (input row, draw), each resampled impact equal weight."""
    st = el[:, 4] == 0
    key = el[st, 0].astype(np.int64) * 1048576 + el[st, 1].astype(np.int64)
    o = np.argsort(key, kind="stable"); key, lat, lon, mass = key[o], el[st, 5][o], el[st, 6][o], el[st, 7][o]
    uk, start = np.unique(key, return_index=True); stop = np.r_[start[1:], len(key)]
    tot = np.add.reduceat(mass, start); share = mass / np.repeat(tot, stop - start)
    want = rows.astype(np.int64) * 1048576 + draws.astype(np.int64)
    pos = np.minimum(np.searchsorted(uk, want), len(uk) - 1); ok = uk[pos] == want  # False: outside the module's domain
    n_el = (stop - start)[pos[ok]]
    idx = np.concatenate([np.arange(a, b) for a, b in zip(start[pos[ok]], stop[pos[ok]])])
    w = share[idx] / len(want)
    Hw = np.histogram2d(lat[idx], lon[idx], bins=[le, oe], weights=w)[0]
    imp = T[rows, 1:3]; Hs = np.histogram2d(imp[:, 0], imp[:, 1], bins=[le, oe])[0]
    il, io = np.repeat(imp[ok, 0], n_el), np.repeat(imp[ok, 1], n_el)
    off = np.hypot((lat[idx] - il) * 111.2, (lon[idx] - io) * 111.2 * np.cos(np.radians(il)))
    oo = np.argsort(off); c = np.cumsum(w[oo]) / w.sum()
    ka = el[:, 0].astype(np.int64) * 1048576 + np.nan_to_num(el[:, 1], nan=-1).astype(np.int64)
    inp = np.isin(ka, want); fa = el[inp, 4]; ma = el[inp, 7]
    afloat = float(ma[fa == 1].sum() / ma[fa >= 0].sum()) if (fa >= 0).any() else float("nan")
    return Hw, Hs, {"afloat_mass_share": afloat, "resampled_impacts": int(len(want)), "distinct_impacts": int(len(np.unique(rows))), "not_computed_impacts": int((~ok).sum()),
                    "not_computed_impact_positions": imp[~ok].tolist(),
                    "settled_offset_km_p50_p90_p99_mass_weighted": [float(off[oo][np.searchsorted(c, q)]) for q in (0.5, 0.9, 0.99)],
                    "mass_share_offset_gt_5km": float(w[off > 5].sum() / w.sum())}


dens, stats = {}, {}
for k in KEYS:
    T, rows, draws, el = SRC[k]
    if len(rows) == 0 or not full[k] or len(full[k][0][2]) == 0:   # no posterior mass in this panel (e.g. a family absent under an option)
        z_ = np.zeros((len(le) - 1, len(oe) - 1)); dens[k] = None
        stats[k] = {"ess_pooled": ESS[k], "estimable": False, "resampled_impacts": 0, "distinct_impacts": 0, "not_computed_impacts": 0,
                    "not_computed_impact_positions": [], "settled_offset_km_p50_p90_p99_mass_weighted": None, "mass_share_offset_gt_5km": None,
                    "area_km2_99_90_50": {"impact_full_weights": [0, 0, 0], "impact_resampled": [0, 0, 0], "wreckage_field": [0, 0, 0]}}
        continue
    Hi = sum(np.histogram2d(la, lo, bins=[le, oe], weights=p)[0] for la, lo, p in full[k])  # full[k] weights already sum to 1 over strata and seeds
    off_grid = 1.0 - float(Hi.sum()); assert abs(off_grid) < 1e-5, f"{k}: {off_grid:.3g} of impact mass off the map grid"
    Hw, Hs, st = seabed_density(T, rows, draws, el)
    dI, dW, dS = smooth(Hi), smooth(Hw), smooth(Hs)
    lI, lW, lS = hpd_levels(dI, LEVELS), hpd_levels(dW, LEVELS), hpd_levels(dS, LEVELS)
    dens[k] = (dI, lI, dW, lW)
    stats[k] = {"ess_pooled": ESS[k], "estimable": bool(ESS[k] >= ESS_MIN), **st,
                "area_km2_99_90_50": {"impact_full_weights": hpd_area(dI, lI), "impact_resampled": hpd_area(dS, lS), "wreckage_field": hpd_area(dW, lW)}}

# common frame: union of 99 % regions
inside = np.zeros_like(next(v for v in dens.values() if v is not None)[0], bool)
for k in KEYS:
    if dens[k] is None: continue
    inside |= dens[k][2] >= dens[k][3][0]; inside |= dens[k][0] >= dens[k][1][0]
r, cc = np.where(inside); mid_lat = 0.5 * (lc[r.min()] + lc[r.max()]); mid_lon = 0.5 * (oc[cc.min()] + oc[cc.max()])
half_lat = 0.55 * (lc[r.max()] - lc[r.min()]); half_lon = 0.55 * (oc[cc.max()] - oc[cc.min()])
half_lat = max(half_lat, half_lon * np.cos(np.radians(mid_lat))); half_lon = half_lat / np.cos(np.radians(mid_lat))
fmt = FuncFormatter(lambda v, _: f"{abs(v):.0f}°{'S' if v < 0 else 'N' if v > 0 else ''}")
n = len(KEYS); ncol = globals().get("NCOL") or (2 if n == 4 else 3 if n in (5, 6) else n); nrow = int(np.ceil(n / ncol))
FIG_H = 3.55 * nrow + (1.75 if n < nrow * ncol else 2.7)
fig, axs = plt.subplots(nrow, ncol, figsize=(3.3 * ncol, FIG_H), squeeze=False, sharex=True, sharey=True,
                        gridspec_kw=dict(wspace=0.06, hspace=0.20))
fmt_ess = lambda e: f"{e / 1e6:.1f} M" if e >= 1e6 else f"{e:,.0f}"
for j, k in enumerate(KEYS):
    ax = axs.flat[j]
    if dens[k] is None:
        ax.set_title(TITLES_W[k], fontsize=7.3, loc="left"); ax.text(0.5, 0.5, "no samples in this family", transform=ax.transAxes, ha="center", fontsize=7, color="#777777")
        ax.set_xticks([]); ax.set_yticks([]); continue
    dI, lI, dW, lW = dens[k]
    step = 1.0 if 2 * half_lat < 6 else 2.0 if 2 * half_lat < 14 else 5.0
    ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.set_axisbelow(True); ax.grid(True, color="#e3e3e3", lw=0.6)
    ax.contourf(oc, lc, dW, levels=lW + [dW.max()], colors=SHADES, antialiased=True)
    ax.contour(oc, lc, dW, levels=lW, colors=EDGE, linewidths=EDGE_W)
    ax.contour(oc, lc, dI, levels=lI, colors=REF["color"], linewidths=REF["lw"], alpha=REF["alpha"], linestyles="--")
    for e, sty in ARCSTY.items():
        if e in arcs: ax.plot(arcs[e][:, 1], arcs[e][:, 0], **sty)
    ax.set_xlim(mid_lon - half_lon, mid_lon + half_lon); ax.set_ylim(mid_lat - half_lat, mid_lat + half_lat)
    ax.set_aspect(1 / np.cos(np.radians(mid_lat))); ax.yaxis.set_major_formatter(fmt); ax.tick_params(labelsize=6.5)
    ax.set_title(TITLES_W[k], fontsize=7.3, loc="left")
    a = stats[k]["area_km2_99_90_50"]
    ax.text(0.97, 0.03, f"90 % area (thousand km²): seabed {a['wreckage_field'][1]/1e3:,.0f}; impacts {a['impact_resampled'][1]/1e3:,.0f}\n"
            f"{stats[k]['resampled_impacts']:,} draws, {stats[k]['distinct_impacts']:,} impacts; ESS {fmt_ess(ESS[k])}"
            + (f"\n{globals().get('PANEL_NOTE', {}).get(k)}" if globals().get('PANEL_NOTE', {}).get(k) else ""),
            transform=ax.transAxes, fontsize=5.8, color="#333333", ha="right", va="bottom",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1.5))
    if not stats[k]["estimable"]:
        ax.text(0.36, 0.82, f"{STAMP}\nimpact ESS {ESS[k]:,.0f} (< {ESS_MIN:,})", transform=ax.transAxes, ha="center", va="center",
                fontsize=7.5, color="#a00000", alpha=0.85, rotation=0, fontweight="bold")
    if j % ncol == 0: ax.set_ylabel("latitude", fontsize=7)
    ax.tick_params(labelbottom=True); ax.set_xlabel("longitude (°E)", fontsize=7)
for j in range(n, nrow * ncol): axs.flat[j].set_visible(False)
hs = [Patch(facecolor=s, edgecolor=EDGE, lw=0.6, label=f"wreckage on the seabed, {int(f * 100)} % of probability") for s, f in zip(SHADES[::-1], LEVELS[::-1])]
hs += [Line2D([], [], color=REF["color"], lw=0.8, ls="--", label="impact on the water, 50/90/99 % of probability")]
hs += [Line2D([], [], **sty) for sty in ARCSTY.values()]
# layout: title and subtitle, panels, legend, then the two footnotes in at most the bottom 25 % of the image
foot_in = (1.75 if n < nrow * ncol else 2.7) / FIG_H
fig.subplots_adjust(top=1 - 0.75 / FIG_H, bottom=foot_in, left=0.07, right=0.98)
if n < nrow * ncol:   # legend in the empty panel slot
    bb = axs.flat[n].get_position(); fig.legend(handles=hs, loc="center", ncol=1, frameon=False, fontsize=7, bbox_to_anchor=(bb.x0 + bb.width / 2, bb.y0 + bb.height / 2))
else:
    fig.legend(handles=hs, loc="upper center", ncol=3, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, foot_in - 0.50 / FIG_H))
fig.text(0.07, 1 - 0.18 / FIG_H, TITLE, fontsize=9.5, ha="left", va="top")
fig.text(0.07, 1 - 0.42 / FIG_H, SUBTITLE, fontsize=7.5, ha="left", va="top", color="#333333")
fig.canvas.draw(); rr = fig.canvas.get_renderer()
leg0 = min(min(a.get_window_extent(rr).y0 for a in fig.legends) / fig.bbox.height, foot_in - 0.42 / FIG_H, 0.25)
t1 = fig.text(0.07, leg0 - 0.012, "Summary (STE): " + FOOT_STE, fontsize=6.2, color="#333333", ha="left", va="top", wrap=True)
fig.canvas.draw(); y1 = t1.get_window_extent(rr).y0 / fig.bbox.height
t2 = fig.text(0.07, y1 - 0.006, "Technical: " + FOOT_TECH, fontsize=5.6, color="#555555", ha="left", va="top", wrap=True)
fig.canvas.draw()
leg_bot = min(a.get_window_extent(rr).y0 for a in fig.legends) / fig.bbox.height
foot_top = t1.get_window_extent(rr).y1 / fig.bbox.height; foot_bot = t2.get_window_extent(rr).y0 / fig.bbox.height
assert foot_top <= 0.25 and foot_bot >= 0.0 and (foot_top < leg_bot or n < nrow * ncol), f"footnotes span {foot_bot:.3f}-{foot_top:.3f}; legend bottom {leg_bot:.3f}"
fig.savefig(OUTSTEM + ".pdf"); fig.savefig(OUTSTEM + ".png", dpi=220)
pathlib.Path(OUTSTEM + ".json").write_text(json.dumps({"options": stats, "smooth_deg": SMOOTH, "grid_deg": GRID, "ess_min": ESS_MIN,
    "afloat_mass_share_of_element_file": {k: float(SRC[k][3][SRC[k][3][:, 4] == 1, 7].sum() / SRC[k][3][SRC[k][3][:, 4] >= 0, 7].sum()) for k in KEYS}}, indent=1))
