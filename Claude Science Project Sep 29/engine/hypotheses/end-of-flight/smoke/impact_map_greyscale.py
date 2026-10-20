"""Project-convention (report/epoch_map.py) impact map: latitude/longitude axes, greyscale highest-posterior-
density bands at 50/90/99 % with dark contour edges, and the 6th (00:11) and 7th (00:19) arcs.

    python3 impact_map_greyscale.py <out-stem> "<title>" <arcs-run.json> <terminal-out-dir> [<dir> ...]
        [--options none__other,r600_inflated__fuel-exhaustion,r1200_inflated__fuel-exhaustion] [--smooth-deg 0.1]

Every seed found under the given directories is pooled with equal weight per seed; each seed's posterior is
displacement_hist.option_posteriors. Density: weighted 0.02 deg histogram, Gaussian-smoothed (default sigma
0.1 deg = 6 NM, finer than epoch_map's 0.3 deg because an impact field is narrower than a 00:19 position field),
HPD levels from the smoothed density. Writes <stem>.pdf, <stem>.png and <stem>.json (per-panel ESS per seed,
pooled median, and the enclosed-mass check).
"""
import argparse, json, pathlib, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator
from scipy.ndimage import gaussian_filter
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from displacement_hist import option_posteriors
from displacement_greyscale import hpd_levels, LEVELS, SHADES, EDGE, EDGE_W, TITLES

GRID = 0.02
ARCS = {"m0011": dict(lw=1.2, color="#b16286", label="6th arc, 00:11 UTC"),
        "m0019a": dict(lw=1.0, color="#4a6fa5", ls="--", label="7th arc, 00:19 UTC")}


def wq(x, p, q):
    o = np.argsort(x); c = np.cumsum(p[o]); return float(np.interp(q, c / c[-1], x[o]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stem"); ap.add_argument("title"); ap.add_argument("arcs"); ap.add_argument("runs", nargs="+")
    ap.add_argument("--options", default="none__other,r600_inflated__fuel-exhaustion,r1200_inflated__fuel-exhaustion")
    ap.add_argument("--smooth-deg", type=float, default=0.1)
    ap.add_argument("--not-estimable", default="", help="comma list of options stamped NOT ESTIMABLE (unconverged posterior)")
    ap.add_argument("--titles", default="", help="opt=title;opt=title overrides")
    ap.add_argument("--assumptions", default="", help="free text appended to the run-information footnote (standing rule, Pete, ~20:20 UTC 9 Oct)")
    a = ap.parse_args(); opts = a.options.split(",")
    arcs = {x["epoch"]: np.asarray(x["lat_lon"], float) for x in json.loads(pathlib.Path(a.arcs).read_text())["reference_arcs"]}
    seeds = [s for d in a.runs for s in sorted(pathlib.Path(d, "bto-bfo").glob("seed-*")) if (s / "impacts.npy").exists()]
    pooled = {k: [] for k in opts}; info = {}
    for s in seeds:
        run = s.parent.parent
        for k, p, c in option_posteriors(run, s):
            if k in opts:
                pooled[k].append((c["lat"], c["lon"], p / p.sum()))
                info.setdefault(k, {"ess_per_seed": {}})["ess_per_seed"][f"{run.name}/{s.name}"] = float(1 / np.sum(p ** 2))
    lat_all = np.concatenate([x[0] for k in opts for x in pooled[k]]); lon_all = np.concatenate([x[1] for k in opts for x in pooled[k]])
    le = np.arange(np.floor(lat_all.min()) - 1, np.ceil(lat_all.max()) + 1 + GRID, GRID)
    oe = np.arange(np.floor(lon_all.min()) - 1, np.ceil(lon_all.max()) + 1 + GRID, GRID)
    lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1])
    dens = {}
    for k in opts:
        H = sum(np.histogram2d(la, lo, bins=[le, oe], weights=p)[0] for la, lo, p in pooled[k]) / len(pooled[k])
        d = gaussian_filter(H, a.smooth_deg / GRID, mode="constant"); dens[k] = d / d.sum()
        la = np.concatenate([x[0] for x in pooled[k]]); lo = np.concatenate([x[1] for x in pooled[k]])
        pp = np.concatenate([x[2] for x in pooled[k]]) / len(pooled[k])
        info[k].update(median_lat_deg=wq(la, pp, 0.5), median_lon_deg=wq(lo, pp, 0.5))
    # One frame for every panel, on the union of the 99 % regions, widened by the latitude cosine.
    inside = np.zeros_like(next(iter(dens.values())), bool)
    lvls = {k: hpd_levels(dens[k], LEVELS) for k in opts}
    for k in opts:
        inside |= dens[k] >= lvls[k][0]
    r, c = np.where(inside); mid_lat = 0.5 * (lc[r.min()] + lc[r.max()]); mid_lon = 0.5 * (oc[c.min()] + oc[c.max()])
    half_lat = max(1.0, 0.6 * (lc[r.max()] - lc[r.min()])); half_lon = max(half_lat, 0.6 * (oc[c.max()] - oc[c.min()]) * np.cos(np.radians(mid_lat))) / np.cos(np.radians(mid_lat))
    half_lat = max(half_lat, half_lon * np.cos(np.radians(mid_lat)))
    fig, axs = plt.subplots(1, len(opts), figsize=(2.5 * len(opts) + 0.4, 3.3), sharey=True, squeeze=False,
                            gridspec_kw=dict(wspace=0.06))
    titles = {k: v.replace("\\n", "\n") for k, v in (t.split("=", 1) for t in a.titles.split(";") if "=" in t)}
    fmt = FuncFormatter(lambda v, _: f"{abs(v):.0f}°{'S' if v < 0 else 'N' if v > 0 else ''}")
    for j, k in enumerate(opts):
        ax = axs[0, j]; lv = lvls[k]
        step = 1.0 if 2 * half_lat < 6 else 2.0 if 2 * half_lat < 14 else 5.0  # epoch_map.py rule
        ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
        ax.set_axisbelow(True); ax.grid(True, color="#e3e3e3", lw=0.6)
        ax.contourf(oc, lc, dens[k], levels=lv + [dens[k].max()], colors=SHADES, antialiased=True)
        ax.contour(oc, lc, dens[k], levels=lv, colors=EDGE, linewidths=EDGE_W)
        for e, st in ARCS.items():
            if e in arcs:
                ax.plot(arcs[e][:, 1], arcs[e][:, 0], **st)
        ax.set_xlim(mid_lon - half_lon, mid_lon + half_lon); ax.set_ylim(mid_lat - half_lat, mid_lat + half_lat)
        ax.set_aspect(1 / np.cos(np.radians(mid_lat))); ax.yaxis.set_major_formatter(fmt); ax.tick_params(labelsize=6)
        ax.set_xlabel("longitude (°E)", fontsize=7); ax.tick_params(labelbottom=True)
        ax.set_title(titles.get(k, TITLES.get(k, k)), fontsize=7.5, loc="left")
        if k in a.not_estimable.split(","):
            ax.text(0.5, 0.97, "NOT ESTIMABLE: posterior unconverged\n(parent-limited; shape not to be read)", transform=ax.transAxes,
                    fontsize=5.8, color="#000000", ha="center", va="top", bbox=dict(boxstyle="square,pad=0.25", fc="white", ec="#000000", lw=0.6)); ax.set_xlabel("longitude (°E)", fontsize=7)
        ess = sum(info[k]["ess_per_seed"].values())
        ax.text(0.97, 0.03, f"ESS {ess:,.0f} ({len(pooled[k])} seed{'s' if len(pooled[k]) > 1 else ''})",
                transform=ax.transAxes, fontsize=6, color="#555555", ha="right", va="bottom")
        info[k]["enclosed_mass_99_90_50"] = [float(dens[k][dens[k] >= l].sum()) for l in lv]
    axs[0, 0].set_ylabel("latitude", fontsize=7)
    hs = [Patch(facecolor=s, edgecolor=EDGE, lw=0.6, label=f"{int(f * 100)} % of probability") for s, f in zip(SHADES[::-1], LEVELS[::-1])]
    hs += [plt.Line2D([], [], **{kk: v for kk, v in st.items()}) for st in ARCS.values()]
    fig.legend(handles=hs, loc="lower center", ncol=5, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle(a.title, fontsize=8, x=0.02, ha="left", y=1.0)
    # Run-information footnote, read from the runs (standing rule): beneath the chart, never inside the axes.
    m = json.loads((pathlib.Path(a.runs[0]) / "run.json").read_text()); cfg = m["config"]; pr = cfg.get("prior", {})
    eof = cfg.get("hypotheses", {}).get("end-of-flight", {}); n_rows = sum(int(np.load(sd / "impacts.npy", mmap_mode="r").shape[0]) for sd in seeds)
    kids, dpc = m["terminal"]["children"], eof.get("descents_per_child", 1)
    foot = (f"Runs: {', '.join(pathlib.Path(r).name for r in a.runs)} (terminal stage on core run '{cfg.get('name')}', hand-off {m['stop']['epoch']} "
            f"from {m['source_run']}). Prior track {pr.get('track_deg')}° (sd {pr.get('track_sd_deg')}°) from {pr.get('time_utc')}. "
            f"Configs: {' + '.join(pathlib.Path(c).name for c in m['config_paths'] if 'seed-' not in c)}. "
            f"{len(seeds)} seeds, {round(n_rows / (kids * dpc) / max(len(seeds), 1)):,} parents/seed x {kids} children x {dpc} descents = {n_rows:,} descents; "
            f"BFO models {', '.join(b['label'] for b in m['terminal']['bfo_models'])}; {len(m['terminal']['module_families'])} module families "
            f"(propulsion x control x profile shape). Panels: {'; '.join(opts)} (option__log-on cause). "
            f"HPD from a {GRID}° weighted histogram smoothed {a.smooth_deg}°, equal weight per seed. Code {m['code_revision']}. {a.assumptions}")
    import textwrap
    fig.text(0.02, -0.10, "\n".join(textwrap.wrap(foot, 230)), fontsize=5.2, color="#333333", ha="left", va="top")
    fig.savefig(a.stem + ".pdf", bbox_inches="tight"); fig.savefig(a.stem + ".png", dpi=200, bbox_inches="tight")
    pathlib.Path(a.stem + ".json").write_text(json.dumps({"seeds": [str(s) for s in seeds], "options": info}, indent=1))
    print("wrote", a.stem)


if __name__ == "__main__":
    main()
