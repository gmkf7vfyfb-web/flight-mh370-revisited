"""Composer pass 0: mix the four core (b) strata, compute PDF statistics, tension quantities and tables, draw figures.

PIPELINE TEST - core (b) unconverged; EoF physics provisional; hydro L_hyd stand-in; GlobCurrent F1; Holland H1/H2 not estimable.
smooth_to_density, stats and overlap are transcribed from summary.rs; the equal-area map from patch B (unlanded).

Usage: python report.py <work dir> <out dir (results/composer-pass0-next-run-b)>
"""
import csv, json, math, pathlib, sys
import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import summarise_stratum as S

STRATA = ["next-free", "next-repro-radar", "next-descent-climb", "next-routes"]
SNAME = {"next-free": "free", "next-repro-radar": "Davey dynamics + radar", "next-descent-climb": "descent-climb", "next-routes": "routes"}
P_CORE = {"next-free": 0.6948, "next-repro-radar": 0.1527, "next-descent-climb": 0.1376, "next-routes": 0.0149}
FE = json.loads(S.FAMILY_EVIDENCE.read_text())
FE_KEY = {"r600": "00:19 R600 BTO Only +alive", "heldout": "00:19 Held Out +alive"}
ONAME = {"r600": "00:19 R600 BTO Only", "heldout": "00:19 Held Out"}
CHAIN = {"P1": "filter", "G": "P1", "Ga": "G", "H": "P1", "Ha": "H", "PE": "P1", "Gx": "P1", "Hx": "P1", "PEx": "P1",
         "Hc": "P1", "PEc": "P1", "D": "P1", "Y": "P1", "S": "P1", "Y0": "P1"}
MAPPED = ["P1", "G", "Ga", "H", "Ha", "Gx", "Hx"]
LABEL = "PIPELINE TEST - core (b) unconverged; EoF physics provisional; hydro L_hyd stand-in; GlobCurrent F1; Holland H1/H2 not estimable"
HALF = int(round(4 * 0.1 / S.GRID_STEP))
KERNEL = np.exp(-0.5 * ((np.arange(-HALF, HALF + 1) * S.GRID_STEP / 0.1) ** 2)); KERNEL /= KERNEL.sum()
GRID = S.GRID_MIN + np.arange(S.NPTS) * S.GRID_STEP


def smooth_to_density(h):
    out = np.zeros_like(h)
    for i in np.nonzero(h)[0]:
        lo, hi = i - HALF, i + HALF + 1
        a, b = max(lo, 0), min(hi, h.size)
        out[a:b] += h[i] * KERNEL[a - lo:KERNEL.size - (hi - b)]
    t = out.sum() * S.GRID_STEP
    return out / t if t > 0 else out


def stats(d):
    cdf = np.cumsum(d * S.GRID_STEP); ue = lambda k: GRID[k] + S.GRID_STEP / 2
    def q(p):
        k = int(np.argmax(cdf >= p)) if (cdf >= p).any() else None
        if k is None:
            return ue(d.size - 1)
        below, x = (0.0, S.GRID_MIN - S.GRID_STEP / 2) if k == 0 else (cdf[k - 1], ue(k - 1))
        t = (p - below) / (cdf[k] - below) if cdf[k] > below else 0.0
        return x + t * S.GRID_STEP
    return {"q025": q(0.025), "median": q(0.5), "q975": q(0.975), "mode": float(GRID[int(np.argmax(d))])}


def overlap(p, q):
    return float(np.minimum(p, q).sum() * S.GRID_STEP)


# equal-area cell geometry
QE = S.authalic_q(S.MAP_LAT[0]) + np.arange(S.NY + 1) * S.Q_STEP
_lat = np.linspace(-60, 20, 160001); _q = S.authalic_q(_lat)
LAT_EDGES = np.interp(QE, _q, _lat); LON_EDGES = S.MAP_LON[0] + np.arange(S.NX + 1) * S.MAP_STEP
LAT_C = np.interp(0.5 * (QE[1:] + QE[:-1]), _q, _lat); LON_C = 0.5 * (LON_EDGES[1:] + LON_EDGES[:-1])


def hdr_mask(p, level):
    o = np.argsort(p)[::-1]; c = np.cumsum(p[o]); m = np.zeros(p.size, bool); m[o[:int(np.searchsorted(c, level * c[-1])) + 1]] = True
    return m


def nm_between(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p1, p2, dl = math.radians(la1), math.radians(la2), math.radians(lo2 - lo1)
    return 3440.065 * math.acos(min(1.0, math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)))


def smoothed_mode(cell):
    m = gaussian_filter(cell.reshape(S.NY, S.NX).astype(float), 1.0); y, x = np.unravel_index(np.argmax(m), m.shape)
    return float(LAT_C[y]), float(LON_C[x])


def load(work):
    D = {}
    for st in STRATA:
        P = json.loads((work / "rust" / st / "products.json").read_text())
        D[st] = {"products": {p["id"]: p for p in P["products"]}, "refusals": P["refusals"],
                 "npz": np.load(work / "summary" / st / "hist.npz"), "summary": json.loads((work / "summary" / st / "summary.json").read_text())}
    return D


def cum_inc(D, st, tag, key):
    tot = 0.0
    while key != "filter":
        tot += D[st]["products"][f"{tag}-{key}"]["log_evidence_increment"]; key = CHAIN[key]
    return tot


def weights(D, tag, key, scheme):
    if scheme == "fixed":
        w = dict(P_CORE)
    elif scheme == "reweighted-0019":
        w = dict(FE["mixtures"][FE_KEY[tag]]["p_family_reweighted"])
    else:  # all evidence in this product
        lw = {s: math.log(P_CORE[s]) + cum_inc(D, s, tag, key) for s in STRATA}; m = max(lw.values())
        w = {s: math.exp(v - m) for s, v in lw.items()}
    t = sum(w.values()); return {s: w[s] / t for s in STRATA}


SCHEMES = ["reweighted-0019", "fixed", "all-evidence"]


def mixture(D, tag, key, scheme, part="lat"):
    w = weights(D, tag, key, scheme)
    return sum(w[s] * D[s]["npz"][f"{tag}-{key}|{part}"].astype(float) for s in STRATA), w


def per_seed_rep(D, st, tag, key):
    return {r["seed"]: r for r in D[st]["products"][f"{tag}-{key}"]["replicates"]}


def main(work, out):
    work, out = pathlib.Path(work), pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    D = load(work)
    R = {"label": LABEL, "options": {}}
    rows_prod, rows_mix, rows_ev, rows_fam, rows_cov = [], [], [], [], []
    for tag in ("r600", "heldout"):
        O = R["options"][tag] = {"name": ONAME[tag], "products": {}, "tension": {}}
        # ---- per stratum, per product
        for st in STRATA:
            prods = D[st]["products"]
            for key in CHAIN:
                pid = f"{tag}-{key}"
                if pid not in prods:
                    continue
                p = prods[pid]; sh = p["split_half"] or {}
                row = {"option": ONAME[tag], "product": key, "label": p["label"], "stratum": SNAME[st], "contains": " + ".join(p["contains"]),
                       "conditional_on": json.dumps(p["conditional_on"]), "ln_evidence_increment_vs_base": p["log_evidence_increment"],
                       "ln_evidence_vs_flight": cum_inc(D, st, tag, key),
                       "split_half_increment_seeds12": (sh.get("log_evidence_increment") or [None, None])[0],
                       "split_half_increment_seeds34": (sh.get("log_evidence_increment") or [None, None])[1],
                       "composer_status": p["status"], "min_ess_parents_per_seed": min(e[1] for e in p["ess_rows_parents"]),
                       "sum_ess_rows_4_seeds": sum(e[0] for e in p["ess_rows_parents"])}
                for f in p["factors"]:
                    row[f"not_computed_weight_max[{f['name']}]"] = max(f["not_computed_weight"]) if f["not_computed_weight"] else 0.0
                    row[f"factor_alone_min_ess_parents[{f['name']}]"] = min(e[1] for e in f["ess_rows_parents"]) if f["ess_rows_parents"] else None
                if key in MAPPED:
                    d = smooth_to_density(D[st]["npz"][f"{pid}|lat"]); row.update({f"lat_{k}": v for k, v in stats(d).items()})
                    row["split_half_overlap"] = overlap(smooth_to_density(D[st]["npz"][f"{pid}|lat_h0"]), smooth_to_density(D[st]["npz"][f"{pid}|lat_h1"]))
                    cell = D[st]["npz"][f"{pid}|cell"].astype(float); row["hdr90_area_km2"] = float(hdr_mask(cell / cell.sum(), 0.9).sum() * S.CELL_KM2)
                    cov = D[st]["summary"]["products"][pid]
                    for f, v in cov["ess_rows_per_seed_by_family"].items():
                        rows_cov.append({"option": ONAME[tag], "product": key, "stratum": SNAME[st], "by": "EoF family code", "value": f, "ess_rows_per_seed": json.dumps([round(x) for x in v])})
                    for b, v in cov["ess_rows_per_seed_by_latitude_band"].items():
                        rows_cov.append({"option": ONAME[tag], "product": key, "stratum": SNAME[st], "by": "impact latitude band", "value": b, "ess_rows_per_seed": json.dumps([round(x) for x in v])})
                rows_prod.append(row)
                for r in p["replicates"]:
                    for m, v in enumerate(r["log_evidence_increment"]):
                        rows_ev.append({"option": ONAME[tag], "product": key, "stratum": SNAME[st], "seed": r["seed"], "mode": m, "ln_D_vs_base": v})
        # ---- mixtures
        for key in MAPPED:
            O["products"][key] = {}
            for sc in SCHEMES:
                h, w = mixture(D, tag, key, sc); d = smooth_to_density(h)
                h0, _ = mixture(D, tag, key, sc, "lat_h0"); h1, _ = mixture(D, tag, key, sc, "lat_h1")
                cell, _ = mixture(D, tag, key, sc, "cell"); cell = cell / cell.sum()
                fam, _ = mixture(D, tag, key, sc, "fam")
                fm = {f: sum(w[s] * D[s]["summary"]["products"][f"{tag}-{key}"]["family_mass"][f] for s in STRATA) for f in range(5)}
                e = {"stratum_weights": w, **stats(d), "split_half_overlap": overlap(smooth_to_density(h0), smooth_to_density(h1)),
                     "hdr50_area_km2": float(hdr_mask(cell, 0.5).sum() * S.CELL_KM2), "hdr90_area_km2": float(hdr_mask(cell, 0.9).sum() * S.CELL_KM2),
                     "smoothed_map_mode_lat_lon": smoothed_mode(cell), "family_probability": {"A1 (with A-then-lost)": fm[1] + fm[4], "A2": fm[2], "B": fm[3], "A-then-lost alone": fm[4], "unlabelled": fm[0]}}
                fams = {"A1 (with A-then-lost)": fam[1] + fam[4], "A2": fam[2], "B": fam[3], "A2 (with A-then-lost, sensitivity)": fam[2] + fam[4], "A1 alone (sensitivity)": fam[1]}
                e["family_stats"] = {k: (stats(smooth_to_density(v)) if v.sum() > 0 else None) for k, v in fams.items()}
                O["products"][key][sc] = e
                rows_mix.append({"option": ONAME[tag], "product": key, "mixture": sc, **{k: e[k] for k in ("q025", "median", "q975", "mode", "split_half_overlap", "hdr50_area_km2", "hdr90_area_km2")},
                                 "map_mode_lat": e["smoothed_map_mode_lat_lon"][0], "map_mode_lon": e["smoothed_map_mode_lat_lon"][1],
                                 "stratum_weights": json.dumps({SNAME[s]: round(v, 4) for s, v in w.items()})})
                for fk, fv in e["family_stats"].items():
                    if fv:
                        rows_fam.append({"option": ONAME[tag], "product": key, "mixture": sc, "family": fk,
                                         "probability": e["family_probability"].get(fk, (fm[2] + fm[4]) if "A2 (with" in fk else fm[1]), **fv})
        # ---- tension quantities for H against G, before and after searches
        for pair, (gk, hk, pe) in {"before searches": ("G", "H", "PE"), "after searches": ("Ga", "Ha", "PE"),
                                   "not-computed excluded": ("Gx", "Hx", "PEx")}.items():
            T = O["tension"][pair] = {"per_stratum": {}}
            for st in STRATA:
                if pair == "after searches":
                    T["per_stratum"][SNAME[st]] = {"ln_R": None, "note": "not computed: needs flight+EoF+searches+Pléiades as the denominator"}
                    continue
                # ln R = ln E[L_P | flight+EoF+drift+hydro] - ln E[L_P | flight+EoF]; the Pléiades A_scene constant cancels
                lr = (cum_inc(D, st, tag, hk) - cum_inc(D, st, tag, gk)) - (cum_inc(D, st, tag, pe) - cum_inc(D, st, tag, "P1"))
                g_r, h_r, pe_r, p1_r = (per_seed_rep(D, st, tag, k) for k in (gk, hk, pe, "P1"))
                ps = {k: (h_r[k]["log_evidence"] - g_r[k]["log_evidence"]) - (pe_r[k]["log_evidence"] - p1_r[k]["log_evidence"]) for k in (1, 2, 3, 4)}
                sh = lambda key: D[st]["products"][f"{tag}-{key}"]["split_half"]["log_evidence_increment"]
                halves = [sh(hk)[j] - sh(gk)[j] - sh(pe)[j] for j in (0, 1)]
                T["per_stratum"][SNAME[st]] = {"ln_R": lr, "ln_R_per_seed": ps, "ln_R_split_halves": halves}
            for sc in SCHEMES:
                wg, wh = weights(D, tag, gk, sc), weights(D, tag, hk, sc)
                cg = mixture(D, tag, gk, sc, "cell")[0]; ch = mixture(D, tag, hk, sc, "cell")[0]; cg, ch = cg / cg.sum(), ch / ch.sum()
                mg, mh = hdr_mask(cg, 0.9), hdr_mask(ch, 0.9)
                # mixture ln R: ln sum_s w_s(G) E_s[L_P|G] - ln sum_s w_s(P1) E_s[L_P|P1], with each scheme's stratum weights
                wp1 = weights(D, tag, "P1", sc)
                lnr = None
                if pair != "after searches":
                    num = sum(wg[s] * math.exp(cum_inc(D, s, tag, hk) - cum_inc(D, s, tag, gk) + 7.0) for s in STRATA)
                    den = sum(wp1[s] * math.exp(cum_inc(D, s, tag, pe) - cum_inc(D, s, tag, "P1") + 7.0) for s in STRATA)
                    lnr = math.log(num / den)
                T[sc] = {"ln_R": lnr, "hdr90_jaccard": float((mg & mh).sum() / (mg | mh).sum()),
                         "share_of_H_hdr90_inside_G_hdr90": float((mg & mh).sum() / mh.sum()), "H_mass_inside_G_hdr90": float(ch[mg].sum()),
                         "map_mode_G": smoothed_mode(cg), "map_mode_H": smoothed_mode(ch),
                         "mode_displacement_nm": nm_between(smoothed_mode(cg), smoothed_mode(ch)),
                         "median_lat_G": stats(smooth_to_density(mixture(D, tag, gk, sc)[0]))["median"],
                         "median_lat_H": stats(smooth_to_density(mixture(D, tag, hk, sc)[0]))["median"]}
        # stratum weights check: P_core x exp(P1 increment) vs EoF's re-weighted P(family)
        O["stratum_weight_check"] = {"composer_P_core_x_Z0019": weights(D, tag, "P1", "all-evidence"), "eof_family_evidence": weights(D, tag, "P1", "reweighted-0019")}
    R["refusals"] = D["next-free"]["refusals"]
    (out / "pass0-results.json").write_text(json.dumps(R, indent=1, default=float))
    for name, rows in (("products-per-stratum.csv", rows_prod), ("mixtures.csv", rows_mix), ("evidence-increments-per-seed-mode.csv", rows_ev),
                       ("families.csv", rows_fam), ("coverage-ess.csv", rows_cov)):
        keys = []
        for r in rows:
            keys += [k for k in r if k not in keys]
        with open(out / name, "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=keys); wr.writeheader(); wr.writerows(rows)
    figures(D, R, out)
    print("ok")


# ------------------------------------------------------------------ figures
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 6.5,
                     "ytick.labelsize": 6.5, "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans"})
COL = {"P1": "#8c8c8c", "G": "#1f5fa8", "Ga": "#1f5fa8", "H": "#c2571a", "Ha": "#c2571a", "Gx": "#1f5fa8", "Hx": "#c2571a"}
NAMES = {"P1": "Flight and descent only", "G": "Add debris drift and underwater sound",
         "Ga": "... then the seabed searches", "H": "Also add the Pléiades objects (if aircraft debris)", "Ha": "... then the seabed searches"}
COMMON_TECH = ("Source: core (b) filter, prior track 289.7 deg, 00:11 hand-off, 4 strata x 4 seeds (51.2 M impact rows); end of flight 3c6319f "
               "(dive class (b), descent rates <= 6,500 ft/min, PROVISIONAL); log-on cause 'other', +alive. Drift: GLORYS12V1 + ERA5 only, 50 km "
               "bandwidth, 9 finds (GlobCurrent excluded: audit F1). Hydroacoustics: stand-in L_hyd (IMOS 4 loggers + Kadri H01W list). "
               "Pléiades: rating 5, 6 clusters, equal weight, GLORYS12, COSMO excluded. Searches: Phase 2 + Bluefin-21, rho 0.05, OI excluded. "
               "Not-computed rows carried at the (seed, mode) mean likelihood ratio (drift 16-25 % of weight, Pléiades 1-3 %). "
               "Strata mixed by P(family) re-weighted by the 00:19 evidence. Holland H1/H2 not estimable and not shown.")


def footer(fig, ste, tech, frac=0.24):
    """Two footnotes, STE100 then technical, inside the bottom `frac` (<= 0.25) of the image."""
    fig.add_artist(matplotlib.lines.Line2D([0.01, 0.99], [frac, frac], color="#999999", lw=0.5))
    fig.text(0.01, frac - 0.008, "PIPELINE TEST - NOT CONVERGED (core (b) split-half). " + ste, fontsize=6.2, va="top", ha="left", wrap=True)
    fig.text(0.01, frac * 0.60, "Technical: " + tech, fontsize=5.6, va="top", ha="left", wrap=True, color="#333333")


def fig_latitude(D, R, out):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.4), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.90, bottom=0.355, wspace=0.06)
    for ax, tag in zip(axes, ("r600", "heldout")):
        for key, ls in (("P1", "-"), ("G", "-"), ("Ga", "--"), ("H", "-"), ("Ha", "--")):
            h, _ = mixture(D, tag, key, "reweighted-0019"); d = smooth_to_density(h)
            ax.plot(GRID, d, ls, color=COL[key], lw=1.6 if key in ("G", "H") else 1.1, label=NAMES[key])
        ax.set_xlim(-44, -24); ax.set_xlabel("Impact latitude (degrees; south is negative)")
        ax.set_title(f"{'Primary case' if tag == 'r600' else 'Comparison case'}: {'00:19 transmission range used' if tag == 'r600' else '00:19 transmissions not used'}", loc="left")
    axes[0].set_ylabel("Probability density (per degree)")
    axes[1].legend(frameon=False, loc="upper right", fontsize=6.5)
    fig.suptitle("Where the aircraft hit the water, as each set of evidence is added", x=0.01, ha="left", fontsize=9)
    footer(fig, "These curves show where the aircraft possibly hit the sea. Each curve adds more evidence. The orange curves are correct only if the "
                "Pléiades objects are aircraft debris. The input sample did not settle, so the curves can change in a new run. Do not use them as a result.",
           COMMON_TECH + " Curves: summary.rs latitude grid (0.05 deg, 0.1 deg Gaussian), pooled per summary.rs pooling().", 0.27)
    fig.savefig(out / "fig1-impact-latitude.png", dpi=200); fig.savefig(out / "fig1-impact-latitude.pdf"); plt.close(fig)


def fig_maps(D, R, out):
    fig, axes = plt.subplots(2, 2, figsize=(6.4, 8.0), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.10, right=0.99, top=0.885, bottom=0.255, wspace=0.04, hspace=0.16)
    for ax, key in zip(axes.flat, ("G", "Ga", "H", "Ha")):
        cell, _ = mixture(D, "r600", key, "reweighted-0019", "cell"); p = cell / cell.sum()
        m50, m90 = hdr_mask(p, 0.5).reshape(S.NY, S.NX), hdr_mask(p, 0.9).reshape(S.NY, S.NX)
        lvl = np.where(m50, 2, np.where(m90, 1, 0)).astype(float); lvl[lvl == 0] = np.nan
        ax.pcolormesh(LON_EDGES, LAT_EDGES, lvl, cmap=matplotlib.colors.ListedColormap(["#c9d7ea" if key[0] == "G" else "#f1d1bd", COL[key]]), vmin=0.5, vmax=2.5, shading="flat")
        e = R["options"]["r600"]["products"][key]["reweighted-0019"]
        ax.plot(e["smoothed_map_mode_lat_lon"][1], e["smoothed_map_mode_lat_lon"][0], "k+", ms=7)
        ax.set_title({"G": "Drift and sound added", "Ga": "... after the seabed searches", "H": "Pléiades objects also added", "Ha": "... after the seabed searches"}[key]
                     + f"\n90 % region {e['hdr90_area_km2'] / 1e3:,.0f}k km²", loc="left", fontsize=7.5)
        ax.set_xlim(85, 106); ax.set_ylim(-44, -24); ax.set_aspect(1 / math.cos(math.radians(34)))
    for ax in axes[1]:
        ax.set_xlabel("Longitude (degrees east)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Latitude (degrees)")
    fig.suptitle("Most probable impact regions, primary case (00:19 transmission range used)", x=0.01, y=0.985, ha="left", fontsize=9)
    fig.text(0.01, 0.950, "Dark: 50 % region.  Light: 90 % region.  +: highest density.", fontsize=7)
    footer(fig, "The dark area holds half the probability, and the dark and light areas together hold 90 %. The lower maps are correct only if the "
                "Pléiades objects are aircraft debris. The input sample did not settle. Do not use these maps for a search.",
           COMMON_TECH + " Regions: highest-density cells of the patch-B equal-area grid (0.25 deg lon x equal authalic-latitude steps, 769.3 km² cells), "
                         "unsmoothed; peak from the map smoothed by 1 cell.", 0.19)
    fig.savefig(out / "fig2-impact-regions.png", dpi=200); fig.savefig(out / "fig2-impact-regions.pdf"); plt.close(fig)


def fig_tension(D, R, out):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.0))
    fig.subplots_adjust(left=0.19, right=0.99, top=0.88, bottom=0.37, wspace=0.55)
    ax = axes[0]; ys = []
    for j, tag in enumerate(("r600", "heldout")):
        T = R["options"][tag]["tension"]["before searches"]
        for i, st in enumerate(STRATA):
            v = T["per_stratum"][SNAME[st]]; y = i + 0.18 * (1 if j else -1)
            ax.plot(list(v["ln_R_per_seed"].values()), [y] * 4, "o", ms=2.5, color=["#1f5fa8", "#8c8c8c"][j], alpha=0.6)
            ax.plot(v["ln_R"], y, "D", ms=5, color=["#1f5fa8", "#8c8c8c"][j], label=ONAME[tag] if i == 0 else None)
        ax.plot(T["reweighted-0019"]["ln_R"], 4 + 0.18 * (1 if j else -1), "D", ms=6, color=["#1f5fa8", "#8c8c8c"][j], mec="k")
    ax.axvline(0, color="k", lw=0.6)
    ax.set_yticks(range(5)); ax.set_yticklabels([SNAME[s] for s in STRATA] + ["mixture"]); ax.invert_yaxis()
    ax.set_xlabel("ln R (positive: drift and sound favour the Pléiades area)")
    ax.set_title("Agreement of drift and sound with the Pléiades area", loc="left"); fig.legend(*ax.get_legend_handles_labels(), frameon=False, loc="upper right", bbox_to_anchor=(0.99, 0.995), ncol=2, fontsize=6.5)
    ax = axes[1]
    keys = ["P1", "D", "Y", "S", "G", "Ga", "PE", "H", "Ha"]
    lab = ["flight + descent", "+ drift alone", "+ sound alone", "+ searches alone", "+ drift + sound", "  then searches", "+ Pléiades alone", "+ drift, sound, Pléiades", "  then searches"]
    for i, k in enumerate(keys):
        for st, mk in zip(STRATA, "os^v"):
            e = min(x[1] for x in D[st]["products"][f"r600-{k}"]["ess_rows_parents"])
            ax.plot(e, i, mk, ms=3.5, color="#1f5fa8", alpha=0.85, label=SNAME[st] if i == 0 else None)
    ax.axvline(1000, color="#b00020", lw=0.8, ls=":"); ax.text(1100, 0.0, "floor 1,000", fontsize=6, color="#b00020", va="center")
    ax.set_xscale("log"); ax.set_yticks(range(len(keys))); ax.set_yticklabels(lab); ax.invert_yaxis()
    ax.set_xlim(300, 1.5e5)
    ax.set_xlabel("Effective parents, smallest seed (log scale)"); ax.set_title("Effective sample size, primary case", loc="left")
    ax.legend(frameon=False, fontsize=6, loc="upper left", bbox_to_anchor=(0.0, 0.62))
    fig.suptitle("Pléiades agreement test and sample adequacy", x=0.01, ha="left", fontsize=9)
    footer(fig, "Left: a value above zero shows that the drift and sound evidence moves the probability towards the Pléiades area. Small dots are the "
                "four seeds. Right: the number of independent samples that each step keeps. The input sample did not settle.",
           COMMON_TECH + " ln R = ln E[L_P | flight+EoF+drift+hydro] - ln E[L_P | flight+EoF] (the Pléiades A_scene constant cancels); "
                         "mixture uses the 00:19-re-weighted strata. ESS: composer Ess.parents (children of one hand-off row summed).", 0.245)
    fig.savefig(out / "fig3-tension-and-ess.png", dpi=200); fig.savefig(out / "fig3-tension-and-ess.pdf"); plt.close(fig)


def fig_families(D, R, out):
    fig, ax = plt.subplots(figsize=(7.2, 4.0)); fig.subplots_adjust(left=0.30, right=0.98, top=0.88, bottom=0.37)
    fams = ["A1 (with A-then-lost)", "A2", "B"]
    names = {"A1 (with A-then-lost)": "A1: fuel exhaustion, no control", "A2": "A2: fuel exhaustion, controlled", "B": "B: planned descent before exhaustion"}
    for j, key in enumerate(("P1", "G", "H")):
        e = R["options"]["r600"]["products"][key]["reweighted-0019"]
        for i, f in enumerate(fams):
            s = e["family_stats"][f]; y = i + (j - 1) * 0.22
            ax.plot([s["q025"], s["q975"]], [y, y], color=COL[key], lw=1.2); ax.plot(s["median"], y, "o", color=COL[key], ms=4, label=NAMES[key] if i == 0 else None)
            ax.text(-23.8, y, f"P = {e['family_probability'][f]:.2f}", fontsize=6, va="center", color=COL[key])
    ax.set_yticks(range(3)); ax.set_yticklabels([names[f] for f in fams]); ax.invert_yaxis(); ax.set_xlim(-44, -22)
    ax.set_xlabel("Impact latitude, median and 95 % interval (degrees)")
    fig.legend(*ax.get_legend_handles_labels(), frameon=False, fontsize=6.5, loc="upper right", ncol=3, bbox_to_anchor=(0.99, 0.995))
    ax.set_title("Impact latitude for each end-of-flight family, primary case", loc="left")
    footer(fig, "Each line shows the impact latitude for one type of end of flight. P is the probability of that type. The data after 00:11 do not "
                "much change these probabilities, so they come mostly from the prior. Type B is only partly modelled.",
           COMMON_TECH + " Families from EoF family_labels (onset_mechanism x control_realised; 4 'A, controlled then lost' composed with A1, "
                         "sensitivity with A2 in families.csv). B covers only descents begun after 00:11.", 0.245)
    fig.savefig(out / "fig4-families.png", dpi=200); fig.savefig(out / "fig4-families.pdf"); plt.close(fig)


def figures(D, R, out):
    fig_latitude(D, R, out); fig_maps(D, R, out); fig_tension(D, R, out); fig_families(D, R, out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
