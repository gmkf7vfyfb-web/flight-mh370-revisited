"""Standard end-of-flight figure set on a production pass (Pete, 17 Oct 2026; the run I set re-made for run J).

    python run_j_figures.py ACC_DIR TABLE_DIR CORE_ROOT OUT_DIR

ACC_DIR holds run-j-maps-accumulators.{npz,json} from run_j_maps_pass.py; TABLE_DIR holds table-0019-mixture.{json,
-latitude.npz} (option_table_0019.py). Writes, each as PNG + PDF:
  run-j-impact-maps            2x2 HPD maps: held out, 00:19:29 range+frequency, both frequencies with shared offset, and the
                               evidence-weighted average of the three both-frequency treatments; searched sea floor; arcs
  run-j-impact-latitude-0019   impact-latitude density per 00:19 treatment
  run-j-impact-maps-by-family  3 families x 6 treatments, each panel normalised to itself; ESS < 1,000 flagged
  run-j-impact-loudness-maps   scatter maps, peak radiated power classes set on the held-out case; share in loudest decile
  run-j-impact-energy-maps     scatter maps coloured by energy transferred; weighted distribution of energy per treatment
and run-j-figures.json (every number printed on the figures).
"""
import json, sys, pathlib, struct, textwrap
import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d
from scipy.special import logsumexp
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import LogNorm

CELLS = ("D0", "D1", "D2", "D3", "D4", "D5")
TNAME = {"D0": "00:19 data not used", "D1": "00:19:29 range only", "D2": "00:19:29 range and frequency",
         "D3": "Both 00:19 frequencies as recorded", "D4": "Both 00:19 frequencies, shared start-up offset",
         "D5": "00:19:29 frequency as recorded, 00:19:37 frequency with offset"}
FNAME = {"A1": "Fuel exhaustion, then no control", "A2": "Fuel exhaustion, then controlled to the surface",
         "B": "Deliberate descent before fuel exhaustion"}
LEV = (0.99, 0.90, 0.50); FILL = ["#dcdcdc", "#a8a8a8", "#6a6a6a"]; LW = [0.5, 0.7, 0.9]
SIG = 0.08
CAVEAT = ("The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all three rounds. Impact energy, "
          "attitude, flight-path angle and energy-transfer duration from this arm are a labelled sensitivity on uncalibrated dynamics, "
          "not a physical prediction.")
TECH = ("End of flight on core run J (accepted as a pass by project ruling, 16 Oct 2026): 4 route families with 24/18/16/16 seeds x 100,000 "
        "hand-off particles at 00:11; 16 children x 4 descents per particle (waypoints), 8 x 4 (others); family weights 0.9982/0.0013/0.0003/0.0002; "
        "binary mh370-eof-rj1 (sha256 19031f41). Round-3 uncontrolled-descent laws; spiral bank limit uniform 52-90 deg; dive to surface p = 0.5. "
        "Log-on causes C1 fuel exhaustion (Erlang lag) + C2 other (1/W, W = 00:10:58-01:15:56 UTC, silent), q = 1/3; survival factor (no in-flight "
        "breakup before 00:19:37) applied; transmission at 00:19 imposed. No treatment uses the 00:19:37 range. Treatments: D0' held out, D1 R600 BTO, "
        "D2 R600 BTO+BFO, D3 both BFOs raw, D4 both BFOs + shared start-up offset (Holland), D5 R600 BFO raw + R1200 BFO with offset U[17,130] Hz. "
        "Families: A1 = code 1, A2 = code 2, B = codes 3+6 (B uncontrolled about 0.001). PROVISIONAL: piloted-turn model, INTERIM pitch-down.")


def style():
    matplotlib.rcParams.update({"font.family": "sans-serif", "font.size": 7, "axes.labelsize": 7, "axes.titlesize": 7, "legend.fontsize": 6,
                                "xtick.labelsize": 6, "ytick.labelsize": 6, "axes.linewidth": 0.6, "axes.spines.top": False,
                                "axes.spines.right": False, "legend.frameon": False, "savefig.dpi": 300, "pdf.fonttype": 42,
                                "axes.titlelocation": "left", "lines.linewidth": 1.2})


def read_cov(path):
    b = pathlib.Path(path).read_bytes(); assert b[:8] == b"MH370COV"
    ver, south, west, step, rows, cols, runs = struct.unpack("<IdddIII", b[8:8 + 40])
    rec = np.frombuffer(b[48:48 + 3 * runs], dtype=np.dtype([("v", "u1"), ("n", "<u2")]))
    q = np.repeat(rec["v"], rec["n"]).astype(np.float32) / 255.0
    return south + step * (np.arange(rows) + 0.5), west + step * (np.arange(cols) + 0.5), q.reshape(rows, cols)


def wq(x, w, qs):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]
    return [float(x[o][min(np.searchsorted(c, q), len(x) - 1)]) for q in qs]


def notes(fig, n1, n2, y=0.004, width=190, fs=5.0):
    fig.text(0.015, y, textwrap.fill("Note 1: " + n1, width) + "\n" + textwrap.fill("Note 2: " + n2, width), fontsize=fs, va="bottom", ha="left")


def fess(e):
    return f"{e/1e6:.2f}M" if e >= 1e6 else (f"{e/1e3:.1f}k" if e >= 1e3 else f"{e:,.0f}")


def geo(ax):
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):.0f}°S"))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}°E"))
    ax.grid(True, color="#eeeeee", lw=0.5); ax.set_axisbelow(True)


def main(acc_dir, table_dir, core_root, out):
    style(); out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    A = np.load(pathlib.Path(acc_dir) / "run-j-maps-accumulators.npz"); AJ = json.load(open(pathlib.Path(acc_dir) / "run-j-maps-accumulators.json"))
    tab = json.load(open(pathlib.Path(table_dir) / "table-0019-mixture.json"))["cells"]
    LZ = {d: tab[f"{d} total q=0.333 (C2 silent)"]["ln_Z"] for d in CELLS}
    G = float(A["grid"]); NLAT, NLON = int(A["nlat"]), int(A["nlon"]); LAT0, LON0 = float(A["lat0"]), float(A["lon0"])
    lat_c = LAT0 + G * (np.arange(NLAT) + 0.5); lon_c = LON0 + G * (np.arange(NLON) + 0.5)
    cell_km2 = (G * 111.32) ** 2 * np.cos(np.radians(lat_c))[:, None] * np.ones((1, NLON))
    here = pathlib.Path(__file__).resolve(); covdir = here.parents[2] / "seabed-search" / "coverage"
    covs = {"Phase 2 seabed search (2014-17)": ("phase2.cov", "#000000"), "Ocean Infinity 2018": ("ocean-infinity-2018.cov", "#7a3b00"),
            "Ocean Infinity 2025": ("ocean-infinity-2025.cov", "#1b6b3a")}
    rasters = {k: (read_cov(covdir / f), c) for k, (f, c) in covs.items() if (covdir / f).exists()}
    arcs = {x["epoch"]: np.asarray(x["lat_lon"], float) for x in json.loads((pathlib.Path(core_root) / "run-j-waypoints" / "run.json").read_text())["reference_arcs"]}
    ess = {k: v["eff_impacts"] for k, v in AJ["cells"].items()}
    R = {"panels": {}, "family_panels": {}, "loudness": {}, "energy": {}}

    def hpd(ax, Hd, searched=True, lw_scale=1.0):
        dens = gaussian_filter(Hd / Hd.sum(), SIG / G)
        flat = np.sort(dens.ravel())[::-1]; cm = np.cumsum(flat)
        lv = [float(flat[min(np.searchsorted(cm, f * cm[-1]), len(flat) - 1)]) for f in LEV]
        ax.contourf(lon_c, lat_c, dens, levels=[lv[0], lv[1], lv[2], dens.max()], colors=FILL)
        ax.contour(lon_c, lat_c, dens, levels=lv, colors="#2b2b2b", linewidths=[x * lw_scale for x in LW])
        if searched:
            for k, ((la, lo, q), c) in rasters.items():
                ax.contour(lo, la, q, levels=[0.5], colors=c, linewidths=1.4 * lw_scale)
        for ep, sty in (("m0011", dict(color="#4a6fa5", lw=1.0 * lw_scale, ls="--")), ("m0019a", dict(color="#b16286", lw=1.2 * lw_scale))):
            if ep in arcs: ax.plot(arcs[ep][:, 1], arcs[ep][:, 0], **sty)
        hl = Hd.sum(axis=1); hc = np.cumsum(hl); hc /= hc[-1]
        return {"hpd_area_thousand_km2": {f"{int(f*100)}%": float(cell_km2[dens >= l].sum() / 1e3) for f, l in zip(LEV, lv)},
                "lat_median": float(lat_c[np.searchsorted(hc, 0.5)]), "lat_q05": float(lat_c[np.searchsorted(hc, 0.05)]),
                "lat_q95": float(lat_c[np.searchsorted(hc, 0.95)]), "lat_peak": float(lat_c[np.argmax(gaussian_filter1d(hl, SIG / G))])}

    def legend_items(lw_scale=1.0):
        h = [Patch(facecolor=f, edgecolor="#2b2b2b", lw=0.6, label=f"{int(l*100)} % of probability") for f, l in zip(FILL[::-1], LEV[::-1])]
        h += [Line2D([], [], color=c, lw=1.4, label=k) for k, (_, c) in rasters.items()]
        h += [Line2D([], [], color="#b16286", lw=1.2, label="7th arc, 00:19:29 UTC"), Line2D([], [], color="#4a6fa5", lw=1.0, ls="--", label="6th arc, 00:10:59 UTC")]
        return h

    # ---------------- F1: impact maps by treatment ----------------
    zmix = logsumexp([LZ["D3"], LZ["D4"], LZ["D5"]]); post = {d: float(np.exp(LZ[d] - zmix)) for d in ("D3", "D4", "D5")}
    Hmix = sum(post[d] * A[f"H_{d}_all"].astype(np.float64) for d in post)
    panels = [("a", TNAME["D0"], A["H_D0_all"].astype(np.float64), ess["D0/all"], "D0"),
              ("b", TNAME["D2"], A["H_D2_all"].astype(np.float64), ess["D2/all"], "D2"),
              ("c", TNAME["D4"], A["H_D4_all"].astype(np.float64), ess["D4/all"], "D4"),
              ("d", f"Average of the three both-frequency treatments,\nweighted by evidence (as recorded {post['D3']:.2f}, shared\noffset {post['D4']:.2f}, "
                    f"offset on 00:19:37 only {post['D5']:.2f})", Hmix, None, "mixed")]
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 8.8), sharex=True, sharey=True)
    for ax, (let, title, Hd, e, key) in zip(axs.ravel(), panels):
        r = hpd(ax, Hd); r["eff_impacts"] = e; R["panels"][key] = r
        ax.set_title(f"{let}  {title}", fontsize=7)
        ax.text(0.98, 0.02, f"median {abs(r['lat_median']):.2f}°S, peak {abs(r['lat_peak']):.2f}°S\n90 % area {r['hpd_area_thousand_km2']['90%']:.0f} thousand km²"
                + (f"\nESS {fess(e)}" if e else ""), transform=ax.transAxes, ha="right", va="bottom", fontsize=6)
        geo(ax)
    for ax in axs.ravel():
        ax.set_xlim(86.5, 99.0); ax.set_ylim(-40.2, -30.0); ax.set_aspect(1 / np.cos(np.radians(-36)))
    for ax in axs[1]: ax.set_xlabel("longitude")
    for ax in axs[:, 0]: ax.set_ylabel("latitude")
    fig.legend(handles=legend_items(), loc="upper center", ncol=3, fontsize=6, bbox_to_anchor=(0.5, 0.955))
    fig.suptitle("Where the aircraft hit the ocean, for each use of the 00:19 satellite data (before the search evidence)", x=0.02, ha="left", fontsize=8, y=0.995)
    notes(fig, "Each panel shows the area that holds 50, 90 and 99 % of the probability of the ocean impact. The panels use the two 00:19 "
          "satellite messages in different ways. The heavy black, brown and green lines show sea floor that was searched. The search result is "
          "not applied here. The log-on cause mixes fuel exhaustion (weight 3) and other causes (weight 1). The flight model is not yet stable, so the "
          "results can change.",
          TECH + f" Panel d = equal-prior average of D3/D4/D5 by ln Z (posterior weights {post['D3']:.3f}/{post['D4']:.3f}/{post['D5']:.3f}). Density 0.02 deg grid, "
          "Gaussian sigma 0.08 deg, HPD 50/90/99 %. Searched ground: coverage >= 0.5 outlines of the seabed-search rasters. ESS = Kish effective impacts "
          "pooled over seeds. Masses reproduce table-0019-mixture.json (ln Z and ESS identical).", width=175)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.87, bottom=0.19, hspace=0.2, wspace=0.06)
    for ext in ("png", "pdf"): fig.savefig(out / f"run-j-impact-maps.{ext}", dpi=250)
    plt.close(fig); R["mixed_weights"] = post

    # ---------------- F2: latitude density ----------------
    z = np.load(pathlib.Path(table_dir) / "table-0019-mixture-latitude.npz"); lat = z["lat"]; dl = lat[1] - lat[0]
    cols = {"D0": "#4d4d4d", "D1": "#9a9a9a", "D2": "#1f77b4", "D3": "#d95f02", "D4": "#7570b3", "D5": "#1b9e77"}
    fig, ax = plt.subplots(figsize=(6.8, 3.8)); R["latitude"] = {}
    for d in CELLS:
        k = f"{d} total q=0.333 (C2 silent)"; p = gaussian_filter1d(z[f"{d}_total_q0.333_C2_silent"], SIG / dl); p = p / (p.sum() * dl)
        q = tab[k]["latitude_q05_q50_q95"]; pk = float(lat[np.argmax(p)])
        R["latitude"][d] = {"peak": pk, "q05_q50_q95": q, "eff_impacts": tab[k]["eff_impacts"]}
        ax.plot(lat, p, color=cols[d], lw=1.6 if d in ("D0", "D4") else 1.0, ls="--" if d == "D1" else "-",
                label=f"{TNAME[d]}: peak {abs(pk):.2f}°S, median {abs(q[1]):.2f}°S")
    ax.set_xlim(-40, -30.5); ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):.0f}°S"))
    ax.set_xlabel("ocean impact latitude"); ax.set_ylabel("probability density (per degree)")
    pk0, pk4 = R["latitude"]["D0"]["peak"], R["latitude"]["D4"]["peak"]
    pks = [abs(R["latitude"][d]["peak"]) for d in CELLS]
    ax.set_title(f"The impact peak lies at {min(pks):.1f}-{max(pks):.1f}°S for every use of the 00:19 data; the northern tail is long", fontsize=7.5)
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.2), fontsize=5.2, handlelength=2.0); ax.margins(y=0.04)
    notes(fig, "Each line shows where the aircraft hit the ocean for one way to use the two satellite messages at 00:19. The log-on cause mixes "
          "fuel exhaustion (weight 3) and other causes (weight 1). A steep descent can continue to the sea or level off (equal weight). The peak is "
          "the most likely latitude. The long northern tail moves the median north. The flight model is not yet stable, so the results can change.",
          TECH + " Kernel smoothing 0.08 deg on a 0.01 deg histogram. ESS: " + " / ".join(f"{d} {fess(R['latitude'][d]['eff_impacts'])}" for d in CELLS) + ".",
          width=170, fs=5.0)
    fig.subplots_adjust(bottom=0.36, top=0.92, left=0.10, right=0.98)
    for ext in ("png", "pdf"): fig.savefig(out / f"run-j-impact-latitude-0019.{ext}", dpi=300)
    plt.close(fig)

    # ---------------- F3: maps by family ----------------
    fig, axs = plt.subplots(3, 6, figsize=(16.5, 11.0), sharex=True, sharey=True)
    for r_, f in enumerate(("A1", "A2", "B")):
        for c_, d in enumerate(CELLS):
            ax = axs[r_, c_]; Hd = A[f"H_{d}_{f}"].astype(np.float64); e = ess[f"{d}/{f}"]
            share = AJ["cells"][f"{d}/{f}"]["mass_rel_table"]
            rr = hpd(ax, Hd, lw_scale=0.8); rr.update(share=share, eff_impacts=e, estimable=bool(e >= 1000)); R["family_panels"][f"{d}/{f}"] = rr
            ax.set_title(f"({'abcdefghijklmnopqr'[r_*6+c_]}) {textwrap.fill(TNAME[d], 34, break_on_hyphens=False)}" if r_ == 0 else f"({'abcdefghijklmnopqr'[r_*6+c_]})", fontsize=6.5)
            ax.text(0.97, 0.03, f"share of the treatment {share*100:.0f} %\n90 % area {rr['hpd_area_thousand_km2']['90%']:.0f} thousand km²\n"
                    f"median {abs(rr['lat_median']):.1f}°S; ESS {e:,.0f}", transform=ax.transAxes, ha="right", va="bottom", fontsize=5.5)
            if e < 1000:
                ax.text(0.5, 0.80, f"Not estimable\nESS {e:,.0f} (< 1,000)", transform=ax.transAxes, ha="center", color="#b2182b", fontsize=7, fontweight="bold")
            geo(ax); ax.set_xlim(82, 108); ax.set_ylim(-41.5, -18); ax.set_aspect(1 / np.cos(np.radians(-32)))
        axs[r_, 0].set_ylabel(f"{FNAME[f]}\n\nlatitude", fontsize=7)
    for ax in axs[2]: ax.set_xlabel("longitude")
    fig.legend(handles=legend_items(), loc="lower center", ncol=8, fontsize=6.5, bbox_to_anchor=(0.5, 0.075))
    fig.suptitle("Where the aircraft hit the ocean, by type of flight end (rows) and by use of the 00:19 satellite data (columns)", x=0.015, ha="left", fontsize=9, y=0.99)
    notes(fig, "Each panel shows only one type of flight end, and is scaled to its own total. The grey areas hold 50, 90 and 99 % of that type's impact "
          "probability. The share tells how much of the column's probability that type holds. When too few independent samples support a panel, the panel "
          "is marked 'Not estimable'. The search result is not applied. The flight model is not yet stable, so the results can change.",
          TECH + " Each panel normalised to itself; density 0.02 deg grid, Gaussian sigma 0.08 deg; ESS = Kish effective impacts of the family-restricted "
          "weights pooled over seeds; below 1,000 not estimable (declared coverage gap). Shares reproduce table-0019-mixture.json.", width=300, fs=5.5)
    fig.subplots_adjust(left=0.06, right=0.99, top=0.94, bottom=0.13, hspace=0.12, wspace=0.05)
    for ext in ("png", "pdf"): fig.savefig(out / f"run-j-impact-maps-by-family.{ext}", dpi=200)
    plt.close(fig)

    # ---------------- F4/F5: loudness and energy scatter maps ----------------
    RS = {d: A[f"RS_{d}"].astype(np.float64) for d in CELLS}   # columns: mass lat lon fam stratum peak energy fpa speed
    r0 = RS["D0"]; ok0 = np.isfinite(r0[:, 5]) & np.isfinite(r0[:, 6])
    tp = wq(r0[ok0, 5], r0[ok0, 0], (0.5, 0.9)); te = wq(r0[ok0, 6], r0[ok0, 0], (0.5, 0.9))
    R["loudness"]["held_out_peak_w_q50_q90"] = tp; R["loudness"]["held_out_energy_j_q50_q90"] = te
    sh = {}
    for d in CELLS:
        x = RS[d]; ok = np.isfinite(x[:, 5]) & np.isfinite(x[:, 6]); m = x[ok, 0]
        sh[d] = (float(m[x[ok, 5] > tp[1]].sum() / m.sum()), float(m[x[ok, 6] > te[1]].sum() / m.sum()))
        R["loudness"][d] = {"share_top_decile_peak_power": sh[d][0], "share_top_decile_energy": sh[d][1],
                            "energy_gj_q05_q50_q95": [v / 1e9 for v in wq(x[ok, 6], m, (0.05, 0.5, 0.95))],
                            "peak_power_w_q05_q50_q95": wq(x[ok, 5], m, (0.05, 0.5, 0.95)), "eff_impacts": ess[f"{d}/all"]}
    rng = np.random.default_rng(7); SP = ("D0", "D2", "D3", "D4", "D5"); NDRAW = 3000
    draws = {}
    for d in SP:
        x = RS[d]; ok = np.where(np.isfinite(x[:, 5]) & np.isfinite(x[:, 6]))[0]; p = x[ok, 0] / x[ok, 0].sum()
        draws[d] = x[ok[rng.choice(len(ok), NDRAW, p=p)]]
    cmap3 = ["#c6dbef", "#4292c6", "#b2182b"]; short = {"D0": "held out", "D1": "00:19:29 range", "D2": "00:19:29 range + frequency",
                                                          "D3": "both frequencies, recorded", "D4": "both, shared offset", "D5": "offset on 00:19:37 only"}
    for kind in ("loudness", "energy"):
        fig, axs = plt.subplots(2, 3, figsize=(7.4, 6.0), gridspec_kw={"wspace": 0.08, "hspace": 0.25})
        for k, d in enumerate(SP):
            ax = axs.flat[k]; x = draws[d]
            if kind == "loudness":
                c = np.digitize(x[:, 5], tp)
                for j in (0, 1, 2):
                    s = c == j; ax.scatter(x[s, 2], x[s, 1], s=2 if j < 2 else 4, c=cmap3[j], edgecolors="none", zorder=2 + j, alpha=0.85)
                txt = f"loudest-decile share {sh[d][0]:.2f}\nESS {fess(ess[d + '/all'])}"
            else:
                o = np.argsort(x[:, 6]); sc = ax.scatter(x[o, 2], x[o, 1], s=2.5, c=np.maximum(x[o, 6], 1e7) / 1e9, cmap="viridis",
                                                         norm=LogNorm(0.1, 30), edgecolors="none")
                q = R["loudness"][d]["energy_gj_q05_q50_q95"]
                txt = f"median {q[1]:.1f} GJ (5-95 %: {q[0]:.1f}-{q[2]:.1f})\nESS {fess(ess[d + '/all'])}"
            ax.text(0.03, 0.04, txt, transform=ax.transAxes, fontsize=5.8)
            ax.set_title(f"{'abcde'[k]}  {textwrap.fill(TNAME[d], 38, break_on_hyphens=False)}", fontsize=7)
            ax.set_xlim(84, 100); ax.set_ylim(-41, -28); geo(ax); ax.set_xticks([86, 90, 94, 98])
            if k % 3: ax.set_yticklabels([])
            else: ax.set_ylabel("latitude")
            if k < 3: ax.set_xticklabels([])
            else: ax.set_xlabel("longitude")
        axf = axs.flat[5]; y = np.arange(len(CELLS))[::-1]
        if kind == "loudness":
            v = np.array([sh[d] for d in CELLS])
            axf.scatter(v[:, 0], y, c="#b2182b", s=14, label="peak radiated power", zorder=3)
            axf.scatter(v[:, 1], y, facecolors="none", edgecolors="k", s=14, label="total energy", zorder=3)
            for i in range(len(CELLS)): axf.plot(v[i], [y[i]] * 2, c="0.7", lw=0.8, zorder=1)
            axf.axvline(0.10, c="0.5", lw=0.6, ls="--"); axf.set_xlim(0, max(0.45, v.max() + 0.05))
            axf.set_xlabel("share in the loudest decile of the held-out case"); axf.set_title("f  Share of the loudest impacts, by measure", fontsize=7)
            axf.legend(fontsize=5.8, loc="lower right")
            axf.set_yticks(y); axf.set_yticklabels([short[d] for d in CELLS], fontsize=5.8); axf.yaxis.tick_right()
            axf.spines["right"].set_visible(True); axf.spines["left"].set_visible(False)
        else:
            for d in CELLS:
                x = RS[d]; ok = np.isfinite(x[:, 6]); e = np.maximum(x[ok, 6], 1e7) / 1e9; o = np.argsort(e); cw = np.cumsum(x[ok, 0][o]); cw /= cw[-1]
                axf.plot(e[o], cw, color=cols[d], lw=1.4 if d in ("D0", "D4") else 0.9, ls="--" if d == "D1" else "-", label=short[d])
            axf.set_xscale("log"); axf.set_xlim(0.1, 30); axf.set_xlabel("energy transferred at impact (GJ)"); axf.set_ylabel("cumulative probability")
            axf.yaxis.tick_right(); axf.yaxis.set_label_position("right"); axf.spines["right"].set_visible(True); axf.spines["left"].set_visible(False)
            axf.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}")); axf.legend(fontsize=5.2, loc="upper left")
            axf.set_title("f  Distribution of impact energy", fontsize=7)
            cb = fig.colorbar(sc, cax=fig.add_axes([0.25, 0.235, 0.5, 0.012]), orientation="horizontal")
            cb.set_label("energy transferred at impact (GJ)"); cb.ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        if kind == "loudness":
            fig.legend(handles=[Line2D([], [], marker="o", ls="", c=cmap3[0], ms=4, label="quieter half"),
                                Line2D([], [], marker="o", ls="", c=cmap3[1], ms=4, label="50-90 %"),
                                Line2D([], [], marker="o", ls="", c=cmap3[2], ms=4, label="loudest 10 %")],
                       loc="upper center", ncol=3, fontsize=6.5, bbox_to_anchor=(0.5, 1.0),
                       title="Peak radiated power at impact; classes set on the case with the 00:19 data not used", title_fontsize=7)
            n1 = ("Each dot is one likely place where the aircraft hit the ocean. The colour shows how loud the impact was, as peak "
                  "radiated power. The classes come from the case that does not use the 00:19 data. Panel f shows how much of each case is in the "
                  "loudest tenth, by peak power and by total energy. If the 00:19 data do not change loudness, the share is 0.10 (dashed line).")
            n2x = (f" Classes: weighted quantiles of D0' peak radiated power, median {tp[0]:.2g} W, top decile {tp[1]:.2g} W (total energy top decile "
                   f"{te[1]/1e9:.1f} GJ), tau90_v1 sidecar.")
        else:
            n1 = ("Each dot is one likely place where the aircraft hit the ocean. The colour shows the energy that went into the water and "
                  "the aircraft at impact. Panel f shows the spread of that energy for each use of the 00:19 data.")
            n2x = " Energy transferred from the tau90_v1 sidecar (floored at 0.01 GJ for display); panel f weighted empirical CDF of the resample."
        notes(fig, n1 + " The flight model for a descent without control is not calibrated, so the loudness and energy are not physical predictions.",
              "NOT A PHYSICAL PREDICTION: " + CAVEAT + " " + TECH + n2x + f" Each map: {NDRAW:,} impacts drawn by weight from a mass-preserving "
              "systematic resample of 10,000 rows per seed per treatment; all four strata. ESS: Kish effective impacts pooled over seeds.", width=200, fs=4.6)
        fig.subplots_adjust(left=0.08, right=0.80 if kind == "loudness" else 0.92, top=0.89 if kind == "loudness" else 0.94, bottom=0.27 if kind == "loudness" else 0.31)
        if kind == "energy":
            pass
        for ext in ("png", "pdf"): fig.savefig(out / f"run-j-impact-{kind}-maps.{ext}", dpi=300)
        plt.close(fig)
    json.dump(R, open(out / "run-j-figures.json", "w"), indent=1)
    print(json.dumps({k: R[k] for k in ("panels", "mixed_weights", "latitude")}, indent=0)[:4000])
    print(json.dumps({k: {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()} if isinstance(v, dict) else v for k, v in R["loudness"].items()}, indent=0)[:3000])


if __name__ == "__main__":
    main(*sys.argv[1:5])
