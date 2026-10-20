"""Figure: fuel exhaustion then no control (A1) under the both-frequency 00:19 treatments, from the A1-branch pass (18 Oct 2026).

    python a1_branch_figure.py BRANCH_STRATUM_DIR PROD_STRATUM_DIR CORE_STRATUM_DIR COMBINED_JSON OUT_DIR

Panels a-c: impact HPD maps (50/90/99 %) of the branch under D3, D4, D5 from the branch pass (8 seeds); panel d: latitude density of
the branch, branch pass (solid) against production's branch rows (dashed, 24 seeds), per treatment. Searched sea floor and arcs as in
run_j_figures.py.
"""
import json, sys, pathlib, textwrap
import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compact_impacts import load
from run_i_maps import cell_logmass, read_cov

LAT0, LON0, G, NLAT, NLON = -42.0, 80.0, 0.02, 1350, 1500
LB = np.arange(-42.0, -15.0 + 1e-9, 0.02)
CELLS = {"D3": "Both 00:19 frequencies as recorded", "D4": "Both 00:19 frequencies, shared start-up offset",
         "D5": "00:19:29 frequency as recorded, 00:19:37 frequency with offset"}
COL = {"D3": "#d95f02", "D4": "#7570b3", "D5": "#1b9e77"}


def accumulate(stratum, core, seeds, restrict, grid):
    H = {d: np.zeros(NLAT * NLON) for d in CELLS} if grid else None; L = {d: np.zeros(len(LB) - 1) for d in CELLS}
    for sd in seeds:
        meta, g = load(sd); lm = cell_logmass(g, meta, pathlib.Path(core) / "bto-bfo" / sd.name / "handoff-m0011" / "handoff.npy")
        br = (g("latent:onset_mechanism") == 2) & (g("latent:control_realised") == 2)
        lat = g("latitude_deg"); lon = g("longitude_deg")
        i = np.floor((lat - LAT0) / G).astype(np.int64); j = np.floor((lon - LON0) / G).astype(np.int64)
        ok = (i >= 0) & (i < NLAT) & (j >= 0) & (j < NLON) & (br if restrict else True)
        for d in CELLS:
            a = lm[d]; fin = np.isfinite(a) & ok
            if not fin.any(): continue
            m = np.zeros(len(a)); m[fin] = np.exp(a[fin] - a[fin].max()); m /= m.sum()   # equal weight per seed, normalised within the seed
            # weight seeds by their evidence: multiply back by exp(max) / sum (kept in log form)
            w_seed = np.exp(a[fin].max()) * np.exp(a[fin] - a[fin].max()).sum()
            if grid: H[d] += np.bincount((i * NLON + j)[fin], m[fin] * w_seed, NLAT * NLON)
            L[d] += np.histogram(lat[fin], LB, weights=m[fin] * w_seed)[0]
        print(f"  {sd}", flush=True)
    return H, L


def main(branch, prod, core, comb, out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True); C = json.load(open(comb))["cells"]
    bseeds = sorted((p for p in pathlib.Path(branch).glob("seed-*") if p.is_dir()), key=lambda p: int(p.name[5:]))
    pseeds = sorted((p for p in pathlib.Path(prod).glob("seed-*") if p.is_dir()), key=lambda p: int(p.name[5:]))
    cache = out / "a1-branch-figure-cache.npz"
    if cache.exists():
        z = np.load(cache); Hb = {d: z[f"H_{d}"] for d in CELLS}; Lb = {d: z[f"Lb_{d}"] for d in CELLS}; Lp = {d: z[f"Lp_{d}"] for d in CELLS}
    else:
        Hb, Lb = accumulate(branch, core, bseeds, False, True); _, Lp = accumulate(prod, core, pseeds, True, False)
        np.savez_compressed(cache, **{f"H_{d}": Hb[d] for d in CELLS}, **{f"Lb_{d}": Lb[d] for d in CELLS}, **{f"Lp_{d}": Lp[d] for d in CELLS})
    lat_c = LAT0 + G * (np.arange(NLAT) + 0.5); lon_c = LON0 + G * (np.arange(NLON) + 0.5)
    here = pathlib.Path(__file__).resolve(); covdir = here.parents[2] / "seabed-search" / "coverage"
    covs = {"Phase 2 seabed search (2014-17)": ("phase2.cov", "#000000"), "Ocean Infinity 2018": ("ocean-infinity-2018.cov", "#7a3b00"),
            "Ocean Infinity 2025": ("ocean-infinity-2025.cov", "#1b6b3a")}
    rasters = {}
    for k, (f, c) in covs.items():
        if (covdir / f).exists():
            s0, w0, stp, q = read_cov(covdir / f); rasters[k] = ((s0 + stp * (np.arange(q.shape[0]) + 0.5), w0 + stp * (np.arange(q.shape[1]) + 0.5), q), c)
    arcs = {x["epoch"]: np.asarray(x["lat_lon"], float) for x in json.loads((pathlib.Path(core) / "run.json").read_text())["reference_arcs"]}
    matplotlib.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "pdf.fonttype": 42})
    LEV = (0.99, 0.90, 0.50); FILL = ["#dcdcdc", "#a8a8a8", "#6a6a6a"]
    fig = plt.figure(figsize=(7.4, 6.4)); gs = fig.add_gridspec(2, 3, height_ratios=[1.25, 1], hspace=0.38, wspace=0.08)
    R = {}
    for k, d in enumerate(CELLS):
        ax = fig.add_subplot(gs[0, k]); Hd = Hb[d].reshape(NLAT, NLON)
        dens = gaussian_filter(Hd / Hd.sum(), 0.08 / G); flat = np.sort(dens.ravel())[::-1]; cm = np.cumsum(flat)
        lv = [float(flat[min(np.searchsorted(cm, f * cm[-1]), len(flat) - 1)]) for f in LEV]
        ax.contourf(lon_c, lat_c, dens, levels=[lv[0], lv[1], lv[2], dens.max()], colors=FILL); ax.contour(lon_c, lat_c, dens, levels=lv, colors="#2b2b2b", linewidths=0.6)
        for kk, ((la, lo, q), c) in rasters.items(): ax.contour(lo, la, q, levels=[0.5], colors=c, linewidths=1.1)
        for ep, sty in (("m0011", dict(color="#4a6fa5", lw=0.9, ls="--")), ("m0019a", dict(color="#b16286", lw=1.0))):
            if ep in arcs: ax.plot(arcs[ep][:, 1], arcs[ep][:, 0], **sty)
        km2 = (G * 111.32) ** 2 * np.cos(np.radians(lat_c))[:, None] * np.ones((1, NLON)); a90 = float(km2[dens >= lv[1]].sum() / 1e3)
        c = C[d]; R[d] = {"area90_thousand_km2": a90, "ess": c["branch_pass_ess_rows"], "lat": c["branch_pass_lat_q05_q50_q95"],
                          "share_stratified": c["stratified"]["A1"], "share_production": c["production"]["A1"]}
        ax.text(0.97, 0.03, f"share of the treatment {c['stratified']['A1']*100:.1f} %\n90 % area {a90:.0f} thousand km²\nmedian {abs(c['branch_pass_lat_q05_q50_q95'][1]):.2f}°S; ESS {c['branch_pass_ess_rows']:,.0f}",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=5.6)
        ax.set_xlim(86.5, 99); ax.set_ylim(-40, -31); ax.set_aspect(1 / np.cos(np.radians(-35.5)))
        ax.set_title(f"{'abc'[k]}  {textwrap.fill(CELLS[d], 38)}", fontsize=6.3, loc="left")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):.0f}°S")); ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}°E"))
        ax.set_xticks([88, 92, 96]); ax.grid(True, color="#eeeeee", lw=0.5)
        if k: ax.set_yticklabels([])
    axd = fig.add_subplot(gs[1, :]); lc = 0.5 * (LB[1:] + LB[:-1])
    for d in CELLS:
        for L, ls, lab in ((Lb[d], "-", "branch pass"), (Lp[d], "--", "production")):
            p = gaussian_filter1d(L / L.sum() / 0.02, 0.08 / 0.02)
            axd.plot(lc, p, color=COL[d], ls=ls, lw=1.3 if ls == "-" else 0.9)
    axd.set_xlim(-39, -33); axd.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):.0f}°S"))
    axd.set_xlabel("ocean impact latitude"); axd.set_ylabel("probability density (per degree)")
    axd.set_title("d  Latitude of these impacts: the new pass (solid) agrees with production (dashed), which was too thin to show the shape", fontsize=6.6, loc="left")
    axd.legend(handles=[Line2D([], [], color=COL[d], lw=1.3, label=CELLS[d]) for d in CELLS] +
               [Line2D([], [], color="k", lw=1.3, label="new pass, 8 seeds"), Line2D([], [], color="k", lw=0.9, ls="--", label="production, 24 seeds")],
               fontsize=5.6, loc="upper right")
    h = [Patch(facecolor=f, edgecolor="#2b2b2b", lw=0.6, label=f"{int(l*100)} % of probability") for f, l in zip(FILL[::-1], LEV[::-1])]
    h += [Line2D([], [], color=c, lw=1.1, label=k) for k, (_, c) in rasters.items()]
    h += [Line2D([], [], color="#b16286", lw=1.0, label="7th arc, 00:19:29 UTC"), Line2D([], [], color="#4a6fa5", lw=0.9, ls="--", label="6th arc, 00:10:59 UTC")]
    fig.legend(handles=h, loc="upper center", ncol=4, fontsize=5.6, bbox_to_anchor=(0.5, 0.995))
    fig.suptitle("Fuel exhaustion, then no control: where these impacts hit the ocean when both 00:19 frequencies are used", x=0.01, ha="left", fontsize=7.5, y=0.925)
    n1 = ("Note 1: These maps show only one type of flight end: the engines stop for lack of fuel and nobody controls the aircraft. A new set of "
          "simulations was aimed at this type, because the main run had too few independent samples for it when both 00:19 frequencies are used "
          "as recorded. The new set agrees with the main run where both can be compared. The search result is not applied. The flight model for a "
          "descent without control is not calibrated, so these results can change.")
    n2 = ("Note 2: A1 no-intervention branch (onset flame-out-associated, control no intervention): conditional pass on core run J waypoints "
          "(accepted as a pass by project ruling, 16 Oct 2026), seeds 1-8 x 100,000 hand-off particles, 16 children x 4 descents, D3-aimed scored selection "
          "(K = 8; BFO-model priors 0.98/0.01/0.01; exact correction), production laws (round-3, bank limit U[52,90] deg, dive p = 0.5), mh370-eof-rj1; seeds 2-8 "
          "Horvitz-Thompson thinned to 1M rows. Stratified estimator Z(d, branch) = Z(D0') P_D0'(branch) E_D0'[L_d | branch]; shares = branch + A1 outside the "
          "branch (production). q = 1/3, C2 silent. Uncontrolled-arm dynamics NOT CALIBRATED (Boeing leave-one-out gate failed in all three rounds).")
    fig.text(0.01, 0.005, textwrap.fill(n1, 200) + "\n" + textwrap.fill(n2, 200), fontsize=4.7, va="bottom")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.2)
    for ext in ("png", "pdf"): fig.savefig(out / f"a1-branch-both-frequencies.{ext}", dpi=300)
    json.dump(R, open(out / "a1-branch-figure.json", "w"), indent=1); print(json.dumps(R, indent=0))


if __name__ == "__main__":
    main(*sys.argv[1:6])
