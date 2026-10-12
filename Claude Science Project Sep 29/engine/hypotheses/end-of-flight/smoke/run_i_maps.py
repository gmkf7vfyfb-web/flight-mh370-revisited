"""Run I impact maps by 00:19 treatment (Pete, 12 Oct 2026) and the decomposition of the R1200 southward shift.

    python run_i_maps.py EOF_ROOT CORE_ROOT OUT_DIR

Panels (each the competing-causes total, q = 1/3, C2 silent, survival factor; strata mixed with core's P(family); seeds pooled
by evidence, as option_table_0019.py):
  held out = D0; R600 only = D2 (R600 BTO + R600 BFO; D1 = R600 BTO only reported in the JSON);
  with R1200 = D4 (both BFOs, shared start-up offset; Holland's H1 data);
  mixed = the equal-prior Bayesian model average of D3, D4 and D5, which score the SAME observations (R600 BTO, R600 BFO,
  R1200 BFO) under three offset models, so their ln Z weights them legitimately.
Density: weighted 0.02 deg histogram, Gaussian sigma 0.08 deg; HPD 50/90/99 %. Searched ground: coverage rasters of the
seabed-search module (coverage >= 0.5 outline). Writes run-i-impact-maps.{pdf,png,json} and run-i-r1200-shift.json.
"""
import json, sys, pathlib, struct, os
import numpy as np
from scipy.special import logsumexp, gammaln
from scipy.ndimage import gaussian_filter
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compact_impacts import load, family_labels
from displacement_hist import derived_logliks, constraint_log_factor, SATCOM_CSV
from option_table_0019 import d5_loglik, W_S
import csv

STRATA = {"next-i-waypoints": 0.9982, "next-i-free": 0.0011, "next-i-repro-radar": 0.0004, "next-i-descent-climb": 0.0002}
T29 = 1394237969.416
LAT0, LAT1, LON0, LON1, G = -42.0, -30.0, 84.0, 102.0, 0.02
NLAT, NLON = int(round((LAT1 - LAT0) / G)), int(round((LON1 - LON0) / G))
CELLS = ("D0", "D1", "D2", "D3", "D4", "D5")
BANDS = {"peak37.0": (-37.25, -36.75), "peak37.7": (-37.95, -37.45)}


def cell_logmass(g, meta, handoff):
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    obs = {r["epoch_id"]: r for r in csv.DictReader(open(SATCOM_CSV))}
    w = g("weight"); lw = np.log(w) - np.log(w.sum())
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
    der = derived_logliks(meta, g, present)
    V = np.asarray(np.load(handoff, mmap_mode="r")[:, 9])[g("parent").astype(np.int64)]
    col = lambda k: np.where(np.isfinite(g("loglik:" + k)), g("loglik:" + k), -np.inf)
    D = {"D0": np.zeros(len(w)), "D1": der["r600-bto"], "D2": col("r600/no-offset"), "D3": col("both/no-offset"),
         "D4": col("both/startup-offset"), "D5": d5_loglik(g, V, obs)}
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    c1 = lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered")
    c2 = -np.log(W_S) + constraint_log_factor(g, logon, "other", "silent")
    p = 0.75
    tot = np.logaddexp(np.log(p) + c1, np.log(1 - p) + c2)
    return {d: lw + surv + D[d] + tot for d in CELLS}


def read_cov(path):
    b = pathlib.Path(path).read_bytes(); assert b[:8] == b"MH370COV"
    ver, south, west, step, rows, cols, runs = struct.unpack("<IdddIII", b[8:8 + 40])
    rec = np.frombuffer(b[48:48 + 3 * runs], dtype=np.dtype([("v", "u1"), ("n", "<u2")]))
    q = np.repeat(rec["v"], rec["n"]).astype(np.float32) / 255.0
    return south, west, step, q.reshape(rows, cols)


def wq(x, w, qs):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]
    return [float(x[o][min(np.searchsorted(c, q), len(x) - 1)]) for q in qs]


def main(eof_root, core_root, out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    H = {d: np.zeros((NLAT, NLON)) for d in CELLS}; L1 = {d: [] for d in CELLS}; L2 = {d: [] for d in CELLS}
    ref = None
    # decomposition accumulators (per cell): samples of (impact lat, 00:19:37 lat, flight time after 00:19:29, family, stratum)
    dec = {d: {"m": [], "lat": [], "lat37": [], "dt": [], "fam": [], "st": [], "dnorth": [], "dive": []} for d in ("D0", "D2", "D4")}
    for st, P in STRATA.items():
        seeds = sorted(p for p in (pathlib.Path(eof_root) / st).glob("seed-*") if p.is_dir()); K = len(seeds)
        for sd in seeds:
            meta, g = load(sd)
            lm = cell_logmass(g, meta, pathlib.Path(core_root) / st / "bto-bfo" / sd.name / "handoff-m0011" / "handoff.npy")
            lat = g("latitude_deg"); lon = g("longitude_deg")
            i = np.floor((lat - LAT0) / G).astype(np.int64); j = np.floor((lon - LON0) / G).astype(np.int64)
            ok = (i >= 0) & (i < NLAT) & (j >= 0) & (j < NLON)
            c = np.log(P / K)
            if ref is None:
                ref = c + max(float(np.max(v[np.isfinite(v)])) for v in lm.values())
            lb = g("latent:last_burst_latitude_deg"); t = g("unix_s")
            dive = g("latent:pushover_to_surface") if "latent:pushover_to_surface" in meta["impact_columns"] else np.full(len(t), np.nan)
            f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
            for d, a in lm.items():
                fin = np.isfinite(a)
                L1[d].append(c + logsumexp(a[fin])); L2[d].append(2 * c + logsumexp(2 * a[fin]))
                m = np.zeros(len(a)); m[fin] = np.exp(c + a[fin] - ref)
                H[d] += np.bincount((i * NLON + j)[ok], weights=m[ok], minlength=NLAT * NLON).reshape(NLAT, NLON)
                if d in dec and m.sum() > 0:
                    # systematic resample of 50,000 rows per seed in proportion to mass (memory bounded, mass preserving)
                    n = 50_000; cs = np.cumsum(m); s = np.minimum(np.searchsorted(cs, (np.arange(n) + 0.5) / n * cs[-1]), len(m) - 1)
                    for k_, v_ in (("m", np.full(n, cs[-1] / n)), ("lat", lat[s]), ("lat37", lb[s]), ("dt", t[s] - T29), ("fam", f4[s]),
                                   ("st", np.full(n, list(STRATA).index(st))), ("dnorth", lat[s] - lb[s]), ("dive", dive[s])):
                        dec[d][k_].append(v_)
            print(f"  {st} {sd.name}", flush=True)
    lz = {d: float(logsumexp(L1[d])) for d in CELLS}
    ess = {d: float(np.exp(2 * lz[d] - logsumexp(L2[d]))) for d in CELLS}
    # mixed: equal-prior BMA of D3/D4/D5 (their H are on the same absolute scale exp(lnZ - ref))
    Hmix = H["D3"] + H["D4"] + H["D5"]
    zmix = logsumexp([lz["D3"], lz["D4"], lz["D5"]])
    post = {d: float(np.exp(lz[d] - zmix)) for d in ("D3", "D4", "D5")}
    panels = [("Held out", "00:19 data not used (D0)", H["D0"], ess["D0"]),
              ("R600 only", "R600 range and frequency (D2)", H["D2"], ess["D2"]),
              ("With R1200", "Both frequencies, shared start-up offset\n(D4, Holland's H1 data)", H["D4"], ess["D4"]),
              ("Mixed", f"Evidence-weighted average of the three\nR1200 treatments (D3 {post['D3']:.2f}, D4 {post['D4']:.2f}, D5 {post['D5']:.2f})", Hmix, None)]
    res = {"ln_Z": lz, "eff_impacts": ess, "mixed_weights": post, "panels": {}}
    np.savez_compressed(out / "run-i-impact-density.npz", lat0=LAT0, lon0=LON0, grid=G, **{d: H[d] for d in CELLS}, mixed=Hmix)
    # decomposition
    shift = {}
    for d, A in dec.items():
        A = {k: np.concatenate(v) for k, v in A.items()}; m = A["m"]
        r = {"impact_lat_q05_q50_q95": wq(A["lat"], m, (.05, .5, .95)), "lat_0019_37_q05_q50_q95": wq(A["lat37"], m, (.05, .5, .95)),
             "northward_displacement_deg_q05_q50_q95": wq(A["dnorth"], m, (.05, .5, .95)),
             "flight_after_001929_s_q05_q50_q95": wq(A["dt"], m, (.05, .5, .95))}
        for b, (lo, hi) in BANDS.items():
            s = (A["lat"] >= lo) & (A["lat"] < hi); ms = m[s]
            r[b] = {"mass_share": float(ms.sum() / m.sum()),
                    "lat_0019_37_q50": wq(A["lat37"][s], ms, (.5,))[0], "northward_displacement_q50": wq(A["dnorth"][s], ms, (.5,))[0],
                    "flight_after_001929_s_q50": wq(A["dt"][s], ms, (.5,))[0],
                    "family_share_A1_A2_B": [float(ms[A["fam"][s] == f].sum() / ms.sum()) for f in (1, 2, 3)],
                    "share_flying_over_600s": float(ms[A["dt"][s] > 600].sum() / ms.sum()),
                    "share_dive_to_surface": float(ms[A["dive"][s] == 1].sum() / ms.sum()),
                    "share_pushover_levelled_off": float(ms[A["dive"][s] == 0].sum() / ms.sum())}
        shift[d] = r
    json.dump(shift, open(out / "run-i-r1200-shift.json", "w"), indent=1)
    # maps
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    lat_c = LAT0 + G * (np.arange(NLAT) + 0.5); lon_c = LON0 + G * (np.arange(NLON) + 0.5)
    here = pathlib.Path(__file__).resolve()
    covdir = here.parents[2] / "seabed-search" / "coverage"
    covs = {"Phase 2 seabed search (2014-17)": covdir / "phase2.cov", "Ocean Infinity 2018": covdir / "ocean-infinity-2018.cov",
            "Ocean Infinity 2025": covdir / "ocean-infinity-2025.cov"}
    cov_style = {"Phase 2 seabed search (2014-17)": dict(colors="#000000", linewidths=1.6),
                 "Ocean Infinity 2018": dict(colors="#7a3b00", linewidths=1.6),
                 "Ocean Infinity 2025": dict(colors="#1b6b3a", linewidths=1.6)}
    rasters = {}
    for k, p in covs.items():
        if p.exists():
            s0, w0, stp, q = read_cov(p); rasters[k] = (s0 + stp * (np.arange(q.shape[0]) + 0.5), w0 + stp * (np.arange(q.shape[1]) + 0.5), q)
    arcs = {x["epoch"]: np.asarray(x["lat_lon"], float) for x in json.loads((pathlib.Path(core_root) / "next-i-waypoints" / "run.json").read_text())["reference_arcs"]}
    LEV = (0.99, 0.90, 0.50); FILL = ["#dcdcdc", "#a8a8a8", "#6a6a6a"]; LW = [0.5, 0.7, 0.9]   # house style (displacement_greyscale.py)
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 8.6), sharex=True, sharey=True)
    view = None
    for ax, (short, long_, Hd, e) in zip(axs.ravel(), panels):
        dens = gaussian_filter(Hd / Hd.sum(), 0.08 / G)
        flat = np.sort(dens.ravel())[::-1]; cm = np.cumsum(flat)
        lv = [float(flat[min(np.searchsorted(cm, f * cm[-1]), len(flat) - 1)]) for f in LEV]
        ax.contourf(lon_c, lat_c, dens, levels=[lv[0], lv[1], lv[2], dens.max()], colors=FILL)
        ax.contour(lon_c, lat_c, dens, levels=lv, colors="#2b2b2b", linewidths=LW)
        for k, (la, lo, q) in rasters.items():
            ax.contour(lo, la, q, levels=[0.5], **cov_style[k])
        for ep, sty in (("m0011", dict(color="#4a6fa5", lw=1.0, ls="--")), ("m0019a", dict(color="#b16286", lw=1.2))):
            if ep in arcs: ax.plot(arcs[ep][:, 1], arcs[ep][:, 0], **sty)
        # HPD areas (km^2) and enclosed mass check
        cell_km2 = (G * 111.32) ** 2 * np.cos(np.radians(lat_c))[:, None] * np.ones((1, NLON))
        areas = {f"{int(f*100)}%": float(cell_km2[dens >= l].sum()) for f, l in zip(LEV, lv)}
        hc = np.cumsum(Hd.sum(axis=1)); hc /= hc[-1]
        q50 = float(lat_c[np.searchsorted(hc, 0.5)])
        res["panels"][short] = {"description": long_, "hpd_area_km2": areas, "lat_median": q50,
                                "lat_mode": float(lat_c[np.argmax(gaussian_filter(Hd.sum(axis=1), 0.08 / G))]), "eff_impacts": e}
        view = (86.5, 99.0, -40.2, -30.0)
        ax.set_title(f"{short}: {long_}", loc="left", fontsize=7, wrap=True)
        txt = f"median {q50:.2f}°, peak {res['panels'][short]['lat_mode']:.2f}°" + (f"\neffective impacts {e/1000:.1f}k" if e else "")
        ax.text(0.98, 0.02, txt, transform=ax.transAxes, ha="right", va="bottom", fontsize=6)
        ax.grid(True, color="#eeeeee", lw=0.5); ax.set_axisbelow(True)
    for ax in axs.ravel():
        ax.set_xlim(view[0], view[1]); ax.set_ylim(view[2], view[3]); ax.set_aspect(1 / np.cos(np.radians(-36)))
    from matplotlib.ticker import FuncFormatter
    for ax in axs.ravel():
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):.0f}°S")); ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}°E"))
    for ax in axs[1]: ax.set_xlabel("longitude (°E)")
    for ax in axs[:, 0]: ax.set_ylabel("latitude (°)")
    h = [Patch(facecolor=f, edgecolor="#2b2b2b", lw=0.6, label=f"{int(l*100)} % of probability") for f, l in zip(FILL[::-1], LEV[::-1])]
    h += [Line2D([], [], **{"color": v["colors"], "lw": v["linewidths"]}, label=k) for k, v in cov_style.items() if k in rasters]
    h += [Line2D([], [], color="#b16286", lw=1.2, label="7th arc, 00:19:29 UTC"), Line2D([], [], color="#4a6fa5", lw=1.0, ls="--", label="6th arc, 00:10:59 UTC")]
    fig.legend(handles=h, loc="upper center", ncol=3, frameon=False, fontsize=6, bbox_to_anchor=(0.5, 0.955))
    fig.suptitle("Where the aircraft hit the ocean, for each use of the 00:19 satellite data (before the search evidence)", x=0.02, ha="left", fontsize=8, y=0.995)
    import textwrap
    n1 = ("Note 1: Each panel shows the area that holds 50, 90 and 99 % of the probability of the ocean impact. The panels use the two "
          "00:19 satellite messages in different ways. The heavy black, brown and green lines show sea floor that was searched; the search result is not "
          "applied here. The log-on cause mixes fuel exhaustion (weight 3) and other causes (weight 1). The results are provisional.")
    n2 = ("Note 2: End of flight on core run I (4 route families x 8 seeds x 100,000 hand-off particles at 00:11, N = 8 children x 4 "
          f"descents; family weights 0.9982/0.0011/0.0004/0.0002; {os.environ.get('EOF_MAP_RUN', 'binary mh370-eof-ri1')}). Competing log-on causes C1 (Erlang lag) + C2 "
          "(1/W, W = 00:10:58-01:15:56, silent), q = 1/3; survival factor applied; no treatment uses the R1200 BTO. Mixed = equal-prior "
          "average of D3/D4/D5 by ln Z. Density 0.02° grid, Gaussian sigma 0.08°. Searched ground: coverage >= 0.5 outlines of the "
          f"seabed-search rasters. PROVISIONAL: piloted-turn model, INTERIM pitch-down, {os.environ.get('EOF_MAP_NOTE', 'SLS thrust 415.45 kN (pre-correction, +2.1%); conditional on push-over recovery by 8,000 ft')}. Core run "
          "I not converged (8-seed floor 0.916). Effective impacts D3/D5 below 1,000 in some C2-silent cells (see COVERAGE).")
    fig.text(0.02, 0.005, textwrap.fill(n1, 175) + "\n" + textwrap.fill(n2, 175), fontsize=5, va="bottom", ha="left")
    fig.subplots_adjust(left=0.09, right=0.98, top=0.87, bottom=0.17, hspace=0.18, wspace=0.06)
    fig.savefig(out / "run-i-impact-maps.pdf"); fig.savefig(out / "run-i-impact-maps.png", dpi=250)
    json.dump(res, open(out / "run-i-impact-maps.json", "w"), indent=1)
    print(json.dumps(res["panels"], indent=1)); print(json.dumps(shift, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
