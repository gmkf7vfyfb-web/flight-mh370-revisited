"""Deliverable 4 figure: conditional impact PDF under H reported WITH its tension measurement.

    python d4_figure.py <rerun-measured dir> <rerun-declared dir> <rerun-pt1h dir> <targets-3km.csv> <out stem>

Inputs are the outputs of rerun_reference.py (gitignored run tree): rerun-reference.csv and
fields-eof2f.npz (pooled eof-2f fields, rho4-0 / equal arm). Writes <out stem>.png and .pdf.
Panels: (a) unconditional impact PDF; (b) H-alone likelihood (ocean-model marginal); (c) conditional
PDF under H, with the unconditional 90% HDR outlined; (d) tension: Handley & Lemos (2019) p for
every spread x ocean-model field, pooled with the eight-seed range.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KERNEL = "eof-2f PROVISIONAL-OVERNIGHT"

from branch_figure import footnote  # noqa: E402  (shared footnote helper)

COMMON_H = (
    "Under H: ocean models GLORYS12 + ERA5 and GlobCurrent daily + ERA5 at equal weight; measured transport error (GDP-replay OU fit "
    "per component, no added diffusivity); windage 0-5 % uniform; released 00:20 UTC 8 Mar. Pleiades rating-5 objects in 6 clusters at 3 km, "
    "equal cluster weights (rho4 = 0). The conditional is p(impact | Pleiades, H); no Bayes factor or P(H | data) is computed or implied."
)

D4_MEASURED_NOTES = [
    "Source posterior: core run reference-snapshots (prior track 295.66 deg, sd 1.0, at 18:01:49 UTC; base config davey2016 + "
    "no-exhaustion-prior + reference-snapshots; 7 Hz BFO sigma baseline; 8 seeds x 7M particles; fails split-half), per-particle positions at "
    "00:19:37 UTC, convolved with the PROVISIONAL eof-2f descent kernel (0.934 within 15 NM; 0.032 NW quadrant 30-50 NM; 0.034 NW quadrant "
    "50-103.4 NM). No 00:19 burst scoring of impacts and no seabed-search evidence. Label: 295.66 deg prior; superseded on re-run.",
    COMMON_H,
    "Panel d: Handley & Lemos (2019) tension probability, pooled (dot) and 8-seed range (bar); 'declared' = superseded sigma_e 0.05 m/s, "
    "T_e 2 d, K 30-1000 m2/s. Orange line: 7th arc (prior-work grid); circles: Pleiades clusters; solid blue: 90 % HDR; dashed grey: "
    "unconditional 90 % HDR.",
]

D4_289_NOTES = [
    "Panels a-b: core run reference-289 (prior track 289.7 deg, sd 1.0, at 18:01:49 UTC; base config davey2016 + no-exhaustion-prior + "
    "reference-snapshots + early-families/overnight/reference-289; 7 Hz BFO sigma baseline; 4 seeds x 7M particles), per-particle positions at 00:19:37 UTC, convolved with the "
    "PROVISIONAL eof-2f descent kernel. No 00:19 burst scoring of impacts and no seabed-search evidence.",
    "Panel c: ln S (Handley & Lemos 2019), pooled (dot) and seed range (bar), per descent kernel: disks; eof-2f; end of flight's displacement "
    "histograms (Boeing glide, +/-160 NM, SMOKE scale, seed 1, N = 16, made on the 295.66 hand-off; 'none' = 00:19 messages held out, "
    "r600/r1200 = 00:19:29 / 00:19:37 message scored; 'other' / 'fuel-exhaustion' = log-on cause; dive class (b) on/off, PROVISIONAL).",
    COMMON_H,
]


def hdr_level(dens, mass, level=0.9):
    o = np.argsort(dens.ravel())[::-1]
    c = np.cumsum(mass.ravel()[o])
    return dens.ravel()[o][min(np.searchsorted(c, level), len(o) - 1)]


def load_fields(d):
    z = np.load(Path(d) / "fields-eof2f.npz", allow_pickle=False)
    return {k: z[k] for k in z.files}


def tension_rows(dirs):
    rows = []
    for tag, d in dirs:
        x = pd.read_csv(Path(d) / "rerun-reference.csv")
        x = x[(x.kernel == KERNEL) & x.field.str.startswith("module") & (x.object_rating == "rho4-0") & (x.cluster_weight == "equal")]
        for f, g in x.groupby("field"):
            model = f.replace("module D3 (", "").rstrip(")")
            model = "marginal" if model.startswith("marginal") else model.split("+")[0]
            pooled = g[g.replicate == "pooled"].iloc[0]
            seeds = g[g.replicate != "pooled"]
            rows.append(dict(spread=tag, model=model, p=pooled.tension_p, p_lo=seeds.tension_p.min(), p_hi=seeds.tension_p.max(),
                             lnS=pooled.ln_S, d=pooled.d_shared, shift=pooled.mean_shift_nm, n_seeds=len(seeds)))
    return pd.DataFrame(rows)


def make(measured, declared, pt1h, targets_csv, out, plt):
    F = load_fields(measured)
    lat, lon, area, unc = F["lat"], F["lon"], F["area"], F["uncond"]
    labels = list(F["labels"])
    im = [i for i, l in enumerate(labels) if l.startswith("marginal")][0]
    L = F["L"][im]
    pu = unc / unc.sum()
    pH = L * area / (L * area).sum()
    pj = pu * L / (pu * L).sum()
    dens = [pu / area, pH / area, pj / area]
    mass = [pu, pH, pj]
    T = pd.read_csv(targets_csv)
    T5 = T[(T.arm == "rating5")]
    ext = [lon[0], lon[-1], lat[0], lat[-1]]
    fig, axs = plt.subplots(1, 4, figsize=(7.1, 2.6), gridspec_kw=dict(width_ratios=[1, 1, 1, 0.9], wspace=0.28))
    titles = ["Flight posterior", "Pléiades likelihood", "Conditional on H"]
    cmap = "Greys"
    for k in range(3):
        ax = axs[k]
        dn = dens[k] / dens[k].max()
        ax.imshow(dn, origin="lower", extent=ext, cmap=cmap, vmin=0, vmax=1, aspect=1 / np.cos(np.radians(36)), interpolation="nearest")
        ax.contour(lon, lat, dens[k], levels=[hdr_level(dens[k], mass[k])], colors=["#1f5fa8"], linewidths=0.9)
        if k == 2:
            ax.contour(lon, lat, dens[0], levels=[hdr_level(dens[0], mass[0])], colors=["#888888"], linewidths=0.7, linestyles="--")
        ax.contour(lon, lat, F["cross"], levels=[0.0], colors=["#c07020"], linewidths=0.7)
        if k >= 1:
            ax.plot(T5.lon, T5.lat, "o", ms=2.5, mfc="none", mec="#b03030", mew=0.7)
        ax.set_title(titles[k], loc="left")
        ax.set_xlabel("Longitude (°E)")
        if k == 0:
            ax.set_ylabel("Latitude (°)")
        ax.set_xlim(88, 95.5)
        ax.set_ylim(-39.5, -32)
        ax.set_yticks(range(-39, -32))
        if k > 0:
            ax.set_yticklabels([])
    R = tension_rows([("declared", declared), ("measured", measured), ("measured, hourly GlobCurrent", pt1h)])
    order = [("declared", "glorys12v1"), ("declared", "globcurrent-my-pt1h"), ("declared", "marginal"),
             ("measured", "glorys12v1"), ("measured", "globcurrent-my-p1d"), ("measured", "marginal"),
             ("measured, hourly GlobCurrent", "globcurrent-my-pt1h")]
    names = {"glorys12v1": "GLORYS12", "globcurrent-my-pt1h": "GlobCurrent hourly", "globcurrent-my-p1d": "GlobCurrent daily", "marginal": "both products"}
    ax = axs[3]
    ys, yl = [], []
    for i, (s, m) in enumerate(order):
        r = R[(R.spread == s) & (R.model == m)]
        if r.empty:
            continue
        r = r.iloc[0]
        y = len(order) - i
        col = "#1f5fa8" if s.startswith("measured") else "#999999"
        ax.plot([r.p_lo, r.p_hi], [y, y], "-", color=col, lw=1.2)
        ax.plot(r.p, y, "o", color=col, ms=3.5)
        ys.append(y)
        yl.append(names[m])
    ax.axvline(0.05, color="#b03030", lw=0.7, ls=":")
    ax.text(0.047, min(ys) - 0.55, "p = 0.05", fontsize=6, color="#b03030", va="center", ha="right")
    ax.set_yticks(ys)
    ax.set_yticklabels(yl)
    ax.set_xscale("log")
    ax.set_xlim(0.02, 1.0)
    ax.set_xticks([0.02, 0.05, 0.1, 0.2, 0.5, 1.0])
    ax.set_xticklabels(["0.02", "0.05", "0.1", "0.2", "0.5", "1"])
    ax.set_ylim(min(ys) - 0.9, max(ys) + 0.9)
    ax.set_xlabel("Tension probability p")
    ax.set_title("No significant tension", loc="left")
    footnote(fig, D4_MEASURED_NOTES, width=200, y=-0.09)
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    for y0, y1, lab in [(5, 7, "declared spread"), (1, 4, "measured spread")]:
        yy = [y for y in ys if y0 <= y <= y1]
        if yy:
            ax.text(0.98, max(yy) + 0.45, lab, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=6, color="#1f5fa8" if lab.startswith("measured") else "#777777")
    fig.savefig(str(out) + ".png", dpi=300, bbox_inches="tight")
    fig.savefig(str(out) + ".pdf", bbox_inches="tight")
    return fig, axs, R


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    make(*sys.argv[1:6], plt=plt)


def kernel_rows(dirs):
    """ln S and mean shift per descent kernel, ocean-model marginal, rho4-0 / equal; pooled + seed range."""
    rows = []
    for tag, d in dirs:
        x = pd.read_csv(Path(d) / "rerun-reference.csv")
        x = x[x.field.str.contains("marginal") & (x.object_rating == "rho4-0") & (x.cluster_weight == "equal")]
        for k, g in x.groupby("kernel", sort=False):
            p, s = g[g.replicate == "pooled"].iloc[0], g[g.replicate != "pooled"]
            rows.append(dict(ref=tag, kernel=k, lnS=p.ln_S, lnS_lo=s.ln_S.min(), lnS_hi=s.ln_S.max(), shift=p.mean_shift_nm,
                             lobe30=p.lobe30, d=p.d_shared, p=p.tension_p))
    return pd.DataFrame(rows)


def short_kernel(k):
    if k.startswith("disk-"):
        return k.replace("disk-", "disk ").replace("nm", " NM")
    if k.startswith("eof-2f"):
        return "eof-2f (provisional)"
    k = k.replace("eof-hist displacement-boeing-glide-", "").replace("-160", "").replace("__pooled", "")
    dive, opt = k.split(" ", 1)
    return f"EoF {opt.replace('__', ', ').replace('_', ' ')}, {dive.replace('-', ' ')}"


def make_compare(dir_new, dir_old, targets_csv, out, plt, new_label="289.7° prior", old_label="295.66° prior"):
    """(a) unconditional and (b) conditional PDF on the new reference (eof-2f); (c) ln S per descent kernel,
    new vs old reference, with seed ranges; the conditional and its tension shown together."""
    F = load_fields(dir_new)
    lat, lon, area, unc = F["lat"], F["lon"], F["area"], F["uncond"]
    im = [i for i, l in enumerate(F["labels"]) if str(l).startswith("marginal")][0]
    L = F["L"][im]
    pu = unc / unc.sum()
    pj = pu * L / (pu * L).sum()
    T = pd.read_csv(targets_csv)
    T5 = T[T.arm == "rating5"]
    ext = [lon[0], lon[-1], lat[0], lat[-1]]
    fig, axs = plt.subplots(1, 3, figsize=(7.1, 2.9), gridspec_kw=dict(width_ratios=[1, 1, 1.5], wspace=0.25))
    for ax, (pm, ttl) in zip(axs[:2], [(pu, f"Flight posterior, {new_label}"), (pj, "Conditional on H")]):
        dn = pm / area
        ax.imshow(dn / dn.max(), origin="lower", extent=ext, cmap="Greys", vmin=0, vmax=1, aspect=1 / np.cos(np.radians(36)), interpolation="nearest")
        ax.contour(lon, lat, dn, levels=[hdr_level(dn, pm)], colors=["#1f5fa8"], linewidths=0.9)
        if pm is pj:
            du = pu / area
            ax.contour(lon, lat, du, levels=[hdr_level(du, pu)], colors=["#888888"], linewidths=0.7, linestyles="--")
            ax.plot(T5.lon, T5.lat, "o", ms=2.5, mfc="none", mec="#b03030", mew=0.7)
        ax.contour(lon, lat, F["cross"], levels=[0.0], colors=["#c07020"], linewidths=0.7)
        ax.set_title(ttl, loc="left")
        ax.set_xlabel("Longitude (°E)")
        ax.set_xlim(88, 95.5)
        ax.set_ylim(-39.5, -32)
        ax.set_yticks(range(-39, -32))
    axs[0].set_ylabel("Latitude (°)")
    axs[1].set_yticklabels([])
    R = kernel_rows([(new_label, dir_new), (old_label, dir_old)])
    ks = list(dict.fromkeys(R.kernel))
    ax = axs[2]
    for off, (lab, col) in zip((0.17, -0.17), [(new_label, "#1f5fa8"), (old_label, "#999999")]):
        for i, k in enumerate(ks):
            r = R[(R.ref == lab) & (R.kernel == k)].iloc[0]
            y = len(ks) - i + off
            ax.plot([r.lnS_lo, r.lnS_hi], [y, y], "-", color=col, lw=1.1)
            ax.plot(r.lnS, y, "o", color=col, ms=3, label=lab if i == 0 else None)
    ax.axvline(0, color="#444444", lw=0.6)
    ax.set_yticks([len(ks) - i for i in range(len(ks))])
    ax.set_yticklabels([short_kernel(k) for k in ks])
    ax.yaxis.tick_right()
    ax.set_xlabel("Suspiciousness ln S (< 0: tension)")
    ax.set_title("Tension by descent kernel", loc="left", pad=12)
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=2, frameon=False, fontsize=6, handletextpad=0.3, borderaxespad=0.0)
    ax.margins(x=0.08)
    footnote(fig, D4_289_NOTES, width=200)
    fig.savefig(str(out) + ".png", dpi=300, bbox_inches="tight")
    fig.savefig(str(out) + ".pdf", bbox_inches="tight")
    return fig, axs, R
