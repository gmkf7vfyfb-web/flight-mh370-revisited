"""Seabed wreckage-field PDF under several impact PDFs, in the project map convention.

Inputs (set before exec): KEYS, TITLES_W, TITLE, SUB (footnote), full (key -> list of per-seed (lat, lon, p)),
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
le = np.arange(-46.0, -20.0 + GRID / 2, GRID); oe = np.arange(80.0, 112.0 + GRID / 2, GRID)
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
    return Hw, Hs, {"resampled_impacts": int(len(want)), "distinct_impacts": int(len(np.unique(rows))), "not_computed_impacts": int((~ok).sum()),
                    "not_computed_impact_positions": imp[~ok].tolist(),
                    "settled_offset_km_p50_p90_p99_mass_weighted": [float(off[oo][np.searchsorted(c, q)]) for q in (0.5, 0.9, 0.99)],
                    "mass_share_offset_gt_5km": float(w[off > 5].sum() / w.sum())}


dens, stats = {}, {}
for k in KEYS:
    T, rows, draws, el = SRC[k]
    Hi = sum(np.histogram2d(la, lo, bins=[le, oe], weights=p)[0] for la, lo, p in full[k]) / len(full[k])
    Hw, Hs, st = seabed_density(T, rows, draws, el)
    dI, dW, dS = smooth(Hi), smooth(Hw), smooth(Hs)
    lI, lW, lS = hpd_levels(dI, LEVELS), hpd_levels(dW, LEVELS), hpd_levels(dS, LEVELS)
    dens[k] = (dI, lI, dW, lW)
    stats[k] = {"ess_pooled": ESS[k], "estimable": bool(ESS[k] >= ESS_MIN), **st,
                "area_km2_99_90_50": {"impact_full_weights": hpd_area(dI, lI), "impact_resampled": hpd_area(dS, lS), "wreckage_field": hpd_area(dW, lW)}}

# common frame: union of 99 % regions
inside = np.zeros_like(dens[KEYS[0]][0], bool)
for k in KEYS:
    inside |= dens[k][2] >= dens[k][3][0]; inside |= dens[k][0] >= dens[k][1][0]
r, cc = np.where(inside); mid_lat = 0.5 * (lc[r.min()] + lc[r.max()]); mid_lon = 0.5 * (oc[cc.min()] + oc[cc.max()])
half_lat = 0.55 * (lc[r.max()] - lc[r.min()]); half_lon = 0.55 * (oc[cc.max()] - oc[cc.min()])
half_lat = max(half_lat, half_lon * np.cos(np.radians(mid_lat))); half_lon = half_lat / np.cos(np.radians(mid_lat))
fmt = FuncFormatter(lambda v, _: f"{abs(v):.0f}°{'S' if v < 0 else 'N' if v > 0 else ''}")
n = len(KEYS); ncol = 2 if n == 4 else n; nrow = int(np.ceil(n / ncol))
fig, axs = plt.subplots(nrow, ncol, figsize=(3.4 * ncol, 3.6 * nrow + 0.5), squeeze=False, sharex=True, sharey=True,
                        gridspec_kw=dict(wspace=0.05, hspace=0.14))
for j, k in enumerate(KEYS):
    ax = axs.flat[j]; dI, lI, dW, lW = dens[k]
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
    ax.text(0.97, 0.03, f"90 % area, thousand km²: seabed {a['wreckage_field'][1]/1e3:,.0f}, same impacts {a['impact_resampled'][1]/1e3:,.0f}\n"
            f"{stats[k]['resampled_impacts']:,} draws on {stats[k]['distinct_impacts']:,} distinct impacts; impact ESS {ESS[k]:,.0f}",
            transform=ax.transAxes, fontsize=5.8, color="#333333", ha="right", va="bottom",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1.5))
    if not stats[k]["estimable"]:
        ax.text(0.36, 0.80, f"NOT ESTIMABLE\nimpact ESS {ESS[k]:,.0f} (< {ESS_MIN:,})", transform=ax.transAxes, ha="center", va="center",
                fontsize=9.5, color="#a00000", alpha=0.8, rotation=0, fontweight="bold")
    if j % ncol == 0: ax.set_ylabel("latitude", fontsize=7)
    if j >= n - ncol: ax.set_xlabel("longitude (°E)", fontsize=7)
for j in range(n, nrow * ncol): axs.flat[j].set_visible(False)
hs = [Patch(facecolor=s, edgecolor=EDGE, lw=0.6, label=f"seabed wreckage, {int(f * 100)} %") for s, f in zip(SHADES[::-1], LEVELS[::-1])]
hs += [Line2D([], [], color=REF["color"], lw=0.8, ls="--", label="impact PDF 50/90/99 % (reference)")]
hs += [Line2D([], [], **sty) for sty in ARCSTY.values()]
fig.legend(handles=hs, loc="lower center", ncol=3, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, 0.025))
fig.suptitle(TITLE, fontsize=8.5, x=0.06, ha="left", y=0.955)
fig.text(0.06, -0.01, SUB, fontsize=6, color="#555555", ha="left", va="top")
fig.savefig(OUTSTEM + ".pdf", bbox_inches="tight"); fig.savefig(OUTSTEM + ".png", dpi=220, bbox_inches="tight")
pathlib.Path(OUTSTEM + ".json").write_text(json.dumps({"options": stats, "smooth_deg": SMOOTH, "grid_deg": GRID, "ess_min": ESS_MIN,
    "afloat_mass_share": {k: float(SRC[k][3][SRC[k][3][:, 4] == 1, 7].sum() / SRC[k][3][SRC[k][3][:, 4] >= 0, 7].sum()) for k in KEYS}}, indent=1))
