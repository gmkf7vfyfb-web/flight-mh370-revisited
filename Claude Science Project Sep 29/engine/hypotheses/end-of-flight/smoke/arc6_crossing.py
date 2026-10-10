"""Where the V2 trajectories that are DESCENDING at 00:11 cross the 6th arc, before and after the 23:15/00:11 data
(Pete, 10 Oct 2026). Uses the module's own state at 00:11 (latent:state_m0011_*), so only descents whose onset
preceded 00:11 have a position; cruise-at-00:11 trajectories are flown by the core then and are not included.

Usage (from engine/): python arc6_crossing.py OUT_STEM ARCS_RUN_JSON RUN [RUN ...]
"""
import json, pathlib, sys, textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy.ndimage import gaussian_filter
from displacement_hist import option_posteriors
from displacement_greyscale import hpd_levels, LEVELS, SHADES, EDGE, EDGE_W

DESC = -300.0  # ft/min


def main():
    stem, arcs_json = sys.argv[1], sys.argv[2]; runs = [pathlib.Path(r) for r in sys.argv[3:]]
    arcs = {x["epoch"]: np.asarray(x["lat_lon"], float) for x in json.loads(pathlib.Path(arcs_json).read_text())["reference_arcs"]}
    sets = {"none__other": [], "m0011-bfo__other": [], "m0011__other": []}
    for run in runs:
        for sd in sorted((run / "bto-bfo").glob("seed-*")):
            m = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(m["impact_columns"])}
            X = np.load(sd / "impacts.npy", mmap_mode="r"); g = lambda k: np.array(X[:, cols[k]], float)
            vz = g("latent:state_m0011_vertical_speed_fpm"); lat = g("latent:state_m0011_latitude_deg"); lon = g("latent:state_m0011_longitude_deg")
            d = np.isfinite(vz) & (vz < DESC) & np.isfinite(lat)
            for k, p, c in option_posteriors(run, sd):
                if k in sets:
                    sets[k].append((lat[d], lon[d], p[d] / max(p[d].sum(), 1e-300), float(p[d].sum()), float(p[d].sum() ** 2 / np.sum(p[d] ** 2)) if p[d].sum() > 0 else 0.0))
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(9.6, 4.0), gridspec_kw=dict(width_ratios=[1.0, 1.25], wspace=0.25))
    info = {}
    # (a) map of 00:11 positions of descending survivors under m0011 (pooled, equal weight per seed)
    L = np.concatenate([s[0] for s in sets["m0011__other"]]); O = np.concatenate([s[1] for s in sets["m0011__other"]])
    W = np.concatenate([s[2] / len(sets["m0011__other"]) for s in sets["m0011__other"]])
    le = np.arange(-40, -20 + 1e-9, 0.05); oe = np.arange(85, 105 + 1e-9, 0.05)
    H, _, _ = np.histogram2d(L, O, bins=[le, oe], weights=W); D = gaussian_filter(H, 2.0)
    lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1]); lv = hpd_levels(D, LEVELS)
    ax.contourf(oc, lc, D, levels=lv + [D.max()], colors=SHADES); ax.contour(oc, lc, D, levels=lv, colors=EDGE, linewidths=EDGE_W)
    for e, st in (("m0011", dict(color="#b16286", lw=1.2, label="6th arc, 00:11")), ("m0019a", dict(color="#4a6fa5", lw=1.0, ls="--", label="7th arc, 00:19"))):
        if e in arcs:
            ax.plot(arcs[e][:, 1], arcs[e][:, 0], **st)
    ax.set_xlim(86, 104); ax.set_ylim(-39, -24); ax.set_aspect(1 / np.cos(np.radians(-32))); ax.grid(True, color="#e6e6e6", lw=0.5)
    ax.set_xlabel("longitude (°E)", fontsize=7.5); ax.set_ylabel("latitude (°)", fontsize=7.5); ax.tick_params(labelsize=7)
    ess = sum(s[4] for s in sets["m0011__other"])
    ax.set_title(f"(a) 00:11 position of V2 descents descending at 00:11\n(< {DESC:.0f} ft/min), weighted by 23:15 BFO + 00:11 BTO/BFO; ESS {ess:,.0f}", fontsize=7.2, loc="left")
    hs = [Patch(facecolor=s, edgecolor=EDGE, lw=0.6, label=f"{int(f * 100)} %") for s, f in zip(SHADES[::-1], LEVELS[::-1])]
    ax.legend(handles=hs, fontsize=6, frameon=False, loc="lower right")
    # (b) along-arc latitude PDFs
    edges = np.arange(-40, -20 + 1e-9, 0.25); cen = 0.5 * (edges[1:] + edges[:-1])
    style = {"none__other": ("prior (no data after 22:41)", "#b0b0b0", "-"), "m0011-bfo__other": ("23:15 + 00:11 BFO only", "#6b6b6b", "--"), "m0011__other": ("23:15 BFO + 00:11 BTO/BFO", "#111111", "-")}
    for k, (lab, colr, ls) in style.items():
        h = sum(np.histogram(s[0], bins=edges, weights=s[2])[0] / len(sets[k]) for s in sets[k]); h = gaussian_filter(h, 1.0); h = h / (h.sum() * 0.25)
        share = np.mean([s[3] for s in sets[k]]); e2 = sum(s[4] for s in sets[k])
        bx.plot(cen, h, color=colr, ls=ls, lw=1.3, label=f"{lab}: descending share {share:.2f}, ESS {e2:,.0f}")
        c = np.cumsum(h) * 0.25; info[k] = {"descending_weight_share_mean": share, "ess_descending": e2, "lat_q05_50_95": [float(np.interp(q, c, cen)) for q in (0.05, 0.5, 0.95)]}
    bx.set_xlabel("latitude where the descent crosses the 6th arc (°; along-arc position)", fontsize=7.5); bx.set_ylabel("density (per degree)", fontsize=7.5)
    bx.set_xlim(-39, -24); bx.grid(True, color="#e6e6e6", lw=0.5); bx.tick_params(labelsize=7); bx.legend(fontsize=6.3, frameon=False, loc="upper left")
    bx.set_title("(b) along-arc PDF of the 6th-arc crossing, V2 descents descending at 00:11", fontsize=7.2, loc="left")
    m = json.loads((runs[0] / "run.json").read_text())
    foot = (f"Runs: {', '.join(r.name for r in runs)} (V2 from core 'reference-289' hand-off m2241, prior track {m['config']['prior']['track_deg']} deg; 100,000 parents x "
            f"{m['terminal']['children']} children x 4 descents per seed). Position and vertical rate at 00:11 are the module's own flown state (latent:state_m0011_*). "
            f"Descending = vertical rate < {DESC:.0f} ft/min at 00:11. Cruise-at-00:11 trajectories (onset later) are core-flown then and not shown. Labels: SMOKE; "
            f"UNCORRECTED FUEL; PROVISIONAL SAMPLER (22:41 population before core request 17). ICAO EEDB Trent 892 idle floor; point-mass descent; Boeing-calibrated glide band. "
            f"Code {m['code_revision']}.")
    fig.text(0.02, -0.04, "\n".join(textwrap.wrap(foot, 200)), fontsize=5.6, color="#333333", ha="left", va="top")
    fig.savefig(stem + ".png", dpi=200, bbox_inches="tight"); fig.savefig(stem + ".pdf", bbox_inches="tight")
    pathlib.Path(stem + ".json").write_text(json.dumps(info, indent=1)); print(json.dumps(info))


if __name__ == "__main__":
    main()
