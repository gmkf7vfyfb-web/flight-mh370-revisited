"""Impact-location maps in the project's greyscale style, from `mh370 terminal` output.

    python3 impact_maps.py <reference-run-dir> <out-dir> <terminal-out-dir> [<terminal-out-dir> ...]
        [--option none|<loglik column, e.g. r600/no-offset>] [--label "295.66° prior; ..."]

Re-runs unchanged on new hand-offs: point it at the new terminal output(s) and the reference run
that produced the hand-offs. Seeds found across all terminal dirs are pooled with EQUAL WEIGHT PER
SEED. Writes:
  impact-overview.{pdf,png}      the reference run's frame (80-104E, 22-42S), 1 deg graticule
  impact-closeup.{pdf,png}       the 90% impact region, 0.5 deg graticule, 00:19:37 positions faint
  impact-by-control.{pdf,png}    close-up split by the control axis of the taxonomy
  impact-maps.json               every number printed on the figures

Weights: the impact sample weight column; with --option, times exp(loglik:<option>) normalised per
seed. With the default option `none` the 00:19 bursts are held out and the map shows what the
descent physics does to the 00:11 hand-off, nothing more.
"""
import argparse, json, pathlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MultipleLocator
from scipy.ndimage import gaussian_filter
from scipy.special import gammaln

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "pdf.fonttype": 42})
LATFMT = FuncFormatter(lambda v, _: f"{abs(v):.0f}°{'S' if v < 0 else 'N' if v > 0 else ''}")
LONFMT = FuncFormatter(lambda v, _: f"{v:.0f}°E")
LEVELS = (0.99, 0.90, 0.50)
SHADES = ["#e4e4e4", "#a8a8a8", "#666666"]            # 99, 90, 50 %
ARC6 = dict(lw=1.4, color="#b5527d")                   # 6th arc, solid
ARC7 = dict(lw=1.4, color="#4a6fa5", ls="--")          # 7th arc, dashed
CONTROL = ["ditching-attempt", "maintained-then-lost", "no-intervention", "upset-then-recovery"]


def hpd_levels(d, fractions):
    flat = np.sort(d.ravel())[::-1]
    share = np.cumsum(flat) / flat.sum()
    return [float(flat[min(np.searchsorted(share, f), len(flat) - 1)]) for f in fractions]


def grid(lat, lon, w, box, cell, smooth):
    la0, la1, lo0, lo1 = box
    le = np.arange(la0, la1 + cell, cell); oe = np.arange(lo0, lo1 + cell, cell)
    c, _, _ = np.histogram2d(lat, lon, bins=[le, oe], weights=w)
    d = gaussian_filter(c, smooth / cell, mode="constant")
    mid = lambda e: 0.5 * (e[:-1] + e[1:])
    return mid(le), mid(oe), d / d.sum()


def wq(x, w, q):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]
    return [float(np.interp(p, c, x[o])) for p in q]


def logon_loglik(flameout, p):
    """Brief section 6, the same formula as LogonParams::log_likelihood in lib.rs (and its test):
    ln gamma(t_logon - t_flameout; shape, scale), -inf for no flame-out or one after the log-on."""
    lag = p["logon_unix_s"] - flameout
    k, th = p["lag_shape"], p["lag_scale_s"]
    with np.errstate(divide="ignore", invalid="ignore"):
        ll = (k - 1) * np.log(lag) - lag / th - k * np.log(th) - gammaln(k)
    return np.where(np.isfinite(flameout) & (lag > 0), ll, -np.inf)


def load_impacts(dirs, option, logon):
    lat, lon, w, ctrl, seeds, disp = [], [], [], [], [], []
    for d in dirs:
        d = pathlib.Path(d)
        run = json.loads((d / "run.json").read_text())
        cols = {c: i for i, c in enumerate(run["impact_columns"])}
        fams = run["terminal"]["module_families"]
        for rep in run["replicates"]:
            f = d / rep["case"] / f"seed-{rep['seed']}" / "impacts.npy"
            if not f.exists() or rep["seed"] in seeds:
                continue
            X = np.load(f, mmap_mode="r")
            wt = np.asarray(X[:, cols["weight"]], float)
            if option != "none":
                ll = np.asarray(X[:, cols[f"loglik:{option}"]], float)
                ll = np.where(np.isfinite(ll), ll, -np.inf)
                wt = wt * np.exp(ll - ll.max())
            if logon == "fuel-exhaustion":
                p = run["config"]["hypotheses"]["end-of-flight"]["logon"]
                ll = logon_loglik(np.asarray(X[:, cols["latent:realised_flameout_unix_s"]], float), p)
                wt = wt * np.exp(ll - ll[np.isfinite(ll)].max())
            wt = wt / wt.sum()
            lat.append(np.asarray(X[:, cols["latitude_deg"]], float))
            lon.append(np.asarray(X[:, cols["longitude_deg"]], float))
            w.append(wt)
            fam = np.asarray(X[:, cols["family"]], int)
            ctrl.append(np.array([CONTROL.index(fams[k].split("/")[2]) for k in range(len(fams))])[fam])
            # Great-circle distance from each trajectory's OWN position at the last burst it flew
            # through (00:19:37) to its impact; NaN where it took over after that burst.
            bl = np.asarray(X[:, cols["latent:last_burst_latitude_deg"]], float)
            bo = np.asarray(X[:, cols["latent:last_burst_longitude_deg"]], float)
            p1, p2 = np.radians(bl), np.radians(lat[-1]); dl = np.radians(lon[-1] - bo)
            hv = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
            disp.append(2 * 6_371_008.8 * np.arcsin(np.sqrt(np.clip(hv, 0, 1))) / 1852.0)
            seeds.append(rep["seed"])
    n = len(seeds)
    load_impacts.disp = np.concatenate(disp)
    return (np.concatenate(lat), np.concatenate(lon), np.concatenate(w) / n, np.concatenate(ctrl), sorted(seeds),
            json.loads((pathlib.Path(dirs[0]) / "run.json").read_text()))


def load_final(ref, seeds, per_seed=4000, rng=np.random.default_rng(11)):
    """A weight-proportional resample of the reference posterior at 00:19:37, for faint display."""
    # Columns by NAME from run.json, so an added column (e.g. a family stratum index) cannot shift them.
    names = json.loads((ref / "run.json").read_text())["final_columns"]
    c = {n: i for i, n in enumerate(names)}
    iw = next(c[n] for n in ("weight", "w", "log_weight") if n in c)
    ilat = next(c[n] for n in ("latitude_deg", "lat_deg", "lat") if n in c)
    ilon = next(c[n] for n in ("longitude_deg", "lon_deg", "lon") if n in c)
    pts = []
    for s in seeds:
        a = np.load(ref / "bto-bfo" / f"seed-{s}" / "final.npy", mmap_mode="r")
        w = np.asarray(a[:, iw], float)
        if names[iw] == "log_weight": w = np.exp(w - w.max())
        w /= w.sum()
        k = rng.choice(len(w), size=per_seed, p=w)
        pts.append(np.stack([np.asarray(a[k, ilat], float), np.asarray(a[k, ilon], float)], axis=1))
    return np.concatenate(pts)


def arcs(ref):
    run = json.loads((ref / "run.json").read_text())
    by = {a["epoch"]: (np.asarray(a["lat_lon"], float), a["altitude_ft"]) for a in run["reference_arcs"]}
    return by["m0011"], by["m0019a"]


def draw(ax, lat, lon, w, box, cell, smooth, arc6, arc7, outline_only=False):
    lc, oc, d = grid(lat, lon, w, box, cell, smooth)
    lv = hpd_levels(d, LEVELS)
    if not outline_only:
        ax.contourf(oc, lc, d, levels=lv + [d.max() * 1.0001], colors=SHADES)
    ax.contour(oc, lc, d, levels=lv, colors="#1e1e1e", linewidths=[0.45, 0.6, 0.75])
    ax.plot(arc6[0][:, 1], arc6[0][:, 0], **ARC6)
    ax.plot(arc7[0][:, 1], arc7[0][:, 0], **ARC7)
    return lc, oc, d, lv


def frame(ax, box, major, minor, mid_lat):
    la0, la1, lo0, lo1 = box
    ax.set_xlim(lo0, lo1); ax.set_ylim(la0, la1)
    ax.set_aspect(1 / np.cos(np.deg2rad(mid_lat)))
    ax.xaxis.set_major_locator(MultipleLocator(major)); ax.yaxis.set_major_locator(MultipleLocator(major))
    ax.xaxis.set_minor_locator(MultipleLocator(minor)); ax.yaxis.set_minor_locator(MultipleLocator(minor))
    ax.grid(True, which="both", color="#dedede", lw=0.5); ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(LONFMT); ax.yaxis.set_major_formatter(LATFMT)
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")


def legend(ax, arc6, arc7, extra=()):
    h = [Patch(facecolor=c, edgecolor="#1e1e1e", lw=0.6, label=f"{int(f * 100)} % of probability")
         for c, f in zip(SHADES[::-1], (0.50, 0.90, 0.99))]
    h += [Line2D([], [], **ARC6, label=f"6th arc, 00:11 UTC ({arc6[1]:,.0f} ft)"),
          Line2D([], [], **ARC7, label=f"7th arc, 00:19 UTC ({arc7[1]:,.0f} ft)")] + list(extra)
    ax.legend(handles=h, loc="upper left", fontsize=7, framealpha=0.92, edgecolor="none")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref"); ap.add_argument("out"); ap.add_argument("dirs", nargs="+")
    ap.add_argument("--option", default="none")
    ap.add_argument("--logon", default="other", choices=["other", "fuel-exhaustion"],
                    help="logon-cause alternative: 'other' leaves the log-on unscored; 'fuel-exhaustion' "
                         "weights by the section 6 lag likelihood")
    ap.add_argument("--label", default="295.66° prior; superseded if core re-runs")
    a = ap.parse_args()
    ref, out = pathlib.Path(a.ref), pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tag = ("" if a.option == "none" else "-" + a.option.replace("/", "-")) + ("-logon" if a.logon == "fuel-exhaustion" else "")
    lat, lon, w, ctrl, seeds, run = load_impacts(a.dirs, a.option, a.logon)
    arc6, arc7 = arcs(ref)
    fin = load_final(ref, seeds)
    rev = run.get("code_revision", "?")
    n_children = run["terminal"]["children"]
    held = "00:19 bursts held out" if a.option == "none" else f"weighted by the 00:19 data, option {a.option}"
    held += ("; log-on caused by fuel exhaustion (section 6 lag likelihood)" if a.logon == "fuel-exhaustion"
             else "; log-on unscored (cause 'other')")
    stamp = (f"end-of-flight impacts, {len(lat):,} samples, seeds {','.join(map(str, seeds))} pooled equally, "
             f"N = {n_children}.\n{held[0].upper() + held[1:]}.\nSMOKE SCALE, not evidence. {a.label}. Equal family priors. Code {rev}.")
    dsp = load_impacts.disp; ok = np.isfinite(dsp)
    own = wq(dsp[ok], w[ok], [0.5, 0.9, 0.99]) if ok.any() else [float("nan")] * 3
    own_share = float(w[ok].sum() / w.sum())
    nums = {"displacement_from_own_0019_nm_50_90_99": own, "share_with_own_0019_position": own_share,
            "logon_cause": a.logon, "seeds": seeds, "samples": int(len(lat)), "option": a.option, "code_revision": rev, "children": n_children,
            "lat_5_50_95": wq(lat, w, [0.05, 0.5, 0.95]), "lon_5_50_95": wq(lon, w, [0.05, 0.5, 0.95])}

    # 1. Overview, the reference run's frame.
    box = (-42.0, -22.0, 80.0, 104.0)
    fig = plt.figure(figsize=(6.6, 7.4)); ax = fig.add_axes([0.12, 0.15, 0.84, 0.76])
    draw(ax, lat, lon, w, box, 0.05, 0.12, arc6, arc7)
    frame(ax, box, 5.0, 1.0, -32.0)
    legend(ax, arc6, arc7)
    ax.set_title("Impact location: end-of-flight stage from the 00:11 hand-off", loc="left", fontsize=10)
    fig.text(0.07, 0.012, stamp, fontsize=6.3, color="#555555")
    for e in ("pdf", "png"):
        fig.savefig(out / f"impact-overview{tag}.{e}", dpi=200)
    plt.close(fig)

    # 2. Close-up on the 90% region, 00:19:37 positions faint behind it.
    lc, oc, d = grid(lat, lon, w, box, 0.05, 0.12)
    lv = hpd_levels(d, LEVELS)
    r, c = np.where(d >= lv[1])
    la0, la1, lo0, lo1 = lc[r.min()], lc[r.max()], oc[c.min()], oc[c.max()]
    pad = 0.6
    mid = 0.5 * (la0 + la1)
    cbox = (np.floor(la0 - pad), np.ceil(la1 + pad), np.floor(lo0 - pad / np.cos(np.deg2rad(mid))),
            np.ceil(lo1 + pad / np.cos(np.deg2rad(mid))))
    nums["closeup_box"] = list(map(float, cbox)); nums["hdr90_extent"] = [float(la0), float(la1), float(lo0), float(lo1)]
    fig = plt.figure(figsize=(7.2, 7.4)); ax = fig.add_axes([0.11, 0.17, 0.85, 0.75])
    draw(ax, lat, lon, w, (cbox[0] - 1, cbox[1] + 1, cbox[2] - 1, cbox[3] + 1), 0.025, 0.06, arc6, arc7)
    ax.scatter(fin[:, 1], fin[:, 0], s=0.8, c="#1f4e8c", alpha=0.18, lw=0, zorder=3, rasterized=True)
    frame(ax, cbox, 1.0, 0.5, mid)
    legend(ax, arc6, arc7, [Line2D([], [], ls="", marker="o", ms=3, color="#1f4e8c", alpha=0.5,
                                    label="aircraft at 00:19:37 (reference posterior)")])
    ax.set_title("Impact location, close-up on the 90 % region", loc="left", fontsize=10)
    fig.text(0.07, 0.012, stamp + f"\nFaint dots: {len(fin):,} weight-proportional draws from the 00:19:37 reference "
             "posterior of the same seeds:\nwhere the cruise-only filter places the aircraft at the last transmission. "
             f"This module's own trajectories at 00:19:37 need not sit there; impacts lie\n{own[0]:.0f} / {own[1]:.0f} / "
             f"{own[2]:.0f} NM (50 / 90 / 99 %) from each trajectory's own 00:19:37 position ({own_share:.0%} of weight flew through it).",
             fontsize=6.3, color="#555555")
    for e in ("pdf", "png"):
        fig.savefig(out / f"impact-closeup{tag}.{e}", dpi=220)
    plt.close(fig)

    # 3. By control axis, same frame.
    fig, axs = plt.subplots(2, 2, figsize=(9.0, 9.2))
    nums["by_control"] = {}
    for k, ax in enumerate(axs.ravel()):
        m = ctrl == k
        share = float(w[m].sum() / w.sum())
        draw(ax, lat[m], lon[m], w[m], (cbox[0] - 1, cbox[1] + 1, cbox[2] - 1, cbox[3] + 1), 0.025, 0.06, arc6, arc7)
        ax.scatter(fin[:, 1], fin[:, 0], s=0.5, c="#1f4e8c", alpha=0.14, lw=0, zorder=3, rasterized=True)
        frame(ax, cbox, 1.0, 0.5, mid)
        ax.set_title(f"{CONTROL[k].replace('-', ' ')}  (weight {share:.3f})", loc="left", fontsize=9)
        nums["by_control"][CONTROL[k]] = {"weight": share, "lat_5_50_95": wq(lat[m], w[m], [0.05, 0.5, 0.95]),
                                          "lon_5_50_95": wq(lon[m], w[m], [0.05, 0.5, 0.95])}
        if k == 0:
            legend(ax, arc6, arc7)
    fig.suptitle("Impact location by the control axis (each panel normalised to its own 50/90/99 %)", x=0.06, ha="left",
                 fontsize=10)
    fig.text(0.06, 0.012, stamp, fontsize=6.3, color="#555555")
    fig.subplots_adjust(left=0.07, right=0.98, top=0.93, bottom=0.08, hspace=0.22, wspace=0.18)
    for e in ("pdf", "png"):
        fig.savefig(out / f"impact-by-control{tag}.{e}", dpi=200)
    plt.close(fig)
    (out / f"impact-maps{tag}.json").write_text(json.dumps(nums, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
